import os
import json
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status

class PresellPublisher:
    """Service for managing the public URLs and access to presell pages."""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url  # Base URL for the deployed application
    
    def get_public_url(self, slug: str) -> str:
        """
        Generate a public URL for a presell based on its slug.
        
        Args:
            slug: The slug of the presell
            
        Returns:
            The complete public URL for accessing the presell
        """
        if self.base_url:
            return f"{self.base_url}/presells/{slug}.html"
        else:
            # If no base URL is set, return a relative path
            return f"/presells/{slug}.html"
    
    def get_absolute_path(self, relative_path: str) -> str:
        """
        Convert a relative path to an absolute path.
        
        Args:
            relative_path: The relative path to convert
            
        Returns:
            The absolute path
        """
        if relative_path.startswith("/"):
            return relative_path
        else:
            return f"/{relative_path}"
    
    def validate_presell_access(self, presell_path: str) -> bool:
        """
        Validate if a presell HTML file exists and is accessible.
        
        Args:
            presell_path: The path to the presell HTML file
            
        Returns:
            True if the presell is accessible, False otherwise
        """
        return os.path.exists(presell_path) and os.access(presell_path, os.R_OK)

# Singleton instance
presell_publisher = PresellPublisher()
