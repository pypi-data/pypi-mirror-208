from django.utils.translation import gettext as _

from material import Fieldset

from aleksis.core.forms import AnnouncementForm, EditGroupForm

AnnouncementForm.add_node_to_layout(Fieldset(_("Options for timetables"), "show_in_timetables"))
EditGroupForm.add_node_to_layout(Fieldset(_("Optional data for timetables"), "subject_id"))
