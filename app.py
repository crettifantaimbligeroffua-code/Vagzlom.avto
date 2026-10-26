from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import io
from pathlib import Path
import uuid
import os
import logging
import threading
import time
import requests
from social_publishing import schedule_new_car

BASE = Path(__file__).resolve().parent
# Render: set DATA_DIR=/var/data and attach a persistent disk mounted at /var/data.
# Then the SQLite database, car photos, and saved posting settings survive deploys.
DATA_DIR = Path(os.environ.get("DATA_DIR", str(BASE))).expanduser().resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "vagzlumauto.db"
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# One-time migration: when a Render disk is first attached, copy the previous
# SQLite database and locally stored uploads into persistent storage if present.
LEGACY_DB_PATH = BASE / "vagzlumauto.db"
LEGACY_UPLOAD_DIR = BASE / "static" / "uploads"
if DB_PATH != LEGACY_DB_PATH and not DB_PATH.exists() and LEGACY_DB_PATH.exists():
    import shutil
    shutil.copy2(LEGACY_DB_PATH, DB_PATH)
if UPLOAD_DIR.resolve() != LEGACY_UPLOAD_DIR.resolve() and LEGACY_UPLOAD_DIR.exists():
    import shutil
    for legacy_file in LEGACY_UPLOAD_DIR.iterdir():
        if legacy_file.is_file():
            target_file = UPLOAD_DIR / legacy_file.name
            if not target_file.exists():
                shutil.copy2(legacy_file, target_file)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
# Keep admin/editor login for 30 days so the user does not need to sign in on every visit.
from datetime import timedelta
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("RENDER", "").lower() == "true"
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024
from config import *

class PGCursor:
    def __init__(self, cursor, lastrowid=None):
        self._cursor = cursor
        self.lastrowid = lastrowid
    def fetchone(self): return self._cursor.fetchone()
    def fetchall(self): return self._cursor.fetchall()
    def __iter__(self): return iter(self._cursor)
    def __getattr__(self, name): return getattr(self._cursor, name)

class PGConnection:
    def __init__(self, raw): self.raw = raw
    def execute(self, sql, params=()):
        sql = sql.strip()
        if sql.upper().startswith("PRAGMA TABLE_INFO(CARS)"):
            cur = self.raw.cursor()
            cur.execute("SELECT ordinal_position-1 AS cid, column_name AS name, data_type AS type, 0 AS notnull, NULL AS dflt_value, 0 AS pk FROM information_schema.columns WHERE table_schema='public' AND table_name='cars' ORDER BY ordinal_position")
            return PGCursor(cur)
        normalized = sql.replace("?", "%s")
        upper = normalized.upper()
        wants_id = upper.startswith("INSERT INTO USERS") or upper.startswith("INSERT INTO CARS")
        if wants_id and "RETURNING" not in upper:
            normalized += " RETURNING id"
        cur = self.raw.cursor()
        cur.execute(normalized, params)
        lastrowid = None
        if wants_id:
            row = cur.fetchone()
            if row is not None: lastrowid = row[0]
            # Return a compatible cursor whose fetchone is empty after consuming RETURNING.
            class EmptyCursor:
                def fetchone(self): return None
                def fetchall(self): return []
                def __iter__(self): return iter(())
            return PGCursor(EmptyCursor(), lastrowid)
        return PGCursor(cur)
    def executescript(self, script):
        cur = self.raw.cursor()
        for statement in script.split(';'):
            statement = statement.strip()
            if not statement: continue
            statement = statement.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
            statement = statement.replace('INTEGER PRIMARY KEY', 'SERIAL PRIMARY KEY')
            statement = statement.replace('REAL', 'DOUBLE PRECISION')
            cur.execute(statement)
        return PGCursor(cur)
    def commit(self): self.raw.commit()
    def rollback(self): self.raw.rollback()
    def close(self): self.raw.close()

