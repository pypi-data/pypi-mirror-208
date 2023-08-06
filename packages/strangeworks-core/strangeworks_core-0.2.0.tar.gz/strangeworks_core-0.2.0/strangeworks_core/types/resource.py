"""resources.py."""
from typing import Any, Dict, Optional

from strangeworks_core.types.product import Product


class Resource:
    """Represents a Platform Resource object."""

    def __init__(
        self,
        slug: str,
        id: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        isDeleted: Optional[str] = None,
        product: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Create a Resource object.

        Parameters
        ----------
         slug: str
            User-friendly identifier.
         id: Optional[str]
            Internal identifier.
        status: Optional[str]
            Status of the resource.
        name: Optional[str]
            Resource name
        isDeleted: Optional[str]
            Indicates whether resource has been deleted.
        product: Optional[Product]
            Product object associated with the resource.
        """
        self.slug: str = slug
        self.resource_id: Optional[str] = id
        self.name: Optional[str] = name
        self.status: Optional[str] = status
        self.is_deleted: Optional[bool] = isDeleted
        self.product: Optional[Product] = (
            Product.from_dict(product) if product else None
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Resource":
        """Generate a Resource object from a dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Resource.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        d: Dict
            Resource object attributes represented as a dictionary.

        Return
        ------
        An intance of the Resource object.
        """
        return cls(**d)

    def proxy_url(
        self,
        path: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> str:
        """Return the proxy URL for the resource.

        Parameters
        ----------
        path: Optional[str]
            additional path to append to the proxy url. Defaults to None.

        base_url: Optional[str]
            base url (for example, https://api.strangeworks.com) to use for the proxy
            url. Defaults to None.

        Returns
        ------
        str:
           url that the proxy will use to make calls to the resource.
        """

        _proxy_url = (
            f"/products/{self.product.slug}/resource/{self.slug}/"
            if path is None
            else f"/products/{self.product.slug}/resource/{self.slug}/{path.strip('/')}"
        )
        return _proxy_url if base_url is None else f"{base_url.strip('/')}{_proxy_url}"
