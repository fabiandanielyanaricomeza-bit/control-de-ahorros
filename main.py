import flet as ft

def main(page: ft.Page):
    # Centrar todo en la pantalla
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def mostrar_hola(e):
        # Crear la ventana de saludo
        dlg = ft.AlertDialog(
            title=ft.Text("¡Hola!"),
            content=ft.Text("La compilación funciona perfectamente.")
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # Botón principal
    boton = ft.ElevatedButton("Presióname", on_click=mostrar_hola)
    
    page.add(boton)

ft.app(target=main)
