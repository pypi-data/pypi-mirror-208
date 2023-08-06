import json
from typing import List, Optional

import requests

API_URL = "https://www.api.experiment-hq.com/"


class Experiment:
    """
    Experiment class for logging parameters to Notion.

    args:
        api_key (str): API key for the ExperimentHQ API
        project (str): Name of the project to log to
        name (Optional[str]): Name of the experiment
        description (Optional[str]): Description of the experiment
        tags (Optional[List[str]]): List of tags to add to the experiment
    """

    def __init__(
        self,
        api_key: str,
        project: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.project = project
        self.api_key = api_key
        self.name = name
        self.description = description
        self.tags = tags
        self.experiment_id = self._start_experiment()

    def _start_experiment(self) -> str:
        post_data = {
            "project": self.project,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        response = requests.post(
            url=f"{API_URL}experiment", data=json.dumps(post_data), headers=headers
        )

        # Raise exception if maximum number of experiments reached
        if response.status_code == 401:
            raise Exception("Invalid API key")

        # Raise exception if maximum number of experiments reached
        elif response.status_code == 403:
            raise Exception("Maximum number of experiments reached")

        elif response.status_code == 404:
            raise Exception("ExperimentHQ database not found")

        elif response.status_code != 200:
            raise Exception("Failed to start experiment with message: " + response.text)

        response_json = response.json()
        return response_json.get("experiment_id")

    def log_parameter(self, name: str, value: str) -> None:
        data = {"parameter_name": name, "parameter_value": value}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(
            url=f"{API_URL}experiments/{self.experiment_id}/parameters",
            data=json.dumps(data),
            headers=headers,
        )

        if response.status_code == 401:
            raise Exception("Invalid API key")

        elif response.status_code == 404:
            raise Exception("ExperimentHQ database not found")

        elif response.status_code != 200:
            raise Exception("Failed to log parameter with message: " + response.text)
