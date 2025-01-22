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

    _BASE_URL = "https://api.track.toggl.com/api/v9/"

    def __init__(self):
        """Initialize the BaseAPI class.
        
        Initiates with a workspace_id for the default workspace in environment variables.
        """
        self.__api_auth: bytes = API_AUTH
        self._default_workspace_id: int = self.get_workspace_id_from_name(
            workspace_name=TOGGL_HOME_WORKSPACE_NAME
        )

    def _get(self, endpoint: str, data: None=None) -> list[dict]:
        """Submits get request to toggl and specified endpoint.
        
        Returns: A list of dictionaries from the response.
        """
        request_string = f"{self._BASE_URL}{endpoint}"
        response = requests.get(
            request_string,
            headers={
                "content-type": "application/json",
                "Authorization": f'Basic {b64encode(self.__api_auth).decode("ascii")}',
            },
            params=data,
            timeout=10,
        )
        if response.status_code != 200:
            raise requests.RequestException(f"API Error: {response.status_code}: {response.text}")
        return response.json()

    def _post(self, endpoint: str, data: dict) -> dict:
        """Submits a post request to toggl."""
        request_string = f"{self._BASE_URL}{endpoint}"
        response = requests.post(
            request_string,
            headers={
                "content-type": "application/json",
                "Authorization": f'Basic {b64encode(self.__api_auth).decode("ascii")}',
            },
            timeout=15,
            json=data,
        )
        if response.status_code != 200:
            raise requests.RequestException(f"API Error: {response.status_code}: {response.text}")
        return response.json()

    def get_workspace_id_from_name(self, workspace_name: str) -> int:
        """Gets a workspace_id for the given workspace_name in toggl.
        
        Returns: workspace_id or error if workspace_id is not found.
        """
        workspace_objects = self._get("me/workspaces")
        workspace_id = None
        for workspace in workspace_objects:
            if workspace.get("name") == workspace_name:
                workspace_id = int(workspace.get("id")) # type: ignore
                break
        if workspace_id:
            return workspace_id
        else:
            raise ValueError(f"Workspace with name {workspace_name} not found.")

