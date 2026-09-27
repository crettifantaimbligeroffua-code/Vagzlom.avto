from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from pathlib import Path
import config
import uuid
import os

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "vagzlumauto.db"
UPLOAD_DIR = BASE / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024 * 1024
MAX_PHOTOS = 100

DETAIL_FIELDS = [
    "generation", "trim", "modification", "eco_standard", "condition", "fuel_consumption",
    "safety", "air_conditioner", "comfort", "optics", "multimedia", "interior_body",
    "headlights", "parking", "airbags"
]

ALLOWED = {"jpg", "jpeg", "png", "webp"}
CAR_BRANDS = ["Volkswagen", "GOLF", "JETTA", "NISAN", "PASSAT", "RENAULT", "TOURAN", "FORD", "DACIA"]
CAR_MODELS = {
    "GOLF": [
        "Golf 1.0 TSI", "Golf 1.2 TSI", "Golf 1.4 TSI", "Golf 1.5 TSI", "Golf 1.5 eTSI",
        "Golf 1.6", "Golf 1.6 TDI", "Golf 2.0", "Golf 2.0 TDI", "Golf 2.0 TSI",
        "Golf 2.0 GTI", "Golf R", "Golf GTE"
    ],
    "JETTA": [
        "Jetta 1.4 TSI", "Jetta 1.6", "Jetta 1.8 TSI", "Jetta 2.0", "Jetta 2.0 TDI", "Jetta GLI"
    ],
    "NISAN": [
        "Almera", "Juke", "Micra", "Navara", "Note", "Qashqai", "X-Trail", "Leaf", "Murano", "Pathfinder", "Primera", "Tiida"
    ],
    "PASSAT": [
        "Passat 1.4 TSI", "Passat 1.5 TSI", "Passat 1.8 TSI", "Passat 2.0 TSI", "Passat 2.0 TDI", "Passat 2.0 BiTDI", "Passat GTE"
    ],
    "RENAULT": [
        "Clio", "Megane", "Laguna", "Scenic", "Espace", "Talisman", "Captur", "Kadjar", "Koleos", "Austral", "Arkana", "Kangoo", "Trafic", "Master", "Zoe"
    ],
    "TOURAN": [
        "Touran 1.2 TSI", "Touran 1.4 TSI", "Touran 1.6 TDI", "Touran 2.0 TDI"
    ],
    "DACIA": [
        "Logan", "Sandero", "Sandero Stepway", "Duster", "Jogger", "Spring",
        "Lodgy", "Dokker", "Dokker Van", "Logan MCV", "Logan Pick-Up",
        "Solenza", "1310", "Bigster"
    ],
    "FORD": [
        "Fiesta", "Focus", "Mondeo", "Fusion", "Taurus", "Mustang", "Puma", "Kuga",
        "Edge", "Explorer", "Escape", "Bronco", "Bronco Sport", "Expedition",
        "EcoSport", "Ecosport", "Maverick", "Ranger", "F-150", "F-250", "F-350",
        "Transit", "Transit Custom", "Transit Connect", "Transit Courier", "Tourneo Connect",
        "Tourneo Custom", "Galaxy", "S-Max", "C-Max", "Grand C-Max", "B-Max", "Ka",
        "Ka+", "Courier", "Crown Victoria", "GT", "GT40", "Probe", "Capri", "Escort",
        "Sierra", "Scorpio", "Granada", "Orion", "Puma ST", "Focus ST", "Focus RS",
        "Fiesta ST", "Mustang Mach-E"
    ],
}

