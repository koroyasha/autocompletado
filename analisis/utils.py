import re
import unicodedata
import math  
from collections import Counter, defaultdict

# Lista de stopwords en español (incluyendo versiones acentuadas)
STOPWORDS_ES = {
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 
    'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 
    'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 
    'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 
    'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 
    'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 
    'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 
    'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 'ellas', 
    'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 
    'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 'nuestra', 'nuestros', 
    'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'esos', 'esas', 'estoy', 
    'estás', 'está', 'estamos', 'estáis', 'están', 'esté', 'estés', 'estemos', 'estéis', 
    'estén', 'estaré', 'estarás', 'estará', 'estaremos', 'estaréis', 'estarán', 'estaría', 
    'estarías', 'estaríamos', 'estaríais', 'estarían', 'estaba', 'estabas', 'estábamos', 
    'estabais', 'estaban', 'estuve', 'estuviste', 'estuvo', 'estuvimos', 'estuvisteis', 
    'estuvieron', 'estuviera', 'estuvieras', 'estuviéramos', 'estuvierais', 'estuvieran', 
    'estuviese', 'estuvieses', 'estuviésemos', 'estuvieseis', 'estuviesen', 'estando', 
    'estado', 'estada', 'estados', 'estadas', 'estad', 'he', 'has', 'ha', 'hemos', 'habéis', 
    'han', 'haya', 'hayas', 'hayamos', 'hayáis', 'hayan', 'habré', 'habrás', 'habrá', 
    'habremos', 'habréis', 'habrán', 'habría', 'habrías', 'habríamos', 'habríais', 'habrían', 
    'había', 'habías', 'habíamos', 'habíais', 'habían', 'hube', 'hubiste', 'hubo', 'hubimos', 
    'hubisteis', 'hubieron', 'hubiera', 'hubieras', 'hubiéramos', 'hubierais', 'hubieran', 
    'hubiese', 'hubieses', 'hubiésemos', 'hubieseis', 'hubiesen', 'habiendo', 'habido', 
    'habida', 'habidos', 'habidas', 'soy', 'eres', 'es', 'somos', 'sois', 'son', 'sea', 
    'seas', 'seamos', 'seáis', 'sean', 'seré', 'serás', 'será', 'seremos', 'seréis', 'serán', 
    'sería', 'serías', 'seríamos', 'seríais', 'serían', 'era', 'eras', 'éramos', 'erais', 
    'eran', 'fui', 'fuiste', 'fue', 'fuimos', 'fuisteis', 'fueron', 'fuera', 'fueras', 
    'fuéramos', 'fuerais', 'fueran', 'fuese', 'fueses', 'fuésemos', 'fueseis', 'fuesen', 
    'sintiendo', 'sentido', 'sentida', 'sentidos', 'sentidas', 'siente', 'sentid', 'tengo', 
    'tienes', 'tiene', 'tenemos', 'tenéis', 'tienen', 'tenga', 'tengas', 'tengamos', 
    'tengáis', 'tengan', 'tendré', 'tendrás', 'tendrá', 'tendremos', 'tendréis', 'tendrán', 
    'tendría', 'tendrías', 'tendríamos', 'tendríais', 'tendrían', 'tenía', 'tenías', 
    'teníamos', 'teníais', 'tenían', 'tuve', 'tuviste', 'tuvo', 'tuvimos', 'tuvisteis', 
    'tuvieron', 'tuviera', 'tuvieras', 'tuviéramos', 'tuvierais', 'tuvieran', 'tuviese', 
    'tuvieses', 'tuviésemos', 'tuvieseis', 'tuviesen', 'teniendo', 'tenido', 'tenida', 
    'tenidos', 'tenidas', 'tened', 'él', 'ésta', 'éstas', 'éste', 'éstos', 'última', 'últimas', 
    'último', 'últimos', 'aún', 'dónde', 'cómo', 'cuándo', 'cuánto', 'cuánta', 'cuántos', 
    'cuántas', 'qué', 'quiénes', 'también', 'además', 'mientras', 'aunque', 'pero', 'sino', 
    'porque', 'aquel', 'aquella', 'aquellos', 'aquellas', 'ése', 'ésa', 'ésos', 'ésas', 
    'mío', 'mía', 'míos', 'mías', 'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 
    'suyas', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 
    'vuestras', 'cuyo', 'cuya', 'cuyos', 'cuyas'
}

def normalizar_acentos(texto):
    """Normaliza los caracteres acentuados preservando ñ y ü"""
    texto = texto.replace('ñ', '__n_tilde__').replace('ü', '__u_dieresis__')
    texto = texto.replace('Ñ', '__N_tilde__').replace('Ü', '__U_dieresis__')
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    texto = texto.replace('__n_tilde__', 'ñ').replace('__u_dieresis__', 'ü')
    texto = texto.replace('__N_tilde__', 'Ñ').replace('__U_dieresis__', 'Ü')
    return texto

