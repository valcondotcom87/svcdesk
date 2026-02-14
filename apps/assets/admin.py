from django.contrib import admin
from apps.assets.models import AssetCategory, Asset


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_tag', 'name', 'category', 'status', 'current_owner')
    list_filter = ('status', 'category')
    search_fields = ('asset_tag', 'name', 'serial_number')
