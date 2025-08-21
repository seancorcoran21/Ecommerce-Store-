from django.contrib import admin
from . models import Category, Customer, Product, Order
from django.utils.html import format_html
# Register your models here.
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_description')

    def short_description(self, obj):
        # Safely replace line breaks with <br>
        return format_html(obj.description.replace("\n", "<br>"))
    short_description.short_description = "Description"