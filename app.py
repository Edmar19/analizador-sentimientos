from flask import Flask, render_template, request, redirect, url_for
import os
import csv
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
        
        # CORRECCIÓN: .csv no .cvs
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
    
    return render_template('resultados.html', resultados=resultados, reporte=reporte)

# CONFIGURACIÓN CORREGIDA PARA RENDER
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)