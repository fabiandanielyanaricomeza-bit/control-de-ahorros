import flet as ft
import csv
import os
from datetime import datetime

archivo = 'mis_ahorros.csv'

def main(page: ft.Page):
    # --- 1. CONFIGURACIÓN DE LA PANTALLA ---
    page.title = "Control de Ahorros"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.AUTO 
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    if not os.path.exists(archivo):
        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Fecha', 'Monto', 'Descripción'])

    # --- 2. LÓGICA DE RESUMEN ---
    def obtener_resumen():
        ingresos = 0.0
        gastos = 0.0
        if os.path.exists(archivo):
            with open(archivo, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for fila in reader:
                    if len(fila) >= 2:
                        try:
                            monto = float(fila[1])
                            if monto > 0: ingresos += monto
                            else: gastos += monto
                        except ValueError:
                            pass
        return ingresos, gastos, ingresos + gastos

    ingresos_val, gastos_val, beneficio_val = obtener_resumen()

    # --- 3. ELEMENTOS VISUALES PRINCIPALES ---
    txt_ingresos = ft.Text(f"{ingresos_val:.2f}", color="#4CAF50") # Verde Hex
    txt_gastos = ft.Text(f"{gastos_val:.2f}", color="#F44336") # Rojo Hex
    txt_beneficio = ft.Text(f"{beneficio_val:.2f}", weight="bold")

    tabla_resumen = ft.DataTable(
        border_radius=10,
        columns=[
            ft.DataColumn(ft.Text("Concepto", weight="bold")),
            ft.DataColumn(ft.Text("Monto", weight="bold"), numeric=True),
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text("Ingresos (+)", color="#4CAF50", weight="bold")), ft.DataCell(txt_ingresos)]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Gastos (-)", color="#F44336", weight="bold")), ft.DataCell(txt_gastos)]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("BENEFICIO", weight="bold")), ft.DataCell(txt_beneficio)]),
        ]
    )

    def actualizar_pantalla():
        i, g, b = obtener_resumen()
        txt_ingresos.value = f"{i:.2f}"
        txt_gastos.value = f"{g:.2f}"
        txt_beneficio.value = f"{b:.2f}"
        page.update()

    def cerrar_modal(dialogo):
        dialogo.open = False
        page.update()

    def abrir_modal(dialogo):
        dialogo.open = True
        page.update()

    # --- 4. MODALES DE TEMAS Y DETALLES ---
    dlg_agregar = ft.AlertDialog(content=ft.Container())
    dlg_historial = ft.AlertDialog(content=ft.Container())
    dlg_confirmar = ft.AlertDialog(content=ft.Container())
    dlg_buscar = ft.AlertDialog(content=ft.Container())
    
    def cambiar_tema(e):
        if e.control.value == "claro":
            page.theme_mode = ft.ThemeMode.LIGHT
        elif e.control.value == "oscuro":
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM
        page.update()

    opciones_tema = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="claro", label="Claro"),
            ft.Radio(value="oscuro", label="Oscuro"),
            ft.Radio(value="sistema", label="Del celular")
        ]),
        on_change=cambiar_tema,
        value="sistema"
    )

    dlg_temas = ft.AlertDialog(
        title=ft.Text("Seleccionar Tema"),
        content=opciones_tema,
        actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_modal(dlg_temas))]
    )

    dlg_detalles = ft.AlertDialog(
        title=ft.Text("Detalles de la App", weight="bold"),
        content=ft.Column([
            ft.Text("Versión: 1.0.0"),
            ft.Text("Desarrollador: Fabián"),
            ft.Text("Contacto: mail de un fabi")
        ], tight=True),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_modal(dlg_detalles))]
    )

    page.overlay.extend([dlg_agregar, dlg_historial, dlg_confirmar, dlg_buscar, dlg_temas, dlg_detalles])

    # --- 5. SOLUCIÓN BLINDADA: BOTONES DE TEXTO EN LA BARRA SUPERIOR ---
    page.appbar = ft.AppBar(
        title=ft.Text("BILLETERA", weight=ft.FontWeight.BOLD, color="#1A237E"),
        center_title=False,
        bgcolor="#E8EAF6",
        actions=[
            ft.TextButton("TEMA", on_click=lambda e: abrir_modal(dlg_temas), style=ft.ButtonStyle(color="#1A237E")),
            ft.TextButton("INFO", on_click=lambda e: abrir_modal(dlg_detalles), style=ft.ButtonStyle(color="#1A237E")),
            ft.Container(width=5)
        ]
    )

    # --- 6. LÓGICA MODAL AGREGAR ---
    input_monto = ft.TextField(label="Monto (+ o -)")
    input_desc = ft.TextField(label="Descripción")

    def guardar_transaccion(e):
        try:
            if not input_monto.value:
                raise ValueError("Vacío")
            monto = float(input_monto.value)
            desc = input_desc.value.strip() if input_desc.value else "Sin descripción"

            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(archivo, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([fecha_actual, monto, desc])

            cerrar_modal(dlg_agregar)
            actualizar_pantalla()

            page.overlay.append(ft.SnackBar(ft.Text("¡Guardado exitosamente!"), open=True))
            page.update()
        except ValueError:
            page.overlay.append(ft.SnackBar(ft.Text("Error: Ingresa un número válido."), open=True))
            page.update()

    def abrir_agregar(e):
        input_monto.value = ""
        input_desc.value = ""
        dlg_agregar.title = ft.Text("Agregar Registro")
        dlg_agregar.content = ft.Column([input_monto, input_desc], tight=True)
        dlg_agregar.actions = [
            ft.TextButton("Cancelar", on_click=lambda ev: cerrar_modal(dlg_agregar)),
            ft.ElevatedButton("Guardar", on_click=guardar_transaccion, bgcolor="#1A237E", color="#FFFFFF")
        ]
        abrir_modal(dlg_agregar)

    # --- 7. LÓGICA MODAL HISTORIAL CON ELIMINACIÓN ---
    container_lista_historial = ft.Column([], scroll=ft.ScrollMode.AUTO, height=220)
    items_historial = []
    modo_borrar = [False]

    def ejecutar_eliminacion_final(ev, filas_a_borrar):
        filas_conservadas = []
        if os.path.exists(archivo):
            with open(archivo, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                cabecera = next(reader, None)
                if cabecera:
                    filas_conservadas.append(cabecera)
                for fila in reader:
                    if fila not in filas_a_borrar:
                        filas_conservadas.append(fila)

        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(filas_conservadas)

        cerrar_modal(dlg_confirmar)
        cerrar_modal(dlg_historial)
        actualizar_pantalla()

        page.overlay.append(ft.SnackBar(ft.Text("Registros eliminados correctamente."), open=True))
        page.update()

    def abrir_confirmacion_borrado(filas_a_borrar):
        detalles_column = ft.Column([], scroll=ft.ScrollMode.AUTO, height=150)
        for f in filas_a_borrar:
            detalles_column.controls.append(ft.Text(f"• [{f[1]}] {f[2]} ({f[0]})", size=12))

        dlg_confirmar.title = ft.Text("¿Estás seguro?", color="#F44336", weight="bold")
        dlg_confirmar.content = ft.Column([
            ft.Text("Se eliminarán permanentemente los siguientes elementos:"),
            ft.Divider(),
            detalles_column
        ], tight=True, width=300)
        dlg_confirmar.actions = [
            ft.TextButton("Cancelar", on_click=lambda ev: cerrar_modal(dlg_confirmar)),
            ft.ElevatedButton("Sí, Eliminar", on_click=lambda ev: ejecutar_eliminacion_final(ev, filas_a_borrar), bgcolor="#F44336", color="#FFFFFF")
        ]
        abrir_modal(dlg_confirmar)

    def alternar_modo_eliminacion(btn_activar_eliminar):
        if not modo_borrar[0]:
            modo_borrar[0] = True
            for chk, _ in items_historial:
                chk.visible = True
            btn_activar_eliminar.text = "Confirmar Borrado"
            btn_activar_eliminar.bgcolor = "#F44336"
            btn_activar_eliminar.color = "#FFFFFF"
        else:
            seleccionados = [fila for chk, fila in items_historial if chk.value]
            if not seleccionados:
                page.overlay.append(ft.SnackBar(ft.Text("No seleccionaste ningún registro."), open=True))
                page.update()
                return
            abrir_confirmacion_borrado(seleccionados)
        page.update()

    def cargar_filas_historial():
        container_lista_historial.controls.clear()
        items_historial.clear()

        if os.path.exists(archivo):
            with open(archivo, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for fila in reader:
                    if len(fila) >= 3:
                        chk = ft.Checkbox(visible=False)
                        items_historial.append((chk, fila))

                        fila_ui = ft.Row([
                            chk,
                            ft.Text(fila[0], size=10, width=105),
                            ft.Text(fila[1], size=11, width=55, weight="bold"),
                            ft.Text(fila[2], size=11, width=120, overflow=ft.TextOverflow.ELLIPSIS)
                        ], spacing=5)
                        container_lista_historial.controls.append(fila_ui)

        if not items_historial:
            container_lista_historial.controls.append(ft.Text("Sin registros en el historial.", color="#9E9E9E"))

    def abrir_historial(e):
        modo_borrar[0] = False
        cargar_filas_historial()

        btn_activar_eliminar = ft.ElevatedButton("Eliminar", bgcolor="#FFCDD2", color="#B71C1C")
        btn_activar_eliminar.on_click = lambda ev: alternar_modo_eliminacion(btn_activar_eliminar)

        dlg_historial.title = ft.Text("Historial Completo")
        dlg_historial.content = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Fecha", weight="bold", size=11, width=105),
                    ft.Text("Monto", weight="bold", size=11, width=55),
                    ft.Text("Detalle", weight="bold", size=11, width=110),
                ]),
                ft.Divider(height=5),
                container_lista_historial
            ]),
            height=320,
            width=335
        )
        dlg_historial.actions = [
            btn_activar_eliminar,
            ft.TextButton("Cerrar", on_click=lambda ev: cerrar_modal(dlg_historial))
        ]
        dlg_historial.actions_alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        abrir_modal(dlg_historial)

    # --- 8. LÓGICA MODAL BUSCAR POR FECHA ---
    in_dia = ft.TextField(label="Día (ej: 5)", width=90)
    in_mes = ft.TextField(label="Mes (ej: 8)", width=90)
    in_anio = ft.TextField(label="Año (ej: 2026)", width=120)
    resultados_column = ft.Column([], scroll=ft.ScrollMode.AUTO, height=180)

    def ejecutar_busqueda(ev):
        resultados_column.controls.clear()

        d_val = in_dia.value.strip() if in_dia.value else ""
        m_val = in_mes.value.strip() if in_mes.value else ""
        a_val = in_anio.value.strip() if in_anio.value else ""

        if not d_val and not m_val and not a_val:
            resultados_column.controls.append(ft.Text("Ingresa al menos un dato.", color="#F44336"))
            page.update()
            return

        d = d_val.zfill(2) if d_val else ""
        m = m_val.zfill(2) if m_val else ""
        a = a_val

        partes = []
        if a: partes.append(a)
        if m: partes.append(m)
        if d: partes.append(d)
        fecha_busqueda = "-".join(partes)

        encontrados = 0
        if os.path.exists(archivo):
            with open(archivo, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for fila in reader:
                    if len(fila) >= 3 and fecha_busqueda in fila[0]:
                        resultados_column.controls.append(
                            ft.Text(f"• [{fila[1]}] {fila[2]} ({fila[0]})")
                        )
                        encontrados += 1

        if encontrados == 0:
            resultados_column.controls.append(ft.Text("No se encontraron registros.", color="#F44336"))
        page.update()

    def abrir_buscar(e):
        in_dia.value = ""
        in_mes.value = ""
        in_anio.value = ""
        resultados_column.controls.clear()

        dlg_buscar.title = ft.Text("Buscar por Fecha")
        dlg_buscar.content = ft.Column([
            ft.Row([in_dia, in_mes], spacing=10),
            in_anio,
            ft.ElevatedButton("Buscar", on_click=ejecutar_busqueda, bgcolor="#1A237E", color="#FFFFFF"),
            ft.Divider(),
            resultados_column
        ], tight=True, height=350)
        dlg_buscar.actions = [ft.TextButton("Cerrar", on_click=lambda ev: cerrar_modal(dlg_buscar))]
        abrir_modal(dlg_buscar)

    # --- 9. BOTONES EN PANTALLA (SOLO TEXTO Y ESTILO) ---
    btn_agregar = ft.ElevatedButton(
        text="AGREGAR",
        width=260, height=65,
        style=ft.ButtonStyle(
            bgcolor="#1A237E", 
            color="#FFFFFF",
            shape=ft.RoundedRectangleBorder(radius=15)
        ),
        on_click=abrir_agregar
    )

    btn_buscar = ft.ElevatedButton(
        text="BUSCAR",
        width=125, height=45,
        style=ft.ButtonStyle(
            bgcolor="#C5CAE9", 
            color="#1A237E",
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=abrir_buscar
    )

    btn_historial = ft.ElevatedButton(
        text="HISTORIAL",
        width=125, height=45,
        style=ft.ButtonStyle(
            bgcolor="#C5CAE9", 
            color="#1A237E",
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=abrir_historial
    )

    fila_botones_chiquitos = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[btn_buscar, btn_historial]
    )

    # --- 10. CONTENEDOR MODO CELULAR ---
    contenedor_celular = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=20),
                tabla_resumen,
                ft.Container(height=50),
                btn_agregar,
                ft.Container(height=15),
                fila_botones_chiquitos,
                ft.Container(height=20)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        width=380,
        padding=10
    )

    page.add(contenedor_celular)
    page.update()

ft.app(target=main)
            
