#!/usr/bin/env python3
"""
Email Agent Web Application
"""

import os
import json
import csv
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dynamic_email_sender import DynamicEmailSender

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize email sender
email_sender = DynamicEmailSender()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_gmail_config():
    """Load Gmail configuration"""
    try:
        # Try multiple possible locations
        possible_paths = [
            "../gmail_config.json",  # Relative to web_app
            "gmail_config.json",     # In current directory
            "../count-r-server/gmail_config.json",  # From root
            os.path.join(os.path.dirname(__file__), "..", "gmail_config.json")  # Absolute path
        ]
        
        for config_file in possible_paths:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def load_github_config():
    """Load GitHub configuration"""
    try:
        config_file = os.path.join(os.path.dirname(__file__), "..", "github_config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading GitHub config: {e}")
        return None

@app.route('/')
def dashboard():
    """Main dashboard"""
    config = load_gmail_config()
    github_config = load_github_config()
    return render_template('dashboard.html', config=config, github_config=github_config)

@app.route('/single-email')
def single_email():
    """Single email page"""
    config = load_gmail_config()
    return render_template('single_email.html', config=config)

@app.route('/bulk-email')
def bulk_email():
    """Bulk email page"""
    config = load_gmail_config()
    return render_template('bulk_email.html', config=config)

@app.route('/personalized-email')
def personalized_email():
    """Personalized email page"""
    config = load_gmail_config()
    return render_template('personalized.html', config=config)

@app.route('/config')
def config_page():
    """Configuration page"""
    config = load_gmail_config()
    return render_template('config.html', config=config)

@app.route('/api/send-single', methods=['POST'])
def send_single_email():
    """API endpoint for sending single email"""
    try:
        data = request.get_json()
        to_email = data.get('to_email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([to_email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required'})
        
        result = email_sender.send_email(to_email, subject, message)
        
        if "✅" in result:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send-bulk', methods=['POST'])
