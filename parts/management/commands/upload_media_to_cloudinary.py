import os
import cloudinary.uploader
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Upload existing media files to Cloudinary'

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        
        if not media_root.exists():
            self.stdout.write(
                self.style.WARNING('Media directory does not exist.')
            )
            return

        uploaded_count = 0
        failed_count = 0

        # Walk through all files in media directory
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = Path(root) / file
                
                # Skip non-image files for now
                if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    continue
                
                # Create relative path for Cloudinary public_id
                relative_path = file_path.relative_to(media_root)
                public_id = str(relative_path).replace('\\', '/').replace('.', '_')
                
                try:
                    # Upload to Cloudinary
                    result = cloudinary.uploader.upload(
                        str(file_path),
                        public_id=public_id,
                        folder="ecm_website_media",
                        resource_type="auto"
                    )
                    
                    uploaded_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Uploaded: {relative_path} -> {result["secure_url"]}'
                        )
                    )
                    
                except Exception as e:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to upload {relative_path}: {str(e)}'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nUpload completed: {uploaded_count} files uploaded, {failed_count} failed'
            )
        )
