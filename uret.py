"""Bir Dakikada video üretici.

Bir konu klasöründen (konular/<konu>/) MoneyPrinterTurbo ile video üretir.

Klasör yapısı:
    konular/arilar-kralice/
        baslik.txt        (zorunlu) Başlık kartındaki soru/başlık
        metin.txt         (isteğe bağlı) Okunacak metin. Yoksa yapay zekâ yazar.
        ses.mp3           (isteğe bağlı) Kendi seslendirmen (.mp3/.m4a/.wav)
        gorseller/        (isteğe bağlı) 1.png, 2.png ... sırayla gösterilir
            kapak.png     (isteğe bağlı) Başlık kartının üstüne konan çizim
        ayar.json         (isteğe bağlı) Bu videoya özel ayarlar (varsayilan.json'u ezer)

Kullanım:
    python uret.py konular/arilar-kralice                 # videoyu üret
    python uret.py konular/arilar-kralice --sadece-metin  # sadece metni yazdır, metin.txt'ye kaydet
    python uret.py konular/*                              # birden fazla konuyu sırayla üret
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
MPT = os.path.join(KOK, "MoneyPrinterTurbo")
sys.path.insert(0, os.path.join(KOK, "araclar"))

from kapak import kapak_uret  # noqa: E402

GORSEL_UZANTILARI = (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov")
SES_ADLARI = ("ses.mp3", "ses.m4a", "ses.wav")


def oku(yol: str) -> str:
    with open(yol, encoding="utf-8") as f:
        return f.read().strip()


def mpt_python() -> str:
    for aday in (
        os.path.join(MPT, ".venv", "Scripts", "python.exe"),
        os.path.join(MPT, ".venv", "bin", "python"),
    ):
        if os.path.exists(aday):
            return aday
    sys.exit("MoneyPrinterTurbo kurulu değil. Önce şunu çalıştırın:  python kur.py")


def bul(nesne, anahtar):
    """İç içe JSON içinde bir anahtarın ilk değerini bulur."""
    if isinstance(nesne, dict):
        if anahtar in nesne and nesne[anahtar]:
            return nesne[anahtar]
        for v in nesne.values():
            sonuc = bul(v, anahtar)
            if sonuc:
                return sonuc
    elif isinstance(nesne, list):
        for v in nesne:
            sonuc = bul(v, anahtar)
            if sonuc:
                return sonuc
    return None


def gorev_hazirla(klasor: str) -> tuple[dict, str]:
    ad = os.path.basename(os.path.normpath(klasor))
    baslik_yolu = os.path.join(klasor, "baslik.txt")
    if not os.path.exists(baslik_yolu):
        sys.exit(f"{klasor}: baslik.txt yok.")
    baslik = oku(baslik_yolu)

    uretilen = os.path.join(klasor, "_uretilen")
    os.makedirs(uretilen, exist_ok=True)

    gorsel_klasoru = os.path.join(klasor, "gorseller")
    kapak_cizim = None
    gorseller = []
    if os.path.isdir(gorsel_klasoru):
        for dosya in sorted(os.listdir(gorsel_klasoru)):
            yol = os.path.abspath(os.path.join(gorsel_klasoru, dosya))
            if not dosya.lower().endswith(GORSEL_UZANTILARI):
                continue
            if os.path.splitext(dosya)[0].lower() == "kapak":
                kapak_cizim = yol
            else:
                gorseller.append(yol)

    kapak = kapak_uret(baslik, os.path.join(uretilen, "kapak.png"), kapak_cizim)
    if not gorseller:
        print(f"  ! {ad}: gorseller/ klasörü boş, video sadece başlık kartından oluşacak.")

    gorev = json.load(open(os.path.join(KOK, "ayarlar", "varsayilan.json"), encoding="utf-8"))
    ozel = os.path.join(klasor, "ayar.json")
    if os.path.exists(ozel):
        gorev.update(json.load(open(ozel, encoding="utf-8")))

    gorev["video_subject"] = baslik
    gorev["custom_system_prompt"] = oku(os.path.join(KOK, "ayarlar", "sistem_promptu.txt"))
    gorev["video_materials"] = [
        {"provider": "local", "url": yol} for yol in [os.path.abspath(kapak), *gorseller]
    ]

    metin_yolu = os.path.join(klasor, "metin.txt")
    if os.path.exists(metin_yolu) and oku(metin_yolu):
        gorev["video_script"] = oku(metin_yolu)

    for ses in SES_ADLARI:
        if os.path.exists(os.path.join(klasor, ses)):
            gorev["custom_audio_file"] = os.path.abspath(os.path.join(klasor, ses))
            break

    manifest = os.path.join(uretilen, "gorev.json")
    with open(manifest, "w", encoding="utf-8") as f:
        json.dump([gorev], f, ensure_ascii=False, indent=2)
    return gorev, manifest


def calistir(manifest: str, dur: str | None) -> dict:
    komut = [mpt_python(), "cli.py", "--batch-file", os.path.abspath(manifest)]
    if dur:
        komut += ["--stop-at", dur]
    sonuc = subprocess.run(komut, cwd=MPT, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    try:
        return json.loads(sonuc.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        sys.exit(f"MoneyPrinterTurbo beklenmedik çıktı verdi (kod {sonuc.returncode}). Yukarıdaki logu kontrol edin.")


def konu_isle(klasor: str, sadece_metin: bool) -> bool:
    ad = os.path.basename(os.path.normpath(klasor))
    print(f"\n=== {ad} ===")
    gorev, manifest = gorev_hazirla(klasor)

    if sadece_metin:
        ozet = calistir(manifest, "script")
        metin = bul(ozet, "script")
        if not metin:
            print(f"  ✗ Metin üretilemedi: {bul(ozet, 'error')}")
            return False
        with open(os.path.join(klasor, "metin.txt"), "w", encoding="utf-8") as f:
            f.write(metin.strip() + "\n")
        print(f"  ✓ metin.txt yazıldı ({len(metin.split())} kelime). Okuyup düzelt, sonra videoyu üret.")
        return True

    ozet = calistir(manifest, None)
    videolar = bul(ozet, "videos") or bul(ozet, "combined_videos")
    if not videolar:
        print(f"  ✗ Video üretilemedi: {bul(ozet, 'error')}")
        return False
    hedef = os.path.join(klasor, f"{ad}.mp4")
    shutil.copy(videolar[0], hedef)
    if "video_script" not in gorev:
        metin = bul(ozet, "script")
        if metin:
            with open(os.path.join(klasor, "metin.txt"), "w", encoding="utf-8") as f:
                f.write(metin.strip() + "\n")
    print(f"  ✓ Video hazır: {hedef}")
    return True


def main():
    p = argparse.ArgumentParser(description="Bir Dakikada video üretici")
    p.add_argument("klasorler", nargs="+", help="konu klasör(ler)i, ör. konular/arilar-kralice")
    p.add_argument("--sadece-metin", action="store_true", help="sadece metni üret ve metin.txt'ye yaz")
    a = p.parse_args()

    klasorler = [k for desen in a.klasorler for k in (glob.glob(desen) or [desen])]
    klasorler = [k for k in klasorler if os.path.isdir(k)]
    if not klasorler:
        sys.exit("Konu klasörü bulunamadı.")
    basarili = sum(konu_isle(k, a.sadece_metin) for k in klasorler)
    print(f"\n{basarili}/{len(klasorler)} konu tamamlandı.")
    sys.exit(0 if basarili == len(klasorler) else 1)


if __name__ == "__main__":
    main()
