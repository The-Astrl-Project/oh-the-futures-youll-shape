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
import pyppeteer
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
__version__: Final[str] = "0.3.1-DEV"
__region_data_file_path__: Final[str] = "./data/region_data.csv"
__available_web__indexers__: Final[dict] = {
    "universities": {
        "usnews": "https://www.usnews.com/best-colleges/{mixed_state_abrv}?_sort=rank&_sortDirection=asc",
        "collegeboard": "https://bigfuture.collegeboard.org/college-search/filters?s={mixed_state_abrv}&txa={majoring_target}",
    },
    "scholarships": {
        "careeronestop": "https://www.careeronestop.org/toolkit/training/find-scholarships.aspx?curPage={page_number}&pagesize=500&studyLevelfilter=High%20School&georestrictionfilter={mixed_state}",
        "scholarshipamerica": "https://scholarshipamerica.org/students/browse-scholarships/?fwp_state_territory={mixed_state}&fwp_paged={page_number}",
    },
    "living_costs": {
        "numbeo": "https://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&city1={current_city}%2C+{current_state_abrv}&country2=United+States&city2={target_city}%2C+{target_state_abrv}"
    },
    "queer_scoring": {
        "lgbtmap": "https://www.lgbtmap.org/equality_maps/profile_state/{mixed_state_abrv}",
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

        # Check if a blank string was just passed
        if len(query.strip()) == 0:
            # Return None
            return None

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

        # Return None
        return None

    def autocomplete_major_from_query(query: str) -> str:
        """
        Returns a College Board recognizable major entry from the given ``query``.

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
        "target_state": list[str],
        "current_state": list[str],
        "majoring_target": str,
        "use_queer_scoring": bool,
    }

    # Constructor
    def __init__(self, target_state: str, current_state: str, majoring_target: str, use_queer_scoring: bool) -> None:
        """
        Instances a ``SearchQuery`` object that holds relevant user inputted data.

        Parameters
        ----------
        target_state : str
            The state/region the user wants to study in
        current_state : str
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
            SearchUtils.autocomplete_major_from_query(majoring_target)
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
        "queer_scoring": {},
    }

    # Execute in "parallel" (this is actually roughly ~600ms faster)
    data: Final[tuple[dict, dict, dict]] = await asyncio.gather(
        _search_for_scholarships(
            target_state=(
                consolidated_data[0][2] if consolidated_data[0] is not None else None
            ),
            current_state=(
                consolidated_data[1][2] if consolidated_data[1] is not None else None
            ),
        ),
        _search_for_universities(
            target_state_abrv=(
                consolidated_data[0][3] if consolidated_data[0] is not None else None
            ),
            current_state_abrv=(
                consolidated_data[1][3] if consolidated_data[1] is not None else None
            ),
            majoring_target=(
                consolidated_data[2] if consolidated_data[2] is not None else None
            ),
        ),
        _search_for_living_costs(
            target_city=(
                consolidated_data[0][4] if consolidated_data[0] is not None else None
            ),
            target_state_abrv=(
                consolidated_data[0][3] if consolidated_data[0] is not None else None
            ),
            current_city=(
                consolidated_data[1][4] if consolidated_data[1] is not None else None
            ),
            current_state_abrv=(
                consolidated_data[1][3] if consolidated_data[1] is not None else None
            ),
        ),
        _search_for_queer_scoring(
            target_state_abrv=(
                consolidated_data[0][3] if consolidated_data[0] is not None else None
            ),
            current_state_abrv=(
                consolidated_data[1][3] if consolidated_data[1] is not None else None
            ),
            use_queer_scoring=(
                consolidated_data[3] if consolidated_data[3] is not None else False
            ),
        ),
    )

    # Store data
    return_data["scholarships"] = data[0]
    return_data["universities"] = data[1]
    return_data["living_costs"] = data[2]
    return_data["queer_scoring"] = data[3]

    # Return
    return return_data

# Private Methods
async def _clean_and_verify_json(json_string: str) -> dict:
    """
    Cleans and verifies the given ``json_string``.

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

async def _standard_fetch(url: str) -> any:
    """
    Makes an asynchronous web request to the given ``url`` via
    aiohttp. This is a quick request but can be blocked by
    anti-web-scraping measures. (ie: Client-Side hydration)

    Parameters
    ----------
    url : str
        The URL to request data from
    """

    # Create a new client session
    session: Final[aiohttp.ClientSession] = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False))

    # Set valid session headers
    session.headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70"

    # Make the HTTP(S) request
    response: Final[aiohttp.ClientResponse] = await session.get(url=url)

    # Store the HTML response
    html_response: Final[any] = await response.content.read()

    # Close the session
    await session.close()

    # Return the HTML response
    return html_response

async def _headless_fetch(url: str) -> any:
    """
    Makes an asynchronous web request to the given ``url`` via
    pyppeteer. This is a much slower request but bypasses basic
    anti-web-scraping measures.

    Parameters
    ----------
    url : str
        The URL to request data from
    """

    # Recursively try to fetch the URL
    try:
        # Create a new browser session
        browser = await pyppeteer.launch({"headless": True, "defaultViewport": None})

        # Open a new page
        web_page = await browser.newPage()

        # Configure the user agent
        await web_page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.2903.70")

        # Open the URL
        await web_page.goto(url=url, options={"waitUntil": "networkidle0"})

        # Extract the whole HTML DOM from the webpage
        html_dom = await web_page.evaluate("() => {return {dom: document.querySelector('*').outerHTML} }")

        # Close the browser session
        await browser.close()

        # Return the HTML DOM
        return html_dom["dom"].strip()

    except Exception as _:
        # This looks painful
        return await _headless_fetch(url=url)

async def _search_for_scholarships(target_state: str, current_state: str) -> dict:
    async def _extract(web_response: any, web_source: str) -> list[dict]:
        """
        Handles the extraction of university information from the given ``web_response``.
        Site specific parsing is handled via the ``web_source`` parameter.

        Parameters
        ----------
        web_response : any
            An HTML string or similar

        web_source : str
            A valid string identifier for where the web response came from
        """

        # Declare the return object
        return_data: list[dict] = []

        # Configure the parser
        parser: Final[BeautifulSoup] = BeautifulSoup(markup=web_response, features="lxml")

        # Switch on web source
        match web_source:
            # Source: https://www.careeronestop.org/toolkit/training/find-scholarships.aspx?curPage=0&pagesize=500&studyLevelfilter=High%20School&georestrictionfilter=Florida
            case "careeronestop":
                # Retrieve the available scholarships table
                scholarships_table = (
                    parser.find("table", attrs={"class": "cos-table-responsive"})
                    .find("tbody")
                    .find_all("tr")
                )

                # Iterate through each table row
                for scholarship_entry in scholarships_table:
                    # Retrieve the scholarship URL
                    scholarship_url: Final[str] = (
                        "https://www.careeronestop.org"
                        + scholarship_entry.find("div", attrs={"class": "notranslate detailPageLink"})
                        .find("a")["href"]
                        .strip()
                        .replace(" ", "%20")
                    )

                    # Retrieve the organization funding the scholarship
                    scholarship_organization_name: Final[str] = (
                        scholarship_entry.find("div", attrs={"class": "notranslate"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the purpose of the scholarship
                    scholarship_organization_purpose: Final[str] = (
                        scholarship_entry.find("td", attrs={"headers": "thAN"})
                        .findChild("div", recursive=False)
                        .findChildren("div", recursive=False)[2]
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                        .replace("\u2019", "'")
                    )

                    # Retrieve the scholarship award type
                    scholarship_award_type: Final[str] = (
                        scholarship_entry.find("td", attrs={"headers": "thAT"})
                        .findChild("div", recursive=False)
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the scholarship award amount
                    scholarship_award_amount: Final[str] = (
                        scholarship_entry.find("div", attrs={"class": "notranslate table-Numeric"})
                        .get_text()
                        .strip()
                        .replace(" ", "-")
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the scholarship submission date
                    scholarship_submission_date: Final[str] = (
                        scholarship_entry.find("td", attrs={"headers": "thD"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Clean up the JSON and append it to the return object
                    return_data.append(
                        await _clean_and_verify_json(
                            json_string=json.dumps(
                                {
                                    "scholarship_url": scholarship_url,
                                    "scholarship_organization_name": scholarship_organization_name,
                                    "scholarship_organization_purpose": scholarship_organization_purpose,
                                    "scholarship_award_type": scholarship_award_type,
                                    "scholarship_award_amount": scholarship_award_amount,
                                    "scholarship_submission_date": scholarship_submission_date,
                                }
                            )
                        )
                    )

            # Source: https://scholarshipamerica.org/students/browse-scholarships/?fwp_state_territory=florida&fwp_paged=0
            case "scholarshipamerica":
                # Retrieve the available scholarships table
                scholarships_table = (
                    parser.find("div", attrs={"class": "facetwp-template"})
                    .find_all("article", attrs={"class": "scholarship"})
                )

                # Iterate through each table row
                for scholarship_entry in scholarships_table:
                    # Retrieve the scholarship URL
                    scholarship_url: Final[str] = (
                        scholarship_entry.find("a", attrs={"class": "text-btn"})["href"]
                        .strip()
                        .replace(" ", "%20")
                    )

                    # Retrieve the organization funding the scholarship
                    scholarship_organization_name: Final[str] = (
                        scholarship_entry.find("h3")
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the purpose of the scholarship
                    scholarship_organization_purpose: Final[str] = (
                        scholarship_entry.find("div", attrs={"class": "info"})
                        .find("p")
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                        or
                        scholarship_entry.find("div", attrs={"class": "info"})
                        .find("span", attr={"data-contrast": "auto"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the scholarship award type
                    scholarship_award_type: Final[str] = "Scholarship"

                    # Retrieve the scholarship award amount
                    scholarship_award_amount: Final[str] = "Unknown"

                    # Retrieve the scholarship submission date
                    scholarship_submission_date: Final[str] = "Unknown"

                    # Clean up the JSON and append it to the return object
                    return_data.append(
                        await _clean_and_verify_json(
                            json_string=json.dumps(
                                {
                                    "scholarship_url": scholarship_url,
                                    "scholarship_organization_name": scholarship_organization_name,
                                    "scholarship_organization_purpose": scholarship_organization_purpose,
                                    "scholarship_award_type": scholarship_award_type,
                                    "scholarship_award_amount": scholarship_award_amount,
                                    "scholarship_submission_date": scholarship_submission_date,
                                }
                            )
                        )
                    )

            # Source: XYZ
            case _:
                pass

        # Return the extracted scholarship information
        return return_data

    async def _search(return_data: dict) -> None:
        """
        Handles the searching of scholarships based on the given parent
        function's params.

        Parameters
        ----------
        return_data : dict
            A reference to the return data object
        """

        async def _non_variable_search(return_data: dict) -> None:
            # Check the target state first
            if target_state is not None:
                # Format the URL
                formatted_url_careeronestop: Final[str] = (
                    __available_web__indexers__.get("scholarships", None)
                    .get("careeronestop", None)
                    .format(mixed_state=target_state, page_number=0)
                    .replace(" ", "%20")
                )

                # Execute a web request
                response: Final[any] = await _standard_fetch(url=formatted_url_careeronestop)

                # Check if a valid response was returned
                if response is None:
                    # No data found ||Set as None
                    return_data["target_state"]["careeronestop"] = None
                else:
                    # Parse the data and store the results
                    return_data["target_state"]["careeronestop"] = await _extract(web_response=response, web_source="careeronestop")

            # Check the current state next
            if current_state is not None:
                # Format the URL
                formatted_url_careeronestop: Final[str] = (
                    __available_web__indexers__.get("scholarships", None)
                    .get("careeronestop", None)
                    .format(mixed_state=current_state, page_number=0)
                    .replace(" ", "%20")
                )

                # Execute a web request
                response: Final[any] = await _standard_fetch(url=formatted_url_careeronestop)

                # Check if a valid response was returned
                if response is None:
                    # No data found ||Set as None
                    return_data["current_state"]["careeronestop"] = None
                else:
                    # Parse the data and store the results
                    return_data["current_state"]["careeronestop"] = await _extract(web_response=response, web_source="careeronestop")

        async def _variable_search(return_data: dict) -> None:
            # Check the target state first
            if target_state is not None:
                # Iterate through 10 pages
                for page_number in range(0, 10):
                    # Format the URL
                    formatted_url_scholarshipamerica: Final[str] = (
                        __available_web__indexers__.get("scholarships", None)
                        .get("scholarshipamerica", None)
                        .format(mixed_state=target_state.lower().replace(" ", "-"), page_number=page_number)
                        .replace(" ", "%20")
                    )

                    # Execute a web request
                    response: Final[any] = await _standard_fetch(url=formatted_url_scholarshipamerica)

                    # Check if a valid response was returned
                    if response is None:
                        # Reached the end of available scholarships || Exit the loop
                        break

                    # Parse the data
                    parsed_data: Final[list[dict]] = await _extract(web_response=response, web_source="scholarshipamerica")

                    # Check if the parsed data contains any scholarships
                    if len(parsed_data) == 0:
                        # Website is dry of scholarships || Exit the loop
                        break

                    # Store the results
                    return_data["target_state"]["scholarshipamerica"] = parsed_data

            # Check the current state next
            if current_state is not None:
                # Iterate through 10 pages
                for page_number in range(0, 10):
                    # Format the URL
                    formatted_url_scholarshipamerica: Final[str] = (
                        __available_web__indexers__.get("scholarships", None)
                        .get("scholarshipamerica", None)
                        .format(mixed_state=current_state.lower().replace(" ", "-"), page_number=page_number)
                        .replace(" ", "%20")
                    )

                    # Execute a web request
                    response: Final[any] = await _standard_fetch(url=formatted_url_scholarshipamerica)

                    # Check if a valid response was returned
                    if response is None:
                        # Reached the end of available scholarships || Exit the loop
                        break

                    # Parse the data
                    parsed_data: Final[list[dict]] = await _extract(web_response=response, web_source="scholarshipamerica")

                    # Check if the parsed data contains any scholarships
                    if len(parsed_data) == 0:
                        # Website is dry of scholarships || Exit the loop
                        break

                    # Store the results
                    return_data["current_state"]["scholarshipamerica"] = parsed_data

        # Search for scholarships in "parallel"
        await asyncio.gather(
            _variable_search(return_data=return_data),
            _non_variable_search(return_data=return_data),
        )

    # Declare the return dictionary
    return_data: dict = {
        "target_state": {
            "careeronestop": [],
            "scholarshipamerica": [],
        },
        "current_state": {
            "careeronestop": [],
            "scholarshipamerica": [],
        },
    }

    # Execute
    await _search(return_data=return_data)

    # Return
    return return_data

async def _search_for_universities(target_state_abrv: str, current_state_abrv: str, majoring_target: str) -> dict:
    async def _extract(web_response: any, web_source: str) -> list[dict]:
        """
        Handles the extraction of university information from the given ``web_response``.
        Site specific parsing is handled via the ``web_source`` parameter.

        Parameters
        ----------
        web_response : any
            An HTML string or similar

        web_source : str
            A valid string identifier for where the web response came from
        """

        # Declare the return object
        return_data: list[dict] = []

        # Configure the parser
        parser: Final[BeautifulSoup] = BeautifulSoup(markup=web_response, features="lxml")

        # Switch on web source
        match web_source:
            # Source: https://bigfuture.collegeboard.org/college-search/filters?s=FL
            case "collegeboard":
                # Declare the university table
                university_table = None

                # College Board doesn't have 404 pages for invalid
                # search queries so if this fails we can safely
                # assume the query is invalid/malformed
                try:
                    # Retrieve the available universities table
                    university_table = (
                        parser.find("div", attrs={"data-testid": "cs-search-results-list"})
                        .find_all("div", attrs={"class": "cs-college-card-outer-container"}, recursive=False)
                    )
                except Exception as _:
                    # Gracefully exit
                    return return_data

                # Iterate through each table row
                for university_entry in university_table:

                    async def _college_board_parsing() -> str:
                        """College Board specific parsing."""

                        # Declare the return string
                        return_string: str = ""

                        # Find all the li tags
                        entries = (
                            university_entry.find("ul", attrs={"class": "cs-college-card-details-profile-inline-list cb-text-list cs-college-card-details-profile-info-text"})
                            .find_all("li")
                        )

                        # Iterate through each
                        for entry in entries:
                            return_string = (
                                return_string
                                + entry.get_text()
                                .strip()
                                .replace("\n", " ")
                                .replace("\xa0", " ")
                                .replace("-", " ")
                                + " - "
                            )

                        # Return
                        return return_string.strip(" - ").strip()

                    # Retrieve the university URL
                    university_entry_url: Final[str] = (
                        university_entry.find("a", attrs={"rel": "noreferrer"})["href"]
                        .strip()
                        .replace(" ", "%20")
                    )

                    # Retrieve the university name
                    university_entry_name: Final[str] = (
                        university_entry.find("span", attrs={"class": "cs-college-card-college-name-link-text"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the university location
                    university_entry_location: Final[str] = (
                        university_entry.find("div", attrs={"data-testid": "cs-college-card-college-address"})
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                    # Retrieve the university overview information
                    university_entry_overview: Final[str] = await _college_board_parsing()

                    # Set as N/A as default
                    university_entry_graduation_rate: str = "N/A"
                    university_entry_average_tuition: str = "N/A"
                    university_entry_sat_range: str = "N/A"

                    # Some schools dont have publicly available gradation rates
                    try:
                        # Retrieve university graduation rate
                        university_entry_graduation_rate = (
                            university_entry.find("div", attrs={"data-testid": "cs-college-card-details-profile-school-graduation-rate"})
                            .find("strong", attrs={"class": "cb-roboto-medium"})
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )
                    except Exception as _:
                        # Keep parsing
                        pass

                    # Some schools dont have publicly available tuition costs
                    try:
                        # Retrieve university average tuition cost (after aid)
                        university_entry_average_tuition = (
                            university_entry.find("div", attrs={"data-testid": "cs-college-card-details-profile-school-average-cost"})
                            .find("strong", attrs={"class": "cb-roboto-medium"})
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )
                    except Exception as _:
                        # Keep parsing
                        pass

                    # Some schools dont have publicly available SAT score ranges
                    try:
                        # Retrieve SAT score ranges
                        university_entry_sat_range = (
                            university_entry.find("div", attrs={"data-testid": "cs-college-card-details-profile-school-sat-range"})
                            .find("strong", attrs={"class": "cb-roboto-medium"})
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                            .replace("\u2013", "-")
                        )
                    except Exception as _:
                        # Keep parsing
                        pass

                    # Clean up the JSON and append it to the return object
                    return_data.append(
                        await _clean_and_verify_json(
                            json_string=json.dumps(
                                {
                                    "university_entry_url": university_entry_url,
                                    "university_entry_name": university_entry_name,
                                    "university_entry_location": university_entry_location,
                                    "university_entry_overview": university_entry_overview,
                                    "university_entry_graduation_rate": university_entry_graduation_rate,
                                    "university_entry_average_tuition": university_entry_average_tuition,
                                    "university_entry_sat_range": university_entry_sat_range,
                                }
                            )
                        )
                    )

            # Source: https://www.usnews.com/best-colleges/fl?_sort=rank&_sortDirection=asc
            case "usnews":
                pass

            # Source: XYZ
            case _:
                pass

        # Return the extracted university information
        return return_data

    async def _search(return_data: dict) -> None:
        """
        Handles the searching of scholarships based on the given parent
        function's params.

        Parameters
        ----------
        return_data : dict
            A reference to the return data object
        """

        # Check the target state first
        if target_state_abrv is not None:
            # Format the URL
            formatted_url_collegeboard: Final[str] = (
                __available_web__indexers__.get("universities", None)
                .get("collegeboard", None)
                .format(mixed_state_abrv=target_state_abrv, majoring_target=majoring_target or "")
                .replace(" ", "%20")
            )

            # Execute a web request
            response: Final[any] = await _headless_fetch(url=formatted_url_collegeboard)

            # Check if a valid response was returned
            if response is None:
                # No data found set as None
                return_data["target_state"]["collegeboard"] = None
            else:
                # Parse the data
                parsed_data: Final[list[dict]] = await _extract(web_response=response, web_source="collegeboard")

                # Check if the parsed data contains any universities
                if len(parsed_data) == 0:
                    # Nothing found
                    return_data["target_state"]["collegeboard"] = None
                else:
                    # Store the results
                    return_data["target_state"]["collegeboard"] = parsed_data

        # Check the current state next
        if current_state_abrv is not None:
            # Format the URL
            formatted_url_collegeboard: Final[str] = (
                __available_web__indexers__.get("universities", None)
                .get("collegeboard", None)
                .format(mixed_state_abrv=current_state_abrv, majoring_target=majoring_target or "")
                .replace(" ", "%20")
            )

            # Execute a web request
            response: Final[any] = await _headless_fetch(url=formatted_url_collegeboard)

            # Check if a valid response was returned
            if response is None:
                # No data found set as None
                return_data["current_state"]["collegeboard"] = None
            else:
                # Parse the data
                parsed_data: Final[list[dict]] = await _extract(web_response=response, web_source="collegeboard")

                # Check if the parsed data contains any universities
                if len(parsed_data) == 0:
                    # Nothing found
                    return_data["current_state"]["collegeboard"] = None
                else:
                    # Store the results
                    return_data["current_state"]["collegeboard"] = parsed_data

    # Declare the return dictionary
    return_data: dict = {
        "target_state": {
            "usnews": [],
            "collegeboard": [],
        },
        "current_state": {
            "usnews": [],
            "collegeboard": [],
        },
    }

    # Execute
    await _search(return_data=return_data)

    # Return
    return return_data

async def _search_for_living_costs(target_city: str, target_state_abrv: str, current_city: str, current_state_abrv: str) -> dict:
    async def _extract(web_response: any, web_source: str) -> list[dict]:
        """
        Handles the extraction of university information from the given ``web_response``.
        Site specific parsing is handled via the ``web_source`` parameter.

        Parameters
        ----------
        web_response : any
            An HTML string or similar

        web_source : str
            A valid string identifier for where the web response came from
        """

        # Declare the return object
        return_data: list[dict] = []

        # Configure the parser
        parser: Final[BeautifulSoup] = BeautifulSoup(markup=web_response, features="lxml")

        # Switch on web source
        match web_source:
            # Source: https://www.numbeo.com/cost-of-living/compare_cities.jsp?country1=United+States&city1=Miami%2C+FL&country2=United+States&city2=New%20York%2C+NY
            case "numbeo":
                # Retrieve the cost table
                cost_table = (
                    parser.find("table", attrs={"class": "data_wide_table new_bar_table cost_comparison_table"})
                    .find_all("tr")
                )

                # Iterate through each table row
                for cost_entry in cost_table:
                    # Check if the current entry is just a header or a valid data entry
                    if cost_entry.find("td") is None:
                        # This is a header || Continue to the next entry
                        continue

                    # All the cost entries have nested data so this will act
                    # as the root node
                    root_node = cost_entry.find_all("td")

                    # The last two entries contain malformed/unneeded data
                    # so when this errors out we are done parsing
                    try:
                        # Retrieve the entry name
                        cost_entry_name: Final[str] = (
                            cost_entry.find("td")
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )

                        # Retrieve the current state cost
                        cost_entry_current_state_cost: Final[str] = (
                            root_node[1]
                            .find("span")
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )

                        # Retrieve the target state cost
                        cost_entry_target_state_cost: Final[str] = (
                            root_node[2]
                            .find("span")
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )

                        # Retrieve the cost difference between both states
                        cost_entry_cost_difference: Final[str] = (
                            root_node[3]
                            .find("span")
                            .get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )

                        # Clean up the JSON and append it to the return object
                        return_data.append(
                            await _clean_and_verify_json(
                                json_string=json.dumps(
                                    {
                                        "cost_entry_name": cost_entry_name,
                                        "cost_entry_current_state_cost": cost_entry_current_state_cost,
                                        "cost_entry_target_state_cost": cost_entry_target_state_cost,
                                        "cost_entry_cost_difference": cost_entry_cost_difference,
                                    }
                                )
                            )
                        )
                    except Exception as _:
                        # Exit the loop
                        break

            # Source: XYZ
            case _:
                pass

        # Return the extracted living cost information
        return return_data

    async def _search(return_data: dict) -> None:
        """
        Handles the searching of scholarships based on the given parent
        function's params.

        Parameters
        ----------
        return_data : dict
            A reference to the return data object
        """

        # Check that all parameters were filled
        if None not in [target_city, target_state_abrv, current_city, current_state_abrv]:
            # Format the URL
            formatted_url_numbeo: Final[str] = (
                __available_web__indexers__.get("living_costs", None)
                .get("numbeo", None)
                .format(target_city=target_city, target_state_abrv=target_state_abrv, current_city=current_city, current_state_abrv=current_state_abrv)
                .replace(" ", "%20")
            )

            # Execute a web request
            response: Final[any] = await _standard_fetch(url=formatted_url_numbeo)

            # Check if a valid response was returned
            if response is None:
                # No data found set as None
                return_data["numbeo"] = None
            else:
                # Parse the data and store the results
                return_data["numbeo"] = await _extract(web_response=response, web_source="numbeo")

    # Declare the return dictionary
    return_data: dict = {
        "numbeo": [],
    }

    # Execute
    await _search(return_data=return_data)

    # Return
    return return_data

async def _search_for_queer_scoring(target_state_abrv: str, current_state_abrv: str, use_queer_scoring: bool) -> dict:
    async def _extract(web_response: any, web_source: str) -> list[dict]:
        """
        Handles the extraction of university information from the given ``web_response``.
        Site specific parsing is handled via the ``web_source`` parameter.

        Parameters
        ----------
        web_response : any
            An HTML string or similar

        web_source : str
            A valid string identifier for where the web response came from
        """

        # Declare the return object
        return_data: list[dict] = []

        # Configure the parser
        parser: Final[BeautifulSoup] = BeautifulSoup(markup=web_response, features="lxml")

        # Switch on web source
        match web_source:
            # Source: https://www.lgbtmap.org/equality_maps/profile_state/FL
            case "lgbtmap":
                # Retrieve the quick facts row
                quick_facts_row = (
                    parser.find("div", attrs={"class": "row quickfacts"})
                    .find("div", attrs={"class": "col-xs-12"})
                    .find_all("div")
                )

                # Retrieve the policy tally row
                policy_tally_row = (
                    parser.find("div", attrs={"class": "policytally"})
                    .find("div", attrs={"class": "col-xs-12 col-md-7"})
                    .find_all("div", attrs={"class": "row policyboxes"})
                )

                # Declare the quick facts list to store the found quick facts
                quick_facts_list: list[str] = []

                # Declare the policy tally list to store the found policy tallies
                policy_tally_list: list[str] = []

                # Iterate through each entry
                for quick_facts_entry in quick_facts_row:
                    # Retrieve the statistical data and append it
                    quick_facts_list.append(
                        quick_facts_entry.find("span")
                        .get_text()
                        .strip()
                        .replace("\n", " ")
                        .replace("\xa0", " ")
                    )

                for policy_tally_entry in policy_tally_row:
                    for entry in policy_tally_entry.find_all("span", attrs={"class": "tally"}):
                        policy_tally_list.append(
                            entry.get_text()
                            .strip()
                            .replace("\n", " ")
                            .replace("\xa0", " ")
                        )

                # Clean up the JSON and append it to the return object
                return_data.append(
                    await _clean_and_verify_json(
                        json_string=json.dumps(
                            {
                                "queer_adults_percentage": quick_facts_list[0],
                                "queer_youth_population": quick_facts_list[1],
                                "queer_workforce_percentage": quick_facts_list[2],
                                "queer_worker_percentage": quick_facts_list[3],
                                "queer_adults_with_children_percentage": quick_facts_list[4],
                                "sexual_orientation_policy_score": policy_tally_list[0],
                                "gender_identity_policy_score": policy_tally_list[1],
                                "overall_policy_score": policy_tally_list[2],
                            }
                        )
                    )
                )

            # Source: XYZ
            case _:
                pass

        # Return the extracted queer scoring
        return return_data

    async def _search(return_data: dict) -> None:
        """
        Handles the searching of scholarships based on the given parent
        function's params.

        Parameters
        ----------
        return_data : dict
            A reference to the return data object
        """

        # Check the target state first
        if target_state_abrv is not None:
            # Format the URL
            formatted_url_lgbtmap: Final[str] = (
                __available_web__indexers__.get("queer_scoring", None)
                .get("lgbtmap", None)
                .format(mixed_state_abrv=target_state_abrv)
                .replace(" ", "%20")
            )

            # Execute a web request
            response: Final[any] = await _standard_fetch(url=formatted_url_lgbtmap)

            # Check if a valid response was returned
            if response is None:
                # No data found || Set as None
                return_data["target_state"]["lgbtmap"] = None
            else:
                # Parse the data and store the results
                return_data["target_state"]["lgbtmap"] = await _extract(web_response=response, web_source="lgbtmap")

        # Check the current state next
        if current_state_abrv is not None:
            # Format the URL
            formatted_url_lgbtmap: Final[str] = (
                __available_web__indexers__.get("queer_scoring", None)
                .get("lgbtmap", None)
                .format(mixed_state_abrv=current_state_abrv)
                .replace(" ", "%20")
            )

            # Execute a web request
            response: Final[any] = await _standard_fetch(url=formatted_url_lgbtmap)

            # Check if a valid response was returned
            if response is None:
                # No data found || Set as None
                return_data["current_state"]["lgbtmap"] = None
            else:
                # Parse the data and store the results
                return_data["current_state"]["lgbtmap"] = await _extract(web_response=response, web_source="lgbtmap")

    # Declare the return dictionary
    return_data: dict = {
        "target_state": {
            "lgbtmap": [],
        },
        "current_state": {
            "lgbtmap": [],
        },
    }

    # Execute
    if use_queer_scoring == True:
        await _search(return_data=return_data)

    # Return
    return return_data

# Script Check
if __name__ == "__main__":
    asyncio.run(
        search(
            SearchQuery(
                target_state="CA",
                current_state="Florida",
                majoring_target="",
                use_queer_scoring=True,
            )
        )
    )