class TogglProjectAPI(BaseAPI):
    """Class for interacting with projects from Toggl.
    
    This class provides methods for creating projects, looking up project_ids, and creating time entries.
    
    Attributes:
        projects (list): A list of project dictionaries from the default workspace.
    """

    def __init__(self):
        """Initializes a new instance of the TogglApi class.
        
        Note: This will initialize with your projects from your workspace in your env file.
        """
        super().__init__()
        self.projects: dict = self._set_class_projects(self._default_workspace_id)
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

    def _set_class_projects(self, workspace_id: int) -> dict:
        """Sets the projects for the class instance based on the workspace_id provided.

        Note:
            This will initialize with your default workspace_id. Call this
            again to change the projects associated with the class instance.
            
        Returns:
            Dictionary of projects with project name as the key and project object as the value.
        """
        toggl_projects = {}
        project_response = self._get(f"workspaces/{workspace_id}/projects")
        for project in project_response:
            # set the project name to be lowercase
            toggl_projects[project["name"].lower()] = project
        self.projects = toggl_projects
        return self.projects

    def lookup_project_id_by_name(self, project_name: str) -> int|None:
        """Returns Toggle project_id based on project_name provided.

        Returns:
            project_id associated with the project_name or None if project_name is not found.
        """
        project: dict = self.projects.get(project_name.lower(), {})
        project_id = project.get("id") if project else None
        return project_id

    def create_generic_project(
        self, project_name: str, color:str|None=None, is_kpi=False, workspace_id: int|None = None
    ) -> dict:
        """Creates a project in toggl with the given project_name for the given workspace.

        Note: If no workspace is given then uses default workspace_id stored in the class.
        
        Colors: (optional)
        -     colors = {
                "blue": "#0b83d9",
                "purple": "#774ba8",
                "pink": "#a03e67",
                "orange": "#e36a00",
                "orange brown": "#905d1f",
                "green": "#438327",
                "teal": "#06a893",
                "beige": "#744f4b",
                "dark blue": "#3b488a",
                "dark purple": "#701576",
                "yellow": "#c7af14",
                "olive green": "#3e4420",
                "red": "#a0312a",
                "graying blue": "#424250",
            }

        Returns: Created project or project object if project already exists.
        """
        colors = {
            "blue": "#0b83d9",
            "purple": "#774ba8",
            "pink": "#a03e67",
            "orange": "#e36a00",
            "orange brown": "#905d1f",
            "green": "#438327",
            "teal": "#06a893",
            "beige": "#744f4b",
            "dark blue": "#3b488a",
            "dark purple": "#701576",
            "yellow": "#c7af14",
            "olive green": "#3e4420",
            "red": "#a0312a",
            "graying blue": "#424250",
        }

        if project_name.lower() in self.projects.keys():
            return self.projects[project_name.lower()]
        if not workspace_id:
            workspace_id = self._default_workspace_id
        new_project = self.new_project_template
        new_project["name"] = project_name
        if color:
            new_project["color"] = colors.get(color.lower(), "#0b83d9")
        if is_kpi:
            new_project["color"] = colors.get("orange", "#e36a00")
        project_response = self._post(f"workspaces/{workspace_id}/projects", data=new_project)
        new_project = {}
        new_project[project_name.lower()] = project_response
        return new_project

    def get_time_entries(self, params: dict) -> list[dict]:
        """Get Toggl time entries based on query parameters.

        Example query parameters provided below:

        Parameters: (optional) (multiple options)
        - params = {'start_date': '2024-06-01', 'end_date': '2024-06-02'}
            - inclusive to exclusive dates
        - params = {'since': 1713899346983}
            - UNIX timestamp, modified entries since UNIX, including deleted ones
        """
        time_entries = self._get("me/time_entries", params) # type: ignore
        return time_entries # type: ignore

    def create_toggl_time_entry(
        self,
        project_id: int,
        duration: int,
        start_at: datetime.datetime,
        description: str = "No description",
        tags: list[str] = [],
        workspace_id: int|None = None,
    ) -> dict:
        """Creates Toggl time entries.

        Parameters:
        - project_id (int): The project_id of the project in Toggl.
        - duration (int): The time in seconds.
        - start_at (datetime): the date to place the time entry.
        - description (str): the activity being done for the project.
        """
        if not workspace_id:
            workspace_id = self._default_workspace_id
        toggl_time_entry_template = {
            "billable": False,
            "created_with": "python_toggl_module",
            "description": description,
            "duration": duration,
            "duronly": True,
            "project_id": project_id,
            "shared_with_user_ids": [],
            "start_date": None,  # not used
            "stop": None,  # not used
            "tag_action": None,
            "tag_ids": [],
            "tags": tags,
            "task_id": None,
            "workspace_id": workspace_id,
        }
        toggl_time_entry_template["start"] = start_at
        time_entry_url = f"workspaces/{workspace_id}/time_entries"
        time_entry_response = self._post(time_entry_url, toggl_time_entry_template)
        return time_entry_response

    def get_tags(self, workspace_id: int|None=None) -> dict:
        """Get tags for a given workspace_id.
        
        Note: Uses default workspace_id if none is provided.
        
        Returns: Dictionary of tags with tag name as the key and tag object as the value.
        """
        if not workspace_id:
            workspace_id = self._default_workspace_id
        tags_response = self._get(f"workspaces/{workspace_id}/tags")
        tags = {}
        for tag in tags_response:
            tag_id = tag.get("id")
            tag_name = tag.get("name")
            tags[tag_name] = tag
        return tags
    
    def delete_tags(self, tags: list[str], workspace_id: int|None=None) -> dict:
        """Delete tags for a given workspace_id.
        
        Note: Uses default workspace_id if none is provided.
        """
        if not workspace_id:
            workspace_id = self._default_workspace_id
            
        tags_by_name = self.get_tags(workspace_id)
        tags_response = {}
        for tag_name, tag_obj in tags_by_name.items():
            if tag_name in tags:
                response = requests.delete(self._BASE_URL + "workspaces/{workspace_id}/tags/{tag_obj['id']}")
                tags_response[tag_name] = response
        return tags_response