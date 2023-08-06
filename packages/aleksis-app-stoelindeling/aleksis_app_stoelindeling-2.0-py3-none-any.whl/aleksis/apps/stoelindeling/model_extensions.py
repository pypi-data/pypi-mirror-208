from typing import Union

from django.apps import apps

from aleksis.apps.chronos.models import Subject
from aleksis.apps.stoelindeling.models import SeatingPlan
from aleksis.core.models import Group, Room


@Group.method
def get_seating_plan(self, room: Room, subject: Subject = None) -> Union[SeatingPlan, None]:
    """Find a seating plan for a group."""
    qs = SeatingPlan.objects.filter(group=self, room=room)
    if subject:
        qs = qs.filter(subject=subject)
    if qs.exists():
        return qs.first()

    qs = SeatingPlan.objects.filter(group=self, room=room)
    if qs.exists():
        return qs.first()

    qs = SeatingPlan.objects.filter(group__child_groups=self, room=room)
    if qs.exists():
        return qs.first()

    return None


if apps.is_installed("aleksis.apps.alsijil"):
    from aleksis.apps.alsijil.models import Event, ExtraLesson, LessonPeriod

    def seating_plan_lesson_period(self):
        """Get the seating plan for a specific lesson period."""
        if self.get_groups().count() == 1:
            return self.get_groups().all()[0].get_seating_plan(self.get_room(), self.get_subject())
        return None

    LessonPeriod.property_(seating_plan_lesson_period, name="seating_plan")

    def seating_plan_extra_lesson(self):
        """Get the seating plan for an extra lesson."""
        if self.groups.count() == 1:
            return self.groups.all()[0].get_seating_plan(self.room, self.subject)
        return None

    ExtraLesson.property_(seating_plan_extra_lesson, name="seating_plan")

    def seating_plan_event(self):
        """Get the seating plan for an event."""
        if self.groups.count() == 1 and self.rooms.count() == 1:
            return self.groups.all()[0].get_seating_plan(self.rooms.all()[0])
        return None

    Event.property_(seating_plan_event, name="seating_plan")
