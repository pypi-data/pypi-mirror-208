from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView

from django_tables2 import SingleTableView
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.core.decorators import pwa_cache
from aleksis.core.mixins import (
    AdvancedCreateView,
    AdvancedDeleteView,
    AdvancedEditView,
    SuccessNextMixin,
)
from aleksis.core.views import LoginView

from .forms import SeatFormSet, SeatingPlanCopyForm, SeatingPlanCreateForm, SeatingPlanForm
from .models import Seat, SeatingPlan
from .tables import SeatingPlanTable
from .util.perms import get_allowed_seating_plans


@method_decorator(pwa_cache, name="dispatch")
class SeatingPlanListView(PermissionRequiredMixin, SingleTableView):
    """Table of all seating plans."""

    model = SeatingPlan
    table_class = SeatingPlanTable
    permission_required = "stoelindeling.view_seatingplans_rule"
    template_name = "stoelindeling/seating_plan/list.html"

    def get_queryset(self):
        return get_allowed_seating_plans(self.request.user)


@method_decorator(pwa_cache, name="dispatch")
class SeatingPlanDetailView(PermissionRequiredMixin, DetailView):
    """Detail view for seating plans."""

    model = SeatingPlan
    permission_required = "stoelindeling.view_seatingplan_rule"
    template_name = "stoelindeling/seating_plan/view.html"


@method_decorator(never_cache, name="dispatch")
class SeatingPlanCreateView(PermissionRequiredMixin, SuccessNextMixin, AdvancedCreateView):
    """Create view for seating plans."""

    model = SeatingPlan
    form_class = SeatingPlanCreateForm
    permission_required = "stoelindeling.create_seatingplan_rule"
    template_name = "stoelindeling/seating_plan/create.html"
    next_page = "seating_plans"
    success_message = _("The seating plan has been created.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        initial = {}
        if "room" in self.request.GET:
            initial["room"] = self.request.GET["room"]
        if "subject" in self.request.GET:
            initial["subject"] = self.request.GET["subject"]
        if "group" in self.request.GET:
            initial["group"] = self.request.GET["group"]
        kwargs["initial"] = initial
        return kwargs


@method_decorator(never_cache, name="dispatch")
class SeatingPlanEditView(PermissionRequiredMixin, SuccessNextMixin, AdvancedEditView):
    """Edit view for seating plans."""

    model = SeatingPlan
    form_class = SeatingPlanForm
    permission_required = "stoelindeling.edit_seatingplan_rule"
    template_name = "stoelindeling/seating_plan/edit.html"
    success_message = _("The seating plan has been saved.")

    def get_success_url(self):
        return LoginView.get_redirect_url(self) or reverse("seating_plan", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        seats = self.object.get_all_seats()
        context["seats"] = seats
        context["seats_without_position"] = seats.without_position()

        start_grid = seats.build_grid()
        context["start_grid"] = start_grid

        initial = []
        for seat in seats:
            initial.append(
                {
                    "pk": seat.person.pk,
                    "x": seat.x,
                    "y": seat.y,
                    "seat": seat,
                    "seated": seat.seated,
                }
            )

        formset = SeatFormSet(self.request.POST or None, initial=initial, prefix="seats")
        self.formset = formset
        context["formset"] = self.formset

        return context

    def form_valid(self, form):
        context = self.get_context_data()

        if self.formset.is_valid():
            objects_to_update = []
            for form in self.formset:
                new_x = form.cleaned_data["x"]
                new_y = form.cleaned_data["y"]
                new_seated = form.cleaned_data["seated"]
                if form.seat.x != new_x or form.seat.y != new_y or form.seat.seated != new_seated:
                    form.seat.x = new_x
                    form.seat.y = new_y
                    form.seat.seated = new_seated
                    objects_to_update.append(form.seat)
                print(form.seat, new_x, new_y, new_seated)

            Seat.objects.bulk_update(objects_to_update, ["x", "y", "seated"])

            messages.success(self.request, _("The seating plan has been updated."))
            return redirect(self.get_success_url())

        return super().form_invalid(form)


@method_decorator(never_cache, name="dispatch")
class SeatingPlanCopyView(PermissionRequiredMixin, SuccessNextMixin, AdvancedEditView):
    """Copy view for seating plans."""

    model = SeatingPlan
    form_class = SeatingPlanCopyForm
    permission_required = "stoelindeling.copy_seatingplan_rule"
    template_name = "stoelindeling/seating_plan/copy.html"

    def get_success_url(self):
        return reverse("edit_seating_plan", args=[self.new_object.pk])  # FiXME NEXT URL

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        context = self.get_context_data()

        self.new_object = self.object
        self.new_object.pk = None
        self.new_object.group = form.cleaned_data["group"]
        self.new_object.subject = form.cleaned_data["subject"]
        self.new_object.save()

        for seat in self.object.seats.all():
            if seat.person in self.new_object.group.members.all():
                new_seat = seat
                new_seat.pk = None
                new_seat.seating_plan = self.new_object
                new_seat.save()

        messages.success(self.request, _("The seating plan has been copied successfully."))
        return redirect(self.get_success_url())


@method_decorator(never_cache, name="dispatch")
class SeatingPlanDeleteView(
    PermissionRequiredMixin, RevisionMixin, SuccessNextMixin, AdvancedDeleteView
):
    """Delete view for seating plans."""

    model = SeatingPlan
    permission_required = "stoelindeling.delete_seatingplan_rule"
    template_name = "core/pages/delete.html"
    next_page = "seating_plans"
    success_message = _("The seating plan has been deleted.")
