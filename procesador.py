import re

def leer_comentarios(archivo):
    """
    Lee comentarios desde un archivo .txt
    Retorna una lista de comentarios
    """
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            comentarios = file.readlines()
        # Remover saltos de línea y espacios extras
        comentarios = [comentario.strip() for comentario in comentarios if comentario.strip()]
        return comentarios
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo}")
        return []

def limpiar_texto(texto):
    """
    Limpia el texto eliminando caracteres especiales,
    números y convierte a minúsculas
    """
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Eliminar URLs
    texto = re.sub(r'http\S+|www\S+', '', texto)
    
    # Eliminar menciones (@usuario)
    texto = re.sub(r'@\w+', '', texto)
    
    # Eliminar hashtags (#tema)
    texto = re.sub(r'#\w+', '', texto)
    
    # Eliminar números
    texto = re.sub(r'\d+', '', texto)
    
    # Eliminar signos de puntuación múltiples (!!!, ???)
    texto = re.sub(r'[!?]{2,}', ' ', texto)
    
    # Eliminar caracteres especiales, mantener solo letras, espacios y puntuación básica
    texto = re.sub(r'[^a-záéíóúñü\s.,;:()]', '', texto)
    
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # Eliminar espacios al inicio y final
    texto = texto.strip()
    
    return texto

def estructurar_datos(comentarios):
    """
    Estructura los comentarios en una lista de diccionarios
    con el texto original y el texto limpio
    """
    datos_estructurados = []
    
    for i, comentario in enumerate(comentarios, 1):
        datos_estructurados.append({
            'id': i,
            'texto_original': comentario,
            'texto_limpio': limpiar_texto(comentario),
            'longitud': len(comentario),
            'palabras': len(comentario.split())
        })
    
    return datos_estructurados

def mostrar_estadisticas(datos):
    """
    Muestra estadísticas básicas de los comentarios
    """
    total = len(datos)
    promedio_palabras = sum(d['palabras'] for d in datos) / total if total > 0 else 0
    
    print(f"\n{'='*50}")
    print(f"ESTADÍSTICAS DE COMENTARIOS")
    print(f"{'='*50}")
    print(f"Total de comentarios: {total}")
    print(f"Promedio de palabras por comentario: {promedio_palabras:.2f}")
    print(f"\nPrimeros 3 comentarios procesados:")
    print(f"{'-'*50}")
    
    for dato in datos[:3]:
        print(f"\nID: {dato['id']}")
        print(f"Original: {dato['texto_original']}")
        print(f"Limpio: {dato['texto_limpio']}")
        print(f"Palabras: {dato['palabras']}")

# Código para probar las funciones
if __name__ == "__main__":
    # Leer comentarios
    comentarios = leer_comentarios('datos/comentarios.txt')
    
    if comentarios:
        print(f"✅ Se leyeron {len(comentarios)} comentarios correctamente\n")
        
        # Estructurar datos
        datos = estructurar_datos(comentarios)
        
        # Mostrar estadísticas
        mostrar_estadisticas(datos)
    else:
        print("❌ No se pudieron leer los comentarios")