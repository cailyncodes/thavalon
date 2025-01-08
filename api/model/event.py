# event.py

import uuid
from datetime import datetime
from typing import Any, Dict


class Event:
    """
    Represents a single event in the event log.
    """

    def __init__(self, event_type: str, payload: Dict[str, Any]):
        self.event_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat() + 'Z'
        self.event_type = event_type
        self.payload = payload

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the event to a dictionary.
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """
        Deserializes an event from a dictionary.
        """
        event = cls(data["event_type"], data["payload"])
        event.event_id = data["event_id"]
        event.timestamp = data["timestamp"]
        return event
