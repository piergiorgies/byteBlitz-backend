import pytest
import requests
from mockup import admin_headers, user_headers, base_url

url = base_url + '/problems'

#region Problem

#TODO: everything

# GET list_problems
def test_list_problems():
    data = {}

    response = requests.get(url=url, headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url, headers=user_headers, json=data)
    assert response.status_code == 200


# GET read_problem
# POST create_problem 
# DELETE delete_problem
# PUT update_problem

#endregion

#region Problem Test Cases

#TODO: everything

# GET list_problem_test_cases
# GET get_specific_test_case
# POST create_problem_test_case
# DELETE delete_problem_test_case
# PUT update_problem_test_case

# endregion

#region Problem Constraints

#TODO: everything

# GET list_problem_constraints
# GET get_specific_constraint
# POST create_problem_constraint
# DELETE delete_problem_constraint
# PUT update_problem_constraint

#endregion