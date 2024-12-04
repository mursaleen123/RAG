# Standard Libraries
from datetime import timedelta

# Django Settings
from django.conf import settings

# Azure Search Libraries
from azure.search.documents.indexes.models import (
    SimpleField, SearchFieldDataType, SearchableField,
    SearchIndex, SearchIndexer, IndexingSchedule
)

# Azure Search Libraries
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient


def create_search_index(index_name, credential):
    '''
    Function to create an Index connected to a existing Data source.

    index_name: (str) Name of the index
    credential: Connection to AzureKeyCredential by Api key identity
    '''

    try:
        # Create a search schema
        index_client = SearchIndexClient(endpoint=settings.RAG_ENDPOINT, credential=credential)

        # Define the index schema
        index_schema = SearchIndex(
            name=index_name,
            fields=[
                # Document unique ID
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),

                # File name and content
                SearchableField(name="metadata_spo_item_name", type=SearchFieldDataType.String, searchable=True, retrievable=True),
                SearchableField(name="content", type=SearchFieldDataType.String, searchable=True, retrievable=True),

                # Metadata fields
                SimpleField(name="metadata_spo_item_last_modified", type=SearchFieldDataType.DateTimeOffset, filterable=True, facetable=True),

                # SharePoint-specific fields
                SimpleField(name="metadata_spo_item_content_type", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="metadata_spo_item_size", type=SearchFieldDataType.Int64, filterable=True, facetable=True),
                SimpleField(name="metadata_spo_item_path", type=SearchFieldDataType.String, searchable=False)
            ]
            # ,
            # # Optional: define suggesters for autocomplete or search suggestions
            # suggesters=[
            #     SearchSuggester(name="fileNameSuggester", source_fields=["fileName"])
            # ]
        )

        # Create or update the index
        index_client.create_or_update_index(index_schema)

        print("Index Creation completed succesfully")

    except Exception as e:
        raise Exception(f"Failed to create an Index: {e}")


def setup_indexer(indexer_name, data_source, index_name, credential):
    '''
    Function to create an Indexer to index the data in Datasource.

    indexer_name: (str) Name of the indexer
    data_source: (str) Name of the data source created.
    index_name: (str) Name of the index to target
    credential: Connection to AzureKeyCredential by Api key identity
    '''

    try:
        # Initialize the Search Indexer Client
        indexer_client = SearchIndexerClient(endpoint=settings.RAG_ENDPOINT,
            credential=credential)

        # Define the indexer
        indexer = SearchIndexer(
            name=indexer_name,
            data_source_name=data_source,
            target_index_name=index_name,
            field_mappings=[
                {
                    "sourceFieldName" : "metadata_spo_site_library_item_id",
                    "targetFieldName" : "id",
                    "mappingFunction" : {
                        "name" : "base64Encode"
                    }
                }
            ],
            schedule=IndexingSchedule(interval=timedelta(days=1)),  # Adjust the schedule as needed
        )

        # Create the indexer
        indexer_client.create_indexer(indexer)

    except Exception as e:
        raise Exception(f"Failed to create an indexer: {e}")


def run_indexer(indexer_name, credential):
    '''
    Function to run manually the indexer provided. (If there's a change in data source or new data added)
    and get the status of the indexer

    indexer_name: (str) Name of the indexer to target
    credential: Connection to AzureKeyCredential by Api key identity
    '''

    indexer_client = SearchIndexerClient(endpoint=settings.RAG_ENDPOINT, credential=credential)
    # Run the indexer manually
    indexer_client.run_indexer(indexer_name)

    print(f"Running Indexer: {indexer_client}")

    # Get the status of the indexer
    indexer_status = indexer_client.get_indexer_status(indexer_name)

    # Check the status
    print(f"Status: {indexer_status.status}")
    print(f"Errors: {indexer_status.last_result.errors}")

