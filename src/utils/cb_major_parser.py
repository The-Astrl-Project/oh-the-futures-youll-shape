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
import os
import sys
import json
import time
from typing import Final
# ---

# ---

# ----------------------------------------------------------------

# File Docstring
# --------------------------------
# Oh, the Futures You'll Shape || utils/cb_major_parser.py
#
# Parses College Board major data into a workable JSON file.
#
# @author @MaxineToTheStars <https://github.com/MaxineToTheStars>
# ----------------------------------------------------------------

# Constants

# Public Variables

# Private Variables

# main
def main() -> None:
    # Local definitions
    start_time: float = 0
    end_time: float = 0

    # Parse args
    args: list[str] = sys.argv

    # Sanity check
    if len(args) < 3:
        # Log
        print("> [ERR] Missing arguments. || Exiting!")

        # Exit
        sys.exit(1)

    # Retrieve the input and output locations
    input_file: Final[str] = sys.argv[1]
    output_file: Final[str] = sys.argv[2]

    # Check the input file exists
    if os.path.isfile(input_file) != True:
        # Log
        print(f"> [ERR] Filepath {input_file} is not a file or is invalid.")

        # Exit
        sys.exit(1)

    # Check if an output file exists
    if os.path.isfile(output_file) != True:
        # Create a new file
        open(output_file, "x").close()

    # Start timer
    start_time = time.time()

    # Log
    print("> [LOG] Loading JSON input into memory...")

    # Open the input file for reading
    file = open(file=input_file, mode="r")

    # Load the JSON into memory
    input_data: Final[str] = json.load(fp=file)

    # Close the input file
    file.close()

    # End timer
    end_time = time.time()

    # Log
    print(f"> [LOG] Done! Took: {(end_time-start_time)*10**3:.03f}ms")

    # Define return data
    return_data: dict = {
        "major-id": [],
        "is-related": [],
    }

    # Start timer
    start_time = time.time()

    # Log
    print("> [LOG] Starting data processing...")

    # Iterate through the data array
    for entry in input_data.get("data", []):
        # Redefine entry
        entry: Final[dict] = entry

        # Grab the title slug and append it
        return_data["major-id"].append(entry.get("titleSlug", ""))

        # Since this is an "umbrella" major this is set to false
        return_data["is-related"].append(False)

        # Iterate through the related majors
        for related_entry in entry.get("relatedMajors", []):
            # Refine related entry
            related_entry: Final[dict] = related_entry

            # Grab the title slug and append it
            return_data["major-id"].append(related_entry.get("titleSlug", ""))

            # Set the related status to True
            return_data["is-related"].append(True)

    # End timer
    end_time = time.time()

    # Log
    print(f"> [LOG] Done! Took: {(end_time-start_time)*10**3:.03f}ms")

    # Open the output file for writing
    file = open(file=output_file, mode="w")

    # Write the output
    json.dump(obj=return_data, fp=file)

    # Log
    print(f"> [LOG] Output written to {output_file}")

# Public Methods

# Private Methods

# Script Check
if __name__ == "__main__":
    main()
