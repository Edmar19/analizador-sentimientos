from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        tipo = request.form.get('tipo')
        comentarios = []
        
        if tipo == 'texto':
            texto = request.form.get('comentarios', '')
            comentarios = [linea.strip() for linea in texto.split('\n') if linea.strip()]
        else:
            return "Solo texto por ahora", 400
        
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
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)