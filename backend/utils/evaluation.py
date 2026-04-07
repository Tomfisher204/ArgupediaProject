"""
The formula for determining whether an argument is winning, losing,
or undecided is as follows:

Let:
WS = count of winning supporters
LA = count of losing attackers
WA = count of winning attackers
LS = count of losing supporters

TotalArgs = WS + LA + WA + LS
ALPHA = constant

Scores:
LHS = WS + LA/2
RHS = WA + LS/2

Decision rule:
Winning if LHS > RHS + ALPHA * TotalArgs
Losing if RHS > LHS + ALPHA * TotalArgs
Otherwise undecided (None)

An argument with no decisive children defaults to winning.
"""

from backend.models import Argument

ALPHA = 0.1

def _compute_is_winning(argument) -> bool | None:
    children = (argument.child_links.select_related("child_argument").only("attacking", "child_argument__is_winning"))
    
    ws = la = wa = ls = 0

    for link in children:
        child_state = link.child_argument.is_winning
        if child_state is None:
            continue
        if link.attacking:
            if child_state:
                wa += 1
            else:
                la += 1
        else:
            if child_state:
                ws += 1
            else:
                ls += 1
    total_args = ws + la + wa + ls

    if total_args == 0:
        return True

    lhs = ws + la / 2
    rhs = wa + ls / 2
    margin = ALPHA * total_args

    if lhs > rhs + margin:
        return True

    if rhs > lhs + margin:
        return False

    return None


def _evaluate_single(argument) -> bool:
    new_state = _compute_is_winning(argument)
    if new_state == argument.is_winning:
        return False
    argument.is_winning = new_state
    argument.save(update_fields=["is_winning"])
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