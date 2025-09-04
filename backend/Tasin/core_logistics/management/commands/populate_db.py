# C:\Code projects\Tasin\backend\Tasin\core_logistics\management\commands\populate_db.py

import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from core_logistics.models import (
    User,
    Driver,
    LogisticsCoordinator,
    Supplier,
    Warehouse,
    Client,
    Route,
    DeliveryItem,
)

class Command(BaseCommand):
    help = "Populates the database with realistic, Calgary-specific sample data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting database population...")

        fake = Faker("en_CA")

        # --- Clean database before populating ---
        self.stdout.write("Clearing old data...")
        DeliveryItem.objects.all().delete()
        Route.objects.all().delete()
        Client.objects.all().delete()
        Warehouse.objects.all().delete()
        Supplier.objects.all().delete()
        LogisticsCoordinator.objects.all().delete()
        Driver.objects.all().delete()
        User.objects.all().delete()

        # --- Create Superuser ---
        self.stdout.write("Creating superuser...")
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@tasin.com",
            password="password123",
            first_name="Admin",
            last_name="User",
            phone_number="403-555-0100",
            address=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
        )

        # --- Create Logistics Coordinators ---
        self.stdout.write("Creating logistics coordinators...")
        coordinators = []
        departments = ["Dispatch", "Receiving", "International", "Domestic"]
        for i in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            coordinator = LogisticsCoordinator.objects.create_user(
                username=f"coord{i}",
                email=f"{first_name.lower()}.{last_name.lower()}@tasin.com",
                password="password123",
                first_name=first_name,
                last_name=last_name,
                phone_number=f"403-555-{random.randint(1000, 1999):04d}",
                address=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
                department=random.choice(departments),
            )
            coordinators.append(coordinator)

        # --- Create Drivers ---
        self.stdout.write("Creating drivers...")
        drivers = []
        vehicle_makes = ["Ford", "Dodge", "Mercedes-Benz", "Freightliner"]
        vehicle_models = ["Transit", "ProMaster", "Sprinter", "M2"]
        for i in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            driver = Driver.objects.create_user(
                username=f"driver{i}",
                email=f"{first_name.lower()}.{last_name.lower()}@driver.com",
                password="password123",
                first_name=first_name,
                last_name=last_name,
                phone_number=f"587-555-{random.randint(2000, 2999):04d}",
                address=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
                license_number=f"DL-{random.randint(1000000, 9999999)}",
                vehicle_make=random.choice(vehicle_makes),
                vehicle_model=random.choice(vehicle_models),
                vehicle_plate=fake.license_plate(),
            )
            drivers.append(driver)

        # --- Create Suppliers ---
        self.stdout.write("Creating suppliers...")
        suppliers = []
        for _ in range(10):
            supplier = Supplier.objects.create(
                name=fake.company(),
                contact_person=fake.name(),
                email=fake.company_email(),
                phone_number=f"825-555-{random.randint(3000, 3999):04d}",
                address=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
            )
            suppliers.append(supplier)

        # --- Create Warehouses ---
        self.stdout.write("Creating warehouses...")
        warehouses = []
        warehouse_names = [
            "Foothills Logistics Hub", "CrossIron Storage", "East Calgary Distribution", "YYC Cargo Centre"
        ]
        for i in range(10):
            warehouse = Warehouse.objects.create(
                name=f"{random.choice(warehouse_names)} #{i+1}",
                location=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
                capacity=random.randint(1000, 10000),
            )
            warehouses.append(warehouse)

        # --- Create Clients ---
        self.stdout.write("Creating clients...")
        clients = []
        for _ in range(10):
            client = Client.objects.create(
                name=fake.company(),
                contact_person=fake.name(),
                email=fake.email(),
                phone_number=f"403-555-{random.randint(4000, 4999):04d}",
                address=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
            )
            clients.append(client)

        # --- Create Routes and Delivery Items ---
        self.stdout.write("Creating routes and delivery items...")
        routes = []
        for i in range(10):
            start_time = timezone.now() + timedelta(days=random.randint(1, 5), hours=random.randint(1, 12))
            duration = random.randint(60, 240)
            route = Route.objects.create(
                name=f"Route YYC-{i+1}",
                driver=random.choice(drivers),
                coordinator=random.choice(coordinators),
                start_warehouse=random.choice(warehouses),
                end_location=f"{fake.street_address()}, Calgary, AB {fake.postalcode_in_province('AB')}",
                scheduled_start_time=start_time,
                scheduled_end_time=start_time + timedelta(minutes=duration),
                status=random.choice([s[0] for s in Route.STATUS_CHOICES]),
                estimated_duration_minutes=duration,
                notes=fake.sentence(),
            )
            routes.append(route)

        item_names = ["Medical Supplies", "Electronics Kit", "Auto Parts", "Office Documents", "Lab Samples"]
        for i in range(10):
            DeliveryItem.objects.create(
                item_name=f"{random.choice(item_names)} #{i+1}",
                item_type=random.choice(["GENERAL", "PHARMACY_MED"]),
                weight_kg=round(random.uniform(0.5, 25.0), 2),
                volume_m3=round(random.uniform(0.01, 0.5), 2),
                supplier=random.choice(suppliers),
                warehouse=random.choice(warehouses),
                client=random.choice(clients),
                route=random.choice(routes),
            )

        self.stdout.write(self.style.SUCCESS("Database has been successfully populated! 🚚"))