"""jobs.py."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from strangeworks_core.types.file import File
from strangeworks_core.types.resource import Resource
from strangeworks_core.utils import str_to_datetime


class Status(str, Enum):
    """Enumeration of possible job statuses."""

    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"


class Job:
    """Object representing a Strangeworks platform job entry."""

    def __init__(
        self,
        slug: str,
        id: Optional[str] = None,
        externalIdentifier: Optional[str] = None,
        status: Optional[str] = None,
        isTerminalState: Optional[bool] = None,
        remoteStatus: Optional[str] = None,
        jobData: Optional[Dict[str, Any]] = None,
        jobDataSchema: Optional[str] = None,
        dateCreated: Optional[str] = None,
        dateUpdated: Optional[str] = None,
        resource: Optional[Dict[str, Any]] = None,
        childJobs: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ):
        """Create a Job object.

        Parameters
        ----------
        slug: str
            User-friendly identifier.
        id: str
            Internal identifier.
        externalIdentifier: Optional[str]
            Identifier if the execution of the job is occurring on an external
            platform.
        status: Optional[str]
            Status of the job.
        isTerminalState: Optional[bool]
            Indicates whether the current state of the job is terminal meaning
            no further state changes will occur.
        remoteStatus: Optional[str]
            Status of the job on external platform. Only valid if job was
            running on external platform.
        jobData: Optional[str]
            Typically information including attributes of the job execution.
        jobDataSchema: Optional[str]
            JSON schema to which the data is expected to adhere to.
        dateCreated: Optional[str]
            Date when the job object was created on platform.
        dateUpdated: Optional[str]
            Date when the job object was last updated.
        resource: Optional[Dict[str, Any]]
            Resource object associated with the job.
        childJobs: Optional[List[Dict[str, Any]]]
            List of jobs which were spawned by the job.
        files: Optional[List[Dict[str, Any]]]
            List of files associated with the job.
        """
        self.slug: str = slug
        self.job_id: Optional[str] = id
        self.external_identifier: Optional[str] = externalIdentifier

        self.status: Optional[Status] = (
            Status(status.strip().upper()) if status else None
        )
        self.is_terminal_state: Optional[bool] = isTerminalState
        self.remote_status: Optional[str] = remoteStatus
        self.job_data_schema: Optional[str] = jobDataSchema
        self.job_data: Optional[Dict[str, Any]] = jobData
        self.date_created: Optional[datetime] = (
            str_to_datetime(dateCreated) if dateCreated else None
        )
        self.date_updated: Optional[datetime] = (
            str_to_datetime(dateUpdated) if dateUpdated else None
        )
        self.resource: Optional[Resource] = (
            Resource.from_dict(resource) if resource else None
        )
        self.child_jobs: Optional[List[Job]] = (
            list(map(lambda x: Job.from_dict(x), childJobs)) if childJobs else None
        )
        self.files: Optional[List[JobFile]] = (
            [JobFile.from_dict(f) for f in files] if files else None
        )

    @classmethod
    def from_dict(cls, res: Dict[str, Any]) -> "Job":
        """Generate a Job object from dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Job.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        res: Dict[str, Any]
            Job attribues represented as a dictionary.

        Return
        ------
        "Job"
            a job object.
        """
        return cls(**res)

    def is_complete(self) -> bool:
        """Check if job is in terminal state.

        deprecated method, kept to limit number of changes
        required for extension SDKs
        """
        return self.is_terminal_state


class JobFile:
    def __init__(
        self,
        file: Dict[str, Any],
        sortWeight: Optional[int] = None,
        isPublic: Optional[bool] = None,
        **kwargs,
    ) -> None:
        """Create a JobFile object.

        Parameters
        ----------
        file: Dict[str, Any]
            File object associated with the job.
        sortWeight: Optional[int]
            Sort weight of the file.
        isPublic: Optional[bool]
            Indicates whether the file is public.
        """
        self.file: File = File.from_dict(file)
        self.sort_weight: Optional[int] = sortWeight
        self.is_public: Optional[bool] = isPublic

    @classmethod
    def from_dict(cls, res: Dict[str, Any]) -> "JobFile":
        """Generate a JobFile object from dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for JobFile.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        res: Dict[str, Any]
            JobFile attribues represented as a dictionary.

        Return
        ------
        "JobFile"
            a job file object.
        """
        return cls(**res)
