from flask import Flask, render_template, request, redirect, url_for
import os
import csv
from analizador import (
    procesar_comentarios_completos, 
    generar_reporte, 
    generar_grafico_pastel, 
    generar_grafico_barras, 
    obtener_top_comentarios
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear carpeta uploads si no existe
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    """Procesa los comentarios y muestra resultados"""
    tipo = request.form.get('tipo')
    comentarios = []
    
    if tipo == 'archivo':
        # Procesar archivo subido
        if 'file' not in request.files:
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(url_for('index'))
        
        # Aceptar tanto .txt como .csv
        if file and (file.filename.endswith('.txt') or file.filename.endswith('.csv')):
            if file.filename.endswith('.csv'):
                # PROCESAR CSV CORRECTAMENTE
                try:
                    # Decodificar el contenido
                    contenido = file.read().decode('utf-8').splitlines()
                    reader = csv.reader(contenido)
                    
                    for fila in reader:
                        if fila:  # Si la fila no está vacía
                            # Buscar la primera columna con texto
                            for celda in fila:
                                if celda.strip():  # Si la celda tiene texto
                                    comentarios.append(celda.strip())
                                    break
                except Exception as e:
                    print(f"Error procesando CSV: {e}")
                    # Fallback: procesar como texto plano
                    file.seek(0)  # Volver al inicio del archivo
                    contenido = file.read().decode('utf-8')
                    lineas = contenido.split('\n')
                    for linea in lineas:
                        if linea.strip():
                            comentarios.append(linea.strip())
            else:
                # Procesar TXT normal
                contenido = file.read().decode('utf-8')
                comentarios = [linea.strip() for linea in contenido.split('\n') if linea.strip()]
    
    elif tipo == 'texto':
        # Procesar texto pegado
        texto = request.form.get('comentarios', '')
        comentarios = [linea.strip() for linea in texto.split('\n') if linea.strip()]
    
    if not comentarios:
        return redirect(url_for('index'))
    
    # Analizar comentarios
    resultados = procesar_comentarios_completos(comentarios)
    reporte = generar_reporte(resultados)
    
    # Generar gráficos y top comentarios
    grafico_pastel = generar_grafico_pastel(reporte)
    grafico_barras = generar_grafico_barras(reporte)
    top_positivos = obtener_top_comentarios(resultados, tipo='positivos', cantidad=5)
    top_negativos = obtener_top_comentarios(resultados, tipo='negativos', cantidad=5)
    
    return render_template('resultados.html', 
                         resultados=resultados, 
                         reporte=reporte,
                         grafico_pastel=grafico_pastel,
                         grafico_barras=grafico_barras,
                         top_positivos=top_positivos,
                         top_negativos=top_negativos)

@app.route('/acerca')
def acerca():
    """Página acerca del proyecto"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Acerca del Analizador de Sentimientos</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🤖 Acerca del Analizador de Sentimientos</h1>
                <p>Una herramienta inteligente para entender a tus clientes</p>
            </header>

            <div class="card">
                <h3>🎯 ¿Qué hace esta aplicación?</h3>
                <p>Esta aplicación analiza automáticamente los comentarios de tus clientes y determina si son positivos, negativos o neutros usando procesamiento de lenguaje natural.</p>
                
                <h3>📊 Características principales:</h3>
                <ul>
                    <li>✅ Análisis de sentimientos en español</li>
                    <li>📁 Soporte para archivos .txt y .csv</li>
                    <li>✍️ Análisis de texto directo</li>
                    <li>📈 Gráficos interactivos</li>
                    <li>🏆 Identificación de comentarios más relevantes</li>
                    <li>🎯 Recomendaciones automáticas</li>
                </ul>

                <h3>🔧 Tecnologías utilizadas:</h3>
                <ul>
                    <li>Python Flask - Backend web</li>
                    <li>TextBlob - Procesamiento de lenguaje natural</li>
                    <li>Matplotlib - Generación de gráficos</li>
                    <li>HTML/CSS/JavaScript - Interfaz de usuario</li>
                </ul>

                <h3>📈 ¿Para quién es útil?</h3>
                <ul>
                    <li>📱 Empresas que quieren entender la satisfacción de clientes</li>
                    <li>🎯 Emprendedores que analizan feedback de productos</li>
                    <li>📊 Investigadores que estudian opiniones en redes sociales</li>
                    <li>💼 Consultores que generan reportes de satisfacción</li>
                </ul>
            </div>

            <div class="card">
                <a href="/" style="text-decoration: none;">
                    <button class="btn">🔙 Volver al Analizador</button>
                </a>
            </div>
        </div>
    </body>
    </html>
    """

# Manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return """
    <div class="container">
        <div class="card">
            <h1>❌ Página no encontrada</h1>
            <p>La página que buscas no existe.</p>
            <a href="/" class="btn">🏠 Volver al inicio</a>
        </div>
    </div>
    """, 404

@app.errorhandler(500)
def error_servidor(error):
    return """
    <div class="container">
        <div class="card">
            <h1>🚨 Error del servidor</h1>
            <p>Ha ocurrido un error interno. Por favor, intenta nuevamente.</p>
            <a href="/" class="btn">🔄 Reintentar</a>
        </div>
    </div>
    """, 500

@app.errorhandler(413)
def archivo_demasiado_grande(error):
    return """
    <div class="container">
        <div class="card">
            <h1>📁 Archivo demasiado grande</h1>
            <p>El archivo que intentas subir excede el tamaño máximo permitido (16MB).</p>
            <a href="/" class="btn">📝 Volver al analizador</a>
        </div>
    </div>
    """, 413

# CONFIGURACIÓN CORREGIDA PARA RENDER
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)