def db():
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import DictCursor
        raw = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor, sslmode="require")
        return PGConnection(raw)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    if DATABASE_URL:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS cars (id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT NOT NULL, model TEXT NOT NULL, year INTEGER, price REAL, mileage INTEGER, power INTEGER, fuel TEXT, gearbox TEXT, body TEXT, color TEXT, engine TEXT, drive TEXT, phone TEXT, description TEXT, vin TEXT, owner_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS car_photos (id INTEGER PRIMARY KEY AUTOINCREMENT, car_id INTEGER NOT NULL, filename TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS uploaded_files (filename TEXT PRIMARY KEY, data BYTEA NOT NULL, mime TEXT NOT NULL);
        """)
    else:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS cars (id INTEGER PRIMARY KEY AUTOINCREMENT, brand TEXT NOT NULL, model TEXT NOT NULL, year INTEGER, price REAL, mileage INTEGER, power INTEGER, fuel TEXT, gearbox TEXT, body TEXT, color TEXT, engine TEXT, drive TEXT, phone TEXT, description TEXT, vin TEXT, owner_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS car_photos (id INTEGER PRIMARY KEY AUTOINCREMENT, car_id INTEGER NOT NULL, filename TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS uploaded_files (filename TEXT PRIMARY KEY, data BLOB NOT NULL, mime TEXT NOT NULL);
        """)
    existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(cars)").fetchall()}
    for field in DETAIL_FIELDS:
        key = field["key"]
        if key not in existing_cols:
            conn.execute(f"ALTER TABLE cars ADD COLUMN {key} TEXT")
    admin_email = os.environ.get("ADMIN_EMAIL", ADMIN_DEFAULT_EMAIL)
    admin_password = os.environ.get("ADMIN_PASSWORD", ADMIN_DEFAULT_PASSWORD)
    existing = conn.execute("SELECT id FROM users WHERE email=?", (admin_email,)).fetchone()
    if not existing:
        conn.execute("INSERT INTO users(email,password_hash,role) VALUES(?,?,?)", (admin_email, generate_password_hash(admin_password), "admin"))
    conn.commit()
    conn.close()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    conn = db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return user

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

def save_upload(file):
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        raise ValueError("Дозволені JPG, JPEG, PNG та WEBP.")
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    raw = file.read()
    mime = file.mimetype or ("image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg")
    conn = db()
    try:
        if DATABASE_URL:
            conn.execute("INSERT INTO uploaded_files(filename,data,mime) VALUES(?,?,?)", (filename, raw, mime))
        else:
            conn.execute("INSERT OR REPLACE INTO uploaded_files(filename,data,mime) VALUES(?,?,?)", (filename, raw, mime))
        conn.commit()
    finally:
        conn.close()
    # Keep local fallback copy for older data and development.
    (UPLOAD_DIR / filename).write_bytes(raw)
    return filename

def require_role(*roles):
    user = current_user()
    if not user or user["role"] not in roles:
        abort(403)
    return user

@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "roles": ROLES, "site": SITE, "phones": PHONES, "ui": TEXT, "nav": NAV, "detail_field_map": DETAIL_FIELD_MAP, "quick_picker": QUICK_PICKER, "main_fields": MAIN_FIELDS, "detail_fields": DETAIL_FIELDS, "max_photos": MAX_PHOTOS}

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    # New photos are stored in the persistent database so Render restarts do not remove them.
    conn = db()
    try:
        row = conn.execute("SELECT data,mime FROM uploaded_files WHERE filename=?", (filename,)).fetchone()
        if row:
            data = row["data"]
            if isinstance(data, memoryview): data = data.tobytes()
            return send_file(io.BytesIO(data), mimetype=row["mime"], download_name=filename, max_age=86400)
    except Exception:
        app.logger.exception("Could not load photo blob from database")
    finally:
        conn.close()
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/")
def home():
    brand = request.args.get("brand", "").strip()
    model = request.args.get("model", "").strip()
    conn = db()
    params = []
    if brand or model:
        sql = """SELECT c.*, (SELECT filename FROM car_photos p WHERE p.car_id=c.id ORDER BY p.id LIMIT 1) AS photo
                 FROM cars c WHERE 1=1"""
        legacy_brand = next((k for k, v in LEGACY_MODEL_BRANDS.items() if v and v.lower() == model.lower()), None) if model else None
        if brand:
            if legacy_brand:
                sql += " AND (LOWER(c.brand)=LOWER(?) OR LOWER(c.brand)=LOWER(?))"
                params.extend([brand, legacy_brand])
            else:
                sql += " AND LOWER(c.brand)=LOWER(?)"
                params.append(brand)
        if model:
            model_condition = "(LOWER(c.model)=LOWER(?) OR LOWER(c.model) LIKE LOWER(?))"
            params.extend([model, model + " %"])
            if legacy_brand and not brand:
                model_condition = f"({model_condition} OR LOWER(c.brand)=LOWER(?))"
                params.append(legacy_brand)
            sql += " AND " + model_condition
        sql += " ORDER BY c.id DESC"
        cars = conn.execute(sql, params).fetchall()
    else:
        cars = conn.execute("""
            SELECT c.*, (SELECT filename FROM car_photos p WHERE p.car_id=c.id ORDER BY p.id LIMIT 1) AS photo
            FROM cars c ORDER BY c.id DESC LIMIT 8
        """).fetchall()
    conn.close()
    return render_template("home.html", cars=cars, selected_brand=brand, selected_model=model,
                           is_filtered=bool(brand or model))

