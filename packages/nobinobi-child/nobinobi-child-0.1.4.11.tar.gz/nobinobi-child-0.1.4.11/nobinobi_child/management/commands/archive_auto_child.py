#  Copyright (C) 2022 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from django.contrib.auth import get_user_model
from django.core.handlers.base import logger
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from nobinobi_child.models import Child

User = get_user_model()


class Command(BaseCommand):
    help = "Command for archive auto child"

    def handle(self, *args, **options):
        logger.info(_("*** Launch command << archive child automatically >> ***"))

        # we collect all children who have an end date and a progress status
        children = Child.objects.filter(date_end_child__isnull=False, status=Child.STATUS.in_progress)

        for child in children:
            now = timezone.localdate()
            # if today is greater than or equal to the current date
            if now >= child.date_end_child:
                # we set its status to "archived
                child.status = Child.STATUS.archived
                # the archiving is recorded in the log
                child.childtrackinglog_set.create(
                    user=User.objects.filter(Q(username__iexact="webmaster") | Q(username__iexact="Admin")).first(),
                    body=_("The child was archived on {}.").format(child.date_end_child)
                )
                child.save()
                logger.info(_("The child {} has been archived.").format(child))

            logger.info(_("*** End command << archive child automatically >> ***"))
