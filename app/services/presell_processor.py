import asyncio
import os
import json
from typing import Optional, Dict, Any

from app.services.image_capture import capture_screenshot_service
from app.services.presell_generator import presell_generator
from app.models.presell import PresellType, PresellStatus
from app.core.config import settings

async def process_presell_creation(
    presell_id: int,
    presell_type: PresellType,
    affiliate_link: str,
    product_url: str,
    language_code: str,
    slug: str,
    custom_background_image_url: Optional[str] = None # Add custom background URL
) -> Dict[str, Optional[str]]:
    """
    Process the creation of a presell by:
    1. Capturing a screenshot of the product URL
    2. Generating the HTML presell page
    3. Returning paths for database update
    """
    result = {
        "screenshot_path": None,
        "generated_html_path": None,
        "public_url": None
    }
    
    # Ensure directories exist
    screenshots_dir = os.path.join(settings.GENERATED_ASSETS_DIR, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # 1. Capture screenshot
    screenshot_filename = f"{slug}_{presell_id}.png"
    screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
    
    try:
        success = await capture_screenshot_service(product_url, screenshot_path)
        if success:
            result["screenshot_path"] = screenshot_path
        else:
            print(f"Failed to capture screenshot for presell {presell_id}")
            return result
    except Exception as e:
        print(f"Error capturing screenshot for presell {presell_id}: {e}")
        return result
    
    # 2. Generate HTML
    try:
        html_path = presell_generator.generate_presell_html(
            presell_id=presell_id,
            presell_type=presell_type,
            affiliate_link=affiliate_link,
            language_code=language_code,
            screenshot_path=screenshot_path, # Path to placeholder
            custom_background_image_url=custom_background_image_url, # Pass custom URL
            slug=slug
        )
        
        if html_path:
            result["generated_html_path"] = html_path
            # 3. Set public URL (relative to the mounted static directory)
            result["public_url"] = f"/presells/{slug}.html"
        else:
            print(f"Failed to generate HTML for presell {presell_id}")
    except Exception as e:
        print(f"Error generating HTML for presell {presell_id}: {e}")
    
    return result
