import sqlite3
from typing import List, Optional


class WikiMapper:
    """Uses a precomputed database created by `create_wikipedia_wikidata_mapping_db`."""

    def __init__(self, path_to_db: str):
        self._path_to_db = path_to_db
        self.conn = sqlite3.connect(self._path_to_db)

    def title_to_id(self, page_title: str) -> Optional[str]:
        """Given a Wikipedia page title, returns the corresponding Wikidata ID.

        The page title is the last part of a Wikipedia url **unescaped** and spaces
        replaced by underscores , e.g. for `https://en.wikipedia.org/wiki/Fermat%27s_Last_Theorem`,
        the title would be `Fermat's_Last_Theorem`.

        Args:
            page_title: The page title of the Wikipedia entry, e.g. `Manatee`.

        Returns:
            Optional[str]: If a mapping could be found for `wiki_page_title`, then return
                           it, else return `None`.

        """

        c = self.conn.execute("SELECT wikidata_id FROM mapping WHERE wikipedia_title=?", (page_title,))
        result = c.fetchone()

        if result is not None and result[0] is not None:
            return result[0]
        else:
            return None

    def url_to_id(self, wiki_url: str) -> Optional[str]:
        """Given an URL to a Wikipedia page, returns the corresponding Wikidata ID.

        This is just a convenience function. It is not checked whether the index and
        URL are from the same dump.

        Args:
            wiki_url: The URL to a Wikipedia entry.

        Returns:
            Optional[str]: If a mapping could be found for `wiki_url`, then return
                           it, else return `None`.

        """

        title = wiki_url.rsplit("/", 1)[-1]
        return self.title_to_id(title)

    def id_to_titles(self, wikidata_id: str) -> List[str]:
        """Given a Wikidata ID, return a list of corresponding pages that are linked to it.

        Due to redirects, the mapping from Wikidata ID to Wikipedia title is not unique.

        Args:
            wikidata_id (str): The Wikidata ID to map, e.g. `Q42797`.

        Returns:
            List[str]: A list of Wikipedia pages that are linked to this Wikidata ID.

        """

        c = self.conn.execute(
            "SELECT DISTINCT wikipedia_title FROM mapping WHERE wikidata_id =?", (wikidata_id,)
        )
        results = c.fetchall()

        return [e[0] for e in results]

    def wikipedia_id_to_id(self, wikipedia_id: int) -> Optional[str]:
        """Given a Wikipedia ID (in other words Page ID), returns the corresponding Wikidata ID.

        Wikipedia ID is another way to access Wikipedia Article and is widely used in Wikipedia dumps.
        For example, for the ID `18630637` we can use the link - `http://en.wikipedia.org/?curid=18630637`.

        Args:
            wikipedia_id (int): The Wikipedia ID to map, e.g. `18630637`

        Returns:
            Optional[str]: If a mapping found for `wikipedia_id`, then return
                           it, else return `None`.
        """

        c = self.conn.execute(
            "SELECT wikidata_id FROM mapping WHERE wikipedia_id=?", (wikipedia_id,)
        )
        result = c.fetchone()

        if result is not None and result[0] is not None:
            return result[0]
        else:
            return None

    def id_to_wikipedia_ids(self, wikidata_id: str) -> List[int]:
        """Given a Wikidata ID, returns the corresponding list of Wikipedia IDs (or Page IDs).

        Due to redirects, there can be multiple Wikipedia IDs for the same Wikidata item.

        Args:
            wikidata_id (str): The Wikidata ID to map, e.g. `Q7553`

        Returns:
            List[int]: A list of Wikipedia IDs linked to the given Wikidata ID.
        """

        # no need for `DISTINCT` as `wikipedia_id` is a PRIMARY KEY, thus we have no duplicates there
        c = self.conn.execute(
            "SELECT wikipedia_id FROM mapping WHERE wikidata_id=?", (wikidata_id,)
        )
        results = c.fetchall()

        return [e[0] for e in results]

    def wikipedia_id_to_title(self, wikipedia_id: int) -> Optional[str]:
        """Given a Wikipedia ID (in other words Page ID), returns the corresponding page title.

        Args:
            wikipedia_id (int): The Wikipedia ID to map, e.g. `11867`

        Returns:
            Optional[str]: If a mapping found for `wikipedia_id`, then return
                           it, else return `None`.
        """

        c = self.conn.execute(
            "SELECT wikipedia_title FROM mapping WHERE wikipedia_id=?", (wikipedia_id,)
        )
        result = c.fetchone()

        if result is not None and result[0] is not None:
            return result[0]
        else:
            return None

    def title_to_wikipedia_id(self, page_title: str) -> Optional[int]:
        """Given a Wikipedia page title, returns the corresponding Wikipedia id.

        Args:
            page_title (str): The Wikipedia page title to map, e.g. `Germany`

        Returns:
            Optional[str]: If a mapping found for `page_title`, then return
                           it, else return `None`.
        """

        # no need for `DISTINCT` as `wikipedia_id` is a PRIMARY KEY, thus we have no duplicates there
        c = self.conn.execute(
            "SELECT wikipedia_id FROM mapping WHERE wikipedia_title=?", (page_title,)
        )
        result = c.fetchone()

        if result is not None and result[0] is not None:
            return result[0]
        else:
            return None
