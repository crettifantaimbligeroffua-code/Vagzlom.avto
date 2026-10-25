# ============================================================
# VagZlumAuto — ВСІ НАЛАШТУВАННЯ САЙТУ В ОДНОМУ ФАЙЛІ
#
# Тут можна змінювати тексти, контакти, марки, моделі, поля
# форми, кузови, паливо, послуги, меню та зовнішні написи.
# Після змін збережи файл і перезапусти app.py.
# ============================================================

SITE = {
    "name": "Vazlom.avto",
    "title": "АвтоПригон Сокаль",
    "city": "Сокаль",
    "region": "Львівська область",
    "address": "м. Сокаль, вул. Татаркавська",
    "working_hours": "Пн–Сб: 09:00–18:00",
    "working_hours_note": "Неділя — за домовленістю",
    "footer": "АвтоПригонСокаль<br>тел. +380 99 956 5333<br>м.Сокаль, вул Тартаківська 58<br>Запитання? vagzlom.avto@gmail.com<br>Vagzlom.avto<br>Сервісний ремонт та обслуговування",
    "hero_badge": "Авто, запчастини, ремонт та колеса у Сокалі",
    "hero_title": "АвтоПригон Сокаль",
    "hero_text": "Продаж вживаних авто з Європи: Volkswagen Touran, Golf, Passat та інші.",
    "hero_middle": "Розбірка Volkswagen, Touran, Jetta, Passat.",
    "hero_subtext": "Сервіс, ремонт, б/у запчастини та б/у колеса.",
    "currency_symbol": "$",
    "currency_name": "доларів США",
    "currency_position": "after",  # before / after
}

# ------------------------------------------------------------
# КОНТАКТИ — ці номери використовуються всіма кнопками дзвінка
# ------------------------------------------------------------
PHONES = [
    {"display": "+380 63 956 5333", "digits": "380639565333"},
    {"display": "+380 99 956 5333", "digits": "380999565333"},
    {"display": "+380 98 956 5333", "digits": "380989565333"},
]

# ------------------------------------------------------------
# МЕНЮ
# key = внутрішній маршрут, name = напис у меню
# ------------------------------------------------------------
NAV = [
    {"key": "home", "name": "Головна", "endpoint": "home"},
    {"key": "cars", "name": "Підібрати авто", "endpoint": "cars"},
    {"key": "parts", "name": "Запчастини", "endpoint": "parts"},
    {"key": "repair", "name": "Ремонт", "endpoint": "repair"},
    {"key": "wheels", "name": "Колеса", "endpoint": "wheels"},
    {"key": "additional", "name": "Додатково", "endpoint": "additional"},
    {"key": "add_car", "name": "Додати", "endpoint": "add_car", "roles": ["editor", "admin"]},
    {"key": "admin_users", "name": "Користувачі", "endpoint": "admin_users", "roles": ["admin"]},
    {"key": "admin_telegram", "name": "Шаблон поста", "endpoint": "admin_telegram", "roles": ["admin"]},
]

