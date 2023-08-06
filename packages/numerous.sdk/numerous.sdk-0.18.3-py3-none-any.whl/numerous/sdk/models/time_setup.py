from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class TimeSetup:
    start: datetime
    end: datetime
    duration: timedelta

    @staticmethod
    def from_document(job_data: dict[str, Any]) -> "TimeSetup":
        start = datetime.fromisoformat(job_data["runSettings"]["startDate"])
        end = datetime.fromisoformat(job_data["runSettings"]["endDate"])
        return TimeSetup(
            start=start,
            end=end,
            duration=end - start,
        )
