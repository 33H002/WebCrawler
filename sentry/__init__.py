import os

import sentry_sdk

from config import Base as Config


def init(profile: str, job: str):
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        environment=profile,
        release=os.environ.get('SENTRY_RELEASE'),
        integrations=[]
    )
    sentry_sdk.set_tag('job', job)
