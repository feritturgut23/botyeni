"""
Video + Music Stream Telegram Bot
Copyright (c) 2022-present levina=lab <https://github.com/levina-lab>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but without any warranty; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/licenses.html>
"""


import traceback

from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, Message

from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.exceptions import NoAudioSourceFound, NoActiveGroupCall, GroupCallNotFound

from driver.decorators import require_admin, check_blacklist
from program.utils.inline import stream_markup
from driver.design.thumbnail import thumb
from driver.design.chatname import CHAT_TITLE
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.core import calls, user, me_user
from driver.utils import bash, remove_if_exists, from_tg_get_msg
from driver.database.dbqueue import add_active_chat, remove_active_chat, music_on
from config import BOT_USERNAME, IMG_5

from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = data["thumbnails"][0]["url"]
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0

async def ytdl(link: str):
    stdout, stderr = await bash(
        f'yt-dlp --geo-bypass -g -f "best[height<=?720][width<=?1280]/best" {link}'
    )
    if stdout:
        return 1, stdout
    return 0, stderr


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


async def play_tg_file(c: Client, m: Message, replied: Message = None, link: str = None):
    chat_id = m.chat.id
    user_id = m.from_user.id
    if link:
        try:
            replied = await from_tg_get_msg(link)
        except Exception as e:
            traceback.print_exc()
            return await m.reply_text(f"🚫 Hata:\n\n» {e}")
    if not replied:
        return await m.reply(
            "» reply to an **audio file** or **aramak için bir şey ver.**"
        )
    if replied.audio or replied.voice:
        if not link:
            suhu = await replied.reply("📥 ses indiriliyor...")
        else:
            suhu = await m.reply(" ses indiriliyor...")
        dl = await replied.download()
        link = replied.link
        songname = "music"
        thumbnail = f"{IMG_5}"
        duration = "00:00"
        try:
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:80]
                else:
                    songname = replied.audio.file_name[:80]
                if replied.audio.thumbs:
                    if not link:
                        thumbnail = await c.download_media(replied.audio.thumbs[0].file_id)
                    else:
                        thumbnail = await user.download_media(replied.audio.thumbs[0].file_id)
                duration = convert_seconds(replied.audio.duration)
            elif replied.voice:
                songname = "voice note"
                duration = convert_seconds(replied.voice.duration)
        except BaseException:
            pass

        if not thumbnail:
            thumbnail = f"{IMG_5}"

        if chat_id in QUEUE:
            await suhu.edit("🔄 Sıra İzleniyor...")
            gcname = m.chat.title
            ctitle = await CHAT_TITLE(gcname)
            title = songname
            userid = m.from_user.id
            image = await thumb(thumbnail, title, userid, ctitle)
            pos = add_to_queue(chat_id, songname, dl, link, "music", 0)
            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
            buttons = stream_markup(user_id)
            await suhu.delete()
            await m.reply_photo(
                photo=image,
                reply_markup=InlineKeyboardMarkup(buttons),
                caption=f"💡 **Parça sıraya eklendi »** `{pos}`\n\n"
                        f"🗂 **İsim:** [{songname}]({link}) | `music`\n"
                        f"⏱️ **Süre:** `{duration}`\n"
                        f"🧸 **Talep eden:** {requester}",
            )
            remove_if_exists(image)
        else:
            try:
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                title = songname
                userid = m.from_user.id
                image = await thumb(thumbnail, title, userid, ctitle)
                await suhu.edit("🔄 Sesli Sohbete Katılıyorum.")
                await music_on(chat_id)
                await add_active_chat(chat_id)
                await calls.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                        HighQualityAudio(),
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "music", 0)
                await suhu.delete()
                buttons = stream_markup(user_id)
                requester = (
                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                )
                await m.reply_photo(
                    photo=image,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"🗂 **İsim:** [{songname}]({link}) | `music`\n"
                            f"⏱️ **Süre:** `{duration}`\n"
                            f"🧸 **Talep eden:** {requester}",
                )
                remove_if_exists(image)
            except (NoActiveGroupCall, GroupCallNotFound):
                await suhu.delete()
                await remove_active_chat(chat_id)
                traceback.print_exc()
                await m.reply_text("❌ Bot, Grup aramasını bulamıyor veya etkin değil.\n\n» Use Grup çağrısını açınız !")
            except BaseException as err:
                print(err)
    else:
        await m.reply(
            "» reply to an **ses dosyası** veya **arayacak bir şey verin.**"
        )


