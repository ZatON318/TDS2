# � TDS2 - Telegram Data Storage v2

**TDS2** (Telegram Data Storage System v2) is a powerful Python library that leverages Telegram's infrastructure as a cloud storage backend. Upload, download, manage, and track files using Telegram channels with automatic logging and progress tracking.

## 🌟 Features

- **📤 File Upload**: Upload files of any size to Telegram channels with progress bars
- **📥 File Download**: Download files using message IDs
- **🗑️ File Management**: Delete messages and manage your storage
- **📊 Automatic Logging**: Optional JSON-based logging with metadata tracking
- **📈 Storage Analytics**: Track total storage size, file counts, and deletion status
- **⚡ Async Support**: Built on Telethon for efficient async operations
- **🔒 Private Storage**: Use your own Telegram channels as secure cloud storage

## 📦 Installation

```bash
pip install tds2
```

## 🚀 Quick Start

```python
from tds2 import tds2client

# Initialize client (without logging)
client = tds2client(
    api_id='YOUR_API_ID',
    api_hash='YOUR_API_HASH',
    group_chat_id='YOUR_CHANNEL_ID'
)

# Upload a file
response = client.upload('/path/to/file.pdf')
print(f"Uploaded! Message ID: {response.id}")

# Download a file
file_path = client.download(response.id)
print(f"Downloaded to: {file_path}")

# Delete a file
client.delete(response.id)

# Get last message ID
last_id = client.get_last()
```

## 📝 With Logging Enabled

Enable automatic JSON logging to track all uploads and deletions:

```python
# Initialize client with logging
client = tds2client(
    api_id='YOUR_API_ID',
    api_hash='YOUR_API_HASH', 
    group_chat_id='YOUR_CHANNEL_ID',
    logfile='my_storage.json'
)

# All operations are now automatically logged
response = client.upload('document.pdf')

# Get storage statistics
summary = client.get_log_summary()
print(f"Total storage used: {summary['total_size_mb']} MB")
print(f"Active files: {summary['active_files']}")
print(f"Deleted files: {summary['deleted_files']}")
```

## 🔑 Getting Started

### 1. Get Telegram API Credentials

1. Visit https://my.telegram.org
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Save your `api_id` and `api_hash`

### 2. Create a Telegram Channel

1. Create a new Telegram channel (private or public)
2. Get the channel ID (use a bot like @raw_data_bot or @username_to_id_bot)
3. Make sure your account has admin rights in the channel

### 3. Use TDS2

```python
from tds2 import tds2client

client = tds2client(
    api_id='12345678',
    api_hash='abcdef1234567890abcdef1234567890',
    group_chat_id='-1001234567890',
    logfile='storage.json'  # Optional
)
```

## 📚 Core Functions

### `upload(file_path)`
Upload a file to your Telegram channel. Returns a message object with the upload details.

### `download(message_id)`
Download a file using its Telegram message ID. Returns the path to the downloaded file.

### `delete(message_id)`
Delete a message/file from the Telegram channel.

### `get_last()`
Get the message ID of the last message in the channel.

### `get_log_summary()`
Get statistics about your storage (only available when logging is enabled).

## 🗂️ JSON Logging Structure

When logging is enabled, TDS2 creates a JSON file with the following structure:

```json
{
  "total_size": 1048576000,
  "files": {
    "123": {
      "message_id": 123,
      "file_name": "document.pdf",
      "size_bytes": 1048576,
      "size_mb": 1.0,
      "upload_date": "2025-12-24T10:30:00.000000",
      "deletion_date": null,
      "deleted": false
    }
  }
}
```

### Log Fields Explained:
- **`total_size`**: Total bytes of non-deleted files
- **`message_id`**: Telegram message ID
- **`file_name`**: Original filename
- **`size_bytes`**: File size in bytes
- **`size_mb`**: File size in megabytes (rounded)
- **`upload_date`**: ISO 8601 timestamp of upload
- **`deletion_date`**: ISO 8601 timestamp of deletion (if deleted)
- **`deleted`**: Boolean indicating deletion status

## 💡 Use Cases

- **Personal Cloud Storage**: Use Telegram as unlimited cloud storage
- **Backup System**: Automated backup of important files
- **File Sharing**: Share large files through Telegram
- **Media Archive**: Store photos, videos, and documents
- **Data Migration**: Transfer files between systems
- **Automated Workflows**: Integrate with scripts and automation

## ⚙️ Advanced Configuration

### Custom Session Name

The library uses Telethon's session management. By default, it creates a session file named `anon.session`. This file stores authentication data so you don't need to log in every time.

### Progress Tracking

All uploads automatically display a progress bar using `tqdm`, showing real-time upload speed and ETA.

## 🔒 Security Considerations

- Keep your `api_id` and `api_hash` secure
- Use private channels for sensitive data
- Consider encrypting files before upload for additional security
- The session file contains authentication data - keep it secure
- Logging files may contain sensitive filenames - protect them appropriately

## 📊 Storage Limits

- Telegram allows files up to **2GB per file**
- No limit on total storage (as of 2025)
- Upload/download speeds depend on your connection and Telegram's servers

## 🛠️ Requirements

- Python 3.7+
- telethon
- tqdm

All dependencies are automatically installed with pip.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Documentation](FUNCTIONS.md) - Detailed function documentation
- [Telethon Documentation](https://docs.telethon.dev/) - Underlying Telegram library
- [Telegram API](https://core.telegram.org/) - Official Telegram API docs

## ⚠️ Disclaimer

This library is for educational and personal use. Respect Telegram's Terms of Service and API usage limits. The developers are not responsible for any misuse of this library.

## 📞 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ by the TDS2 community**
