def cart_item_count(request):
    count = 0
    if request.user.is_authenticated:
        cart = request.session.get('cart', {})
        count = len(cart)
    return {'cart_item_count': count}
