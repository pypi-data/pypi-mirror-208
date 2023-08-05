# ViaZoom

An API wrapper for Zoom.

## Installation

Install viazoom with pip

```bash
  pip install viazoom
```

## Usage/Examples

```python
from viazoom import ZoomOAuthClient

client = ZoomOAuthClient(account_id="YOUR_ACCOUNT_ID", client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET")
access_token = client.get_access_token()
print(access_token)
```
