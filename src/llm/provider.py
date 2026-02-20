import os
import sys
import logging
import litellm

logger = logging.getLogger(__name__)

# Load local environment configuration
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_llm() -> str:
    """
    Returns a model identifier optimized for LiteLLM compatibility out of the box.
    Allows mixing Open Source, Proprietary, and highly optimized Local models trivially.
    Mimics the flexibility of Cline and Kilo (e.g. OpenAI, Anthropic, OpenRouter, Ollama).
    """
    
    # 1. Primary Model String
    model_string = os.getenv("SWARM_MODEL", "openai/gpt-4o")
    
    # 2. Local Model / WebUI Support (e.g., LM Studio, Ollama, vLLM)
    custom_base = os.getenv("CUSTOM_API_BASE")
    if custom_base:
        litellm.api_base = custom_base
        logger.info(f"[LLM Router] Detected CUSTOM_API_BASE: {custom_base}. Overriding standard Litellm routing.")
        
    # 3. Simple Validation
    if model_string.startswith("anthropic/") and not os.getenv("ANTHROPIC_API_KEY"):
        logger.warning("SWARM_MODEL is Anthropic, but ANTHROPIC_API_KEY is not set.")
    elif model_string.startswith("openai/") and not os.getenv("OPENAI_API_KEY"):
        logger.warning("SWARM_MODEL is OpenAI, but OPENAI_API_KEY is not set.")
        
    logger.info(f"[LLM Router] Engaging primary engine: {model_string}")
        
    # LiteLLM parses things like "ollama/llama3" and "openrouter/claude" automatically
    # returned directly to the CrewAI LLM param
    return model_string
