"""
Borehole Log Overflow and Multi-Page Module

This module handles overflow detection and multi-page layout for borehole logs
when content exceeds single page capacity.

Key Functions:
- check_depth_overflow: Detect when depth range exceeds page capacity
- calculate_page_breaks: Determine optimal page break points
- handle_multi_page_layout: Coordinate multi-page rendering
- get_page_depth_range: Calculate depth range for each page
"""

import logging
from typing import List, Tuple, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


def check_depth_overflow(
    total_depth: float,
    page_height_available: float,
    depth_scale: float = 50.0,  # pixels per meter
    min_page_depth: float = 5.0,  # minimum depth per page
) -> Tuple[bool, int, List[Tuple[float, float]]]:
    """
    Check if borehole depth requires multiple pages and calculate page breaks.

    Args:
        total_depth: Total borehole depth in meters
        page_height_available: Available height for plotting in pixels
        depth_scale: Scale factor (pixels per meter)
        min_page_depth: Minimum depth range per page

    Returns:
        tuple: (needs_overflow, total_pages, page_depth_ranges)
    """
    try:
        # Calculate maximum depth that fits on one page
        max_depth_per_page = page_height_available / depth_scale

        # Check if overflow is needed
        needs_overflow = total_depth > max_depth_per_page

        if not needs_overflow:
            return False, 1, [(0.0, total_depth)]

        # Calculate optimal page breaks
        page_depth_ranges = _calculate_optimal_page_breaks(
            total_depth, max_depth_per_page, min_page_depth
        )

        total_pages = len(page_depth_ranges)

        logger.info(
            f"Multi-page layout required: {total_pages} pages for {total_depth}m depth"
        )
        return True, total_pages, page_depth_ranges

    except Exception as e:
        logger.error(f"Error checking depth overflow: {e}")
        return False, 1, [(0.0, total_depth)]


def _calculate_optimal_page_breaks(
    total_depth: float, max_depth_per_page: float, min_page_depth: float
) -> List[Tuple[float, float]]:
    """Calculate optimal page break points for multi-page layout."""

    page_ranges = []
    current_depth = 0.0

    while current_depth < total_depth:
        # Calculate remaining depth
        remaining_depth = total_depth - current_depth

        if remaining_depth <= max_depth_per_page:
            # Last page - use all remaining depth
            page_ranges.append((current_depth, total_depth))
            break
        else:
            # Check if splitting would leave too little for next page
            if remaining_depth - max_depth_per_page < min_page_depth:
                # Adjust current page to leave minimum for next page
                page_end = total_depth - min_page_depth
                page_ranges.append((current_depth, page_end))
                current_depth = page_end
            else:
                # Standard page break
                page_end = current_depth + max_depth_per_page
                page_ranges.append((current_depth, page_end))
                current_depth = page_end

    return page_ranges


def calculate_page_breaks_by_stratum(
    geology_data: List[Dict],
    total_depth: float,
    max_depth_per_page: float,
    prefer_stratum_breaks: bool = True,
) -> List[Tuple[float, float]]:
    """
    Calculate page breaks preferring geological stratum boundaries.

    Args:
        geology_data: List of geological strata with depth information
        total_depth: Total borehole depth
        max_depth_per_page: Maximum depth per page
        prefer_stratum_breaks: Whether to prefer breaking at stratum boundaries

    Returns:
        list: Page depth ranges as (start_depth, end_depth) tuples
    """
    try:
        if not prefer_stratum_breaks or not geology_data:
            return _calculate_optimal_page_breaks(total_depth, max_depth_per_page, 5.0)

        # Extract stratum boundaries
        stratum_boundaries = _extract_stratum_boundaries(geology_data)

        # Calculate page breaks considering boundaries
        page_ranges = []
        current_depth = 0.0

        while current_depth < total_depth:
            remaining_depth = total_depth - current_depth

            if remaining_depth <= max_depth_per_page:
                page_ranges.append((current_depth, total_depth))
                break

            # Find best break point near max page depth
            target_break = current_depth + max_depth_per_page
            best_break = _find_best_stratum_break(
                stratum_boundaries, target_break, current_depth, total_depth
            )

            page_ranges.append((current_depth, best_break))
            current_depth = best_break

        return page_ranges

    except Exception as e:
        logger.error(f"Error calculating stratum-based page breaks: {e}")
        return _calculate_optimal_page_breaks(total_depth, max_depth_per_page, 5.0)


