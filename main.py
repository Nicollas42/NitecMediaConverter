import flet as ft
from src.views.HomeView import HomeView

def main(page: ft.Page):
    page.title = "Nitec Media Converter"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.theme_mode = "dark"
    
    # CORREÇÃO: Nova sintaxe do Flet 0.24+
    page.window.width = 800
    page.window.height = 700
    page.window.resizable = False
    
    # Adiciona a view à página
    app = HomeView(page)
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)