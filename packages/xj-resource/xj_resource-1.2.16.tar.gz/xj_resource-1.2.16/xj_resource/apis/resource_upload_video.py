from rest_framework.response import Response
from rest_framework.views import APIView

from xj_user.services.user_service import UserService
from ..services.resource_upload_service import ResourceUploadService
from ..services.resource_video_service import ResourceVideoService


class UploadVideo(APIView):
    def post(self, request):
        # ========== 一、检查：验证权限 ==========
        # TODO 以后改成装饰器，by sieyoo
        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return Response({'err': 6001, 'msg': '缺少Token', })
        user_serv, error_text = UserService.check_token(token)
        if error_text:
            return Response({'err': 6002, 'msg': error_text, })
        user_id = user_serv.get('user_id', None)
        if not user_id:
            return Response({'err': 7001, 'msg': "用户不存在", })

        # ========== 二、检查：必填性 ==========
        # 对应postman的Body的key=file，value=上传文件的名称 watermelonhh.jpg
        input_file = request.FILES.get("video")
        title = request.POST.get("title")
        group_id = request.POST.get('group_id', None)
        print("> UploadImage: user_id, title, group_id:", user_id, title, group_id)
        if input_file is None:
            return Response({'err': 2001, 'msg': '未选择上传图片', 'tip': '未选择上传图片', })

        # ========== 三、检查：内容的准确性 ==========
        upload_serv = ResourceUploadService(upload_type='video')
        file_info, error_text = upload_serv.init(input_file, by_month=True, user_id=user_id, title=title,
                                                 group_id=group_id, limit_size=None)
        if error_text:
            return Response({'err': 4005, 'msg': error_text, })

        # 写入磁盘
        upload_serv.write(target='disk')
        # print("> UploadImage: upload_serv:", upload_serv)

        # 写入数据库
        video_instance, error_text = ResourceVideoService.add(params=file_info)
        print("> UploadVideo: video_instance:", video_instance, type(video_instance))
        if error_text:
            return Response({'err': 4006, 'msg': error_text, })
        if video_instance:
            file_info['id'] = video_instance.id

        video_dict, error_text = ResourceVideoService.get(video_id=video_instance.id)
        if error_text:
            return Response({'err': 4007, 'msg': error_text, })

        return Response({'err': 0, 'msg': 'OK', 'data': video_dict})
