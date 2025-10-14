#!/usr/bin/env python3
"""
Quality Evaluator Agent - No Tools
Uses prompt-based evaluation by invoking the browser evaluation method
"""

import json
import logging
import sys
from datetime import datetime, timezone

from strands import Agent
from strands.models import BedrockModel
from tenacity import Retrying, stop_after_attempt, wait_exponential, retry_if_exception
from strands_browser_direct import evaluate_website_feature
from config_loader import get_config, Feature, WebsiteKey

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

# Load configuration
config = get_config()

def process_and_save_result(website_key, result, feature_key=None, city=None, checkin_checkout_offset=None):
    """Process and save a single recording result"""
    import os
    import sys

    print(f"\n🌐 Website: {website_key}")
    print("-" * 40)
    if isinstance(result, str) and "Error:" not in result:
        print(result)
    else:
        print(f"❌ {result}")

    # Convert to string values for filename
    website_key_str = website_key.value
    checkin_checkout_str = f"offset_{checkin_checkout_offset[0]}_{checkin_checkout_offset[1]}"
    city_str = city

    # Always use current working directory
    base_dir = os.getcwd()

    # Create nested directory structure using config
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(
        base_dir,
        config.get_output_base_directory(),
        config.get_text_recording_dir(),
        feature_key,
        city_str,
        checkin_checkout_str,
        website_key_str
    )
    filename = f"{timestamp}.md"

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        f.write(str(result))

    print(f"📄 Results saved to: {filepath}")


def create_quality_evaluator():
    """
    Create a Strands agent without tools that can generate evaluation prompts
    and invoke the browser evaluation method

    Returns:
        Agent: Configured Strands agent for quality evaluation
    """
    # Create explicit Bedrock model from config
    bedrock_model = BedrockModel(
        model_id=config.get_model_id(),
        region_name=config.get_model_region(),
        temperature=config.get_model_temperature()
    )

    # Create Strands agent without any tools
    agent = Agent(
        name="QualityEvaluator",
        model=bedrock_model,
        tools=[],  # No tools - pure prompt-based agent
        system_prompt=config.get_quality_evaluator_system_prompt()
    )

    return agent


def execute_website_evaluations(websites, feature_instruction, feature_key=None, city=None, checkin_checkout_offset=None):
    """Execute evaluations for all websites sequentially"""
    results = {}

    for website in websites:
        website_url = website['url']
        print(f"🔄 Starting evaluation for {website_url}")

        try:
            feature_prompt = f"""Navigate to {website_url} and execute the following:
{feature_instruction}
"""

            # Use explicit Retrying object for deterministic retry behavior
            retrying = Retrying(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=4, max=10),
                retry=retry_if_exception(Exception)
            )

            result = retrying(evaluate_website_feature, feature_prompt, website_key=website.get('key'))
            results[website_url] = result
            print(f"✅ Completed evaluation for {website_url}")

            # Process and save result immediately
            process_and_save_result(website.get('key'), result, feature_key, city, checkin_checkout_offset)

        except Exception as exc:
            print(f"❌ {website_url} generated an exception: {exc}")
            error_result = f"Error: {exc}"
            results[website_url] = error_result

            # Process and save error result immediately
            process_and_save_result(website.get('key'), error_result, feature_key, city, checkin_checkout_offset)

    return results


