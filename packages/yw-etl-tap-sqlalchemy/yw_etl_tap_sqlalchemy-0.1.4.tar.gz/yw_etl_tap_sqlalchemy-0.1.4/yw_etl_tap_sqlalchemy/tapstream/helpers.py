import singer
from singer import CatalogEntry


def _get_stream_meta(catalog_entry: CatalogEntry):
    compiled = singer.metadata.to_map(catalog_entry.metadata)
    return compiled.get((), None)