# ------------------------------------------------------------
# МАРКИ ТА ВСІ МОДЕЛІ
# Додавай нову марку одним ключем і список її моделей нижче.
# ------------------------------------------------------------
CAR_MODELS = {
    "Volkswagen": [
        "Amarok", "Arteon", "Atlas", "Beetle", "Bora", "Caddy", "CC", "Crafter", "Eos", "Fox", "Golf", "Golf 1.0 TSI", "Golf 1.2 TSI", "Golf 1.4 TSI", "Golf 1.5 TSI", "Golf 1.6", "Golf 1.6 TDI", "Golf 1.8 TSI", "Golf 1.9 TDI", "Golf 2.0", "Golf 2.0 TDI", "Golf 2.0 TSI", "Golf GTI", "Golf R", "Golf GTE", "ID.3", "ID.4", "ID.5", "ID.7", "Jetta", "Jetta 1.4 TSI", "Jetta 1.6", "Jetta 1.9 TDI", "Jetta 2.0", "Passat", "Passat B5", "Passat B6", "Passat B7", "Passat B8", "Passat 1.6 TDI", "Passat 1.9 TDI", "Passat 2.0 TDI", "Passat GTE", "Phaeton", "Polo", "Scirocco", "Sharan", "T-Cross", "T-Roc", "Taigo", "Tiguan", "Touareg", "Touran", "Touran 1.6", "Touran 1.6 TDI", "Touran 1.9 TDI", "Touran 2.0 TDI", "Transporter", "Multivan", "up!"
    ],
    "Audi": ["A1", "A2", "A3", "A4", "A4 Allroad", "A5", "A6", "A6 Allroad", "A7", "A8", "Q2", "Q3", "Q4 e-tron", "Q5", "Q7", "Q8", "e-tron", "TT", "R8", "S3", "S4", "S5", "S6", "RS3", "RS4", "RS6"],
    "Škoda": ["Citigo", "Fabia", "Kamiq", "Karoq", "Kodiaq", "Octavia", "Octavia 1.6", "Octavia 1.9 TDI", "Octavia 2.0 TDI", "Rapid", "Roomster", "Scala", "Superb", "Yeti", "Enyaq", "Elroq"],
    "SEAT": ["Alhambra", "Altea", "Arona", "Ateca", "Cordoba", "Exeo", "Ibiza", "Leon", "Mii", "Tarraco", "Toledo"],
    "CUPRA": ["Ateca", "Born", "Formentor", "Leon", "Tavascan", "Terramar"],
    "Kia": ["Carens", "Carnival", "Ceed", "Cerato", "EV3", "EV6", "EV9", "Niro", "Optima", "Picanto", "Proceed", "Rio", "Sorento", "Soul", "Sportage", "Stinger", "Stonic", "Telluride", "Venga", "XCeed"],
    "Renault": ["Arkana", "Austral", "Captur", "Clio", "Espace", "Fluence", "Kadjar", "Kangoo", "Koleos", "Laguna", "Master", "Megane", "Scenic", "Talisman", "Trafic", "Twingo", "Zoe"],
    "Ford": ["B-Max", "C-Max", "EcoSport", "Edge", "Escape", "Explorer", "Fiesta", "Focus", "Focus ST", "Fusion", "Galaxy", "Kuga", "Mondeo", "Mustang", "Puma", "Ranger", "S-Max", "Tourneo Connect", "Tourneo Custom", "Transit", "Transit Connect", "Transit Custom"],
    "Dacia": ["Bigster", "Dokker", "Duster", "Jogger", "Lodgy", "Logan", "Logan MCV", "Sandero", "Sandero Stepway", "Spring"],
    "Nissan": ["Almera", "Juke", "Leaf", "Micra", "Murano", "Navara", "Note", "Pathfinder", "Primera", "Qashqai", "Tiida", "X-Trail"],
    "Toyota": ["Auris", "Avensis", "Aygo", "C-HR", "Camry", "Corolla", "Hilux", "Highlander", "Land Cruiser", "Prius", "RAV4", "Yaris"],
    "Honda": ["Accord", "Civic", "CR-V", "HR-V", "Jazz", "Pilot"],
    "Hyundai": ["Accent", "Bayon", "Elantra", "i10", "i20", "i30", "Ioniq", "Kona", "Santa Fe", "Tucson"],
    "Mazda": ["2", "3", "6", "CX-3", "CX-30", "CX-5", "CX-60", "MX-5"],
    "Peugeot": ["107", "208", "2008", "308", "3008", "508", "5008", "Partner", "Rifter", "Traveller"],
    "Citroën": ["Berlingo", "C3", "C3 Aircross", "C4", "C4 Picasso", "C5 Aircross", "Jumpy", "SpaceTourer"],
    "Opel": ["Astra", "Combo", "Corsa", "Crossland", "Grandland", "Insignia", "Meriva", "Mokka", "Vectra", "Zafira"],
    "BMW": ["1 Series", "2 Series", "3 Series", "4 Series", "5 Series", "6 Series", "7 Series", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "i3", "i4", "iX"],
    "Mercedes-Benz": ["A-Class", "B-Class", "C-Class", "CLA", "CLK", "CLS", "E-Class", "GLA", "GLB", "GLC", "GLE", "GLS", "S-Class", "Sprinter", "Vito"],
    "Volvo": ["C30", "S60", "S90", "V40", "V60", "V70", "V90", "XC40", "XC60", "XC90"],
    "Mitsubishi": ["ASX", "Colt", "L200", "Lancer", "Outlander", "Pajero", "Space Star"],
    "Suzuki": ["Baleno", "Ignis", "Jimny", "Swift", "Vitara", "SX4", "S-Cross"],
    "Fiat": ["500", "500L", "500X", "Doblo", "Ducato", "Panda", "Punto", "Tipo"],
    "Chevrolet": ["Aveo", "Captiva", "Cruze", "Lacetti", "Malibu", "Spark", "Trax"],
    "Subaru": ["Forester", "Impreza", "Legacy", "Outback", "XV"],
    "Jeep": ["Avenger", "Cherokee", "Compass", "Grand Cherokee", "Renegade", "Wrangler"],
    "Tesla": ["Model 3", "Model S", "Model X", "Model Y"],
}
# Додаткові сучасні марки та моделі, включно з комерційним транспортом і причепами.
CAR_MODELS.update({
    "Boro": ["K4 2022"],
    "Porsche": ["718", "911", "Cayenne", "Macan", "Panamera", "Taycan"],
    "Land Rover": ["Defender", "Discovery", "Discovery Sport", "Range Rover", "Range Rover Evoque", "Range Rover Sport", "Range Rover Velar"],
    "Jaguar": ["E-Pace", "F-Pace", "F-Type", "I-Pace", "XE", "XF", "XJ"],
    "Lexus": ["ES", "GS", "IS", "LBX", "LC", "LM", "LS", "NX", "RX", "RZ", "UX", "GX", "LX", "TX"],
    "MINI": ["Cooper", "Cooper Electric", "Countryman", "Clubman", "Aceman", "Convertible"],
    "Alfa Romeo": ["Giulia", "Stelvio", "Tonale", "Junior", "Giulietta"],
    "BYD": ["Atto 3", "Dolphin", "Han", "Seal", "Seal U", "Sealion 7", "Tang", "Song Plus", "Yuan Plus", "Qin Plus"],
    "MG": ["3", "4", "5", "Cyberster", "HS", "ZS", "Marvel R", "MG5 Electric"],
    "Geely": ["Atlas", "Coolray", "Monjaro", "Geometry C", "Emgrand", "Tugella", "EX5"],
    "Chery": ["Arrizo 5", "Arrizo 8", "Tiggo 4", "Tiggo 7", "Tiggo 8", "Tiggo 9", "Omoda 5"],
    "Haval": ["H2", "H6", "H6 Hybrid", "H7", "H9", "Jolion", "Dargo", "F7"],
    "Great Wall": ["Poer", "Wingle 5", "Wingle 7"],
    "Zeekr": ["001", "007", "009", "X", "7X"],
    "Polestar": ["1", "2", "3", "4"],
    "XPeng": ["G3", "G6", "G9", "P5", "P7", "X9"],
    "NIO": ["ET5", "ET7", "EL6", "EL7", "EL8", "ES6", "ES8", "EC6", "EC7"],
    "Smart": ["#1", "#3", "ForTwo", "ForFour"],
    "Genesis": ["G70", "G80", "G90", "GV60", "GV70", "GV80"],
    "Infiniti": ["Q30", "Q50", "QX30", "QX50", "QX60", "QX80"],
    "Lada": ["Granta", "Niva", "Vesta", "Largus", "XRAY"],
    "SsangYong / KGM": ["Korando", "Rexton", "Tivoli", "Torres", "Musso", "Actyon"],
    "Maxus": ["Deliver 3", "Deliver 9", "eDeliver 3", "eDeliver 9", "T90 EV", "Mifa 9"],
    "Omoda": ["C5", "E5", "C7"],
    "Jaecoo": ["J5", "J7", "J8"],
    "Leapmotor": ["T03", "C10", "C16", "B10"],
    "Li Auto": ["L6", "L7", "L8", "L9", "Mega"],
    "Hongqi": ["E-HS9", "H5", "H6", "H9", "HS3", "HS5", "HS7"],
})

