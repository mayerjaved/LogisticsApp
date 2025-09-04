# C:\Code projects\Tasin\backend\Tasin\core_logistics\models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from datetime import datetime, time, timedelta
from django.utils import timezone


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


class Driver(User):
    license_number = models.CharField(max_length=50, unique=True)
    vehicle_make = models.CharField(max_length=100, blank=True, null=True)
    vehicle_model = models.CharField(max_length=100, blank=True, null=True)
    vehicle_plate = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Driver)"


class LogisticsCoordinator(User):
    department = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Logistics Coordinator"
        verbose_name_plural = "Logistics Coordinators"

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Coordinator)"


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.TextField()
    capacity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class Route(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    name = models.CharField(max_length=255)
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_routes",
    )
    coordinator = models.ForeignKey(
        LogisticsCoordinator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_routes",
    )
    start_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="start_routes"
    )
    # The 'end_location' is now implicit, based on the last delivery item.
    scheduled_start_time = models.DateTimeField(default=timezone.now)
    scheduled_end_time = models.DateTimeField(blank=True, null=True)
    actual_start_time = models.DateTimeField(blank=True, null=True)
    actual_end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estimated_duration_minutes = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Route {self.name} ({self.status})"

    def get_items_details(self):
        """
        Returns a list of dictionaries with details for all items on this route.
        """
        items_data = []
        for item in self.items.all():
            items_data.append({
                'item_name': item.item_name,
                'barcode': item.barcode,
                'client_name': item.client.name,
                'delivery_address': item.client.address,
                'due_time': item.due_time,
            })
        return items_data

    @property
    def total_stops(self):
        """
        Returns the total number of delivery stops for this route.
        """
        return self.items.count()


class DeliveryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ("GENERAL", "General"),
        ("PHARMACY_MED", "Pharmacy Med"),
    ]

    item_name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=6, unique=True, blank=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES, default="GENERAL")
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volume_m3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="supplied_items"
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="stored_items"
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="delivery_items")
    route = models.ForeignKey(
        Route, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    is_delivered = models.BooleanField(default=False)
    delivery_timestamp = models.DateTimeField(blank=True, null=True)
    due_time = models.TimeField(blank=True, null=True)
    created_date = models.DateField(auto_now_add=True)
    
    # Add the delivery_index field here
    delivery_index = models.IntegerField(null=True, blank=True)

    def generate_barcode(self):
        today = datetime.today().date()
        while True:
            barcode = str(random.randint(100000, 999999))
            if not DeliveryItem.objects.filter(barcode=barcode, created_date=today).exists():
                return barcode

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = self.generate_barcode()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} (Barcode: {self.barcode})"