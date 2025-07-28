# GitHub Tools for MCP Server

This module provides comprehensive GitHub integration tools for pull request management, code review, and repository operations.

## Setup

### 1. GitHub Token Setup
Set your GitHub Personal Access Token as an environment variable:

```bash
export GITHUB_TOKEN="your_github_token_here"
```

### 2. Required Permissions
Your GitHub token needs the following permissions:
- `repo` - Full control of private repositories
- `pull_request` - Access to pull requests
- `workflow` - Access to GitHub Actions

## Available Tools

### Pull Request Management

#### `github_create_pull_request`
Create a new pull request on GitHub.

**Parameters:**
- `owner`: Repository owner (username or organization)
- `repo`: Repository name
- `title`: Pull request title
- `body`: Pull request description
- `head`: Source branch name
- `base`: Target branch name (default: main)

**Example:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "title": "Add new feature",
  "body": "This PR adds a new feature to improve functionality",
  "head": "feature-branch",
  "base": "main"
}
```

#### `github_list_pull_requests`
List pull requests in a GitHub repository.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `state`: PR state filter (open, closed, all)

#### `github_get_pull_request`
Get details of a specific pull request.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `pr_number`: Pull request number

### Code Review Tools

#### `github_review_pull_request`
Review a pull request (approve, request changes, or comment).

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `pr_number`: Pull request number
- `event`: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
- `body`: Review comment

**Example:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "pr_number": 1,
  "event": "APPROVE",
  "body": "Great work! This looks good to merge."
}
```

#### `github_add_comment_to_pr`
Add a comment to a pull request.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `pr_number`: Pull request number
- `body`: Comment text
- `commit_id`: Optional commit SHA for line-specific comment
- `path`: Optional file path for line-specific comment
- `line`: Optional line number for line-specific comment

#### `github_analyze_code_changes`
Analyze code changes in a pull request.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `pr_number`: Pull request number

**Returns analysis including:**
- Number of additions/deletions
- Changed files count
- Commit count
- Review status
- Mergeability status

### Repository Management

#### `github_get_repository_status`
Get repository status and information.

#### `github_list_branches`
List branches in a repository.

#### `github_create_branch`
Create a new branch in a repository.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `branch_name`: Name of the new branch
- `source_sha`: SHA of the commit to branch from

#### `github_get_commit_details`
Get details of a specific commit.

#### `github_get_file_contents`
Get contents of a file in the repository.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `path`: File path in the repository
- `ref`: Branch or commit reference (default: main)

### Merge Operations

#### `github_merge_pull_request`
Merge a pull request.

**Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `pr_number`: Pull request number
- `merge_method`: Merge method (merge, squash, rebase)

## Usage Examples

### Complete Code Review Workflow

1. **List open PRs:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "state": "open"
}
```

2. **Get PR details:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "pr_number": 1
}
```

3. **Analyze changes:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "pr_number": 1
}
```

4. **Add review comment:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "pr_number": 1,
  "body": "Consider adding error handling here",
  "path": "src/main.py",
  "line": 42
}
```

5. **Approve PR:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "pr_number": 1,
  "event": "APPROVE",
  "body": "Looks good! Ready to merge."
}
```

6. **Merge PR:**
```json
{
  "owner": "abiodun2025",
  "repo": "mcp",
  "pr_number": 1,
  "merge_method": "squash"
}
```

## Error Handling

All tools return a consistent response format:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Security Notes

- Never commit your GitHub token to version control
- Use environment variables for sensitive data
- Regularly rotate your GitHub tokens
- Use the minimum required permissions for your token

## Integration with Workflows

These GitHub tools can be integrated with the workflow orchestrator to create automated code review and PR management workflows.

Example workflow:
1. Monitor repository for new PRs
2. Automatically analyze code changes
3. Run automated tests
4. Post results to Slack/Teams
5. Create review comments
6. Approve or request changes based on criteria 