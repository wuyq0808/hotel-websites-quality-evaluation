#!/usr/bin/env python3
"""
Configuration Loader for Quality Evaluation System
Loads settings and prompts from config.yaml
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
from enum import Enum


class WebsiteKey(Enum):
    """Enum for website identifiers"""
    GOOGLE_TRAVEL = "google_travel"
    AGODA = "agoda"
    BOOKING_COM = "booking_com"
    SKYSCANNER = "skyscanner"


class Feature(Enum):
    """Enum for feature identifiers"""
    RELEVANCE_OF_TOP_LISTINGS = "relevance_of_top_listings"
    AUTOCOMPLETE_FOR_DESTINATIONS_HOTELS = "autocomplete_for_destinations_hotels"
    FIVE_PARTNERS_PER_HOTEL = "five_partners_per_hotel"
    HERO_POSITION_PARTNER_MIX = "hero_position_partner_mix"
    DISTANCE_ACCURACY = "distance_accuracy"


class ConfigLoader:
    """
    Loads and provides access to all configuration settings
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader

        Args:
            config_path: Path to config.yaml file. If None, looks in script directory.

        Raises:
            FileNotFoundError: If config.yaml is not found
            yaml.YAMLError: If config.yaml is malformed
        """
        if config_path is None:
            # Look for config.yaml next to the executable (PyInstaller) or in src
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable - look next to the executable
                app_dir = Path(sys.executable).parent
                config_path = app_dir / "config.yaml"
            else:
                # Running as normal Python script - look in same directory (src)
                src_dir = Path(__file__).parent
                config_path = src_dir / "config.yaml"

        self.config_path = Path(config_path)

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please ensure config.yaml exists in the same directory as the executable."
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Error parsing configuration file {self.config_path}: {e}"
            )

        if self.config is None:
            raise ValueError(f"Configuration file is empty: {self.config_path}")

    # =========================================================================
    # Browser & Model Settings
    # =========================================================================
    # Browser config removed - now using local ReBrowser Playwright (no AWS config needed)

    def get_model_id(self) -> str:
        """Get Bedrock model ID"""
        return self.config['model']['model_id']

    def get_model_region(self) -> str:
        """Get AWS region for Bedrock model"""
        return self.config['model']['region_name']

    def get_model_temperature(self) -> float:
        """Get model temperature setting"""
        return self.config['model']['temperature']

    # =========================================================================
    # Test Parameters
    # =========================================================================

    def get_cities(self) -> List[str]:
        """Get list of cities to test"""
        return self.config['test_parameters']['cities']

    def get_checkin_checkout_offset(self) -> tuple[int, int]:
        """
        Get checkin/checkout day offsets from today

        Returns:
            Tuple of (checkin_offset, checkout_offset)
        """
        cc = self.config['test_parameters']['checkin_checkout']['next_day_one_night']
        return (cc['checkin_offset'], cc['checkout_offset'])

    # =========================================================================
    # Website Configurations
    # =========================================================================

    def get_enabled_websites(self) -> List[Dict[str, Any]]:
        """
        Get list of all defined websites with their configurations
        Note: 'enabled' flag removed - all websites with URLs are returned
        Which websites actually run is controlled by features config

        Returns:
            List of dicts with 'key', 'url' for each website
        """
        websites = []
        for site_name, site_config in self.config['websites'].items():
            if site_config.get('url'):
                websites.append({
                    'key': WebsiteKey(site_name),
                    'url': site_config['url']
                })
        return websites

    def get_website_url(self, website_key: WebsiteKey) -> Optional[str]:
        """Get URL for a specific website"""
        site_config = self.config['websites'].get(website_key.value)
        return site_config['url'] if site_config else None

    def is_website_enabled(self, website_key: WebsiteKey) -> bool:
        """Check if a website is defined (has a URL)
        Note: 'enabled' flag removed - this now just checks if website exists"""
        site_config = self.config['websites'].get(website_key.value)
        return bool(site_config and site_config.get('url')) if site_config else False

    # =========================================================================
    # Features
    # =========================================================================

    def get_enabled_features(self) -> List[Feature]:
        """
        Get list of enabled features

        Returns:
            List of Feature enums
        """
        features = []
        for feature_name, feature_config in self.config['features'].items():
            if feature_config.get('enabled', False):
                features.append(Feature(feature_name))
        return features

    def is_feature_enabled(self, feature: Feature) -> bool:
        """Check if a feature is enabled"""
        feature_config = self.config['features'].get(feature.value)
        return feature_config.get('enabled', False) if feature_config else False

    # =========================================================================
    # Feature-Specific Websites (Special Logic)
    # =========================================================================

    def get_feature_websites(self, feature: Feature) -> List[Dict[str, Any]]:
        """
        Get websites to test for a specific feature
        Reads from feature's 'websites' config if specified, otherwise uses all enabled sites

        Args:
            feature: Feature enum

        Returns:
            List of enabled websites appropriate for this feature
        """
        feature_config = self.config['features'].get(feature.value, {})
        specified_websites = feature_config.get('websites', [])

        # If websites list is empty or not specified, use all defined websites
        if not specified_websites:
            return self.get_enabled_websites()

        # Otherwise, use the specified websites (feature-level list is authoritative)
        websites = []
        for website_name in specified_websites:
            try:
                website_key = WebsiteKey(website_name)
                url = self.get_website_url(website_key)
                if url:
                    websites.append({
                        'key': website_key,
                        'url': url
                    })
                else:
                    print(f"⚠️  Warning: Website '{website_name}' specified for feature {feature.value} but has no URL configured")
            except ValueError:
                # Invalid website name in config, skip it
                print(f"⚠️  Warning: Invalid website '{website_name}' specified for feature {feature.value}")
                continue

        return websites

    # =========================================================================
    # Site-Specific Instructions
    # =========================================================================

    def get_site_instructions(self, website_key: WebsiteKey) -> str:
        """
        Get site-specific instructions for browser agent

        Args:
            website_key: WebsiteKey enum

        Returns:
            Instructions string (may be empty)
        """
        return self.config['site_instructions'].get(website_key.value, "")

    # =========================================================================
    # Feature Prompts
    # =========================================================================

    def get_feature_prompt(
        self,
        feature: Feature,
        destination: str,
        checkin_date: str,
        checkout_date: str
    ) -> str:
        """
        Get feature prompt with variables substituted

        Args:
            feature: Feature enum
            destination: City/destination name
            checkin_date: Check-in date string (YYYY-MM-DD)
            checkout_date: Check-out date string (YYYY-MM-DD)

        Returns:
            Feature prompt with variables filled in
        """
        prompt_template = self.config['feature_prompts'].get(feature.value, "")
        return prompt_template.format(
            destination=destination,
            checkin_date=checkin_date,
            checkout_date=checkout_date
        )

    # =========================================================================
    # Common Prompts
    # =========================================================================

    def get_browser_agent_system_prompt(self) -> str:
        """Get system prompt for browser agent"""
        return self.config['prompts']['browser_agent_system']

    def get_quality_evaluator_system_prompt(self) -> str:
        """Get system prompt for quality evaluator agent"""
        return self.config['prompts']['quality_evaluator_system']

    # =========================================================================
    # Output Settings
    # =========================================================================

    def get_output_base_directory(self) -> str:
        """Get base output directory name"""
        return self.config['output']['base_directory']

    def get_text_recording_dir(self) -> str:
        """Get text recording subdirectory name"""
        return self.config['output']['text_recording_dir']

    def get_comparison_analysis_dir(self) -> str:
        """Get comparison analysis subdirectory name"""
        return self.config['output']['comparison_analysis_dir']


# Global config instance
_config_instance: Optional[ConfigLoader] = None


def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Get global config instance (singleton pattern)

    Args:
        config_path: Optional path to config file (only used on first call)

    Returns:
        ConfigLoader instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    return _config_instance


# Convenience function for backward compatibility
def load_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Load configuration from file

    Args:
        config_path: Path to config.yaml (optional)

    Returns:
        ConfigLoader instance
    """
    return get_config(config_path)


if __name__ == "__main__":
    # Test config loading
    try:
        config = load_config()
        print("✅ Configuration loaded successfully!")
        print(f"\nEnabled websites: {[w['key'].value for w in config.get_enabled_websites()]}")
        print(f"Enabled features: {[f.value for f in config.get_enabled_features()]}")
        print(f"Test cities: {config.get_cities()}")
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)
