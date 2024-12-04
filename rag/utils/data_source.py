# Standard Libraries

# Django Settings
from django.conf import settings

# Azure Search Libraries
from azure.search.documents.indexes.models import (
    SearchIndexerDataSourceConnection, SearchIndexerDataContainer,
    SimpleField, SearchFieldDataType, SearchableField,
    SearchIndex
)
from azure.search.documents.indexes import SearchIndexerClient


def create_connection_data_source(data_source, credential):
    '''
    Function to create a Data source in RAG instance
    The function will target a library in sharepoint where all the files will be indexed to collect data.
    datasource: (str) Name of the data source
    credential: Connection to AzureKeyCredential by Api key identity
    '''

    try:
        # Initialize the Search Indexer Client
        search_indexer_client = SearchIndexerClient(
            endpoint=settings.RAG_ENDPOINT,
            credential=credential
        )

        # Define the data source connection
        data_source_connection = SearchIndexerDataSourceConnection(
            name=data_source,
            type="sharepoint",
            connection_string=f"SharePointOnlineEndpoint=https://{settings.sharepoint_path}/sites/{your-organization-name};ApplicationId={settings.APPLICATION_ID};ApplicationSecret={settings.API_KEY};TenantId={settings.TENANT_ID}",

            container = {
                "name" : "useQuery",
                # The query parameter is used to specify the SharePoint library to index
                "query" : "includeLibrary=https://{settings.sharepoint_path}/sites/{your-organization-name}/Prueba/Forms/AllItems.aspx"
            },
            description="SharePoint Data source"
        )

        # Creates the data source
        search_indexer_client.create_data_source_connection(data_source_connection)
        print("SharePoint Data source created successfully.")

    except Exception as e:
        raise Exception(f"Creation Data source error: {e}")


def get_datasource_connection(data_source, credential):
    '''
    Get a Data source connection if needed
    datasource: (str) Name of the data source created previously
    credential: Connection to AzureKeyCredential by Api key identity
    '''

    # Initialize the Search Indexer Client
    indexer_client = SearchIndexerClient(
        endpoint=settings.RAG_ENDPOINT,
        credential=credential
    )

    # Get the data source connection
    indexer_client.get_data_source_connection(data_source)
