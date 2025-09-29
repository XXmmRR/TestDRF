from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_order_confirmation_email(order_id, recipient_email):
    subject = f'Подтверждение заказа #{order_id}'
    message = (
        f'Здравствуйте!\n\nВаш заказ №{order_id} успешно оформлен.\n'
    )
    from_email = settings.EMAIL_HOST_USER or 'noreply@nextshop.com'

    send_mail(
        subject,
        message,
        from_email,
        [recipient_email],
        fail_silently=False,
    )