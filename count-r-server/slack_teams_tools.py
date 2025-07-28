import os
import json
import requests
from typing import Dict, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackTools:
    """Tools for posting updates and alerts to Slack channels"""
    
    def __init__(self):
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_base_url = "https://slack.com/api"
        
    def post_message(self, channel: str, message: str, thread_ts: Optional[str] = None) -> Dict:
        """
        Post a message to a Slack channel
        
        Args:
            channel: Channel name or ID (e.g., "#general" or "C1234567890")
            message: Message text to post
            thread_ts: Optional timestamp to reply in a thread
            
        Returns:
            Dict with status and response details
        """
        if not self.slack_token:
            return {
                "status": "error",
                "message": "SLACK_BOT_TOKEN environment variable not set"
            }
            
        try:
            url = f"{self.slack_base_url}/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.slack_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "channel": channel,
                "text": message
            }
            
            if thread_ts:
                payload["thread_ts"] = thread_ts
                
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response_data = response.json()
            
            if response_data.get("ok"):
                return {
                    "status": "success",
                    "message": f"Message posted to {channel}",
                    "ts": response_data.get("ts"),
                    "channel": response_data.get("channel")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Slack API error: {response_data.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Error posting to Slack: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post message: {str(e)}"
            }
    
    def post_alert(self, channel: str, title: str, message: str, severity: str = "info") -> Dict:
        """
        Post an alert message with formatting to Slack
        
        Args:
            channel: Channel name or ID
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error, success)
            
        Returns:
            Dict with status and response details
        """
        severity_icons = {
            "info": "ℹ️",
            "warning": "⚠️", 
            "error": "🚨",
            "success": "✅"
        }
        
        icon = severity_icons.get(severity, "ℹ️")
        formatted_message = f"{icon} *{title}*\n{message}"
        
        return self.post_message(channel, formatted_message)
    
    def post_rich_message(self, channel: str, blocks: List[Dict]) -> Dict:
        """
        Post a rich message with Slack blocks
        
        Args:
            channel: Channel name or ID
            blocks: List of Slack block objects
            
        Returns:
            Dict with status and response details
        """
        if not self.slack_token:
            return {
                "status": "error",
                "message": "SLACK_BOT_TOKEN environment variable not set"
            }
            
        try:
            url = f"{self.slack_base_url}/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.slack_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "channel": channel,
                "blocks": blocks
            }
                
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response_data = response.json()
            
            if response_data.get("ok"):
                return {
                    "status": "success",
                    "message": f"Rich message posted to {channel}",
                    "ts": response_data.get("ts"),
                    "channel": response_data.get("channel")
                }
            else:
                return {
                    "status": "error",
                    "message": f"Slack API error: {response_data.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Error posting rich message to Slack: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post rich message: {str(e)}"
            }
    
    def list_channels(self) -> Dict:
        """
        List all accessible Slack channels
        
        Returns:
            Dict with list of channels
        """
        if not self.slack_token:
            return {
                "status": "error",
                "message": "SLACK_BOT_TOKEN environment variable not set"
            }
            
        try:
            url = f"{self.slack_base_url}/conversations.list"
            headers = {
                "Authorization": f"Bearer {self.slack_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "types": "public_channel,private_channel",
                "limit": 1000
            }
                
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response_data = response.json()
            
            if response_data.get("ok"):
                channels = []
                for channel in response_data.get("channels", []):
                    channels.append({
                        "id": channel.get("id"),
                        "name": channel.get("name"),
                        "is_private": channel.get("is_private", False),
                        "member_count": channel.get("num_members", 0)
                    })
                
                return {
                    "status": "success",
                    "channels": channels,
                    "count": len(channels)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Slack API error: {response_data.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Error listing Slack channels: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to list channels: {str(e)}"
            }


class TeamsTools:
    """Tools for posting updates and alerts to Microsoft Teams channels"""
    
    def __init__(self):
        self.teams_webhook_urls = {}
        self._load_webhook_config()
        
    def _load_webhook_config(self):
        """Load Teams webhook URLs from environment or config file"""
        # Try to load from environment variables
        webhook_config = os.getenv('TEAMS_WEBHOOKS')
        if webhook_config:
            try:
                self.teams_webhook_urls = json.loads(webhook_config)
            except json.JSONDecodeError:
                logger.warning("Invalid TEAMS_WEBHOOKS environment variable format")
        
        # Try to load from config file
        config_file = os.path.join(os.path.dirname(__file__), 'teams_config.json')
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.teams_webhook_urls.update(config.get('webhooks', {}))
            except Exception as e:
                logger.warning(f"Could not load Teams config file: {str(e)}")
    
    def post_message(self, channel: str, message: str) -> Dict:
        """
        Post a message to a Teams channel
        
        Args:
            channel: Channel name (must have webhook configured)
            message: Message text to post
            
        Returns:
            Dict with status and response details
        """
        webhook_url = self.teams_webhook_urls.get(channel)
        if not webhook_url:
            return {
                "status": "error",
                "message": f"No webhook configured for channel '{channel}'. Available channels: {list(self.teams_webhook_urls.keys())}"
            }
            
        try:
            payload = {
                "text": message
            }
            
            response = requests.post(webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Message posted to Teams channel '{channel}'",
                    "channel": channel
                }
            else:
                return {
                    "status": "error",
                    "message": f"Teams webhook error: HTTP {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error posting to Teams: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post message: {str(e)}"
            }
    
    def post_alert(self, channel: str, title: str, message: str, severity: str = "info") -> Dict:
        """
        Post an alert message with formatting to Teams
        
        Args:
            channel: Channel name
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, error, success)
            
        Returns:
            Dict with status and response details
        """
        severity_colors = {
            "info": "0076D7",
            "warning": "FF8C00",
            "error": "D13438",
            "success": "107C10"
        }
        
        color = severity_colors.get(severity, "0076D7")
        
        webhook_url = self.teams_webhook_urls.get(channel)
        if not webhook_url:
            return {
                "status": "error",
                "message": f"No webhook configured for channel '{channel}'. Available channels: {list(self.teams_webhook_urls.keys())}"
            }
            
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": color,
                "title": title,
                "text": message,
                "sections": [
                    {
                        "activityTitle": title,
                        "activityText": message,
                        "markdown": True
                    }
                ]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Alert posted to Teams channel '{channel}'",
                    "channel": channel,
                    "severity": severity
                }
            else:
                return {
                    "status": "error",
                    "message": f"Teams webhook error: HTTP {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error posting alert to Teams: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post alert: {str(e)}"
            }
    
    def post_rich_message(self, channel: str, title: str, text: str, facts: Optional[List[Dict]] = None) -> Dict:
        """
        Post a rich message with facts to Teams
        
        Args:
            channel: Channel name
            title: Message title
            text: Message text
            facts: Optional list of fact objects with name and value
            
        Returns:
            Dict with status and response details
        """
        webhook_url = self.teams_webhook_urls.get(channel)
        if not webhook_url:
            return {
                "status": "error",
                "message": f"No webhook configured for channel '{channel}'. Available channels: {list(self.teams_webhook_urls.keys())}"
            }
            
        try:
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "title": title,
                "text": text,
                "sections": [
                    {
                        "activityTitle": title,
                        "activityText": text,
                        "markdown": True
                    }
                ]
            }
            
            if facts:
                payload["sections"][0]["facts"] = facts
            
            response = requests.post(webhook_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Rich message posted to Teams channel '{channel}'",
                    "channel": channel
                }
            else:
                return {
                    "status": "error",
                    "message": f"Teams webhook error: HTTP {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error posting rich message to Teams: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to post rich message: {str(e)}"
            }
    
    def list_channels(self) -> Dict:
        """
        List all configured Teams channels
        
        Returns:
            Dict with list of configured channels
        """
        channels = []
        for channel_name, webhook_url in self.teams_webhook_urls.items():
            channels.append({
                "name": channel_name,
                "webhook_configured": True,
                "webhook_url": webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url
            })
        
        return {
            "status": "success",
            "channels": channels,
            "count": len(channels)
        }


# Initialize global instances
slack_tools = SlackTools()
teams_tools = TeamsTools() 