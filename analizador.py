from textblob import TextBlob
import re

class AnalizadorSentimientos:
    """
    Clase mejorada para analizar sentimientos en español
    """
    def __init__(self):
        # Palabras clave en español - EXPANDIDAS Y MEJOR ORGANIZADAS
        self.palabras_positivas = {
            'excelente', 'bueno', 'buena', 'genial', 'increíble', 'perfecto', 
            'recomendado', 'encanta', 'encantó', 'mejor', 'feliz', 'contento',
            'maravilloso', 'fantástico', 'súper', 'amor', 'amo', 'love',
            'calidad', 'rápido', 'eficiente', 'profesional', 'amable',
            'superó', 'expectativas', 'satisfecho', 'vale', 'pena', 'estrellas',
            'recomiendo', 'felicitaciones', 'gracias', 'exito', 'hermoso',
            'bonito', 'agradable', 'divertido', 'útil', 'práctico', 'barato',
            'económico', 'fácil', 'sencillo', 'claro', 'preciso', 'exacto',
            'correcto', 'adecuado', 'apropiado', 'conveniente', 'ideal',
            'optimo', 'destacado', 'sobresaliente', 'notable', 'brillante',
            'impresionante', 'asombroso', 'sorprendente', 'inmejorable',
            'inigualable', 'extraordinario', 'magnífico', 'espléndido',
            'estupendo', 'fenomenal', 'provechoso', 'beneficioso', 'ventajoso'
        }
        
        self.palabras_negativas = {
            'malo', 'mala', 'pésimo', 'pésima', 'horrible', 'terrible',
            'defectuoso', 'roto', 'nunca', 'jamás', 'peor', 'lento',
            'caro', 'estafa', 'fraude', 'decepción', 'decepcionante',
            'problema', 'problemas', 'falla', 'defecto', 'insatisfecho',
            'gustó', 'diferente', 'desilusion', 'engaño', 'rompió',
            'desperfecto', 'averiado', 'dañado', 'estropeado', 'inútil',
            'inservible', 'inadecuado', 'inapropiado', 'incorrecto',
            'erróneo', 'equivocado', 'deficiente', 'imperfecto', 'defectuoso',
            'desastroso', 'catastrófico', 'desalentador', 'frustrante',
            'molesto', 'irritante', 'fastidioso', 'engorroso', 'complicado',
            'difícil', 'complejo', 'confuso', 'ambiguo', 'incierto',
            'dudoso', 'sospechoso', 'deshonesto', 'fraudulento', 'estafador'
        }
        
        # Palabras que indican neutralidad (no suman ni restan)
        self.palabras_neutras = {
            'normal', 'regular', 'común', 'estándar', 'básico', 'cumple',
            'función', 'aceptable', 'ok', 'está bien', 'nada especial',
            'promedio', 'ni bien ni mal', 'justo', 'adecuado', 'usual',
            'habitual', 'corriente', 'ordinario', 'convencional'
        }
        
        self.palabras_muy_positivas = {
            'excelente', 'increíble', 'maravilloso', 'fantástico', 'perfecto',
            'encanta', 'amor', 'amo', 'espectacular', 'genial', 'increible',
            'sobresaliente', 'brillante', 'impresionante', 'asombroso'
        }
        
        self.palabras_muy_negativas = {
            'pésimo', 'pésima', 'horrible', 'terrible', 'nunca más', 'estafa',
            'fraude', 'desastre', 'engaño', 'desilusión', 'catastrófico',
            'desastroso', 'abusivo', 'estafador'
        }
        
        # Negaciones que invierten el sentimiento
        self.negaciones = {'no', 'nunca', 'jamás', 'tampoco', 'sin', 'ni'}
        
        # Intensificadores que aumentan el sentimiento
        self.intensificadores = {
            'muy', 'mucho', 'bastante', 'totalmente', 'completamente',
            'absolutamente', 'realmente', 'extremadamente', 'increíblemente'
        }
        
        # Atenuadores que disminuyen el sentimiento
        self.atenuadores = {
            'poco', 'ligeramente', 'algo', 'medianamente', 'relativamente'
        }
        
        # Frases negativas completas
        self.frases_negativas = {
            'se rompió', 'mala calidad', 'no sirve', 'no funciona', 'no me gustó',
            'no lo recomiendo', 'no vale la pena', 'no cumple', 'no es lo que esperaba',
            'perdida de tiempo', 'no volveré', 'no lo compren'
        }
        
        # Frases positivas completas
        self.frases_positivas = {
            'lo recomiendo', 'vale la pena', 'superó expectativas', 'cumple con lo prometido',
            'excelente calidad', 'muy buen', 'muy buena', 'totalmente recomendado',
            'volveré a comprar', 'excelente servicio'
        }

    def limpiar_texto(self, texto):
        """
        Limpia el texto removiendo caracteres especiales innecesarios
        pero manteniendo signos de puntuación importantes
        """
        # Remover caracteres especiales pero mantener signos básicos
        texto_limpio = re.sub(r'[^\w\s¡!¿?.,]', '', texto)
        # Normalizar espacios
        texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
        return texto_limpio

    def detectar_negacion(self, texto, palabra_objetivo):
        """
        Detecta negaciones mejor - busca 'no' antes de la palabra con contexto
        """
        palabras = texto.lower().split()
        try:
            idx = palabras.index(palabra_objetivo)
            # Revisar hasta 4 palabras antes
            for i in range(max(0, idx-4), idx):
                if palabras[i] in self.negaciones:
                    # Verificar que no haya un intensificador entre la negación y la palabra
                    tiene_intensificador = any(
                        pal in self.intensificadores 
                        for pal in palabras[i+1:idx]
                    )
                    if not tiene_intensificador:
                        return True
        except ValueError:
            pass
        return False

    def en_contexto_negativo(self, texto, palabra):
        """
        Detecta si una palabra está en contexto negativo con mejor precisión
        """
        palabras = texto.lower().split()
        try:
            idx = palabras.index(palabra)
            # Palabras que indican contexto negativo antes
            indicadores_negativos = {
                'roto', 'rompió', 'mal', 'mala', 'malo', 'defectuoso', 'pésim',
                'horrible', 'terrible', 'decepción', 'problema', 'falla'
            }
            
            # Revisar 3 palabras antes y después
            inicio = max(0, idx-3)
            fin = min(len(palabras), idx+4)
            
            for i in range(inicio, fin):
                if i != idx and palabras[i] in indicadores_negativos:
                    return True
                    
        except ValueError:
            pass
        return False

    def calcular_intensidad(self, texto, palabra):
        """
        Calcula la intensidad de una palabra basado en intensificadores/atenuadores
        """
        palabras = texto.lower().split()
        try:
            idx = palabras.index(palabra)
            # Buscar intensificadores antes de la palabra
            for i in range(max(0, idx-3), idx):
                if palabras[i] in self.intensificadores:
                    return 1.5  # Aumenta intensidad
                elif palabras[i] in self.atenuadores:
                    return 0.5  # Disminuye intensidad
        except ValueError:
            pass
        return 1.0  # Intensidad normal

    def analizar_patrones_especiales(self, texto):
        """
        Analiza patrones especiales que indican sentimiento claro
        """
        texto_lower = texto.lower()
        score = 0
        
        # Patrones muy positivos
        patrones_positivos = [
            r'\b(lo recomiendo|recomendado totalmente)\b',
            r'\b(vale la pena|excelente calidad)\b',
            r'\b(superó (mis|las) expectativas)\b',
            r'\b(volver[ée] a comprar)\b',
            r'\b((muy|totalmente) satisfecho)\b'
        ]
        
        # Patrones muy negativos
        patrones_negativos = [
            r'\b(no lo recomiendo|no recomendado)\b',
            r'\b(no vale la pena)\b',
            r'\b(no (sirve|funciona))\b',
            r'\b(nunca m[aá]s|jam[aá]s)\b',
            r'\b(perdida de tiempo)\b',
            r'\b(estafa|fraude|engaño)\b'
        ]
        
        for patron in patrones_positivos:
            if re.search(patron, texto_lower):
                score += 2
                
        for patron in patrones_negativos:
            if re.search(patron, texto_lower):
                score -= 2
                
        return score

    def analizar_sentimiento_textblob(self, texto):
        """
        Usa TextBlob como respaldo para comparación
        """
        try:
            analysis = TextBlob(texto)
            # TextBlob devuelve polaridad entre -1 y 1
            return analysis.sentiment.polarity
        except:
            return 0

    def analizar_sentimiento(self, texto):
        """
        Analiza el sentimiento de un texto en español con mejor precisión
        """
        if not texto or texto.strip() == "":
            return {
                'sentimiento': 'Neutro',
                'emoji': '😐',
                'score': 0,
                'confianza': 0,
                'palabras_positivas': 0,
                'palabras_negativas': 0
            }
        
        texto_limpio = self.limpiar_texto(texto)
        texto_lower = texto_limpio.lower()
        palabras = texto_lower.split()
        
        # Contadores mejorados
        score_positivo = 0
        score_negativo = 0
        tiene_palabras_neutras = False
        
        # Análisis de patrones especiales primero (tienen mayor peso)
        score_patrones = self.analizar_patrones_especiales(texto_limpio)
        if score_patrones > 0:
            score_positivo += score_patrones
        elif score_patrones < 0:
            score_negativo += abs(score_patrones)

        # Verificar frases completas
        for frase in self.frases_positivas:
            if frase in texto_lower:
                score_positivo += 2
                
        for frase in self.frases_negativas:
            if frase in texto_lower:
                score_negativo += 2

        # Verificar si tiene palabras explícitamente neutras
        for palabra_neutra in self.palabras_neutras:
            if palabra_neutra in texto_lower:
                tiene_palabras_neutras = True

        # Análisis de palabras individuales con intensidad
        todas_palabras_relevantes = (self.palabras_muy_positivas | self.palabras_positivas | 
                                   self.palabras_muy_negativas | self.palabras_negativas)
        
        for palabra in todas_palabras_relevantes:
            if palabra in palabras:
                intensidad = self.calcular_intensidad(texto_lower, palabra)
                negado = self.detectar_negacion(texto_lower, palabra)
                contexto_negativo = self.en_contexto_negativo(texto_lower, palabra)
                
                # Determinar puntuación base
                if palabra in self.palabras_muy_positivas:
                    base_score = 2
                elif palabra in self.palabras_positivas:
                    base_score = 1
                elif palabra in self.palabras_muy_negativas:
                    base_score = -2
                else:  # palabras negativas normales
                    base_score = -1
                
                # Aplicar modificadores
                if negado:
                    base_score = -base_score  # Invertir sentimiento
                elif contexto_negativo and base_score > 0:
                    base_score = -abs(base_score)  # Convertir a negativo
                
                # Aplicar intensidad
                score_final_palabra = base_score * intensidad
                
                if score_final_palabra > 0:
                    score_positivo += score_final_palabra
                else:
                    score_negativo += abs(score_final_palabra)

        # Análisis de signos de puntuación y emojis mejorado
        exclamaciones = len(re.findall(r'!+', texto))
        interrogaciones = len(re.findall(r'\?+', texto))
        
        if exclamaciones > 0:
            # Las exclamaciones intensifican el sentimiento predominante
            if score_positivo > score_negativo:
                score_positivo += min(exclamaciones * 0.3, 2)  # Límite máximo
            elif score_negativo > score_positivo:
                score_negativo += min(exclamaciones * 0.3, 2)

        # Emojis con pesos específicos
        emojis_tristes = re.findall(r'[😞😢😭😔😩😫💔]', texto)
        emojis_felices = re.findall(r'[😊😃😄😁🤗❤️💖👍⭐🌟✨🎉]', texto)
        
        score_negativo += len(emojis_tristes) * 0.8
        score_positivo += len(emojis_felices) * 0.8

        # Usar TextBlob como respaldo para casos dudosos
        score_textblob = self.analizar_sentimiento_textblob(texto_limpio)
        
        # Calcular score final con ponderación
        score_final = (score_positivo - score_negativo)
        
        # Si TextBlob tiene una opinión fuerte y estamos en caso dudoso, considerar su input
        if abs(score_final) <= 1 and abs(score_textblob) > 0.3:
            score_final += score_textblob * 2

        # Calcular confianza mejorada
        total_palabras_significativas = score_positivo + score_negativo
        if total_palabras_significativas > 0:
            confianza = (max(score_positivo, score_negativo) / total_palabras_significativas) * 100
            # Aumentar confianza si hay patrones especiales o muchos emojis
            if score_patrones != 0 or (len(emojis_tristes) + len(emojis_felices)) > 0:
                confianza = min(confianza + 10, 95)
        else:
            confianza = 0

        # Clasificación mejorada con umbrales adaptativos
        umbral_positivo = 1.0
        umbral_negativo = -1.0
        
        # Ajustar umbrales basado en la longitud del texto
        if len(palabras) <= 3:  # Textos muy cortos
            umbral_positivo = 0.5
            umbral_negativo = -0.5

        if tiene_palabras_neutras and abs(score_final) <= 1.5:
            sentimiento = 'Neutro'
            emoji = '😐'
            # Ajustar confianza para neutros
            confianza = max(confianza, 60) if total_palabras_significativas > 0 else 50
        elif score_final > umbral_positivo:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_final < umbral_negativo:
            sentimiento = 'Negativo'
            emoji = '😞'
        else:
            sentimiento = 'Neutro'
            emoji = '😐'

        # Limitar confianza entre 0 y 100
        confianza = max(0, min(100, confianza))

        return {
            'sentimiento': sentimiento,
            'emoji': emoji,
            'score': round(score_final, 2),
            'confianza': round(confianza, 2),
            'palabras_positivas': round(score_positivo, 2),
            'palabras_negativas': round(score_negativo, 2)
        }

