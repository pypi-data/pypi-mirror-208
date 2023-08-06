import asyncio
import datetime
import inspect
import json
import sys
import time
import traceback
from inspect import signature

import aiohttp
import pyrogram
import requests
from pyrogram import Client
from pyrogram.errors.exceptions import bad_request_400

from . import generals
from .cog import Cog
from .objects import Message, ChatActions, UserProfilePicture, CallbackQuery, Command, ChatPermission, \
    PromotePermission, PreCheckOutQuery, Chat, User


class CallbackError(Exception):
    def __init__(self, message=None, *args):
        if message is not None:
            self.message = message
            super().__init__(message, *args)
        else:
            super().__init__(*args)


class ToMenyRequests(Exception):
    def __init__(self, message=None, *args):
        if message is not None:
            self.message = message
            super().__init__(message, *args)
        else:
            super().__init__(*args)


class TgAPIException(Exception):
    def __init__(self, message=None, *args):
        if message is not None:
            self.message = message
            super().__init__(message, *args)
        else:
            super().__init__(*args)


class Bot:

    def __init__(self, prefixs, user_id, user_hash, **kwargs):
        if user_id and user_hash:
            self.pyrogram = Client('me', user_id, user_hash).start()
        else:
            self.pyrogram = None
        self.random_cog = None
        self.url = ''
        self.token = ''
        self.offset = None
        self.type_error_message = 'Вы не правильно указали одно значение. Вместо \'{}\' нужна {}'
        self.bot = self
        self.prefix = prefixs
        self.__cogs = {}
        self.group_photos = []
        self.actions_from_cog = {}
        self.command_roles = {}
        self.ignore_listener_filter = []
        self.trigger_on_forward_message = True
        self.message_handlers = {}
        self.listeners_handle = {}
        self.aliases = {}
        self.chat_filter = []
        self.ignore_filter = []
        self.all_commands = {}
        self._skip_check = lambda x, y: x == y
        timeout = aiohttp.ClientTimeout(total=100, connect=10)
        user_agent = kwargs.get('user_agent', None)
        if user_agent:
            headers = {
                'User-Agent': user_agent
            }
            self.session = kwargs.get('session', aiohttp.ClientSession(timeout=timeout, headers=headers))
        else:
            self.session = kwargs.get('session', aiohttp.ClientSession(timeout=timeout))

        self.loop = asyncio.get_event_loop()

    def add_chat_filter(self, chat_id: int):
        self.chat_filter.append(chat_id)

    # <---- custom API actions start ----> #

    async def delete_message(self, chat_id, message_id, revoke=True):
        """
        Delete message in chat_id with id of message_id

        Parameters
        -----------
        chat_id: :class:`int`
            The chat id where need delete message
        message_id: :class:`int`
            The uid of message who need delete
        """
        return await self.pyrogram.delete_messages(chat_id, message_id, revoke)

    async def forward_message(self,chat_id:int,message_id:int,from_chat_id:int,**kwargs):
        dic = {
            'chat_id':chat_id,
            'message_id':message_id,
            'from_chat_id':from_chat_id
        }
        if kwargs:
            dic.update(kwargs)
        return await self._tg_request('forwardMessage',True,**dic)

    async def send_photo(self, chat_id: int, photo: str, **kwargs):
        """
        Send photo in chat with chat_id

        Parameters
        -----------
        chat_id: :class:`int`
            The chat id where need send photo
        photo: :class:`str`
            The file_id of file
        **kwargs:
            another parameters, see `Telegramm API <https://core.telegram.org/bots/api#sendphoto>`_
        """
        dic = {
            'chat_id': chat_id,
            'photo': photo
        }
        if 'reply_markup' in kwargs:
            dic.update({'reply_markup': json.dumps(kwargs.get('reply_markup').to_dict())})
            kwargs.pop('reply_markup')
        dic.update(**kwargs)
        return await self._tg_request('sendPhoto', True, **dic)

    async def send_sticker(self, chat_id, sticker, **kwargs):
        """
        Send stricker in chat with chat_id

        Parameters
        -----------
        chat_id: :class:`int`
            The chat id where need send sticker
        sticker: :class:`str`
            The file_id of sticker
        **kwargs:
            another parameters, see `Telegramm API <https://core.telegram.org/bots/api#sendsticker>`_
        """
        dic = {
            'chat_id': chat_id,
            'sticker': sticker
        }
        dic.update(kwargs)
        return await self._tg_request('sendSticker', True, **dic)

    async def send_chat_action(self, chat_id, chat_action: ChatActions):
        """
        Send bot action in chat with chat_id

        Parameters
        -----------
        chat_id: :class:`int`
            The chat id where need send action
        chat_action: :class:`.ChatActions`
            The chat action that will be display in chat. see `Telegramm API <https://core.telegram.org/bots/api#sendchataction>`_
        """
        return await self._tg_request('sendChatAction', True, **{'chat_id': chat_id, 'action': chat_action.value})

    async def send_dice(self, chat_id, emoji, **kwargs):
        """
        Send dice in chat with chat_id

        Parameters
        -----------
        chat_id: :class:`int`
            The chat id where need send dice
        emoji: :class:`str`
            The emoji that need send
        **kwargs:
            see `Telegramm API <https://core.telegram.org/bots/api#senddice>`_
        """
        dic = {
            'chat_id': chat_id,
            'emoji': emoji
        }
        dic.update(kwargs)
        rs = await self._tg_request('sendDice', True, **dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(message=None, *rs)
        return rs.get('result').get('dice').get('value')

    async def send_invoice(self,chat_id:int,title:str,description:str,payload:str,provider_token:str,prices,currency='RUB',**kwargs):
        """
        Send invoice (payment) message in chat

        Parameters
        -----------
        chat_id: :class:`int`
            The chat id where need send photo
        title: :class:`str`
            The title of invoice
        description: :class:`str`
            The description of invoice
        payload: :class:`str`
            The some information who will be transfer in handler, who handler user's pay
        provider_token: :class:`str`
            The payment token, see https://core.telegram.org/bots/payments
        prices: :class:`int`
            The price
        currency: :class:`str`
            The code of price, eg. 'RUB','USD'
        **kwargs:
            see `Telegramm API <https://core.telegram.org/bots/api#sendinvoice>`_
        """
        dic = {
            'chat_id':chat_id,
            'title':title,
            'description':description,
            'payload':payload,
            'provider_token':provider_token,
            'currency':currency,
            'prices':json.dumps([r.to_dict for r in prices]),
        }
        dic.update(kwargs)
        rs = await self._tg_request('sendInvoice', True, **dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(message=None, *rs)
        return rs

    async def get_chat(self,chat_id:int):
        rs = await self._tg_request('getChat',True,**{'chat_id':chat_id})
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(rs.get('description'), rs)
            else:
                raise TgAPIException(rs)
        return Chat(rs.get('result'))

    async def restrict_chat_member(self, chat_id: int, user_id: int, permission: ChatPermission, until_date=None):
        dic = {
            'chat_id': chat_id,
            'user_id': user_id,
            'permission': permission.to_dict
        }
        if until_date:
            dt = datetime.datetime.now() + datetime.timedelta(seconds=int(30))
            unix_time = time.mktime(dt.timetuple())
            dic.update({'until_date': unix_time})
        rs = await self._tg_request('restrictChatMember', True, **dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(rs.get('description'), rs)
            else:
                raise TgAPIException(rs)
        return rs

    async def promote_chat_member(self, chat_id: int, user_id: int, promotePermission: PromotePermission):
        dic = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        dic.update(promotePermission.to_dict)
        rs = await self._tg_request('promoteChatMember', True, **dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(rs.get('description'), rs)
            else:
                raise TgAPIException(rs)
        return rs

    async def set_chat_administrator_custom_title(self, chat_id: int, user_id: int, custom_title: str):
        dic = {
            'chat_id': chat_id,
            'user_id': user_id,
            'custom_title': custom_title
        }
        rs = await self._tg_request('setChatAdministratorCustomTitle', True, **dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(rs.get('description'), rs)
            else:
                raise TgAPIException(rs)
        return rs

    async def create_forum_topic(self, chat_id: int, name: str, icon_color=None, icon_custom_emoji_id=None):
        dic = {
            'chat_id': chat_id,
            'name': name
        }
        if icon_color:
            dic.update({'icon_color': icon_color})
        if icon_custom_emoji_id:
            dic.update({'icon_custom_emoji_id': icon_custom_emoji_id})
        rs = await self._tg_request('createForumTopic', True, **dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(rs.get('description'), rs)
            else:
                raise TgAPIException(rs)
        return rs

    async def get_user_profile_picture(self, user_id, **kwargs):
        dic = {
            'user_id': user_id
        }
        dic.update(kwargs)
        rs = await self._tg_request('getUserProfilePhotos', True, **dic)
        return UserProfilePicture(rs.get('result'))

    async def kick_chat_member(self, chat_id: int, user_id: int):
        return await self._tg_request('kickChatMember', True, **{'chat_id': chat_id, 'user_id': user_id})

    async def unban_chat_member(self, chat_id: int, user_id: int,only_if_banned:bool = False):
        return await self._tg_request('unbanChatMember', True, **{'chat_id': chat_id, 'user_id': user_id, 'only_if_banned':only_if_banned})

    async def answer_callback_query(self, id: int, text: str, show_alert=False):
        dic = {
            'callback_query_id': id,
            'text': text,
            'show_alert': show_alert
        }
        rs = await self._tg_request('answerCallbackQuery', True, **dic)
        return await self.prefe_incomming_message(rs)

    async def answer_pre_checkout_query(self,pre_checkout_query_id:str,ok:bool,error_message=None):
        dic = {
            'pre_checkout_query_id':pre_checkout_query_id,
            'ok':ok
        }
        if error_message:
            dic.update({'error_message':error_message})
        rs = await self._tg_request('answerPreCheckoutQuery', True, **dic)
        return await self.prefe_incomming_message(rs)

    async def send_message(self, chat_id: int, text: str, reply_markup=None, **kwargs):
        dic = {
            'chat_id': chat_id,
            'text': text
        }
        if reply_markup:
            dic.update({'reply_markup': json.dumps(reply_markup.to_dict())})
        dic.update(kwargs)
        rs = await self._tg_request('sendMessage', True, **dic)
        return await self.prefe_incomming_message(rs)

    async def get_file(self,file_id:str):
        dic = {'file_id':file_id}
        rs = await self._tg_request('getFile',True,**dic)
        if not rs.get('ok'):
            if rs.get('error_code') == 429:
                raise ToMenyRequests(rs.get('description'), rs)
            else:
                raise TgAPIException(rs)
        return rs

    async def prefe_incomming_message(self, message):
        if not message.get('ok'):
            for _m in self.listeners_handle.get('on_invoke_command_error'):
                if _m in self.actions_from_cog:
                    await _m(self.actions_from_cog.get(_m), message)
                else:
                    await _m(message)
            return None
        else:
            try:
                message_ = Message(self, message.get('result'))
                return message_
            except AttributeError:
                return message

    # <---- custom API actions end ----> #

    # <---- COGS start ----> #

    def command(self, name, aliases=None, usage=None, description=None, roles=None, ignore_filter=False,
                has_arts=False):
        def decorator(func):
            command = Command(func, name, description, aliases, usage, roles, ignore_filter, has_arts=has_arts)
            self.add_command(name, command)
            if ignore_filter:
                self.ignore_filter.append(command)
            if aliases is not None:
                for al in aliases:
                    self.add_command(al, command)
            keys = self.all_commands.get('main') or []
            keys.append(command)
            self.all_commands.update({'main': keys})

        return decorator

    def listener(self, ignore_filter=False):
        def decorator(func):
            self.add_listener(func.__name__, func)
            if ignore_filter:
                self.ignore_listener_filter.append(func)

        return decorator

    def add_listener(self, name, func):
        if name in self.listeners_handle:
            self.listeners_handle.get(name).append(func)
        else:
            self.listeners_handle.update({name: [func]})

    async def dispacth_query(self, query):
        for _m in self.listeners_handle.get('on_callback_query'):
            if _m in self.actions_from_cog:
                await _m(self.actions_from_cog.get(_m), query)
            else:
                await _m(query)

    async def dispatch_pre_checkout_query(self,preCheckOutQuery:PreCheckOutQuery):
        for _m in self.listeners_handle.get('pre_checkout_query'):
            if _m in self.actions_from_cog:
                await _m(self.actions_from_cog.get(_m), preCheckOutQuery)
            else:
                await _m(preCheckOutQuery)

    async def check_date(self, message):
        date = datetime.datetime.now() - datetime.timedelta(seconds=5)
        return message.date > date

    async def handleMessage(self, obj):
        if len(obj) >= 1:
            self.offset = obj.get('update_id') + 1
            if 'message' in obj:
                message = Message(self, obj.get('message'))
                if await self.check_date(message):
                    if not self.trigger_on_forward_message:
                        if message.forward_from is not None or message.forward_date is not None:
                            return
                    return await self.dispatch(message)
            elif 'callback_query' in obj:
                query = CallbackQuery(self, obj.get('callback_query'))
                try:
                    return await self.dispacth_query(query)
                except Exception:
                    traceback.print_exc()
            elif 'pre_checkout_query' in obj:
                preCheckOunt = PreCheckOutQuery(obj.get('pre_checkout_query'))
                try:
                    return await self.dispatch_pre_checkout_query(preCheckOunt)
                except Exception:
                    traceback.print_exc()

    def has_prefix(self, message):
        if message.text:
            return message.text.split(' ')[0] in self.prefix
        else:
            return False

    # <---- dispatch events start ---->#

    async def dispatch_message(self, message):
        if self.listeners_handle.get('on_message_new'):
            for _m in self.listeners_handle.get('on_message_new'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message)
                    else:
                        await _m(message)

    async def dispatch_command(self, message, command,args):
        if 'on_pre_command' in self.listeners_handle:
            for _m in self.listeners_handle.get('on_pre_command'):
                if _m in self.actions_from_cog:
                    await _m(self.actions_from_cog.get(_m), command, message)
                else:
                    await _m(command, message)

        if command in self.actions_from_cog:
            await command.func(self.actions_from_cog.get(command), message,*args)
        else:
            await command.func(message,*args)

    async def dispatch_uknow_command(self, message):
        if self.listeners_handle.get("on_unknow_command"):
            for _m in self.listeners_handle.get('on_unknow_command'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message)
                    else:
                        await _m(message)

    async def dispatch_error_command_invoke(self, message, command, exception):
        if self.listeners_handle.get('on_command_error'):
            for _m in self.listeners_handle.get('on_command_error'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message, command, exception)
                    else:
                        await _m(message, command, exception)

    async def dispath_group_photo(self, message):
        time.sleep(1)
        if len(self.group_photos) > 1:
            for _m in self.listeners_handle.get('on_group_photo'):
                if _m in self.actions_from_cog:
                    await _m(self.actions_from_cog.get(_m), message, self.group_photos)
                else:
                    _m(message, self.group_photos)
        else:
            if self.listeners_handle.get('on_photo'):
                for _m in self.listeners_handle.get('on_photo'):
                    if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                        if _m in self.actions_from_cog:
                            await _m(self.actions_from_cog.get(_m), message)
                        else:
                            await _m(message)
        self.group_photos = []

    async def dispatch_payment(self,message):
        if self.listeners_handle.get('on_payment'):
            for _m in self.listeners_handle.get('on_payment'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message)
                    else:
                        await _m(message)

    async def dispatch_photo(self, message):
        await self.dispath_group_photo(message)

    async def dispatch_sticker(self, message):
        if self.listeners_handle.get('on_sticker_new'):
            for _m in self.listeners_handle.get('on_sticker_new'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message)
                    else:
                        await _m(message)

    async def dispatch_new_member(self, message):
        if self.listeners_handle.get('on_new_member'):
            for _m in self.listeners_handle.get('on_new_member'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message)
                    else:
                        await _m(message)

    async def dispatch_chat_left_member(self, message):
        if self.listeners_handle.get('on_member_leave'):
            for _m in self.listeners_handle.get('on_member_leave'):
                if _m in self.ignore_listener_filter or message.chat.id in self.chat_filter:
                    if _m in self.actions_from_cog:
                        await _m(self.actions_from_cog.get(_m), message)
                    else:
                        await _m(message)

    async def dispatch_chat_filter_error(self, message):
        if self.listeners_handle.get('on_chat_filter'):
            for _m in self.listeners_handle.get('on_chat_filter'):
                if _m in self.actions_from_cog:
                    await _m(self.actions_from_cog.get(_m), message)
                else:
                    await _m(message)

    # <---- dispatch events end ---->#

    def search(self, name):
        last_fitting = None
        level = self.message_handlers
        c = 0
        from_aliases = False
        for word in name.split():
            if word not in level:
                break
            c += 1
            level = level[word]
            if '' in level:
                last_fitting = level['']
        return last_fitting, c, from_aliases

    def add_command(self, name, command):
        level = self.message_handlers
        for word in name.split():
            if word not in level:
                level[word] = {}
            level = level[word]
        level[''] = command

    def add_cog(self, cls: Cog):
        self.random_cog = cls
        for v in cls.__class__.__dict__.values():
            if '__command__' in dir(v):
                command = Command(v, v.__command__)
                if 'description' in dir(v):
                    command.description = v.description
                if 'usage' in dir(v):
                    command.usage = v.usage
                if 'roles' in dir(v):
                    command.roles = v.roles
                if v.__ignore_filter__:
                    self.ignore_filter.append(command)
                if 'aliases' in dir(v):
                    command.aliases = v.aliases
                    for al in v.aliases:
                        self.add_command(al, command)
                if 'has_arts' in dir(v):
                    command.has_arts = v.has_arts
                self.add_command(v.__command__, command)
                self.actions_from_cog.update({command: cls})
                values = self.all_commands.get(cls.__class__.__name__) or []
                values.append(command)
                self.all_commands.update({cls.__class__.__name__: values})
            elif '__listener__' in dir(v):
                self.add_listener(v.__listener__, v)
                self.actions_from_cog.update({v: cls})
                if v.__ignore_filter__:
                    self.ignore_listener_filter.append(v)

    async def get_args(self,args):
        data = []
        for arg in args:
            try:
                data.append(int(arg))
                continue
            except:
                pass
            if arg[0] == '@':
                data.append(await User.load(arg,self))
                continue
            data.append(arg)
        return data

    async def tupe_error(self,message, arg,need_type):
        type = need_type
        if need_type==int:
            type = 'число'
        elif need_type==str:
            type = 'строка'
        elif need_type==User:
            type = 'пользователь'
        await message.reply(self.type_error_message.format(arg,type))


    async def dispatch(self, message):
        if self.has_prefix(message):
            ms = message.text.split()
            ms.pop(0)
            rs, c, from_aliases = self.search(' '.join(ms))
            if rs:
                for i in range(c):
                    ms.pop(0)
                args = await self.get_args(ms)
                need_args = signature(rs.func)
                put_args = []
                minus = 1
                na = dict(need_args.parameters)
                if 'self' in na.keys():
                    na.pop('self')
                try:
                    na.pop(list(na.keys())[0])
                except:
                    print("ERROR: ",na,'\n','put_args: ',put_args,'\nargs: ',args)
                for i in range(0,len(na)):
                    val = list(na.values())[i]
                    try:
                        if val.annotation != inspect.Parameter.empty:
                            if not isinstance(args[i-minus],val.annotation):
                                return await self.tupe_error(message,args[i-minus],val.annotation)
                    except IndexError as e:
                        put_args.append(None)
                        continue
                    put_args.append(args[i-minus])
                    ms.pop(0)
                message.text = ' '.join(ms)
                setattr(message, 'texts', ms)
                if len(self.chat_filter) > 0:
                    if message.chat.id not in self.chat_filter and rs not in self.ignore_filter:
                        return await self.dispatch_chat_filter_error(message)
                try:
                    await self.dispatch_command(message, rs,put_args)
                except CallbackError as e:
                    await message.reply(e.message)
                    return await self.dispatch_error_command_invoke(message, rs, e)
                except Exception as e:
                    await self.dispatch_error_command_invoke(message, rs, e)
                    traceback.print_exc()
            else:
                await self.dispatch_uknow_command(message)
        await self.dispatch_message(message)
        if message.successful_payment:
            await self.dispatch_payment(message)
        elif message.photo:
            await self.dispatch_photo(message)
        elif message.sticker:
            await self.dispatch_sticker(message)
        elif message.new_chat_member or message.new_chat_participant:
            await self.dispatch_new_member(message)
        elif message.left_chat_member or message.left_chat_participant:
            await self.dispatch_chat_left_member(message)


    async def longpoll(self):
        data = {}
        if self.offset is None:
            self.offset = 0
        data.update({'offset': self.offset})
        r = requests.post(self.url, data=data)
        json_ = r.json()
        if json_.get('ok'):
            ar = json_.get('result')
            return ar
        return None

    async def _run(self):
        updates = []
        if 'on_start' in self.listeners_handle:
            for _m in self.listeners_handle.get('on_start'):
                if _m in self.actions_from_cog:
                    await _m(self.actions_from_cog.get(_m))
                else:
                    await _m()
        while True:
            lp = self.loop.create_task(self.longpoll())
            if updates is not None:
                for update in updates:
                    await self.handleMessage(update)
            updates = await lp

    async def general_request(self, url, post=False, file=None, **params):
        params = generals.convert_params(params)
        for tries in range(5):
            try:
                req = self.session.post(url, data=params) if post else self.session.get(url, params=params)
                async with req as r:
                    if r.content_type == 'application/json':
                        return await r.json()
                    return await r.text()
            except Exception as e:
                print('Got exception in request: {}\nRetrying in {} seconds'.format(e, tries * 2 + 1), file=sys.stderr)
                await asyncio.sleep(tries * 2 + 1)

    async def _tg_request(self, method, post, **kwargs):
        res = await self.general_request('https://api.telegram.org/bot{}/{}'.format(self.token, method), post=post,
                                         **kwargs)
        return res

    async def tg_request(self, method, post=True, **kwargs):
        return await self._tg_request(method, post, **kwargs)

    def run(self, token):
        generals.token = token
        self.url = f'https://api.telegram.org/bot{token}/getUpdates'
        self.token = token
        self.loop.create_task(self._run())
        self.loop.run_forever()
