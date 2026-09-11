import httpx


BASE_URL = "http://127.0.0.1:8001"


def register_user(username, email, password):
    response = httpx.post(
        f"{BASE_URL}/api/register/",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )

    return response


"""
This file's job is:
CLI
 ↓
api_client.py
 ↓
HTTP request
 ↓
Django API"""


def login_user(username, password):
    response = httpx.post(
        f"{BASE_URL}/api/token/",
        json={
            "username": username,
            "password": password,
        },
    )

    return response

def get_tasks(access_token):
    response = httpx.get(
        f"{BASE_URL}/api/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}" 
            #That's how your CLI tells Django:
            #"This request belongs to the user represented by this JWT."""
        }
    )

    return response
def create_task(access_token, title, description=""):
    response = httpx.post(
        f"{BASE_URL}/api/tasks/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": title,
            "description": description,
        },
    )

    return response
"""The flow is:
CLI
 ↓
create_task()
 ↓
POST /api/tasks/
 ↓
JWT → Django identifies request.user
 ↓
serializer.save(owner=request.user)
 ↓
Database"""
def complete_task(access_token, task_id):
    response = httpx.patch(
        f"{BASE_URL}/api/task/{task_id}/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "done": True
        },
    )

    return response

def update_task(access_token, task_id, title, description):
    response = httpx.patch(
        f"{BASE_URL}/api/task/{task_id}/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": title,
            "description": description
        },
    )

    return response
def get_task(access_token, task_id):
    response = httpx.get(
        f"{BASE_URL}/api/task/{task_id}/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    return response


def delete_task(access_token, task_id):
    response = httpx.delete(
        f"{BASE_URL}/api/task/{task_id}/",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    return response