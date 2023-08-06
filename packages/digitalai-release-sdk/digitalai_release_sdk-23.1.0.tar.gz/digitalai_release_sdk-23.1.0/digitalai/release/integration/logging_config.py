import sys
LOGGING_CONFIG = ({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-7s [%(filename)s:%(lineno)d] - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': sys.stdout
        }
    },
    'loggers': {
        'Digitalai': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        },
        '__main__': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
        'propagate': False
    }
})
