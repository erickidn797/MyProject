import os
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# Minimal example of regional code mapping for demonstration
# Key is 6-digit regional code, value is a dict with province, regency, district
REGIONS = {
    "150403": {
        "province": "Jambi",
        "regency": "Kabupaten Batanghari",
        "district": "Kecamatan Muara Bulian"
    },
    "320301": {
        "province": "Jawa Barat",
        "regency": "Kabupaten Bandung",
        "district": "Kecamatan Andir"
    },
    # Add more region codes as needed here...
}

def decode_nik(nik: str):
    """
    Decode the Indonesian NIK (Nomor Induk Kependudukan).

    Format:
    - 6 digits: region code (province+regency+district)
    - 6 digits: date of birth DDMMYY (for females, day + 40)
    - 4 digits: registration number

    Returns dict with extracted info or None if invalid
    """
    if len(nik) != 16 or not nik.isdigit():
        return None
    
    region_code = nik[:6]
    dob_part = nik[6:12]
    reg_number = nik[12:]
    
    # Lookup region info
    region_info = REGIONS.get(region_code, {
        "province": "Unknown",
        "regency": "Unknown",
        "district": "Unknown"
    })
    
    # Parse date of birth and gender
    day = int(dob_part[:2])
    month = int(dob_part[2:4])
    year = int(dob_part[4:6])
    
    # Gender detection and adjustment for female
    if day > 40:
        gender = "Perempuan"
        day -= 40
    else:
        gender = "Laki-laki"
        
    # Year adjustment (assuming 1900-1999, can be improved for 2000+)
    if year >= 0 and year <= 20: # assume year between 2000 and 2020 for example
        full_year = 2000 + year
    else:
        full_year = 1900 + year
    
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

def cek_nik(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.strip()
    match = re.match(r'^Cek (\d{16})$', message_text, re.IGNORECASE)
    if match:
        nik = match.group(1)
        decoded = decode_nik(nik)
        if decoded is None:
            response = "NIK yang Anda masukkan tidak valid. Pastikan formatnya benar dan terdiri dari 16 digit angka."
        else:
            response = (
                f"NIK: {decoded['nik']}\n"
                f"Provinsi: {decoded['province']}\n"
                f"Kabupaten: {decoded['regency']}\n"
                f"Kecamatan: {decoded['district']}\n"
                f"Tanggal Lahir: {decoded['birth_date']}\n"
                f"Jenis Kelamin: {decoded['gender']}\n"
                f"Nomor Urut Registrasi: {decoded['registration_number']}"
            )
    else:
        response = "Format salah! Gunakan format: Cek [NIK]\nContoh: Cek 1504030911840001"
    
    update.message.reply_text(response)

def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable tidak ditemukan.")
        return
    
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, cek_nik))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

