class TiradorDeParo:
    def __init__(self, gestor_recursos, detector_interbloqueos):
        self.gestor_recursos = gestor_recursos
        self.detector = detector_interbloqueos

    def resolver_interbloqueo(self, procesos_bloqueados):
        print("\n[!] TIRADOR DE PARO ACTIVADO: Resolviendo interbloqueo...")
        
        # Estrategia: Seleccionar un proceso "víctima" para terminarlo y liberar sus recursos.
        # Para hacerlo simple, elegimos el último proceso que entró en la lista de bloqueados.
        victima = procesos_bloqueados.pop() 
        
        print(f"[*] Proceso víctima seleccionado: {victima.pid}")
        
        # 1. Identificar qué recursos tenía la víctima (ej. "Impresora_1")[cite: 3]
        recursos_a_liberar = victima.recursos_actuales 
        
        # 2. Liberar los recursos a la fuerza (rompemos la condición de No Expropiación)
        for recurso in recursos_a_liberar:
            self.gestor_recursos.liberar_recurso(victima.pid, recurso)
            print(f"[*] Recurso {recurso} liberado a la fuerza de {victima.pid}")
            
        # 3. Cambiar el estado de la víctima
        victima.estado = "terminado_forzosamente"
        victima.recursos_actuales = []
        
        # 4. Actualizar el grafo del detector de interbloqueos
        self.detector.remover_nodo(victima.pid)
        
        print("[+] Interbloqueo resuelto. El sistema puede continuar con los demás procesos.")
        return True