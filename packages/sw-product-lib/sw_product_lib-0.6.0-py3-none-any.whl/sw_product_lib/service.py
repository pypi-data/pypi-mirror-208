"""product.py."""
import json
import os
import tempfile
from dataclasses import dataclass
from functools import singledispatch
from typing import Any, Dict, List, Optional, Union

import requests
from deprecated import deprecated
from fastapi import Request
from jose import jwt
from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.platform import auth
from strangeworks_core.platform.gql import API, APIInfo
from strangeworks_core.types.job import Status as JobStatus

from sw_product_lib.client import backend, billing, resource
from sw_product_lib.client.billing import BillingTransaction
from sw_product_lib.platform.gql import ProductAPI
from sw_product_lib.types import job
from sw_product_lib.types.job import AppliedJobTag, File, Job
from sw_product_lib.types.resource import Resource


DEFAULT_PLATFORM_BASE_URL = "https://api.strangeworks.com"
api_key = os.getenv("PRODUCT_LIB_API_KEY")
base_url = os.getenv("PRODUCT_LIB_BASE_URL", DEFAULT_PLATFORM_BASE_URL)


def _api():
    return (
        ProductAPI(api_key=api_key, base_url=base_url) if api_key and base_url else None
    )


@dataclass
class RequestContext:
    resource_token_id: str
    workspace_member_slug: str
    product_slug: str
    resource_slug: str
    job_id: Optional[str] = None
    resource_entitlements: Optional[List[str]] = None
    api: Optional[API] = None
    _auth_token: Optional[str] = None
    parent_job_slug: Optional[str] = None
    product_api_key: Optional[str] = api_key

    @staticmethod
    def new(
        workspace_member_slug: str,
        product_slug: str,
        resource_slug: str,
        resource_token_id: Optional[str] = None,
        job_id: Optional[str] = None,
        resource_entitlements: List[str] = None,
        api: Optional[API] = None,
        auth_token: Optional[str] = None,
        parent_job_slug: Optional[str] = None,
        product_api_key: Optional[str] = None,
    ):
        return RequestContext(
            resource_token_id=resource_token_id,
            workspace_member_slug=workspace_member_slug,
            product_slug=product_slug,
            resource_slug=resource_slug,
            job_id=job_id,
            resource_entitlements=resource_entitlements,
            api=api,
            _auth_token=auth_token,
            parent_job_slug=parent_job_slug,
            product_api_key=product_api_key or api_key,
        )

    @staticmethod
    def from_request(request: Request):
        token = request.headers.get("x-strangeworks-access-token")
        if not token:
            raise StrangeworksError.forbidden_error(
                message="request missing access token"
            )
        return RequestContext.from_jwt(
            token=token,
            parent_job_slug=request.headers.get("x-strangeworks-parent-job-slug"),
            _auth_token=token,
            product_api_key=api_key,
        )

    @staticmethod
    def from_jwt(token: str, **kwargs):
        # the key to verify each token will be available as API_SIGNING_KEY
        message = jwt.decode(token=token, key=None, options={"verify_signature": False})
        return RequestContext(
            resource_token_id=message["ResourceTokenID"],
            workspace_member_slug=message["WorkspaceMemberSlug"],
            product_slug=message["ProductSlug"],
            resource_slug=message["ResourceSlug"],
            resource_entitlements=message["ResourceEntitlements"],
            **kwargs,
        )


def create_job(
    ctx: RequestContext,
    external_identifier: Optional[str] = None,
    status: str = "CREATED",
    remote_status: Optional[str] = None,
    job_data_schema: Optional[str] = None,
    job_data: Optional[str] = None,
    **kvargs,
) -> Job:
    """Create a job entry for the request

    This method should be called only after the product has either has a job in place
    which will be executed either immediately or within a given period of time.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    parent_job_slug: Optional[str]
        slug of the job which created this job.
    external_identifier: Optional[str]
        id typically generated as a result of making a request to an external system.
    status: Optional[str]
        status of the job. Refer to the  platform for possible values.
    remote_status: Optional[str]
        status of job that was initiated on an  external (non-Strangeworks) system.
    job_data_schema: Optional[str]
        link to the json schema describing job output.
    job_data: Optional[str]
        job output.
    """
    return job.create(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
        workspace_member_slug=ctx.workspace_member_slug,
        parent_job_slug=ctx.parent_job_slug,
        external_identifier=external_identifier,
        status=status,
        remote_status=remote_status,
        job_data_schema=job_data_schema,
        job_data=job_data,
    )


