LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False

REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}

DATETIME_FORMAT = "Y-m-d H:i:s"
DATE_FORMAT = "Y m d"


def rewrite_to(module):
    if not isinstance(module, dict):
        module = module.__dict__
    for k, v in globals().items():
        if k.isupper() and not k.startswith('__'):
            module[k] = v
