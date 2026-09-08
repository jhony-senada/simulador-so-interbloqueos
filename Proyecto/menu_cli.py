import os

from simulador import MotorSimulador


def mostrar_menu():
    while True:
        print("\n" + "="*20)
        print("  Simulador de recursos e interbloqueos  ")
        print("="*20)
        print("1. Cargar escenario (JSON con formato) y ejecutar paso a paso")
        print("2. salir del simulador")
        print("="*20)
        opcion = input("seleccionar un opción (1 o 2): ")
        if opcion == '1':
            ruta= input("\n ingresa el nombre o la ruta exacta del archivo JSON: \n")

            if not os.path.exists(ruta):
                print(f"\n[Error] El archivo {ruta} no existe o la ruta es invalida.")
                continue
            print(f"\n[*] Iniciando entorno con {ruta}...")
            motor = MotorSimulador(ruta)
            if motor.preparar_sistema():
                motor.ejecutar_paso_a_paso(limite_ticks=6)
            else:
                print("\n[Error] El escenario tiene datos incompletos o inválidos.")
        elif opcion=='2':
            print("\nApagando el sistema...")
            break
        else:
            print("\n[!] Opcion no valida, por favor seleccionar 1 o 2.")

if __name__ == "__main__":
    mostrar_menu()
