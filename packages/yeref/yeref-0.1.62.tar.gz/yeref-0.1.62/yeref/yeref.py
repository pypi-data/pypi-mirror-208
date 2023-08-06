#!/usr/bin/python3
# region data
import ast
import asyncio
import datetime
import io
import json
import logging
import mimetypes
import os
import random
import re
import shutil
import sqlite3
import string
from calendar import monthrange
from contextlib import closing
from math import radians, cos, sin, asin, sqrt
from random import randrange
from uuid import uuid4
import httplib2
import moviepy.editor as mp
from PIL import Image
from aiogram import types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramRetryAfter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.text_decorations import markdown_decoration
from exiftool import ExifToolHelper
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger
from oauth2client.service_account import ServiceAccountCredentials
from pydub import AudioSegment
from pyrogram import enums, Client, utils
from pyrogram.errors import FloodWait, UserAlreadyParticipant, UsernameInvalid, BadRequest, SlowmodeWait, \
    UserDeactivatedBan, SessionRevoked, SessionExpired, AuthKeyUnregistered, AuthKeyInvalid, AuthKeyDuplicated, \
    InviteHashExpired, InviteHashInvalid, ChatAdminRequired, UserDeactivated, UsernameNotOccupied, ChannelBanned
from pyrogram.raw import functions
from stegano import lsb, exifHeader
from telegraph.aio import Telegraph

import yeref

one_minute = 60
one_hour = 3600
seconds_in_day = 86400
my_tid = 5491025132
my_tids = [
    '5900268983',
    '6283902226',
    '6090677494',

    '5754810063',
    '5491025132',
    '5360564451',
    '6281795468',
]
old_tid = 5_000_000_000
lat_company = 59.395881
long_company = 24.658980
lkjhgfdsa_channel_id = -1001657854832
lkjhgfdsa_channel_un = "lkjhgfdsa_channel"
tg_ch_ads_un = 'kiejakn3_djdjn4m_ads'
tg_ch_ads_id = -1001921910898
price_one = 200
price_all = 500
passwd = 'lost9'
bin_empty = b'\xe2\x81\xa0\xe2\x81\xa0'  # .encode("utf-8")
hex_empty = 'e281a0e281a0'  # .encode("utf-8").hex()  || bytes.fromhex()
str_empty = bin_empty.decode('utf-8')

TGPH_TOKEN_MAIN = 'a9335172886eae62ec0743bf8a4e195286ec30cff067da5fd1db2899d008'
TGPH_TOKENS = {
    "https://telegra.ph/pst-FereyDemoBot-05-08": "f8c69d50846e8d55e08f8e3de514f41266e0150434219059f2c91fb4d75f",
    "https://telegra.ph/pst-FereyBotBot-05-08": "e7f943fcc98bac07ad6aaf6e570d0f51abadf02567938c997dbc1ad1923b",
    "https://telegra.ph/pst-FereyPostBot-05-08": "14085be3058c0a25616d094f4bb65c73dc61f783468f01da41d99fb6ace1",
    "https://telegra.ph/pst-FereyMediaBot-05-08": "cf71a596b7ecdc96d30ddffdbf1e26863dd39755f47b4fc343fc3867f373",
    "https://telegra.ph/pst-FereyChannelBot-05-08": "f43f375b8aec531cee0d5048878943a3ccee97da4143d311d5b2c7ed3237",
    "https://telegra.ph/pst-FereyGroupBot-05-08": "c08f94618b94dd25ef75de70c1ed565853efef5479057c68a5720609bb7f",
    "https://telegra.ph/pst-FereyFindBot-05-08": "2d005bb366dc5bef023d58b93d5f45fb9a02a7d2b0f9063a6fc277b5a62d",
    "https://telegra.ph/pst-FereyTargetBot-05-08": "bda8c0a4b7a35101d34252568acd46df7bd3d8d85f4e13dd35f3bddc2f80",
    "https://telegra.ph/pst-FereyToolsBot-05-08": "ea83403eb6ac7d2ad24d7e7a86163be20cd2d7f4734267808e154a8fd0a6",
    "https://telegra.ph/pst-FereyVPNBot-05-08": "38086caf43905ef827715da999aae0be2427ebd7a05d9ff7420543b50613",
    "https://telegra.ph/pst-FereyAIBot-05-08": "bcda631d991c16b4fdfd15e7af6512bcf8fd679fee6bd4c717f6266671a0",
    "https://telegra.ph/pst-FereyUserBot-05-08": "3698a3432c233bef48c238b35cfe94db844858b2ba98594007c7757dcf03",
    "https://telegra.ph/pst-FereyWorkBot-05-08": "d4930b2a9311ad63f7f0ae3d61ca7224ecf76a2434a50161e239a45199c5",
    "https://telegra.ph/pst-FereyAdsBot-05-08": "c1024508f1a5de4f9544dd10793b1401da95de5719bdcf0b4c9f6c26a672",
}
SECTION = 'CONFIG'
LINES_ON_PAGE = 5
short_name = 'me'
const_url = 'https://t.me/'
phone_number = '79999999999'
vk_group = 'https://vk.com'
vk_account = 'https://vk.com'
website = 'https://google.com'
facebook = 'https://www.facebook.com'
telegram_account = 'https://t.me'
ferey_telegram_username = 'ferey_support'
ferey_telegram_demo_bot = 'ferey_demo_bot'
ferey_telegram_group = 'ferey_group_europe'
ferey_telegram_channel = 'ferey_channel_europe'
ferey_instagram = 'https://www.instagram.com/ferey.chatbot'
ferey_address = "Estônia, Tāllin, Mäepealse, 2/1"
ferey_title = "Ferey Inc."
payment_link = 'http://bagazhznaniy.ru/wp-content/uploads/2014/03/zhivaya-priroda.jpg'
whatsup = f'https://api.whatsapp.com/send?phone={phone_number}&text=%D0%94%D0%BE%D0%B1%D1%80%D1%8B%D0%B9%20%D0%B4%D0' \
          f'%B5%D0%BD%D1%8C%2C%20%D1%8F%20%D0%BF%D0%BE%20%D0%BF%D0%BE%D0%B2%D0%BE%D0%B4%D1%83%20%D0%92%D0%B0%D1%88%D0' \
          f'%B5%D0%B3%D0%BE%20%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D0%B0!'

ferey_thumb = 'https://telegra.ph/file/bf7d8c073cdfa91b6d624.jpg'
ferey_theme = 'https://t.me/addtheme/lzbKZktZjqv5VDdY'
ferey_wp = 'https://t.me/bg/Mr2tXPkzQUoGAgAAv-ssUh01-P4'
ferey_set = 'https://t.me/addstickers/Mr2tXPkzQUoGAgAAv-ssUh01-P4'
ferey_emoji = 'https://t.me/addemoji/Mr2tXPkzQUoGAgAAv-ssUh01-P4'
reactions_ = ['👍', '❤', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🙏',
              '👌', '🕊', '🤡', '🥱', '🥴', '😍', '🐳', '❤\u200d🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆',
              '💔', '🤨', '😐', '🍓', '🍾', '💋', '😈', '😴', '😭', '🤓', '👻', '👨\u200d💻', '👀', '🎃',
              '🙈', '😇', '😨', '🤝', '✍', '🤗', '\U0001fae1', '😂', '🎄', '⛄', ' 🆒', '🗿']
themes_ = ['🐥', '⛄', '💎', '👨\u200d🏫', '🌷', '💜', '🎄', '🎮']  # все в порядке, все ставятся, если не стояли
bot_father = "@BotFather"
text_jpeg = 'https://telegra.ph/file/0c675e5a3724deff3b2e1.jpg'
bot_logo_jpeg = 'https://telegra.ph/file/99d4f150a52dcf78b3e8a.jpg'
channel_logo_jpeg = 'https://telegra.ph/file/8418e1cd70484eac89477.jpg'
group_logo_jpeg = 'https://telegra.ph/file/807e0d4fc4f271899272a.jpg'
payment_photo = 'https://telegra.ph/file/75747cf7bc68f45a0e8b8.jpg'

photo_jpg = 'https://telegra.ph/file/d39e358971fc050e4fc88.jpg'
gif_jpg = 'https://telegra.ph/file/e147d6798a43fb1fc4bea.jpg'
video_jpg = 'https://telegra.ph/file/692d65420f9801d757b0c.jpg'
video_note_jpg = 'https://telegra.ph/file/a0ebd72b7ab97b8d6de24.jpg'
audio_jpg = 'https://telegra.ph/file/15da5534cb4edfbdf7601.jpg'
voice_jpg = 'https://telegra.ph/file/10ada321eaa60d70a125d.jpg'
document_jpg = 'https://telegra.ph/file/28b6c218157833c0f4030.jpg'
sticker_jpg = 'https://telegra.ph/file/986323df1836577cbe55d.jpg'
log_ = f"\033[{92}m%s\033[0m"

short_description = f"""🌱 Top 10 Telegram-Marketing Bot

All projects: t.me/FereyDemoBot
🇬🇧🇨🇳🇦🇪🇪🇸🇷🇸🇫🇷
"""

markupAdmin = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text='⬅️ Prev'), types.KeyboardButton(text='↩️ Menu'),
     types.KeyboardButton(text='➡️️ Next')]], resize_keyboard=True, selective=True, row_width=3)


# endregion


# region db
def sqlite_lower(value_):
    return value_.lower() if value_ else None


def sqlite_upper(value_):
    return value_.upper() if value_ else None


def ignore_case_collation(value1_, value2_):
    if value1_ is None or value2_ is None:
        return 1
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


async def db_select(sql, param=None, db=None):
    retry = 2
    while retry > 0:
        try:
            with closing(sqlite3.connect(db, timeout=15)) as con:
                con.execute('PRAGMA foreign_keys=ON;')
                # con.create_collation("NOCASE", ignore_case_collation)
                # con.create_function("LOWER", 1, sqlite_lower)
                # con.create_function("UPPER", 1, sqlite_upper)
                with closing(con.cursor()) as cur:
                    if param:
                        cur.execute(sql, param)
                    else:
                        cur.execute(sql)

                    return cur.fetchall()
        except Exception as e:
            await log(e)
            await asyncio.sleep(round(random.uniform(1, 2), 2))
            retry -= 1
    return []


async def db_change(sql, param=None, db=None):
    retry = 2
    while retry > 0:
        try:
            with closing(sqlite3.connect(db, timeout=15)) as con:
                con.execute('PRAGMA foreign_keys=ON;')
                with closing(con.cursor()) as cur:
                    if param:
                        cur.execute(sql, param)
                    else:
                        cur.execute(sql)

                    con.commit()
                    return cur.lastrowid
        except Exception as e:
            await log(e)
            await asyncio.sleep(round(random.uniform(1, 2), 2))
            retry -= 1
    return 0


# endregion


# region menu
async def post_offer(bot, data, BASE_D):
    try:
        for item in data:
            try:
                OFFER_ID, OFFER_USERTID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, \
                    OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, \
                    OFFER_DT, OFFER_TZ = item

                sign_ = OFFER_TZ[0]
                h_, m_ = OFFER_TZ.strip(sign_).split(':')
                dt_now = datetime.datetime.utcnow()
                if sign_ == "+":
                    dt_cur = dt_now + datetime.timedelta(hours=int(h_), minutes=int(m_))
                else:
                    dt_cur = dt_now - datetime.timedelta(hours=int(h_), minutes=int(m_))
                timedelta_ = (dt_cur - datetime.datetime.strptime(OFFER_DT, "%d-%m-%Y %H:%M"))

                if timedelta_.days >= 0 and timedelta_.seconds >= 0:
                    sql = "UPDATE OFFER SET OFFER_DT=NULL, OFFER_STATUS=0 WHERE OFFER_ID=?"
                    await db_change(sql, (OFFER_ID,), BASE_D)

                    loop_minute = asyncio.get_event_loop()
                    loop_minute.create_task(broadcast_send_admin(bot, OFFER_USERTID, 'en', OFFER_ID, BASE_D, []))
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def bots_by_inline(chat_id, message, BASE_D):
    result = []
    try:
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        data = [
            ['👩🏽‍💻 @FereyDemoBot', yeref.l_inline_demo[lz], 'https://t.me/FereyDemoBot'],
            ['👩🏽‍💻 @FereyBotBot', yeref.l_inline_bot[lz], 'https://t.me/FereyBotBot'],
            ['👩🏽‍💻 @FereyPostBot', yeref.l_inline_post[lz], 'https://t.me/FereyPostBot'],
            ['👩🏽‍💻 @FereyMediaBot', yeref.l_inline_media[lz], 'https://t.me/FereyMediaBot'],
            ['👩🏽‍💻 @FereyChannelBot', yeref.l_inline_channel[lz], 'https://t.me/FereyChannelBot'],
            ['👩🏽‍💻 @FereyGroupBot', yeref.l_inline_group[lz], 'https://t.me/FereyGroupBot'],
            ['👩🏽‍💻 @FereyFindBot', yeref.l_inline_find[lz], 'https://t.me/FereyFindBot'],
            ['👩🏽‍💻 @FereyAIBot', yeref.l_inline_ai[lz], 'https://t.me/FereyAIBot'],
            ['👩🏽‍💻 @FereyAdsBot', yeref.l_inline_ads[lz], 'https://t.me/FereyAdsBot'],
            ['👩🏽‍💻 @FereyVPNBot', yeref.l_inline_vpn[lz], 'https://t.me/FereyVPNBot'],
            ['👩🏽‍💻 @FereyTargetBot', yeref.l_inline_target[lz], 'https://t.me/FereyTargetBot'],
            ['👩🏽‍💻 @FereyUserBot', yeref.l_inline_user[lz], 'https://t.me/FereyUserBot'],
            ['👩🏽‍💻 @FereyToolsBot', yeref.l_inline_tools[lz], 'https://t.me/FereyToolsBot'],
            ['👩🏽‍💻 @FereyWorkBot', yeref.l_inline_work[lz], 'https://t.me/FereyWorkBot'],
        ]

        for i in range(0, len(data)):
            title, desc, text = data[i]

            input_message_content = types.InputTextMessageContent(message_text=text, disable_web_page_preview=False)
            result.append(types.InlineQueryResultArticle(id=str(uuid4()),
                                                         title=title,
                                                         description=desc,
                                                         thumb_url=bot_logo_jpeg,
                                                         input_message_content=input_message_content))
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def get_buttons_main(lz, bot_un, BASE_D):
    result = []
    try:
        result = [
            types.InlineKeyboardButton(text="👩🏽‍💼Acc", url=f"tg://user?id={my_tid}"),
            types.InlineKeyboardButton(text="🙌🏽Tgph", web_app=types.WebAppInfo(url='https://telegra.ph')),
            types.InlineKeyboardButton(text="🔗Share",
                                       url=f'https://t.me/share/url?url=https%3A%2F%2Ft.me%2F{bot_un}&text=%40{bot_un}'),
            types.InlineKeyboardButton(text=f"{(await read_likes(BASE_D))}♥️Like", callback_data=f"like"),
            types.InlineKeyboardButton(text="🦋Chan", url=f"https://t.me/{get_tg_channel(lz)}"),
            types.InlineKeyboardButton(text="🫥Bots", switch_inline_query_current_chat=f"~"),
        ]
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


# endregion


# region telegraph
async def get_telegraph_page(access_token, url):
    result = telegraph_ = None
    try:
        telegraph_ = Telegraph(access_token=access_token)
        pages_ = (await telegraph_.get_page_list())['pages']

        for page_ in pages_:
            if page_['url'] == url:
                result = await telegraph_.get_page(path=page_['path'], return_content=True, return_html=False)
                return
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return telegraph_, result


async def tgph_change(access_token, url, json_):
    retry = 2
    while retry > 0:
        try:
            await asyncio.sleep(round(random.uniform(0, 1), 2))
            telegraph_ = Telegraph(access_token=access_token)
            pages_ = await telegraph_.get_page_list()

            for page_ in pages_['pages']:
                if page_['url'] != url: continue

                get_page_ = await telegraph_.get_page(path=page_['path'], return_content=True, return_html=False)
                try:
                    content_json = json.loads(str(get_page_['content'][0]))
                except:
                    content_json = {}

                timestamp_ = str(utils.datetime_to_timestamp(datetime.datetime.utcnow()))
                content_json[timestamp_] = json_
                post_dumps = json.dumps(content_json, ensure_ascii=False)
                await telegraph_.edit_page(path=page_['path'], title=page_['title'], html_content=post_dumps)
                return 1
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))
        finally:
            retry -= 1
    return 0


async def tgph_clear(access_token, url):
    retry = 2
    while retry > 0:
        try:
            await asyncio.sleep(round(random.uniform(0, 1), 2))
            telegraph_ = Telegraph(access_token=access_token)
            pages_ = await telegraph_.get_page_list()

            for page_ in pages_['pages']:
                if page_['url'] == url:
                    await telegraph_.edit_page(path=page_['path'], title=page_['title'], html_content='{}')
                return 1
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))
        finally:
            retry -= 1
    return 0