def update_job(
    ctx: RequestContext,
    job_slug: str,
    parent_job_slug: Optional[str] = None,
    external_identifier: Optional[str] = None,
    status: Optional[str] = None,
    remote_status: Optional[str] = None,
    job_data_schema: Optional[str] = None,
    job_data: Optional[str] = None,
    **kvargs,
) -> Job:
    """Update the job identified by job_slug.


    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    job_slug: str
      slug of the job that needs values updated.
    parent_job_slug: Optional[str]
        slug of the job which created this job.
    external_identifier: Optional[str]
        id typically generated as a result of making a request to an external system.
    status: Optional[str]
        status of the job. Refer to the  platform for possible values.
    remote_status: Optional[str]
        status of job that was initiated on an  external (non-Strangeworks) system.
    job_data_schema: Optional[str]
        link to the json schema describing job output.
    job_data: Optional[str]
        job output.
    """
    return job.update(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
        job_slug=job_slug,
        parent_job_slug=parent_job_slug,
        external_identifier=external_identifier,
        status=status,
        remote_status=remote_status,
        job_data_schema=job_data_schema,
        job_data=job_data,
    )


def add_job_tags(
    ctx: RequestContext,
    job_slug: str,
    tags: List[str],
) -> List[AppliedJobTag]:
    """Apply a list of tags to a job.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    job_slug: str
      slug of the job that needs values updated.
    tags: List[str]
        list of tags to apply to the job
    """
    return job.add_tags(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
        job_slug=job_slug,
        tags=tags,
    )


def create_billing_transaction(
    ctx: RequestContext,
    job_slug: str,
    amount: float,
    unit: str = "USD",
    description: Optional[str] = None,
) -> BillingTransaction:
    """Create a billing transaction.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    job_slug: str
        used as identifier for the job.
    amount: float
        numerical amount. can be negative.
    unit: str
        describes the unit for the amount. for example, USD for currency.
    description: str
        a brief description that can be seen by the user.
    """
    return billing.create_transaction(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
        job_slug=job_slug,
        amount=amount,
        unit=unit,
        description=description,
    )


def request_job_clearance(
    ctx: RequestContext,
    amount: float,
    unit: str = "USD",
):
    """Request clearance from platform to run a job.

    Parameters
    ----------
    workspaceMemberSlug: str
            used to map workspace and user.
    amount: float
        numerical amount to indicate cost (negative amount) or credit(positive amount)
    unit: str
        unit for the amount
    """
    return billing.request_approval(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
        workspace_member_slug=ctx.workspace_member_slug,
        amount=amount,
        currency=unit,
    )


def get_resource(ctx: RequestContext) -> Resource:
    """Retrieve a resource definition.

    The resource slug, which is used to identify the resource entry, is retrieved
    from the request context object passed in.

    Parameters:
    ctx: RequestContext
        contains key-values specific to the current request.

    """
    return resource.get(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
    )


