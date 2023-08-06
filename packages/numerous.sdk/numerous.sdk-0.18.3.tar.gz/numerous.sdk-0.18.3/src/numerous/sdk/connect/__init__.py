"""numerous.sdk.connect - connect your code to the numerous platform!

The connect package contains all the functionality needed to build applications
that connect to and take advantage of the numerous platform.
"""

from .job_client import JobClient, JobStatus

__all__ = ("JobClient", "JobStatus")
