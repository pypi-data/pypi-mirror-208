from django.utils.translation import gettext as _

from jsonstore import CharField

from aleksis.core.mixins import ExtensibleModel

for model in ExtensibleModel.__subclasses__():
    model.field(import_ref_csv=CharField(verbose_name=_("CSV import reference"), blank=True))
