"""
VTube Studio service - Copied from AIKA and simplified for control panel
Handles WebSocket connection and parameter control
"""

import asyncio
import logging
import json
import threading
import os
from typing import Dict, List, Optional, Any
from vts_api import VTSAPI

logger = logging.getLogger(__name__)

class VTSService:
    """VTube Studio service for parameter management."""
    
    def __init__(self, config_manager):
        """Initialize the VTS service."""
        self.config = config_manager
        self.vts_api: Optional[VTSAPI] = None
        self.connected = False
        self.authenticated = False
        self.custom_params = {}
        
        # Event loop for VTS operations - keep it persistent
        self._loop = None
        self._loop_thread = None
        
        logger.info("VTS Service initialized")
    
    def _start_event_loop(self):
        """Start persistent event loop in background thread."""
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
        
        self._loop_thread = threading.Thread(target=run_loop, daemon=True)
        self._loop_thread.start()
        
        # Wait for loop to be ready
        import time
        while self._loop is None:
            time.sleep(0.01)
        
        logger.info("Event loop started")
    
    def _stop_event_loop(self):
        """Stop the persistent event loop."""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._loop = None
        logger.info("Event loop stopped")
    
    async def connect(self) -> bool:
        """Connect to VTube Studio."""
        try:
            # Get connection settings from config
            api_url = self.config.get_string('VTS', 'api_url', 'ws://localhost:8001/')
            
            # Create VTS API instance
            self.vts_api = VTSAPI(api_url)
            
            # Connect to VTube Studio
            if not await self.vts_api.connect():
                logger.error("Failed to connect to VTube Studio")
                return False
            
            logger.info("VTS WebSocket connection established")
            
            # Check if we have a saved token
            token = self.config.get_string('VTS', 'auth_token', '')
            
            if token:
                # Try to authenticate with saved token
                if await self.vts_api.authenticate(token):
                    self.authenticated = True
                    logger.info("Authenticated with saved token")
                else:
                    logger.warning("Saved token invalid, requesting new token")
                    token = await self.vts_api.request_authentication_token()
                    if token:
                        self.config.set_value('VTS', 'auth_token', token)
                        self.config.save()
                        if await self.vts_api.authenticate(token):
                            self.authenticated = True
                            logger.info("Authenticated with new token")
            else:
                # Request new token
                token = await self.vts_api.request_authentication_token()
                if token:
                    self.config.set_value('VTS', 'auth_token', token)
                    self.config.save()
                    if await self.vts_api.authenticate(token):
                        self.authenticated = True
                        logger.info("Authenticated with new token")
            
            if not self.authenticated:
                logger.error("Failed to authenticate with VTube Studio")
                return False
            
            self.connected = True
            logger.info("Successfully connected to VTS")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to VTS: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from VTube Studio."""
        try:
            if self.vts_api:
                await self.vts_api.disconnect()
                self.vts_api = None
            
            self.connected = False
            self.authenticated = False
            
            # Stop event loop
            self._stop_event_loop()
            
            logger.info("Disconnected from VTS")
            
        except Exception as e:
            logger.error(f"Error disconnecting from VTS: {e}")
    
    def _send_parameters_sync(self, parameters: List[Dict[str, Any]]):
        """Send parameters synchronously via WebSocket using persistent loop."""
        try:
            import json
            import uuid
            
            if not self._loop:
                logger.error("No event loop available")
                return False
            
            message = {
                "apiName": "VTubeStudioPublicAPI",
                "apiVersion": "1.0",
                "requestID": str(uuid.uuid4()),
                "messageType": "InjectParameterDataRequest",
                "data": {
                    "faceFound": False,
                    "mode": "set",
                    "parameterValues": parameters
                }
            }
            
            # Send via persistent loop
            async def send():
                try:
                    if hasattr(self.vts_api, 'ws') and self.vts_api.ws:
                        await self.vts_api.ws.send(json.dumps(message))
                        logger.debug(f"Sent {len(parameters)} parameters to VTS")
                        return True
                    else:
                        logger.warning("No WebSocket connection available")
                        return False
                except Exception as e:
                    logger.error(f"WebSocket error: {e}")
                    return False
            
            # Schedule on persistent loop
            future = asyncio.run_coroutine_threadsafe(send(), self._loop)
            result = future.result(timeout=2.0)
            return result
                
        except Exception as e:
            logger.error(f"Error sending parameters synchronously: {e}")
            return False
    
    async def create_parameter_async(
        self,
        parameter_name: str,
        explanation: str,
        min_value: float,
        max_value: float,
        default_value: float
    ) -> bool:
        """Create a custom parameter in VTube Studio."""
        if not self.vts_api:
            logger.error("VTS API not available")
            return False
        
        return await self.vts_api.create_parameter(
            name=parameter_name,
            explanation=explanation,
            min_val=min_value,
            max_val=max_value,
            default_val=default_value
        )
    
    async def delete_parameter_async(self, parameter_name: str) -> bool:
        """Delete a custom parameter."""
        if not self.vts_api:
            logger.error("VTS API not available")
            return False
        
        return await self.vts_api.delete_parameter(parameter_name)
    
    async def get_available_parameters(self) -> List[Dict[str, Any]]:
        """Get list of available parameters from VTube Studio."""
        if not self.vts_api:
            logger.error("VTS API not available")
            return []
        
        try:
            data = await self.vts_api.get_input_parameter_list()
            # Only get default parameters (Live2D params active for current model)
            default_params = data.get("defaultParameters", [])
            logger.info(f"Retrieved {len(default_params)} active model parameters")
            return default_params
        except Exception as e:
            logger.error(f"Error getting parameters: {e}")
            return []
    
    def is_authenticated(self) -> bool:
        """Check if connected and authenticated."""
        return self.connected and self.authenticated
    
    # Methods expected by VTSParamsComponent
    
    async def create_parameter(
        self,
        parameter_name: str,
        explanation: str,
        min_value: float,
        max_value: float,
        default_value: float
    ) -> bool:
        """Create parameter - async version for VTSParamsComponent."""
        if not self.is_authenticated():
            logger.warning(f"Cannot create parameter {parameter_name}: Not connected to VTS")
            return False
        
        if not self._loop:
            logger.error("No event loop available")
            return False
        
        # Run on persistent loop
        future = asyncio.run_coroutine_threadsafe(
            self.create_parameter_async(parameter_name, explanation, min_value, max_value, default_value),
            self._loop
        )
        try:
            return future.result(timeout=5.0)
        except Exception as e:
            logger.error(f"Error creating parameter: {e}")
            return False
    
    def send_parameters(self, parameters, mode="set", smoothing=False) -> bool:
        """Send parameters - async version (actually sync via thread)."""
        if not self.is_authenticated():
            logger.debug("Cannot send parameters: Not connected to VTS")
            return False
        
        # Convert dict to list if needed
        param_list = []
        if isinstance(parameters, dict):
            for name, value in parameters.items():
                param_list.append({"id": name, "value": value})
        elif isinstance(parameters, list):
            param_list = parameters
        else:
            return False
        
        return self._send_parameters_sync(param_list)
    
    def send_parameters_sync(self, parameters, mode="set", smoothing=False) -> bool:
        """Send parameters synchronously."""
        return self.send_parameters(parameters, mode, smoothing)
    
    def get_available_parameters_sync(self) -> List[Dict[str, Any]]:
        """Get available parameters synchronously."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_available_parameters())
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error getting parameters sync: {e}")
            return []
    
    def extract_vts_parameters(self) -> List[Dict[str, Any]]:
        """Extract parameters from VTS."""
        if not self.is_authenticated():
            logger.error("Not connected to VTS")
            return []
        
        return self.get_available_parameters_sync()
