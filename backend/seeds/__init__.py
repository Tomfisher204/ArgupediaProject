from .seed_users import seed_users
from .seed_argument_themes import seed_argument_themes
from .seed_argument_schemes import seed_argument_schemes
from .seed_arguments import seed_arguments
from .seed_critical_questions import seed_critical_questions
from .seed_argument_links import seed_argument_links

def seed_all(test=False):
    seed_users(test=test)
    seed_argument_themes(test=test)
    seed_argument_schemes(test=test)
    seed_arguments(test=test)
    seed_critical_questions(test=test)
    seed_argument_links(test=test)