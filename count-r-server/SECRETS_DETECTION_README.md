# 🔐 Secrets Detection Tool - Installation & Usage Guide

This guide explains how to install and use the Secrets Detection Tool integrated into your MCP server.

## 🚀 Quick Start

The Secrets Detection Tool integrates **Gitleaks** and **TruffleHog** to provide comprehensive secret scanning capabilities for your MCP server.

## 📋 Prerequisites

- Python 3.7+
- Git (for repository scanning)
- Access to install system packages

## 🛠️ Installation

### 1. Install Gitleaks

#### macOS (using Homebrew)
```bash
brew install gitleaks
```

#### Linux (Ubuntu/Debian)
```bash
# Download latest release
curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/install.sh | sh -s -- -b /usr/local/bin

# Or using package manager
sudo apt-get install gitleaks
```

#### Linux (CentOS/RHEL)
```bash
# Download latest release
curl -sSfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/install.sh | sh -s -- -b /usr/local/bin
```

#### Windows
```bash
# Using Chocolatey
choco install gitleaks

# Or download from GitHub releases
# https://github.com/gitleaks/gitleaks/releases
```

### 2. Install TruffleHog

#### macOS (using Homebrew)
```bash
brew install trufflesecurity/trufflehog/trufflehog
```

#### Linux
```bash
# Download latest release
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
```

#### Windows
```bash
# Using Chocolatey
choco install trufflehog

# Or download from GitHub releases
# https://github.com/trufflesecurity/trufflehog/releases
```

### 3. Verify Installation

```bash
# Check Gitleaks
gitleaks version

# Check TruffleHog
trufflehog --version
```

## 🔧 Configuration

The tool comes with sensible defaults, but you can customize the configuration:

### Default Configuration
```json
{
  "gitleaks": {
    "enabled": true,
    "timeout": 300,
    "output_format": "json",
    "verbose": false
  },
  "trufflehog": {
    "enabled": true,
    "timeout": 120,
    "max_depth": 10,
    "only_verified": false
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
```

### Customizing Configuration
You can update the configuration using the `configure_scan_rules` tool:

```json
{
  "gitleaks": {
    "timeout": 600,
    "verbose": true
  },
  "trufflehog": {
    "max_depth": 5,
    "only_verified": true
  }
}
```

## 🎯 Available Tools

### 1. `scan_repository`
Scans a Git repository for secrets using both Gitleaks and TruffleHog.

**Parameters:**
- `repo_path`: Path to the repository
- `use_gitleaks`: Whether to use Gitleaks (default: true)
- `use_trufflehog`: Whether to use TruffleHog (default: true)

**Example:**
```python
# Scan current repository
result = scan_repository("./", True, True)

# Scan specific repository
result = scan_repository("/path/to/repo", True, False)
```

### 2. `scan_file`
Scans a single file for secrets using TruffleHog.

**Parameters:**
- `file_path`: Path to the file
- `use_trufflehog`: Whether to use TruffleHog (default: true)

**Example:**
```python
# Scan a specific file
result = scan_file("/path/to/config.py")
```

### 3. `scan_directory`
Scans a directory for secrets using TruffleHog.

**Parameters:**
- `dir_path`: Path to the directory
- `recursive`: Whether to scan subdirectories (default: true)
- `use_trufflehog`: Whether to use TruffleHog (default: true)

**Example:**
```python
# Scan current directory recursively
result = scan_directory(".", True, True)

# Scan specific directory non-recursively
result = scan_directory("/path/to/dir", False, True)
```

### 4. `get_scan_history`
Retrieves recent scan history.

**Parameters:**
- `limit`: Maximum number of recent scans (default: 10)

**Example:**
```python
# Get last 5 scans
history = get_scan_history(5)
```

### 5. `configure_scan_rules`
Updates scan configuration.

**Parameters:**
- `config_updates`: JSON string with configuration updates

**Example:**
```python
config = '{"gitleaks": {"timeout": 600}}'
result = configure_scan_rules(config)
```

### 6. `get_scan_config`
Retrieves current scan configuration.

**Example:**
```python
config = get_scan_config()
```

### 7. `clear_scan_history`
Clears all scan history.

**Example:**
```python
result = clear_scan_history()
```

## 📊 Understanding Results

### Scan Result Structure
```json
{
  "target": "/path/to/target",
  "scan_type": "repository|file|directory",
  "start_time": "2024-01-01T12:00:00",
  "end_time": "2024-01-01T12:01:00",
  "duration": 60.5,
  "tools_used": ["gitleaks", "trufflehog"],
  "findings": [...],
  "total_findings": 5,
  "severity_summary": {
    "high": 2,
    "medium": 2,
    "low": 1,
    "unknown": 0
  },
  "summary": {
    "gitleaks": {
      "status": "success",
      "findings_count": 3
    },
    "trufflehog": {
      "status": "success",
      "findings_count": 2
    }
  }
}
```

### Finding Structure
```json
{
  "rule_id": "aws-access-key-id",
  "severity": "high",
  "description": "AWS Access Key ID",
  "file": "config.py",
  "line": 15,
  "secret": "AKIAIOSFODNN7EXAMPLE",
  "context": "AWS_ACCESS_KEY_ID = 'AKIAIOSFODNN7EXAMPLE'"
}
```

## 🚨 Common Issues & Solutions

### 1. "Gitleaks not found" Error
**Solution:** Install Gitleaks following the installation guide above.

### 2. "TruffleHog not found" Error
**Solution:** Install TruffleHog following the installation guide above.

### 3. Scan Timeout Errors
**Solution:** Increase timeout in configuration:
```json
{
  "gitleaks": {"timeout": 600},
  "trufflehog": {"timeout": 300}
}
```

### 4. Permission Denied Errors
**Solution:** Ensure the tool has read access to the target directory/files.

### 5. Large Repository Performance
**Solution:** 
- Use `use_gitleaks: false` for very large repositories
- Adjust `max_depth` in TruffleHog configuration
- Consider scanning specific directories instead of entire repositories

## 🔒 Security Best Practices

1. **Never commit scan results** containing actual secrets
2. **Use in isolated environments** when scanning untrusted code
3. **Review findings manually** before taking action
4. **Rotate secrets immediately** if found in production code
5. **Implement pre-commit hooks** using these tools

## 📚 Integration Examples

### Workflow Integration
```python
# Example workflow step
{
  "name": "security_scan",
  "description": "Scan repository for secrets",
  "tool_name": "scan_repository",
  "parameters": {
    "repo_path": "{{workspace_path}}",
    "use_gitleaks": true,
    "use_trufflehog": true
  }
}
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Security Scan
  run: |
    python -c "
    from secrets_detection import secrets_detector
    result = secrets_detector.scan_repository('.')
    if result['total_findings'] > 0:
        print('Secrets found!')
        exit(1)
    "
```

## 🆘 Support

If you encounter issues:

1. Check tool installation: `gitleaks version` and `trufflehog --version`
2. Verify file permissions
3. Check configuration settings
4. Review scan logs for detailed error messages

## 📝 Changelog

- **v1.0.0**: Initial release with Gitleaks and TruffleHog integration
- Support for repository, file, and directory scanning
- Configurable scan rules and timeouts
- Comprehensive scan history and reporting
