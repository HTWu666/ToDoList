from unittest.mock import patch
import pytest
from json import dumps
from app import app
from models.tasks import Task

API_VERSION = "v1"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
        Task.tasks_dict.clear()


def test_create_task_success(client):
    """Test successfully creating a task"""
    # create the first task
    data_first_task = {"name": "First Test Task", "status": False}
    response_first = client.post(
        f"/api/{API_VERSION}/task",
        data=dumps(data_first_task),
        content_type="application/json",
    )
    assert response_first.status_code == 201
    json_data_first = response_first.get_json()
    assert "result" in json_data_first
    assert json_data_first["result"]["name"] == "First Test Task"
    assert (
        json_data_first["result"]["status"] == False
    )  # status is incomplete by default
    assert json_data_first["result"]["id"] == 1

    # create the second task to check that id is auto increment
    data_second_task = {"name": "Second Test Task", "status": True}
    response_second = client.post(
        f"/api/{API_VERSION}/task",
        data=dumps(data_second_task),
        content_type="application/json",
    )
    assert response_second.status_code == 201
    json_data_second = response_second.get_json()
    assert "result" in json_data_second
    assert json_data_second["result"]["name"] == "Second Test Task"
    assert (
        json_data_second["result"]["status"] == False
    )  # status is incomplete by default
    assert json_data_second["result"]["id"] == 2


@pytest.mark.parametrize(
    "payload",
    [
        ({}),  # test the name field not exist
        ({"name": ""}),  # test the name is null
        ({"name": "a" * 51}),  # test the length of name exceed upper limit
    ],
)
def test_create_task_name_validation(client, payload):
    """Test boundary conditions for the name field"""
    response = client.post(
        f"/api/{API_VERSION}/task", data=dumps(payload), content_type="application/json"
    )
    assert (
        response.status_code == 400
    ), "Expected 400 status code for invalid name field"
    json_data = response.get_json()
    assert "errors" in json_data, "Expected errors key in the response"


def test_create_task_unexpected_error(client):
    """Test creating a task encountering unexpected error"""
    with patch("models.tasks.Task.create") as mock_create:
        mock_create.side_effect = Exception("Unexpected error")
        response = client.post(f"/api/{API_VERSION}/task", json={"name": "Sample Task"})

        assert (
            response.status_code == 500
        ), "Expected a 500 status code for an internal server error"

        data = response.get_json()
        assert "errors" in data, "Expected the response to contain an 'errors' key"


def test_create_task_with_non_json_content_type(client):
    """Test creating a task with non-JSON content type results in a 400 error"""
    response = client.post(
        f"/api/{API_VERSION}/task",
        data="This is not a JSON string",
        content_type="text/plain",  # invalid content type
    )

    assert (
        response.status_code == 400
    ), "Expected a 400 status code for non-JSON content type"

    json_data = response.get_json()
    assert "errors" in json_data, "Expected 'errors' key in the response"
    assert (
        json_data["errors"] == "Invalid or missing JSON"
    ), "Expected specific error message for non-JSON content"
