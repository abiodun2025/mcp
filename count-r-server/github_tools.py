import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

class GitHubTools:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        } if self.token else {}
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to GitHub API"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def create_pull_request(self, owner: str, repo: str, title: str, body: str, 
                          head: str, base: str = "main") -> dict:
        """Create a new pull request"""
        endpoint = f"/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        return self._make_request("POST", endpoint, data)
    
    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> dict:
        """List pull requests in a repository"""
        endpoint = f"/repos/{owner}/{repo}/pulls?state={state}"
        return self._make_request("GET", endpoint)
    
    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> dict:
        """Get details of a specific pull request"""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        return self._make_request("GET", endpoint)
    
    def review_pull_request(self, owner: str, repo: str, pr_number: int, 
                          event: str, body: str = "") -> dict:
        """Review a pull request (approve, request changes, comment)"""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        data = {
            "event": event,  # APPROVE, REQUEST_CHANGES, COMMENT
            "body": body
        }
        return self._make_request("POST", endpoint, data)
    
    def add_comment_to_pr(self, owner: str, repo: str, pr_number: int, 
                         body: str, commit_id: str = None, path: str = None, 
                         line: int = None) -> dict:
        """Add a comment to a pull request"""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/comments"
        data = {"body": body}
        if commit_id:
            data["commit_id"] = commit_id
        if path:
            data["path"] = path
        if line:
            data["line"] = line
        return self._make_request("POST", endpoint, data)
    
    def merge_pull_request(self, owner: str, repo: str, pr_number: int, 
                          merge_method: str = "merge") -> dict:
        """Merge a pull request"""
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/merge"
        data = {"merge_method": merge_method}
        return self._make_request("PUT", endpoint, data)
    
    def get_repository_status(self, owner: str, repo: str) -> dict:
        """Get repository status and information"""
        endpoint = f"/repos/{owner}/{repo}"
        return self._make_request("GET", endpoint)
    
    def list_branches(self, owner: str, repo: str) -> dict:
        """List branches in a repository"""
        endpoint = f"/repos/{owner}/{repo}/branches"
        return self._make_request("GET", endpoint)
    
    def create_branch(self, owner: str, repo: str, branch_name: str, 
                     source_sha: str) -> dict:
        """Create a new branch"""
        endpoint = f"/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": source_sha
        }
        return self._make_request("POST", endpoint, data)
    
    def get_commit_details(self, owner: str, repo: str, commit_sha: str) -> dict:
        """Get details of a specific commit"""
        endpoint = f"/repos/{owner}/{repo}/commits/{commit_sha}"
        return self._make_request("GET", endpoint)
    
    def get_file_contents(self, owner: str, repo: str, path: str, 
                         ref: str = "main") -> dict:
        """Get contents of a file in the repository"""
        endpoint = f"/repos/{owner}/{repo}/contents/{path}?ref={ref}"
        return self._make_request("GET", endpoint)
    
    def analyze_code_changes(self, owner: str, repo: str, pr_number: int) -> dict:
        """Analyze code changes in a pull request"""
        pr_data = self.get_pull_request(owner, repo, pr_number)
        if not pr_data["success"]:
            return pr_data
        
        pr = pr_data["data"]
        analysis = {
            "pr_number": pr_number,
            "title": pr["title"],
            "state": pr["state"],
            "additions": pr["additions"],
            "deletions": pr["deletions"],
            "changed_files": pr["changed_files"],
            "commits": pr["commits"],
            "review_comments": pr["review_comments"],
            "comments": pr["comments"],
            "mergeable": pr["mergeable"],
            "mergeable_state": pr["mergeable_state"]
        }
        
        return {"success": True, "data": analysis}

# Initialize GitHub tools instance
github_tools = GitHubTools() 