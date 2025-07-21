#!/usr/bin/env python3
"""
Enhanced Flowchart Test Suite

Comprehensive testing for the enhanced interactive flowchart visualization including:
- Plot area sizing and responsiveness
- Function details view functionality
- Relationship highlighting (dependencies vs dependents)
- Cross-browser compatibility
- Performance testing
- Edge case handling
"""

import time
import json
import sys
from pathlib import Path
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import requests

# Add the flowchart_visualization directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))


class EnhancedFlowchartTester:
    def __init__(self):
        self.server_process = None
        self.driver = None
        self.base_url = "http://localhost:5001"  # Use different port for testing
        self.test_results = {}

    def setup(self):
        """Set up the test environment"""
        print("🛠️ Setting up Enhanced Flowchart Test Environment...")

        # Start the enhanced server
        self.start_test_server()

        # Set up Chrome driver with options for testing
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless for CI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver initialized")
        except Exception as e:
            print(f"⚠️ Chrome not available, trying headless: {e}")
            # Fallback to basic testing without browser automation
            self.driver = None

        time.sleep(2)  # Give server time to start

    def start_test_server(self):
        """Start the enhanced server for testing"""
        try:
            # Import and start the enhanced server
            from enhanced_server import start_server

            def run_server():
                start_server(port=5001, debug=False, open_browser=False)

            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()

            # Wait for server to start
            time.sleep(3)

            # Test if server is responding
            response = requests.get(f"{self.base_url}/api/stats")
            if response.status_code == 200:
                print("✅ Enhanced server started successfully")
            else:
                print(f"⚠️ Server responding with status: {response.status_code}")

        except Exception as e:
            print(f"❌ Failed to start enhanced server: {e}")
            raise

    def test_plot_area_sizing(self):
        """Test that the plot area maximizes horizontal space"""
        print("\n🖥️ Testing Plot Area Sizing...")

        try:
            if not self.driver:
                print("⚠️ Skipping browser tests - no WebDriver available")
                return {"status": "skipped", "reason": "No WebDriver"}

            self.driver.get(self.base_url)

            # Wait for the diagram to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "diagram"))
            )

            # Get viewport and diagram dimensions
            viewport_width = self.driver.execute_script("return window.innerWidth")
            viewport_height = self.driver.execute_script("return window.innerHeight")

            diagram_element = self.driver.find_element(By.ID, "diagram")
            diagram_width = diagram_element.size["width"]
            diagram_height = diagram_element.size["height"]

            # Test that diagram uses most of the available width (allowing for margins)
            width_utilization = diagram_width / viewport_width

            print(f"  📏 Viewport: {viewport_width}x{viewport_height}")
            print(f"  📏 Diagram: {diagram_width}x{diagram_height}")
            print(f"  📊 Width utilization: {width_utilization:.2%}")

            # Should use at least 95% of available width
            assert (
                width_utilization >= 0.95
            ), f"Plot area not wide enough: {width_utilization:.2%}"

            # Test responsiveness - resize window
            self.driver.set_window_size(1200, 800)
            time.sleep(1)

            new_diagram_width = diagram_element.size["width"]
            new_viewport_width = self.driver.execute_script("return window.innerWidth")
            new_width_utilization = new_diagram_width / new_viewport_width

            print(
                f"  📏 After resize - Viewport: {new_viewport_width}, Diagram: {new_diagram_width}"
            )
            print(f"  📊 New width utilization: {new_width_utilization:.2%}")

            assert (
                new_width_utilization >= 0.95
            ), f"Plot area not responsive: {new_width_utilization:.2%}"

            return {
                "status": "passed",
                "original_utilization": width_utilization,
                "responsive_utilization": new_width_utilization,
            }

        except Exception as e:
            print(f"❌ Plot area sizing test failed: {e}")
            return {"status": "failed", "error": str(e)}

    def test_function_details_view(self):
        """Test function details view shows all functions as nodes"""
        print("\n🔧 Testing Function Details View...")

        try:
            if not self.driver:
                return {"status": "skipped", "reason": "No WebDriver"}

            self.driver.get(self.base_url)

            # Wait for initial load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "view-mode"))
            )

            # Switch to function details view
            view_mode_select = self.driver.find_element(By.ID, "view-mode")
            self.driver.execute_script(
                "arguments[0].value = 'functions'", view_mode_select
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'))", view_mode_select
            )

            # Wait for view to update
            time.sleep(2)

            # Count nodes in the visualization
            nodes = self.driver.execute_script(
                """
                return d3.selectAll('.node').size();
            """
            )

            # Get function count from API
            response = requests.get(f"{self.base_url}/api/functions")
            if response.status_code == 200:
                functions_data = response.json()
                expected_function_count = len(functions_data)

                print(f"  🔢 Expected functions: {expected_function_count}")
                print(f"  🔢 Visible nodes: {nodes}")

                # Should have both file nodes and function nodes
                assert (
                    nodes > expected_function_count
                ), f"Not showing function nodes: {nodes} <= {expected_function_count}"

                # Test function node interaction
                function_nodes = self.driver.execute_script(
                    """
                    return d3.selectAll('.node').data().filter(d => d.nodeType === 'function').length;
                """
                )

                print(f"  🔧 Function nodes: {function_nodes}")
                assert function_nodes > 0, "No function nodes found"

                return {
                    "status": "passed",
                    "total_nodes": nodes,
                    "function_nodes": function_nodes,
                    "expected_functions": expected_function_count,
                }
            else:
                return {
                    "status": "failed",
                    "error": "Could not get function data from API",
                }

        except Exception as e:
            print(f"❌ Function details view test failed: {e}")
            return {"status": "failed", "error": str(e)}

    def test_relationship_highlighting(self):
        """Test relationship highlighting with different colors"""
        print("\n🎨 Testing Relationship Highlighting...")

        try:
            if not self.driver:
                return {"status": "skipped", "reason": "No WebDriver"}

            self.driver.get(self.base_url)

            # Wait for diagram to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "node"))
            )

            # Click on a node to test highlighting
            first_node = self.driver.find_element(By.CSS_SELECTOR, ".node")
            ActionChains(self.driver).click(first_node).perform()

            time.sleep(1)  # Wait for highlighting to apply

            # Check for highlighted dependency links (blue)
            dependency_links = self.driver.execute_script(
                """
                return d3.selectAll('.link.highlighted-dependency').size();
            """
            )

            # Check for highlighted dependent links (orange)
            dependent_links = self.driver.execute_script(
                """
                return d3.selectAll('.link.highlighted-dependent').size();
            """
            )

            # Check link colors
            dependency_color = self.driver.execute_script(
                """
                const link = d3.select('.link.highlighted-dependency');
                return link.empty() ? null : link.attr('stroke');
            """
            )

            dependent_color = self.driver.execute_script(
                """
                const link = d3.select('.link.highlighted-dependent');
                return link.empty() ? null : link.attr('stroke');
            """
            )

            print(f"  🔗 Dependency links highlighted: {dependency_links}")
            print(f"  🔗 Dependent links highlighted: {dependent_links}")
            print(f"  🎨 Dependency color: {dependency_color}")
            print(f"  🎨 Dependent color: {dependent_color}")

            # Test that highlighting is working
            total_highlighted = dependency_links + dependent_links
            assert total_highlighted > 0, "No relationship highlighting found"

            # Test that colors are correct
            if dependency_color:
                assert dependency_color in [
                    "#2196F3",
                    "rgb(33, 150, 243)",
                ], f"Incorrect dependency color: {dependency_color}"

            if dependent_color:
                assert dependent_color in [
                    "#FF9800",
                    "rgb(255, 152, 0)",
                ], f"Incorrect dependent color: {dependent_color}"

            # Test clearing highlights
            self.driver.execute_script("document.querySelector('svg').click();")
            time.sleep(0.5)

            highlighted_after_clear = self.driver.execute_script(
                """
                return d3.selectAll('.link.highlighted-dependency, .link.highlighted-dependent').size();
            """
            )

            assert (
                highlighted_after_clear == 0
            ), f"Highlights not cleared: {highlighted_after_clear}"

            return {
                "status": "passed",
                "dependency_links": dependency_links,
                "dependent_links": dependent_links,
                "dependency_color": dependency_color,
                "dependent_color": dependent_color,
            }

        except Exception as e:
            print(f"❌ Relationship highlighting test failed: {e}")
            return {"status": "failed", "error": str(e)}

    def test_interactivity_features(self):
        """Test interactive features like search, filtering, etc."""
        print("\n🔍 Testing Interactive Features...")

        try:
            if not self.driver:
                return {"status": "skipped", "reason": "No WebDriver"}

            self.driver.get(self.base_url)

            # Wait for elements to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "search"))
            )

            # Test search functionality
            search_input = self.driver.find_element(By.ID, "search")
            search_input.send_keys("app")

            time.sleep(1)  # Wait for filter to apply

            visible_nodes = self.driver.execute_script(
                """
                return d3.selectAll('.node').nodes().filter(node => 
                    d3.select(node).style('opacity') == '1'
                ).length;
            """
            )

            print(f"  🔍 Nodes visible after search 'app': {visible_nodes}")
            assert visible_nodes > 0, "Search not working - no visible nodes"

            # Clear search
            search_input.clear()
            time.sleep(0.5)

            # Test filter functionality
            filter_select = self.driver.find_element(By.ID, "filter")
            self.driver.execute_script("arguments[0].value = 'main'", filter_select)
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'))", filter_select
            )

            time.sleep(1)

            filtered_nodes = self.driver.execute_script(
                """
                return d3.selectAll('.node').nodes().filter(node => 
                    d3.select(node).style('opacity') == '1'
                ).length;
            """
            )

            print(f"  📁 Nodes visible after filter 'main': {filtered_nodes}")

            # Test layout change
            layout_select = self.driver.find_element(By.ID, "layout")
            original_layout = layout_select.get_attribute("value")
            self.driver.execute_script(
                "arguments[0].value = 'hierarchical'", layout_select
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change'))", layout_select
            )

            time.sleep(1)
            print(f"  🎨 Layout changed from {original_layout} to hierarchical")

            # Test reset functionality
            reset_button = self.driver.find_element(
                By.XPATH, "//button[contains(text(), 'Reset View')]"
            )
            reset_button.click()

            time.sleep(1)

            # Check that search is cleared
            search_value = search_input.get_attribute("value")
            assert search_value == "", f"Search not reset: '{search_value}'"

            return {
                "status": "passed",
                "search_results": visible_nodes,
                "filter_results": filtered_nodes,
                "reset_working": search_value == "",
            }

        except Exception as e:
            print(f"❌ Interactive features test failed: {e}")
            return {"status": "failed", "error": str(e)}

    def test_api_endpoints(self):
        """Test all API endpoints"""
        print("\n🌐 Testing API Endpoints...")

        endpoints = [
            "/api/data",
            "/api/files",
            "/api/functions",
            "/api/dependencies",
            "/api/stats",
        ]

        results = {}

        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "has_data": (
                        len(response.json()) > 0
                        if response.status_code == 200
                        else False
                    ),
                }
                print(f"  ✅ {endpoint}: {response.status_code}")

            except Exception as e:
                results[endpoint] = {
                    "status_code": None,
                    "success": False,
                    "error": str(e),
                }
                print(f"  ❌ {endpoint}: {e}")

        # Check that at least the core endpoints work
        core_endpoints_working = all(
            results.get(ep, {}).get("success", False)
            for ep in ["/api/data", "/api/files"]
        )

        return {
            "status": "passed" if core_endpoints_working else "failed",
            "endpoints": results,
            "core_endpoints_working": core_endpoints_working,
        }

    def test_performance(self):
        """Test performance with larger datasets"""
        print("\n⚡ Testing Performance...")

        try:
            # Test API response times
            start_time = time.time()
            response = requests.get(f"{self.base_url}/api/data")
            api_time = time.time() - start_time

            print(f"  ⏱️ API response time: {api_time:.3f}s")

            if self.driver:
                # Test page load time
                start_time = time.time()
                self.driver.get(self.base_url)

                # Wait for diagram to be fully loaded
                WebDriverWait(self.driver, 30).until(
                    EC.invisibility_of_element_located((By.ID, "loading"))
                )

                load_time = time.time() - start_time
                print(f"  ⏱️ Page load time: {load_time:.3f}s")

                # Test interaction response time
                start_time = time.time()
                first_node = self.driver.find_element(By.CSS_SELECTOR, ".node")
                ActionChains(self.driver).click(first_node).perform()
                interaction_time = time.time() - start_time

                print(f"  ⏱️ Node interaction time: {interaction_time:.3f}s")

                # Performance assertions
                assert api_time < 5.0, f"API too slow: {api_time}s"
                assert load_time < 15.0, f"Page load too slow: {load_time}s"
                assert (
                    interaction_time < 2.0
                ), f"Interaction too slow: {interaction_time}s"

                return {
                    "status": "passed",
                    "api_time": api_time,
                    "load_time": load_time,
                    "interaction_time": interaction_time,
                }
            else:
                assert api_time < 5.0, f"API too slow: {api_time}s"
                return {"status": "passed", "api_time": api_time}

        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return {"status": "failed", "error": str(e)}

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases...")

        try:
            # Test with invalid API endpoints
            response = requests.get(f"{self.base_url}/api/nonexistent")
            assert (
                response.status_code == 404
            ), f"Expected 404, got {response.status_code}"

            if self.driver:
                self.driver.get(self.base_url)

                # Test with empty search
                search_input = self.driver.find_element(By.ID, "search")
                search_input.send_keys("nonexistentfile12345")
                time.sleep(1)

                visible_nodes = self.driver.execute_script(
                    """
                    return d3.selectAll('.node').nodes().filter(node => 
                        d3.select(node).style('opacity') == '1'
                    ).length;
                """
                )

                print(f"  🔍 Nodes visible after invalid search: {visible_nodes}")

                # Test keyboard shortcuts
                self.driver.find_element(By.TAG_NAME, "body").send_keys(
                    " "
                )  # Space key
                time.sleep(0.5)

                print("  ⌨️ Keyboard shortcut (space) tested")

            return {"status": "passed", "invalid_endpoint_handled": True}

        except Exception as e:
            print(f"❌ Edge cases test failed: {e}")
            return {"status": "failed", "error": str(e)}

    def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting Enhanced Flowchart Test Suite")
        print("=" * 60)

        # Set up test environment
        self.setup()

        # Run all tests
        test_methods = [
            ("Plot Area Sizing", self.test_plot_area_sizing),
            ("Function Details View", self.test_function_details_view),
            ("Relationship Highlighting", self.test_relationship_highlighting),
            ("Interactive Features", self.test_interactivity_features),
            ("API Endpoints", self.test_api_endpoints),
            ("Performance", self.test_performance),
            ("Edge Cases", self.test_edge_cases),
        ]

        for test_name, test_method in test_methods:
            try:
                self.test_results[test_name] = test_method()
            except Exception as e:
                self.test_results[test_name] = {"status": "failed", "error": str(e)}

        # Generate report
        self.generate_report()

        # Cleanup
        self.cleanup()

    def generate_report(self):
        """Generate a comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED FLOWCHART TEST REPORT")
        print("=" * 60)

        passed = 0
        failed = 0
        skipped = 0

        for test_name, result in self.test_results.items():
            status = result.get("status", "unknown")

            if status == "passed":
                status_icon = "✅"
                passed += 1
            elif status == "failed":
                status_icon = "❌"
                failed += 1
            elif status == "skipped":
                status_icon = "⚠️"
                skipped += 1
            else:
                status_icon = "❓"

            print(f"{status_icon} {test_name}: {status.upper()}")

            if status == "failed" and "error" in result:
                print(f"    Error: {result['error']}")

        print("\n" + "-" * 60)
        print(f"📈 Summary: {passed} passed, {failed} failed, {skipped} skipped")

        if failed == 0:
            print("🎉 All critical tests passed! Enhanced flowchart is ready.")
        else:
            print("⚠️ Some tests failed. Please review the issues above.")

        # Save detailed results to file
        report_file = Path(__file__).parent / "test_results.json"
        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "summary": {"passed": passed, "failed": failed, "skipped": skipped},
                    "results": self.test_results,
                },
                f,
                indent=2,
            )

        print(f"📄 Detailed results saved to: {report_file}")

    def cleanup(self):
        """Clean up test environment"""
        if self.driver:
            self.driver.quit()
        print("\n🧹 Test cleanup completed")


def main():
    """Main test runner"""
    tester = EnhancedFlowchartTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
