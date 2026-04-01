import os
import sqlite3
import uuid
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "site.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}

DEFAULT_SETTINGS = {
    "business_name": "Manzan Barber",
    "badge": "Sejam Bem-Vindos",
    "description": (
        "Uma experiencia old school com atendimento diferenciado, "
        "acabamento refinado e um ambiente criado para quem valoriza presenca."
    ),
    "address": "R. Castro Alves, 84 - Chafariz, Sacramento - MG",
    "hours_week": "Seg a Sex - 09:00 as 19:00",
    "hours_sat": "Sabado - 09:00 as 18:00",
    "hours_sun": "Domingo - Fechado",
    "whatsapp_link": "https://api.whatsapp.com/send?phone=5534999222926&text=",
    "horario_link": "https://sites.appbarber.com.br/agendamento/manzanbarbearia-3xbv?fbclid=PAVERFWAQ4zwVleHRuA2FlbQIxMQBzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAad50Ln_bvW2hXom66ewBmtL1LknDMmIwy-n94fWAUV_dRCgDCF4p-D3vn3Apw_aem_fZp7wKHpv1D32TpYn-6-wQ",
    "maps_link": "https://maps.app.goo.gl/CkKm6DkmB15PJuP78?g_st=iw",
    "offer_title": "Experiencia Classica",
    "offer_text": "Toalha quente, navalha, cuidado nos detalhes e atendimento exclusivo.",
    "hero_cta": "Ver fotos",
    "about_eyebrow": "Sobre mim",
    "about_title": "Muito alem da cadeira, aqui voce encontra identidade, estilo e personalidade.",
    "about_paragraph_1": (
        "Sou o rosto por tras da Exodo Barbearia e transformei minha paixao por estilo, "
        "atendimento e presenca em uma experiencia pensada nos detalhes."
    ),
    "about_paragraph_2": (
        "Meu objetivo e entregar mais do que um corte: quero que cada cliente saia daqui "
        "se sentindo confiante, alinhado e com uma imagem que realmente represente quem ele e."
    ),
    "about_paragraph_3": (
        "Cada atendimento e feito com atencao, tecnica e respeito ao seu estilo. "
        "A proposta da Exodo e unir profissionalismo, ambiente marcante e uma conexao verdadeira com cada cliente."
    ),
    "structure_title": "Um ambiente onde voce se sente em casa, com toque classico e atendimento exclusivo.",
    "structure_highlight_1": "Atmosfera tematica com referencias classicas de barbearia tradicional.",
    "structure_highlight_2": "Atendimento com horario marcado, pontualidade e experiencia personalizada.",
    "structure_highlight_3": "Tecnica, ritual e acabamento profissional do corte a barba.",
    "structure_highlight_4": "Ambiente confortavel para transformar um simples atendimento em experiencia.",
    "structure_image": "/static/foto-barbearia.jpg",
}

DEFAULT_PRICING = [
    ("Barba", "R$30,00"),
    ("Barba com Barboterapia", "R$40,00"),
    ("Cabelo - Barba e Barboterapia", "R$70,00"),
    ("Corte", "R$40,00"),
    ("Corte - Barba", "R$60,00"),
    ("Corte - Barba - Pigmentacao", "R$85,00"),
    ("Corte e Pigmentacao", "R$55,00"),
    ("Corte Infantil", "R$45,00"),
    ("Pezinho", "R$15,00"),
    ("Sobrancelha", "R$15,00"),
]

DEFAULT_REVIEWS = [
    (
        "Rafael M.",
        "Ambiente impecavel, atendimento pontual e o corte sempre vem exatamente como eu preciso.",
        5,
        1,
    ),
    (
        "Lucas A.",
        "A barba ficou muito acima do que eu encontrava em outras barbearias. Virou meu lugar fixo.",
        5,
        1,
    ),
    (
        "Thiago S.",
        "Da recepcao ao acabamento final, da para sentir que tudo foi pensado para entregar nivel premium.",
        5,
        1,
    ),
]

