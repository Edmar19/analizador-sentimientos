from flask import Flask, render_template, request, redirect, url_for
import os
import csv
import traceback
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear carpetas necesarias si no existen
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if not os.path.exists('static/img'):
    os.makedirs('static/img')

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    """Procesa los comentarios y muestra resultados"""
    try:
        logger.info("Iniciando análisis de comentarios...")
        
        tipo = request.form.get('tipo')
        comentarios = []
        
        logger.info(f"Tipo de análisis: {tipo}")
        
        if tipo == 'archivo':
            logger.info("Procesando archivo...")
            if 'file' not in request.files:
                logger.error("No se encontró el archivo en la request")
                return redirect(url_for('index'))
            
            file = request.files['file']
            logger.info(f"Archivo recibido: {file.filename}")
            
            if file.filename == '':
                logger.error("Nombre de archivo vacío")
                return redirect(url_for('index'))
            
            if file and (file.filename.endswith('.txt') or file.filename.endswith('.csv')):
                if file.filename.endswith('.csv'):
                    try:
                        logger.info("Procesando archivo CSV...")
                        contenido = file.read().decode('utf-8').splitlines()
                        reader = csv.reader(contenido)
                        
                        for fila in reader:
                            if fila:
                                for celda in fila:
                                    if celda.strip():
                                        comentarios.append(celda.strip())
                                        break
                        logger.info(f"CSV procesado: {len(comentarios)} comentarios")
                    except Exception as e:
                        logger.error(f"Error procesando CSV: {e}")
                        file.seek(0)
                        contenido = file.read().decode('utf-8')
                        lineas = contenido.split('\n')
                        for linea in lineas:
                            if linea.strip():
                                comentarios.append(linea.strip())
                        logger.info(f"Fallback a texto plano: {len(comentarios)} comentarios")
                else:
                    logger.info("Procesando archivo TXT...")
                    contenido = file.read().decode('utf-8')
                    comentarios = [linea.strip() for linea in contenido.split('\n') if linea.strip()]
                    logger.info(f"TXT procesado: {len(comentarios)} comentarios")
        
        elif tipo == 'texto':
            logger.info("Procesando texto pegado...")
            texto = request.form.get('comentarios', '')
            comentarios = [linea.strip() for linea in texto.split('\n') if linea.strip()]
            logger.info(f"Texto procesado: {len(comentarios)} comentarios")
        
        logger.info(f"Total de comentarios a analizar: {len(comentarios)}")
        
        if not comentarios:
            logger.error("No hay comentarios para analizar")
            return redirect(url_for('index'))
        
        # Importar y analizar comentarios
        try:
            logger.info("Importando módulos del analizador...")
            from analizador import procesar_comentarios_completos, generar_reporte, generar_grafica_base64
            logger.info("Módulos importados correctamente")
        except ImportError as e:
            logger.error(f"Error importando módulos: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return f"Error importando módulos: {e}", 500
        
        # Analizar comentarios
        try:
            logger.info("Iniciando procesamiento de comentarios...")
            resultados = procesar_comentarios_completos(comentarios)
            logger.info(f"Comentarios procesados: {len(resultados)}")
            
            reporte = generar_reporte(resultados)
            logger.info(f"Reporte generado: {reporte}")
            
            logger.info("Generando gráfica...")
            grafica_base64 = generar_grafica_base64(reporte)
            if grafica_base64:
                logger.info("Gráfica generada exitosamente")
            else:
                logger.warning("No se pudo generar la gráfica")
            
            logger.info("Renderizando template de resultados...")
            return render_template('resultados.html', 
                                 resultados=resultados, 
                                 reporte=reporte,
                                 grafica_base64=grafica_base64)
                                 
        except Exception as e:
            logger.error(f"Error en procesamiento: {e}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            return f"Error procesando comentarios: {str(e)}", 500
            
    except Exception as e:
        logger.error(f"Error general: {e}")
        logger.error(f"Traceback completo: {traceback.format_exc()}")
        return f"Error interno del servidor: {str(e)}", 500

# Ruta para testing básico
@app.route('/test')
def test():
    """Página de prueba para verificar que el analizador funciona"""
    try:
        logger.info("Ejecutando prueba del analizador...")
        
        # Importar módulos
        from analizador import procesar_comentarios_completos, generar_reporte, generar_grafica_base64
        
        # Comentarios de prueba simples
        comentarios_prueba = [
            "Excelente producto, muy recomendado",
            "No me gustó, mala calidad",
            "Está regular, nada especial",
            "Increíble servicio al cliente",
            "Pésima experiencia, no vuelvo"
        ]
        
        logger.info(f"Comentarios de prueba: {comentarios_prueba}")
        
        # Procesar
        resultados = procesar_comentarios_completos(comentarios_prueba)
        reporte = generar_reporte(resultados)
        grafica_base64 = generar_grafica_base64(reporte)
        
        # Resultado simple
        resultado_html = f"""
        <h1>Prueba Exitosa</h1>
        <p>Comentarios procesados: {len(resultados)}</p>
        <p>Reporte: {reporte}</p>
        <p>Gráfica generada: {'Sí' if grafica_base64 else 'No'}</p>
        <h3>Resultados:</h3>
        """
        
        for resultado in resultados:
            resultado_html += f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px;">
                <strong>{resultado['sentimiento']} {resultado['emoji']}</strong><br>
                {resultado['comentario']}<br>
                Score: {resultado['score']} | Confianza: {resultado['confianza']}%
            </div>
            """
        
        return resultado_html
        
    except Exception as e:
        logger.error(f"Error en prueba: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"""
        <h1>Error en Prueba</h1>
        <p>Error: {str(e)}</p>
        <pre>{traceback.format_exc()}</pre>
        """

# CONFIGURACIÓN CORREGIDA PARA RENDER
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=True)