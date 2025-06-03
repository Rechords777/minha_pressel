import asyncio
import os
from app.services.presell_generator import presell_generator
from app.models.presell import PresellType

async def test_presell_generator():
    """Test the presell generator service."""
    # Test parameters
    presell_id = 1
    presell_type = PresellType.COOKIES
    affiliate_link = "https://example.com/affiliate"
    language_code = "pt"
    screenshot_path = "/home/ubuntu/presell_platform_backend/generated_assets/screenshots/test_screenshot.png"
    slug = "test-presell"
    
    # Ensure the screenshot file exists (create a dummy if not)
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    if not os.path.exists(screenshot_path):
        with open(screenshot_path, "w") as f:
            f.write("dummy screenshot")
    
    # Generate HTML
    html_path = presell_generator.generate_presell_html(
        presell_id=presell_id,
        presell_type=presell_type,
        affiliate_link=affiliate_link,
        language_code=language_code,
        screenshot_path=screenshot_path,
        slug=slug
    )
    
    # Verify the HTML file was created
    assert os.path.exists(html_path), f"HTML file was not created at {html_path}"
    
    # Verify the content of the HTML file
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "{{" not in content, "Not all placeholders were replaced"
        assert "}}" not in content, "Not all placeholders were replaced"
        assert affiliate_link in content, "Affiliate link was not injected"
        assert language_code in content, "Language code was not set"
    
    print(f"HTML file generated successfully at: {html_path}")
    return html_path

if __name__ == "__main__":
    # Run the test
    html_path = asyncio.run(test_presell_generator())
    print(f"Test completed. HTML file: {html_path}")
