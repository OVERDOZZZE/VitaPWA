from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from cloudinary.models import CloudinaryField


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    address = models.CharField(
        max_length=255,
        verbose_name='Адрес'
    )
    store_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Название точки'
    )
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Номер телефона'
    )
    # image = models.ImageField(
    #     upload_to='users/',
    #     default='images/default_user.png',
    #     blank=True,
    #     null=True,
    #     verbose_name='Фото профиля'
    # )
    image = CloudinaryField(
        'users/',
        blank=True,
        null=True,
        default='https://res.cloudinary.com/desy8wuw7/image/upload/v1740053714/default_profile_gg8l4z.png'
    )

    def __str__(self):
        return self.username

    @property
    def total_order_value(self):
        total = self.order.aggregate(
            total=Sum(
                ExpressionWrapper(F('item__price') * F('item__quantity'), output_field=DecimalField())
            )
        )['total']
        if total:
            return round(total, 2)
        else:
            return 0

    @property
    def image_url(self):
        try:
            return self.image.url
        except:
            return 0
        
    
