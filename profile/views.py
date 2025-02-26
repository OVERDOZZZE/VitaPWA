from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ContactForm
from django.core.mail import send_mail
from .forms import UserUpdateForm, ProfileUpdateForm
from django.http import HttpResponse


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile:profile')
        else:
            print(user_form.errors)
            print(profile_form.errors)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profile/edit_profile.html', context)


# user/views.py
import json
import datetime
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from shop.models import Order, OrderItem


@login_required
def profile_view(request):
    profile = request.user


    # --- График 1: Ежемесячные траты за текущий год ---
    current_year = datetime.date.today().year
    monthly_data = OrderItem.objects.filter(
        order__user=request.user,
        order__created_at__year=current_year
    ).annotate(
        month=TruncMonth('order__created_at')
    ).values('month').annotate(
        total_spent=Sum(
            ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField())
        )
    ).order_by('month')

    monthly_labels = []
    monthly_values = []
    for entry in monthly_data:
        month_label = entry['month'].strftime('%B')
        monthly_labels.append(month_label)
        monthly_values.append(float(entry['total_spent'] or 0))

    # --- График 2: Дневные траты за текущий месяц ---
    today = datetime.date.today()
    daily_data = OrderItem.objects.filter(
        order__user=request.user,
        order__created_at__year=today.year,
        order__created_at__month=today.month
    ).annotate(
        day=TruncDay('order__created_at')
    ).values('day').annotate(
        total_spent=Sum(
            ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField())
        )
    ).order_by('day')

    daily_labels = []
    daily_values = []
    for entry in daily_data:
        day_label = entry['day'].day  # число дня месяца
        daily_labels.append(day_label)
        daily_values.append(float(entry['total_spent'] or 0))

    # --- График 3: Гистограмма для сравнения расходов на овощи и фрукты ---
    veg_total = OrderItem.objects.filter(
        order__user=request.user,
        product__category__name__iexact='овощи'
    ).aggregate(
        total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
    )['total'] or 0

    fruit_total = OrderItem.objects.filter(
        order__user=request.user,
        product__category__name__iexact='фрукты'
    ).aggregate(
        total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
    )['total'] or 0

    # --- Дополнительный 1: Круговая диаграмма "Распределение заказов по статусам" ---
    order_status_data = Order.objects.filter(user=request.user).values('status').annotate(count=Count('id'))
    # Определим соответствие ключ-значение для статусов:
    status_mapping = {
        'pending': 'В обработке',
        'in_progress': 'В процессе',
        'completed': 'Выполнен',
        'cancelled': 'Отменён',  # добавляем для обработки статуса 'cancelled'
    }
    # Обеспечим наличие всех статусов, даже если их нет в запросе:
    order_status_counts = {key: 0 for key in status_mapping.keys()}
    for entry in order_status_data:
        order_status_counts[entry['status']] = entry['count']

    orders_status_labels = [status_mapping[key] for key in order_status_counts]
    orders_status_values = [order_status_counts[key] for key in order_status_counts]

    # --- Дополнительный 2: Топ-5 продаваемых продуктов по суммарной выручке ---
    top_products = OrderItem.objects.filter(order__user=request.user).values('product__name').annotate(
        revenue=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
    ).order_by('-revenue')[:5]
    top_products_labels = [item['product__name'] for item in top_products]
    top_products_values = [float(item['revenue'] or 0) for item in top_products]

    # --- Дополнительный 3: Динамика продаж по неделям текущего года ---
    weekly_data = OrderItem.objects.filter(
        order__user=request.user,
        order__created_at__year=current_year
    ).annotate(
        week=TruncWeek('order__created_at')
    ).values('week').annotate(
        total=Sum(ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField()))
    ).order_by('week')

    weekly_labels = []
    weekly_values = []
    for entry in weekly_data:
        # Выводим номер недели, например "Week 12"
        week_label = entry['week'].strftime('Week %W')
        weekly_labels.append(week_label)
        weekly_values.append(float(entry['total'] or 0))

    # Собираем все данные для графиков
    chart_data = {
        'monthly_labels': monthly_labels,
        'monthly_values': monthly_values,
        'daily_labels': daily_labels,
        'daily_values': daily_values,
        'veg_total': float(veg_total),
        'fruit_total': float(fruit_total),
        'orders_status_labels': orders_status_labels,
        'orders_status_values': orders_status_values,
        'top_products_labels': top_products_labels,
        'top_products_values': top_products_values,
        'weekly_labels': weekly_labels,
        'weekly_values': weekly_values,
    }
    context = {
        'profile': profile,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'profile/profile.html', context)


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = 'Новый запрос'
            address = form.cleaned_data['address']
            store_name = form.cleaned_data['store_name']
            phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']

            # Construct email message
            email_message = f"""Name: {name}\nEmail: {email}\n\nMessage:\n{message}
Адрес: {address}
Точка: {store_name}
Номер телефона: {phone_number}
Доп сообщение: {message}
"""
            # Send email
            send_mail(
                subject,
                email_message,
                email,  # Reply-to email
                ['kyrgyzpink@gmail.com', 'aikol.abdykadyrov22.08.00@gmail.com'],  # Recipient email
                fail_silently=False,
            )

            return redirect('profile:success_page')  # Redirect after successful submission

    else:
        form = ContactForm()

    return render(request, 'profile/contact_form.html', {'form': form})


def success_page(request):
    return render(request, 'profile/contact_success.html')
