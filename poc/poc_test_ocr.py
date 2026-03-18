import os
import fitz # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import subprocess

def setup_test_files():
    print("Creazione file PDF e Immagine di test...")
    
    pdf_path = "test_doc.pdf"
    img_path = "test_img.png"
    
    # Crea PDF di test
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Questo e' un documento di test generato digitalmente.\nServe a verificare che PyMuPDF funzioni correttamente.")
    doc.save(pdf_path)
    doc.close()
    
    # Crea immagine di test con testo
    img = Image.new('RGB', (400, 150), color = (255, 255, 255))
    d = ImageDraw.Draw(img)
    # Testo base leggibile dall'OCR
    d.text((20, 50), "Testo in un'immagine.", fill=(0,0,0))
    d.text((20, 80), "Verifica Tesseract OCR.", fill=(0,0,0))
    img.save(img_path)
    
    return pdf_path, img_path

def test_tool_lettura(pdf_path, img_path):
    tool_path = os.path.join(os.path.dirname(__file__), "..", "tools", "tool_lettura.py")
    
    print("\n--- TEST: LETTURA PDF ---")
    result_pdf = subprocess.run(["python", tool_path, pdf_path], capture_output=True, text=True)
    print("Output:\n" + result_pdf.stdout)
    if result_pdf.stderr:
        print("Errori:\n" + result_pdf.stderr)
        
    print("\n--- TEST: LETTURA IMMAGINE (OCR) ---")
    result_img = subprocess.run(["python", tool_path, img_path], capture_output=True, text=True)
    print("Output:\n" + result_img.stdout)
    if result_img.stderr:
        print("Errori:\n" + result_img.stderr)

if __name__ == "__main__":
    pdf, img = setup_test_files()
    test_tool_lettura(pdf, img)
    
    # Pulizia
    os.remove(pdf)
    os.remove(img)