def _extract_stratum_boundaries(geology_data: List[Dict]) -> List[float]:
    """Extract depth boundaries from geological strata data."""
    boundaries = []

    for stratum in geology_data:
        if "GEOL_TOP" in stratum and stratum["GEOL_TOP"] is not None:
            try:
                boundaries.append(float(stratum["GEOL_TOP"]))
            except (ValueError, TypeError):
                continue

        if "GEOL_BASE" in stratum and stratum["GEOL_BASE"] is not None:
            try:
                boundaries.append(float(stratum["GEOL_BASE"]))
            except (ValueError, TypeError):
                continue

    # Remove duplicates and sort
    boundaries = sorted(list(set(boundaries)))
    return boundaries


def _find_best_stratum_break(
    boundaries: List[float],
    target_depth: float,
    min_depth: float,
    max_depth: float,
    tolerance: float = 2.0,
) -> float:
    """Find the best stratum boundary near the target depth for page break."""

    # Filter boundaries within reasonable range
    candidates = [
        b
        for b in boundaries
        if min_depth + 2.0 <= b <= max_depth - 2.0  # Leave some margin
    ]

    if not candidates:
        return min(target_depth, max_depth)

    # Find boundary closest to target within tolerance
    close_boundaries = [b for b in candidates if abs(b - target_depth) <= tolerance]

    if close_boundaries:
        # Choose the closest boundary to target
        return min(close_boundaries, key=lambda x: abs(x - target_depth))

    # If no boundaries within tolerance, find the best compromise
    # Prefer boundaries before target depth to avoid overshooting
    before_target = [b for b in candidates if b <= target_depth]

    if before_target:
        return max(before_target)  # Latest boundary before target
    else:
        return min(candidates)  # Earliest boundary after target


def get_page_depth_range(
    page_number: int, page_ranges: List[Tuple[float, float]]
) -> Tuple[float, float]:
    """
    Get the depth range for a specific page.

    Args:
        page_number: Page number (1-indexed)
        page_ranges: List of page depth ranges

    Returns:
        tuple: (start_depth, end_depth) for the page
    """
    try:
        if 1 <= page_number <= len(page_ranges):
            return page_ranges[page_number - 1]
        else:
            logger.warning(f"Invalid page number {page_number}, returning full range")
            return page_ranges[0] if page_ranges else (0.0, 0.0)
    except Exception as e:
        logger.error(f"Error getting page depth range: {e}")
        return (0.0, 0.0)


def filter_data_for_page(
    data_list: List[Dict],
    page_start_depth: float,
    page_end_depth: float,
    depth_field: str = "GEOL_TOP",
    depth_field_end: Optional[str] = "GEOL_BASE",
) -> List[Dict]:
    """
    Filter geological/sample data for a specific page depth range.

    Args:
        data_list: List of data records
        page_start_depth: Page start depth
        page_end_depth: Page end depth
        depth_field: Field name for depth start
        depth_field_end: Field name for depth end (optional)

    Returns:
        list: Filtered data records for the page
    """
    filtered_data = []

    for record in data_list:
        try:
            # Get record depth
            record_top = record.get(depth_field)
            if record_top is None:
                continue

            record_top = float(record_top)

            # Get record base depth if available
            record_base = record_top
            if depth_field_end and record.get(depth_field_end) is not None:
                try:
                    record_base = float(record.get(depth_field_end))
                except (ValueError, TypeError):
                    record_base = record_top

            # Check if record overlaps with page range
            if _record_overlaps_page(
                record_top, record_base, page_start_depth, page_end_depth
            ):
                filtered_data.append(record)

        except (ValueError, TypeError) as e:
            logger.warning(f"Skipping record with invalid depth: {e}")
            continue

    return filtered_data


