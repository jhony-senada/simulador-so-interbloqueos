# tester.py
from constructor_casos import ContrictorEscenarios
from detector import MóduloInterbloqueos


def ejecutar_prueba():
    print("--- INICIANDO TESTER MODULAR ---\n")
    
    # 1. Cargamos el escenario desde el archivo JSON[cite: 9, 10]
    constructor = ContrictorEscenarios("D:\Apuntes\Codigos\Proyecto\ejemplo2.json")
    constructor.cargar_datos()
    
    # 2. Inicializamos el sistema y extraemos los recursos
    datos_sistema,permite_expropiar = constructor.inicializar_sistema()
    if not datos_sistema:
        print("Error: No se pudo inicializar el sistema.")
        return
        
    # Extraemos solo los IDs de los recursos exclusivos (están en la posición 1)[cite: 10]
    diccionarios_recursos = datos_sistema[2]
    ids_exclusivos = [recurso['id'] for recurso in diccionarios_recursos]
    
    # 3. Inicializamos los procesos con sus acciones pendientes[cite: 10]
    procesos_cargados = constructor.inicializar_proceso()
    
    # 4. Instanciamos el detector pasándole la lista de IDs
    detector = MóduloInterbloqueos(ids_exclusivos,permite_expropiar)
    
    # 5. Ejecutamos el análisis con los procesos cargados[cite: 11]
    hay_bloqueo, procesos_afectados = detector.detectar_y_analizar(procesos_cargados)
    
    if hay_bloqueo:
        print(f"\n[!] TEST COMPLETADO: Interbloqueo detectado en {procesos_afectados}")
    else:
        print("\n[✓] TEST COMPLETADO: No se detectaron bloqueos.")

if __name__ == "__main__":
    ejecutar_prueba()