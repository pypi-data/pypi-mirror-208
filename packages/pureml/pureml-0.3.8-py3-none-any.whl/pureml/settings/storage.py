from pureml.schema import StorageSchema


def set_storage(storage_key: str) -> None:
    """Set the storage key.

    Args:
        storage (str): The storage key to reference storage details added in secret.
    """
    storage: StorageSchema = StorageSchema().get_instance()
    storage.STORAGE = storage_key
    # print(storage)
    # print(StorageSchema().get_instance())
