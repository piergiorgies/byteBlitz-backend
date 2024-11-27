import pytest
import requests
from app.test.mock import admin_headers, user_headers, base_url

url = base_url + 'users/'

#TODO: RUN TESTS
#TODO: all this code should be adapted to the new role checking system

# GET list_users
def test_list_users():
    data = {}

    limit = 20
    offset = 0
    params = "?limit=" + str(limit) + "&offset=" + str(offset)

    # authentication
    response = requests.get(url=url, headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url, headers=user_headers, json=data)
    assert response.status_code == 403

    # base_functionalities
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert "data" in response.json() and "count" in response.json()
    assert response.json().get("count") == 5

    # code_checks
    limit = 1
    offset = 2
    response = requests.get(url=url + params, headers=admin_headers, json=data)
    assert len(response.json().get("data")) == 1
    assert response.json().get("count") == 5

    limit = 2
    offset = 0
    response = requests.get(url=url + params, headers=admin_headers, json=data)
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

# GET read_user
def test_read_user():
    # authentication
    response = requests.get(url=url + '1/', headers=admin_headers)
    assert response.status_code == 200
    
    response = requests.get(url=url + '2/', headers=user_headers)
    assert response.status_code == 403

    response = requests.get(url=url + '3/', headers=user_headers)
    assert response.status_code == 403

    # base_functionalities
    response = requests.get(url=url + '1/', headers=admin_headers)
    assert response.json().get("id") == 1
    assert response.json().get("username") == "admin"

    response = requests.get(url=url + '2/', headers=admin_headers)
    assert response.json().get("id") == 2
    assert response.json().get("username") == "user"

    # code_checks
    response = requests.get(url=url + '11/', headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    response = requests.get(url=url + 'test/', headers=admin_headers)
    assert response.status_code == 422

# DELETE delete_user
def test_delete_user():
    json = {"username": "new_user", "email": "new_user@user.com", "password": "new_user123"}
    response = requests.post(url=base_url + 'auth/signup/', headers=admin_headers, json=json)
    assert response.status_code == 201

    # authentication
    response = requests.delete(url=url + '6/', headers=user_headers)
    assert response.status_code == 403

    response = requests.delete(url=url + '6/', headers=admin_headers)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '6/', headers=admin_headers)
    assert response.status_code == 404
    
    # code_checks
    response = requests.delete(url=url + '11/', headers=admin_headers)
    assert response.status_code == 404
    
    # edge_cases
    response = requests.delete(url=url + 'test/', headers=admin_headers)
    assert response.status_code == 422

# PATCH update_user_data
def test_update_user_data():
    json = {"username": "new_user", "email": "new_user@user.com", "password": "new_user123"}
    response = requests.post(url=base_url + 'auth/signup/', headers=admin_headers, json=json)
    assert response.status_code == 201

    # authentication
    json = {"username": "updated_user", "password": "updated_user123"}
    response = requests.patch(url=url + '7/', headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.patch(url=url + '7/', headers=admin_headers, json=json)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '7/', headers=admin_headers)
    assert response.json().get("username") == "updated_user"

    # code_checks
    json = {"username": "user", "password": "updated_user123"}
    response = requests.patch(url=url + '7/', headers=admin_headers, json=json)
    assert response.status_code == 409
    
    # edge_cases
    json = {"username": "", "password": "updated_user123"}
    response = requests.patch(url=url + '7/', headers=admin_headers, json=json)
    assert response.status_code == 422

# PATCH update_user_permissions
def test_update_user_permissions():
    sub_url = 'permissions/'

    # authentication
    json = {"user_type_id": 1}
    response = requests.patch(url=url + '7/' + sub_url, headers=user_headers, json=json)
    assert response.status_code == 403

    response = requests.patch(url=url + '7/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 200
    
    # base_functionalities
    response = requests.get(url=url + '7/', headers=admin_headers)
    assert response.json().get("user_type_id") == 1

    # code_checks
    json = {"user_type_id": 99}
    response = requests.patch(url=url + '7/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 400
    
    # edge_cases
    json = {"user_type_id": ""}
    response = requests.patch(url=url + '7/' + sub_url, headers=admin_headers, json=json)
    assert response.status_code == 422
