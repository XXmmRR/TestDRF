import pytest
from rest_framework import status
from django.urls import reverse
from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import User

# URL для списка заказов
ORDERS_LIST_URL = reverse("order-list")


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def test_user(db, django_user_model):
    return django_user_model.objects.create_user(email='testuser_for_order@example.com', password='password123')


@pytest.fixture
def admin_user(db, django_user_model):
    return django_user_model.objects.create_superuser(email='admin_for_order@example.com', password='password123')


@pytest.fixture
def authenticated_user_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def product_in_db(db):
    return Product.objects.create(name="Test Product", price=100.00, stock=50)


@pytest.fixture
def order_data(product_in_db):
    return {
        "items": [
            {"product": product_in_db.id, "quantity": 2},
        ]
    }


@pytest.fixture
def order_in_db(db, test_user, product_in_db):
    order = Order.objects.create(user=test_user, total_price=200.00)
    OrderItem.objects.create(order=order, product=product_in_db, quantity=2, price=100.00)
    return order


### Тесты для обычных пользователей

def test_authenticated_user_can_list_their_orders(authenticated_user_client, order_in_db, db):
    """Проверяет, что обычный пользователь видит только свои заказы."""
    response = authenticated_user_client.get(ORDERS_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]["id"] == order_in_db.id


def test_authenticated_user_can_create_order(authenticated_user_client, order_data, test_user, db):
    response = authenticated_user_client.post(ORDERS_LIST_URL, order_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.filter(user=test_user).count() == 1
    order = Order.objects.get(user=test_user)
    assert order.items.first().product.id == order_data['items'][0]['product']
    assert order.user == test_user


### Тесты для администраторов

def test_admin_can_list_all_orders(authenticated_admin_client, order_in_db, db):
    """Проверяет, что администратор видит все заказы."""
    # Создаем еще один заказ для другого пользователя
    user2 = User.objects.create(email="user2_for_order_test@example.com", is_staff=False, is_superuser=False)
    Order.objects.create(user=user2, total_price=50.00)
    
    response = authenticated_admin_client.get(ORDERS_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    # Исправлено: проверяем длину списка результатов внутри словаря
    assert len(response.data['results']) == 2

def test_admin_can_update_order(authenticated_admin_client, order_in_db):
    """Проверяет, что администратор может обновить заказ."""
    url = reverse("order-detail", args=[order_in_db.id])
    # Исправлено: обновляем статус, а не total_price, так как цена является read-only
    response = authenticated_admin_client.patch(url, {"status": "completed"}, format="json")
    
    order_in_db.refresh_from_db()
    
    assert response.status_code == status.HTTP_200_OK
    assert order_in_db.status == "completed"