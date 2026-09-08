import os

import psutil
from simulador import MotorSimulador


def mostrar_menu():
    while True:
        print("\n" + "="*40)
        print(" SIMULADOR DE RECURSOS E INTERBLOQUEOS ")
        print("="*40)
        print("1. Ejecución Automática (Rápida)")
        print("2. Ejecución Paso a Paso (Interactiva)")
        print("3. Monitoreo de Hardware Real (psutil)")
        print("4. Salir del simulador")
        print("="*40)
        opcion = input("Seleccionar una opción (1-4): ")
        
        if opcion in ['1', '2']:
            ruta = input("\nIngresa el nombre del JSON (ejemplo: ejemplo.json): \n")
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            ruta_segura = os.path.join(directorio_actual, ruta)

            if not os.path.exists(ruta_segura):
                print(f"\n[Error] El archivo {ruta_segura} no existe o la ruta es inválida.")
                continue
                
            print(f"\n[*] Iniciando entorno con {ruta_segura}...")
            motor = MotorSimulador(ruta_segura)
            
            if motor.preparar_sistema():
                if opcion == '1':
                    motor.ejecutar_simulacion(modo_automatico=True)
                else:
                    motor.ejecutar_simulacion(modo_automatico=False)
            else:
                print("\n[Error] El escenario tiene datos incompletos o inválidos.")
                
        elif opcion == '3':
            print("\n--- MONITOREO DE HARDWARE REAL (psutil) ---")
            print("Nota: Estos datos reflejan el estado de tu PC física, no de la simulación.")
            print(f" -> Uso de CPU: {psutil.cpu_percent(interval=1)}%")
            memoria = psutil.virtual_memory()
            print(f" -> Uso de RAM: {memoria.percent}% (Total: {memoria.total / (1024**3):.2f} GB)")
            print(f" -> Red (Bytes enviados): {psutil.net_io_counters().bytes_sent}")
            print(f" -> Red (Bytes recibidos): {psutil.net_io_counters().bytes_recv}")
            
        elif opcion == '4':
            print("\nApagando el sistema...")
            break
        else:
            print("\n[!] Opción no válida, por favor seleccionar 1, 2, 3 o 4.")

if __name__ == "__main__":
    mostrar_menu()