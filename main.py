import json
import functions_framework
import requests
from datetime import datetime, timezone
from typing import Dict, Any


def trigger_openhab_if_match(
    message: Dict[str, Any],
    openhab_url: str,
    openhab_item: str = "CameraPersonDetected",
    openhab_token: str = None,
    event_type: str = "sdm.devices.events.CameraPerson.Person",
    thread_state: str = "STARTED"
) -> bool:
    """
    Trigger OpenHAB item update if message matches event type and thread state.
    
    Args:
        message: The event message dictionary
        openhab_url: OpenHAB base URL (e.g., http://openhab.local:8080)
        openhab_item: Item name to update
        openhab_token: Optional API token for authentication
        event_type: Event type to match (default: CameraPerson.Person)
        thread_state: Thread state to match (default: STARTED)
    
    Returns:
        True if triggered, False otherwise
    """
    
    # Check if thread state matches
    if message.get("eventThreadState") != thread_state:
        print(f"Thread state mismatch: {message.get('eventThreadState')} != {thread_state}")
        return False
    
    # Check if event type matches
    resource_update = message.get("resourceUpdate", {})
    events = resource_update.get("events", {})
    
    if event_type not in events:
        print(f"Event type not found: {event_type}")
        return False
    
    # Both conditions match - trigger OpenHAB
    try:
        # Get current timestamp in ISO format
        current_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Construct OpenHAB REST API URL
        item_url = f"{openhab_url}/rest/items/{openhab_item}"
        
        # Prepare headers
        headers = {
            "Content-Type": "text/plain",
            "Accept": "application/json",
            "CF-Access-Client-Id": "",
            "CF-Access-Client-Secret": ""
        }
        
        # Add authentication if token provided
        if openhab_token:
            headers["Authorization"] = f"Bearer {openhab_token}"
        
        # Send POST request to update item state
        response = requests.post(
            item_url,
            data=current_timestamp,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        
        print(f"Successfully triggered OpenHAB item {openhab_item} with timestamp {current_timestamp}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error triggering OpenHAB: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise



@functions_framework.cloud_event
def handle_camera_event_pubsub(cloud_event):
    """
    Alternative: Cloud Run function triggered by Pub/Sub.
    
    Use this if events come through Pub/Sub instead of HTTP.
    """
    import base64
    
    openhab_url = 'https://openhab.local'
    openhab_item = 'CameraPersonDetected'
    openhab_token = ''
    
    try:
        # Decode Pub/Sub message
        message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        message_json = json.loads(message_data)
        
        # Process the message
        success = trigger_openhab_if_match(
            message=message_json,
            openhab_url=openhab_url,
            openhab_item=openhab_item,
            openhab_token=openhab_token
        )
        
        if success:
            print(f"OpenHAB item {openhab_item} triggered")
        else:
            print("Event did not match criteria")
            
    except Exception as e:
        print(f"Error processing Pub/Sub message: {str(e)}")
        raise
