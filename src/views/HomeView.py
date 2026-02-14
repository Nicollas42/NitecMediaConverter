import flet as ft
import os
import shutil
import tempfile
from src.services.ConversorService import ConversorService
from src.services.DocumentoService import DocumentoService

class HomeView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        
        # Serviços
        self.midia_service = ConversorService()
        self.doc_service = DocumentoService()
        
        # Estado
        self.caminho_entrada = None
        self.caminho_temp_saida = None
        self.pasta_temp = os.path.join(tempfile.gettempdir(), "NitecConverter")
        self.modo_atual = "midia" # 'midia' ou 'doc'
        
        self.chave_pix = "637c36ed-2fc5-40c3-bd09-117adff9553c"
        
        # Cores
        self.cor_bg = "#0f172a"
        self.cor_painel = "#1e293b"
        self.cor_azul = "#3b82f6"     # Cor Tab Mídia
        self.cor_laranja = "#f97316"  # Cor Tab Doc
        self.cor_verde = "#10b981"
        self.cor_cinza = "#64748b"
        self.cor_ativa = self.cor_azul # Começa azul

        # --- MODAL PIX ---
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nitec Converter v2.0 🚀", text_align="center"),
            content=ft.Column([
                ft.Text("Agora com suporte a Documentos e PDF!", text_align="center"),
                ft.Divider(),
                ft.Container(
                    content=ft.Image(src="assets/pix.png", width=200, height=200, fit=ft.ImageFit.CONTAIN, error_content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED)),
                    alignment=ft.alignment.center
                ),
                ft.Row([
                    ft.Text(f"Chave: {self.chave_pix}", size=12, color="grey"),
                    ft.IconButton(icon=ft.icons.COPY, icon_size=16, on_click=self._copiar_pix)
                ], alignment="center"),
            ], height=400, width=320, alignment="center"),
            actions=[ft.TextButton("Acessar App", on_click=self._fechar_modal)],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

    def did_mount(self):
        self.page.dialog = self.dlg_modal
        self.dlg_modal.open = True
        self.page.update()

    def _fechar_modal(self, e):
        self.dlg_modal.open = False
        self.page.update()

    def _copiar_pix(self, e):
        self.page.set_clipboard(self.chave_pix)
        self.page.snack_bar = ft.SnackBar(ft.Text("Copiado!"), bgcolor="green")
        self.page.snack_bar.open = True
        self.page.update()

    def build(self):
        # --- ABAS DE NAVEGAÇÃO ---
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            indicator_color="white",
            label_color="white",
            unselected_label_color="grey",
            on_change=self._mudanca_aba,
            tabs=[
                # CORREÇÃO AQUI: Usando strings para evitar erros de atributo
                ft.Tab(
                    text="Áudio & Vídeo",
                    icon="play_circle_filled", 
                ),
                ft.Tab(
                    text="Documentos PDF",
                    icon="picture_as_pdf",
                ),
            ],
            divider_color="transparent"
        )

        # --- COMPONENTES INPUT ---
        self.icone_input = ft.Icon(ft.icons.CLOUD_UPLOAD, size=50, color=self.cor_ativa)
        self.texto_input = ft.Text("Selecionar Mídia", color="white")
        
        self.card_upload = ft.Container(
            content=ft.Column([self.icone_input, self.texto_input], alignment="center", horizontal_alignment="center"),
            width=300, height=200,
            border=ft.border.all(2, self.cor_ativa), border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, self.cor_ativa),
            on_click=lambda _: self.picker_entrada.pick_files(), ink=True
        )

        self.dd_formato = ft.Dropdown(
            label="Converter para", width=300, value="mp3", border_color=self.cor_ativa,
            options=self._opcoes_midia()
        )

        self.btn_converter = ft.ElevatedButton(
            "CONVERTER MÍDIA", icon=ft.icons.BOLT,
            style=ft.ButtonStyle(bgcolor=self.cor_ativa, color="white", padding=20),
            width=300, on_click=self._iniciar_conversao, disabled=True
        )

        self.txt_progresso = ft.Text("0%", color=self.cor_ativa, visible=False)
        self.barra_progresso = ft.ProgressBar(width=300, color=self.cor_ativa, bgcolor="#333", visible=False)

        # --- COMPONENTES OUTPUT ---
        self.icone_output = ft.Icon(ft.icons.DOWNLOAD, size=50, color=self.cor_cinza)
        self.texto_output = ft.Text("Aguardando...", color=self.cor_cinza)
        
        self.card_download = ft.Container(
            content=ft.Column([self.icone_output, self.texto_output], alignment="center", horizontal_alignment="center"),
            width=300, height=200,
            border=ft.border.all(2, self.cor_cinza), border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, self.cor_cinza)
        )

        self.btn_salvar = ft.ElevatedButton(
            "BAIXAR ARQUIVO", icon=ft.icons.SAVE_ALT,
            style=ft.ButtonStyle(bgcolor=self.cor_cinza, color="white", padding=20),
            width=300,
            on_click=lambda _: self.picker_saida.save_file(file_name=os.path.basename(self.caminho_temp_saida)),
            disabled=True
        )
        
        self.btn_reset = ft.TextButton("Limpar", icon=ft.icons.REFRESH, visible=False, on_click=self._resetar)

        # --- PICKERS ---
        self.picker_entrada = ft.FilePicker(on_result=self._arquivo_selecionado)
        self.picker_saida = ft.FilePicker(on_result=self._salvar_arquivo)
        self.page.overlay.extend([self.picker_entrada, self.picker_saida])

        # --- LAYOUT FINAL ---
        coluna_esquerda = ft.Container(
            padding=20, bgcolor=self.cor_painel, border_radius=15,
            content=ft.Column([
                ft.Text("1. ENTRADA", weight="bold", color="white", size=16),
                ft.Divider(color="transparent", height=5),
                self.card_upload,
                ft.Divider(color="transparent", height=10),
                self.dd_formato,
                ft.Divider(color="transparent", height=10),
                self.btn_converter,
                ft.Column([self.txt_progresso, self.barra_progresso], spacing=5)
            ], horizontal_alignment="center")
        )

        coluna_direita = ft.Container(
            padding=20, bgcolor=self.cor_painel, border_radius=15,
            content=ft.Column([
                ft.Text("2. SAÍDA", weight="bold", color=self.cor_verde, size=16),
                ft.Divider(color="transparent", height=5),
                self.card_download,
                ft.Divider(color="transparent", height=10),
                ft.Container(height=60), 
                self.btn_salvar,
                self.btn_reset
            ], horizontal_alignment="center")
        )

        return ft.Container(
            expand=True, bgcolor=self.cor_bg, padding=20,
            content=ft.Column([
                self.tabs,
                ft.Divider(color="transparent", height=10),
                ft.Row(
                    controls=[coluna_esquerda, coluna_direita],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=30,
                    scroll=ft.ScrollMode.AUTO
                )
            ])
        )

    # --- LISTAS DE OPÇÕES ---
    def _opcoes_midia(self):
        return [
            ft.dropdown.Option("mp3"), ft.dropdown.Option("mp4"),
            ft.dropdown.Option("wav"), ft.dropdown.Option("avi"),
            ft.dropdown.Option("mkv"), ft.dropdown.Option("gif"),
        ]

    def _opcoes_doc(self):
        return [
            ft.dropdown.Option("pdf_to_docx", text="PDF para Word"),
            ft.dropdown.Option("img_to_pdf", text="Imagem para PDF"),
        ]

    # --- LÓGICA ---
    def _mudanca_aba(self, e):
        if e.control.selected_index == 0:
            self.modo_atual = "midia"
            self.cor_ativa = self.cor_azul
            self.dd_formato.options = self._opcoes_midia()
            self.dd_formato.value = "mp3"
            self.btn_converter.text = "CONVERTER MÍDIA"
            self.texto_input.value = "Selecionar Mídia"
        else:
            self.modo_atual = "doc"
            self.cor_ativa = self.cor_laranja
            self.dd_formato.options = self._opcoes_doc()
            self.dd_formato.value = "pdf_to_docx"
            self.btn_converter.text = "CONVERTER DOC"
            self.texto_input.value = "Selecionar Documento"

        self.icone_input.color = self.cor_ativa
        self.card_upload.border.color = self.cor_ativa
        self.card_upload.bgcolor = ft.colors.with_opacity(0.1, self.cor_ativa)
        self.dd_formato.border_color = self.cor_ativa
        self.btn_converter.style.bgcolor = self.cor_ativa
        self.barra_progresso.color = self.cor_ativa
        self.txt_progresso.color = self.cor_ativa
        
        self._resetar(None)
        self.update()

    def _arquivo_selecionado(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.caminho_entrada = e.files[0].path
            nome = e.files[0].name
            if len(nome) > 25: nome = nome[:22] + "..."
            self.icone_input.name = ft.icons.CHECK_CIRCLE
            self.texto_input.value = nome
            self.btn_converter.disabled = False
            self.update()

    def _iniciar_conversao(self, e):
        if not self.caminho_entrada: return
        self.btn_converter.disabled = True
        self.btn_converter.text = "PROCESSANDO..."
        self.txt_progresso.visible = True
        self.barra_progresso.visible = True
        self.update()

        try:
            formato = self.dd_formato.value
            
            if self.modo_atual == "midia":
                gerador = self.midia_service.converter_com_progresso(
                    self.caminho_entrada, formato, self.pasta_temp
                )
            else:
                gerador = self.doc_service.converter_documento(
                    self.caminho_entrada, formato, self.pasta_temp
                )

            for progresso, caminho_final in gerador:
                self.barra_progresso.value = progresso
                self.txt_progresso.value = f"{int(progresso * 100)}%"
                self.update()
                if caminho_final:
                    self.caminho_temp_saida = caminho_final
            self._ativar_sucesso()
            
        except Exception as erro:
            print(erro)
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Erro: {erro}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()
            self.btn_converter.disabled = False
            self.btn_converter.text = "TENTAR NOVAMENTE"

    def _ativar_sucesso(self):
        self.icone_output.name = ft.icons.CHECK_CIRCLE
        self.icone_output.color = self.cor_verde
        self.texto_output.value = "Concluído!"
        self.card_download.border = ft.border.all(2, self.cor_verde)
        self.btn_salvar.style.bgcolor = self.cor_verde
        self.btn_salvar.disabled = False
        self.btn_reset.visible = True
        self.btn_converter.text = "CONCLUÍDO"
        self.barra_progresso.visible = False
        self.txt_progresso.visible = False
        self.update()

    def _salvar_arquivo(self, e: ft.FilePickerResultEvent):
        if e.path and self.caminho_temp_saida:
            try:
                shutil.copy(self.caminho_temp_saida, e.path)
                self.page.snack_bar = ft.SnackBar(ft.Text("Salvo!"), bgcolor="green")
                self.page.snack_bar.open = True
                self.page.update()
            except Exception: pass

    def _resetar(self, e):
        self.caminho_entrada = None
        self.icone_input.name = ft.icons.CLOUD_UPLOAD
        
        texto_padrao = "Selecionar Mídia" if self.modo_atual == "midia" else "Selecionar Documento"
        self.texto_input.value = texto_padrao
        
        self.btn_converter.text = "CONVERTER"
        self.btn_converter.disabled = True
        
        self.icone_output.name = ft.icons.DOWNLOAD
        self.icone_output.color = self.cor_cinza
        self.texto_output.value = "Aguardando..."
        self.card_download.border = ft.border.all(2, self.cor_cinza)
        self.btn_salvar.style.bgcolor = self.cor_cinza
        self.btn_salvar.disabled = True
        self.btn_reset.visible = False
        self.update()