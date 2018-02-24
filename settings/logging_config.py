from django.utils.log import DEFAULT_LOGGING


def get_config(log_dir, log_level='debug'):
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                # exact format is not important, this is the minimum information
                'format': (
                    "[%(asctime)s] %(levelname)s [%(name)s:"
                    " %(funcName)s: %(lineno)s] %(message)s"
                )
            },
            'django.server': DEFAULT_LOGGING['formatters']['django.server'],
        },
        'handlers': {
            # console logs to stderr
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            # Add Handler for Sentry for `warning` and above
            'sentry': {
                'level': 'WARNING',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
            'django.server': DEFAULT_LOGGING['handlers']['django.server'],
        },
        'loggers': {
            # default for all undefined Python modules
            '': {
                'level': 'WARNING',
                'handlers': ['console', 'sentry'],
            },
            # Our application code
            'app': {
                'level': log_level,
                'handlers': ['console', 'sentry'],
                # Avoid double logging because of root logger
                'propagate': False,
            },
            # Prevent noisy modules from logging to Sentry
            'requests': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False,
            },
            # Default runserver request logging
            'django.server': DEFAULT_LOGGING['loggers']['django.server'],
            'django.db.backends': {
                'level': log_level,
                'handlers': ['console'],
            }
        },
    }