@Client.on_message(command(["play", f"play@{BOT_USERNAME}"]) & other_filters)
@check_blacklist()
@require_admin(permissions=["can_manage_voice_chats", "can_delete_messages", "can_invite_users"], self=True)
async def play(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    user_id = m.from_user.id
    if m.sender_chat:
        return await m.reply_text(
            "you're an __Anonymous__ user !\n\n» revert back to your real user account to use this bot."
        )
    try:
        ubot = me_user.id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "banned":
            try:
                await m.reply_text("❌ Kullanıcı robotu bu sohbette yasaklanmıştır, müzik çalabilmek için önce kullanıcı robotunun yasağını kaldırın. !")
                await remove_active_chat(chat_id)
            except BaseException:
                pass
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
    except UserNotParticipant:
        try:
            invitelink = (await c.get_chat(chat_id)).invite_link
            if not invitelink:
                await c.export_chat_invite_link(chat_id)
                invitelink = (await c.get_chat(chat_id)).invite_link
            if invitelink.startswith("https://t.me/+"):
                invitelink = invitelink.replace(
                    "https://t.me/+", "https://t.me/joinchat/"
                )
            await user.join_chat(invitelink)
            await remove_active_chat(chat_id)
        except UserAlreadyParticipant:
            pass
        except Exception as e:
            traceback.print_exc()
            return await m.reply_text(
                f"❌ **Asistan Katılmadı**\n\n**reason**: `{e}`"
            )
    if replied:
        if replied.audio or replied.voice:
            await play_tg_file(c, m, replied)
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» reply to an **audio file** or **aramak için bir şey ver.**"
                )
            else:
                suhu = await c.send_message(chat_id, "🔍 **Yükleniyor...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                if search == 0:
                    await suhu.edit("❌ **Sonuç bulunamadı**")
                else:
                    songname = search[0]
                    title = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    userid = m.from_user.id
                    gcname = m.chat.title
                    ctitle = await CHAT_TITLE(gcname)
                    image = await thumb(thumbnail, title, userid, ctitle)
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await suhu.edit(f"❌  yt-dl sorunları algılandı\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            await suhu.edit("🔄 Sıra İzleniyor...")
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "music", 0
                            )
                            await suhu.delete()
                            buttons = stream_markup(user_id)
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=image,
                                reply_markup=InlineKeyboardMarkup(buttons),
                                caption=f"💡 **Track added to queue »** `{pos}`\n\n🗂 **İsim:** [{songname}]({url}) | `music`\n**⏱ Süre:** `{duration}`\n🧸 **Talep eden:** {requester}",
                            )
                            remove_if_exists(image)
                        else:
                            try:
                                await suhu.edit("🔄 Sesli sohbete katılıyorum")
                                await music_on(chat_id)
                                await add_active_chat(chat_id)
                                await calls.join_group_call(
                                    chat_id,
                                    AudioPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                                await suhu.delete()
                                buttons = stream_markup(user_id)
                                requester = (
                                    f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                )
                                await m.reply_photo(
                                    photo=image,
                                    reply_markup=InlineKeyboardMarkup(buttons),
                                    caption=f"🗂 **İsim:** [{songname}]({url}) | `music`\n**⏱ Süre:** `{duration}`\n🧸 **Talep Eden:** {requester}",
                                )
                                remove_if_exists(image)
                            except (NoActiveGroupCall, GroupCallNotFound):
                                await suhu.delete()
                                await remove_active_chat(chat_id)
                                await m.reply_text("❌  Bot, Grup aramasını bulamıyor veya etkin değil.\n\n» Grup aramasını açmak için /startvc komutunu kullanın !")
                            except NoAudioSourceFound:
                                await suhu.delete()
                                await remove_active_chat(chat_id)
                                await m.reply_text("❌ Oynatmak için sağladığınız içeriğin ses kaynağı yok")
                            except BaseException as err:
                                print(err)

    else:
        if len(m.command) < 2:
            await m.reply(
                "» reply to an **audio file** or **aramak için bir şey ver.**"
            )
        elif "t.me" in m.command[1]:
            for i in m.command[1:]:
                if "t.me" in i:
                    await play_tg_file(c, m, link=i)
                continue
        else:
            suhu = await c.send_message(chat_id, "🔍 **Yükleniyor...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await suhu.edit("❌ **Sonuç bulunamadı**")
            else:
                songname = search[0]
                title = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                userid = m.from_user.id
                gcname = m.chat.title
                ctitle = await CHAT_TITLE(gcname)
                image = await thumb(thumbnail, title, userid, ctitle)
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await suhu.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        await suhu.edit("🔄 Queueing Track...")
                        pos = add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                        await suhu.delete()
                        requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        buttons = stream_markup(user_id)
                        await m.reply_photo(
                            photo=image,
                            reply_markup=InlineKeyboardMarkup(buttons),
                            caption=f"💡 **Track added to queue »** `{pos}`\n\n🗂 **İsim:** [{songname}]({url}) | `music`\n**⏱ Süre:** `{duration}`\n🧸 **Talep Eden:** {requester}",
                        )
                        remove_if_exists(image)
                    else:
                        try:
                            await suhu.edit("🔄 Sesli Sohbete Katılıyorum")
                            await music_on(chat_id)
                            await add_active_chat(chat_id)
                            await calls.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "music", 0)
                            await suhu.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            buttons = stream_markup(user_id)
                            await m.reply_photo(
                                photo=image,
                                reply_markup=InlineKeyboardMarkup(buttons),
                                caption=f"🗂 **İsim:** [{songname}]({url}) | `music`\n**⏱ Süre:** `{duration}`\n🧸 **Talep Eden:** {requester}",
                            )
                            remove_if_exists(image)
                        except (NoActiveGroupCall, GroupCallNotFound):
                            await suhu.delete()
                            await remove_active_chat(chat_id)
                            await m.reply_text("❌ Bot, Grup aramasını bulamıyor veya etkin değil.\n\n» Use Grup aramasını açmak için /startvc komutu!")
                        except NoAudioSourceFound:
                            await suhu.delete()
                            await remove_active_chat(chat_id)
                            await m.reply_text("❌ Oynatmak için sağladığınız içeriğin ses kaynağı yok.\n\n» başka bir şarkı çalmayı deneyin veya daha sonra tekrar deneyin !")
                        except BaseException as err:
                            print(err)