# Розширені покоління та популярні модифікації для точного пошуку.
_MODEL_VARIANTS = {'Volkswagen': ['Golf I', 'Golf II', 'Golf III', 'Golf IV', 'Golf V', 'Golf VI', 'Golf VII', 'Golf VIII', 'Golf Mk1', 'Golf Mk2', 'Golf Mk3', 'Golf Mk4', 'Golf Mk5', 'Golf Mk6', 'Golf Mk7', 'Golf Mk8', 'Golf Variant', 'Golf Plus', 'Golf Sportsvan', 'Golf Alltrack', 'Golf e-Golf', 'Golf 1.4', 'Golf 1.4 TSI', 'Golf 1.6 FSI', 'Golf 1.6 MPI', 'Golf 1.9 SDI', 'Golf 2.0 SDI', 'Golf 2.0 GTI', 'Golf 2.0 TDI 4Motion', 'Jetta I', 'Jetta II', 'Jetta III', 'Jetta IV', 'Jetta V', 'Jetta VI', 'Jetta VII', 'Jetta A5', 'Jetta A6', 'Jetta A7', 'Passat B1', 'Passat B2', 'Passat B3', 'Passat B4', 'Passat B5', 'Passat B5.5', 'Passat B6', 'Passat B7', 'Passat B8', 'Passat B9', 'Passat Variant', 'Passat Alltrack', 'Passat CC', 'Touran I', 'Touran II', 'Touran 1T1', 'Touran 1T2', 'Touran 1T3', 'Touran 5T', 'Touran 1.4 TSI', 'Touran 1.9 TDI', 'Touran 2.0 SDI', 'Touran 2.0 TDI', 'Tiguan I', 'Tiguan II', 'Tiguan III', 'Tiguan Allspace', 'Polo III', 'Polo IV', 'Polo V', 'Polo VI', 'Caddy II', 'Caddy III', 'Caddy IV', 'Caddy V', 'Transporter T4', 'Transporter T5', 'Transporter T6', 'Transporter T6.1', 'Transporter T7', 'Multivan T5', 'Multivan T6', 'Multivan T7', 'Sharan I', 'Sharan II', 'Touareg I', 'Touareg II', 'Touareg III'], 'Audi': ['A3 8L', 'A3 8P', 'A3 8V', 'A3 8Y', 'A4 B5', 'A4 B6', 'A4 B7', 'A4 B8', 'A4 B9', 'A6 C4', 'A6 C5', 'A6 C6', 'A6 C7', 'A6 C8', 'Q3 8U', 'Q3 F3', 'Q5 8R', 'Q5 FY', 'Q7 4L', 'Q7 4M', 'Q8 e-tron', 'A5 B8', 'A5 B9', 'A8 D3', 'A8 D4', 'A8 D5'], 'Škoda': ['Octavia I', 'Octavia II', 'Octavia III', 'Octavia IV', 'Octavia Tour', 'Octavia A5', 'Octavia A7', 'Octavia A8', 'Superb I', 'Superb II', 'Superb III', 'Superb IV', 'Fabia I', 'Fabia II', 'Fabia III', 'Fabia IV', 'Rapid Spaceback', 'Kodiaq I', 'Kodiaq II', 'Karoq NU', 'Yeti 5L'], 'SEAT': ['Leon I', 'Leon II', 'Leon III', 'Leon IV', 'Ibiza II', 'Ibiza III', 'Ibiza IV', 'Ibiza V', 'Alhambra I', 'Alhambra II'], 'CUPRA': ['Formentor VZ', 'Leon Sportstourer', 'Born VZ'], 'Kia': ['Ceed I', 'Ceed II', 'Ceed III', 'Ceed SW', 'ProCeed', 'Sportage II', 'Sportage III', 'Sportage IV', 'Sportage V', 'Sorento II', 'Sorento III', 'Sorento IV', 'Rio II', 'Rio III', 'Rio IV', 'Optima JF', 'Niro HEV', 'Niro EV', 'XCeed'], 'Renault': ['Megane I', 'Megane II', 'Megane III', 'Megane IV', 'Megane E-Tech', 'Clio II', 'Clio III', 'Clio IV', 'Clio V', 'Scenic II', 'Scenic III', 'Scenic IV', 'Grand Scenic', 'Kangoo I', 'Kangoo II', 'Kangoo III', 'Trafic II', 'Trafic III', 'Master II', 'Master III', 'Laguna II', 'Laguna III'], 'Ford': ['Focus I', 'Focus II', 'Focus III', 'Focus IV', 'Focus Mk1', 'Focus Mk2', 'Focus Mk3', 'Focus Mk4', 'Fiesta V', 'Fiesta VI', 'Fiesta VII', 'Mondeo III', 'Mondeo IV', 'Mondeo V', 'Kuga I', 'Kuga II', 'Kuga III', 'C-Max I', 'C-Max II', 'S-Max I', 'S-Max II', 'Galaxy II', 'Galaxy III', 'Transit Mk6', 'Transit Mk7', 'Transit Custom', 'Tourneo Connect'], 'Dacia': ['Logan I', 'Logan II', 'Logan III', 'Sandero I', 'Sandero II', 'Sandero III', 'Duster I', 'Duster II', 'Duster III', 'Lodgy', 'Dokker Van', 'Jogger Hybrid'], 'Nissan': ['Qashqai J10', 'Qashqai J11', 'Qashqai J12', 'X-Trail T30', 'X-Trail T31', 'X-Trail T32', 'X-Trail T33', 'Juke F15', 'Juke F16', 'Leaf ZE0', 'Leaf ZE1'], 'Toyota': ['Corolla E120', 'Corolla E150', 'Corolla E180', 'Corolla E210', 'RAV4 XA30', 'RAV4 XA40', 'RAV4 XA50', 'Avensis T25', 'Avensis T27', 'Yaris XP10', 'Yaris XP90', 'Yaris XP130', 'Yaris XP210'], 'BMW': ['3 Series E36', '3 Series E46', '3 Series E90', '3 Series F30', '3 Series G20', '5 Series E39', '5 Series E60', '5 Series F10', '5 Series G30', 'X3 E83', 'X3 F25', 'X3 G01', 'X5 E53', 'X5 E70', 'X5 F15', 'X5 G05'], 'Mercedes-Benz': ['C-Class W203', 'C-Class W204', 'C-Class W205', 'C-Class W206', 'E-Class W211', 'E-Class W212', 'E-Class W213', 'E-Class W214', 'Sprinter W906', 'Sprinter W907', 'Vito W639', 'Vito W447'], 'Opel': ['Astra G', 'Astra H', 'Astra J', 'Astra K', 'Astra L', 'Corsa D', 'Corsa E', 'Corsa F', 'Zafira A', 'Zafira B', 'Zafira C', 'Insignia A', 'Insignia B'], 'Peugeot': ['308 I', '308 II', '308 III', '3008 I', '3008 II', '3008 III', '5008 I', '5008 II', 'Partner Tepee', 'Partner III'], 'Citroën': ['C4 I', 'C4 II', 'C4 III', 'C4 Picasso', 'Grand C4 Picasso', 'Berlingo II', 'Berlingo III'], 'Mazda': ['Mazda 3 BK', 'Mazda 3 BL', 'Mazda 3 BM', 'Mazda 3 BP', 'Mazda 6 GG', 'Mazda 6 GH', 'Mazda 6 GJ', 'Mazda 6 GL', 'CX-5 KE', 'CX-5 KF', 'CX-5 KF2'], 'Hyundai': ['i30 I', 'i30 II', 'i30 III', 'Tucson JM', 'Tucson LM', 'Tucson TL', 'Tucson NX4', 'Santa Fe CM', 'Santa Fe DM', 'Santa Fe TM', 'Santa Fe MX5'], 'Honda': ['Civic VII', 'Civic VIII', 'Civic IX', 'Civic X', 'Civic XI', 'CR-V II', 'CR-V III', 'CR-V IV', 'CR-V V', 'CR-V VI'], 'Mitsubishi': ['Outlander I', 'Outlander II', 'Outlander III', 'Lancer IX', 'Lancer X', 'Pajero III', 'Pajero IV'], 'Suzuki': ['Vitara LY', 'Grand Vitara JT', 'SX4 S-Cross', 'Swift III', 'Swift IV', 'Swift V'], 'Fiat': ['Doblo I', 'Doblo II', 'Ducato X250', 'Ducato X290', 'Tipo 356', 'Panda II', 'Panda III'], 'Subaru': ['Forester SG', 'Forester SH', 'Forester SJ', 'Forester SK', 'Outback BP', 'Outback BR', 'Outback BS', 'Outback BT']}
for _brand, _variants in _MODEL_VARIANTS.items():
    if _brand in CAR_MODELS:
        CAR_MODELS[_brand] = list(dict.fromkeys(CAR_MODELS[_brand] + _variants))


