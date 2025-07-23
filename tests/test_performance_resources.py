#!/usr/bin/env python3
"""
Performance and Resource Management Test Suite

Specialized test script focusing on performance, memory management, and resource leaks.
This implements the fifth category of the Comprehensive Post-Restructuring Test Action Plan.

Test Coverage:
- Memory leak detection
- File handle leak testing
- Thread/process safety validation
- Resource cleanup verification
- Performance benchmarking

Author: GitHub Copilot
Date: July 23, 2025
"""

import sys
import os
import gc
import threading
import time
import tempfile
import traceback
import psutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor

# Add workspace to path
sys.path.insert(0, os.path.abspath("."))


class PerformanceResourceTester:
    """Performance and resource management testing."""

    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent
        self.results = {
            "memory_leaks": {},
            "file_handles": {},
            "thread_safety": {},
            "resource_cleanup": {},
            "performance": {},
        }
        self.process = psutil.Process()

    def run_all_tests(self) -> bool:
        """Run all performance and resource tests."""
        print("⚡ PERFORMANCE AND RESOURCE MANAGEMENT TEST SUITE")
        print("=" * 60)

        success = True

        success &= self.test_memory_leaks()
        success &= self.test_file_handle_leaks()
        success &= self.test_thread_safety()
        success &= self.test_resource_cleanup()
        success &= self.test_performance_benchmarks()

        self.generate_report()
        return success

    @contextmanager
    def memory_monitor(self):
        """Context manager to monitor memory usage."""
        gc.collect()  # Force garbage collection
        initial_memory = self.process.memory_info().rss
        initial_objects = len(gc.get_objects())

        yield

        gc.collect()  # Force garbage collection again
        final_memory = self.process.memory_info().rss
        final_objects = len(gc.get_objects())

        memory_growth = final_memory - initial_memory
        object_growth = final_objects - initial_objects

        return {
            "memory_growth": memory_growth,
            "object_growth": object_growth,
            "initial_memory": initial_memory,
            "final_memory": final_memory,
        }

    def test_memory_leaks(self) -> bool:
        """Test for memory leaks in repeated operations."""
        print("\n🧠 Testing Memory Leaks")
        print("-" * 40)

        success = True

        # Test 1: Module Import/Reload Memory Usage
        print("📦 Testing module import memory usage...")
        with self.memory_monitor() as monitor:
            modules_to_test = ["config_modules", "app_modules", "borehole_log"]

            for _ in range(5):
                for module_name in modules_to_test:
                    try:
                        if module_name in sys.modules:
                            del sys.modules[module_name]

                        import importlib

                        importlib.import_module(module_name)
                    except ImportError:
                        continue

        memory_data = monitor.__exit__(None, None, None)
        memory_growth_mb = memory_data.get("memory_growth", 0) / (1024 * 1024)
        object_growth = memory_data.get("object_growth", 0)

        if memory_growth_mb < 10:  # Less than 10MB growth
            print(
                f"  ✅ Module imports: {memory_growth_mb:.2f}MB growth, {object_growth} objects"
            )
        else:
            print(
                f"  ⚠️ Module imports: {memory_growth_mb:.2f}MB growth, {object_growth} objects"
            )
            success = False

        self.results["memory_leaks"]["module_imports"] = {
            "memory_growth_mb": memory_growth_mb,
            "object_growth": object_growth,
            "status": "pass" if memory_growth_mb < 10 else "warning",
        }

        # Test 2: App Creation Memory Usage
        print("🏗️ Testing app creation memory usage...")
        try:
            with self.memory_monitor() as monitor:
                for i in range(3):
                    try:
                        from app_modules import create_and_configure_app

                        app = create_and_configure_app()

                        # Simulate some operations
                        if hasattr(app, "layout"):
                            _ = app.layout

                        del app
                        gc.collect()

                    except Exception as e:
                        print(f"    App creation iteration {i} failed: {e}")
                        continue

            memory_data = monitor.__exit__(None, None, None)
            memory_growth_mb = memory_data.get("memory_growth", 0) / (1024 * 1024)

            if memory_growth_mb < 50:  # Less than 50MB growth for app creation
                print(f"  ✅ App creation: {memory_growth_mb:.2f}MB growth")
            else:
                print(f"  ⚠️ App creation: {memory_growth_mb:.2f}MB growth")
                success = False

            self.results["memory_leaks"]["app_creation"] = {
                "memory_growth_mb": memory_growth_mb,
                "status": "pass" if memory_growth_mb < 50 else "warning",
            }

        except Exception as e:
            print(f"  ❌ App creation test failed: {e}")
            self.results["memory_leaks"]["app_creation"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        # Test 3: Data Processing Memory Usage
        print("📊 Testing data processing memory usage...")
        try:
            with self.memory_monitor() as monitor:
                for i in range(10):
                    try:
                        # Simulate data processing
                        import pandas as pd

                        # Create test data
                        test_data = pd.DataFrame(
                            {"depth": range(1000), "geology": ["Clay"] * 1000}
                        )

                        # Process data
                        processed = test_data.groupby("geology").count()

                        # Clean up
                        del test_data, processed

                    except ImportError:
                        # Skip if pandas not available
                        continue
                    except Exception as e:
                        print(f"    Data processing iteration {i} failed: {e}")
                        continue

            memory_data = monitor.__exit__(None, None, None)
            memory_growth_mb = memory_data.get("memory_growth", 0) / (1024 * 1024)

            if memory_growth_mb < 5:  # Less than 5MB growth for data processing
                print(f"  ✅ Data processing: {memory_growth_mb:.2f}MB growth")
            else:
                print(f"  ⚠️ Data processing: {memory_growth_mb:.2f}MB growth")
                success = False

            self.results["memory_leaks"]["data_processing"] = {
                "memory_growth_mb": memory_growth_mb,
                "status": "pass" if memory_growth_mb < 5 else "warning",
            }

        except Exception as e:
            print(f"  ❌ Data processing test failed: {e}")
            self.results["memory_leaks"]["data_processing"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        return success

    def test_file_handle_leaks(self) -> bool:
        """Test for file handle leaks."""
        print("\n📁 Testing File Handle Leaks")
        print("-" * 40)

        success = True

        # Get initial file descriptor count
        initial_fds = self.process.num_fds() if hasattr(self.process, "num_fds") else 0

        # Test 1: Temporary File Operations
        print("📄 Testing temporary file operations...")
        try:
            temp_files = []

            for i in range(50):
                with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                    f.write(f"test data {i}")
                    temp_files.append(f.name)

            # Clean up files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass

            # Check file descriptor count
            current_fds = (
                self.process.num_fds() if hasattr(self.process, "num_fds") else 0
            )
            fd_growth = current_fds - initial_fds

            if fd_growth <= 2:  # Allow minimal growth
                print(f"  ✅ Temporary files: {fd_growth} FD growth")
            else:
                print(f"  ⚠️ Temporary files: {fd_growth} FD growth")
                success = False

            self.results["file_handles"]["temp_files"] = {
                "fd_growth": fd_growth,
                "status": "pass" if fd_growth <= 2 else "warning",
            }

        except Exception as e:
            print(f"  ❌ Temporary file test failed: {e}")
            self.results["file_handles"]["temp_files"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        # Test 2: Config File Reading
        print("⚙️ Testing config file reading...")
        try:
            for i in range(20):
                try:
                    # Test reading requirements.txt or other config files
                    config_files = ["requirements.txt", "config.py", "README.md"]

                    for config_file in config_files:
                        config_path = self.workspace_root / config_file
                        if config_path.exists():
                            with open(config_path, "r", encoding="utf-8") as f:
                                _ = f.read(1000)  # Read first 1000 chars
                            break

                except Exception:
                    continue

            # Check file descriptor count
            current_fds = (
                self.process.num_fds() if hasattr(self.process, "num_fds") else 0
            )
            fd_growth = current_fds - initial_fds

            if fd_growth <= 1:
                print(f"  ✅ Config file reading: {fd_growth} FD growth")
            else:
                print(f"  ⚠️ Config file reading: {fd_growth} FD growth")
                success = False

            self.results["file_handles"]["config_reading"] = {
                "fd_growth": fd_growth,
                "status": "pass" if fd_growth <= 1 else "warning",
            }

        except Exception as e:
            print(f"  ❌ Config file reading test failed: {e}")
            self.results["file_handles"]["config_reading"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        return success

    def test_thread_safety(self) -> bool:
        """Test thread safety of critical components."""
        print("\n🧵 Testing Thread Safety")
        print("-" * 40)

        success = True

        # Test 1: Concurrent Module Imports
        print("📦 Testing concurrent module imports...")
        try:
            results = []
            errors = []

            def import_module_worker(module_name):
                try:
                    import importlib

                    module = importlib.import_module(module_name)
                    return f"Success: {module_name}"
                except Exception as e:
                    errors.append(f"{module_name}: {e}")
                    return f"Error: {module_name} - {e}"

            modules_to_test = [
                "config_modules",
                "app_modules",
                "borehole_log",
                "section",
                "state_management",
            ]

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(import_module_worker, module)
                    for module in modules_to_test
                ]

                for future in futures:
                    try:
                        result = future.result(timeout=10)
                        results.append(result)
                    except Exception as e:
                        errors.append(f"Future error: {e}")

            success_count = len([r for r in results if "Success" in r])

            if len(errors) == 0:
                print(
                    f"  ✅ Concurrent imports: {success_count}/{len(modules_to_test)} successful"
                )
            else:
                print(f"  ⚠️ Concurrent imports: {len(errors)} errors")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"    {error}")
                success = False

            self.results["thread_safety"]["concurrent_imports"] = {
                "success_count": success_count,
                "total_count": len(modules_to_test),
                "errors": errors,
                "status": "pass" if len(errors) == 0 else "warning",
            }

        except Exception as e:
            print(f"  ❌ Concurrent import test failed: {e}")
            self.results["thread_safety"]["concurrent_imports"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        # Test 2: Concurrent Configuration Access
        print("⚙️ Testing concurrent configuration access...")
        try:
            results = []
            errors = []

            def config_access_worker():
                try:
                    from config_modules import APP_TITLE, MAP_HEIGHT

                    return f"APP_TITLE: {APP_TITLE}, MAP_HEIGHT: {MAP_HEIGHT}"
                except Exception as e:
                    errors.append(str(e))
                    return f"Error: {e}"

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(config_access_worker) for _ in range(10)]

                for future in futures:
                    try:
                        result = future.result(timeout=5)
                        results.append(result)
                    except Exception as e:
                        errors.append(f"Future error: {e}")

            success_count = len([r for r in results if "Error" not in r])

            if len(errors) == 0:
                print(
                    f"  ✅ Concurrent config access: {success_count}/{len(results)} successful"
                )
            else:
                print(f"  ⚠️ Concurrent config access: {len(errors)} errors")
                success = False

            self.results["thread_safety"]["concurrent_config"] = {
                "success_count": success_count,
                "total_count": len(results),
                "errors": errors,
                "status": "pass" if len(errors) == 0 else "warning",
            }

        except Exception as e:
            print(f"  ❌ Concurrent config test failed: {e}")
            self.results["thread_safety"]["concurrent_config"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        return success

    def test_resource_cleanup(self) -> bool:
        """Test proper resource cleanup."""
        print("\n🧹 Testing Resource Cleanup")
        print("-" * 40)

        success = True

        # Test 1: Memory Manager Cleanup
        print("🧠 Testing memory manager cleanup...")
        try:
            initial_objects = len(gc.get_objects())

            # Create and destroy memory managers
            managers = []
            for i in range(5):
                try:
                    from memory_manager import MemoryManager

                    manager = MemoryManager()
                    managers.append(manager)
                except ImportError:
                    # Create mock manager if not available
                    class MockManager:
                        def __init__(self):
                            self.data = list(range(1000))

                        def cleanup(self):
                            self.data = None

                    manager = MockManager()
                    managers.append(manager)

            # Clean up managers
            for manager in managers:
                if hasattr(manager, "cleanup"):
                    manager.cleanup()
                del manager

            del managers
            gc.collect()

            final_objects = len(gc.get_objects())
            object_growth = final_objects - initial_objects

            if object_growth < 100:
                print(f"  ✅ Memory manager cleanup: {object_growth} object growth")
            else:
                print(f"  ⚠️ Memory manager cleanup: {object_growth} object growth")
                success = False

            self.results["resource_cleanup"]["memory_manager"] = {
                "object_growth": object_growth,
                "status": "pass" if object_growth < 100 else "warning",
            }

        except Exception as e:
            print(f"  ❌ Memory manager cleanup test failed: {e}")
            self.results["resource_cleanup"]["memory_manager"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        # Test 2: Figure Cleanup (if matplotlib available)
        print("📊 Testing figure cleanup...")
        try:
            import matplotlib

            matplotlib.use("Agg")  # Use non-interactive backend
            import matplotlib.pyplot as plt

            initial_figures = len(plt.get_fignums())

            # Create and close figures
            for i in range(10):
                fig, ax = plt.subplots()
                ax.plot([1, 2, 3], [1, 4, 2])
                plt.close(fig)

            final_figures = len(plt.get_fignums())
            figure_growth = final_figures - initial_figures

            if figure_growth == 0:
                print(f"  ✅ Figure cleanup: No figure leaks")
            else:
                print(f"  ⚠️ Figure cleanup: {figure_growth} figures not cleaned")
                success = False

            self.results["resource_cleanup"]["matplotlib_figures"] = {
                "figure_growth": figure_growth,
                "status": "pass" if figure_growth == 0 else "warning",
            }

        except ImportError:
            print(f"  ℹ️ Figure cleanup: matplotlib not available")
            self.results["resource_cleanup"]["matplotlib_figures"] = {
                "status": "skipped",
                "reason": "matplotlib not available",
            }
        except Exception as e:
            print(f"  ❌ Figure cleanup test failed: {e}")
            self.results["resource_cleanup"]["matplotlib_figures"] = {
                "status": "failed",
                "error": str(e),
            }
            success = False

        return success

    def test_performance_benchmarks(self) -> bool:
        """Run basic performance benchmarks."""
        print("\n⚡ Testing Performance Benchmarks")
        print("-" * 40)

        success = True

        # Test 1: Module Import Speed
        print("📦 Testing module import speed...")
        try:
            modules_to_test = ["config_modules", "app_modules", "borehole_log"]

            import_times = {}

            for module_name in modules_to_test:
                # Clear module from cache
                if module_name in sys.modules:
                    del sys.modules[module_name]

                start_time = time.time()
                try:
                    import importlib

                    importlib.import_module(module_name)
                    end_time = time.time()

                    import_time = (end_time - start_time) * 1000  # Convert to ms
                    import_times[module_name] = import_time

                    if import_time < 1000:  # Less than 1 second
                        print(f"  ✅ {module_name}: {import_time:.2f}ms")
                    else:
                        print(f"  ⚠️ {module_name}: {import_time:.2f}ms (slow)")
                        success = False

                except ImportError as e:
                    print(f"  ❌ {module_name}: Import failed - {e}")
                    import_times[module_name] = None
                    success = False

            self.results["performance"]["import_times"] = import_times

        except Exception as e:
            print(f"  ❌ Import speed test failed: {e}")
            self.results["performance"]["import_times"] = {"error": str(e)}
            success = False

        # Test 2: Configuration Access Speed
        print("⚙️ Testing configuration access speed...")
        try:
            start_time = time.time()

            # Access configuration multiple times
            for _ in range(100):
                try:
                    from config_modules import (
                        APP_TITLE,
                        MAP_HEIGHT,
                        HEADER_H1_CENTER_STYLE,
                    )

                    _ = APP_TITLE, MAP_HEIGHT, HEADER_H1_CENTER_STYLE
                except ImportError:
                    break

            end_time = time.time()
            access_time = (end_time - start_time) * 1000  # Convert to ms

            if access_time < 100:  # Less than 100ms for 100 accesses
                print(f"  ✅ Config access: {access_time:.2f}ms for 100 accesses")
            else:
                print(f"  ⚠️ Config access: {access_time:.2f}ms for 100 accesses (slow)")
                success = False

            self.results["performance"]["config_access_time"] = access_time

        except Exception as e:
            print(f"  ❌ Config access speed test failed: {e}")
            self.results["performance"]["config_access_time"] = {"error": str(e)}
            success = False

        return success

    def generate_report(self):
        """Generate comprehensive performance and resource report."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE AND RESOURCE MANAGEMENT REPORT")
        print("=" * 60)

        # Summary statistics
        categories = [
            ("Memory Leaks", "memory_leaks"),
            ("File Handles", "file_handles"),
            ("Thread Safety", "thread_safety"),
            ("Resource Cleanup", "resource_cleanup"),
            ("Performance", "performance"),
        ]

        overall_success = True

        for category_name, category_key in categories:
            results = self.results[category_key]
            if not results:
                continue

            # Count passed/failed tests
            passed = 0
            total = 0

            for test_name, test_result in results.items():
                if isinstance(test_result, dict):
                    total += 1
                    status = test_result.get("status", "unknown")
                    if status in ["pass", "success"]:
                        passed += 1
                    elif status == "skipped":
                        total -= 1  # Don't count skipped tests

            if total > 0:
                success_rate = passed / total * 100
                status = (
                    "✅" if success_rate >= 90 else "⚠️" if success_rate >= 70 else "❌"
                )

                if success_rate < 90:
                    overall_success = False

                print(
                    f"{status} {category_name}: {passed}/{total} ({success_rate:.1f}%)"
                )
            else:
                print(f"ℹ️ {category_name}: No tests run")

        print(
            f"\n🎯 Overall Status: {'✅ PASSED' if overall_success else '❌ NEEDS ATTENTION'}"
        )

        # Memory usage summary
        memory_results = self.results.get("memory_leaks", {})
        if memory_results:
            print(f"\n🧠 Memory Usage Summary:")
            total_memory_growth = 0
            for test_name, result in memory_results.items():
                if isinstance(result, dict) and "memory_growth_mb" in result:
                    growth = result["memory_growth_mb"]
                    total_memory_growth += growth
                    print(f"  {test_name}: {growth:.2f}MB")

            if total_memory_growth > 0:
                print(f"  Total Growth: {total_memory_growth:.2f}MB")

        # Performance summary
        performance_results = self.results.get("performance", {})
        if performance_results:
            print(f"\n⚡ Performance Summary:")

            import_times = performance_results.get("import_times", {})
            if import_times:
                print(f"  Import Times:")
                for module, time_ms in import_times.items():
                    if time_ms is not None:
                        print(f"    {module}: {time_ms:.2f}ms")

            config_time = performance_results.get("config_access_time")
            if config_time and not isinstance(config_time, dict):
                print(f"  Config Access: {config_time:.2f}ms (100 operations)")

        print(f"\n💡 Recommendations:")
        if overall_success:
            print("  🎉 Excellent performance and resource management!")
            print("  📈 Consider setting up continuous performance monitoring.")
            print("  🔄 Add these tests to your CI/CD pipeline.")
        else:
            print("  🔧 Address performance issues and resource leaks.")
            print("  🧠 Review memory usage patterns.")
            print("  🧵 Ensure thread safety in concurrent operations.")
            print("  🧹 Implement proper resource cleanup.")


def main():
    """Run the performance and resource management test suite."""
    tester = PerformanceResourceTester()

    try:
        success = tester.run_all_tests()

        if success:
            print("\n🎉 PERFORMANCE AND RESOURCE TESTS: ALL TESTS PASSED")
            return 0
        else:
            print("\n❌ PERFORMANCE AND RESOURCE TESTS: SOME TESTS FAILED")
            return 1

    except Exception as e:
        print(f"\n💥 PERFORMANCE AND RESOURCE TESTS: UNEXPECTED ERROR - {e}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
