import re
import logging

class AnalizadorSentimientos:
    """
    Clase mejorada para analizar sentimientos en español con mejor precisión
    """
    def __init__(self, debug=False):
        self.debug = debug
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Palabras positivas expandidas
        self.palabras_positivas = {
            'excelente', 'bueno', 'buena', 'buenos', 'buenas', 'genial', 'increíble', 
            'perfecto', 'perfecta', 'recomendado', 'recomendada', 'encanta', 'encantó', 
            'mejor', 'mejores', 'feliz', 'contento', 'contenta', 'maravilloso', 'maravillosa',
            'fantástico', 'fantástica', 'súper', 'super', 'amor', 'amo', 'love',
            'calidad', 'rápido', 'rápida', 'eficiente', 'profesional', 'amable',
            'superó', 'expectativas', 'satisfecho', 'satisfecha', 'vale', 'pena',
            'estrellas', 'recomiendo', 'felicitaciones', 'gracias', 'éxito', 'exitoso',
            'hermoso', 'hermosa', 'bonito', 'bonita', 'agradable', 'divertido',
            'útil', 'práctico', 'práctica', 'barato', 'barata', 'económico',
            'fácil', 'sencillo', 'sencilla', 'claro', 'clara', 'preciso', 'exacto',
            'correcto', 'adecuado', 'apropiado', 'conveniente', 'ideal',
            'óptimo', 'destacado', 'sobresaliente', 'notable', 'brillante',
            'impresionante', 'asombroso', 'sorprendente', 'inmejorable',
            'inigualable', 'extraordinario', 'magnífico', 'espléndido',
            'estupendo', 'fenomenal', 'provechoso', 'beneficioso', 'ventajoso',
            'encantador', 'precioso', 'divino', 'exquisito', 'espectacular',
            # Palabras coloquiales mexicanas/latinoamericanas
            'chido', 'chida', 'padre', 'padrísimo', 'chingón', 'chingona',
            'chévere', 'piola', 'joya', 'bacán', 'capo', 'crack'
        }
        
        self.palabras_negativas = {
            'malo', 'mala', 'malos', 'malas', 'pésimo', 'pésima', 'horrible', 
            'terrible', 'defectuoso', 'defectuosa', 'roto', 'rota', 'nunca', 
            'jamás', 'peor', 'peores', 'lento', 'lenta', 'caro', 'cara',
            'estafa', 'fraude', 'decepción', 'decepcionante', 'problema', 
            'problemas', 'falla', 'fallas', 'defecto', 'defectos', 'insatisfecho',
            'insatisfecha', 'desagradable', 'diferente', 'desilusión', 'engaño', 
            'rompió', 'desperfecto', 'averiado', 'dañado', 'estropeado', 'inútil',
            'inservible', 'inadecuado', 'inapropiado', 'incorrecto',
            'erróneo', 'equivocado', 'deficiente', 'imperfecto', 'desastroso', 
            'catastrófico', 'desalentador', 'frustrante', 'molesto', 'irritante', 
            'fastidioso', 'engorroso', 'complicado', 'difícil', 'complejo', 
            'confuso', 'ambiguo', 'incierto', 'dudoso', 'sospechoso', 'deshonesto', 
            'fraudulento', 'estafador', 'mediocre', 'pobre', 'basura', 'asco',
            'horrendo', 'repugnante', 'deplorable', 'lamentable',
            # Palabras coloquiales mexicanas/latinoamericanas
            'gacho', 'gacha', 'culero', 'pirata', 'chafa', 'corriente', 'feo'
        }
        
        self.palabras_neutras = {
            'normal', 'regular', 'común', 'estándar', 'básico', 'cumple',
            'función', 'aceptable', 'ok', 'bien', 'nada', 'especial',
            'promedio', 'justo', 'usual', 'habitual', 'corriente', 
            'ordinario', 'convencional', 'simple', 'típico'
        }
        
        self.palabras_muy_positivas = {
            'excelente', 'increíble', 'maravilloso', 'fantástico', 'perfecto',
            'encanta', 'amor', 'amo', 'espectacular', 'genial', 'súper',
            'sobresaliente', 'brillante', 'impresionante', 'asombroso',
            'extraordinario', 'magnífico', 'espléndido', 'fenomenal',
            'padrísimo', 'chingón', 'chingona'
        }
        
        self.palabras_muy_negativas = {
            'pésimo', 'pésima', 'horrible', 'terrible', 'estafa', 'fraude', 
            'desastre', 'engaño', 'desilusión', 'catastrófico', 'desastroso', 
            'basura', 'asco', 'repugnante', 'deplorable', 'horrendo'
        }
        
        self.negaciones = {
            'no', 'nunca', 'jamás', 'tampoco', 'sin', 'ni', 'nada'
        }
        
        self.intensificadores = {
            'muy', 'mucho', 'mucha', 'bastante', 'totalmente', 'completamente',
            'absolutamente', 'realmente', 'extremadamente', 'increíblemente',
            'sumamente', 'demasiado', 'tan', 'bien', 'súper', 'mega', 'ultra'
        }
        
        self.atenuadores = {
            'poco', 'ligeramente', 'algo', 'medianamente', 'relativamente',
            'apenas', 'casi', 'medio', 'más', 'menos'
        }
        
        # Frases completas con contexto
        self.frases_negativas = {
            'se rompió', 'mala calidad', 'no sirve', 'no funciona', 'no me gustó',
            'no lo recomiendo', 'no vale la pena', 'no cumple', 'no es lo que esperaba',
            'pérdida de tiempo', 'no volveré', 'no lo compren', 'nunca más',
            'jamás lo recomendaría', 'decepción total', 'no lo vuelvo a comprar',
            'no vale', 'no merece', 'no lo compraría', 'estafa total',
            'puro cuento', 'pura mentira'
        }
        
        self.frases_positivas = {
            'lo recomiendo', 'vale la pena', 'superó expectativas', 'cumple con lo prometido',
            'excelente calidad', 'muy buen', 'muy buena', 'totalmente recomendado',
            'volveré a comprar', 'excelente servicio', 'muy contento', 'muy feliz',
            'completamente satisfecho', 'mejor compra', 'vale cada peso', 'lo amo',
            'a toda madre', 'de lujo', 'primera calidad'
        }
        
        # Aspectos para análisis detallado
        self.aspectos = {
            'calidad': ['calidad', 'material', 'construcción', 'acabado', 'duradero'],
            'precio': ['precio', 'caro', 'barato', 'costo', 'económico', 'vale'],
            'servicio': ['servicio', 'atención', 'entrega', 'envío', 'soporte'],
            'funcionalidad': ['funciona', 'sirve', 'uso', 'útil', 'práctico']
        }

    def normalizar_texto(self, texto):
        """Normaliza variaciones comunes en el texto"""
        # Normalizar repeticiones excesivas de puntuación
        texto = re.sub(r'([!?.]){3,}', r'\1\1', texto)
        
        # Normalizar letras repetidas (pero mantener algunas válidas)
        # "bueeeno" → "bueno", pero no afectar "llevar"
        texto = re.sub(r'(.)\1{3,}', r'\1\1', texto)
        
        return texto

    def limpiar_texto(self, texto):
        """Limpia el texto manteniendo caracteres importantes"""
        texto = self.normalizar_texto(texto)
        # Convertir a minúsculas para uniformidad
        texto = texto.lower()
        # Remover URLs
        texto = re.sub(r'http\S+|www\S+', '', texto)
        # Normalizar espacios
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def detectar_negacion_mejorada(self, texto, posicion_palabra):
        """
        Detecta negaciones de forma más precisa considerando el contexto
        Mejora: maneja doble negación ("no es malo" = positivo)
        """
        palabras = texto.split()
        
        if posicion_palabra >= len(palabras):
            return False
        
        palabra_actual = palabras[posicion_palabra]
        
        # Buscar negaciones en las 3 palabras anteriores
        inicio = max(0, posicion_palabra - 3)
        segmento_previo = palabras[inicio:posicion_palabra]
        
        # Contar negaciones
        negaciones_encontradas = sum(1 for p in segmento_previo if p in self.negaciones)
        
        # Doble negación: "no es malo" debería ser positivo
        if negaciones_encontradas > 0:
            # Si la palabra actual es negativa y hay negación, se vuelve positiva
            if palabra_actual in self.palabras_negativas:
                return True  # Invertir
            # Si la palabra es positiva y hay negación, se vuelve negativa
            elif palabra_actual in self.palabras_positivas:
                return True  # Invertir
        
        # Si hay número impar de negaciones, se invierte el sentimiento
        return negaciones_encontradas % 2 == 1

    def calcular_intensidad_mejorada(self, texto, posicion_palabra):
        """
        Calcula la intensidad considerando modificadores cercanos
        """
        palabras = texto.split()
        intensidad = 1.0
        
        # Buscar modificadores en las 2 palabras anteriores
        inicio = max(0, posicion_palabra - 2)
        segmento_previo = palabras[inicio:posicion_palabra]
        
        for palabra in segmento_previo:
            if palabra in self.intensificadores:
                intensidad *= 1.5
            elif palabra in self.atenuadores:
                intensidad *= 0.6
        
        return min(intensidad, 3.0)  # Limitar intensidad máxima

    def detectar_sarcasmo(self, texto):
        """
        Detecta posible sarcasmo básico
        """
        # Sarcasmo común: palabras positivas con muchos signos de puntuación
        if re.search(r'(excelente|genial|perfecto|bueno)[.!]{3,}', texto):
            return True
        
        # "Qué bueno..." o "Muy bien..." con puntos suspensivos (tono sarcástico)
        if re.search(r'(bueno|bien|genial)\.\.\.$', texto):
            return True
        
        # "Excelente" seguido de "no"
        if re.search(r'(excelente|genial|perfecto).{0,10}(no|pero)', texto):
            return True
        
        return False

    def analizar_frases_contextuales(self, texto):
        """
        Analiza frases completas que tienen un sentimiento claro
        """
        score = 0
        
        # Buscar frases positivas
        for frase in self.frases_positivas:
            if frase in texto:
                score += 2.5
                if self.debug:
                    logging.debug(f"Frase positiva encontrada: {frase}")
        
        # Buscar frases negativas
        for frase in self.frases_negativas:
            if frase in texto:
                score -= 2.5
                if self.debug:
                    logging.debug(f"Frase negativa encontrada: {frase}")
        
        return score

    def analizar_patrones_regex(self, texto):
        """
        Detecta patrones mediante expresiones regulares
        """
        score = 0
        
        # Patrones muy positivos
        if re.search(r'\b(lo re?comiendo|recomendad[oa] totalmente)\b', texto):
            score += 2
        if re.search(r'\b(vale la pena|excelente calidad)\b', texto):
            score += 2
        if re.search(r'\b(super[oó] (mis|las) expectativas)\b', texto):
            score += 2
        if re.search(r'\b(volver[ée] a comprar)\b', texto):
            score += 1.5
        
        # Patrones muy negativos
        if re.search(r'\b(no lo re?comiendo|no recomendado)\b', texto):
            score -= 2.5
        if re.search(r'\b(no vale la pena)\b', texto):
            score -= 2
        if re.search(r'\b(no (sirve|funciona|me gust[oó]))\b', texto):
            score -= 2
        if re.search(r'\b(nunca m[aá]s|jam[aá]s|p[ée]rdida de tiempo)\b', texto):
            score -= 2.5
        if re.search(r'\b(estafa|fraude|enga[ñn]o)\b', texto):
            score -= 3
        
        if self.debug and score != 0:
            logging.debug(f"Score de patrones regex: {score}")
        
        return score

    def analizar_emojis_y_puntuacion(self, texto):
        """
        Analiza emojis y signos de puntuación
        """
        score = 0
        
        # Emojis positivos
        emojis_positivos = len(re.findall(r'[😊😃😄😁🤗❤️💖👍⭐🌟✨🎉😍🥰😘]', texto))
        score += emojis_positivos * 1.0
        
        # Emojis negativos
        emojis_negativos = len(re.findall(r'[😞😢😭😔😩😫💔😠😡🤬😤]', texto))
        score -= emojis_negativos * 1.0
        
        # Exclamaciones (amplifican el sentimiento)
        exclamaciones = len(re.findall(r'!+', texto))
        
        if self.debug and (emojis_positivos > 0 or emojis_negativos > 0):
            logging.debug(f"Emojis positivos: {emojis_positivos}, negativos: {emojis_negativos}")
        
        return score, exclamaciones

    def analizar_aspectos(self, texto):
        """
        Identifica qué aspectos se están evaluando
        """
        aspectos_encontrados = {}
        
        for aspecto, palabras_clave in self.aspectos.items():
            if any(palabra in texto for palabra in palabras_clave):
                aspectos_encontrados[aspecto] = True
        
        return aspectos_encontrados

    def analizar_sentimiento(self, texto):
        """
        Análisis principal de sentimiento con mejor precisión
        """
        if not texto or texto.strip() == "":
            return {
                'sentimiento': 'Neutro',
                'emoji': '😐',
                'score': 0,
                'confianza': 0,
                'palabras_positivas': 0,
                'palabras_negativas': 0,
                'aspectos': {}
            }
        
        texto_original = texto
        texto = self.limpiar_texto(texto)
        palabras = texto.split()
        
        if self.debug:
            logging.debug(f"Analizando: {texto}")
        
        # Detectar sarcasmo
        tiene_sarcasmo = self.detectar_sarcasmo(texto)
        if tiene_sarcasmo and self.debug:
            logging.debug("Posible sarcasmo detectado")
        
        # Inicializar contadores
        score_positivo = 0
        score_negativo = 0
        palabras_analizadas = 0
        
        # 1. Analizar frases contextuales (mayor peso)
        score_frases = self.analizar_frases_contextuales(texto)
        if score_frases > 0:
            score_positivo += score_frases
            palabras_analizadas += 1
        elif score_frases < 0:
            score_negativo += abs(score_frases)
            palabras_analizadas += 1
        
        # 2. Analizar patrones con regex
        score_patrones = self.analizar_patrones_regex(texto)
        if score_patrones > 0:
            score_positivo += score_patrones
            palabras_analizadas += 1
        elif score_patrones < 0:
            score_negativo += abs(score_patrones)
            palabras_analizadas += 1
        
        # 3. Analizar palabras individuales con contexto
        for i, palabra in enumerate(palabras):
            # Determinar si la palabra es significativa
            es_positiva = palabra in self.palabras_positivas
            es_negativa = palabra in self.palabras_negativas
            es_muy_positiva = palabra in self.palabras_muy_positivas
            es_muy_negativa = palabra in self.palabras_muy_negativas
            
            if es_positiva or es_negativa or es_muy_positiva or es_muy_negativa:
                palabras_analizadas += 1
                
                # Calcular peso base
                if es_muy_positiva:
                    peso_base = 2.0
                elif es_positiva:
                    peso_base = 1.0
                elif es_muy_negativa:
                    peso_base = -2.0
                else:
                    peso_base = -1.0
                
                # Detectar negación mejorada
                tiene_negacion = self.detectar_negacion_mejorada(texto, i)
                
                # Calcular intensidad
                intensidad = self.calcular_intensidad_mejorada(texto, i)
                
                # Aplicar modificadores
                if tiene_negacion:
                    peso_base = -peso_base
                
                peso_final = peso_base * intensidad
                
                if self.debug:
                    logging.debug(f"Palabra: {palabra}, peso_base: {peso_base}, intensidad: {intensidad}, negación: {tiene_negacion}, peso_final: {peso_final}")
                
                # Acumular en el score correspondiente
                if peso_final > 0:
                    score_positivo += peso_final
                else:
                    score_negativo += abs(peso_final)
        
        # 4. Analizar emojis y puntuación
        score_emoji, exclamaciones = self.analizar_emojis_y_puntuacion(texto_original)
        if score_emoji > 0:
            score_positivo += score_emoji
        elif score_emoji < 0:
            score_negativo += abs(score_emoji)
        
        # Las exclamaciones amplifican el sentimiento dominante
        if exclamaciones > 0 and palabras_analizadas > 0:
            factor_exclamacion = min(1 + (exclamaciones * 0.1), 1.5)
            if score_positivo > score_negativo:
                score_positivo *= factor_exclamacion
            elif score_negativo > score_positivo:
                score_negativo *= factor_exclamacion
        
        # 5. Detectar palabras neutras explícitas
        tiene_neutras = any(palabra in self.palabras_neutras for palabra in palabras)
        
        # 6. Analizar aspectos
        aspectos = self.analizar_aspectos(texto)
        
        # Calcular score final
        score_final = score_positivo - score_negativo
        
        # Ajustar por sarcasmo (invertir si es muy positivo con sarcasmo)
        if tiene_sarcasmo and score_final > 2:
            score_final = -abs(score_final) * 0.7
            if self.debug:
                logging.debug("Score ajustado por sarcasmo")
        
        # Calcular confianza
        total_palabras_significativas = palabras_analizadas
        if total_palabras_significativas > 0:
            diferencia = abs(score_positivo - score_negativo)
            total_score = score_positivo + score_negativo
            
            if total_score > 0:
                confianza = (diferencia / total_score) * 100
            else:
                confianza = 50
            
            # Ajustar confianza según el número de palabras analizadas
            if total_palabras_significativas >= 3:
                confianza = min(confianza + 10, 95)
            elif total_palabras_significativas == 1:
                confianza = max(confianza - 10, 40)
        else:
            confianza = 30
        
        if self.debug:
            logging.debug(f"Score positivo: {score_positivo}, Score negativo: {score_negativo}, Score final: {score_final}")
        
        # Clasificación final con umbrales adaptativos
        umbral_fuerte = 2.0
        umbral_debil = 0.5
        
        if tiene_neutras and abs(score_final) < 1.5:
            sentimiento = 'Neutro'
            emoji = '😐'
            confianza = max(confianza, 60)
        elif score_final > umbral_fuerte:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_final > umbral_debil:
            sentimiento = 'Positivo'
            emoji = '😊'
            confianza = max(confianza - 10, 50)
        elif score_final < -umbral_fuerte:
            sentimiento = 'Negativo'
            emoji = '😞'
        elif score_final < -umbral_debil:
            sentimiento = 'Negativo'
            emoji = '😞'
            confianza = max(confianza - 10, 50)
        else:
            sentimiento = 'Neutro'
            emoji = '😐'
        
        # Limitar confianza
        confianza = max(30, min(95, confianza))
        
        return {
            'sentimiento': sentimiento,
            'emoji': emoji,
            'score': round(score_final, 2),
            'confianza': round(confianza, 2),
            'palabras_positivas': round(score_positivo, 2),
            'palabras_negativas': round(score_negativo, 2),
            'aspectos': aspectos
        }


