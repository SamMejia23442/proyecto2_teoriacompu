class Transicion:
    def __init__(self, simbolo, destino):
        # caracter que dispara la transicion, se dice e para epsilon
        self.simbolo = simbolo
        # estado al que llega
        self.destino = destino


class TransicionPDA(Transicion):
    def __init__(self, simbolo_entrada, simbolo_pop, destino, simbolos_push, etiqueta=""):
        # extiende la transicion de automata finito agregando operaciones de pila
        super().__init__(simbolo_entrada, destino)
        # simbolo que debe estar en el tope de la pila para extraer (e si no extrae)
        self.simbolo_pop = simbolo_pop
        # lista de simbolos que se empujan a la pila (el primero queda en el tope)
        self.simbolos_push = list(simbolos_push) if simbolos_push else []
        # descripcion opcional de la regla gramatical asociada
        self.etiqueta = etiqueta

    def __repr__(self):
        push_str = " ".join(self.simbolos_push) if self.simbolos_push else "e"
        return f"({self.simbolo}, {self.simbolo_pop} -> {push_str}) => q{self.destino.id}"


class Estado:
    # contador global para dar id unico a cada estado
    _id_counter = 0

    def __init__(self, es_aceptacion=False, nombre=None):
        self.id = Estado._id_counter
        Estado._id_counter += 1
        self.nombre = nombre if nombre is not None else f"q{self.id}"
        
        self.es_aceptacion = es_aceptacion
        # lista de flechas que salen del nodo
        self.transiciones = []

    def agregar_transicion(self, simbolo, destino):
        self.transiciones.append(Transicion(simbolo, destino))

    def agregar_transicion_pda(self, simbolo_entrada, simbolo_pop, destino, simbolos_push, etiqueta=""):
        self.transiciones.append(
            TransicionPDA(simbolo_entrada, simbolo_pop, destino, simbolos_push, etiqueta)
        )


class AFN:
    def __init__(self, estado_inicial, estado_final):
        # thompson genera fragmentos con un inicio y fin claro
        self.estado_inicial = estado_inicial
        self.estado_final = estado_final


class AFD:
    def __init__(self, estado_inicial):
        self.estado_inicial = estado_inicial
        # el afd puede tener multiples estados de aceptacion
        self.estados_aceptacion = []
        # se guardan todos los estados para minimizarlos luego
        self.estados = []


class Pila:
    def __init__(self, contenido_inicial=None):
        # el tope de la pila es el ultimo elemento de la lista
        self.elementos = list(contenido_inicial) if contenido_inicial else []

    def push(self, simbolo):
        if simbolo != 'e':
            self.elementos.append(simbolo)

    def push_secuencia(self, simbolos):
        # recibe simbolos en orden de produccion (ej. ['NP', 'VP'])
        # se empujan en orden inverso para que el primero quede en el tope
        for s in reversed(simbolos):
            if s != 'e':
                self.elementos.append(s)

    def pop(self):
        if not self.elementos:
            return None
        return self.elementos.pop()

    def tope(self):
        if not self.elementos:
            return None
        return self.elementos[-1]

    def esta_vacia(self):
        return len(self.elementos) == 0

    def clonar(self):
        return Pila(self.elementos)

    def como_cadena(self):
        # muestra el tope de la pila a la izquierda (notacion estandar de ID)
        if not self.elementos:
            return "e"
        return " ".join(reversed(self.elementos))

    def __len__(self):
        return len(self.elementos)


class DescripcionInstantanea:
    def __init__(self, estado, entrada_restante, pila_str, accion=""):
        # representa la tupla (q, w, gamma) en un instante del calculo
        self.estado = estado
        self.entrada_restante = entrada_restante
        self.pila_str = pila_str
        self.accion = accion

    def formatear(self):
        w_str = " ".join(self.entrada_restante) if self.entrada_restante else "e"
        base = f"({self.estado}, '{w_str}', [{self.pila_str}])"
        if self.accion:
            return f"{base}   <-- {self.accion}"
        return base


class PDA(AFD):
    def __init__(self, estado_inicial, simbolo_inicial_pila='Z0'):
        # extiende la definicion de automata finito agregando alfabeto y pila
        super().__init__(estado_inicial)
        self.alfabeto_entrada = set()
        self.alfabeto_pila = set()
        self.simbolo_inicial_pila = simbolo_inicial_pila
        self.pila = Pila([simbolo_inicial_pila])

