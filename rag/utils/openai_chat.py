# Standard Libraries
import json

# Django settings
from django.conf import settings

# DRF
from rest_framework.response import Response
from rest_framework import status

# Open AI
from openai import AzureOpenAI

# Models
# from MVPautomation.project.models import MethodologyModel, ProposalsModel

# Utils
from sharepoint.utils import get_all_values


def create_chat(GROUNDED_PROMPT, example, query, sources_formatted):
    '''
    Function to create an instance for OpenAI client and initiate chat with a specific prompt
    '''
    print(f"GROUNDED_PROMPT is in the obkect : {GROUNDED_PROMPT}")
    print(f"sources_formatted is in the obkect : {sources_formatted}")

    # Initiate Open AI service
    openai_client = AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version="2024-02-01",
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
    )

    # Create OpenAI chat
    try:
        response = openai_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": GROUNDED_PROMPT.format(example=example, query=query, sources=sources_formatted)
                }
            ],
            model=settings.AZURE_DEPLOYMENT_MODEL,
            temperature=0.2
        )

        print(" ---- The following are the results of the CHATGPT QUERY ----")

        data = response.choices[0].message.content 
        print(f"Data is in the obkect : {data}")
        try:
            clean_data = data.strip('```json\n```')
            data_json = json.loads(clean_data)

        except Exception as inner_exception:
            print(f"Error during JSON parsing: {inner_exception}")
            return data, False

        return data_json, True

    except Exception as e:
        print(f'Error in chat GPT query: {e}')
        raise Exception(f"Error in chat GPT query: {e}")



def converted_to_chunks(results):
    '''
    Function to convert the results into chunks with a maximum content length of 1000 characters.

    results: List of documents to process

    Returns: Formatted sources in chunks
    '''
    current_batch = []

    # Process results in chunks of 10
    for count, each_file in enumerate(results, start=1):
        current_batch.append(each_file)

        if len(current_batch) == 10:
            sources_formatted = "\n".join([f'{document["metadata_spo_item_name"]}:{document["content"][:1000]}:{document["metadata_spo_item_path"]}' for document in current_batch])
            
            # Clear the batch for the next chunk
            current_batch = []
            return sources_formatted

    # For the last batch if not a multiple of 10
    if current_batch:
        sources_formatted = "\n".join([f'{document["metadata_spo_item_name"]}:{document["content"][:1000]}:{document["metadata_spo_item_path"]}' for document in current_batch])
        return sources_formatted

    return ""


