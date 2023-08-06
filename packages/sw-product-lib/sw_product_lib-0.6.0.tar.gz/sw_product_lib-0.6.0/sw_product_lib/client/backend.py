"""backend.py."""
import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.platform.gql import API, Operation
from strangeworks_core.types.backend import Backend as BackendBase
from strangeworks_core.types.backend import Status


@dataclass
class BackendTags:
    id: str
    tag: str
    display_name: str
    tag_group: str
    is_system: bool


@dataclass
class BackendType:
    id: str
    slug: str
    display_name: str
    description: str
    schema_url: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(res: dict):
        return BackendType(
            id=res["id"],
            slug=res["slug"],
            display_name=res["displayName"],
            description=res["description"],
            schema_url=res["schemaURL"],
        )


@dataclass
class BackendTypeInput:
    slug: str
    data: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {"typeSlug": self.slug, "data": json.dumps(self.data)}


@dataclass
class BackendRegistration:
    backend_type_id: str
    data: Dict[str, Any]
    backend_type: Optional[BackendType] = None

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, res: Dict[str, Any]):
        return cls(
            backend_type_id=res["backendTypeId"],
            data=res["data"],
            backend_type=BackendType.from_dict(res.get("backendType"))
            if "backendType" in res
            else None,
        )


@dataclass
class BackendUpdateInput:
    backendSlug: str
    data: Optional[str] = None
    dataSchema: Optional[str] = None
    name: Optional[str] = None
    remoteBackendId: Optional[str] = None
    remoteStatus: Optional[str] = None
    status: Optional[Status] = None

    def get(self) -> Dict[str, str]:
        # filter out all attributes that are None
        # then convert status from Status to string.
        return dict(
            map(
                lambda tup: (
                    tup[0],
                    tup[1] if tup[0] != "status" else str(tup[1]),
                ),
                filter(lambda item: item[1], self.__dict__.items()),
            )
        )


