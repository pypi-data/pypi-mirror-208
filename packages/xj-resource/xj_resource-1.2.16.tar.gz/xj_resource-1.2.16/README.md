# 模块介绍

## 1.资源上传

1.文件上传

2.图片上传

# SQL

```mysql
CREATE TABLE `resource_file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `title` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `url` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '保存路径',
  `filename` varchar(80) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '文件名称',
  `format` varchar(10) COLLATE utf8_unicode_ci NOT NULL COMMENT '文件后缀',
  `thumb` varchar(255) COLLATE utf8_unicode_ci DEFAULT '' COMMENT '缩略图位置',
  `md5` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `snapshot` json DEFAULT NULL COMMENT '文件快照',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='文件上传表';


CREATE TABLE `resource_file_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `file_id` int(11) NOT NULL COMMENT '图片ID',
  `source_id` int(11) NOT NULL COMMENT '来源表 关联ID',
  `source_table` varchar(255) COLLATE utf8_unicode_ci NOT NULL COMMENT '来源表表明',
  `price` int(10) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `image_id` (`file_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;


CREATE TABLE `resource_image` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL DEFAULT '0' COMMENT '用户ID',
  `title` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `url` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '保存路径',
  `filename` varchar(80) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '文件名称',
  `format` varchar(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT '文件后缀',
  `thumb` varchar(255) COLLATE utf8_unicode_ci DEFAULT '' COMMENT '缩略图位置',
  `md5` varchar(255) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `snapshot` json DEFAULT NULL COMMENT '文件快照',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='文件上传表';

CREATE TABLE `resource_image_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_id` int(11) NOT NULL COMMENT '图片ID',
  `source_id` int(11) NOT NULL COMMENT '来源表 关联ID',
  `source_table` varchar(255) COLLATE utf8_unicode_ci NOT NULL COMMENT '来源表表明',
  `price` int(10) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `image_id` (`image_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
```



# 配置

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
```

# xj-resource



### 依赖

无



### 配置

- **settings.py**

```python
STATIC_URL = '/static/'  # 配置浏览器访问静态资源的“根路径”

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")  # 不要和 STATICFILES_DIRS 相同，会冲突的 部署django项目需要用到STATIC_ROOT
# 注意：STATIC_ROOT 和 STATICFILES_DIRS 不是同一个东西，只有在这里才是真的 /static/

# 公共的静态文件的文件夹

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "resource"),
    # os.path.join(BASE_DIR, "media")
    # os.path.join(BASE_DIR, "static")

]
```




====================





