from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

@dataclass
class IntentModel():
    """ The Intent definition contract
    """
    callback: Callable
    webhook_token: str
    node_name: str
    fallback_message: Optional[str] = None


