
from abc import ABC, abstractmethod
from typing import List

class guardian(ABC):
    """Confirms that the uses proper interface. Also guard tokens ans so forth 
    """
    def __init__(self):
        self.detained = []


    @abstractmethod
    def inspect(self, event: dict) -> bool:
        """inspects that the passed json makes sense, calls self.detain() by default if there if doesn't pass  the tests 

        Args:
            event (str): event string to be verified

        Returns:
            bool: whether it passes as an inspected method
        """
        return True

    def filter(self, events: List[dict]) -> List[dict]:
        """Filters and returns events that are good

        Args:
            events (List[str]): events to be filtered

        Returns:
            List[str]: events to be filtered
        """
        success_events = []
        for event in events:
            cleared = self.inspect(event)
            if(cleared):
                success_events.append(event)
            else:
                self.detained.append(event)
                self.detain(event)
        return success_events
        
    @abstractmethod
    def detain(self, event:str):
        """Handling of erroneous, and potentially malicious inputs

        Args:
            event (str): event to be processed on error
        """
        pass


class BasicTokenGuardian(guardian):
    def __init__(self, token = "", token_field="token"):
        super().__init__()
        self.token = token
        self.token_field = token_field
    
    def inspect(self, event: dict) -> bool:
        token = event.get(self.token_field, '')
        return  token == self.token

    def detain(self, event: str):
        print(f"event detained: {event}")
        return super().detain(event) # Does nothing




class MockBasicTokenGuardian(guardian):
    def __init__(self, token = ""):
        super().__init__()
        self.token = token
    
    def inspect(self, event: str) -> bool:
        print(f"Inspecting: {event}")
        return super().inspect(event) # Returns True

    def detain(self, event: str):
        print(f"event detained: {event}")
        return super().detain(event) # Does nothing

