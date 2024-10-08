import pytest
import requests
from app.test.mock import admin_headers, user_headers, base_url

url = base_url + 'problems/'

#region Problem

#TODO: everything

# GET list_problems
def test_list_problems():
    # authentication
    data = {}

    response = requests.get(url=url, headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url, headers=user_headers, json=data)
    assert response.status_code == 200
    # base_functionalities
    # code_checks
    # edge_cases

# GET read_problem
def test_read_problem():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# POST create_problem
def test_create_problem():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# DELETE delete_problem
def test_delete_problem():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# PUT update_problem
def test_update_problem():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

#endregion

#region Problem Test Cases

#TODO: everything

# GET list_problem_test_cases
def test_list_problem_test_cases():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# GET get_specific_test_case
def test_lget_specific_test_case():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# POST create_problem_test_case
def test_create_problem_test_case():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# DELETE delete_problem_test_case
def test_delete_problem_test_case():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# PUT update_problem_test_case
def test_update_problem_test_case():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# endregion

#region Problem Constraints

#TODO: everything

# GET list_problem_constraints
def test_list_problem_constraints():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# GET get_specific_constraint
def test_get_specific_constraint():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# POST create_problem_constraint
def test_create_problem_constraint():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# DELETE delete_problem_constraint
def test_delete_problem_constraint():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

# PUT update_problem_constraint
def test_update_problem_constraint():
    # authentication
    # base_functionalities
    # code_checks
    # edge_cases
    pass

#endregion