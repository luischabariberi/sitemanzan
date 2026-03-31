from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    business = {
        "name": "Manzan Barber",
        "badge": "Sejam Bem-Vindos",
        "hero_kicker": "",
        "headline_top": "",
        "headline_bottom": "",
        "description": (
            "Uma experiência old school com atendimento diferenciado, "
            "acabamento refinado e um ambiente criado para quem valoriza presença."
        ),
        "address": "R. Castro Alves, 84 - Chafariz, Sacramento - MG",
        "hours_week": "Seg a Sex - 09:00 as 19:00",
        "hours_sat": "Sábado - 09:00 as 18:00",
        "hours_sun": "Domingo - Fechado",
        "whatsapp_link": "https://sites.appbarber.com.br/agendamento/manzanbarbearia-3xbv?fbclid=PAVERFWAQ4zwVleHRuA2FlbQIxMQBzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAad50Ln_bvW2hXom66ewBmtL1LknDMmIwy-n94fWAUV_dRCgDCF4p-D3vn3Apw_aem_fZp7wKHpv1D32TpYn-6-wQ",
        "maps_link": "https://maps.app.goo.gl/CkKm6DkmB15PJuP78?g_st=iw",
        "offer_title": "Experiência Clássica",
        "offer_text": "Toalha quente, navalha, cuidado nos detalhes e atendimento exclusivo.",
        "hero_cta": "Ver fotos",
    }

    about_me = {
        "eyebrow": "Sobre mim",
        "title": "Muito além da cadeira, aqui você encontra identidade, estilo e personalidade.",
        "paragraphs": [
            "Sou o rosto por trás da Êxodo Barbearia e transformei minha paixão por estilo, atendimento e presença em uma experiência pensada nos detalhes.",
            "Meu objetivo e entregar mais do que um corte: quero que cada cliente saia daqui se sentindo confiante, alinhado e com uma imagem que realmente represente quem ele e.",
            "Cada atendimento é feito com atenção, técnica e respeito ao seu estilo. A proposta da Êxodo e unir profissionalismo, ambiente marcante e uma conexão verdadeira com cada cliente.",
        ],
    }

    highlights = [
        "Atmosfera temática com referências clássicas de barbearia tradicional.",
        "Atendimento com horário marcado, pontualidade e experiência personalizada.",
        "Técnica, ritual e acabamento profissional do corte a barba.",
        "Ambiente confortável para transformar um simples atendimento em experiência.",
    ]

    pricing = [
        {"name": "Barba", "price": "R$30,00"},
        {"name": "Barba com Barboterapia", "price": "R$40,00"},
        {"name": "Cabelo - Barba e Barboterapia", "price": "R$70,00"},
        {"name": "Corte", "price": "R$40,00"},
        {"name": "Corte - Barba", "price": "R$60,00"},
        {"name": "Corte - Barba - Pigmentacao", "price": "R$85,00"},
        {"name": "Corte e Pigmentacao", "price": "R$55,00"},
        {"name": "Corte Infantil", "price": "R$45,00"},
        {"name": "Pezinho", "price": "R$15,00"},
        {"name": "Sobrancelha", "price": "R$15,00"},
    ]

    testimonials = [
        {
            "quote": "Ambiente impecável, atendimento pontual e o corte sempre vem exatamente como eu preciso.",
            "author": "Rafael M.",
        },
        {
            "quote": "A barba ficou muito acima do que eu encontrava em outras barbearias. Virou meu lugar fixo.",
            "author": "Lucas A.",
        },
        {
            "quote": "Da recepcao ao acabamento final, da para sentir que tudo foi pensado para entregar nivel premium.",
            "author": "Thiago S.",
        },
    ]

    gallery = [
        {
            "src": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?auto=format&fit=crop&w=900&q=80",
            "alt": "Barbeiro finalizando corte masculino com maquina",
        },
        {
            "src": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=900&q=80",
            "alt": "Cliente em cadeira de barbearia premium",
        },
        {
            "src": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?auto=format&fit=crop&w=900&q=80",
            "alt": "Detalhe de corte degrade masculino",
        },
        {
            "src": "https://images.unsplash.com/photo-1517832606299-7ae9b720a186?auto=format&fit=crop&w=900&q=80",
            "alt": "Interior de barbearia com visual sofisticado",
        },
    ]

    return render_template(
        'index.html',
        business=business,
        about_me=about_me,
        highlights=highlights,
        pricing=pricing,
        testimonials=testimonials,
        gallery=gallery,
    )


if __name__ == '__main__':
    app.run(debug=True)
