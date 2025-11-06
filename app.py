from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from analizador import procesar_comentarios_completos, generar_reporte

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
        
        if file and file.filename.endswith('.txt'):
            # Leer el archivo directamente
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
    
    return render_template('resultados.html', resultados=resultados, reporte=reporte)

if __name__ == '__main__':
    app.run(debug=True)