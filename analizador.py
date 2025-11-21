# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

class AnalizadorSentimientos:
    def __init__(self):
        self.palabras_positivas = ['excelente', 'bueno', 'buena', 'genial', 'perfecto', 'recomendado', 'feliz', 'contento', 'maravilloso', 'fantastico', 'amor', 'calidad', 'rapido', 'eficiente', 'profesional', 'amable']
        self.palabras_negativas = ['malo', 'mala', 'pesimo', 'horrible', 'terrible', 'defectuoso', 'roto', 'nunca', 'peor', 'lento', 'caro', 'estafa', 'problema', 'falla', 'defecto', 'insatisfecho']

    def analizar_sentimiento(self, texto):
        if not texto or texto.strip() == "":
            return self.resultado_neutro()
        
        texto = texto.lower()
        score_positivo = 0
        score_negativo = 0
        
        for palabra in self.palabras_positivas:
            if palabra in texto:
                score_positivo += 1
        
        for palabra in self.palabras_negativas:
            if palabra in texto:
                score_negativo += 1
        
        score_final = score_positivo - score_negativo
        
        if score_final > 0:
            sentimiento = 'Positivo'
            emoji = '😊'
        elif score_final < 0:
            sentimiento = 'Negativo'
            emoji = '😞'
        else:
            sentimiento = 'Neutro'
            emoji = '😐'
        
        total = score_positivo + score_negativo
        if total > 0:
            confianza = (max(score_positivo, score_negativo) / total) * 100
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
    total = len(resultados)
    positivos = 0
    negativos = 0
    neutros = 0
    
    for resultado in resultados:
        if resultado['sentimiento'] == 'Positivo':
            positivos += 1
        elif resultado['sentimiento'] == 'Negativo':
            negativos += 1
        else:
            neutros += 1
    
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

def generar_grafica_base64(reporte):
    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = ['Positivos', 'Negativos', 'Neutros']
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
        
        ax.set_title('Distribucion de Sentimientos', fontweight='bold')
        
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