def procesar_comentarios_completos(comentarios, debug=False):
    """
    Procesa una lista completa de comentarios
    """
    analizador = AnalizadorSentimientos(debug=debug)
    resultados = []
    
    for i, comentario in enumerate(comentarios, 1):
        analisis = analizador.analizar_sentimiento(comentario)
        
        resultados.append({
            'id': i,
            'comentario': comentario,
            'sentimiento': analisis['sentimiento'],
            'emoji': analisis['emoji'],
            'confianza': analisis['confianza'],
            'score': analisis['score'],
            'aspectos': analisis['aspectos']
        })
    
    return resultados


def generar_reporte(resultados):
    """
    Genera un reporte estadístico de los sentimientos
    """
    total = len(resultados)
    if total == 0:
        return {
            'total': 0,
            'positivos': 0,
            'negativos': 0,
            'neutros': 0,
            'porcentaje_positivos': 0,
            'porcentaje_negativos': 0,
            'porcentaje_neutros': 0
        }
    
    positivos = sum(1 for r in resultados if r['sentimiento'] == 'Positivo')
    negativos = sum(1 for r in resultados if r['sentimiento'] == 'Negativo')
    neutros = sum(1 for r in resultados if r['sentimiento'] == 'Neutro')
    
    reporte = {
        'total': total,
        'positivos': positivos,
        'negativos': negativos,
        'neutros': neutros,
        'porcentaje_positivos': round((positivos / total * 100), 2),
        'porcentaje_negativos': round((negativos / total * 100), 2),
        'porcentaje_neutros': round((neutros / total * 100), 2)
    }
    
    return reporte


