# tg_bottng

python library for easy creation of a telegram bot

## Install

Use pip3

```
pip3 install tg-botting
```

Quick Start

```python
from tg_botting.bot import Bot

# user_id and user_hash - user application in telegram 

bot = Bot(['prefixs'],'user_id','user_hash')

# send message

@bot.command('ping')
async def ping(message):
    await bot.send_message(message.chat.id,'pong')

# reply

@bot.command('ping reply')
async def ping(message):
    await message.reply('pong reply')
    
# start

bot.run(your_bot_token)

```

for find user_id and user_hash:
 1) Visit https://my.telegram.org/apps and log in with your Telegram account.

 2) Fill out the form with your details and register a new Telegram application.

 3) Done. The API key consists of two parts: api_id and api_hash. Keep it secret.


Visit full doc: https://github.com/2sweetheart2/tg_botting/wiki/Start
