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
from typing import Final

# ---

# ---

# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || bot/bot.py
#
# Responsible for scraping the internet for relevant data. Also handles
# the caching of frequently requested data.
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Constants
__version__: Final[str] = "0.1.0-DEV"

# Public Variables

# Private Variables
US_SCHOLARSHIPS: dict = {
    # Capital state name || All = US
    "gov": "https://www.careeronestop.org/toolkit/training/find-scholarships.aspx?curPage={page_number}&pagesize=500&studyLevelfilter=High%20School&georestrictionfilter={state}",
    # Lowercase state name || All = remove fwp_state_territory
    "org": "https://scholarshipamerica.org/students/browse-scholarships/?fwp_state_territory={state}&fwp_paged={page_number}",
}

# main
def main() -> None:
    # Print project info
    print(f"Oh, the Futures You'll Shape || Web Crawler v{ __version__}\nCopyright (c) 2024 Astrl\n\n")

# Class Definitions
class SearchQuery:
    """An object that holds user search data."""

    # Enums

    # Interfaces

    # Constants

    # Public Variables

    # Private Variables
    _search_query: dict = {
        "target_state": tuple[str, str],
        "current_state": tuple[str, str],
        "study_target": str,
        "queer_score": bool,
    }

    # Constructor
    def __init__(
        self,
        target_state: tuple[str, str] = ("Miami, Florida"),
        current_state: tuple[str, str] = ("Miami, Florida"),
        study_target: str = "Computer Science",
        queer_score: bool = True,
    ) -> None:
        """
        Instances a ``SearchQuery`` object that holds relevant user inputted data.

        Parameters
        ----------
        target_state : tuple[str, str]
            The state/region the user wants to study in
        current_state : tuple[str, str]
            The state/region the user currently resides in
        study_target : str
            The major the user plans to achieve
        queer_score : bool
            The queer score of the targeted region compared to the current region
        """

        # Store the submitted data
        self._search_query["target_state"] = target_state
        self._search_query["current_state"] = current_state
        self._search_query["study_target"] = study_target
        self._search_query["queer_score"] = queer_score

    # Public Static Methods

    # Public Inherited Methods
    def get_query_options(self) -> dict:
        """Returns the options ``dict`` that holds the relevant search data."""
        return self._search_query

    # Private Static Methods

    # Private Inherited Methods

# Public Methods
def search(query: SearchQuery) -> None:
    print(query.get_query_options())

# Private Methods

# Script Check
if __name__ == "__main__":
    main()
