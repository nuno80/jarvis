import sys
import os
import argparse
import fitz  # PyMuPDF
import cv2
import pytesseract
from PIL import Image
from pathlib import Path

# Logger centralizzato JARVIS
sys.path.insert(0, str(Path(__file__).parent.parent))
from logger import get_logger

logger = get_logger("jarvis.tool.lettura")

# Configurazione Tesseract per Windows (modifica se in un path diverso e non in PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_pdf(pdf_path):
    """Estrae testo da un PDF testuale."""
    logger.info(f"Lettura PDF: {pdf_path}")
    testo_completo = ""
    try:
        pdf_document = fitz.open(pdf_path)
        for num_pagina in range(len(pdf_document)):
            pagina = pdf_document.load_page(num_pagina)
            testo_completo += pagina.get_text() + "\n"
        pdf_document.close()
        logger.info(f"PDF letto con successo ({len(testo_completo)} caratteri).")
        return testo_completo.strip()
    except Exception as e:
        logger.exception(f"Lettura PDF fallita: {pdf_path}")
        return f"[ERRORE] Lettura PDF fallita: {str(e)}"


def extract_text_from_image(image_path):
    """Estrae testo da un'immagine usando Tesseract OCR."""
    logger.info(f"OCR immagine: {image_path}")
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        pil_img = Image.fromarray(thresh)
        testo = pytesseract.image_to_string(pil_img, lang="ita+eng")
        logger.info(f"OCR completato ({len(testo)} caratteri).")
        return testo.strip()
    except Exception as e:
        logger.exception(f"OCR immagine fallita: {image_path}")
        return f"[ERRORE] Lettura Immagine tramite OCR fallita: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Tool di Lettura Jarvis (PDF e Immagini OCR)")
    parser.add_argument("filepath", type=str, help="Il percorso del file da leggere.")
    args = parser.parse_args()
    file_path = args.filepath

    if not os.path.exists(file_path):
        logger.error(f"File non trovato: '{file_path}'")
        print(f"[ERRORE] Il file '{file_path}' non esiste.")
        sys.exit(1)

    estensione = os.path.splitext(file_path)[1].lower()

    if estensione == ".pdf":
        risultato = extract_text_from_pdf(file_path)
    elif estensione in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        risultato = extract_text_from_image(file_path)
    else:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                risultato = f.read()
            logger.info(f"Letto file testo semplice: {file_path}")
        except Exception as e:
            risultato = f"[ERRORE] Formato file non supportato: {estensione}"
            logger.error(risultato)

    # ZeroClaw cattura lo STDOUT come output del tool
    print(risultato)


if __name__ == "__main__":
    main()