# Додаткові покоління та двигуни для вибору моделі (однаковий формат для всіх марок).
_EXTRA_MODEL_VARIANTS = {
    "Volkswagen": {
        "Golf": ["Golf I", "Golf II", "Golf III", "Golf IV", "Golf V", "Golf VI", "Golf VII", "Golf VIII", "Golf Plus", "Golf Variant", "Golf Sportsvan", "Golf 1.0 TSI", "Golf 1.2 TSI", "Golf 1.4", "Golf 1.4 TSI", "Golf 1.6", "Golf 1.6 FSI", "Golf 1.6 MPI", "Golf 1.9 SDI", "Golf 1.9 TDI", "Golf 2.0", "Golf 2.0 TDI", "Golf 2.0 GTI"],
        "Touran": ["Touran I", "Touran II", "Touran 1T1", "Touran 1T2", "Touran 1T3", "Touran 5T", "Touran 1.4 TSI", "Touran 1.6", "Touran 1.6 FSI", "Touran 1.6 TDI", "Touran 1.9 TDI", "Touran 2.0 SDI", "Touran 2.0 TDI"],
        "Jetta": ["Jetta I", "Jetta II", "Jetta III", "Jetta IV", "Jetta V", "Jetta VI", "Jetta VII", "Jetta 1.4 TSI", "Jetta 1.6", "Jetta 1.6 MPI", "Jetta 1.9 TDI", "Jetta 2.0", "Jetta 2.0 TDI"],
        "Passat": ["Passat B1", "Passat B2", "Passat B3", "Passat B4", "Passat B5", "Passat B5.5", "Passat B6", "Passat B7", "Passat B8", "Passat B9", "Passat 1.6", "Passat 1.8 T", "Passat 1.9 TDI", "Passat 2.0 TDI", "Passat 2.5 TDI", "Passat 3.0 TDI", "Passat Variant", "Passat CC"],
        "Polo": ["Polo III", "Polo IV", "Polo V", "Polo VI", "Polo 1.2", "Polo 1.4", "Polo 1.6", "Polo 1.9 SDI", "Polo 1.9 TDI"],
        "Tiguan": ["Tiguan I", "Tiguan II", "Tiguan III", "Tiguan Allspace", "Tiguan 1.4 TSI", "Tiguan 2.0 TDI"],
        "Caddy": ["Caddy II", "Caddy III", "Caddy IV", "Caddy V", "Caddy 1.6", "Caddy 1.9 TDI", "Caddy 2.0 TDI"],
    },
    "Audi": {"A3": ["A3 8L", "A3 8P", "A3 8V", "A3 8Y", "A3 1.6", "A3 1.9 TDI", "A3 2.0 TDI"], "A4": ["A4 B5", "A4 B6", "A4 B7", "A4 B8", "A4 B9", "A4 1.8 T", "A4 1.9 TDI", "A4 2.0 TDI", "A4 3.0 TDI"], "A6": ["A6 C4", "A6 C5", "A6 C6", "A6 C7", "A6 C8", "A6 1.9 TDI", "A6 2.0 TDI", "A6 2.5 TDI", "A6 3.0 TDI"], "Q5": ["Q5 8R", "Q5 FY", "Q5 2.0 TDI", "Q5 2.0 TFSI"]},
    "Škoda": {"Octavia": ["Octavia I", "Octavia II", "Octavia III", "Octavia IV", "Octavia Tour", "Octavia A5", "Octavia A7", "Octavia 1.6 MPI", "Octavia 1.9 TDI", "Octavia 2.0 TDI"], "Superb": ["Superb I", "Superb II", "Superb III", "Superb IV", "Superb 1.9 TDI", "Superb 2.0 TDI"], "Fabia": ["Fabia I", "Fabia II", "Fabia III", "Fabia IV", "Fabia 1.2", "Fabia 1.4", "Fabia 1.6 TDI"]},
    "Renault": {"Megane": ["Megane I", "Megane II", "Megane III", "Megane IV", "Megane 1.5 dCi", "Megane 1.6", "Megane 1.9 dCi", "Megane 2.0 dCi"], "Clio": ["Clio II", "Clio III", "Clio IV", "Clio V", "Clio 1.2", "Clio 1.5 dCi"], "Scenic": ["Scenic I", "Scenic II", "Scenic III", "Scenic IV", "Grand Scenic", "Scenic 1.5 dCi", "Scenic 1.9 dCi"]},
    "Ford": {"Focus": ["Focus I", "Focus II", "Focus III", "Focus IV", "Focus 1.6", "Focus 1.6 TDCi", "Focus 1.8 TDCi", "Focus 2.0 TDCi"], "Mondeo": ["Mondeo I", "Mondeo II", "Mondeo III", "Mondeo IV", "Mondeo V", "Mondeo 1.8 TDCi", "Mondeo 2.0 TDCi"], "Fiesta": ["Fiesta IV", "Fiesta V", "Fiesta VI", "Fiesta VII", "Fiesta 1.25", "Fiesta 1.4 TDCi"]},
    "Dacia": {"Logan": ["Logan I", "Logan II", "Logan III", "Logan 1.4", "Logan 1.6", "Logan 1.5 dCi"], "Sandero": ["Sandero I", "Sandero II", "Sandero III", "Sandero 1.2", "Sandero 1.5 dCi"], "Duster": ["Duster I", "Duster II", "Duster III", "Duster 1.5 dCi", "Duster 1.6", "Duster 1.3 TCe"]},
    "BMW": {"3 Series": ["3 Series E36", "3 Series E46", "3 Series E90", "3 Series F30", "3 Series G20"], "5 Series": ["5 Series E39", "5 Series E60", "5 Series F10", "5 Series G30"], "X5": ["X5 E53", "X5 E70", "X5 F15", "X5 G05"]},
    "Mercedes-Benz": {"C-Class": ["C-Class W202", "C-Class W203", "C-Class W204", "C-Class W205", "C-Class W206"], "E-Class": ["E-Class W210", "E-Class W211", "E-Class W212", "E-Class W213", "E-Class W214"]},
    "Toyota": {"Corolla": ["Corolla E120", "Corolla E150", "Corolla E180", "Corolla E210"], "RAV4": ["RAV4 XA10", "RAV4 XA20", "RAV4 XA30", "RAV4 XA40", "RAV4 XA50"]},
    "Nissan": {"Qashqai": ["Qashqai J10", "Qashqai J11", "Qashqai J12"], "X-Trail": ["X-Trail T30", "X-Trail T31", "X-Trail T32", "X-Trail T33"]},
    "Kia": {"Ceed": ["Ceed I", "Ceed II", "Ceed III", "Ceed 1.6 CRDi"], "Sportage": ["Sportage I", "Sportage II", "Sportage III", "Sportage IV", "Sportage V"]},
    "Opel": {"Astra": ["Astra F", "Astra G", "Astra H", "Astra J", "Astra K", "Astra L"], "Zafira": ["Zafira A", "Zafira B", "Zafira C"]},
    "Peugeot": {"308": ["308 I", "308 II", "308 III", "308 1.6 HDi"], "3008": ["3008 I", "3008 II", "3008 III"]},
    "Citroën": {"Berlingo": ["Berlingo I", "Berlingo II", "Berlingo III", "Berlingo 1.6 HDi"]},
}
for _brand, _models in _EXTRA_MODEL_VARIANTS.items():
    for _base, _variants in _models.items():
        if _brand in CAR_MODELS:
            CAR_MODELS[_brand] = list(dict.fromkeys(CAR_MODELS[_brand] + _variants))

