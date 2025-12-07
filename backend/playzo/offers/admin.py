# offers/admin.py
from django.contrib import admin
from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'offer_type', 'status', 'is_featured', 'is_active_display', 'start_date', 'end_date']
    list_filter = ['status', 'offer_type', 'is_featured', 'is_exclusive', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'is_active_display']
    list_editable = ['is_featured', 'status']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'offer_type')
        }),
        ('Visual Properties', {
            'fields': ('color', 'image', 'image_url')
        }),
        ('Validity & Status', {
            'fields': ('start_date', 'end_date', 'status', 'is_featured', 'is_exclusive')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_active_display')
        }),
    )

    def is_active_display(self, obj):
        return obj.is_active

    is_active_display.boolean = True
    is_active_display.short_description = 'Is Active'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
