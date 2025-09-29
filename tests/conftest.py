import pytest
from django.core.management import call_command
from django.conf import settings


@pytest.fixture(scope="session", autouse=True)
def load_fixtures(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("loaddata", "accounts/fixtures/users.json")
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES_EXCEPTIONS = True
    # Test host
    if not hasattr(settings, "EMAIL_HOST_USER"):
        settings.EMAIL_HOST_USER = "test@yourdomain.com"
