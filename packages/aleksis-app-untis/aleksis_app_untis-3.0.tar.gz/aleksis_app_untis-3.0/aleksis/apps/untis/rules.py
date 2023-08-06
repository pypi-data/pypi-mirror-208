from rules import add_perm

from aleksis.core.util.predicates import has_global_perm, has_person

assign_subjects_to_groups_predicate = has_person & has_global_perm(
    "untis.assign_subjects_to_groups"
)
add_perm("untis.assign_subjects_to_groups_rule", assign_subjects_to_groups_predicate)
