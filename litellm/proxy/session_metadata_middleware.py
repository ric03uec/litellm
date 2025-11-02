"""
Session Metadata Middleware for LiteLLM Proxy

This middleware automatically injects session metadata from environment variables
into request metadata, which then becomes span attributes in Phoenix traces.
"""
import os
from typing import Any, Dict, Optional
from litellm._logging import verbose_proxy_logger


def inject_session_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject session metadata from environment variables into request metadata.

    This allows Phoenix to filter traces by session attributes.

    Environment Variables:
        PHOENIX_SESSION_ID: Unique session identifier
        PHOENIX_SESSION_TYPE: Workflow type (code-review, debugging, etc.)
        PHOENIX_PROMPT_VERSION: Prompt version (v1, v2, v3)
        PHOENIX_SESSION_NAME: Optional descriptive name

    Returns:
        Modified data dict with session metadata injected
    """
    # Get session metadata from environment
    session_id = os.getenv("PHOENIX_SESSION_ID")
    session_type = os.getenv("PHOENIX_SESSION_TYPE", "general")
    prompt_version = os.getenv("PHOENIX_PROMPT_VERSION", "v1")
    session_name = os.getenv("PHOENIX_SESSION_NAME")

    # Session data must go into litellm_params["metadata"]["metadata"] to flow into requester_metadata
    # Initialize litellm_params metadata structure if not present
    if "litellm_params" not in data:
        data["litellm_params"] = {}
    if "metadata" not in data["litellm_params"]:
        data["litellm_params"]["metadata"] = {}
    if "metadata" not in data["litellm_params"]["metadata"]:
        data["litellm_params"]["metadata"]["metadata"] = {}

    # Inject session metadata into the nested metadata dict
    # This will become standard_logging_payload["metadata"]["requester_metadata"]
    if session_id:
        data["litellm_params"]["metadata"]["metadata"]["session_id"] = session_id
        print(f"[SESSION] Injected session_id into litellm_params: {session_id}", flush=True)
        verbose_proxy_logger.info(f"[SESSION] Injected session_id: {session_id}")

    if session_type:
        data["litellm_params"]["metadata"]["metadata"]["session_type"] = session_type
        print(f"[SESSION] Injected session_type into litellm_params: {session_type}", flush=True)
        verbose_proxy_logger.info(f"[SESSION] Injected session_type: {session_type}")

    if prompt_version:
        data["litellm_params"]["metadata"]["metadata"]["session_prompt_version"] = prompt_version
        print(f"[SESSION] Injected session_prompt_version into litellm_params: {prompt_version}", flush=True)
        verbose_proxy_logger.info(f"[SESSION] Injected session_prompt_version: {prompt_version}")

    if session_name:
        data["litellm_params"]["metadata"]["metadata"]["session_name"] = session_name
        print(f"[SESSION] Injected session_name into litellm_params: {session_name}", flush=True)
        verbose_proxy_logger.info(f"[SESSION] Injected session_name: {session_name}")

    return data
