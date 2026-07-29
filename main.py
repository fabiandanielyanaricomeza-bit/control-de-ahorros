import flet as ft
import csv
import os
import shutil
from datetime import datetime
import calendar

archivo = 'mis_ahorros.csv'

def main(page: ft.Page):
    # --- 1. CONFIGURACIÓN DE LA PANTALLA ---
    page.title = "Control de Ahorros"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    if not os.path.exists(archivo):
        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Fecha', 'Monto', 'Descripción'])

    def cerrar_modal(dialogo):
        dialogo.open = False
        page.update()

    def abrir_modal(dialogo):
        if dialogo not in page.overlay:
            page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    # --- 2. LÓGICA DE DATOS Y CACHÉ RÁPIDO ---
    def leer_todas_las_transacciones():
        transacciones = []
        if os.path.exists(archivo):
            with open(archivo, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)
                for fila in reader:
                    if len(fila) >= 2:
                        transacciones.append(fila)
        return transacciones

    def obtener_resumen():
        ingresos = 0.0
        gastos = 0.0
        for fila in leer_todas_las_transacciones():
            try:
                monto = float(fila[1])
                if monto > 0: ingresos += monto
                else: gastos += monto
            except ValueError:
                pass
        return ingresos, gastos, ingresos + gastos

    ingresos_val, gastos_val, beneficio_val = obtener_resumen()

    txt_ingresos = ft.Text(f"{ingresos_val:.2f}", color="green")
    txt_gastos = ft.Text(f"{gastos_val:.2f}", color="red")
    txt_beneficio = ft.Text(f"{beneficio_val:.2f}", weight="bold")

    tabla_resumen = ft.DataTable(
        border_radius=10,
        columns=[
            ft.DataColumn(ft.Text("Concepto", weight="bold")),
            ft.DataColumn(ft.Text("Monto", weight="bold"), numeric=True),
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text("Ingresos (+)", color="green")), ft.DataCell(txt_ingresos)]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("Gastos (-)", color="red")), ft.DataCell(txt_gastos)]),
            ft.DataRow(cells=[ft.DataCell(ft.Text("BENEFICIO", weight="bold")), ft.DataCell(txt_beneficio)]),
        ]
    )

    def actualizar_pantalla():
        i, g, b = obtener_resumen()
        txt_ingresos.value = f"{i:.2f}"
        txt_gastos.value = f"{g:.2f}"
        txt_beneficio.value = f"{b:.2f}"
        page.update()

    # --- 3. GUARDADO Y CARGA MANUAL SEGURA ---
    input_nombre_respaldo = ft.TextField(label="Nombre del respaldo", value="respaldo_ahorros.csv")
    dlg_guardar = ft.AlertDialog(content=ft.Container())
    dlg_cargar = ft.AlertDialog(content=ft.Container())

    def ejecutar_guardado_manual(e):
        nombre = input_nombre_respaldo.value.strip()
        if not nombre.endswith(".csv"):
            nombre += ".csv"
        try:
            shutil.copy(archivo, nombre)
            cerrar_modal(dlg_guardar)
            page.overlay.append(ft.SnackBar(ft.Text(f"Guardado como: {nombre}"), open=True))
            page.update()
        except Exception as ex:
            page.overlay.append(ft.SnackBar(ft.Text(f"Error al guardar: {ex}"), open=True))
            page.update()

    def abrir_dialogo_guardar(e):
        input_nombre_respaldo.value = "respaldo_ahorros.csv"
        dlg_guardar.title = ft.Text("Guardar Respaldo")
        dlg_guardar.content = ft.Column([
            ft.Text("Se creará una copia de seguridad en la carpeta de la app."),
            input_nombre_respaldo
        ], tight=True)
        dlg_guardar.actions = [
            ft.TextButton("Cancelar", on_click=lambda ev: cerrar_modal(dlg_guardar)),
            ft.Button("Guardar", on_click=ejecutar_guardado_manual)
        ]
        abrir_modal(dlg_guardar)

    input_nombre_carga = ft.TextField(label="Nombre del archivo a cargar", value="respaldo_ahorros.csv")

    def ejecutar_carga_manual(e):
        nombre = input_nombre_carga.value.strip()
        if os.path.exists(nombre):
            try:
                shutil.copy(nombre, archivo)
                actualizar_pantalla()
                if en_calendario[0]:
                    renderizar_calendario_pantalla()
                cerrar_modal(dlg_cargar)
                page.overlay.append(ft.SnackBar(ft.Text("¡Datos restaurados con éxito!"), open=True))
                page.update()
            except Exception as ex:
                page.overlay.append(ft.SnackBar(ft.Text(f"Error al cargar: {ex}"), open=True))
                page.update()
        else:
            page.overlay.append(ft.SnackBar(ft.Text("No se encontró un archivo con ese nombre."), open=True))
            page.update()

    def abrir_dialogo_cargar(e):
        input_nombre_carga.value = "respaldo_ahorros.csv"
        dlg_cargar.title = ft.Text("Cargar Respaldo")
        dlg_cargar.content = ft.Column([
            ft.Text("Escribe el nombre del archivo CSV a restaurar:"),
            input_nombre_carga
        ], tight=True)
        dlg_cargar.actions = [
            ft.TextButton("Cancelar", on_click=lambda ev: cerrar_modal(dlg_cargar)),
            ft.Button("Cargar", on_click=ejecutar_carga_manual)
        ]
        abrir_modal(dlg_cargar)

    # --- 4. BARRA SUPERIOR Y TEMA DINÁMICO ---
    app_bar_title = ft.Text("MI BILLETERA", weight=ft.FontWeight.BOLD)
    btn_accion_vista = ft.TextButton(">", on_click=lambda e: alternar_vista())

    def actualizar_estilo_appbar():
        if page.theme_mode == ft.ThemeMode.DARK:
            app_bar.bgcolor = "#121212"
            app_bar_title.color = "#90CAF9"
            btn_accion_vista.style = ft.ButtonStyle(color="#90CAF9")
        else:
            app_bar.bgcolor = "#E8EAF6"
            app_bar_title.color = "#1A237E"
            btn_accion_vista.style = ft.ButtonStyle(color="#1A237E")

    def cambiar_tema(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        actualizar_estilo_appbar()
        page.update()

    dlg_info = ft.AlertDialog(
        title=ft.Text("Acerca de", weight="bold"),
        content=ft.Text("Control de Ahorros v2.2\nEstudiante de Ingeniería.", text_align=ft.TextAlign.CENTER),
        actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_modal(dlg_info))]
    )

    app_bar = ft.AppBar(
        leading=ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Text("Guardar"), 
                    icon="save", 
                    on_click=abrir_dialogo_guardar
                ),
                ft.PopupMenuItem(
                    content=ft.Text("Cargar"), 
                    icon="file_upload", 
                    on_click=abrir_dialogo_cargar
                ),
                ft.PopupMenuItem(content=ft.Text("Cambiar Tema"), icon="brightness_6", on_click=cambiar_tema),
                ft.PopupMenuItem(content=ft.Text("Info de la App"), icon="info", on_click=lambda e: abrir_modal(dlg_info))
            ]
        ),
        title=app_bar_title,
        center_title=True,
        actions=[btn_accion_vista]
    )
    
    actualizar_estilo_appbar()
    page.appbar = app_bar

    # --- 5. LÓGICA DEL CALENDARIO ---
    fecha_hoy = datetime.now()
    estado_calendario = {"mes": fecha_hoy.month, "anio": fecha_hoy.year}
    
    contenedor_calendario_grid = ft.Column(tight=True, alignment=ft.MainAxisAlignment.CENTER)
    txt_anio = ft.Text(weight="bold", size=18)
    txt_mes = ft.Text(weight="bold", size=18)

    dlg_dia = ft.AlertDialog(content=ft.Column([], scroll=ft.ScrollMode.AUTO, height=150))
    
    def ver_registros_dia(dia, anio, mes, registros):
        dlg_dia.title = ft.Text(f"Movimientos del {dia}/{mes}/{anio}", size=14, weight="bold")
        lista_ui = ft.Column([], scroll=ft.ScrollMode.AUTO, height=150)
        for fila in registros:
            color_monto = "green" if float(fila[1]) > 0 else "red"
            lista_ui.controls.append(ft.Text(f"• S/ {fila[1]} : {fila[2]}", color=color_monto))
        
        dlg_dia.content = lista_ui
        dlg_dia.actions = [ft.TextButton("Cerrar", on_click=lambda e: cerrar_modal(dlg_dia))]
        abrir_modal(dlg_dia)

    def obtener_datos_mes(anio, mes):
        dias_activos = {}
        for fila in leer_todas_las_transacciones():
            if len(fila) >= 3:
                try:
                    f_date = datetime.strptime(fila[0].split(" ")[0], "%Y-%m-%d")
                    if f_date.year == anio and f_date.month == mes:
                        if f_date.day not in dias_activos:
                            dias_activos[f_date.day] = []
                        dias_activos[f_date.day].append(fila)
                except:
                    pass
        return dias_activos

    def renderizar_calendario_pantalla():
        anio, mes = estado_calendario["anio"], estado_calendario["mes"]
        nombres_meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        txt_anio.value = str(anio)
        txt_mes.value = nombres_meses[mes]
        
        dias_activos = obtener_datos_mes(anio, mes)
        cal = calendar.monthcalendar(anio, mes)
        contenedor_calendario_grid.controls.clear()
        
        dias_semana = ["L", "M", "X", "J", "V", "S", "D"]
        header_row = ft.Row([ft.Container(content=ft.Text(d, weight="bold", size=14), width=38, alignment=ft.Alignment(0, 0)) for d in dias_semana], alignment=ft.MainAxisAlignment.CENTER)
        contenedor_calendario_grid.controls.append(header_row)
        contenedor_calendario_grid.controls.append(ft.Container(height=10))

        for semana in cal:
            fila_semana = ft.Row(alignment=ft.MainAxisAlignment.CENTER)
            for dia in semana:
                if dia == 0:
                    fila_semana.controls.append(ft.Container(width=38, height=38))
                else:
                    tiene_registro = dia in dias_activos
                    bg_color = "indigo" if tiene_registro else "transparent"
                    txt_color = "white" if tiene_registro else None
                    
                    btn_dia = ft.Container(
                        content=ft.Text(str(dia), color=txt_color, size=13),
                        width=38, height=38,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=bg_color,
                        border_radius=19,
                        on_click=lambda e, d=dia: ver_registros_dia(d, anio, mes, dias_activos[d]) if d in dias_activos else None
                    )
                    fila_semana.controls.append(btn_dia)
            contenedor_calendario_grid.controls.append(fila_semana)
        page.update()

    def cambiar_mes(delta):
        estado_calendario["mes"] += delta
        if estado_calendario["mes"] > 12:
            estado_calendario["mes"] = 1
            estado_calendario["anio"] += 1
        elif estado_calendario["mes"] < 1:
            estado_calendario["mes"] = 12
            estado_calendario["anio"] -= 1
        renderizar_calendario_pantalla()

    # --- 6. VISTAS PRINCIPALES ---
    btn_agregar = ft.Button("AGREGAR", width=260, height=60, icon="add_circle", on_click=lambda e: abrir_agregar(e))
    btn_buscar = ft.Button("Buscar", width=125, height=45, icon="search", on_click=lambda e: abrir_buscar(e))
    btn_historial = ft.Button("Historial", width=125, height=45, icon="history", on_click=lambda e: abrir_historial(e))

    vista_principal = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=10),
                tabla_resumen,
                ft.Container(height=30),
                btn_agregar,
                ft.Container(height=10),
                ft.Row([btn_buscar, btn_historial], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=380,
        alignment=ft.Alignment(0, 0)
    )

    vista_calendario = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(height=10),
                ft.Row([
                    txt_anio,
                    txt_mes
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=320),
                ft.Container(height=15),
                contenedor_calendario_grid,
                ft.Container(height=20),
                ft.Row([
                    ft.Button("Mes Anterior", icon="chevron_left", on_click=lambda e: cambiar_mes(-1)),
                    ft.Button("Mes Siguiente", icon="chevron_right", on_click=lambda e: cambiar_mes(1))
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=380,
        alignment=ft.Alignment(0, 0),
        visible=False
    )

    en_calendario = [False]

    def alternar_vista():
        if not en_calendario[0]:
            en_calendario[0] = True
            app_bar_title.value = "CALENDARIO"
            btn_accion_vista.text = "X"
            vista_principal.visible = False
            vista_calendario.visible = True
            renderizar_calendario_pantalla()
        else:
            en_calendario[0] = False
            app_bar_title.value = "MI BILLETERA"
            btn_accion_vista.text = ">"
            vista_calendario.visible = False
            vista_principal.visible = True
            actualizar_pantalla()
        actualizar_estilo_appbar()
        page.update()

    # --- 7. MODALES SECUNDARIOS ---
    dlg_agregar = ft.AlertDialog(content=ft.Container())
    dlg_historial = ft.AlertDialog(content=ft.Container())
    dlg_confirmar = ft.AlertDialog(content=ft.Container())
    dlg_buscar = ft.AlertDialog(content=ft.Container())

    input_monto = ft.TextField(label="Monto (+ o -)", prefix_icon="attach_money")
    input_desc = ft.TextField(label="Descripción", prefix_icon="description")

    def guardar_transaccion(e):
        try:
            monto = float(input_monto.value)
            desc = input_desc.value.strip() if input_desc.value else "Sin descripción"
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            with open(archivo, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([fecha_actual, monto, desc])
            cerrar_modal(dlg_agregar)
            actualizar_pantalla()
            if en_calendario[0]:
                renderizar_calendario_pantalla()
            page.overlay.append(ft.SnackBar(ft.Text("¡Guardado!"), open=True))
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
            ft.Button("Guardar", on_click=guardar_transaccion)
        ]
        abrir_modal(dlg_agregar)

    container_lista_historial = ft.Column([], scroll=ft.ScrollMode.AUTO, height=220)
    items_historial = []
    modo_borrar = [False]

    def ejecutar_eliminacion_final(ev, filas_a_borrar):
        filas_conservadas = []
        for fila in leer_todas_las_transacciones():
            if fila not in filas_a_borrar:
                filas_conservadas.append(fila)
        with open(archivo, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Fecha', 'Monto', 'Descripción'])
            writer.writerows(filas_conservadas)
        cerrar_modal(dlg_confirmar)
        cerrar_modal(dlg_historial)
        actualizar_pantalla()
        if en_calendario[0]:
            renderizar_calendario_pantalla()

    def abrir_confirmacion_borrado(filas_a_borrar):
        detalles_column = ft.Column([ft.Text(f"• {f[1]} ({f[0]})", size=12) for f in filas_a_borrar], scroll=ft.ScrollMode.AUTO, height=100)
        dlg_confirmar.title = ft.Text("¿Estás seguro?", color="red")
        dlg_confirmar.content = ft.Column([ft.Text("Se eliminarán:"), detalles_column], tight=True)
        dlg_confirmar.actions = [
            ft.TextButton("Cancelar", on_click=lambda ev: cerrar_modal(dlg_confirmar)),
            ft.Button("Eliminar", on_click=lambda ev: ejecutar_eliminacion_final(ev, filas_a_borrar), color="white", bgcolor="red")
        ]
        abrir_modal(dlg_confirmar)

    def alternar_modo_eliminacion(btn_eliminar):
        if not modo_borrar[0]:
            modo_borrar[0] = True
            for chk, _ in items_historial: chk.visible = True
            btn_eliminar.text = "Confirmar Borrado"
            btn_eliminar.style = ft.ButtonStyle(color="red")
        else:
            seleccionados = [fila for chk, fila in items_historial if chk.value]
            if seleccionados: abrir_confirmacion_borrado(seleccionados)
        page.update()

    def abrir_historial(e):
        modo_borrar[0] = False
        container_lista_historial.controls.clear()
        items_historial.clear()
        
        for fila in leer_todas_las_transacciones():
            chk = ft.Checkbox(visible=False)
            items_historial.append((chk, fila))
            container_lista_historial.controls.append(
                ft.Row([chk, ft.Text(fila[0], size=10, width=105), ft.Text(fila[1], size=11, width=55, weight="bold"), ft.Text(fila[2], size=11, width=120)], spacing=5)
            )
                    
        btn_eliminar = ft.TextButton("Eliminar", style=ft.ButtonStyle(color="red"))
        btn_eliminar.on_click = lambda ev: alternar_modo_eliminacion(btn_eliminar)
        
        btn_cerrar = ft.TextButton("Cerrar", on_click=lambda ev: cerrar_modal(dlg_historial))

        dlg_historial.title = ft.Text("Historial")
        dlg_historial.content = container_lista_historial
        dlg_historial.actions = [
            ft.Row(
                [btn_eliminar, btn_cerrar],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=280
            )
        ]
        abrir_modal(dlg_historial)

    in_dia = ft.TextField(label="Día (ej: 5)", width=90)
    in_mes = ft.TextField(label="Mes (ej: 8)", width=90)
    in_anio = ft.TextField(label="Año (ej: 2026)", width=120)
    resultados_column = ft.Column([], scroll=ft.ScrollMode.AUTO, height=180)

    def ejecutar_busqueda(ev):
        resultados_column.controls.clear()
        d = in_dia.value.strip().zfill(2) if in_dia.value else ""
        m = in_mes.value.strip().zfill(2) if in_mes.value else ""
        a = in_anio.value.strip()
        fecha_busqueda = "-".join(filter(None, [a, m, d]))
        
        for fila in leer_todas_las_transacciones():
            if fecha_busqueda in fila[0]:
                resultados_column.controls.append(ft.Text(f"• [{fila[1]}] {fila[2]} ({fila[0]})"))
        page.update()

    def abrir_buscar(e):
        in_dia.value = in_mes.value = in_anio.value = ""
        resultados_column.controls.clear()
        dlg_buscar.title = ft.Text("Buscar")
        dlg_buscar.content = ft.Column([ft.Row([in_dia, in_mes]), in_anio, ft.Button("Buscar", on_click=ejecutar_busqueda), resultados_column], tight=True)
        dlg_buscar.actions = [ft.TextButton("Cerrar", on_click=lambda ev: cerrar_modal(dlg_buscar))]
        abrir_modal(dlg_buscar)

    page.add(vista_principal, vista_calendario)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
