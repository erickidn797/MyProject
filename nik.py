import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from aiohttp import web

# Load regional data
def load_regions(file_path):
    regions = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':', 1)
            if len(parts) != 2:
                continue
            code = parts[0].strip()
            location_parts = parts[1].split(',')
            if len(location_parts) != 3:
                continue
            province = location_parts[0].strip()
            regency = location_parts[1].strip()
            district = location_parts[2].strip()
            regions[code] = {
                "province": province,
                "regency": regency,
                "district": district
            }
    return regions

regions = load_regions('regions.txt')

# Decode NIK
def decode_nik(nik: str):
    if len(nik) != 16 or not nik.isdigit():
        return None
    region_code = nik[:6]
    dob_part = nik[6:12]
    reg_number = nik[12:]

    region_info = regions.get(region_code, {
        "province": "Unknown",
        "regency": "Unknown",
        "district": "Unknown"
    })

    day = int(dob_part[:2])
    month = int(dob_part[2:4])
    year = int(dob_part[4:6])

    if day > 40:
        gender = "Perempuan"
        day -= 40
    else:
        gender = "Laki-laki"

    full_year = 2000 + year if year <= 20 else 1900 + year

    try:
        dob = datetime(full_year, month, day)
        dob_str = dob.strftime("%d %B %Y")
    except ValueError:
        dob_str = "Tanggal lahir tidak valid"

    return {
        "nik": nik,
        "province": region_info["province"],
        "regency": region_info["regency"],
        "district": region_info["district"],
        "birth_date": dob_str,
        "gender": gender,
        "registration_number": reg_number
    }

# Bot handler
async def cek_nik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    match = re.match(r'^Cek (\d{16})$', message_text, re.IGNORECASE)
    if match:
        nik = match.group(1)
        decoded = decode_nik(nik)
        if decoded is None:
            response = "NIK tidak valid. Format harus 16 digit angka."
        else:
            response = (
                f"NIK: {decoded['nik']}\n"
                f"Provinsi: {decoded['province']}\n"
                f"Kabupaten: {decoded['regency']}\n"
                f"Kecamatan: {decoded['district']}\n"
                f"Tanggal Lahir: {decoded['birth_date']}\n"
                f"Jenis Kelamin: {decoded['gender']}\n"
                f"Nomor Registrasi: {decoded['registration_number']}"
            )
    else:
        response = "Format salah! Gunakan: Cek [NIK]\nContoh: Cek 1504030911840001"

    await update.message.reply_text(response)

# Entry point
async def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    PORT = int(os.getenv("PORT", "8443"))
    HOST = "0.0.0.0"
    APP_URL = os.getenv("RENDER_EXTERNAL_URL")  # ex: https://your-bot.onrender.com

    if not TOKEN or not APP_URL:
        print("Token atau URL tidak ditemukan.")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cek_nik))

    await application.bot.set_webhook(f"{APP_URL}/webhook")
    await application.run_webhook(
        listen=HOST,
        port=PORT,
        webhook_path="/webhook",
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
