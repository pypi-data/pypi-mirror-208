import time
import logging

from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Union

from vecdb.api import api
from vecdb.api import helpers
from vecdb import types
from vecdb import errors

import vecdb.collections.field
from vecdb.utils import document

from concurrent.futures import ThreadPoolExecutor


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class Dataset:
    def __init__(self, api: api.API, dataset_id: str):
        self._api = api
        self._dataset_id = dataset_id

    @property
    def api(self) -> api.API:
        return self._api

    @classmethod
    def from_details(cls: "Dataset", dataset_id: str, token: str) -> "Dataset":
        return cls(api.API(helpers.process_token(token)), dataset_id)

    @property
    def token(self):
        return self.api.credentials.token

    def __getitem__(self, index: str) -> vecdb.collections.field.Field:
        if isinstance(index, str):
            return vecdb.collections.field.Field(dataset=self, field=index)
        else:
            raise NotImplementedError("index must of type `str` (field in dataset)")

    def __len__(self, *args, **kwargs) -> int:
        return self.search(1, *args, **kwargs)["count"]

    @property
    def dataset_id(self) -> str:
        return self._dataset_id

    @property
    def schema(self) -> types.Schema:
        return self.api._get_schema(self._dataset_id)

    def health(self) -> Dict[str, Any]:
        return self.api._get_health(self._dataset_id)

    def bulk_insert(
        self,
        documents: Union[List[document.Document], document.DocumentList],
        insert_chunksize: int = 20,
        max_workers: int = 2,
        **kwargs,
    ):
        def chunk_documents_with_kwargs(documents):
            for i in range(len(documents) // insert_chunksize + 1):
                yield {"documents": documents[i * insert_chunksize : (i + 1) * insert_chunksize], **kwargs}

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = executor.map(lambda kw: self.insert(**kw), chunk_documents_with_kwargs(documents))

        results = {"inserted": 0, "failed_documents": []}
        for result in futures:
            results["inserted"] += result["inserted"]
            results["failed_documents"] += result["failed_documents"]

        return results

    def insert(
        self,
        documents: Union[List[document.Document], document.DocumentList] = None,
        ids: List[str] = None,
        data: List[str] = None,
        metadata: List[Dict[str, Any]] = None,
        vector: List[List[float]] = None,
        encoders: List[types.Encoder] = None,
        *args,
        **kwargs,
    ) -> Dict[str, Any]:

        encoders = [] if encoders is None else encoders
        if not encoders:
            encoders += [{"model_name": "all-mpnet-base-v2", "field": "text", "body": "text"}]

        if not documents:
            if metadata:
                assert len(data) == len(metadata)
                documents = [{"text": d, **md} for d, md in zip(data, metadata)]

            else:
                documents = [{"text": d} for d in data]

            if vector:
                assert len(vector) == len(data)
                for index, document in enumerate(documents):
                    document["text_vector_"] = vector[index]

            if ids:
                assert len(ids) == len(data)
                for index, document in enumerate(documents):
                    document["_id"] = ids[index]

        if hasattr(documents, "to_json"):
            documents = documents.to_json()
        else:
            for index in range(len(documents)):
                if hasattr(documents[index], "to_json"):
                    documents[index] = documents[index].to_json()

        return self.api._bulk_insert(
            dataset_id=self._dataset_id, documents=documents, encoders=encoders, *args, **kwargs
        )

    def update(
        self,
        documents: Union[List[document.Document], document.DocumentList],
        insert_date: bool = True,
        ingest_in_background: bool = True,
        update_schema: bool = True,
    ) -> Dict[str, Any]:
        if hasattr(documents, "to_json"):
            documents = documents.to_json()
        else:
            for index in range(len(documents)):
                if hasattr(documents[index], "to_json"):
                    documents[index] = documents[index].to_json()
        return self.api._bulk_update(
            dataset_id=self._dataset_id,
            documents=documents,
            insert_date=insert_date,
            ingest_in_background=ingest_in_background,
            update_schema=update_schema,
        )

    def search(
        self,
        page_size: int = None,
        sort: list = None,
        filters: List[types.Filter] = None,
        select_fields: List[str] = None,
        include_vector: bool = None,
        after_id: list = None,
        text: str = None,
        vector: List[float] = None,
        field: str = None,
        model: str = "all-mpnet-base-v2",
        query: dict = None,
    ) -> Dict[str, Any]:

        if text or vector:
            vector_search_query = {}

            vector_search_query["model"] = model
            if text:
                vector_search_query["query"] = text
            if vector:
                vector_search_query["vector"] = vector
            if not field:
                vector_search_query["field"] = "text_vector_"

        elif query:
            vector_search_query = query

        else:
            vector_search_query = None

        res = self.api._get_where(
            dataset_id=self._dataset_id,
            page_size=page_size,
            filters=filters,
            sort=sort,
            select_fields=select_fields,
            include_vector=include_vector,
            after_id=after_id,
            vector_search_query=vector_search_query,
        )
        res["documents"] = document.DocumentList(res["documents"])
        return res

    def delete(self, filters: Optional[List[types.Filter]] = None, ids: Union[str, list] = None) -> Dict[str, Any]:
        if not filters:
            filters = []
        if ids:
            if isinstance(ids, str):
                ids = [ids]
            filters += self["ids"] == ids
        res = self.api._delete_where(dataset_id=self._dataset_id, filters=filters)
        return res

    def get_all(
        self,
        page_size: int = 64,
        filters: Optional[List[types.Filter]] = None,
        select_fields: Optional[List[str]] = None,
        sort: Optional[list] = None,
        include_vector: bool = True,
        after_id: Optional[List] = None,
        max_retries: int = 3,
        retry_delay: int = 2,
    ) -> Dict[str, Any]:
        documents = []
        retry_count = 0
        while True:
            try:
                chunk = self.search(
                    page_size=page_size,
                    filters=filters,
                    select_fields=select_fields,
                    after_id=after_id,
                    sort=sort,
                    include_vector=include_vector,
                )
            except ConnectionError as e:
                logger.exception(e)
                retry_count += 1
                time.sleep(retry_delay)

                if retry_count >= max_retries:
                    raise errors.MaxRetriesError("max number of retries exceeded")

            except JSONDecodeError as e:
                logger.exception(e)
                retry_count += 1
                time.sleep(retry_delay)

                if retry_count >= max_retries:
                    raise errors.MaxRetriesError("max number of retries exceeded")

            else:
                after_id = chunk["after_id"]
                if not chunk["documents"]:
                    break
                documents += chunk["documents"]
                retry_count = 0

        res = {}
        res["documents"] = document.DocumentList(documents)
        return res

    def len(self, *args, **kwargs):
        """
        Get length of dataset, usually used with filters
        """
        return self.api._get_where(dataset_id=self._dataset_id, page_size=1, *args, **kwargs)["count"]

    def insert_metadata(self, metadata: Dict[str, Any]):
        return self.api._update_dataset_metadata(dataset_id=self._dataset_id, metadata=metadata)

    def update_metadata(self, metadata: Dict[str, Any]):
        old_metadata: dict = self.get_metadata()["results"]

        def merge_dicts(dict1, dict2):
            """Recursively merges dict2 into dict1"""
            if not isinstance(dict1, dict) or not isinstance(dict2, dict):
                return dict2
            for k in dict2:
                if k in dict1:
                    dict1[k] = merge_dicts(dict1[k], dict2[k])
                else:
                    dict1[k] = dict2[k]
            return dict1

        return self.api._update_dataset_metadata(
            dataset_id=self._dataset_id, metadata=merge_dicts(old_metadata, metadata)
        )

    def get_metadata(self) -> Dict[str, Any]:
        return self.api._get_metadata(dataset_id=self._dataset_id)

    def insert_local_medias(self, file_paths: List[str]) -> List[str]:
        presigned_urls = self.api._get_file_upload_urls(self.dataset_id, files=file_paths)
        urls = []
        for index, file_path in enumerate(file_paths):
            url = presigned_urls["files"][index]["url"]
            upload_url = presigned_urls["files"][index]["upload_url"]
            with open(file_path, "rb") as fn_byte:
                media_content = bytes(fn_byte.read())
            urls.append(url)
            response = self.api._upload_media(presigned_url=upload_url, media_content=media_content)
            assert response.status_code == 200
        return urls

    def facets(self, fields: List[str], data_interval: str = "monthly", page_size: int = 10000, asc: bool = False):
        return self.api._facets(
            dataset_id=self.dataset_id, fields=fields, data_interval=data_interval, page_size=page_size, asc=asc
        )

    def aggregate(
        self,
        page_size: str = 20,
        page: str = 1,
        asc: str = False,
        groupby: List[types.GroupBy] = None,
        metrics: List[types.Metric] = None,
        sort: List[Any] = None,
        dataset_ids: List[str] = None,
        filters: List[types.Filter] = None,
    ):
        return self.api._aggregate(
            dataset_id=self._dataset_id,
            page_size=page_size,
            page=page,
            asc=asc,
            aggregation_query=dict(
                groupby=[] if groupby is None else groupby,
                metrics=[] if metrics is None else metrics,
                sort=[] if sort is None else sort,
            ),
            dataset_ids=dataset_ids,
            filters=filters,
        )

    def get_settings(self):
        return self.api._get_dataset_settings(self.dataset_id)

    def update_settings(self, settings: Dict[str, Any]):
        return self.api._upsert_dataset_settings(dataset_id=self.dataset_id, settings=settings)
