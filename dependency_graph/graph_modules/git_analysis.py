"""
Git Analysis Module
==================

Analyzes git history to provide insights into code change patterns,
file modification frequency, and development hotspots.

Key Features:
- Change frequency analysis (how often files change)
- Churn analysis (lines added/removed over time)
- Hotspot detection (frequently modified files)
- Author contribution patterns
- Commit timeline analysis

Dependencies:
- subprocess: For executing git commands
- datetime: For timestamp handling
- pathlib: For path operations
"""

import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class GitAnalyzer:
    """Analyzes git repository for change patterns and file modification frequency."""

    def __init__(self, repo_path: str = "."):
        """Initialize git analyzer for the specified repository."""
        self.repo_path = Path(repo_path).resolve()
        self.is_git_available = self._check_git_availability()

    def _check_git_availability(self) -> bool:
        """Check if git is available and if we're in a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def get_file_change_frequency(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """
        Analyze file change frequency over the specified number of days.

        Args:
            days: Number of days to look back in git history

        Returns:
            Dict with file paths as keys and change statistics as values
        """
        if not self.is_git_available:
            print("🚫 Git not available - skipping change frequency analysis")
            return {}

        try:
            # Get commit history for the specified period
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            cmd = [
                "git",
                "log",
                f"--since={since_date}",
                "--name-only",
                "--format=format:%H|%ad|%s",
                "--date=iso",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_path, timeout=30
            )

            if result.returncode != 0:
                print(f"🚫 Git log failed: {result.stderr}")
                return {}

            return self._parse_change_frequency(result.stdout, days)

        except subprocess.TimeoutExpired:
            print("🚫 Git analysis timed out")
            return {}
        except Exception as e:
            print(f"🚫 Error analyzing git history: {e}")
            return {}

    def _parse_change_frequency(
        self, git_output: str, days: int
    ) -> Dict[str, Dict[str, Any]]:
        """Parse git log output to extract file change statistics."""
        file_stats = {}
        commit_count = 0

        lines = git_output.strip().split("\n")
        current_commit = None
        current_date = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a commit header line
            if "|" in line and len(line.split("|")) >= 3:
                commit_parts = line.split("|")
                current_commit = commit_parts[0]
                current_date = commit_parts[1]
                commit_count += 1
                continue

            # This should be a file path
            if current_commit and line.endswith(".py"):
                # Normalize path separators for consistency
                file_path = line.replace("\\", "/")

                if file_path not in file_stats:
                    file_stats[file_path] = {
                        "change_count": 0,
                        "last_modified": None,
                        "first_modified": None,
                        "commits": [],
                    }

                file_stats[file_path]["change_count"] += 1
                file_stats[file_path]["commits"].append(
                    {"commit": current_commit, "date": current_date}
                )

                # Update first/last modified dates
                if file_stats[file_path]["last_modified"] is None:
                    file_stats[file_path]["last_modified"] = current_date

                file_stats[file_path]["first_modified"] = current_date

        # Calculate change frequency scores and classifications
        for file_path, stats in file_stats.items():
            stats["change_frequency_score"] = self._calculate_frequency_score(
                stats["change_count"], commit_count, days
            )
            stats["change_classification"] = self._classify_change_frequency(
                stats["change_frequency_score"]
            )

        return file_stats

    def _calculate_frequency_score(
        self, change_count: int, total_commits: int, days: int
    ) -> float:
        """Calculate a normalized frequency score (0-1) for file changes."""
        if total_commits == 0:
            return 0.0

        # Normalize by total commits to get percentage of commits affecting this file
        commit_percentage = change_count / total_commits

        # Normalize by time period (changes per day)
        changes_per_day = change_count / max(days, 1)

        # Combine both metrics, weighted towards commit percentage
        frequency_score = (commit_percentage * 0.7) + (
            min(changes_per_day / 2, 1.0) * 0.3
        )

        return min(frequency_score, 1.0)

    def _classify_change_frequency(self, score: float) -> str:
        """Classify change frequency based on score."""
        if score >= 0.7:
            return "very_high"
        elif score >= 0.5:
            return "high"
        elif score >= 0.3:
            return "medium"
        elif score >= 0.1:
            return "low"
        else:
            return "very_low"

    def get_file_churn_analysis(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """
        Analyze code churn (lines added/removed) for files.

        Args:
            days: Number of days to look back in git history

        Returns:
            Dict with file paths as keys and churn statistics as values
        """
        if not self.is_git_available:
            print("🚫 Git not available - skipping churn analysis")
            return {}

        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            cmd = [
                "git",
                "log",
                f"--since={since_date}",
                "--numstat",
                "--format=format:%H|%ad",
                "--date=iso",
                "--",
                "*.py",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.repo_path, timeout=30
            )

            if result.returncode != 0:
                print(f"🚫 Git numstat failed: {result.stderr}")
                return {}

            return self._parse_churn_analysis(result.stdout)

        except subprocess.TimeoutExpired:
            print("🚫 Git churn analysis timed out")
            return {}
        except Exception as e:
            print(f"🚫 Error analyzing git churn: {e}")
            return {}

    def _parse_churn_analysis(self, git_output: str) -> Dict[str, Dict[str, Any]]:
        """Parse git numstat output to extract churn statistics."""
        file_churn = {}

        lines = git_output.strip().split("\n")
        current_commit = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a commit header
            if "|" in line:
                current_commit = line.split("|")[0]
                continue

            # Parse numstat line: additions, deletions, filename
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    additions = int(parts[0]) if parts[0] != "-" else 0
                    deletions = int(parts[1]) if parts[1] != "-" else 0
                    file_path = parts[2].replace("\\", "/")

                    if file_path.endswith(".py"):
                        if file_path not in file_churn:
                            file_churn[file_path] = {
                                "total_additions": 0,
                                "total_deletions": 0,
                                "total_churn": 0,
                                "commit_count": 0,
                            }

                        file_churn[file_path]["total_additions"] += additions
                        file_churn[file_path]["total_deletions"] += deletions
                        file_churn[file_path]["total_churn"] += additions + deletions
                        file_churn[file_path]["commit_count"] += 1

                except (ValueError, IndexError):
                    # Skip malformed lines
                    continue

        # Calculate churn metrics
        for file_path, stats in file_churn.items():
            if stats["commit_count"] > 0:
                stats["avg_churn_per_commit"] = (
                    stats["total_churn"] / stats["commit_count"]
                )
                stats["churn_classification"] = self._classify_churn(
                    stats["total_churn"]
                )
            else:
                stats["avg_churn_per_commit"] = 0
                stats["churn_classification"] = "none"

        return file_churn

    def _classify_churn(self, total_churn: int) -> str:
        """Classify churn level based on total lines changed."""
        if total_churn >= 1000:
            return "very_high"
        elif total_churn >= 500:
            return "high"
        elif total_churn >= 100:
            return "medium"
        elif total_churn >= 10:
            return "low"
        else:
            return "very_low"

    def get_combined_analysis(self, days: int = 30) -> Dict[str, Any]:
        """
        Get combined git analysis including both frequency and churn data.

        Args:
            days: Number of days to look back in git history

        Returns:
            Combined analysis results
        """
        print(f"🔄 Analyzing git history for the last {days} days...")

        frequency_data = self.get_file_change_frequency(days)
        churn_data = self.get_file_churn_analysis(days)

        # Combine the data
        combined_data = {}
        all_files = set(frequency_data.keys()) | set(churn_data.keys())

        for file_path in all_files:
            combined_data[file_path] = {
                **frequency_data.get(file_path, {}),
                **churn_data.get(file_path, {}),
                "hotspot_score": self._calculate_hotspot_score(
                    frequency_data.get(file_path, {}), churn_data.get(file_path, {})
                ),
            }

        analysis_summary = {
            "total_files_analyzed": len(combined_data),
            "analysis_period_days": days,
            "git_available": self.is_git_available,
            "hotspots": self._identify_hotspots(combined_data),
            "stable_files": self._identify_stable_files(combined_data),
            "file_data": combined_data,
        }

        print(
            f"✅ Git analysis complete - found {len(combined_data)} files with changes"
        )
        return analysis_summary

    def _calculate_hotspot_score(self, frequency_data: Dict, churn_data: Dict) -> float:
        """Calculate a combined hotspot score from frequency and churn data."""
        frequency_score = frequency_data.get("change_frequency_score", 0.0)
        churn_score = min(
            churn_data.get("total_churn", 0) / 1000.0, 1.0
        )  # Normalize churn

        # Weight frequency higher than churn for hotspot detection
        hotspot_score = (frequency_score * 0.7) + (churn_score * 0.3)
        return min(hotspot_score, 1.0)

    def _identify_hotspots(self, combined_data: Dict) -> List[Dict[str, Any]]:
        """Identify development hotspots (frequently changing files)."""
        hotspots = []

        for file_path, data in combined_data.items():
            hotspot_score = data.get("hotspot_score", 0.0)
            if hotspot_score >= 0.5:  # High hotspot threshold
                hotspots.append(
                    {
                        "file_path": file_path,
                        "hotspot_score": hotspot_score,
                        "change_count": data.get("change_count", 0),
                        "total_churn": data.get("total_churn", 0),
                        "classification": "hotspot",
                    }
                )

        return sorted(hotspots, key=lambda x: x["hotspot_score"], reverse=True)

    def _identify_stable_files(self, combined_data: Dict) -> List[Dict[str, Any]]:
        """Identify stable files (rarely changing)."""
        stable_files = []

        for file_path, data in combined_data.items():
            hotspot_score = data.get("hotspot_score", 0.0)
            if hotspot_score <= 0.1:  # Low change threshold
                stable_files.append(
                    {
                        "file_path": file_path,
                        "hotspot_score": hotspot_score,
                        "change_count": data.get("change_count", 0),
                        "classification": "stable",
                    }
                )

        return sorted(stable_files, key=lambda x: x["hotspot_score"])
