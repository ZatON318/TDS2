# 📚 TDS2 Function Documentation

Complete reference for all TDS2 functions with detailed explanations, parameters, return values, and examples.

## 📑 Table of Contents

- [Class: tds2client](#class-tds2client)
- [Initialization](#initialization)
- [Public Methods](#public-methods)
  - [upload()](#upload)
  - [download()](#download)
  - [delete()](#delete)
  - [get_last()](#get_last)
  - [get_log_summary()](#get_log_summary)
- [Async Methods (Internal)](#async-methods-internal)
  - [upload_file()](#upload_file)
  - [download_file()](#download_file)
  - [delete_message()](#delete_message)
  - [get_last_massage_id()](#get_last_massage_id)
- [Private Methods](#private-methods)
  - [_load_log()](#_load_log)
  - [_save_log()](#_save_log)
  - [_calculate_total_size()](#_calculate_total_size)
  - [_log_upload()](#_log_upload)
  - [_log_deletion()](#_log_deletion)

---

## Class: tds2client

The main class for interacting with Telegram as a storage backend.

```python
from tds2 import tds2client
```

---

## Initialization

### `tds2client(api_id, api_hash, group_chat_id, logfile=None)`

Initialize a new TDS2 client instance to manage files in a Telegram channel.

#### Parameters:

- **`api_id`** (str or int): Your Telegram API ID obtained from https://my.telegram.org
  - Example: `'12345678'` or `12345678`
  
- **`api_hash`** (str): Your Telegram API hash obtained from https://my.telegram.org
  - Example: `'abcdef1234567890abcdef1234567890'`
  
- **`group_chat_id`** (str or int): The Telegram channel/group ID where files will be stored
  - Format: `'-1001234567890'` or `-1001234567890`
  - Must be a channel where you have admin/posting rights
  
- **`logfile`** (str, optional): Path to JSON file for automatic logging of operations
  - Default: `None` (logging disabled)
  - Example: `'storage.json'`, `'logs/tds2_log.json'`
  - If enabled, automatically tracks uploads, deletions, and storage statistics

#### Returns:
- `tds2client` instance

#### Attributes Created:
- `self.client`: Telethon TelegramClient instance
- `self.safe`: Parsed integer channel ID
- `self.logfile`: Path to log file (or None)
- `self.bandwidth_safety`: Class variable (default: False)

#### Example:

```python
from tds2 import tds2client

# Basic initialization (no logging)
client = tds2client(
    api_id='12345678',
    api_hash='abcdef1234567890abcdef1234567890',
    group_chat_id='-1001234567890'
)

# With logging enabled
client = tds2client(
    api_id='12345678',
    api_hash='abcdef1234567890abcdef1234567890',
    group_chat_id='-1001234567890',
    logfile='my_storage.json'
)

# Using integer values
client = tds2client(
    api_id=12345678,
    api_hash='abcdef1234567890abcdef1234567890',
    group_chat_id=-1001234567890,
    logfile='storage_log.json'
)
```

#### Notes:
- Creates a session file named `anon.session` in the current directory
- First run will prompt for phone number and verification code
- Session file persists authentication across runs
- The channel must exist and you must have posting permissions

---

## Public Methods

### `upload(file_path)`

Upload a file to the Telegram channel. This is a synchronous wrapper around the async `upload_file()` method.

#### Parameters:

- **`file_path`** (str): Path to the file to upload
  - Can be absolute: `'/home/user/document.pdf'`
  - Can be relative: `'files/image.jpg'`
  - File must exist and be readable

#### Returns:

- **`telegram.Message`** object containing:
  - `.id`: Message ID (integer) - use this for download/delete operations
  - `.file`: File information
  - `.date`: Upload timestamp
  - `.media`: Media object with file details
  - And many other Telegram message attributes

#### Raises:

- `FileNotFoundError`: If the specified file doesn't exist
- `PermissionError`: If the file cannot be read
- `TelegramError`: If upload fails (network, API limits, etc.)

#### Behavior:

1. Validates file exists
2. Starts Telegram client session
3. Uploads file with progress bar (tqdm)
4. If logging enabled: records upload metadata
5. Disconnects from Telegram
6. Returns message object

#### Example:

```python
# Upload a file
response = client.upload('/path/to/document.pdf')
print(f"Uploaded successfully!")
print(f"Message ID: {response.id}")
print(f"File name: {response.file.name}")
print(f"File size: {response.file.size} bytes")

# Save message ID for later use
message_id = response.id

# Upload relative path
response = client.upload('photo.jpg')

# Upload with error handling
try:
    response = client.upload('large_video.mp4')
    print(f"Upload successful: {response.id}")
except FileNotFoundError:
    print("File not found!")
except Exception as e:
    print(f"Upload failed: {e}")
```

#### Progress Bar:

During upload, you'll see a progress bar like:
```
Uploading: 100%|████████████| 1.05M/1.05M [00:03<00:00, 342kB/s]
```

#### Logged Data (if logging enabled):

```json
{
  "message_id": 123,
  "file_name": "document.pdf",
  "size_bytes": 1048576,
  "size_mb": 1.0,
  "upload_date": "2025-12-24T10:30:00.123456",
  "deletion_date": null,
  "deleted": false
}
```

---

### `download(message_id)`

Download a file from Telegram using its message ID. This is a synchronous wrapper around the async `download_file()` method.

#### Parameters:

- **`message_id`** (int): The Telegram message ID of the file to download
  - Obtained from `upload()` return value
  - Or from Telegram channel directly

#### Returns:

- **`str`**: Path to the downloaded file
  - Format: `'downloads/filename.ext'` (default Telethon behavior)
  - Returns `None` if message has no media

#### Raises:

- `ValueError`: If message_id is invalid
- `TelegramError`: If download fails or message doesn't exist

#### Behavior:

1. Starts Telegram client session
2. Retrieves message by ID from the channel
3. Checks if message contains media
4. Downloads media to default location
5. Disconnects from Telegram
6. Returns file path

#### Example:

```python
# Download a file
file_path = client.download(123)
print(f"Downloaded to: {file_path}")

# Download with error handling
try:
    file_path = client.download(message_id)
    if file_path:
        print(f"File saved at: {file_path}")
        # Process the file
        with open(file_path, 'rb') as f:
            data = f.read()
    else:
        print("Message has no media")
except Exception as e:
    print(f"Download failed: {e}")

# Download multiple files
message_ids = [123, 124, 125]
for msg_id in message_ids:
    path = client.download(msg_id)
    print(f"Downloaded: {path}")
```

#### Notes:

- Downloads to Telethon's default location (usually `downloads/` folder)
- Automatically creates directory if it doesn't exist
- Original filename is preserved
- If file exists, may be overwritten or renamed (Telethon behavior)
- No progress bar for downloads (Telethon limitation)

---

### `delete(message_id)`

Delete a message (and its file) from the Telegram channel. This is a synchronous wrapper around the async `delete_message()` method.

#### Parameters:

- **`message_id`** (int): The Telegram message ID to delete
  - Must be a message in your configured channel
  - Must have admin/delete permissions

#### Returns:

- **`telegram.messages.AffectedMessages`** object:
  - Contains information about the deletion operation
  - Usually not needed - operation success can be assumed if no exception

#### Raises:

- `ValueError`: If message_id is invalid  
- `TelegramError`: If deletion fails (permissions, message doesn't exist, etc.)

#### Behavior:

1. Starts Telegram client session
2. Deletes the specified message from the channel
3. Prints confirmation: `"Message {message_id} deleted"`
4. If logging enabled: updates log to mark file as deleted
5. Disconnects from Telegram
6. Returns deletion response

#### Example:

```python
# Delete a file
client.delete(123)
print("File deleted successfully")

# Delete with error handling
try:
    client.delete(message_id)
    print(f"Message {message_id} deleted")
except Exception as e:
    print(f"Deletion failed: {e}")

# Delete multiple files
message_ids = [123, 124, 125]
for msg_id in message_ids:
    try:
        client.delete(msg_id)
        print(f"Deleted: {msg_id}")
    except Exception as e:
        print(f"Failed to delete {msg_id}: {e}")

# Upload, then delete
response = client.upload('temp_file.txt')
# ... do something ...
client.delete(response.id)  # Clean up
```

#### Logged Data Update (if logging enabled):

After deletion, the log entry is updated:
```json
{
  "message_id": 123,
  "deleted": true,
  "deletion_date": "2025-12-24T11:00:00.123456"
}
```

The `total_size` field is automatically recalculated to exclude deleted files.

#### Notes:

- Deletion is permanent and cannot be undone
- Removes both the message and the uploaded file
- Requires appropriate permissions in the channel
- Does not delete the log entry, only marks it as deleted

---

### `get_last()`

Get the message ID of the last (most recent) message in the channel. This is a synchronous wrapper around the async `get_last_massage_id()` method.

#### Parameters:

None

#### Returns:

- **`int`**: Message ID of the last message
- **`None`**: If the channel is empty

#### Raises:

- `TelegramError`: If unable to fetch messages (permissions, network, etc.)

#### Behavior:

1. Starts Telegram client session
2. Fetches the last message (limit=1) from the channel
3. Extracts message ID if message exists
4. Disconnects from Telegram
5. Returns message ID or None

#### Example:

```python
# Get last message ID
last_id = client.get_last()
if last_id:
    print(f"Last message ID: {last_id}")
else:
    print("Channel is empty")

# Use to track uploads
before = client.get_last()
client.upload('file.txt')
after = client.get_last()
print(f"New message ID: {after}")
assert after > before  # New message has higher ID

# Download the last uploaded file
last_msg = client.get_last()
if last_msg:
    file_path = client.download(last_msg)
    print(f"Downloaded last file: {file_path}")

# Check if channel has any files
if client.get_last() is None:
    print("Channel is empty, uploading first file...")
    client.upload('initial_file.txt')
```

#### Use Cases:

- Verify successful upload (message ID increased)
- Download most recent file
- Check if channel is empty
- Track the latest state of your storage
- Implement sequential processing of uploads

#### Notes:

- Message IDs are sequential integers
- Deleted messages create gaps in the sequence
- Returns the highest message ID, not necessarily a file message
- Could be any type of message (file, text, media, etc.)

---

### `get_log_summary()`

Get a summary of storage statistics from the log file. Only available when logging is enabled.

#### Parameters:

None

#### Returns:

- **`dict`** with storage statistics (if logging enabled):
  ```python
  {
      "total_size": 1048576000,        # Total bytes (non-deleted files)
      "total_size_mb": 1000.0,         # Total MB (non-deleted files)
      "active_files": 15,              # Number of non-deleted files
      "deleted_files": 5,              # Number of deleted files
      "total_files": 20                # Total files (active + deleted)
  }
  ```

- **`None`**: If logging is disabled (`logfile=None`)

#### Raises:

- `FileNotFoundError`: If log file doesn't exist (should not happen normally)
- `json.JSONDecodeError`: If log file is corrupted

#### Behavior:

1. Checks if logging is enabled
2. Loads log file
3. Counts active files (deleted=false)
4. Counts deleted files (deleted=true)
5. Returns total size of active files only
6. Returns summary dictionary

#### Example:

```python
# Get storage summary
summary = client.get_log_summary()

if summary:
    print("=" * 50)
    print("Storage Summary")
    print("=" * 50)
    print(f"Total Storage: {summary['total_size_mb']:.2f} MB")
    print(f"Total Storage: {summary['total_size']:,} bytes")
    print(f"Active Files: {summary['active_files']}")
    print(f"Deleted Files: {summary['deleted_files']}")
    print(f"Total Files Tracked: {summary['total_files']}")
    print("=" * 50)
else:
    print("Logging is not enabled")

# Check storage before upload
summary = client.get_log_summary()
if summary and summary['total_size_mb'] > 1000:
    print("Warning: Storage exceeds 1GB!")

# Calculate average file size
summary = client.get_log_summary()
if summary and summary['active_files'] > 0:
    avg_size = summary['total_size'] / summary['active_files']
    print(f"Average file size: {avg_size / (1024*1024):.2f} MB")

# Monitor storage growth
import time
while True:
    summary = client.get_log_summary()
    print(f"Storage: {summary['total_size_mb']:.2f} MB", end='\r')
    time.sleep(60)  # Update every minute
```

#### Summary Fields Explained:

- **`total_size`**: Sum of all non-deleted file sizes in bytes
  - Only counts files where `deleted=false`
  - Automatically recalculated after deletions
  
- **`total_size_mb`**: Same as total_size but in megabytes
  - Rounded to 2 decimal places
  - More human-readable format

- **`active_files`**: Count of files that haven't been deleted
  - `deleted=false` in the log
  - Represents current storage

- **`deleted_files`**: Count of files that have been deleted
  - `deleted=true` in the log
  - Historical record

- **`total_files`**: Sum of active and deleted files
  - Total number of uploads tracked
  - Includes all historical data

#### Notes:

- Returns `None` if logging wasn't enabled during initialization
- Deleted files don't count toward total_size
- Log file persists even after deletions (for audit trail)
- Summary is calculated on-demand (not cached)
- Thread-safe for reading

---

## Async Methods (Internal)

These methods are called internally by the public methods. You can use them directly if you're working in an async context, but most users should use the synchronous public methods instead.

### `async upload_file(file_path)`

Async version of `upload()`. Handles the actual file upload to Telegram.

#### Parameters:

- **`file_path`** (str): Path to the file to upload

#### Returns:

- `telegram.Message` object with upload details

#### Behavior:

1. Starts Telegram client (`await self.client.start()`)
2. Gets file size for progress bar
3. Creates progress callback function
4. Uploads file with `tqdm` progress bar
5. Calls `_log_upload()` to record metadata (if logging enabled)
6. Disconnects client
7. Returns message object

#### Example (async context):

```python
import asyncio
from tds2 import tds2client

async def upload_multiple():
    client = tds2client(api_id, api_hash, channel_id, logfile='log.json')
    
    files = ['file1.txt', 'file2.pdf', 'file3.jpg']
    for file in files:
        response = await client.upload_file(file)
        print(f"Uploaded {file}: message ID {response.id}")

asyncio.run(upload_multiple())
```

#### Progress Callback:

The internal progress callback updates the tqdm bar:
```python
def callback(current, total):
    bar.update(current - bar.n)
```

---

### `async download_file(message_id)`

Async version of `download()`. Handles the actual file download from Telegram.

#### Parameters:

- **`message_id`** (int): Message ID to download

#### Returns:

- `str`: Path to downloaded file, or `None` if no media

#### Behavior:

1. Starts Telegram client
2. Fetches message by ID
3. Checks for media
4. Downloads media if present
5. Disconnects client
6. Returns file path

#### Example (async context):

```python
import asyncio

async def download_multiple():
    client = tds2client(api_id, api_hash, channel_id)
    
    message_ids = [123, 124, 125]
    for msg_id in message_ids:
        path = await client.download_file(msg_id)
        print(f"Downloaded to: {path}")

asyncio.run(download_multiple())
```

---

### `async delete_message(message_id)`

Async version of `delete()`. Handles the actual message deletion.

#### Parameters:

- **`message_id`** (int): Message ID to delete

#### Returns:

- Telegram deletion response object

#### Behavior:

1. Starts Telegram client
2. Deletes message
3. Prints confirmation
4. Calls `_log_deletion()` (if logging enabled)
5. Disconnects client
6. Returns response

---

### `async get_last_massage_id()`

Async version of `get_last()`. Fetches the last message ID.

**Note:** There's a typo in the method name (`massage` instead of `message`). This may be fixed in future versions.

#### Parameters:

None

#### Returns:

- `int`: Last message ID, or `None` if channel is empty

#### Behavior:

1. Starts Telegram client
2. Gets last message (limit=1)
3. Extracts ID if message exists
4. Disconnects client
5. Returns ID or None

---

## Private Methods

These methods handle logging functionality internally. They should not be called directly by users.

### `_load_log()`

Load the JSON log file from disk.

#### Returns:

- `dict`: Parsed JSON log data
- `None`: If logging is disabled
- `dict`: Empty log structure if file doesn't exist:
  ```python
  {"total_size": 0, "files": {}}
  ```

#### Behavior:

- Checks if logging is enabled
- Reads and parses JSON file
- Creates default structure if file doesn't exist

---

### `_save_log(log_data)`

Save the log data structure to the JSON file.

#### Parameters:

- **`log_data`** (dict): Log data structure to save

#### Behavior:

- Checks if logging is enabled
- Writes JSON file with indent=2 (pretty print)
- Creates file if it doesn't exist

---

### `_calculate_total_size(log_data)`

Calculate the total size of all non-deleted files.

#### Parameters:

- **`log_data`** (dict): Log data structure

#### Returns:

- `int`: Total bytes of files where `deleted=false`

#### Behavior:

- Iterates through all files in log
- Sums `size_bytes` where `deleted=false`
- Skips deleted files

---

### `_log_upload(message_id, file_path)`

Record an upload operation in the log file.

#### Parameters:

- **`message_id`** (int): Telegram message ID
- **`file_path`** (str): Path to uploaded file

#### Behavior:

1. Returns immediately if logging disabled
2. Loads current log
3. Gets file size
4. Creates log entry with metadata
5. Recalculates total_size
6. Saves updated log

#### Log Entry Created:

```json
{
  "message_id": 123,
  "file_name": "document.pdf",
  "size_bytes": 1048576,
  "size_mb": 1.0,
  "upload_date": "2025-12-24T10:30:00.123456",
  "deletion_date": null,
  "deleted": false
}
```

---

### `_log_deletion(message_id)`

Record a deletion operation in the log file.

#### Parameters:

- **`message_id`** (int): Telegram message ID that was deleted

#### Behavior:

1. Returns immediately if logging disabled
2. Loads current log
3. Finds file entry by message_id
4. Updates `deleted=true`
5. Sets `deletion_date` to current timestamp
6. Recalculates total_size (excludes this file)
7. Saves updated log

#### Log Entry Updated:

```json
{
  "message_id": 123,
  "deleted": true,
  "deletion_date": "2025-12-24T11:00:00.123456"
}
```

---

## Complete Usage Example

```python
from tds2 import tds2client
import os

# Initialize with logging
client = tds2client(
    api_id='12345678',
    api_hash='abcdef1234567890',
    group_chat_id='-1001234567890',
    logfile='storage.json'
)

# Upload files
print("Uploading files...")
files_to_upload = ['doc1.pdf', 'photo.jpg', 'video.mp4']
message_ids = []

for file in files_to_upload:
    if os.path.exists(file):
        response = client.upload(file)
        message_ids.append(response.id)
        print(f"✓ Uploaded {file}: ID {response.id}")

# Check storage
summary = client.get_log_summary()
print(f"\nStorage used: {summary['total_size_mb']:.2f} MB")
print(f"Files stored: {summary['active_files']}")

# Download a file
print("\nDownloading first file...")
path = client.download(message_ids[0])
print(f"Downloaded to: {path}")

# Get last message
last_id = client.get_last()
print(f"Last message ID: {last_id}")

# Delete a file
print("\nDeleting file...")
client.delete(message_ids[0])

# Check updated storage
summary = client.get_log_summary()
print(f"\nUpdated storage: {summary['total_size_mb']:.2f} MB")
print(f"Active files: {summary['active_files']}")
print(f"Deleted files: {summary['deleted_files']}")
```

---

## Error Handling Best Practices

```python
from tds2 import tds2client
import os

client = tds2client(api_id, api_hash, channel_id, logfile='log.json')

# Safe upload
def safe_upload(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return None
        
        response = client.upload(file_path)
        print(f"Upload successful: {response.id}")
        return response.id
        
    except PermissionError:
        print(f"Error: Cannot read file: {file_path}")
    except Exception as e:
        print(f"Upload failed: {e}")
    return None

# Safe download
def safe_download(message_id):
    try:
        path = client.download(message_id)
        if path:
            print(f"Downloaded to: {path}")
            return path
        else:
            print("No media in message")
            return None
    except Exception as e:
        print(f"Download failed: {e}")
        return None

# Safe delete
def safe_delete(message_id):
    try:
        client.delete(message_id)
        print(f"Deleted message: {message_id}")
        return True
    except Exception as e:
        print(f"Deletion failed: {e}")
        return False
```

---

## Performance Considerations

- **Upload Speed**: Limited by your internet connection and Telegram servers
- **Download Speed**: Generally faster than upload
- **Progress Tracking**: Uses tqdm, minimal performance impact
- **Logging**: JSON operations are fast, negligible overhead
- **Session Management**: Session file reduces authentication overhead
- **Async Operations**: Internally async, but wrapped for convenience

---

## Troubleshooting

### "Could not connect"
- Check internet connection
- Verify API credentials
- Ensure Telegram isn't blocked

### "Message not found"
- Message may have been deleted
- Wrong channel ID
- Invalid message ID

### "Permission denied"
- Check admin rights in channel
- Verify channel ID is correct
- Ensure bot/account has posting rights

### "File not found"
- Check file path is correct
- Use absolute paths when possible
- Verify file permissions

---

**For more information, see the [README](README.md) for general usage and examples.**
if isinstance(result, dict):
    print(f"Uploaded in {result['total_chunks']} chunks")
    print(f"File ID: {result['file_id']}")

# Upload without progress bar
message = client.upload("data.csv", show_progress=False)
```

---

### `download(file_id_or_message_id, output_dir="downloads", show_progress=True)`

Download a file from the Telegram channel. Automatically reassembles chunked files.

**Parameters:**
- `file_id_or_message_id` (str/int): File ID from storage or Telegram message ID
- `output_dir` (str, optional): Directory to save the downloaded file. Default: `"downloads"`
- `show_progress` (bool, optional): Display progress bar during download. Default: `True`

**Returns:** `str` - Absolute path to the downloaded file

**Raises:**
- `TelegramError`: If download fails or message doesn't contain a file

**Behavior:**
- Creates output directory if it doesn't exist
- For single files: Downloads directly
- For chunked files: Downloads all chunks and reassembles them
- Verifies MD5 hash for chunked files
- Displays integrity check result

**Example:**
```python
# Download by message ID
file_path = client.download(123)
print(f"Downloaded to: {file_path}")

# Download to custom directory
file_path = client.download(123, output_dir="backups")

# Download chunked file by file ID
file_path = client.download("chunked_abc123def456")

# Download without progress bar
file_path = client.download(123, show_progress=False)
```

---

### `delete(file_id_or_message_id)`

Delete a file from the Telegram channel. For chunked files, deletes all chunks. Marks file as deleted in local storage (doesn't remove the entry).

**Parameters:**
- `file_id_or_message_id` (str/int): File ID from storage or Telegram message ID

**Returns:** `bool` - `True` if successful

**Raises:**
- `TelegramError`: If deletion fails

**Behavior:**
- Deletes message(s) from Telegram channel
- Marks file as `deleted: true` in storage
- Adds `delete_date` timestamp to storage entry
- For chunked files: Deletes all chunk messages
- Keeps metadata in storage for audit log

**Example:**
```python
# Delete by message ID
client.delete(123)

# Delete chunked file by file ID
client.delete("chunked_abc123def456")

# Verify deletion in storage
files = client.list_files()
for fid, meta in files.items():
    if meta.get('deleted'):
        print(f"Deleted: {meta['filename']} on {meta['delete_date']}")
```

---

## Storage Management

### `list_files(include_deleted=True)`

List all files tracked in local storage.

**Parameters:**
- `include_deleted` (bool, optional): Include files marked as deleted. Default: `True`

**Returns:** `dict` - Dictionary where keys are file IDs and values are metadata dictionaries

**Metadata Structure:**
```python
{
    "file_id": {
        "message_id": 123,
        "filename": "document.pdf",
        "file_size": 1048576,
        "file_hash": "abc123...",
        "upload_date": "2025-12-24T10:30:00",
        "caption": "My Document",
        "chunked": False,
        "deleted": False,
        "delete_date": None  # Only present if deleted=True
    }
}
```

**Example:**
```python
# List all files including deleted
all_files = client.list_files()
print(f"Total files: {len(all_files)}")

# List only active files
active_files = client.list_files(include_deleted=False)
for file_id, meta in active_files.items():
    size_mb = meta['file_size'] / (1024 * 1024)
    print(f"{meta['filename']}: {size_mb:.2f} MB")
```

---

### `get_file_info(file_id)`

Get metadata for a specific file.

**Parameters:**
- `file_id` (str): File ID from storage

**Returns:** 
- `dict` - File metadata dictionary
- `None` - If file ID not found

**Example:**
```python
# Get info for a specific file
info = client.get_file_info("123")
if info:
    print(f"Filename: {info['filename']}")
    print(f"Size: {info['file_size']} bytes")
    print(f"Hash: {info['file_hash']}")
    print(f"Deleted: {info.get('deleted', False)}")
else:
    print("File not found")
```

---

### `clear_storage()`

Clear all local storage data. This removes all file metadata from the JSON storage file.

**Parameters:** None

**Returns:** None

**Warning:** This action cannot be undone. The storage file will be reset to empty state.

**Example:**
```python
# Clear all storage
client.clear_storage()
print("Storage cleared")

# Verify
files = client.list_files()
print(f"Files remaining: {len(files)}")  # Should be 0
```

---

## Search Functions

### `search_files(filename=None, include_deleted=True)`

Search for files by filename using partial matching (case-insensitive).

**Parameters:**
- `filename` (str, optional): Filename or partial filename to search for. If `None`, returns all files.
- `include_deleted` (bool, optional): Include deleted files in results. Default: `True`

**Returns:** `dict` - Dictionary of matching files

**Example:**
```python
# Search for files containing "report"
results = client.search_files("report")
for fid, meta in results.items():
    print(f"{meta['filename']} - {meta['upload_date']}")

# Search only in active files
results = client.search_files("document", include_deleted=False)

# Get all files
all_files = client.search_files()
```

---

### `search_by_hash(file_hash)`

Search for files by their MD5 hash. Useful for finding duplicate files.

**Parameters:**
- `file_hash` (str): MD5 hash to search for

**Returns:** `dict` - Dictionary of matching files

**Example:**
```python
# Find files with specific hash
hash_to_find = "5d41402abc4b2a76b9719d911017c592"
results = client.search_by_hash(hash_to_find)

if results:
    print(f"Found {len(results)} file(s) with this hash:")
    for fid, meta in results.items():
        print(f"  - {meta['filename']}")
else:
    print("No files found with this hash")
```

---

### `search_by_size(min_size=None, max_size=None)`

Search for files within a specific size range.

**Parameters:**
- `min_size` (int, optional): Minimum file size in bytes
- `max_size` (int, optional): Maximum file size in bytes

**Returns:** `dict` - Dictionary of matching files

**Example:**
```python
# Find files larger than 10 MB
large_files = client.search_by_size(min_size=10*1024*1024)

# Find files smaller than 1 MB
small_files = client.search_by_size(max_size=1024*1024)

# Find files between 1 MB and 10 MB
medium_files = client.search_by_size(
    min_size=1024*1024,
    max_size=10*1024*1024
)

for fid, meta in medium_files.items():
    size_mb = meta['file_size'] / (1024*1024)
    print(f"{meta['filename']}: {size_mb:.2f} MB")
```

---

### `search_by_date_range(start_date=None, end_date=None, date_type="upload")`

Search for files within a specific date range.

**Parameters:**
- `start_date` (str, optional): Start date in ISO format (e.g., "2025-12-24")
- `end_date` (str, optional): End date in ISO format
- `date_type` (str, optional): Type of date to search - `"upload"` or `"delete"`. Default: `"upload"`

**Returns:** `dict` - Dictionary of matching files

**Example:**
```python
# Find files uploaded today
from datetime import datetime
today = datetime.now().date().isoformat()
today_files = client.search_by_date_range(start_date=today)

# Find files uploaded in December 2025
december_files = client.search_by_date_range(
    start_date="2025-12-01",
    end_date="2025-12-31"
)

# Find files deleted this week
from datetime import timedelta
week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
deleted_this_week = client.search_by_date_range(
    start_date=week_ago,
    date_type="delete"
)
```

---

### `search_deleted_files(deleted_only=True)`

Search specifically for deleted or active files.

**Parameters:**
- `deleted_only` (bool, optional): If `True`, return only deleted files. If `False`, only active files. Default: `True`

**Returns:** `dict` - Dictionary of matching files

**Example:**
```python
# Get all deleted files
deleted = client.search_deleted_files(deleted_only=True)
print(f"Found {len(deleted)} deleted files")

# Get all active files
active = client.search_deleted_files(deleted_only=False)

# Show deleted files with delete dates
for fid, meta in deleted.items():
    print(f"{meta['filename']} - Deleted on {meta.get('delete_date', 'N/A')}")
```

---

### `search_chunked_files(chunked_only=True)`

Search for chunked or non-chunked files.

**Parameters:**
- `chunked_only` (bool, optional): If `True`, return only chunked files. If `False`, only single files. Default: `True`

**Returns:** `dict` - Dictionary of matching files

**Example:**
```python
# Get all chunked files
chunked = client.search_chunked_files(chunked_only=True)
for fid, meta in chunked.items():
    print(f"{meta['filename']} - {meta['total_chunks']} chunks")

# Get all single files
single = client.search_chunked_files(chunked_only=False)
print(f"Single files: {len(single)}")
```

---

### `advanced_search(filename=None, min_size=None, max_size=None, deleted=None, chunked=None, file_hash=None)`

Perform an advanced search with multiple criteria. All criteria are combined with AND logic.

**Parameters:**
- `filename` (str, optional): Filename to search for (partial match, case-insensitive)
- `min_size` (int, optional): Minimum file size in bytes
- `max_size` (int, optional): Maximum file size in bytes
- `deleted` (bool, optional): Filter by deleted status (`True`/`False`/`None` for all)
- `chunked` (bool, optional): Filter by chunked status (`True`/`False`/`None` for all)
- `file_hash` (str, optional): MD5 hash to match exactly

**Returns:** `dict` - Dictionary of files matching ALL criteria

**Example:**
```python
# Find large active PDFs
results = client.advanced_search(
    filename=".pdf",
    min_size=5*1024*1024,  # > 5 MB
    deleted=False
)

# Find chunked files that are not deleted
results = client.advanced_search(
    chunked=True,
    deleted=False
)

# Find small text files uploaded recently
results = client.advanced_search(
    filename=".txt",
    max_size=10*1024,  # < 10 KB
    deleted=False
)

for fid, meta in results.items():
    print(f"{meta['filename']}: {meta['file_size']} bytes")
```

---

## Statistics

### `get_storage_stats()`

Get comprehensive statistics about all stored files.

**Parameters:** None

**Returns:** `dict` with the following keys:
- `total_files` (int): Total number of files in storage
- `active_files` (int): Number of non-deleted files
- `deleted_files` (int): Number of deleted files
- `chunked_files` (int): Number of chunked files
- `total_size` (int): Total size of all files in bytes
- `total_size_mb` (float): Total size in megabytes
- `active_size` (int): Total size of active files in bytes
- `active_size_mb` (float): Active size in megabytes

**Example:**
```python
stats = client.get_storage_stats()

print(f"Storage Statistics")
print(f"=" * 40)
print(f"Total files: {stats['total_files']}")
print(f"Active files: {stats['active_files']}")
print(f"Deleted files: {stats['deleted_files']}")
print(f"Chunked files: {stats['chunked_files']}")
print(f"Total storage: {stats['total_size_mb']:.2f} MB")
print(f"Active storage: {stats['active_size_mb']:.2f} MB")

# Calculate percentage
if stats['total_files'] > 0:
    deleted_pct = (stats['deleted_files'] / stats['total_files']) * 100
    print(f"Deleted: {deleted_pct:.1f}%")
```

---

## Utility Functions

### `get_info()`

Get information about the Telegram channel.

**Parameters:** None

**Returns:** `telegram.Chat` object with channel information

**Example:**
```python
info = client.get_info()
print(f"Channel: {info.title}")
print(f"ID: {info.id}")
print(f"Type: {info.type}")
print(f"Description: {info.description}")
```

---

## Complete Usage Example

```python
from tds2 import tds2client
import os

# Initialize
client = tds2client("YOUR_BOT_TOKEN", "YOUR_CHANNEL_ID")

# Upload files
for filename in os.listdir("documents"):
    if filename.endswith(".pdf"):
        result = client.upload(f"documents/{filename}")
        print(f"Uploaded {filename}")

# Search and download
pdf_files = client.advanced_search(
    filename=".pdf",
    min_size=1024*1024,  # > 1 MB
    deleted=False
)

print(f"Found {len(pdf_files)} PDF files")

# Download first result
if pdf_files:
    first_file = list(pdf_files.values())[0]
    file_path = client.download(first_file['message_id'], "backups")
    print(f"Downloaded to: {file_path}")

# Get statistics
stats = client.get_storage_stats()
print(f"Total storage used: {stats['total_size_mb']:.2f} MB")

# Clean up old files
old_deleted = client.search_by_date_range(
    end_date="2025-11-01",
    date_type="delete"
)
print(f"Files deleted before November: {len(old_deleted)}")
```

---

## Error Handling

All functions may raise `TelegramError` for API-related issues. It's recommended to wrap calls in try-except blocks:

```python
from telegram.error import TelegramError

try:
    message = client.upload("large_file.zip")
    print("Upload successful!")
except FileNotFoundError:
    print("File not found!")
except TelegramError as e:
    print(f"Telegram error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```
