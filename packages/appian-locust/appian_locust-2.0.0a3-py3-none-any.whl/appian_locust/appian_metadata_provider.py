from typing import Any, Dict

from ._interactor import _Interactor
from ._reports import _Reports


class AppianMetadataProvider:

    def __init__(self, interactor: _Interactor):
        self.__interactor = interactor
        self.__reports = _Reports(self.__interactor)

    def get_all_reports(self) -> Dict[str, Any]:
        return self.__reports.get_all()
