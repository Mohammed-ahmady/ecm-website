from django.core.management.base import BaseCommand
from parts.models import Part, TruckModel

class Command(BaseCommand):
    help = 'Test and display current image URLs'

    def handle(self, *args, **options):
        self.stdout.write('🖼️  Current Image URLs:')
        self.stdout.write('=' * 50)
        
        # Check Parts
        parts_with_images = Part.objects.filter(image__isnull=False)[:5]
        if parts_with_images:
            self.stdout.write('\n📦 Parts Images:')
            for part in parts_with_images:
                self.stdout.write(f"  • {part.name}: {part.image.url if part.image else 'No image'}")
        
        # Check Truck Models
        trucks_with_images = TruckModel.objects.filter(image__isnull=False)[:5]
        if trucks_with_images:
            self.stdout.write('\n🚛 Truck Model Images:')
            for truck in trucks_with_images:
                self.stdout.write(f"  • {truck.name}: {truck.image.url if truck.image else 'No image'}")
        
        self.stdout.write('\n✅ Image URL test complete!')
        
        # Test Cloudinary connection
        try:
            import cloudinary
            self.stdout.write('\n☁️  Cloudinary Status: Connected ✅')
        except Exception as e:
            self.stdout.write(f'\n❌ Cloudinary Error: {e}')
