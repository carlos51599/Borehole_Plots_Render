"""
AGS Data Parsing Module

This module handles parsing of AGS (Association of Geotechnical and Geoenvironmental Specialists)
format files for geological and borehole data extraction.

Key Functions:
- parse_ags_geol_section_from_string: Parse AGS content to extract GEOL, LOCA, and ABBR data
- parse_ags_group: Parse individual AGS group sections
- validate_ags_format: Validate AGS file format compliance

The parser handles:
- Multi-group AGS file parsing
- Data type conversion for geological and location data
- Error handling for malformed AGS files
- Memory-efficient DataFrame creation
"""

import pandas as pd
import csv
import logging
from typing import Tuple, Optional, Dict, List, Any

logger = logging.getLogger(__name__)


def parse_ags_geol_section_from_string(
    content: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Parse AGS content string and extract GEOL, LOCA, and ABBR group data as DataFrames.

    Args:
        content: AGS file content as string

    Returns:
        tuple: (geol_df, loca_df, abbr_df) - DataFrames containing geological,
               location, and abbreviation data respectively
    """
    try:
        logger.debug(f"Parsing AGS content: {len(content)} characters")
        lines = content.splitlines()
        parsed = _parse_csv_lines(lines)

        # Parse each group
        geol_df = _parse_ags_group(parsed, "GEOL", ["GEOL_TOP", "GEOL_BASE"])
        loca_df = _parse_ags_group(
            parsed, "LOCA", ["LOCA_NATE", "LOCA_NATN", "LOCA_GL"]
        )
        abbr_df = _parse_ags_group(parsed, "ABBR", [])

        logger.info(
            f"Successfully parsed AGS: GEOL={len(geol_df)}, "
            f"LOCA={len(loca_df)}, ABBR={len(abbr_df) if abbr_df is not None else 0}"
        )

        return geol_df, loca_df, abbr_df

    except Exception as e:
        logger.error(f"Error parsing AGS content: {e}")
        # Return empty DataFrames on error
        return pd.DataFrame(), pd.DataFrame(), None


def _parse_csv_lines(lines: List[str]) -> List[List[str]]:
    """Parse CSV-formatted lines using proper CSV reader."""
    try:
        return list(csv.reader(lines, delimiter=",", quotechar='"'))
    except Exception as e:
        logger.error(f"Error parsing CSV lines: {e}")
        return []


def _parse_ags_group(
    parsed_lines: List[List[str]], group_name: str, numeric_columns: List[str]
) -> pd.DataFrame:
    """
    Parse a specific AGS group from parsed lines.

    Args:
        parsed_lines: List of parsed CSV rows
        group_name: Name of the AGS group to parse (e.g., "GEOL", "LOCA")
        numeric_columns: List of column names that should be converted to numeric

    Returns:
        pd.DataFrame: Parsed group data
    """
    try:
        headings = []
        data = []
        in_group = False

        for row in parsed_lines:
            if not row:
                continue

            # Check for group start
            if row[0] == "GROUP" and len(row) > 1 and row[1] == group_name:
                in_group = True
                continue

            # Check for group end (another GROUP line that's not our group)
            if (
                in_group
                and row[0] == "GROUP"
                and (len(row) < 2 or row[1] != group_name)
            ):
                break

            # Parse headings
            if in_group and row[0] == "HEADING":
                headings = row[1:]
                continue

            # Parse data
            if in_group and row[0] == "DATA":
                # Ensure we don't exceed the number of headings
                data_row = row[1 : len(headings) + 1] if headings else []
                data.append(data_row)
                continue

        # Create DataFrame
        if not headings:
            logger.warning(f"No headings found for group {group_name}")
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=headings)

        # Clean LOCA_ID if present
        if "LOCA_ID" in df.columns:
            df["LOCA_ID"] = df["LOCA_ID"].str.strip()

        # Convert numeric columns
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        logger.debug(
            f"Parsed {group_name} group: {len(df)} rows, {len(df.columns)} columns"
        )
        return df

    except Exception as e:
        logger.error(f"Error parsing AGS group {group_name}: {e}")
        return pd.DataFrame()


def validate_ags_format(content: str) -> Tuple[bool, str]:
    """
    Validate basic AGS format compliance.

    Args:
        content: AGS file content as string

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not content.strip():
            return False, "Empty file content"

        lines = content.splitlines()

        # Check for basic AGS structure
        has_group = any("GROUP" in line for line in lines[:10])
        has_heading = any("HEADING" in line for line in lines[:20])
        has_data = any("DATA" in line for line in lines[:50])

        if not has_group:
            return False, "No GROUP declarations found - not a valid AGS file"

        if not has_heading:
            return False, "No HEADING declarations found - invalid AGS structure"

        if not has_data:
            return False, "No DATA rows found - file appears to be empty"

        # Check for required groups
        required_groups = ["LOCA"]
        found_groups = []

        for line in lines:
            if "GROUP" in line and "LOCA" in line:
                found_groups.append("LOCA")
                break

        missing_groups = [
            group for group in required_groups if group not in found_groups
        ]
        if missing_groups:
            return False, f"Missing required AGS groups: {', '.join(missing_groups)}"

        return True, "Valid AGS format"

    except Exception as e:
        return False, f"Error validating AGS format: {e}"


def extract_ags_metadata(content: str) -> Dict[str, Any]:
    """
    Extract metadata from AGS file content.

    Args:
        content: AGS file content as string

    Returns:
        dict: Metadata including project info, file info, etc.
    """
    metadata = {
        "project_name": None,
        "file_format": "AGS",
        "groups_found": [],
        "total_lines": 0,
        "data_rows": 0,
    }

    try:
        lines = content.splitlines()
        metadata["total_lines"] = len(lines)

        parsed = _parse_csv_lines(lines)

        # Count data rows and find groups
        groups_found = set()
        data_count = 0

        for row in parsed:
            if not row:
                continue

            if row[0] == "GROUP" and len(row) > 1:
                groups_found.add(row[1])
            elif row[0] == "DATA":
                data_count += 1

        metadata["groups_found"] = sorted(list(groups_found))
        metadata["data_rows"] = data_count

        # Try to extract project information from PROJ group if available
        proj_df = _parse_ags_group(parsed, "PROJ", [])
        if not proj_df.empty and "PROJ_NAME" in proj_df.columns:
            if len(proj_df) > 0:
                metadata["project_name"] = proj_df.iloc[0]["PROJ_NAME"]

        return metadata

    except Exception as e:
        logger.error(f"Error extracting AGS metadata: {e}")
        return metadata