CAR_BRANDS = list(CAR_MODELS.keys())

# Швидкі картки на сторінці «Підібрати авто».
# type=model — показує конкретну модель Volkswagen; type=brand — всю марку.
QUICK_PICKER = [
    {"title": "GOLF", "brand": "Volkswagen", "model": "Golf", "type": "model"},
    {"title": "JETTA", "brand": "Volkswagen", "model": "Jetta", "type": "model"},
    {"title": "PASSAT", "brand": "Volkswagen", "model": "Passat", "type": "model"},
    {"title": "TOURAN", "brand": "Volkswagen", "model": "Touran", "type": "model"},
    {"title": "ŠKODA", "brand": "Škoda", "model": "", "type": "brand"},
    {"title": "AUDI", "brand": "Audi", "model": "", "type": "brand"},
    {"title": "SEAT", "brand": "SEAT", "model": "", "type": "brand"},
    {"title": "CUPRA", "brand": "CUPRA", "model": "", "type": "brand"},
    {"title": "KIA", "brand": "Kia", "model": "", "type": "brand"},
    {"title": "RENAULT", "brand": "Renault", "model": "", "type": "brand"},
    {"title": "FORD", "brand": "Ford", "model": "", "type": "brand"},
    {"title": "DACIA", "brand": "Dacia", "model": "", "type": "brand"},
]

