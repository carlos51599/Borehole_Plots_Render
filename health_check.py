"""
Application Health Check System

Provides comprehensive health monitoring, system diagnostics, and status reporting
for the Geo Borehole Sections Render application.

Features:
- System resource monitoring
- Service health checks
- Performance metrics
- Error rate tracking
- Configuration validation
- Dependency status checks
"""

import logging
import time
import os
import sys
import psutil
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import traceback

from app_constants import APP_VERSION, CONFIG_VERSION, PERFORMANCE_CONFIG, FILE_LIMITS
from coordinate_service import get_coordinate_service
from error_recovery import get_recovery_manager

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class SystemMonitor:
    """
    Monitors system resources and performance metrics.
    """

    def __init__(self):
        self.start_time = time.time()
        self.check_history = []
        self.max_history = 100

    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information."""
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "uptime_seconds": time.time() - psutil.boot_time(),
        }

    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory usage information."""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "total_mb": round(memory.total / 1024 / 1024, 2),
            "available_mb": round(memory.available / 1024 / 1024, 2),
            "used_mb": round(memory.used / 1024 / 1024, 2),
            "percent_used": memory.percent,
            "swap_total_mb": round(swap.total / 1024 / 1024, 2),
            "swap_used_mb": round(swap.used / 1024 / 1024, 2),
            "swap_percent": swap.percent,
            "status": self._assess_memory_status(memory.percent),
        }

    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU usage information."""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        return {
            "percent_used": cpu_percent,
            "logical_cores": cpu_count,
            "physical_cores": psutil.cpu_count(logical=False),
            "current_freq_mhz": cpu_freq.current if cpu_freq else None,
            "max_freq_mhz": cpu_freq.max if cpu_freq else None,
            "status": self._assess_cpu_status(cpu_percent),
        }

    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk usage information."""
        try:
            disk_usage = psutil.disk_usage("/")
            disk_io = psutil.disk_io_counters()

            return {
                "total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                "free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2),
                "used_gb": round(disk_usage.used / 1024 / 1024 / 1024, 2),
                "percent_used": round((disk_usage.used / disk_usage.total) * 100, 2),
                "read_count": disk_io.read_count if disk_io else None,
                "write_count": disk_io.write_count if disk_io else None,
                "status": self._assess_disk_status(
                    (disk_usage.used / disk_usage.total) * 100
                ),
            }
        except Exception as e:
            logger.warning(f"Could not get disk info: {e}")
            return {"status": HealthStatus.UNKNOWN, "error": str(e)}

    def _assess_memory_status(self, memory_percent: float) -> str:
        """Assess memory health status."""
        if memory_percent < 70:
            return HealthStatus.HEALTHY
        elif memory_percent < 85:
            return HealthStatus.WARNING
        else:
            return HealthStatus.CRITICAL

    def _assess_cpu_status(self, cpu_percent: float) -> str:
        """Assess CPU health status."""
        if cpu_percent < 60:
            return HealthStatus.HEALTHY
        elif cpu_percent < 80:
            return HealthStatus.WARNING
        else:
            return HealthStatus.CRITICAL

    def _assess_disk_status(self, disk_percent: float) -> str:
        """Assess disk health status."""
        if disk_percent < 80:
            return HealthStatus.HEALTHY
        elif disk_percent < 90:
            return HealthStatus.WARNING
        else:
            return HealthStatus.CRITICAL


