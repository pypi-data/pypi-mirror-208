from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView, ListView

from django_tables2 import SingleTableMixin
from rules.contrib.views import PermissionRequiredMixin, permission_required

from aleksis.core.util.celery_progress import render_progress_page

from .forms import CSVUploadForm, ImportTemplateUploadForm
from .models import ImportJob, ImportTemplate
from .tables import ImportTemplateTable
from .tasks import import_csv


@permission_required("csv_import.import_data_rule")
def csv_import(request: HttpRequest) -> HttpResponse:
    context = {}

    upload_form = CSVUploadForm()

    if request.method == "POST":
        upload_form = CSVUploadForm(request.POST, request.FILES)

        if upload_form.is_valid():
            import_job = ImportJob(
                school_term=upload_form.cleaned_data["school_term"],
                template=upload_form.cleaned_data["template"],
                data_file=request.FILES["csv"],
            )
            import_job.save()

            result = import_csv.delay(
                import_job.pk,
            )

            return render_progress_page(
                request,
                result,
                title=_("Progress: Import data from CSV"),
                progress_title=_("Import objects …"),
                success_message=_("The import was done successfully."),
                error_message=_("There was a problem while importing data."),
                back_url=reverse("csv_import"),
            )

    context["upload_form"] = upload_form

    return render(request, "csv_import/csv_import.html", context)


class ImportTemplateListView(PermissionRequiredMixin, SingleTableMixin, ListView):
    """Table of all school terms."""

    model = ImportTemplate
    table_class = ImportTemplateTable
    permission_required = "csv_import.view_importtemplate_rule"
    template_name = "csv_import/import_template/list.html"


class ImportTemplateUploadView(PermissionRequiredMixin, FormView):
    form_class = ImportTemplateUploadForm
    permission_required = "csv_import.upload_importtemplate_rule"
    template_name = "csv_import/import_template/upload.html"

    def form_valid(self, form):
        template_defs = form.cleaned_data["template"]
        try:
            ImportTemplate.update_or_create_templates(template_defs)
        except Exception as e:
            messages.error(
                self.request, _("The import of the import templates failed: \n {}").format(e)
            )
            return self.form_invalid(form)
        messages.success(self.request, _("The import of the import templates was successful."))
        return redirect("import_templates")
