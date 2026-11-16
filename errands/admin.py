from django.contrib import admin
from .models import Category, ErrandRequest


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ErrandRequest)
class ErrandRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'taker', 'category', 'reward', 'status', 'deadline')
    list_filter = ('status', 'category')
    search_fields = ('title', 'owner__username', 'taker__username')