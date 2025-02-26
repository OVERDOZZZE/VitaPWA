from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Product, Order, Category, OrderItem
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import date
from django.conf import settings
from VitaCargo.settings import EMAIL_IS_ACTIVE
from django.contrib import messages
from django.utils.html import strip_tags
from django.db.models import Case, When, Value, IntegerField

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Product


@login_required
@require_POST
def add_to_cart(request):
    """Add a product to the user's cart or increment its quantity."""
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'Product ID is required.'}, status=400)

    # Validate product exists
    get_object_or_404(Product, pk=product_id)

    cart = request.session.get('cart', {})
    if product_id in cart:
        # Increment by 0.1 and round to 1 decimal place
        cart[product_id] = round(float(cart[product_id]) + 0.1, 1)
    else:
        # Initial quantity
        cart[product_id] = 1.0

    request.session['cart'] = cart
    request.session.modified = True  # Ensure session saves
    return JsonResponse({'product_id': product_id, 'quantity': cart[product_id]})


@login_required
@require_POST
def update_cart(request):
    """Update the quantity of a product in the cart."""
    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    if not product_id or quantity is None:
        return JsonResponse({'error': 'Invalid data provided.'}, status=400)

    try:
        quantity = float(quantity)
        quantity = max(round(quantity, 1), 0.0)  # Ensure non-negative
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity value.'}, status=400)

    # Validate product exists
    get_object_or_404(Product, pk=product_id)

    cart = request.session.get('cart', {})
    if quantity > 0:
        cart[product_id] = quantity
    elif product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'product_id': product_id, 'quantity': cart.get(product_id, 0)})


@login_required
@require_POST
def remove_from_cart(request):
    """Remove a product from the cart."""
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'Product ID is required.'}, status=400)

    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        request.session.modified = True

    return JsonResponse({'product_id': product_id, 'quantity': 0})


@login_required
def cart(request):
    """Display the user's cart contents."""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0.0

    for product_id, quantity in cart.items():
        try:
            product = get_object_or_404(Product, pk=product_id)
            item_total = float(product.price) * float(quantity)
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': float(quantity),
                'item_total': round(item_total, 2),
            })
        except Exception as e:
            # Log error and skip invalid items
            print(f"Error processing cart item {product_id}: {e}")
            continue

    context = {
        'cart_items': cart_items,
        'total': round(total, 2),
        'cart_quantity': len(cart_items),
    }
    return render(request, 'shop/pages/cart.html', context)


def email_sending(order, subject, request, template, status):
    if status == True:
        today = date.today()

        order_items = order.item.all()
        product_list = []
        total_sum = 0
        for item in order_items:
            product_list.append(f"{item.product.formatted_name} x {item.formatted_quantity}")
            total_sum += item.quantity * item.price

        try:
            user = request.user
            customer_name = user.username
            customer_address = user.address
            store_name = user.store_name
            phone_number = user.phone_number
        except Profile.DoesNotExist:
            customer_name = request.user
            customer_address = 'Не указан'
            store_name = 'Не указан'
            phone_number = 'Не указан'

        html_message = render_to_string(
            template,
            {
                'customer_name': customer_name,
                'customer_address': customer_address,
                'store_name': store_name,
                'phone_number': phone_number,
                'order_date': today.strftime("%B %d, %Y"),
                'product_list': product_list,
                'total_sum': round(order.total_order_price, 2),
                'comment': order.comment
            }
        )
        plain_message = strip_tags(html_message)
        message = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['kyrgyzpink@gmail.com', 'aikol.abdykadyrov22.08.00@gmail.com'],
        )
        message.attach_alternative(html_message, 'text/html')
        message.send()
    else:
        pass


@login_required
def checkout(request):
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Корзина пуста.")
            return redirect('shop:product_list')
        
        # Создаём заказ на основе данных корзины
        order = Order.objects.create(user=request.user, comment=comment)

        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, pk=product_id)
            qty = float(quantity)
            # if product.stock < qty:
            #     messages.error(request, f"На складе недостаточно товара: {product.name}.")
            #     order.delete()  # Отменяем создание заказа
            #     return redirect('shop:cart')
            
            # Вычитаем заказанное количество товара со склада
            # product.stock = float(product.stock) - qty
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
        # Отправка email
        email_sending(
            order=order,
            subject='Новый заказ!',
            request=request,
            template='shop/layouts/email_template.html',
            status=settings.EMAIL_IS_ACTIVE
        )

        # Очищаем корзину в сессии
        request.session['cart'] = {}

        messages.success(request, "Order is confirmed")
        return redirect('shop:order_list')
    return render(request, 'shop/pages/checkout.html')


from django.db.models import Q

@login_required
def product_list(request):
    # Гарантируем, что в сессии есть ключ 'cart'
    cart = request.session.get('cart', {})
    request.session.setdefault('cart', cart)
    cart_items = sum(cart.values())

    # Начинаем с выборки всех товаров
    products = Product.objects.all()

    # Получаем поисковый запрос из GET-параметров
    search_query = request.GET.get('q')
    if search_query:
        # Фильтруем товары по полям name, description и code
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(code__icontains=search_query)
        )

    # Пагинация
    from django.core.paginator import Paginator
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cart_items': cart_items,
        'session_cart': cart,
        'cart_quantity': len(cart),
        'products_total': len(products)
    }
    return render(request, 'shop/pages/product_list.html', context)


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 19)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'shop/pages/order_list.html',
        {
            'page_obj': page_obj
        }
    )


@login_required
def category_list(request):
    categories = Category.objects.all()
    for i in categories:
        print(i.image_url)
    return render(request, 'shop/pages/category_list.html', {'categories': categories})


@login_required
def cart_count(request):
    cart = request.session.get('cart', {})
    count = len(cart)
    return JsonResponse({'cart_item_count': count})


def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


@login_required
@require_POST
def cancel_order(request):
    order_id = request.POST.get('order_id')
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        email_sending(
            order=order,
            subject=f'Заказ #{order.id} отменен',
            request=request,
            template='shop/layouts/email_cancelation.html',
            status=settings.EMAIL_IS_ACTIVE
        )
        return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})
    else:
        return JsonResponse({'success': False, 'message': 'Only pending orders can be cancelled.'})
