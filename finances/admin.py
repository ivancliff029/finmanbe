from django.contrib import admin
from .models import Category, Item, Budget, ToBuy

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'get_total_amount', 'get_items_count']
    search_fields = ['name']
    
    def get_total_amount(self, obj):
        return f"{obj.total_amount:,.2f} UGX"
    get_total_amount.short_description = 'Total Amount'
    
    def get_items_count(self, obj):
        # Fixed: use 'itemsItem' instead of 'items'
        return obj.itemsItem.count()
    get_items_count.short_description = 'Items Count'

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'amount', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'amount','type', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'

@admin.register(ToBuy)
class ToBuyAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'