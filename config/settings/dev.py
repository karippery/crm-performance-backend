from .base import *

if DEBUG:

    INSTALLED_APPS += [
        'debug_toolbar',
        'drf_yasg',
    ]

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
