"""
The formula for determining whether an argument is winning or losing is as follows:

An argument is winning iff:
    (WS + LA/2) > (WA + LS/2) + ALPHA * TotalArgs

Where:
    WS = count of winning supporters (child links with attacking=False, is_winning=True)
    LA = count of losing attackers (child links with attacking=True,  is_winning=False)
    WA = count of winning attackers (child links with attacking=True,  is_winning=True)
    LS = count of losing  supporters (child links with attacking=False, is_winning=False)
    TotalArgs = WS + LA + WA + LS  (total direct children)
    ALPHA = dampening constant so TotalArgs does not dominate the RHS

An argument with no children defaults to winning (nothing is attacking it).
"""

from backend.models import Argument

ALPHA = 0.1

def _compute_is_winning(argument) -> bool:
    children = (
        argument.child_links
        .select_related('child_argument')
        .only('attacking', 'child_argument__is_winning')
    )
    ws = la = wa = ls = 0
    for link in children:
        child_winning = link.child_argument.is_winning
        if link.attacking:
            if child_winning:
                wa += 1
            else:
                la += 1
        else:
            if child_winning:
                ws += 1
            else:
                ls += 1
    total_args = ws + la + wa + ls
    if total_args == 0:
        return True
    lhs = ws + la / 2
    rhs = wa + ls / 2 + ALPHA * total_args
    return lhs > rhs


def _evaluate_single(argument) -> bool:
    new_winning = _compute_is_winning(argument)
    if new_winning == argument.is_winning:
        return False
    argument.is_winning = new_winning
    argument.save(update_fields=['is_winning'])
    return True


def evaluate_and_propagate(argument) -> None:
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
        parents = (
            Argument.objects
            .filter(child_links__child_argument=current)
            .exclude(id__in=visited)
            .distinct()
        )
        queue.extend(parents)