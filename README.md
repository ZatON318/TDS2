# TDS2
TDS2 - Telegram Data Storage System. 
TDS2 is python library that use telegram api to manage files in your channels. 
This system also have a webgui that can be used as your private cloud that stores files in telegram channels

## Example use
```
from tds2 import tdsclient

client = tdsclient(API_ID, API_HASH, channel_id)
message_id = client.upload("/path/to/file")

client.download(message_id)
```
