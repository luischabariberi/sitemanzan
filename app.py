import os
import uuid
from functools import wraps
from pathlib import Path

import cloudinary
import cloudinary.uploader
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v"}


def cloudinary_is_configured():
    return bool(
        os.environ.get("CLOUDINARY_CLOUD_NAME")
        and os.environ.get("CLOUDINARY_API_KEY")
        and os.environ.get("CLOUDINARY_API_SECRET")
    )


if cloudinary_is_configured():
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )

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
        True,
    ),
    (
        "Lucas A.",
        "A barba ficou muito acima do que eu encontrava em outras barbearias. Virou meu lugar fixo.",
        5,
        True,
    ),
    (
        "Thiago S.",
        "Da recepcao ao acabamento final, da para sentir que tudo foi pensado para entregar nivel premium.",
        5,
        True,
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


def normalized_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return database_url
    return f"sqlite:///{(BASE_DIR / 'site.db').as_posix()}"


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "manzan-admin-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = normalized_database_url()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Setting(db.Model):
    __tablename__ = "settings"
    key = db.Column(db.String(120), primary_key=True)
    value = db.Column(db.Text, nullable=False)


class PricingItem(db.Model):
    __tablename__ = "pricing"
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(100), nullable=False)


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    quote = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=5)
    approved = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class GalleryCard(db.Model):
    __tablename__ = "gallery_cards"
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String(40), nullable=False)
    alt = db.Column(db.String(255), nullable=False)
    video_url = db.Column(db.Text, nullable=False, default="")
    poster_url = db.Column(db.Text, nullable=False, default="")
    media_items = db.relationship(
        "GalleryMedia",
        backref="card",
        cascade="all, delete-orphan",
        order_by="GalleryMedia.position",
        lazy=True,
    )


