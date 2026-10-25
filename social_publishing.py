import os
import json
import time
import threading
import requests
from pathlib import Path
import sqlite3

BASE = Path(__file__).resolve().parent
UPLOAD_DIR = BASE / "static" / "uploads"

DEFAULT_TEMPLATE = """🔥 {brand} {model} {engine_info} {year}
🪪 {vin}
🌐 Посилання на сайт з детальними характеристиками: https://vagzlomavto.onrender.com/

🚙 Пробіг: {mileage} тис. км
🔥 Паливо: {fuel}
🚙 Привід: {drive}
🚙 Коробка: {gearbox}

💵 Ціна: ${price}

* Ціна авто у Львові .
У вартість автомобіля враховані всі транспортні витрати і розмитнення!

Наші контакти :📲
{phone}

Хочеш схоже авто ?
Привеземо за найкращою ціною в Україні 🤝"""

def _s(v):
    return str(v).strip() if v is not None else ""

def _async_send_to_telegram(car_id, delay=60):
    time.sleep(delay)
    
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

    if not BOT_TOKEN or not CHANNEL_ID:
        print("Telegram Bot Token або Channel ID не задані!")
        return

    db_path = BASE / "vagzlumauto.db"
    if not db_path.exists():
        print(f"База даних не знайдена: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
        photos = conn.execute("SELECT filename FROM car_photos WHERE car_id=? ORDER BY id", (car_id,)).fetchall()
        
        # Get custom template from settings table if exists
        tmpl_row = conn.execute("SELECT value FROM settings WHERE key='telegram_template'").fetchone()
        template = tmpl_row["value"] if tmpl_row and tmpl_row["value"] else DEFAULT_TEMPLATE
    except Exception as e:
        print(f"Помилка бази даних: {e}")
        template = DEFAULT_TEMPLATE
    finally:
        conn.close()

    if not car:
        print(f"Авто {car_id} не знайдено.")
        return

    car = dict(car)
    photo_paths = [UPLOAD_DIR / p["filename"] for p in photos]

    site_url = _s(os.getenv("SITE_URL")).rstrip("/")
    if not site_url:
        site_url = "https://vagzlomavto.onrender.com"
    listing_url = f"{site_url}/cars/{car_id}"

    brand = _s(car.get('brand'))
    model = _s(car.get('model'))
    year = _s(car.get('year'))
    vin = _s(car.get('vin') or car.get('vin_code') or 'Не вказано')
    mileage = _s(car.get('mileage'))
    fuel = _s(car.get('fuel'))
    drive = _s(car.get('drive')) or 'Не вказано'
    gearbox = _s(car.get('gearbox')) or 'Не вказано'
    price = _s(car.get('price'))
    phone = _s(car.get('phone') or '+380989565333')
    engine_info = _s(car.get('engine') or car.get('power') or '')

    # Older saved templates may not yet contain the gearbox placeholder.
    if "{gearbox}" not in template:
        if "🚙 Привід: {drive}" in template:
            template = template.replace("🚙 Привід: {drive}", "🚙 Привід: {drive}\n🚙 Коробка: {gearbox}", 1)
        else:
            template = template.rstrip() + "\n🚙 Коробка: {gearbox}"

    # Format caption using customizable template
    try:
        caption = template.format(
            brand=brand,
            model=model,
            year=year,
            vin=vin,
            url=site_url + "/",
            mileage=mileage,
            fuel=fuel,
            drive=drive,
            gearbox=gearbox,
            price=price,
            phone=phone,
            engine_info=engine_info
        )
    except Exception as err:
        print(f"Помилка форматування шаблону Telegram: {err}")
        caption = (
            f"🔥 {brand} {model} {engine_info} {year}\n"
            f"🪪 {vin}\n"
            f"🌐 Посилання на сайт з детальними характеристиками: https://vagzlomavto.onrender.com/\n\n"
            f"🚙 Пробіг: {mileage} тис. км\n"
            f"🔥 Паливо: {fuel}\n"
            f"🚙 Привід: {drive}\n"
            f"🚙 Коробка: {gearbox}\n\n"
            f"💵 Ціна: ${price}\n\n"
            f"* Ціна авто у Львові .\n"
            f"У вартість автомобіля враховані всі транспортні витрати і розмитнення!\n\n"
            f"Наші контакти :📲\n"
            f"{phone}\n\n"
            f"Хочеш схоже авто ?\n"
            f"Привеземо за найкращою ціною в Україні 🤝"
        )

    # Надсилаємо ВСІ фото: Telegram дозволяє до 10 фото в одній медіагрупі.
    # Якщо фото більше 10 — ділимо на групи, не відкидаючи решту.
    valid_paths = [path for path in photo_paths if path and path.exists()]
    if not valid_paths:
        text_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        try:
            resp = requests.post(text_url, data={"chat_id": CHANNEL_ID, "text": caption}, timeout=30)
            if not resp.ok:
                print(f"Telegram sendMessage error: {resp.status_code} {resp.text[:500]}")
        except Exception as e:
            print(f"Помилка публікації тексту в Telegram: {e}")
        return

    for batch_start in range(0, len(valid_paths), 10):
        batch = valid_paths[batch_start:batch_start + 10]
        is_first_batch = batch_start == 0
        files = {}
        try:
            if len(batch) == 1:
                # sendMediaGroup вимагає щонайменше два елементи.
                path = batch[0]
                with open(path, "rb") as photo_file:
                    data = {"chat_id": CHANNEL_ID}
                    if is_first_batch:
                        data["caption"] = caption[:1024]
                    resp = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                        data=data, files={"photo": photo_file}, timeout=90
                    )
            else:
                media = []
                for i, path in enumerate(batch):
                    file_key = f"photo{i}"
                    files[file_key] = open(path, "rb")
                    item = {"type": "photo", "media": f"attach://{file_key}"}
                    if is_first_batch and i == 0:
                        item["caption"] = caption[:1024]
                    media.append(item)
                resp = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
                    data={"chat_id": CHANNEL_ID, "media": json.dumps(media, ensure_ascii=False)},
                    files=files, timeout=120
                )

            try:
                result = resp.json()
            except Exception:
                result = {"ok": False, "description": resp.text[:500]}
            if not resp.ok or not result.get("ok"):
                print(f"Помилка Telegram API (фото {batch_start + 1}-{batch_start + len(batch)}): {result}")
                # Не продовжуємо, щоб не створювати частково дубльовані публікації після помилки.
                break
            print(f"Telegram: надіслано фото {batch_start + 1}-{batch_start + len(batch)} з {len(valid_paths)} для авто {car_id}.")
        except Exception as e:
            print(f"Помилка публікації фото в Telegram: {e}")
            break
        finally:
            for f in files.values():
                try:
                    f.close()
                except Exception:
                    pass

def schedule_new_car(car_id):
    try:
        thread = threading.Thread(target=_async_send_to_telegram, args=(car_id, 60))
        thread.daemon = True
        thread.start()
    except Exception as e:
        print(f"Помилка створення потоку: {e}")