def create_prompt_request(data, action, results, proposal=None):
    '''
    Function to create prompt based on the request made and pass the results to OpenAI chat.

    data: JSON object with data to search into
    action: string - action to be performed
    results: File Results from semantic search
    proposal: Optional - Proposal model (if needed for some actions)
    '''
   
    keywords = data.get('keywords')

    # Validate when a proposal instance is included and pass to the query
    # if isinstance(proposal, ProposalsModel):
    #     methodology = MethodologyModel.objects.get(proposal_id=proposal)

    try:
        if action == 'summarize':
            query = f"Provide an accurate and comprehensive summary of the given documents in at least 5 paragraphs. Use the content examined in the documents to include main information such as the client name, industries mentioned, solutions provided, and the purpose of the content. Ensure the summary encapsulates the key aspects clearly and fluently. Retain the original filename and file path exactly as given."

            example = "[{ \"metadata_spo_item_name\": filename, \"metadata_spo_item_path\": file_path, \"content\": summarize content }, { \"metadata_spo_item_name\": filename, \"metadata_spo_item_path\": file_path, \"content\": summarize content}, ...]"

            GROUNDED_PROMPT = """
            Act as an expert consultant specializing in summarizing and analyzing text and documents.
            The summary should cover all the key points and main ideas presented in the original document, while avoiding any unnecessary information or repetition. Ensure that all information presented comes exclusively from the document, without adding or inventing content.
            Please provide the summarize for each file wrap in a list with JSON format.
            Output example:\n{example}
            Query: {query}
            Sources:\n{sources}
            """
            sources_formatted = converted_to_chunks(results)

        elif action == 'context_ai':
            query = f"Search for files related to {proposal.dealname} - {proposal.client_name}. Generate the next content, consider that for (Context) I need a context description paragraph about the overall documents provided, for (Main_goal) infer from the input documents the main market research goal that summarizes the main need of the client for the proposal, lastly for (Specific_goals) infer 3 specific goals from the input documents that complement with the (Main_goal)."

            example = "[{ \"Context\": file context, \"Main_goal\": file main goal, \"Specific_goals\": \"Goal 1\": goal 1, \"Goal 2\": goal 2, \"Goal 3\": goal 3 }]"

            GROUNDED_PROMPT = """
            Act as an expert market research consultant focused on client proposals. Based on the documents provided in this query,
            your task is to generate the next content <content>.
            Do not generate answers that don't use the sources below.
            Please provide the answers wrap in a list with JSON format
            <content>
            # Context:
            # Main goal:
            # Specific goals:
            - Goal 1
            - Goal 2
            - Goal 3
            </content>
            Query: {query}
            Sources:\n{sources}
            """
            sources_formatted = converted_to_chunks(results)

        elif action == 'advanced_search':
            print("Data set", data)
            print("Results set", results)

            # query = f"Search for files related to {keywords}, using any combination of these filters. Display the 5 most relevant results, including for each: file name, path and a three-sentence summary of the content. If no exact matches, don't suggest related files. Analyze not only the file name but the content to search the keywords in it."
            query = f"Search for files related to {keywords}. Display the 5 most relevant results, showing their file name, path, and a brief three-sentence summary. If no exact matches are found, do not suggest related files. Analyze both the file name and the content to search for the keywords."

            example = "[{ \"file_name\": filename, \"path\": file_path, \"summary\": file_summary }, { \"file_name\": filename, \"path\": file_path, \"summary\": file_summary }, ...]"

            GROUNDED_PROMPT = """
            You are an AI assistant specialized in analyzing file contexts and retrieving relevant information.
            Answer ONLY with the facts listed in the list of sources below.
            Do not generate answers that don't use the sources below.
            Please provide the answers wrap in a list with JSON format with their specific key and value to identify.
            If you don't have enough resources say that you don't know.
            Output example:\n{example}
            Query: {query}
            Sources:\n{sources}
            """
            sources_formatted = converted_to_chunks(results)

        elif action == 'use_cases':
            query = f"Retrieve relevant information for use cases from our sources, considering the client's industry, similar clients, and the type of project (service and activities) to be performed. Organize each selected use case into four concise paragraphs: Name (Name of the project), Description (Brief description about the project made in use case),Situation (Briefly describe the initial client scenario or challenge), Task (Outline the specific objectives or requirements of the project), What we did (Summarize our approach and key actions taken), and Results (Highlight the concrete outcomes and benefits achieved). Focus on clear, impactful information that demonstrates value to prospective clients."

            example = "[{ \"name\": usecase name, \"Description\": usecase description, \"Situation\": usecase situation, \"Task\": usecase task, \"What we did\": usecase summary or approach, \"Results\": usecase results }, { \"name\": usecase name, \"Description\": usecase description, \"Situation\": usecase situation, \"Task\": usecase task, \"What we did\": usecase summary or approach, \"Results\": usecase results }, ...]"

            GROUNDED_PROMPT = """
            You are an AI assistant specialized in analyzing file contexts and retrieving relevant information for use cases.
            Answer ONLY with the facts listed in the list of sources below.
            Do not generate answers that don't use the sources below.
            Please provide the answers in JSON format with their specific key and value to identify.
            If you don't have enough resources say that you don't know.
            Output example:\n{example}
            Query: {query}
            Sources:\n{sources}
            """
            sources_formatted = converted_to_chunks(results)

        elif action == 'backup_slides':
            query = f'Extract the information on the most relevant file and Provide an accurate and comprehensive long summary with the main ideas.'

            example = "{ \"main ideas\": [example1, example2], \"summary\": long summary of the file, \"specific ideas\": main ideas }"

            GROUNDED_PROMPT = """
            I am an AI assistant designed to help users find information efficiently.
            Based on the following information, return the content information from the file.
            Answer ONLY with the facts listed in the list of sources below.
            Do not generate answers that don't use the sources below.
            If you don't have enough resources say that you don't know.
            Output example:\n{example}
            Query: {query}
            Sources:\n{sources}
            """
            sources_formatted = converted_to_chunks(results)

        elif action == 'knowledge_center':
            return large_search_advanced(results, data)

        else:
            raise ValueError(f"Action {action} is not supported.")
        
        # Create the chat response using the generated prompt
        chat_response, state = create_chat(GROUNDED_PROMPT, example, query, sources_formatted)

        return chat_response, state

    except Exception as e:
        # If any error occurs, catch the exception and return the error message
        error_message = f"Error occurred while creating the prompt: {str(e)}"
        print(error_message)
        return {"error": error_message}


def large_search_advanced(results, data):
    '''
    Function to process large searches with multiple request to OpenAI (Make sure is always multiple of 10)

    - results:
    - data:

    - Return: None action return
    '''
    keywords = data.get('keywords')

    current_batch = []

    files_summarize = []

    query = f"Find the most accurate documents in the list provided in \"Sources\" that match with the {keywords}"

    example = "[{ \"metadata_spo_item_name\": filename, \"metadata_spo_item_path\": file_path }, { \"metadata_spo_item_name\": filename, \"metadata_spo_item_path\": file_path}, { \"metadata_spo_item_name\": filename, \"metadata_spo_item_path\": file_path }, ...]"

    GROUNDED_PROMPT="""
    You are an AI assistant specialized in analyzing file contexts and retrieving relevant information from the input files provided by the user.
    Your task is to determine the most accurate path and file name that match with the query request "Query"
    Adhere to the following criteria:\n1.Answer ONLY with the documents listed in the list of "Sources" below.\n2.Avoid to generate new content, just work with the files provided in "Sources".\n3.Please provide the answers wrap in a list with dictionaries format like the example <example>.\n4.If you don't have enough resources just answer ['Can't find mathches, insufficient sources provided'].
    Answer ONLY with the facts listed in the list of sources below.
    Expected Output:\n{example}
    Query: {query}
    Sources:\n{sources}
    """


    for count, each_file in enumerate(results, start=1):
        current_batch.append(each_file)

        if len(current_batch) == 10:

            # Include the results documents in the Prompt - Limit the con tent to 1000 tokens to speed the search
            sources_formatted = "\n".join([f'{document["metadata_spo_item_name"]}:{document["content"][:1000]}:{document["metadata_spo_item_path"]}' for document in current_batch])

            chat_response, state = create_chat(GROUNDED_PROMPT, example, query, sources_formatted)

            # Save each chunks of files
            if state is not False:
                files_summarize.extend(chat_response)

            # Restart the list
            current_batch = []

    return files_summarize, True
