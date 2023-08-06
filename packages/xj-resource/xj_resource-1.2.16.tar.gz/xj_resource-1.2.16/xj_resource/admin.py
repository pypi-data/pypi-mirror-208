from django.contrib import admin

from config.config import JConfig
from .models import ResourceImage, ResourceImageMap, ResourceFile, ResourceFileMap, ResourceVideo, ResourceVideoMap

# Register your models here.
config = JConfig()
admin.site.site_header = config.get('main', 'app_name', 'msa一体化管理后台')
admin.site.site_title = config.get('main', 'app_name', 'msa一体化管理后台')


# =============================== 图片 ==========================================
class ResourceImageAdmin(admin.ModelAdmin):
    fields = ('id', 'user_id', 'group', 'title', 'url', 'filename', 'format',
              'size', 'thumb', 'md5', 'snapshot', 'created_at', 'updated_at', 'counter')
    list_display = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')
    search_fields = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')
    readonly_fields = ['id']


class ResourceImageMapAdmin(admin.ModelAdmin):
    fields = ('id', 'image_id', 'source_id', 'source_table', 'price',)
    list_display = ('id', 'image_id', 'source_id', 'source_table', 'price',)
    search_fields = ('id', 'image_id', 'source_id', 'source_table', 'price',)


# =============================== 文件 ==========================================
class ResourceFileAdmin(admin.ModelAdmin):
    fields = ('user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot', 'thumb')
    list_display = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')
    search_fields = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')


class ResourceFileMapAdmin(admin.ModelAdmin):
    fields = ('id', 'file_id', 'source_id', 'source_table', 'price',)
    list_display = ('id', 'file_id', 'source_id', 'source_table', 'price',)
    search_fields = ('id', 'file_id', 'source_id', 'source_table', 'price',)


# =============================== 视频 ==========================================
class ResourceVideoAdmin(admin.ModelAdmin):
    fields = ('user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot', 'thumb')
    list_display = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')
    search_fields = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'snapshot')


class ResourceVideoMapAdmin(admin.ModelAdmin):
    fields = ('id', 'video_id', 'source_id', 'source_table', 'price',)
    list_display = ('id', 'video_id', 'source_id', 'source_table', 'price',)
    search_fields = ('id', 'video_id', 'source_id', 'source_table', 'price',)


# =============================== end ==========================================
admin.site.register(ResourceImage, ResourceImageAdmin)
admin.site.register(ResourceImageMap, ResourceImageMapAdmin)

admin.site.register(ResourceFile, ResourceFileAdmin)
admin.site.register(ResourceFileMap, ResourceFileMapAdmin)

admin.site.register(ResourceVideo, ResourceFileAdmin)
admin.site.register(ResourceVideoMap, ResourceVideoMapAdmin)
