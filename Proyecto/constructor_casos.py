import json

class Accion_pendiente:
    def __init__(self,tipo,objetivo):
        self.tipo=tipo
        self.objetivo=objetivo

class Proceso:
    def __init__(self,pid,acciones,memoria,estado_inicial,recursos_actuales,recursos_necesarios):
        self.pid=pid
        self.acciones=acciones
        self.memoria=memoria
        self.estado_inicial=estado_inicial
        self.recursos_actuales=recursos_actuales
        self.recursos_necesarios=recursos_necesarios

class ContrictorEscenarios:
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.datos=None

    def cargar_datos(self):
        try:
            with open(self.ruta_archivo,'r') as archivo:
                self.datos= json.load(archivo)
            print(f"Cargando escenario: {self.datos['nombre_escenario']}")
        except FileNotFoundError:
            print("Error: El archivo de escenario tiene datos incompletos o invalidos... o no existe")

    def inicializar_sistema(self):
        if not self.datos:
            return None
            
        lista_procesos = []
        # Iteramos sobre los procesos
        for p_data in self.datos['procesos']:
            pid=p_data['pid']
            memoria=p_data['memoria_requerida']
            estado_i=p_data['estado_inicial']
            recursos_actuales = p_data['recursos_actuales'] 
            recursos_necesita=p_data['recursos_necesarios']
            # Ahora acciones_pendientes es una lista de diccionarios
            acciones_estructuradas = p_data['acciones_pendientes'] 
            lista_acciones=[]
            print(f"\nInicializando Proceso: {p_data['pid']}")
            
            # Así es como el simulador leerá las acciones ahora:
            for accion in acciones_estructuradas:
                tipo = accion['tipo_accion'] # Ej: "solicitar_recurso"[cite: 3]
                objetivo = accion['objetivo'] # Ej: "Disco_Externo"[cite: 3]
                print(f" -> Acción cargada: El proceso quiere {tipo} apuntando a {objetivo}")
            
            # Aquí instanciarías tu clase Process pasándole 'acciones_estructuradas'
            # nuevo_proceso = Process(pid=p_data['pid'], ..., acciones=acciones_estructuradas)
            # lista_procesos.append(nuevo_proceso)
            accion_pendiente=Accion_pendiente(tipo,objetivo)
            lista_acciones.append(accion_pendiente)
            proceso=Proceso(pid,lista_acciones,memoria,estado_i,recursos_actuales,recursos_necesita)
            lista_procesos.append(proceso)
        return lista_procesos