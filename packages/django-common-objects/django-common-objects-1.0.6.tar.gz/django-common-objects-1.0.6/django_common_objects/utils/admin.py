from django.contrib import admin


def get_registered_models():
    models = []
    for x in admin.site._registry:
        models.append(x)
    return models
