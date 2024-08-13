"""Module for connecting the toggl api."""

import datetime
import os
from base64 import b64encode

import requests
from dotenv import load_dotenv

load_dotenv()

TOGGL_KEY: str = os.getenv("TOGGL_KEY", "")
TOGGL_HOME_WORKSPACE_NAME: str = os.getenv("TOGGL_HOME_WORKSPACE_NAME", "")
API_AUTH: bytes = bytes(f"{TOGGL_KEY}:api_token", "utf-8")


class BaseAPI:
    """Base level api class that provides basic replacement values for get and posting data to toggl."""

    BASE_URL = "https://api.track.toggl.com/api/v9/"

    def __init__(self):
        """Initialize the BaseAPI class."""
        self.api_auth: bytes = API_AUTH
        self.default_workspace_id: int = self.get_workspace_id_from_name(
            workspace_name=TOGGL_HOME_WORKSPACE_NAME
        )

    def _get(self, endpoint: str, data=None) -> dict:
        """Submits get request to toggl and specified endpoint."""
        request_string = f"{self.BASE_URL}{endpoint}"
        response = requests.get(
            request_string,
            headers={
                "content-type": "application/json",
                "Authorization": f'Basic {b64encode(self.api_auth).decode("ascii")}',
            },
            params=data,
            timeout=10,
        )
        if response.status_code != 200:
            raise requests.RequestException(f"API Error: {response.status_code}: {response.text}")
        return response.json()

    def _post(self, endpoint, data):
        """Submits a post request to toggl."""
        request_string = f"{self.BASE_URL}{endpoint}"
        response = requests.post(
            request_string,
            headers={
                "content-type": "application/json",
                "Authorization": f'Basic {b64encode(self.api_auth).decode("ascii")}',
            },
            timeout=15,
            json=data,
        )
        if response.status_code != 200:
            raise requests.RequestException(f"API Error: {response.status_code}: {response.text}")
        return response.json()

    def get_workspace_id_from_name(self, workspace_name: str) -> int:
        """Returns a workspace_id for the given workspace_name in toggl."""
        workspace_objects = self._get("me/workspaces")
        for workspace in workspace_objects:
            if workspace.get("name") == workspace_name:
                return workspace.get("id")
        return None


class TogglProjectAPI(BaseAPI):
    """Class for interacting with projects from Toggl."""

    def __init__(self):
        """Initializes a new instance of the TogglApi class."""
        super().__init__()
        self.projects: dict = self._get_projects(self.default_workspace_id)
        self.new_project_template = {
            "active": True,
            "auto_estimates": None,
            "billable": None,
            "cid": None,
            "client_id": None,
            "client_name": None,
            "color": None,
            "currency": None,
            "end_date": None,
            "estimated_hours": None,
            "fixed_fee": None,
            "is_private": True,
            "name": None,
            "rate": None,
            "rate_change_mode": None,
            "recurring": False,
            "start_date": None,
            "template": None,
            "template_id": None,
        }

    def _get_projects(self, workspace_id: int) -> dict:
        """Returns projects and their details from Toggl based on the workspace id.

        Note:
            This will initialize with your default workspace_id. Call this
            again to change the projects associated with the class instance.
        """
        toggl_projects = {}
        project_response = self._get(f"workspaces/{workspace_id}/projects")
        for project in project_response:
            toggl_projects[project["name"]] = project
        self.projects = toggl_projects
        return self.projects

    def get_project_id_from_name(self, project_name: str) -> int:
        """Returns Toggle project_id based on project_name provided.

        Optionally set if should match_case.
        """
        project: dict = self.projects.get(project_name.lower())
        project_id = project.get("id") if project else None
        return project_id

    def create_generic_project(
        self, project_name: str, is_kpi=False, workspace_id: int = None
    ) -> dict:
        """Creates a project in toggl with the given project_name for the given workspace.

        If no workspace is given then uses default workspace_id.

        Returns:
        Created project or empty object if project already exists.
        """
        if project_name in self.projects.keys():
            raise ValueError(f"Project with name {project_name} already exists.")
        if not workspace_id:
            workspace_id = self.default_workspace_id
        new_project = self.new_project_template
        new_project["name"] = project_name
        if is_kpi:
            new_project["color"] = "#e36a00"
        created_project_obj = self._post(f"workspaces/{workspace_id}/projects", data=new_project)
        return created_project_obj

    def get_time_entries(self, params: dict):
        """Get Toggl time entries based on query parameters.

        Example query parameters provided below:

        Paramters: (optional) (multiple options)
        - params = {'start_date': '2024-06-01', 'end_date': '2024-06-02'}
            - inclusive to exclusive dates
        - params = {'since': 1713899346983}
            - UNIX timestamp, modified entries since UNIX, including deleted ones
        """
        time_entries = self._get("me/time_entries", params)
        return time_entries

    def create_toggl_time_entry(
        self,
        project_id: int,
        duration: int,
        start_at: datetime.datetime.utcnow,
        description: str = "No description",
        workspace_id: int = None,
    ) -> dict:
        """Creates Toggl time entries.

        Parameters:
        - project_id (int): The project_id of the project in Toggl.
        - duration (int): The time in seconds.
        - start_at (datetime): the date to place the .
        - description (str): the activity being done for the project.
        """
        if not workspace_id:
            workspace_id = self.default_workspace_id
        toggl_time_entry_template = {
            "billable": False,
            "created_with": "python_toggl_module",
            "description": description,
            "duration": duration,
            "duronly": True,
            "project_id": project_id,
            "shared_with_user_ids": [],
            "start_date": None,  # fix
            "stop": None,  # fix
            "tag_action": None,
            "tag_ids": [],
            "tags": [],
            "task_id": None,
            "workspace_id": workspace_id,
        }
        toggl_time_entry_template["start"] = start_at
        time_entry_url = f"workspaces/{workspace_id}/time_entries"
        time_entry_response = self._post(time_entry_url, toggl_time_entry_template)
        return time_entry_response
