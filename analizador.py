from textblob import TextBlob
import re
import matplotlib.pyplot as plt
import io
import base64

class AnalizadorSentimientos:
    """
    Clase para analizar sentimientos en español
    """
    def __init__(self):
        # Palabras clave en español
        self.palabras_positivas = {
            'excelente', 'bueno', 'buena', 'genial', 'increíble', 'perfecto', 
            'recomendado', 'encanta', 'encantó', 'mejor', 'feliz', 'contento',
            'maravilloso', 'fantástico', 'súper', 'amor', 'amo', 'love',
            'calidad', 'rápido', 'eficiente', 'profesional', 'amable',
            'superó', 'expectativas', 'satisfecho', 'vale', 'pena', 'estrellas',
            'recomiendo', 'felicitaciones', 'gracias', 'exito', 'hermoso',
            'agradable', 'satisfactorio', 'impresionante', 'brillante', 'notable',
            'destacado', 'eficaz', 'útil', 'práctico', 'cómodo', 'barato', 'económico'
        }
        
        self.palabras_negativas = {
            'malo', 'mala', 'pésimo', 'pésima', 'horrible', 'terrible',
            'defectuoso', 'roto', 'nunca', 'jamás', 'peor', 'lento',
            'caro', 'estafa', 'fraude', 'decepción', 'decepcionante',
            'problema', 'problemas', 'falla', 'defecto', 'insatisfecho',
            'deficiente', 'pobre', 'insuficiente', 'lamentable', 'desilusionado',
            'frustrado', 'molesto', 'enojado', 'costoso', 'complicado', 'difícil'
        }
        
        # Palabras que indican neutralidad (no suman ni restan)
        self.palabras_neutras = {
            'normal', 'regular', 'común', 'estándar', 'básico', 'cumple',
            'función', 'aceptable', 'ok', 'está bien', 'nada especial',
            'promedio', 'ni bien ni mal', 'justo', 'adecuado'
        }
        
        self.palabras_muy_positivas = {
            'excelente', 'increíble', 'maravilloso', 'fantástico', 'perfecto',
            'encanta', 'amor', 'amo', 'espectacular', 'genial'
        }
        
        self.palabras_muy_negativas = {
            'pésimo', 'pésima', 'horrible', 'terrible', 'nunca más', 'estafa',
            'fraude', 'desastre'
        }
        
        # Negaciones que invierten el sentimiento
        self.negaciones = {'no', 'nunca', 'jamás', 'tampoco', 'sin'}
    
    def detectar_negacion(self, texto, palabra_objetivo):
        """
        Detecta si hay una negación cerca de una palabra específica
        """
        palabras = texto.lower().split()
        try:
            idx = palabras.index(palabra_objetivo)
            # Verificar las 2 palabras anteriores para negaciones
            for i in range(max(0, idx-2), idx):
                if palabras[i] in self.negaciones:
                    return True
        except ValueError:
            return False
        return False
    
    def analizar_sentimiento(self, texto):
        """
        Analiza el sentimiento de un texto en español
        """
        texto_lower = texto.lower()
        palabras = texto_lower.split()
        
        # Contar palabras positivas y negativas
        score_positivo = 0
        score_negativo = 0
        tiene_palabras_neutras = False
        
        # Verificar si tiene palabras explícitamente neutras
        for palabra_neutra in self.palabras_neutras:
            if palabra_neutra in texto_lower:
                tiene_palabras_neutras = True
        
        # Analizar cada palabra individualmente para mejor precisión
        for palabra in palabras:
            palabra_limpia = re.sub(r'[^\w]', '', palabra)  # Limpiar puntuación
            
            if palabra_limpia in self.palabras_neutras:
                tiene_palabras_neutras = True
                
            elif palabra_limpia in self.palabras_muy_positivas:
                if self.detectar_negacion(texto_lower, palabra_limpia):
                    score_negativo += 2  # Invierte a negativo
                else:
                    score_positivo += 2
                    
            elif palabra_limpia in self.palabras_positivas:
                if self.detectar_negacion(texto_lower, palabra_limpia):
                    score_negativo += 1
                else:
                    score_positivo += 1
                    
            elif palabra_limpia in self.palabras_muy_negativas:
                score_negativo += 2
                
            elif palabra_limpia in self.palabras_negativas:
                score_negativo += 1
        
        # Detectar signos de exclamación múltiples (intensifican el sentimiento)
        exclamaciones = len(re.findall(r'!+', texto))
        if exclamaciones > 0:
            if score_positivo > score_negativo:
                score_positivo += exclamaciones * 0.5
            elif score_negativo > score_positivo:
                score_negativo += exclamaciones * 0.5
        
        # Detectar emojis tristes
        if ':(' in texto or '😞' in texto or '😢' in texto or '😭' in texto:
            score_negativo += 1
        
        # Detectar emojis felices
        if ':)' in texto or '😊' in texto or '😃' in texto or '😄' in texto or '❤' in texto:
            score_positivo += 1
        
        # Calcular score final
        score_final = score_positivo - score_negativo
        
        # Calcular confianza (fórmula mejorada)
        total_palabras_relevantes = score_positivo + score_negativo
        if total_palabras_relevantes > 0:
            diferencia = abs(score_positivo - score_negativo)
            confianza = (diferencia / total_palabras_relevantes) * 100
        else:
            confianza = 0
        
        # Clasificar sentimiento
        # Si tiene palabras neutras explícitas y el score es bajo, clasificar como neutro
        if tiene_palabras_neutras and abs(score_final) <= 1:
            sentimiento = 'Neutro'
            emoji = '😐'
        elif score_final > 0:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_final < 0:
            sentimiento = 'Negativo'
            emoji = '😞'
        else:
            sentimiento = 'Neutro'
            emoji = '😐'
        
        return {
            'sentimiento': sentimiento,
            'emoji': emoji,
            'score': score_final,
            'confianza': round(confianza, 2),
            'palabras_positivas': score_positivo,
            'palabras_negativas': score_negativo
        }

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