class ServiceHealthChecker:
    """
    Checks the health of application services and dependencies.
    """

    def check_coordinate_service(self) -> Dict[str, Any]:
        """Check coordinate transformation service health."""
        try:
            start_time = time.time()

            # Test coordinate service
            service = get_coordinate_service()

            # Test basic transformation
            lat, lon = service.transform_bng_to_wgs84(529090, 181680)

            # Check if result is reasonable (London area)
            if 51.0 <= lat <= 52.0 and -1.0 <= lon <= 0.0:
                status = HealthStatus.HEALTHY
                message = "Coordinate transformations working correctly"
            else:
                status = HealthStatus.WARNING
                message = f"Coordinate transformation returned unexpected result: {lat}, {lon}"

            response_time = time.time() - start_time
            cache_stats = service.get_cache_stats()

            return {
                "status": status,
                "message": message,
                "response_time_ms": round(response_time * 1000, 2),
                "cache_stats": cache_stats,
                "test_result": {"lat": lat, "lon": lon},
            }

        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"Coordinate service failed: {str(e)}",
                "error": traceback.format_exc(),
            }

    def check_file_system(self) -> Dict[str, Any]:
        """Check file system access and permissions."""
        try:
            # Check if we can read/write to the current directory
            test_file = "health_check_test.tmp"
            test_content = "health check test"

            # Write test
            with open(test_file, "w") as f:
                f.write(test_content)

            # Read test
            with open(test_file, "r") as f:
                content = f.read()

            # Cleanup
            os.remove(test_file)

            if content == test_content:
                return {
                    "status": HealthStatus.HEALTHY,
                    "message": "File system read/write operations working",
                    "permissions": "read/write",
                }
            else:
                return {
                    "status": HealthStatus.WARNING,
                    "message": "File content mismatch",
                    "expected": test_content,
                    "actual": content,
                }

        except PermissionError:
            return {
                "status": HealthStatus.CRITICAL,
                "message": "No write permission in current directory",
                "permissions": "read-only",
            }
        except Exception as e:
            return {
                "status": HealthStatus.CRITICAL,
                "message": f"File system error: {str(e)}",
                "error": traceback.format_exc(),
            }

    def check_required_modules(self) -> Dict[str, Any]:
        """Check if all required Python modules are available."""
        required_modules = [
            "dash",
            "pandas",
            "numpy",
            "matplotlib",
            "pyproj",
            "shapely",
            "dash_leaflet",
            "sklearn",
            "psutil",
        ]

        module_status = {}
        all_healthy = True

        for module_name in required_modules:
            try:
                __import__(module_name)
                module_status[module_name] = {
                    "status": HealthStatus.HEALTHY,
                    "available": True,
                }
            except ImportError as e:
                module_status[module_name] = {
                    "status": HealthStatus.CRITICAL,
                    "available": False,
                    "error": str(e),
                }
                all_healthy = False

        overall_status = HealthStatus.HEALTHY if all_healthy else HealthStatus.CRITICAL

        return {
            "status": overall_status,
            "modules": module_status,
            "total_modules": len(required_modules),
            "available_modules": sum(
                1 for m in module_status.values() if m["available"]
            ),
        }


class PerformanceMonitor:
    """
    Monitors application performance metrics.
    """

    def __init__(self):
        self.metrics = {}
        self.request_times = []
        self.max_request_history = 1000

    def record_request_time(self, operation: str, duration: float):
        """Record the duration of an operation."""
        timestamp = time.time()
        self.request_times.append(
            {"operation": operation, "duration": duration, "timestamp": timestamp}
        )

        # Keep only recent requests
        cutoff_time = timestamp - 3600  # Last hour
        self.request_times = [
            r for r in self.request_times if r["timestamp"] > cutoff_time
        ][-self.max_request_history :]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.request_times:
            return {
                "status": HealthStatus.UNKNOWN,
                "message": "No performance data available",
                "total_requests": 0,
            }

        # Calculate statistics
        durations = [r["duration"] for r in self.request_times]
        recent_requests = [
            r
            for r in self.request_times
            if r["timestamp"] > time.time() - 300  # Last 5 minutes
        ]

        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        # Assess performance status
        if avg_duration < 1.0:
            status = HealthStatus.HEALTHY
        elif avg_duration < 5.0:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.CRITICAL

        return {
            "status": status,
            "total_requests": len(self.request_times),
            "recent_requests_5min": len(recent_requests),
            "avg_response_time_s": round(avg_duration, 3),
            "max_response_time_s": round(max_duration, 3),
            "min_response_time_s": round(min_duration, 3),
            "requests_per_minute": len(recent_requests) / 5 if recent_requests else 0,
        }


