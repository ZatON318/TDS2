from telethon import TelegramClient
from tqdm import tqdm
import os
import asyncio
import json
from datetime import datetime

class tds2client:

    bandwidth_safety = False

    def __init__(self, api_id, api_hash, group_chat_id, logfile=None):

        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.safe = int(group_chat_id)
        self.logfile = logfile

    def _get_client(self):
        """Create a new Telegram client instance"""
        return TelegramClient('anon', self.api_id, self.api_hash)

    def _load_log(self):
        """Load the JSON log file"""
        if not self.logfile:
            return None
        if os.path.exists(self.logfile):
            with open(self.logfile, 'r') as f:
                return json.load(f)
        return {"total_size": 0, "files": {}}

    def _save_log(self, log_data):
        """Save the JSON log file"""
        if not self.logfile:
            return
        with open(self.logfile, 'w') as f:
            json.dump(log_data, f, indent=2)

    def _calculate_total_size(self, log_data):
        """Calculate total size of non-deleted files"""
        total = 0
        for file_id, file_info in log_data.get("files", {}).items():
            if not file_info.get("deleted", False):
                total += file_info.get("size_bytes", 0)
        return total

    def _log_upload(self, message_id, file_path):
        """Log file upload to JSON"""
        if not self.logfile:
            return
        
        log_data = self._load_log()
        
        file_size = os.path.getsize(file_path)
        file_info = {
            "message_id": message_id,
            "file_name": os.path.basename(file_path),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "upload_date": datetime.now().isoformat(),
            "deletion_date": None,
            "deleted": False
        }
        
        log_data["files"][str(message_id)] = file_info
        log_data["total_size"] = self._calculate_total_size(log_data)
        
        self._save_log(log_data)

    def _log_deletion(self, message_id):
        """Log file deletion to JSON"""
        if not self.logfile:
            return
        
        log_data = self._load_log()
        
        if str(message_id) in log_data["files"]:
            log_data["files"][str(message_id)]["deleted"] = True
            log_data["files"][str(message_id)]["deletion_date"] = datetime.now().isoformat()
            log_data["total_size"] = self._calculate_total_size(log_data)
            
            self._save_log(log_data)

    def get_log_summary(self):
        """Get summary of logged files"""
        if not self.logfile:
            return None
        
        log_data = self._load_log()
        
        files = log_data.get("files", {})
        active_count = sum(1 for f in files.values() if not f.get("deleted", False))
        deleted_count = sum(1 for f in files.values() if f.get("deleted", False))
        
        return {
            "total_size": log_data["total_size"],
            "total_size_mb": round(log_data["total_size"] / (1024 * 1024), 2),
            "active_files": active_count,
            "deleted_files": deleted_count,
            "total_files": len(files)
        }

    async def upload_file(self, file_path):
        client = self._get_client()
        await client.start()
        
        total_size = os.path.getsize(file_path)
        response = None

        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Uploading') as bar:
            def callback(current, total):
                bar.update(current - bar.n)

            response = await client.send_file(self.safe, file_path, progress_callback=callback)
        
        # Log the upload
        self._log_upload(response.id, file_path)
        
        await client.disconnect()
        return response
    
    async def download_file(self, message_id):
        client = self._get_client()
        await client.start()

        message = await client.get_messages(self.safe, ids=message_id)
       
        if message.media:
            response = await client.download_media(message.media)

        await client.disconnect()
        return response
    
    async def get_last_massage_id(self):
        client = self._get_client()
        await client.start()

        message = await client.get_messages(self.safe, limit=1)
        last_message_id = message[0].id if message else None
        
        await client.disconnect()
        return last_message_id
    
    async def delete_message(self, message_id):
        client = self._get_client()
        await client.start()

        response = await client.delete_messages(self.safe, message_id)
        print(f'Message {message_id} deleted')
        
        # Log the deletion
        self._log_deletion(message_id)

        await client.disconnect()
        return response
    
    #Primary functions
    def upload(self, file_path):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.upload_file(file_path))
        finally:
            loop.close()

    def download(self, message_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.download_file(message_id))
        finally:
            loop.close()

    def delete(self, message_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.delete_message(message_id))
        finally:
            loop.close()

    def get_last(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_last_massage_id())
        finally:
            loop.close()