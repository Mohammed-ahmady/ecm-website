from django.core.management.base import BaseCommand
from parts.models import Part, TruckModel, PartImage
import cloudinary
from pathlib import Path

class Command(BaseCommand):
    help = 'Sync existing part records with their Cloudinary URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Update Parts
        parts_updated = 0
        parts = Part.objects.filter(image__isnull=False)
        
        for part in parts:
            if part.image and hasattr(part.image, 'name'):
                # Convert file path to Cloudinary URL format
                image_path = str(part.image.name)
                if image_path.startswith('parts_images/'):
                    # Convert to Cloudinary public ID format
                    public_id = f"ecm_website_media/{image_path}".replace('\\', '/')
                    public_id = public_id.replace('.', '_').replace('/', '/')
                    
                    if not dry_run:
                        # Update with Cloudinary field
                        part.image = public_id
                        part.save()
                    
                    parts_updated += 1
                    self.stdout.write(f"{'Would update' if dry_run else 'Updated'} Part: {part.name} -> {public_id}")
        
        # Update TruckModels
        trucks_updated = 0
        truck_models = TruckModel.objects.filter(image__isnull=False)
        
        for truck in truck_models:
            if truck.image and hasattr(truck.image, 'name'):
                image_path = str(truck.image.name)
                if image_path.startswith('truck_models/'):
                    public_id = f"ecm_website_media/{image_path}".replace('\\', '/')
                    public_id = public_id.replace('.', '_').replace('/', '/')
                    
                    if not dry_run:
                        truck.image = public_id
                        truck.save()
                    
                    trucks_updated += 1
                    self.stdout.write(f"{'Would update' if dry_run else 'Updated'} Truck: {truck.name} -> {public_id}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would update' if dry_run else 'Updated'} {parts_updated} parts and {trucks_updated} truck models"
            )
        )
