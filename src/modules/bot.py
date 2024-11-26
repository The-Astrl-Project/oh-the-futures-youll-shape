#
# Copyright (c) 2024 Astrl.
#
# This file is part of oh-the-futures-youll-shape. It is subject to the license terms in
# the LICENSE file found in the top-level directory of this project and at
# https://github.com/The-Astrl-Project/oh-the-futures-youll-shape/blob/HEAD/LICENSE.
#
# This file may not be copied, modified, propagated, or distributed
# except according to the terms contained in the LICENSE file.
#

# Import Statements
# ----------------------------------------------------------------
import csv
from typing import Final

# ---

# ---

# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || modules/bot.py
#
# Responsible for scraping the internet for relevant data. Also handles
# the caching of frequently requested data.
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Constants
__version__: Final[str] = "0.2.0-DEV"
__region_data_filepath__: Final[str] = "./data/region_data.csv"
UNIVERSITY_INDEXERS: Final[dict] = {
    # Major has to be modified "Computer Science" => computer-science. || data-testid="cs-show-more-results" since pages cant be hyperlinked
    "collegeboard": "https://bigfuture.collegeboard.org/college-search/filters?s={target_state_abrv}&txa={majoring_target}"
}
SCHOLARSHIP_INDEXERS: Final[dict] = {
    # Capital state name || All = US
    "gov": "https://www.careeronestop.org/toolkit/training/find-scholarships.aspx?curPage={page_number}&pagesize=500&studyLevelfilter=High%20School&georestrictionfilter={mixed_state}",
    # Lowercase state name || All = remove fwp_state_territory
    "org": "https://scholarshipamerica.org/students/browse-scholarships/?fwp_state_territory={mixed_state}&fwp_paged={page_number}",
}
LIVING_COSTS_INDEXERS: Final[dict] = {
    "numbeo": "https://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&city1={current_city}%2C+{current_state_abrv}&country2=United+States&city2={target_city}%2C+{target_state_abrv}"
}

# Public Variables

# Private Variables


# Class Definitions
class SearchUtils:
    """Provides external utility functions for cleaning/parsing data."""

    # Enums

    # Interfaces

    # Constants

    # Public Variables

    # Private Variables

    # Constructor

    # Public Static Methods
    def autocomplete_region_from_query(query: str) -> list[str]:
        """
        Returns the closest region match from the given ``query``.

        Parameters
        ----------
        query : str
            The query to match

        Notes
        -----
        While it would *probably* be nice to have this be async rather than
        sync I don't really get paid (0.00) much to care.
        """

        # Clean up the query
        test_case: Final[str] = query.strip().lower().replace(" ", ",").split(",")[0]

        # Open the CSV file
        with open(__region_data_filepath__, mode="r") as file:
            # Instance a new CSV reader
            file_reader: Final[csv._reader] = csv.reader(file, delimiter=",")

            # Skip the CSV header
            next(file_reader)

            # Iterate through the rows
            for region_row in file_reader:
                # Retrieve the state and city names
                state_name: Final[str] = region_row[2].strip().lower()
                city_name: Final[str] = region_row[4].strip().lower()

                # Attempt to match the query
                if state_name.startswith(test_case) or city_name.startswith(test_case):
                    # Return the region row as a converted list
                    return list(region_row)

            # No match found
            file.close()

        # Return null
        return None

    # Public Inherited Methods

    # Private Static Methods

    # Private Inherited Methods


class SearchQuery:
    """An object that holds the user's search queries."""

    # Enums

    # Interfaces

    # Constants

    # Public Variables

    # Private Variables
    _search_query: dict = {
        "target_state": tuple[str, str],
        "current_state": tuple[str, str],
        "majoring_target": str,
        "use_queer_scoring": bool,
    }

    # Constructor
    def __init__(
        self,
        target_state: list[str],
        current_state: list[str],
        majoring_target: str,
        use_queer_scoring: bool,
    ) -> None:
        """
        Instances a ``SearchQuery`` object that holds relevant user inputted data.

        Parameters
        ----------
        target_state : tuple[str, str]
            The state/region the user wants to study in
        current_state : tuple[str, str]
            The state/region the user currently resides in
        majoring_target : str
            The major the user plans to achieve
        use_queer_scoring : bool
            Compare the overall M.A.P score of the targeted region to the current, residing, region
        """

        # Store the submitted data
        self._search_query["target_state"] = SearchUtils.autocomplete_region_from_query(
            target_state
        )
        self._search_query["current_state"] = (
            SearchUtils.autocomplete_region_from_query(current_state)
        )
        self._search_query["majoring_target"] = (
            majoring_target.strip().lower().replace(" ", "-")
            if majoring_target is not None
            else None
        )
        self._search_query["use_queer_scoring"] = use_queer_scoring

    # Public Static Methods

    # Public Inherited Methods
    def get_query_option(self, option: str) -> any:
        """Returns the query option from the given ``option`` key."""
        # Return from option key
        return self._search_query.get(option, None)

    def consolidate_query_options(self) -> list[any]:
        """Consolidates the search queries into one workable Python list."""
        # Return consolidated list
        return [
            self._search_query.get("target_state", None),
            self._search_query.get("current_state", None),
            self._search_query.get("majoring_target", None),
            self._search_query.get("use_queer_scoring", None),
        ]

    # Private Static Methods

    # Private Inherited Methods


# Public Methods
def search(query: SearchQuery) -> dict:
    # Consolidate the query
    consolidated_data: Final[list[any]] = query.consolidate_query_options()

    # Validate
    print(consolidated_data)


# Private Methods

# Script Check
if __name__ == "__main__":
    print(
        "Poggers Chat:",
        search(
            SearchQuery(
                target_state=("miami"),
                current_state=("washington"),
                majoring_target="computer science",
                use_queer_scoring=True,
            )
        ),
    )
