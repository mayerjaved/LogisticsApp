# core_logistics/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Driver, LogisticsCoordinator,
    Supplier, Warehouse, Client,
    Route, DeliveryItem
)

# -----------------
# Inlines
# -----------------
class DeliveryItemInline(admin.TabularInline):
    """
    Show delivery items linked to a route directly in
    the Route admin page.
    """
    model = DeliveryItem
    fields = ("item_name", "client", "client_address", "due_time", "is_delivered")
    readonly_fields = ("client_address",)
    extra = 0

    def client_address(self, obj):
        return obj.client.address
    client_address.short_description = "Delivery Address"


# -----------------
# Admin Configurations
# -----------------
@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    """
    Customizes the Route admin display.
    """
    list_display = ("name", "driver", "status", "scheduled_start_time", "total_stops_display")
    list_filter = ("status", "driver")
    search_fields = ("name", "driver__first_name", "driver__last_name")
    inlines = [DeliveryItemInline]

    def total_stops_display(self, obj):
        return obj.items.count()
    total_stops_display.short_description = "Total Stops"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Register the custom User model with Django's built-in
    user management functionality.
    """
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number", "address")}),
    )


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "license_number", "vehicle_plate")
    search_fields = ("first_name", "last_name", "license_number")


@admin.register(LogisticsCoordinator)
class LogisticsCoordinatorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "department")
    search_fields = ("first_name", "last_name", "department")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone_number")
    search_fields = ("name", "contact_person")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "capacity")
    search_fields = ("name", "location")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "phone_number", "address")
    search_fields = ("name", "contact_person")


@admin.register(DeliveryItem)
class DeliveryItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "barcode", "delivery_index", "client", "route", "is_delivered", "due_time")
    list_filter = ("is_delivered", "item_type")
    search_fields = ("item_name", "barcode", "client__name")