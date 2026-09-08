import customtkinter as ctk
from tkinter import filedialog
from simulador import MotorSimulador
import time

motor = None

def cargar_archivo():
    global motor

    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar escenario JSON",
        filetypes=[("Archivos JSON", "*.json")]
    )
    
    if ruta_archivo:

        motor = MotorSimulador(ruta_archivo)

        if motor.preparar_sistema():
            label_alerta.configure(text="Escenario cargado exitosamente caballero.", text_color="green")
            boton_avanzar.configure(state="normal")
            boton_automatico.configure(state="normal")
            actualizar_pantalla()
        else:
            label_alerta.configure(text="Error al cargar el escenario X_x", text_color="red")

def actualizar_pantalla():
    if not motor: return
    
    label_reloj.configure(text=f"Tick Actual: {motor.reloj}")
    label_memoria.configure(text=f"Memoria RAM: {motor.memoria_disponible} MB Libres de {motor.memoria_total} MB")
    
    # estado de  procesos
    activos = [p.pid for p in motor.procesos if p.estado_inicial == "activo"]
    esperando = [p.pid for p in motor.procesos if p.estado_inicial == "esperando"]
    terminados = [p.pid for p in motor.procesos if p.estado_inicial not in ["activo", "esperando"]]
    
    texto_activos.configure(text=f"Activos: {activos if activos else 'Ninguno'}")
    texto_esperando.configure(text=f"Esperando/Bloqueados: {esperando if esperando else 'Ninguno'}")
    texto_terminados.configure(text=f"Terminados: {terminados if terminados else 'Ninguno'}")

    # estado de recursos
    dueños = []
    for p in motor.procesos:
        for r in p.recursos_actuales:
            dueños.append(f"{r} (Dueño: {p.pid})")
            
    texto_rec_libres.configure(text=f"Recursos Libres: {motor.recursos_libres if motor.recursos_libres else 'Ninguno'}")
    texto_rec_ocupados.configure(text=f"Recursos Ocupados: {dueños if dueños else 'Ninguno'}")

    # estados de archivos
    if motor.archivos:
        archivos_str = " | ".join([f"{k} ({v})" for k, v in motor.archivos.items()])
    else:
        archivos_str = "Ninguno"
    texto_archivos.configure(text=f"Archivos: {archivos_str}")

def verificar_fin_simulacion(hubo_bloqueo):
    pendientes = [p for p in motor.procesos if p.estado_inicial in ["activo", "esperando"]]
    
    if hubo_bloqueo:
        label_alerta.configure(text="¡ALERTA: Interbloqueo detectado y resuelto!", text_color="red")
    elif not pendientes:
        label_alerta.configure(text="¡Simulación completada caballero! .", text_color="cyan")
        motor.mostrar_metricas_finales()
        boton_avanzar.configure(state="disabled")
        boton_automatico.configure(state="disabled")
        return True
    else:
        label_alerta.configure(text="Sistema estable. Prosiguiendo caballero...", text_color="yellow")
    return False

def boton_paso_a_paso():
    if not motor: return
    hubo_bloqueo = motor.ejecutar_un_paso_gui()
    actualizar_pantalla()
    verificar_fin_simulacion(hubo_bloqueo)

def boton_modo_automatico():
    if not motor: return

    boton_avanzar.configure(state="disabled")
    boton_automatico.configure(state="disabled")
    
    pendientes = [p for p in motor.procesos if p.estado_inicial in ["activo", "esperando"]]
    while pendientes:

        hubo_bloqueo = motor.ejecutar_un_paso_gui()
        actualizar_pantalla()

        ventana.update()
        time.sleep(0.5)

        if verificar_fin_simulacion(hubo_bloqueo):
            break
        pendientes = [p for p in motor.procesos if p.estado_inicial in ["activo", "esperando"]]

#  configuración de Ventana
ctk.set_appearance_mode("dark")
ventana = ctk.CTk()
ventana.title("Simulador de Interbloqueos (GUI)")
ventana.geometry("800x700")

# interfaz Visual
titulo = ctk.CTkLabel(ventana, text="Monitor del Sistema Operativo", font=("Arial", 20, "bold"))
titulo.pack(pady=10)

boton_cargar = ctk.CTkButton(ventana, text="Cargar Escenario (.json)", command=cargar_archivo)
boton_cargar.pack(pady=5)

label_reloj = ctk.CTkLabel(ventana, text="Tick Actual: 0", font=("Arial", 16))
label_reloj.pack()

label_memoria = ctk.CTkLabel(ventana, text="Memoria RAM: --", font=("Arial", 14, "italic"), text_color="lightblue")
label_memoria.pack(pady=5)

panel_procesos = ctk.CTkFrame(ventana)
panel_procesos.pack(pady=5, padx=20, fill="both", expand=True)


ctk.CTkLabel(panel_procesos, text="ESTADO DE PROCESOS", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=2)

texto_activos = ctk.CTkLabel(panel_procesos, text="Activos: ", font=("Arial", 14))
texto_activos.pack(anchor="w", padx=10, pady=2)

texto_esperando = ctk.CTkLabel(panel_procesos, text="Esperando/Bloqueados: ", font=("Arial", 14))
texto_esperando.pack(anchor="w", padx=10, pady=2)

texto_terminados = ctk.CTkLabel(panel_procesos, text="Terminados: ", font=("Arial", 14))
texto_terminados.pack(anchor="w", padx=10, pady=2)

panel_recursos = ctk.CTkFrame(ventana)
panel_recursos.pack(pady=5, padx=20, fill="both", expand=True)


ctk.CTkLabel(panel_recursos, text="RECURSOS Y ARCHIVOS", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=2)

texto_rec_libres = ctk.CTkLabel(panel_recursos, text="Recursos Libres: ", font=("Arial", 14))
texto_rec_libres.pack(anchor="w", padx=10, pady=2)

texto_rec_ocupados = ctk.CTkLabel(panel_recursos, text="Recursos Ocupados: ", font=("Arial", 14))
texto_rec_ocupados.pack(anchor="w", padx=10, pady=2)

texto_archivos = ctk.CTkLabel(panel_recursos, text="Archivos: ", font=("Arial", 14))
texto_archivos.pack(anchor="w", padx=10, pady=2)

label_alerta = ctk.CTkLabel(ventana, text="Esperando cargar escenario...", font=("Arial", 14, "bold"), text_color="gray")
label_alerta.pack(pady=10)

panel_botones = ctk.CTkFrame(ventana, fg_color="transparent")
panel_botones.pack(pady=10)

boton_avanzar = ctk.CTkButton(panel_botones, text="Paso a Paso", command=boton_paso_a_paso, state="disabled")
boton_avanzar.pack(side="left", padx=10)

boton_automatico = ctk.CTkButton(panel_botones, text="Modo Automático", command=boton_modo_automatico, state="disabled", fg_color="darkgreen")
boton_automatico.pack(side="left", padx=10)

ventana.mainloop()