FUEL = ["Бензин", "Дизель", "Гібрид", "Електро"]
GEARBOX = ["Механіка", "Автомат", "DSG", "Варіатор"]
BODY = ["Хетчбек", "Седан", "Універсал", "Купе", "Кабріолет", "Ліфтбек", "Фастбек", "Тарга", "Родстер", "Кросовер", "Позашляховик", "Мінівен", "Мікроавтобус", "Фургон", "Пікап", "Універсал/фургон"]
DRIVE = ["Передній", "Задній", "Повний"]
ROLES = {"user": "Користувач", "editor": "Редактор", "admin": "Адміністратор"}
# Центральні налаштування з config.py.
# Старі константи вище залишені як сумісність зі старими базами.
if hasattr(config, "CAR_MODELS"):
    CAR_MODELS = config.CAR_MODELS
    CAR_BRANDS = getattr(config, "CAR_BRANDS", list(CAR_MODELS.keys()))
if hasattr(config, "FUEL"):
    FUEL = config.FUEL
if hasattr(config, "GEARBOX"):
    GEARBOX = config.GEARBOX
if hasattr(config, "BODY"):
    BODY = config.BODY
if hasattr(config, "DRIVE"):
    DRIVE = config.DRIVE
if hasattr(config, "DETAIL_FIELDS"):
    DETAIL_FIELDS = [field["key"] for field in config.DETAIL_FIELDS]


ADDITIONAL_SERVICES = [
    {
        "slug": "shinomontazh",
        "name": "Шиномонтаж",
        "icon": "◉",
        "description": "Монтаж та демонтаж шин, балансування коліс, перевірка тиску та підготовка автомобіля до сезону.",
    },
    {
        "slug": "himchistka",
        "name": "Хімчистка",
        "icon": "✦",
        "description": "Професійна хімчистка салону автомобіля: сидіння, стеля, підлога, пластик та важкодоступні місця.",
    },
    {
        "slug": "myika-avto",
        "name": "Мийка авто",
        "icon": "✧",
        "description": "Комплексна мийка автомобіля з очищенням кузова, скла та коліс. Доступні різні варіанти миття.",
    },
    {
        "slug": "detailing",
        "name": "Детейлінг",
        "icon": "◆",
        "description": "Детейлінг кузова та салону: глибоке очищення, відновлення зовнішнього вигляду та захист поверхонь.",
    },
    {
        "slug": "computer-diagnostics",
        "name": "Компʼютерна діагностика",
        "icon": "⚡",
        "description": "Компʼютерна перевірка електронних блоків автомобіля, зчитування помилок та діагностика несправностей.",
    },
    {
        "slug": "prygon-avto",
        "name": "Пригон авто",
        "icon": "➜",
        "description": "Допоможемо підібрати та пригнати автомобіль під ваш бюджет і побажання, перевіримо варіанти перед купівлею.",
    },
]

