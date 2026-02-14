import flet as ft
import os
import shutil
from src.services.ConversorService import ConversorService

class HomeView(ft.UserControl):
    """
    Interface principal do conversor.
    Layout fixo para evitar quebras de renderização.
    """

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.conversor_service = ConversorService()
        
        # Estado
        self.caminho_entrada = None
        self.caminho_temp_saida = None
        self.pasta_temp = os.path.join(os.getcwd(), "temp_files")
        
        # Cores Sólidas
        self.cor_bg = "#0f172a"
        self.cor_painel = "#1e293b"
        self.cor_azul = "#3b82f6"
        self.cor_verde = "#10b981"
        self.cor_cinza = "#64748b"

    def build(self):
        # --- COMPONENTES ESQUERDA (INPUT) ---
        
        self.icone_input = ft.Icon(ft.icons.CLOUD_UPLOAD, size=50, color=self.cor_azul)
        self.texto_input = ft.Text("Selecionar Arquivo", color="white")
        
        # Card de Upload com TAMANHO FIXO para não quebrar
        self.card_upload = ft.Container(
            content=ft.Column([
                self.icone_input,
                self.texto_input
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=300,  # Largura travada
            height=200, # Altura travada
            border=ft.border.all(2, self.cor_azul),
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, self.cor_azul),
            on_click=lambda _: self.picker_entrada.pick_files(),
            ink=True
        )

        self.dd_formato = ft.Dropdown(
            label="Formato",
            width=300,
            options=[
                ft.dropdown.Option("mp3"), ft.dropdown.Option("mp4"),
                ft.dropdown.Option("wav"), ft.dropdown.Option("avi"),
                ft.dropdown.Option("mkv"), ft.dropdown.Option("gif"),
            ],
            value="mp3",
            border_color=self.cor_azul
        )

        self.btn_converter = ft.ElevatedButton(
            "CONVERTER",
            icon=ft.icons.BOLT,
            style=ft.ButtonStyle(bgcolor=self.cor_azul, color="white", padding=20),
            width=300,
            on_click=self._iniciar_conversao,
            disabled=True
        )

        # Progresso
        self.txt_progresso = ft.Text("0%", color=self.cor_azul, visible=False)
        self.barra_progresso = ft.ProgressBar(width=300, color=self.cor_azul, bgcolor="#333", visible=False)

        # Coluna Esquerda
        coluna_esquerda = ft.Container(
            padding=20,
            bgcolor=self.cor_painel,
            border_radius=15,
            content=ft.Column([
                ft.Text("1. ENTRADA", weight="bold", color=self.cor_azul, size=16),
                ft.Divider(color="transparent", height=10),
                self.card_upload,
                ft.Divider(color="transparent", height=10),
                self.dd_formato,
                ft.Divider(color="transparent", height=10),
                self.btn_converter,
                ft.Column([self.txt_progresso, self.barra_progresso], spacing=5)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        # --- COMPONENTES DIREITA (OUTPUT) ---
        
        self.icone_output = ft.Icon(ft.icons.DOWNLOAD, size=50, color=self.cor_cinza)
        self.texto_output = ft.Text("Aguardando...", color=self.cor_cinza)

        # Card de Download com TAMANHO FIXO
        self.card_download = ft.Container(
            content=ft.Column([
                self.icone_output,
                self.texto_output
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=300,  # Largura travada
            height=200, # Altura travada
            border=ft.border.all(2, self.cor_cinza),
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, self.cor_cinza)
        )

        self.btn_salvar = ft.ElevatedButton(
            "BAIXAR ARQUIVO",
            icon=ft.icons.SAVE_ALT,
            style=ft.ButtonStyle(bgcolor=self.cor_cinza, color="white", padding=20),
            width=300,
            on_click=lambda _: self.picker_saida.save_file(file_name=os.path.basename(self.caminho_temp_saida)),
            disabled=True
        )
        
        self.btn_reset = ft.TextButton("Limpar", icon=ft.icons.REFRESH, visible=False, on_click=self._resetar)

        # Coluna Direita
        coluna_direita = ft.Container(
            padding=20,
            bgcolor=self.cor_painel,
            border_radius=15,
            content=ft.Column([
                ft.Text("2. SAÍDA", weight="bold", color=self.cor_verde, size=16),
                ft.Divider(color="transparent", height=10),
                self.card_download,
                ft.Divider(color="transparent", height=10),
                # Espaço vazio para alinhar altura com o lado esquerdo
                ft.Container(height=60), 
                self.btn_salvar,
                self.btn_reset
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        # --- SETUP ---
        self.picker_entrada = ft.FilePicker(on_result=self._arquivo_selecionado)
        self.picker_saida = ft.FilePicker(on_result=self._salvar_arquivo)
        self.page.overlay.extend([self.picker_entrada, self.picker_saida])

        # Layout Principal (Com Scroll para garantir que cabe tudo)
        return ft.Container(
            expand=True,
            bgcolor=self.cor_bg,
            padding=30,
            alignment=ft.alignment.center,
            content=ft.Row(
                controls=[coluna_esquerda, coluna_direita],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=30,
                scroll=ft.ScrollMode.AUTO # Permite rolar se a tela for pequena
            )
        )

    # --- LÓGICA ---

    def _arquivo_selecionado(self, e: ft.FilePickerResultEvent):
        if e.files:
            self._limpar_temp()
            self.caminho_entrada = e.files[0].path
            
            # Atualiza UI
            nome = e.files[0].name
            if len(nome) > 25: nome = nome[:22] + "..."
            
            self.icone_input.name = ft.icons.CHECK_CIRCLE
            self.texto_input.value = nome
            self.card_upload.border = ft.border.all(2, self.cor_azul)
            self.btn_converter.disabled = False
            self._resetar_direita()
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
            gerador = self.conversor_service.converter_com_progresso(
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
            self.btn_converter.disabled = False
            self.btn_converter.text = "CONVERTER"

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
            except Exception:
                pass

    def _resetar(self, e):
        self.caminho_entrada = None
        self._limpar_temp()
        
        # Reseta Esquerda
        self.icone_input.name = ft.icons.CLOUD_UPLOAD
        self.texto_input.value = "Selecionar Arquivo"
        self.card_upload.border = ft.border.all(2, self.cor_azul)
        self.btn_converter.text = "CONVERTER"
        self.btn_converter.disabled = True
        
        # Reseta Direita
        self._resetar_direita()
        self.update()

    def _resetar_direita(self):
        self.icone_output.name = ft.icons.DOWNLOAD
        self.icone_output.color = self.cor_cinza
        self.texto_output.value = "Aguardando..."
        self.card_download.border = ft.border.all(2, self.cor_cinza)
        self.btn_salvar.style.bgcolor = self.cor_cinza
        self.btn_salvar.disabled = True
        self.btn_reset.visible = False

    def _limpar_temp(self):
        if os.path.exists(self.pasta_temp):
            shutil.rmtree(self.pasta_temp)