@singledispatch
def upload_job_artifact(
    data,
    ctx: RequestContext,
    job_slug: str,
    file_name: Optional[str] = None,
    json_schema: Optional[str] = None,
    label: Optional[str] = None,
    overwrite: bool = False,
    is_hidden: bool = False,
    sort_weight: int = 0,
    *args,
    **kwargs,
) -> File:
    """Upload payload as a file to the platform.

    Parameters
    ----------
    ctx: RequestContext
        used for making calls to service lib.
    job_slug: str
        maps the file to a job.
    data: Any
        file contents. Only dict supported at this time.
    file_name: Optional[str]
        the name of the file on the platform. if not supplied, the tempfile name will
        be used.
    json_schema: Optional[str]
        identifier or link to a json schema which corresponds to the file contents. If
        the file contents adhere to a schema, it is highly recommended that this field
        is populated.
    label: Optional[str]
        Optional string to set the display name of the file. Used by the platform
        portal.
    overwrite: bool
        indicates whether the file should be overwritten if its already been uploaded
        for the job. Defaults to False.
    is_hidden: bool
        If true, this file will not be displayed in the portal.
        This can be useful for supporting files that should be saved against the job,
        but typically would be referenced by URL in other contexts.
        (i.e.: an image file which is referenced in a JSON model.)
        This does **not*** prevent a user from accessing this file in other contexts,
        such as job archives.
    sort_weight: int
        This is the primary sorting instruction for JobFiles
        when returned to the client.
        The default is 0.
        Files with a higher sort order will be returned first.
        This allows you to control the order of files in the portal if desired.
    Returns
    -------
    None
    """
    with tempfile.NamedTemporaryFile(mode="+w") as tmp:
        tmp.write(data)
        tmp.flush()
        return upload_job_file(
            ctx=ctx,
            job_slug=job_slug,
            name=file_name or tmp.name,
            path=tmp.name,
            json_schema=json_schema,
            sort_weight=sort_weight,
            label=label,
            is_hidden=is_hidden,
            overwrite=overwrite,
        )


@upload_job_artifact.register
def _(
    data: dict,
    **kwargs,
) -> File:
    """Upload data in the form of ajson object as a file associated with a job.

    Note that the order of parameters is slightly different for this method with the
    data field coming first. This is to allow the singledispatch decorator to work.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    job_slug: str
        identifies which job the file is associated with.
    data: str
        string to be uploaded as a file.
    file_name: Optional[str]
        file name.
    label: Optional[str]
        Optional string to set the label for the file.
    overwrite: bool
        if True, overwrite the file if it already exists.
    is_hidden: bool
        if True, the file will not be visible to the user.
    sort_weight: int
        used to sort files in the UI.
    """
    as_str = json.dumps(data)
    return upload_job_artifact(
        as_str,
        **kwargs,
    )


def upload_job_file(
    ctx: RequestContext,
    job_slug: str,
    name: Optional[str],
    path: str,
    json_schema: Optional[str] = None,
    label: Optional[str] = None,
    overwrite: bool = False,
    is_hidden: bool = False,
    sort_weight: int = 0,
) -> File:
    """Upload a file associated with a job.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    job_slug: str
        identifies which job the file is associated with.
    name: Optional[str]
        file name.
    path: str
        fully qualified path to the file.
    json_schema: Optional[str]
        identifier or link to a json schema which corresponds to the file contents. If
        the file contents adhere to a schema, it is highly recommended that this field
        is populated.
    label: Optional[str]
        Optional string to set the display name of the file. Used by the platform
        portal.
    overwrite: bool
        indicates whether the file should be overwritten if its already been uploaded
        for the job. Defaults to False.
    is_hidden: bool
        If true, this file will not be displayed in the portal.
        This can be useful for supporting files that should be saved against the job,
        but typically would be referenced by URL in other contexts.
        (i.e.: an image file which is referenced in a JSON model.)
        This does **not*** prevent a user from accessing this file in other contexts,
        such as job archives.
    sort_weight: int
        This is the primary sorting instruction for JobFiles
        when returned to the client.
        The default is 0.
        Files with a higher sort order will be returned first.
        This allows you to control the order of files in the portal if desired.

    Return
    ------
    File
        Object with information about the file that was uploaded.

    raises StrangeworksError if any issues arise while attempting to upload the file.
    """
    f, signedUrl = job.upload_file(
        api=ctx.api or _api(),
        resource_slug=ctx.resource_slug,
        job_slug=job_slug,
        file_path=path,
        file_name=name,
        override_existing=overwrite,
        json_schema=json_schema,
        is_hidden=is_hidden,
        sort_weight=sort_weight,
        label=label,
    )
    try:
        fd = open(path, "rb")
    except IOError as e:
        raise StrangeworksError(message=f"unable to open file: {str(e)}")
    else:
        with fd:
            headers = {"content-type": "application/x-www-form-urlencoded"}
            r = requests.put(signedUrl, data=fd, headers=headers)
            if r.status_code not in {requests.codes.ok, requests.codes.no_content}:
                raise StrangeworksError(
                    "unable to upload job file", r.status_code, str(r.content)
                )

    return f


