from django.contrib import admin
from .models import Category, Service, PeriodTime


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount', 'notification', 'parent')
    list_editable = ('discount', 'notification', 'parent')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount', 'notification', 'duration', 'category')
    list_editable = ('price', 'discount', 'notification', 'duration', 'category')


@admin.register(PeriodTime)
class PeriodTimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time')
    list_editable = ('start_time', 'end_time')
    ordering = ('-created_date', )