# ------------------------------------------------------------
# ВАРІАНТИ ФОРМИ ДОДАВАННЯ АВТО
# ------------------------------------------------------------
FUEL = ["Бензин", "Дизель", "Гібрид", "Електро", "Газ/бензин", "Водень"]
GEARBOX = ["Механіка", "Автомат", "DSG", "Варіатор", "Робот"]
BODY = [
    "Седан", "Хетчбек", "Універсал", "Купе", "Кабріолет", "Ліфтбек", "Фастбек", "Тарга", "Родстер",
    "Кросовер", "Позашляховик", "Мінівен", "Мікроавтобус", "Фургон", "Пікап", "Універсал/фургон", "Компактвен", "Причіп", "Напівпричіп"
]
DRIVE = ["Передній", "Задній", "Повний"]

# Поля основної інформації: name, key, type, required, placeholder.
MAIN_FIELDS = [
    {"key": "brand", "name": "Марка", "type": "select", "required": True},
    {"key": "model", "name": "Модель", "type": "select", "required": True},
    {"key": "year", "name": "Рік", "type": "number", "required": True, "placeholder": "2021"},
    {"key": "price", "name": "Ціна, $", "type": "number", "required": True, "placeholder": "25000"},
    {"key": "mileage", "name": "Пробіг, тис. км", "type": "number", "placeholder": "226"},
    {"key": "fuel", "name": "Паливо", "type": "select"},
    {"key": "gearbox", "name": "Коробка", "type": "select"},
    {"key": "body", "name": "Кузов", "type": "select"},
    {"key": "color", "name": "Колір", "type": "text", "placeholder": "Чорний"},
    {"key": "engine", "name": "Двигун", "type": "text", "placeholder": "2.0 л"},
    {"key": "drive", "name": "Привід", "type": "select"},
    {"key": "phone", "name": "Телефон", "type": "text", "placeholder": "+380...", "full": True},
    {"key": "description", "name": "Опис", "type": "textarea", "placeholder": "Опис автомобіля...", "full": True},
    {"key": "vin", "name": "VIN", "type": "text", "placeholder": "VIN-код автомобіля", "full": True},
]

