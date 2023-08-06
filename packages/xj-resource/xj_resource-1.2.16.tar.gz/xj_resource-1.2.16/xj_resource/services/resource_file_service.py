# coding=utf-8
from django.core.paginator import Paginator

from ..models import ResourceFile


# 用于异常处理
def robust(actual_do):
    def add_robust(*args, **keyargs):
        try:
            return actual_do(*args, **keyargs)
        except Exception as e:
            print(str(e))

    return add_robust


# # 声明序列化，处理处理数据并写入数据
# class UploadImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ResourceImage
#         # 序列化验证检查，检查必填项的字段
#         fields = ['id', 'group', 'group_id', 'user_id', 'title', 'url', 'filename', 'format', 'size', 'thumb', 'md5', 'snapshot',
#                   'counter']
#
#
# class ResourceImageService:
#
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def create(params):
#         serializer = UploadImageSerializer(data=params)
#         if not serializer.is_valid():
#             return None, serializer.errors
#
#         instance = serializer.save()
#         return instance, None


class ResourceFileService:

    def __init__(self):
        pass

    @staticmethod
    def get(file_id):
        image_set = ResourceFile.objects.filter(id=file_id).values(
            "id",
            "group_id",
            "user_id",
            "title",
            "filename",
            "url",
            "format",
            "size",
            "thumb",
            "md5",
            "snapshot",
            "counter",
        ).first()
        if not image_set:
            return None, '数据库找不到图片'
        return image_set, None

    @staticmethod
    def add(params):
        # print("> ResourceImageService create:", params)
        # # 检查MD5是否有历史上传记录，暂不使用，因为目录按月份分组时这些数据变得不稳定
        # md5 = params.get('md5', None)
        # if md5 is None:
        #     return False
        # instance = ResourceImage.objects.filter(md5=md5).first()
        # if instance:
        #     return instance, None

        # sieyoo注，数据写入最好通过显式的方式，这样可以随时修改和扩展复杂的需求，代价是必须和模型一致，另一个好处是开发者加深数据库结构的记忆
        new_params = {
            'group_id': params.get('group_id', None),
            'user_id': params.get('user_id', None),
            'title': params.get('title', None),
            'url': params.get('url', None),
            'filename': params.get('filename', None),
            'format': params.get('format', None),
            'size': params.get('size', None),
            'thumb': params.get('thumb', None),
            'md5': params.get('md5', None),
            'snapshot': params.get('snapshot', None),
            'counter': params.get('counter', 1),
        }
        image_set = ResourceFile(**new_params)
        image_set.save()
        return image_set, None

    @staticmethod
    def get_list(params):
        limit = params.pop('limit', 20)
        page = params.pop('page', 20)
        list_obj = ResourceFile.objects.filter(**params)
        count = list_obj.count()
        list_obj = list_obj.values(
            "id",
            "user_id",
            "title",
            "url",
            "filename",
            "format",
            "thumb",
            "md5",
            "snapshot"
        )
        res_set = Paginator(list_obj, limit).get_page(page)
        page_list = []
        if res_set:
            page_list = list(res_set.object_list)
        print(page_list)
        return {'count': count, 'page': page, 'limit': limit, "list": page_list}, None
