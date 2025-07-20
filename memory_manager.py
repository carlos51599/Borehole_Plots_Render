"""
Memory Management Module

This module provides comprehensive memory monitoring, cleanup routines, and optimization
utilities for the Geo Borehole Sections Render application.
"""

import gc
import logging
import psutil
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MemoryStats:
    """Memory usage statistics."""

    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    percent: float  # Memory percentage
    available_mb: float  # Available system memory in MB
    timestamp: datetime


class MemoryManager:
    """
    Comprehensive memory management for the application.

    Features:
    - Memory usage monitoring and alerts
    - Automatic cleanup routines
    - DataFrame memory optimization
    - Cache management
    - Memory leak detection
    """

    def __init__(
        self,
        memory_threshold_mb: float = 500.0,
        cleanup_interval_minutes: int = 30,
        enable_auto_cleanup: bool = True,
    ):
        """
        Initialize memory manager.

        Args:
            memory_threshold_mb: Memory usage threshold for alerts (MB)
            cleanup_interval_minutes: Minutes between automatic cleanup
            enable_auto_cleanup: Whether to enable automatic cleanup
        """
        self.memory_threshold_mb = memory_threshold_mb
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self.enable_auto_cleanup = enable_auto_cleanup

        self.last_cleanup = datetime.now()
        self.memory_history: List[MemoryStats] = []
        self.max_history_size = 100  # Keep last 100 measurements

        # Cache references for cleanup
        self.cache_references: Dict[str, Any] = {}

        logger.info(
            f"MemoryManager initialized: threshold={memory_threshold_mb}MB, "
            f"cleanup_interval={cleanup_interval_minutes}min, auto_cleanup={enable_auto_cleanup}"
        )

    def get_current_memory_usage(self) -> MemoryStats:
        """Get current memory usage statistics."""

        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # Get system memory info
            system_memory = psutil.virtual_memory()

            stats = MemoryStats(
                rss_mb=memory_info.rss / 1024 / 1024,
                vms_mb=memory_info.vms / 1024 / 1024,
                percent=memory_percent,
                available_mb=system_memory.available / 1024 / 1024,
                timestamp=datetime.now(),
            )

            # Add to history
            self.memory_history.append(stats)
            if len(self.memory_history) > self.max_history_size:
                self.memory_history.pop(0)

            return stats

        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return MemoryStats(0, 0, 0, 0, datetime.now())

    def check_memory_threshold(self) -> bool:
        """Check if memory usage exceeds threshold."""

        stats = self.get_current_memory_usage()
        return stats.rss_mb > self.memory_threshold_mb

    def should_cleanup(self) -> bool:
        """Determine if cleanup should be performed."""

        if not self.enable_auto_cleanup:
            return False

        # Check time interval
        time_since_cleanup = datetime.now() - self.last_cleanup
        if time_since_cleanup.total_seconds() < (self.cleanup_interval_minutes * 60):
            return False

        # Check memory threshold
        return self.check_memory_threshold()

    def perform_cleanup(self, force: bool = False) -> Dict[str, Any]:
        """
        Perform memory cleanup operations.

        Args:
            force: Force cleanup regardless of conditions

        Returns:
            Dictionary with cleanup results
        """

        if not force and not self.should_cleanup():
            return {"performed": False, "reason": "conditions not met"}

        logger.info("🧹 Starting memory cleanup operation")

        start_stats = self.get_current_memory_usage()
        cleanup_results = {
            "performed": True,
            "start_memory_mb": start_stats.rss_mb,
            "actions": [],
        }

        try:
            # 1. Clear cache references
            cache_count = len(self.cache_references)
            self.cache_references.clear()
            cleanup_results["actions"].append(f"Cleared {cache_count} cache references")

            # 2. Force garbage collection
            collected = gc.collect()
            cleanup_results["actions"].append(f"Garbage collected {collected} objects")

            # 3. Clear any global caches (marker manager, coordinate service, etc.)
            self._clear_global_caches()
            cleanup_results["actions"].append("Cleared global caches")

            # 4. Clean up old DataFrames in memory history
            if len(self.memory_history) > 50:
                self.memory_history = self.memory_history[-50:]
                cleanup_results["actions"].append("Trimmed memory history")

            # Update last cleanup time
            self.last_cleanup = datetime.now()

            # Measure final memory usage
            end_stats = self.get_current_memory_usage()
            memory_saved = start_stats.rss_mb - end_stats.rss_mb

            cleanup_results.update(
                {
                    "end_memory_mb": end_stats.rss_mb,
                    "memory_saved_mb": memory_saved,
                    "timestamp": datetime.now(),
                }
            )

            logger.info(
                f"✅ Memory cleanup completed: {memory_saved:.2f}MB freed, "
                f"current usage: {end_stats.rss_mb:.2f}MB"
            )

            return cleanup_results

        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            cleanup_results["error"] = str(e)
            return cleanup_results

    def _clear_global_caches(self):
        """Clear caches from global singletons."""

        try:
            # Clear lazy marker manager cache
            from lazy_marker_manager import get_lazy_marker_manager

            marker_manager = get_lazy_marker_manager()
            marker_manager.clear_cache()

            # Clear coordinate service cache if available
            try:
                from coordinate_service import get_coordinate_service

                coord_service = get_coordinate_service()
                if hasattr(coord_service, "clear_cache"):
                    coord_service.clear_cache()
            except ImportError:
                pass  # Coordinate service might not be available

        except Exception as e:
            logger.warning(f"Error clearing global caches: {e}")

    def optimize_dataframe(
        self, df: pd.DataFrame, inplace: bool = False
    ) -> pd.DataFrame:
        """
        Optimize DataFrame memory usage.

        Args:
            df: DataFrame to optimize
            inplace: Whether to modify DataFrame in place

        Returns:
            Optimized DataFrame
        """

        if df.empty:
            return df

        result_df = df if inplace else df.copy()

        try:
            memory_before = result_df.memory_usage(deep=True).sum() / 1024 / 1024

            # Optimize numeric columns
            for col in result_df.select_dtypes(include=["int64"]).columns:
                if result_df[col].min() >= -32768 and result_df[col].max() <= 32767:
                    result_df[col] = result_df[col].astype("int16")
                elif (
                    result_df[col].min() >= -2147483648
                    and result_df[col].max() <= 2147483647
                ):
                    result_df[col] = result_df[col].astype("int32")

            for col in result_df.select_dtypes(include=["float64"]).columns:
                result_df[col] = pd.to_numeric(result_df[col], downcast="float")

            # Optimize object columns to category if beneficial
            for col in result_df.select_dtypes(include=["object"]).columns:
                if (
                    result_df[col].nunique() < len(result_df) * 0.5
                ):  # Less than 50% unique values
                    result_df[col] = result_df[col].astype("category")

            memory_after = result_df.memory_usage(deep=True).sum() / 1024 / 1024
            memory_saved = memory_before - memory_after

            if memory_saved > 0.1:  # Only log if significant savings
                logger.info(
                    f"DataFrame optimized: {memory_saved:.2f}MB saved "
                    f"({memory_before:.2f}MB → {memory_after:.2f}MB)"
                )

            return result_df

        except Exception as e:
            logger.error(f"Error optimizing DataFrame: {e}")
            return result_df

    def register_cache_reference(self, name: str, cache_object: Any):
        """Register a cache object for cleanup."""

        self.cache_references[name] = cache_object
        logger.debug(f"Registered cache reference: {name}")

    def unregister_cache_reference(self, name: str):
        """Unregister a cache object."""

        if name in self.cache_references:
            del self.cache_references[name]
            logger.debug(f"Unregistered cache reference: {name}")

    def get_memory_report(self) -> Dict[str, Any]:
        """Generate comprehensive memory usage report."""

        current_stats = self.get_current_memory_usage()

        # Calculate trends if we have history
        trend_data = {}
        if len(self.memory_history) >= 2:
            recent_memory = [s.rss_mb for s in self.memory_history[-10:]]
            trend_data = {
                "avg_recent_mb": sum(recent_memory) / len(recent_memory),
                "max_recent_mb": max(recent_memory),
                "min_recent_mb": min(recent_memory),
            }

        # Get system information
        system_info = {}
        try:
            system_memory = psutil.virtual_memory()
            system_info = {
                "total_system_mb": system_memory.total / 1024 / 1024,
                "available_system_mb": system_memory.available / 1024 / 1024,
                "system_percent_used": system_memory.percent,
            }
        except Exception as e:
            logger.warning(f"Could not get system memory info: {e}")

        return {
            "current_usage": {
                "rss_mb": current_stats.rss_mb,
                "vms_mb": current_stats.vms_mb,
                "percent": current_stats.percent,
            },
            "trend_data": trend_data,
            "system_info": system_info,
            "thresholds": {
                "memory_threshold_mb": self.memory_threshold_mb,
                "threshold_exceeded": current_stats.rss_mb > self.memory_threshold_mb,
            },
            "cache_info": {
                "registered_caches": len(self.cache_references),
                "cache_names": list(self.cache_references.keys()),
            },
            "cleanup_info": {
                "auto_cleanup_enabled": self.enable_auto_cleanup,
                "last_cleanup": (
                    self.last_cleanup.isoformat() if self.last_cleanup else None
                ),
                "next_cleanup_due": (
                    (
                        self.last_cleanup
                        + timedelta(minutes=self.cleanup_interval_minutes)
                    ).isoformat()
                    if self.last_cleanup
                    else None
                ),
            },
            "timestamp": current_stats.timestamp.isoformat(),
        }

    def monitor_memory_async(self, callback_func: Optional[callable] = None):
        """
        Start asynchronous memory monitoring.

        Args:
            callback_func: Optional callback function to call on threshold breach
        """

        def memory_check():
            stats = self.get_current_memory_usage()

            if stats.rss_mb > self.memory_threshold_mb:
                logger.warning(
                    f"⚠️ Memory threshold exceeded: {stats.rss_mb:.2f}MB > {self.memory_threshold_mb}MB"
                )

                if callback_func:
                    try:
                        callback_func(stats)
                    except Exception as e:
                        logger.error(f"Error in memory callback: {e}")

                # Perform automatic cleanup if enabled
                if self.enable_auto_cleanup:
                    self.perform_cleanup()

        # For now, just check once - in a real implementation, this could use threading
        memory_check()


# Global instance
_memory_manager = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""

    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def cleanup_memory(force: bool = False) -> Dict[str, Any]:
    """Convenience function to perform memory cleanup."""

    manager = get_memory_manager()
    return manager.perform_cleanup(force=force)


def optimize_dataframe_memory(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """Convenience function to optimize DataFrame memory usage."""

    manager = get_memory_manager()
    return manager.optimize_dataframe(df, inplace=inplace)


def get_memory_stats() -> MemoryStats:
    """Convenience function to get current memory statistics."""

    manager = get_memory_manager()
    return manager.get_current_memory_usage()


def monitor_memory_usage(log_level: str = "INFO"):
    """Convenience function to log current memory usage."""

    stats = get_memory_stats()
    log_func = getattr(logger, log_level.lower(), logger.info)
    log_func(
        f"Memory usage: {stats.rss_mb:.2f}MB RSS, {stats.percent:.1f}% of system, "
        f"{stats.available_mb:.2f}MB available"
    )
