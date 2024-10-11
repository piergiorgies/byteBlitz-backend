import pytest
import requests
from app.models.mapping.problem import Problem
from app.test.mock import admin_headers, user_headers, base_url

url = base_url + 'problems/'

#region Problem

#TODO: everything

# GET list_problems
def test_list_problems():
    data = {}

    limit = 20
    offset = 0
    params = "?limit=" + str(limit) + "&offset=" + str(offset)

    # authentication
    # [**LEO**] in questa sezione si controlla che, per ogni tipologia di utente,
    # lo status code sia coerente con quello che abbiamo definito 
    response = requests.get(url=url, headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url, headers=user_headers, json=data)
    assert response.status_code == 200 #in case this could be 403/404 idk

    # base_functionalities
    # [**LEO**] in questa sezione controlliamo che l'endpoint si comporti
    # come vogliamo. In questo caso ciò significa:
    # 1. l'admin deve ricevere un json con due parametri: data e count
    # 2. l'utente deve ricevere un json uguale ma con un count inferiore
    # (deve nascondere i problemi non false)
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    #assert isinstance(problem, Problem) #TODO: to be fixed. 
    assert response.json().get("count") == 9

    response = requests.get(url=url + params, headers=user_headers, json=data)
    assert "data" in response.json() and "count" in response.json()
    assert response.json().get("count") == 5
    # code_checks
    # [**LEO**] qui invece andiamo a controllare che i controlli implementati
    # a livello di codice funzionino correttamente. In questo caso dobbiamo controllare che
    # modificando limit e offset questi vengano modificati realmente (MA COUNT DEVE RIMANERE UGUALE!!) 
    limit = 1
    offset = 2
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert len(response.json().get("data")) == 1
    assert response.json().get("count") == 9

    limit = 2
    offset = 0
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert len(response.json().get("data")) == 2
    assert response.json().get("count") == 5
    # edge_cases
    # [**LEO**] qui proviamo tutti i casi limite, principalmente quelli non realizzabili a livello di
    # frontend per rendere l'applicazione robusta (es. offset = count, limit = 0)

    limit = 0
    offset = 1
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert response.status_code == 422

    limit = 1
    offset = -1
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert response.status_code == 422

    limit = 1
    offset = 10
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert response.status_code == 422

    limit = 1
    offset = "count"
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert response.status_code == 422

# GET read_problem
def test_read_problem():
    # authentication
    response = requests.get(url=url + '3/', headers=admin_headers)
    assert response.status_code == 200
    
    response = requests.get(url=url + '1/', headers=user_headers)
    assert response.status_code == 200

    response = requests.get(url=url + '3/', headers=user_headers)
    assert response.status_code == 404
    # base_functionalities
    response = requests.get(url=url + '3/', headers=admin_headers) #TODO: to be finished.
    # code_checks
    # edge_cases

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