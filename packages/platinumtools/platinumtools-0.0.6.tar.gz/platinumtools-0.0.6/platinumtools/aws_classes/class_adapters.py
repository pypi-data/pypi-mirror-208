
from abc import ABC, abstractmethod
from typing import List
from platinumtools.dda_models import *
from platinumtools.aws_classes.class_helpers import OrganizationalQuerier
from platinumtools.dda_constants import *

import uuid

class ToSocketAdapter:
    def __init__():
        pass

    @abstractmethod
    def prepare():
        pass

    def publish():
        # Calls lambda iwth this.
        pass

    @abstractmethod
    def populateCredentials():
        pass

    
    
class Audit365ToSocketAdaptor(ToSocketAdapter):

    def __init__(self, organization_querier: OrganizationalQuerier):
        self.organization_querier = organization_querier

    def prepare():
        # Using the right credentials it populates a list with that body

        # Call transform and receive the information to be published

        pass
    
    def transform(organization_querier: OrganizationalQuerier, rawAPIBodies: dict)-> dict: 
        """Converts dictionary with raw details into dictionary with File Interface details. 

        Args:
            organization_querier (OrganizationalQuerier): to fech the required data to populate into the interface
            rawAPIBodies (dict): dict implementing the staging_events interface

        Returns:
            dict: dict implemeneting staging_events interface but now tih details implementing List of File
        """

        management_api = ManagementAPIStagingModel()
    

        organization_params = organization_querier.getOrganizationParameters_365(
            orgnaization_guid_365=management_api.organization_guid )
        
        OrganizationId = organization_params["organization_id"]
        management_api.organization_guid=OrganizationId
        management_api.actor=rawAPIBodies[0]["ObjectId"]
        management_api.item_count = len(rawAPIBodies)
        management_api.details = rawAPIBodies
        # management_api.actor=rawAPIBodies[0]["Operation"]



        return management_api.to_dict()
    
    def populateCredentials():
        # In the case of 365 it needs the credentials to the objects with the actual data.
        pass



