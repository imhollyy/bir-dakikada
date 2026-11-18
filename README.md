# Bir Dakikada

[@birdakikada.official](https://www.instagram.com/birdakikada.official/) için yarı otomatik video üretim hattı.
Montajı, seslendirmeyi, altyazıyı ve müziği [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) yapar.
Kanalın görünümü (lacivert zemin, çizim görseller, aralıklı büyük harfli başlık) bu repodaki ayarlarla korunur.

```
konu klasörü  ──►  başlık kartı (otomatik)  ──►  MoneyPrinterTurbo  ──►  hazır .mp4
 baslik.txt          lacivert şablon              ses + altyazı
 metin.txt                                         müzik + montaj
 gorseller/
```

## Kurulum (bir kere)

Gerekenler: **Python 3.11+** ve **git**. (İsteğe bağlı ama daha hızlı: [uv](https://docs.astral.sh/uv/))

```bash
git clone https://github.com/imhollyy/bir-dakikada.git
cd bir-dakikada
python kur.py
```

`kur.py` şunları yapar:
1. MoneyPrinterTurbo'yu `MoneyPrinterTurbo/` klasörüne indirir (yaklaşık 200 MB, repoya girmez)
2. Python ortamını kurar
3. Ayarları Türkçe ve Gemini için yapar, Gemini API anahtarını sorar ([buradan ücretsiz alınır](https://aistudio.google.com/app/apikey))

Anahtarlar sadece senin bilgisayarındaki `MoneyPrinterTurbo/config.toml` içinde durur, GitHub'a gitmez.

## Bir video üretmek

### 1. Konu klasörü aç

`konular/` altına yeni bir klasör aç (Türkçe karakter ve boşluk kullanma), örn. `konular/dinozorlar-neden-yok-oldu/`:

| Dosya | Zorunlu mu | Ne işe yarar |
|---|---|---|
| `baslik.txt` | **Evet** | Başlık kartındaki soru. Örn: `Dinozorları ne yok etti?` |
| `metin.txt` | Hayır | Okunacak metin. Yoksa yapay zekâ kanalın tarzında yazar. |
| `ses.mp3` | Hayır | Kendi seslendirmen (`.mp3`, `.m4a` veya `.wav`) |
| `gorseller/` | Önerilir | `kapak.png` başlık kartına, `1.png`, `2.png`... sırayla videoya girer |
| `ayar.json` | Hayır | Sadece bu videoya özel ayar (örn. `{"voice_name": "tr-TR-EmelNeural-Female"}`) |

Örnek olarak `konular/arilar-kralice/` ve `konular/ahtapot-uc-kalp/` hazır. Metinleri yazılı, görsel listeleri `gorseller/BENI-OKU.md` içinde.

**Metin yapısı (60 sn):** kanca (0-3 sn) → "Bir Dakikada'ya hoş geldin." (3-5 sn) → konu (5-52 sn) → kapanış + "Daha fazlası için Bir Dakikada'yı takip etmeyi unutma." (52-60 sn). Kendi metnini yazarken de bu kalıbı kullan; yaklaşık 115-130 kelime.

### 2. (İsteğe bağlı) Önce metni üret ve kontrol et

```bash
python uret.py konular/dinozorlar-neden-yok-oldu --sadece-metin
```

`metin.txt` oluşur. Oku, yanlış bilgi varsa düzelt. Yapay zekâ metinlerini yayınlamadan önce mutlaka kontrol et.

### 3. Videoyu üret

```bash
python uret.py konular/dinozorlar-neden-yok-oldu
```

Video klasörün içine `dinozorlar-neden-yok-oldu.mp4` olarak kaydedilir.

**Toplu üretim:** Hafta sonu 5 konu klasörü hazırla, sonra tek komutla hepsini üret:

```bash
python uret.py konular/*
```

## Üç çalışma şekli

| Şekil | Ne yaparsın | Not |
|---|---|---|
| **En hızlı** | Sadece `baslik.txt` + görseller | Metni yapay zekâ yazar, yapay zekâ sesi okur |
| **Önerilen** | `baslik.txt` + kendi `metin.txt`'in + görseller | Bilgi doğruluğu sende, ses yapay zekâda |
| **En kişisel** | Yukarıdakine ek olarak `ses.mp3` | Kendi sesin. Altyazı için aşağıdaki ayara bak. |

**Kendi sesini kullanırken altyazı:** Hazır Türkçe ses kullanılırken altyazı otomatik çıkar.
Kendi sesinde altyazının otomatik çıkması için `MoneyPrinterTurbo/config.toml` dosyasında
`subtitle_provider = "edge"` satırını `subtitle_provider = "whisper"` yap.
İlk seferde ses tanıma modeli indirileceği için biraz uzun sürer. İstersen altyazıyı kapatıp
(`ayar.json`: `{"subtitle_enabled": false}`) Instagram'ın kendi altyazısını da kullanabilirsin.

## Ayarlar

- `ayarlar/varsayilan.json`: Tüm videoların ortak ayarları (ses, hız, altyazı rengi/boyutu, müzik seviyesi, geçiş efekti)
  - Ses: `tr-TR-AhmetNeural-Male` (erkek) veya `tr-TR-EmelNeural-Female` (kadın)
  - `voice_rate`: 1.0 normal, 1.1 biraz hızlı
  - `video_clip_duration`: Her görselin ekranda kalma süresi (saniye)
- `ayarlar/sistem_promptu.txt`: Yapay zekânın metni nasıl yazacağı (kanca, uzunluk, ton)
- `araclar/kapak.py`: Başlık kartı şablonu (renkler en üstte)

Sadece başlık kartını denemek için:

```bash
python araclar/kapak.py "Arılar kraliçeyi neden değiştirir?" deneme.png --gorsel gorseller/kapak.png
```

## Sorun çıkarsa

- **"MoneyPrinterTurbo kurulu değil"**: `python kur.py` çalıştır.
- **Gemini kota/anahtar hatası**: Anahtarı kontrol et ya da metni kendin yaz (`metin.txt`).
- **Ayarları görsel arayüzden değiştirmek istersen**: `MoneyPrinterTurbo` klasöründe `webui.bat` (Windows) veya `sh webui.sh` (Mac/Linux).
- **MoneyPrinterTurbo'yu güncellemek**: `python kur.py --guncelle`

MoneyPrinterTurbo MIT lisanslıdır © harry0703.
