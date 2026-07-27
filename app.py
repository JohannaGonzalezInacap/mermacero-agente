# -*- coding: utf-8 -*-
"""
MermaCero — Agente de IA que responde preguntas sobre control de mermas de
cristalería y recomendación de proveedores de vidrio de borosilicato.

Challenge final — Oracle Next Education (ONE) x Alura.
"""
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from groq import Groq

from document_loader import build_context

load_dotenv()

app = Flask(__name__)

# El cliente lee la variable de entorno GROQ_API_KEY automáticamente.
client = Groq()
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

DOCUMENT_CONTEXT = build_context(
    csv_path=os.path.join(DATA_DIR, "catalogo_proveedores_borosilicato.csv"),
    pdf_path=os.path.join(DATA_DIR, "faq_control_mermas_cristaleria.pdf"),
)

SYSTEM_PROMPT = f"""Eres el agente de MermaCero, una plataforma que ayuda a dueños de bares
a medir sus pérdidas (mermas) de cristalería y a elegir un proveedor de vidrio de borosilicato
adecuado a su negocio.

Responde siempre en español, de forma breve y directa.
Basa tus respuestas SOLO en la información del contexto entregado abajo.
Si la pregunta no se puede responder con esa información, dilo claramente en vez de inventar datos.

--- CONTEXTO ---
{DOCUMENT_CONTEXT}
--- FIN DEL CONTEXTO ---
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True, silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Falta el campo 'question'"}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=500,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        )
        answer = response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001 - se expone el error para depurar el challenge
        return jsonify({"error": str(exc)}), 500

    return jsonify({"question": question, "answer": answer})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
