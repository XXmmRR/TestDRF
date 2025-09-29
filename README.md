## Структура

| Компонент | Назначение |
| :--- | :--- |
| `accounts/` | Модель пользователя (Custom User Model), аутентификация. |
| `products/` | Управление списком продуктов. |
| `orders/` | Управление заказами|
| `core/settings.py` | Основные настройки Django. |
| `core/celery.py`, `orders/tasks.py` | Настройка и задачи Celery. |
| `tests/` | Набор тестов Pytest (Unit/Integration). |
| `docker-compose.dev.yml` | Конфигурация для локальной разработки. |
| `docker-compose.prod.yml` | Конфигурация для прода. |


### 1\. Запуск Сервисов

Соберите образы и запустите все сервисы (веб, БД, Redis, Celery Worker) в режиме демона:

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

### 3\. Доступ к Приложению

После успешного запуска сервисы будут доступны:

  * **Документация API ** `http://localhost:8000/api/docs/`

-----

## ✅ Тестирование (Development)

Тесты изолированы в отдельном сервисе `test` и запускаются через Pytest.

### Запуск тестов

Выполните команду в корне проекта, чтобы запустить тестовый контейнер. Он выполнит миграции (если нужно), запустит тесты, а затем удалится:

```bash
docker compose -f docker-compose.dev.yml run --rm test
```

-----

## ☁️ Продакшен (Deployment)

Для развертывания используется конфигурация `docker-compose.prod.yml` с Gunicorn.

### 1\. Подготовка Продакшен-Файла

1.  Создайте файл переменных окружения для продакшена:
    ```bash
    cp env.sample .env.prod
    ```

### 2\. Запуск Продакшен-Среды

Соберите и запустите продакшен-сервисы (Web, DB, Redis, Celery Worker):

```bash
docker compose -f docker-compose.prod.yml up --build -d
```
### 3\. Создание миграций
Запустит временный контейнер, выполнит команду и удалит контейнер.

docker compose -f docker-compose.dev.yml run --rm web python manage.py makemigrations

Миграции применяются автоматически в entrypoint.sh

### 4\. Примеры CURL запросов

### 4.1\. Аутентификация (Получение токена)

Используйте эту команду, чтобы получить `access` токен для пользователя.

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
     -H 'Content-Type: application/json' \
     -d '{
         "email": "testuser_for_order@example.com",
         "password": "password123"
     }'
```

-----

### 4.2\. Продукты (Только для Админа)

Операции требуют токена администратора.

| Операция | Метод | Команда |
| :--- | :--- | :--- |
| **Создать** | `POST` | \`\`\`bash
curl -X POST http://localhost:8000/api/products/  
\-H "Authorization: Bearer ${ACCESS\_TOKEN}"  
\-H 'Content-Type: application/json'  
\-d '{"name": "Ноутбук", "price": 1299.99, "stock": 10}'

````|
| **Список** | `GET` | ```bash
curl -X GET http://localhost:8000/api/products/ \
     -H "Authorization: Bearer ${ACCESS_TOKEN}"
``` |
| **Удалить** | `DELETE` | ```bash
# Используйте ID существующего продукта
curl -X DELETE http://localhost:8000/api/products/1/ \
     -H "Authorization: Bearer ${ACCESS_TOKEN}"
``` |

---

### 4.3. Заказы (Пользовательские операции)

Операции требуют токена аутентифицированного пользователя.

| Операция | Метод | Команда |
| :--- | :--- | :--- |
| **Создать** | `POST` | ```bash
# Используйте ID существующего продукта (e.g., 1)
curl -X POST http://localhost:8000/api/orders/ \
     -H "Authorization: Bearer ${ACCESS_TOKEN}" \
     -H 'Content-Type: application/json' \
     -d '{"items": [{"product": 1, "quantity": 2}]}'
``` |
| **Список** | `GET` | ```bash
# Просмотр своих заказов
curl -X GET http://localhost:8000/api/orders/ \
     -H "Authorization: Bearer ${ACCESS_TOKEN}"
``` |
| **Фильтр** | `GET` | ```bash
# Фильтр по статусу (например, 'new')
curl -X GET "http://localhost:8000/api/orders/?status=new" \
     -H "Authorization: Bearer ${ACCESS_TOKEN}"
``` |

---

### 4.4. Управление Заказами (Только для Админа)

Операции требуют токена администратора.

| Операция | Метод | Команда |
| :--- | :--- | :--- |
| **Обновить статус** | `PATCH` | ```bash
# Используйте ID существующего заказа
curl -X PATCH http://localhost:8000/api/orders/1/set_status/ \
     -H "Authorization: Bearer ${ACCESS_TOKEN}" \
     -H 'Content-Type: application/json' \
     -d '{"status": "completed"}'
``` |
````