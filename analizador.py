import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os

class AnalizadorSentimientos:
    def __init__(self):
        # Palabras positivas
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
            'fácil', 'sencillo', 'sencilla', 'claro', 'clara', 'preciso', 'exacto'
        }
        
        # Palabras negativas
        self.palabras_negativas = {
            'malo', 'mala', 'malos', 'malas', 'pésimo', 'pésima', 'horrible', 
            'terrible', 'defectuoso', 'defectuosa', 'roto', 'rota', 'nunca', 
            'jamás', 'peor', 'peores', 'lento', 'lenta', 'caro', 'cara',
            'estafa', 'fraude', 'decepción', 'decepcionante', 'problema', 
            'problemas', 'falla', 'fallas', 'defecto', 'defectos', 'insatisfecho',
            'insatisfecha', 'desagradable', 'diferente', 'desilusión', 'engaño', 
            'rompió', 'desperfecto', 'averiado', 'dañado', 'estropeado', 'inútil'
        }
        
        # Palabras neutras
        self.palabras_neutras = {
            'normal', 'regular', 'común', 'estándar', 'básico', 'cumple',
            'función', 'aceptable', 'ok', 'bien', 'nada', 'especial',
            'promedio', 'justo', 'usual', 'habitual'
        }
        
        # Negaciones
        self.negaciones = {'no', 'nunca', 'jamás', 'tampoco', 'sin', 'ni', 'nada'}
        
        # Frases completas
        self.frases_negativas = {
            'se rompió', 'mala calidad', 'no sirve', 'no funciona', 'no me gustó',
            'no lo recomiendo', 'no vale la pena', 'no cumple'
        }
        
        self.frases_positivas = {
            'lo recomiendo', 'vale la pena', 'superó expectativas', 'cumple con lo prometido',
            'excelente calidad', 'muy buen', 'muy buena', 'totalmente recomendado'
        }

    def limpiar_texto(self, texto):
        if not texto:
            return ""
        texto = texto.lower()
        texto = re.sub(r'http\S+|www\S+', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def analizar_sentimiento(self, texto):
        if not texto or texto.strip() == "":
            return self._resultado_neutro()
        
        texto_limpio = self.limpiar_texto(texto)
        palabras = texto_limpio.split()
        
        score_positivo = 0
        score_negativo = 0
        
        # Analizar frases completas primero
        for frase in self.frases_positivas:
            if frase in texto_limpio:
                score_positivo += 2
        
        for frase in self.frases_negativas:
            if frase in texto_limpio:
                score_negativo += 2
        
        # Analizar palabras individuales
        for palabra in palabras:
            if palabra in self.palabras_positivas:
                score_positivo += 1
            elif palabra in self.palabras_negativas:
                score_negativo += 1
        
        # Analizar emojis
        emojis_positivos = len(re.findall(r'[😊😃😄😁🤗❤️💖👍⭐🌟✨🎉]', texto))
        emojis_negativos = len(re.findall(r'[😞😢😭😔😩😫💔😠😡]', texto))
        
        score_positivo += emojis_positivos
        score_negativo += emojis_negativos
        
        # Calcular score final
        score_final = score_positivo - score_negativo
        
        # Determinar sentimiento
        if score_final > 0:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_final < 0:
            sentimiento = 'Negativo'
            emoji = '😞'
        else:
            sentimiento = 'Neutro'
            emoji = '😐'
        
        # Calcular confianza básica
        total_puntos = score_positivo + score_negativo
        if total_puntos > 0:
            confianza = (max(score_positivo, score_negativo) / total_puntos) * 100
        else:
            confianza = 50
        
        return {
            'sentimiento': sentimiento,
            'emoji': emoji,
            'score': score_final,
            'confianza': round(confianza, 2),
            'palabras_positivas': score_positivo,
            'palabras_negativas': score_negativo
        }
    
    def _resultado_neutro(self):
        return {
            'sentimiento': 'Neutro',
            'emoji': '😐',
            'score': 0,
            'confianza': 0,
            'palabras_positivas': 0,
            'palabras_negativas': 0
        }


# FUNCIÓN CORREGIDA - nombre correcto
def procesar_comentarios_completos(comentarios):
    analizador = AnalizadorSentimientos()
    resultados = []
    
    for i, comentario in enumerate(comentarios, 1):
        try:
            analisis = analizador.analizar_sentimiento(comentario)
            resultados.append({
                'id': i,
                'comentario': comentario,
                'sentimiento': analisis['sentimiento'],
                'emoji': analisis['emoji'],
                'confianza': analisis['confianza'],
                'score': analisis['score']
            })
        except Exception as e:
            resultados.append({
                'id': i,
                'comentario': comentario,
                'sentimiento': 'Error',
                'emoji': '❌',
                'confianza': 0,
                'score': 0
            })
    
    return resultados


def generar_reporte(resultados):
    try:
        total = len(resultados)
        positivos = sum(1 for r in resultados if r['sentimiento'] == 'Positivo')
        negativos = sum(1 for r in resultados if r['sentimiento'] == 'Negativo')
        neutros = sum(1 for r in resultados if r['sentimiento'] == 'Neutro')
        
        porcentaje_positivos = round((positivos / total * 100), 2) if total > 0 else 0
        porcentaje_negativos = round((negativos / total * 100), 2) if total > 0 else 0
        porcentaje_neutros = round((neutros / total * 100), 2) if total > 0 else 0
        
        return {
            'total': total,
            'positivos': positivos,
            'negativos': negativos,
            'neutros': neutros,
            'porcentaje_positivos': porcentaje_positivos,
            'porcentaje_negativos': porcentaje_negativos,
            'porcentaje_neutros': porcentaje_neutros
        }
    except Exception:
        return {
            'total': 0,
            'positivos': 0,
            'negativos': 0,
            'neutros': 0,
            'porcentaje_positivos': 0,
            'porcentaje_negativos': 0,
            'porcentaje_neutros': 0
        }


def generar_grafica_base64(reporte):
    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['Positivos 😊', 'Negativos 😞', 'Neutros 😐']
        sizes = [
            reporte['porcentaje_positivos'],
            reporte['porcentaje_negativos'], 
            reporte['porcentaje_neutros']
        ]
        colors = ['#38ef7d', '#f45c43', '#bdc3c7']
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Distribución de Sentimientos', fontweight='bold')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{graphic}"
        
    except Exception:
        return None