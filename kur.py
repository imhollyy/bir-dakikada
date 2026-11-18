"""Bir Dakikada kurulumu.

1. MoneyPrinterTurbo'yu bu klasörün içine indirir (MoneyPrinterTurbo/)
2. Python ortamını kurar (.venv)
3. config.toml'u Bir Dakikada için ayarlar (Türkçe, Gemini, Edge altyazı)

Kullanım:
    python kur.py                 # ilk kurulum
    python kur.py --guncelle      # MoneyPrinterTurbo'yu son sürüme güncelle
"""

from __future__ import annotations

import argparse
import getpass
import os
import re
import shutil
import subprocess
import sys

KOK = os.path.dirname(os.path.abspath(__file__))
MPT = os.path.join(KOK, "MoneyPrinterTurbo")
MPT_REPO = "https://github.com/harry0703/MoneyPrinterTurbo.git"


def calistir(komut, **kw):
    print("  $", " ".join(komut))
    subprocess.run(komut, check=True, **kw)


def indir(guncelle: bool):
    if not shutil.which("git"):
        sys.exit("git bulunamadı. https://git-scm.com adresinden kurun.")
    if not os.path.isdir(MPT):
        print("→ MoneyPrinterTurbo indiriliyor (yaklaşık 200 MB, birkaç dakika sürebilir)...")
        calistir(["git", "clone", "--depth", "1", MPT_REPO, MPT])
    elif guncelle:
        print("→ MoneyPrinterTurbo güncelleniyor...")
        calistir(["git", "pull", "--ff-only"], cwd=MPT)
    else:
        print("✓ MoneyPrinterTurbo zaten indirilmiş.")


def ortam_kur():
    if shutil.which("uv"):
        print("→ Python ortamı uv ile kuruluyor...")
        calistir(["uv", "sync", "--frozen"], cwd=MPT)
        return
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 veya üstü gerekli (ya da 'uv' kurun: https://docs.astral.sh/uv/).")
    print("→ Python ortamı venv + pip ile kuruluyor...")
    venv = os.path.join(MPT, ".venv")
    if not os.path.isdir(venv):
        calistir([sys.executable, "-m", "venv", venv])
    py = os.path.join(venv, "Scripts", "python.exe") if os.name == "nt" else os.path.join(venv, "bin", "python")
    calistir([py, "-m", "pip", "install", "-r", "requirements.txt"], cwd=MPT)


def ayarla(anahtar_metni: str, deger: str, metin: str) -> str:
    """config.toml'daki ilk 'anahtar = ...' satırını değiştirir."""
    yeni, adet = re.subn(
        rf'(?m)^{re.escape(anahtar_metni)}\s*=.*$',
        lambda _: f"{anahtar_metni} = {deger}",
        metin,
        count=1,
    )
    if not adet:
        print(f"  ! config.toml'da '{anahtar_metni}' bulunamadı, atlandı.")
    return yeni


def config_hazirla():
    hedef = os.path.join(MPT, "config.toml")
    if not os.path.exists(hedef):
        shutil.copy(os.path.join(MPT, "config.example.toml"), hedef)
    with open(hedef, encoding="utf-8") as f:
        metin = f.read()

    metin = ayarla("llm_provider", '"gemini"', metin)
    metin = ayarla("subtitle_provider", '"edge"', metin)
    metin = ayarla("listen_host", '"127.0.0.1"', metin)

    if '\ngemini_api_key = ""' in metin:
        print("\nSenaryoyu yapay zekânın yazması için ücretsiz bir Gemini API anahtarı gerekir.")
        print("Almak için: https://aistudio.google.com/app/apikey")
        print("(Metinleri hep kendin yazacaksan Enter'a basıp geçebilirsin.)")
        anahtar = getpass.getpass("Gemini API anahtarı (ekranda görünmez): ").strip()
        if anahtar:
            metin = ayarla("gemini_api_key", f'"{anahtar}"', metin)

    with open(hedef, "w", encoding="utf-8") as f:
        f.write(metin)
    print("✓ config.toml hazır (anahtarlar sadece bu bilgisayarda, GitHub'a gitmez).")


def main():
    p = argparse.ArgumentParser(description="Bir Dakikada kurulumu")
    p.add_argument("--guncelle", action="store_true", help="MoneyPrinterTurbo'yu güncelle")
    a = p.parse_args()

    indir(a.guncelle)
    ortam_kur()
    config_hazirla()
    print("\nKurulum tamam. Deneme videosu için:")
    print("  python uret.py konular/arilar-kralice")


if __name__ == "__main__":
    main()
