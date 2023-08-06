# _*_coding:utf-8_*_
from django.conf import settings
from django.conf.urls import static
from django.conf.urls import url
from django.urls import re_path

from .apis.resource_image_list import UploadImageList
from .apis.resource_file_list import UploadFileList
from .apis.resource_upload_file import UploadFile
from .apis.resource_upload_image import UploadImage
from .apis.resource_upload_video import UploadVideo

# 应用名称
app_name = 'resource'

urlpatterns = [
    url(r'upload_file/?$', UploadFile.as_view(), name='st_upload_file'),  # 文件上传
    url(r'upload_image/?$', UploadImage.as_view(), name='st_upload_image'),  # 图片上传
    url(r'upload_video/?$', UploadVideo.as_view(), name='st_upload_image'),  # 图片上传

    url(r'image_list/?$', UploadImageList.as_view(), name='st_upload_image'),  # 图片上传
    url(r'file_list/?$', UploadFileList.as_view(), name='st_file_image'),  #
    # re_path(r'^_upload_image/?$', UploadImage.as_view(), ),

]
