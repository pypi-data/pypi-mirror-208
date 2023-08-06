import re
import os
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.utils import timezone
import datetime

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
    model = ChunkedUpload
    user_field_name = "user"  # the field name that point towards the AUTH_USER in ChunkedUpload class or its subclasses

    def get_queryset(self, request):
        """
        Get (and filter) ChunkedUpload queryset.
        By default, users can only continue uploading their own uploads.
        """
        queryset = self.model.objects.all()
        if hasattr(request, "user") and is_authenticated(request.user):
            queryset = queryset.filter(**{self.user_field_name: request.user})
        return queryset


    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary-like object.
        Called *only* if POST is successful.
        """
        return {}

    def save(self, chunked_upload, request, new=False):
        """
        Method that calls save(). Overriding may be useful is save() needs
        special args or kwargs.
        """
        chunked_upload.save()

    def _save(self, chunked_upload):
        """
        Wraps save() method.
        """
        new = chunked_upload.id is None
        self.save(chunked_upload, self.request, new=new)

    def check_permissions(self, request):
        """
        Grants permission to start/continue an upload based on the request.
        """
        if hasattr(request, "user") and not is_authenticated(request.user):
            raise ChunkedUploadError(
                status=http_status.HTTP_403_FORBIDDEN,
                detail="Authentication credentials were not provided",
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

    field_name = "file"
    content_range_header = "HTTP_CONTENT_RANGE"
    content_range_pattern = re.compile(
        r"^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+)$"
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

    def create_chunked_upload(self, save=False, **attrs):
        """
        Creates new chunked upload instance. Called if no 'upload_id' is
        found in the POST data.
        """
        chunked_upload = self.model(**attrs)
        # file starts empty
        chunked_upload.file.save(name="", content=ContentFile(""), save=save)
        return chunked_upload

    def is_valid_chunked_upload(self, chunked_upload):
        """
        Check if chunked upload has already expired or is already complete.
        """
        if chunked_upload.expired:
            raise ChunkedUploadError(
                status=http_status.HTTP_410_GONE, detail="Upload has expired"
            )
        error_msg = 'Upload has already been marked as "%s"'
        if chunked_upload.status == COMPLETE:
            raise ChunkedUploadError(
                status=http_status.HTTP_400_BAD_REQUEST, detail=error_msg % "complete"
            )

    def get_response_data(self, chunked_upload, request):
        """
        Data for the response. Should return a dictionary-like object.
        """
        return {
            "upload_id": chunked_upload.upload_id,
            "offset": chunked_upload.offset,
            "expires": chunked_upload.expires_on,
        }

    def _post(self, request, *args, **kwargs):
        print(request)
        chunk = request.data["file"]
        if chunk is None:
            raise ChunkedUploadError(
                status=http_status.HTTP_400_BAD_REQUEST,
                detail="No chunk file was submitted",
            )

        upload_id = request.data["upload_id"]
        chunk_num = request.data['chunk_num']
        if upload_id:
            chunked_upload = get_object_or_404(
                self.get_queryset(request), upload_id=upload_id
            )
            self.is_valid_chunked_upload(chunked_upload)
        else:
            attrs = {"filename": chunk.name}
            if hasattr(request, "user") and is_authenticated(request.user):
                attrs["user"] = request.user
            attrs.update(self.get_extra_attrs(request))
            chunked_upload = self.create_chunked_upload(save=False, **attrs)
    
        chunked_upload.append_chunk(chunk, chunk_size=chunk.size, save=False,chunk_num = chunk_num)

        self._save(chunked_upload)

        return Response(
            self.get_response_data(chunked_upload, request),
            status=http_status.HTTP_200_OK,
        )

class ChunkedUploadApiViewSet(viewsets.ModelViewSet):

    today = timezone.localtime(timezone.now()).date()
    client = storage.Client()
    bucket = client.get_bucket("cos-dev-filestore")
    queryset = MyChunkedUpload.objects.all()
    model = MyChunkedUpload
    serializer_class = ChunkedUploadSerializer
    CHUNK_SIZE = 262144

    def md5(self, file):
        """
        Caculates md5 hash value of a give file
        """
        md5 = hashlib.md5()
        for chunk in file.chunks(self.CHUNK_SIZE):
            md5.update(chunk)
        md5 = md5.hexdigest()
        return md5

    def create(self, request, pk=None):
        """
        Takes in various chunks and stores them in a file. Also updates the database.
        """
        filename = request.data["filename"] 
        chunk_num = request.data["chunk_num"]
        chunk = request.data["chunk"]
        file_md5 = request.data['file_md5'] 
        chunk_md5 = request.data['chunk_md5']
        #file_size = request.data["size"]
        if(chunk_md5 != self.md5(chunk)):
            return Response({"chunk_num" : chunk_num,"message" :"File Corrupt","status" : 2})

        if self.queryset.filter(file_md5=file_md5).exists():
            resume_upload = self.queryset.get(file_md5=file_md5)
            resume_serializer = ChunkedUploadSerializer(resume_upload)
            upload_id = resume_serializer.data["upload_id"]
            if resume_serializer.data['status'] == 2:
                return Response({"chunk_num" : chunk_num,"message" :"File Already Uploaded","status" : 3,"url" :f"{resume_serializer.data['file']}"})
            print(resume_serializer.data)
            cuv = ChunkedUploadView()
            cuv.request = request
            request.data['upload_id'] = upload_id
            request.data['file'] = chunk.open()
            request.data['chunk_num'] = chunk_num
            x = cuv._post(request)
            print(x)
        else:
            request.data["file_md5"] = file_md5
            request.data["file"] = chunk
            serializer = ChunkedUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(request)
            upload_id = serializer.data["upload_id"]
            print(serializer.data["offset"])
            print(upload_id)    
        return Response({"chunk_num" : chunk_num, "message" : "Done","status" : 1})
    

    @action(methods=["PATCH"], detail=False)
    def combine_chunks(self, request):
        """
        Checks if all chunks are present and Combines them. Also deletes already combined chunks.
        """
        filename = request.data["filename"] 
        file_md5 = request.data['file_md5'] 
        file_size = int(request.data["size"])
        if file_size%self.CHUNK_SIZE == 0:
            ciel = int(file_size/self.CHUNK_SIZE)
        else:
            ciel = int(file_size/self.CHUNK_SIZE) + 1
        if self.queryset.filter(file_md5=file_md5).exists():
            fetch = 1
            resume_upload = self.queryset.get(file_md5=file_md5)
            resume_serializer = ChunkedUploadSerializer(resume_upload)
            upload_id = resume_serializer.data["upload_id"]
            #if resume_serializer.data['status'] == 2:
                #return Response({"url" : f"{resume_serializer.data['file']}", "message" : "Done" , "status": 1})
            print(resume_serializer.data['file'])
            path = f'./chunked_uploads/{upload_id}/{filename}'
            for i in range(2, ciel + 1):
                if os.path.isfile(path+str(i)) == False:
                    return Response({"chunk_num": {i},"message" : f"Chunk Number : {i} not arrived", "status": "failure"})

            with open(path, "ab") as file_obj:  # mode = append+binary
                for i in range(2,ciel + 1):
                    with open(path+str(i),'rb') as chunk:
                        file_obj.write(
                            chunk.read()
                        )
                    os.remove(path+str(i))
                
        else:
            return Response({"message" : "wrong md5", "status": 2})
        # GCS
        try:
            blob = self.bucket.blob(f"chunked_uploads/{self.today}/{upload_id}/{filename}")
            with open(path,'rb') as file:
                blob.upload_from_file(file,rewind=True)
            url = blob.generate_signed_url(
                    version="v2",
                    # This URL is valid for 365 days
                    expiration=datetime.timedelta(days=365),
                    # Allow GET requests using this URL.
                    method="GET",
                )
            if self.queryset.filter(file_md5=file_md5).exists():
                resume_upload = self.queryset.get(file_md5=file_md5)
                resume_upload.file = url
                resume_upload.completed_on = timezone.datetime.now()
                resume_upload.status = 2
                serializer = ChunkedUploadSerializer(resume_upload, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
            os.remove(path)
        except:
            return Response({"status" : 3, "message" : "Error on upload"})
        return Response({"url" : f"{url}", "message" : "Done", "status": 1})
    