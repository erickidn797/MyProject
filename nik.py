import os
import re
from datetime import datetime
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
import asyncio

# Load regional data (pastikan file regions.txt ada dan benar formatnya)
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

# Fungsi decode NIK
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

# Handler /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is running with webhook!")

# Handler untuk cek NIK
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

async def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cek_nik))

    await app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=token,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{token}"
    )

if __name__ == "__main__":
    asyncio.run(main())
