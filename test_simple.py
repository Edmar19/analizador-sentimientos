#!/usr/bin/env python3
"""
Script para probar el analizador de forma aislada
"""

import sys
import os
import traceback

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

def test_analizador():
    """Prueba básica del analizador"""
    try:
        print("=== INICIANDO PRUEBA DEL ANALIZADOR ===")
        
        # Importar módulos
        print("1. Importando módulos...")
        from analizador import AnalizadorSentimientos, procesar_comentarios_completos, generar_reporte
        
        print("2. Creando instancia del analizador...")
        analizador = AnalizadorSentimientos()
        
        print("3. Probando análisis individual...")
        test_comentarios = [
            "Excelente producto",
            "Muy mala calidad",
            "Regular, nada especial",
            ""
        ]
        
        for comentario in test_comentarios:
            resultado = analizador.analizar_sentimiento(comentario)
            print(f"   '{comentario}' -> {resultado['sentimiento']} {resultado['emoji']}")
        
        print("4. Probando procesamiento por lotes...")
        resultados = procesar_comentarios_completos(test_comentarios)
        print(f"   Procesados: {len(resultados)} comentarios")
        
        print("5. Generando reporte...")
        reporte = generar_reporte(resultados)
        print(f"   Reporte: {reporte}")
        
        print("6. Probando generación de gráfica...")
        from analizador import generar_grafica_base64
        grafica = generar_grafica_base64(reporte)
        if grafica:
            print("   ✓ Gráfica generada exitosamente")
        else:
            print("   ✗ Error generando gráfica")
        
        print("=== PRUEBA COMPLETADA EXITOSAMENTE ===")
        return True
        
    except Exception as e:
        print(f"=== ERROR EN LA PRUEBA ===")
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_analizador()
    sys.exit(0 if success else 1)