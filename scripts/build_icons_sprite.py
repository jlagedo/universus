"""
Generate sprite sheets from individual icon files.

Takes a folder of 80x80 PNG icons and creates sprite sheets (4096x4096)
with a JSON index mapping each icon to its location.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class SpriteSheetGenerator:
    """Generate sprite sheets from individual icon images."""
    
    SHEET_SIZE = 4096
    ICON_SIZE = 80
    ICONS_PER_ROW = SHEET_SIZE // ICON_SIZE  # 51 icons per row/column
    ICONS_PER_SHEET = ICONS_PER_ROW * ICONS_PER_ROW  # 2601 icons per sheet
    
    def __init__(self, input_folder: str, output_folder: str):
        """Initialize sprite sheet generator.
        
        Args:
            input_folder: Path to folder containing 80x80 PNG files
            output_folder: Path to output folder for sprite sheets and JSON
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Input folder: {self.input_folder}")
        logger.info(f"Output folder: {self.output_folder}")
        logger.info(f"Sprite sheet size: {self.SHEET_SIZE}x{self.SHEET_SIZE}")
        logger.info(f"Icon size: {self.ICON_SIZE}x{self.ICON_SIZE}")
        logger.info(f"Icons per sheet: {self.ICONS_PER_SHEET} ({self.ICONS_PER_ROW}x{self.ICONS_PER_ROW})")
    
    def load_icons(self) -> List[Tuple[str, Image.Image]]:
        """Load all PNG icon files from input folder.
        
        Returns:
            List of tuples (filename, image) sorted by filename
        """
        icons = []
        resized_count = 0
        
        for png_file in sorted(self.input_folder.glob('*.png')):
            try:
                img = Image.open(png_file)
                
                # Resize if necessary
                if img.size != (self.ICON_SIZE, self.ICON_SIZE):
                    if img.size[0] > self.ICON_SIZE or img.size[1] > self.ICON_SIZE:
                        # Resize larger images
                        img = img.resize((self.ICON_SIZE, self.ICON_SIZE), Image.Resampling.LANCZOS)
                        resized_count += 1
                        if resized_count <= 5:  # Log first 5 resizes
                            logger.info(f"Resized {png_file.name} to {self.ICON_SIZE}x{self.ICON_SIZE}")
                    else:
                        # Skip smaller images
                        logger.warning(
                            f"Image {png_file.name} has size {img.size}, "
                            f"expected {self.ICON_SIZE}x{self.ICON_SIZE}. Skipping."
                        )
                        continue
                
                # Ensure RGBA format and load into memory
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                else:
                    # Force load into memory to close file handle
                    img.load()
                
                # Create a copy to ensure the file handle is closed
                img_copy = img.copy()
                icons.append((png_file.stem, img_copy))
                
                if len(icons) % 2000 == 0:
                    logger.info(f"Loaded {len(icons)} icons...")
            except Exception as e:
                logger.error(f"Error loading {png_file}: {e}")
        
        logger.info(f"Loaded {len(icons)} icons ({resized_count} resized)")
        return icons
    
    def create_sprite_sheets(self, icons: List[Tuple[str, Image.Image]]) -> Tuple[List[Image.Image], Dict]:
        """Create sprite sheets from icons.
        
        Args:
            icons: List of (filename, image) tuples
            
        Returns:
            Tuple of (sprite_sheets, index_dict)
            - sprite_sheets: List of PIL Images
            - index_dict: Mapping of filename to {sheet, x, y, w, h}
        """
        sprite_sheets = []
        index_dict = {}
        
        # Calculate number of sheets needed
        num_sheets = (len(icons) + self.ICONS_PER_SHEET - 1) // self.ICONS_PER_SHEET
        logger.info(f"Will create {num_sheets} sprite sheets for {len(icons)} icons")
        
        # Create sheets with transparent background
        for sheet_num in range(num_sheets):
            sheet = Image.new(
                'RGBA',
                (self.SHEET_SIZE, self.SHEET_SIZE),
                (0, 0, 0, 0)  # Fully transparent background (RGBA with alpha=0)
            )
            sprite_sheets.append(sheet)
        
        # Place icons into sheets
        for icon_index, (filename, icon_img) in enumerate(icons):
            # Determine sheet and position
            sheet_num = icon_index // self.ICONS_PER_SHEET
            position_in_sheet = icon_index % self.ICONS_PER_SHEET
            
            row = position_in_sheet // self.ICONS_PER_ROW
            col = position_in_sheet % self.ICONS_PER_ROW
            
            x = col * self.ICON_SIZE
            y = row * self.ICON_SIZE
            
            # Paste icon into sheet, preserving transparency
            # Using the icon itself as the alpha mask ensures transparency is preserved
            sprite_sheets[sheet_num].paste(icon_img, (x, y), icon_img)
            
            # Record in index
            index_dict[filename] = {
                'sheet': sheet_num,
                'x': x,
                'y': y,
                'w': self.ICON_SIZE,
                'h': self.ICON_SIZE
            }
            
            if (icon_index + 1) % 1000 == 0:
                logger.info(f"Placed {icon_index + 1} icons...")
        
        logger.info(f"Created {len(sprite_sheets)} sprite sheets with transparent backgrounds")
        return sprite_sheets, index_dict
    
    def save_sprite_sheets(self, sprite_sheets: List[Image.Image]):
        """Save sprite sheets to disk.
        
        Args:
            sprite_sheets: List of PIL Images
        """
        for sheet_num, sheet in enumerate(sprite_sheets):
            output_file = self.output_folder / f'spritesheet_{sheet_num}.png'
            # Save with PNG format to preserve transparency
            sheet.save(output_file, 'PNG', optimize=True)
            logger.info(f"Saved {output_file}")
    
    def save_index(self, index_dict: Dict):
        """Save sprite index to JSON file.
        
        Args:
            index_dict: Mapping of filename to sprite location
        """
        index_file = self.output_folder / 'sprite_index.json'
        
        with open(index_file, 'w') as f:
            json.dump(index_dict, f, indent=2, sort_keys=True)
        
        logger.info(f"Saved sprite index to {index_file}")
        logger.info(f"Index contains {len(index_dict)} entries")
    
    def generate(self):
        """Generate sprite sheets and index."""
        logger.info("Starting sprite sheet generation...")
        
        # Load icons
        icons = self.load_icons()
        if not icons:
            logger.error("No icons found!")
            return False
        
        # Create sprite sheets
        sprite_sheets, index_dict = self.create_sprite_sheets(icons)
        
        # Save sprite sheets
        self.save_sprite_sheets(sprite_sheets)
        
        # Save index
        self.save_index(index_dict)
        
        logger.info("Sprite sheet generation complete!")
        return True


def main():
    """Main entry point."""
    logger = logging.getLogger(__name__)
    
    # Use build folder for input and output
    build_folder = Path(__file__).parent.parent / 'build'
    input_folder = build_folder / 'icon_output'
    output_folder = build_folder / 'sprites'
    
    if not input_folder.exists():
        logger.error(f"Input folder not found: {input_folder}")
        logger.error("Please run build_icons.py first to generate icon files.")
        return False
    
    # Generate sprite sheets
    generator = SpriteSheetGenerator(str(input_folder), str(output_folder))
    return generator.generate()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    success = main()
    exit(0 if success else 1)
