from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from .models import *


admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Category)
admin.site.register(SubCategory)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('formatted_name', 'formatted_price', 'duplicate_link')

    def formatted_name(self, obj):
        return obj.formatted_name

    formatted_name.short_description = "Название"

    def formatted_price(self, obj):
        return obj.formatted_price

    formatted_price.short_description = "Цена"

    def duplicate_link(self, obj):
        url = reverse('admin:shop_product_duplicate', args=[obj.pk])
        return format_html('<a href="{}" class="button">Дублировать</a>', url)

    duplicate_link.short_description = "Дубликация"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/duplicate/', self.admin_site.admin_view(self.duplicate_object_view), name="shop_product_duplicate"),
        ]
        return custom_urls + urls

    def duplicate_object_view(self, request, pk):
        obj = Product.objects.get(pk=pk)
        obj.pk = None
        obj.save()
        self.message_user(request, _("Product duplicated successfully."))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/shop/product/'))
