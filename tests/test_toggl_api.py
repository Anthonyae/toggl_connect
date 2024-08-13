"""This is a testing module for toggl."""

import unittest
from unittest.mock import patch

from toggl_connect import TogglProjectAPI


class TestTogglProjectAPI(unittest.TestCase):
    """Test class for TogglProjectAPI."""

    @patch("toggl_connect.TogglProjectAPI._get")
    def test_get_projects(self, mock_get):
        """Test the get_projects method."""
        api = TogglProjectAPI()
        mock_get.return_value = [{"name": "Project1", "id": 1}, {"name": "Project2", "id": 2}]

        workspace_id = 12345
        projects = api._get_projects(workspace_id)

        expected_projects = {
            "Project1": {"name": "Project1", "id": 1},
            "Project2": {"name": "Project2", "id": 2},
        }
        self.assertEqual(projects, expected_projects)

    @patch("toggl_connect.TogglProjectAPI._post")
    def test_create_generic_project(self, mock_post):
        """Test the create_generic_project method."""
        api = TogglProjectAPI()
        mock_post.return_value = {"id": 12345, "name": "Test Project"}

        project_name = "Test Project"
        created_project = api.create_generic_project(project_name)

        self.assertEqual(created_project, {"id": 12345, "name": "Test Project"})
