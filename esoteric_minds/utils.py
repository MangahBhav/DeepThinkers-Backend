from django.contrib import admin
from bson import ObjectId
from django.forms import ModelForm


class BaseModelAdmin(admin.ModelAdmin):
    actions = ['delete_selected']

    @admin.action(description='Delete selected items')
    def delete_selected(self, request, queryset):
        selected_id_list = request.POST.getlist('_selected_action')
        request.POST._mutable = True
        request.POST['_selected_action'] = list(map(lambda x: ObjectId(x), selected_id_list))
        queryset = self.model.objects.filter(_id__in=request.POST['_selected_action'])
        queryset.delete()


class BaseModelForm(ModelForm):
    def clean(self):

        super().clean()