class GalleryMedia(db.Model):
    __tablename__ = "gallery_media"
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey("gallery_cards.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    media_url = db.Column(db.Text, nullable=False)


def allowed_file(filename, allowed_extensions):
    return Path(filename).suffix.lower() in allowed_extensions


def save_upload(file_storage, folder_name, allowed_extensions):
    if not file_storage or not file_storage.filename:
        return None

    filename = secure_filename(file_storage.filename)
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        return None

    if cloudinary_is_configured():
        upload_options = {
            "folder": f"manzanbarber/{folder_name}",
            "resource_type": "video" if allowed_extensions == ALLOWED_VIDEO_EXTENSIONS else "image",
            "public_id": uuid.uuid4().hex,
            "overwrite": True,
        }
        uploaded = cloudinary.uploader.upload(file_storage, **upload_options)
        return uploaded.get("secure_url")

    target_dir = UPLOAD_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"{uuid.uuid4().hex}{suffix}"
    target_path = target_dir / target_name
    file_storage.save(target_path)
    return f"/static/uploads/{folder_name}/{target_name}"


def setting_value(key, fallback=""):
    row = db.session.get(Setting, key)
    return row.value if row else fallback


def set_setting(key, value):
    row = db.session.get(Setting, key)
    if row:
        row.value = value
    else:
        db.session.add(Setting(key=key, value=value))


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
    return [
        {
            "id": item.id,
            "position": item.position,
            "name": item.name,
            "price": item.price,
        }
        for item in PricingItem.query.order_by(PricingItem.position, PricingItem.id).all()
    ]


def get_gallery_cards():
    cards = GalleryCard.query.order_by(GalleryCard.position, GalleryCard.id).all()
    results = []
    for card in cards:
        results.append(
            {
                "id": card.id,
                "position": card.position,
                "type": card.type,
                "alt": card.alt,
                "video": card.video_url,
                "poster": card.poster_url,
                "images": [media.media_url for media in card.media_items],
                "media_rows": [
                    {"id": media.id, "position": media.position, "media_url": media.media_url}
                    for media in card.media_items
                ],
            }
        )
    return results


def get_public_reviews():
    rows = (
        Review.query.filter_by(approved=True)
        .order_by(Review.id.desc())
        .limit(6)
        .all()
    )
    return [
        {
            "id": row.id,
            "author": row.author,
            "quote": row.quote,
            "rating": row.rating,
        }
        for row in rows
    ]


def get_all_reviews():
    return [
        {
            "id": row.id,
            "author": row.author,
            "quote": row.quote,
            "rating": row.rating,
            "approved": row.approved,
            "created_at": row.created_at,
        }
        for row in Review.query.order_by(Review.id.desc()).all()
    ]


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


def seed_defaults():
    for key, value in DEFAULT_SETTINGS.items():
        if not db.session.get(Setting, key):
            db.session.add(Setting(key=key, value=value))

    if PricingItem.query.count() == 0:
        for index, (name, price) in enumerate(DEFAULT_PRICING, start=1):
            db.session.add(PricingItem(position=index, name=name, price=price))

    reviews_seeded = setting_value("_reviews_seeded", "")
    if not reviews_seeded and Review.query.count() == 0:
        for author, quote, rating, approved in DEFAULT_REVIEWS:
            db.session.add(
                Review(author=author, quote=quote, rating=rating, approved=approved)
            )
        set_setting("_reviews_seeded", "1")

    if GalleryCard.query.count() == 0:
        for index, item in enumerate(DEFAULT_GALLERY, start=1):
            card = GalleryCard(
                position=index,
                type=item["type"],
                alt=item["alt"],
                video_url=item["video_url"],
                poster_url=item["poster_url"],
            )
            db.session.add(card)
            db.session.flush()
            for media_index, media_url in enumerate(item["media"], start=1):
                db.session.add(
                    GalleryMedia(
                        card_id=card.id,
                        position=media_index,
                        media_url=media_url,
                    )
                )

    db.session.commit()


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
    db.session.add(
        Review(author=author[:80], quote=quote[:1000], rating=rating_value, approved=False)
    )
    db.session.commit()
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
    db.session.commit()
    flash("Conteudos e horarios atualizados.", "success")
    return redirect(url_for("admin_dashboard") + "#settings")


@app.post("/admin/structure-image")
@admin_required
def update_structure_image():
    image_url = save_upload(
        request.files.get("structure_image"),
        "structure",
        ALLOWED_IMAGE_EXTENSIONS,
    )
    if not image_url:
        flash("Envie uma imagem valida para a estrutura.", "error")
        return redirect(url_for("admin_dashboard") + "#structure")

    set_setting("structure_image", image_url)
    db.session.commit()
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

    position = (db.session.query(db.func.coalesce(db.func.max(PricingItem.position), 0)).scalar() or 0) + 1
    db.session.add(PricingItem(position=position, name=name, price=price))
    db.session.commit()
    flash("Servico adicionado.", "success")
    return redirect(url_for("admin_dashboard") + "#pricing")


@app.post("/admin/pricing/<int:item_id>/update")
@admin_required
def update_pricing(item_id):
    item = db.session.get(PricingItem, item_id)
    if not item:
        flash("Servico nao encontrado.", "error")
        return redirect(url_for("admin_dashboard") + "#pricing")

    name = request.form.get("name", "").strip()
    price = request.form.get("price", "").strip()
    if not name or not price:
        flash("Preencha nome e valor do servico.", "error")
        return redirect(url_for("admin_dashboard") + "#pricing")

    item.name = name
    item.price = price
    db.session.commit()
    flash("Servico atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#pricing")


@app.post("/admin/pricing/<int:item_id>/delete")
@admin_required
def delete_pricing(item_id):
    item = db.session.get(PricingItem, item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Servico removido.", "success")
    return redirect(url_for("admin_dashboard") + "#pricing")


@app.post("/admin/gallery/<int:card_id>/update")
@admin_required
def update_gallery_card(card_id):
    card = db.session.get(GalleryCard, card_id)
    if not card:
        flash("Card de galeria nao encontrado.", "error")
        return redirect(url_for("admin_dashboard") + "#gallery")

    card.type = request.form.get("type", card.type).strip() or card.type
    card.alt = request.form.get("alt", "").strip() or card.alt

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

    card.video_url = video_url
    card.poster_url = poster_url

    if card.type == "slideshow":
        media_urls = [
            line.strip()
            for line in request.form.get("media_urls", "").splitlines()
            if line.strip()
        ]
        for image in request.files.getlist("image_files"):
            saved = save_upload(image, "gallery", ALLOWED_IMAGE_EXTENSIONS)
            if saved:
                media_urls.append(saved)

        GalleryMedia.query.filter_by(card_id=card.id).delete()
        for index, media_url in enumerate(media_urls, start=1):
            db.session.add(GalleryMedia(card_id=card.id, position=index, media_url=media_url))

    db.session.commit()
    flash("Card da galeria atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#gallery")


@app.post("/admin/reviews/<int:review_id>/toggle")
@admin_required
def toggle_review(review_id):
    review = db.session.get(Review, review_id)
    if review:
        review.approved = not review.approved
        db.session.commit()
        flash("Status da avaliacao atualizado.", "success")
    return redirect(url_for("admin_dashboard") + "#reviews")


@app.post("/admin/reviews/<int:review_id>/delete")
@admin_required
def delete_review(review_id):
    review = db.session.get(Review, review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        flash("Avaliacao removida.", "success")
    return redirect(url_for("admin_dashboard") + "#reviews")


with app.app_context():
    db.create_all()
    seed_defaults()


if __name__ == "__main__":
    app.run(debug=True)
