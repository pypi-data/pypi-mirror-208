"""backends.py."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from strangeworks_core.types.product import Product
from strangeworks_core.utils import is_empty_str, str_to_datetime


class Status(Enum):
    """Enumeration of possible backend statuses."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def from_str(s: Optional[str] = None) -> Status:
        """Return Status from string."""
        if is_empty_str(s):
            return Status.UNKNOWN
        adj_str = s.strip().upper()
        possible_status = [e for e in Status if e.value == adj_str]
        return possible_status[0] if len(possible_status) == 1 else Status.UNKNOWN

    def __str__(self):
        return str(self.value)


class Backend:
    """Represents a Strangeworks platform Backend object."""

    def __init__(
        self,
        name: str,
        slug: str,
        status: str,
        id: Optional[str] = None,
        data: Optional[str] = None,
        dataSchema: Optional[str] = None,
        remoteBackendId: Optional[str] = None,
        remoteStatus: Optional[str] = None,
        dateCreated: Optional[str] = None,
        dateUpdated: Optional[str] = None,
        product: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Create a Backend object.

        Parameters
        ----------
        name: str
            Backend name.
        slug: str
            User-friendly identifier.
        status: str
            Status of the backend.
        id:  Optional[str]
            Internal identifier.
        data: Optional[str]
            Typically configuration data.
        dataSchema: Optional[str]
            JSON schema to which the data is expected to adhere to.
        remoteBackendId: Optional[str]
            Identifier used by the vendor.
        remoteStatus: Optional[str]
            Status from the vendor.
        dateCreated: Optional[str]
            Date when the backend object was created on platform.
        dateUpdated: Optional[str]
            Date when the backend object was last updated.
        product: Optional[Dict[str, Any]]
            Product associated with the backend represended as a dictionary.
        """
        self.name: str = name
        self.slug: str = slug
        self.status: Status = Status.from_str(status)
        self.product: Optional[Product] = (
            Product.from_dict(product) if product else None
        )
        self.backend_id: Optional[str] = id
        self.data: Optional[Dict[str, Any]] = data
        self.data_schema: Optional[str] = dataSchema
        self.remote_backend_id: Optional[str] = remoteBackendId
        self.remote_status: Optional[str] = remoteStatus
        self.date_created: Optional[datetime] = (
            str_to_datetime(dateCreated) if dateCreated else None
        )
        self.date_updated: Optional[datetime] = (
            str_to_datetime(dateUpdated) if dateUpdated else None
        )

    @classmethod
    def from_dict(cls, backend: Dict[str, Any]) -> Backend:
        """Create a Backend object from Dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Backend.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        d : Dict[str, Any]
            Backend represented as a dictionary.
        """
        return cls(**backend)