async def get_tgph_link(file_name):
    result = None
    try:
        if file_name and os.path.exists(file_name) and os.path.getsize(file_name) < 5242880:
            try:
                # jpg, .jpeg, .png, .gif and .mp4
                telegraph_ = Telegraph()
                res = await telegraph_.upload_file(file_name)
                if res:
                    result = f"{'https://telegra.ph'}{res[0]['src']}"
            except Exception as e:
                logger.info(log_ % f"Telegraph: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def is_ban_menu(chat_id):
    result = False
    try:
        telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        pages = await telegraph_.get_page_list()

        for item in pages['pages']:
            try:
                if item['path'] == 'ban-04-11-7':
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                    ban_ids = str(page['content']).split()

                    if str(chat_id) in ban_ids:
                        result = True
                    return
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        # telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        # html_ = {'one': '1', 'two': '2'}
        # html_ = json.dumps(html_, ensure_ascii=False)
        # page_ = telegraph_.create_page(title='broadcasting', html_content=html_, author_name='bot_username', author_url='https://t.me/bot_username', return_content=True)
        # page_url = page_['url']
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def ban_handler_menu(bot, chat_id, args):
    try:
        telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        pages = await telegraph_.get_page_list()

        if not args:
            for item in pages['pages']:
                try:
                    if item['path'] == 'ban-04-11-7':
                        page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                        ban_ids = str(page['content'])
                        ban_ids = ban_ids[:4096]
                        ban_ids = ' '.join([f"<code>{it}</code>" for it in ban_ids.split()])

                        await bot.send_message(chat_id, ban_ids)
                        return
                except Exception as e:
                    logger.info(log_ % str(e))
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

        prepare_ids = args.split()
        prepare_ids = [prepare_id for prepare_id in prepare_ids if prepare_id.isdigit()]
        if not len(prepare_ids): return

        for item in pages['pages']:
            try:
                if item['path'] == 'ban-04-11-7':
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                    ban_ids = str(page['content']).split()
                    length1 = len(ban_ids)
                    ban_ids = f"{page['content']} {' '.join(prepare_ids)}"
                    ban_ids = ban_ids.split()
                    ban_ids = list(set(ban_ids))
                    length2 = len(ban_ids)
                    modul = abs(length1 - length2)
                    await telegraph_.edit_page(path=item['path'], title="ban", html_content=' '.join(ban_ids))

                    if length1 != length2:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th added to /ban (len: {length2})")
                    else:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th already in /ban (len: {length2})")
                    break
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def unban_handler_menu(bot, chat_id, args):
    try:
        if not args:
            return
        else:
            prepare_ids = args.split()

        prepare_ids = [prepare_id for prepare_id in prepare_ids if prepare_id.isdigit()]
        if not len(prepare_ids): return
        telegraph_ = Telegraph(access_token=TGPH_TOKEN_MAIN)
        pages = await telegraph_.get_page_list()

        for item in pages['pages']:
            try:
                if item['path'] == 'ban-04-11-7':
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=True)
                    ban_ids = str(page['content']).split()
                    length1 = len(ban_ids)

                    ban_ids = [ban_id for ban_id in ban_ids if ban_id not in prepare_ids]
                    length2 = len(ban_ids)
                    ban_ids = list(set(ban_ids))
                    modul = abs(length1 - length2)
                    html_content = ' '.join(ban_ids)
                    html_content = '0' if html_content == '' else html_content
                    await telegraph_.edit_page(path=item['path'], title="ban", html_content=html_content)

                    if length1 != length2:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th removed from /ban (len: {length2})")
                    else:
                        await bot.send_message(chat_id, f"👩🏽‍💻 {modul}th already deleted from /ban (len: {length2})")
                    break
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def check_tgph_posts(bot_username, BASE_D):
    try:
        arr = [k for k, v in TGPH_TOKENS.items() if bot_username in k]
        access_key = arr[0] if len(arr) else None
        if not access_key: return

        access_token = TGPH_TOKENS[access_key]
        telegraph_ = Telegraph(access_token=access_token)
        pages = await telegraph_.get_page_list()

        for item in pages['pages']:
            try:
                if item['url'] == access_key:
                    page = await telegraph_.get_page(path=item['path'], return_content=True, return_html=False)
                    try:
                        content_json = json.loads(str(page['content'][0]))
                    except:
                        content_json = {}

                    for OFFER_USERTID, v in content_json.items():
                        OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, \
                            OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, \
                            OFFER_DT, OFFER_TZ = v

                        sql = "INSERT OR IGNORE INTO OFFER (OFFER_USERTID, OFFER_TEXT, OFFER_MEDIATYPE, " \
                              "OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, " \
                              "OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT, " \
                              "OFFER_TZ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                        await db_change(sql, (int(OFFER_USERTID), v[OFFER_TEXT], v[OFFER_MEDIATYPE],
                                              v[OFFER_FILEID], v[OFFER_BUTTON], v[OFFER_ISBUTTON],
                                              v[OFFER_TGPHLINK], v[OFFER_ISTGPH], v[OFFER_ISSPOILER],
                                              v[OFFER_ISPIN], v[OFFER_ISSILENCE], v[OFFER_ISGALLERY],
                                              v[OFFER_DT], v[OFFER_TZ],), BASE_D)

                        del content_json[str(OFFER_USERTID)]
                        post_dumps = json.dumps(content_json, ensure_ascii=False)
                        await telegraph_.edit_page(path=item['path'], title=access_key, html_content=post_dumps)
                        return
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(0, 1), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
# endregion


