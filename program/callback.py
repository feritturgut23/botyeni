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


from driver.core import me_bot, me_user
from driver.queues import QUEUE
from driver.decorators import check_blacklist
from program.utils.inline import menu_markup, stream_markup

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    BOT_USERNAME,
    GROUP_SUPPORT,
    OWNER_USERNAME,
    UPDATES_CHANNEL,
    SUDO_USERS,
    OWNER_ID,
)


@Client.on_callback_query(filters.regex("home_start"))
@check_blacklist()
async def start_set(_, query: CallbackQuery):
    await query.answer("home start")
    await query.edit_message_text(
        f"""✨ **Hoşgeldin [{query.message.chat.first_name}](tg://user?id={query.message.chat.id}) !**\n
💭 [{me_bot.first_name}](https://t.me/{BOT_USERNAME}) **Telegram Grup görüntülü sohbeti aracılığıyla gruplar halinde müzik ve video oynatmak için bir bot!**

💡 **Bot'un tüm komutlarını ve nasıl çalıştıklarını aşağıdaki butona tıklayarak öğrenin. » 📚 Komutlar!**

🔖 **Bu botun nasıl kullanılacağını öğrenmek için lütfen tıklayın » ❓ Basit Komutlar**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Gruba ekle ➕",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                    )
                ],
                [InlineKeyboardButton("❓ Basit Komutlar", callback_data="user_guide")],
                [
                    InlineKeyboardButton("📚 komutlar", callback_data="command_list"),
                    InlineKeyboardButton("❤ Donate", url=f"https://t.me/{OWNER_USERNAME}"),
                ],
                [
                    InlineKeyboardButton(
                        "👥 Resmi Group", url=f"https://t.me/{GROUP_SUPPORT}"
                    ),
                    InlineKeyboardButton(
                        "📣 Resmi kanal", url=f"https://t.me/{UPDATES_CHANNEL}"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🌐 Kelime botu", url="https://t.me/deezerkelimebot"
                    )
                ],
            ]
        ),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("quick_use"))
@check_blacklist()
async def quick_set(_, query: CallbackQuery):
    await query.answer("quick bot usage")
    await query.edit_message_text(
        f"""ℹ️ Hızlı kullanım Kılavuzu bot, lütfen tamamını okuyun !

👩🏻‍💼 » /oynat- Müzik çalmak için şarkı başlığını veya youtube bağlantısını veya ses dosyasını vererek bunu yazın. (Bu komutu kullanarak YouTube canlı yayınını oynatmamayı unutmayın!, çünkü bu öngörülemeyen sorunlara neden olacaktır.)

👩🏻‍💼 » /izlet - Videoyu oynatmak için şarkı başlığını veya youtube bağlantısını veya video dosyasını vererek bunu yazın. (Bu komutu kullanarak YouTube canlı videosunu oynatmamayı unutmayın!, çünkü bu öngörülemeyen sorunlara neden olacaktır.)
👩🏻‍💼 » /cizle - Canlı Videoyu oynatmak için YouTube canlı akış video bağlantısını veya m3u8 bağlantısını vererek bunu yazın. (Bu komutu kullanarak yerel ses/video dosyalarını veya canlı olmayan YouTube videolarını oynatmamayı unutmayın!, çünkü bu öngörülemeyen sorunlara neden olacaktır.)
❓ Have questions? Contact us in [Support Group](https://t.me/{GROUP_SUPPORT}).""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri dön", callback_data="user_guide")]]
        ),
        disable_web_page_preview=True,
    )


