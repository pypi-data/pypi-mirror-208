from django import forms

from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from material import Layout

from .models import AutomaticPlan, LessonSubstitution, SupervisionSubstitution
from .util.chronos_helpers import get_teachers


class LessonSubstitutionForm(forms.ModelForm):
    """Form to manage substitutions."""

    class Meta:
        model = LessonSubstitution
        fields = ["subject", "teachers", "room", "cancelled", "comment"]
        widgets = {
            "teachers": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields["teachers"].queryset = get_teachers(request.user)


class SupervisionSubstitutionForm(forms.ModelForm):
    """Form to manage supervisions substitutions."""

    class Meta:
        model = SupervisionSubstitution
        fields = ["teacher"]
        widgets = {
            "teacher": ModelSelect2Widget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields["teacher"].queryset = get_teachers(request.user)


class AutomaticPlanForm(forms.ModelForm):
    layout = Layout("slug", "name", "number_of_days", "show_header_box")

    class Meta:
        model = AutomaticPlan
        fields = ["slug", "name", "number_of_days", "show_header_box"]
