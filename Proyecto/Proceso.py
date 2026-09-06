import json

class Proceso:
    def __init__(self, pid, memoria, estado, rec_actuales, rec_necesarios, acciones):
        self.pid = pid
        self.memoria_requerida = memoria
        self.estado = estado
        self.recursos_actuales = rec_actuales
        self.recursos_necesarios = rec_necesarios
        self.acciones_pendientes = acciones

    def __str__(self):
        #Método para imprimir el objeto en consola de manera legible
        return f"[{self.pid}] Estado: {self.estado} | Memoria: {self.memoria_requerida}MB"

with open('Escenario_2.json', encoding='utf-8') as f:
    data = json.load(f)
    #Acceso a las claves tal como se nombraron en el archivo 
    nombre_prueba = data["nombre_escenario"]
    memoria_sistema = data["configuracion"]["memoria_total_mb"]
    recursos_sistema = data["recursos_exclusivos"]

    print(f" Iniciando prueba: {nombre_prueba} ")
    print(f" Memoria total del sistema: {memoria_sistema}MB\n ")

    cola_activos = []
    cola_espera = []

    #data["Procesos"] es una lista de diccionarios.
    for p_data in data["Procesos"]:
        nuevo_proceso = Proceso(
            pid=p_data["pid"],
            memoria=p_data["memoria_requerida_mb"],
            estado=p_data["estado"],
            rec_actuales=p_data["recursos_actuales"],
            rec_necesarios=p_data["recursos_necesarios"],
            acciones=p_data["acciones_pendientes"]
        )

        #Como todos incian "activos" en el JSON, los mandamos a esa cola
        cola_activos.append(nuevo_proceso)

        #Verificamos que se hayan cargado correctamente
        print("Procesos cargados en el planificador:")
        for proc in cola_activos:
            print(proc)

# Diccionario global (o atributo de tu clase Planificador) para rastrear quién tiene qué
estado_recursos = {
    "Impresora_1": "P1", # Ocupado por P1 inicialmente (según tu JSON del Escenario 2)
    "Disco_Externo": None # Libre
}

def procesar_accion(proceso, cola_activos, cola_espera):
    # Si ya no tiene acciones, terminó su trabajo
    if not proceso.acciones_pendientes:
        proceso.estado = "terminado"
        return
        
    # Tomamos la acción actual en la que está trabajando
    accion = proceso.acciones_pendientes[0] 
    
    if accion["tipo_accion"] == "solicitar_recurso":
        recurso = accion["objetivo"]
        
        if estado_recursos[recurso] is None:
            # El recurso está libre: se lo asignamos
            estado_recursos[recurso] = proceso.pid
            proceso.recursos_actuales.append(recurso)
            proceso.acciones_pendientes.pop(0) # Acción completada, la borramos
            print(f"[*] {proceso.pid} adquirió el recurso {recurso}.")
        else:
            # El recurso está ocupado: pasa a estado correspondiente de espera
            proceso.estado = "esperando"
            cola_activos.remove(proceso)
            cola_espera.append(proceso) # Se forma al final de la cola FIFO
            print(f"[-] {proceso.pid} bloqueado. {recurso} ocupado por {estado_recursos[recurso]}.")
            
    elif accion["tipo_accion"] == "liberar_recurso":
        recurso = accion["objetivo"]
        
        # Liberamos el recurso de sus manos
        estado_recursos[recurso] = None
        proceso.recursos_actuales.remove(recurso)
        proceso.acciones_pendientes.pop(0)
        print(f"[+] {proceso.pid} liberó el recurso {recurso}.")
        
        # El sistema reevalúa la fila FIFO para ver quién lo estaba esperando[cite: 1]
        for proc_esperando in cola_espera:
            accion_esperada = proc_esperando.acciones_pendientes[0]
            
            if accion_esperada["tipo_accion"] == "solicitar_recurso" and accion_esperada["objetivo"] == recurso:
                # Encontramos al primero de la fila que quería este recurso exacto
                proc_esperando.estado = "activo"
                cola_espera.remove(proc_esperando)
                cola_activos.append(proc_esperando)
                print(f"[*] {proc_esperando.pid} salió de la fila FIFO y volvió a la cola de activos.")
                break # Rompemos el ciclo para despertar solo al primero (lógica FIFO)