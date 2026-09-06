import matplotlib.pyplot as plt
import networkx as nx


class MóduloInterbloqueos:
    def __init__(self, lista_recursos_exclusivos, permite_expropiacion):
        # Guardamos qué recursos no se pueden compartir
        self.recursos_exclusivos = lista_recursos_exclusivos
        self.permite_expropiacion = permite_expropiacion 

    def detectar_y_analizar(self, procesos):
        grafo = nx.DiGraph()
        
        # 1. Construir el grafo real con los datos
        for p in procesos:
            # Aristas de Retención (Recurso -> Proceso)
            for r in p.recursos_actuales:
                grafo.add_edge(r, p.pid)
            # Aristas de Espera (Proceso -> Recurso)
            for r in p.recursos_necesarios:
                grafo.add_edge(p.pid, r)

        # 2. Comprobar ESPERA CIRCULAR (Condición 4)
        try:
            ciclo = nx.find_cycle(grafo, orientation="original")
            espera_circular = True
            
            # --- CORRECCIÓN AQUÍ ---
            nodos_en_ciclo = set()
            for arista in ciclo:
                nodos_en_ciclo.add(arista[0]) # Saca el origen (Ej: 'Impresora_1')
                nodos_en_ciclo.add(arista[1]) # Saca el destino (Ej: 'P1')
                
            # Ahora sí buscamos en los textos sueltos
            pids_validos = [p.pid for p in procesos]
            procesos_en_ciclo = [nodo for nodo in nodos_en_ciclo if nodo in pids_validos]
            # Print de depuración para asegurarnos de que atrapó a P1 y P2
            print(f"\n[DEBUG] Procesos atrapados en el ciclo: {procesos_en_ciclo}")
            
        except nx.NetworkXNoCycle:
            espera_circular = False
            return False, [] # Si no hay ciclo, no hay interbloqueo

        print("\n--- ANALIZANDO LAS 4 CONDICIONES AUTOMÁTICAMENTE ---")
        
        # 3. Comprobar EXCLUSIÓN MUTUA (Condición 1)
        # ¿Los recursos involucrados en el ciclo están en la lista de exclusivos?
        recursos_en_ciclo = [nodo[0] for nodo in ciclo if nodo[0] in self.recursos_exclusivos]
        explotacion_mutua = len(recursos_en_ciclo) > 0
        print(f"1. Exclusión mutua: {explotacion_mutua} (Recursos exclusivos detectados: {recursos_en_ciclo})")

        # 4. Comprobar ESPERA Y RETENCIÓN (Condición 2)
        # ¿Hay algún proceso en el ciclo que TENGA recursos (>0) y PIDA recursos (>0)?
        espera_retencion = False
        for p in procesos:
            if p.pid in procesos_en_ciclo:
                print("entró a p.pid in procesos")
                if len(p.recursos_actuales) > 0 and len(p.recursos_necesarios) > 0:
                    espera_retencion = True
                    break
        print(f"2. Espera y retención: {espera_retencion}")

        # 5. Comprobar NO EXPROPIACIÓN (Condición 3)
        # En esta simulación, es True por defecto hasta que actúa el recuperador
        
        condicion_no_expropiacion = not self.permite_expropiacion
        print(f"3. No expropiación: {condicion_no_expropiacion} (Configuración del sistema)")
        
        print(f"4. Espera circular: {espera_circular} (Ciclo detectado: {ciclo})")

        # Mostrar visualización obligatoria
        if espera_circular:
            self.visualizar_grafo(grafo)
            if explotacion_mutua== True and espera_circular== True and espera_retencion==True and condicion_no_expropiacion== True:
                return True, procesos_en_ciclo
            return False, []

    def visualizar_grafo(self, grafo):
        plt.figure(figsize=(6, 4))
        pos = nx.spring_layout(grafo)
        nx.draw(grafo, pos, with_labels=True, node_color="lightblue", font_weight="bold", node_size=1500, arrows=True)
        plt.title("Grafo de Asignación de Recursos (Interbloqueo)")
        plt.show()