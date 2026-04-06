from .seed_users import seed_users
from .seed_themes import seed_argument_themes
from .seed_schemes import seed_argument_schemes
from .seed_arguments import seed_arguments
from .seed_critical_questions import seed_critical_questions

def seed_all(test=False):
    seed_users(test=test)
    seed_argument_themes(test=test)
    seed_argument_schemes(test=test)
    seed_critical_questions(test=test)
    seed_arguments(test=test)