class Backend(BackendBase):
    def __init__(
        self,
        backendRegistrations: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.backend_registrations: Optional[List[BackendRegistration]] = (
            [BackendRegistration.from_dict(br) for br in backendRegistrations]
            if backendRegistrations
            else None
        )

        self.tags: Optional[List[str]] = tags

    def dict(self):
        return self.__dict__

    def to_create_request(self):
        return {
            "data": json.dumps(self.data),
            "dataSchema": self.data_schema,
            "name": self.name,
            "remoteBackendId": self.remote_backend_id,
            "remoteStatus": self.remote_status,
            "status": self.status.value.upper(),
        }

    def to_update_request(self):
        return {
            "backendSlug": self.slug,
            "data": json.dumps(self.data),
            "dataSchema": self.data_schema,
            "name": self.name,
            "remoteBackendId": self.remote_backend_id,
            "remoteStatus": self.remote_status,
            "status": self.status.value.upper,
        }

    @classmethod
    def from_dict(cls, res: Dict[str, Any]):
        return cls(**res)


get_all_strangeworks_backends_request = Operation(
    query="""
        query backends(
            $product_slugs: [String!],
            $backend_type_slugs: [String!],
            $backend_statuses: [BackendStatus!],
            $backend_tags: [String!]) {
                backends(
                    productSlugs: $product_slugs,
                    backendTypeSlugs: $backend_type_slugs,
                    backendStatuses: $backend_statuses,
                    backendTags: $backend_tags){
                        id,
                        name,
                        status,
                        remoteBackendId,
                        remoteStatus,
                        slug,
                    }
                }
    """
)


def get_backends(
    api: API,
    product_slugs: List[str] = None,
    backend_type_slugs: List[str] = None,
    backend_statuses: List[str] = None,
    backend_tags: List[str] = None,
) -> List[Backend]:
    """Retrieve a list of available backends."""
    backends_response = api.execute(
        op=get_all_strangeworks_backends_request,
        **locals(),
    )
    return [Backend.from_dict(b) for b in backends_response["backends"]]


get_backends_request = Operation(
    query="""
    query v($status: BackendStatus, $remote_backend_id: String) {
    viewer {
        backends(status: $status, remoteBackendId: $remote_backend_id) {
            id
            slug
            name
            status
            remoteBackendId
            remoteStatus
            data
            dataSchema
            dateRefreshed
            backendRegistrations {
                backendType {
                    id
                    schemaURL
                    slug
                    displayName
                    description
                }
                backendTypeId
                data
            }
        }
    }
    }
    """,
)


def get_product_backends(
    api: API,
    status: str = None,
    remote_backend_id: str = None,
) -> List[Backend]:
    """Fetch backends for product

    Parameters
    ----------
    api: API
        provides access to the product API
    status: str
        filter by backend status
    remote_backend_id: str
        filter by the backend id set by the product

    Returns
    -------
    List[Backend]
        The list of backends filtered by the params
    """
    platform_res = api.execute(op=get_backends_request, **locals())
    return [Backend.from_dict(b) for b in platform_res["viewer"]["backends"]]


backend_add_type_mutation = Operation(
    query="""
    mutation backendAddTypes(
        $backend_slug: String!,
        $backend_types: [BackendTypeInput!]
        ){
        backendAddTypes(input: {
            backendSlug: $backend_slug,
            backendTypes: $backend_types
        }) {
            backendSlug
            backendTypeSlugs
        }
    }
    """,
)


def backend_add_types(
    api: API,
    backend_slug: str,
    backend_types: List[BackendTypeInput],
) -> None:
    platform_res = api.execute(
        op=backend_add_type_mutation,
        backend_slug=backend_slug,
        backend_types=[t.as_dict() for t in backend_types],
    )
    if "backendAddTypes" not in platform_res:
        raise StrangeworksError.server_error(f"invalid response {platform_res}")


backend_remove_types_mutation = Operation(
    query="""
    mutation backendRemoveTypes($backend_slug: String!, $backend_type_slugs: [String!]){
        backendRemoveTypes(input: {
            backendSlug: $backend_slug,
            backendTypeSlugs: $backend_type_slugs
        }) {
            backendSlug
            backendTypeSlugs
        }
    }
    """,
)


def backend_remove_types(
    api: API,
    backend_slug: str,
    backend_type_slugs: List[str],
) -> None:
    platform_res = api.execute(op=backend_remove_types_mutation, **locals())
    if "backendRemoveTypes" not in platform_res:
        raise StrangeworksError.server_error(f"invalid response {platform_res}")


backend_create_mutation = Operation(
    query="""
    mutation backendCreate($backends: [ProductBackendInput!]){
        backendCreate(input: {backends: $backends}) {
            backends {
                id
                slug
                name
                status
                remoteBackendId
                remoteStatus
                data
                dataSchema
                dateRefreshed
                backendRegistrations {
                    backendType {
                        id
                        schemaURL
                        slug
                        displayName
                        description
                    }
                    backendTypeId
                    data
                }
            }
        }
    }
    """
)


def backend_create(
    api: API,
    payload: List[Backend],
) -> List[Backend]:
    backends = [b.to_create_request() for b in payload]
    platform_res = api.execute(
        op=backend_create_mutation,
        backends=backends,
    )

    if (
        "backendCreate" not in platform_res
        and "backends" not in platform_res["backendCreate"]
    ):
        raise StrangeworksError.server_error(f"invalid response {platform_res}")
    res = [
        Backend.from_dict(backend_dict)
        for backend_dict in platform_res["backendCreate"]["backends"]
    ]
    return res


backend_delete_mutation = Operation(
    query="""
    mutation backendDelete($backend_slug: String!){
        backendDelete(input: { backendSlug: $backend_slug })
    }
    """,
)


def backend_delete(
    api: API,
    backend_slug: str,
) -> None:
    api.execute(op=backend_delete_mutation, **locals())


backend_update_mutation = Operation(
    query="""
    mutation backendUpdate($backends: [ProductBackendUpdateInput!]){
        backendUpdate(input: {backends: $backends}) {
            backends {
                id
                slug
                name
                status
                remoteBackendId
                remoteStatus
                data
                dataSchema
                dateRefreshed
                backendRegistrations {
                    backendType {
                        id
                        schemaURL
                        slug
                        displayName
                        description
                    }
                    backendTypeId
                    data
                }
            }
        }
    }
    """,
)


def backend_update(
    api: API,
    backend_update_input: List[BackendUpdateInput],
) -> Backend:
    backends = [update.get() for update in backend_update_input]

    platform_res = api.execute(op=backend_update_mutation, backends=backends)
    if (
        "backendUpdate" not in platform_res
        and "backends" not in platform_res["backendUpdate"]
    ):
        raise StrangeworksError.server_error(f"invalid response {platform_res}")
    return [Backend.from_dict(res) for res in platform_res["backendUpdate"]["backends"]]
