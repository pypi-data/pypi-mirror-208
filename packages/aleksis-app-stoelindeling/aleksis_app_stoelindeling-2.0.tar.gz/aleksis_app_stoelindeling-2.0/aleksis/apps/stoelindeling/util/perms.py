from django.db.models import Q

from guardian.shortcuts import get_objects_for_user
from rules import predicate

from aleksis.core.models import Group, Person

from ..models import SeatingPlan


@predicate
def is_group_owner_of_any_group(user) -> bool:
    """Predicate which checks if the user is a owner of any group."""
    return user.person.owner_of.all().exists()


@predicate
def is_group_owner(user, group: Group) -> bool:
    """Predicate which checks if the user is a owner of the group."""
    if not isinstance(group, Group):
        return False
    return user.person in group.owners.all()


@predicate
def is_plan_group_owner(user, seating_plan: SeatingPlan) -> bool:
    """Predicate which checks if the user is a owner of the seating plan's group."""
    if not isinstance(seating_plan, SeatingPlan):
        return False
    return user.person in seating_plan.group.owners.all()


@predicate
def is_plan_child_group_owner(user, seating_plan: SeatingPlan) -> bool:
    """Predicate which checks if the user is an owner of the seating plan's child groups."""
    if not isinstance(seating_plan, SeatingPlan):
        return False
    return user.person in Person.objects.filter(owner_of__in=seating_plan.group.child_groups.all())


def get_allowed_seating_plans(user):
    """Get all seating plans the user is allowed to see."""
    if not user.has_perm("stoelindeling.view_seatingplan"):
        qs = SeatingPlan.objects.filter(
            Q(
                pk__in=get_objects_for_user(
                    user, "stoelindeling.view_seatingplan", SeatingPlan
                ).values_list("pk", flat=True)
            )
            | Q(group__owners=user.person)
        )
        return qs

    return SeatingPlan.objects.all()