def get_job(ctx: RequestContext, job_slug: str) -> Job:
    """Get the job identified by job_slug.


    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    job_slug: str
        job_slug identifies the job which is fetched.

    Returns
    -------
    Job
        A Job object identified by the slug.
    """
    return job.get(api=ctx.api or _api(), resource_slug=ctx.resource_slug, id=job_slug)


def get_job_by_external_identifier(
    ctx: RequestContext, external_identifier: str
) -> Optional[Job]:
    """Get the job identified by external_identifier.
    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    external_identifier: str
        external_identifier identifies the job which is fetched.
    Returns
    -------
    Optional[Job]
        A Job object identified by the product identifier or None.
    """
    return job.get_by_external_identifier(
        api=ctx.api or _api(),
        id=external_identifier,
    )


def get_jobs_by_statuses(
    ctx: RequestContext, statuses: List[JobStatus]
) -> Optional[Dict[JobStatus, List[Job]]]:
    """Retrieve jobs filtered by job statuses.

    Parameters:
    ----------
     ctx: RequestContext
        contains key-values specific to the current request.
    statuses: List[JobStatus]
        the statuses used to filter for jobs.

    Returns:
    ----------
    A dictionary where the jobs are grouped by statuses.
    The keys in the dictionary are the statuses.
    Each status has their list of jobs.

    Optional[Dict[JobStatus, List[Job]]]
    """
    return job.get_by_statuses(api=ctx.api or _api(), statuses=statuses)


def get_backends(
    ctx: RequestContext,
    product_slugs: Optional[List[str]] = None,
    backend_type_slugs: Optional[List[str]] = None,
    backend_statuses: Optional[List[str]] = None,
    backend_tags: Optional[List[str]] = None,
) -> List[backend.Backend]:
    """Get the backends that live in strangeworks platform.
    Backends can be filtered by various input parameters.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    product_slugs: Optional[List[str]]
        filter by one or more product slugs
    backend_type_slugs: Optional[List[str]]
        filter by one or more backendType slugs
    backend_statuses: Optional[List[str]]
        filter by one or more backend statuses
    backend_tags: Optional[List[str]]
        filter by one or more backend tags
    status: Optional[str]
        filter by status, optional
    remote_backend_id: Optional[str]
        filter by remote backend id, optional

    Returns
    -------
    List[Backend]
        The list of backend filtered by the params
    """
    return backend.get_backends(
        api=ctx.api or _api(),
        product_slugs=product_slugs,
        backend_type_slugs=backend_type_slugs,
        backend_statuses=backend_statuses,
        backend_tags=backend_tags,
    )


def get_product_backends(
    ctx: RequestContext,
    status: Optional[str] = None,
    remote_backend_id: Optional[str] = None,
) -> List[backend.Backend]:
    """Get the backends that this product owns.
    Backends can be filtered by various input parameters.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    status: Optional[str]
        filter by status, optional
    remote_backend_id: Optional[str]
        filter by remote backend id, optional

    Returns
    -------
    List[Backend]
        The list of backend filtered by the params
    """
    return backend.get_product_backends(
        api=ctx.api or _api(), status=status, remote_backend_id=remote_backend_id
    )


def create_backends(
    ctx: RequestContext, backends: List[backend.Backend]
) -> List[backend.Backend]:
    """Create backends specified by the payload

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    backends: List[Backend]
        backends to create

    Returns
    -------
    List[Backend]
        The list of backends created
    """
    return backend.backend_create(api=ctx.api or _api(), payload=backends)


