import unittest
from gramatica import construir_gramatica_proyecto2, tokenizar_frase
from pda import gramatica_a_pda, simular_pda
from cyk import algoritmo_cyk, calcular_operaciones_teoricas_cyk

class TestProyecto2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = construir_gramatica_proyecto2()
        cls.pda = gramatica_a_pda(cls.g)

    def assert_ambos(self, frase, esperado, msg=""):
        res_pda = simular_pda(self.pda, frase)
        res_cyk = algoritmo_cyk(self.g, frase)
        
        self.assertEqual(res_pda['aceptada'], esperado, f"PDA fallo en '{frase}': {msg}. Esperado {esperado}, obtuvo {res_pda['aceptada']}")
        self.assertEqual(res_cyk['aceptada'], esperado, f"CYK fallo en '{frase}': {msg}. Esperado {esperado}, obtuvo {res_cyk['aceptada']}")
        self.assertGreater(res_pda['operaciones'], 0)
        self.assertGreater(res_cyk['operaciones'], 0)
        
        if esperado:
            self.assertGreater(len(res_pda['descripciones_instantaneas']), 0)
            self.assertGreater(len(res_pda['derivacion']), 0)
            self.assertGreater(len(res_cyk['derivacion']), 0)
            self.assertGreater(len(res_cyk['arbol']), 0)

    def test_frases_validas_simples(self):
        casos = [
            "he cooks",
            "she drinks",
            "he eats",
            "she cuts",
            "the cat cooks",
            "a dog drinks",
            "the fork cuts",
            "a spoon drinks"
        ]
        for c in casos:
            self.assert_ambos(c, True)

    def test_frases_validas_transitivas(self):
        casos = [
            "he eats a cake",
            "she drinks the juice",
            "the cat cuts the meat",
            "a dog cooks a soup",
            "she cuts the beer"
        ]
        for c in casos:
            self.assert_ambos(c, True)

    def test_frases_validas_con_preposicionales(self):
        casos = [
            "he eats with a fork",
            "she drinks in the oven",
            "the dog eats the meat with a spoon",
            "the cat cuts a cake with a knife in the oven",
            "he drinks the juice with a spoon in the oven with a knife"
        ]
        for c in casos:
            self.assert_ambos(c, True)

    def test_frases_invalidas_sintaxis(self):
        casos = [
            "",
            "eats",
            "she",
            "cat drinks", # N necesita Det
            "she eats cake", # N cake necesita Det
            "he drinks juice with a spoon", # N juice necesita Det
            "the cat drinks oven", # oven necesita Det y prep
            "cooks she",
            "with a fork he eats",
            "the the cat eats",
            "she eats a",
            "she eats with with a fork"
        ]
        for c in casos:
            self.assert_ambos(c, False)

    def test_frases_palabras_fuera_alfabeto(self):
        casos = [
            "she eats pizza",
            "a robot drinks oil",
            "the elephant cuts the grass"
        ]
        for c in casos:
            self.assert_ambos(c, False)

    def test_cyk_teorico_vs_empirico(self):
        for n in range(1, 10):
            tokens = ["she"] + ["eats"] * (n - 1)
            frase = " ".join(tokens)
            res = algoritmo_cyk(self.g, frase)
            ops_teorica = calcular_operaciones_teoricas_cyk(n, num_terminales=len(self.g.producciones_terminales), num_binarias=len(self.g.producciones_binarias))
            self.assertEqual(res['operaciones'], ops_teorica, f"Discrepancia en n={n}: empirico={res['operaciones']}, teorico={ops_teorica}")

if __name__ == '__main__':
    unittest.main()
