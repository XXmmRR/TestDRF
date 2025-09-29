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