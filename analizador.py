# analizador.py
# Versión A: Analizador de sentimientos en español - Reglas mejoradas
# Listo para copiar/pegar. Autor: (mejorado por ChatGPT)
# Recomendación: ejecutar con Python 3.8+

import re
import logging
from collections import defaultdict, Counter
from typing import List, Dict, Any

# ---------- CONFIGURACIÓN ----------
DEFAULT_DEBUG = False

# ---------- UTILIDADES DE NORMALIZACIÓN ----------
def reemplazar_acentos(texto: str) -> str:
    # Mapeo básico para normalizar acentos y algunas ligaduras
    mapa = str.maketrans({
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ü': 'u', 'Ü': 'U'
    })
    return texto.translate(mapa)

def quitar_espacios_extra(texto: str) -> str:
    return re.sub(r'\s+', ' ', texto).strip()

def normalizar_repeticiones(texto: str) -> str:
    # "noooooo" -> "nooo" (limitar repeticiones)
    texto = re.sub(r'(.)\1{3,}', r'\1\1\1', texto)
    # Puntuación repetida "!!!" -> "!!"
    texto = re.sub(r'([!?\.]){3,}', r'\1\1', texto)
    return texto

# Tokenización simple pero respetando emojis y palabras con apostrofes
def tokenize(texto: str) -> List[str]:
    # Mantener emojis como tokens (rango básico)
    emoji_re = r'[\U0001F300-\U0001F64F\U0001F680-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]'
    # Separar palabras, números, emoticonos y emojis
    tokens = re.findall(rf"{emoji_re}|[A-Za-z0-9ñÑáéíóúÁÉÍÓÚüÜ]+(?:'[A-Za-z]+)?|[!?.]+|[,;:()\"%€$]+", texto)
    return tokens

