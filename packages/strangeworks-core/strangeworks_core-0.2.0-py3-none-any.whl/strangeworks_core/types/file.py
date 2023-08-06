"""file.py."""
from datetime import datetime
from typing import Any, Dict, Optional

from strangeworks_core.utils import str_to_datetime


class File:
    """Class that represents a file associated with a job."""

    def __init__(
        self,
        slug: str,
        id: Optional[str] = None,
        label: Optional[str] = None,
        fileName: Optional[str] = None,
        url: Optional[str] = None,
        dateCreated: Optional[str] = None,
        dateUpdated: Optional[str] = None,
        **kwargs,
    ):
        """Create a File object.

        Parameters
        ----------
        slug: str
            User-friendly identifier.
        id: Optional[str]
            Internal identifier.
        label: Optional[str]
            Label
        fileName: Optional[str]
            File name used when saving on platform.
        url: Optional[str]
            URL to access the file from the platform.
        dateCreated: Optional[str]
            Date when the file object was created on platform.
        dateUpdated: Optional[str]
            Date when the file object was last updated.
        """
        self.slug: str = slug
        self.file_id: Optional[str] = id
        self.label: Optional[str] = label
        self.file_name: Optional[str] = fileName
        self.url: Optional[str] = url
        self.date_created: Optional[datetime] = (
            str_to_datetime(dateCreated) if dateCreated else None
        )
        self.date_updated: Optional[datetime] = (
            str_to_datetime(dateUpdated) if dateUpdated else None
        )

    @classmethod
    def from_dict(cls, res: Dict[str, Any]) -> "File":
        """Create a File object from a Dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for File.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        res : Dict[str, Any]
            File represented as a dictionary.
        """
        return cls(**res)
