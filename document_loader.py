# -*- coding: utf-8 -*-
"""
Lee los documentos fuente (CSV de proveedores y PDF de FAQ) y los convierte
en texto plano que se usa como contexto para el agente.
"""
import csv
from pypdf import PdfReader


def load_csv_context(csv_path: str) -> str:
    """Convierte el catálogo de proveedores (CSV) en líneas de texto legibles."""
    lines = ["Catálogo de proveedores de vidrio de borosilicato:"]
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(
                f"- {row['proveedor']}: {row['tipo_producto']}, "
                f"${row['precio_unitario_clp']} CLP por unidad, "
                f"pedido mínimo {row['moq_unidades']} unidades, "
                f"entrega en {row['tiempo_entrega_dias']} días, "
                f"despacho a {row['zona_despacho']}, "
                f"garantía: {row['garantia']}, "
                f"contacto: {row['contacto']}"
            )
    return "\n".join(lines)


def load_pdf_context(pdf_path: str) -> str:
    """Extrae el texto plano del FAQ en PDF."""
    reader = PdfReader(pdf_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def build_context(csv_path: str, pdf_path: str) -> str:
    """Une ambos documentos en un solo bloque de contexto para el system prompt."""
    return load_pdf_context(pdf_path) + "\n\n" + load_csv_context(csv_path)


if __name__ == "__main__":
    # Prueba rápida en local: python document_loader.py
    ctx = build_context(
        "data/catalogo_proveedores_borosilicato.csv",
        "data/faq_control_mermas_cristaleria.pdf",
    )
    print(ctx)
    print(f"\n--- {len(ctx)} caracteres de contexto ---")
