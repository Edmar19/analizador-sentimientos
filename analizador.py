# analizador.py
# Versión mejorada y corregida del Analizador de Sentimientos en español (solo reglas)
# Recomendación: ejecutar con Python 3.8+
import re
import logging
from collections import Counter
from typing import List, Dict, Any

# ---------- CONFIGURACIÓN ----------
DEFAULT_DEBUG = False

# ---------- UTILIDADES DE NORMALIZACIÓN ----------
def reemplazar_acentos(texto: str) -> str:
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
    # limitar repeticiones de letras y puntuación
    texto = re.sub(r'(.)\1{3,}', r'\1\1\1', texto)
    texto = re.sub(r'([!?\.]){3,}', r'\1\1', texto)
    return texto

def tokenize(texto: str) -> List[str]:
    # Mantener muchos emojis básicos y palabras con acentos/ñ; capturar puntuación significativa
    emoji_re = r'[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]'
    word_re = r"[A-Za-z0-9ñÑáéíóúÁÉÍÓÚüÜ]+(?:'[A-Za-z]+)?"
    punct_re = r"[!?.]+|[,;:()\"%€$]"
    pattern = rf"{emoji_re}|{word_re}|{punct_re}"
    return re.findall(pattern, texto, flags=re.UNICODE)

# ---------- CLASE PRINCIPAL ----------
class AnalizadorSentimientos:
    """
    Analizador de sentimiento en español - reglas (no ML).
    Mejoras: manejo de fuertes, mejor sarcasmo, aspectos con límites de palabra.
    """

    def __init__(self, debug: bool = DEFAULT_DEBUG):
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # Diccionarios / léxicos
        self.p_positivas = {
            'excelente','increible','increíble','genial','perfecto','perfecta','perfectos','perfectas',
            'maravilloso','maravillosa','fantastico','fantástico','fantastica','fenomenal','magico','magnifico',
            'sorprendente','satisfecho','satisfecha','encanta','encantó','recomiendo','recomendado',
            'vale','pena','util','útil','practico','práctico','bueno','buena','buenisimo','buenísimo',
            'amable','rapido','rápido','eficiente','gracias','feliz','contento','contenta','mejor','sobresaliente',
            'impecable','premium','exitoso','estupendo',
            'magnífica','magnífica','fantabuloso','increíblemente','óptimo','óptima','maravillosamente',
            'excelentemente','grandioso','grandiosa','placentero','placentera','positivo','positiva',
            'útilísimo','útilisima','formidable','excelentísimo','excelentisimo','comodísimo','comodisimo',
            'inmejorable','brillante','top','hermoso','hermosa','valioso','valiosa','increíblemente bueno',
            'agradable','agradablemente','perfectísimo','perfectisimo','eficaz','efectivo','efectiva',
            'superior','notable','respetuoso','respetuosa','profesional','detallado','detallada',
            'rápidamente','amablemente','gentil','atento','atenta','servicial','responsable','puntual',
            'topísimo','topisimo','maravillosamente bien','excelente atención','excelente servicio',
            'bien hecho','recomendadísimo','útil y práctico','estético','bonito','bonita',
            'encantador','encantadora','excepcional','extraordinario','extraordinaria'
            }
        # Palabras positivas FUERTES (peso mayor por sí solas)
        self.p_positivas_fuertes = {
            'excelente', 'increible', 'increíble', 'maravilloso', 'fenomenal',
            'impecable', 'sobresaliente', 'buenisimo', 'buenísimo', 'magnífico',
            'magnifico', 'espectacular', 'perfecto', 'perfecta', 'fantástico',
            'fantastico', 'extraordinario', 'extraordinaria', 'sensacional',
            'impresionante', 'formidable', 'inmejorable', 'brillante',
            'genial', 'excepcional', 'increíblemente bueno', 'maravillosamente bien'
            }

        self.p_negativas = {
            'malo','mala','peor','peores','pésimo','pésima','horrible','terrible','decepcion','decepcionante',
            'defectuoso','defectuosa','defecto','defectos','dañado','dañada','roto','rota','falla','fallas',
            'inutil','inútil','inservible','estafa','fraude','engaño','engañó','engañar','cobro','lento','lenta',
            'caro','cara','basura','asco','trabas','traba','crash','crasheo','crashé','error','errores','frustrante',
            'no sirve','no funciona','no me gustó','no me gusto','jamás','nunca','pésimo servicio','miserable',
            # Problemas de funcionamiento
            'no sirve','no funciona','no me gustó','no me gusto','no prende','no carga','no enciende',
            'se apaga','se traba','se congela','se descompone','se descompuso','se rompió','no responde',
            # Negativo fuerte sobre servicio
            'jamás','nunca','tarde','tardado','tardanza','pésimo servicio','mal servicio','descuidado',
            'irresponsable','mala atención','poca atención','mal trato','grosero','grosera','ineficiente',
            # Experiencia negativa
            'miserable','horrendo','terrible experiencia','torpe','deplorable','patético','patetico',
            'lamentable','deficiente','molesto','molesta','molestia','inaceptable','inadmisible',
            'desastroso','desastre','crítico','critico','problemático','problematico',
            # Temas de dinero
            'costoso','sobreprecio','carísimo','carisimo','cobran de más','cobro indebido','estafadores',
            'estafa total','robo','robado','robada','mal negocio',
            # Problemas de entrega/envío
            'no llegó','no llega','no entregaron','no entregan','tardó demasiado','dañado en el envío',
            'paquete incompleto','producto incompleto','faltante','faltantes',
            # Problemas de calidad
            'mal acabado','mal hecho','mal fabricado','mal ensamblado','pobre calidad','baja calidad',
            'cutre','barato y malo','quebradizo','fragil','frágil',
            # Sensación negativa
            'arrepentido','arrepentida','arrepentimiento','vergonzoso','desagradable','molesto','terrible producto'
            }
        
        # Palabras negativas FUERTES
        self.p_negativas_fuertes = {
            'pésimo','pesimo','horrible','terrible','estafa','fraude','miserable', "peligroso", "estafadores", "mentiras"
            'asqueroso', 'patetico', 'patético', 'nefasta', 'nefasto',
            'basura', 'malísimo', 'malisimo', 'engañoso', 'engaño',
            'inútil', 'inutil', 'desastroso', 'defectuoso', 'repugnante',
            'abominable', 'lamentable', 'engañoso', 'corrupto',
            'pérdida', 'perdida', 'timo', 'fraudulento', 'inservible',
            'pésima', 'pesima', 'horroroso', 'deplorable', 'desagradable',
            'peligrosísimo', 'peligrosisimo', 'arruinado', 'arruina',
            'falso', 'falsificado', 'ilegal', 'riesgoso', 'maltrato',
            'estafado', 'deficiente', 'descompuesto', 'estafadora',
            'inadmisible', 'vergonzoso', 'fatal', 'inaceptable'
            }

        # Negaciones e intensificadores
        self.negaciones = {'no','nunca','jamás','jamas','tampoco','sin','ni','nadie','ninguno','ninguna','nada'}
        self.intensificadores = {'muy','mucho','muchisimo','muchísimo','bastante','totalmente','completamente','absolutamente','realmente','sumamente','demasiado','extremadamente','super','súper'}
        self.atenuadores = {'poco','algo','medianamente','relativamente','ligeramente','apenas','casi','un poco'}

        # Frases contextuales
        self.frases_positivas = {
            'lo recomiendo', 'vale la pena', 'calidad excepcional', 'supero las expectativas',
            'superó expectativas', 'cumple con lo prometido', 'excelente calidad',
            'volveré a comprar', 'totalmente recomendado', 'super recomendado', 'mejor compra',
            'vale cada peso', 'de primera calidad', 'muy satisfecho', 'funciona perfectamente',
            'encantado con el producto', 'superó lo esperado', 'compra recomendada',
            'buena calidad', 'muy buena compra', 'me sorprendió para bien',
            'excelente atención', 'justo lo que buscaba', 'funciona de maravilla',
            'producto confiable', 'gran experiencia de compra', 'vale muchísimo la pena'
            }
        self.frases_negativas = {
            'perdida de tiempo', 'no vale la pena', 'no lo recomiendo',
            'no lo volveré a comprar', 'estafa total', 'decepcion total',
            'no merece', 'muy mala calidad', 'no sirve para nada',
            'no funciona bien', 'producto defectuoso', 'experiencia terrible',
            'muy mala experiencia', 'malísima calidad', 'pésima calidad',
            'mal servicio', 'engañado con el producto', 'publicidad engañosa',
            'se descompuso rápido', 'no cumple lo prometido', 'nada recomendable',
            'no es lo que esperaba', 'no vale lo que cuesta', 'me arrepiento de comprarlo',
            'muy decepcionado', 'es una estafa', 'malísimo producto'
        }

        self.bigrams_positive = {
            'muy bueno', 'muy bien', 'excelente servicio', 'muy util', 'muy útil',
            'super recomendado', 'superó expectativas', 'muy satisfecho',
            'altamente recomendado', 'muy contento', 'muy buena calidad',
            'gran producto', 'muy funcional', 'perfecto estado', 'excelente atención'
        }
        
        self.bigrams_negative = {
            'muy malo', 'muy mal', 'no funciona', 'no sirve', 'pésimo servicio',
            'nunca mas', 'nunca más', 'no lo recomiendo', 'muy decepcionado',
            'pésima calidad', 'muy mala calidad', 'mala experiencia',
            'muy defectuoso', 'no cumple', 'no recomendable', 'pésimo producto',
            'no vale', 'muy lento', 'se traba', 'se descompone'
        }

        # Aspectos (clave -> palabras claves)
        self.aspectos = {
            'calidad': ['calidad', 'material', 'acabado', 'duradero', 'duradera', 'resistente'],
            'precio': ['precio', 'caro', 'barato', 'coste', 'costo', 'economico', 'económico'],
            'servicio': ['servicio', 'atención', 'atencion', 'entrega', 'envio', 'envío', 'soporte', 'devolución', 'devolucion'],
            'funcionalidad': ['funciona', 'funcionar', 'uso', 'usar', 'util', 'útil', 'práctico']
        }

        # Pesos y umbrales
        self.PESO_FRASE = 2.5
        self.PESO_BIGRAM = 1.5
        self.PESO_PALABRA_MUY = 2.0
        self.PESO_PALABRA = 1.0
        self.PESO_NEG_MUY = -2.2
        self.PESO_NEG = -1.0

    # ---------- Normalización ----------
    def limpiar_texto(self, texto: str) -> str:
        if not texto:
            return ''
        texto = re.sub(r'http\S+|www\.\S+', '', texto)
        texto = reemplazar_acentos(texto)
        texto = texto.lower()
        texto = normalizar_repeticiones(texto)
        texto = quitar_espacios_extra(texto)
        return texto

    # ---------- Negación ----------
    def ventana_negacion(self, tokens: List[str], indice: int, ventana: int = 3) -> bool:
        inicio = max(0, indice - ventana)
        segmento = tokens[inicio:indice]
        neg_count = sum(1 for t in segmento if t in self.negaciones)
        if self.debug:
            logging.debug(f"Ventana negación tokens[{inicio}:{indice}]={segmento} -> neg_count={neg_count}")
        return (neg_count % 2) == 1

    # ---------- Modificadores ----------
    def calcular_modificador(self, tokens: List[str], indice: int) -> float:
        factor = 1.0
        inicio = max(0, indice - 2)
        for t in tokens[inicio:indice]:
            if t in self.intensificadores:
                factor *= 1.5
            elif t in self.atenuadores:
                factor *= 0.7
        factor = max(0.4, min(factor, 3.0))
        if self.debug:
            logging.debug(f"Modificador tokens[{inicio}:{indice}] -> factor={factor}")
        return factor

    # ---------- Sarcasmo ----------
    def detectar_sarcasmo_simple(self, texto_original: str) -> bool:
        # Emojis típicos de sarcasmo / ironía
        sarcasm_emojis = {'🙄', '😒', '😑', '😜', '😏'}
        if any(e in texto_original for e in sarcasm_emojis):
            return True
        # Positivo seguido de ellipsis o varios signos
        if re.search(r'\b(excelente|genial|perfecto|bueno|buenísimo|buenisimo)\b\s*[.!]{2,}', texto_original, flags=re.I):
            return True
        # Positivo + "pero" cerca
        if re.search(r'\b(excelente|genial|perfecto|bueno)\b.{0,12}\bpero\b', texto_original, flags=re.I):
            return True
        # Interjecciones largas tipo "JAJAJA" en contexto de positivo (puede ser risa por sarcasmo)
        if re.search(r'\b(jaja{1,}|jajaja+)\b', texto_original, flags=re.I) and re.search(r'\b(qué|esta|esto|ese)\b', texto_original, flags=re.I):
            return True
        return False

    # ---------- Análisis principal ----------
    def analizar_sentimiento(self, texto: str) -> Dict[str, Any]:
        if not texto or not isinstance(texto, str) or texto.strip() == '':
            return {
                'sentimiento': 'Neutro',
                'emoji': '😐',
                'score': 0.0,
                'confianza': 0.0,
                'positivos': 0.0,
                'negativos': 0.0,
                'aspectos': {},
                'tokens_analizados': 0,
                'sarcasmo': False
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

        # Frases contextuales
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

        # Bigrams
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

        # Palabras individuales con contexto
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
                    peso_base = self.PESO_PALABRA_MUY if palabra in self.p_positivas_fuertes else self.PESO_PALABRA
                    if invertir:
                        peso = -peso_base * mod
                        cuenta_neg += abs(peso)
                        score += peso
                        if self.debug:
                            logging.debug(f"Palabra positiva '{palabra}' invertida por negación -> {peso}")
                    else:
                        peso = peso_base * mod
                        cuenta_pos += abs(peso)
                        score += peso
                        if self.debug:
                            logging.debug(f"Palabra positiva '{palabra}' -> +{peso}")
                else:
                    peso_base = self.PESO_NEG_MUY if palabra in self.p_negativas_fuertes else self.PESO_NEG
                    if invertir:
                        # invertir efecto de palabra negativa
                        peso = -peso_base * mod  # peso_base es negativo -> -peso_base es positivo
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

        # Emojis y signos
        emojis_positivos = re.findall(r'[😊😃😄😁🤗❤️💖👍⭐🌟✨🎉😍🥰😘]', texto_orig)
        emojis_negativos = re.findall(r'[😞😢😭😔😩😫💔😠😡🤬😤]', texto_orig)
        score += len(emojis_positivos) * 1.0
        score -= len(emojis_negativos) * 1.0
        if self.debug and (emojis_positivos or emojis_negativos):
            logging.debug(f"Emojis +{len(emojis_positivos)} -{len(emojis_negativos)}")

        exclam_count = len(re.findall(r'!+', texto_orig))
        if exclam_count > 0 and score != 0:
            multiplier = (1 + min(exclam_count * 0.08, 0.4))
            score *= multiplier
            if self.debug:
                logging.debug(f"Exclamaciones: {exclam_count}, multiplicador {multiplier}, score ahora {score}")

        # Aspectos encontrados (usando límites por palabra para reducir falsos positivos)
        aspectos_encontrados = {}
        for aspecto, claves in self.aspectos.items():
            for k in claves:
                # buscar palabra con límites \b para no coger substrings irrelevantes
                if re.search(r'\b' + re.escape(k) + r'\b', texto):
                    aspectos_encontrados.setdefault(aspecto, 0)
                    aspectos_encontrados[aspecto] += 1

        # Sarcasmo
        sarcasmo = self.detectar_sarcasmo_simple(texto_orig)
        if sarcasmo and score > 1.5:
            score = -abs(score) * 0.6
            if self.debug:
                logging.debug("Sarcasmo detectado: ajuste de score")

        # Limitar score y escalar -10..10 -> -5..5
        score = max(-10.0, min(10.0, score))
        score_scaled = (score / 10.0) * 5.0

        # Confianza
        suma_cuentas = cuenta_pos + cuenta_neg
        if suma_cuentas > 0:
            diff = abs(cuenta_pos - cuenta_neg)
            confianza = (diff / suma_cuentas) * 100.0
            # ajustar por palabras analizadas (máx +20)
            confianza += min(max((palabras_analizadas - 1) * 5.0, 0.0), 20.0)
            # frases fuertes aumentan confianza un poco
            if any(f in texto for f in (self.frases_positivas | self.frases_negativas)):
                confianza = min(confianza + 8.0, 100.0)
        else:
            confianza = 35.0

        if sarcasmo:
            confianza = max(15.0, confianza - 25.0)

        confianza = max(0.0, min(100.0, confianza))

        # Clasificación final
        umbral_fuerte = 1.2
        umbral_debil = 0.4

        if abs(score_scaled) < umbral_debil:
            sentimiento = 'Neutro'
            emoji = '😐'
        elif score_scaled >= umbral_fuerte:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_scaled <= -umbral_fuerte:
            sentimiento = 'Negativo'
            emoji = '😞'
        else:
            # caso intermedio entre umbral_debil y umbral_fuerte
            sentimiento = 'Positivo' if score_scaled > 0 else 'Negativo'
            emoji = '😊' if score_scaled > 0 else '😞'

        # Afinar: palabras neutras
        palabras_neutras = {'normal','regular','ok','aceptable','promedio','cumple','justo','usual'}
        if any(re.search(r'\b' + re.escape(p) + r'\b', texto) for p in palabras_neutras) and abs(score_scaled) < 1.0:
            sentimiento = 'Neutro'
            emoji = '😐'
            confianza = max(confianza, 50.0)

        resultado = {
            'sentimiento': sentimiento,
            'emoji': emoji,
            'score': round(score_scaled, 2),
            'confianza': round(confianza, 1),
            'positivos': round(cuenta_pos, 2),
            'negativos': round(cuenta_neg, 2),
            'aspectos': aspectos_encontrados,
            'tokens_analizados': int(palabras_analizadas),
            'sarcasmo': sarcasmo
        }

        if self.debug:
            logging.debug(f"Resultado raw score: {score}, scaled: {score_scaled}, cuenta_pos: {cuenta_pos}, cuenta_neg: {cuenta_neg}")
            logging.debug(f"Resultado final: {resultado}")

        return resultado

# ---------- Funciones auxiliares ----------
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
        "0/10, jamás volvería a usar esto.",
        "Genial... pero falla cada vez.",
        "Sí, claro 🙄 funciona perfecto (modo sarcasmo)."
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