# Детальні характеристики — ці назви і підказки можна повністю міняти тут.
DETAIL_FIELDS = [
    {"key": "generation", "name": "Покоління", "placeholder": "Mk7"},
    {"key": "trim", "name": "Комплектація", "placeholder": "Highline / GTI / Business"},
    {"key": "modification", "name": "Модифікація", "placeholder": "2.0 TSI 245 к.с."},
    {"key": "eco_standard", "name": "Екологічний стандарт", "placeholder": "Євро 6"},
    {"key": "condition", "name": "Стан", "placeholder": "Не битий, не фарбований"},
    {"key": "fuel_consumption", "name": "Витрати пального (л/100км)", "placeholder": "7.0 місто / 5.0 траса"},
    {"key": "safety", "name": "Безпека (через кому)", "placeholder": "ABS, ESP, ASR, EBD", "full": True},
    {"key": "air_conditioner", "name": "Кондиціонер (через кому)", "placeholder": "Клімат-контроль, кондиціонер", "full": True},
    {"key": "comfort", "name": "Комфорт (через кому)", "placeholder": "Підігрів сидінь, круїз-контроль", "full": True},
    {"key": "optics", "name": "Оптика (через кому)", "placeholder": "LED фари, ДХВ", "full": True},
    {"key": "multimedia", "name": "Мультимедіа (через кому)", "placeholder": "Apple CarPlay, Android Auto, Bluetooth", "full": True},
    {"key": "interior_body", "name": "Матеріали салону (через кому)", "placeholder": "Шкіряний салон, алюмінієві вставки", "full": True},
    {"key": "headlights", "name": "Фари (через кому)", "placeholder": "LED, автоматичне включення", "full": True},
    {"key": "parking", "name": "Система допомоги при паркуванні (через кому)", "placeholder": "Парктроніки передні/задні, камера", "full": True},
    {"key": "airbags", "name": "Подушки безпеки (через кому)", "placeholder": "Фронтальні, бічні, занавіски", "full": True},
]
DETAIL_FIELD_MAP = {x["key"]: x for x in DETAIL_FIELDS}

