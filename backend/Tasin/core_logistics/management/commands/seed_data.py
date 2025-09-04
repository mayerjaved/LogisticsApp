import random
from datetime import timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from core_logistics.models import (
    Driver, LogisticsCoordinator, Supplier, Warehouse, Client, Route, DeliveryItem
)

# Use Canadian English for Faker to get relevant data
fake = Faker('en_CA')

# A large list of unique, realistic-looking Calgary addresses
CALGARY_LOCATIONS = [
    "201 5 Ave SW, Calgary, AB T2P 3N7", "600 7 Ave SW, Calgary, AB T2P 0V4", "123 10 Ave SE, Calgary, AB T2G 0V9",
    "510 17 Ave SW, Calgary, AB T2S 0A9", "3625 Shaganappi Trail NW, Calgary, AB T3A 0E2", "324 8 Ave SW, Calgary, AB T2P 2Z2",
    "1140 10 Ave SW, Calgary, AB T2R 0B5", "1901 6 St NE, Calgary, AB T2E 7V9", "2120 16 Ave NW, Calgary, AB T2M 4K6",
    "1515 9 Ave SE, Calgary, AB T2G 1S5", "400 Saddletowne Circle NE, Calgary, AB T3J 4A1", "2323 32 Ave NE, Calgary, AB T2E 6Z3",
    "8510 120 Ave SE, Calgary, AB T2Z 4N5", "2000 16 Ave NW, Calgary, AB T2M 0L2", "4000 Glenmore Trail SE, Calgary, AB T2C 2E9",
    "500 4 St SW, Calgary, AB T2P 2V6", "999 8 St SW, Calgary, AB T2R 1J5", "2335 15 St SW, Calgary, AB T2T 3X7",
    "2526 12 Ave SE, Calgary, AB T2G 1A8", "401 9 Ave SE, Calgary, AB T2G 0H5", "835 8 Ave SW, Calgary, AB T2P 2J1",
    "1122 40 Ave NE, Calgary, AB T2E 6L6", "1307 9 Ave SE, Calgary, AB T2G 0T2", "345 6 Ave SW, Calgary, AB T2P 0V9",
    "1316 9 Ave SE, Calgary, AB T2G 0T3", "1245 14 St SW, Calgary, AB T3C 1C9", "4500 16 Ave NW, Calgary, AB T3B 0M6",
    "500 Macleod Trail SE, Calgary, AB T2G 2M6", "8120 4 St SE, Calgary, AB T2H 3B5", "5805 Signal Hill Centre SW, Calgary, AB T3H 3P8",
    "606 5 St SW, Calgary, AB T2P 1Y1", "1202 Centre St N, Calgary, AB T2E 2M7", "11654 Elbow Dr SW, Calgary, AB T2W 1R2",
    "3803 116 Ave SE, Calgary, AB T2Z 3X1", "2000 Veterans Pl, Calgary, AB T3E 6B2", "3000 37 St SW, Calgary, AB T3E 3R8",
    "1500 14 St SW, Calgary, AB T3C 1C9", "4403 17 Ave SE, Calgary, AB T2A 0N1", "2220 16 Ave NE, Calgary, AB T2E 6N7",
    "1317 10 St SW, Calgary, AB T2R 1B5", "1018 7 Ave SW, Calgary, AB T2P 1A7", "4935 40 Ave NW, Calgary, AB T3A 2N1",
    "3500 46 St NW, Calgary, AB T2L 2A7", "501 18 Ave SW, Calgary, AB T2S 0C7", "333 96 Ave NE, Calgary, AB T3K 0S4",
    "2120 16 Ave NW, Calgary, AB T2M 4K6", "9750 Macleod Trail SE, Calgary, AB T2J 0P9", "1200 45 St SE, Calgary, AB T2A 6A8",
    "1000 7 Ave SW, Calgary, AB T2P 1A5", "820 11 Ave SW, Calgary, AB T2R 0E5", "2800 24 Ave NW, Calgary, AB T2N 4Z6",
    "3401 3 St SE, Calgary, AB T2G 2R6", "2300 24 St SW, Calgary, AB T2T 5H7", "630 8 Ave SW, Calgary, AB T2P 1G6",
    "734 7 Ave SW, Calgary, AB T2P 2P8", "855 8 Ave SW, Calgary, AB T2P 2J1", "1414 8 St SW, Calgary, AB T2R 1B5",
    "500 4 Ave SW, Calgary, AB T2P 2V6", "1301 8 St SW, Calgary, AB T2R 1B5", "1201 5 St SW, Calgary, AB T2R 1A5",
    "909 3 St SW, Calgary, AB T2P 2W9", "615 10 Ave SW, Calgary, AB T2R 0B5", "421 7 Ave SW, Calgary, AB T2P 4K2",
    "1018 7 Ave SW, Calgary, AB T2P 1A7", "712 11 Ave SW, Calgary, AB T2R 0E4", "1050 17 Ave SW, Calgary, AB T2T 0A2",
    "2500 4 St SW, Calgary, AB T2S 1X8", "530 8 Ave SW, Calgary, AB T2P 2Z8", "211 4 St SW, Calgary, AB T2P 1R7",
    "1303 14 Ave SW, Calgary, AB T3C 1B9", "610 8 Ave SW, Calgary, AB T2P 1G6", "1100 11 St SW, Calgary, AB T2R 0E3",
    "202 12 Ave SE, Calgary, AB T2G 1A8", "120 10 Ave SW, Calgary, AB T2R 0B4", "515 8 Ave SW, Calgary, AB T2P 1G6",
    "718 10 Ave SW, Calgary, AB T2R 0B3", "1245 10 Ave SE, Calgary, AB T2G 0S6", "118 14 Ave SW, Calgary, AB T2R 0A4",
    "2519 14 St SW, Calgary, AB T2T 3S5", "1314 17 Ave SW, Calgary, AB T2T 0C3", "1015 11 Ave SW, Calgary, AB T2R 0E5",
    "2404 4 St SW, Calgary, AB T2S 1X8", "1331 17 Ave SW, Calgary, AB T2T 0C3", "201 17 Ave SE, Calgary, AB T2G 1C3",
    "1010 10 Ave SW, Calgary, AB T2R 0E4", "1111 11 St SW, Calgary, AB T2R 0E3", "1008 14 St SW, Calgary, AB T3C 1C9",
    "1323 17 Ave SW, Calgary, AB T2T 0C3", "420 17 Ave SW, Calgary, AB T2S 0A9", "1002 17 Ave SW, Calgary, AB T2T 0A2",
    "1400 17 Ave SW, Calgary, AB T2T 0C4", "1025 17 Ave SW, Calgary, AB T2T 0A2", "1313 14 St SW, Calgary, AB T3C 1C9",
    "222 17 Ave SE, Calgary, AB T2G 1C3", "1104 17 Ave SW, Calgary, AB T2T 0A4", "1024 17 Ave SW, Calgary, AB T2T 0A3",
    "1010 14 St SW, Calgary, AB T2R 0R3", "1010 11 Ave SW, Calgary, AB T2R 0E5", "1110 10 Ave SW, Calgary, AB T2R 0B4",
    "1030 11 Ave SW, Calgary, AB T2R 0E5", "1111 10 Ave SW, Calgary, AB T2R 0E3", "1120 10 Ave SW, Calgary, AB T2R 0E3",
    "1009 17 Ave SW, Calgary, AB T2T 0A2", "1105 17 Ave SW, Calgary, AB T2T 0A4", "1008 17 Ave SW, Calgary, AB T2T 0A3",
    "1112 17 Ave SW, Calgary, AB T2T 0A4", "1109 17 Ave SW, Calgary, AB T2T 0A4", "1116 17 Ave SW, Calgary, AB T2T 0A4",
    "1011 17 Ave SW, Calgary, AB T2T 0A2", "1014 17 Ave SW, Calgary, AB T2T 0A3", "1118 17 Ave SW, Calgary, AB T2T 0A4",
    "1012 17 Ave SW, Calgary, AB T2T 0A3", "1119 17 Ave SW, Calgary, AB T2T 0A4", "1114 17 Ave SW, Calgary, AB T2T 0A4",
    "1020 17 Ave SW, Calgary, AB T2T 0A3", "1115 17 Ave SW, Calgary, AB T2T 0A4", "1121 17 Ave SW, Calgary, AB T2T 0A4",
    "1108 17 Ave SW, Calgary, AB T2T 0A4", "1113 17 Ave SW, Calgary, AB T2T 0A4", "1122 17 Ave SW, Calgary, AB T2T 0A4",
    "1106 17 Ave SW, Calgary, AB T2T 0A4", "1123 17 Ave SW, Calgary, AB T2T 0A4", "1022 17 Ave SW, Calgary, AB T2T 0A3",
]


