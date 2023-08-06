import os
import time
import uuid
import logging
import requests

from requests.models import Response
from json import JSONDecodeError
from functools import wraps

from typing import Any, Dict, List, Optional, Literal

from vecdb.utils import document
from vecdb.types import Credentials, FieldTransformer, Filter, Schema

from vecdb import __version__


LOG_REQUESTS = bool(os.getenv("LOG_REQUESTS"))
if LOG_REQUESTS:
    # Get the current Unix timestamp as a string
    timestamp = str(int(time.time()))

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(f"{timestamp}_request_logs.log")],
    )
else:
    logger = logging.getLogger(__name__)
    # logger.setLevel(logging.DEBUG)


def to_curl(request: requests.PreparedRequest):
    command = "curl -X {method} '{url}'".format(method=request.method, url=request.url)

    for header, value in request.headers.items():
        if header.lower() == "authorization":
            value = "MASKED"
        command += " -H '{header}: {value}'".format(header=header, value=value)

    if request.body:
        command += " -d '{data}'".format(data=request.body)

    return command


def log_request(request: requests.PreparedRequest):
    curl_command = to_curl(request)
    logging.debug(curl_command)


def log_response(response: requests.Response):
    logging.debug("Response Headers: %s", response.headers)
    logging.debug("Response Content: %s\n", response.text)


def get_response(response: requests.Response) -> Dict[str, Any]:
    # get a json response
    # if errors - print what the response contains
    if response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            logger.exception(e)
            raise e
    else:
        datum = {"error": response.content.decode("utf-8")}
        if "x-trace-id" in response.headers:
            datum["x-trace-id"] = response.headers["x-trace-id"]

        try:
            # Log this somewhere if it errors
            logger.error(datum)
        except Exception as no_content_e:
            # in case there's no content
            logger.exception(no_content_e)
            # we still want to raise the right error for retrying
            # continue to raise exception so that any retry logic still holds
            raise no_content_e


# We implement retry as a function for several reasons
# first - we can get a
def retry(num_of_retries: int = 3, timeout: int = 30):
    """
    Allows the function to retry upon failure.
    Args:
        num_of_retries: The number of times the function should retry
        timeout: The number of seconds to wait between each retry
    """
    num_of_retries = 3
    timeout = 30

    def _retry(func):
        @wraps(func)
        def function_wrapper(*args, **kwargs):
            for i in range(num_of_retries):
                try:
                    return func(*args, **kwargs)
                # Using general error to avoid any possible error dependencies.
                except (ConnectionError, JSONDecodeError) as error:
                    logger.exception(error)
                    print(f"Sleeping in {timeout}")
                    time.sleep(timeout)
                    if i == num_of_retries - 1:
                        raise error
                    continue
                except Exception as error:
                    print(error)
                    logger.exception(error)

        return function_wrapper

    return _retry