@Client.on_callback_query(filters.regex("user_guide"))
@check_blacklist()
async def guide_set(_, query: CallbackQuery):
    await query.answer("user guide")
    await query.edit_message_text(
        f"""❓ Bu Bot nasıl kullanılır ?, read the Guide below !

1.) İlk önce, bu botu Grubunuza ekleyin.
2.) Ardından, bu botu Grupta yönetici olarak yükseltin, Anonim yönetici dışındaki tüm izinleri de verin.(yada sadece Bağlantı ile davet,Görüntülü sohbet ve mesaj silme yetkisi verebilirsiniz)
3.) Bu botu tanıttıktan sonra, yönetici verilerini güncellemek için Grup'a /reload yazın.
3.) Grubunuza @{me_user.username} grubunuza veya onu davet etmek için /gel yazın ve sonra `/oynat (şarkı adı)` veya `/izlet (şarkı adı)` yazdığınızda userbot kendi kendine katılacak.
4.) Video/müzik oynatmaya başlamadan önce görüntülü sohbeti açın/başlatın.

`- SON, HER ŞEY AYARLANDI -`

📌 Kullanıcı robotu görüntülü sohbete katılmadıysa, görüntülü sohbetin zaten açık olduğundan ve kullanıcı robotunun sohbette olduğundan emin olun..

💡 Bu bot hakkında takip eden sorularınız varsa, bunu buradaki destek sohbetimde iletebilirsiniz.: @{GROUP_SUPPORT}.""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("» Quick use Guide «", callback_data="quick_use")
                ],[
                    InlineKeyboardButton("🔙 Go Back", callback_data="home_start")
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("command_list"))
@check_blacklist()
async def commands_set(_, query: CallbackQuery):
    user_id = query.from_user.id
    await query.answer("commands menu")
    await query.edit_message_text(
        f"""✨ **Merhaba [{query.message.chat.first_name}](tg://user?id={query.message.chat.id}) !**

» Modül bilgilerini okumak ve mevcut Komutların listesini görmek için aşağıdaki menüye göz atın !

All commands can be used with (`! / .`) handler""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("👮🏻‍♀️ Admin komut", callback_data="admin_command"),
                ],[
                    InlineKeyboardButton("👩🏻‍💼 Kullanıcı komut", callback_data="user_command"),
                ],[
                    InlineKeyboardButton("Yetkili komut", callback_data="sudo_command"),
                    InlineKeyboardButton("Sahip komut", callback_data="owner_command"),
                ],[
                    InlineKeyboardButton("🔙 Geri dön", callback_data="home_start")
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("user_command"))
@check_blacklist()
async def user_set(_, query: CallbackQuery):
    BOT_NAME = me_bot.first_name
    await query.answer("basic commands")
    await query.edit_message_text(
        f"""✏️ Tüm kullanıcılar için komut listesi.

» /oynat (şarkı adı/bağlantısı) - görüntülü sohbette müzik çal
» /izlet (video name/link) - görüntülü sohbette video oynat
» /cizle (m3u8/yt live link) - play live stream video
» /playlist - çalmakta olan şarkıyı görün
» /indir (sorgu) - Youtube'dan şarkı indirme
» /ara (sorgu) - youtube'dan video indirme
» /ping - bot ping durumunu göster
» /uptime - bot çalışma süresi durumunu göster
» /alive - botun canlı bilgilerini göster (yalnızca Grupta)

⚡️ __Powered by {BOT_NAME} AI__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri dön", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("admin_command"))
@check_blacklist()
async def admin_set(_, query: CallbackQuery):
    BOT_NAME = me_bot.first_name
    await query.answer("admin commands")
    await query.edit_message_text(
        f"""✏️ Grup yöneticisi için komut listesi.

» /dur - çalınmakta olan parçayı duraklat
» /devam - önceden duraklatılmış parçayı çal
» /atla - sonraki parçaya gider
» /son - parçanın çalınmasını durdurur ve kuyruğu temizler
» /vmute - grup aramasında yayıncı kullanıcı robotunun sesini kapat
» /vunmute - grup aramasında yayıncı kullanıcı robotunun sesini aç
» /volume `1-200` - müziğin sesini ayarlayın (Asistan yönetici olmalıdır)
» /reload - botu yeniden yükleyin ve yönetici verilerini yenileyin
» /gel - Asistan gruba katılır.
» /git - Asistan gruptan ayrılır
» /startvc - grup aramasını başlat/yeniden başlat
» /stopvc - grup aramasını bitir

⚡️ __Powered by {BOT_NAME} AI__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri Dön", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("sudo_command"))
@check_blacklist()
async def sudo_set(_, query: CallbackQuery):
    user_id = query.from_user.id
    BOT_NAME = me_bot.first_name
    if user_id not in SUDO_USERS:
        await query.answer("⚠️ Bu düğmeyi tıklama izniniz yok\n\n» This button is reserved for sudo members of this bot.", show_alert=True)
        return
    await query.answer("sudo commands")
    await query.edit_message_text(
        f"""✏️ Sahip komutları.

» /stats - bot mevcut istatistiğini al
» /calls - veritabanındaki tüm aktif grup aramalarının listesini göster
» /block(`chat_id`) - herhangi bir grubun botunuzu kullanmasını kara listeye almak için bunu kullanın
» /unblock (`chat_id`) - botunuzu kullanan herhangi bir grubu beyaz listeye eklemek için bunu kullanın
» /blocklist - size kara listeye alınan tüm sohbetlerin listesini göster
» /speedtest - bot sunucusu hız testini çalıştırın
» /sysinfo - sistem bilgilerini göster
» /logs - mevcut bot günlüklerini oluştur
» /eval - herhangi bir kodu yürütün ('geliştirici öğeleri')
» /sh - herhangi bir komutu çalıştırın ('geliştirici öğeleri')

⚡ __Powered by {BOT_NAME} AI__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri Dön", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("owner_command"))
@check_blacklist()
async def owner_set(_, query: CallbackQuery):
    user_id = query.from_user.id
    BOT_NAME = me_bot.first_name
    if user_id not in OWNER_ID:
        await query.answer("⚠️ Bu düğmeyi tıklama izniniz yok\n\n» This button is reserved for owner of this bot.", show_alert=True)
        return
    await query.answer("owner commands")
    await query.edit_message_text(
        f"""✏️ Bot sahibi için komut listesi.

» /gban (`username` veya `user_id`) - küresel olarak yasaklanmış kişiler için, yalnızca grup içinde kullanılabilir
» /ungban (`username` veya `user_id`) - küresel olmayan yasaklı kişiler için, yalnızca grup içinde kullanılabilir
» /update -botunuzu en son sürüme güncelleyin
» /restart - botunuzu doğrudan yeniden başlatın
» /leaveall - Asistan'ın tüm gruptan ayrılmasını emret
» /leavebot (`chat id`) - botun belirttiğiniz gruptan ayrılmasını emreder
» /broadcast (`message`) - bot veritabanındaki tüm gruplara bir yayın mesajı gönder
» /broadcast_pin (`message`) - sohbet pini ile bot veritabanındaki tüm gruplara bir yayın mesajı gönderin

⚡ __Powered by {BOT_NAME} AI__""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Geri dön", callback_data="command_list")]]
        ),
    )


@Client.on_callback_query(filters.regex("stream_menu_panel"))
@check_blacklist()
async def at_set_markup_menu(_, query: CallbackQuery):
    user_id = query.from_user.id
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Yalnızca bu düğmeye dokunabilen görüntülü sohbet yönetme iznine sahip yönetici !", show_alert=True)
    chat_id = query.message.chat.id
    user_id = query.message.from_user.id
    buttons = menu_markup(user_id)
    if chat_id in QUEUE:
        await query.answer("control panel opened")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await query.answer("❌ şu anda hiçbir şey yayınlanmıyor", show_alert=True)


@Client.on_callback_query(filters.regex("stream_home_panel"))
@check_blacklist()
async def is_set_home_menu(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Yalnızca bu düğmeye dokunabilen görüntülü sohbet yönetme iznine sahip yönetici !", show_alert=True)
    await query.answer("control panel closed")
    user_id = query.message.from_user.id
    buttons = stream_markup(user_id)
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("set_close"))
@check_blacklist()
async def on_close_menu(_, query: CallbackQuery):
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("💡 Yalnızca bu düğmeye dokunabilen görüntülü sohbet yönetme iznine sahip yönetici !", show_alert=True)
    await query.message.delete()


@Client.on_callback_query(filters.regex("close_panel"))
@check_blacklist()
async def in_close_panel(_, query: CallbackQuery):
    await query.message.delete()
