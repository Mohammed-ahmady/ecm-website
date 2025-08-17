import os
import shutil
from pathlib import Path

# Source and target directories
base_dir = Path(r'c:\Users\Mohammed\Downloads\ecm-website-main\ecm-website-main')
source_dir = base_dir / 'media' / 'parts_images_organized_BACKUP'
target_dir = base_dir / 'media' / 'parts_images_cleaned'

# Create target directory if it doesn't exist
if not target_dir.exists():
    target_dir.mkdir(parents=True, exist_ok=True)

# Keep track of statistics
total_images = 0
renamed_images = 0
skipped_images = 0

# Process all folders in the source directory
for part_folder in source_dir.iterdir():
    if not part_folder.is_dir():
        continue
        
    part_number = part_folder.name
    
    # Skip non-standard part number folders if needed
    if not part_number[0].isdigit():
        print(f"Skipping non-standard part number folder: {part_number}")
        continue
        
    # Process all image files in this part folder
    for image_file in part_folder.iterdir():
        if not image_file.is_file() or not image_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            continue
            
        total_images += 1
        
        # Create new filename: just the part number + original extension
        new_filename = f"{part_number}{image_file.suffix}"
        target_path = target_dir / new_filename
        
        # If there are multiple images for one part, add a number suffix
        counter = 1
        while target_path.exists():
            new_filename = f"{part_number}_{counter}{image_file.suffix}"
            target_path = target_dir / new_filename
            counter += 1
            
        # Copy the image with the new name
        try:
            shutil.copy2(image_file, target_path)
            print(f"Copied: {image_file.name} → {new_filename}")
            renamed_images += 1
        except Exception as e:
            print(f"Error copying {image_file}: {e}")
            skipped_images += 1

# Summary
print("\n=== Summary ===")
print(f"Total images processed: {total_images}")
print(f"Successfully renamed and copied: {renamed_images}")
print(f"Skipped or errors: {skipped_images}")
print(f"\nRenamed images are in: {target_dir}")