SERVICES = [
    ("Заміна масла та фільтрів", "Регулярне ТО та заміна витратних матеріалів.", "від 800 грн"),
    ("Діагностика двигуна", "Комп'ютерна та механічна діагностика.", "від 500 грн"),
    ("Ремонт гальмівної системи", "Колодки, диски, супорти та гальмівна рідина.", "від 1 500 грн"),
    ("Ремонт підвіски", "Діагностика та заміна елементів ходової.", "від 2 000 грн"),
    ("Ремонт та заміна двигуна", "Ремонтні роботи та заміна агрегатів.", "від 15 000 грн"),
    ("Ремонт коробки передач", "Механічні та автоматичні КПП.", "від 8 000 грн"),
    ("Електрика та діагностика", "Пошук і усунення електричних несправностей.", "від 600 грн"),
    ("Ремонт кондиціонера", "Заправка, діагностика та ремонт системи.", "від 600 грн"),
    ("Ремонт вихлопної системи", "Глушник, каталізатор та інші елементи.", "від 2 500 грн"),
    ("Комп'ютерна діагностика", "Повна перевірка електронних блоків автомобіля.", "від 400 грн"),
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER,
        price REAL,
        mileage INTEGER,
        power INTEGER,
        fuel TEXT,
        gearbox TEXT,
        body TEXT,
        color TEXT,
        engine TEXT,
        drive TEXT,
        phone TEXT,
        description TEXT,
        vin TEXT,
        owner_id INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS car_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER NOT NULL,
        filename TEXT NOT NULL
    );
    """)
    # Додаємо детальні характеристики до вже існуючих баз без втрати даних.
    existing_cols = {r[1] for r in conn.execute("PRAGMA table_info(cars)").fetchall()}
    for field in DETAIL_FIELDS:
        if field not in existing_cols:
            conn.execute(f"ALTER TABLE cars ADD COLUMN {field} TEXT")
    admin_email = os.environ.get("ADMIN_EMAIL", getattr(config, "ADMIN_DEFAULT_EMAIL", "admin@vagzlumauto.local"))
    admin_password = os.environ.get("ADMIN_PASSWORD", getattr(config, "ADMIN_DEFAULT_PASSWORD", "Admin123!"))
    existing = conn.execute("SELECT id FROM users WHERE email=?", (admin_email,)).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users(email,password_hash,role) VALUES(?,?,?)",
            (admin_email, generate_password_hash(admin_password), "admin")
        )
    else:
        # У виданій версії архіву цей обліковий запис гарантовано має вказані нижче
        # стартові дані для входу в адмінпанель. Змінити їх можна через змінні середовища.
        conn.execute(
            "UPDATE users SET password_hash=?, role='admin' WHERE id=?",
            (generate_password_hash(admin_password), existing[0])
        )
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
    file.save(UPLOAD_DIR / filename)
    return filename

def require_role(*roles):
    user = current_user()
    if not user or user["role"] not in roles:
        abort(403)
    return user

@app.context_processor
def inject_globals():
    # SITE читається з config.py на кожен HTTP-запит.
    # Тому після збереження config.py достатньо оновити сторінку.
    return {"current_user": current_user(), "roles": ROLES, "site": config.SITE, "text": getattr(config, "TEXT", {}), "picker": getattr(config, "PICKER", {}), "config_nav": getattr(config, "NAV", []), "config_phones": getattr(config, "PHONES", [])}

@app.route("/")
def home():
    conn = db()
    cars = conn.execute("""
        SELECT c.*, (SELECT filename FROM car_photos p WHERE p.car_id=c.id ORDER BY p.id LIMIT 1) AS photo
        FROM cars c ORDER BY c.id DESC LIMIT 8
    """).fetchall()
    conn.close()
    return render_template("home.html", cars=cars)

@app.route("/cars")
def cars():
    brand = request.args.get("brand", "")
    model = request.args.get("model", "")
    conn = db()
    sql = """SELECT c.*, (SELECT filename FROM car_photos p WHERE p.car_id=c.id ORDER BY p.id LIMIT 1) AS photo
             FROM cars c WHERE 1=1"""
    params = []
    if brand:
        sql += " AND LOWER(c.brand)=LOWER(?)"
        params.append(brand)
    if model:
        sql += " AND LOWER(c.model) LIKE LOWER(?)"
        params.append(model.rstrip() + "%")
    sql += " ORDER BY c.id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return render_template("cars.html", cars=rows, brands=CAR_BRANDS, models=CAR_MODELS, selected_brand=brand, selected_model=model)

@app.route("/cars/<int:car_id>")
def car_detail(car_id):
    conn = db()
    car = conn.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    photos = conn.execute("SELECT * FROM car_photos WHERE car_id=? ORDER BY id", (car_id,)).fetchall()
    conn.close()
    if not car:
        abort(404)
    return render_template("car_detail.html", car=car, photos=photos)

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
        except sqlite3.IntegrityError:
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
    defaults.update({field: "" for field in DETAIL_FIELDS})

    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in defaults}
        if not fields["brand"] or not fields["model"]:
            flash("Марка та модель є обов'язковими.", "error")
            return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                                   fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                                   drive_options=DRIVE, existing_cars=get_existing_cars())
        conn = db()
        cur = conn.execute("""
            INSERT INTO cars(brand,model,year,price,mileage,power,fuel,gearbox,body,color,engine,drive,phone,description,vin,owner_id,
            generation,trim,modification,eco_standard,condition,fuel_consumption,safety,air_conditioner,comfort,optics,multimedia,interior_body,headlights,parking,airbags)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, tuple(fields[k] if k not in {"owner_id"} else fields[k] for k in []) +
             (fields["brand"], fields["model"], fields["year"] or None, fields["price"] or None, fields["mileage"] or None,
              fields["power"] or None, fields["fuel"], fields["gearbox"], fields["body"], fields["color"], fields["engine"],
              fields["drive"], fields["phone"], fields["description"], fields["vin"], user["id"],
              *(fields[f] for f in DETAIL_FIELDS)))
        car_id = cur.lastrowid
        photo_files = [f for f in request.files.getlist("photos") if f and f.filename]
        if len(photo_files) > MAX_PHOTOS:
            conn.rollback(); conn.close()
            flash(f"Можна додати максимум {MAX_PHOTOS} фото до одного авто.", "error")
            return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                                   fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                                   drive_options=DRIVE, existing_cars=get_existing_cars())
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
                                   drive_options=DRIVE, existing_cars=get_existing_cars())
        conn.commit(); conn.close()
        flash("Автомобіль додано.", "success")
        return redirect(url_for("add_car"))

    return render_template("car_form.html", **defaults, brands=CAR_BRANDS, models=CAR_MODELS,
                           fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY,
                           drive_options=DRIVE, existing_cars=get_existing_cars())


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
        "phone", "description", "vin", *DETAIL_FIELDS
    ]}

    if request.method == "POST":
        fields = {key: request.form.get(key, "").strip() for key in fields}
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
                fields["drive"], fields["phone"], fields["description"], fields["vin"], *(fields[f] for f in DETAIL_FIELDS), car_id
            ))
            photo_files = [f for f in request.files.getlist("photos") if f and f.filename]
            current_count = conn.execute("SELECT COUNT(*) FROM car_photos WHERE car_id=?", (car_id,)).fetchone()[0]
            if current_count + len(photo_files) > MAX_PHOTOS:
                conn.rollback(); conn.close()
                flash(f"Можна мати максимум {MAX_PHOTOS} фото до одного авто.", "error")
                return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
                    fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY, drive_options=DRIVE,
                    existing_cars=get_existing_cars(), edit_mode=True, edit_car_id=car_id, edit_photos=photos)
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
                    existing_cars=get_existing_cars(), edit_mode=True, edit_car_id=car_id, edit_photos=photos)
            conn.commit()
            conn.close()
            flash("Автомобіль оновлено.", "success")
            return redirect(url_for("edit_car", car_id=car_id))

    return render_template("car_form.html", **fields, brands=CAR_BRANDS, models=CAR_MODELS,
        fuel_options=FUEL, gearbox_options=GEARBOX, body_options=BODY, drive_options=DRIVE,
        existing_cars=get_existing_cars(), edit_mode=True, edit_car_id=car_id, edit_photos=photos)

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
    return render_template("parts.html")

@app.route("/repair")
def repair():
    return render_template("repair.html", services=SERVICES)

@app.route("/wheels")
def wheels():
    return render_template("wheels.html")

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

init_db()


def _show_lan_address():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = socket.gethostbyname(socket.gethostname())
    print("\n" + "="*55)
    print("VagZlumAuto запущено для локальної мережі")
    print(f"На ПК:      http://127.0.0.1:8000")
    print(f"На телефоні: http://{ip}:8000")
    print("ПК і телефон повинні бути в ОДНІЙ Wi-Fi мережі.")
    print("="*55 + "\n")

if __name__ == "__main__":
    _show_lan_address()
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        use_reloader=False,
        threaded=True
    )