"""Bir Dakikada tarzında 1080x1920 başlık kartı üretir.

Lacivert zemin, üstte (varsa) illüstrasyon, altta harfleri aralıklı büyük
harfli başlık ve küçük kırmızı ✕ işaretleri.

Kullanım:
    python araclar/kapak.py "Arılar kraliçeyi neden değiştirir?" cikti.png
    python araclar/kapak.py "Başlık" cikti.png --gorsel gorseller/kapak.png
"""

from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

GENISLIK, YUKSEKLIK = 1080, 1920
LACIVERT = (37, 46, 124)        # kanaldaki zemin rengi (#252e7c)
YAZI = (246, 242, 255)
PEMBE = (255, 92, 170)
CAMGOBEGI = (70, 220, 255)
KIRMIZI = (226, 48, 58)

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VARSAYILAN_FONT = os.path.join(
    KOK, "MoneyPrinterTurbo", "resource", "fonts", "BeVietnamPro-Bold.ttf"
)


def turkce_buyuk(metin: str) -> str:
    """'i' -> 'İ', 'ı' -> 'I' dönüşümüyle doğru Türkçe büyük harf."""
    return metin.replace("i", "İ").replace("ı", "I").upper()


def aralikli_genislik(ciz, metin, font, aralik):
    if not metin:
        return 0
    toplam = sum(ciz.textlength(h, font=font) for h in metin)
    return toplam + aralik * (len(metin) - 1)


def satirlara_bol(ciz, metin, font, aralik, max_genislik):
    satirlar, satir = [], ""
    for kelime in metin.split():
        deneme = f"{satir} {kelime}".strip()
        if aralikli_genislik(ciz, deneme, font, aralik) <= max_genislik or not satir:
            satir = deneme
        else:
            satirlar.append(satir)
            satir = kelime
    if satir:
        satirlar.append(satir)
    return satirlar


def aralikli_yaz(ciz, x, y, metin, font, aralik, renk):
    for harf in metin:
        ciz.text((x, y), harf, font=font, fill=renk)
        x += ciz.textlength(harf, font=font) + aralik


def carpi(ciz, merkez, boyut=22, kalinlik=7):
    cx, cy = merkez
    ciz.line((cx - boyut, cy - boyut, cx + boyut, cy + boyut), fill=KIRMIZI, width=kalinlik)
    ciz.line((cx - boyut, cy + boyut, cx + boyut, cy - boyut), fill=KIRMIZI, width=kalinlik)


def kapak_uret(baslik: str, cikti: str, gorsel: str | None = None, font_yolu: str | None = None) -> str:
    font_yolu = font_yolu or VARSAYILAN_FONT
    if not os.path.exists(font_yolu):
        sys.exit(f"Font bulunamadı: {font_yolu}\nÖnce 'python kur.py' çalıştırın.")

    tuval = Image.new("RGB", (GENISLIK, YUKSEKLIK), LACIVERT)

    # Üst bölüm: illüstrasyon (oranı korunarak sığdırılır)
    gorsel_alt = 820
    if gorsel and os.path.exists(gorsel):
        with Image.open(gorsel) as g:
            g = g.convert("RGBA")
            g.thumbnail((860, 860))
            x = (GENISLIK - g.width) // 2
            y = 120 + (860 - g.height) // 2
            tuval.paste(g, (x, y), g)
            gorsel_alt = y + g.height

    ciz = ImageDraw.Draw(tuval)
    metin = turkce_buyuk(baslik.strip())

    # Başlık: sığana kadar fontu küçült
    max_genislik = GENISLIK - 160
    boyut = 92
    while True:
        font = ImageFont.truetype(font_yolu, boyut)
        aralik = int(boyut * 0.22)
        satirlar = satirlara_bol(ciz, metin, font, aralik, max_genislik)
        satir_yuk = int(boyut * 1.45)
        sigiyor = all(aralikli_genislik(ciz, s, font, aralik) <= max_genislik for s in satirlar)
        if (sigiyor and len(satirlar) * satir_yuk <= 760) or boyut <= 48:
            break
        boyut -= 4

    blok = len(satirlar) * satir_yuk
    ust = max(gorsel_alt + 120, 1000) if gorsel else (YUKSEKLIK - blok) // 2
    ust = min(ust, YUKSEKLIK - blok - 160)

    for i, satir in enumerate(satirlar):
        w = aralikli_genislik(ciz, satir, font, aralik)
        x = (GENISLIK - w) / 2
        y = ust + i * satir_yuk
        aralikli_yaz(ciz, x - 4, y, satir, font, aralik, CAMGOBEGI)   # renk kayması efekti
        aralikli_yaz(ciz, x + 4, y, satir, font, aralik, PEMBE)
        aralikli_yaz(ciz, x, y, satir, font, aralik, YAZI)

    # Kanaldaki gibi küçük kırmızı çarpılar
    carpi(ciz, (90, ust + satir_yuk // 2))
    if gorsel:
        carpi(ciz, (GENISLIK - 110, max(220, gorsel_alt - 60)))
    else:
        carpi(ciz, (GENISLIK - 110, ust + blok + 70))

    os.makedirs(os.path.dirname(os.path.abspath(cikti)), exist_ok=True)
    tuval.save(cikti)
    return cikti


def main():
    p = argparse.ArgumentParser(description="Bir Dakikada başlık kartı üretici")
    p.add_argument("baslik")
    p.add_argument("cikti")
    p.add_argument("--gorsel", help="kartın üstüne konacak illüstrasyon (PNG, şeffaf zemin ideal)")
    p.add_argument("--font", help="font dosyası yolu")
    a = p.parse_args()
    print(kapak_uret(a.baslik, a.cikti, a.gorsel, a.font))


if __name__ == "__main__":
    main()
