# Standard Libraries
import itertools

# Django
from django.conf import settings


# Models
#from MVPautomation.project.models import MethodologyModel, ProposalsModel, UseCasesModel

# Office Libraries
from pptx.util import Pt
from pptx.dml.color import RGBColor

# Utils
#from MVPautomation.sharepoint.utils.include_data_json import search_and_include_info



    '''
    Function to include Budget and general info from Proposal (Use cases)
    into Sharepoint template in Memory.
    '''

    try:
        # Return the saved Budget information from Proposal Instance Model
        proposal_info = ProposalsModel.objects.get(id=proposal_id)
        data_proposal = proposal_info.budget_info

        # Extract investment values
        key, value = data_proposal.popitem()

        # Return use cases
        use_cases = UseCasesModel.objects.filter(proposal=proposal_id)

        data = {
                '{project_price}': value['price'], '{duration}': value['duration'],
                '{considerations}': value['considerations'],
                '{solution_name}': proposal_info.solution.name if proposal_info.solution else '',
            }

        if use_cases:

            for num, use_case in enumerate(use_cases, start=1):

                temp_dict = {
                    '{usecase_name' + f"{num}" + '}': use_case.name,
                    '{usecase_description' + f"{num}" + '}': use_case.description,
                    '{usecase_situation' + f"{num}" + '}': use_case.situation,
                    '{usecase_task' + f"{num}" + '}': use_case.task,
                    '{usecase_actions' + f"{num}" + '}': use_case.action,
                    '{usecase_results' + f"{num}" + '}': use_case.results
                }

                data.update(temp_dict)

        search_and_include_info(presentation, data)

        print("Proposal file modified successfully.")

    except Exception as e:
        raise Exception(f"Replace information error: {e}")