# region admin
async def pre_upload(bot, chat_id, media_name, media_type, EXTRA_D, BASE_D):
    result = None
    try:
        sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILENAME=?"
        data = await db_select(sql, (media_name,), BASE_D)

        if not len(data):
            media = types.FSInputFile(os.path.join(EXTRA_D, media_name))
            res = None

            if media_type == 'photo':
                res = await bot.send_photo(chat_id=chat_id, photo=media)
                result = res.photo[-1].file_id
            elif media_type == 'video':
                res = await bot.send_video(chat_id=chat_id, video=media)
                result = res.video.file_id
            elif media_type == 'animation':
                res = await bot.send_animation(chat_id=chat_id, animation=media)
                result = res.animation.file_id
            elif media_type == 'audio':
                res = await bot.send_audio(chat_id=chat_id, audio=media)
                result = res.audio.file_id
            elif media_type == 'voice':
                res = await bot.send_voice(chat_id=chat_id, voice=media)
                result = res.voice.file_id
            elif media_type == 'video_note':
                res = await bot.send_video_note(chat_id=chat_id, video_note=media)
                result = res.video_note.file_id
            elif media_type == 'document':
                res = await bot.send_document(chat_id=chat_id, document=media, disable_content_type_detection=True)
                result = res.document.file_id
            elif media_type == 'sticker':
                res = await bot.send_sticker(chat_id=chat_id, sticker=media)
                result = res.sticker.file_id

            if res:
                await bot.delete_message(chat_id, res.message_id)
            sql = "INSERT OR IGNORE INTO FILE(FILE_FILEID, FILE_FILENAME) VALUES (?, ?)"
            await db_change(sql, (result, media_name,), BASE_D)
            logger.info(log_ % str(f'FILE_FILEID: {result}'))
        else:
            result = data[0][0]

        if media_type == 'photo':
            await bot.send_chat_action(chat_id=chat_id, action='upload_photo')
        elif media_type == 'video':
            await bot.send_chat_action(chat_id=chat_id, action='record_video')
        elif media_type == 'video_note':
            await bot.send_chat_action(chat_id=chat_id, action='record_video_note')
        elif media_type == 'animation':
            await bot.send_chat_action(chat_id=chat_id, action='record_video')
        elif media_type == 'audio':
            await bot.send_chat_action(chat_id=chat_id, action='upload_audio')
        elif media_type == 'voice':
            await bot.send_chat_action(chat_id=chat_id, action='record_voice')
        elif media_type == 'document':
            await bot.send_chat_action(chat_id=chat_id, action='upload_document')
        elif media_type == 'sticker':
            await bot.send_chat_action(chat_id=chat_id, action='choose_sticker')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id=1,
                            call=None):
    try:
        sql = "SELECT OFFER_ID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, " \
              "OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT FROM OFFER"
        data_offers = await db_select(sql, (), BASE_D)
        if not data_offers:
            if call: await call.message.delete()
            await bot.send_message(chat_id, yeref.l_post_text[lz], reply_markup=markupAdmin)
            await state.set_state(FsmOffer.text)
            return

        # region config
        post_id = 1 if post_id < 1 else post_id
        item = data_offers[post_id - 1]
        OFFER_ID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_ISTGPH, \
            OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT = item
        show_offers_datetime = yeref.l_post_datetime[lz]
        show_offers_button = yeref.l_post_buttons[lz]
        show_offers_off = yeref.l_off[lz]

        extra = f"\n\n{show_offers_datetime}: {OFFER_DT if OFFER_DT else show_offers_off}\n" \
                f"{show_offers_button}: {OFFER_BUTTON if OFFER_BUTTON else show_offers_off}\n"
        OFFER_TEXT = OFFER_TEXT or ''
        OFFER_TEXT = '' if OFFER_MEDIATYPE == 'video_note' or OFFER_MEDIATYPE == 'sticker' else OFFER_TEXT
        moment = 1020 - len(OFFER_TEXT) - len(extra)
        OFFER_TEXT = await correct_tag(
            f"{yeref.l_post_text[0:(len(OFFER_TEXT) + moment)]}") if moment <= 0 else OFFER_TEXT

        # endregion
        # region reply_markup
        reply_markup = get_keyboard_admin(data_offers, 'offers', post_id)

        buttons = [
            types.InlineKeyboardButton(text=f"✅ {yeref.l_btn[lz]}" if OFFER_ISBUTTON else f"☑️ {yeref.l_btn[lz]}",
                                       callback_data=f'ofr_isbtn_{OFFER_ID}_{post_id}'),
            types.InlineKeyboardButton(text=f"✅ {yeref.l_pin[lz]}" if OFFER_ISPIN else f"☑️ {yeref.l_pin[lz]}",
                                       callback_data=f'ofr_ispin_{OFFER_ID}_{post_id}'),
            types.InlineKeyboardButton(
                text=f"✅ {yeref.l_silence[lz]}" if OFFER_ISSILENCE else f"☑️ {yeref.l_silence[lz]}",
                callback_data=f'ofr_issilence_{OFFER_ID}_{post_id}'),
        ]
        reply_markup.row(*buttons)

        buttons = [
            types.InlineKeyboardButton(
                text=f"✅ {yeref.l_gallery[lz]}" if OFFER_ISGALLERY else f"☑️ {yeref.l_gallery[lz]}",
                callback_data=f'ofr_isgallery_{OFFER_ID}_{post_id}'),
            types.InlineKeyboardButton(text=f"✅ {yeref.l_preview[lz]}" if OFFER_ISTGPH else f"☑️ {yeref.l_preview[lz]}",
                                       callback_data=f'ofr_ispreview_{OFFER_ID}_{post_id}'),
            types.InlineKeyboardButton(
                text=f"✅ {yeref.l_spoiler[lz]}" if OFFER_ISSPOILER else f"☑️ {yeref.l_spoiler[lz]}",
                callback_data=f'ofr_isspoiler_{OFFER_ID}_{post_id}'),
        ]
        reply_markup.row(*buttons)

        buttons = [
            types.InlineKeyboardButton(text=yeref.l_post_new[lz],
                                       callback_data=f'ofr_new_{OFFER_ID}_{post_id}'),
            types.InlineKeyboardButton(text=yeref.l_post_delete[lz],
                                       callback_data=f'ofr_del_{OFFER_ID}_{post_id}'),
            types.InlineKeyboardButton(text=yeref.l_post_change[lz],
                                       callback_data=f'ofr_edit_{OFFER_ID}_{post_id}'),
        ]
        reply_markup.row(*buttons)

        reply_markup.row(types.InlineKeyboardButton(text=yeref.l_post_publish[lz],
                                                    callback_data=f'ofr_publication_{OFFER_ID}_{post_id}'))

        # endregion
        # region show
        if OFFER_FILEID and '[' not in OFFER_FILEID:
            OFFER_TEXT = OFFER_TEXT + extra
            if not call:
                if OFFER_MEDIATYPE == 'photo' or OFFER_MEDIATYPE == 'text':
                    await bot.send_photo(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                         reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                elif OFFER_MEDIATYPE == 'animation':
                    await bot.send_animation(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                elif OFFER_MEDIATYPE == 'video':
                    await bot.send_video(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                         reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                elif OFFER_MEDIATYPE == 'audio':
                    await bot.send_audio(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                         reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'document':
                    await bot.send_document(chat_id=chat_id, document=OFFER_FILEID, caption=OFFER_TEXT,
                                            disable_content_type_detection=True,
                                            reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'sticker':
                    await bot.send_sticker(chat_id=chat_id, sticker=OFFER_FILEID)
                    await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
                elif OFFER_MEDIATYPE == 'voice':
                    if has_restricted:
                        text = yeref.l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                        await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                               disable_web_page_preview=True)
                    else:
                        await bot.send_voice(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'video_note':
                    if has_restricted:
                        text = yeref.l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                    else:
                        await bot.send_video_note(chat_id=chat_id, video_note=OFFER_FILEID)
                    await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
            else:
                if OFFER_MEDIATYPE == 'photo' or OFFER_MEDIATYPE == 'text':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_photo(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                    else:
                        media = types.InputMediaPhoto(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                      has_spoiler=OFFER_ISSPOILER)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'animation':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_animation(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                                 reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                    else:
                        media = types.InputMediaAnimation(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                          has_spoiler=OFFER_ISSPOILER)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'video':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_video(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup(), has_spoiler=OFFER_ISSPOILER)
                    else:
                        media = types.InputMediaVideo(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                      has_spoiler=OFFER_ISSPOILER)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'audio':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_audio(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup())
                    else:
                        media = types.InputMediaAudio(media=OFFER_FILEID, caption=OFFER_TEXT)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'document':
                    if call.message.video_note or call.message.voice or call.message.sticker or call.message.text:
                        await bot.send_document(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                                disable_content_type_detection=True,
                                                reply_markup=reply_markup.as_markup())
                    else:
                        media = types.InputMediaDocument(media=OFFER_FILEID, caption=OFFER_TEXT,
                                                         disable_content_type_detection=True)
                        await call.message.edit_media(media=media, reply_markup=reply_markup.as_markup())
                elif OFFER_MEDIATYPE == 'sticker':
                    await bot.send_sticker(chat_id, OFFER_FILEID)
                    await bot.send_message(chat_id=chat_id, text=OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
                elif OFFER_MEDIATYPE == 'video_note':
                    if has_restricted:
                        text = yeref.l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                    else:
                        await bot.send_video_note(chat_id=chat_id, video_note=OFFER_FILEID)
                    await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                           disable_web_page_preview=True)
                elif OFFER_MEDIATYPE == 'voice':
                    if has_restricted:
                        text = yeref.l_post_has_restricted[lz].format(bot_un)
                        await bot.send_message(chat_id, text, disable_web_page_preview=True)
                        await bot.send_message(chat_id, OFFER_TEXT, reply_markup=reply_markup.as_markup(),
                                               disable_web_page_preview=True)
                    else:
                        await bot.send_voice(chat_id, OFFER_FILEID, caption=OFFER_TEXT,
                                             reply_markup=reply_markup.as_markup())
        else:
            if call and str(post_id) == await get_current_page_number(call):
                await call.message.edit_reply_markup(reply_markup=reply_markup.as_markup())
            elif OFFER_FILEID:
                OFFER_FILEID = ast.literal_eval(OFFER_FILEID) if OFFER_FILEID and '[' in OFFER_FILEID else OFFER_FILEID
                OFFER_MEDIATYPE = ast.literal_eval(
                    OFFER_MEDIATYPE) if OFFER_MEDIATYPE and '[' in OFFER_MEDIATYPE else OFFER_MEDIATYPE

                media = []
                for i in range(0, len(OFFER_FILEID)):
                    caption = OFFER_TEXT if i == 0 else None

                    if OFFER_MEDIATYPE[i] == 'photo':
                        media.append(
                            types.InputMediaPhoto(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                    elif OFFER_MEDIATYPE[i] == 'video':
                        media.append(
                            types.InputMediaVideo(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                    elif OFFER_MEDIATYPE[i] == 'audio':
                        media.append(types.InputMediaAudio(media=OFFER_FILEID[i], caption=caption))
                    elif OFFER_MEDIATYPE[i] == 'document':
                        media.append(types.InputMediaDocument(media=OFFER_FILEID[i], caption=caption,
                                                              disable_content_type_detection=True))

                await bot.send_media_group(chat_id, media)
                await bot.send_message(chat_id=chat_id, text=extra, reply_markup=reply_markup.as_markup())
        # endregion
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def get_current_page_number(call):
    result = '_'
    try:
        lst = call.message.reply_markup.inline_keyboard
        for items in lst:
            for it in items:
                if it.text.startswith('·'):
                    result = it.text.strip('·')
                    result = result.strip()
                    break
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, ids):
    try:
        if ids == 'me':
            user_ids = [chat_id]
        elif not ids or ids == 'all':
            sql = "SELECT USER_TID FROM USER"
            data = await db_select(sql, (), BASE_D)
            user_ids = [item[0] for item in data]
        else:
            sql = "SELECT USER_TID FROM USER"
            data = await db_select(sql, (), BASE_D)
            user_ids = [item[0] for item in data]
            user_ids = [item for item in user_ids if str(item) in ids]

        duration = 0 if len(user_ids) < 50 else int(len(user_ids) / 50)
        if str(chat_id) in my_tids:
            text = yeref.l_broadcast_start[lz].format(duration)
            await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
        all_len = len(user_ids)
        max_size = 20  # 1
        # max_size = 1  # 1
        fact_len = 0

        while True:
            try:
                random.shuffle(user_ids)
                await asyncio.sleep(0.05)
                tmp_user_ids = [user_ids.pop() for _ in range(0, max_size) if len(user_ids)]
                coroutines = [send_user(bot, tmp_user_id, offer_id, BASE_D) for tmp_user_id in tmp_user_ids]
                results = await asyncio.gather(*coroutines)

                for result in results:
                    if result:
                        fact_len += 1

                if not len(user_ids): break
                per = int(float(len(user_ids)) / float(all_len) * 100.0)

                if str(chat_id) in my_tids:
                    text = yeref.l_broadcast_process[lz].format(100 - per)
                    await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
            except Exception as e:
                logger.info(log_ % {str(e)})
                await asyncio.sleep(round(random.uniform(0, 1), 2))

        if str(chat_id) not in my_tids:
            sql = "DELETE FROM OFFER WHERE OFFER_ID=?"
            await db_change(sql, (offer_id,), BASE_D)

        text = yeref.l_broadcast_finish[lz].format(fact_len)
        await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def send_user(bot, chat_id, offer_id, BASE_D, message_id=None, current=1):
    result = None
    try:
        sql = "SELECT OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, " \
              "OFFER_TGPHLINK, OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, " \
              "OFFER_DT FROM OFFER WHERE OFFER_ID=?"
        data = await db_select(sql, (offer_id,), BASE_D)
        if not len(data): return
        OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, \
            OFFER_ISTGPH, OFFER_ISSPOILER, OFFER_ISPIN, OFFER_ISSILENCE, OFFER_ISGALLERY, OFFER_DT = data[0]

        len_ = 1
        if OFFER_ISBUTTON:
            reply_markup = await create_replymarkup2(bot, offer_id, OFFER_BUTTON, 'ofr')
        else:
            reply_markup = InlineKeyboardBuilder()

        if '[' in OFFER_MEDIATYPE:
            OFFER_FILEID = ast.literal_eval(OFFER_FILEID)
            OFFER_MEDIATYPE = ast.literal_eval(OFFER_MEDIATYPE)
            OFFER_TGPHLINK = ast.literal_eval(OFFER_TGPHLINK)
            len_ = len(OFFER_FILEID)

            OFFER_FILEID = OFFER_FILEID[current - 1] if message_id else OFFER_FILEID[0]
            OFFER_MEDIATYPE = OFFER_MEDIATYPE[current - 1] if message_id else OFFER_MEDIATYPE[0]
            OFFER_TGPHLINK = OFFER_TGPHLINK[current - 1] if message_id else OFFER_TGPHLINK[0]

        if OFFER_ISTGPH and OFFER_TGPHLINK and '[' not in OFFER_TGPHLINK:
            OFFER_MEDIATYPE = 'text'
            OFFER_TEXT = OFFER_TEXT if OFFER_TEXT and OFFER_TEXT != '' else "."
            OFFER_TEXT = f"<a href='{OFFER_TGPHLINK}'>​</a>{OFFER_TEXT}"

            if OFFER_ISGALLERY:
                buttons = [
                    types.InlineKeyboardButton(text="←", callback_data=f'gallery_prev_{offer_id}_{current}_{len_}'),
                    types.InlineKeyboardButton(text=f"{current}/{len_}",
                                               callback_data=f'gallery_current_{offer_id}_{current}_{len_}'),
                    types.InlineKeyboardButton(text="→", callback_data=f'gallery_next_{offer_id}_{current}_{len_}'),
                ]
                reply_markup.row(*buttons)

        if '[' in OFFER_MEDIATYPE and not message_id:
            media = []
            for i in range(0, len(OFFER_FILEID)):
                caption = OFFER_TEXT if i == 0 else None

                if OFFER_MEDIATYPE[i] == 'photo':
                    media.append(
                        types.InputMediaPhoto(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'video':
                    media.append(
                        types.InputMediaVideo(media=OFFER_FILEID[i], caption=caption, has_spoiler=OFFER_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'audio':
                    media.append(types.InputMediaAudio(media=OFFER_FILEID[i], caption=caption))
                elif OFFER_MEDIATYPE[i] == 'document':
                    media.append(types.InputMediaDocument(media=OFFER_FILEID[i], caption=caption,
                                                          disable_content_type_detection=True))

            result = await bot.send_media_group(chat_id, media)
        if OFFER_MEDIATYPE == 'text':
            # await bot.send_message(chat_id=5491025132, text='OFFER_TEXT2')
            result = await bot.send_message(chat_id=chat_id,
                                            text=OFFER_TEXT,
                                            disable_web_page_preview=not OFFER_ISTGPH,
                                            disable_notification=OFFER_ISSILENCE,
                                            reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'animation':
            result = await bot.send_animation(chat_id=chat_id,
                                              animation=OFFER_FILEID,
                                              caption=OFFER_TEXT,
                                              has_spoiler=OFFER_ISSPOILER,
                                              disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'photo':
            result = await bot.send_photo(chat_id=chat_id,
                                          photo=OFFER_FILEID,
                                          caption=OFFER_TEXT,
                                          has_spoiler=OFFER_ISSPOILER,
                                          disable_notification=OFFER_ISSILENCE,
                                          reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'video':
            result = await bot.send_video(chat_id=chat_id,
                                          video=OFFER_FILEID,
                                          caption=OFFER_TEXT,
                                          has_spoiler=OFFER_ISSPOILER,
                                          disable_notification=OFFER_ISSILENCE,
                                          reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'audio':
            result = await bot.send_audio(chat_id=chat_id,
                                          audio=OFFER_FILEID,
                                          caption=OFFER_TEXT,
                                          disable_notification=OFFER_ISSILENCE,
                                          reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'voice':
            has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

            if has_restricted:
                result = await bot.send_voice(chat_id=chat_id,
                                              voice=OFFER_FILEID,
                                              caption=OFFER_TEXT,
                                              disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
            else:
                result = await bot.send_audio(chat_id=chat_id,
                                              audio=OFFER_FILEID,
                                              caption=OFFER_TEXT,
                                              disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'document':
            result = await bot.send_document(chat_id=chat_id,
                                             document=OFFER_FILEID,
                                             caption=OFFER_TEXT,
                                             disable_notification=OFFER_ISSILENCE,
                                             disable_content_type_detection=True,
                                             reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'video_note':
            has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

            if has_restricted:
                result = await bot.send_video(chat_id=chat_id,
                                              video=OFFER_FILEID,
                                              caption=OFFER_TEXT,
                                              has_spoiler=OFFER_ISSPOILER,
                                              disable_notification=OFFER_ISSILENCE,
                                              reply_markup=reply_markup.as_markup())
            else:
                result = await bot.send_video_note(chat_id=chat_id,
                                                   video_note=OFFER_FILEID,
                                                   disable_notification=OFFER_ISSILENCE,
                                                   reply_markup=reply_markup.as_markup())
        elif OFFER_MEDIATYPE == 'sticker':
            result = await bot.send_sticker(chat_id=chat_id,
                                            sticker=OFFER_FILEID,
                                            disable_notification=OFFER_ISSILENCE,
                                            reply_markup=reply_markup.as_markup())

        if result and OFFER_ISPIN and not message_id and isinstance(result, list):
            await bot.pin_chat_message(chat_id=chat_id, message_id=result[0].message_id, disable_notification=False)
        elif result and OFFER_ISPIN and not message_id:
            await bot.pin_chat_message(chat_id=chat_id, message_id=result.message_id, disable_notification=False)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def generate_calendar_admin(bot, state, lz, chat_id, message_id=None, is_new=True):
    try:
        data = await state.get_data()
        shift_month = data.get('shift_month', 0)

        dt_ = datetime.datetime.utcnow() + datetime.timedelta(hours=0) + datetime.timedelta(days=32 * shift_month)
        if shift_month:
            dt_ = datetime.datetime(year=dt_.year, month=dt_.month, day=1)

        month_dic = {
            1: yeref.l_month_1[lz],
            2: yeref.l_month_2[lz],
            3: yeref.l_month_3[lz],
            4: yeref.l_month_4[lz],
            5: yeref.l_month_5[lz],
            6: yeref.l_month_6[lz],
            7: yeref.l_month_7[lz],
            8: yeref.l_month_8[lz],
            9: yeref.l_month_9[lz],
            10: yeref.l_month_10[lz],
            11: yeref.l_month_11[lz],
            12: yeref.l_month_12[lz]
        }
        month = month_dic[dt_.month]

        reply_markup = InlineKeyboardBuilder()
        buttons = [
            types.InlineKeyboardButton(text="«", callback_data=f'calendar_left'),
            types.InlineKeyboardButton(text=f"{month} {dt_.year}", callback_data='cb_99'),
            types.InlineKeyboardButton(text="»", callback_data=f'calendar_right'),
        ]
        reply_markup.row(*buttons)

        buttons_ = [
            types.InlineKeyboardButton(text=yeref.l_weekday_1[lz], callback_data='cb_99'),
            types.InlineKeyboardButton(text=yeref.l_weekday_2[lz], callback_data='cb_99'),
            types.InlineKeyboardButton(text=yeref.l_weekday_3[lz], callback_data='cb_99'),
            types.InlineKeyboardButton(text=yeref.l_weekday_4[lz], callback_data='cb_99'),
            types.InlineKeyboardButton(text=yeref.l_weekday_5[lz], callback_data='cb_99'),
            types.InlineKeyboardButton(text=yeref.l_weekday_6[lz], callback_data='cb_99'),
            types.InlineKeyboardButton(text=yeref.l_weekday_7[lz], callback_data='cb_99'),
        ]
        reply_markup.row(*buttons_)

        week_first_day = datetime.datetime(year=dt_.year, month=dt_.month, day=1).weekday() + 1
        buttons_ = []
        for i in range(0, 6 * 7):
            buttons_.append(types.InlineKeyboardButton(text=" ", callback_data=f'cb_99'))

        month_days = monthrange(dt_.year, dt_.month)[1]
        for i in range(week_first_day + dt_.day - 1, month_days + week_first_day):
            cb_ = f'cb_{i - week_first_day + 1}..{dt_.month}..{dt_.year}'
            buttons_[i - 1] = types.InlineKeyboardButton(text=f"{i - week_first_day + 1}", callback_data=cb_)

        tmp = []
        for i in range(0, len(buttons_)):
            tmp.append(buttons_[i])
            if len(tmp) >= 7:
                reply_markup.row(*tmp)
                tmp = []

        if is_new:
            await bot.send_message(chat_id=chat_id, text=yeref.l_post_date[lz], reply_markup=reply_markup.as_markup())
        else:
            await bot.edit_message_text(chat_id=chat_id, text=yeref.l_post_date[lz], message_id=message_id,
                                        reply_markup=reply_markup.as_markup())
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def callbacks_ofr_admin(bot, FsmOffer, call, state, BASE_D, bot_un):
    try:
        chat_id = call.from_user.id
        cmd = str(call.data.split("_")[1])
        post_id = int(call.data.split("_")[-1])
        offer_id = int(call.data.split("_")[-2])
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

        if cmd == 'new':
            await state.clear()

            await state.set_state(FsmOffer.text)

            await bot.send_message(call.from_user.id, yeref.l_post_text[lz], reply_markup=markupAdmin)
        elif cmd == 'del':
            await state.clear()

            sql = "DELETE FROM OFFER WHERE OFFER_ID=?"
            await db_change(sql, (offer_id,), BASE_D)

            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id - 1,
                                    call)
        elif cmd == 'edit':
            await state.clear()

            await state.set_state(FsmOffer.text)
            await state.update_data(offer_id=offer_id)

            await bot.send_message(call.from_user.id, yeref.l_post_edit[lz], reply_markup=markupAdmin)
        elif cmd == 'isbtn':
            sql = "SELECT OFFER_BUTTON, OFFER_ISBUTTON FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_BUTTON, OFFER_ISBUTTON = data[0]

            if OFFER_BUTTON:
                OFFER_ISBUTTON = 0 if OFFER_ISBUTTON else 1
                sql = "UPDATE OFFER SET OFFER_ISBUTTON=? WHERE OFFER_ID=?"
                await db_change(sql, (OFFER_ISBUTTON, offer_id,), BASE_D)
                await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id,
                                        call)
            else:
                text = yeref.l_buttons_text[lz]
                await call.answer(text=text, show_alert=True)
        elif cmd == 'ispin':
            sql = "SELECT OFFER_ISPIN FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISPIN = 0 if data[0][0] else 1
            sql = "UPDATE OFFER SET OFFER_ISPIN=? WHERE OFFER_ID=?"
            await db_change(sql, (OFFER_ISPIN, offer_id,), BASE_D)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
        elif cmd == 'issilence':
            sql = "SELECT OFFER_ISSILENCE FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISSILENCE = 0 if data[0][0] else 1
            sql = "UPDATE OFFER SET OFFER_ISSILENCE=? WHERE OFFER_ID=?"
            await db_change(sql, (OFFER_ISSILENCE, offer_id,), BASE_D)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
        elif cmd == 'isgallery':
            sql = "SELECT OFFER_ISGALLERY, OFFER_FILEID FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISGALLERY, OFFER_FILEID = data[0]

            if OFFER_FILEID and '[' in OFFER_FILEID:
                OFFER_ISGALLERY = 0 if data[0][0] else 1
                sql = "UPDATE OFFER SET OFFER_ISGALLERY=? WHERE OFFER_ID=?"
                await db_change(sql, (OFFER_ISGALLERY, offer_id,), BASE_D)
                await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id,
                                        call)
            else:
                text = yeref.l_gallery_text[lz]
                await call.answer(text=text, show_alert=True)
        elif cmd == 'ispreview':
            sql = "SELECT OFFER_ISTGPH, OFFER_TGPHLINK FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISTGPH, OFFER_TGPHLINK = data[0]

            if not OFFER_TGPHLINK:
                text = yeref.l_preview_text[lz]
                await call.answer(text=text, show_alert=True)

            OFFER_ISTGPH = 0 if OFFER_ISTGPH else 1
            sql = "UPDATE OFFER SET OFFER_ISTGPH=? WHERE OFFER_ID=?"
            await db_change(sql, (OFFER_ISTGPH, offer_id,), BASE_D)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
        elif cmd == 'isspoiler':
            sql = "SELECT OFFER_ISSPOILER, OFFER_MEDIATYPE FROM OFFER WHERE OFFER_ID=?"
            data = await db_select(sql, (offer_id,), BASE_D)
            OFFER_ISSPOILER, OFFER_MEDIATYPE = data[0]

            if OFFER_MEDIATYPE and OFFER_MEDIATYPE in ['photo', 'animation', 'video'] or '[' in OFFER_MEDIATYPE:
                OFFER_ISSPOILER = 0 if data[0][0] else 1
                sql = "UPDATE OFFER SET OFFER_ISSPOILER=? WHERE OFFER_ID=?"
                await db_change(sql, (OFFER_ISSPOILER, offer_id,), BASE_D)
                await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id,
                                        call)
            else:
                text = yeref.l_spoiler_text[lz]
                await call.answer(text=text, show_alert=True)
        elif cmd == 'pub':
            await state.clear()
            await call.answer()

            reply_markup = InlineKeyboardBuilder()
            buttons = [
                types.InlineKeyboardButton(text=yeref.l_me[lz], callback_data=f"publication_me_{offer_id}"),
                types.InlineKeyboardButton(text=yeref.l_all[lz], callback_data=f"publication_all_{offer_id}"),
                types.InlineKeyboardButton(text=yeref.l_ids[lz], callback_data=f"publication_ids_{offer_id}"),
            ]
            reply_markup.add(*buttons).adjust(1)

            text = yeref.l_recipient[lz]
            await bot.send_message(chat_id, text, reply_markup=reply_markup.as_markup())
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def callbacks_publication_admin(bot, FsmIds, call, state, BASE_D):
    try:
        chat_id = call.from_user.id
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        data, option, offer_id = call.data.split('_')

        if option == 'me':
            loop = asyncio.get_event_loop()
            loop.create_task(broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, 'me'))
        elif option == 'all':
            loop = asyncio.get_event_loop()
            loop.create_task(broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, 'all'))
        elif option == 'ids':
            await state.set_state(FsmIds.start)
            await state.update_data(offer_id=offer_id)

            text = yeref.l_enter[lz]
            await bot.send_message(chat_id, text)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_ids_start_admin(bot, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)
        arr = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./?]', message.text)
        ids = [it for it in arr if it != '']
        data = await state.get_data()
        offer_id = data.get('offer_id')

        loop = asyncio.get_event_loop()
        loop.create_task(broadcast_send_admin(bot, chat_id, lz, offer_id, BASE_D, ids))
        await state.clear()
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_text_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        if message.text == '⬅️ Prev':
            await bot.send_message(chat_id, yeref.l_post_text[lz])
            await state.set_state(FsmOffer.text)
        elif message.text in ['➡️️ Next', '/Next']:
            await bot.send_message(chat_id, yeref.l_post_media[lz])
            await state.set_state(FsmOffer.media)
        else:
            if len(message.html_text) >= 1024:
                text = yeref.l_post_text_limit[lz].format(len(message.html_text))
                await bot.send_message(chat_id, text)
                return

            await state.update_data(offer_text=message.html_text)
            await bot.send_message(chat_id=chat_id, text=yeref.l_post_media[lz])
            await state.set_state(FsmOffer.media)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_album_admin(bot, FsmOffer, message, album, state, MEDIA_D, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        offer_text = None
        offer_file_id = None
        offer_file_type = None
        offer_tgph_link = None
        file_name_part = None

        if message.text == '⬅️ Prev':
            await bot.send_message(chat_id, yeref.l_post_text[lz])
            await state.set_state(FsmOffer.text)
        elif message.text in ['➡️️ Next', '/Next']:
            if not offer_text:
                await bot.send_message(chat_id, yeref.l_post_text_empty[lz].format(yeref.l_post_text[lz]))
                await state.set_state(FsmOffer.text)
            else:
                await generate_calendar_admin(bot, state, lz, chat_id)
                await state.set_state(FsmOffer.date_)
        else:
            await bot.send_message(chat_id, yeref.l_post_media_wait[lz].format('album', 1))

            for obj in album:
                if obj.photo:
                    media_id = obj.photo[-1].file_id
                    media_type = 'photo'
                    dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.jpg')
                    file_name_part_new = f"{dt_}"
                elif obj.video:
                    media_id = obj.video.file_id
                    media_type = 'video'
                    file_name_part_new = obj.video.file_name
                elif obj.audio:
                    media_id = obj.audio.file_id
                    media_type = 'video_note'
                    file_name_part_new = obj.video.file_name
                else:
                    media_id = obj.document.file_id
                    media_type = 'document'
                    file_name_part_new = obj.video.file_name

                file_name = os.path.join(MEDIA_D, file_name_part_new)
                file = await bot.get_file(media_id)
                await bot.download_file(file.file_path, file_name)

                tgph_link = await get_tgph_link(file_name)
                tgph_link = '' if tgph_link is None else tgph_link
                if file_name and os.path.exists(file_name): os.remove(file_name)

                offer_tgph_link = (ast.literal_eval(str(offer_tgph_link)) + [tgph_link]) if offer_tgph_link else [
                    tgph_link]
                file_name_part = (ast.literal_eval(str(file_name_part)) + [file_name_part_new]) if file_name_part else [
                    file_name_part_new]
                offer_file_id = (ast.literal_eval(str(offer_file_id)) + [media_id]) if offer_file_id else [media_id]
                offer_file_type = (ast.literal_eval(str(offer_file_type)) + [media_type]) if offer_file_type else [
                    media_type]

                await state.update_data(offer_file_id=str(offer_file_id),
                                        offer_file_type=str(offer_file_type),
                                        offer_tgph_link=str(offer_tgph_link),
                                        file_name_part=str(file_name_part))
                await asyncio.sleep(0.05)

            if len(ast.literal_eval(str(offer_file_id))) < 2:
                await bot.send_message(chat_id=chat_id, text=yeref.l_post_media[lz])
                await state.set_state(FsmOffer.media)
                return

            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_media_admin(bot, FsmOffer, message, state, MEDIA_D, BASE_D, EXTRA_D):
    chat_id = message.from_user.id
    lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

    try:
        data = await state.get_data()
        offer_text = data.get('offer_text', None)

        if message.text == '⬅️ Prev':
            await bot.send_message(chat_id, yeref.l_post_text[lz])
            await state.set_state(FsmOffer.text)
        elif message.text in ['➡️️ Next', '/Next']:
            if not offer_text:
                await bot.send_message(chat_id, yeref.l_post_text_empty[lz].format(yeref.l_post_text[lz]))
                await state.set_state(FsmOffer.text)
            else:
                text = yeref.l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                    yeref.l_post_button[lz].replace('XXXXX', '')
                await bot.send_message(chat_id, text)
                await state.set_state(FsmOffer.button)
        else:
            file_name = file_name_part = file_id = file_id_note = file_type = offer_tgph_link = None
            if message.text:
                await bot.send_message(chat_id=chat_id, text=yeref.l_post_media[lz])
                return
            elif message.photo:
                file_id = message.photo[-1].file_id
                file_name_part = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.jpg')}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'photo'
            elif message.animation:
                await bot.send_message(chat_id, yeref.l_post_media_wait[lz].format('giff', 1))
                file_id = message.animation.file_id
                file_name_part = f"{message.animation.file_name}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'animation'

                if not (file_name.lower().endswith('.mp4') or file_name.lower().endswith(
                        '.gif') or file_name.lower().endswith('.giff')):
                    clip = mp.VideoFileClip(file_name)
                    tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
                    clip.write_videofile(tmp_name, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                                         remove_temp=True)

                    if os.path.exists(file_name): os.remove(file_name)
                    file_name = os.path.join(os.path.dirname(file_name), get_name_without_ext(file_name) + '.mp4')
                    file_name_part = os.path.basename(file_name)
                    if os.path.exists(tmp_name): os.rename(tmp_name, file_name)
            elif message.sticker:
                if message.sticker.is_animated or message.sticker.is_video:
                    await bot.send_message(chat_id=chat_id, text=yeref.yeref.l_post_media[lz])
                    await state.set_state(FsmOffer.media)
                    return

                file_id = message.sticker.file_id
                dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.webp')
                file_name_part = f"{dt_}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'sticker'
            elif message.video:
                await bot.send_message(chat_id, yeref.l_post_media_wait[lz].format('video', 1))
                file_id = message.video.file_id
                file_name_part = f"{message.video.file_name}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)

                clip = mp.VideoFileClip(file_name)
                if int(clip.duration) < 60 and clip.size and clip.size[0] == clip.size[1] and clip.size[0] <= 640:
                    res = await bot.send_video_note(chat_id, types.FSInputFile(file_name))
                    file_id = res.video_note.file_id
                    file_type = 'video_note'
                else:
                    file_type = 'video'
            elif message.audio:  # m4a
                file_id = message.audio.file_id
                file_name_part = f"{message.audio.file_name}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'audio'

                performer = message.from_user.username if message.from_user.username else '@performer'
                title = message.from_user.first_name
                thumbnail = types.InputFile(os.path.join(EXTRA_D, 'img.jpg'))
                res = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(file_name), thumbnail=thumbnail,
                                           title=title, performer=performer)
                file_id = res.audio.file_id
                await bot.delete_message(chat_id, res.message_id)
            elif message.voice:
                await bot.send_message(chat_id, yeref.l_post_media_wait[lz].format('voice', 1))
                file_id = message.voice.file_id
                dt_ = datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.ogg')
                file_name_part = f"{dt_}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'voice'

                ogg_version = AudioSegment.from_ogg(file_name)
                ogg_version.export(file_name[:file_name.rfind('.')] + '.mp3', format="mp3")

                performer = message.from_user.username if message.from_user.username else '@performer'
                title = message.from_user.first_name
                thumbnail = types.InputFile(os.path.join(EXTRA_D, 'img.jpg'))
                res = await bot.send_audio(chat_id=chat_id, audio=types.FSInputFile(file_name), thumbnail=thumbnail,
                                           title=title, performer=performer)
                file_id_note = res.audio.file_id
                await bot.delete_message(chat_id, res.message_id)
            elif message.video_note:
                file_id = message.video_note.file_id
                file_name_part = f"{datetime.datetime.utcnow().strftime('%d-%m-%Y_%H-%M-%S-%f.mp4')}"
                file_name = os.path.join(MEDIA_D, file_name_part)
                file = await bot.get_file(file_id)
                await bot.download_file(file.file_path, file_name)
                file_type = 'video_note'

                res = await bot.send_video(chat_id=chat_id, video=types.FSInputFile(file_name))
                file_id_note = res.video.file_id
                await bot.delete_message(chat_id, res.message_id)
            elif message.document:
                file_id = message.document.file_id
                file_name_part = f"{message.document.file_name}"
                file_type = 'document'

            offer_tgph_link = await get_tgph_link(file_name)
            offer_tgph_link = '' if offer_tgph_link is None else offer_tgph_link
            if file_name and os.path.exists(file_name): os.remove(file_name)

            await state.update_data(offer_file_id=file_id, offer_file_id_note=file_id_note, offer_file_type=file_type,
                                    offer_tgph_link=offer_tgph_link, file_name_part=file_name_part)

            text = yeref.l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                yeref.l_post_button[lz].replace('XXXXX', '')
            await bot.send_message(chat_id, text)
            await state.set_state(FsmOffer.button)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    # except FileIsTooBig as e:
    #     logger.info(log_ % str(e))
    #     await asyncio.sleep(round(random.uniform(0, 1), 2))
    #     await bot.send_message(chat_id, yeref.l_post_media_toobig[lz])
    except Exception as e:
        if 'too big' in str(e):
            await bot.send_message(chat_id, yeref.l_post_media_toobig[lz])
        else:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_button_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        if message.text == '⬅️ Prev':
            await bot.send_message(message.from_user.id, yeref.l_post_media[lz])
            await state.set_state(FsmOffer.media)
        elif message.text in ['➡️️ Next', '/Next']:
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        else:
            res_ = await check_buttons(bot, chat_id, message.text.strip())
            if len(res_) == 0:
                text = yeref.l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                    yeref.l_post_button[lz].replace('XXXXX', '')
                await bot.send_message(chat_id, text)
                await state.set_state(FsmOffer.button)
                return

            await state.update_data(offer_button=message.text.strip())
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_date_cb_admin(bot, FsmOffer, call, state, BASE_D):
    try:
        chat_id = call.from_user.id
        offer_date = call.data.split('_')[-1]
        if offer_date == '99': return
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)

        day_, month_, year_ = offer_date.split('..')
        dt_user = datetime.datetime(year=int(year_), month=int(month_), day=int(day_))
        dt_user = dt_user.strftime("%d-%m-%Y")
        await state.update_data(offer_date=offer_date)

        sql = "SELECT USER_TZ FROM USER WHERE USER_TZ=?"
        data = await db_select(sql, (chat_id,), BASE_D)
        USER_TZ = data[0][0] if data[0][0] else "+00:00"
        offer_tz = USER_TZ
        await state.update_data(offer_tz=offer_tz)
        sign_ = USER_TZ[0]
        h_, m_ = USER_TZ.strip(sign_).split(':')
        dt_now = datetime.datetime.utcnow()
        if sign_ == "+":
            dt_cur = dt_now + datetime.timedelta(hours=int(h_), minutes=int(m_))
        else:
            dt_cur = dt_now - datetime.timedelta(hours=int(h_), minutes=int(m_))

        datetime_plus = (dt_cur + datetime.timedelta(hours=1)).strftime("%H:%M")
        datetime_current = dt_cur.strftime("%H:%M")

        text = yeref.l_generate_calendar_time[lz].format(dt_user, datetime_plus, datetime_current, USER_TZ)
        await bot.send_message(chat_id, text)
        await state.set_state(FsmOffer.time_)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def calendar_handler_admin(bot, call, state, BASE_D):
    try:
        chat_id = call.from_user.id
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        message_id = call.message.message_id
        shift = call.data.split('_')[-1]

        data = await state.get_data()
        shift_month = data.get('shift_month', 0)

        if shift == 'left':
            shift_month = 0 if shift_month == 0 else shift_month - 1
        elif shift == 'right':
            shift_month = shift_month + 1

        await state.update_data(shift_month=shift_month)
        await generate_calendar_admin(bot, state, lz, chat_id, message_id, False)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_date_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)

        if message.text == '⬅️ Prev':
            text = yeref.l_post_button[lz].replace('XXXXX', message.chat.username) if message.chat.username else \
                yeref.l_post_button[lz].replace('XXXXX', '')
            await bot.send_message(chat_id, text)
            await state.set_state(FsmOffer.button)
        else:
            await bot.send_message(chat_id, yeref.l_post_finish[lz])
            await state.set_state(FsmOffer.finish)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_time_admin(bot, FsmOffer, message, state, BASE_D):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)
        text = message.text.strip()

        data = await state.get_data()
        offer_date = data.get('offer_date')
        day_, month_, year_ = offer_date.split('..')
        dt_user = datetime.datetime(year=int(year_), month=int(month_), day=int(day_))

        if message.text == '⬅️ Prev':
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        elif message.text in ['➡️️ Next', '/Next']:
            await bot.send_message(chat_id, yeref.l_post_finish[lz])
            await state.set_state(FsmOffer.finish)
        else:
            sql = "SELECT USER_TZ FROM USER WHERE USER_TID=?"
            data = await db_select(sql, (chat_id,), BASE_D)
            USER_TZ = data[0][0] if data[0][0] else "+00:00"
            offer_tz = USER_TZ
            await state.update_data(offer_tz=offer_tz)
            sign_ = USER_TZ[0]
            h_, m_ = USER_TZ.strip(sign_).split(':')
            dt_now = datetime.datetime.utcnow()
            if sign_ == "+":
                dt_cur = dt_now + datetime.timedelta(hours=int(h_), minutes=int(m_))
            else:
                dt_cur = dt_now - datetime.timedelta(hours=int(h_), minutes=int(m_))
            datetime_plus = (dt_cur + datetime.timedelta(hours=1)).strftime("%H:%M")
            datetime_current = dt_cur.strftime("%H:%M")

            try:
                arr = text.strip().split(':')
                dt_user_new = datetime.datetime(year=int(year_), month=int(month_), day=int(day_), hour=int(arr[0]),
                                                minute=int(arr[1]))
                if dt_user_new < dt_cur:
                    await message.answer(text=yeref.l_post_time_future[lz])
                    return
            except Exception as e:
                logger.info(log_ % str(e))
                text = yeref.l_generate_calendar_time[lz].format(dt_user.strftime("%d-%m-%Y"), datetime_plus,
                                                                 datetime_current, USER_TZ)
                await bot.send_message(chat_id, text)
                return

            offer_dt = dt_user_new.strftime('%d-%m-%Y %H:%M')
            await state.update_data(offer_dt=offer_dt)

            await bot.send_message(chat_id, yeref.l_post_finish[lz])
            await state.set_state(FsmOffer.finish)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fsm_finish_admin(bot, FsmOffer, message, state, EXTRA_D, BASE_D, bot_un):
    try:
        chat_id = message.from_user.id
        lz = await lz_code(chat_id, message.from_user.language_code, BASE_D)
        has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

        if message.text == '⬅️ Prev':
            await generate_calendar_admin(bot, state, lz, chat_id)
            await state.set_state(FsmOffer.date_)
        elif message.text in ['➡️️ Next', '/Next']:
            data = await state.get_data()
            offer_id = data.get('offer_id', None)
            offer_text = data.get('offer_text', None)
            offer_file_type = data.get('offer_file_type', 'text')
            default_photo = await pre_upload(bot, chat_id, 'text.jpg', 'photo', EXTRA_D, BASE_D)
            file_name_part = data.get('file_name_part', None)
            offer_file_id = data.get('offer_file_id', default_photo)
            offer_file_id_note = data.get('offer_file_id_note')

            offer_button = data.get('offer_button', None)
            offer_isbutton = 1 if offer_button else 0
            offer_tgph_link = data.get('offer_tgph_link', None)
            if offer_tgph_link and '[' in offer_tgph_link:
                offer_istgph = 1 if len([it for it in ast.literal_eval(str(offer_tgph_link)) if it != '']) else 0
            else:
                offer_istgph = 1 if offer_tgph_link else 0

            offer_tz = data.get('offer_tz', "+00:00")
            offer_dt = data.get('offer_dt', None)

            if offer_id:
                sql = "UPDATE OFFER SET OFFER_USERTID=?, OFFER_TEXT=?, OFFER_MEDIATYPE=?, OFFER_FILENAME=?, " \
                      "OFFER_FILEID=?, OFFER_FILEIDNOTE=?, OFFER_BUTTON=?, OFFER_ISBUTTON=?, OFFER_TGPHLINK=?, " \
                      "OFFER_ISTGPH=?, OFFER_DT=?, OFFER_TZ=?, OFFER_STATUS=? WHERE OFFER_ID=?"
                await db_change(sql, (chat_id, offer_text, offer_file_type, file_name_part, offer_file_id,
                                      offer_file_id_note, offer_button, offer_isbutton, offer_tgph_link,
                                      offer_istgph, offer_dt, offer_tz, 1, offer_id,), BASE_D)
            else:
                sql = "INSERT OR IGNORE INTO OFFER (OFFER_USERTID, OFFER_TEXT, OFFER_MEDIATYPE, OFFER_FILENAME, " \
                      "OFFER_FILEID, OFFER_FILEIDNOTE, OFFER_BUTTON, OFFER_ISBUTTON, OFFER_TGPHLINK, OFFER_ISTGPH, " \
                      "OFFER_DT, OFFER_TZ, OFFER_STATUS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                await db_change(sql, (chat_id, offer_text, offer_file_type, file_name_part, offer_file_id,
                                      offer_file_id_note, offer_button, offer_isbutton, offer_tgph_link,
                                      offer_istgph, offer_dt, offer_tz, 1,), BASE_D)

            sql = "SELECT * FROM OFFER"
            data = await db_select(sql, (), BASE_D)
            items = [item[0] for item in data]
            view_post_id = items.index(offer_id) + 1 if offer_id else len(data)
            await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, view_post_id)
            await state.clear()
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


def get_keyboard_admin(data, src, post_id=1):
    row_width = len(data) if len(data) < 5 else 5
    reply_markup = InlineKeyboardBuilder()
    btns = get_numbers_with_mark(data, post_id, row_width)
    buttons = []

    for i in range(1, row_width + 1):
        arr = re.split(r'\s|[«‹·›»]', btns[i - 1])  # ('\s|(?<!\d)[,.](?!\d)', s)
        page_i = list(filter(None, arr))[0]
        page_name = f'offers_{src}_{str(int(page_i))}'
        buttons.append(types.InlineKeyboardButton(text=btns[i - 1], callback_data=page_name))
    reply_markup.add(*buttons).adjust(row_width)

    return reply_markup


async def callbacks_offers_admin(bot, FsmOffer, call, state, BASE_D, bot_un):
    try:
        chat_id = call.from_user.id
        post_id = int(call.data.split("_")[-1])
        lz = await lz_code(chat_id, call.from_user.language_code, BASE_D)
        has_restricted = (await bot.get_chat(chat_id)).has_restricted_voice_and_video_messages

        await show_offers_admin(bot, FsmOffer, chat_id, lz, state, has_restricted, BASE_D, bot_un, post_id, call)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def gallery_handler_admin(bot, call, state, BASE_D):
    try:
        await state.clear()
        chat_id = call.from_user.id
        message_id = call.message.message_id
        data, option, offer_id, current, len_ = call.data.split("_")
        offer_id = int(offer_id)
        current = int(current)
        len_ = int(len_)

        if option == 'prev':
            current = len_ if current == 1 and option == 'prev' else current - 1
            await send_user(bot, chat_id, offer_id, BASE_D, message_id, current)
        elif option == 'next':
            current = 1 if current == len_ and option == 'next' else current + 1
            await send_user(bot, chat_id, offer_id, BASE_D, message_id, current)
        elif data[1] == 'current':
            pass
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def edit_inline(bot, post_id, inline_message_id, current, BASE_D):
    result = None
    try:
        sql = "SELECT POST_TEXT, POST_MEDIATYPE, POST_FILEID, POST_FILEIDNOTE, POST_BUTTON, POST_ISBUTTON, " \
              "POST_TGPHLINK, POST_ISTGPH, POST_ISGALLERY, POST_ISSPOILER FROM POST WHERE POST_ID=?"
        data_posts = await db_select(sql, (post_id,), BASE_D)
        if not len(data_posts): return
        item = data_posts[0]
        POST_TEXT, POST_MEDIATYPE, POST_FILEID, POST_FILEIDNOTE, POST_BUTTON, POST_ISBUTTON, POST_TGPHLINK, \
            POST_ISTGPH, POST_ISGALLERY, POST_ISSPOILER = item

        len_ = 0
        POST_TEXT = POST_TEXT if POST_TEXT else ''
        reply_markup = await create_replymarkup2(bot, post_id,
                                                 POST_BUTTON) if POST_ISBUTTON else InlineKeyboardBuilder()

        if '[' in POST_MEDIATYPE:
            POST_FILEID = ast.literal_eval(POST_FILEID)
            POST_MEDIATYPE = ast.literal_eval(POST_MEDIATYPE)
            POST_TGPHLINK = ast.literal_eval(POST_TGPHLINK)

            len_ = len(POST_FILEID)
            POST_FILEID = POST_FILEID[0]
            POST_MEDIATYPE = POST_MEDIATYPE[0]
            POST_TGPHLINK = POST_TGPHLINK[0]

        if POST_ISTGPH and POST_TGPHLINK:
            POST_MEDIATYPE = 'text'
            POST_TEXT = POST_TEXT if POST_TEXT and POST_TEXT != '' else "."
            POST_TEXT = f"<a href='{POST_TGPHLINK}'>​</a>{POST_TEXT}"

        if POST_ISGALLERY:
            buttons = [
                types.InlineKeyboardButton(text="←", callback_data=f'gal_prev_{post_id}_{current}_{len_}'),
                types.InlineKeyboardButton(text=f"{current}/{len_}",
                                           callback_data=f'gal_current_{post_id}_{current}_{len_}'),
                types.InlineKeyboardButton(text="→", callback_data=f'gal_next_{post_id}_{current}_{len_}'),
            ]
            reply_markup.row(*buttons)

        if POST_MEDIATYPE == 'text':
            await bot.edit_message_text(inline_message_id=inline_message_id, text=POST_TEXT,
                                        reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'photo':
            media = types.InputMediaPhoto(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'animation':
            media = types.InputMediaAnimation(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'video':
            media = types.InputMediaVideo(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'video_note':
            media = types.InputMediaVideo(media=POST_FILEIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'audio':
            media = types.InputMediaAudio(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'voice':
            media = types.InputMediaAudio(media=POST_FILEIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'document':
            media = types.InputMediaDocument(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
        else:
            media = types.InputMedia(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, inline_message_id=inline_message_id,
                                         reply_markup=reply_markup.as_markup())
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def edit_simple(bot, chat_id, post_id, message_id, current, BASE_D):
    result = None
    try:
        sql = "SELECT POST_TEXT, POST_MEDIATYPE, POST_FILEID, POST_FILEIDNOTE, POST_BUTTON, POST_ISBUTTON, " \
              "POST_TGPHLINK, POST_ISTGPH, POST_ISGALLERY, POST_ISSPOILER FROM POST WHERE POST_ID=?"
        data_posts = await db_select(sql, (post_id,), BASE_D)
        if not len(data_posts): return
        item = data_posts[0]
        POST_TEXT, POST_MEDIATYPE, POST_FILEID, POST_FILEIDNOTE, POST_BUTTON, POST_ISBUTTON, POST_TGPHLINK, \
            POST_ISTGPH, POST_ISGALLERY, POST_ISSPOILER = item

        len_ = 0
        POST_TEXT = POST_TEXT if POST_TEXT else ''
        reply_markup = await create_replymarkup2(bot, post_id,
                                                 POST_BUTTON) if POST_ISBUTTON else InlineKeyboardBuilder()

        if '[' in POST_MEDIATYPE and POST_ISGALLERY:
            POST_FILEID = ast.literal_eval(POST_FILEID)
            POST_MEDIATYPE = ast.literal_eval(POST_MEDIATYPE)
            POST_TGPHLINK = ast.literal_eval(POST_TGPHLINK)

            len_ = len(POST_FILEID)
            POST_FILEID = POST_FILEID[0]
            POST_MEDIATYPE = POST_MEDIATYPE[0]
            POST_TGPHLINK = POST_TGPHLINK[0]

        if POST_ISTGPH and POST_TGPHLINK:
            POST_MEDIATYPE = 'text'
            POST_TEXT = POST_TEXT if POST_TEXT and POST_TEXT != '' else "."
            POST_TEXT = f"<a href='{POST_TGPHLINK}'>​</a>{POST_TEXT}"

        if POST_ISGALLERY:
            buttons = [
                types.InlineKeyboardButton(text="←", callback_data=f'gal_prev_{post_id}_{current}_{len_}'),
                types.InlineKeyboardButton(text=f"{current}/{len_}",
                                           callback_data=f'gal_current_{post_id}_{current}_{len_}'),
                types.InlineKeyboardButton(text="→", callback_data=f'gal_next_{post_id}_{current}_{len_}'),
            ]
            reply_markup.row(*buttons)

        if POST_MEDIATYPE == 'text':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=POST_TEXT,
                                        reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'photo':
            media = types.InputMediaPhoto(media=POST_FILEID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,

                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'animation':
            media = types.InputMediaAnimation(media=POST_FILEID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'video':
            media = types.InputMediaVideo(media=POST_FILEID, caption=POST_TEXT, has_spoiler=POST_ISSPOILER)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'video_note':
            media = types.InputMediaVideo(media=POST_FILEIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'audio':
            media = types.InputMediaAudio(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'voice':
            media = types.InputMediaAudio(media=POST_FILEIDNOTE, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        elif POST_MEDIATYPE == 'document':
            media = types.InputMediaDocument(media=POST_FILEID, caption=POST_TEXT)
            await bot.edit_message_media(media=media, chat_id=chat_id, message_id=message_id,
                                         reply_markup=reply_markup.as_markup())
        else:
            OFFER_FILEID = ast.literal_eval(POST_FILEID) if POST_FILEID and '[' in POST_FILEID else POST_FILEID
            OFFER_MEDIATYPE = ast.literal_eval(POST_MEDIATYPE) if POST_MEDIATYPE and '[' in POST_MEDIATYPE else POST_MEDIATYPE

            media = []
            for i in range(0, len(OFFER_FILEID)):
                caption = POST_TEXT if i == 0 else None

                if OFFER_MEDIATYPE[i] == 'photo':
                    media.append(
                        types.InputMediaPhoto(media=OFFER_FILEID[i], caption=caption, has_spoiler=POST_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'video':
                    media.append(
                        types.InputMediaVideo(media=OFFER_FILEID[i], caption=caption, has_spoiler=POST_ISSPOILER))
                elif OFFER_MEDIATYPE[i] == 'audio':
                    media.append(types.InputMediaAudio(media=OFFER_FILEID[i], caption=caption))
                elif OFFER_MEDIATYPE[i] == 'document':
                    media.append(types.InputMediaDocument(media=OFFER_FILEID[i], caption=caption,
                                                          disable_content_type_detection=True))

            await bot.send_media_group(chat_id, media)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result

# endregion


# region functions
def escape_md(*content, sep=" ") -> str:
    """
    Escape markdown text

    E.g. for usernames

    :param content:
    :param sep:
    :return:
    """
    return markdown_decoration.quote(_join(*content, sep=sep))


def _join(*content, sep=" "):
    return sep.join(map(str, content))


async def get_chat_channel(bot, link, SESSION_D, BASE_S):
    result = None
    try:
        sql = "SELECT SESSION_TID, SESSION_STATUS FROM SESSION"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)

        for _ in data:
            sql = "SELECT SESSION_TID, SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_STATUS FROM SESSION"
            data = await db_select(sql, (), BASE_S)
            random.shuffle(data)
            SESSION_TID, SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_STATUS = data[0]
            if SESSION_STATUS is not None: continue

            try:
                sql = "UPDATE SESSION SET SESSION_STATUS=? WHERE SESSION_TID=?"
                await db_change(sql, (f'get_chat_channel', SESSION_TID,), BASE_S)

                logger.info(log_ % f"{SESSION_TID} {SESSION_NAME}")
                async with Client(name=os.path.join(SESSION_D, SESSION_NAME),
                                  api_id=SESSION_APIID, api_hash=SESSION_APIHASH) as app:
                    r = await join_my_chat(bot, app, my_tid, link, SESSION_TID, BASE_S)
                    try:
                        result = await bot.get_chat(r.id)
                    finally:
                        return
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired, SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS=? WHERE SESSION_TID=?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def auto_destroy_msg(bot, telegram_bot, chat_id, text, message_id, type_='text', sec=5):
    result = None
    try:
        step = 1
        by = f"<a href='https://t.me/{ferey_telegram_demo_bot}'>by</a>"
        text = f"{text}\n\n{by} @{telegram_bot} <b>{sec}</b>sec"
        ix_sec = text.rfind('</b>sec')
        while text[ix_sec] != '>': ix_sec -= 1

        while sec > 0:
            try:
                text = text.replace(f"<b>{sec}</b>sec", f"<b>{sec - 1}</b>sec")
                sec -= step
                if type_ == 'text':
                    await bot.edit_message_text(text, chat_id, message_id, disable_web_page_preview=True)
                else:
                    await bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=text)
                await asyncio.sleep(1)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
                break
        await bot.delete_message(chat_id, message_id)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def log_old(txt, LOG_DEFAULT, colour=92):
    try:
        logging.info(f'\033[{colour}m%s\033[0m' % (str(txt)))
        with open(LOG_DEFAULT, 'a') as f:
            f.write(str(txt) + '\n')
    except Exception as e:
        logger.info(f'\033[{95}m%s\033[0m' % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def log(txt, color=21):
    try:
        '''DESC
21 - underscore     !
30 - black          !
90 - grey
91 - red            !
92 - green          !
93 - yellow         
94 - blue
95 - purple         !
96 - cyan           !
97 - white
---------------------
100 - grey bg
101 - red bg
102 - green bg
103 - yellow bg
104 - blue bg
105 - purple bg
106 - cyan bg
107 - white bg
'''

        logger.info(f'\033[{color}m%s\033[0m' % str(txt))
    except Exception:
        await asyncio.sleep(round(random.uniform(0, 1), 2))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def fun_empty(txt):
    try:
        txt = str(txt)
        if '%' in txt:
            print(txt)
    except Exception as e:
        await log(f'\033[95m%s\033[0m' % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def lz_code(chat_id, lan, BASE_D):
    result = 'en'
    try:
        sql = "SELECT USER_LZ FROM USER WHERE USER_TID=?"
        data = await db_select(sql, (chat_id,), BASE_D)

        # first enter before DB
        if not len(data) or not data[0][0]:
            # chinese
            if lan in ['zh', 'zh-chs', 'zh-cht', 'ja', 'ko', 'zh-CN', 'zh-TW', 'th', 'vi', 'tw', 'sg']:
                result = 'zh'
            # arabic    # ir, af
            elif lan in ['ar-XA', 'ar', 'tr', 'ur', 'fa', 'tj', 'dz', 'eg', 'iq', 'sy', 'ae', 'sa', 'tn', 'ir', 'af']:
                result = 'ar'
            # spanish   # portugal: 'pt', 'br', 'ao', 'mz'
            elif lan in ['es', 'ar', 'cl', 'co', 'cu', 've', 'bo', 'pe', 'ec', 'pt', 'br', 'ao', 'mz']:
                result = 'es'
            # french
            elif lan in ['fr', 'ch', 'be', 'ca']:
                result = 'fr'
            # europe
            elif lan in ['ru', 'kz', 'kg', 'uz', 'tm', 'md', 'am', 'uk-UA', 'uk', 'kk', 'tk', 'ky']:
                result = 'ru'

            sql = "UPDATE USER SET USER_LZ=? WHERE USER_TID=?"
            await db_change(sql, (result, chat_id,), BASE_D)
        else:
            result = data[0][0]
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def no_war_text(txt):
    result = txt
    try:
        pass
        # result = txt.replace('а', 'ä').replace('А', 'Ä').replace('в', 'ʙ').replace('В', 'B').replace('г', 'ґ')
        # .replace('Г', 'Ґ').replace('е', 'é').replace('Е', 'É').replace('ж', 'җ').replace('Ж', 'Җ').replace('з', 'з́')
        # .replace('З', 'З́').replace('й', 'ҋ').replace('Й', 'Ҋ').replace('к','қ').replace('К', 'Қ').replace('М', 'M')
        # .replace('Н','H').replace('о', 'ô').replace('О', 'Ô').replace('р', 'p').replace('Р', 'P').replace('с', 'č')
        # .replace('С', 'Č').replace('т', 'ҭ').replace('Т', 'Ҭ').replace('у', 'ў').replace('У', 'Ў').replace('х', 'x')
        # .replace('Х', 'X').replace('э', 'є').replace('Э', 'Є')
        # result = txt.replace('А', 'Ä').replace('в', 'ʙ').replace('В', 'B').replace('г', 'ґ').replace('Г', 'Ґ').
        # replace('Е', 'É').replace('ж', 'җ').replace('Ж', 'Җ').replace('й', 'ҋ').replace('К', 'Қ').replace('М', 'M')
        # .replace('Н', 'H').replace('о', 'ô').replace('О', 'Ô').replace('р', 'p').replace('Р', 'P').replace('С', 'Č')
        # .replace('Т', 'Ҭ').replace('У', 'Ў').replace('х', 'x').replace('Х', 'X').replace('э', 'є')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def get_from_media(CONF_P, EXTRA_D, MEDIA_D, BASE_D, src, re_write=False, basewidth=1024):
    result = None
    try:
        is_link = await is_url(src)
        file_id = await get_fileid_from_src(src, is_link, BASE_D)
        if is_link and 'drive.google.com' not in src:
            result = src
        elif src is None:
            result = None
        elif file_id and re_write is False:
            result = file_id
        else:
            if os.path.basename(src) in os.listdir(MEDIA_D) and re_write is False:
                result = os.path.abspath(os.path.join(MEDIA_D, os.path.basename(src)))
            else:
                scopes = r_conf('scopes', CONF_P)
                credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
                credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
                http_auth = credentials.authorize(httplib2.Http())
                drive_service = build('drive', 'v3', http=http_auth, cache_discovery=False)

                if is_link:
                    docid = get_doc_id_from_link(src)
                    file_list_dic = await api_get_file_list(drive_service, docid, {}, is_file=True)
                else:
                    file_list_dic = await api_get_file_list(drive_service, (r_conf('share_folder_id', CONF_P))[0], {})

                for k, v in file_list_dic.items():
                    if is_link:
                        result = await api_dl_file(drive_service, k, v[0], v[1], MEDIA_D)
                        break
                    elif str(v[0]).lower() == str(os.path.basename(src)).lower():
                        result = await api_dl_file(drive_service, k, v[0], v[1], MEDIA_D)
                        break

            if await is_image(result):
                result = await resize_media(result, basewidth)
            elif await is_video(result):
                result = await resize_video_note(result, basewidth)
            logger.info(log_ % 'dl media ok')
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def is_url(url):
    status = False
    try:
        if url and '://' in url:  # and requests.get(url).status_code == 200:
            status = True
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return status


async def get_fileid_from_src(src, is_link, BASE_D):
    data = None
    try:
        if is_link:
            sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILELINK = ?"
        else:
            sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILENAME = ?"
        data = await db_select(sql, (src,), BASE_D)
        if not data:
            return None
        data = data[0][0]
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return data


async def is_image(file_name):
    im = None
    try:
        if str(file_name).lower().endswith('.docx') or str(file_name).lower().endswith('.pdf') or str(
                file_name).lower().endswith('.mp4'):
            return False
        im = Image.open(file_name)
    except Exception as e:
        logger.info(log_ % 'isImage: ' + str(e))
    finally:
        return im


async def is_video(file_name):
    vi = None
    try:
        vi = True if str(mimetypes.guess_type(file_name)[0]).startswith('video') else False
    except Exception as e:
        logger.info(log_ % 'isVideo: ' + str(e))
    finally:
        return vi


async def resize_media(file_name, basewidth=1024):
    result = file_name
    try:
        if str(file_name).lower().endswith('.png'):
            im = Image.open(file_name)
            rgb_im = im.convert('RGB')
            tmp_name = os.path.join(os.path.dirname(file_name), get_name_without_ext(file_name) + '.jpg')
            rgb_im.save(tmp_name)
            if os.path.exists(file_name):
                os.remove(file_name)
            result = file_name = tmp_name

        img = Image.open(file_name)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), Image.LANCZOS)
        img.save(file_name)
        result = file_name
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def resize_video_note(file_name, basewidth):
    result = file_name
    try:
        if not str(file_name).lower().endswith('.mp4'):
            clip = mp.VideoFileClip(file_name)
            tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
            clip.write_videofile(tmp_name, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                                 remove_temp=True)

            if os.path.exists(file_name):
                os.remove(file_name)
            file_name = os.path.join(os.path.dirname(file_name), get_name_without_ext(file_name) + '.mp4')
            if os.path.exists(tmp_name):
                os.rename(tmp_name, file_name)
            result = file_name
        if basewidth == 440:
            clip = mp.VideoFileClip(file_name)
            clip_resized = clip.resize((basewidth, basewidth))
            tmp_name = os.path.join(os.path.dirname(file_name), 'r_' + os.path.basename(file_name))
            clip_resized.write_videofile(tmp_name, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a',
                                         remove_temp=True)
            if os.path.exists(file_name):
                os.remove(file_name)
            if os.path.exists(tmp_name):
                os.rename(tmp_name, file_name)
            result = file_name
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def get_thumb(MEDIA_D, file_name, sz_thumbnail=32):
    size = sz_thumbnail, sz_thumbnail
    result = ''
    try:
        name = get_name_without_ext(file_name)
        im = Image.open(file_name)
        im.thumbnail(size, Image.ANTIALIAS)
        result = f'{MEDIA_D}/"thumbnail_"{name}'
        im.save(result, "JPEG")
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def check_username(username):
    result = True
    try:
        if str(username).isdigit():
            result = False
        elif len(username) < 4 or len(username) > 31:
            result = False
        elif username.startswith('_') or username.endswith('_'):
            result = False
        elif '@' in username and not username.startswith('@'):
            result = False
        else:
            for it in username:
                if it not in string.ascii_letters + string.digits + "@_":
                    result = False
                    return
    except TelegramRetryAfter as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


def touch(path):
    if not os.path.exists(path):
        with open(path, 'a'):
            os.utime(path, None)


def get_numbers_with_mark(data, id_, row_width=5):
    btns = []
    middle = int(row_width / 2 + 1)
    length = 5 if len(data) < 5 else len(data)

    if id_ == 1 or id_ == 2 or id_ == 3:
        btns.insert(0, f'1')
        btns.insert(1, f'2')
        btns.insert(2, f'3')
        btns.insert(3, f'4›')
        btns.insert(4, f'{length}»')

        btns[id_ - 1] = f'· {id_} ·'
    elif middle < id_ < length - middle + 1:  # 4
        btns.insert(0, f'«1')
        btns.insert(1, f'‹{id_ - 1}')
        btns.insert(2, f'· {id_} ·')
        btns.insert(3, f'{id_ + 1}›')
        btns.insert(4, f'{length}»')
    elif id_ == length or id_ == length - 1 or id_ == length - 2:
        btns.insert(0, f'«1')
        btns.insert(1, f'‹{length - 3}')
        btns.insert(2, f'{length - 2}')
        btns.insert(3, f'{length - 1}')
        btns.insert(4, f'{length}')

        btns[(row_width - (length - id_)) - 1] = f'· {id_} ·'

    if id_ == 4 and len(data) == 4:
        btns = ['«1', '‹2', '3', '· 4 ·', '5']

    return btns


def get_keyboard(data, src, post_id=1, group_id=''):
    row_width = len(data) if len(data) < 5 else 5
    reply_markup = InlineKeyboardBuilder()
    btns = get_numbers_with_mark(data, post_id, row_width)
    buttons = []

    for i in range(1, row_width + 1):
        arr = re.split(r'\s|[«‹·›»]', btns[i - 1])  # ('\s|(?<!\d)[,.](?!\d)', s)
        page_i = list(filter(None, arr))[0]
        page_name = f'page_{src}_{group_id}_{str(int(page_i))}'
        buttons.append(types.InlineKeyboardButton(text=btns[i - 1], callback_data=page_name))
    reply_markup.row(*buttons).adjust(row_width)

    return reply_markup


async def save_fileid(message, src, BASE_D):
    if message is None: return
    file_id = usr_id = ''
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.animation:  # giff
        file_id = message.animation.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.audio:  # m4a
        file_id = message.audio.file_id
    elif message.voice:
        file_id = message.voice.file_id
    elif message.video_note:
        file_id = message.video_note.file_id
    elif message.document:
        file_id = message.document.file_id
    elif message.poll:
        file_id = message.poll.id

    if await is_url(src):
        sql = f"INSERT OR IGNORE INTO FILE (FILE_FILEID, FILE_FILELINK) VALUES (?, ?);"
    else:
        sql = "INSERT OR IGNORE INTO FILE (FILE_FILEID, FILE_FILENAME) VALUES (?, ?);"
    if not await is_exists_filename_or_filelink(src, BASE_D):
        usr_id = await db_change(sql, (file_id, src,), BASE_D)
    return usr_id


async def is_exists_filename_or_filelink(src, BASE_D):
    sql = "SELECT * FROM FILE"
    data = await db_select(sql, (), BASE_D)
    for item in data:
        if src in item:
            return True
    return False


async def check_email(content):
    # Email-check regular expression
    result = None
    try:
        parts = content.split()
        for part in parts:
            USER_EMAIL = re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", part)
            if len(USER_EMAIL) != 0:
                result = USER_EMAIL[0]
                break
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def check_phone(content):
    result = None
    try:
        for phone in content.split():
            if phone and (str(phone).startswith('+') or str(phone).startswith('8') or str(phone).startswith('9') or str(
                    phone).startswith('7')) and len(str(phone)) >= 10:
                result = phone
                break
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


async def get_photo_file_id(bot, chat_id, file_id_text, BASE_D):
    result = None
    try:
        sql = "SELECT FILE_FILEID FROM FILE WHERE FILE_FILENAME='text.jpg'"
        data2 = await db_select(sql, (), BASE_D)
        if not len(data2):
            res = await bot.send_photo(chat_id, text_jpeg)
            result = res.photo[-1].file_id
            sql = "INSERT OR IGNORE INTO FILE (FILE_FILEID, FILE_FILENAME) VALUES (?, ?)"
            await db_change(sql, (file_id_text, 'text.jpg',), BASE_D)
        else:
            result = data2[0][0]
    except Exception as e:
        logger.info(log_ % str(e))
    finally:
        return result


def is_yes_not(msg):
    result = False
    try:
        if msg and str(msg).lower().strip() in ['y', 'yes', 'да', 'д', 'lf', 'l', '1']:
            result = True
    finally:
        return result


def w_conf(key, val, CONF_P, INI_D):
    try:
        CONF_P.read(INI_D)
        CONF_P.set(SECTION, key, str(val))

        with open(INI_D, 'w') as configfile:
            CONF_P.write(configfile)
    except Exception as e:
        print(e, 95)


def r_conf(key, CONF_P):
    result = None
    try:
        s = CONF_P.get(SECTION, key)
        result = ast.literal_eval(s)
        if len(result) == 0:
            result = None
    finally:
        return result


def get_doc_id_from_link(link):
    try:
        begin = link[0:link.rindex('/')].rindex('/') + 1
        end = link.rindex('/')
        link = link[begin:end]
    finally:
        return link


def get_tg_channel(lan):
    result = 'ferey_channel_english'
    try:
        # chinese
        if lan in ['zh', 'zh-chs', 'zh-cht', 'ja', 'ko', 'zh-CN', 'zh-TW', 'th', 'vi', 'tw', 'sg']:
            result = 'ferey_channel_chinese'
        # arabic    # ir, af
        elif lan in ['ar-XA', 'ar', 'tr', 'ur', 'fa', 'tj', 'dz', 'eg', 'iq', 'sy', 'ae', 'sa', 'tn', 'ir', 'af']:
            result = 'ferey_channel_arabic'
        # spanish   # portugal: 'pt', 'br', 'ao', 'mz'
        elif lan in ['es', 'ar', 'cl', 'co', 'cu', 've', 'bo', 'pe', 'ec', 'pt', 'br', 'ao', 'mz']:
            result = 'ferey_channel_spanish'
        # french
        elif lan in ['fr', 'ch', 'be', 'ca']:
            result = 'ferey_channel_french'
        # europe
        elif lan in ['ru', 'kz', 'kg', 'uz', 'tm', 'md', 'am', 'uk-UA', 'uk', 'kk', 'tk', 'ky']:
            result = 'ferey_channel_europe'
    except Exception as e:
        logger.info(e)
    finally:
        return result


def get_tg_group(lan):
    result = 'ferey_group_english'
    try:
        # chinese
        if lan in ['zh', 'zh-chs', 'zh-cht', 'ja', 'ko', 'zh-CN', 'zh-TW', 'th', 'vi', 'tw', 'sg']:
            result = 'ferey_group_chinese'
        # arabic    # ir, af
        elif lan in ['ar-XA', 'ar', 'tr', 'ur', 'fa', 'tj', 'dz', 'eg', 'iq', 'sy', 'ae', 'sa', 'tn', 'ir', 'af']:
            result = 'ferey_group_arabic'
        # spanish   # portugal: 'pt', 'br', 'ao', 'mz'
        elif lan in ['es', 'ar', 'cl', 'co', 'cu', 've', 'bo', 'pe', 'ec', 'pt', 'br', 'ao', 'mz']:
            result = 'ferey_group_spanish'
        # french
        elif lan in ['fr', 'ch', 'be', 'ca']:
            result = 'ferey_group_french'
        # europe
        elif lan in ['ru', 'kz', 'kg', 'uz', 'tm', 'md', 'am', 'uk-UA', 'uk', 'kk', 'tk', 'ky']:
            result = 'ferey_group_europe'
    except Exception as e:
        logger.info(e)
    finally:
        return result


async def send_to_admins(bot, CONF_P, txt):
    try:
        for admin_id in r_conf('admin_id', CONF_P):
            try:
                await bot.send_message(chat_id=int(admin_id), text=txt)
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
        logger.info(log_ % txt)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def template_sender(CONF_P, EXTRA_D, MEDIA_D):
    # post_media_id = None
    post_media_options = None

    # 1
    post_txt = f'''
🍃 Через 1 час в 20:00 я проведу прямой эфир!

Подключайся и смотри все самые интересные моменты!

🍂 Не пропусти возможность!
Переходи по моей ссылке, встроенной в кнопку.
'''
    post_btn = '🎥 Прямой эфир в instagram'
    post_url = 'https://www.instagram.com'
    post_media_type = 'photo'
    post_media_name = os.path.join(MEDIA_D, (r_conf('logo_name', CONF_P))[0])
    post_pin = False
    tmp_date = datetime.datetime.now() + datetime.timedelta(days=3)
    post_time = datetime.datetime(tmp_date.year, tmp_date.month, tmp_date.day, hour=20, minute=0)
    await save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name,
                                    post_media_type, post_pin, post_time, post_media_options)

    # 2
    post_txt = f'''
🔥 Как тебе прямой эфир? 
Расскажи об этом. 
Ниже я прикреплю Google-форму обратной связи

При заполнении, пришлю тебе Чек-лист по твоему запросу
'''
    post_btn = '⚠️ Google-форма обратной связи'
    post_url = 'https://docs.google.com/forms/d/e/1FAIpQLSehCkXuL9nCgRvPEdddgTnC99SMW-d_qTPzDjBzbASTAnX_lg/viewform'
    post_media_type = 'photo'
    post_media_name = os.path.join(MEDIA_D, (r_conf('logo_name', CONF_P))[0])
    post_pin = True
    tmp_date = datetime.datetime.now() + datetime.timedelta(days=4)
    post_time = datetime.datetime(tmp_date.year, tmp_date.month, tmp_date.day, hour=20, minute=0)
    await save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name,
                                    post_media_type, post_pin, post_time, post_media_options)

    # 3
    post_txt = post_btn = post_url = post_pin = None
    post_media_name = os.path.join(MEDIA_D, (r_conf('logo_name', CONF_P))[0])
    post_media_type = 'video_note'
    tmp_date = datetime.datetime.now() + datetime.timedelta(days=5)
    post_time = datetime.datetime(tmp_date.year, tmp_date.month, tmp_date.day, hour=20, minute=0)
    await save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name,
                                    post_media_type, post_pin, post_time, post_media_options)


async def api_update_send_folder(CONF_P, EXTRA_D, INI_D):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0]), r_conf('scopes', CONF_P))
    httpAuth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
    dynamic_folder_name = (r_conf('dynamic_folder_id', CONF_P))[0]
    file_list_dic = await api_get_file_list(drive_service, dynamic_folder_name, {})

    tmp = {}
    for k, v in file_list_dic.items():
        try:
            if v[1] == 'application/vnd.google-apps.folder':
                # google_folder.append(v[0])
                tmp[k] = v[0]
                # google_key.append(v[2])
        except Exception as e:
            logger.info(log_ % str(e))
            await asyncio.sleep(round(random.uniform(1, 2), 2))

    tmp = dict(sorted(tmp.items(), key=lambda para: para[-1], reverse=False))
    google_folder = []
    google_key = []
    for k, v in tmp.items():
        google_key.append(k)
        google_folder.append(v)

    # google_folder.sort()
    w_conf('google_folder', google_folder, CONF_P, INI_D)
    w_conf('google_key', google_key, CONF_P, INI_D)
    logger.info(log_ % google_folder)


async def scheduled_hour(part_of_hour, CONF_P, EXTRA_D, INI_D):
    logger.info(log_ % 'scheduled_hour ok')
    # await templateSender()
    await api_update_send_folder(CONF_P, EXTRA_D, INI_D)
    await asyncio.sleep(part_of_hour + 200)
    while True:
        logger.info(log_ % f'start sending...{str(datetime.datetime.now())}')
        await api_update_send_folder(CONF_P, EXTRA_D, INI_D)
        await asyncio.sleep(one_hour - (datetime.datetime.now()).minute * 60 + 200)


async def read_likes(BASE_D, POST_ID=1):
    cnt = '⁰'
    try:
        sql = "SELECT USER_ID FROM LIKE WHERE POST_ID = ?"
        data = await db_select(sql, (POST_ID,), BASE_D)
        cnt = str(0 + len(data))
        cnt = cnt.replace('0', '⁰').replace('1', '¹').replace('2', '²').replace('3', '³').replace('4', '⁴') \
            .replace('5', '⁵').replace('6', '⁶').replace('7', '⁷').replace('8', '⁸').replace('9', '⁹')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return cnt


async def db_has_like(user_id, post_id, BASE_D):
    data = True
    try:
        sql = "SELECT LIKE_ID FROM LIKE WHERE USER_ID=? AND POST_ID=?"
        data = await db_select(sql, (user_id, post_id,), BASE_D)
        data = True if data else False
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return data


async def random_text(text):
    result = text
    try:
        space_arr = []
        start_pos = 0
        for item in text:
            try:
                if item == ' ':
                    start_pos = (text.find(' ', start_pos)) + 1
                    space_arr.append(start_pos)
            except Exception:
                pass
        if len(space_arr) != 0:
            random_pos = random.choice(space_arr)
            result = f"{text[:random_pos]} {text[random_pos:]}"

        dic_char = {'В': 'B', 'М': '𐌑', 'С': 'Ϲ', 'а': 'a', 'в': 'ʙ', 'р': 'ρ', 'с': 'ϲ', 'п': 'n', 'ш': 'ɯ', 'э': '϶',
                    'к': 'κ'}  # 'и': 'ᥙ',
        arr = ['В', 'М', 'С', 'а', 'в', 'р', 'с', 'п', 'ш', 'э', 'к']  # 'и',
        random_chr = random.choice(arr)
        random_pos = arr.index(random_chr)
        for ix in range(0, random_pos):
            try:
                result = result.replace(arr[ix], dic_char[arr[ix]])
                result = f"{result}​"
            except Exception as e:
                logger.info(log_ % str(e))
                # await asyncio.sleep(round(random.uniform(1, 2), 2))

        result = result[0:1023]
        # result = result.replace('р', 'р')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


def is_tid(item):
    result = False
    try:
        result = int(item)
    except Exception:
        # logger.info(log_ % str(e))
        pass
    finally:
        return result


async def create_replymarkup(bot, owner_id, chat_id, offer_id, OFFER_BUTTON, BASE_D, COLUMN_OWNER="OFFER_CHATTID"):
    result = InlineKeyboardBuilder()
    try:
        if OFFER_BUTTON is None or OFFER_BUTTON == '': return
        tmp = []
        dic_btns = await check_buttons(bot, None, OFFER_BUTTON)
        buttons = []
        offer_id = int(offer_id)
        for k, v in dic_btns.items():
            try:
                if v[0]:
                    sql = f"SELECT * FROM OFFER WHERE {COLUMN_OWNER}=?"
                    data = await db_select(sql, (owner_id,), BASE_D)
                    items = [item[0] for item in data]
                    view_post_id = items.index(offer_id) + 1 if offer_id else len(data)

                    if len(tmp) > 0 and tmp[-1] is None:
                        result.add(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                        elif str(v[1]).startswith('btn_'):
                            buttons = [types.InlineKeyboardButton(text=str(v[0]),
                                                                  callback_data=f"{v[1]}_{chat_id}_{view_post_id}")]
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                        elif str(v[1]).startswith('btn_'):
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]),
                                                                      callback_data=f"{v[1]}_{chat_id}_{view_post_id}"))
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
        if len(buttons) > 0:
            result.add(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result.as_markup()


async def create_replymarkup2(bot, offer_id, OFFER_BUTTON, type_='pst'):
    result = None
    try:
        if OFFER_BUTTON is None or OFFER_BUTTON == '': return
        tmp = []
        buttons = []
        offer_id = int(offer_id)
        dic_btns = await check_buttons(bot, None, OFFER_BUTTON)
        result = InlineKeyboardBuilder()
        for k, v in dic_btns.items():
            try:
                if v[0]:
                    if len(tmp) > 0 and tmp[-1] is None:
                        result.add(*buttons)
                        if 'ᴵ' in v[0]:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat='')]
                        elif str(v[1]).startswith("btn_"):
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), callback_data=f"btn_{type_}_{offer_id}_{k}")]
                        else:
                            buttons = [types.InlineKeyboardButton(text=str(v[0]), url=v[1])]
                    else:
                        if 'ᴵ' in v[0]:
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), switch_inline_query_current_chat=''))
                        elif str(v[1]).startswith("btn_"):
                            buttons.append(
                                types.InlineKeyboardButton(text=str(v[0]), callback_data=f"btn_{type_}_{offer_id}_{k}"))
                        else:
                            buttons.append(types.InlineKeyboardButton(text=str(v[0]), url=v[1]))
                tmp.append(v[0])
            except Exception as e:
                logger.info(log_ % str(e))
                pass
        if len(buttons) > 0:
            result.add(*buttons)
    except Exception as e:
        logger.info(log_ % str(e))
        pass
    finally:
        return result


async def check_buttons(bot, chat_id, txt):
    result = {}
    txt = txt.strip()
    try:
        start_ = []
        finish_ = []
        for ix in range(0, len(txt)):
            try:
                if txt[ix] == '[':
                    start_.append([ix, '['])
                elif txt[ix] == ']':
                    finish_.append([ix, ']'])
                elif txt[ix] == '\n':
                    start_.append([ix, '\n'])
                    finish_.append([ix, '\n'])
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        if len(start_) != len(finish_): return

        for ix in range(0, len(start_)):
            try:
                if start_[ix][-1] == '\n':
                    result[ix] = [None, None]
                else:
                    tmp = txt[start_[ix][0] + 1: finish_[ix][0]]
                    split_btn = tmp.strip().split('|')
                    if len(split_btn) > 1:
                        btn_name = split_btn[0].strip() if len(split_btn) > 1 else "🔗 Go"
                        btn_link = split_btn[-1].strip()
                        if not await is_url(btn_link):
                            await bot.send_message(chat_id, f"🔗 {btn_link}: invalid")
                            return
                    else:
                        btn_name = split_btn[0]
                        # btn_link = cleanhtml(split_btn[0])[:20]
                        # btn_link = f"btn_{btn_link.encode('utf-8').hex()}"
                        btn_link = f"btn_"

                    result[ix] = [btn_name, btn_link]
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}", 95)
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html.strip())
    return cleantext


def get_post_of_dict(dicti_, pos=1):
    tmp = 1
    for k, v in dicti_.items():
        if tmp == pos:
            return k, v
        tmp += 1
    return None, None


async def get_proxy(identifier, EXTRA_D, CONF_P, server=None):
    result = None
    try:
        if r_conf('proxy', CONF_P) == 0: return

        with open(os.path.join(EXTRA_D, "proxy.txt"), "r") as f:
            lines = f.readlines()
        random.shuffle(lines)

        for line in lines:
            try:
                hostname, port, username, password = line.strip().split('..')
                # logger.info(log_ % f"proxy ({identifier}): {hostname}")
                result = {
                    "scheme": "socks5",
                    "hostname": hostname,
                    "port": int(port),
                    "username": username,
                    "password": password
                }
                break
            except Exception as e:
                await log(e)
                await asyncio.sleep(round(random.uniform(1, 2), 2))
    except Exception as e:
        logger.info(log_ % f"{str(e)}, {identifier}, {server}")
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def correct_link(link):
    result = link
    try:
        if len(str(link).strip()) < 4:
            result = None
            return
        link = link.strip()
        res = link.split()
        try:
            float(res[0])
            link = str(link.split()[1]).strip('@\'!')
        except:
            link = str(link.split()[0]).strip('@\'!')

        if link.startswith('t.me/') and not ('+' in link or 'join_my_chat' in link):
            link = link.replace('t.me/', '')
        elif link.startswith('t.me/') and ('+' in link or 'join_my_chat' in link):
            link = f"https://{link}"
        elif link.endswith('.t.me'):
            link = link.replace('.t.me', '')
        else:
            if 'http://' in link:
                link = link.replace('http://', 'https://')
            link = link[len(const_url):len(link)] if const_url in link and not (
                    't.me/+' in link or 't.me/join_my_chat/' in link) else link

        if 'https://telesco.pe/' in link:
            link = link.replace('https://telesco.pe/', '')

        try:
            link = str(int(link))
        except Exception:
            link = link if 't.me/+' in str(link) or 't.me/join_my_chat/' in str(link) else f"@{link}"

        try:
            if link.split('/')[-1].isdigit():
                link = f"{link[:link.rindex('/')]}"
        except Exception:
            pass

        try:
            if '+' in link:
                link = str(int(link.split('+')[-1]))
        except Exception:
            pass

        try:
            if link.startswith('join_my_chat/'):
                link = f"t.me/{link}"
            elif link.startswith('@join_my_chat/'):
                link = link.replace('@', 't.me/')
        except Exception:
            pass

        link = link.lstrip(':-.')

        try:
            link = link.replace('@://', '')
            link = link.replace('@//', '')
            link = link.replace('@/', '')
            link = link.replace('@.me/', '')
            link = link.replace('@.', '')
            link = link.replace('@@', '')
            for el in link:
                if el not in string.ascii_letters + string.digits + "@_https://t.me/+ ":
                    link = link.replace(el, '')
        except Exception:
            pass

        result = link
    except Exception:
        # await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


def is_names(phrase):
    # (?s)\bhello\b.*?\b
    keywords = ['names', 'сотка', 'скорость', 'like', 'концентрат', 'aяз', 'чит-код', "сборная", 'ск-', 'капитан',
                'лагерь']
    for keyword in keywords:
        if keyword.lower() in phrase.lower():
            return True
    return False


async def fun_stegano(f_name):
    result = f_name
    try:
        if not os.path.exists(f_name):
            logger.info(log_ % f"SteganoFun: no file {f_name}")
            return
        b_name = os.path.basename(f_name)
        d_name = os.path.dirname(f_name)
        random_name = os.path.join(d_name, f"{random.choice(string.ascii_letters + string.digits)}_{b_name}")
        random_len = random.randrange(5, 15)
        random_txt = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random_len))

        if f_name.lower().endswith('png'):
            tmp = lsb.hide(f_name, random_txt)
            tmp.save(random_name)

            if os.path.exists(f_name):
                os.remove(f_name)
            result = random_name
        elif f_name.lower().endswith('jpeg') or f_name.lower().endswith('jpg'):
            exifHeader.hide(f_name, random_name, random_txt)

            if os.path.exists(f_name):
                os.remove(f_name)
            result = random_name
        elif f_name.lower().endswith('pdf'):
            keys = ['Title', 'Author', 'Producer', 'Creator', 'Language', 'PDFVersion', 'CreatorTool', 'DocumentID',
                    'InstanceID', 'FileModifyDate']
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        et.set_tags([f_name], tags={key: random_txt}, params=["-P", "-overwrite_original"])
                except Exception:
                    # logger.info(log_ % f"for file {f_name}: {str(e)}");  logger.debug("")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            try:
                with ExifToolHelper() as et:
                    et.set_tags([f_name], tags={'FilePermissions': 777777}, params=["-P", "-overwrite_original"])
            except Exception:
                # logger.info(log_ % f"for file {f_name}: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))

            if os.path.exists(f_name):
                shutil.copyfile(f_name, random_name)
                os.remove(f_name)
            result = random_name
        elif f_name.lower().endswith('mov') or f_name.lower().endswith('mp4'):
            keys = ['Copyright', 'FileModifyDate', 'CreateDate', 'ModifyDate', 'TrackCreateDate', 'TrackModifyDate',
                    'MediaCreateDate', 'MediaModifyDate', 'MinorVersion']  # PageCount
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        random_date = (datetime.datetime.utcnow() - datetime.timedelta(
                            hours=random.randrange(1, 23))).strftime('%Y:%m:%d %H:%M:%S+03:00')
                        et.set_tags([f_name], tags={key: random_date}, params=["-P", "-overwrite_original"])
                except Exception:
                    # logger.info(log_ % f"for file {f_name}: {str(e)}")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            keys = ['XResolution', 'YResolution', 'Duration']
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        random_num = random.randrange(1, 180)
                        et.set_tags([f_name], tags={key: random_num}, params=["-P", "-overwrite_original"])
                except Exception:
                    # logger.info(log_ % f"for file {f_name}: {str(e)}")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            if os.path.exists(f_name):
                shutil.copyfile(f_name, random_name)
                os.remove(f_name)
            result = random_name
        else:
            keys = ['FileModifyDate']
            for key in keys:
                try:
                    with ExifToolHelper() as et:
                        random_date = (datetime.datetime.utcnow() - datetime.timedelta(
                            hours=random.randrange(1, 23))).strftime('%Y:%m:%d %H:%M:%S+03:00')
                        et.set_tags([f_name], tags={key: random_date}, params=["-P", "-overwrite_original"])
                except Exception as e:
                    logger.info(log_ % f"for file {f_name}: {str(e)}")
                    await asyncio.sleep(round(random.uniform(0, 1), 2))

            try:
                with ExifToolHelper() as et:
                    et.set_tags([f_name], tags={'FilePermissions': 777777}, params=["-P", "-overwrite_original"])
            except Exception as e:
                logger.info(log_ % f"for file {f_name}: {str(e)}")
                await asyncio.sleep(round(random.uniform(0, 1), 2))

            if os.path.exists(f_name):
                shutil.copyfile(f_name, random_name)
                os.remove(f_name)
            result = random_name
        logger.info(log_ % f"stagano ok")
    except Exception as e:
        logger.info(log_ % f"stageno error: {str(e)}")
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


async def correct_tag(txt):
    result = txt
    try:
        cnt_open = cnt_close = 0
        last_ix_open = last_ix_close = 0
        for i in range(0, len(txt)):
            try:
                if txt[i] == '<' and i + 1 < len(txt) - 1 and txt[i + 1] != '/':
                    cnt_open += 1
                    last_ix_open = i
                elif txt[i] == '<' and i + 1 < len(txt) - 1 and txt[i + 1] == '/':
                    cnt_close += 1
                    last_ix_close = i
            except Exception as e:
                logger.info(log_ % str(e))
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        if cnt_open and cnt_close:
            flag = False
            tmp = last_ix_close
            while tmp < len(txt) - 1:
                tmp += 1
                if txt[tmp] == '>':
                    flag = True
                    break
            if not flag:
                result = f"{txt[0:last_ix_open]}.."
        elif cnt_open and cnt_close and cnt_open != cnt_close:
            result = f"{txt[0:last_ix_open]}.."
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def haversine(lon1, lat1, lon2, lat2):
    result = None
    try:
        """
        Calculate the great circle distance in kilometers between two points
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6372
        result = c * r * 1000.0
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


# endregion


# region pyrogram
async def get_session(SESSION_TID, SESSION_D, BASE_S, EXTRA_D, CONF_P, is_proxy=False):
    res = proxy = None
    try:
        sql = "SELECT SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_PHONE FROM SESSION WHERE SESSION_TID = ?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not len(data): return
        SESSION_NAME, SESSION_APIID, SESSION_APIHASH, SESSION_PHONE = data[0]

        if is_proxy:
            proxy = await get_proxy(SESSION_TID, EXTRA_D, CONF_P)

        res = Client(name=os.path.join(SESSION_D, SESSION_NAME), api_id=SESSION_APIID, api_hash=SESSION_APIHASH,
                     phone_number=SESSION_PHONE, proxy=proxy)
    finally:
        return res


async def is_my_chat(bot, chat_id, link, SESSIONS_D, EXTRA_D, CONF_P, BASE_S, BASE_E, is_history=False):
    result = None
    get_chat_history_count = 0
    try:
        sql = "SELECT SESSION_TID,SESSION_STATUS FROM SESSION WHERE SESSION_SPAM IS NOT '*' LIMIT 10"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)
        for item in data:
            SESSION_TID, SESSION_STATUS = item
            if not (await check_session_flood(SESSION_TID, BASE_S) and (
                    SESSION_STATUS == '' or SESSION_STATUS is None)): continue
            try:
                link = await correct_link(link)
                if not link: return

                # process
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (f'isChat', SESSION_TID,), BASE_S)

                async with await get_session(SESSION_TID, SESSIONS_D, BASE_S, EXTRA_D, CONF_P, False) as app:
                    r = await join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S)
                    if r is None:
                        logger.info(log_ % f"{link} is None")
                        return
                    txt_ = f"👩🏽‍💻 Администратор закрытой группы не принял заявки на вступление"
                    if r == -1:
                        await bot.send_message(chat_id, txt_)
                        return
                    result = await app.get_chat(r.id)
                    if is_history:
                        try:
                            get_chat_history_count = await app.get_chat_history_count(r.id)
                        except Exception as e:
                            await log(e)
                            await asyncio.sleep(round(random.uniform(0, 1), 2))

                    await leave_my_chat(app, result, link)
                break
            except (FloodWait, SlowmodeWait) as e:
                wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
                logger.info(log_ % wait_)
                await asyncio.sleep(round(random.uniform(5, 10), 2))

                till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime(
                    "%d-%m-%Y_%H-%M")
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                SESSION_STATUS = f'Wait {till_time}'
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired,
                    SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
                await delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S)
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(1, 2), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result, get_chat_history_count


async def is_invite_chat(bot, chat_id, link, SESSIONS_D, EXTRA_D, CONF_P, BASE_S, BASE_E):
    result = None
    try:
        sql = "SELECT SESSION_TID,SESSION_STATUS FROM SESSION WHERE SESSION_SPAM IS NOT '*'"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)
        for item in data:
            SESSION_TID, SESSION_STATUS = item
            if not (await check_session_flood(SESSION_TID, BASE_S) and (
                    SESSION_STATUS == '' or SESSION_STATUS is None)): continue
            try:
                link = await correct_link(link)
                if not link: continue

                # process
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (f'isChat', SESSION_TID,), BASE_S)

                async with await get_session(SESSION_TID, SESSIONS_D, BASE_S, EXTRA_D, CONF_P) as app:
                    r = await join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S)

                    # get_chat https://t.me/+KO7_fV4aGKZkYTUy
                    if r == -1 or r is None: return
                    r = await app.get_chat(r.id)
                    logger.info(log_ % f"{SESSION_TID} get_chat {r.id}")

                    if not (r.type.value in ['group', 'supergroup']):
                        text = "🚶 Вставь ссылку на группу, а не канал"
                        await bot.send_message(chat_id, text)
                    elif hasattr(r.permissions, 'can_invite_users') and not r.permissions.can_invite_users:
                        text = "🚶 Зайди в «Разрешения» группы и включи <i>участникам группы</i> возможность: " \
                               "«Добавление участников»"
                        await bot.send_message(chat_id, text)
                    else:
                        text = "🚶 Начинаем проверку группы..\n#длительность 2мин"
                        await bot.send_message(chat_id, text)
                        # await asyncio.sleep(r_conf('AWAIT_JOIN'))

                        try:
                            get_chat_member = await app.get_chat_member(chat_id=r.id, user_id=int(SESSION_TID))
                            result = True if get_chat_member and get_chat_member.status.value == 'member' else False
                        except Exception as e:
                            await log(e)
                            await asyncio.sleep(round(random.uniform(1, 2), 2))

                    # leave_chat
                    await leave_my_chat(app, r, link)
                break
            except (FloodWait, SlowmodeWait) as e:
                wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
                logger.info(log_ % wait_)
                await asyncio.sleep(round(random.uniform(5, 10), 2))

                till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime(
                    "%d-%m-%Y_%H-%M")
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                SESSION_STATUS = f'Wait {till_time}'
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired,
                    SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
                await delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S)
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(1, 2), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S):
    result = None
    try:
        if 't.me/c/' in str(link):
            try:
                tmp = link.strip('https://t.me/c/').split('/')[0]
                peer_channel = await app.resolve_peer(int(f"-100{tmp}"))
                result = await app.invoke(functions.channels.JoinChannel(channel=peer_channel))
            except Exception as e:
                await log(e)
        else:
            result = await app.join_chat(link)
        await asyncio.sleep(1)
    except (FloodWait, SlowmodeWait) as e:
        text = log_ % f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
        logger.info(text)
        await asyncio.sleep(round(random.uniform(5, 10), 2))

        till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime("%d-%m-%Y_%H-%M")
        sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
        SESSION_STATUS = f'Wait {till_time}'
        await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except UserAlreadyParticipant as e:
        logger.info(log_ % f"UserAlreadyParticipant {link}: {str(e)}")
        try:
            result = await app.get_chat(link)
        except Exception:
            pass
    except (InviteHashExpired, InviteHashInvalid) as e:
        await log(e)
        try:
            result = await app.join_chat(link)
        except Exception:
            await bot.send_message(chat_id, f"️👩🏽‍💻 Link {link} is invalid or try later")
    except (UsernameInvalid, UsernameNotOccupied, ChannelBanned) as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
        await bot.send_message(chat_id, f"️👩🏽‍💻 Link {link} is invalid or try later")
    except BadRequest as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(2, 3), 2))

        try:
            result = await app.join_chat(link)
        except Exception:
            result = -1
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def leave_my_chat(app, r, link):
    try:
        chat_id = r.id if r and ('t.me/+' in str(link) or 'join_my_chat/' in str(link)) else link
        # like_names_res = is_names(r.title)
        if r.username and f'ferey' in r.username: return

        await app.leave_chat(chat_id, True)
        # logger.info(log_ % f"\t{link} leave chat")
    except (FloodWait, SlowmodeWait) as e:
        wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
        logger.info(log_ % wait_)
        await asyncio.sleep(e.value + 1)
    except Exception:
        # logger.info(log_ % f"leave_my_chat_error: {link} {str(e)}")
        await asyncio.sleep(round(random.uniform(5, 10), 2))


async def get_chat_members(bot, chat_id, link, SESSIONS_D, EXTRA_D, CONF_P, BASE_S, BASE_E):
    result = []
    try:
        text = f"🚶 Проверяем участников группы..\n#длительность 1мин"
        await bot.send_message(chat_id, text)
        sql = "SELECT SESSION_TID,SESSION_STATUS FROM SESSION WHERE SESSION_SPAM IS NOT '*'"
        data = await db_select(sql, (), BASE_S)
        random.shuffle(data)
        for item in data:
            tmp_members = []
            SESSION_TID, SESSION_STATUS = item
            if not (await check_session_flood(SESSION_TID, BASE_S) and (
                    SESSION_STATUS == '' or SESSION_STATUS is None)): continue
            try:
                link = await correct_link(link)
                if not link: continue

                # process
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (f'getChatMembers', SESSION_TID,), BASE_S)

                async with await get_session(SESSION_TID, SESSIONS_D, BASE_S, EXTRA_D, CONF_P) as app:
                    r = await join_my_chat(bot, app, chat_id, link, SESSION_TID, BASE_S)

                    # get members
                    sql = "SELECT SESSION_TID FROM SESSION"
                    data_ = await db_select(sql, (), BASE_S)
                    data_ = [str(item[0]) for item in data_]
                    try:
                        async for member in app.get_chat_members(r.id, filter=enums.ChatMembersFilter.SEARCH):
                            if member.user.username and not member.user.is_bot and not member.user.is_deleted and \
                                    not member.user.is_scam and not member.user.is_fake and not member.user.is_support \
                                    and str(member.user.id) not in data_:
                                tmp_members.append(member.user.username)
                    except ChatAdminRequired as e:
                        await log(e)
                        await bot.send_message(chat_id, f"🔺 Требуются права админа")
                        return
                    except Exception as e:
                        await log(e)

                    # leave chat
                    await leave_my_chat(app, r, link)

                    result = tmp_members
                    break
            except (FloodWait, SlowmodeWait) as e:
                wait_ = f"Wait: {datetime.datetime.utcfromtimestamp(e.value + 1).strftime('%H:%M:%S')}"
                logger.info(log_ % wait_)
                await asyncio.sleep(round(random.uniform(5, 10), 2))

                till_time = (datetime.datetime.now() + datetime.timedelta(seconds=e.value + 1)).strftime(
                    "%d-%m-%Y_%H-%M")
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                SESSION_STATUS = f'Wait {till_time}'
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
            except (UserDeactivatedBan, UserDeactivated, AuthKeyInvalid, AuthKeyUnregistered, AuthKeyDuplicated,
                    SessionExpired,
                    SessionRevoked) as e:
                logger.info(log_ % f"{SESSION_TID} deactivated: {str(e)}")
                await asyncio.sleep(round(random.uniform(5, 10), 2))
                await delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S)
            except Exception as e:
                logger.info(log_ % f"{SESSION_TID}: {str(e)}")
                await asyncio.sleep(round(random.uniform(1, 2), 2))
            finally:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (SESSION_STATUS, SESSION_TID,), BASE_S)
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def delete_account(bot, SESSION_TID, SESSIONS_D, CONF_P, BASE_S):
    try:
        sql = "SELECT SESSION_NAME FROM SESSION WHERE SESSION_TID=?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not data:
            await bot.send_message(my_tid, f"✅ Account {SESSION_TID} doesnt exist")
            return
        SESSION_NAME = os.path.join(SESSIONS_D, f'{data[0][0]}.session')

        sql = "DELETE FROM SESSION WHERE SESSION_TID = ?"
        await db_change(sql, (SESSION_TID,), BASE_S)

        sql = "DELETE FROM COMPANY WHERE COMPANY_FROMUSERTID = ?"
        await db_change(sql, (SESSION_TID,), BASE_S)

        if os.path.exists(SESSION_NAME):
            os.remove(SESSION_NAME)
        await bot.send_message(my_tid, f"✅ deleteAccount {SESSION_TID} ok")
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        await log(e, CONF_P)
        await asyncio.sleep(round(random.uniform(1, 2), 2))


async def delete_invalid_chat(chat, BASE_E):
    sql = "DELETE FROM CHANNEL WHERE CHANNEL_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM CHAT WHERE CHAT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM USER WHERE USER_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM BOT WHERE BOT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    chat = chat.strip('@')

    sql = "DELETE FROM CHANNEL WHERE CHANNEL_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM CHAT WHERE CHAT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM USER WHERE USER_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    sql = "DELETE FROM BOT WHERE BOT_USERNAME=?"
    await db_change(sql, (chat,), BASE_E)

    # chat = chat if 'https://' in chat else f"@{chat}"
    # await send_to_admins(f"deleteInvalidChat {chat}")


async def check_session_flood(SESSION_TID, BASE_S):
    result = SESSION_TID
    try:
        sql = "SELECT SESSION_STATUS FROM SESSION WHERE SESSION_TID = ?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not data: return

        t_t = str(data[0][0]).split()
        if len(t_t) == 2:
            date_ = t_t[1].split('_')[0]
            time_ = t_t[1].split('_')[1]

            day = int(date_.split('-')[0])
            month = int(date_.split('-')[1])
            year = int(date_.split('-')[2])
            hour = int(time_.split('-')[0])
            minute = int(time_.split('-')[1])

            diff = datetime.datetime.now() - datetime.datetime(year=year, month=month, day=day, hour=hour,
                                                               minute=minute)

            if diff.days >= 0:
                sql = "UPDATE SESSION SET SESSION_STATUS = ? WHERE SESSION_TID = ?"
                await db_change(sql, (None, SESSION_TID,), BASE_S)
                result = SESSION_TID
            else:
                result = None
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def check_session_limit(SESSION_TID, LIMIT_NAME, LIMIT, BASE_S):
    result = SESSION_TID
    try:
        sql = f"SELECT {LIMIT_NAME} FROM SESSION WHERE SESSION_TID = ?"
        data = await db_select(sql, (SESSION_TID,), BASE_S)
        if not data: return

        t_t = str(data[0][0]).split()
        if len(t_t) == 2:
            msg_by_day = int(t_t[0])
            date_ = t_t[1].split('-')

            day = int(date_[0])
            month = int(date_[1])
            year = int(date_[2])

            diff = datetime.datetime.now() - datetime.datetime(year=year, month=month, day=day)

            if diff.days > 0:
                result = f"0 {datetime.datetime.now().strftime('%d-%m-%Y')}"
                sql = f"UPDATE SESSION SET {LIMIT_NAME} = ? WHERE SESSION_TID = ?"
                await db_change(sql, (result, SESSION_TID,), BASE_S)
            elif msg_by_day < LIMIT:
                result = SESSION_TID
            else:
                result = None
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


async def check_inviteday(CONF_P, BASE_S, threshold=0):
    result = 0
    try:
        sql = "SELECT SESSION_TID,SESSION_INVITEDAY FROM SESSION WHERE SESSION_SPAM IS NOT '*'"
        data = await db_select(sql, (), BASE_S)
        for item in data:
            try:
                SESSION_TID, SESSION_INVITEDAY = item
                INVITEDAY_LIMIT_ = r_conf('INVITEDAY_LIMIT', CONF_P)
                checkSessionLimit_ = await check_session_limit(SESSION_TID, 'SESSION_INVITEDAY', INVITEDAY_LIMIT_,
                                                               BASE_S)
                if SESSION_INVITEDAY == '' or SESSION_INVITEDAY is None:
                    result += INVITEDAY_LIMIT_
                elif await check_session_flood(SESSION_TID, BASE_S) and checkSessionLimit_:
                    result += r_conf('INVITEDAY_LIMIT', CONF_P) - int(SESSION_INVITEDAY.split()[0])
            except Exception as e:
                await log(e)
                await asyncio.sleep(round(random.uniform(1, 2), 2))

        result = int(result * 0.6)
        if threshold:
            result = result if result < threshold else threshold
    except Exception as e:
        await log(e)
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return result


# endregion


# region apiGoogle
async def api_sync_all(value_many, spreadsheet_id, CONF_P, EXTRA_D, range_many='A2', sheet_id='Sheet1',
                       value_input_option='USER_ENTERED', major_dimension="ROWS"):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    http_auth = credentials.authorize(httplib2.Http())
    sheets_service = build('sheets', 'v4', http=http_auth, cache_discovery=False)

    convert_value = []
    for item in value_many:
        convert_value.append(list(item))

    await api_write_cells(sheets_service, convert_value, range_many, spreadsheet_id, sheet_id, value_input_option,
                          major_dimension)


async def api_sync_update(value_many, spreadsheet_id, range_many, CONF_P, EXTRA_D, sheet_id='Sheet1',
                          value_input_option='USER_ENTERED', major_dimension="ROWS"):
    try:
        if range_many is None:
            logger.info(log_ % 'range_many is None')
            return
        scopes = r_conf('scopes', CONF_P)
        credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
        httpAuth = credentials.authorize(httplib2.Http())
        sheets_service = build('sheets', 'v4', http=httpAuth, cache_discovery=False)

        convert_value = []
        for item in value_many:
            convert_value.append(list(item))

        await api_write_cells(sheets_service, convert_value, range_many, spreadsheet_id, sheet_id, value_input_option,
                              major_dimension)
    except Exception as e:
        await log(e)


async def api_find_row_by_tid(USER_TID, CONF_P, EXTRA_D, sheet_id='Sheet1'):
    result = None
    try:
        scopes_ = r_conf('scopes', CONF_P)
        credential_file_ = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
        credentials_ = ServiceAccountCredentials.from_json_keyfile_name(credential_file_, scopes_)
        http_auth = credentials_.authorize(httplib2.Http())
        sheets_service = build('sheets', 'v4', http=http_auth, cache_discovery=False)
        spreadsheet_id = (r_conf('db_file_id', CONF_P))[0]

        values_list = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_id,
                                                                 fields='values').execute().get('values', [])

        row = 0
        for ix, item in enumerate(values_list):
            if str(USER_TID) in item:
                row = ix + 1
                break
        result = 'A' + str(row)
    finally:
        return result


async def api_write_cells(sheets_service, value_many, range_many, spreadsheet_id, sheet_id, valueInputOption,
                          majorDimension="ROWS"):
    result = False
    try:
        result = sheets_service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
            "valueInputOption": valueInputOption,
            "data": [{
                "range": f"{sheet_id}!{range_many}",
                "majorDimension": majorDimension,
                "values": value_many,
            }]}).execute()
        logger.info(log_ % 'write to db ok')
    except Exception as e:
        await log(e)
    finally:
        return result


async def api_append_cells(sheets_service, value_many, spreadsheet_id, valueInputOption):
    result = True
    try:
        sheets_service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range='A1',
                                                      valueInputOption=valueInputOption,
                                                      body={"values": value_many}).execute()

        logger.info(log_ % 'write to db ok')
    except Exception as e:
        await log(e)
        result = False
    return result


async def api_read_cells(sheets_service, range_many, spreadsheet_id, sheet_id='Sheet1'):
    result = None
    try:
        r = sheets_service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheet_id, ranges=f"{sheet_id}!{range_many}"
        ).execute()

        result = r.get('valueRanges', [])[0]['values'] if len(r.get('valueRanges', [])) > 0 else None
        logger.info(log_ % 'read from db ok')
    except Exception as e:
        await log(e)
    finally:
        return result


def get_random_color():
    """
    Создаю случайный цвет с альфа каном
    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/other#Color
    :return:
    """
    return {
        "red": randrange(0, 255) / 255,
        "green": randrange(0, 255) / 255,
        "blue": randrange(0, 255) / 255,
        "alpha": randrange(0, 10) / 10  # 0.0 - прозрачный
    }


def api_create_file_or_folder(drive_service, mime_type, name, parent_id):
    creation_id = None
    try:
        body = {
            'name': name,
            'mimeType': mime_type,
            'parents': [parent_id],
            'properties': {'title': 'titleSpreadSheet', 'locale': 'ru_RU'},
            'locale': 'ru_RU'
        }
        result_folder = drive_service.files().create(body=body, fields='id').execute()
        creation_id = result_folder['id']
    finally:
        return creation_id


async def table_init(TABLE_API_JSON, CELL_NAMES, EXTRA_D, CONF_P, INI_D):
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.path.join(EXTRA_D, TABLE_API_JSON),
            r_conf('scopes', CONF_P))
        httpAuth = credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
        file_list_dic = await api_get_file_list(drive_service, (r_conf('share_folder_id', CONF_P))[0], {})

        files = []
        db_file_name = 'db'
        files = await is_need_for_create(file_list_dic, files, 'application/vnd.google-apps.spreadsheet', db_file_name,
                                         CONF_P, INI_D)
        for i in range(0, len(files)):
            creation_id = api_create_file_or_folder(drive_service, 'application/vnd.google-apps.spreadsheet',
                                                    db_file_name, (r_conf('share_folder_id', CONF_P))[0])
            w_conf(get_new_key_config(files[i], CONF_P, INI_D), [creation_id], CONF_P, INI_D)
            await api_sync_all([CELL_NAMES], (r_conf('db_file_id', CONF_P))[0], CONF_P, EXTRA_D, 'A1')
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))


async def send_my_copy(bot, cnt, USER_TID, USER_USERNAME, result):
    try:
        # USER_TID = 5150111687
        await bot.copy_message(chat_id=int(USER_TID), from_chat_id=result.chat.id, message_id=result.message_id,
                               reply_markup=result.reply_markup)
        cnt += 1
        logger.info(log_ % f"\t{cnt}. send to user {USER_TID}-{USER_USERNAME} ok")
        await asyncio.sleep(0.05)
    except TelegramRetryAfter as e:
        logger.info(log_ % f"TelegramRetryAfter {e.retry_after}")
        await asyncio.sleep(e.retry_after + 1)
    except Exception as e:
        await log(e)
        logger.info(log_ % f"\tsend to user {USER_TID}-{USER_USERNAME} error")
        await asyncio.sleep(round(random.uniform(1, 2), 2))
    finally:
        return cnt


async def api_get_file_list(drive_service, folder_id, tmp_dic=None, parent_name='', is_file=False):
    if tmp_dic is None:
        tmp_dic = {} or None
    if is_file:
        file = drive_service.files().get(fileId=folder_id, fields="id, name, size, modifiedTime, mimeType").execute()
        tmp_dic[file['id']] = [file['name'], file['mimeType'], parent_name, file['modifiedTime']]
        return tmp_dic
    q = "\'" + folder_id + "\'" + " in parents"
    fields = "nextPageToken, files(id, name, size, modifiedTime, mimeType)"
    results = drive_service.files().list(pageSize=1000, q=q, fields=fields).execute()
    items = results.get('files', [])
    for item in items:
        try:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                tmp_dic[item['id']] = [item['name'], item['mimeType'], parent_name, item['modifiedTime']]
                await api_get_file_list(drive_service, item['id'], tmp_dic, item['name'])
            else:
                tmp_dic[item['id']] = [item['name'], item['mimeType'], parent_name, item['modifiedTime']]
        except Exception as e:
            await log(e)

    tmp_dic_2 = {}
    for k, v in reversed(tmp_dic.items()):
        tmp_dic_2[k] = v

    return tmp_dic_2


async def upload_file(drive_service, name, post_media_name, folder_id):
    result = None
    try:
        if name == 'нет' or name is None: return

        request_ = drive_service.files().create(
            media_body=MediaFileUpload(filename=post_media_name, resumable=True),
            body={'name': name, 'parents': [folder_id]}
        )
        response = None
        while response is None:
            status, response = request_.next_chunk()
            if status: logger.info(log_ % "Uploaded %d%%." % int(status.progress() * 100))
        logger.info(log_ % "Upload Complete!")
        # if os.path.exists(post_media_name):
        #     os.remove(post_media_name)
        result = True
    except Exception as e:
        await log(e)
    finally:
        return result


async def api_dl_file(drive_service, id_, name, gdrive_mime_type, MEDIA_D):
    save_mime_type = None
    file_name = add = ''

    if gdrive_mime_type.endswith('document') and not (name.endswith('doc') or name.endswith('docx')):
        save_mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif gdrive_mime_type.endswith('sheet') and not (name.endswith('xls') or name.endswith('xlsx')):
        save_mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif gdrive_mime_type.endswith('presentation') and not (name.endswith('ppt') or name.endswith('pptx')):
        save_mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif gdrive_mime_type == 'application/vnd.google-apps.folder':
        return ''

    if save_mime_type:
        request_ = drive_service.files().export_media(fileId=id_, mimeType=save_mime_type)
    else:
        request_ = drive_service.files().get_media(fileId=id_)

    if request_:
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request_)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(log_ % "Download %d%%." % int(status.progress() * 100))

        if gdrive_mime_type.endswith('.spreadsheet'):
            add = '.xlsx'
        elif gdrive_mime_type.endswith('.document'):
            add = '.docx'
        elif gdrive_mime_type.endswith('.presentation'):
            add = '.pptx'
        file_name = return_cutted_filename(name, add, MEDIA_D)
        with io.open(file_name, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())
        await asyncio.sleep(1)
    return file_name


def return_cutted_filename(name, add, MEDIA_D):
    file_name = f'{MEDIA_D}/{name}{add}'
    l_ = len(file_name)
    diff = 255 - l_
    if diff <= 0:
        ext = get_ext(name)
        name = name[0:len(name) - 1 - abs(diff) - len(ext)] + ext
        file_name = f'{MEDIA_D}/{name}{add}'
    return file_name


def get_name_without_ext(file_name):
    name = file_name
    try:
        ext = get_ext(name)
        if ext != '':
            index_ext = str(name).rindex(ext)
            index_slash = str(name).rindex('/') + 1 if '/' in name else 0
            name = name[index_slash:index_ext]
    finally:
        return name


def get_ext(name):
    ext = ''
    try:
        index = str(name).rindex('.')
        ext = name[index:len(name)]
        if len(ext) > 5:
            ext = ''
    finally:
        return ext


async def is_need_for_create(file_list_dic, unit, mime_type, name, CONF_P, INI_D):
    flag = False
    for k, v in file_list_dic.items():
        if v[0] == name and v[1] == mime_type:
            flag = True
            w_conf(get_new_key_config(name, CONF_P, INI_D), [k], CONF_P, INI_D)
            break
    if not flag: unit.append(name)
    return unit


def is_exists_google_id(file_list_dic, mime_type, name, parent_name):
    result = None
    for k, v in file_list_dic.items():
        if v[0] == name and v[1] == mime_type and v[2] == parent_name:
            return k
    return result


def get_new_key_config(value, CONF_P, INI_D):
    new_key = ""
    try:
        CONF_P.read(INI_D)
        for k, v in CONF_P.items('CONFIG'):
            if value == ast.literal_eval(v)[0]:
                arr = str(k).split('_')
                new_key = f'{arr[0]}_{arr[1]}_id'
                break
    finally:
        return new_key


async def api_init(CONF_P, INI_D, EXTRA_D, fields_0):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    httpAuth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
    file_list_dic = await api_get_file_list(drive_service, (r_conf('share_folder_id', CONF_P))[0], {})

    subflders = []
    mimeType_folder = 'application/vnd.google-apps.folder'
    static_folder_name = (r_conf('static_folder_name', CONF_P))[0]
    dynamic_folder_name = (r_conf('dynamic_folder_name', CONF_P))[0]
    subflders = await is_need_for_create(file_list_dic, subflders, mimeType_folder, static_folder_name, CONF_P, INI_D)
    subflders = await is_need_for_create(file_list_dic, subflders, mimeType_folder, dynamic_folder_name, CONF_P, INI_D)
    for i in range(0, len(subflders)):
        share_folder_id = (r_conf('share_folder_id', CONF_P))[0]
        creation_id = api_create_file_or_folder(drive_service, mimeType_folder, subflders[i], share_folder_id)
        w_conf(get_new_key_config(subflders[i], CONF_P, INI_D), [creation_id], CONF_P, INI_D)

    files = []
    mimeType_sheet = 'application/vnd.google-apps.spreadsheet'
    db_file_name = (r_conf('db_file_name', CONF_P))[0]
    files = await is_need_for_create(file_list_dic, files, mimeType_sheet, db_file_name, CONF_P, INI_D)
    for i in range(0, len(files)):
        db_file_name = (r_conf('db_file_name', CONF_P))[0]
        mimeType_sheet = 'application/vnd.google-apps.spreadsheet'
        share_folder_id = (r_conf('share_folder_id', CONF_P))[0]
        creation_id = api_create_file_or_folder(drive_service, mimeType_sheet, db_file_name, share_folder_id)
        w_conf(get_new_key_config(files[i], CONF_P, INI_D), [creation_id], CONF_P, INI_D)
        value_many = [fields_0]
        spreadsheetId = (r_conf('db_file_id', CONF_P))[0]
        await api_sync_all(value_many, spreadsheetId, CONF_P, EXTRA_D, 'A1')
    logger.info(log_ % 'api init ok')


async def get_cell_dialog(range_many, CONF_P, EXTRA_D):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    http_auth = credentials.authorize(httplib2.Http())
    sheets_service = build('sheets', 'v4', http=http_auth, cache_discovery=False)
    spreadsheet_id = '1sQWH3NpJAh8t4QDmP-8vvc7XaCTx4Uflc6LADA9zvN8'
    sheet_id = 'Лист1'

    result = None
    try:
        ranges = f"{sheet_id}!{range_many}"
        r = sheets_service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=ranges).execute()
        if ':' in range_many:
            result = r.get('valueRanges', [])[0]['values'] if len(r.get('valueRanges', [])) > 0 else None
            result = [item[0] for item in result]
        else:
            result = r.get('valueRanges', [])[0]['values'][0][0] if len(r.get('valueRanges', [])) > 0 else None
        logger.info(log_ % 'read from db ok')
    except Exception as e:
        await log(e)
    finally:
        return result


async def get_list_of_send_folder(CONF_P, EXTRA_D):
    scopes = r_conf('scopes', CONF_P)
    credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
    httpAuth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)

    tmp = []
    file_list_dic = await api_get_file_list(drive_service, (r_conf('dynamic_folder_id', CONF_P))[0], {})
    for k, v in file_list_dic.items():
        try:
            parent_folder = v[2]
            name_folder = v[0]
            datetime_ = datetime.datetime.now()
            if parent_folder == '' and datetime_ < datetime.datetime.strptime(name_folder, "%d-%m-%Y %H:%M"):
                tmp.append([name_folder, k])
        except Exception as e:
            await log(e)

    return tmp


async def save_post_to_google_drive(CONF_P, EXTRA_D, post_txt, post_btn, post_url, post_media_name,
                                    post_media_type, post_pin, post_time, post_media_options, post_users='*'):
    try:
        scopes = r_conf('scopes', CONF_P)
        credential_file = os.path.join(EXTRA_D, (r_conf('credential_file', CONF_P))[0])
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scopes)
        httpAuth = credentials.authorize(httplib2.Http())
        drive_service = build('drive', 'v3', http=httpAuth, cache_discovery=False)
        file_list_dic = await api_get_file_list(drive_service, (r_conf('dynamic_folder_id', CONF_P))[0], {})

        mime_type_folder = 'application/vnd.google-apps.folder'
        id_time_folder = is_exists_google_id(file_list_dic, mime_type_folder, post_time.strftime("%d-%m-%Y %H:%M"), '')
        if id_time_folder is None:
            id_time_folder = api_create_file_or_folder(drive_service, 'application/vnd.google-apps.folder',
                                                       post_time.strftime("%d-%m-%Y %H:%M"),
                                                       (r_conf('dynamic_folder_id', CONF_P))[0])

        mime_type_sheet = 'application/vnd.google-apps.spreadsheet'
        id_InfoXlsx = is_exists_google_id(file_list_dic, mime_type_sheet, 'info', post_time.strftime("%d-%m-%Y %H:%M"))
        if id_InfoXlsx is None:
            mime_type_sheet = 'application/vnd.google-apps.spreadsheet'
            id_InfoXlsx = api_create_file_or_folder(drive_service, mime_type_sheet, 'info', id_time_folder)
            v_m = [["текст", "кнопка(имя)", "кнопка(ссылка)", "медиа", "медиа тип", "закрепить(pin)", "пользователи"]]
            spreadsheet_id = id_InfoXlsx
            await api_sync_all(
                value_many=v_m,
                spreadsheet_id=spreadsheet_id,
                CONF_P=CONF_P,
                EXTRA_D=EXTRA_D,
                range_many='A1',
                major_dimension="COLUMNS"
            )

        name = os.path.basename(post_media_name) if post_media_name else 'нет'
        if post_media_type == 'poll':
            post_txt = post_media_name
            name = str(post_media_options)
        else:
            await upload_file(drive_service, name, post_media_name, id_time_folder)

        v_m = [[post_txt, post_btn if post_btn else 'no', post_url if post_url else 'no', name,
                post_media_type if post_media_type else 'no',
                'yes' if post_pin else 'no', post_users]]
        spreadsheet_id = id_InfoXlsx
        await api_sync_all(
            value_many=v_m,
            spreadsheet_id=spreadsheet_id,
            CONF_P=CONF_P,
            EXTRA_D=EXTRA_D,
            range_many='B1',
            major_dimension="COLUMNS"
        )
        logger.info(log_ % 'save to google ok')
    except Exception as e:
        await log(e)


# endregion


# region aiogram
async def convert_domain_to_currency(domain):
    result = 'EUR'
    try:
        if domain == 'ae':
            result = 'AED'
        elif domain == 'af':
            result = 'AFN'
        elif domain == 'al':
            result = 'AFN'
        elif domain == 'am':
            result = 'AMD'
        elif domain == 'ar':
            result = 'ARS'
        elif domain == 'au':
            result = 'AUD'
        elif domain == 'az':
            result = 'AZN'
        elif domain == 'ba':
            result = 'BAM'
        elif domain == 'bd':
            result = 'BDT'
        elif domain == 'bg':
            result = 'BGN'
        elif domain == 'bn':
            result = 'BND'
        elif domain == 'bo':
            result = 'BOB'
        elif domain == 'br':
            result = 'BRL'
        elif domain == 'by':
            result = 'BYN'
        elif domain == 'ca':
            result = 'CAD'
        elif domain == 'ch':
            result = 'CHF'
        elif domain == 'cl':
            result = 'CLP'
        elif domain == 'cn':
            result = 'CNY'
        elif domain == 'co':
            result = 'COP'
        elif domain == 'cr':
            result = 'CRC'
        elif domain == 'cz':
            result = 'CZK'
        elif domain == 'dk':
            result = 'DKK'
        elif domain == 'do':
            result = 'DOP'
        elif domain == 'dz':
            result = 'DZD'
        elif domain == 'eg':
            result = 'EGP'
        elif domain == 'et':
            result = 'ETB'
        elif domain == 'uk':
            result = 'GBP'
        elif domain == 'ge':
            result = 'GEL'
        elif domain == 'gt':
            result = 'GTQ'
        elif domain == 'hk':
            result = 'HKD'
        elif domain == 'hh':
            result = 'HNL'
        elif domain == 'hr':
            result = 'HRK'
        elif domain == 'hu':
            result = 'HUF'
        elif domain == 'id':
            result = 'IDR'
        elif domain == 'il':
            result = 'ILS'
        elif domain == 'in':
            result = 'INR'
        elif domain == 'is':
            result = 'ISK'
        elif domain == 'jm':
            result = 'JMD'
        elif domain == 'ke':
            result = 'KES'
        elif domain == 'kg':
            result = 'KGS'
        elif domain == 'kr':
            result = 'KRW'
        elif domain == 'kz':
            result = 'KZT'
        elif domain == 'lb':
            result = 'LBP'
        elif domain == 'lk':
            result = 'LKR'
        elif domain == 'ma':
            result = 'MAD'
        elif domain == 'md':
            result = 'MDL'
        elif domain == 'mn':
            result = 'MNT'
        elif domain == 'mu':
            result = 'MUR'
        elif domain == 'mv':
            result = 'MVR'
        elif domain == 'mx':
            result = 'MXN'
        elif domain == 'my':
            result = 'MYR'
        elif domain == 'mz':
            result = 'MZN'
        elif domain == 'ng':
            result = 'NGN'
        elif domain == 'ni':
            result = 'NIO'
        elif domain == 'no':
            result = 'NOK'
        elif domain == 'np':
            result = 'NPR'
        elif domain == 'nz':
            result = 'NZD'
        elif domain == 'pa':
            result = 'PAB'
        elif domain == 'pe':
            result = 'PEN'
        elif domain == 'ph':
            result = 'PHP'
        elif domain == 'pk':
            result = 'PKR'
        elif domain == 'pl':
            result = 'PLN'
        elif domain == 'py':
            result = 'PYG'
        elif domain == 'qa':
            result = 'QAR'
        elif domain == 'ro':
            result = 'RON'
        elif domain == 'rs':
            result = 'RSD'
        elif domain == 'ru':
            result = 'RUB'
        elif domain == 'sa':
            result = 'SAR'
        elif domain == 'se':
            result = 'SEK'
        elif domain == 'sg':
            result = 'SGD'
        elif domain == 'th':
            result = 'THB'
        elif domain == 'tj':
            result = 'TJS'
        elif domain == 'tr':
            result = 'TRY'
        elif domain == 'tt':
            result = 'TTD'
        elif domain == 'tw':
            result = 'TWD'
        elif domain == 'tz':
            result = 'TZS'
        elif domain == 'ua':
            result = 'UAH'
        elif domain == 'ug':
            result = 'UGX'
        elif domain == 'us':
            result = 'USD'
        elif domain == 'uy':
            result = 'UYU'
        elif domain == 'uz':
            result = 'UZS'
        elif domain == 'vn':
            result = 'VND'
        elif domain == 'ye':
            result = 'YER'
        elif domain == 'za':
            result = 'ZAR'
    except Exception as e:
        logger.info(log_ % str(e))
        await asyncio.sleep(round(random.uniform(0, 1), 2))
    finally:
        return result


# endregion


# region notes
# sys.path.append('../hub')
# print("In module products sys.path[0], __package__ ==", sys.path[-1], __package__)
# from .. .hub import xtra
# dp.register_chosen_inline_handler(chosen_inline_handler_fun, lambda chosen_inline_result: True)
# dp.register_inline_handler(inline_handler_main, lambda inline_handler_main_: True)
# channel_post_handler
# edited_channel_post_handler
# poll_handler - а это получается реакция на размещение опроса
# poll_answer_handler - реакция на голосование
# chat_join_request_handler
# errors_handler
# current_state

# apt install redis -y
# nano /etc/redis/redis.conf
# systemctl restart redis.service
# systemctl status redis
# redis-cli
# netstat -lnp | grep redis

# https://www.namecheap.com
# A Record * 212.73.150.86
# A Record @ 212.73.150.86

# apt update && apt upgrade -y
# curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
# apt install -y nodejs build-essential nginx yarn
# npm install -g npm pm2@latest -g
# ufw allow 'Nginx Full'
# curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null
# echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list
# node -v
# nginx -v
# yarn -v

# rm /etc/nginx/sites-enabled/default
# nano /etc/nginx/sites-enabled/tg6002
# nano /etc/nginx/sites-available/fmessenger86.com
# upstream tg1{
#     server localhost:6000;
# }
# server{
#     listen 80;
#     server_name tg1.fmessenger86.com www.tg1.fmessenger86.com;
#     charset utf-8;
#     client_max_body_size 50M;
#
#     location / {
#         proxy_redirect off;
#         proxy_set_header   X-Real-IP $remote_addr;
#         proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_set_header   X-Forwarded-Proto $scheme;
#         proxy_set_header   Host $http_host;
#         proxy_set_header   X-NginX-Proxy    true;
#         proxy_set_header   Connection "";
#         proxy_http_version 1.1;
#         proxy_pass         http://tg1;
#         proxy_set_header     Access-Control-Allow-Origin "*";
#         proxy_set_header     Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";
#     }
# }
# server {
#     server_name www.tg1.fmessenger86.com;
#     return 301 $scheme://tg1.fmessenger86.com$request_uri;
# }

# systemctl restart nginx
# systemctl reload nginx
# snap install core;  snap refresh core
# apt remove python3-certbot-nginx certbot -y
# rm -rf /etc/letsencrypt/renewal/
# rm -rf /etc/letsencrypt/archive/
# rm -rf /etc/letsencrypt/live/
# rm -rf /opt/letsencrypt
# rm -rf /etc/letsencrypt
# snap install --classic certbot
# ln -s /snap/bin/certbot /usr/bin/certbot
# certbot --nginx   # certbot --nginx -d tg1.fmessenger86.com -d www.tg1.fmessenger86.com
# certbot renew --dry-run
# systemctl reload nginx && nginx -t
#
# https://www.tg6002.fmessenger86.com
# too many certificates (5) already issued for this exact set of domains in the last 168 hours

# это вроде уже не нужно
# apt install python3-certbot-nginx -y
# certbot --nginx -d tg6001.YOURDOMAIN.com -d www.tg6001.YOURDOMAIN.com
# carwellhobbot4@mail.ee, Agree, No, Redirect, True
# certbot certificates
# endregion


def main():
    pass


if __name__ == "__main__":
    main()
