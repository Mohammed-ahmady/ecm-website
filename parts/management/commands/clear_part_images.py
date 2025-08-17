import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.core.management.base import BaseCommand
from django.conf import settings
from parts.models import Part, PartImage

class Command(BaseCommand):
    help = 'Delete all part images from database and Cloudinary storage (DOES NOT affect TruckModel images)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='confirm',
            default=False,
            help='Required confirmation to actually delete images',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        confirm = options['confirm']
        
        # Counter for tracking
        deleted_count = 0
        cloudinary_deleted = 0
        errors = 0
        
        # Safety check - require explicit confirmation
        if not dry_run and not confirm:
            self.stdout.write(self.style.ERROR(
                'SAFETY CHECK: You must include --confirm to actually delete images.\n'
                'Please run with --confirm if you really want to delete all part images.\n'
                'Example: python manage.py clear_part_images --confirm\n'
                'Or run with --dry-run to see what would be deleted without making changes.'
            ))
            return
            
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No actual changes will be made'))
            
        self.stdout.write(self.style.WARNING(
            '\nSAFETY NOTICE: This will ONLY delete images from:\n'
            '  - Part model (part.image field)\n'
            '  - PartImage model records\n'
            'It will NOT touch TruckModel images or any other images.\n'
        ))
        
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
            api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
            api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
        )
        
        # 1. First handle PartImage records
        self.stdout.write('Processing PartImage records...')
        part_images = PartImage.objects.all()
        part_images_count = part_images.count()
        
        self.stdout.write(f'Found {part_images_count} PartImage records')
        
        for part_image in part_images:
            try:
                # Get the Cloudinary public_id if it exists
                if part_image.image:
                    public_id = part_image.image.public_id
                    
                    # Delete from Cloudinary
                    if not dry_run:
                        try:
                            result = cloudinary.uploader.destroy(public_id)
                            if result.get('result') == 'ok':
                                cloudinary_deleted += 1
                                self.stdout.write(f'  Deleted from Cloudinary: {public_id}')
                            else:
                                self.stdout.write(self.style.WARNING(f'  Failed to delete from Cloudinary: {public_id}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  Error deleting from Cloudinary: {e}'))
                            errors += 1
                    else:
                        self.stdout.write(f'  Would delete from Cloudinary: {public_id}')
                
                # Delete from database
                if not dry_run:
                    part_image.delete()
                    deleted_count += 1
                else:
                    deleted_count += 1
                    self.stdout.write(f'  Would delete PartImage #{part_image.id}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error processing PartImage #{part_image.id}: {e}'))
                errors += 1
        
        # 2. Clear image fields on Part records
        self.stdout.write('\nProcessing Part records...')
        parts = Part.objects.exclude(image='').exclude(image__isnull=True)
        parts_count = parts.count()
        
        self.stdout.write(f'Found {parts_count} Part records with images')
        
        for part in parts:
            try:
                if part.image:
                    public_id = part.image.public_id
                    
                    # Delete from Cloudinary
                    if not dry_run:
                        try:
                            result = cloudinary.uploader.destroy(public_id)
                            if result.get('result') == 'ok':
                                cloudinary_deleted += 1
                                self.stdout.write(f'  Deleted from Cloudinary: {public_id}')
                            else:
                                self.stdout.write(self.style.WARNING(f'  Failed to delete from Cloudinary: {public_id}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'  Error deleting from Cloudinary: {e}'))
                            errors += 1
                    else:
                        self.stdout.write(f'  Would delete from Cloudinary: {public_id}')
                
                # Clear the image field
                if not dry_run:
                    part.image = None
                    part.save(update_fields=['image'])
                    deleted_count += 1
                else:
                    deleted_count += 1
                    self.stdout.write(f'  Would clear image on Part #{part.id}')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Error processing Part #{part.id}: {e}'))
                errors += 1
        
        # Summary
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'\nDRY RUN SUMMARY:'))
            self.stdout.write(f'  {deleted_count} database records would be cleared')
            self.stdout.write(f'  {part_images_count + parts_count} Cloudinary images would be deleted')
            self.stdout.write(f'  {errors} errors would occur')
            self.stdout.write(self.style.WARNING('\nRun without --dry-run to actually delete the images'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nDONE:'))
            self.stdout.write(f'  {deleted_count} database records cleared')
            self.stdout.write(f'  {cloudinary_deleted} Cloudinary images deleted')
            self.stdout.write(f'  {errors} errors occurred')
            
        return '\nImage cleanup complete!'
