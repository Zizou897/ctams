from django.contrib import admin
from django.utils.html import format_html
from .models import QuoteRequest, Devis, DevisLine, DevisStatus


# ── QuoteRequest ──────────────────────────────────────────────────────────────

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display  = ["company_name", "contact_name", "email", "phone", "service_type", "vehicle_count", "is_processed", "created_at"]
    list_filter   = ["is_processed", "service_type", "created_at"]
    search_fields = ["company_name", "contact_name", "email", "phone"]
    readonly_fields = ["created_at"]
    list_editable = ["is_processed"]
    date_hierarchy = "created_at"

    actions = ["mark_processed", "create_devis"]

    @admin.action(description="Marquer comme traité")
    def mark_processed(self, request, queryset):
        updated = queryset.update(is_processed=True)
        self.message_user(request, f"{updated} demande(s) marquée(s) comme traitée(s).")

    @admin.action(description="Créer un devis depuis la sélection")
    def create_devis(self, request, queryset):
        created = 0
        for qr in queryset:
            Devis.objects.create(
                quote_request=qr,
                company_name=qr.company_name,
                contact_name=qr.contact_name,
                email=qr.email,
                phone=qr.phone,
                vehicle_count=qr.vehicle_count or 1,
            )
            created += 1
        self.message_user(request, f"{created} devis créé(s) en brouillon.")


# ── Devis ─────────────────────────────────────────────────────────────────────

class DevisLineInline(admin.TabularInline):
    model  = DevisLine
    extra  = 3
    fields = ["description", "quantity", "unit", "unit_price"]


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display    = ["reference", "company_name", "contact_name", "vehicle_count", "status_badge", "get_total_display", "valid_until", "created_at"]
    list_filter     = ["status", "created_at"]
    search_fields   = ["reference", "company_name", "contact_name", "email"]
    readonly_fields = ["reference", "created_at", "updated_at", "totals_display"]
    inlines         = [DevisLineInline]
    date_hierarchy  = "created_at"
    save_on_top     = True

    fieldsets = [
        ("Référence & statut", {
            "fields": ["reference", "status", "valid_until", "quote_request"],
        }),
        ("Client", {
            "fields": ["company_name", "contact_name", "email", "phone", "vehicle_count"],
        }),
        ("Conditions financières", {
            "fields": ["tax_rate", "terms", "totals_display"],
        }),
        ("Notes internes", {
            "fields": ["notes"],
            "classes": ["collapse"],
        }),
        ("Métadonnées", {
            "fields": ["created_at", "updated_at", "created_by"],
            "classes": ["collapse"],
        }),
    ]

    # ── Colonnes enrichies ────────────────────────────────────────────────────

    @admin.display(description="Statut", ordering="status")
    def status_badge(self, obj):
        colors = {
            DevisStatus.DRAFT:    ("#6b7280", "#f3f4f6"),
            DevisStatus.SENT:     ("#2133B0", "#E0E7FF"),
            DevisStatus.ACCEPTED: ("#16a34a", "#dcfce7"),
            DevisStatus.REJECTED: ("#CC1111", "#fee2e2"),
            DevisStatus.EXPIRED:  ("#92400e", "#fef3c7"),
        }
        fg, bg = colors.get(obj.status, ("#374151", "#f9fafb"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:999px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display()
        )

    @admin.display(description="Total TTC")
    def get_total_display(self, obj):
        total = obj.get_total()
        if total:
            return format_html('<strong>{:,.0f} FCFA</strong>', total)
        return "—"

    @admin.display(description="Récapitulatif financier")
    def totals_display(self, obj):
        subtotal = obj.get_subtotal()
        tax      = obj.get_tax_amount()
        total    = obj.get_total()
        return format_html(
            '<table style="border-collapse:collapse;min-width:260px;">'
            '<tr><td style="padding:4px 12px 4px 0;color:#6b7280;">Sous-total HT</td>'
            '<td style="padding:4px 0;text-align:right;font-weight:600;">{:,.0f} FCFA</td></tr>'
            '<tr><td style="padding:4px 12px 4px 0;color:#6b7280;">TVA ({} %)</td>'
            '<td style="padding:4px 0;text-align:right;">{:,.0f} FCFA</td></tr>'
            '<tr style="border-top:2px solid #e5e7eb;">'
            '<td style="padding:8px 12px 4px 0;font-weight:700;">Total TTC</td>'
            '<td style="padding:8px 0 4px;text-align:right;font-weight:700;font-size:16px;">{:,.0f} FCFA</td></tr>'
            '</table>',
            subtotal, obj.tax_rate, tax, total
        )

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
