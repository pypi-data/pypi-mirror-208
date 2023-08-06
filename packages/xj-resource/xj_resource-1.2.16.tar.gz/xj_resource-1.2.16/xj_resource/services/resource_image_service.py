# coding=utf-8
import os

from rest_framework import serializers

from ..models import ResourceImage


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


class ResourceImageService:

    def __init__(self):
        pass

    @staticmethod
    def get(image_id):
        image_set = ResourceImage.objects.filter(id=image_id).values(
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

        try:
            image_set = ResourceImage(**new_params)
            image_set.save()
        except Exception as e:
            return None, f"""图片保存失败，请检查数据库。 {str(e)} in "{str(e.__traceback__.tb_frame.f_globals["__file__"])}" : Line {str(e.__traceback__.tb_lineno)}"""

        return image_set, None
