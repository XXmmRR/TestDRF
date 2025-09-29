import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.fixture
def api_client():
    return Client()


@pytest.mark.django_db
def test_user_creation():
    assert User.objects.count() == 2
    user = User.objects.get(email="testuser@example.com")
    assert user.full_name == "Тестовый Пользователь"


@pytest.mark.django_db
def test_user_is_not_staff():
    user = User.objects.get(email="testuser@example.com")
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_admin_is_superuser():
    admin = User.objects.get(email="admin@example.com")
    assert admin.is_staff
    assert admin.is_superuser


@pytest.mark.django_db
def test_user_string_representation():
    user = User.objects.get(email="testuser@example.com")
    assert str(user) == "testuser@example.com"
