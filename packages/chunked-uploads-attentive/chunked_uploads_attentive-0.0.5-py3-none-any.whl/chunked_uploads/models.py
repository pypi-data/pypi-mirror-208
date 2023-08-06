import hashlib
import uuid

from django.db import models
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from google.cloud import storage

from .settings import EXPIRATION_DELTA, UPLOAD_TO, STORAGE, DEFAULT_MODEL_USER_FIELD_NULL, DEFAULT_MODEL_USER_FIELD_BLANK
from .constants import CHUNKED_UPLOAD_CHOICES, UPLOADING


def generate_upload_id():
    return uuid.uuid4().hex

def upload_remote_path(instance, filename):
    parent_folder = "chunked_uploads"
    today = timezone.localtime(timezone.now()).date()
    upload_id = instance.upload_id
    filename = instance.filename
    return f"{parent_folder}/{today}/{upload_id}/{filename}"

class AbstractChunkedUpload(models.Model):
    """
    Base chunked upload model. This model is abstract (doesn't create a table
    in the database).
    Inherit from this model to implement your own.
    """

    upload_id = models.CharField(max_length=32, unique=True, editable=False,
                                 default=generate_upload_id)
    file = models.FileField(max_length=255, upload_to=upload_remote_path,
                            storage=STORAGE)
    filename = models.CharField(max_length=255)
    offset = models.BigIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.PositiveSmallIntegerField(choices=CHUNKED_UPLOAD_CHOICES,
                                              default=UPLOADING)
    completed_on = models.DateTimeField(null=True, blank=True)
    file_md5 = models.CharField(null=True, max_length=128)

    @property
    def expires_on(self):
        return self.created_on + EXPIRATION_DELTA

    @property
    def expired(self):
        return self.expires_on <= timezone.now()

    @property
    def md5(self):
        if getattr(self, '_md5', None) is None:
            md5 = hashlib.md5()
            for chunk in self.file.chunks():
                md5.update(chunk)
            self._md5 = md5.hexdigest()
        return self._md5

    def delete(self, delete_file=True, *args, **kwargs):
        if self.file:
            storage, path = self.file.storage, self.file.path
        super(AbstractChunkedUpload, self).delete(*args, **kwargs)
        if self.file and delete_file:
            storage.delete(path)

    def __str__(self):
        return u'<%s - upload_id: %s - bytes: %s - status: %s>' % (
            self.filename, self.upload_id, self.offset, self.status)

    def append_chunk(self, chunk, chunk_size=None,chunk_number=0, save=True,attrs= None):
        today = attrs['today']
        bucket = attrs['bucket']
        blob = bucket.blob(f"chunked_uploads/{today}/{self.upload_id}/{self.filename}{chunk_number}")
        blob.upload_from_file(chunk, content_type=chunk.content_type,rewind=True)
        if chunk_size is not None:
            self.offset += chunk_size
        elif hasattr(chunk, 'size'):
            self.offset += chunk.size
        else:
            self.offset = self.file.size
        self._md5 = None  # Clear cached md5
        if save:
            self.save()
        self.file.close()  # Flush

    def get_uploaded_file(self):
        self.file.close()
        self.file.open(mode='rb')  # mode = read+binary
        return UploadedFile(file=self.file, name=self.filename,
                            size=self.offset)

    class Meta:
        abstract = True


class ChunkedUpload(AbstractChunkedUpload):
    """
    Default chunked upload model.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chunked_uploads',
        null=DEFAULT_MODEL_USER_FIELD_NULL,
        blank=DEFAULT_MODEL_USER_FIELD_BLANK
    )

MyChunkedUpload = ChunkedUpload
