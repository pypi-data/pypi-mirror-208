from django.urls import path

from .apps import get_app_label
from .preview import *

app_name = get_app_label()

urlpatterns = [

    # path(
    #    "add/<slug:content_type_app_name>/<slug:content_type_model_name>/<int:parent_page_id>/preview/",
    #    PreviewOnCreate.as_view(),
    #    name="preview_on_add",
    # ),

    path(
        "<str:pk>/edit/preview/",
        PreviewOnEdit.as_view(),
        name="preview_on_edit",
    ),

]
