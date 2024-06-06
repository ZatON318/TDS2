from telethon import TelegramClient
from tqdm import tqdm
import os
import asyncio
from dotenv import load_dotenv

class tds2client:

    bandwidth_safety = False

    def __init__(self):
        load_dotenv()

        api_id = os.environ.get("API_ID")
        api_hash = os.environ.get("API_HASH")

        self.client = TelegramClient('anon', api_id, api_hash)
        self.safe = int(os.environ.get("GROUP_CHAT_ID"))

    async def upload_file(self, file_path):
        await self.client.start()
        
        total_size = os.path.getsize(file_path)
        response = None

        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Uploading') as bar:
            def callback(current, total):
                bar.update(current - bar.n)

            response = await self.client.send_file(self.safe, file_path, progress_callback=callback)
            print(response)
        
        await self.client.disconnect()
        return response
    
    async def download_file(self, message_id):
        await self.client.start()

        message = await self.client.get_messages(self.safe, ids=message_id)
       
        if message.media:
            response = await self.client.download_media(message.media)

        await self.client.disconnect()
        return response
    
    async def get_last_massage_id(self):
        await self.client.start()

        message = await self.client.get_messages(self.safe, limit=1)
        last_message_id = message[0].id if message else None
        
        await self.client.disconnect()
        return last_message_id
    
    async def delete_message(self, message_id):
        await self.client.start()

        response = await self.client.delete_messages(self.safe, message_id)
        print(f'Message {message_id} deleted')

        await self.client.disconnect()
        return response
    
    #Primary functions
    def upload(self, file_path):
        return asyncio.run(self.upload_file(file_path))

    def download(self, message_id):
        return asyncio.run(self.download_file(message_id))

    def delete(self, message_id):
        return asyncio.run(self.delete_message(message_id))

    def get_last(self):
        return asyncio.run(self.get_last_massage_id())