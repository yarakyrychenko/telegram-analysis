import configparser
import json
import asyncio
from datetime import date, datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)

def scan(path_to_file):
    """ open txt dictionaries """ 
    text_file = open(path_to_file, "r")
    file = text_file.read().split("\n")
    text_file.close()
    file = [word for word in file if word != ""]
    return file

file = scan("Media-Telegram-Channels.txt")

# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()
    number = 1
    errors = []
    for entity in file[70:]:
        print(f"number {number}, channel {entity}")
        number +=1

        try:
            my_channel = await client.get_entity(entity)
        except:
            errors.append(entity)
            continue
                

        offset_id = 0
        limit = 10000
        all_messages = []
        total_messages = 0
        total_count_limit = 0

        while True:
            print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
            history = await client(GetHistoryRequest(
                peer=my_channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            if not history.messages:
                break
            messages = history.messages
            for message in messages:
                all_messages.append(message.to_dict())
            offset_id = messages[len(messages) - 1].id
            total_messages = len(all_messages)
            if total_count_limit != 0 and total_messages >= total_count_limit:
                break

        new_name = entity.split("/")[-1]
        with open(f'MediaTelegram/{new_name}.json', 'w') as outfile:
            json.dump(all_messages, outfile, cls=DateTimeEncoder)
        print(f"Done with number {number}, channel {entity}")

    f = open("errors.txt", "w")
    for error in errors:
        f.write(f"{error}\n")
    f.close()
        

with client:
    client.loop.run_until_complete(main(phone))
