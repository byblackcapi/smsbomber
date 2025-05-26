from telethon import TelegramClient, events from sms import SendSms import asyncio from concurrent.futures import ThreadPoolExecutor from datetime import datetime import logging

Telegram API bilgileri

api_id = 23350184 api_hash = "41f0c2a157268e158f91ab7d59f4fc19" bot_token = "7107604320:AAEcx_S-aa8IwW8PiOWcAdNm_dAX0EczFX4"

Log ayarları

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

client = TelegramClient('smsbomber_bot', api_id, api_hash).start(bot_token=bot_token)

active_tasks = {} status_counts = {} executor = ThreadPoolExecutor(max_workers=50)

@client.on(events.NewMessage(pattern='/start')) async def start_handler(event): await event.respond( "Capi SMS Bomber'a Hoş Geldin!\n\n" "Bu bot belirli servisler üzerinden SMS gönderimi simüle eder.\n\n" "Komutlar:\n" "📲 /sms <telefon> - SMS göndermeye başla\n" "⛔ /stop - Gönderimi durdur\n" "ℹ️ /help - Yardım\n" "🔧 /servisler - Mevcut servis sayısını göster\n\n" "⚠️ Bu proje sadece test amaçlıdır.\n" "Etik kurallar çerçevesinde kullanınız.", parse_mode='markdown' )

@client.on(events.NewMessage(pattern='/help')) async def help_handler(event): await event.respond( "Yardım Menüsü\n\n" "/sms <telefon> - SMS göndermeye başlar\n" "/stop - Aktif bombardımanı durdurur\n" "/servisler - Servis sayısını listeler\n" "/start - Bilgi mesajını tekrar gösterir" )

@client.on(events.NewMessage(pattern='/servisler')) async def service_count_handler(event): dummy_sms = SendSms("0000000000", "") service_count = len([ func for func in dir(SendSms) if callable(getattr(dummy_sms, func)) and not func.startswith("__") ]) await event.respond(f"Mevcut servis sayısı: {service_count} adet", parse_mode='markdown')

@client.on(events.NewMessage(pattern=r'/sms (\d{10})')) async def sms_handler(event): user_id = event.chat_id phone = event.pattern_match.group(1) status_counts[user_id] = {"basarili": 0, "basarisiz": 0}

# Başlangıç mesajı
await event.respond(f"SMS gönderimi başlatılıyor: `0{phone}`", parse_mode='markdown')
status_msg = await event.respond("______________________\nBaşarılı [0]\nBaşarısız [0]\nSuana kadar başarılı yollanan mesaj [0]\n______________________")

send_sms = SendSms(phone, "")
services = [
    getattr(send_sms, method) for method in dir(SendSms)
    if callable(getattr(send_sms, method)) and not method.startswith("__")
]
logging.info(f"{user_id} kullanıcısı için {len(services)} servis ile SMS gönderimi başlatıldı.")

async def spam():
    try:
        while user_id in active_tasks:
            loop = asyncio.get_event_loop()
            futures = [loop.run_in_executor(executor, service) for service in services]
            results = await asyncio.gather(*futures, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    status_counts[user_id]["basarisiz"] += 1
                else:
                    status_counts[user_id]["basarili"] += 1

            # Mesajı düzenle
            await client.edit_message(
                status_msg.chat_id,
                status_msg.id,
                f"______________________\n"
                f"Başarılı [{status_counts[user_id]['basarili']}]\n"
                f"Başarısız [{status_counts[user_id]['basarisiz']}]\n"
                f"Suana kadar başarılı yollanan mesaj [{status_counts[user_id]['basarili']}]\n"
                f"______________________"
            )

            # Konsola log
            logging.info(
                f"0{phone} | Başarılı: {status_counts[user_id]['basarili']} | "
                f"Başarısız: {status_counts[user_id]['basarisiz']}"
            )
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        logging.info(f"{user_id} kullanıcısı SMS gönderimini durdurdu.")

task = asyncio.create_task(spam())
active_tasks[user_id] = task

@client.on(events.NewMessage(pattern='/stop')) async def stop_handler(event): user_id = event.chat_id task = active_tasks.pop(user_id, None) if task: task.cancel() await event.respond("SMS gönderimi durduruldu.") logging.info(f"{user_id} için SMS gönderimi durduruldu.") else: await event.respond("Zaten aktif bir işlem bulunmuyor.")

client.run_until_disconnected()