def generate_feature_comparison(feature, feature_instruction, websites, results, city=None, checkin_checkout_offset=None):
    """Generate comparison analysis using QualityEvaluator agent"""
    print("\n🤖 Generating comparison analysis...")
    evaluator = create_quality_evaluator()

    # Build comparison prompt for all websites
    website_results = []
    for i, website in enumerate(websites, 1):
        website_url = website['url']
        website_results.append(f"Website {i}: {website_url}")
        website_results.append(f"Results {i}: {results[website_url]}")
        website_results.append("")

    comparison_prompt = f"""
    Based on these detailed recording sessions that were produced by executing the following test request, evaluate and compare:

Feature: {feature.value.replace("_", " ").title()}

Feature checks:
{feature_instruction}

Recording Results from executing the above checks:
{"\n".join(website_results)}
    """

    comparison_result = evaluator(comparison_prompt)

    # Save comparison to file with full hierarchy: feature/city/checkin_checkout
    import os
    import sys

    # Always use current working directory
    base_dir = os.getcwd()

    city_str = city
    checkin_checkout_str = f"offset_{checkin_checkout_offset[0]}_{checkin_checkout_offset[1]}"
    output_dir = os.path.join(
        base_dir,
        config.get_output_base_directory(),
        config.get_comparison_analysis_dir(),
        feature.value,
        city_str,
        checkin_checkout_str
    )
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_filename = f"{timestamp}.md"
    comparison_filepath = os.path.join(output_dir, comparison_filename)

    with open(comparison_filepath, "w") as f:
        f.write(str(comparison_result))

    print(f"📄 Comparison analysis saved to: {comparison_filepath}")



# These functions now delegate to config loader
def get_feature_websites(feature):
    """Get websites to test for a specific feature (delegates to config)"""
    return config.get_feature_websites(feature)


def get_feature_prompt(feature, destination, checkin_date, checkout_date):
    """Get feature prompt by name with parameterized destination and dates (delegates to config)"""
    return config.get_feature_prompt(feature, destination, checkin_date, checkout_date)


if __name__ == "__main__":
    import concurrent.futures
    from datetime import datetime, timedelta
    from strands_browser_direct import evaluate_website_feature

    # Print configuration on startup
    print("=" * 80)
    print("🚀 Quality Evaluation Tool - Configuration")
    print("=" * 80)

    # Get features from config
    features = config.get_enabled_features()
    print(f"\n📋 Enabled Features: {[f.value for f in features]}")

    if not features:
        print("❌ No features enabled in config.yaml")
        sys.exit(1)

    # Print global websites configuration
    all_websites = config.get_enabled_websites()
    print(f"\n🌐 All Defined Websites: {[w['key'].value for w in all_websites]}")

    # Print feature-specific website configuration
    print("\n📊 Feature Website Mapping:")
    for feature in features:
        feature_websites = config.get_feature_websites(feature)
        print(f"  • {feature.value}:")
        if feature_websites:
            for website in feature_websites:
                print(f"    - {website['key'].value}: {website['url']}")
        else:
            print(f"    - No websites configured")

    print("\n" + "=" * 80 + "\n")

    # Get checkin_checkout offset from config
    checkin_checkout_offset = config.get_checkin_checkout_offset()

    # Calculate check-in and check-out dates from config
    today = datetime.now()
    checkin_days, checkout_days = checkin_checkout_offset
    checkin_date = (today + timedelta(days=checkin_days)).strftime("%Y-%m-%d")
    checkout_date = (today + timedelta(days=checkout_days)).strftime("%Y-%m-%d")

    # Get cities from config
    cities = config.get_cities()

    if not cities:
        print("❌ No cities configured in config.yaml")
        sys.exit(1)

    # Loop through all cities
    for city in cities:
        print(f"\n🏙️ Starting evaluation for city: {city}")

        # Loop through all features for each city
        for feature in features:
            print(f"\n🚀 Testing feature: {feature.value}")

            feature_instruction = get_feature_prompt(feature, city, checkin_date, checkout_date)
            feature_websites = get_feature_websites(feature)

            if not feature_websites:
                print(f"⚠️ No websites enabled for feature {feature.value}")
                continue

            # Execute evaluations sequentially
            results = execute_website_evaluations(feature_websites, feature_instruction, feature.value, city, checkin_checkout_offset)

            # Generate comparison analysis
            generate_feature_comparison(feature, feature_instruction, feature_websites, results, city, checkin_checkout_offset)

            print(f"✅ Completed feature: {feature.value} for city: {city}")

        print(f"✅ Completed all features for city: {city}")