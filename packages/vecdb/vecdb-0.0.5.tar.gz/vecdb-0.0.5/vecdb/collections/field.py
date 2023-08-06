import uuid
import numpy as np

from typing import Dict, Any, List, Optional, Union

from vecdb import types

from vecdb.utils import document


class Field:
    def __init__(self, dataset, field: str):
        from vecdb.collections.dataset import Dataset

        self._dataset: Dataset = dataset
        self._field = field
        if field != "_id":
            self._dtype = dataset.schema.get(field)
        else:
            self._dtype = None
        self._filter_type = self._get_filter_type()

    @property
    def dataset(self):
        return self._dataset

    @property
    def dataset_id(self):
        return self._dataset.dataset_id

    @property
    def field(self):
        return self._field

    def list_field_parents(self) -> List[str]:
        all_field_children = self.dataset.list_field_children()["results"]
        field_parents = []
        for relationship in all_field_children:
            if self.field in relationship["field_children"]:
                field_parents += [relationship["field"]]
        return list(set(field_parents))

    def list_field_children(self) -> List[str]:
        all_field_children = self.dataset.list_field_children()["results"]
        field_children = []
        for relationship in all_field_children:
            if relationship["field"] == self.field:
                field_children += relationship["field_children"]
        return list(set(field_children))

    def add_field_children(
        self,
        field_children: List[str],
        fieldchildren_id: str = None,
        metadata: Dict[str, Any] = None,
        recursive: bool = False,
    ):
        if fieldchildren_id is None:
            fieldchildren_id = str(uuid.uuid4())
        return self.dataset.set_field_children(
            fieldchildren_id=fieldchildren_id,
            field=self.field,
            field_children=field_children,
            recursive=recursive,
            metadata=metadata,
        )

    def _get_filter_type(self) -> str:
        if self._dtype == "numeric":
            filter_type = "numeric"
        elif self._dtype == "date":
            filter_type = "date"
        elif self._dtype is None:
            filter_type = "ids"
        else:
            filter_type = "exact_match"
        return filter_type

    def __eq__(self, other: Union[str, float, int, bool, None], filter_type: Optional[str] = None) -> types.Filter:
        if filter_type is None:
            filter_type = self._filter_type
        return [{"field": self._field, "filter_type": filter_type, "condition": "==", "condition_value": other}]

    def __lt__(self, other: Union[str, float, int, bool, None], filter_type: Optional[str] = None) -> types.Filter:
        if filter_type is None:
            filter_type = self._filter_type
        return [{"field": self._field, "filter_type": filter_type, "condition": "<", "condition_value": other}]

    def __le__(self, other: Union[str, float, int, bool, None], filter_type: Optional[str] = None) -> types.Filter:
        if filter_type is None:
            filter_type = self._filter_type
        return [{"field": self._field, "filter_type": filter_type, "condition": "<=", "condition_value": other}]

    def __gt__(self, other: Union[str, float, int, bool, None], filter_type: Optional[str] = None) -> types.Filter:
        if filter_type is None:
            filter_type = self._filter_type
        return [{"field": self._field, "filter_type": filter_type, "condition": ">", "condition_value": other}]

    def __ge__(self, other: Union[str, float, int, bool, None], filter_type: Optional[str] = None) -> types.Filter:
        if filter_type is None:
            filter_type = self._filter_type
        return [{"field": self._field, "filter_type": filter_type, "condition": ">=", "condition_value": other}]

    def contains(self, other: str) -> types.Filter:
        return [{"field": self._field, "filter_type": "contains", "condition": "==", "condition_value": other}]

    def exists(self) -> types.Filter:
        if "_chunk_" in self._field:
            count = self._field.count(".")
            if count:
                parent_field = self._field.split(".")[0]
            else:
                parent_field = self._field

            return [{"chunk": {"path": parent_field, "filters": [{"fieldExists": {"field": self._field}}]}}]
        return [{"field": self._field, "filter_type": "exists", "condition": "==", "condition_value": " "}]

    def not_exists(self) -> types.Filter:
        return [{"field": self._field, "filter_type": "exists", "condition": "!=", "condition_value": " "}]

    def insert_centroids(self, centroid_documents: document.DocumentList):
        raise NotImplementedError(f"`insert_centroids` not available for non-vector fields")

    def label_openai(
        self,
        field: str,
        question_suffix: str,
        accuracy: int = 4,
        cluster_ids: list = None,
        dont_save_summaries: bool = True,
        filters: list = None,
    ):
        raise NotImplementedError(f"`label_openai` not available for non-vector fields")

    def get_centroids(
        self, page_size: int = 5, page: int = 1, cluster_ids: Optional[List] = None, include_vector: bool = False
    ):
        raise NotImplementedError(f"`get_centroids` not available for non-vector fields")

    def get_all_centroids(self):
        raise NotImplementedError(f"`get_all_centroids` not available for non-vector fields")

    def create_centroid_documents(self):
        raise NotImplementedError(f"`create_centroid_documents` not available for non-vector fields")

    def list_closest_to_center(
        self,
        centroid_vector_fields: List[str],
        cluster_field: str,
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
        filters: List[types.Filter] = None,
        select_fields: List[str] = None,
    ):
        raise NotImplementedError("`list_closest_to_center` not available for non-vector fields")

    def get_keyphrase(self, keyphrase_id: str):
        raise NotImplementedError(f"`get_keyphrase` not available for non-keyphrase fields")

    def update_keyphrase(
        self,
        keyphrase_id: str,
        alias: str,
        keyphrase: str,
        frequency: int = 0,
        ancestors: list = None,
        parents: list = None,
        metadata: dict = None,
        keyphrase_score: float = 0,
        level: int = 0,
    ):
        raise NotImplementedError(f"`update_keyphrase` not available for non-keyphrase fields")

    def delete_keyphrase(self, keyphrase_id: str):
        raise NotImplementedError(f"`delete_keyphrase` not available for non-keyphrase fields")

    def bulk_update_keyphrases(self, updates: List[dict]):
        raise NotImplementedError(f"`bulk_update_keyphrases` not available for non-keyphrase fields")

    def list_keyphrases(self, page_size: int = 100, page: int = 1, sort: list = None):
        raise NotImplementedError(f"`list_keyphrases` not available for non-keyphrase fields")

    def search(self, query_vector: List[float], page_size: int = 20, filters: list = None):
        return self._dataset.api._search(
            dataset_id=self.dataset._dataset_id, query=query_vector, page_size=page_size, filters=filters
        )
