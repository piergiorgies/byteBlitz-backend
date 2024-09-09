import pytest
import requests
from mock import admin_headers, user_headers, base_url

url = base_url + 'contests/'


# region Contest
def test_create_contest():
    data = {
        "name": "Test Contest",
        "description": "This is a test contest",
        "start_datetime": "2022-01-01T00:00:00",
        "end_datetime": "2022-01-02T00:00:00",
    }

    # send data as admin
    response = requests.post(url=url, headers=admin_headers, json=data)
    assert response.status_code == 201

    # send data as user
    response = requests.post(url=url, headers=user_headers, json=data)
    assert response.status_code == 403

def test_get_contests():
    data = {}
    
    response = requests.get(url=url, headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url, headers=user_headers, json=data)
    assert response.status_code == 200

def test_get_contest():
    data = {}
    
    response = requests.get(url=url + '8/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url + '8/', headers=user_headers, json=data)
    assert response.status_code == 200

def test_update_contest():
    data = {
        "name": "Test Contest",
        "description": "This is a test contest",
        "start_datetime": "2022-01-01T00:00:00",
        "end_datetime": "2022-01-02T00:00:00",
    }

    # send data as admin
    response = requests.put(url=url + '8/', headers=admin_headers, json=data)
    print(response.json())
    assert response.status_code == 200

    # send data as user
    response = requests.put(url=url + '8/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_delete_contest():
    data = {}
    
    response = requests.delete(url=url + '8/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.delete(url=url + '8/', headers=user_headers, json=data)
    assert response.status_code == 403

# endregion

# region Contest Problems

def test_get_contest_problems():
    data = {}
    
    response = requests.get(url=url + '8/problems/', headers=admin_headers, json=data)
    print(response.json())
    assert response.status_code == 200

    response = requests.get(url=url + '8/problems/', headers=user_headers, json=data)
    assert response.status_code == 200

def test_add_problem_to_contest():
    data = {
        "id": 2,
        "publication_delay": 100
    }

    # send data as admin
    response = requests.post(url=url + '8/problems/', headers=admin_headers, json=data)
    assert response.status_code == 201

    # send data as user
    response = requests.post(url=url + '8/problems/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_remove_problem_from_contest():
    data = 2
    
    response = requests.delete(url=url + '8/problems/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.delete(url=url + '8/problems/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_update_problem_publication_delay():
    data = {
        "id": 2,
        "publication_delay": 200
    }

    # send data as admin
    response = requests.patch(url=url + '8/problems/', headers=admin_headers, json=data)
    assert response.status_code == 200

    # send data as user
    response = requests.patch(url=url + '8/problems/', headers=user_headers, json=data)
    assert response.status_code == 403

# endregion

# region Contest Participants

def test_get_contest_participants():
    data = {}
    
    response = requests.get(url=url + '8/users/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url + '8/users/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_add_user_to_contest():
    data = 4

    response = requests.post(url=url + '8/users/', headers=admin_headers, json=data)
    print(response.json())
    assert response.status_code == 201

    response = requests.post(url=url + '8/users/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_remove_user_from_contest():
    data = 4
    
    response = requests.delete(url=url + '8/users/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.delete(url=url + '8/users/', headers=user_headers, json=data)
    assert response.status_code == 403

# endregion

# region Contest Teams

def test_get_contest_teams():
    data = {}
    
    response = requests.get(url=url + '8/teams/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.get(url=url + '8/teams/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_add_team_to_contest():
    data = 1

    response = requests.post(url=url + '8/teams/', headers=admin_headers, json=data)
    assert response.status_code == 201

    response = requests.post(url=url + '8/teams/', headers=user_headers, json=data)
    assert response.status_code == 403

def test_remove_team_from_contest():
    data = 1
    
    response = requests.delete(url=url + '8/teams/', headers=admin_headers, json=data)
    assert response.status_code == 200

    response = requests.delete(url=url + '8/teams/', headers=user_headers, json=data)
    assert response.status_code == 403

# endregion

