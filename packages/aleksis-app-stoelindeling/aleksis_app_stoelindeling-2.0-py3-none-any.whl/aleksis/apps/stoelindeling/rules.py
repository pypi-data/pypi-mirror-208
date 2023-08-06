from rules import add_perm

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models import SeatingPlan
from .util.perms import (
    is_group_owner,
    is_group_owner_of_any_group,
    is_plan_child_group_owner,
    is_plan_group_owner,
)

# View seating plan list
view_seatingplans_predicate = has_person & (
    has_global_perm("stoelindeling.view_seatingplan")
    | has_global_perm("stoelindeling.add_seatingplan")
    | has_any_object("stoelindeling.view_seatingplan", SeatingPlan)
)
add_perm("stoelindeling.view_seatingplans_rule", view_seatingplans_predicate)

# View seating plan
view_seatingplan_predicate = has_person & (
    has_global_perm("stoelindeling.view_seatingplan")
    | has_object_perm("stoelindeling.view_seatingplan")
    | is_plan_group_owner
    | is_plan_child_group_owner
)
add_perm("stoelindeling.view_seatingplan_rule", view_seatingplan_predicate)

#
view_seatingplan_for_group_predicate = has_person & (
    has_global_perm("stoelindeling.view_seatingplan") | is_group_owner
)
add_perm("stoelindeling.view_seatingplan_for_group_rule", view_seatingplan_for_group_predicate)

# Add seating plan
create_seatingplan_predicate = has_person & (
    has_global_perm("stoelindeling.add_seatingplan") | is_group_owner_of_any_group
)
add_perm("stoelindeling.create_seatingplan_rule", create_seatingplan_predicate)

# Copy seating plan
copy_seatingplan_for_group_predicate = view_seatingplan_for_group_predicate & (
    create_seatingplan_predicate | is_plan_group_owner
)
add_perm("stoelindeling.copy_seatingplan_for_group_rule", copy_seatingplan_for_group_predicate)

# Copy seating plan
copy_seatingplan_predicate = view_seatingplan_predicate
add_perm("stoelindeling.copy_seatingplan_rule", copy_seatingplan_predicate)

# Edit seating plan
edit_seatingplan_predicate = view_seatingplan_predicate & (
    has_global_perm("stoelindeling.change_seatingplan")
    | is_plan_group_owner
    | has_object_perm("stoelindeling.change_seatingplan")
)
add_perm("stoelindeling.edit_seatingplan_rule", edit_seatingplan_predicate)

# Delete seating plan
delete_seatingplan_predicate = view_seatingplan_predicate & (
    has_global_perm("stoelindeling.delete_seatingplan")
    | is_plan_group_owner
    | has_object_perm("stoelindeling.delete_seatingplan")
)
add_perm("stoelindeling.delete_seatingplan_rule", delete_seatingplan_predicate)
