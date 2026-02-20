"""
twistedpair_client.py - TwistedPair V2 REST API Client for TwistedNews

Provides interface to TwistedPair V2 server at localhost:8001
for generating commentary on news articles.

API Endpoint: POST http://localhost:8001/distort-manual
"""

import requests
import time
from typing import Optional
from dataclasses import dataclass
import logging
import config

logger = logging.getLogger(__name__)


@dataclass
class DistortionResult:
    """Result from TwistedPair distortion."""
    output: str
    mode: str
    tone: str
    gain: int
    model: str
    timestamp: str
    
    def __str__(self) -> str:
        return self.output


class TwistedPairClient:
    """Client for TwistedPair V2 API."""
    
    def __init__(self, base_url: str = None, timeout: int = None, verbose: bool = None):
        """
        Initialize TwistedPair client.
        
        Args:
            base_url: TwistedPair server URL (default from config)
            timeout: Request timeout in seconds (default from config)
            verbose: Enable debug logging (default from config)
        """
        self.base_url = base_url or config.TWISTEDPAIR_BASE_URL
        self.timeout = timeout or config.TWISTEDPAIR_TIMEOUT
        self.verbose = verbose if verbose is not None else config.VERBOSE
        self.distort_endpoint = f"{self.base_url}/distort-manual"
        self.health_endpoint = f"{self.base_url}/health"
        
    def is_healthy(self) -> bool:
        """
        Check if TwistedPair V2 server is running.
        
        Returns:
            True if server responds, False otherwise
        """
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            healthy = response.status_code == 200
            if self.verbose:
                logger.info(f"TwistedPair health check: {'online' if healthy else 'offline'}")
            return healthy
        except Exception as e:
            logger.error(f"TwistedPair health check failed: {e}")
            return False
    
    def generate_commentary(
        self,
        text: str,
        mode: str = None,
        tone: str = None,
        gain: int = None,
        model: str = None
    ) -> DistortionResult:
        """
        Generate commentary on news articles using TwistedPair V2 API.
        
        Args:
            text: Combined article content
            mode: Rhetorical mode (default from config)
            tone: Verbal style (default from config)
            gain: Intensity level 1-10 (default from config)
            model: Ollama model name (default from config)
        
        Returns:
            DistortionResult with commentary and metadata
            
        Raises:
            ConnectionError: If server is unreachable
            ValueError: If server returns error
            TimeoutError: If request times out
        """
        # Use config defaults if not provided
        mode = mode or config.TWISTEDPAIR_MODE
        tone = tone or config.TWISTEDPAIR_TONE
        gain = gain or config.TWISTEDPAIR_GAIN
        model = model or config.OLLAMA_MODEL
        
        # Validate inputs
        if mode not in config.DISTORTION_MODES:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {config.DISTORTION_MODES}")
        
        if tone not in config.DISTORTION_TONES:
            raise ValueError(f"Invalid tone: {tone}. Must be one of {config.DISTORTION_TONES}")
        
        if not (1 <= gain <= 10):
            raise ValueError(f"Invalid gain: {gain}. Must be between 1 and 10")
        
        # Build request payload
        payload = {
            "text": text,
            "mode": mode,
            "tone": tone,
            "gain": gain,
            "model": model
        }
        
        # Add num_ctx if configured
        if hasattr(config, 'OLLAMA_NUM_CTX'):
            payload["num_ctx"] = config.OLLAMA_NUM_CTX
        
        logger.info(f"Generating commentary with mode={mode}, tone={tone}, gain={gain}, model={model}")
        if self.verbose:
            logger.debug(f"Input length: {len(text)} characters")
            logger.debug(f"Input preview: {text[:200]}...")
        
        try:
            # Send request
            start_time = time.time()
            response = requests.post(
                self.distort_endpoint,
                json=payload,
                timeout=self.timeout
            )
            elapsed = time.time() - start_time
            
            # Check response
            if response.status_code != 200:
                error_msg = f"TwistedPair API error: {response.status_code}"
                try:
                    error_detail = response.json().get("detail", response.text)
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                raise ValueError(error_msg)
            
            # Parse response
            data = response.json()
            
            # Extract output - handle both string and nested dict formats
            output = data.get("output", "")
            if isinstance(output, dict):
                # V2 API may return nested structure
                output = output.get("response", output.get("text", str(output)))
            
            if not isinstance(output, str):
                output = str(output)
            
            result = DistortionResult(
                output=output,
                mode=data.get("mode", mode),
                tone=data.get("tone", tone),
                gain=data.get("gain", gain),
                model=data.get("model", model),
                timestamp=data.get("timestamp", "")
            )
            
            logger.info(f"Commentary generated in {elapsed:.1f}s")
            if self.verbose:
                logger.debug(f"Output length: {len(result.output)} characters")
                logger.debug(f"Output preview: {result.output[:200]}...")
            
            return result
            
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"TwistedPair request timed out after {self.timeout}s. "
                f"Try increasing TWISTEDPAIR_TIMEOUT environment variable"
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot connect to TwistedPair at {self.base_url}. "
                f"Ensure TwistedPair V2 server is running on localhost:8001"
            )
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            raise RuntimeError(f"TwistedPair commentary generation failed: {e}")
    
    def get_available_models(self) -> list:
        """
        Get list of available Ollama models from TwistedPair server.
        
        Returns:
            List of model names, empty list if server unavailable
        """
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
        except Exception as e:
            logger.warning(f"Failed to get available models: {e}")
        
        return []
