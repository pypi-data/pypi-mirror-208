from django.db import models
from django.utils.translation import gettext_lazy as _

from aleksis.apps.chronos.models import Subject
from aleksis.apps.stoelindeling.managers import SeatManager, SeatQuerySet
from aleksis.core.mixins import ExtensibleModel
from aleksis.core.models import Group, Person, Room


class SeatingPlan(ExtensibleModel):
    """Seating plan model."""

    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_("Group"))
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, verbose_name=_("Subject"), blank=True, null=True
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name=_("Room"))

    def get_all_seats(self) -> SeatQuerySet:
        """Get  seats for all persons in the group."""
        missing_seats = (
            Person.objects.filter(member_of=self.group).exclude(seats__plan=self).distinct()
        )
        seats_to_create = []
        for person in missing_seats:
            seat = Seat(person=person, plan=self)
            seats_to_create.append(seat)
        Seat.objects.bulk_create(seats_to_create)
        return self.seats.all()

    class Meta:
        verbose_name = _("Seating plan")
        verbose_name_plural = _("Seating plans")
        constraints = [
            models.UniqueConstraint(
                fields=["group", "subject", "room"], name="unique_group_subject_room"
            )
        ]

    def __str__(self):
        return f"{self.group} - {self.subject} - {self.room}"


class Seat(ExtensibleModel):
    """Seat model."""

    objects = SeatManager.from_queryset(SeatQuerySet)()

    plan = models.ForeignKey(
        SeatingPlan, on_delete=models.CASCADE, verbose_name=_("Seating plan"), related_name="seats"
    )

    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name=_("Person"), related_name="seats"
    )
    x = models.IntegerField(verbose_name=_("X position"), default=0)
    y = models.IntegerField(verbose_name=_("Y position"), default=0)

    seated = models.BooleanField(verbose_name=_("Seated"), default=False)

    class Meta:
        verbose_name = _("Seat")
        verbose_name_plural = _("Seats")
        constraints = [
            models.UniqueConstraint(fields=["plan", "person"], name="unique_plan_person"),
        ]