DEFAULT_GALLERY = [
    {
        "type": "slideshow",
        "alt": "Corte masculino sendo finalizado na barbearia",
        "video_url": "",
        "poster_url": "",
        "media": [
            "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=900&q=80",
        ],
    },
    {
        "type": "slideshow",
        "alt": "Cliente recebendo acabamento de barba",
        "video_url": "",
        "poster_url": "",
        "media": [
            "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1517832606299-7ae9b720a186?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1512690459411-b0fd1c86b8ce?auto=format&fit=crop&w=900&q=80",
        ],
    },
    {
        "type": "slideshow",
        "alt": "Ambiente interno da barbearia",
        "video_url": "",
        "poster_url": "",
        "media": [
            "/static/foto-barbearia.jpg",
            "https://images.unsplash.com/photo-1511920170033-f8396924c348?auto=format&fit=crop&w=900&q=80",
            "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?auto=format&fit=crop&w=900&q=80",
        ],
    },
    {
        "type": "video",
        "alt": "Video de apresentacao da barbearia",
        "video_url": "https://www.w3schools.com/html/mov_bbb.mp4",
        "poster_url": "/static/foto-barbearia.jpg",
        "media": [],
    },
]


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "manzan-admin-secret")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pricing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position INTEGER NOT NULL,
            name TEXT NOT NULL,
            price TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            quote TEXT NOT NULL,
            rating INTEGER NOT NULL,
            approved INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS gallery_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position INTEGER NOT NULL,
            type TEXT NOT NULL,
            alt TEXT NOT NULL,
            video_url TEXT DEFAULT '',
            poster_url TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS gallery_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            media_url TEXT NOT NULL,
            FOREIGN KEY(card_id) REFERENCES gallery_cards(id) ON DELETE CASCADE
        );
        """
    )

    existing_settings = {
        row["key"] for row in cursor.execute("SELECT key FROM settings").fetchall()
    }
    for key, value in DEFAULT_SETTINGS.items():
        if key not in existing_settings:
            cursor.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )

    pricing_count = cursor.execute("SELECT COUNT(*) FROM pricing").fetchone()[0]
    if pricing_count == 0:
        for index, (name, price) in enumerate(DEFAULT_PRICING, start=1):
            cursor.execute(
                "INSERT INTO pricing (position, name, price) VALUES (?, ?, ?)",
                (index, name, price),
            )

    reviews_count = cursor.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    if reviews_count == 0:
        cursor.executemany(
            "INSERT INTO reviews (author, quote, rating, approved) VALUES (?, ?, ?, ?)",
            DEFAULT_REVIEWS,
        )

    gallery_count = cursor.execute("SELECT COUNT(*) FROM gallery_cards").fetchone()[0]
    if gallery_count == 0:
        for index, item in enumerate(DEFAULT_GALLERY, start=1):
            cursor.execute(
                """
                INSERT INTO gallery_cards (position, type, alt, video_url, poster_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    index,
                    item["type"],
                    item["alt"],
                    item["video_url"],
                    item["poster_url"],
                ),
            )
            card_id = cursor.lastrowid
            for media_index, media_url in enumerate(item["media"], start=1):
                cursor.execute(
                    """
                    INSERT INTO gallery_media (card_id, position, media_url)
                    VALUES (?, ?, ?)
                    """,
                    (card_id, media_index, media_url),
                )

    db.commit()
    db.close()


def allowed_file(filename, allowed_extensions):
    return Path(filename).suffix.lower() in allowed_extensions


def save_upload(file_storage, folder_name, allowed_extensions):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        return None

    target_dir = UPLOAD_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"{uuid.uuid4().hex}{suffix}"
    target_path = target_dir / target_name
    file_storage.save(target_path)
    return f"/static/uploads/{folder_name}/{target_name}"


def setting_value(key, fallback=""):
    row = get_db().execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else fallback


