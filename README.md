# 🚀 Capi SMS Bomber Bot

> ⚠️ **UYARI:** Bu bot yalnızca **eğitim** ve **test** amaçlıdır. İzinsiz kullanımı KVKK ve diğer yasal düzenlemeleri ihlal edebilir. **Sorumluluk kullanıcıya aittir.**

---

## 🔎 Proje Hakkında

Capi SMS Bomber Bot, belirlediğiniz telefon numarasına çok sayıda SMS gönderimi simüle eden bir **Telegram botudur**.  
SMS gönderimi, `sms.py` içindeki servis metotları kullanılarak paralel olarak gerçekleştirilir.

---

## ✨ Özellikler

- 📲 `/sms <telefon_numarası>` komutuyla **Bass Mode** (yüksek hızlı) SMS bombardımanı  
- ⛔ `/stop` komutuyla anlık gönderimi durdurma  
- ℹ️ `/help` komutuyla komut listesini görüntüleme  
- 🚧 Başarı ve başarısız gönderim sayıları **canlı** olarak güncellenen durum kutusu  
- ⚙️ Basit kurulum ve yapılandırma  
- 🔒 Sadece test ortamı için, izinsiz kullanıma ve spam'a karşı **sorumluluk** uyarıları  

---

## 📦 Gereksinimler

- Python 3.7 veya üzeri  
- Kütüphaneler:
  - `aiogram==2.25.2`
  - `requests`
  - `colorama`

```bash
pip install aiogram requests colorama
```

---

## ⚙️ Kurulum & Yapılandırma

1. Depoyu klonlayın veya indirin:
   ```bash
   git clone https://github.com/byblackcapi/smsbomber.git
   cd smsbomber
   ```
2. Gerekli Python paketlerini yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. `bot.py`, `sms.py` ve `requirements.txt` dosyalarının aynı klasörde olduğundan emin olun.  
4. `bot.py` içindeki `API_TOKEN` değerini, Telegram BotFather'dan aldığınız token ile değiştirin.

---

## 🚀 Kullanım

Telegram'da botunuzu çalıştırdıktan sonra:

1. **Başlat**  
   ```
   /start
   ```
   📝 Bot size karşılama ve komut bilgilendirmesini gönderecek.

2. **SMS Gönderimi**  
   ```
   /sms 5051234567
   ```
   🔄 Parçalı tüm servisler tetiklenir; başarı/başarısız sayıları canlı güncellenir.

3. **Durdur**  
   ```
   /stop
   ```
   ⛔ Anlık gönderim işlemini durdurur.

4. **Yardım**  
   ```
   /help
   ```
   ℹ️ Tüm komutların listesini gösterir.

---

## 📋 Servis Listesi

`servis.json` içine yazılan veya `sms.py` içerisindeki metot ismiyle eşleşen servisler kullanılır. Örnek:
```json
[
  "Akasya",
  "Akbati",
  "Ayyildiz",
  "Baydoner",
  ...
  "Yuffi"
]
```

---

## 🛡️ Güvenlik & Etik

- Sadece **kendi** telefon numaralarınızda deneyin.  
- İzinsiz SMS göndermek **suçtur** ve yasal yaptırımlara neden olabilir.  
- Botu sorumlu ve etik kurallar çerçevesinde kullanın.

---

### 🚀 İyi Testler!  
**Capi** tarafından geliştirilmiştir.  







