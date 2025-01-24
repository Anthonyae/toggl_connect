x = {
        "id": 3771028704,
        "workspace_id": 8367760,
        "project_id": "None",
        "task_id": "None",
        "billable": "False",
        "start": "2025-01-21T19:07:55+00:00",
        "stop": "2025-01-21T23:25:33+00:00",
        "duration": 15458,
        "description": "fix(habit scheduler: Update plugins for anki and toggl",
        "tags": [],
        "tag_ids": [],
        "duronly": "True",
        "at": "2025-01-21T23:26:13.577412Z",
        "server_deleted_at": "None",
        "user_id": 10839867,
        "uid": 10839867,
        "wid": 8367760
    },
    {
        "id": 3770817242,
        "workspace_id": 8367760,
        "project_id": "None",
        "task_id": "None",
        "billable": "False",
        "start": "2025-01-21T16:58:40+00:00",
        "stop": "2025-01-21T17:38:43+00:00",
        "duration": 2403,
        "description": "fix(habit scheduler: Update plugins for anki and toggl",
        "tags": [],
        "tag_ids": [],
        "duronly": "True",
        "at": "2025-01-21T17:39:24.143555Z",
        "server_deleted_at": "None",
        "user_id": 10839867,
        "uid": 10839867,
        "wid": 8367760
    },


def convert_dict_to_standard_dict(input_dict: dict, key_name: str) -> dict:
        """Converts a list of dicts into a single dict and makes a key of the given field_name."""
        result = { [key_name]: dict for dict in input_dict}
        return result

print(convert_dict_to_standard_dict(x, "id"),)