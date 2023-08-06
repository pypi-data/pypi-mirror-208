from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView

from xj_resource.services.resource_file_service import ResourceFileService
from ..models import *
from ..utils.model_handle import util_response, only_filed_handle, parse_model


class UploadFileList(APIView):
    # 文件列表
    def get(self, request):
        params = request.query_params.copy()
        limit = params.pop('limit', 20)
        page = params.pop('page', 20)
        params = only_filed_handle(params, {
            "title": "title__contains",
            "filename": "filename_contains",
            "md5": "md5",
            "user_id": "user_id"
        }, None)
        resource_serv, error_text = ResourceFileService.get_list(params)
        if error_text:
            return Response({'err': 6002, 'msg': error_text, })
        return util_response(data=resource_serv)

