from .models import MyChunkedUpload
from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """Base Serializer class to be inherited by other Serializer classes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # noqa

class ChunkedUploadSerializer(BaseModelSerializer):
    class Meta:
        model = MyChunkedUpload
        fields = "__all__"
    def md5(self,obj):
        return obj.md5

    def get_uploaded_file(self,obj):
        return obj.get_uploaded_file()