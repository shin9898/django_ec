# order/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order):
    """
    購入確認メールを送信
    """
    try:
        subject = f'ご注文ありがとうございます（注文番号: #{order.id}）'

        # HTMLメールテンプレート
        html_message = render_to_string('order/email/order_confirmation.html', {
            'order': order,
            'order_items': order.items.all(),
        })

        # テキスト版メール
        plain_message = render_to_string('order/email/order_confirmation.txt', {
            'order': order,
            'order_items': order.items.all(),
        })

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [order.email]

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f'Order confirmation email sent to {order.email} for order #{order.id}')
        return True

    except Exception as e:
        logger.error(f'Failed to send order confirmation email for order #{order.id}: {str(e)}')
        return False
