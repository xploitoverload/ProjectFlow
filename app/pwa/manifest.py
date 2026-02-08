"""Web App Manifest generation and management."""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ManifestIcon:
    """Manifest icon definition."""
    src: str
    sizes: str
    type: str = "image/png"
    purpose: str = "any"


@dataclass
class ManifestScreenshot:
    """Screenshot definition."""
    src: str
    sizes: str
    type: str = "image/png"


@dataclass
class ManifestShortcut:
    """App shortcut definition."""
    name: str
    short_name: str
    description: str
    url: str
    icons: List[ManifestIcon] = None


class ManifestGenerator:
    """Generates and manages web app manifest."""
    
    def __init__(self):
        """Initialize manifest generator."""
        self.name = "Project Management Pro"
        self.short_name = "ProjectPro"
        self.description = "Advanced project management and team collaboration platform"
        self.start_url = "/"
        self.scope = "/"
        self.display = "standalone"
        self.orientation = "portrait-primary"
        self.background_color = "#ffffff"
        self.theme_color = "#3b82f6"
        self.icons: List[ManifestIcon] = []
        self.screenshots: List[ManifestScreenshot] = []
        self.shortcuts: List[ManifestShortcut] = []
        self.categories = ["productivity", "business"]
        self.screenshots_mobile: List[ManifestScreenshot] = []
        self.screenshots_wide: List[ManifestScreenshot] = []
        self._setup_defaults()
    
    def _setup_defaults(self):
        """Setup default icons and metadata."""
        # Default icons
        icon_sizes = [
            (192, 192),
            (512, 512),
            (256, 256),
            (384, 384)
        ]
        
        for width, height in icon_sizes:
            self.add_icon(
                src=f"/static/images/icons/icon-{width}x{height}.png",
                sizes=f"{width}x{height}",
                purpose="any"
            )
        
        # Maskable icon for adaptive display
        self.add_icon(
            src="/static/images/icons/icon-maskable-192x192.png",
            sizes="192x192",
            purpose="maskable"
        )
    
    def add_icon(self, src: str, sizes: str, type: str = "image/png", 
                 purpose: str = "any") -> None:
        """
        Add icon to manifest.
        
        Args:
            src: Icon source path
            sizes: Icon sizes
            type: MIME type
            purpose: Icon purpose
        """
        icon = ManifestIcon(src=src, sizes=sizes, type=type, purpose=purpose)
        self.icons.append(icon)
        logger.info(f"Added icon: {sizes}")
    
    def add_screenshot(self, src: str, sizes: str, form_factor: str = "narrow",
                      type: str = "image/png") -> None:
        """
        Add screenshot to manifest.
        
        Args:
            src: Screenshot source path
            sizes: Screenshot sizes
            form_factor: 'narrow' or 'wide'
            type: MIME type
        """
        screenshot = ManifestScreenshot(src=src, sizes=sizes, type=type)
        self.screenshots.append(screenshot)
        
        if form_factor == "narrow":
            self.screenshots_mobile.append(screenshot)
        else:
            self.screenshots_wide.append(screenshot)
        
        logger.info(f"Added screenshot: {sizes}")
    
    def add_shortcut(self, name: str, short_name: str, description: str,
                     url: str, icon_src: str = None) -> None:
        """
        Add app shortcut to manifest.
        
        Args:
            name: Full shortcut name
            short_name: Short name
            description: Shortcut description
            url: Target URL
            icon_src: Optional icon path
        """
        icons = []
        if icon_src:
            icons = [ManifestIcon(src=icon_src, sizes="96x96")]
        
        shortcut = ManifestShortcut(
            name=name,
            short_name=short_name,
            description=description,
            url=url,
            icons=icons
        )
        self.shortcuts.append(shortcut)
        logger.info(f"Added shortcut: {name}")
    
    def generate_manifest_json(self) -> Dict:
        """
        Generate manifest JSON object.
        
        Returns:
            Dictionary containing manifest data
        """
        manifest = {
            "name": self.name,
            "short_name": self.short_name,
            "description": self.description,
            "start_url": self.start_url,
            "scope": self.scope,
            "display": self.display,
            "orientation": self.orientation,
            "background_color": self.background_color,
            "theme_color": self.theme_color,
            "icons": [asdict(icon) for icon in self.icons],
            "categories": self.categories,
            "screenshots": [asdict(ss) for ss in self.screenshots],
        }
        
        if self.shortcuts:
            manifest["shortcuts"] = [
                {
                    "name": s.name,
                    "short_name": s.short_name,
                    "description": s.description,
                    "url": s.url,
                    "icons": [asdict(icon) for icon in s.icons] if s.icons else []
                }
                for s in self.shortcuts
            ]
        
        return manifest
    
    def generate_manifest_json_string(self) -> str:
        """
        Generate manifest as JSON string.
        
        Returns:
            JSON string
        """
        manifest = self.generate_manifest_json()
        return json.dumps(manifest, indent=2)
    
    def get_manifest_html_tags(self) -> str:
        """
        Generate HTML meta tags for PWA manifest.
        
        Returns:
            HTML meta tags
        """
        tags = f"""<!-- PWA Manifest -->
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="{self.theme_color}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="{self.short_name}">
<meta name="mobile-web-app-capable" content="yes">
<!-- PWA Icons -->
<link rel="apple-touch-icon" href="/static/images/icons/icon-192x192.png">
<link rel="icon" type="image/png" href="/static/images/icons/icon-192x192.png">
"""
        return tags
    
    def set_theme_color(self, color: str) -> None:
        """
        Set theme color.
        
        Args:
            color: Hex color code
        """
        self.theme_color = color
        logger.info(f"Theme color set to {color}")
    
    def set_background_color(self, color: str) -> None:
        """
        Set background color.
        
        Args:
            color: Hex color code
        """
        self.background_color = color
        logger.info(f"Background color set to {color}")
    
    def get_stats(self) -> Dict:
        """
        Get manifest statistics.
        
        Returns:
            Dictionary with stats
        """
        return {
            "name": self.name,
            "short_name": self.short_name,
            "start_url": self.start_url,
            "display": self.display,
            "icons_count": len(self.icons),
            "screenshots_count": len(self.screenshots),
            "shortcuts_count": len(self.shortcuts),
            "theme_color": self.theme_color,
            "background_color": self.background_color
        }