@app.route("/cars")
def cars():
    brand = request.args.get("brand", "").strip()
    model = request.args.get("model", "").strip()
    conn = db()
    sql = """SELECT c.*, (SELECT filename FROM car_photos p WHERE p.car_id=c.id ORDER BY p.id LIMIT 1) AS photo
             FROM cars c WHERE 1=1"""
    params = []
    if brand:
        sql += " AND LOWER(c.brand)=LOWER(?)"
        params.append(brand)
    if model:
        sql += " AND (LOWER(c.model)=LOWER(?) OR LOWER(c.model) LIKE LOWER(?))"
        params.extend([model, model + " %"])
    sql += " ORDER BY c.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template("cars.html", cars=rows, brands=CAR_BRANDS, models=CAR_MODELS,
                           selected_brand=brand, selected_model=model)

@app.route("/cars/<int:car_id>")
def car_detail(car_id):
    conn = db()
    car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    photos = conn.execute("SELECT * FROM car_photos WHERE car_id=? ORDER BY id", (car_id,)).fetchall()
    conn.close()
    if not car:
        abort(404)
    return render_template("car_detail.html", car=car, photos=photos, detail_groups=DETAIL_GROUPS)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or len(password) < 6:
            flash("Вкажіть email та пароль мінімум із 6 символів.", "error")
            return redirect(url_for("register"))
        conn = db()
        try:
            cur = conn.execute(
                "INSERT INTO users(email,password_hash,role) VALUES(?,?,?)",
                (email, generate_password_hash(password), "user")
            )
            conn.commit()
            session["user_id"] = cur.lastrowid
            flash("Реєстрація успішна. Зараз у вас звичайні права користувача.", "success")
            return redirect(url_for("home"))
        except (sqlite3.IntegrityError,):
            flash("Такий email уже зареєстрований.", "error")
        finally:
            conn.close()
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session.permanent = True
            session["user_id"] = user["id"]
            flash("Ви увійшли на сайт.", "success")
            return redirect(url_for("home"))
        flash("Невірний email або пароль.", "error")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin/users")
def admin_users():
    require_role("admin")
    conn = db()
    users = conn.execute("SELECT id,email,role,created_at FROM users ORDER BY id").fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)

@app.route("/admin/users/<int:user_id>/role", methods=["POST"])
def change_role(user_id):
    require_role("admin")
    role = request.form.get("role")
    if role not in ROLES:
        abort(400)
    conn = db()
    conn.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    conn.commit()
    conn.close()
    flash("Права користувача змінено.", "success")
    return redirect(url_for("admin_users"))

