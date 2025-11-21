import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os

class AnalizadorSentimientos:
    def __init__(self):
        self.palabras_positivas = {
            'excelente', 'bueno', 'buena', 'genial', 'increible', 
            'perfecto', 'recomendado', 'encanta', 'encanto', 
            'mejor', 'feliz', 'contento', 'maravilloso', 'fantastico',
            'super', 'amor', 'amo', 'calidad', 'rapido', 'eficiente',
            'profesional', 'amable', 'supero', 'satisfecho', 'vale',
            'recomiendo', 'gracias', 'exito', 'hermoso', 'bonito',
            'agradable', 'divertido', 'util', 'practico', 'barato',
            'economico', 'facil', 'sencillo', 'claro'
        }
        
        self.palabras_negativas = {
            'malo', 'mala', 'pesimo', 'pesima', 'horrible', 
            'terrible', 'defectuoso', 'roto', 'nunca', 
            'jamas', 'peor', 'lento', 'caro', 'estafa', 'fraude',
            'decepcion', 'decepcionante', 'problema', 'falla',
            'defecto', 'insatisfecho', 'desagradable', 'diferente',
            'desilusion', 'engano', 'rompio', 'inutil', 'complicado',
            'dificil', 'complejo', 'confuso'
        }
        
        self.frases_negativas = {
            'se rompio', 'mala calidad', 'no sirve', 'no funciona', 
            'no me gusto', 'no lo recomiendo', 'no vale la pena', 
            'no cumple', 'no es lo que esperaba'
        }
        
        self.frases_positivas = {
            'lo recomiendo', 'vale la pena', 'supero expectativas', 
            'cumple con lo prometido', 'excelente calidad', 
            'muy buen', 'muy buena', 'totalmente recomendado'
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
            return self.resultado_neutro()
        
        texto_limpio = self.limpiar_texto(texto)
        
        score_positivo = 0
        score_negativo = 0
        
        # Analizar frases completas
        for frase in self.frases_positivas:
            if frase in texto_limpio:
                score_positivo += 2
        
        for frase in self.frases_negativas:
            if frase in texto_limpio:
                score_negativo += 2
        
        # Analizar palabras individuales
        palabras = texto_limpio.split()
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
        
        # Calcular confianza
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
    
    def resultado_neutro(self):
        return {
            'sentimiento': 'Neutro',
            'emoji': '😐',
            'score': 0,
            'confianza': 0,
            'palabras_positivas': 0,
            'palabras_negativas': 0
        }


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