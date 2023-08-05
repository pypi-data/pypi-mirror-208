from abc import abstractmethod

from singer import CatalogEntry

from .helpers import _get_stream_meta


class TapStream:
    def __init__(self, catalog_entry: CatalogEntry, config: dict, state: dict):
        self.config = config
        self.state = state
        self.catalog_entry = catalog_entry

        self.stream_meta = _get_stream_meta(self.catalog_entry)

    @property
    def stream_name(self) -> str:
        return self.catalog_entry.stream

    @property
    def stream_id(self) -> str:
        return self.catalog_entry.tap_stream_id

    @abstractmethod
    def sync(self):
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.stream_name}, id={self.stream_id})"
