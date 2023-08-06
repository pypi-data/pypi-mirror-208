from django.conf import settings
from django.utils.translation import gettext_lazy as _

NOBI_CHILD_CLASSROOM_OBJECT_NAME = getattr(settings, 'NOBI_CHILD_CLASSROOM_OBJECT_NAME', _("Classroom"))
