from pureml.schema import BackendSchema


def set_backend(backend_url: str) -> None:
    """Set the backend url.

    Args:
        backend_url (str): The url of the backend.
    """
    backend: BackendSchema = BackendSchema().get_instance()
    backend.BASE_URL = backend_url
