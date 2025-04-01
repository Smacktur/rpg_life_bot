from .phase import router as phase_router
from .quests import router as quests_router
from .insight import router as insight_router
from .reflect import router as reflect_router
from .reminder import router as reminder_router
from .user import router as user_router
from .settings import router as settings_router
from .onboarding import router as onboarding_router
from .buttons import router as buttons_router
from .faq import router as faq_router

__all__ = [
    "phase_router",
    "quests_router",
    "insight_router",
    "reflect_router",
    "reminder_router",
    "user_router",
    "settings_router",
    "onboarding_router",
    "buttons_router",
    "faq_router",
]