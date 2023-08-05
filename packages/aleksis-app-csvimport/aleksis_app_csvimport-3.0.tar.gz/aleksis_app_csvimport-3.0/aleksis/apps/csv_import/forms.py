from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ruamel.yaml import YAML, YAMLError

from aleksis.apps.csv_import.models import ImportTemplate
from aleksis.core.models import SchoolTerm


class CSVUploadForm(forms.Form):
    csv = forms.FileField(label=_("CSV file"))
    school_term = forms.ModelChoiceField(
        queryset=SchoolTerm.objects.all(),
        label=_("Related school term"),
    )
    template = forms.ModelChoiceField(
        queryset=ImportTemplate.objects.all(), label=_("Import template")
    )

    def __init__(self, *args, **kwargs):
        try:
            school_terms = SchoolTerm.objects.on_day(timezone.now().date())
            kwargs["initial"] = {"school_term": school_terms[0] if school_terms.exists() else None}
        except SchoolTerm.DoesNotExist:
            pass
        super().__init__(*args, **kwargs)


class ImportTemplateUploadForm(forms.Form):
    template = forms.FileField(
        label=_("CSV template"), validators=[FileExtensionValidator(["yml", "yaml"])]
    )

    def clean_template(self):
        """Check if the template is a valid YAML file."""
        file = self.cleaned_data["template"]
        try:
            yaml = YAML(typ="safe")
            template_defs = yaml.load(file)

            default_template_names = ImportTemplate.objects.filter(from_default=True).values_list(
                "name", flat=True
            )
            if set(template_defs.keys()) & set(default_template_names):
                raise ValidationError(
                    _("You cannot import a template with the same name as a default template.")
                )
            return template_defs
        except YAMLError as e:
            raise ValidationError(_("Invalid YAML file uploaded: \n {}").format(e))
