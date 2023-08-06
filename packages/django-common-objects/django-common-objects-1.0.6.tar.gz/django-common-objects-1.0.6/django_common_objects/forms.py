import json

from django import forms
from .choices import CategoryModelChoices, TagModelChoices, FieldConfigModelChoices
from .models import CommonCategory, CommonFieldConfig, CommonTag
from .utils import foreign_key


class FieldConfigForm(forms.ModelForm):
    model = forms.ChoiceField(choices=FieldConfigModelChoices.choices, label="所属模型", required=True)


class CategoryForm(forms.ModelForm):
    model = forms.ChoiceField(choices=CategoryModelChoices.choices, label="所属模型", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance: CommonCategory = self.instance
        if instance.id:
            self.fields['parent'].queryset = CommonCategory.objects.filter(
                model=instance.model, user=instance.user
            ).exclude(id__in=foreign_key.get_related_object_ids(instance))
        else:
            fields = CommonFieldConfig.objects.filter(model=instance._meta.label).values_list('key', 'value')
            self.fields['config'].initial = {k: v for k, v in fields}

    def clean(self):
        cleaned_data = super().clean()
        model = cleaned_data.get('model')
        parent = cleaned_data.get('parent')
        if model and parent and model != parent.model:
            raise forms.ValidationError('所属模型不一致')
        return cleaned_data

    class Meta:
        model = CommonCategory
        fields = "__all__"


class TagForm(forms.ModelForm):
    model = forms.ChoiceField(choices=TagModelChoices.choices, label="所属模型", required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance: CommonTag = self.instance
        if not instance.id:
            fields = CommonFieldConfig.objects.filter(model=instance._meta.label).values_list('key', 'value')
            self.fields['config'].initial = {k: v for k, v in fields}

    class Meta:
        model = CommonTag
        fields = "__all__"