# Las funciones de procesamiento y reporte se mantienen igual
def procesar_comentarios_completos(comentarios):
    """
    Procesa una lista completa de comentarios
    """
    analizador = AnalizadorSentimientos()
    resultados = []
    
    for i, comentario in enumerate(comentarios, 1):
        analisis = analizador.analizar_sentimiento(comentario)
        
        resultados.append({
            'id': i,
            'comentario': comentario,
            'sentimiento': analisis['sentimiento'],
            'emoji': analisis['emoji'],
            'confianza': analisis['confianza'],
            'score': analisis['score']
        })
    
    return resultados

def generar_reporte(resultados):
    """
    Genera un reporte estadístico de los sentimientos
    """
    total = len(resultados)
    positivos = sum(1 for r in resultados if r['sentimiento'] == 'Positivo')
    negativos = sum(1 for r in resultados if r['sentimiento'] == 'Negativo')
    neutros = sum(1 for r in resultados if r['sentimiento'] == 'Neutro')
    
    reporte = {
        'total': total,
        'positivos': positivos,
        'negativos': negativos,
        'neutros': neutros,
        'porcentaje_positivos': round((positivos / total * 100), 2) if total > 0 else 0,
        'porcentaje_negativos': round((negativos / total * 100), 2) if total > 0 else 0,
        'porcentaje_neutros': round((neutros / total * 100), 2) if total > 0 else 0
    }
    
    return reporte

def obtener_top_comentarios(resultados, tipo='positivos', cantidad=5):
    """
    Obtiene los comentarios más positivos o negativos
    """
    if tipo == 'positivos':
        # Filtrar solo positivos y ordenar por score descendente
        positivos = [r for r in resultados if r['sentimiento'] == 'Positivo']
        positivos_ordenados = sorted(positivos, key=lambda x: x['score'], reverse=True)
        return positivos_ordenados[:cantidad]
    else:
        # Filtrar solo negativos y ordenar por score ascendente
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