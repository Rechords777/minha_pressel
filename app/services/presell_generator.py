import os
import json
import shutil
from typing import Dict, Optional, Any, List
from pathlib import Path

from app.models.presell import PresellType
from app.core.config import settings

# Map model enum values to template file names
TEMPLATE_MAP = {
    PresellType.COOKIES: "cookies.html",
    PresellType.IDADE: "age.html",
    PresellType.SEXO: "sex.html",
    PresellType.FANTASMA: "ghost.html",
    PresellType.PAIS: "country.html",
}

# Map model enum values to language file keys
LANG_KEY_MAP = {
    PresellType.COOKIES: "cookies",
    PresellType.IDADE: "age",
    PresellType.SEXO: "sex",
    PresellType.FANTASMA: "ghost",
    PresellType.PAIS: "country",
}

class PresellGenerator:
    """Service for generating HTML presell pages based on templates and language files."""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.langs_dir = Path(__file__).parent / "langs"
        self.output_dir = Path(settings.GENERATED_ASSETS_DIR) / "html_presells"
        self.screenshots_dir = Path(settings.GENERATED_ASSETS_DIR) / "screenshots"
        
        # Ensure directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_language_file(self, language_code: str) -> Dict[str, Any]:
        """Load language file for the specified language code."""
        lang_file = self.langs_dir / f"{language_code}.json"
        
        # If language file doesn't exist, use English as fallback
        if not lang_file.exists():
            # Copy English file as a new language file
            en_file = self.langs_dir / "en.json"
            if en_file.exists():
                shutil.copy(en_file, lang_file)
            
            # Load English as fallback
            lang_file = self.langs_dir / "en.json"
        
        with open(lang_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _get_template(self, presell_type: PresellType) -> str:
        """Get the template content for the specified presell type."""
        template_file = self.templates_dir / TEMPLATE_MAP.get(presell_type, "cookies.html")
        
        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()
    
    def generate_presell_html(
        self,
        presell_id: int,
        presell_type: PresellType,
        affiliate_link: str,
        language_code: str,
        screenshot_path: str, # Placeholder path
        custom_background_image_url: Optional[str], # Custom image URL
        slug: str
    ) -> str:
        """
        Generate HTML for a presell based on type, language, and affiliate link.
        Returns the path to the generated HTML file.
        """
        # Load language data
        lang_data = self._load_language_file(language_code)
        
        # Get template
        template = self._get_template(presell_type)
        
        # Get type-specific language keys
        type_key = LANG_KEY_MAP.get(presell_type, "cookies")
        type_texts = lang_data.get(type_key, {})
        
        # Determine background image path/URL
        background_image_src = custom_background_image_url if custom_background_image_url else f"../screenshots/{os.path.basename(screenshot_path)}"
        
        # Prepare replacements
        replacements = {
            "{{language_code}}": language_code,
            "{{title}}": type_texts.get("title", ""),
            "{{message}}": type_texts.get("message", ""),
            "{{affiliate_link}}": affiliate_link,
            "{{screenshot_path}}": background_image_src, # Use custom or placeholder
        }
        
        # Add type-specific replacements
        if presell_type == PresellType.COOKIES:
            replacements.update({
                "{{accept}}": type_texts.get("accept", "Accept"),
                "{{close}}": type_texts.get("close", "Close"),
                "{{learn_more}}": type_texts.get("learn_more", "Learn more"),
            })
        elif presell_type == PresellType.IDADE:
            replacements.update({
                "{{confirm}}": type_texts.get("confirm", "I am over 18"),
                "{{deny}}": type_texts.get("deny", "I am under 18"),
            })
        elif presell_type == PresellType.SEXO:
            replacements.update({
                "{{male}}": type_texts.get("male", "Male"),
                "{{female}}": type_texts.get("female", "Female"),
                "{{other}}": type_texts.get("other", "Other"),
                "{{skip}}": type_texts.get("skip", "Skip"),
            })
        elif presell_type in [PresellType.FANTASMA, PresellType.PAIS]:
            replacements.update({
                "{{continue}}": type_texts.get("continue", "Continue"),
                "{{close}}": type_texts.get("close", "Close"),
            })
        
        # Set language selector options
        replacements.update({
            "{{pt_selected}}": "selected" if language_code == "pt" else "",
            "{{en_selected}}": "selected" if language_code == "en" else "",
            "{{es_selected}}": "selected" if language_code == "es" else "",
        })
        
        # Apply replacements
        for key, value in replacements.items():
            template = template.replace(key, str(value))
        
        # Generate output file path
        output_file = self.output_dir / f"{slug}.html"
        
        # Write the generated HTML
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(template)
        
        return str(output_file)

# Singleton instance
presell_generator = PresellGenerator()
