#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analizador de Sentimientos en Español - Versión Profesional
============================================================

Módulo optimizado para análisis de sentimientos en español con soporte
para detección contextual, negaciones, intensificadores y emojis.

Autor: Equipo de Desarrollo
Versión: 2.0.0
Python: 3.8+
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import re
import logging
from functools import lru_cache

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ResultadoAnalisis:
    """Clase de datos para almacenar resultados del análisis."""
    sentimiento: str
    emoji: str
    score: float
    confianza: float
    palabras_positivas: float
    palabras_negativas: float
    palabras_analizadas: int = 0
    
    def to_dict(self) -> Dict:
        """Convierte el resultado a diccionario."""
        return {
            'sentimiento': self.sentimiento,
            'emoji': self.emoji,
            'score': round(self.score, 2),
            'confianza': round(self.confianza, 2),
            'palabras_positivas': round(self.palabras_positivas, 2),
            'palabras_negativas': round(self.palabras_negativas, 2)
        }


class AnalizadorSentimientos:
    """
    Analizador avanzado de sentimientos para texto en español.
    
    Características:
    - Detección contextual de negaciones
    - Análisis de intensificadores y atenuadores
    - Reconocimiento de frases idiomáticas
    - Soporte para emojis y puntuación
    - Sistema de pesos ponderados
    
    Ejemplo:
        >>> analizador = AnalizadorSentimientos()
        >>> resultado = analizador.analizar_sentimiento("¡Excelente producto!")
        >>> print(resultado['sentimiento'])
        'Positivo'
    """
    
    # Constantes de configuración
    UMBRAL_FUERTE = 2.0
    UMBRAL_DEBIL = 0.5
    FACTOR_INTENSIFICADOR = 1.5
    FACTOR_ATENUADOR = 0.6
    PESO_FRASE_CONTEXTUAL = 2.5
    MAX_INTENSIDAD = 3.0
    VENTANA_NEGACION = 3
    VENTANA_INTENSIDAD = 2
    
    def __init__(self):
        """Inicializa el analizador con diccionarios optimizados."""
        logger.info("Inicializando AnalizadorSentimientos v2.0")
        
        # Diccionarios de palabras - usando frozenset para optimización
        self.palabras_positivas: Set[str] = frozenset({
            'excelente', 'bueno', 'buena', 'buenos', 'buenas', 'genial', 'increíble', 
            'perfecto', 'perfecta', 'recomendado', 'recomendada', 'encanta', 'encantó', 
            'mejor', 'mejores', 'feliz', 'contento', 'contenta', 'maravilloso', 'maravillosa',
            'fantástico', 'fantástica', 'súper', 'super', 'amor', 'amo', 'love',
            'calidad', 'rápido', 'rápida', 'eficiente', 'profesional', 'amable',
            'superó', 'expectativas', 'satisfecho', 'satisfecha', 'vale', 'pena',
            'estrellas', 'recomiendo', 'felicitaciones', 'gracias', 'éxito', 'exitoso',
            'hermoso', 'hermosa', 'bonito', 'bonita', 'agradable', 'divertido',
            'útil', 'práctico', 'práctica', 'barato', 'barata', 'económico',
            'fácil', 'sencillo', 'sencilla', 'claro', 'clara', 'preciso', 'exacto',
            'correcto', 'adecuado', 'apropiado', 'conveniente', 'ideal',
            'óptimo', 'destacado', 'sobresaliente', 'notable', 'brillante',
            'impresionante', 'asombroso', 'sorprendente', 'inmejorable',
            'inigualable', 'extraordinario', 'magnífico', 'espléndido',
            'estupendo', 'fenomenal', 'provechoso', 'beneficioso', 'ventajoso',
            'encantador', 'precioso', 'divino', 'exquisito', 'espectacular',
            'maravilla', 'tremendo', 'formidable', 'admirable', 'glorioso'
        })
        
        self.palabras_negativas: Set[str] = frozenset({
            'malo', 'mala', 'malos', 'malas', 'pésimo', 'pésima', 'horrible', 
            'terrible', 'defectuoso', 'defectuosa', 'roto', 'rota', 'nunca', 
            'jamás', 'peor', 'peores', 'lento', 'lenta', 'caro', 'cara',
            'estafa', 'fraude', 'decepción', 'decepcionante', 'problema', 
            'problemas', 'falla', 'fallas', 'defecto', 'defectos', 'insatisfecho',
            'insatisfecha', 'desagradable', 'desilusión', 'engaño', 
            'rompió', 'desperfecto', 'averiado', 'dañado', 'estropeado', 'inútil',
            'inservible', 'inadecuado', 'inapropiado', 'incorrecto',
            'erróneo', 'equivocado', 'deficiente', 'imperfecto', 'desastroso', 
            'catastrófico', 'desalentador', 'frustrante', 'molesto', 'irritante', 
            'fastidioso', 'engorroso', 'complicado', 'difícil', 'complejo', 
            'confuso', 'ambiguo', 'incierto', 'dudoso', 'sospechoso', 'deshonesto', 
            'fraudulento', 'estafador', 'mediocre', 'pobre', 'basura', 'asco',
            'horrendo', 'repugnante', 'deplorable', 'lamentable', 'desastre',
            'patético', 'vergonzoso', 'abominable', 'nefasto', 'funesto'
        })
        
        self.palabras_neutras: Set[str] = frozenset({
            'normal', 'regular', 'común', 'estándar', 'básico', 'cumple',
            'función', 'aceptable', 'ok', 'bien', 'nada', 'especial',
            'promedio', 'justo', 'usual', 'habitual', 'corriente', 
            'ordinario', 'convencional', 'simple', 'típico', 'medio'
        })
        
        self.palabras_muy_positivas: Set[str] = frozenset({
            'excelente', 'increíble', 'maravilloso', 'fantástico', 'perfecto',
            'encanta', 'amor', 'amo', 'espectacular', 'genial', 'súper',
            'sobresaliente', 'brillante', 'impresionante', 'asombroso',
            'extraordinario', 'magnífico', 'espléndido', 'fenomenal',
            'divino', 'glorioso', 'maravilla'
        })
        
        self.palabras_muy_negativas: Set[str] = frozenset({
            'pésimo', 'pésima', 'horrible', 'terrible', 'estafa', 'fraude', 
            'desastre', 'engaño', 'desilusión', 'catastrófico', 'desastroso', 
            'basura', 'asco', 'repugnante', 'deplorable', 'horrendo',
            'abominable', 'nefasto', 'patético'
        })
        
        self.negaciones: Set[str] = frozenset({
            'no', 'nunca', 'jamás', 'tampoco', 'sin', 'ni', 'nada', 'ningún',
            'ninguna', 'ninguno'
        })
        
        self.intensificadores: Set[str] = frozenset({
            'muy', 'mucho', 'mucha', 'bastante', 'totalmente', 'completamente',
            'absolutamente', 'realmente', 'extremadamente', 'increíblemente',
            'sumamente', 'demasiado', 'tan', 'bien', 'súper', 'ultra',
            'mega', 'hiper', 'super'
        })
        
        self.atenuadores: Set[str] = frozenset({
            'poco', 'ligeramente', 'algo', 'medianamente', 'relativamente',
            'apenas', 'casi', 'medio', 'más', 'menos', 'cierto'
        })
        
        # Frases contextuales compiladas para mejor rendimiento
        self._compilar_frases()
        
        # Patrones regex compilados
        self._compilar_patrones()
        
        logger.info("AnalizadorSentimientos inicializado correctamente")
    
    def _compilar_frases(self) -> None:
        """Compila las frases contextuales en un diccionario optimizado."""
        self.frases_negativas: Dict[str, float] = {
            'se rompió': -2.5,
            'mala calidad': -2.0,
            'no sirve': -2.5,
            'no funciona': -2.5,
            'no me gustó': -2.0,
            'no lo recomiendo': -3.0,
            'no vale la pena': -2.5,
            'no cumple': -2.0,
            'no es lo que esperaba': -2.0,
            'pérdida de tiempo': -3.0,
            'no volveré': -2.5,
            'no lo compren': -3.0,
            'nunca más': -3.0,
            'jamás lo recomendaría': -3.0,
            'decepción total': -2.5,
            'no lo vuelvo a comprar': -2.5,
            'no vale': -2.0,
            'no merece': -2.0,
            'no lo compraría': -2.5,
            'estafa total': -3.5
        }
        
        self.frases_positivas: Dict[str, float] = {
            'lo recomiendo': 3.0,
            'vale la pena': 2.5,
            'superó expectativas': 3.0,
            'cumple con lo prometido': 2.5,
            'excelente calidad': 3.0,
            'muy buen': 2.0,
            'muy buena': 2.0,
            'totalmente recomendado': 3.5,
            'volveré a comprar': 2.5,
            'excelente servicio': 3.0,
            'muy contento': 2.0,
            'muy feliz': 2.0,
            'completamente satisfecho': 3.0,
            'mejor compra': 2.5,
            'vale cada peso': 2.5,
            'lo amo': 3.0,
            'lo amé': 3.0,
            '100% recomendado': 3.5
        }
    
    def _compilar_patrones(self) -> None:
        """Compila patrones regex para optimizar búsquedas."""
        self.patrones_positivos = [
            re.compile(r'\b(lo\s+re?comiendo|recomendad[oa]\s+totalmente)\b', re.IGNORECASE),
            re.compile(r'\b(vale\s+la\s+pena|excelente\s+calidad)\b', re.IGNORECASE),
            re.compile(r'\b(super[oó]\s+(mis|las)\s+expectativas)\b', re.IGNORECASE),
            re.compile(r'\b(volver[ée]\s+a\s+comprar)\b', re.IGNORECASE),
            re.compile(r'\b(100%\s+recomendado|totalmente\s+recomendado)\b', re.IGNORECASE)
        ]
        
        self.patrones_negativos = [
            re.compile(r'\b(no\s+lo\s+re?comiendo|no\s+recomendado)\b', re.IGNORECASE),
            re.compile(r'\b(no\s+vale\s+la\s+pena)\b', re.IGNORECASE),
            re.compile(r'\b(no\s+(sirve|funciona|me\s+gust[oó]))\b', re.IGNORECASE),
            re.compile(r'\b(nunca\s+m[aá]s|jam[aá]s|p[ée]rdida\s+de\s+tiempo)\b', re.IGNORECASE),
            re.compile(r'\b(estafa|fraude|enga[ñn]o)\b', re.IGNORECASE)
        ]
        
        self.patron_emojis_positivos = re.compile(r'[😊😃😄😁🤗❤️💖👍⭐🌟✨🎉😍🥰😘💚💙💛🎊🎈]')
        self.patron_emojis_negativos = re.compile(r'[😞😢😭😔😩😫💔😠😡🤬😤😖😣😟☹️]')
        self.patron_exclamaciones = re.compile(r'!+')
        self.patron_urls = re.compile(r'http\S+|www\S+')
        self.patron_espacios = re.compile(r'\s+')
    
    @lru_cache(maxsize=1024)
    def limpiar_texto(self, texto: str) -> str:
        """
        Limpia y normaliza el texto de entrada.
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            Texto limpio y normalizado en minúsculas
        """
        if not texto:
            return ""
        
        # Convertir a minúsculas
        texto = texto.lower()
        
        # Remover URLs
        texto = self.patron_urls.sub('', texto)
        
        # Normalizar espacios
        texto = self.patron_espacios.sub(' ', texto).strip()
        
        return texto
    
    def detectar_negacion_avanzada(self, palabras: List[str], posicion: int) -> bool:
        """
        Detecta negaciones considerando el contexto y doble negación.
        
        Args:
            palabras: Lista de palabras del texto
            posicion: Posición de la palabra objetivo
            
        Returns:
            True si hay negación activa (número impar de negaciones)
        """
        inicio = max(0, posicion - self.VENTANA_NEGACION)
        segmento_previo = palabras[inicio:posicion]
        
        # Contar negaciones en la ventana
        negaciones_encontradas = sum(1 for p in segmento_previo if p in self.negaciones)
        
        # Número impar de negaciones = negación activa
        return negaciones_encontradas % 2 == 1
    
    def calcular_intensidad_mejorada(self, palabras: List[str], posicion: int) -> float:
        """
        Calcula el factor de intensidad basado en modificadores cercanos.
        
        Args:
            palabras: Lista de palabras del texto
            posicion: Posición de la palabra objetivo
            
        Returns:
            Factor de intensidad (0.6 a 3.0)
        """
        intensidad = 1.0
        inicio = max(0, posicion - self.VENTANA_INTENSIDAD)
        segmento_previo = palabras[inicio:posicion]
        
        for palabra in segmento_previo:
            if palabra in self.intensificadores:
                intensidad *= self.FACTOR_INTENSIFICADOR
            elif palabra in self.atenuadores:
                intensidad *= self.FACTOR_ATENUADOR
        
        return min(intensidad, self.MAX_INTENSIDAD)
    
    def analizar_frases_contextuales(self, texto: str) -> float:
        """
        Analiza frases completas con significado contextual.
        
        Args:
            texto: Texto limpio a analizar
            
        Returns:
            Score acumulado de frases detectadas
        """
        score = 0.0
        
        # Buscar frases positivas
        for frase, peso in self.frases_positivas.items():
            if frase in texto:
                score += peso
                logger.debug(f"Frase positiva detectada: '{frase}' (+{peso})")
        
        # Buscar frases negativas
        for frase, peso in self.frases_negativas.items():
            if frase in texto:
                score += peso  # peso ya es negativo
                logger.debug(f"Frase negativa detectada: '{frase}' ({peso})")
        
        return score
    
    def analizar_patrones_regex(self, texto: str) -> float:
        """
        Detecta patrones mediante expresiones regulares compiladas.
        
        Args:
            texto: Texto limpio a analizar
            
        Returns:
            Score basado en patrones detectados
        """
        score = 0.0
        
        # Patrones positivos
        for patron in self.patrones_positivos:
            if patron.search(texto):
                score += 2.0
        
        # Patrones negativos
        for patron in self.patrones_negativos:
            if patron.search(texto):
                score -= 2.5
        
        return score
    
    def analizar_emojis_y_puntuacion(self, texto: str) -> Tuple[float, int]:
        """
        Analiza emojis y signos de puntuación para determinar intensidad.
        
        Args:
            texto: Texto original (sin limpiar)
            
        Returns:
            Tupla (score_emojis, cantidad_exclamaciones)
        """
        # Contar emojis
        emojis_positivos = len(self.patron_emojis_positivos.findall(texto))
        emojis_negativos = len(self.patron_emojis_negativos.findall(texto))
        
        score = (emojis_positivos - emojis_negativos) * 1.0
        
        # Contar exclamaciones
        exclamaciones = len(self.patron_exclamaciones.findall(texto))
        
        return score, exclamaciones
    
    def analizar_sentimiento(self, texto: str) -> Dict:
        """
        Realiza el análisis completo de sentimiento del texto.
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Diccionario con resultados del análisis
            
        Raises:
            ValueError: Si el texto es None
        """
        if texto is None:
            raise ValueError("El texto no puede ser None")
        
        if not texto or texto.strip() == "":
            logger.warning("Texto vacío recibido")
            return ResultadoAnalisis(
                sentimiento='Neutro',
                emoji='😐',
                score=0.0,
                confianza=0.0,
                palabras_positivas=0.0,
                palabras_negativas=0.0
            ).to_dict()
        
        try:
            texto_original = texto
            texto = self.limpiar_texto(texto)
            palabras = texto.split()
            
            # Contadores
            score_positivo = 0.0
            score_negativo = 0.0
            palabras_analizadas = 0
            
            # 1. Análisis de frases contextuales (mayor prioridad)
            score_frases = self.analizar_frases_contextuales(texto)
            if score_frases > 0:
                score_positivo += score_frases
                palabras_analizadas += 1
            elif score_frases < 0:
                score_negativo += abs(score_frases)
                palabras_analizadas += 1
            
            # 2. Análisis de patrones regex
            score_patrones = self.analizar_patrones_regex(texto)
            if score_patrones > 0:
                score_positivo += score_patrones
                palabras_analizadas += 1
            elif score_patrones < 0:
                score_negativo += abs(score_patrones)
                palabras_analizadas += 1
            
            # 3. Análisis de palabras individuales con contexto
            for i, palabra in enumerate(palabras):
                # Determinar tipo de palabra
                es_muy_positiva = palabra in self.palabras_muy_positivas
                es_muy_negativa = palabra in self.palabras_muy_negativas
                es_positiva = palabra in self.palabras_positivas
                es_negativa = palabra in self.palabras_negativas
                
                if not (es_positiva or es_negativa or es_muy_positiva or es_muy_negativa):
                    continue
                
                palabras_analizadas += 1
                
                # Calcular peso base
                if es_muy_positiva:
                    peso_base = 2.0
                elif es_positiva:
                    peso_base = 1.0
                elif es_muy_negativa:
                    peso_base = -2.0
                else:
                    peso_base = -1.0
                
                # Aplicar modificadores contextuales
                tiene_negacion = self.detectar_negacion_avanzada(palabras, i)
                if tiene_negacion:
                    peso_base = -peso_base
                
                intensidad = self.calcular_intensidad_mejorada(palabras, i)
                peso_final = peso_base * intensidad
                
                # Acumular score
                if peso_final > 0:
                    score_positivo += peso_final
                else:
                    score_negativo += abs(peso_final)
            
            # 4. Análisis de emojis y puntuación
            score_emoji, exclamaciones = self.analizar_emojis_y_puntuacion(texto_original)
            if score_emoji > 0:
                score_positivo += score_emoji
            elif score_emoji < 0:
                score_negativo += abs(score_emoji)
            
            # Amplificar con exclamaciones
            if exclamaciones > 0 and palabras_analizadas > 0:
                factor_exclamacion = min(1 + (exclamaciones * 0.1), 1.5)
                if score_positivo > score_negativo:
                    score_positivo *= factor_exclamacion
                elif score_negativo > score_positivo:
                    score_negativo *= factor_exclamacion
            
            # 5. Detectar palabras neutras explícitas
            tiene_neutras = any(p in self.palabras_neutras for p in palabras)
            
            # Calcular score final
            score_final = score_positivo - score_negativo
            
            # Calcular confianza
            confianza = self._calcular_confianza(
                score_positivo, 
                score_negativo, 
                palabras_analizadas
            )
            
            # Clasificación final
            sentimiento, emoji = self._clasificar_sentimiento(
                score_final, 
                tiene_neutras, 
                confianza
            )
            
            # Ajustar confianza según clasificación
            if sentimiento == 'Neutro' and tiene_neutras:
                confianza = max(confianza, 60.0)
            
            resultado = ResultadoAnalisis(
                sentimiento=sentimiento,
                emoji=emoji,
                score=score_final,
                confianza=confianza,
                palabras_positivas=score_positivo,
                palabras_negativas=score_negativo,
                palabras_analizadas=palabras_analizadas
            )
            
            logger.debug(f"Análisis completado: {resultado}")
            return resultado.to_dict()
            
        except Exception as e:
            logger.error(f"Error al analizar sentimiento: {str(e)}", exc_info=True)
            # Retornar resultado neutro en caso de error
            return ResultadoAnalisis(
                sentimiento='Neutro',
                emoji='😐',
                score=0.0,
                confianza=0.0,
                palabras_positivas=0.0,
                palabras_negativas=0.0
            ).to_dict()
    
    def _calcular_confianza(
        self, 
        score_positivo: float, 
        score_negativo: float, 
        palabras_analizadas: int
    ) -> float:
        """
        Calcula el nivel de confianza del análisis.
        
        Args:
            score_positivo: Score acumulado positivo
            score_negativo: Score acumulado negativo
            palabras_analizadas: Cantidad de palabras significativas
            
        Returns:
            Nivel de confianza entre 30 y 95
        """
        if palabras_analizadas == 0:
            return 30.0
        
        diferencia = abs(score_positivo - score_negativo)
        total_score = score_positivo + score_negativo
        
        if total_score > 0:
            confianza = (diferencia / total_score) * 100
        else:
            confianza = 50.0
        
        # Ajustes por cantidad de evidencia
        if palabras_analizadas >= 3:
            confianza = min(confianza + 10, 95)
        elif palabras_analizadas == 1:
            confianza = max(confianza - 10, 40)
        
        return max(30.0, min(95.0, confianza))
    
    def _clasificar_sentimiento(
        self, 
        score_final: float, 
        tiene_neutras: bool, 
        confianza: float
    ) -> Tuple[str, str]:
        """
        Clasifica el sentimiento basado en el score final.
        
        Args:
            score_final: Score total calculado
            tiene_neutras: Si el texto tiene palabras neutras explícitas
            confianza: Nivel de confianza del análisis
            
        Returns:
            Tupla (sentimiento, emoji)
        """
        if tiene_neutras and abs(score_final) < 1.5:
            return 'Neutro', '😐'
        
        if score_final > self.UMBRAL_FUERTE:
            return 'Positivo', '😊'
        elif score_final > self.UMBRAL_DEBIL:
            return 'Positivo', '😊'
        elif score_final < -self.UMBRAL_FUERTE:
            return 'Negativo', '😞'
        elif score_final < -self.UMBRAL_DEBIL:
            return 'Negativo', '😞'
        else:
            return 'Neutro', '😐'