class HealthChecker:
    """
    Main health checker that coordinates all health monitoring.
    """

    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.service_checker = ServiceHealthChecker()
        self.performance_monitor = PerformanceMonitor()
        self.last_check_time = None
        self.last_check_result = None

    def run_health_check(self, include_detailed: bool = True) -> Dict[str, Any]:
        """
        Run a comprehensive health check of the application.

        Args:
            include_detailed: Whether to include detailed system metrics

        Returns:
            Dict containing health check results
        """
        start_time = time.time()
        check_time = datetime.now().isoformat()

        health_data = {
            "timestamp": check_time,
            "application": {
                "name": "Geo Borehole Sections Render",
                "version": APP_VERSION,
                "config_version": CONFIG_VERSION,
                "uptime_seconds": time.time() - self.system_monitor.start_time,
                "status": HealthStatus.HEALTHY,
            },
            "services": {},
            "system": {},
            "performance": {},
            "overall_status": HealthStatus.HEALTHY,
            "check_duration_ms": 0,
        }

        # Check services
        try:
            health_data["services"][
                "coordinate_service"
            ] = self.service_checker.check_coordinate_service()
            health_data["services"][
                "file_system"
            ] = self.service_checker.check_file_system()
            health_data["services"][
                "modules"
            ] = self.service_checker.check_required_modules()
        except Exception as e:
            health_data["services"]["error"] = str(e)
            health_data["overall_status"] = HealthStatus.CRITICAL

        # Check system resources if detailed check requested
        if include_detailed:
            try:
                health_data["system"]["info"] = self.system_monitor.get_system_info()
                health_data["system"]["memory"] = self.system_monitor.get_memory_info()
                health_data["system"]["cpu"] = self.system_monitor.get_cpu_info()
                health_data["system"]["disk"] = self.system_monitor.get_disk_info()
            except Exception as e:
                health_data["system"]["error"] = str(e)

        # Performance metrics
        try:
            health_data["performance"] = (
                self.performance_monitor.get_performance_stats()
            )
        except Exception as e:
            health_data["performance"] = {
                "error": str(e),
                "status": HealthStatus.UNKNOWN,
            }

        # Error recovery status
        try:
            recovery_manager = get_recovery_manager()
            health_data["error_recovery"] = recovery_manager.get_system_health()
        except Exception as e:
            health_data["error_recovery"] = {"error": str(e)}

        # Determine overall status
        health_data["overall_status"] = self._determine_overall_status(health_data)

        # Record check duration
        health_data["check_duration_ms"] = round((time.time() - start_time) * 1000, 2)

        # Update cache
        self.last_check_time = time.time()
        self.last_check_result = health_data

        return health_data

    def _determine_overall_status(self, health_data: Dict[str, Any]) -> str:
        """Determine overall application health status."""
        statuses = []

        # Collect all status values
        for service_data in health_data.get("services", {}).values():
            if isinstance(service_data, dict) and "status" in service_data:
                statuses.append(service_data["status"])

        for system_data in health_data.get("system", {}).values():
            if isinstance(system_data, dict) and "status" in system_data:
                statuses.append(system_data["status"])

        performance = health_data.get("performance", {})
        if "status" in performance:
            statuses.append(performance["status"])

        # Determine overall status
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def get_quick_status(self) -> Dict[str, Any]:
        """Get a quick health status without detailed checks."""
        if (
            self.last_check_result
            and self.last_check_time
            and time.time() - self.last_check_time < 60
        ):  # Use cached result if less than 1 minute old

            return {
                "status": self.last_check_result["overall_status"],
                "timestamp": self.last_check_result["timestamp"],
                "cached": True,
                "uptime_seconds": time.time() - self.system_monitor.start_time,
            }

        # Run a quick health check without detailed system info
        try:
            result = self.run_health_check(include_detailed=False)
            return {
                "status": result["overall_status"],
                "timestamp": result["timestamp"],
                "cached": False,
                "uptime_seconds": result["application"]["uptime_seconds"],
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN,
                "timestamp": datetime.now().isoformat(),
                "cached": False,
                "error": str(e),
                "uptime_seconds": time.time() - self.system_monitor.start_time,
            }


# Global health checker instance
_health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    return _health_checker


def run_health_check() -> Dict[str, Any]:
    """Run a comprehensive health check."""
    return get_health_checker().run_health_check()


def get_quick_health_status() -> Dict[str, Any]:
    """Get a quick health status."""
    return get_health_checker().get_quick_status()


if __name__ == "__main__":
    # Test health check system
    print("Health Check System Test")
    print("=" * 50)

    checker = get_health_checker()

    # Run quick health check
    print("Running health check...")
    health_data = checker.run_health_check()

    print(f"Overall Status: {health_data['overall_status']}")
    print(f"Check Duration: {health_data['check_duration_ms']}ms")
    print(f"Services Checked: {len(health_data.get('services', {}))}")
    print(f"Uptime: {health_data['application']['uptime_seconds']:.1f}s")

    # Print service statuses
    print("\nService Status:")
    for service_name, service_data in health_data.get("services", {}).items():
        if isinstance(service_data, dict) and "status" in service_data:
            print(f"  {service_name}: {service_data['status']}")

    print("\n✓ Health check system ready!")
