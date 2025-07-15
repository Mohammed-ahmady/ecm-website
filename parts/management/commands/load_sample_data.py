from django.core.management.base import BaseCommand
from parts.models import Category, TruckModel, Engine, Part, PartImage
from django.core.files.base import ContentFile
import os


class Command(BaseCommand):
    help = 'Load sample data into the database'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Categories
        engine_category, _ = Category.objects.get_or_create(
            name='Engine Components',
            defaults={'description': 'Essential engine parts and components'}
        )
        
        transmission_category, _ = Category.objects.get_or_create(
            name='Transmission',
            defaults={'description': 'Transmission and drivetrain components'}
        )
        
        # Create Truck Models
        volvo_fe, _ = TruckModel.objects.get_or_create(
            name='Volvo FE/FL',
            defaults={
                'description': 'Volvo FE/FL series trucks - versatile medium-duty vehicles',
                'slug': 'volvo-fe-fl'
            }
        )
        
        magirus_m, _ = TruckModel.objects.get_or_create(
            name='Magirus M-Series',
            defaults={
                'description': 'Magirus M-Series heavy-duty trucks',
                'slug': 'magirus-m-series'
            }
        )
        
        # Create Engines
        tcd2013, _ = Engine.objects.get_or_create(
            name='TCD 2013',
            defaults={
                'power_output': '180 HP',
                'fuel_type': 'Diesel',
                'emissions_standard': 'Euro 5'
            }
        )
        # Add truck model relationship
        tcd2013.truck_models.add(volvo_fe)
        
        # Create Parts
        cylinder_head, _ = Part.objects.get_or_create(
            name='Cylinder Head TCD2013-01',
            defaults={
                'description': 'Complete cylinder head assembly for TCD 2013 engine. High-quality replacement part with all necessary components.',
                'part_number': 'CH-TCD2013-01',
                'category': engine_category,
                'price': 1250.00,
                'stock': 5,
                'slug': 'ch-tcd2013-01-cylinder-head'
            }
        )
        # Add truck model relationships
        cylinder_head.truck_models.add(volvo_fe)
        
        turbo_assembly, _ = Part.objects.get_or_create(
            name='Turbocharger Assembly TCD2013',
            defaults={
                'description': 'Complete turbocharger assembly for TCD 2013 engine. Includes all gaskets and mounting hardware.',
                'part_number': 'TC-TCD2013-02',
                'category': engine_category,
                'price': 850.00,
                'stock': 8,
                'slug': 'tc-tcd2013-turbocharger-assembly'
            }
        )
        turbo_assembly.truck_models.add(volvo_fe)
        
        transmission_part, _ = Part.objects.get_or_create(
            name='Transmission Filter Kit',
            defaults={
                'description': 'Complete transmission filter kit with gaskets and seals.',
                'part_number': 'TF-MAG-001',
                'category': transmission_category,
                'price': 125.00,
                'stock': 15,
                'slug': 'tf-mag-001-transmission-filter'
            }
        )
        transmission_part.truck_models.add(magirus_m)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write(f'Created {Part.objects.count()} parts in the database.')
