from flask import Flask, render_template, request, redirect, url_for
import os
import csv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

if not os.path.exists('uploads'):
    os.makedirs('uploads')

if not os.path.exists('static/img'):
    os.makedirs('static/img')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        tipo = request.form.get('tipo')
        comentarios = []
        
        if tipo == 'archivo':
            if 'file' not in request.files:
                return redirect(url_for('index'))
            
            file = request.files['file']
            
            if file.filename == '':
                return redirect(url_for('index'))
            
            if file and (file.filename.endswith('.txt') or file.filename.endswith('.csv')):
                if file.filename.endswith('.csv'):
                    try:
                        contenido = file.read().decode('utf-8').splitlines()
                        reader = csv.reader(contenido)
                        for fila in reader:
                            if fila:
                                for celda in fila:
                                    if celda.strip():
                                        comentarios.append(celda.strip())
                                        break
                    except Exception:
                        file.seek(0)
                        contenido = file.read().decode('utf-8')
                        lineas = contenido.split('\n')
                        for linea in lineas:
                            if linea.strip():
                                comentarios.append(linea.strip())
                else:
                    contenido = file.read().decode('utf-8')
                    comentarios = [linea.strip() for linea in contenido.split('\n') if linea.strip()]
        
        elif tipo == 'texto':
            texto = request.form.get('comentarios', '')
            comentarios = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        
        if not comentarios:
            return redirect(url_for('index'))
        
        from analizador import procesar_comentarios_completos, generar_reporte, generar_grafica_base64
        
        resultados = procesar_comentarios_completos(comentarios)
        reporte = generar_reporte(resultados)
        grafica_base64 = generar_grafica_base64(reporte)
        
        return render_template('resultados.html', 
                             resultados=resultados, 
                             reporte=reporte,
                             grafica_base64=grafica_base64)
                             
    except Exception as e:
        return f"Error procesando comentarios: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)