def set_setting(key, value):
    get_db().execute(
        """
        INSERT INTO settings (key, value) VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )


def get_business_settings():
    return {
        "name": setting_value("business_name", DEFAULT_SETTINGS["business_name"]),
        "badge": setting_value("badge", DEFAULT_SETTINGS["badge"]),
        "description": setting_value("description", DEFAULT_SETTINGS["description"]),
        "address": setting_value("address", DEFAULT_SETTINGS["address"]),
        "hours_week": setting_value("hours_week", DEFAULT_SETTINGS["hours_week"]),
        "hours_sat": setting_value("hours_sat", DEFAULT_SETTINGS["hours_sat"]),
        "hours_sun": setting_value("hours_sun", DEFAULT_SETTINGS["hours_sun"]),
        "whatsapp_link": setting_value("whatsapp_link", DEFAULT_SETTINGS["whatsapp_link"]),
        "horario_link": setting_value("horario_link", DEFAULT_SETTINGS["horario_link"]),
        "maps_link": setting_value("maps_link", DEFAULT_SETTINGS["maps_link"]),
        "offer_title": setting_value("offer_title", DEFAULT_SETTINGS["offer_title"]),
        "offer_text": setting_value("offer_text", DEFAULT_SETTINGS["offer_text"]),
        "hero_cta": setting_value("hero_cta", DEFAULT_SETTINGS["hero_cta"]),
    }


def get_about_content():
    return {
        "eyebrow": setting_value("about_eyebrow", DEFAULT_SETTINGS["about_eyebrow"]),
        "title": setting_value("about_title", DEFAULT_SETTINGS["about_title"]),
        "paragraphs": [
            setting_value("about_paragraph_1", DEFAULT_SETTINGS["about_paragraph_1"]),
            setting_value("about_paragraph_2", DEFAULT_SETTINGS["about_paragraph_2"]),
            setting_value("about_paragraph_3", DEFAULT_SETTINGS["about_paragraph_3"]),
        ],
    }


def get_structure_content():
    return {
        "title": setting_value("structure_title", DEFAULT_SETTINGS["structure_title"]),
        "image": setting_value("structure_image", DEFAULT_SETTINGS["structure_image"]),
        "highlights": [
            setting_value("structure_highlight_1", DEFAULT_SETTINGS["structure_highlight_1"]),
            setting_value("structure_highlight_2", DEFAULT_SETTINGS["structure_highlight_2"]),
            setting_value("structure_highlight_3", DEFAULT_SETTINGS["structure_highlight_3"]),
            setting_value("structure_highlight_4", DEFAULT_SETTINGS["structure_highlight_4"]),
        ],
    }


def get_pricing():
    rows = get_db().execute(
        "SELECT id, position, name, price FROM pricing ORDER BY position, id"
    ).fetchall()
    return [dict(row) for row in rows]


def get_gallery_cards():
    db = get_db()
    cards = db.execute(
        """
        SELECT id, position, type, alt, video_url, poster_url
        FROM gallery_cards
        ORDER BY position, id
        """
    ).fetchall()
    results = []
    for card in cards:
        media_rows = db.execute(
            """
            SELECT id, position, media_url
            FROM gallery_media
            WHERE card_id = ?
            ORDER BY position, id
            """,
            (card["id"],),
        ).fetchall()
        results.append(
            {
                "id": card["id"],
                "position": card["position"],
                "type": card["type"],
                "alt": card["alt"],
                "video": card["video_url"],
                "poster": card["poster_url"],
                "images": [row["media_url"] for row in media_rows],
                "media_rows": [dict(row) for row in media_rows],
            }
        )
    return results


def get_public_reviews():
    rows = get_db().execute(
        """
        SELECT id, author, quote, rating
        FROM reviews
        WHERE approved = 1
        ORDER BY id DESC
        LIMIT 6
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_all_reviews():
    rows = get_db().execute(
        """
        SELECT id, author, quote, rating, approved, created_at
        FROM reviews
        ORDER BY id DESC
        """
    ).fetchall()
    return [dict(row) for row in rows]


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


@app.context_processor
def inject_admin_flag():
    return {"admin_logged_in": bool(session.get("admin_logged_in"))}


@app.route("/")
def home():
    business = get_business_settings()
    about_me = get_about_content()
    structure = get_structure_content()
    pricing = get_pricing()
    testimonials = get_public_reviews()
    gallery = get_gallery_cards()

    return render_template(
        "index.html",
        business=business,
        about_me=about_me,
        highlights=structure["highlights"],
        structure=structure,
        pricing=pricing,
        testimonials=testimonials,
        gallery=gallery,
    )


@app.post("/reviews")
def submit_review():
    author = request.form.get("author", "").strip() or "Cliente"
    quote = request.form.get("comment", "").strip()
    rating = request.form.get("rating", "").strip()

    if not quote or not rating.isdigit():
        flash("Preencha comentario e nota para enviar sua avaliacao.", "error")
        return redirect(url_for("home") + "#avaliacoes")

    rating_value = max(1, min(5, int(rating)))
    get_db().execute(
        """
        INSERT INTO reviews (author, quote, rating, approved)
        VALUES (?, ?, ?, 0)
        """,
        (author[:80], quote[:1000], rating_value),
    )
    get_db().commit()
    flash("Avaliacao enviada com sucesso", "success")
    return redirect(url_for("home") + "#avaliacoes")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        if password == admin_password:
            session["admin_logged_in"] = True
            flash("Login realizado com sucesso.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Senha invalida.", "error")

    return render_template("admin_login.html")


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    flash("Sessao encerrada.", "success")
    return redirect(url_for("admin_login"))


@app.get("/admin")
@admin_required
def admin_dashboard():
    business = get_business_settings()
    about_me = get_about_content()
    structure = get_structure_content()
    pricing = get_pricing()
    gallery = get_gallery_cards()
    reviews = get_all_reviews()
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    return render_template(
        "admin_dashboard.html",
        business=business,
        about_me=about_me,
        structure=structure,
        pricing=pricing,
        gallery=gallery,
        reviews=reviews,
        admin_password_hint=admin_password,
    )


@app.post("/admin/settings")
@admin_required
def update_settings():
    form_keys = [
        "business_name",
        "badge",
        "description",
        "address",
        "hours_week",
        "hours_sat",
        "hours_sun",
        "whatsapp_link",
        "horario_link",
        "maps_link",
        "offer_title",
        "offer_text",
        "hero_cta",
        "about_eyebrow",
        "about_title",
        "about_paragraph_1",
        "about_paragraph_2",
        "about_paragraph_3",
        "structure_title",
        "structure_highlight_1",
        "structure_highlight_2",
        "structure_highlight_3",
        "structure_highlight_4",
    ]
    for key in form_keys:
        if key in request.form:
            set_setting(key, request.form.get(key, "").strip())
    get_db().commit()
    flash("Conteudos e horarios atualizados.", "success")
    return redirect(url_for("admin_dashboard") + "#settings")


@app.post("/admin/structure-image")
@admin_required
def update_structure_image():
    image = request.files.get("structure_image")
    image_url = save_upload(image, "structure", ALLOWED_IMAGE_EXTENSIONS)
    if not image_url:
        flash("Envie uma imagem valida para a estrutura.", "error")
        return redirect(url_for("admin_dashboard") + "#structure")

    set_setting("structure_image", image_url)
    get_db().commit()
    flash("Imagem da estrutura atualizada.", "success")
    return redirect(url_for("admin_dashboard") + "#structure")


@app.post("/admin/pricing/add")
@admin_required
def add_pricing():
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    if not name or not price:
        flash("Preencha nome e valor do servico.", "error")
        return redirect(url_for("admin_dashboard") + "#pricing")

    db = get_db()
    position = db.execute("SELECT COALESCE(MAX(position), 0) + 1 FROM pricing").fetchone()[0]
    db.execute(
        "INSERT INTO pricing (position, name, price) VALUES (?, ?, ?)",
        (position, name, price),
    )
    db.commit()
    flash("Servico adicionado.", "success")
    return redirect(url_for("admin_dashboard") + "#pricing")


@app.post("/admin/pricing/<int:item_id>/update")
@admin_required
def update_pricing(item_id):
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    if not name or not price:
        flash("Preencha nome e valor do servico.", "error")
        return redirect(url_for("admin_dashboard") + "#pricing")

    get_db().execute(
        "UPDATE pricing SET name = ?, price = ? WHERE id = ?",
        (name, price, item_id),
    )
    get_db().commit()
    flash("Servico atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#pricing")


@app.post("/admin/pricing/<int:item_id>/delete")
@admin_required
def delete_pricing(item_id):
    get_db().execute("DELETE FROM pricing WHERE id = ?", (item_id,))
    get_db().commit()
    flash("Servico removido.", "success")
    return redirect(url_for("admin_dashboard") + "#pricing")


@app.post("/admin/gallery/<int:card_id>/update")
@admin_required
def update_gallery_card(card_id):
    db = get_db()
    card = db.execute(
        "SELECT id, type FROM gallery_cards WHERE id = ?",
        (card_id,),
    ).fetchone()
    if not card:
        flash("Card de galeria nao encontrado.", "error")
        return redirect(url_for("admin_dashboard") + "#gallery")

    card_type = request.form.get("type", card["type"]).strip() or card["type"]
    alt = request.form.get("alt", "").strip()

    video_url = request.form.get("video_url", "").strip()
    poster_url = request.form.get("poster_url", "").strip()

    uploaded_video = save_upload(
        request.files.get("video_file"),
        "gallery",
        ALLOWED_VIDEO_EXTENSIONS,
    )
    uploaded_poster = save_upload(
        request.files.get("poster_file"),
        "gallery",
        ALLOWED_IMAGE_EXTENSIONS,
    )
    if uploaded_video:
        video_url = uploaded_video
    if uploaded_poster:
        poster_url = uploaded_poster

    db.execute(
        """
        UPDATE gallery_cards
        SET type = ?, alt = ?, video_url = ?, poster_url = ?
        WHERE id = ?
        """,
        (card_type, alt, video_url, poster_url, card_id),
    )

    if card_type == "slideshow":
        media_urls = [
            line.strip()
            for line in request.form.get("media_urls", "").splitlines()
            if line.strip()
        ]
        uploaded_images = request.files.getlist("image_files")
        for image in uploaded_images:
            saved = save_upload(image, "gallery", ALLOWED_IMAGE_EXTENSIONS)
            if saved:
                media_urls.append(saved)

        db.execute("DELETE FROM gallery_media WHERE card_id = ?", (card_id,))
        for index, media_url in enumerate(media_urls, start=1):
            db.execute(
                "INSERT INTO gallery_media (card_id, position, media_url) VALUES (?, ?, ?)",
                (card_id, index, media_url),
            )

    db.commit()
    flash("Card da galeria atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#gallery")


@app.post("/admin/reviews/<int:review_id>/toggle")
@admin_required
def toggle_review(review_id):
    db = get_db()
    row = db.execute(
        "SELECT approved FROM reviews WHERE id = ?",
        (review_id,),
    ).fetchone()
    if row:
        new_value = 0 if row["approved"] else 1
        db.execute("UPDATE reviews SET approved = ? WHERE id = ?", (new_value, review_id))
        db.commit()
        flash("Status da avaliacao atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#reviews")


@app.post("/admin/reviews/<int:review_id>/delete")
@admin_required
def delete_review(review_id):
    get_db().execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    get_db().commit()
    flash("Avaliacao removida.", "success")
    return redirect(url_for("admin_dashboard") + "#reviews")


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
