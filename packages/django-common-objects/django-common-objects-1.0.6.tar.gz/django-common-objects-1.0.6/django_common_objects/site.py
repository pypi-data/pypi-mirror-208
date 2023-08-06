from collections import OrderedDict
from django.contrib import admin
from django.conf import settings


class CommonAdminSite(admin.AdminSite):

    def __init__(self, *args, **kwargs):
        super(CommonAdminSite, self).__init__(*args, **kwargs)
        self._registry = OrderedDict()
        self.apps_order_list = getattr(settings, 'APPS_ORDER_LIST', [])
        self.apps_order_dict = {app: index for index, app in enumerate(self.apps_order_list)}

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request, app_label)
        app_list = sorted(app_dict.values(), key=lambda x: self.apps_order_dict.get(x['app_label'], 1))
        # for app in app_list:
        #     app["models"].sort(key=lambda x: x["name"])
        return app_list
