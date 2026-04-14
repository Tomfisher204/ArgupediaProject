from backend.models import Argument
from django.db.models import Count, Q

ALPHA = 0.1

def _compute_is_winning(argument):
    """Computes the winning state of an argument based on its children."""
    counts = argument.child_links.aggregate(
        ws=Count("id", filter=Q(attacking=False, child_argument__is_winning=True)),
        wa=Count("id", filter=Q(attacking=True, child_argument__is_winning=True)),
        ls=Count("id", filter=Q(attacking=False, child_argument__is_winning=False)),
        la=Count("id", filter=Q(attacking=True, child_argument__is_winning=False)),
    )
    total_args = counts['ws'] + counts['la'] + counts['wa'] + counts['ls']
    if total_args == 0:
        return True
    lhs = counts['ws'] + counts['la'] / 2
    rhs = counts['wa'] + counts['ls'] / 2
    margin = ALPHA * total_args
    if lhs > rhs + margin:
        return True
    if rhs > lhs + margin:
        return False
    return None

def _evaluate_single(argument):
    """Evaluates and updates the winning state of a single argument returning true if the argument changes."""
    new_state = _compute_is_winning(argument)
    if new_state == argument.is_winning:
        return False
    argument.is_winning = new_state
    argument.save(update_fields=["is_winning"])
    return True

def evaluate_and_propagate(argument):
    """Evaluates an argument and propagates changes up the graph it has been added to."""
    visited: set[int] = set()
    queue: list[Argument] = [argument]
    while queue:
        current = queue.pop()
        if current.id in visited:
            continue
        visited.add(current.id)
        changed = _evaluate_single(current)
        if not changed:
            continue
        parents = (Argument.objects.filter(child_links__child_argument=current).exclude(id__in=visited).distinct())
        queue.extend(parents)