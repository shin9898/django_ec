from django import template
from cart.models import Cart

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_count(context):
    """カート数量を取得するテンプレートタグ"""
    request = context['request']
    session_key = request.session.session_key

    if not session_key:
        return 0

    try:
        cart = Cart.objects.get(session_key=session_key)
        return cart.total_items_count
    except Cart.DoesNotExist:
        return 0
