#!/usr/bin/env python3
"""
Secrets Detection Tool for MCP Server
Integrates Gitleaks and TruffleHog for comprehensive secret scanning
"""

import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecretsDetector:
    """Main class for secrets detection using Gitleaks and TruffleHog"""
    
    def __init__(self):
        self.scan_history = []
        self.config = self._load_default_config()
        
    def _load_default_config(self) -> Dict:
        """Load default configuration for scanning"""
        return {
            "gitleaks": {
                "enabled": True,
                "timeout": 300,  # 5 minutes
                "output_format": "json",
                "verbose": False
            },
            "trufflehog": {
                "enabled": True,
                "timeout": 120,  # 2 minutes
                "max_depth": 10,
                "only_verified": False
            },
            "scan_rules": {
                "ignore_patterns": [
                    "*.log", "*.tmp", "*.cache", "node_modules/*", 
                    ".git/*", "*.pyc", "__pycache__/*"
                ],
                "severity_levels": ["high", "medium", "low"],
                "custom_patterns": []
            }
        }
    
    def _check_tool_availability(self, tool_name: str) -> bool:
        """Check if a security tool is available in the system"""
        try:
            result = subprocess.run([tool_name, "--version"], 
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _parse_gitleaks_output(self, output: str) -> List[Dict]:
        """Parse Gitleaks human-readable output into structured format"""
        findings = []
        current_finding = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('Finding:'):
                if current_finding:
                    findings.append(current_finding)
                current_finding = {'rule_id': 'unknown'}
                current_finding['description'] = line.replace('Finding:', '').strip()
            elif line.startswith('Secret:'):
                current_finding['secret'] = line.replace('Secret:', '').strip()
            elif line.startswith('RuleID:'):
                current_finding['rule_id'] = line.replace('RuleID:', '').strip()
            elif line.startswith('File:'):
                current_finding['file'] = line.replace('File:', '').strip()
            elif line.startswith('Line:'):
                try:
                    current_finding['line'] = int(line.replace('Line:', '').strip())
                except ValueError:
                    current_finding['line'] = 0
            elif line.startswith('Commit:'):
                current_finding['commit'] = line.replace('Commit:', '').strip()
        
        if current_finding:
            findings.append(current_finding)
        
        return findings
    
    def _run_gitleaks_scan(self, target_path: str, is_repo: bool = True) -> Dict:
        """Run Gitleaks scan on repository or directory"""
        if not self._check_tool_availability("gitleaks"):
            return {
                "success": False,
                "error": "Gitleaks not found. Please install it first.",
                "tool": "gitleaks"
            }
        
        try:
            cmd = [
                "gitleaks", "detect",
                "--source", target_path,
                "--report-format", self.config["gitleaks"]["output_format"],
                "--verbose"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["gitleaks"]["timeout"] + 30
            )
            
            # Gitleaks returns exit code 1 when secrets are found (this is normal)
            if result.returncode in [0, 1]:
                # Parse JSON output from stdout
                try:
                    findings = json.loads(result.stdout) if result.stdout.strip() else []
                    return {
                        "success": True,
                        "tool": "gitleaks",
                        "findings": findings,
                        "count": len(findings),
                        "output": result.stdout,
                        "secrets_found": result.returncode == 1
                    }
                except json.JSONDecodeError:
                    # If no JSON output, try to parse stderr for findings
                    if result.stderr and "Finding:" in result.stderr:
                        # Parse the human-readable output
                        findings = self._parse_gitleaks_output(result.stderr)
                        return {
                            "success": True,
                            "tool": "gitleaks",
                            "findings": findings,
                            "count": len(findings),
                            "output": result.stderr,
                            "secrets_found": True
                        }
                    else:
                        return {
                            "success": True,
                            "tool": "gitleaks",
                            "findings": [],
                            "count": 0,
                            "output": result.stdout,
                            "warning": "Could not parse JSON output"
                        }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "tool": "gitleaks",
                    "return_code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Gitleaks scan timed out",
                "tool": "gitleaks"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Gitleaks scan failed: {str(e)}",
                "tool": "gitleaks"
            }
    
    def _run_trufflehog_scan(self, target_path: str) -> Dict:
        """Run TruffleHog scan on files or directory"""
        if not self._check_tool_availability("trufflehog"):
            return {
                "success": False,
                "error": "TruffleHog not found. Please install it first.",
                "tool": "trufflehog"
            }
        
        try:
            cmd = [
                "trufflehog", "filesystem",
                "--json",
                target_path
            ]
            
            if self.config["trufflehog"]["only_verified"]:
                cmd.append("--no-verification")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config["trufflehog"]["timeout"] + 30
            )
            
            if result.returncode == 0:
                # Parse JSON output (TruffleHog outputs one JSON object per line)
                findings = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            finding = json.loads(line)
                            # Only include actual findings, not log messages
                            if "SourceMetadata" in finding and "DetectorType" in finding:
                                findings.append(finding)
                        except json.JSONDecodeError:
                            continue
                
                return {
                    "success": True,
                    "tool": "trufflehog",
                    "findings": findings,
                    "count": len(findings),
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "tool": "trufflehog",
                    "return_code": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "TruffleHog scan timed out",
                "tool": "trufflehog"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"TruffleHog scan failed: {str(e)}",
                "tool": "trufflehog"
            }
    
    def scan_repository(self, repo_path: str, use_gitleaks: bool = True, 
                       use_trufflehog: bool = True) -> Dict:
        """
        Scan a Git repository for secrets
        
        Args:
            repo_path: Path to the repository
            use_gitleaks: Whether to use Gitleaks for scanning
            use_trufflehog: Whether to use TruffleHog for scanning
            
        Returns:
            Dict containing scan results
        """
        if not os.path.exists(repo_path):
            return {
                "success": False,
                "error": f"Repository path does not exist: {repo_path}"
            }
        
        # Check if it's a Git repository
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.exists(git_dir):
            return {
                "success": False,
                "error": f"Not a Git repository: {repo_path}"
            }
        
        scan_start = datetime.now()
        results = {
            "target": repo_path,
            "scan_type": "repository",
            "start_time": scan_start.isoformat(),
            "tools_used": [],
            "findings": [],
            "summary": {}
        }
        
        # Run Gitleaks scan
        if use_gitleaks and self.config["gitleaks"]["enabled"]:
            logger.info(f"Running Gitleaks scan on {repo_path}")
            gitleaks_result = self._run_gitleaks_scan(repo_path, is_repo=True)
            results["tools_used"].append("gitleaks")
            results["findings"].extend(gitleaks_result.get("findings", []))
            
            if gitleaks_result["success"]:
                results["summary"]["gitleaks"] = {
                    "status": "success",
                    "findings_count": gitleaks_result["count"]
                }
            else:
                results["summary"]["gitleaks"] = {
                    "status": "failed",
                    "error": gitleaks_result["error"]
                }
        
        # Run TruffleHog scan
        if use_trufflehog and self.config["trufflehog"]["enabled"]:
            logger.info(f"Running TruffleHog scan on {repo_path}")
            trufflehog_result = self._run_trufflehog_scan(repo_path)
            results["tools_used"].append("trufflehog")
            results["findings"].extend(trufflehog_result.get("findings", []))
            
            if trufflehog_result["success"]:
                results["summary"]["trufflehog"] = {
                    "status": "success",
                    "findings_count": trufflehog_result["count"]
                }
            else:
                results["summary"]["trufflehog"] = {
                    "status": "failed",
                    "error": trufflehog_result["error"]
                }
        
        # Calculate summary
        results["end_time"] = datetime.now().isoformat()
        results["duration"] = (datetime.now() - scan_start).total_seconds()
        results["total_findings"] = len(results["findings"])
        
        # Categorize findings by severity
        severity_counts = {"high": 0, "medium": 0, "low": 0, "unknown": 0}
        for finding in results["findings"]:
            # Map detector types to severity levels
            detector_type = finding.get("DetectorType", 0)
            detector_name = finding.get("DetectorName", "").lower()
            
            # High severity: API keys, private keys, database credentials
            if any(keyword in detector_name for keyword in ["api", "private", "secret", "password", "key"]):
                severity = "high"
            # Medium severity: connection strings, tokens
            elif any(keyword in detector_name for keyword in ["connection", "token", "stripe", "postgres", "mongodb"]):
                severity = "medium"
            # Low severity: URLs, general patterns
            elif any(keyword in detector_name for keyword in ["uri", "url"]):
                severity = "low"
            else:
                severity = "unknown"
            
            severity_counts[severity] += 1
            
            # Add severity to finding for consistency
            finding["severity"] = severity
        
        results["severity_summary"] = severity_counts
        
        # Store in history
        self.scan_history.append(results)
        
        # Normalize findings for consistent output
        normalized_findings = []
        for finding in results["findings"]:
            if "DetectorName" in finding:  # TruffleHog format
                normalized_finding = {
                    "rule_id": finding.get("DetectorName", "unknown"),
                    "severity": finding.get("severity", "unknown"),
                    "description": finding.get("DetectorDescription", "Unknown"),
                    "file": finding.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("file", "Unknown"),
                    "line": finding.get("SourceMetadata", {}).get("Data", {}).get("Filesystem", {}).get("line", 0),
                    "secret": finding.get("Raw", "Unknown"),
                    "context": finding.get("Raw", "Unknown"),
                    "tool": "trufflehog"
                }
            else:  # Gitleaks format
                normalized_finding = {
                    "rule_id": finding.get("rule_id", "unknown"),
                    "severity": finding.get("severity", "unknown"),
                    "description": finding.get("description", "Unknown"),
                    "file": finding.get("file", "Unknown"),
                    "line": finding.get("line", 0),
                    "secret": finding.get("secret", "Unknown"),
                    "context": finding.get("context", "Unknown"),
                    "tool": "gitleaks"
                }
            normalized_findings.append(normalized_finding)
        
        results["normalized_findings"] = normalized_findings
        
        return results
    
    def scan_file(self, file_path: str, use_trufflehog: bool = True) -> Dict:
        """
        Scan a single file for secrets
        
        Args:
            file_path: Path to the file to scan
            use_trufflehog: Whether to use TruffleHog for scanning
            
        Returns:
            Dict containing scan results
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File does not exist: {file_path}"
            }
        
        if not os.path.isfile(file_path):
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}"
            }
        
        scan_start = datetime.now()
        results = {
            "target": file_path,
            "scan_type": "file",
            "start_time": scan_start.isoformat(),
            "tools_used": [],
            "findings": [],
            "summary": {}
        }
        
        # Run TruffleHog scan on file
        if use_trufflehog and self.config["trufflehog"]["enabled"]:
            logger.info(f"Running TruffleHog scan on {file_path}")
            trufflehog_result = self._run_trufflehog_scan(file_path)
            results["tools_used"].append("trufflehog")
            results["findings"].extend(trufflehog_result.get("findings", []))
            
            if trufflehog_result["success"]:
                results["summary"]["trufflehog"] = {
                    "status": "success",
                    "findings_count": trufflehog_result["count"]
                }
            else:
                results["summary"]["trufflehog"] = {
                    "status": "failed",
                    "error": trufflehog_result["error"]
                }
        
        # Calculate summary
        results["end_time"] = datetime.now().isoformat()
        results["duration"] = (datetime.now() - scan_start).total_seconds()
        results["total_findings"] = len(results["findings"])
        
        # Store in history
        self.scan_history.append(results)
        
        return results
    
    def scan_directory(self, dir_path: str, recursive: bool = True, 
                      use_trufflehog: bool = True) -> Dict:
        """
        Scan a directory for secrets
        
        Args:
            dir_path: Path to the directory to scan
            recursive: Whether to scan subdirectories
            use_trufflehog: Whether to use TruffleHog for scanning
            
        Returns:
            Dict containing scan results
        """
        if not os.path.exists(dir_path):
            return {
                "success": False,
                "error": f"Directory does not exist: {dir_path}"
            }
        
        if not os.path.isdir(dir_path):
            return {
                "success": False,
                "error": f"Path is not a directory: {dir_path}"
            }
        
        scan_start = datetime.now()
        results = {
            "target": dir_path,
            "scan_type": "directory",
            "recursive": recursive,
            "start_time": scan_start.isoformat(),
            "tools_used": [],
            "findings": [],
            "summary": {}
        }
        
        # Run TruffleHog scan on directory
        if use_trufflehog and self.config["trufflehog"]["enabled"]:
            logger.info(f"Running TruffleHog scan on {dir_path}")
            trufflehog_result = self._run_trufflehog_scan(dir_path)
            results["tools_used"].append("trufflehog")
            results["findings"].extend(trufflehog_result.get("findings", []))
            
            if trufflehog_result["success"]:
                results["summary"]["trufflehog"] = {
                    "status": "success",
                    "findings_count": trufflehog_result["count"]
                }
            else:
                results["summary"]["trufflehog"] = {
                    "status": "failed",
                    "error": trufflehog_result["error"]
                }
        
        # Calculate summary
        results["end_time"] = datetime.now().isoformat()
        results["duration"] = (datetime.now() - scan_start).total_seconds()
        results["total_findings"] = len(results["findings"])
        
        # Store in history
        self.scan_history.append(results)
        
        return results
    
    def get_scan_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent scan history
        
        Args:
            limit: Maximum number of recent scans to return
            
        Returns:
            List of recent scan results
        """
        return self.scan_history[-limit:] if self.scan_history else []
    
    def configure_scan_rules(self, config_updates: Dict) -> Dict:
        """
        Update scan configuration
        
        Args:
            config_updates: Dictionary containing configuration updates
            
        Returns:
            Updated configuration
        """
        try:
            # Deep merge configuration
            def deep_merge(base, updates):
                for key, value in updates.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value
            
            deep_merge(self.config, config_updates)
            
            return {
                "success": True,
                "message": "Configuration updated successfully",
                "config": self.config
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update configuration: {str(e)}"
            }
    
    def get_scan_config(self) -> Dict:
        """Get current scan configuration"""
        return self.config
    
    def clear_scan_history(self) -> Dict:
        """Clear scan history"""
        self.scan_history.clear()
        return {
            "success": True,
            "message": "Scan history cleared successfully"
        }

# Global instance
secrets_detector = SecretsDetector()
