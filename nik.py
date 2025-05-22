from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import re

# Peta kode wilayah (bisa kamu tambah sendiri)
kode_wilayah = {
    '15': 'Jambi',
    '1504': 'Kabupaten Batanghari',
    '150403': 'Kecamatan Muara Bulian'
}

def parse_nik(nik):
    if len(nik) != 16 or not nik.isdigit():
        return None

    provinsi = kode_wilayah.get(nik[:2], 'Tidak diketahui')
    kabupaten = kode_wilayah.get(nik[:4], 'Tidak diketahui')
    kecamatan = kode_wilayah.get(nik[:6], f'Kode {nik[4:6]}')

    day = int(nik[6:8])
    month = int(nik[8:10])
    year = int(nik[10:12])
    gender = 'Perempuan' if day > 40 else 'Laki-laki'
    if gender == 'Perempuan':
        day -= 40

    months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
              'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    year_full = 1900 + year if year >= 25 else 2000 + year
    tanggal_lahir = f"{day} {months[month - 1]} {year_full}"
    urut = nik[12:]

    return (f"NIK: {nik}\n"
            f"Provinsi: {provinsi}\n"
            f"Kabupaten: {kabupaten}\n"
            f"Kecamatan: {kecamatan}\n"
            f"Tanggal Lahir: {tanggal_lahir}\n"
            f"Jenis Kelamin: {gender}\n"
            f"Nomor Urut Registrasi: {urut}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    # Deteksi format "Cek 1234567890123456"
    match = re.match(r'^[Cc]ek\\s+(\\d{16})$', text)
    if not match:
        return  # Abaikan jika bukan format valid

    nik = match.group(1)
    response = parse_nik(nik)
    if response:
        await update.message.reply_text(response)

if __name__ == '__main__':
    TOKEN = "ISI_DENGAN_TOKEN_BOT_KAMU"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot NIK checker aktif...")
    app.run_polling()
