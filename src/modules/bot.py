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
import json
from typing import Final
# ---

# ---
import aiohttp
import asyncio
from bs4 import BeautifulSoup
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
__region_data_file_path__: Final[str] = "./data/region_data.csv"
__available_web__indexers__: Final[dict] = {
    "university": {
        "college_board": "https://bigfuture.collegeboard.org/college-search/filters?s={target_state_abrv}&txa={majoring_target}",
    },
    "scholarships": {
        "gov": "https://www.careeronestop.org/toolkit/training/find-scholarships.aspx?curPage={page_number}&pagesize=500&studyLevelfilter=High%20School&georestrictionfilter={mixed_state}",
        "org": "https://scholarshipamerica.org/students/browse-scholarships/?fwp_state_territory={mixed_state}&fwp_paged={page_number}",
    },
    "costs": {
        "numbeo": "https://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&city1={current_city}%2C+{current_state_abrv}&country2=United+States&city2={target_city}%2C+{target_state_abrv}"
    },
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
        """

        # Clean up the query and create a list of possible queries
        possible_queries: Final[list[str]] = query.strip().lower().replace(" ", ",").split(",")

        # Set the query
        query: Final[str] = possible_queries[0] if len(possible_queries) == 1 else possible_queries[-1]

        # Open the CSV file
        with open(__region_data_file_path__, mode="r", encoding="utf-8") as file:
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
                if state_name.startswith(query) or city_name.startswith(query) or state_name.find(query) != -1 or city_name.find(query) != -1:
                    # Return the region row as a converted list
                    return list(region_row)

            # No match found
            file.close()

        # Return null
        return None

    def convert_query_to_college_board_major(query: str) -> str:
        """
        Converts the given ``query`` into a College Board recognizable entry.

        Parameters
        ----------
        query : str
            The query string to convert
        """

        # Return
        return query.strip().lower().replace(" ", "-")

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
    def __init__(self, target_state: list[str], current_state: list[str], majoring_target: str, use_queer_scoring: bool) -> None:
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
        self._search_query["target_state"] = (
            SearchUtils.autocomplete_region_from_query(target_state)
            if target_state is not None
            else None
        )
        self._search_query["current_state"] = (
            SearchUtils.autocomplete_region_from_query(current_state)
            if current_state is not None
            else None
        )
        self._search_query["majoring_target"] = (
            SearchUtils.convert_query_to_college_board_major(majoring_target)
            if majoring_target is not None
            else None
        )
        self._search_query["use_queer_scoring"] = (
            use_queer_scoring
            if use_queer_scoring is not None
            else False
        )

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
async def search(query: SearchQuery) -> dict:
    # Consolidate the query
    consolidated_data: Final[list[any]] = query.consolidate_query_options()

    # Declare the return dictionary
    return_data: dict = {
        "scholarships": {},
        "universities": {},
        "living_costs": {},
    }

    # Execute in "parallel" (this is actually roughly ~600ms faster)
    data: Final[list[dict]] = await asyncio.gather(
        _search_for_scholarships(
            target_state=(
                consolidated_data[0][2]
                if consolidated_data[0] is not None
                else None
            ),
            current_state=(
                consolidated_data[1][2]
                if consolidated_data[1] is not None
                else None
            ),
        ),
        _search_for_living_costs(
            target_city=(
                consolidated_data[0][4]
                if consolidated_data[0] is not None
                else None
            ),
            target_state_abrv=(
                consolidated_data[0][3]
                if consolidated_data[0] is not None
                else None
            ),
            current_city=(
                consolidated_data[1][4]
                if consolidated_data[1] is not None
                else None
            ),
            current_state_abrv=(
                consolidated_data[1][3]
                if consolidated_data[1] is not None
                else None
            )
        )
    )

    # Store data
    return_data["scholarships"] = data[0]
    return_data["living_costs"] = data[1]

    # Log
    print(return_data)

# Private Methods
async def _util_clean_extracted_json(json_string: str) -> dict:
    """
    Cleans the given ``json_string``.

    Parameters
    ----------
    json_string : str
        A JSON string
    """

    # Try to load the given json_string
    try:
        # Load the given json_string
        json.loads(json_string)
    # Capture the exception and save it as error
    except json.JSONDecodeError as error:
        # Create a set of invalid characters found in the error
        invalid_characters: Final[set] = set(error.doc[error.pos])

        # Iterate through the invalid characters set
        for character in invalid_characters:
            # Replace the characters in the JSON string
            json_string = json_string.replace(character, "")

    # Return
    return json.loads(json_string)

async def _util_make_web_request(url: str) -> any:
    """
    Makes an asynchronous web request to the given ``url``.

    Parameters
    ----------
    url : str
        The URL to request data from
    """

    # Create a new client session
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        # Set headers
        session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70"

        # Make the HTTP(S) request
        async with session.get(url=url) as response:
            # Return the response
            return await response.content.read()

async def _search_for_scholarships(target_state: str, current_state: str) -> dict:
    # Local method for handling the parsing of scholarship data
    async def _local_util_extract_scholarship_information(data: any, is_gov: bool) -> dict:
        # Declare the return dictionary
        return_data: list[dict] = []

        # Configure the parser
        parser: Final[BeautifulSoup] = BeautifulSoup(markup=data, features="html.parser")

        # Switch on selection
        match is_gov:
            case True:
                # Retrieve the scholarship rows
                scholarship_rows = parser.find("table", attrs={"class": "cos-table-responsive"}).find("tbody").find_all("tr")

                # Iterate though each row
                for scholarship_row in scholarship_rows:
                    # Retrieve the permanent URL
                    permanent_url: Final[str] = f"https://www.careeronestop.org{scholarship_row.find("div", attrs={"class": "notranslate detailPageLink"}).find("a")["href"]}".strip().replace(" ", "%20")

                    # Retrieve the organization funding the scholarship
                    organization_name: Final[str] = (
                        scholarship_row.find("div", attrs={"class": "notranslate"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )
                    # Retrieve the purpose of the scholarship
                    organization_purpose: Final[str] = (
                        scholarship_row.find("td", attrs={"headers": "thAN"})
                        .findChild("div", recursive=False)
                        .findChildren("div", recursive=False)[2]
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the award type
                    award_type: Final[str] = (
                        scholarship_row.find("td", attrs={"headers": "thAT"})
                        .findChild("div", recursive=False)
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the award amount
                    award_amount: Final[str] = (
                        scholarship_row.find("div", attrs={"class": "notranslate table-Numeric"})
                        .get_text()
                        .strip()
                        .replace(" ", "-")
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the submission date
                    submission_date: Final[str] = (
                        scholarship_row.find("td", attrs={"headers": "thD"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Create JSON object
                    obj: dict = {
                        "url": permanent_url,
                        "organization_name": organization_name,
                        "organization_purpose": organization_purpose,
                        "award_type": award_type,
                        "award_amount": award_amount,
                        "submission_date": submission_date,
                    }

                    # Clean up the JSON
                    obj = await _util_clean_extracted_json(json_string=json.dumps(obj))

                    # Append to return data
                    return_data.append(obj)

            case False:
                # Retrieve the scholarship rows
                scholarship_rows = parser.find("div", attrs={"class": "facetwp-template"}).find_all("article", attrs={"class": "scholarship"})

                # Iterate through each row
                for scholarship_row in scholarship_rows:
                    # Retrieve the permanent url
                    permanent_url: Final[str] = (
                        scholarship_row.find("a", attrs={"class": "text-btn"})["href"]
                        .strip()
                        .replace(" ", "%20")
                    )

                    # Retrieve the organization funding the scholarship
                    organization_name: Final[str] = (
                        scholarship_row.find("h3")
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the organization purpose
                    organization_purpose: Final[str] = (
                        scholarship_row.find("div", attrs={"class": "info"})
                        .find("p")
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                        or scholarship_row.find("div", attrs={"class": "info"})
                        .find("span", attr={"data-contrast": "auto"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Hardcoded award type
                    award_type: Final[str] = "Scholarship"

                    # Hardcoded award amount
                    award_amount: Final[str] = "Unknown"

                    # Retrieve the submission date
                    submission_date: Final[str] = "Unknown"

                    # Create JSON object
                    obj: dict = {
                        "url": permanent_url,
                        "organization_name": organization_name,
                        "organization_purpose": organization_purpose,
                        "award_type": award_type,
                        "award_amount": award_amount,
                        "submission_date": submission_date,
                    }

                    # Clean up the JSON
                    obj = await _util_clean_extracted_json(json_string=json.dumps(obj))

                    # Append to return data
                    return_data.append(obj)

        # Return found scholarships
        return return_data

    # Local method for handling the searching of scholarships on the federal level
    async def _local_search_for_federal_scholarships(return_data: dict) -> dict:
        if target_state is not None:
            # Format the URL
            formatted_url_gov: Final[str] = (
                __available_web__indexers__.get("scholarships", None)
                .get("gov", None)
                .format(page_number=0, mixed_state=target_state)
            )

            # Execute a web request
            response: Final[any] = await _util_make_web_request(url=formatted_url_gov)

            # Check is a valid response was returned
            if response is None:
                # Store as null
                return_data["target_state"]["gov"] = None

                # Return
                return

            # Parse the data and store the results
            return_data["target_state"]["gov"] = await _local_util_extract_scholarship_information(data=response, is_gov=True)

        if current_state is not None:
            # Format the URL
            formatted_url_gov: Final[str] = (
                __available_web__indexers__.get("scholarships", None)
                .get("gov", None)
                .format(page_number=0, mixed_state=current_state)
            )

            # Execute a web request
            response: Final[any] = await _util_make_web_request(url=formatted_url_gov)

            # Check is a valid response was returned
            if response is None:
                # Store as null
                return_data["current_state"]["gov"] = None

                # Return
                return

            # Parse the data and store the results
            return_data["current_state"]["gov"] = await _local_util_extract_scholarship_information(data=response, is_gov=True)

    # Local method for handling the searching of scholarships on the organizational level
    async def _local_search_for_organizational_scholarships(return_data: dict) -> dict:
        if target_state is not None:
            for page_number in range(0, 10):
                # Format the URL
                formatted_url_org: Final[str] = (
                    __available_web__indexers__.get("scholarships", None)
                    .get("org", None)
                    .format(page_number=page_number, mixed_state=target_state.lower().replace(" ", "-"))
                )

                # Execute a web request
                response: Final[any] = await _util_make_web_request(url=formatted_url_org)

                # Check is a valid response was returned
                if response is None:
                    # Invalid server response
                    break

                # Parse the data
                parsed_data: Final[list[dict]] = await _local_util_extract_scholarship_information(data=response, is_gov=False)

                # Check if parsed data has any scholarships
                if len(parsed_data) == 0:
                    # Website is dry of scholarships
                    break

                # Append results
                return_data["target_state"]["org"].append(parsed_data)

        if current_state is not None:
            for page_number in range(0, 10):
                # Format the URL
                formatted_url_org: Final[str] = (
                    __available_web__indexers__.get("scholarships", None)
                    .get("org", None)
                    .format(page_number=page_number, mixed_state=current_state.lower().replace(" ", "-"))
                )

                # Execute a web request
                response: Final[any] = await _util_make_web_request(url=formatted_url_org)

                # Check is a valid response was returned
                if response is None:
                    # Invalid server response
                    break

                # Parse the data
                parsed_data: Final[list[dict]] = await _local_util_extract_scholarship_information(data=response, is_gov=False)

                # Check if parsed data has any scholarships
                if len(parsed_data) == 0:
                    # Website is dry of scholarships
                    break

                # Append results
                return_data["current_state"]["org"].append(parsed_data)

    # Declare the return dictionary
    return_data: dict = {
        "target_state": {
            "gov": [],
            "org": [],
        },
        "current_state": {
            "gov": [],
            "org": [],
        },
    }

    # Run in "parallel"
    await asyncio.gather(
        _local_search_for_federal_scholarships(return_data=return_data),
        _local_search_for_organizational_scholarships(return_data=return_data)
    )

    # Return
    return return_data

async def _search_for_living_costs(target_city: str, target_state_abrv: str, current_city: str, current_state_abrv: str) -> dict:
    # Local method for handling the extraction of living costs
    async def _local_util_extract_living_costs(data: any) -> list[dict]:
        # Declare return data
        return_data: list[dict] = []

        # Configure the parser
        parser: Final[BeautifulSoup] = BeautifulSoup(markup=data, features="html.parser")

        # Retrieve the costs row
        costs_rows = parser.find("table", attrs={"class": "data_wide_table new_bar_table cost_comparison_table"}).find_all("tr")

        # Iterate through each row
        for cost_row in costs_rows:
            # Check if the row has a <td> tag as a child (skips the headers)
            if cost_row.find("td") is None:
                # Next iteration
                continue

            # All the data is nested so this is necessary
            data_entries = cost_row.find_all("td")

            # Try to parse table data
            try:
                # Retrieve the entry name
                entry_name: Final[str] = (
                    cost_row.find("td")
                    .get_text()
                    .strip()
                    .replace("\n", " ")
                    .replace("\xa0", " ")
                )

                # Retrieve current state cost
                current_state_cost: Final[str] = (
                    data_entries[1]
                    .find("span")
                    .get_text()
                    .strip()
                    .replace("\n", " ")
                    .replace("\xa0", " ")
                )

                # Retrieve target state cost
                target_state_cost: Final[str] = (
                    data_entries[2]
                    .find("span")
                    .get_text()
                    .strip()
                    .replace("\n", " ")
                    .replace("\xa0", " ")
                )

                # Retrieve cost difference
                cost_difference: Final[str] = (
                    data_entries[3]
                    .find("span")
                    .get_text()
                    .strip()
                    .replace("\n", " ")
                    .replace("\xa0", " ")
                )

                # Create JSON object
                obj: dict = {
                    "entry_name": entry_name,
                    "current_state_cost": current_state_cost,
                    "target_state_cost": target_state_cost,
                    "cost_difference": cost_difference,
                }

                # Clean up the JSON
                obj = await _util_clean_extracted_json(json_string=json.dumps(obj))

                # Append to return data
                return_data.append(obj)
            # Reached the end of the table
            except Exception as e:
                # Exit the loop
                break

        # Return
        return return_data

    # Local method for searching and retrieving living costs
    async def _local_util_search_for_living_costs(return_data: dict) -> dict:
        # Format the URL
        formatted_url_costs: Final[str] = (
            __available_web__indexers__.get("costs", None)
            .get("numbeo", None)
            .format(target_city=target_city, target_state_abrv=target_state_abrv, current_city=current_city, current_state_abrv=current_state_abrv)
        )

        # Execute a web request
        response: Final[any] = await _util_make_web_request(url=formatted_url_costs)

        # Check is a valid response was returned
        if response is None:
            # Invalid server response
            return return_data

        # Parse the data
        parsed_data: Final[list[dict]] = await _local_util_extract_living_costs(data=response)

        # Append
        return_data["costs"] = parsed_data

    # Declare the return dictionary
    return_data: dict = {"costs": []}

    # Sanity check
    if None in [target_city, target_state_abrv, current_city, current_state_abrv]:
        return return_data

    # Execute
    await _local_util_search_for_living_costs(return_data=return_data)

    # Return
    return return_data

# Script Check
if __name__ == "__main__":
    asyncio.run(
        search(
            SearchQuery(
                target_state=("florida florida miami"),
                current_state=("new new york"),
                majoring_target="professional programmer",
                use_queer_scoring=True,
            )
        )
    )
