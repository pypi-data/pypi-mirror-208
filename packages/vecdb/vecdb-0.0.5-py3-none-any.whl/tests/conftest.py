import os
import random
import pytest
import string

from vecdb.api.local import Client
from vecdb.api.helpers import process_token
from vecdb.collections.dataset import Dataset
from vecdb.utils.document import Document, DocumentList
from vecdb.utils.example_documents import mock_documents, static_documents, tag_documents

TEST_TOKEN = os.getenv("DEVELOPMENT_TOKEN")
test_creds = process_token(TEST_TOKEN)


@pytest.fixture(scope="session")
def test_token() -> str:
    return TEST_TOKEN


@pytest.fixture(scope="session")
def test_client(test_token: str) -> Client:
    return Client(test_token)


@pytest.fixture(scope="function")
def test_dataset_id() -> str:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    return dataset_id


@pytest.fixture(scope="class")
def empty_dataset(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="class")
def full_dataset(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    dataset.insert(mock_documents(20))
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="class")
def mixed_dataset(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    documents = mock_documents(10)
    stripped = mock_documents(10)
    for document in stripped:
        document.pop("_chunk_")
    documents += stripped
    dataset.insert(documents)
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="class")
def static_dataset(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    dataset.insert(static_documents(20))
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="class")
def dense_input_dataset(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    dataset.insert(static_documents(2))
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="class")
def dense_output_dataset1(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="class")
def dense_output_dataset2(test_client: Client) -> Dataset:
    salt = "".join(random.choices(string.ascii_lowercase, k=10))
    dataset_id = f"_sample_dataset_{salt}"
    dataset = test_client.create_dataset(dataset_id, expire=True)
    yield dataset
    test_client.delete_dataset(dataset_id)


@pytest.fixture(scope="function")
def test_document() -> Document:
    raw_dict = {"field1": {"field2": 1}, "field3": 3}
    return Document(raw_dict)


@pytest.fixture(scope="function")
def test_documents() -> DocumentList:
    return mock_documents()


@pytest.fixture(scope="function")
def test_tag_documents() -> DocumentList:
    return tag_documents()
