import io
import logging
import mimetypes

from .errors import InvalidTypeError
from .fields import (
    Base64Field,
    BooleanField,
    DateTimeField,
    EWSElementField,
    FieldPath,
    IdField,
    IntegerField,
    ItemField,
    TextField,
    URIField,
)
from .properties import BaseItemId, EWSElement, EWSMeta

log = logging.getLogger(__name__)


class AttachmentId(BaseItemId):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/attachmentid"""

    ELEMENT_NAME = "AttachmentId"

    ID_ATTR = "Id"
    ROOT_ID_ATTR = "RootItemId"
    ROOT_CHANGEKEY_ATTR = "RootItemChangeKey"

    id = IdField(field_uri=ID_ATTR, is_required=True)
    root_id = IdField(field_uri=ROOT_ID_ATTR)
    root_changekey = IdField(field_uri=ROOT_CHANGEKEY_ATTR)


class Attachment(EWSElement, metaclass=EWSMeta):
    """Base class for FileAttachment and ItemAttachment."""

    attachment_id = EWSElementField(value_cls=AttachmentId)
    name = TextField(field_uri="Name")
    content_type = TextField(field_uri="ContentType")
    content_id = TextField(field_uri="ContentId")
    content_location = URIField(field_uri="ContentLocation")
    size = IntegerField(field_uri="Size", is_read_only=True)  # Attachment size in bytes
    last_modified_time = DateTimeField(field_uri="LastModifiedTime")
    is_inline = BooleanField(field_uri="IsInline")

    __slots__ = ("parent_item",)

    def __init__(self, **kwargs):
        self.parent_item = kwargs.pop("parent_item", None)
        super().__init__(**kwargs)

    def clean(self, version=None):
        from .items import Item

        if self.parent_item is not None and not isinstance(self.parent_item, Item):
            raise InvalidTypeError("parent_item", self.parent_item, Item)
        if self.content_type is None and self.name is not None:
            self.content_type = mimetypes.guess_type(self.name)[0] or "application/octet-stream"
        super().clean(version=version)

    def attach(self):
        from .services import CreateAttachment

        # Adds this attachment to an item and updates the changekey of the parent item
        if self.attachment_id:
            raise ValueError("This attachment has already been created")
        if not self.parent_item or not self.parent_item.account:
            raise ValueError(f"Parent item {self.parent_item} must have an account")
        item = CreateAttachment(account=self.parent_item.account).get(parent_item=self.parent_item, items=[self])
        attachment_id = item.attachment_id
        self.parent_item.changekey = attachment_id.root_changekey
        # EWS does not like receiving root_id and root_changekey on subsequent requests
        attachment_id.root_id = None
        attachment_id.root_changekey = None
        self.attachment_id = attachment_id

    def detach(self):
        from .services import DeleteAttachment

        # Deletes an attachment remotely and updates the changekey of the parent item
        if not self.attachment_id:
            raise ValueError("This attachment has not been created")
        if not self.parent_item or not self.parent_item.account:
            raise ValueError(f"Parent item {self.parent_item} must have an account")
        DeleteAttachment(account=self.parent_item.account).get(items=[self.attachment_id])
        self.parent_item = None
        self.attachment_id = None

    def __hash__(self):
        if self.attachment_id:
            return hash(self.attachment_id)
        # Be careful to avoid recursion on the back-reference to the parent item
        return hash(tuple(getattr(self, f) for f in self._slots_keys if f != "parent_item"))

    def __repr__(self):
        args_str = ", ".join(
            f"{f.name}={getattr(self, f.name)!r}" for f in self.FIELDS if f.name not in ("_item", "_content")
        )
        return f"{self.__class__.__name__}({args_str})"


class FileAttachment(Attachment):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/fileattachment"""

    ELEMENT_NAME = "FileAttachment"

    is_contact_photo = BooleanField(field_uri="IsContactPhoto")
    _content = Base64Field(field_uri="Content")

    __slots__ = ("_fp",)

    def __init__(self, **kwargs):
        kwargs["_content"] = kwargs.pop("content", None)
        super().__init__(**kwargs)
        self._fp = None

    @property
    def fp(self):
        # Return a file-like object for the content. This avoids creating multiple in-memory copies of the content.
        if self._fp is None:
            self._init_fp()
        return self._fp

    def _init_fp(self):
        # Create a file-like object for the attachment content. We try hard to reduce memory consumption, so we never
        # store the full attachment content in-memory.
        if not self.parent_item or not self.parent_item.account:
            raise ValueError(f"{self.__class__.__name__} must have an account")
        self._fp = FileAttachmentIO(attachment=self)

    @property
    def content(self):
        """Return the attachment content. Stores a local copy of the content in case you want to upload the attachment
        again later.
        """
        if self.attachment_id is None:
            return self._content
        if self._content is not None:
            return self._content
        # We have an ID to the data but still haven't called GetAttachment to get the actual data. Do that now.
        with self.fp as fp:
            self._content = fp.read()
        return self._content

    @content.setter
    def content(self, value):
        """Replace the attachment content."""
        if not isinstance(value, bytes):
            raise InvalidTypeError("value", value, bytes)
        self._content = value

    @classmethod
    def from_xml(cls, elem, account):
        kwargs = {f.name: f.from_xml(elem=elem, account=account) for f in cls.FIELDS}
        kwargs["content"] = kwargs.pop("_content")
        cls._clear(elem)
        return cls(**kwargs)

    def to_xml(self, version):
        self._content = self.content  # Make sure content is available, to avoid ErrorRequiredPropertyMissing
        return super().to_xml(version=version)

    def __getstate__(self):
        # The fp does not need to be pickled
        state = {k: getattr(self, k) for k in self._slots_keys}
        del state["_fp"]
        return state

    def __setstate__(self, state):
        # Restore the fp
        for k in self._slots_keys:
            setattr(self, k, state.get(k))
        self._fp = None


