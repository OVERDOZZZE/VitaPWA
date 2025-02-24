from django.urls import path
from .views import product_list, order_list, category_list, cart, checkout, \
    add_to_cart, update_cart, remove_from_cart, cart_count, cancel_order

app_name = 'shop'

urlpatterns = [
    path('', product_list, name='product_list'),
    path('order_list/', order_list, name='order_list'),
    path('category_list/', category_list, name='category_list'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/count/', cart_count, name='cart_count'),
    path('cancel_order/', cancel_order, name='cancel_order'),

]
