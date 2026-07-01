import re

_PT_HINTS = {
    "qual", "quais", "você", "voce", "não", "nao", "sim", "meu", "minha",
    "quanto", "quantos", "como", "onde", "quando", "porque", "por", "para",
    "pedido", "entrega", "entregas", "pagamento", "pagamentos", "obrigado",
    "cartão", "cartao", "reembolso", "produto", "produtos", "preço", "preco",
    "está", "esta", "são", "sao", "tem", "fazer", "posso", "gostaria",
}

_EN_HINTS = {
    "what", "which", "how", "where", "when", "why", "my", "the", "is", "are",
    "can", "could", "do", "does", "your", "order", "payment", "delivery",
    "product", "products", "refund", "price", "shipping", "please", "would",
}

_PT_DIACRITICS = set("ãõçáéíóúâêôàü")


def detect_language(text: str) -> str:
    words = set(re.findall(r"\w+", text.lower()))
    pt_score = len(words & _PT_HINTS)
    en_score = len(words & _EN_HINTS)
    if any(char in _PT_DIACRITICS for char in text.lower()):
        pt_score += 2
    return "pt" if pt_score > en_score else "en"


_MESSAGES = {
    "blocked": {
        "pt": (
            "Não posso processar essa solicitação. Evite compartilhar dados sensíveis "
            "como CPF ou número de cartão, e reformule sua pergunta."
        ),
        "en": (
            "I can't process this request. Please avoid sharing sensitive data such as "
            "government IDs or card numbers, and rephrase your question."
        ),
    },
    "out_of_scope": {
        "pt": (
            "Desculpe, só consigo ajudar com dúvidas sobre produtos, entregas ou pagamentos."
        ),
        "en": (
            "I'm sorry, I can only help with questions about products, delivery, or payments."
        ),
    },
    "escalation": {
        "pt": (
            "Não consegui resolver totalmente a sua dúvida, então encaminhei para um "
            "atendente humano, que vai entrar em contato em breve."
        ),
        "en": (
            "I wasn't able to fully resolve your question, so I've forwarded it to a human "
            "agent who will follow up with you shortly."
        ),
    },
    "system_error": {
        "pt": (
            "Estamos com um problema técnico no momento, então encaminhei a sua dúvida para "
            "um atendente humano, que vai entrar em contato em breve."
        ),
        "en": (
            "We're experiencing a technical issue right now, so I've forwarded your question "
            "to a human agent who will follow up with you shortly."
        ),
    },
}


def message(key: str, language: str) -> str:
    return _MESSAGES[key].get(language, _MESSAGES[key]["en"])
