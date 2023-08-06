import pytest
from platinumtools.aws_classes.class_enhancement import *
from platinumtools.dda_constants import *




@pytest.fixture
def common_processor_using_mock():

    publisher_credentials = {}
    publisher_settings = {}

    organizationDBProvider = MockOrganizationQuerier
    publishingDBProvider = MockDatabaseProvider(credentials=publisher_credentials, settings=publisher_settings)
    processor = BetterCommonProcessor(
        job_parameters={"guid": "387a26ff-ceed-5015-a6c9-a2cad90329c0" },
        organization_provider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider
    ) # Should expect for transformation Strategies to be automatically updated

    return processor

def test_picks_chrome_enhancement_instantiation(common_processor_using_mock):
    processor = common_processor_using_mock
    processor.runJobs() # Should also post at the Mock Database


def test_picks_salesforce_enhancement():
    
    organizationDBProvider = MockOrganizationQuerier
    publishingDBProvider = MockDatabaseProvider(credentials={}, settings={})
    processor = BetterCommonProcessor(
        job_parameters={"guid": "f27ecb0c-975d-dbac-82af-152b68e89902" },
        organization_provider=organizationDBProvider,
        publishingDBProvider=publishingDBProvider
    ) # Should expect for transformation Strategies to be automatically updated
    
    processor.runJobs() # Should also post at the Mock Database
