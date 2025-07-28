# Slack/Teams Integration Tools

This module provides tools for posting updates and alerts to Slack and Microsoft Teams channels through your MCP server.

## Available Tools

### Slack Tools

1. **slack_post_message** - Post a simple message to a Slack channel
2. **slack_post_alert** - Post a formatted alert message with severity levels
3. **slack_post_rich_message** - Post rich messages using Slack blocks
4. **slack_list_channels** - List all accessible Slack channels

### Teams Tools

1. **teams_post_message** - Post a simple message to a Teams channel
2. **teams_post_alert** - Post a formatted alert message with severity levels
3. **teams_post_rich_message** - Post rich messages with facts
4. **teams_list_channels** - List all configured Teams channels

## Setup Instructions

### Slack Setup

1. **Create a Slack App:**
   - Go to https://api.slack.com/apps
   - Click "Create New App" → "From scratch"
   - Give your app a name and select your workspace

2. **Configure Bot Token Scopes:**
   - Go to "OAuth & Permissions" in your app settings
   - Add the following scopes:
     - `chat:write` - Send messages to channels
     - `channels:read` - View basic channel info
     - `groups:read` - View private channels
     - `im:read` - View direct messages
     - `mpim:read` - View group direct messages

3. **Install the App:**
   - Click "Install to Workspace"
   - Authorize the app

4. **Get the Bot Token:**
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)
   - Set it as an environment variable:
     ```bash
     export SLACK_BOT_TOKEN="xoxb-your-token-here"
     ```

### Teams Setup

1. **Create Incoming Webhooks:**
   - In Teams, go to the channel where you want to post messages
   - Click the "..." menu → "Connectors"
   - Find "Incoming Webhook" and click "Configure"
   - Give it a name and optionally an icon
   - Click "Create"
   - Copy the webhook URL

2. **Configure Webhook URLs:**
   
   **Option A: Environment Variable**
   ```bash
   export TEAMS_WEBHOOKS='{"general":"https://your-org.webhook.office.com/webhookb2/url1","alerts":"https://your-org.webhook.office.com/webhookb2/url2"}'
   ```
   
   **Option B: Configuration File**
   Edit `teams_config.json`:
   ```json
   {
     "webhooks": {
       "general": "https://your-org.webhook.office.com/webhookb2/your-webhook-url-1",
       "alerts": "https://your-org.webhook.office.com/webhookb2/your-webhook-url-2",
       "dev-team": "https://your-org.webhook.office.com/webhookb2/your-webhook-url-3"
     }
   }
   ```

## Usage Examples

### Slack Examples

**Simple Message:**
```json
{
  "name": "slack_post_message",
  "arguments": {
    "channel": "#general",
    "message": "Hello from the MCP server!"
  }
}
```

**Alert Message:**
```json
{
  "name": "slack_post_alert",
  "arguments": {
    "channel": "#alerts",
    "title": "System Alert",
    "message": "Database connection restored",
    "severity": "success"
  }
}
```

**Rich Message with Blocks:**
```json
{
  "name": "slack_post_rich_message",
  "arguments": {
    "channel": "#general",
    "blocks_json": "[{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"*Hello!* This is a rich message.\"}},{\"type\":\"divider\"},{\"type\":\"section\",\"fields\":[{\"type\":\"mrkdwn\",\"text\":\"*Status:* Online\"},{\"type\":\"mrkdwn\",\"text\":\"*Version:* 1.0.0\"}]}]"
  }
}
```

**List Channels:**
```json
{
  "name": "slack_list_channels",
  "arguments": {}
}
```

### Teams Examples

**Simple Message:**
```json
{
  "name": "teams_post_message",
  "arguments": {
    "channel": "general",
    "message": "Hello from the MCP server!"
  }
}
```

**Alert Message:**
```json
{
  "name": "teams_post_alert",
  "arguments": {
    "channel": "alerts",
    "title": "System Alert",
    "message": "Database connection restored",
    "severity": "success"
  }
}
```

**Rich Message with Facts:**
```json
{
  "name": "teams_post_rich_message",
  "arguments": {
    "channel": "general",
    "title": "System Status",
    "text": "Current system status report",
    "facts_json": "[{\"name\":\"Status\",\"value\":\"Online\"},{\"name\":\"Version\",\"value\":\"1.0.0\"},{\"name\":\"Uptime\",\"value\":\"99.9%\"}]"
  }
}
```

**List Channels:**
```json
{
  "name": "teams_list_channels",
  "arguments": {}
}
```

## Severity Levels

Both Slack and Teams support the following severity levels:

- **info** (default) - Blue color, ℹ️ icon
- **warning** - Orange color, ⚠️ icon  
- **error** - Red color, 🚨 icon
- **success** - Green color, ✅ icon

## Error Handling

All tools return a consistent response format:

**Success:**
```json
{
  "status": "success",
  "message": "Message posted to #general",
  "channel": "C1234567890",
  "ts": "1234567890.123456"
}
```

**Error:**
```json
{
  "status": "error",
  "message": "SLACK_BOT_TOKEN environment variable not set"
}
```

## Security Notes

- Keep your Slack bot tokens and Teams webhook URLs secure
- Never commit tokens or webhook URLs to version control
- Use environment variables or secure configuration management
- Regularly rotate your tokens and webhook URLs
- Monitor your app's usage and permissions

## Troubleshooting

### Common Issues

1. **"SLACK_BOT_TOKEN environment variable not set"**
   - Make sure you've set the `SLACK_BOT_TOKEN` environment variable
   - Verify the token starts with `xoxb-`

2. **"No webhook configured for channel"**
   - Check your `teams_config.json` file or `TEAMS_WEBHOOKS` environment variable
   - Verify the channel name matches exactly

3. **"Slack API error: channel_not_found"**
   - Make sure the bot is invited to the channel
   - Check that the channel name or ID is correct

4. **"Teams webhook error: HTTP 403"**
   - Verify the webhook URL is correct and not expired
   - Check that the webhook is still active in Teams

### Testing

You can test the tools using curl or any MCP client:

```bash
# Test Slack message
curl -X POST http://localhost:5000/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "name": "slack_post_message",
    "arguments": {
      "channel": "#general",
      "message": "Test message from MCP server"
    }
  }'
```

## Dependencies

Make sure you have the required Python packages:

```bash
pip install requests
```

The `requests` library is used for HTTP calls to Slack and Teams APIs. 