def generar_grafico_pastel(reporte):
    """
    Genera un gráfico de pastel con los porcentajes de sentimientos
    Retorna la imagen en base64 para mostrar en HTML
    """
    # Datos para el gráfico
    labels = ['Positivos', 'Negativos', 'Neutros']
    sizes = [
        reporte['porcentaje_positivos'],
        reporte['porcentaje_negativos'], 
        reporte['porcentaje_neutros']
    ]
    colors = ['#38ef7d', '#f45c43', '#bdc3c7']
    explode = (0.05, 0.05, 0.05)  # Separar ligeramente las porciones
    
    # Crear gráfico
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, 
            autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Distribución de Sentimientos', fontsize=16, fontweight='bold')
    
    # Convertir a base64 para HTML
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{graph_url}"

def generar_grafico_barras(reporte):
    """
    Genera un gráfico de barras con los conteos de sentimientos
    """
    labels = ['Positivos', 'Negativos', 'Neutros']
    counts = [
        reporte['positivos'],
        reporte['negativos'], 
        reporte['neutros']
    ]
    colors = ['#38ef7d', '#f45c43', '#bdc3c7']
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, counts, color=colors, alpha=0.8)
    
    # Agregar valores en las barras
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{count}', ha='center', va='bottom', fontweight='bold')
    
    plt.title('Cantidad de Comentarios por Sentimiento', fontsize=16, fontweight='bold')
    plt.ylabel('Cantidad de Comentarios')
    plt.grid(axis='y', alpha=0.3)
    
    # Convertir a base64
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{graph_url}"

def generar_datos_grafico(reporte):
    """
    Genera datos para el gráfico de pastel (función legacy)
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

# Función para probar el analizador
if __name__ == "__main__":
    # Pruebas básicas
    analizador = AnalizadorSentimientos()
    
    comentarios_prueba = [
        "Excelente producto, me encantó la calidad",
        "Pésimo servicio, nunca más vuelvo",
        "Está bien, cumple su función",
        "No me gustó para nada, muy decepcionante",
        "Increíble atención, superó mis expectativas"
    ]
    
    print("🔍 Probando analizador de sentimientos...")
    for comentario in comentarios_prueba:
        resultado = analizador.analizar_sentimiento(comentario)
        print(f"\n📝 Comentario: {comentario}")
        print(f"🎯 Sentimiento: {resultado['sentimiento']} {resultado['emoji']}")
        print(f"📊 Score: {resultado['score']} | Confianza: {resultado['confianza']}%")