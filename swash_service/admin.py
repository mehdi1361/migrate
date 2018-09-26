from django.contrib import admin
from .models import Category, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount', 'notification', 'parent')
    list_editable = ('discount', 'notification', 'parent')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'notification', 'duration', 'category')
    list_editable = ('price', 'discount', 'notification', 'duration', 'category')