def limpiar_texto(texto, usar_stopwords=True):
    """Limpia el texto: minúsculas, elimina puntuación y stopwords"""
    texto = texto.lower()
    texto = normalizar_acentos(texto)
    
    # Eliminar símbolos de puntuación y caracteres especiales
    texto_limpio = re.sub(r'[^\w\sñü]', ' ', texto)
    
    # Tokenizar
    palabras = texto_limpio.split()
    
    # Eliminar stopwords si se solicita
    if usar_stopwords:
        stopwords_normalizadas = {normalizar_acentos(palabra) for palabra in STOPWORDS_ES}
        palabras = [palabra for palabra in palabras if palabra not in stopwords_normalizadas and len(palabra) > 1]
    
    return palabras

def limpiar_texto_con_fronteras(texto):
    """Limpia el texto incluyendo fronteras de oración <s> y </s>"""
    texto = texto.lower()
    texto = normalizar_acentos(texto)
    
    # Eliminar símbolos de puntuación y caracteres especiales
    texto_limpio = re.sub(r'[^\w\sñü]', ' ', texto)
    
    # Dividir en oraciones usando puntuación
    oraciones = re.split(r'[.!?]+', texto_limpio)
    
    # Procesar cada oración por separado
    todas_palabras = []
    for oracion in oraciones:
        oracion = oracion.strip()
        if oracion:
            # Añadir marcador de inicio de oración
            todas_palabras.append('<s>')
            
            # Tokenizar y filtrar stopwords
            palabras = oracion.split()
            stopwords_normalizadas = {normalizar_acentos(palabra) for palabra in STOPWORDS_ES}
            palabras_filtradas = [
                palabra for palabra in palabras 
                if palabra not in stopwords_normalizadas and len(palabra) > 1
            ]
            
            todas_palabras.extend(palabras_filtradas)
            
            # Añadir marcador de fin de oración
            todas_palabras.append('</s>')
    
    return todas_palabras

def generar_ngramas(tokens, n=2):
    """Genera n-gramas a partir de una lista de tokens"""
    if n <= 1 or len(tokens) < n:
        return []
    
    ngramas = []
    for i in range(len(tokens) - n + 1):
        ngrama = ' '.join(tokens[i:i+n])
        ngramas.append(ngrama)
    
    return ngramas

def calcular_probabilidad_ngramas_general(tokens, n):
    """
    Calcula probabilidades para n-gramas usando la fórmula:
    P(w_i|w_{i-n+1}^{i-1}) = C(w_{i-n+1}^{i}) / C(w_{i-n+1}^{i-1})
    """
    if n < 2:
        return {}
    
    # Generar n-gramas
    ngramas = generar_ngramas(tokens, n)
    
    # Generar (n-1)-gramas (contextos)
    n_minus1_gramas = generar_ngramas(tokens, n-1)
    
    # Contar frecuencias
    freq_ngramas = Counter(ngramas)
    freq_contextos = Counter(n_minus1_gramas)
    
    # Calcular probabilidades
    probabilidades = {}
    for ngrama, count_ngrama in freq_ngramas.items():
        # Extraer el contexto (primeras n-1 palabras)
        palabras = ngrama.split()
        contexto = ' '.join(palabras[:-1])
        
        count_contexto = freq_contextos.get(contexto, 0)
        
        if count_contexto > 0:
            probabilidad = count_ngrama / count_contexto
        else:
            probabilidad = 0.0
        
        # Calcular log probabilidad
        log_probabilidad = math.log(probabilidad) if probabilidad > 0 else float('-inf')
        
        probabilidades[ngrama] = {
            'frecuencia_ngrama': count_ngrama,
            'contexto': contexto,
            'frecuencia_contexto': count_contexto,
            'probabilidad': probabilidad,
            'log_probabilidad': log_probabilidad,
            'palabra_objetivo': palabras[-1],
            'orden_ngrama': n
        }
    
    return probabilidades

def calcular_probabilidad_ngramas(tokens, n):
    """Función wrapper para mantener compatibilidad"""
    return calcular_probabilidad_ngramas_general(tokens, n)

