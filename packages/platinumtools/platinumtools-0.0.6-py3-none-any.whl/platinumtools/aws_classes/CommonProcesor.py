from abc import ABC, abstractmethod
from typing import List
from platinumtools.aws_classes.class_helpers import *


class SourceAdapter(ABC):
    @abstractmethod
    def adapt(rows: str)->List[dict]:
        return {}

class MockAdapter(SourceAdapter):
    def adapt(body: str) -> List[dict]:
        return {"adapted": True}

class TransformationStrategy(ABC):
    """Transformation Strategy to be implemented
    """

    def transform(rows:dict)->dict:
        pass

class basicEnhancement(TransformationStrategy):
    """
    This will resource to an source adaper based on its settings, 
    then it will run an standard businessEnhancements on that.
    """
    def __init__(self, organization_querier):
        self.organization_querier = organization_querier
    
    def transform(events: List[dict]) -> dict:
        pass
        
    def businessEnhacnecement(events:List[dict]):
        pass



class CommonProcessor():
    def __init__(self, credentials, rawSourceProvider: DatabaseProvider):
        def runJobs():
            pass

        def getTransforamtionStrategy():
            pass

        def transform(body: str, transformationStrategy):
            pass

        



