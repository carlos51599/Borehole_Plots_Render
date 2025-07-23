"""
AGS (Association of Geotechnical and Geoenvironmental Specialists) file data loader.

This module handles the parsing and loading of AGS format files, which are the
standard format for geotechnical data exchange in the UK. It provides functions
to extract specific data groups (like LOCA for location data) and combine data
from multiple AGS files.

Key Functions:
- parse_group(): Extract a specific data group from AGS file content
- load_all_loca_data(): Load and combine location data from multiple AGS files

AGS File Structure:
AGS files contain structured data organized into groups, with each group having:
- GROUP header line specifying the group name
- HEADING line defining column names
- DATA lines containing the actual data values

Author: [Project Team]
Last Modified: July 2025
"""

import csv
import pandas as pd
import os


def parse_group(content, group_name):
    """
    Parse a specific data group from AGS file content.

    This function extracts data for a specified group (e.g., 'LOCA', 'GEOL', 'SAMP')
    from AGS file content and returns it as a pandas DataFrame.

    Args:
        content (str): Complete AGS file content as string
        group_name (str): Name of the group to extract (e.g., 'LOCA', 'GEOL')

    Returns:
        pandas.DataFrame: Extracted data with proper column headers

    AGS File Format:
        GROUP,LOCA
        HEADING,LOCA_ID,LOCA_TYPE,LOCA_NATE,LOCA_NATN
        DATA,BH001,RC,123456,654321
        DATA,BH002,RC,123457,654322

    Example:
        >>> content = "GROUP,LOCA\\nHEADING,LOCA_ID,LOCA_NATE\\nDATA,BH001,123456"
        >>> df = parse_group(content, "LOCA")
        >>> print(df.columns.tolist())
        ['LOCA_ID', 'LOCA_NATE']
    """
    lines = content.splitlines()
    parsed = list(csv.reader(lines, delimiter=",", quotechar='"'))
    headings = []
    data = []
    in_group = False

    for row in parsed:
        # Check for GROUP header matching our target group
        if row and row[0] == "GROUP" and len(row) > 1 and row[1] == group_name:
            in_group = True
            continue

        # Extract column headings within the group
        if in_group and row and row[0] == "HEADING":
            headings = row[1:]  # Skip the "HEADING" identifier
            continue

        # Extract data rows within the group
        if in_group and row and row[0] == "DATA":
            data.append(
                row[1 : len(headings) + 1]
            )  # Extract data matching heading count
            continue

        # Stop processing when we hit a different group
        if (
            in_group
            and row
            and row[0] == "GROUP"
            and (len(row) < 2 or row[1] != group_name)
        ):
            break

    df = pd.DataFrame(data, columns=headings)
    return df


def load_all_loca_data(ags_files):
    """
    Load and combine location (LOCA) data from multiple AGS files.

    This function processes multiple AGS files, extracts location data from each,
    handles coordinate conversion, and combines all data into a single DataFrame
    while avoiding ID conflicts between files.

    Args:
        ags_files (list): List of tuples (filename, content) for each AGS file

    Returns:
        tuple: (combined_dataframe, filename_content_map)
            - combined_dataframe (pandas.DataFrame): All LOCA data combined
            - filename_content_map (dict): Mapping of filename to file content

    Processing Steps:
        1. Extract LOCA group from each file
        2. Convert coordinate columns to numeric (LOCA_NATE, LOCA_NATN)
        3. Remove rows with invalid coordinates
        4. Handle duplicate LOCA_ID values by adding file suffix
        5. Add source file tracking
        6. Combine all data into single DataFrame

    Data Columns Added:
        - original_LOCA_ID: Preserves original ID before any modifications
        - ags_file: Source filename for each borehole
        - LOCA_ID: Modified ID (with suffix if duplicates exist)

    Example:
        >>> files = [("site1.ags", "GROUP,LOCA\\n..."), ("site2.ags", "GROUP,LOCA\\n...")]
        >>> combined_df, file_map = load_all_loca_data(files)
        >>> print(combined_df.columns.tolist())
        ['LOCA_ID', 'LOCA_NATE', 'LOCA_NATN', 'original_LOCA_ID', 'ags_file']
    """
    all_loca = []
    filename_map = {}
    existing_ids = set()

    for fname, content in ags_files:
        # Parse LOCA group from current file
        loca_df = parse_group(content, "LOCA")

        # Convert coordinate columns to numeric, invalid values become NaN
        for col in ["LOCA_NATE", "LOCA_NATN"]:
            if col in loca_df.columns:
                loca_df[col] = pd.to_numeric(loca_df[col], errors="coerce")

        # Remove rows with missing coordinates
        loca_df = loca_df.dropna(subset=["LOCA_NATE", "LOCA_NATN"])

        # Create unique suffix from filename (first 19 chars without extension)
        suffix = os.path.splitext(fname)[0][:19]

        # Preserve original IDs and create unique IDs for duplicates
        loca_df["original_LOCA_ID"] = loca_df["LOCA_ID"]
        loca_df["LOCA_ID"] = loca_df["LOCA_ID"].apply(
            lambda x: f"{x}_{suffix}" if x in existing_ids else x
        )
        existing_ids.update(loca_df["LOCA_ID"].tolist())

        # Add source file tracking
        loca_df["ags_file"] = fname
        all_loca.append(loca_df)
        filename_map[fname] = content

    return pd.concat(all_loca, ignore_index=True), filename_map
