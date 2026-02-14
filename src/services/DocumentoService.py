import os
from pypdf import PdfReader, PdfWriter
from pdf2docx import Converter
import img2pdf # Vamos usar se quiser imagem -> pdf, mas por enquanto vamos focar no básico
from PIL import Image

class DocumentoService:
    def converter_documento(self, caminho_entrada: str, acao: str, pasta_temp: str):
        """
        Gerenciador de conversões de documentos.
        Retorna um generator para barra de progresso.
        """
        nome_arquivo = os.path.basename(caminho_entrada)
        nome_base = os.path.splitext(nome_arquivo)[0]
        
        # Cria pasta temp se não existir
        os.makedirs(pasta_temp, exist_ok=True)

        try:
            # --- PDF PARA WORD ---
            if acao == "pdf_to_docx":
                caminho_saida = os.path.join(pasta_temp, f"{nome_base}.docx")
                yield 0.1, None
                
                # Usa a lib pdf2docx
                cv = Converter(caminho_entrada)
                yield 0.3, None
                
                # A conversão real (sem progresso detalhado, infelizmente)
                cv.convert(caminho_saida, start=0, end=None)
                cv.close()
                
                yield 1.0, caminho_saida

            # --- IMAGEM PARA PDF ---
            elif acao == "img_to_pdf":
                caminho_saida = os.path.join(pasta_temp, f"{nome_base}.pdf")
                yield 0.2, None
                
                image = Image.open(caminho_entrada)
                pdf_bytes = image.convert('RGB')
                pdf_bytes.save(caminho_saida)
                
                yield 1.0, caminho_saida

            # --- PDF PARA IMAGEM (CAPA) ---
            elif acao == "extract_img":
                # Extrai apenas a primeira página como exemplo
                # Requereria bibliotecas mais pesadas para todas as páginas
                pass 

        except Exception as e:
            print(f"Erro documento: {e}")
            raise e