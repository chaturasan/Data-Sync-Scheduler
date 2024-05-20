from abc import ABC, abstractmethod


class Connector(ABC):
    """
    Abstract base class for connectors.

    This class defines the interface for connectors that interact with external systems to perform data synchronization.

    Attributes:
        None

    Methods:
        list_objects: Retrieves a list of objects from the external system.
        get_object_size: Retrieves the size of a specific object from the external system.
        fetch_object_in_chunks: Retrieves a specific object from the external system in chunks.

    """

    @abstractmethod
    def list_objects(self, config, pagination_token=None):
        pass

    @abstractmethod
    def get_object_size(self, config, object_key):
        pass

    @abstractmethod
    def fetch_object_in_chunks(self, config, object_key, start_position, object_size):
        pass
