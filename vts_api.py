"""
VTube Studio API Implementation - Copied from AIKA
Based on official VTS API documentation
"""

import asyncio
import json
import logging
import uuid
import websockets
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class VTSAPI:
    """VTube Studio API client following official documentation."""
    
    def __init__(self, url: str = "ws://localhost:8001/"):
        """Initialize VTS API client."""
        self.url = url
        self.ws = None
        self.connected = False
        self.authenticated = False
        self.plugin_name = "VTS-Control-Panel"
        self.plugin_developer = "VTS Control Panel"
        self.authentication_token = None
        self.request_id = 0
        self.pending_requests = {}
        
    async def connect(self) -> bool:
        """Connect to VTube Studio WebSocket."""
        try:
            logger.info(f"Connecting to VTube Studio at {self.url}")
            self.ws = await websockets.connect(self.url)
            self.connected = True
            logger.info("Connected to VTube Studio")
            
            # Start message listener
            asyncio.create_task(self._message_listener())
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to VTube Studio: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from VTube Studio."""
        if self.ws:
            await self.ws.close()
            self.ws = None
        self.connected = False
        self.authenticated = False
        logger.info("Disconnected from VTube Studio")
    
    async def _message_listener(self):
        """Listen for incoming messages from VTube Studio."""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.connected = False
        except Exception as e:
            logger.error(f"Error in message listener: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming messages from VTube Studio."""
        message_type = data.get("messageType")
        request_id = data.get("requestID")
        
        # Handle responses to our requests
        if request_id and request_id in self.pending_requests:
            future = self.pending_requests.pop(request_id, None)
            if future and not future.done():
                future.set_result(data)
        
        # Handle specific message types
        if message_type == "AuthenticationResponse":
            self.authenticated = data.get("data", {}).get("authenticated", False)
            if self.authenticated:
                logger.info("Successfully authenticated with VTube Studio")
            else:
                logger.warning("Authentication failed")
        
        elif message_type == "APIError":
            error_data = data.get("data", {})
            error_id = error_data.get("errorID")
            error_message = error_data.get("message", "Unknown error")
            logger.error(f"VTS API Error {error_id}: {error_message}")
    
    async def _send_request(self, message_type: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to VTube Studio and wait for response."""
        if not self.connected or not self.ws:
            raise Exception("Not connected to VTube Studio")
        
        request_id = str(uuid.uuid4())
        
        request = {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": request_id,
            "messageType": message_type
        }
        
        if data:
            request["data"] = data
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        try:
            # Send request
            await self.ws.send(json.dumps(request))
            logger.debug(f"Sent {message_type} request")
            
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=10.0)
            return response
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for {message_type} response")
            self.pending_requests.pop(request_id, None)
            raise Exception(f"Timeout waiting for {message_type} response")
        except Exception as e:
            logger.error(f"Error sending {message_type} request: {e}")
            self.pending_requests.pop(request_id, None)
            raise
    
    async def request_authentication_token(self) -> Optional[str]:
        """Request authentication token from VTube Studio."""
        try:
            data = {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer
            }
            
            response = await self._send_request("AuthenticationTokenRequest", data)
            
            if response.get("messageType") == "AuthenticationTokenResponse":
                token = response.get("data", {}).get("authenticationToken")
                if token:
                    self.authentication_token = token
                    logger.info("Authentication token obtained")
                    return token
                else:
                    logger.error("No authentication token in response")
                    return None
            else:
                logger.error(f"Failed to get authentication token: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error requesting authentication token: {e}")
            return None
    
    async def authenticate(self, token: str = None) -> bool:
        """Authenticate with VTube Studio using token."""
        try:
            if not token and not self.authentication_token:
                logger.error("No authentication token available")
                return False
            
            token = token or self.authentication_token
            
            data = {
                "pluginName": self.plugin_name,
                "pluginDeveloper": self.plugin_developer,
                "authenticationToken": token
            }
            
            response = await self._send_request("AuthenticationRequest", data)
            
            if response.get("messageType") == "AuthenticationResponse":
                self.authenticated = response.get("data", {}).get("authenticated", False)
                if self.authenticated:
                    logger.info("Successfully authenticated with VTube Studio")
                    return True
                else:
                    logger.warning("Authentication failed")
                    return False
            else:
                logger.error(f"Authentication failed: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return False
    
    async def create_parameter(self, name: str, explanation: str = "", min_val: float = -1.0, max_val: float = 1.0, default_val: float = 0.0) -> bool:
        """Create a new custom parameter."""
        try:
            data = {
                "parameterName": name,
                "explanation": explanation,
                "min": min_val,
                "max": max_val,
                "defaultValue": default_val
            }
            
            response = await self._send_request("ParameterCreationRequest", data)
            
            if response.get("messageType") == "ParameterCreationResponse":
                logger.info(f"Successfully created parameter: {name}")
                return True
            else:
                logger.error(f"Failed to create parameter: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating parameter: {e}")
            return False
    
    async def delete_parameter(self, name: str) -> bool:
        """Delete a custom parameter."""
        try:
            data = {"parameterName": name}
            response = await self._send_request("ParameterDeletionRequest", data)
            
            if response.get("messageType") == "ParameterDeletionResponse":
                logger.info(f"Successfully deleted parameter: {name}")
                return True
            else:
                logger.error(f"Failed to delete parameter: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting parameter: {e}")
            return False
    
    async def get_input_parameter_list(self) -> Dict[str, Any]:
        """Get list of all input parameters."""
        try:
            response = await self._send_request("InputParameterListRequest", {})
            
            if response.get("messageType") == "InputParameterListResponse":
                return response.get("data", {})
            else:
                logger.error(f"Failed to get input parameter list: {response}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting input parameter list: {e}")
            return {}