def send_bulk_email():
    """API endpoint for sending bulk emails"""
    try:
        data = request.get_json()
        recipients = data.get('recipients', [])
        subject = data.get('subject')
        message = data.get('message')
        
        if not recipients or not subject or not message:
            return jsonify({'success': False, 'error': 'All fields are required'})
        
        results = email_sender.send_to_multiple_recipients(recipients, subject, message)
        
        successful = sum(1 for _, result in results if "✅" in result)
        failed = len(results) - successful
        
        return jsonify({
            'success': True,
            'message': f'Sent {successful} emails successfully, {failed} failed',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send-personalized', methods=['POST'])
def send_personalized_email():
    """API endpoint for sending personalized emails"""
    try:
        data = request.get_json()
        recipients_data = data.get('recipients', [])
        subject_template = data.get('subject_template')
        message_template = data.get('message_template')
        
        if not recipients_data or not subject_template or not message_template:
            return jsonify({'success': False, 'error': 'All fields are required'})
        
        results = email_sender.send_personalized_emails(recipients_data, subject_template, message_template)
        
        successful = sum(1 for _, result in results if "✅" in result)
        failed = len(results) - successful
        
        return jsonify({
            'success': True,
            'message': f'Sent {successful} personalized emails successfully, {failed} failed',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """API endpoint for uploading CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse CSV and return data
            recipients_data = email_sender.load_recipients_from_csv(filepath)
            
            return jsonify({
                'success': True,
                'message': f'Uploaded {len(recipients_data)} recipients',
                'recipients': recipients_data
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file type. Please upload a CSV file.'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-connection')
def test_connection():
    """API endpoint for testing Gmail SMTP connection"""
    try:
        config = load_gmail_config()
        if not config:
            return jsonify({'success': False, 'error': 'Gmail configuration not found'})
        
        # Test connection
        import smtplib
        import ssl
        
        context = email_sender.create_ssl_context()
        
        with smtplib.SMTP(email_sender.smtp_server, email_sender.smtp_port) as server:
            server.starttls(context=context)
            server.login(config["email"], config["app_password"])
        
        return jsonify({'success': True, 'message': 'Gmail SMTP connection successful!'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Connection failed: {str(e)}'})

@app.route('/api/save-config', methods=['POST'])
def save_config():
    """API endpoint for saving Gmail configuration"""
    try:
        data = request.get_json()
        email = data.get('email')
        app_password = data.get('app_password')
        
        if not email or not app_password:
            return jsonify({'success': False, 'error': 'Email and App Password are required'})
        
        config = {
            'email': email,
            'app_password': app_password
        }
        
        config_file = "../gmail_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# MCP Tools Integration
def call_mcp_tool(tool_name, **kwargs):
    """Call MCP tool via HTTP request"""
    try:
        # MCP server runs on port 5000, but Flask app also uses 5000
        # We'll use a different port for MCP server or call it directly
        # For now, let's implement the tools directly in the web app
        
        if tool_name == "count_r":
            word = kwargs.get('word', '')
            return word.lower().count('r')
        
        elif tool_name == "list_desktop_contents":
            desktop_path = os.path.expanduser("~/Desktop")
            return os.listdir(desktop_path)
        
        elif tool_name == "get_desktop_path":
            return os.path.expanduser("~/Desktop")
        
        elif tool_name == "open_gmail":
            import webbrowser
            webbrowser.open("https://mail.google.com")
            return "Gmail opened successfully in your default browser"
        
        elif tool_name == "open_gmail_compose":
            import webbrowser
            webbrowser.open("https://mail.google.com/mail/u/0/#compose")
            return "Gmail compose window opened successfully"
        
        elif tool_name == "sendmail":
            to_email = kwargs.get('to_email')
            subject = kwargs.get('subject')
            body = kwargs.get('body')
            from_email = kwargs.get('from_email')
            
            # Use the existing email sender
            result = email_sender.send_email(to_email, subject, body)
            return result
        
        elif tool_name == "sendmail_simple":
            to_email = kwargs.get('to_email')
            subject = kwargs.get('subject')
            message = kwargs.get('message')
            
            # Use the existing email sender
            result = email_sender.send_email(to_email, subject, message)
            return result
        
        elif tool_name == "github_login":
            print("GitHub login tool called")  # Debug log
            username = kwargs.get('username')
            password = kwargs.get('password')
            token = kwargs.get('token')
            
            print(f"Tool - Username: {username}, Has password: {bool(password)}, Has token: {bool(token)}")  # Debug log
            
            import requests
            from requests.auth import HTTPBasicAuth
            
            if token:
                print("Using token authentication")  # Debug log
                headers = {
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                response = requests.get('https://api.github.com/user', headers=headers)
            elif password:
                print("Using password authentication")  # Debug log
                auth = HTTPBasicAuth(username, password)
                response = requests.get('https://api.github.com/user', auth=auth)
            else:
                return "Error: Either password or token must be provided"
            
            print(f"GitHub API response status: {response.status_code}")  # Debug log
            print(f"GitHub API response: {response.text[:200]}...")  # Debug log
            
            if response.status_code == 200:
                user_data = response.json()
                return f"Successfully logged in as {user_data['login']} ({user_data['name']})"
            else:
                return f"Login failed: {response.status_code} - {response.text}"
        
        elif tool_name == "create_pull_request":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            title = kwargs.get('title')
            body = kwargs.get('body')
            head = kwargs.get('head')
            base = kwargs.get('base', 'main')
            token = kwargs.get('token')
            
            if not token:
                return "Error: GitHub token is required for creating pull requests"
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'title': title,
                'body': body,
                'head': head,
                'base': base
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                pr_data = response.json()
                return f"Pull request created successfully! URL: {pr_data['html_url']}"
            else:
                return f"Failed to create pull request: {response.status_code} - {response.text}"
        
        elif tool_name == "review_pull_request":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            pull_number = kwargs.get('pull_number')
            body = kwargs.get('body')
            event = kwargs.get('event', 'COMMENT')
            token = kwargs.get('token')
            
            if not token:
                return "Error: GitHub token is required for reviewing pull requests"
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'body': body,
                'event': event.upper()
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews'
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                review_data = response.json()
                return f"Review submitted successfully for PR #{pull_number}. Review ID: {review_data.get('id', 'N/A')}"
            else:
                return f"Failed to submit review: {response.status_code} - {response.text}"
        
        elif tool_name == "get_pull_request_details":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            pull_number = kwargs.get('pull_number')
            token = kwargs.get('token')
            
            if not token:
                return {"error": "GitHub token is required to get PR details"}
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                pr_data = response.json()
                return {
                    'number': pr_data['number'],
                    'title': pr_data['title'],
                    'body': pr_data['body'],
                    'state': pr_data['state'],
                    'user': pr_data['user']['login'],
                    'html_url': pr_data['html_url'],
                    'created_at': pr_data['created_at'],
                    'updated_at': pr_data['updated_at'],
                    'head': {
                        'ref': pr_data['head']['ref'],
                        'sha': pr_data['head']['sha']
                    },
                    'base': {
                        'ref': pr_data['base']['ref'],
                        'sha': pr_data['base']['sha']
                    },
                    'mergeable': pr_data.get('mergeable'),
                    'mergeable_state': pr_data.get('mergeable_state'),
                    'comments': pr_data.get('comments', 0),
                    'review_comments': pr_data.get('review_comments', 0),
                    'commits': pr_data.get('commits', 0),
                    'additions': pr_data.get('additions', 0),
                    'deletions': pr_data.get('deletions', 0),
                    'changed_files': pr_data.get('changed_files', 0)
                }
            else:
                return {"error": f"Failed to get PR details: {response.status_code} - {response.text}"}
        
        elif tool_name == "get_pull_request_reviews":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            pull_number = kwargs.get('pull_number')
            token = kwargs.get('token')
            
            if not token:
                return {"error": "GitHub token is required to get PR reviews"}
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/reviews'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                reviews = response.json()
                formatted_reviews = []
                for review in reviews:
                    formatted_reviews.append({
                        'id': review['id'],
                        'user': review['user']['login'],
                        'body': review['body'],
                        'state': review['state'],
                        'submitted_at': review['submitted_at'],
                        'commit_id': review['commit_id']
                    })
                return formatted_reviews
            else:
                return {"error": f"Failed to get PR reviews: {response.status_code} - {response.text}"}
        
        elif tool_name == "get_pull_request_files":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            pull_number = kwargs.get('pull_number')
            token = kwargs.get('token')
            
            if not token:
                return {"error": "GitHub token is required to get PR files"}
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                files = response.json()
                formatted_files = []
                for file in files:
                    formatted_files.append({
                        'filename': file['filename'],
                        'status': file['status'],
                        'additions': file['additions'],
                        'deletions': file['deletions'],
                        'changes': file['changes'],
                        'patch': file.get('patch', '')
                    })
                return formatted_files
            else:
                return {"error": f"Failed to get PR files: {response.status_code} - {response.text}"}
        
        elif tool_name == "list_pull_requests":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            state = kwargs.get('state', 'open')
            token = kwargs.get('token')
            
            import requests
            headers = {}
            if token:
                headers['Authorization'] = f'token {token}'
            headers['Accept'] = 'application/vnd.github.v3+json'
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
            params = {'state': state}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return [{"error": f"Failed to list PRs: {response.status_code} - {response.text}"}]
        
        elif tool_name == "list_my_repositories":
            token = kwargs.get('token')
            
            if not token:
                return [{"error": "GitHub token is required to list repositories"}]
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Get user's repositories
            url = 'https://api.github.com/user/repos'
            params = {
                'sort': 'updated',
                'per_page': 100  # Get up to 100 repos
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                repos = response.json()
                # Format the response to include key information
                formatted_repos = []
                for repo in repos:
                    formatted_repos.append({
                        'name': repo['name'],
                        'full_name': repo['full_name'],
                        'description': repo['description'],
                        'private': repo['private'],
                        'html_url': repo['html_url'],
                        'clone_url': repo['clone_url'],
                        'updated_at': repo['updated_at'],
                        'language': repo['language'],
                        'stargazers_count': repo['stargazers_count'],
                        'forks_count': repo['forks_count']
                    })
                return formatted_repos
            else:
                return [{"error": f"Failed to list repositories: {response.status_code} - {response.text}"}]
        
        elif tool_name == "list_repository_pull_requests":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            state = kwargs.get('state', 'open')
            token = kwargs.get('token')
            
            print(f"DEBUG: Tool called with - owner: '{owner}', repo: '{repo}', state: '{state}'")
            
            if not token:
                print("DEBUG: No token provided")
                return [{"error": "GitHub token is required to list pull requests"}]
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
            params = {'state': state, 'per_page': 50}
            
            print(f"DEBUG: Making request to: {url}")
            print(f"DEBUG: With params: {params}")
            
            response = requests.get(url, headers=headers, params=params)
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text[:200]}...")
            
            if response.status_code == 200:
                prs = response.json()
                print(f"DEBUG: Found {len(prs)} pull requests")
                formatted_prs = []
                for pr in prs:
                    formatted_prs.append({
                        'number': pr['number'],
                        'title': pr['title'],
                        'state': pr['state'],
                        'user': pr['user']['login'],
                        'html_url': pr['html_url'],
                        'created_at': pr['created_at'],
                        'updated_at': pr['updated_at'],
                        'comments': pr.get('comments', 0),
                        'review_comments': pr.get('review_comments', 0),
                        'commits': pr.get('commits', 0),
                        'additions': pr.get('additions', 0),
                        'deletions': pr.get('deletions', 0),
                        'changed_files': pr.get('changed_files', 0),
                        'mergeable': pr.get('mergeable'),
                        'mergeable_state': pr.get('mergeable_state')
                    })
                return formatted_prs
            else:
                return [{"error": f"Failed to list PRs: {response.status_code} - {response.text}"}]
        
        elif tool_name == "search_pull_requests":
            query = kwargs.get('query', '')
            token = kwargs.get('token')
            
            if not token:
                return [{"error": "GitHub token is required to search pull requests"}]
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = 'https://api.github.com/search/issues'
            params = {
                'q': f'{query} is:pr',
                'per_page': 20
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                results = response.json()
                formatted_results = []
                for item in results.get('items', []):
                    # Extract repo info from the URL
                    url_parts = item['repository_url'].split('/')
                    owner = url_parts[-2]
                    repo = url_parts[-1]
                    
                    formatted_results.append({
                        'number': item['number'],
                        'title': item['title'],
                        'state': item['state'],
                        'user': item['user']['login'],
                        'html_url': item['html_url'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at'],
                        'owner': owner,
                        'repo': repo,
                        'comments': item.get('comments', 0)
                    })
                return formatted_results
            else:
                return [{"error": f"Failed to search PRs: {response.status_code} - {response.text}"}]
        
        elif tool_name == "get_user_pull_requests":
            state = kwargs.get('state', 'open')
            token = kwargs.get('token')
            
            if not token:
                return [{"error": "GitHub token is required to get user pull requests"}]
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = 'https://api.github.com/search/issues'
            params = {
                'q': f'author:@me is:pr state:{state}',
                'per_page': 30
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                results = response.json()
                formatted_results = []
                for item in results.get('items', []):
                    # Extract repo info from the URL
                    url_parts = item['repository_url'].split('/')
                    owner = url_parts[-2]
                    repo = url_parts[-1]
                    
                    formatted_results.append({
                        'number': item['number'],
                        'title': item['title'],
                        'state': item['state'],
                        'user': item['user']['login'],
                        'html_url': item['html_url'],
                        'created_at': item['created_at'],
                        'updated_at': item['updated_at'],
                        'owner': owner,
                        'repo': repo,
                        'comments': item.get('comments', 0)
                    })
                return formatted_results
            else:
                return [{"error": f"Failed to get user PRs: {response.status_code} - {response.text}"}]
        
        elif tool_name == "get_repository_branches":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            token = kwargs.get('token')

            print(f"DEBUG: Tool called with - owner: '{owner}', repo: '{repo}'")

            if not token:
                print("DEBUG: No token provided")
                return [{"error": "GitHub token is required to get repository branches"}]

            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }

            url = f'https://api.github.com/repos/{owner}/{repo}/branches'
            params = {'per_page': 100}

            print(f"DEBUG: Making request to: {url}")
            print(f"DEBUG: With params: {params}")

            response = requests.get(url, headers=headers, params=params)

            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text[:200]}...")

            if response.status_code == 200:
                branches = response.json()
                print(f"DEBUG: Found {len(branches)} branches")
                
                if len(branches) == 0:
                    print("DEBUG: No branches found in repository")
                    return [{"error": f"No branches found in repository {owner}/{repo}. This might be an empty repository."}]
                
                formatted_branches = []
                for branch in branches:
                    formatted_branches.append({
                        'name': branch['name'],
                        'commit': branch['commit']['sha'][:7],
                        'protected': branch.get('protected', False)
                    })
                return formatted_branches
            else:
                error_msg = f"Failed to get branches: {response.status_code} - {response.text}"
                print(f"DEBUG: {error_msg}")
                return [{"error": error_msg}]
        
        elif tool_name == "generate_pr_template":
            pr_type = kwargs.get('type', 'feature')
            title = kwargs.get('title', '')
            description = kwargs.get('description', '')
            
            templates = {
                'feature': f"""## 🚀 Feature: {title}

{description}

### Changes Made
- [ ] Add your changes here

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

### Screenshots (if applicable)
<!-- Add screenshots here -->

### Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes introduced""",
                
                'bugfix': f"""## 🐛 Bug Fix: {title}

{description}

### Problem
<!-- Describe the bug -->

### Solution
<!-- Describe the fix -->

### Testing
- [ ] Bug reproduction steps verified
- [ ] Fix tested and working
- [ ] Regression tests added

### Checklist
- [ ] Root cause identified
- [ ] Fix is minimal and targeted
- [ ] No new bugs introduced
- [ ] Tests added/updated""",
                
                'hotfix': f"""## 🔥 Hotfix: {title}

{description}

### Issue
<!-- Describe the critical issue -->

### Fix
<!-- Describe the emergency fix -->

### Testing
- [ ] Critical functionality verified
- [ ] No regressions introduced

### Deployment
- [ ] Ready for immediate deployment
- [ ] Rollback plan prepared""",
                
                'refactor': f"""## 🔧 Refactor: {title}

{description}

### Changes
<!-- Describe the refactoring -->

### Benefits
<!-- What improvements this brings -->

### Testing
- [ ] All existing functionality preserved
- [ ] Performance improved/maintained
- [ ] Code quality improved

### Checklist
- [ ] No functional changes
- [ ] Tests updated
- [ ] Documentation updated""",
                
                'docs': f"""## 📚 Documentation: {title}

{description}

### Changes
<!-- Describe documentation updates -->

### Files Modified
<!-- List files that were updated -->

### Checklist
- [ ] Content is accurate and up-to-date
- [ ] Grammar and spelling checked
- [ ] Links are working
- [ ] Examples are clear and helpful"""
            }
            
            return templates.get(pr_type, templates['feature'])
        
        elif tool_name == "quick_create_pr":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            title = kwargs.get('title')
            head = kwargs.get('head')
            base = kwargs.get('base', 'main')
            pr_type = kwargs.get('type', 'feature')
            description = kwargs.get('description', '')
            token = kwargs.get('token')
            
            if not token:
                return "Error: GitHub token is required for creating pull requests"
            
            # Generate PR template
            body = call_mcp_tool('generate_pr_template', type=pr_type, title=title, description=description)
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'title': title,
                'body': body,
                'head': head,
                'base': base
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    'success': True,
                    'message': f"Pull request created successfully!",
                    'url': pr_data['html_url'],
                    'number': pr_data['number'],
                    'title': pr_data['title']
                }
            else:
                return {
                    'success': False,
                    'error': f"Failed to create pull request: {response.status_code} - {response.text}"
                }
        
        elif tool_name == "get_repository_info":
            owner = kwargs.get('owner')
            repo = kwargs.get('repo')
            token = kwargs.get('token')
            
            if not token:
                return {"error": "GitHub token is required to get repository info"}
            
            import requests
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f'https://api.github.com/repos/{owner}/{repo}'
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'name': repo_data['name'],
                    'full_name': repo_data['full_name'],
                    'description': repo_data['description'],
                    'private': repo_data['private'],
                    'html_url': repo_data['html_url'],
                    'default_branch': repo_data['default_branch'],
                    'language': repo_data['language'],
                    'stargazers_count': repo_data['stargazers_count'],
                    'forks_count': repo_data['forks_count'],
                    'open_issues_count': repo_data['open_issues_count'],
                    'updated_at': repo_data['updated_at']
                }
            else:
                return {"error": f"Failed to get repository info: {response.status_code} - {response.text}"}
        
        else:
            return f"Unknown tool: {tool_name}"
            
    except Exception as e:
        return f"Error calling tool {tool_name}: {str(e)}"

@app.route('/api/mcp/count-r', methods=['POST'])
def mcp_count_r():
    """API endpoint for count_r tool"""
    try:
        data = request.get_json()
        word = data.get('word', '')
        result = call_mcp_tool('count_r', word=word)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mcp/list-desktop', methods=['GET'])
def mcp_list_desktop():
    """API endpoint for list_desktop_contents tool"""
    try:
        result = call_mcp_tool('list_desktop_contents')
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mcp/get-desktop-path', methods=['GET'])
def mcp_get_desktop_path():
    """API endpoint for get_desktop_path tool"""
    try:
        result = call_mcp_tool('get_desktop_path')
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mcp/open-gmail', methods=['POST'])
def mcp_open_gmail():
    """API endpoint for open_gmail tool"""
    try:
        result = call_mcp_tool('open_gmail')
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mcp/open-gmail-compose', methods=['POST'])
def mcp_open_gmail_compose():
    """API endpoint for open_gmail_compose tool"""
    try:
        result = call_mcp_tool('open_gmail_compose')
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mcp/sendmail', methods=['POST'])
def mcp_sendmail():
    """API endpoint for sendmail tool"""
    try:
        data = request.get_json()
        to_email = data.get('to_email')
        subject = data.get('subject')
        body = data.get('body')
        from_email = data.get('from_email')
        
        if not all([to_email, subject, body]):
            return jsonify({'success': False, 'error': 'to_email, subject, and body are required'})
        
        result = call_mcp_tool('sendmail', to_email=to_email, subject=subject, body=body, from_email=from_email)
        
        if "✅" in result:
            return jsonify({'success': True, 'result': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/mcp/sendmail-simple', methods=['POST'])
def mcp_sendmail_simple():
    """API endpoint for sendmail_simple tool"""
    try:
        data = request.get_json()
        to_email = data.get('to_email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([to_email, subject, message]):
            return jsonify({'success': False, 'error': 'to_email, subject, and message are required'})
        
        result = call_mcp_tool('sendmail_simple', to_email=to_email, subject=subject, message=message)
        
        if "✅" in result:
            return jsonify({'success': True, 'result': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/login', methods=['POST'])
def api_github_login():
    """API endpoint for GitHub login"""
    try:
        print("GitHub login endpoint called")  # Debug log
        data = request.get_json()
        print(f"Received data: {data}")  # Debug log
        
        username = data.get('username')
        password = data.get('password')
        token = data.get('token')
        
        print(f"Username: {username}, Has password: {bool(password)}, Has token: {bool(token)}")  # Debug log
        
        if not username or (not password and not token):
            return jsonify({'success': False, 'error': 'Username and either password or token are required'})
        
        # Call the MCP tool
        print("Calling MCP tool...")  # Debug log
        result = call_mcp_tool('github_login', username=username, password=password, token=token)
        print(f"MCP tool result: {result}")  # Debug log
        
        if "Successfully logged in" in result:
            # Save token if provided
            if token:
                config = {'username': username, 'token': token}
                config_file = "../github_config.json"
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"Saved config to {config_file}")  # Debug log
            
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        print(f"Error in GitHub login: {e}")  # Debug log
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/create-pr', methods=['POST'])
def api_create_pr():
    """API endpoint for creating pull requests"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        title = data.get('title')
        body = data.get('body')
        head = data.get('head')
        base = data.get('base', 'main')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('create_pull_request', 
                              owner=owner, repo=repo, title=title, 
                              body=body, head=head, base=base, 
                              token=github_config['token'])
        
        if "Pull request created successfully" in result:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/review-pr', methods=['POST'])
def api_review_pr():
    """API endpoint for reviewing pull requests"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        pull_number = data.get('pull_number')
        body = data.get('body')
        event = data.get('event', 'COMMENT')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('review_pull_request', 
                              owner=owner, repo=repo, pull_number=pull_number,
                              body=body, event=event, token=github_config['token'])
        
        if "Review submitted successfully" in result:
            return jsonify({'success': True, 'message': result})
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/list-prs', methods=['POST'])
def api_list_prs():
    """API endpoint for listing pull requests"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        state = data.get('state', 'open')
        
        # Get token from config
        github_config = load_github_config()
        token = github_config.get('token') if github_config else None
        
        result = call_mcp_tool('list_pull_requests', 
                              owner=owner, repo=repo, state=state, token=token)
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'pull_requests': result})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No results"})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/list-my-repos', methods=['POST'])
def api_list_my_repos():
    """API endpoint for listing user's repositories"""
    try:
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('list_my_repositories', token=github_config['token'])
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'repositories': result})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No repositories found"})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/get-pr-details', methods=['POST'])
def api_get_pr_details():
    """API endpoint for getting pull request details"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        pull_number = data.get('pull_number')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('get_pull_request_details', 
                              owner=owner, repo=repo, pull_number=pull_number, 
                              token=github_config['token'])
        
        if isinstance(result, dict) and not result.get("error"):
            return jsonify({'success': True, 'pr_details': result})
        else:
            return jsonify({'success': False, 'error': result.get("error", "Unknown error") if isinstance(result, dict) else str(result)})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/get-pr-reviews', methods=['POST'])
def api_get_pr_reviews():
    """API endpoint for getting pull request reviews"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        pull_number = data.get('pull_number')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('get_pull_request_reviews', 
                              owner=owner, repo=repo, pull_number=pull_number, 
                              token=github_config['token'])
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'reviews': result})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No reviews found"})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/get-pr-files', methods=['POST'])
def api_get_pr_files():
    """API endpoint for getting pull request files"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        pull_number = data.get('pull_number')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('get_pull_request_files', 
                              owner=owner, repo=repo, pull_number=pull_number, 
                              token=github_config['token'])
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'files': result})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No files found"})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/list-repo-prs', methods=['POST'])
def api_list_repo_prs():
    """API endpoint for listing repository pull requests"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        state = data.get('state', 'open')
        
        print(f"DEBUG: Received request - owner: '{owner}', repo: '{repo}', state: '{state}'")
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            print("DEBUG: No GitHub token found in config")
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        print(f"DEBUG: Using token for user: {github_config.get('username', 'unknown')}")
        
        result = call_mcp_tool('list_repository_pull_requests', 
                              owner=owner, repo=repo, state=state, 
                              token=github_config['token'])
        
        print(f"DEBUG: Tool result: {result}")
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'pull_requests': result})
        elif isinstance(result, list) and len(result) == 0:
            return jsonify({'success': True, 'pull_requests': [], 'message': 'No pull requests found in this repository'})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No pull requests found"})
            
    except Exception as e:
        print(f"DEBUG: Exception in api_list_repo_prs: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/search-prs', methods=['POST'])
def api_search_prs():
    """API endpoint for searching pull requests"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('search_pull_requests', 
                              query=query, token=github_config['token'])
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'pull_requests': result})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No pull requests found"})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/get-user-prs', methods=['POST'])
def api_get_user_prs():
    """API endpoint for getting user's pull requests"""
    try:
        data = request.get_json()
        state = data.get('state', 'open')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('get_user_pull_requests', state=state, token=github_config['token'])
        
        if isinstance(result, list) and len(result) > 0 and not result[0].get("error"):
            return jsonify({'success': True, 'pull_requests': result})
        else:
            return jsonify({'success': False, 'error': result[0].get("error", "Unknown error") if result else "No pull requests found"})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/get-branches', methods=['POST'])
def api_get_branches():
    """API endpoint for getting repository branches"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')

        print(f"DEBUG: Getting branches for owner: '{owner}', repo: '{repo}'")

        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            print("DEBUG: No GitHub token configured")
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})

        print(f"DEBUG: Using token for user: {github_config.get('username', 'unknown')}")

        result = call_mcp_tool('get_repository_branches', owner=owner, repo=repo, token=github_config['token'])

        print(f"DEBUG: Tool result: {result}")

        if isinstance(result, list) and len(result) > 0:
            if result[0].get("error"):
                error_msg = result[0].get("error", "Unknown error")
                print(f"DEBUG: Error getting branches: {error_msg}")
                return jsonify({'success': False, 'error': error_msg})
            else:
                print(f"DEBUG: Successfully found {len(result)} branches")
                return jsonify({'success': True, 'branches': result})
        else:
            print("DEBUG: No branches found or empty result")
            return jsonify({'success': False, 'error': 'No branches found in repository. This might be an empty repository.'})
            
    except Exception as e:
        print(f"DEBUG: Exception in api_get_branches: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/generate-template', methods=['POST'])
def api_generate_template():
    """API endpoint for generating PR templates"""
    try:
        data = request.get_json()
        pr_type = data.get('type', 'feature')
        title = data.get('title', '')
        description = data.get('description', '')
        
        result = call_mcp_tool('generate_pr_template', type=pr_type, title=title, description=description)
        
        return jsonify({'success': True, 'template': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/quick-create-pr', methods=['POST'])
def api_quick_create_pr():
    """API endpoint for quick PR creation with templates"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        title = data.get('title')
        head = data.get('head')
        base = data.get('base', 'main')
        pr_type = data.get('type', 'feature')
        description = data.get('description', '')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('quick_create_pr', 
                              owner=owner, repo=repo, title=title, 
                              head=head, base=base, type=pr_type, 
                              description=description, token=github_config['token'])
        
        if isinstance(result, dict) and result.get('success'):
            return jsonify(result)
        else:
            return jsonify({'success': False, 'error': result})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/github/get-repo-info', methods=['POST'])
def api_get_repo_info():
    """API endpoint for getting repository information"""
    try:
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')
        
        # Get token from config
        github_config = load_github_config()
        if not github_config or not github_config.get('token'):
            return jsonify({'success': False, 'error': 'GitHub token not configured. Please login first.'})
        
        result = call_mcp_tool('get_repository_info', owner=owner, repo=repo, token=github_config['token'])
        
        if isinstance(result, dict) and not result.get("error"):
            return jsonify({'success': True, 'repository': result})
        else:
            return jsonify({'success': False, 'error': result.get("error", "Unknown error") if isinstance(result, dict) else str(result)})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("🌐 Starting Email Agent Web Application...")
    print("📧 Access the application at: http://localhost:5001")
    print("🔧 Make sure Gmail SMTP is configured before sending emails")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 