class Command(BaseCommand):
    help = 'Seeds the database with realistic sample data for the logistics app.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Starting database seeding...'))

        # --- Clean up old data to prevent duplicates ---
        self.stdout.write('🧹 Clearing out old data...')
        DeliveryItem.objects.all().delete()
        Route.objects.all().delete()
        Client.objects.all().delete()
        Warehouse.objects.all().delete()
        Supplier.objects.all().delete()
        Driver.objects.all().delete()
        LogisticsCoordinator.objects.all().delete()

        # --- Create core objects first ---
        self.stdout.write('👤 Creating Drivers, Coordinators, and other core entities...')
        drivers = [Driver.objects.create_user(
            username=f'driver{i + 1}', password='password123', first_name=fake.first_name(),
            last_name=fake.last_name(), email=fake.email(), phone_number=fake.phone_number(),
            address=fake.address(), license_number=f'DL-{fake.unique.random_number(digits=8, fix_len=True)}',
            vehicle_make=random.choice(['Ford', 'Dodge', 'Chevrolet', 'Mercedes-Benz']),
            vehicle_model=random.choice(['Transit', 'ProMaster', 'Express', 'Sprinter']),
            vehicle_plate=f'{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()}-{fake.random_number(digits=3, fix_len=True)}'
        ) for i in range(10)]

        coordinators = [LogisticsCoordinator.objects.create_user(
            username=f'coord{i + 1}', password='password123', first_name=fake.first_name(),
            last_name=fake.last_name(), email=fake.email(), phone_number=fake.phone_number(),
            address=fake.address(), department=random.choice(['Dispatch', 'Fleet', 'Planning'])
        ) for i in range(5)]

        warehouses = [Warehouse.objects.create(
            name=f'Calgary {loc} Warehouse', location=loc, capacity=random.randint(500, 2000)
        ) for loc in ["SE Industrial", "NorthEast Hub", "West Logistics", "South Bay"]]

        suppliers = [Supplier.objects.create(
            name=fake.company(), contact_person=fake.name(), email=fake.email(),
            phone_number=fake.phone_number(), address=fake.address()
        ) for _ in range(10)]

        # Create more clients than locations to simulate multiple clients at the same address
        clients = [Client.objects.create(
            name=fake.company(), contact_person=fake.name(), email=fake.email(),
            phone_number=fake.phone_number(), address=random.choice(CALGARY_LOCATIONS)
        ) for _ in range(200)] 

        # --- Create Routes and associated Delivery Items ---
        self.stdout.write('🚚 Creating Routes and their Delivery Items...')
        for i in range(20):  # Create 20 routes for more variety
            start_time = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=random.randint(0, 5))
            duration_minutes = random.randint(480, 540) # 8 to 9 hours
            end_time = start_time + timedelta(minutes=duration_minutes)

            route = Route.objects.create(
                name=f'Calgary Route {i + 1}',
                driver=random.choice(drivers),
                coordinator=random.choice(coordinators),
                start_warehouse=random.choice(warehouses),
                scheduled_start_time=start_time,
                scheduled_end_time=end_time,
                status=random.choice(["PENDING", "IN_PROGRESS"]),
                estimated_duration_minutes=duration_minutes,
                notes=fake.sentence(nb_words=10)
            )

            # Assign a random number of delivery items to each route
            num_deliveries = random.randint(8, 15)
            for j in range(num_deliveries):
                due_hour = random.choice([10, 11, 12, 13, 14, 15, 16])
                # Assign a delivery index based on the loop counter
                delivery_index = 0 
                DeliveryItem.objects.create(
                    item_name=f'{random.choice(["Standard", "Fragile", "Urgent"])} Package',
                    item_type=random.choice(["GENERAL", "PHARMACY_MED"]),
                    weight_kg=round(random.uniform(0.5, 25.0), 2),
                    volume_m3=round(random.uniform(0.01, 0.5), 2),
                    supplier=random.choice(suppliers),
                    warehouse=route.start_warehouse,
                    client=random.choice(clients),
                    route=route,
                    due_time=time(hour=due_hour, minute=random.choice([0, 15, 30, 45])),
                    delivery_index=delivery_index
                )

        self.stdout.write(self.style.SUCCESS('✅ Database seeding complete!'))

