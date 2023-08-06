"""product.py."""
from typing import Dict, Optional


class Product:
    """Represents a Platform Product object."""

    def __init__(
        self,
        slug: str,
        id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ):
        """Create a Product object.

        Parameters
        ----------
        slug: str
            User-friendly identifier.
        id: Optional[str]
            Internal identifier.
        name: Optional[str]
            Product name.
        """
        self.slug: str = slug
        self.product_id: Optional[str] = id
        self.name: Optional[str] = name

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "Product":
        """Create a Product object from Dictionary.

        The key names in the dictionary must match field names as specified by the
        GraphQL schema for Product.

        Parameters
        ----------
        cls
            Class that will be instantiated.
        d : Dict[str, Any]
            Product represented as a dictionary.
        """
        return cls(**d)