def _record_overlaps_page(
    record_top: float, record_base: float, page_start: float, page_end: float
) -> bool:
    """Check if a record overlaps with the page depth range."""

    # Ensure record_base >= record_top
    if record_base < record_top:
        record_base = record_top

    # Check for overlap
    return not (record_base < page_start or record_top > page_end)


def calculate_continuation_indicators(
    page_ranges: List[Tuple[float, float]], page_number: int
) -> Dict[str, bool]:
    """
    Calculate whether continuation indicators are needed for a page.

    Args:
        page_ranges: List of all page depth ranges
        page_number: Current page number (1-indexed)

    Returns:
        dict: Continuation indicators {'continues_above': bool, 'continues_below': bool}
    """
    indicators = {"continues_above": False, "continues_below": False}

    try:
        if 1 <= page_number <= len(page_ranges):
            page_start, page_end = page_ranges[page_number - 1]

            # Check if there are pages above
            indicators["continues_above"] = page_number > 1

            # Check if there are pages below
            indicators["continues_below"] = page_number < len(page_ranges)

    except Exception as e:
        logger.error(f"Error calculating continuation indicators: {e}")

    return indicators


def get_overflow_summary(
    total_depth: float, page_ranges: List[Tuple[float, float]]
) -> Dict:
    """
    Get summary information about multi-page overflow layout.

    Args:
        total_depth: Total borehole depth
        page_ranges: List of page depth ranges

    Returns:
        dict: Summary information
    """
    summary = {
        "total_depth": total_depth,
        "total_pages": len(page_ranges),
        "requires_overflow": len(page_ranges) > 1,
        "average_page_depth": 0.0,
        "page_depths": [],
        "depth_distribution": {},
    }

    try:
        if page_ranges:
            page_depths = [end - start for start, end in page_ranges]
            summary["page_depths"] = page_depths
            summary["average_page_depth"] = sum(page_depths) / len(page_depths)

            # Depth distribution
            summary["depth_distribution"] = {
                f"page_{i+1}": {
                    "start_depth": start,
                    "end_depth": end,
                    "depth_range": end - start,
                }
                for i, (start, end) in enumerate(page_ranges)
            }

    except Exception as e:
        logger.error(f"Error creating overflow summary: {e}")

    return summary


def validate_page_layout(
    page_ranges: List[Tuple[float, float]],
    total_depth: float,
    min_page_depth: float = 2.0,
) -> Tuple[bool, List[str]]:
    """
    Validate multi-page layout for consistency and reasonableness.

    Args:
        page_ranges: List of page depth ranges
        total_depth: Total expected depth
        min_page_depth: Minimum acceptable page depth

    Returns:
        tuple: (is_valid, list_of_warnings)
    """
    warnings = []

    try:
        if not page_ranges:
            warnings.append("No page ranges defined")
            return False, warnings

        # Check continuity
        for i in range(len(page_ranges) - 1):
            current_end = page_ranges[i][1]
            next_start = page_ranges[i + 1][0]

            if abs(current_end - next_start) > 0.01:  # Allow small rounding errors
                warnings.append(f"Gap or overlap between pages {i+1} and {i+2}")

        # Check total depth coverage
        if page_ranges:
            first_start = page_ranges[0][0]
            last_end = page_ranges[-1][1]

            if first_start > 0.01:
                warnings.append(
                    f"Pages don't start from surface (start: {first_start})"
                )

            if abs(last_end - total_depth) > 0.01:
                warnings.append(
                    f"Pages don't cover full depth (end: {last_end}, total: {total_depth})"
                )

        # Check page depth reasonableness
        for i, (start, end) in enumerate(page_ranges):
            page_depth = end - start
            if page_depth < min_page_depth:
                warnings.append(
                    f"Page {i+1} depth ({page_depth:.1f}m) below minimum ({min_page_depth}m)"
                )

            if page_depth <= 0:
                warnings.append(
                    f"Page {i+1} has invalid depth range ({start} to {end})"
                )

    except Exception as e:
        warnings.append(f"Error during validation: {e}")

    is_valid = len(warnings) == 0
    return is_valid, warnings