# ============================================================================
# Funciones de utilidad
# ============================================================================

def procesar_comentarios_completos(comentarios: List[str]) -> List[Dict]:
    """
    Procesa una lista completa de comentarios.
    
    Args:
        comentarios: Lista de textos a analizar
        
    Returns:
        Lista de diccionarios con resultados
        
    Raises:
        ValueError: Si comentarios no es una lista
    """
    if not isinstance(comentarios, list):
        raise ValueError("comentarios debe ser una lista")
    
    analizador = AnalizadorSentimientos()
    resultados = []
    
    logger.info(f"Procesando {len(comentarios)} comentarios")
    
    for i, comentario in enumerate(comentarios, 1):
        try:
            analisis = analizador.analizar_sentimiento(comentario)
            
            resultados.append({
                'id': i,
                'comentario': comentario,
                'sentimiento': analisis['sentimiento'],
                'emoji': analisis['emoji'],
                'confianza': analisis['confianza'],
                'score': analisis['score']
            })
        except Exception as e:
            logger.error(f"Error procesando comentario {i}: {str(e)}")
            continue
    
    logger.info(f"Procesamiento completado: {len(resultados)} comentarios analizados")
    return resultados


def generar_reporte(resultados: List[Dict]) -> Dict:
    """
    Genera un reporte estadístico de los sentimientos.
    
    Args:
        resultados: Lista de resultados de análisis
        
    Returns:
        Diccionario con estadísticas
    """
    if not resultados:
        logger.warning("Lista de resultados vacía")
        return {
            'total': 0,
            'positivos': 0,
            'negativos': 0,
            'neutros': 0,
            'porcentaje_positivos': 0.0,
            'porcentaje_negativos': 0.0,
            'porcentaje_neutros': 0.0
        }
    
    total = len(resultados)
    positivos = sum(1 for r in resultados if r['sentimiento'] == 'Positivo')