import pytest
from rest_framework import status
from django.urls import reverse
from products.models import Product

PRODUCTS_LIST_URL = reverse("product-list")


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def authenticated_admin_client(api_client, db, django_user_model):
    user = django_user_model.objects.get(email="admin@example.com")
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def product_data():
    """Фикстура для тестовых данных продукта."""
    return {"name": "Тестовый Продукт", "price": 99.99, "stock": 10}


def test_get_product_list_requires_admin_permissions(api_client):
    response = api_client.get(PRODUCTS_LIST_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_admin_can_get_product_list(authenticated_admin_client):
    response = authenticated_admin_client.get(PRODUCTS_LIST_URL)
    assert response.status_code == status.HTTP_200_OK


def test_admin_can_create_product(authenticated_admin_client, product_data):
    response = authenticated_admin_client.post(
        PRODUCTS_LIST_URL, product_data, format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Product.objects.count() == 1
    assert Product.objects.first().name == product_data["name"]


def test_admin_can_update_product(authenticated_admin_client, product_data):
    product = Product.objects.create(**product_data)

    # URL для детализации продукта
    url = reverse("product-detail", args=[product.pk])

    updated_data = {"name": "Обновленный Продукт", "price": 150.00}

    response = authenticated_admin_client.patch(url, updated_data, format="json")

    product.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert product.name == updated_data["name"]
    assert product.price == updated_data["price"]


def test_admin_can_delete_product(authenticated_admin_client, product_data):
    product = Product.objects.create(**product_data)

    url = reverse("product-detail", args=[product.pk])

    response = authenticated_admin_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Product.objects.filter(pk=product.pk).exists()


def test_get_product_detail_is_not_allowed_for_unauthenticated_user(
    api_client, db, product_data
):
    product = Product.objects.create(**product_data)
    url = reverse("product-detail", args=[product.pk])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
