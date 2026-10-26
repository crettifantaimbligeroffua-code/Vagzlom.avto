"""Publish newly added car listings to a Telegram channel."""
import io
import json
import os
import sqlite3
import time
from pathlib import Path

import requests

BASE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE))).expanduser().resolve()
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]

DEFAULT_TEMPLATE = """🔥 {brand} {model} {engine_info} {year}
🪪 {vin}
🌐 Посилання на сайт з детальними характеристиками: {listing_url}

🚙 Пробіг: {mileage} тис. км
🔥 Паливо: {fuel}
🚙 Привід: {drive}
🚙 Коробка: {gearbox}

💵 Ціна: ${price}

* Ціна авто у Львові.
У вартість автомобіля враховані всі транспортні витрати і розмитнення!

Наші контакти :📲
{phone}

Хочеш схоже авто?
Привеземо за найкращою ціною в Україні 🤝"""


def _s(value):
    return str(value).strip() if value is not None else ""


def _load_car_and_photos(car_id):
    """Read from the same database configured for the Flask app (SQLite or PostgreSQL)."""
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode="require")
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cars WHERE id=%s", (car_id,))
                car = cur.fetchone()
                cur.execute("SELECT filename FROM car_photos WHERE car_id=%s ORDER BY id", (car_id,))
                photos = cur.fetchall()
                cur.execute("SELECT value FROM settings WHERE key=%s", ("telegram_template",))
                tmpl = cur.fetchone()
                # Database-backed photo bytes keep publishing working even if local files are absent.
                photo_data = {}
                for photo in photos:
                    filename = photo["filename"]
                    cur.execute("SELECT data,mime FROM uploaded_files WHERE filename=%s", (filename,))
                    blob = cur.fetchone()
                    if blob:
                        photo_data[filename] = (bytes(blob["data"]), blob["mime"])
            return (dict(car) if car else None, [dict(p) for p in photos],
                    (tmpl["value"] if tmpl and tmpl.get("value") else None), photo_data)
        finally:
            conn.close()

    db_path = DATA_DIR / "vagzlumauto.db"
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite database not found: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
        photos = conn.execute("SELECT filename FROM car_photos WHERE car_id=? ORDER BY id", (car_id,)).fetchall()
        tmpl = conn.execute("SELECT value FROM settings WHERE key=?", ("telegram_template",)).fetchone()
        return (dict(car) if car else None, [dict(p) for p in photos],
                tmpl["value"] if tmpl and tmpl["value"] else None, {})
    finally:
        conn.close()


def _send_telegram(car_id, delay=3):
    time.sleep(max(0, delay))
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
    if not token or not channel_id:
        print(f"Telegram: пропущено — відсутня змінна {'TELEGRAM_BOT_TOKEN' if not token else 'TELEGRAM_CHANNEL_ID'} у Render Environment.", flush=True)
        return

    site_url = os.getenv("SITE_URL", "https://vagzlom-avto3.onrender.com").strip().rstrip("/")
    listing_url = f"{site_url}/cars/{car_id}"
    try:
        car, photos, template, photo_data = _load_car_and_photos(car_id)
    except Exception:
        print(f"Telegram: не вдалося прочитати авто {car_id} з бази даних.", flush=True)
        import traceback
        traceback.print_exc()
        return
    if not car:
        print(f"Telegram: авто id={car_id} не знайдено в базі.", flush=True)
        return

    brand = _s(car.get("brand")); model = _s(car.get("model")); year = _s(car.get("year"))
    vin = _s(car.get("vin") or car.get("vin_code") or "Не вказано")
    mileage = _s(car.get("mileage")); fuel = _s(car.get("fuel"))
    drive = _s(car.get("drive")) or "Не вказано"
    gearbox = _s(car.get("gearbox")) or "Не вказано"
    price = _s(car.get("price")); phone = _s(car.get("phone") or "+380989565333")
    engine_info = _s(car.get("engine") or car.get("power") or "")
    template = template or DEFAULT_TEMPLATE
    try:
        caption = template.format(brand=brand, model=model, year=year, vin=vin,
            mileage=mileage, fuel=fuel, drive=drive, gearbox=gearbox, price=price,
            phone=phone, engine_info=engine_info, url=site_url + "/", listing_url=listing_url)
    except Exception as exc:
        print(f"Telegram: помилка шаблону ({exc}); використовую стандартний текст.", flush=True)
        caption = DEFAULT_TEMPLATE.format(brand=brand, model=model, year=year, vin=vin,
            mileage=mileage, fuel=fuel, drive=drive, gearbox=gearbox, price=price,
            phone=phone, engine_info=engine_info, url=site_url + "/", listing_url=listing_url)

    caption = caption.replace("https://vagzlomavto.onrender.com", site_url).replace("https://vagzlumavto.onrender.com", site_url)

    # Prefer persistent DB photo bytes, then the local upload file.
    images = []
    for row in photos:
        filename = row["filename"]
        if filename in photo_data:
            raw, mime = photo_data[filename]
            images.append((filename, raw, mime))
        else:
            path = UPLOAD_DIR / filename
            if path.exists():
                images.append((filename, path.read_bytes(), "image/jpeg"))
        if len(images) >= 10:
            break

    try:
        if not images:
            response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                data={"chat_id": channel_id, "text": caption}, timeout=30)
            result = response.json()
            if not response.ok or not result.get("ok"):
                print(f"Telegram sendMessage failed: HTTP {response.status_code}; {result}", flush=True)
                return
            print(f"Telegram: опубліковано текст оголошення авто id={car_id}.", flush=True)
            return

        if len(images) == 1:
            filename, raw, mime = images[0]
            response = requests.post(f"https://api.telegram.org/bot{token}/sendPhoto",
                data={"chat_id": channel_id, "caption": caption[:1024]},
                files={"photo": (filename, io.BytesIO(raw), mime)}, timeout=90)
        else:
            media = []
            files = {}
            for index, (filename, raw, mime) in enumerate(images):
                key = f"photo{index}"
                files[key] = (filename, io.BytesIO(raw), mime)
                item = {"type": "photo", "media": f"attach://{key}"}
                if index == 0:
                    item["caption"] = caption[:1024]
                media.append(item)
            response = requests.post(f"https://api.telegram.org/bot{token}/sendMediaGroup",
                data={"chat_id": channel_id, "media": json.dumps(media, ensure_ascii=False)},
                files=files, timeout=120)
        try:
            result = response.json()
        except Exception:
            result = {"description": response.text[:500], "ok": False}
        if not response.ok or not result.get("ok"):
            print(f"Telegram photo publish failed for car id={car_id}: HTTP {response.status_code}; {result}", flush=True)
        else:
            print(f"Telegram: успішно опубліковано авто id={car_id}, фото: {len(images)}.", flush=True)
    except Exception:
        print(f"Telegram: помилка надсилання оголошення авто id={car_id}.", flush=True)
        import traceback
        traceback.print_exc()


def schedule_new_car(car_id):
    """Schedule asynchronous Telegram publication 30 seconds after saving the listing."""
    try:
        import threading
        thread = threading.Thread(target=_send_telegram, args=(car_id, 3), daemon=True)
        thread.start()
        print(f"Telegram: заплановано публікацію авто id={car_id} через 3 секунди.", flush=True)
    except Exception:
        import traceback
        print("Telegram: не вдалося запустити фонову публікацію.", flush=True)
        traceback.print_exc()
