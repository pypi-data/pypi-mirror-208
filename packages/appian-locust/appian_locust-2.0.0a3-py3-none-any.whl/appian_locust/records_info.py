from typing import Any, Dict

from ._records import _Records


class RecordsInfo():
    """
    Class which provides metadata about available record types from the Tempo Records tab
    """

    def __init__(self, records: _Records):
        self.__records = records

    def get_all_available_record_types(self) -> Dict[str, Any]:
        """
        Get all metadata for visible record types on Tempo Records.

        Returns (dict): List of record types and associated metadata
        """
        return self.__records.get_all_record_types()