def delete_backend(ctx: RequestContext, backend_slug: str) -> None:
    """Delete backend by slug

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    backend_slug: str
        backend to delete

    Returns
    -------
    None
    """
    return backend.backend_delete(api=ctx.api or _api(), backend_slug=backend_slug)


def update_backends(
    ctx: RequestContext, backends: List[backend.BackendUpdateInput]
) -> List[backend.Backend]:
    """Update backends specified by the payload
    Overwites all write-able fields, so must include
    original payload, otherwise some fields could be deleted

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    backends: List[BackendUpdateInput]
        backend update input for each backend to update

    Returns
    -------
    List[Backend]
        The list of backends updated
    """
    return backend.backend_update(api=ctx.api or _api(), backend_update_input=backends)


def add_backend_types(
    ctx: RequestContext, backend_slug: str, types: List[backend.BackendTypeInput]
):
    """Add backend types to a certain backend.
    Strangeworks defines certain types a backend can adhere to.
    This registers the specified backend with the many types provided.
    The type slugs have to be known by Strangeworks.
    Will raise a StrangeworksError if any types are unkown.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    backend_slug: str
        backend slug that identifies the backend which you will add types to
    types: List[backend.BackendTypeInput]
        the many types you are registering to this backend.

    """
    backend.backend_add_types(
        api=ctx.api or _api(), backend_slug=backend_slug, backend_types=types
    )


def remove_backend_types(ctx: RequestContext, backend_slug: str, types: List[str]):
    """Remove backend types from a certain backend.
    Strangeworks defines certain types a backend can adhere to.
    This un-registers the specified backend with the many types provided.
    The type slugs have to be known by Strangeworks.
    Will raise a StrangeworksError if any types are unkown.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    backend_slug: str
        backend slug that identifies the backend which you will add types to
    types: List[str]
        the many types you are un-registering from this backend.

    """
    backend.backend_remove_types(
        api=ctx.api or _api(), backend_slug=backend_slug, backend_types=types
    )


@deprecated(
    reason=(
        "This function is deprecated and will be removed. Use auth.get_token instead."
    )
)
def get_token(key: Optional[str] = None, url: Optional[str] = None) -> str:
    """Obtain a product api token.

    This function is deprecated and will be removed in a future release. Use the
    auth.get_token function to obtain a one-time token or obtain a Callable using
    auth.get_authenticator to refresh tokens from clients such as requests.

    Parameters
    ----------
    key: Optional[str]
        key to use to obtain the token.
    url: Optional[str]
        strangeworks platform base url.

    Return
    ------
    :str
        A JWT token to make calls to the platform.
    """
    return auth.get_token(
        api_key=key or api_key,
        base_url=url or base_url,
        auth_url=APIInfo.PRODUCT.value.get("auth_url"),
    )


def execute_subjob(
    ctx: RequestContext,
    subjob_resource: Resource,
    parent_job: Union[str, Job],
    subjob_path: Optional[str] = None,
    subjob_payload: Optional[Dict[str, Any]] = None,
) -> Job:
    """Execute a subjob.

    Parameters
    ----------
    ctx: RequestContext
        contains key-values specific to the current request.
    subjob_resource: Resource
        The resource to execute the subjob on.
    parent_job: Union[str, Job]
        A string or job object with the parent job slug.
    parent_job_slug: Optional[str]
        The slug of the parent job of the sub-job.
    subjob_path: Optional[str]
        The path to the sub-job.
    subjob_payload: Optional[Dict[str, Any]]
        The payload of the sub-job.

    Returns
    -------
    Job
        A job object denoting the sub-job.
    """
    parent_slug = parent_job.slug if isinstance(parent_job, Job) else parent_job
    if not parent_slug:
        raise ValueError("parent_job (slug or Job object) must be provided.")
    retval = job.execute_subjob(
        parent_job_slug=parent_slug,
        api_key=ctx.product_api_key,
        proxy_auth_token=ctx._auth_token,
        resource=subjob_resource,
        path=subjob_path,
        data=subjob_payload,
        base_url=base_url,
    )
    as_json = retval.json()

    return Job.from_dict(as_json)
