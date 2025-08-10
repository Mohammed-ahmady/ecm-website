from django.core.management.base import BaseCommand
from parts.models import Part, TruckModel, PartImage
import os

class Command(BaseCommand):
    help = 'Update database records to use Cloudinary URLs instead of local file paths'

    def handle(self, *args, **options):
        updated_parts = 0
        updated_trucks = 0
        
        self.stdout.write('Starting database update for Cloudinary URLs...')
        
        # Update Parts with images
        for part in Part.objects.all():
            if part.image:
                # Convert local path to Cloudinary public_id
                old_path = str(part.image)
                if not old_path.startswith('http'):
                    # This is a local path, needs to be updated
                    if old_path.startswith('parts_images/'):
                        # Extract filename and create Cloudinary public_id
                        filename = os.path.basename(old_path)
                        name_without_ext = os.path.splitext(filename)[0]
                        ext = os.path.splitext(filename)[1][1:]  # Remove the dot
                        public_id = f"ecm_website_media/parts_images/{name_without_ext}_{ext}"
                        
                        part.image = public_id
                        part.save()
                        updated_parts += 1
                        self.stdout.write(f"Updated Part: {part.name} -> {public_id}")
        
        # Update TruckModels with images
        for truck in TruckModel.objects.all():
            if truck.image:
                old_path = str(truck.image)
                if not old_path.startswith('http'):
                    if old_path.startswith('truck_models/'):
                        filename = os.path.basename(old_path)
                        name_without_ext = os.path.splitext(filename)[0]
                        ext = os.path.splitext(filename)[1][1:]
                        public_id = f"ecm_website_media/truck_models/{name_without_ext}_{ext}"
                        
                        truck.image = public_id
                        truck.save()
                        updated_trucks += 1
                        self.stdout.write(f"Updated Truck: {truck.name} -> {public_id}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {updated_parts} parts and {updated_trucks} truck models'
            )
        )
