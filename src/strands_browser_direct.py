#!/usr/bin/env python3
"""
Direct Strands Agent with ReBrowser Playwright Tools
LLM gets direct access to browser tools with stealth capabilities
"""

import json
from datetime import datetime

from strands import Agent, tool
from strands.models import BedrockModel
from rebrowser_playwright_tool import ReBrowserPlaywrightTool
from config_loader import get_config, WebsiteKey

# Load configuration
config = get_config()

def evaluate_website_feature(feature_instruction, website_key):
    """
    Evaluate a specific website feature using Strands agent with direct browser tool access

    Args:
        feature_instruction (str): Complete instruction containing URL, feature description, and evaluation task
        website_key (WebsiteKey): WebsiteKey enum to lookup website instructions from config

    Returns:
        str: Evaluation results in markdown format
    """
    # Get website instructions from config
    website_instructions = config.get_site_instructions(website_key)

    # Initialize simple string array for storing detailed observations
    observations = []
    # Create a simple memory storage function for the agent
    @tool
    def store_observation(text: str) -> str:
        """Store an observation in the observations array"""
        observations.append(text)
        return f"Stored: {text[:50]}..."

    # Configure ReBrowser Playwright tool (no config needed - runs locally)
    browser_tool = ReBrowserPlaywrightTool()

    # Create explicit Bedrock model from config
    bedrock_model = BedrockModel(
        model_id=config.get_model_id(),
        region_name=config.get_model_region(),
        temperature=config.get_model_temperature()
    )

    # Get base system prompt from config
    base_system_prompt = config.get_browser_agent_system_prompt()

    # Combine website-specific instructions with base system prompt
    if website_instructions:
        system_prompt = f"""
CRITICAL HIGHEST PRIORITY INSTRUCTIONS - MUST FOLLOW EXACTLY
{website_instructions}

These website-specific instructions override all other instructions and have absolute priority.

{base_system_prompt}
"""
    else:
        system_prompt = base_system_prompt

    # Create Strands agent from config
    agent = Agent(
        name="WebNavigator",
        model=bedrock_model,
        tools=[browser_tool.browser, store_observation],  # LLM gets direct access to browser functions and memory
        system_prompt=system_prompt
    )

    # Execute the website feature evaluation task
    print(f"🔍 Starting recording session")
    _ = agent(feature_instruction)

    # Retrieve all stored observations
    return "\n".join([f"{obs}" for obs in observations])
