import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from orders.models import Order, OrderItem
from products.models import Product
from accounts.models import User
from django.core import mail

ORDERS_LIST_URL = reverse("order-list")

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_data(db, django_user_model):
    user = django_user_model.objects.create_user(email='testuser_for_order@example.com', password='password123')
    admin_user = django_user_model.objects.create_superuser(email='admin_for_order@example.com', password='password123')
    return user, admin_user


@pytest.fixture
def authenticated_user_client(api_client, user_data):
    user, _ = user_data
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, user_data):
    _, admin_user = user_data
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
def order_in_db(db, user_data, product_in_db):
    user, _ = user_data
    order = Order.objects.create(user=user, total_price=200.00)
    OrderItem.objects.create(order=order, product=product_in_db, quantity=2, price=100.00)
    return order


@pytest.fixture
def setup_products_for_filter(db):
    Product.objects.create(id=1, name="Laptop", price=1000.00, stock=50)
    Product.objects.create(id=2, name="Mouse", price=25.00, stock=100)
    return Product.objects.all()


@pytest.fixture
def setup_orders(db, user_data, setup_products_for_filter):
    user, _ = user_data
    
    order_1 = Order.objects.create(user=user, total_price=1000.00, status='new')
    OrderItem.objects.create(order=order_1, product_id=1, quantity=1, price=1000.00)
    
    order_2 = Order.objects.create(user=user, total_price=50.00, status='in_progress')
    OrderItem.objects.create(order=order_2, product_id=2, quantity=2, price=25.00)
    
    order_3 = Order.objects.create(user=user, total_price=25.00, status='completed')
    OrderItem.objects.create(order=order_3, product_id=2, quantity=1, price=25.00)
    
    _, admin_user = user_data
    order_4 = Order.objects.create(user=admin_user, total_price=1000.00, status='new')
    OrderItem.objects.create(order=order_4, product_id=1, quantity=1, price=1000.00)

    return order_1, order_2, order_3, order_4

def test_authenticated_user_can_list_their_orders(authenticated_user_client, order_in_db, db):
    response = authenticated_user_client.get(ORDERS_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]["id"] == order_in_db.id


def test_authenticated_user_can_create_order(authenticated_user_client, order_data, user_data, db):
    user, _ = user_data
    response = authenticated_user_client.post(ORDERS_LIST_URL, order_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Order.objects.filter(user=user).count() == 1
    order = Order.objects.get(user=user)
    assert order.items.first().product.id == order_data['items'][0]['product']
    assert order.user == user

def test_admin_can_list_all_orders(authenticated_admin_client, order_in_db, db):
    user2 = User.objects.create(email="user2_for_order_test@example.com", is_staff=False, is_superuser=False)
    Order.objects.create(user=user2, total_price=50.00)
    
    response = authenticated_admin_client.get(ORDERS_LIST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


def test_admin_can_update_order(authenticated_admin_client, order_in_db):
    url = reverse("order-set-status", args=[order_in_db.id]) 
    response = authenticated_admin_client.patch(url, {"status": "completed"}, format="json") 
    
    order_in_db.refresh_from_db()
    
    assert response.status_code == status.HTTP_200_OK
    assert order_in_db.status == "completed"

@pytest.mark.django_db
def test_filter_orders_by_status_for_regular_user(api_client, user_data, setup_orders):
    user, _ = user_data
    order_1, order_2, _, _ = setup_orders
    
    api_client.force_authenticate(user=user)
    list_url = reverse("order-list") 
    
    response = api_client.get(list_url, {"status": "new"})
    
    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']
    
    assert len(results) == 1 
    
    response_ids = {item["id"] for item in results}
    expected_ids = {order_1.id}
    assert response_ids == expected_ids
    
    for item in results:
        assert item["status"] == "new"

    response = api_client.get(list_url, {"status": "in_progress"})
    
    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']
    
    assert len(results) == 1
    assert results[0]["id"] == order_2.id
    assert results[0]["status"] == "in_progress"


@pytest.mark.django_db
def test_admin_can_filter_all_orders_by_status(api_client, user_data, setup_orders):
    _, admin_user = user_data
    order_1, _, order_3, order_4 = setup_orders
    
    api_client.force_authenticate(user=admin_user)
    list_url = reverse("order-list") 
    
    response = api_client.get(list_url, {"status": "completed"})
    
    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']
    
    assert len(results) == 1
    assert results[0]["id"] == order_3.id
    assert results[0]["status"] == "completed"
    
    response_pending = api_client.get(list_url, {"status": "new"})
    assert response_pending.status_code == status.HTTP_200_OK
    assert len(response_pending.data['results']) == 2
    
    response_no_filter = api_client.get(list_url)
    assert len(response_no_filter.data['results']) == 4


@pytest.mark.django_db
def test_order_creation_sends_confirmation_email(authenticated_user_client, order_data, user_data):
    user, _ = user_data
    
    assert len(mail.outbox) == 0
    
    response = authenticated_user_client.post(ORDERS_LIST_URL, order_data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    
    assert len(mail.outbox) == 1
    
    email = mail.outbox[0]
    
    order_id = response.data['id']
    expected_subject = f'Подтверждение заказа #{order_id}'
    assert email.subject == expected_subject
    
    assert email.to == [user.email]
    
    assert str(order_id) in email.body