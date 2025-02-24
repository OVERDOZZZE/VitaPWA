from django.db import models
from profile.models import CustomUser
from django.utils.timezone import now
from django.templatetags.static import static
from cloudinary.models import CloudinaryField



class Category(models.Model):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название категории'
    )
    image = CloudinaryField(
        'categories/',
        blank=True,
        null=True,
        default='https://res.cloudinary.com/desy8wuw7/image/upload/v1740053714/default_item_mnkqtc.png'
    )

    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        try:
            return self.image.url
        except:
            return 0


class SubCategory(models.Model):
    class Meta:
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )

    def __str__(self):
        return f'{self.category.name} - {self.name}'


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('unit', 'Штучно'),
        ('weight', 'По весу')
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        verbose_name='Тип продукта'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория',
        help_text='Необязательно'
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Подкатегория',
        help_text='Необязательно'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Необязательно'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Код продукта',
        help_text='Необязательно'
    )
    stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='В стоке',
        help_text='Количество товара, которое имеется на складе или на руках',
        default=0
    )
    image = CloudinaryField(
        'products/',
        blank=True,
        null=True,
        default='https://res.cloudinary.com/desy8wuw7/image/upload/v1740053714/default_item_mnkqtc.png'
    )

    def __str__(self):
        if self.type == 'unit':
            return f'{self.name} шт'
        elif self.type == 'weight':
            return f'{self.name} вес'
        return self.name

    @property
    def formatted_name(self):
        if self.type == 'unit':
            return f'{self.name} шт'
        elif self.type == 'weight':
            return f'{self.name} вес'
        return self.name

    @property
    def formatted_price(self):
        if self.type == 'unit':
            return f'{self.price} сом/шт'
        elif self.type == 'weight':
            return f'{self.price} сом/кг'
        return self.price

    @property
    def formatted_stock(self):
        if self.type == 'unit':
            return f'{self.stock} шт'
        elif self.type == 'weight':
            return f'{self.stock} кг'
        return self.stock

    @property
    def image_url(self):
        try:
            return self.image.url
        except Exception:
            return static('images/default_item.png')


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'В обработке'),
        ('in_progress', 'В процессе'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен')
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Заказчик',
        related_name='order'
    )
    created_at = models.DateTimeField(
        default=now,
        verbose_name='Дата и время создания заказа',
        help_text='Сохраняется автоматически'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name='Статус заказа'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий к заказу',
        help_text='Необязательно'
    )

    def __str__(self):
        return f'{self.user.username} Заказ #{self.id}, {self.created_at.strftime("%B %d, %Y")}'

    @property
    def total_order_price(self):
        items = self.item.all()
        total = sum([item.total_price for item in items])
        return total

    @property
    def order_items(self):
        items = self.item.all()
        total = sum([item.quantity for item in items])
        return total

class OrderItem(models.Model):
    class Meta:
        verbose_name = 'Предмет заказа'
        verbose_name_plural = 'Предметы заказа'

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='item'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Продукт'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за ед.'
    )

    @property
    def formatted_quantity(self):
        if self.product.type == 'unit':
            return f'{self.quantity} шт'
        elif self.product.type == 'weight':
            return f'{self.quantity} кг'
        return self.quantity

    @property
    def total_price(self):
        return round(self.quantity * self.product.price, 2)
#
# Покажи как мне реализовать функционал "корзины" на основе сессий ( то есть сбрасывается при выходе или окончании сессии) на моем сайте на Django. Используй JS где понадобится (отдельно от html файла). Части моего кода будут приведены ниже. Есть страница product_list.html со списком всех продуктов.
#
# 1. Надо, чтобы возле каждого продукта была кнопка "Добавить".
# 2. При нажатии добавляется 1 единица продукта в корзину.
# 3. Так же теперь появляются кнопка "Убавить" и посередине двух кнопок input показывающий количество уже добавленного количества (Минимум 1), и пользователь может вручную вводить количество товара в этот input.
# 4. Если пользователь убавляет количество продукта до нуля, input и кнопка "Убавить" снова скрывается и остается только кнопка "Добавить" (Исходное положение)
# 5. Значения в input и корзине сохраняются до окончания сессии
#
# Так же, должна быть страница cart.html, в которой будут отображаться все выбранные в корзину товары.
# 1. Оттуда тоже можно регулировать количество выбранного продукта.
# 2. Есть кнопка "Удалить", которая удалят продукт из корзины полностью
# 3. Возле каждого продукта указана цена, выбранное количество и общая стоимость
# 4. В самом конце списка указана общая сумма корзины
# 5. На странице есть кнопка "Оформить", которая переносит на страницу checkout.html
#
# На странице checkout.html есть только кнопка "Подтвердить оформление", которая при нажатии создает Order с выбранными в корзине продуктами и опустошает корзину.
#
# Дополнительно: Если понадобится, можешь дополнять, изменять и удалять структуру предоставленного мною кода.
# Доложи, если в моем коде есть логические конфликты, которые делают создание функционала корзины осложненным.
#
# Предоставь весь необходимый код.
# Если есть вопросы по коду - задавай.
#
# КОД:
