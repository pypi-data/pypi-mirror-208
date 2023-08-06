from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class B2C_Users(Consumer):
    """Inteface to B2C users resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("b2c-users")
    def list(
        self,
        user_role: Query(type=str) = None,
        company_uid: Query(type=str) = None,
    ):
        """This call will return B2C user information for the specified criteria."""

    @returns.json
    @http_get("b2c-users/{uid_or_email}")
    def get(
        self,
        uid_or_email: str,
    ):
        """This call will return the B2C user for the specified uid or email."""

    @returns.json
    @json
    @post("b2c-users")
    def insert(
        self,
        b2c_user: Body,
    ):
        """This call will insert a new B2C user."""

    @returns.json
    @json
    @post("b2c-users/batch")
    def batch_insert(
        self,
        b2c_user_batch: Body,
    ):
        """This call will insert a batch of new B2C users."""

    @returns.json
    @json
    @patch("b2c-users/batch")
    def batch_update(
        self,
        b2c_user_batch: Body,
    ):
        """This call will update a batch of B2C users."""

    @json
    @patch("b2c-users/{uid_or_email}")
    def update(
        self,
        uid_or_email: str,
        b2c_user: Body,
    ):
        """This call will update a B2C user based on uid or email."""

    @delete("b2c-users/{uid}")
    def delete(self, uid: str):
        """This call will the B2C user."""
