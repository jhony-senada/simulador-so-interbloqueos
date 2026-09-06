import time

from constructor_casos import ContrictorEscenarios
from detector import MóduloInterbloqueos
from recuperacion import TiradorDeParoInteligente


class MotorSimulador:
    def __init__(self, ruta_escenario):
        self.ruta_escenario = ruta_escenario
        self.procesos = []
        self.detector = None
        self.recuperador = TiradorDeParoInteligente()
        self.reloj = 0

    def preparar_sistema(self):
        print("=== INICIANDO ARRANQUE DEL SISTEMA OPERATIVO ===")
        constructor = ContrictorEscenarios(self.ruta_escenario)
        constructor.cargar_datos()

        datos_sistema, permite_expropiar = constructor.inicializar_sistema()
        if not datos_sistema: return False

        ids_exclusivos = [r['id'] for r in datos_sistema[1]]
        self.procesos = constructor.inicializar_proceso()
        
        # Validar estado inicial: Si necesitan recursos, inician esperando
        for p in self.procesos:
            if len(p.recursos_necesarios) > 0:
                p.estado_inicial = "esperando"
                
        self.detector = MóduloInterbloqueos(ids_exclusivos, permite_expropiar)
        return True

    def reasignar_recursos(self, recursos_liberados):
        if not recursos_liberados: return
        
        print("\n>> [GESTOR DE RECURSOS] Reasignando recursos recuperados...")
        for recurso in recursos_liberados:
            asignado = False
            # ORDENAMOS: Prioridad a los procesos que necesitan menos recursos para terminar
            procesos_ordenados = sorted(self.procesos, key=lambda x: len(x.recursos_necesarios))
            
            for p in procesos_ordenados:
                if p.estado_inicial != "terminado_forzosamente" and recurso in p.recursos_necesarios:
                    p.recursos_necesarios.remove(recurso)
                    p.recursos_actuales.append(recurso)
                    print(f" [+] Recurso '{recurso}' asignado a {p.pid}.")
                    
                    if len(p.recursos_necesarios) == 0:
                        p.estado_inicial = "activo"
                        print(f" [^] {p.pid} tiene todos sus recursos. Despierta a estado 'activo'.")
                    asignado = True
                    break 
            if not asignado:
                print(f" [-] Recurso '{recurso}' queda libre en el sistema.")

    def avanzar_procesos_activos(self):
        print("\n>> [CPU] Ejecutando procesos activos...")
        for p in self.procesos:
            # SOLO ejecuta si tiene todos los recursos que necesita (recursos_necesarios == 0)
            if p.estado_inicial == "activo" and len(p.recursos_necesarios) == 0:
                if len(p.acciones) > 0:
                    accion = p.acciones.pop(0) 
                    print(f" [>] {p.pid} ejecutando: {accion.tipo} -> {accion.objetivo}")
                
                # Si se quedó sin acciones, termina y LIBERA SUS RECURSOS
                if len(p.acciones) == 0:
                    p.estado_inicial = "terminado_exitosamente"
                    print(f" [✓] {p.pid} ha completado tareas y LIBERA sus recursos.")
                    recursos_a_liberar = p.recursos_actuales.copy()
                    p.recursos_actuales = []
                    # Devolvemos los recursos al sistema para que otros los usen
                    self.reasignar_recursos(recursos_a_liberar)

    def ejecutar_paso_a_paso(self, limite_ticks=4):
        print("\n=== INICIANDO MODO PASO A PASO ===")
        
        while self.reloj < limite_ticks:
            self.reloj += 1
            print(f"\n" + "="*40 + f"\n   [TICK DE RELOJ: {self.reloj}]\n" + "="*40)
            
            # 1. Ejecutar procesos primero (para que los que no ocupan nada terminen y liberen)
            self.avanzar_procesos_activos()
            
            # 2. Detectar Interbloqueos con el nuevo estado
            hay_bloqueo, pids_afectados = self.detector.detectar_y_analizar(self.procesos)
            
            # 3. Recuperar y Reasignar si hay problemas
            if hay_bloqueo:
                print(f"\n[!] ALERTA CRÍTICA: Interbloqueo detectado.")
                recursos_salvados = self.recuperador.resolver_interbloqueo(pids_afectados, self.procesos)
                self.reasignar_recursos(recursos_salvados) 
            else:
                print("\n[✓] Sistema estable.")
            
            self.mostrar_estado_sistema()
            time.sleep(1.5)

    def mostrar_estado_sistema(self):
        activos = [p.pid for p in self.procesos if p.estado_inicial == "activo"]
        esperando = [p.pid for p in self.procesos if p.estado_inicial == "esperando"]
        terminados = [p.pid for p in self.procesos if p.estado_inicial.startswith("terminado")]
        
        print(f"\n--- ESTADO DEL SISTEMA ---")
        print(f" -> Activos: {activos if activos else 'Ninguno'}")
        print(f" -> Esperando: {esperando if esperando else 'Ninguno'}")
        print(f" -> Terminados: {terminados if terminados else 'Ninguno'}")


if __name__ == "__main__":
    motor = MotorSimulador("D:\Apuntes\Codigos\Proyecto\ejemplo2.json")
    if motor.preparar_sistema():
        motor.ejecutar_paso_a_paso(limite_ticks=5)