@app.route("/admin/cars/new", methods=["GET", "POST"])
def add_car():
    user = require_role("editor", "admin")
    defaults = {"brand":"", "model":"", "year":"", "price":"", "mileage":"", "power":"",
                "fuel":"", "gearbox":"", "body":"", "color":"", "engine":"", "drive":"",
                "phone":"", "description":"", "vin":""}
    defaults.update({field["key"]: "" for field in DETAIL_FIELDS})
    detail_values = {field["key"]: "" for field in DETAIL_FIELDS}

    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in defaults}
        if not fields["brand"] or not fields["model"]:
            flash("Марка та модель є обов'язковими.", "error")
            return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                                   fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                                   drive_options=DRIVE, existing_cars=get_existing_cars(), detail_values={k: fields.get(k, "") for k in DETAIL_FIELD_MAP})
        conn = db()
        cur = conn.execute("""
            INSERT INTO cars(brand,model,year,price,mileage,power,fuel,gearbox,body,color,engine,drive,phone,description,vin,owner_id,
            generation,trim,modification,eco_standard,condition,fuel_consumption,safety,air_conditioner,comfort,optics,multimedia,interior_body,headlights,parking,airbags)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, tuple(fields[k] if k not in {"owner_id"} else fields[k] for k in []) +
             (fields["brand"], fields["model"], fields["year"] or None, fields["price"] or None, fields["mileage"] or None,
              fields["power"] or None, fields["fuel"], fields["gearbox"], fields["body"], fields["color"], fields["engine"],
              fields["drive"], fields["phone"], fields["description"], fields["vin"], user["id"],
              *(fields[f["key"]] for f in DETAIL_FIELDS)))
        car_id = cur.lastrowid
        photo_files = [f for f in request.files.getlist("photos") if f and f.filename]
        if len(photo_files) > MAX_PHOTOS:
            conn.rollback(); conn.close()
            flash(f"Можна додати максимум {MAX_PHOTOS} фото до одного авто.", "error")
            return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                                   fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                                   drive_options=DRIVE, existing_cars=get_existing_cars(), detail_values={k: fields.get(k, "") for k in DETAIL_FIELD_MAP})
        saved_files = []
        try:
            for f in photo_files:
                filename = save_upload(f)
                if filename:
                    saved_files.append(filename)
                    conn.execute("INSERT INTO car_photos(car_id,filename) VALUES(?,?)", (car_id, filename))
        except ValueError as exc:
            conn.rollback()
            for filename in saved_files: (UPLOAD_DIR / filename).unlink(missing_ok=True)
            conn.close()
            flash(str(exc), "error")
            return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                                   fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                                   drive_options=DRIVE, existing_cars=get_existing_cars(), detail_values={k: fields.get(k, "") for k in DETAIL_FIELD_MAP})
        conn.commit(); conn.close()
        # Auto-publish this new listing after 30 seconds; credentials are configured as environment variables.
        schedule_new_car(car_id)
        flash("Автомобіль додано.", "success")
        return redirect(url_for("add_car"))

    return render_template("car_form.html", **defaults, brands=CAR_BRANDS, models=CAR_MODELS,
                           fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                           drive_options=DRIVE, existing_cars=get_existing_cars(), detail_values=detail_values)


@app.route("/admin/cars/<int:car_id>/edit", methods=["GET", "POST"])
def edit_car(car_id):
    user = require_role("editor", "admin")
    conn = db()
    car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    photos = conn.execute("SELECT * FROM car_photos WHERE car_id=? ORDER BY id", (car_id,)).fetchall()
    conn.close()
    if not car:
        abort(404)

    fields = {key: (car[key] if key in car.keys() else "") for key in [
        "brand", "model", "year", "price", "mileage", "power", "fuel", "gearbox", "body", "color", "engine", "drive",
        "phone", "description", "vin", *(f["key"] for f in DETAIL_FIELDS)
    ]}
    detail_values = {f["key"]: fields.get(f["key"], "") for f in DETAIL_FIELDS}

    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in fields}
        detail_values = {f["key"]: fields.get(f["key"], "") for f in DETAIL_FIELDS}
        if not fields["brand"] or not fields["model"]:
            flash("Марка та модель є обов'язковими.", "error")
        else:
            conn = db()
            conn.execute("""
                UPDATE cars SET brand=?,model=?,year=?,price=?,mileage=?,power=?,fuel=?,gearbox=?,body=?,color=?,engine=?,drive=?,phone=?,description=?,vin=?,
                generation=?,trim=?,modification=?,eco_standard=?,condition=?,fuel_consumption=?,safety=?,air_conditioner=?,comfort=?,optics=?,multimedia=?,interior_body=?,headlights=?,parking=?,airbags=?
                WHERE id=?
            """, (
                fields["brand"], fields["model"], fields["year"] or None, fields["price"] or None, fields["mileage"] or None,
                fields["power"] or None, fields["fuel"], fields["gearbox"], fields["body"], fields["color"], fields["engine"],
                fields["drive"], fields["phone"], fields["description"], fields["vin"], *(fields[f["key"]] for f in DETAIL_FIELDS), car_id
            ))
            photo_files = [f for f in request.files.getlist("photos") if f and f.filename]
            current_count = conn.execute("SELECT COUNT(*) FROM car_photos WHERE car_id=?", (car_id,)).fetchone()[0]
            if current_count + len(photo_files) > MAX_PHOTOS:
                conn.rollback(); conn.close()
                flash(f"Можна мати максимум {MAX_PHOTOS} фото до одного авто.", "error")
                return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                    fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY, drive_options=DRIVE,
                    existing_cars=get_existing_cars(), detail_values=detail_values, edit_mode=True, edit_car_id=car_id, edit_photos=photos)
            saved_files = []
            try:
                for f in photo_files:
                    filename = save_upload(f)
                    if filename:
                        saved_files.append(filename)
                        conn.execute("INSERT INTO car_photos(car_id,filename) VALUES(?,?)", (car_id, filename))
            except ValueError as exc:
                conn.rollback()
                for filename in saved_files: (UPLOAD_DIR / filename).unlink(missing_ok=True)
                conn.close()
                flash(str(exc), "error")
                return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                    fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY, drive_options=DRIVE,
                    existing_cars=get_existing_cars(), detail_values=detail_values, edit_mode=True, edit_car_id=car_id, edit_photos=photos)
            conn.commit()
            conn.close()
            flash("Автомобіль оновлено.", "success")
            return redirect(url_for("edit_car", car_id=car_id))

    return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
        fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY, drive_options=DRIVE,
        existing_cars=get_existing_cars(), detail_values=detail_values, edit_mode=True, edit_car_id=car_id, edit_photos=photos)

@app.route("/admin/cars/<int:car_id>/photos/<int:photo_id>/delete", methods=["POST"])
def delete_car_photo(car_id, photo_id):
    require_role("editor", "admin")
    conn = db()
    photo = conn.execute("SELECT filename FROM car_photos WHERE id=? AND car_id=?", (photo_id, car_id)).fetchone()
    if not photo:
        conn.close()
        abort(404)
    conn.execute("DELETE FROM car_photos WHERE id=? AND car_id=?", (photo_id, car_id))
    conn.commit()
    conn.close()
    try:
        (UPLOAD_DIR / photo["filename"]).unlink(missing_ok=True)
    except OSError:
        pass
    flash("Фото видалено.", "success")
    return redirect(url_for("edit_car", car_id=car_id))

def get_existing_cars():
    conn = db()
    rows = conn.execute("""SELECT c.*, (SELECT filename FROM car_photos p WHERE p.car_id=c.id ORDER BY p.id LIMIT 1) AS photo,
                          (SELECT COUNT(*) FROM car_photos p WHERE p.car_id=c.id) AS photo_count
                          FROM cars c ORDER BY c.id DESC""").fetchall()
    conn.close()
    return rows

@app.route("/admin/cars/<int:car_id>/delete", methods=["POST"])
def delete_car(car_id):
    require_role("editor", "admin")
    conn = db()
    photos = conn.execute("SELECT filename FROM car_photos WHERE car_id=?", (car_id,)).fetchall()
    conn.execute("DELETE FROM car_photos WHERE car_id=?", (car_id,))
    conn.execute("DELETE FROM cars WHERE id=?", (car_id,))
    conn.commit()
    conn.close()
    for p in photos:
        try:
            (UPLOAD_DIR / p["filename"]).unlink(missing_ok=True)
        except OSError:
            pass
    flash("Оголошення видалено.", "success")
    return redirect(url_for("cars"))

@app.route("/parts")
def parts():
    return render_template("contact_service.html", page="Запчастини", icon="🔧", color="orange",
                           text="У нас є запчастини з розборки та нові деталі для GOLF, JETTA, NISSAN, PASSAT, RENAULT і TOURAN.")

@app.route("/repair")
def repair():
    return render_template("repair.html", services=SERVICES)

@app.route("/wheels")
def wheels():
    return render_template("contact_service.html", page="Колеса та диски", icon="◉", color="blue",
                           text="Б/у колеса, диски та титани. Підберемо комплект під ваш автомобіль.")

@app.route("/additional")
def additional():
    return render_template("additional.html", services=ADDITIONAL_SERVICES)

@app.route("/additional/<slug>")
def additional_detail(slug):
    service = next((item for item in ADDITIONAL_SERVICES if item["slug"] == slug), None)
    if not service:
        abort(404)
    return render_template("additional_detail.html", service=service)

@app.route("/admin")
def admin():
    require_role("admin")
    conn = db()
    users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    cars_count = conn.execute("SELECT COUNT(*) FROM cars").fetchone()[0]
    editors_count = conn.execute("SELECT COUNT(*) FROM users WHERE role='editor'").fetchone()[0]
    conn.close()
    return render_template("admin.html", users_count=users_count, cars_count=cars_count, editors_count=editors_count)


@app.route("/admin/telegram", methods=["GET", "POST"])
def admin_telegram():
    if not current_user() or current_user()["role"] not in ["editor", "admin"]:
        flash("У вас немає доступу до цієї сторінки.", "error")
        return redirect(url_for("login"))
    
    conn = db()
    if request.method == "POST":
        template_text = request.form.get("telegram_template", "")
        conn.execute("INSERT INTO settings (key, value) VALUES ('telegram_template', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (template_text,))
        conn.commit()
        conn.close()
        flash("Шаблон для Telegram автопостингу успішно збережено!", "success")
        return redirect(url_for("admin_telegram"))

    row = conn.execute("SELECT value FROM settings WHERE key='telegram_template'").fetchone()
    conn.close()
    
    default_tmpl = """🔥 {brand} {model} {engine_info} {year}
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

    current_tmpl = row["value"] if row and row["value"] else default_tmpl
    return render_template("admin_telegram.html", template_text=current_tmpl)


@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

init_db()

# Lightweight self-ping bot: requests the public site every 5 minutes by default.
# Set SITE_URL (or rely on Render's RENDER_EXTERNAL_URL) to the public base URL.
# This is a best-effort keep-awake helper, not a substitute for persistent storage
# and not a guarantee against Render free-tier sleep/restarts.
@app.route("/healthz")
def healthz():
    return {"status": "ok"}, 200

def _start_self_ping_bot():
    site_url = (os.environ.get("SITE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
    if not site_url:
        app.logger.warning("Self-ping bot is not configured: set SITE_URL or RENDER_EXTERNAL_URL")
        return
    try:
        interval_minutes = float(os.environ.get("SELF_PING_INTERVAL_MINUTES", "5"))
    except (TypeError, ValueError):
        interval_minutes = 5.0
    interval_minutes = min(10.0, max(5.0, interval_minutes))
    ping_url = site_url + "/healthz"

    def _loop():
        # First ping after the interval to avoid delaying startup.
        while True:
            time.sleep(interval_minutes * 60)
            try:
                response = requests.get(ping_url, timeout=20)
                app.logger.info("Self-ping bot: GET %s -> %s", ping_url, response.status_code)
            except requests.RequestException as exc:
                app.logger.warning("Self-ping bot request failed: %s", exc)

    thread = threading.Thread(target=_loop, name="site-self-ping", daemon=True)
    thread.start()
    app.logger.info("Self-ping bot started; interval=%.1f minutes; URL=%s", interval_minutes, ping_url)

_start_self_ping_bot()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        debug=False,
        use_reloader=False,
        threaded=True
    )