class ItemAttachment(Attachment):
    """MSDN: https://docs.microsoft.com/en-us/exchange/client-developer/web-service-reference/itemattachment"""

    ELEMENT_NAME = "ItemAttachment"

    _item = ItemField(field_uri="Item")

    def __init__(self, **kwargs):
        kwargs["_item"] = kwargs.pop("item", None)
        super().__init__(**kwargs)

    @property
    def item(self):
        from .folders import BaseFolder
        from .services import GetAttachment

        if self.attachment_id is None:
            return self._item
        if self._item is not None:
            return self._item
        # We have an ID to the data but still haven't called GetAttachment to get the actual data. Do that now.
        if not self.parent_item or not self.parent_item.account:
            raise ValueError(f"{self.__class__.__name__} must have an account")
        additional_fields = {
            FieldPath(field=f) for f in BaseFolder.allowed_item_fields(version=self.parent_item.account.version)
        }
        attachment = GetAttachment(account=self.parent_item.account).get(
            items=[self.attachment_id],
            include_mime_content=True,
            body_type=None,
            filter_html_content=None,
            additional_fields=additional_fields,
        )
        self._item = attachment.item
        return self._item

    @item.setter
    def item(self, value):
        from .items import Item

        if not isinstance(value, Item):
            raise InvalidTypeError("value", value, Item)
        self._item = value

    @classmethod
    def from_xml(cls, elem, account):
        kwargs = {f.name: f.from_xml(elem=elem, account=account) for f in cls.FIELDS}
        kwargs["item"] = kwargs.pop("_item")
        cls._clear(elem)
        return cls(**kwargs)


class FileAttachmentIO(io.RawIOBase):
    """A BytesIO where the stream of data comes from the GetAttachment service."""

    def __init__(self, attachment):
        self._attachment = attachment
        self._stream = None
        self._overflow = None

    def readable(self):
        return True

    @property
    def closed(self):
        return self._stream is None

    def readinto(self, b):
        buf_size = len(b)  # We can't return more than l bytes
        try:
            chunk = self._overflow or next(self._stream)
        except StopIteration:
            return 0
        else:
            output, self._overflow = chunk[:buf_size], chunk[buf_size:]
            b[: len(output)] = output
            return len(output)

    def __enter__(self):
        from .services import GetAttachment

        self._stream = GetAttachment(account=self._attachment.parent_item.account).stream_file_content(
            attachment_id=self._attachment.attachment_id
        )
        self._overflow = None
        return io.BufferedReader(self, buffer_size=io.DEFAULT_BUFFER_SIZE)

    def __exit__(self, *args, **kwargs):
        self._stream = None
        self._overflow = None
