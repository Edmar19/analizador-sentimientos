from textblob import TextBlob
import re

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
            'recomiendo', 'felicitaciones', 'gracias', 'exito', 'hermoso'
        }
        
        self.palabras_negativas = {
            'malo', 'mala', 'pésimo', 'pésima', 'horrible', 'terrible',
            'defectuoso', 'roto', 'nunca', 'jamás', 'peor', 'lento',
            'caro', 'estafa', 'fraude', 'decepción', 'decepcionante',
            'problema', 'problemas', 'falla', 'defecto', 'insatisfecho'
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
    
    def detectar_negacion(self, texto, posicion_palabra):
        """
        Detecta si hay una negación cerca de una palabra
        """
        palabras = texto.lower().split()
        if posicion_palabra > 0:
            palabra_anterior = palabras[posicion_palabra - 1]
            if palabra_anterior in self.negaciones:
                return True
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
        
        # Palabras muy positivas valen más
        for palabra in self.palabras_muy_positivas:
            if palabra in texto_lower:
                # Verificar si está negada (ej: "no es excelente")
                if palabra in ' '.join(palabras):
                    idx = palabras.index(palabra) if palabra in palabras else -1
                    if idx > 0 and self.detectar_negacion(texto, idx):
                        score_negativo += 2  # Invierte a negativo
                    else:
                        score_positivo += 2
        
        # Palabras positivas normales
        for palabra in self.palabras_positivas:
            if palabra in texto_lower:
                score_positivo += 1
        
        # Palabras muy negativas
        for palabra in self.palabras_muy_negativas:
            if palabra in texto_lower:
                score_negativo += 2
        
        # Palabras negativas normales
        for palabra in self.palabras_negativas:
            if palabra in texto_lower:
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
        
        # Calcular confianza
        total_palabras = score_positivo + score_negativo
        if total_palabras > 0:
            confianza = (max(score_positivo, score_negativo) / total_palabras) * 100
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

def mostrar_resultados(resultados, reporte):
    """
    Muestra los resultados en consola de forma visual
    """
    print("\n" + "="*70)
    print("ANÁLISIS DE SENTIMIENTOS - RESULTADOS")
    print("="*70 + "\n")
    
    for resultado in resultados:
        print(f"[{resultado['id']}] {resultado['emoji']} {resultado['sentimiento']} "
              f"(Score: {resultado['score']}, Confianza: {resultado['confianza']}%)")
        print(f"    📝 {resultado['comentario']}")
        print()
    
    print("="*70)
    print("RESUMEN ESTADÍSTICO")
    print("="*70)
    print(f"Total de comentarios: {reporte['total']}")
    print(f"\n😊 Positivos: {reporte['positivos']} ({reporte['porcentaje_positivos']}%)")
    print(f"😞 Negativos: {reporte['negativos']} ({reporte['porcentaje_negativos']}%)")
    print(f"😐 Neutros: {reporte['neutros']} ({reporte['porcentaje_neutros']}%)")
    print("="*70 + "\n")
    
    # Mostrar sentimiento general
    if reporte['porcentaje_positivos'] > reporte['porcentaje_negativos'] + 10:
        print("📊 SENTIMIENTO GENERAL: Los clientes están SATISFECHOS 👍")
        print("💡 Recomendación: Mantén la calidad de tu servicio/producto")
    elif reporte['porcentaje_negativos'] > reporte['porcentaje_positivos'] + 10:
        print("📊 SENTIMIENTO GENERAL: Los clientes están INSATISFECHOS 👎")
        print("⚠️  Recomendación: Revisa urgentemente las áreas problemáticas")
    else:
        print("📊 SENTIMIENTO GENERAL: Opiniones MIXTAS 🤔")
        print("💡 Recomendación: Identifica puntos de mejora específicos")
    print()

# Código para probar el analizador
if __name__ == "__main__":
    from procesador import leer_comentarios
    
    # Leer comentarios del archivo
    comentarios = leer_comentarios('datos/comentarios.txt')
    
    if comentarios:
        print("🚀 Iniciando análisis de sentimientos en ESPAÑOL (versión mejorada)...\n")
        
        # Procesar todos los comentarios
        resultados = procesar_comentarios_completos(comentarios)
        
        # Generar reporte estadístico
        reporte = generar_reporte(resultados)
        
        # Mostrar resultados
        mostrar_resultados(resultados, reporte)
        
        # Mostrar top comentarios por categoría
        print("\n" + "="*70)
        print("TOP COMENTARIOS POR CATEGORÍA")
        print("="*70)
        
        # Más positivo
        mas_positivo = max(resultados, key=lambda x: x['score'] if x['sentimiento'] == 'Positivo' else -999)
        if mas_positivo['sentimiento'] == 'Positivo':
            print(f"\n😊 MÁS POSITIVO (Score: {mas_positivo['score']}):")
            print(f"   {mas_positivo['comentario']}")
        
        # Más negativo
        mas_negativo = min(resultados, key=lambda x: x['score'] if x['sentimiento'] == 'Negativo' else 999)
        if mas_negativo['sentimiento'] == 'Negativo':
            print(f"\n😞 MÁS NEGATIVO (Score: {mas_negativo['score']}):")
            print(f"   {mas_negativo['comentario']}")
        
        print("\n" + "="*70 + "\n")
    else:
        print("❌ No se pudieron leer los comentarios")