import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from logger import Logger
from toggl_api import TogglProjectAPI

if __name__ == "__main__":

    def log_toggl_time_entries() -> None:
        """Log Toggl time entries to dataset."""
        load_dotenv()
        logger = Logger()
        dataset_path = os.environ["DATASET_PATH"]
        today = datetime.now().date()

        toggl = TogglProjectAPI()
        lookback_window_days = 30
        previous_days = 1
        time_entries = toggl.get_time_entries(
            params={
                "start_date": today - timedelta(days=lookback_window_days),
                "end_date": today - timedelta(days=previous_days),
                "meta": "true",
            }
        )
        standard_time_entries = logger.convert_list_of_dicts_to_dict(time_entries, "id")  # type: ignore
        logger.log(os.path.join(dataset_path, "time_entries.json"), standard_time_entries)  # type: ignore

    log_toggl_time_entries()
