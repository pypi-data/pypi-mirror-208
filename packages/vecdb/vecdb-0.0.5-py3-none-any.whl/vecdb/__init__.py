import os
import getpass

__version__ = "0.0.5"


def Client(token: str):
    import vecdb.api.local

    return vecdb.api.local.Client(token)


def Dataset(token: str, dataset_id: str):
    import vecdb.api.local

    client = vecdb.api.local.Client(token)
    return client.create_dataset(dataset_id)


def init(api_key: str = None):
    if not api_key:
        api_key = getpass.getpass("VecDB API Key:")
    os.environ["VECDB_API_KEY"] = api_key