class API:
    def __init__(self, credentials: Credentials, job_id: str = None, name: str = None) -> None:
        self._credentials = credentials
        self._base_url = f"https://api-{self.credentials.region}.stack.tryrelevance.com/latest"
        self._headers = dict(
            Authorization=f"{self.credentials.project}:{self.credentials.api_key}", vecdb_version=__version__
        )
        if job_id is not None:
            self.headers.update(vecdb_job_id=job_id)
        if name is not None:
            self.headers.update(vecdb_name=name)

        self.session = requests.Session()

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def headers(self) -> Dict[str, str]:
        return self._headers

    @retry()
    def _request(self, method: Literal["GET", "POST"], suffix: str, *args, **kwargs) -> Response:
        request = requests.Request(method=method, url=self.base_url + suffix, headers=self.headers, *args, **kwargs)
        prepared_request = request.prepare()

        if LOG_REQUESTS:
            log_request(prepared_request)

        response = self.session.send(prepared_request)

        if LOG_REQUESTS:
            log_response(response)

        return response

    def get(self, suffix: str, *args, **kwargs) -> Response:
        return self._request(method="GET", suffix=suffix, *args, **kwargs)

    def post(self, suffix: str, *args, **kwargs) -> Response:
        return self._request(method="POST", suffix=suffix, *args, **kwargs)

    def _list_datasets(self):
        response = self.get(suffix="/datasets/list")
        return get_response(response)

    def _create_dataset(
        self, dataset_id: str, schema: Optional[Schema] = None, upsert: bool = True, expire: bool = False
    ) -> Any:
        response = self.post(
            suffix=f"/datasets/create", json=dict(id=dataset_id, schema=schema, upsert=upsert, expire=expire)
        )
        return get_response(response)

    def _delete_dataset(self, dataset_id: str) -> Any:
        response = self.post(suffix=f"/datasets/{dataset_id}/delete")
        return get_response(response)

    def _get_schema(self, dataset_id: str) -> Schema:
        response = self.get(suffix=f"/datasets/{dataset_id}/schema")
        return get_response(response)

    def _bulk_insert(
        self,
        dataset_id: str,
        documents: List[document.Document],
        insert_date: bool = True,
        overwrite: bool = True,
        update_schema: bool = True,
        wait_for_update: bool = True,
        field_transformers: List[FieldTransformer] = None,
        ingest_in_background: bool = False,
        encoders: list = None,
    ) -> Any:
        response = self.post(
            suffix=f"/datasets/{dataset_id}/documents/bulk_insert",
            json=dict(
                documents=documents,
                insert_date=insert_date,
                overwrite=overwrite,
                update_schema=update_schema,
                field_transformers=[] if field_transformers is None else field_transformers,
                ingest_in_background=ingest_in_background,
                wait_for_update=wait_for_update,
                encoders=encoders if encoders else [],
            ),
        )
        return get_response(response)

    def _bulk_update(
        self,
        dataset_id: str,
        documents: List[document.Document],
        insert_date: bool = True,
        ingest_in_background: bool = True,
        update_schema: bool = True,
    ) -> Any:
        response = self.post(
            suffix=f"/datasets/{dataset_id}/documents/bulk_update",
            json=dict(
                updates=documents,
                insert_date=insert_date,
                ingest_in_background=ingest_in_background,
                update_schema=update_schema,
            ),
        )
        return get_response(response)

    def _get_where(
        self,
        dataset_id: str,
        page_size: int = None,
        sort: list = None,
        filters: List[Filter] = None,
        select_fields: List[str] = None,
        include_vector: bool = None,
        after_id: list = None,
        query: str = None,
        vector_search_query: dict = None,
    ):
        json = {}
        if page_size:
            json["page_size"] = page_size
        if sort:
            json["sort"] = sort
        if filters:
            json["filters"] = filters
        if select_fields:
            json["select_fields"] = select_fields
        if include_vector:
            json["include_vector"] = include_vector
        if after_id:
            json["after_id"] = after_id
        if query:
            json["query"] = query
        if vector_search_query:
            json["vector_search_query"] = vector_search_query
        response = self.post(suffix=f"/datasets/{dataset_id}/documents/get_where", json=json)
        return get_response(response)

    def _delete_where(self, dataset_id: str, filters: Optional[List[Filter]] = None):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/documents/delete_where",
            json=dict(filters=[] if filters is None else filters),
        )
        return get_response(response)

    def _update_dataset_metadata(self, dataset_id: str, metadata: Dict[str, Any]):
        """
        Edit and add metadata about a dataset. Notably description, data source, etc
        """
        response = self.post(
            suffix=f"/datasets/{dataset_id}/metadata", json=dict(dataset_id=dataset_id, metadata=metadata)
        )
        return get_response(response)

    def _get_metadata(self, dataset_id: str) -> Dict[str, Any]:
        response = self.get(suffix=f"/datasets/{dataset_id}/metadata")
        return get_response(response)

    def _insert_centroids(
        self, dataset_id: str, cluster_centers: List[document.Document], vector_fields: List[str], alias: str
    ):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/cluster/centroids/insert",
            json=dict(dataset_id=dataset_id, cluster_centers=cluster_centers, vector_fields=vector_fields, alias=alias),
        )
        return get_response(response)

    def _get_centroids(
        self,
        dataset_id: str,
        vector_fields: List[str],
        alias: str,
        page_size: int = 5,
        page: int = 1,
        cluster_ids: Optional[List] = None,
        include_vector: bool = False,
    ):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/cluster/centroids/documents",
            json=dict(
                cluster_ids=[] if cluster_ids is None else cluster_ids,
                vector_fields=vector_fields,
                alias=alias,
                page_size=min(9999, page_size),
                page=page,
                include_vector=include_vector,
            ),
        )
        return get_response(response)

    def _get_health(self, dataset_id: str):
        response = self.get(suffix=f"/datasets/{dataset_id}/monitor/health")
        return get_response(response)

    def _get_workflow_status(self, job_id: str):
        response = self.post(suffix=f"/workflows/{job_id}/get")
        return get_response(response)

    def _update_workflow_metadata(self, job_id: str, metadata: Dict[str, Any]):
        response = self.post(suffix=f"/workflows/{job_id}/metadata", json=dict(metadata=metadata))
        return get_response(response)

    def _get_file_upload_urls(self, dataset_id: str, files: List[str]):
        response = self.post(suffix=f"/datasets/{dataset_id}/get_file_upload_urls", json=dict(files=files))
        return get_response(response)

    def _get_temp_file_upload_url(self):
        """Use this for temporary file uploads.
        returns: {'download_url': ..., 'upload_url': ...}
        """
        response = self.post(suffix=f"/services/get_temporary_file_upload_url")
        return get_response(response)

    def _upload_temporary_media(self, presigned_url: str, media_content: bytes):
        return requests.put(presigned_url, headers={"x-amz-tagging": "Expire=true"}, data=media_content)

    def _upload_media(self, presigned_url: str, media_content: bytes):
        # dont use get response since response cannot be json decoded
        return requests.put(presigned_url, data=media_content)

    def _facets(
        self,
        dataset_id: str,
        fields: List[str],
        data_interval: str = "monthly",
        page_size: int = 1000,
        asc: bool = False,
    ):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/facets",
            json=dict(fields=fields, data_interval=data_interval, page_size=min(9999, page_size), asc=asc),
        )
        return get_response(response)

    def _upsert_dataset_settings(self, dataset_id: str, settings: Optional[Dict[str, Any]] = None):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/settings", json=dict(settings={} if settings is None else settings)
        )
        return get_response(response)

    def _get_dataset_settings(self, dataset_id: str):
        response = self.get(suffix=f"/datasets/{dataset_id}/settings")
        return get_response(response)

    def _create_deployable(self, dataset_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        response = self.post(
            suffix="/deployables/create",
            json=dict(dataset_id=dataset_id, configuration={} if config is None else config),
        )
        return get_response(response)

    def _aggregate(
        self,
        dataset_id: str,
        page_size: str = 20,
        page: str = 1,
        asc: str = False,
        aggregation_query: Dict[str, List[Dict[str, Any]]] = None,
        dataset_ids: List[str] = None,
        filters: List[Filter] = None,
    ):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/aggregate",
            json=dict(
                filters=[] if filters is None else filters,
                aggregation_query=aggregation_query,
                page_size=min(9999, page_size),
                page=page,
                asc=asc,
                dataset_ids=[] if dataset_ids is None else dataset_ids,
                dataset_id=dataset_id,
            ),
        )
        return get_response(response)

    def _list_closest_to_center(
        self,
        dataset_id: str,
        vector_fields: List[str],
        alias: str,
        approx: int = 0,
        sum_fields: bool = True,
        page: int = 1,
        similarity_metric: str = "cosine",
        min_score: float = 0,
        include_vector: bool = False,
        include_count: bool = True,
        include_relevance: bool = False,
        page_size: int = 20,
        cluster_properties_filter: Dict[str, Any] = None,
        cluster_ids: List[str] = None,
        filters: List[Filter] = None,
        select_fields: List[str] = None,
    ):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/cluster/centroids/list_closest_to_center",
            json=dict(
                vector_fields=vector_fields,
                alias=alias,
                approx=approx,
                sum_fields=sum_fields,
                page=page,
                similarity_metric=similarity_metric,
                min_score=min_score,
                include_vector=include_vector,
                include_count=include_count,
                include_relevance=include_relevance,
                page_size=min(9999, page_size),
                cluster_properties_filter=cluster_properties_filter if cluster_properties_filter is not None else {},
                filters=filters if filters is not None else [],
                cluster_ids=cluster_ids if cluster_ids is not None else [],
                select_fields=select_fields if select_fields is not None else [],
            ),
        )
        return get_response(response)

    def _list_project_keys(self):
        response = self.get(suffix="/projects/keys/list")
        return get_response(response)

    def _get_project_key(self, key: str, token: str):
        response = self.post(suffix="/projects/keys/get", json=dict(key=key, token=token))
        return get_response(response)

    def _set_project_key(self, key: str, value: str):
        response = self.post(suffix="/projects/keys/set", json=dict(key=key, value=value))
        return get_response(response)

    def _delete_project_key(self, key: str):
        response = self.post(suffix="/projects/keys/delete", json=dict(key=key))
        return get_response(response)

    def _update_version_aliases(self, development_version: str, production_version: str):
        response = self.post(
            suffix="/workflows/types/version_aliases/update",
            json={"aliases": {"development_version": development_version, "production_version": production_version}},
        )
        return get_response(response)

    def _search(self, dataset_id: str, query: str, page_size: int, filters: Optional[List[Filter]]):
        response = self.post(
            suffix=f"/datasets/{dataset_id}/search",
            json={"query": query, "pageSize": page_size, "filters": [] if filters is None else filters},
        )
        return get_response(response)