# ------------------------------------------------------------
# ДОДАТКОВІ ПОСЛУГИ
# ------------------------------------------------------------
ADDITIONAL_SERVICES = [
    {"slug": "shinomontazh", "name": "Шиномонтаж", "icon": "◉", "description": "Монтаж та демонтаж шин, балансування коліс, перевірка тиску та підготовка автомобіля до сезону."},
    {"slug": "himchistka", "name": "Хімчистка", "icon": "✦", "description": "Професійна хімчистка салону автомобіля: сидіння, стеля, підлога, пластик та важкодоступні місця."},
    {"slug": "myika-avto", "name": "Мийка авто", "icon": "✧", "description": "Комплексна мийка автомобіля з очищенням кузова, скла та коліс. Доступні різні варіанти миття."},
    {"slug": "detailing", "name": "Детейлінг", "icon": "◆", "description": "Детейлінг кузова та салону: глибоке очищення, відновлення зовнішнього вигляду та захист поверхонь."},
    {"slug": "computer-diagnostics", "name": "Компʼютерна діагностика", "icon": "⚡", "description": "Компʼютерна перевірка електронних блоків автомобіля, зчитування помилок та діагностика несправностей."},
    {"slug": "prygon-avto", "name": "Пригон авто", "icon": "➜", "description": "Допоможемо підібрати та пригнати автомобіль під ваш бюджет і побажання, перевіримо варіанти перед купівлею."},
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

# ------------------------------------------------------------
# УСІ НАПИСИ І ПОВІДОМЛЕННЯ САЙТУ
# ------------------------------------------------------------
TEXT = {
    "nav_call": "☎ Зателефонувати",
    "nav_login": "Увійти",
    "nav_logout": "Вийти",
    "call_title": "Зателефонуйте нам",
    "call_subtitle": "Оберіть зручний номер для зв’язку",
    "viber": "◯ Вайбер",
    "telegram": "➤ Телеграм",
    "close": "Закрити",
    "catalog": "Каталог",
    "pick_title": "Підібрати авто",
    "pick_subtitle": "Оберіть марку та модель автомобіля",
    "show_cars": "Показати авто ›",
    "show_all": "Показати всі авто ›",
    "all_cars": "Всі авто ›",
    "recommended": "Рекомендовані авто",
    "recommended_subtitle": "Найкращі пропозиції у Сокалі",
    "recommended_badge": "Рекомендуємо",
    "details": "Детальніше ›",
    "back_to_picker": "← Повернутися до підбору",
    "change_selection": "Змінити вибір ›",
    "filter_note": "Показуємо лише автомобілі за вашим вибором",
    "empty_filter_title": "Такого автомобіля зараз немає",
    "empty_filter_text": "Автомобілів за вашим вибором не знайдено. Зателефонуйте нам — допоможемо знайти потрібну машину.",
    "empty_cars": "Поки що автомобілів немає.",
    "price_request": "Ціна за запитом",
    "year": "рік",
    "thousand_km": "тис. км",
    "call_us": "☎ Зателефонувати нам",
    "detail_back": "← Назад до списку",
    "detail_characteristics": "Характеристики",
    "detail_description": "Опис",
    "no_description": "Опис автомобіля не додано.",
    "interested": "Зацікавило це авто?",
    "interested_text": "Зателефонуйте нам, щоб дізнатися більше та домовитися про огляд у Львові.",
    "form_panel": "Панель редактора",
    "add_car": "Додати автомобіль",
    "edit_car": "Редагувати автомобіль",
    "add_hint": "Заповніть характеристики та додайте фото.",
    "edit_hint": "Змініть характеристики, додайте нові фото або видаліть непотрібні.",
    "main_info": "Основна інформація",
    "choose_brand": "Оберіть марку",
    "choose_model": "Оберіть модель",
    "empty_option": "—",
    "detail_info": "Детальні характеристики",
    "photos": "Фото",
    "added_photos": "Додані фото",
    "new_photos": "Додати нові фото",
    "photo_choose": "Оберіть фото з телефону або ПК",
    "photo_hint": "Можна додати максимум 100 фото до одного автомобіля.",
    "photo_edit_hint": "Можна додати нові фото, якщо загальна кількість не перевищить 100.",
    "delete_photo": "Видалити фото",
    "save_changes": "Зберегти зміни",
    "publish_car": "Опублікувати авто",
    "existing_cars": "Існуючі авто",
    "edit": "Редагувати",
    "delete": "Видалити",
    "admin_details": "Детальніше",
    "confirm_delete_photo": "Видалити це фото?",
    "confirm_delete_car": "Видалити це авто?",
    "parts_text": "У нас є запчастини з розборки та нові деталі для GOLF, JETTA, PASSAT, RENAULT, FORD, DACIA, NISSAN і TOURAN.",
    "wheels_text": "Б/у колеса, диски та титани. Підберемо комплект під ваш автомобіль.",
    "no_match_call": "Якщо потрібної машини немає — зателефонуйте нам, і ми допоможемо з пошуком.",
}

# Заголовки блоків на сторінці детального авто.
DETAIL_GROUPS = [
    ("Безпека", "safety"),
    ("Кондиціонер", "air_conditioner"),
    ("Комфорт", "comfort"),
    ("Оптика", "optics"),
    ("Мультимедіа", "multimedia"),
    ("Салон та кузов", "interior_body"),
    ("Фари", "headlights"),
    ("Система допомоги при паркуванні", "parking"),
    ("Подушка безпеки", "airbags"),
]

# ------------------------------------------------------------
# РОЛІ / ФОТО / БАЗА
# ------------------------------------------------------------
ROLES = {"user": "Користувач", "editor": "Редактор", "admin": "Адміністратор"}
MAX_PHOTOS = 100
ALLOWED = {"jpg", "jpeg", "png", "webp"}
ADMIN_DEFAULT_EMAIL = "admin@vagzlumauto.local"
ADMIN_DEFAULT_PASSWORD = "Admin123!"

# Старі записи бази, створені до схеми Марка -> Модель.
LEGACY_MODEL_BRANDS = {
    "GOLF": "Golf", "JETTA": "Jetta", "PASSAT": "Passat", "TOURAN": "Touran",
    "RENAULT": None, "FORD": None, "DACIA": None,
}

# Необов'язкові стартові автомобілі. Працюють тільки якщо база порожня.
DEMO_CARS = []
