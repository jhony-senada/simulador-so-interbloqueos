import customtkinter as ctk
from simulador import MotorSimulador # Clase main

#inciaicar motor
motor = MotorSimulador(r"C:\Users\Wicho\Desktop\Universidad\5° Semestre\Sistemas Operativos\proyecto_SO\simulador-so-interbloqueos\Proyecto\ejemplo.json")
motor.preparar_sistema()

# Configurar ventana
ctk.set_appearance_mode("dark")
ventana = ctk.CTk()
ventana.title("Simulador de Interbloqueos")
ventana.geometry("700x500")

# Funciones de la interfaz
def actualizar_pantalla():
    """Lee el estado actual del motor y actualiza los textos en pantalla"""
    label_reloj.configure(text=f"Tick Actual: {motor.reloj}")

    activos = [p.id for p in motor.procesos if p.estado_inicial == "activo"]
    esperando = [p.pid for p in motor.procesos if p.estado_inicial == "esperando"]
    terminados = [p.id for p in motor.procesos if p.estado_inicial.startswith("terminado")]

    texto_activos.configure(text=f"Activos: {activos if activos else 'Ninguno'}")
    texto_esperando.configure(text=f"Esperando: {esperando if esperando else 'Ninguno'}")
    texto_terminados.configure(text=f"Terminados: {terminados if terminados else 'Ninguno'}")

def boton_paso_a_paso():
    """Lo que sucede al hacer clic en el botón"""
    hubo_bloqueo = motor.ejecutar_un_paso_gui()
    actualizar_pantalla()

    if hubo_bloqueo:
        label_alerta.configure(text="Interbloqueo detectado y resuelto!!", text_color="red")
    else:
        label_alerta.configure(text="Sistema Estable", text_color="green")

# Elementos Visuales
## Titulo y relog
titulo = ctk.CTkLabel(ventana, text="Monitor del Sistema Operativo", font=("Arial", 16))
titulo.pack(pady=10)

label_reloj = ctk.CTkLabel(ventana, text="Tick Actual: 0", font=("Arial", 16))
label_reloj.pack()

# panel de estados
panel_estados = ctk.CTkFrame(ventana)
panel_estados.pack(pady=20, padx=20, fill="both", expand=True)

texto_activos = ctk.CTkLabel(panel_estados, text="Activos: ", font=("Arial", 14))
texto_activos.pack(anchor="w", padx=10, pady=5)

texto_esperando = ctk.CTkLabel(panel_estados, text="Esperando: ", font=("Arial", 14))
texto_esperando.pack(anchor="w", padx=10, pady=5)

texto_terminados = ctk.CTkLabel(panel_estados, text="Terminados: ", font=("Arial", 14))
texto_terminados.pack(pady=10)

label_alerta = ctk.CTkLabel(ventana, text="Sistema Preparado", font=("Arial", 14, "bold"), text_color="yellow")
label_alerta.pack(pady=10)

boton_avanzar = ctk.CTkButton(ventana, text="Avanzar 1 Tick (Paso a paso)", command=boton_paso_a_paso)
boton_avanzar.pack(pady=20)

#cargar datos inciales
actualizar_pantalla()

#incial aplicacióni
ventana.mainloop()
