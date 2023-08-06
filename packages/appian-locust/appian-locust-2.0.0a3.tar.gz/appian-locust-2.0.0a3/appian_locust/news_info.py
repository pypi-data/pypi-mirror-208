from typing import Any, Dict, Optional, Tuple

from ._interactor import _Interactor
from ._news import _News


class NewsInfo:
    """
    Class which provides metadata about news entries from the Tempo News tab
    """

    def __init__(self, interactor: _Interactor):
        self.__news = _News(interactor)

    def get_all_available_entries(self, search_string: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves all the available "news" and associated metadata from "Appian-Tempo-News"

        Args:
            search_string(str, optional): results will be filtered based on the search string.

        Returns (dict): List of news and associated metadata

        Examples:

            >>> news_info.get_all()
        """
        return self.__news.get_all(search_string=search_string)

    def get_news(self, news_name: str, exact_match: bool = True, search_string: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the information about specific news by name.

        Args:
            news_name (str): name of the news entry
            exact_match (bool, optional): Should news name match exactly or to be partial match. Default : True
            search_string (str, optional): results will be filtered based on the search string.

        Returns: Specific News's info

        Raises: In case news is not found in the system, it throws an "Exception"

        Example:
            If full name of action is known,

            >>> news_info.get_news("news_name")

            If only partial name is known,

            >>> news_info.get_news("news_name", exact_match=False)

        """
        return self.__news.get_news(news_name, exact_match, search_string)

    def visit_news_entry(self, news_name: str, exact_match: bool = True, search_string: Optional[str] = None) -> Tuple:
        """
        This function simulates navigating to a single entry in the ui. There are two parts to navigating to a
        news entry: navigating to the view and getting the news entry's feed.

        Args:
            news_name (str): Name of the news entry to be called
            exact_match (bool, optional): Should news name match exactly or to be partial match. Default : True
            search_string (str, optional): results will be filtered based on the search string.

        Returns (Tuple): Response codes for the view navigation and getting the feed entry

        Examples:

            If full name of news is known,

            >>> news_info.visit_news_entry("news_name")

            If only partial name is known,

            >>> news_info.visit_news_entry("news_n", exact_match=False)
        """
        return self.__news.visit_news_entry(news_name, exact_match, search_string)