# ---------- CLASE PRINCIPAL ----------
class AnalizadorSentimientos:
    """
    Analizador de sentimiento en español - Sólo reglas (no ML).
    Diseñado para mejorar detección de matices, negaciones y contexto.
    """

    def __init__(self, debug: bool = DEFAULT_DEBUG):
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # Diccionarios / lexicos
        self.p_positivas = set([
            'excelente','increible','increíble','genial','perfecto','perfecta','perfectos','perfectas',
            'maravilloso','maravillosa','fantastico','fantástico','fantastica','fenomenal','magico','magnifico',
            'sorprendente','satisfecho','satisfecha','satisfechos','encanta','encantó','recomiendo','recomendado',
            'recomendada','vale','pena','util','útil','practico','práctico','bueno','buena','buenisimo','buenísimo',
            'amable','rapido','rápido','eficiente','gracias','feliz','contento','contenta','de lujo','de lujo',
            'lo amo','lo adoro','mejor','mejoró','supero','superó','sobresaliente','impecable','premium','decalidad',
            'exitoso','estupendo','excelente servicio','vale cada peso','muy bueno','muy buena'
        ])

        self.p_negativas = set([
            'malo','mala','peor','peores','pésimo','pésima','horrible','terrible','decepcion','decepciono','decepcionante',
            'defectuoso','defectuosa','defecto','defectos','dañado','dañada','roto','rota','rota','falla','fallas',
            'inutil','inútil','inservible','estafa','fraude','engaño','engañó','engañar','cobro','lento','lenta',
            'caro','cara','basura','asco','trabas','traba','crash','crasheo','crashé','error','errores','frustrante',
            'no sirve','no funciona','no me gustó','no me gusto','jamás','nunca','pésimo servicio','miserable'
        ])

        # palabras que suelen invertir o afectar (doble sentido)
        self.negaciones = set(['no','nunca','jamás','jamas','tampoco','sin','ni','nadie','ninguno','ninguna','nada'])
        self.intensificadores = set(['muy','mucho','muchisimo','muchísimo','bastante','totalmente','completamente','absolutamente','realmente','sumamente','demasiado','extremadamente','super','súper'])
        self.atenuadores = set(['poco','algo','medianamente','relativamente','ligeramente','apenas','casi','algo','un poco'])

        # frases contextuales con peso mayor
        self.frases_positivas = set([
            'lo recomiendo','vale la pena','supero las expectativas','superó expectativas','superó mis expectativas',
            'cumple con lo prometido','excelente calidad','volveré a comprar','volveré a comprarlo','totalmente recomendado',
            'mejor compra','vale cada peso','de primera','de primera calidad','100% recomendado','recomendado 100'
        ])
        self.frases_negativas = set([
            'pérdida de tiempo','perdida de tiempo','no vale la pena','no lo recomiendo','no lo volveré a comprar','no volveré a comprar','estafa total','decepción total','no merece'
        ])

        # bigrams/combinaciones que suelen ser indicativas
        self.bigrams_positive = set(['muy bueno','muy bien','excelente servicio','muy util','muy útil','super recomendado','superó expectativas'])
        self.bigrams_negative = set(['muy malo','muy mal','no funciona','no sirve','pésimo servicio','nunca mas','nunca más','no lo recomiendo'])

        # Aspectos analizables
        self.aspectos = {
            'calidad': ['calidad', 'material', 'acabado', 'duradero', 'duradera', 'resistente'],
            'precio': ['precio', 'caro', 'barato', 'coste', 'costo', 'economico', 'económico'],
            'servicio': ['servicio', 'atención', 'atencion', 'entrega', 'envio', 'envío', 'soporte', 'devolución'],
            'funcionalidad': ['funciona', 'funcionar', 'uso', 'usar', 'util', 'útil', 'práctico']
        }

        # Umbrales y pesos
        self.PESO_FRASE = 2.5
        self.PESO_BIGRAM = 1.5
        self.PESO_PALABRA_MUY = 2.0
        self.PESO_PALABRA = 1.0
        self.PESO_NEG_MUY = -2.2
        self.PESO_NEG = -1.0

    # ---------- Normalización y limpieza ----------
    def limpiar_texto(self, texto: str) -> str:
        if not texto:
            return ''
        # Remover URLs
        texto = re.sub(r'http\S+|www\.\S+', '', texto)
        # Reemplazar acentos y normalizar case
        texto = reemplazar_acentos(texto)
        texto = texto.lower()
        # Normalizar repeticiones y signos
        texto = normalizar_repeticiones(texto)
        texto = quitar_espacios_extra(texto)
        return texto

    # ---------- Detección de negación ----------
    def ventana_negacion(self, tokens: List[str], indice: int, ventana: int = 3) -> bool:
        """
        Busca negaciones en un rango de N tokens antes de la palabra objetivo.
        Retorna True si cantidad de negaciones es impar (invirtiendo el sentido).
        """
        inicio = max(0, indice - ventana)
        segmento = tokens[inicio:indice]
        neg_count = sum(1 for t in segmento if t in self.negaciones)
        if self.debug:
            logging.debug(f"Ventana negación tokens[{inicio}:{indice}]={segmento} -> neg_count={neg_count}")
        return (neg_count % 2) == 1

    # ---------- Calcular modificadores (intensidad) ----------
    def calcular_modificador(self, tokens: List[str], indice: int) -> float:
        """
        Busca intensificadores o atenuadores en ventana corta (2 tokens previos).
        Retorna factor multiplicador (>1 intensifica, <1 atenúa)
        """
        factor = 1.0
        inicio = max(0, indice - 2)
        for t in tokens[inicio:indice]:
            if t in self.intensificadores:
                factor *= 1.5
            elif t in self.atenuadores:
                factor *= 0.7
        # limitar factor para estabilidad
        factor = max(0.4, min(factor, 3.0))
        if self.debug:
            logging.debug(f"Modificador tokens[{inicio}:{indice}] -> factor={factor}")
        return factor

    # ---------- Detección de sarcasmo simple ----------
    def detectar_sarcasmo_simple(self, texto_original: str) -> bool:
        """
        Heurística sencilla: palabras positivas con muchos puntos suspensivos o '!' inconsistentes,
        o frases que combinan positivo + 'pero' negativo muy cerca, etc.
        """
        # "Excelente..." (con puntos de suspenso) o "Genial!!!" seguido de negativo
        if re.search(r'(excelente|genial|perfecto|excelente)\s*[.!]{2,}', texto_original, flags=re.I):
            return True
        if re.search(r'\b(bueno|bien|genial)\b.*\b(peropero|pero)\b', texto_original.replace(' ', ''), flags=re.I):
            return True
        # patrón: "¡Genial, pero..." (positivo + "pero")
        if re.search(r'\b(excelente|genial|perfecto|bueno)\b.{0,12}\bpero\b', texto_original, flags=re.I):
            return True
        return False

    # ---------- Análisis principal ----------
    def analizar_sentimiento(self, texto: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento y devuelve: sentimiento (Positivo/Negativo/Neutro),
        emoji, score (-5..+5 aprox), confianza (0..100), conteo de positivos/negativos y aspectos.
        """
        if not texto or not isinstance(texto, str) or texto.strip() == '':
            return {
                'sentimiento': 'Neutro',
                'emoji': '😐',
                'score': 0.0,
                'confianza': 0,
                'positivos': 0,
                'negativos': 0,
                'aspectos': {}
            }

        texto_orig = texto
        texto = self.limpiar_texto(texto)
        tokens = tokenize(texto)
        tokens_simple = [t.strip('.,;:!?') for t in tokens if t.strip()]
        if self.debug:
            logging.debug(f"Original: {texto_orig}")
            logging.debug(f"Normalizado: {texto}")
            logging.debug(f"Tokens: {tokens}")

        score = 0.0
        cuenta_pos = 0.0
        cuenta_neg = 0.0
        palabras_analizadas = 0

        # 1) Frases contextuales (pesos grandes)
        for frase in self.frases_positivas:
            if frase in texto:
                score += self.PESO_FRASE
                cuenta_pos += abs(self.PESO_FRASE)
                palabras_analizadas += 1
                if self.debug:
                    logging.debug(f"Frase positiva detectada: {frase} -> +{self.PESO_FRASE}")
        for frase in self.frases_negativas:
            if frase in texto:
                score -= self.PESO_FRASE
                cuenta_neg += abs(self.PESO_FRASE)
                palabras_analizadas += 1
                if self.debug:
                    logging.debug(f"Frase negativa detectada: {frase} -> -{self.PESO_FRASE}")

        # 2) Bigrams / combinaciones
        texto_compacto = ' '.join(tokens_simple)
        for big in self.bigrams_positive:
            if big in texto_compacto:
                score += self.PESO_BIGRAM
                cuenta_pos += abs(self.PESO_BIGRAM)
                palabras_analizadas += 1
                if self.debug:
                    logging.debug(f"Bigram positivo: {big} -> +{self.PESO_BIGRAM}")
        for big in self.bigrams_negative:
            if big in texto_compacto:
                score -= self.PESO_BIGRAM
                cuenta_neg += abs(self.PESO_BIGRAM)
                palabras_analizadas += 1
                if self.debug:
                    logging.debug(f"Bigram negativo: {big} -> -{self.PESO_BIGRAM}")

        # 3) Palabras individuales con contexto (negación, modificadores)
        for i, token in enumerate(tokens_simple):
            if token == '':
                continue
            palabra = token.lower()
            es_pos = palabra in self.p_positivas
            es_neg = palabra in self.p_negativas

            if es_pos or es_neg:
                palabras_analizadas += 1
                mod = self.calcular_modificador(tokens_simple, i)
                invertir = self.ventana_negacion(tokens_simple, i, ventana=3)

                if es_pos:
                    peso_base = self.PESO_PALABRA_MUY if palabra in self.p_positivas and palabra in self.p_positivas else self.PESO_PALABRA
                    # Si hay negación, se invierte a negativo
                    if invertir:
                        peso = -peso_base * mod
                        cuenta_neg += abs(peso)
                        score += peso
                        if self.debug:
                            logging.debug(f"Palabra '{palabra}' invertida por negación -> {peso}")
                    else:
                        peso = peso_base * mod
                        cuenta_pos += peso
                        score += peso
                        if self.debug:
                            logging.debug(f"Palabra positiva '{palabra}' -> +{peso}")
                else:
                    # negativa
                    peso_base = self.PESO_NEG_MUY if palabra in self.p_negativas and palabra in self.p_negativas else self.PESO_NEG
                    if invertir:
                        # "no malo" -> positivo
                        peso = -peso_base * mod  # invertir signo (peso_base es negativo)
                        cuenta_pos += abs(peso)
                        score += peso
                        if self.debug:
                            logging.debug(f"Palabra negativa '{palabra}' invertida por negación -> +{peso}")
                    else:
                        peso = peso_base * mod
                        cuenta_neg += abs(peso)
                        score += peso
                        if self.debug:
                            logging.debug(f"Palabra negativa '{palabra}' -> {peso}")

        # 4) Emojis y signos de exclamación
        emojis_positivos = re.findall(r'[😊😃😄😁🤗❤️💖👍⭐🌟✨🎉😍🥰😘]', texto_orig)
        emojis_negativos = re.findall(r'[😞😢😭😔😩😫💔😠😡🤬😤]', texto_orig)
        score += len(emojis_positivos) * 1.0
        score -= len(emojis_negativos) * 1.0
        if self.debug and (emojis_positivos or emojis_negativos):
            logging.debug(f"Emojis +{len(emojis_positivos)} -{len(emojis_negativos)}")

        exclam_count = len(re.findall(r'!+', texto_orig))
        if exclam_count > 0:
            # amplifica el sentimiento dominante (pero con límite)
            if score > 0:
                score *= (1 + min(exclam_count * 0.08, 0.4))
            elif score < 0:
                score *= (1 + min(exclam_count * 0.08, 0.4))

        # 5) Aspectos encontrados
        aspectos_encontrados = {}
        for aspecto, claves in self.aspectos.items():
            for k in claves:
                if k in texto:
                    aspectos_encontrados.setdefault(aspecto, 0)
                    aspectos_encontrados[aspecto] += 1

        # 6) Sarcasmo (ajustar score si aplica)
        sarcasmo = self.detectar_sarcasmo_simple(texto_orig)
        if sarcasmo and score > 1.5:
            # reducir o invertir parcialmente
            score = -abs(score) * 0.6
            if self.debug:
                logging.debug("Sarcasmo detectado: ajuste de score")

        # Normalizar escala del score a un rango aproximado -5..+5
        # Dependiendo de la magnitud, escalamos suavemente
        # Primero acotamos extremos por robustez
        score = max(-10.0, min(10.0, score))
        # Escalado no lineal para mantener sensibilidad en torno a 0
        if score >= 0:
            score_scaled = (score / 10.0) * 5.0
        else:
            score_scaled = (score / 10.0) * 5.0

        # 7) Cálculo de confianza
        # Basado en: cantidad de tokens analizados, diferencia entre positivo/negativo, presencia de frases contextuales
        suma_cuentas = cuenta_pos + cuenta_neg
        if suma_cuentas > 0:
            diff = abs(cuenta_pos - cuenta_neg)
            confianza = (diff / suma_cuentas) * 100
            # ajustar por palabras analizadas
            confianza = confianza + min(max((palabras_analizadas - 1) * 8, 0), 25)
            # si hay frases fuertes, subir confianza
            if any(f in texto for f in (self.frases_positivas | self.frases_negativas)):
                confianza = min(confianza + 10, 100)
        else:
            confianza = 35.0  # default cuando no hay señales

        # Si sarcasmo detectado, bajar confianza
        if sarcasmo:
            confianza = max(20.0, confianza - 25.0)

        # Ajuste final de confianza y límites
        confianza = max(0.0, min(100.0, confianza))

        # Clasificación final basada en umbrales del score escalado
        umbral_fuerte = 1.2   # en escala -5..5
        umbral_debil = 0.4

        if abs(score_scaled) < umbral_debil:
            sentimiento = 'Neutro'
            emoji = '😐'
        elif score_scaled >= umbral_fuerte:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_scaled > umbral_debil:  # typo safety, not reached
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_scaled <= -umbral_fuerte:
            sentimiento = 'Negativo'
            emoji = '😞'
        else:
            sentimiento = 'Negativo'
            emoji = '😞'

        # Afinar: si se detectaron palabras neutras y score pequeño, subir probabilidad de neutro
        palabras_neutras = set(['normal','regular','ok','aceptable','promedio','cumple','justo','usual'])
        if any(p in texto for p in palabras_neutras) and abs(score_scaled) < 1.0:
            sentimiento = 'Neutro'
            emoji = '😐'
            confianza = max(confianza, 50.0)

        # Resultado final
        resultado = {
            'sentimiento': sentimiento,
            'emoji': emoji,
            'score': round(score_scaled, 2),
            'confianza': round(confianza, 1),
            'positivos': round(cuenta_pos, 2),
            'negativos': round(cuenta_neg, 2),
            'aspectos': aspectos_encontrados,
            'tokens_analizados': palabras_analizadas,
            'sarcasmo': sarcasmo
        }

        if self.debug:
            logging.debug(f"Resultado raw score: {score}, scaled: {score_scaled}, cuenta_pos: {cuenta_pos}, cuenta_neg: {cuenta_neg}")
            logging.debug(f"Resultado final: {resultado}")

        return resultado

# ---------- Funciones auxiliares para procesar lotes y reportes ----------
def procesar_comentarios_completos(comentarios: List[str], debug: bool = False) -> List[Dict[str, Any]]:
    analizador = AnalizadorSentimientos(debug=debug)
    resultados = []
    for i, c in enumerate(comentarios, 1):
        r = analizador.analizar_sentimiento(c)
        resultados.append({
            'id': i,
            'comentario': c,
            'sentimiento': r['sentimiento'],
            'emoji': r['emoji'],
            'score': r['score'],
            'confianza': r['confianza'],
            'aspectos': r['aspectos'],
            'sarcasmo': r['sarcasmo']
        })
    return resultados

def generar_reporte(resultados: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(resultados)
    if total == 0:
        return {}
    cont = Counter(r['sentimiento'] for r in resultados)
    reporte = {
        'total': total,
        'positivos': cont.get('Positivo', 0),
        'negativos': cont.get('Negativo', 0),
        'neutros': cont.get('Neutro', 0),
        'porcentaje_positivos': round(cont.get('Positivo', 0) / total * 100, 2),
        'porcentaje_negativos': round(cont.get('Negativo', 0) / total * 100, 2),
        'porcentaje_neutros': round(cont.get('Neutro', 0) / total * 100, 2)
    }
    return reporte

def obtener_top_comentarios(resultados: List[Dict[str, Any]], tipo: str = 'positivos', cantidad: int = 5) -> List[Dict[str, Any]]:
    if tipo == 'positivos':
        filtrados = [r for r in resultados if r['sentimiento'] == 'Positivo']
        orden = sorted(filtrados, key=lambda x: x['score'], reverse=True)
    elif tipo == 'negativos':
        filtrados = [r for r in resultados if r['sentimiento'] == 'Negativo']
        orden = sorted(filtrados, key=lambda x: x['score'])  # score negativo orden ascendente
    else:
        orden = []
    return orden[:cantidad]

# ---------- EJEMPLO / PRUEBAS ----------
if __name__ == "__main__":
    analizador = AnalizadorSentimientos(debug=True)
    pruebas = [
        "Me encantó el servicio, todo llegó súper rápido.",
        "La verdad no estoy satisfecho, esperaba mucho más.",
        "Está bien, pero podría mejorar en algunos detalles.",
        "¿Alguien más tuvo problemas al iniciar sesión?",
        "Excelente atención, volvería a comprar sin duda.",
        "Qué decepción, no funciona como prometen.",
        "El producto llegó dañado, quiero un reembolso.",
        "JAJAJA esto está increíble 😂",
        "No me gustó para nada, es una estafa",
        "Pensé que sería mediocre, pero terminó sorprendiéndome para bien.",
        "No sirve, ya lo intenté varias veces.",
        "Perfecto para lo que busco, gracias!",
        "0/10, jamás volvería a usar esto."
    ]

    resultados = procesar_comentarios_completos(pruebas, debug=True)
    for r in resultados:
        print(f"[{r['id']}] {r['emoji']} {r['sentimiento']:8s} | Score: {r['score']:>5} | Conf: {r['confianza']:>5}% | {r['comentario']}")
    print("\nREPORTE:")
    print(generar_reporte(resultados))
    print("\nTOP negativos:")
    print(obtener_top_comentarios(resultados, tipo='negativos', cantidad=3))
    print("\nTOP positivos:")
    print(obtener_top_comentarios(resultados, tipo='positivos', cantidad=3))