def generar_tabla_probabilidades_avanzada(probabilidades_dict, n_grama, titulo):
    """Genera una tabla HTML con las probabilidades condicionales para n-gramas"""
    if not probabilidades_dict:
        return f"<p>No hay {titulo.lower()} para mostrar</p>"
    
    # Ordenar por frecuencia descendente
    items_ordenados = sorted(
        probabilidades_dict.items(), 
        key=lambda x: x[1]['frecuencia_ngrama'], 
        reverse=True
    )
    
    # Determinar la fórmula según el tipo de n-grama
    if n_grama == 2:
        formula = "P(w_i|w_{i-1}) = C(w_{i-1}, w_i) / C(w_{i-1})"
    else:
        formula = f"P(w_i|w_{{i-{n_grama-1}}}^{{i-1}}) = C(w_{{i-{n_grama-1}}}^{{i}}) / C(w_{{i-{n_grama-1}}}^{{i-1}})"
        
    html = f"""
    <div class="table-container">
        <h3>{titulo}</h3>
        <p class="formula">Fórmula: {formula}</p>
        <table>
            <thead>
                <tr>
                    <th>{n_grama}-grama completo</th>
                    <th>Contexto histórico ({n_grama-1} palabras)</th>
                    <th>Palabra objetivo</th>
                    <th>C(contexto, palabra)</th>
                    <th>C(contexto)</th>
                    <th>Probabilidad</th>
                    <th>Log Probabilidad</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for ngrama, datos in items_ordenados[:15]:
        html += f"""
                <tr>
                    <td><strong>{ngrama}</strong></td>
                    <td>{datos['contexto']}</td>
                    <td>{datos['palabra_objetivo']}</td>
                    <td>{datos['frecuencia_ngrama']}</td>
                    <td>{datos['frecuencia_contexto']}</td>
                    <td>{datos['probabilidad']:.6f}</td>
                    <td>{datos['log_probabilidad']:.6f if datos['log_probabilidad'] != float('-inf') else '-∞'}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return html

def procesar_texto_completo(contenido, n_grama=1, usar_fronteras=False, n_gramas_comparacion=None):
    """Función principal para procesar el texto"""
    if n_gramas_comparacion is None:
        n_gramas_comparacion = [2, 3, 4, 5]
    
    # Limpiar el texto (con o sin fronteras)
    if usar_fronteras:
        palabras_limpias = limpiar_texto_con_fronteras(contenido)
    else:
        palabras_limpias = limpiar_texto(contenido)
    
    # Generar histograma con palabras individuales
    contador_palabras = Counter(palabras_limpias)
    palabras_comunes = contador_palabras.most_common(20)
    
    # Generar n-gramas y probabilidades
    ngramas_comunes = []
    ngramas_probabilidades = {}
    ngramas_comparacion = {}
    
    if n_grama > 1 and len(palabras_limpias) >= n_grama:
        ngramas = generar_ngramas(palabras_limpias, n_grama)
        if ngramas:
            contador_ngramas = Counter(ngramas)
            ngramas_comunes = contador_ngramas.most_common(20)
            ngramas_probabilidades = calcular_probabilidad_ngramas(palabras_limpias, n_grama)
    
    # Calcular n-gramas para comparación
    for n in n_gramas_comparacion:
        if n != n_grama and len(palabras_limpias) >= n:
            ngramas_comparacion[n] = calcular_probabilidad_ngramas(palabras_limpias, n)
    
    return {
        'palabras_comunes': palabras_comunes,
        'ngramas_comunes': ngramas_comunes,
        'ngramas_probabilidades': ngramas_probabilidades,
        'ngramas_comparacion': ngramas_comparacion,
        'total_palabras': len(palabras_limpias),
        'palabras_limpias': palabras_limpias,
        'n_grama': n_grama,
        'usar_fronteras': usar_fronteras,
        'n_gramas_comparacion': n_gramas_comparacion
    }

def predecir_siguiente_palabra(contexto, ngramas_probabilidades, n=2):
    """
    Predice la siguiente palabra dado un contexto y un modelo de n-gramas
    """
    sugerencias = []
    
    for ngrama, datos in ngramas_probabilidades.items():
        if datos['contexto'] == contexto:
            sugerencias.append((datos['palabra_objetivo'], datos['probabilidad']))
    
    # Ordenar por probabilidad descendente
    sugerencias.sort(key=lambda x: x[1], reverse=True)
    
    return sugerencias

def generar_modelo_autocompletado(tokens, n=2):
    """
    Genera un modelo de autocompletado basado en n-gramas
    """
    if n < 2:
        return {}
    
    # Calcular probabilidades de n-gramas
    ngramas_prob = calcular_probabilidad_ngramas(tokens, n)
    
    # Organizar por contextos
    modelo = {}
    for ngrama, datos in ngramas_prob.items():
        contexto = datos['contexto']
        if contexto not in modelo:
            modelo[contexto] = []
        
        modelo[contexto].append({
            'palabra': datos['palabra_objetivo'],
            'probabilidad': datos['probabilidad'],
            'frecuencia': datos['frecuencia_ngrama']
        })
    
    # Ordenar cada lista de sugerencias por probabilidad
    for contexto in modelo:
        modelo[contexto].sort(key=lambda x: x['probabilidad'], reverse=True)
    
    return modelo