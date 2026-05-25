from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display    = ["name", "email", "phone", "message_preview", "is_read_badge", "created_at"]
    list_filter     = ["is_read", "created_at"]
    search_fields   = ["name", "email", "phone", "message"]
    readonly_fields = ["name", "email", "phone", "message", "created_at"]
    list_editable   = []
    date_hierarchy  = "created_at"

    actions = ["mark_read", "mark_unread"]

    fieldsets = [
        ("Expéditeur", {
            "fields": ["name", "email", "phone", "created_at"],
        }),
        ("Message", {
            "fields": ["message"],
        }),
        ("Suivi", {
            "fields": ["is_read"],
        }),
    ]

    @admin.display(description="Aperçu")
    def message_preview(self, obj):
        preview = obj.message[:80]
        if len(obj.message) > 80:
            preview += "…"
        return preview

    @admin.display(description="Lu", boolean=False, ordering="is_read")
    def is_read_badge(self, obj):
        if obj.is_read:
            return mark_safe(
                '<span style="background:#dcfce7;color:#16a34a;padding:2px 10px;border-radius:999px;font-size:11px;font-weight:600;">Lu</span>'
            )
        return mark_safe(
            '<span style="background:#fee2e2;color:#CC1111;padding:2px 10px;border-radius:999px;font-size:11px;font-weight:600;">Non lu</span>'
        )

    @admin.action(description="Marquer comme lu")
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} message(s) marqué(s) comme lu(s).")

    @admin.action(description="Marquer comme non lu")
    def mark_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} message(s) marqué(s) comme non lu(s).")

    def has_add_permission(self, request):
        return False