def obtener_top_comentarios(resultados, tipo='positivos', cantidad=5):
    """
    Obtiene los comentarios más positivos o negativos
    """
    if tipo == 'positivos':
        positivos = [r for r in resultados if r['sentimiento'] == 'Positivo']
        positivos_ordenados = sorted(positivos, key=lambda x: x['score'], reverse=True)
        return positivos_ordenados[:cantidad]
    else:
        negativos = [r for r in resultados if r['sentimiento'] == 'Negativo']
        negativos_ordenados = sorted(negativos, key=lambda x: x['score'])
        return negativos_ordenados[:cantidad]


def generar_datos_grafico(reporte):
    """
    Genera datos para el gráfico de pastel
    """
    labels = ['Positivos', 'Negativos', 'Neutros']
    values = [
        reporte['porcentaje_positivos'], 
        reporte['porcentaje_negativos'], 
        reporte['porcentaje_neutros']
    ]
    colors = ['#38ef7d', '#f45c43', '#bdc3c7']
    
    return {
        'labels': labels,
        'values': values,
        'colors': colors
    }


# Ejemplo de uso
if __name__ == "__main__":
    # Pruebas básicas
    analizador = AnalizadorSentimientos(debug=True)
    
    pruebas = [
        "Este producto es excelente, lo recomiendo totalmente 😊",
        "No me gustó para nada, es una estafa",
        "Está bien, nada especial",
        "No es malo, cumple su función",
        "Muy bueno!! Superó mis expectativas",
        "Pésimo servicio, nunca más vuelvo",
        "Es chido, vale la pena"
    ]
    
    print("=" * 60)
    print("PRUEBAS DEL ANALIZADOR DE SENTIMIENTOS MEJORADO")
    print("=" * 60)
    
    for texto in pruebas:
        resultado = analizador.analizar_sentimiento(texto)
        print(f"\nTexto: {texto}")
        print(f"Sentimiento: {resultado['sentimiento']} {resultado['emoji']}")
        print(f"Score: {resultado['score']}")
        print(f"Confianza: {resultado['confianza']}%")
        print(f"Aspectos: {list(resultado['aspectos'].keys())}")
        print("-" * 60)