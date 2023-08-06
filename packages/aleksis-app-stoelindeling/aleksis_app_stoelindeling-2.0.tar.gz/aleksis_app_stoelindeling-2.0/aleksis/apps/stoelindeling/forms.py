from django import forms
from django.utils.translation import gettext as _

from django_select2.forms import ModelSelect2Widget
from material import Layout, Row

from aleksis.core.mixins import ExtensibleForm
from aleksis.core.models import Group

from .models import Seat, SeatingPlan


class SeatingPlanCreateForm(forms.ModelForm):
    layout = Layout(
        Row(
            "group",
            "subject",
            "room",
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        qs = Group.objects.all()
        if not self.request.user.has_perm("stoelindeling.add_seatingplan"):
            qs = qs.filter(owners=self.request.user.person)

        self.fields["group"].queryset = qs

    def clean(self):
        cleaned_data = super().clean()
        if (
            cleaned_data["group"].subject
            and cleaned_data["subject"]
            and cleaned_data["group"].subject != cleaned_data["subject"]
        ):
            raise forms.ValidationError(
                _(
                    "The group you selected has a fixed subject ({}). "
                    "You are not allowed to use another subject than it."
                ).format(cleaned_data["group"].subject)
            )
        return cleaned_data

    class Meta:
        model = SeatingPlan
        fields = ["group", "subject", "room"]
        widgets = {
            "group": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "subject": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "room": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }


class SeatingPlanCopyForm(forms.ModelForm):
    layout = Layout(
        Row(
            "room",
            "group",
            "subject",
        )
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        self.fields["room"].disabled = True

        qs = Group.objects.filter(parent_groups=self.instance.group)
        if not self.request.user.has_perm("stoelindeling.add_seatingplan"):
            qs = qs.filter(owners=self.request.user.person)

        self.fields["group"].queryset = qs

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["group"] == self.instance.group:
            raise forms.ValidationError(_("Group cannot be the same as the original."))
        if (
            cleaned_data["group"].subject
            and cleaned_data["subject"]
            and cleaned_data["group"].subject != cleaned_data["subject"]
        ):
            raise forms.ValidationError(
                _(
                    "The group you selected has a fixed subject ({}). "
                    "You are not allowed to use another subject than it."
                ).format(cleaned_data["group"].subject)
            )
        return cleaned_data

    class Meta:
        model = SeatingPlan
        fields = ["room", "group", "subject"]
        widgets = {
            "group": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "subject": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }


class SeatingPlanForm(forms.ModelForm):
    layout = Layout(
        Row(
            "subject",
            "room",
        )
    )

    class Meta:
        model = SeatingPlan
        fields = ["subject", "room"]
        widgets = {
            "subject": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "room": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }


class SeatForm(ExtensibleForm):
    pk = forms.IntegerField(
        widget=forms.HiddenInput(attrs={"class": "pk-input"}),
    )
    x = forms.IntegerField(initial=0, widget=forms.HiddenInput(attrs={"class": "x-input"}))
    y = forms.IntegerField(initial=0, widget=forms.HiddenInput(attrs={"class": "y-input"}))
    seated = forms.BooleanField(
        initial=False, widget=forms.HiddenInput(attrs={"class": "seated-input"}), required=False
    )

    class Meta:
        model = Seat
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.seat = self.initial["seat"]


SeatFormSet = forms.formset_factory(form=SeatForm, max_num=0, extra=0)
