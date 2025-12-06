import logging
import sys
import csv
import shutil
from pathlib import Path

"""Load marketable items from Universalis API and join with item CSV.

Script to fetch marketable items and join with item data from SaintCoinach CSV.
Locates corresponding PNG icon files and copies them to icon_output folder.
"""

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_client import UniversalisAPI


def load_items_from_csv(csv_path: str) -> dict:
    """Load items from CSV file.
    
    Args:
        csv_path: Path to the item.csv file
        
    Returns:
        Dictionary mapping item ID to icon
    """
    items = {}
    logger = logging.getLogger(__name__)
    
    logger.info(f"Loading items from CSV: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            # Skip header rows (first 3 rows)
            next(reader)  # Column names
            next(reader)  # Data types
            
            for row in reader:
                if len(row) > 0 and row[0].isdigit():
                    item_id = int(row[0])
                    # Icon is at column 11 (0-indexed)
                    icon = row[11] if len(row) > 11 else None
                    items[item_id] = {'icon': icon}
        
        logger.info(f"Loaded {len(items)} items from CSV")
        return items
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise


def extract_icon_number(icon_path: str) -> str:
    """Extract icon number from icon path.
    
    Icon path format: ui/icon/020000/020001.tex
    Returns the filename part: 020001
    
    Args:
        icon_path: Full icon path from CSV
        
    Returns:
        Icon number (e.g., '020001')
    """
    if not icon_path:
        return None
    # Extract filename without extension
    filename = Path(icon_path).stem
    return filename


def find_icon_file(saintcoinach_root: str, icon_number: str) -> Path:
    """Find PNG icon file in SaintCoinach directory.
    
    PNG files are named like: 009011_hr1.png
    We search for files matching the icon number.
    
    Args:
        saintcoinach_root: Root path to SaintCoinach directory
        icon_number: Icon number (e.g., '020001')
        
    Returns:
        Path to the PNG file if found, None otherwise
    """
    if not icon_number:
        return None
    
    root_path = Path(saintcoinach_root)
    
    # Search for PNG files matching the icon number
    # Files are named like: 009011_hr1.png, 009011_hr2.png, etc.
    for png_file in root_path.rglob(f'{icon_number}*.png'):
        # Prefer hr1 version, but accept any
        if '_hr1.png' in png_file.name:
            return png_file
    
    # If no hr1 found, return the first match
    for png_file in root_path.rglob(f'{icon_number}*.png'):
        return png_file
    
    return None


def copy_icons(joined_items: list, saintcoinach_root: str, output_folder: str) -> int:
    """Copy icon files to output folder with item ID as filename.
    
    Args:
        joined_items: List of items with id and icon
        saintcoinach_root: Root path to SaintCoinach directory
        output_folder: Output folder path
        
    Returns:
        Number of files copied
    """
    logger = logging.getLogger(__name__)
    
    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output folder: {output_path}")
    
    copied_count = 0
    not_found_count = 0
    
    for item in joined_items:
        item_id = item['id']
        icon_path = item['icon']
        
        # Extract icon number from path
        icon_number = extract_icon_number(icon_path)
        
        # Find the PNG file
        png_file = find_icon_file(saintcoinach_root, icon_number)
        
        if png_file and png_file.exists():
            # Copy file with item ID as filename
            output_file = output_path / f"{item_id}.png"
            try:
                shutil.copy2(png_file, output_file)
                copied_count += 1
                if copied_count % 1000 == 0:
                    logger.info(f"Copied {copied_count} files...")
            except Exception as e:
                logger.error(f"Error copying {png_file} to {output_file}: {e}")
        else:
            not_found_count += 1
            if not_found_count <= 10:  # Log first 10 not found
                logger.debug(f"PNG file not found for item {item_id} (icon: {icon_number})")
    
    logger.info(f"Copied {copied_count} icons, {not_found_count} not found")
    return copied_count


def main():
    """Load marketable items from API and join with item CSV."""
    logger = logging.getLogger(__name__)
    
    # Initialize API client
    api = UniversalisAPI()
    
    # Fetch marketable items
    logger.info("Fetching marketable items...")
    marketable_items = api.get_marketable_items()
    logger.info(f"Retrieved {len(marketable_items)} marketable items")
    
    # Load items from CSV
    csv_path = r'E:\dev\SaintCoinach\2025.10.30.0000.0000\exd\item.csv'
    item_data = load_items_from_csv(csv_path)
    
    # Join: Create list of marketable items with their icon
    joined_list = []
    for item_id in marketable_items:
        if item_id in item_data:
            joined_list.append({
                'id': item_id,
                'icon': item_data[item_id]['icon']
            })
    
    logger.info(f"Joined {len(joined_list)} items")
    
    # Copy icon files
    saintcoinach_root = r'E:\dev\SaintCoinach\2025.10.30.0000.0000'
    build_folder = Path(__file__).parent.parent / 'build'
    output_folder = str(build_folder / 'icon_output')
    
    logger.info(f"Copying icons from {saintcoinach_root}")
    copied_count = copy_icons(joined_list, saintcoinach_root, output_folder)
    
    # Display results
    print(f"\nTotal marketable items: {len(marketable_items)}")
    print(f"Items found in CSV: {len(joined_list)}")
    print(f"Icons copied: {copied_count}")
    print(f"Output folder: {output_folder}")
    
    return joined_list


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    joined_items = main()