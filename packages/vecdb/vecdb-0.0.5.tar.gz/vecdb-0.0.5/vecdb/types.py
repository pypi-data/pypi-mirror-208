from typing import Any, Dict, List, NamedTuple, NewType, Literal, Union


Vector = NewType("Vector", List[float])

Filter = NewType("Filter", Dict[str, Any])

FieldTransformer = NewType("FieldTransformer", Dict[str, Any])

Schema = NewType("Schema", Dict[str, str])


class Credentials(NamedTuple):
    project: str
    api_key: str
    region: str
    firebase_uid: str

    @property
    def token(self):
        return f"{self.project}:{self.api_key}:{self.region}:{self.firebase_uid}"


GroupBy = NewType("GroupBy", List[Dict[str, Any]])
Metric = NewType("Metric", List[Dict[str, Any]])

EncoderModel = Literal[
    "image_text",
    "text_image",
    "all-mpnet-base-v2",
    "clip-vit-b-32-image",
    "clip-vit-b-32-text",
    "clip-vit-l-14-image",
    "clip-vit-l-14-text",
    "sentence-transformers",
    "text-embedding-ada-002",
    "cohere-small",
    "cohere-large",
    "cohere-multilingual-22-12",
]

Encoder = Dict[str, Union[EncoderModel, str]]
