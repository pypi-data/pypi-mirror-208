import re
import os
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.utils import timezone

from .settings import MAX_BYTES
from .models import ChunkedUpload, MyChunkedUpload
from .response import Response
from .constants import http_status, COMPLETE
from .exceptions import ChunkedUploadError

from django.views.generic.base import TemplateView
from uploads.serializers import ChunkedUploadSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from django.middleware.csrf import get_token
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

import hashlib
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from google.cloud import storage

def is_authenticated(user):
    if callable(user.is_authenticated):
        return user.is_authenticated()  # Django <2.0
    return user.is_authenticated  # Django >=2.0




class ChunkedUploadBaseView(View):
    """
    Base view for the rest of chunked upload views.
    """

    # Has to be a ChunkedUpload subclass
    today = timezone.localtime(timezone.now()).date()
    client = storage.Client()
    bucket = client.get_bucket('cos-dev-filestore')
    model = ChunkedUpload
    user_field_name = 'user'  # the field name that point towards the AUTH_USER in ChunkedUpload class or its subclasses

    def get_queryset(self, request):
        """
        Get (and filter) ChunkedUpload queryset.
        By default, users can only continue uploading their own uploads.
        """
        queryset = self.model.objects.all()
        if hasattr(request, 'user') and is_authenticated(request.user):
            queryset = queryset.filter(**{self.user_field_name: request.user})
        return queryset

    def validate(self, request):
        """
        Placeholder method to define extra validation.
        Must raise ChunkedUploadError if validation fails.
        """

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary-like object.
        Called *only* if POST is successful.
        """
        return {}

    def pre_save(self, chunked_upload, request, new=False):
        """
        Placeholder method for calling before saving an object.
        May be used to set attributes on the object that are implicit
        in either the request, or the url.
        """

    def save(self, chunked_upload, request, new=False):
        """
        Method that calls save(). Overriding may be useful is save() needs
        special args or kwargs.
        """
        chunked_upload.save()

    def post_save(self, chunked_upload, request, new=False):
        """
        Placeholder method for calling after saving an object.
        """

    def _save(self, chunked_upload):
        """
        Wraps save() method.
        """
        new = chunked_upload.id is None
        self.pre_save(chunked_upload, self.request, new=new)
        self.save(chunked_upload, self.request, new=new)
        self.post_save(chunked_upload, self.request, new=new)

    def check_permissions(self, request):
        """
        Grants permission to start/continue an upload based on the request.
        """
        if hasattr(request, 'user') and not is_authenticated(request.user):
            raise ChunkedUploadError(
                status=http_status.HTTP_403_FORBIDDEN,
                detail='Authentication credentials were not provided'
            )

    def _post(self, request, *args, **kwargs):
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests.
        """
        try:
            self.check_permissions(request)
            return self._post(request, *args, **kwargs)
        except ChunkedUploadError as error:
            return Response(error.data, status=error.status_code)


