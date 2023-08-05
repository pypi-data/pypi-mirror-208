from django.urls import path

from . import views

urlpatterns = [
    path("import/", views.csv_import, name="csv_import"),
    path("templates/", views.ImportTemplateListView.as_view(), name="import_templates"),
    path(
        "templates/upload/", views.ImportTemplateUploadView.as_view(), name="upload_import_template"
    ),
]
