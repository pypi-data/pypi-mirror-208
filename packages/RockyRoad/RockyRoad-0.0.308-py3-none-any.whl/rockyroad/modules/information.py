from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Information(Consumer):
    """Inteface to Information resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def sites(self):
        return self.__Sites(self)

    def brands(self):
        return self.__Brands(self)

    def securityGroups(self):
        return self.__Security_Groups(self)

    def securityRoles(self):
        return self.__Security_Roles(self)

    def securityProductLines(self):
        return self.__Security_Product_Lines(self)

    def securityAreas(self):
        return self.__Security_Areas(self)

    def securityProductLineKeys(self):
        return self.__Security_Product_Line_Keys(self)

    def securityAreaKeys(self):
        return self.__Security_Area_Keys(self)

    def securityAuthMapping(self):
        return self.__Security_Auth_Mapping(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Sites(Consumer):
        """Inteface to Sites resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/sites")
        def list(
            self,
        ):
            """This call will return a list of sites."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Brands(Consumer):
        """Inteface to Brands resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/brands")
        def list(
            self,
        ):
            """This call will return a list of brands."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Groups(Consumer):
        """Inteface to Security Groups resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-groups")
        def list(
            self,
        ):
            """This call will return a list of security groups."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Groups(Consumer):
        """Inteface to Security Groups resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-groups")
        def list(
            self,
        ):
            """This call will return a list of security groups."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Roles(Consumer):
        """Inteface to Security Roles resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-roles")
        def list(
            self,
        ):
            """This call will return a list of security roles."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Product_Lines(Consumer):
        """Inteface to Security Product Lines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-product-lines")
        def list(
            self,
        ):
            """This call will return a list of security product lines."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Areas(Consumer):
        """Inteface to Security Areas resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-areas")
        def list(
            self,
        ):
            """This call will return a list of security areas."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Product_Line_Keys(Consumer):
        """Inteface to Security Product Lines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-product-line-keys")
        def list(
            self,
        ):
            """This call will return a list of security product line keys."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Area_Keys(Consumer):
        """Inteface to Security Areas resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-area-keys")
        def list(
            self,
        ):
            """This call will return a list of security area keys."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Security_Auth_Mapping(Consumer):
        """Inteface to Security Auth Mapping resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-auth-mapping")
        def list(
            self,
        ):
            """This call will return a mapping of security authorization keys and product lines."""