class ChunkedUploadView(ChunkedUploadBaseView):
    """
    Uploads large files in multiple chunks. Also, has the ability to resume
    if the upload is interrupted.
    """

    field_name = 'file'
    content_range_header = 'HTTP_CONTENT_RANGE'
    content_range_pattern = re.compile(
        r'^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+)$'
    )
    max_bytes = MAX_BYTES  # Max amount of data that can be uploaded
    # If `fail_if_no_header` is True, an exception will be raised if the
    # content-range header is not found. Default is False to match Jquery File
    # Upload behavior (doesn't send header if the file is smaller than chunk)
    fail_if_no_header = False

    def get_extra_attrs(self, request):
        """
        Extra attribute values to be passed to the new ChunkedUpload instance.
        Should return a dictionary-like object.
        """
        return {}

    def get_max_bytes(self, request):
        """
        Used to limit the max amount of data that can be uploaded. `None` means
        no limit.
        You can override this to have a custom `max_bytes`, e.g. based on
        logged user.
        """

        return self.max_bytes

    def create_chunked_upload(self, save=False, **attrs):
        """
        Creates new chunked upload instance. Called if no 'upload_id' is
        found in the POST data.
        """
        chunked_upload = self.model(**attrs)
        # file starts empty
        chunked_upload.file.save(name='', content=ContentFile(''), save=save)
        return chunked_upload

    def is_valid_chunked_upload(self, chunked_upload):
        """
        Check if chunked upload has already expired or is already complete.
        """
        if chunked_upload.expired:
            raise ChunkedUploadError(status=http_status.HTTP_410_GONE,
                                     detail='Upload has expired')
        error_msg = 'Upload has already been marked as "%s"'
        if chunked_upload.status == COMPLETE:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail=error_msg % 'complete')

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary-like object.
        """
        return {
            'upload_id': chunked_upload.upload_id,
            'offset': chunked_upload.offset,
            'expires': chunked_upload.expires_on
        }

    def _post(self, request, *args, **kwargs):
        print(request)
        chunk = request.data['file']
        if chunk is None:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail='No chunk file was submitted')
        self.validate(request)

        upload_id = request.data['upload_id']
        if request.data['chunk_number']:
            chunk_number = request.data['chunk_number'] 
        if upload_id:
            chunked_upload = get_object_or_404(self.get_queryset(request),
                                               upload_id=upload_id)
            self.is_valid_chunked_upload(chunked_upload)
        else:
            attrs = {'filename': chunk.name}
            if hasattr(request, 'user') and is_authenticated(request.user):
                attrs['user'] = request.user
            attrs.update(self.get_extra_attrs(request))
            chunked_upload = self.create_chunked_upload(save=False, **attrs)

        content_range = request.META.get(self.content_range_header, '')
        match = self.content_range_pattern.match(content_range)
        print(chunk.size)
        comments = """if offset:
            start = int(match.group('start'))
            end = int(match.group('end'))
            total = int(match.group('total'))
        elif self.fail_if_no_header:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail='Error in request headers')
        else:
            # Use the whole size when HTTP_CONTENT_RANGE is not provided
            start = 0
            end = chunk.size - 1
            total = chunk.size

        chunk_size = end - start + 1
        max_bytes = self.get_max_bytes(request)

        if max_bytes is not None and total > max_bytes:
            raise ChunkedUploadError(
                status=http_status.HTTP_400_BAD_REQUEST,
                detail='Size of file exceeds the limit (%s bytes)' % max_bytes
            )
        print(chunked_upload.offset)
        print(start)
        if chunked_upload.offset != start:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail='Offsets do not match',
                                     offset=chunked_upload.offset)
        if chunk.size != chunk_size:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail="File size doesn't match headers")
        """
        attrs = {}
        attrs['today'] = self.today
        attrs['bucket'] = self.bucket
        chunked_upload.append_chunk(chunk, chunk_size=chunk.size, chunk_number=chunk_number,save=False,attrs=attrs)

        self._save(chunked_upload)

        return Response(self.get_response_data(chunked_upload, request),
                        status=http_status.HTTP_200_OK)


class ChunkedUploadCompleteView(ChunkedUploadBaseView):
    """
    Completes an chunked upload. Method `on_completion` is a placeholder to
    define what to do when upload is complete.
    """

    # I wouldn't recommend to turn off the md5 check, unless is really
    # impacting your performance. Proceed at your own risk.
    do_md5_check = False

    def on_completion(self, uploaded_file, request):
        """
        Placeholder method to define what to do when upload is complete.
        """

    def is_valid_chunked_upload(self, chunked_upload):
        """
        Check if chunked upload is already complete.
        """
        if chunked_upload.status == COMPLETE:
            error_msg = "Upload has already been marked as complete"
            return ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                      detail=error_msg)

    def md5_check(self, chunked_upload, md5):
        """
        Verify if md5 checksum sent by client matches generated md5.
        """
        if chunked_upload.md5 != md5:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail='md5 checksum does not match')

    def _post(self, request, *args, **kwargs):
        upload_id = request.data['upload_id']
        md5 = request.data['md5']

        error_msg = None
        if self.do_md5_check:
            if not upload_id or not md5:
                error_msg = "Both 'upload_id' and 'md5' are required"
        elif not upload_id:
            error_msg = "'upload_id' is required"
        if error_msg:
            raise ChunkedUploadError(status=http_status.HTTP_400_BAD_REQUEST,
                                     detail=error_msg)

        chunked_upload = get_object_or_404(self.get_queryset(request),
                                           upload_id=upload_id)

        self.validate(request)
        self.is_valid_chunked_upload(chunked_upload)
        if self.do_md5_check:
            self.md5_check(chunked_upload, md5)

        chunked_upload.status = COMPLETE
        chunked_upload.completed_on = timezone.now()
        self._save(chunked_upload)
        self.on_completion(chunked_upload.get_uploaded_file(), request)

        return Response(self.get_response_data(chunked_upload, request),
                        status=http_status.HTTP_200_OK)

class MyChunkedUploadView(ChunkedUploadView):

    model = MyChunkedUpload
    field_name = 'the_file'

    def check_permissions(self, request):
        # Allow non authenticated users to make uploads
        pass

class ChunkedUploadApiViewSet(viewsets.ModelViewSet):

    queryset = MyChunkedUpload.objects.all()
    model = MyChunkedUpload
    serializer_class = ChunkedUploadSerializer
    def get_response_data(self, chunked_upload):
        """
        Data for the response. Should return a dictionary-like object.
        """
        return {
            'upload_id': chunked_upload.upload_id,
            'offset': chunked_upload.offset,
            'expires': chunked_upload.expires_on
        }
    def md5(self,file):
        CHUNK_SIZE = 10485760
        md5 = hashlib.md5()
        for chunk in file.chunks(CHUNK_SIZE):
            md5.update(chunk)
        md5 = md5.hexdigest()
        return md5
    def create(self, request, pk=None):
        print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        file = request.data['file']
        content_type = file.content_type
        print(type(file))
        md5 = self.md5(file)
        fetch = 0
        offset = 0
        if self.queryset.filter(file_md5=md5).exists():
            fetch = 1
            resume_upload = self.queryset.get(file_md5=md5)
            resume_serializer = ChunkedUploadSerializer(resume_upload)
            upload_id = resume_serializer.data['upload_id']
            offset = resume_serializer.data['offset']
            print(resume_serializer.data)

        CHUNK_SIZE = 10485760
        chunk_number = 1
        cuv = MyChunkedUploadView()
        today = timezone.localtime(timezone.now()).date()
        filename = request.data['filename']
        for chunk in file.chunks(CHUNK_SIZE):
            print(type(chunk))
            content = ContentFile(chunk)
            chunk = InMemoryUploadedFile(content, None, filename, content_type, len(chunk), None)
            if fetch == 0 and chunk_number == 1:
                request.data['file_md5'] = md5
                request.data['file'] = chunk
                serializer = ChunkedUploadSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                print(request)
                upload_id = serializer.data['upload_id']
                print(serializer.data['offset'])
                print(upload_id)
            if fetch == 1 and chunk_number == 1 and offset != 0:
                offset -= CHUNK_SIZE
                continue
            else:
                cuv.request = request
                request.data['chunk_number'] = chunk_number
                request.data['upload_id'] = upload_id
                request.data['file'] = chunk
                x = cuv._post(request)
                print(x)
            chunk_number += 1
        today = cuv.today
        bucket = cuv.bucket
        outputfile = f"chunked_uploads/{today}/{upload_id}/{filename}"
        blobs = []
        for shard in range(1,7):
            sfile = f'chunked_uploads/{today}/{upload_id}/{filename}{shard}'
            blob = bucket.blob(sfile)
            if not blob.exists():
                # this causes a retry in 60s
                raise ValueError(f'branch {sfile} not present')
            blobs.append(blob)
            bucket.blob(outputfile).compose(blobs)
        for blob in blobs:
            blob.delete()
        chunked_upload = self.queryset.get(upload_id=upload_id)
        if (md5 == chunked_upload.md5):
            data = {"status" : 2,"completed_on" : timezone.now()}
            serializer = ChunkedUploadSerializer(chunked_upload, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
        else:
            error_msg = 'Md5 is wrong, byte transfer error'
            return Response(error_msg, status=400)
        return Response(serializer.data)

    resume = """def resume(self, request):
        file = request.data['file']
        upload_id = request.data['upload_id']
        cuv = MyChunkedUploadView()
        chunked_upload = self.queryset.get(upload_id=upload_id)
        serializer = ChunkedUploadSerializer(chunked_upload)
        offset = serializer.data['offset']
        CHUNK_SIZE = 10485760
        for chunk in file.chunks(CHUNK_SIZE):
            if offset != 0:
                offset -= CHUNK_SIZE
                continue
            cuv.request = request
            request.data['file'] = chunk
            x = cuv._post(request)
            print(x)

        chunked_upload = self.queryset.get(upload_id=upload_id)
        if (self.md5(file) == chunked_upload.md5):
            data = {"status" : 2,"completed_on" : timezone.now()}
            serializer = ChunkedUploadSerializer(chunked_upload, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
        else:
            error_msg = 'Md5 is wrong, byte transfer error'
            return Response(error_msg, status=400)
        return Response(serializer.get_uploaded_file(chunked_upload))"""
    
    combine = '''@action(methods=["POST"], detail=False)
    def combine(self, request):
        today = timezone.localtime(timezone.now()).date()
        client = storage.Client()
        filename = "trees.mp4"
        upload_id = "5ebceb9203204fcab712be5422fa2e04"
        bucket = client.get_bucket('cos-dev-filestore')
        outputfile = f"chunked_uploads/{today}/{upload_id}/{filename}"
        blobs = []
        for shard in range(1,7):
            sfile = f'chunked_uploads/{today}/{upload_id}/{filename}{shard}'
            blob = bucket.blob(sfile)
            if not blob.exists():
                # this causes a retry in 60s
                raise ValueError(f'branch {sfile} not present')
            blobs.append(blob)
            bucket.blob(outputfile).compose(blobs)
        for blob in blobs:
            blob.delete()

        return Response("Done")'''
    