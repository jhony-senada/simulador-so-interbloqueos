import logging
import os
import time

from constructor_casos import ContrictorEscenarios
from detector import MóduloInterbloqueos
from recuperacion import TiradorDeParoInteligente


class MotorSimulador:
    def __init__(self, ruta_escenario):
        self.ruta_escenario = ruta_escenario
        self.procesos = []
        self.detector = None
        self.recuperador = TiradorDeParoInteligente(False)
        self.reloj = 0
        # Variables de memoria añadidas
        self.memoria_total = 0
        self.memoria_disponible = 0
        self.uso_maximo_memoria = 0
        self.recursos_libres = [] # NUEVO: Inventario del sistema
        self.archivos = {} # Nuevo gestor de archivos
        self.configurar_logger()
        self.metricas = {
            "solicitudes_recursos": 0,
            "veces_espera": 0,
            "interbloqueos_detectados": 0,
            "interbloqueos_resueltos": 0,
            "recursos_involucrados": set(),
            "recursos_liberados": 0
        }

    def configurar_logger(self):
        """Crea y configura el archivo simulacion.log (Cumple Sección 4.9)"""
        self.logger = logging.getLogger("SimuladorSO")
        self.logger.setLevel(logging.INFO)
        
        # Evitamos que se dupliquen los logs si corremos el menú varias veces
        if not self.logger.handlers:
            # Crea el archivo en la misma carpeta que el script
            directorio = os.path.dirname(os.path.abspath(__file__))
            ruta_log = os.path.join(directorio, "simulacion.log")
            
            # mode='w' sobreescribe el log en cada nueva simulación para mantenerlo limpio
            handler = logging.FileHandler(ruta_log, mode='w', encoding='utf-8')
            formato = logging.Formatter('%(asctime)s | TICK: %(message)s', datefmt='%H:%M:%S')
            handler.setFormatter(formato)
            self.logger.addHandler(handler)
    
    def preparar_sistema(self):
        print("=== INICIANDO ARRANQUE DEL SISTEMA OPERATIVO ===")
        self.logger.info(f"0 | [INICIO] Arrancando simulación con escenario: {self.ruta_escenario}")
        constructor = ContrictorEscenarios(self.ruta_escenario)
        constructor.cargar_datos()

        datos_sistema, permite_expropiar = constructor.inicializar_sistema()
        if not datos_sistema: return False

        self.memoria_total = datos_sistema[0]
        self.memoria_disponible = self.memoria_total
        self.logger.info(f"0 | [MEMORIA] Memoria total configurada: {self.memoria_total} MB")

        ids_exclusivos = [r['id'] for r in datos_sistema[1]]
        self.recursos_libres = ids_exclusivos.copy() # Llenamos el inventario
        procesos_brutos = constructor.inicializar_proceso()
        # Validar estado inicial: Si necesitan recursos, inician esperando
        print("\n>> [GESTOR DE MEMORIA] Asignando...")
        for p in procesos_brutos:
            if p.memoria <= self.memoria_disponible:
                self.memoria_disponible -= p.memoria
                self.procesos.append(p)
                print(f" [+] {p.pid} admitido. Memoria restante: {self.memoria_disponible} MB")
                self.logger.info(f"0 | [PROCESO] {p.pid} cargado y se le asignaron {p.memoria} MB.")

                uso_actual = self.memoria_total - self.memoria_disponible
                if uso_actual > self.uso_maximo_memoria:  # noqa: PLR1730
                    self.uso_maximo_memoria = uso_actual
                # Descontamos del inventario los recursos que ya trae este proceso
                for r in p.recursos_actuales:
                    if r in self.recursos_libres:
                        self.recursos_libres.remove(r)

                if len(p.recursos_necesarios) > 0:
                    p.estado_inicial = "esperando"
            else:
                p.estado_inicial = "rechazado_por_memoria"
                print(f" [!] {p.pid} RECHAZADO: Requiere {p.memoria} MB pero solo hay {self.memoria_disponible} MB.")
                self.logger.warning(f"0 | [MEMORIA] {p.pid} rechazado por falta de memoria.")

        # Cargar los archivos desde el JSON al sistema
        if 'archivos_simulados' in constructor.datos:
            for arch in constructor.datos['archivos_simulados']:
                self.archivos[arch['nombre']] = arch['estado']
        self.detector = MóduloInterbloqueos(ids_exclusivos, permite_expropiar)
        return True
    
    def intentar_asignar_recursos_libres(self):
        """Revisa el inventario y entrega los recursos a quienes los esperan"""
        if not self.recursos_libres: return
        
        procesos_ordenados = sorted(self.procesos, key=lambda x: len(x.recursos_necesarios))
        for p in procesos_ordenados:
            if p.estado_inicial == "esperando":
                recursos_entregados = []
                for rec_necesitado in p.recursos_necesarios:
                    if rec_necesitado in self.recursos_libres:
                        p.recursos_actuales.append(rec_necesitado)
                        recursos_entregados.append(rec_necesitado)
                        print(f" [+] Recurso '{rec_necesitado}' extraído del pool y asignado a {p.pid}.")
                        self.logger.info(f"{self.reloj} | [ASIGNACIÓN] '{rec_necesitado}' asignado a {p.pid}.")
                
                # Borramos los recursos entregados de la lista de necesidades y del pool
                for r in recursos_entregados:
                    p.recursos_necesarios.remove(r)
                    self.recursos_libres.remove(r)
                    
                if len(p.recursos_necesarios) == 0:
                    p.estado_inicial = "activo"
                    print(f" [^] {p.pid} tiene todos sus recursos. Despierta a estado 'activo'.")
                    self.logger.info(f"{self.reloj} | [ESTADO] {p.pid} cambia a estado ACTIVO.")

    def reasignar_recursos(self, recursos_liberados):
        """Recibe recursos soltados y llama al repartidor"""
        if not recursos_liberados: return
        print(f"\n>> [GESTOR DE RECURSOS] Reintegrando {recursos_liberados} al pool general...")
        for r in recursos_liberados:
            if r not in self.recursos_libres:
                self.recursos_libres.append(r)
                
        # Una vez en el inventario, intentamos repartirlos
        self.intentar_asignar_recursos_libres()

    def avanzar_procesos_activos(self):
        print("\n>> [CPU] Ejecutando procesos activos...")
        for p in self.procesos:
            if p.estado_inicial == "activo" and len(p.recursos_necesarios) == 0:
                if len(p.acciones) > 0:
                    accion = p.acciones[0] # Miramos la acción sin sacarla aún
                    
                    # CUMPLE 4.6: Registro de Llamada al Sistema
                    print(f" [SYSCALL] El proceso {p.pid} solicita servicio al SO: '{accion.tipo}'")
                    self.logger.info(f"{self.reloj} | [SYSCALL] {p.pid} ejecuta: {accion.tipo} sobre {accion.objetivo}")
                    if accion.tipo == "solicitar_recurso":
                        self.metricas["solicitudes_recursos"] += 1
                    # CUMPLE 4.4: Lógica de Archivos
                    if "archivo" in accion.tipo:
                        objetivo = accion.objetivo
                        
                        if accion.tipo == "crear_archivo":
                            if objetivo in self.archivos:
                                print(f"   [!] Error: El archivo {objetivo} ya existe.")
                            else:
                                self.archivos[objetivo] = "disponible"
                                print(f"   [>] {p.pid} creó el archivo {objetivo}.")
                                p.acciones.pop(0) # Completada
                                
                        elif accion.tipo in ["leer_archivo", "escribir_archivo"]:
                            if self.archivos.get(objetivo) == "disponible":
                                print(f"   [>] {p.pid} ejecutando {accion.tipo} sobre {objetivo}.")
                                p.acciones.pop(0) # Completada
                            elif self.archivos.get(objetivo) == "en_uso":
                                print(f"   [!] {p.pid} en espera: el archivo {objetivo} está en uso.")
                                # No hacemos pop, lo intentará en el siguiente tick
                            else:
                                print(f"   [!] Error: El archivo {objetivo} no existe en el disco.")
                                p.acciones.pop(0) # Falla y avanza
                                
                        elif accion.tipo == "eliminar_archivo":
                            if objetivo in self.archivos:
                                del self.archivos[objetivo]
                                print(f"   [>] {p.pid} eliminó el archivo {objetivo}.")
                            else:
                                print(f"   [!] Error: No se puede eliminar {objetivo}, no existe.")
                            p.acciones.pop(0)
                            
                    else:
                        # Si no es un archivo (ej. recursos normales)
                        print(f"   [>] {p.pid} ejecutando acción genérica: {accion.tipo} -> {accion.objetivo}")
                        p.acciones.pop(0)
                
                # CUMPLE 4.3: Liberación de memoria y recursos
                if len(p.acciones) == 0:
                    p.estado_inicial = "terminado_exitosamente"
                    print(f" [:D] {p.pid} ha completado tareas. LIBERA sus recursos y memoria.")
                    self.logger.info(f"{self.reloj} | [TERMINACIÓN] {p.pid} terminó exitosamente. Liberando {p.memoria} MB.")
                    recursos_a_liberar = p.recursos_actuales.copy()
                    p.recursos_actuales = []
                    self.reasignar_recursos(recursos_a_liberar)
                    
                    self.memoria_disponible += p.memoria
                    print(f" [^] Memoria liberada por {p.pid}: {p.memoria} MB. (Total disponible: {self.memoria_disponible} MB)")

    def ejecutar_simulacion(self, limite_ticks=20, modo_automatico=False):
        modo_texto = "AUTOMÁTICA" if modo_automatico else "PASO A PASO"
        print(f"\n=== INICIANDO SIMULACIÓN ({modo_texto}) ===")
        
        while self.reloj < limite_ticks:
            pendientes = [p for p in self.procesos if p.estado_inicial in ["activo", "esperando"]]
            if not pendientes:
                print("\n[*] Todos los procesos han finalizado sus tareas. Simulación completada.")
                self.logger.info(f"{self.reloj} | [FIN] Simulación completada. No hay procesos pendientes.")
                break

            self.reloj += 1
            print("\n" + "="*40 + f"\n   [TICK DE RELOJ: {self.reloj}]\n" + "="*40)
            self.intentar_asignar_recursos_libres()
            self.avanzar_procesos_activos()
            
            hay_bloqueo, pids_afectados = self.detector.detectar_y_analizar(self.procesos)
            
            if hay_bloqueo:
                print("\n[!] ALERTA CRÍTICA: Interbloqueo detectado.")
                self.logger.warning(f"{self.reloj} | [INTERBLOQUEO] Detectado entre los procesos: {pids_afectados}")
                
                # --- NUEVO: MÉTRICAS DE INTERBLOQUEO ---
                self.metricas["interbloqueos_detectados"] += 1
                for proc in self.procesos:
                    if proc.pid in pids_afectados:
                        self.metricas["recursos_involucrados"].update(proc.recursos_actuales)
                
                recursos_salvados = self.recuperador.resolver_interbloqueo(pids_afectados, self.procesos)
                
                # --- NUEVO: MÉTRICAS DE RESOLUCIÓN ---
                self.metricas["interbloqueos_resueltos"] += 1
                self.metricas["recursos_liberados"] += len(recursos_salvados)
                for proc in self.procesos:
                    if proc.pid in pids_afectados and proc.estado_inicial == "esperando":
                        self.metricas["veces_espera"] += 1
                
                self.logger.info(f"{self.reloj} | [RECUPERACIÓN] Estrategia aplicada. Recursos recuperados: {recursos_salvados}")
                self.reasignar_recursos(recursos_salvados) 
            
            self.mostrar_estado_sistema()
            
            if not modo_automatico:
                input("\n[Pausa] Presiona ENTER para avanzar al siguiente evento...")
            else:
                time.sleep(0.3)
                
        # --- NUEVO: LLAMADA AL TABLERO FINAL AL SALIR DEL BUCLE ---
        self.mostrar_metricas_finales()

    def mostrar_estado_sistema(self):
        activos = [p.pid for p in self.procesos if p.estado_inicial == "activo"]
        esperando = [p.pid for p in self.procesos if p.estado_inicial == "esperando"]
        terminados = [p.pid for p in self.procesos if p.estado_inicial.startswith("terminado")]
        
        print("\n--- ESTADO DEL SISTEMA ---")
        print(f" -> Activos: {activos if activos else 'Ninguno'}")
        print(f" -> Esperando: {esperando if esperando else 'Ninguno'}")
        print(f" -> Terminados: {terminados if terminados else 'Ninguno'}")
        print(f" -> Memoria: {self.memoria_disponible} MB Libres (Uso Máx Registrado: {self.uso_maximo_memoria} MB)")

    def mostrar_metricas_finales(self):
        """Genera el tablero de resultados finales (Cumple Sección 7)"""
        total_procesos = len(self.procesos)
        terminados_ok = [p.pid for p in self.procesos if p.estado_inicial == "terminado_exitosamente"]
        terminados_mal = [p.pid for p in self.procesos if p.estado_inicial == "terminado_forzosamente"]
        bloqueados = [p.pid for p in self.procesos if p.estado_inicial in ["esperando", "activo"]]
        
        print("\n" + "="*60)
        print("          RESULTADOS Y MÉTRICAS DE LA SIMULACIÓN")
        print("="*60)
        print(f" -> Número total de procesos: {total_procesos}")
        print(f" -> Procesos terminados correctamente: {len(terminados_ok)} {terminados_ok}")
        print(f" -> Procesos terminados por el sistema (Víctimas): {len(terminados_mal)} {terminados_mal}")
        print(f" -> Procesos que quedaron bloqueados o esperando: {len(bloqueados)} {bloqueados}")
        print(f" -> Uso máximo de memoria RAM alcanzado: {self.uso_maximo_memoria} MB")
        print(f" -> Número de solicitudes de recursos realizadas: {self.metricas['solicitudes_recursos']}")
        print(f" -> Número de veces que un proceso tuvo que esperar: {self.metricas['veces_espera']}")
        print(f" -> Número de interbloqueos detectados: {self.metricas['interbloqueos_detectados']}")
        print(f" -> Número de interbloqueos resueltos: {self.metricas['interbloqueos_resueltos']}")
        print(f" -> Recursos exclusivos que causaron bloqueos: {list(self.metricas['recursos_involucrados'])}")
        print(f" -> Resumen de recursos exclusivos liberados forzosamente: {self.metricas['recursos_liberados']}")
        print("="*60 + "\n")
        
        # Guardar en el log
        self.logger.info("--- MÉTRICAS FINALES DE LA SIMULACIÓN ---")
        self.logger.info(f"Procesos Totales: {total_procesos} | Terminados OK: {len(terminados_ok)} | Terminados Forzosos: {len(terminados_mal)}")
        self.logger.info(f"Interbloqueos Detectados: {self.metricas['interbloqueos_detectados']} | Recursos Liberados: {self.metricas['recursos_liberados']}")
        
    def ejecutar_un_paso_gui(self):
        """Ejecuta un solo tick para el modo paso a paso de la GUI"""
        #Ejecuta solo un tick para el paso a paso
        self.reloj += 1

        self.intentar_asignar_recursos_libres()
        
        # Ejecuta procesos
        self.avanzar_procesos_activos()

        # Detecta interbloqueos
        hay_bloqueo, pids_afectados = self.detector.detectar_y_analizar(self.procesos)

        # Recupera
        if hay_bloqueo:
            recursos_salvados = self.recuperador.resolver_interbloqueo(pids_afectados, self.procesos)
            self.reasignar_recursos(recursos_salvados)

        return hay_bloqueo

if __name__ == "__main__":
    import os
    
    # Ruta dinámica para el tester
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_json = os.path.join(directorio_actual, "ejemplo.json")
    
    motor = MotorSimulador(ruta_json)
    if motor.preparar_sistema():
        motor.ejecutar_paso_a_paso(limite_ticks=5)