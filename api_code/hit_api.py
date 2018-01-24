#!/usr/bin/python

import sys
import logging
import requests
import json
from   dyn365auth import Dynamics365Auth
from   connectors.dyn365conn import Dynamics365RestConnector
from   processors.dyn365map import Dynamics365Mapper

# dynamics365auth = Dynamics365Auth()
##############################################################################################################
dyn365_auth_url   = 'http://localhost:5001/api/v2.0/token'
dyn365_base_url   = 'https://lixarqa.api.crm3.dynamics.com/api/data/v8.2/'
# dynamics365Mapper = Dynamics365Mapper()
query             = 'opportunities'


# def get_created_by_fn(execution_date):
#     return DAG_NAME + "-" + get_created_date_fn(execution_date)
#
#
# def get_created_date_fn(execution_date):
#     return execution_date.strftime("%Y-%m-%dT%H:%M:%S")

access_token_key = "access_token"
response = requests.get(url=dyn365_auth_url)
try:
    response_json = response.json()
    dyn365_access_token = response_json[access_token_key]
    # print(dyn365_access_token)
except Exception as e:
    dyn365_access_token = None


def check_access_token_for_dyn365_fn():
    if dyn365_access_token is not None:
        status = "Valid"
    else:
        status = "Not-Valid"
    return status


# Get user input for desired OpportunityID
# def get_user_input():
#     opportunityid = input('Enter the Opportunity ID of desired Data:')
#     return opportunityid


def process_web_api_fn():
    # opportunityid          = get_user_input()
    test_opportunityid       = 'd50424ed-cada-e711-8127-480fcfea20c1'
    status                   = check_access_token_for_dyn365_fn()

    if status == "Valid":
        ########### CALL OPPORTUNITIES API ###########
        # https://lixarqa.api.crm3.dynamics.com/api/data/v8.2/opportunities(d5bda00a-4ea2-e711-811c-480fcfea20c1)?$select=name --> returns that oppid with name field
        # select=name,salesstage,stepname -- calls specific fields
        search               = dyn365_base_url + 'opportunities(' + test_opportunityid + ')?$select=name,_customerid_value,salesstage,stepname'
        specific_query       = query #+ '(' + test_opportunityid + ')'
        base_url             = dyn365_base_url + specific_query
        header               = {
            "Authorization": "Bearer " + dyn365_access_token,
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'Prefer': 'odata.maxpagesize=1',
            'Prefer': 'odata.include-annotations=OData.Community.Display.V1.FormattedValue'
        }
        opp_response      = requests.get(url=search, headers=header)
        opp_string        = opp_response.text  # Turns to a dict so we can't replace


        ########### CALL PROJECT API ###########
        project_search_base = 'https://lixarqa.api.crm3.dynamics.com/api/data/v8.2/psa_projects/'
        project_query = 'psa_name,_psa_opportunity_value&$filter=_psa_opportunity_value eq ' \
                        + test_opportunityid

        # Queries Projects based on OppId
        # https://lixarqa.api.crm3.dynamics.com/api/data/v8.2/psa_projects?$select=psa_name,_psa_opportunity_value&$filter=_psa_opportunity_value%20eq%20d50424ed-cada-e711-8127-480fcfea20c1
        project_search = project_search_base + '?$select=' + project_query

        project_response = requests.get(url=project_search, headers=header)
        project_string = project_response.text
        print('String: ------ ' + project_string)




        return opp_string, project_string, test_opportunityid
    else:
        print("Token Not Valid")
        sys.exit(0)


def make_pretty():                             # Will be used more to clean up stuff
    opp_string, project_string, test_opportunityid = process_web_api_fn()          # Returns the String version
    opp_json                                       = json.loads(opp_string)
    project_json                                   = json.loads(project_string)
    return opp_string, opp_json, project_string, project_json, test_opportunityid

def get_vars_based_from_json():
    opp_string, opp_json, project_string, project_json, test_opportunityid = make_pretty()

    ##### GET VARS FROM OPP JSON #####
    opportunityid           = opp_json['opportunityid']            # OppId from Opps
    _customerid_value       = opp_json['_customerid_value']        # _customerid from Opps
    salesstage              = opp_json['salesstage']               # Sales stage from Opps
    stepname                = opp_json['stepname']                 # stepname (2-Qualified) from Opps
    print('\n' + opportunityid)
    ##### GET VARS FROM PROJECT JSON #####
    # # psa_name                = project_json['psa_name']
    # psa_projectid           = project_json['psa_projectid']
    # _psa_opportunity_value  = project_json['_psa_opportunity_value']
    # # print( '\n' + psa_projectid + '\n' + _psa_opportunity_value)

def main():
    res = get_vars_based_from_json()
    # print(res)

main()