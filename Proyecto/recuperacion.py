class TiradorDeParoInteligente:
    def __init__(self, permite_expropiacion):
        # Recibe la configuración estricta del JSON
        self.permite_expropiacion = permite_expropiacion
    def resolver_interbloqueo(self, pids_bloqueados, lista_procesos_totales):
        print("\n>> [TIRADOR DE PARO] Analizando los procesos...")
        
        # 1. Obtener los objetos Proceso reales usando los PIDs atrapados
        victimas_potenciales = [p for p in lista_procesos_totales if p.pid in pids_bloqueados]
        
        # 2. Calcular la heurística de costo (Elegir al que tenga menos recursos)
        # lambda p: len(p.recursos_actuales) ordena de menor a mayor cantidad de recursos
        victimas_potenciales.sort(key=lambda p: len(p.recursos_actuales))
        victima = victimas_potenciales[0]
        
        cantidad_recursos = len(victima.recursos_actuales)
        print(f"[*] Víctima seleccionada: {victima.pid} (Acapara {cantidad_recursos} recursos).")
        
        recursos_recuperados = []
        
        # 3. El Sistema Decide Dinámicamente
        if self.permite_expropiacion and cantidad_recursos <= 1:
            # ESTRATEGIA: EXPROPIACIÓN TÁCTICA
            print(f"[*] Decisión del Sistema: EXPROPIAR RECURSOS. El proceso {victima.pid} perderá sus recursos pero seguirá vivo... por ahora...")
            recursos_recuperados = victima.recursos_actuales.copy()
            
            victima.recursos_actuales = []
            victima.estado_inicial = "esperando" # Se queda en pausa
            victima.recursos_necesarios.extend(recursos_recuperados) # Tendrá que volver a pedirlos
            
        else:
            if not self.permite_expropiacion:
                print("[!] Regla estricta de retención activa (No Expropiación = True).")
            # ESTRATEGIA: TERMINACIÓN NUCLEAR
            print(f"[*] Decisión del Sistema: TERMINAR PROCESO. El proceso {victima.pid} es un cuello de botella y será destruido.")
            recursos_recuperados = victima.recursos_actuales.copy()
            
            victima.estado_inicial = "terminado_forzosamente"
            victima.recursos_actuales = []
            victima.recursos_necesarios = []
            victima.acciones = [] # Borramos sus acciones pendientes para que el motor lo ignore
            
        print(f"[+] El interbloqueo se ha roto. Recursos devueltos al sistema: {recursos_recuperados}")
        return recursos_recuperados