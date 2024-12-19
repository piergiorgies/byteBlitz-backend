from re import sub
import pytest
from lorem_text import lorem
import requests
from app.test.mock import admin_headers, user_headers, base_url

url = base_url + 'problems/'

#TODO: RUN TESTS
#TODO: all this code should be adapted to the new role checking system

#region Problem

# GET list_problems
def test_list_problems():
    data = {}

    limit = 20
    offset = 0
    params = "?limit=" + str(limit) + "&offset=" + str(offset)

    # authentication
    response = requests.get(url=url, headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url, headers=user_headers, json=data)
    assert response.status_code == 200

    # base_functionalities
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert "data" in response.json() and "count" in response.json()
    assert response.json().get("count") == 9

    response = requests.get(url=url + params, headers=user_headers, json=data)
    assert "data" in response.json() and "count" in response.json()
    assert response.json().get("count") == 5
    
    # code_checks
    limit = 1
    offset = 2
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert len(response.json().get("data")) == 1
    assert response.json().get("count") == 9

    limit = 2
    offset = 0
    response = requests.get(url=url + params, headers=user_headers, json=data)
    assert len(response.json().get("data")) == 2
    assert response.json().get("count") == 5

    limit = 3
    offset = 0
    response = requests.get(url=url + params, headers=user_headers, json=data)
    assert len(response.json().get("data")) == 2
    assert response.json().get("count") == 5
    
    # edge_cases
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

    limit = "limit"
    offset = 1
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
    response = requests.get(url=url + '3/', headers=admin_headers)
    assert response.json().get("id") == 3
    assert response.json().get("name") == "Princess Kibo"
    assert response.json().get("is_public") == False

    response = requests.get(url=url + '1/', headers=user_headers)
    assert response.json().get("id") == 1
    assert response.json().get("name") == "Bonio the Painter"
    assert response.json().get("is_public") == True

    # code_checks
    response = requests.get(url=url + '11/', headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    response = requests.get(url=url + 'test/', headers=admin_headers)
    assert response.status_code == 422

    response = requests.get(url=url + '/', headers=admin_headers)
    assert response.status_code == 404

# POST create_problem
def test_create_problem():
    # authentication
    json = {"title": "JavaMaxxing", "description": "Motty needs to maximize his java skills. " + lorem.paragraph(), "points": 0, "is_public": True, "author_id": 1}
    response = requests.post(url=url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.post(url=url, headers=admin_headers, json=json)
    assert response.status_code == 201
    
    # base_functionalities
    response = requests.get(url=url + '10/', headers=admin_headers)
    assert response.json().get("title") == "JavaMaxxing"
    assert response.json().get("points") == 0
    assert response.json().get("is_public") == True

    # code_checks
    json = {"title": "JavaMaxxing", "description": "Motty needs to maximize his java skills.", "points": 0, "is_public": True, "author_id": 1}
    response = requests.post(url=url, headers=admin_headers, json=json)
    assert response.status_code == 409

    json = {"title": "JavaMaxxxing", "description": "Motty needs to maxximize his java skills.", "points": -1, "is_public": True, "author_id": 1}
    response = requests.post(url=url, headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"title": "", "description": "Motty needs to maximize his java skills.", "points": 0, "is_public": True, "author_id": 1}
    response = requests.post(url=url, headers=admin_headers, json=json)
    assert response.status_code == 422

# DELETE delete_problem
def test_delete_problem():
    # authentication
    response = requests.delete(url=url + '3/', headers=user_headers)
    assert response.status_code == 403

    response = requests.delete(url=url + '3/', headers=admin_headers)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '3/', headers=admin_headers)
    assert response.status_code == 404
    
    # code_checks
    response = requests.delete(url=url + '11/', headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    response = requests.delete(url=url + 'test/', headers=admin_headers)
    assert response.status_code == 422

# PUT update_problem
def test_update_problem():
    # authentication
    json = {"title": "Updated Title", "description": "Updated description.", "points": 10, "is_public": True, "author_id": 2}
    response = requests.put(url=url + '3/', headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.put(url=url + '3/', headers=admin_headers, json=json)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '3/', headers=admin_headers)
    assert response.json().get("title") == "Updated Title"
    assert response.json().get("description") == "Updated description."
    assert response.json().get("points") == 10
    assert response.json().get("is_public") == True
    
    # code_checks
    json = {"title": "Updated Title", "description": "Updated description.", "points": -1, "is_public": True}
    response = requests.put(url=url + '3/', headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"title": "", "description": "Updated description.", "points": 10, "is_public": True}
    response = requests.put(url=url + '3/', headers=admin_headers, json=json)
    assert response.status_code == 422

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
    # assert isinstance(problem, Problem) #TODO: to be fixed. 
    assert "data" in response.json() and "count" in response.json()
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
    response = requests.get(url=url + params, headers=user_headers, json=data)
    assert len(response.json().get("data")) == 2
    assert response.json().get("count") == 5

    limit = 3
    offset = 0
    response = requests.get(url=url + params, headers=user_headers, json=data)
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

    limit = "limit"
    offset = 1
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
    assert response.json().get("id") == 3
    # assert response.json().get("name") == "Princess Kibo"
    # assert response.json().get("description") == "Princess Kibo is a very simple problem."
    # assert response.json().get("points") == 0
    # assert response.json().get("is_public") == False
    # assert response.json().get("authon_id") == 1

    response = requests.get(url=url + '1/', headers=user_headers)
    assert response.json().get("id") == 1
    # code_checks
    response = requests.get(url=url + '11/', headers=admin_headers)
    assert response.status_code == 404
    # edge_cases
    response = requests.get(url=url + 'test/', headers=admin_headers)
    assert response.status_code == 422

    response = requests.get(url=url + '/', headers=admin_headers)
    assert response.status_code == 404

# POST create_problem
def test_create_problem():
    # authentication
    json = {"name": "JavaMaxxing", "description": "Motty needs to maximize his java skills.", "points": 0, "is_public": True, "author_id": 1}
    response = requests.post(url=url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.post(url=url, headers=admin_headers, json=json)
    assert response.status_code == 201
    
    # base_functionalities
    # code_checks
    json = {"name": "JavaMaxxing", "description": "Motty needs to maximize his java skills.", "points": 0, "is_public": True, "author_id": 1}
    response = requests.post(url=url, headers=admin_headers, json=json)
    assert response.status_code == 409

    
    # edge_cases

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

sub_url = "testcases/"
subs_url = "testcase/"

# GET list_problem_test_cases
def test_list_problem_test_cases():
    # authentication
    response = requests.get(url=url + '2/' + sub_url, headers=admin_headers)
    assert response.status_code == 200
    
    response = requests.get(url=url + '2/' + sub_url, headers=user_headers)
    assert response.status_code == 403
    
    # base_functionalities
    response = requests.get(url=url + '2/' + sub_url, headers=admin_headers)
    assert "data" in response.json() and "count" in response.json()
    
    # code_checks
    response = requests.get(url=url + '11/' + sub_url, headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    response = requests.get(url=url + 'test/' + sub_url, headers=admin_headers)
    assert response.status_code == 422

# GET get_specific_test_case
def test_get_specific_test_case():
    query_params = "?testcaseid=1"

    # authentication
    response = requests.get(url=url + '2/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 200
    
    response = requests.get(url=url + '2/' + subs_url + query_params, headers=user_headers)
    assert response.status_code == 403
    
    # base_functionalities
    response = requests.get(url=url + '2/' + subs_url + query_params, headers=admin_headers)
    assert response.json().get("id") == 1
    
    # code_checks
    response = requests.get(url=url + '11/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    query_params = "?testcaseid=test"
    response = requests.get(url=url + '2/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 422

# POST create_problem_test_case
def test_create_problem_test_case():
    # authentication
    json = {"notes": "Test case notes", "input": "input data", "output": "output data", "points": 10, "is_pretest": False}
    response = requests.post(url=url + '3/' + sub_url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.post(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 201
    
    # base_functionalities
    query_params = "?testcaseid=1"
    response = requests.get(url=url + '3/' + subs_url + query_params, headers=admin_headers)
    assert response.json().get("notes") == "Test case notes"
    assert response.json().get("input") == "input data"
    assert response.json().get("output") == "output data"
    assert response.json().get("points") == 10
    assert response.json().get("is_pretest") == False
    
    # code_checks
    json = {"notes": "Test case notes", "input": "input data", "output": "output data", "points": -1, "is_pretest": False}
    response = requests.post(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"notes": "", "input": "input data", "output": "output data", "points": 10, "is_pretest": False}
    response = requests.post(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 422

# DELETE delete_problem_test_case
def test_delete_problem_test_case():
    body = {"ids": [1]}

    # authentication
    response = requests.delete(url=url + '3/' + sub_url, headers=user_headers, data=body)
    assert response.status_code == 403

    response = requests.delete(url=url + '3/' + sub_url, headers=admin_headers, data=body)
    assert response.status_code == 200
    
    # base_functionalities
    query_params = "?testcaseid=1"
    response = requests.get(url=url + '3/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 404
    
    # code_checks
    body = {"ids": [11]}
    response = requests.delete(url=url + '3/' + sub_url, headers=admin_headers, data=body)
    assert response.status_code == 404
    
    # edge_cases
    body = {"ids": ["test"]}
    response = requests.delete(url=url + '3/' + sub_url, headers=admin_headers, data=body)
    assert response.status_code == 422

# PUT update_problem_test_case
def test_update_problem_test_case():
    json = {"notes": "Test case notes", "input": "input data", "output": "output data", "points": 10, "is_pretest": False}
    response = requests.post(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 201

    # authentication
    json = {"id": 2, "notes": "Updated notes", "input": "updated input", "output": "updated output", "points": 20, "is_pretest": False}
    response = requests.put(url=url + '3/' + sub_url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.put(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '3/' + subs_url, headers=admin_headers)
    assert response.json().get("notes") == "Updated notes"
    assert response.json().get("input") == "updated input"
    assert response.json().get("output") == "updated output"
    assert response.json().get("points") == 20
    assert response.json().get("is_pretest") == False
    
    # code_checks
    json = {"notes": "Updated notes", "input": "updated input", "output": "updated output", "points": -1, "is_pretest": False}
    response = requests.put(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"notes": "", "input": "updated input", "output": "updated output", "points": 20, "is_pretest": False}
    response = requests.put(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 422

# endregion

#region Problem Constraints

sub_url = "constraints/"
subs_url = "constraint/"

# GET list_problem_constraints
def test_list_problem_constraints():
    # authentication
    response = requests.get(url=url + '4/' + sub_url, headers=admin_headers)
    assert response.status_code == 200
    
    response = requests.get(url=url + '4/' + sub_url, headers=user_headers)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '4/' + sub_url, headers=admin_headers)
    assert "data" in response.json() and "count" in response.json()
    
    # code_checks
    response = requests.get(url=url + '11/' + sub_url, headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    response = requests.get(url=url + 'test/' + sub_url, headers=admin_headers)
    assert response.status_code == 422

# GET get_specific_constraint
def test_get_specific_constraint():
    query_params = "?languageid=3"

    # authentication
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 200
    
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=user_headers)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.json().get("problem_id") == 4
    assert response.json().get("language_id") == 3
    
    # code_checks
    query_params = "?languageid=11"
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    query_params = "?languageid=test"
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 422

# POST create_problem_constraint
def test_create_problem_constraint():
    # authentication
    json = {"language_id": 1, "memory_limit": 256, "time_limit": 2000}
    response = requests.post(url=url + '4/' + sub_url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.post(url=url + '4/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 201
    
    # base_functionalities
    query_params = "?languageid=1"
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.json().get("language_id") == 1
    assert response.json().get("memory_limit") == 256
    assert response.json().get("time_limit") == 2000
    
    # code_checks
    json = {"language_id": 1, "memory_limit": -1, "time_limit": 2}
    response = requests.post(url=url + '4/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"language_id": 1, "memory_limit": 256, "time_limit": 0}
    response = requests.post(url=url + '4/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 422

# DELETE delete_problem_constraint
def test_delete_problem_constraint():
    body = {"ids": [1]}

    # authentication
    response = requests.delete(url=url + '4/' + sub_url, headers=user_headers, data=body)
    assert response.status_code == 403

    response = requests.delete(url=url + '4/' + sub_url, headers=admin_headers, data=body)
    assert response.status_code == 200
    
    # base_functionalities
    query_params = "?testcaseid=1"
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.status_code == 404
    
    # code_checks
    body = {"ids": [11]}
    response = requests.delete(url=url + '4/' + sub_url, headers=admin_headers, data=body)
    assert response.status_code == 404
    
    # edge_cases
    body = {"ids": ["test"]}
    response = requests.delete(url=url + '4/' + sub_url, headers=admin_headers, data=body)
    assert response.status_code == 422

# PUT update_problem_constraint
def test_update_problem_constraint():
    json = {"language_id": 1, "memory_limit": 256, "time_limit": 2000}
    response = requests.post(url=url + '4/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 201

    # authentication
    json = {"language_id": 1, "memory_limit": 512, "time_limit": 4000}
    response = requests.put(url=url + '3/' + sub_url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.put(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 200
    
    # base_functionalities
    query_params = "?languageid=1"
    response = requests.get(url=url + '4/' + subs_url + query_params, headers=admin_headers)
    assert response.json().get("language_id") == 1
    assert response.json().get("memory_limit") == 512
    assert response.json().get("time_limit") == 4000
    
    # code_checks
    json = {"language_id": 1, "memory_limit": -1, "time_limit": 4}
    response = requests.put(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"language_id": 1, "memory_limit": 512, "time_limit": 0}
    response = requests.put(url=url + '3/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 422

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