# views.py - Actualizar las importaciones
import re
import json
from collections import Counter
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import TextoAnalizadoForm
from .models import TextoAnalizado
from .utils import procesar_texto_completo, limpiar_texto, limpiar_texto_con_fronteras, calcular_probabilidad_ngramas

def subir_texto(request):
    if request.method == 'POST':
        form = TextoAnalizadoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_textos')
    else:
        form = TextoAnalizadoForm()
    return render(request, 'subir.html', {'form': form})

def lista_textos(request):
    textos = TextoAnalizado.objects.all().order_by('-fecha_subida')
    return render(request, 'lista.html', {'textos': textos})

def analizar_texto(request, texto_id, n_grama=1):
    if 'n_grama' in request.GET:
        try:
            n_grama = int(request.GET.get('n_grama', 1))
            if n_grama < 1:
                n_grama = 1
            elif n_grama > 100:
                n_grama = 100
        except (ValueError, TypeError):
            n_grama = 1
    
    # Verificar si se solicitan fronteras de oración
    usar_fronteras = request.GET.get('fronteras', 'false').lower() == 'true'
    
    # Obtener n-gramas para comparación
    n_gramas_comparacion = [2, 3, 4, 5, 6]
    
    texto_obj = get_object_or_404(TextoAnalizado, id=texto_id)
    
    # Leer el contenido del archivo
    try:
        with texto_obj.archivo.open('r') as archivo:
            contenido = archivo.read()
    except:
        contenido = ""
    
    # Procesar el texto
    resultado = procesar_texto_completo(contenido, n_grama, usar_fronteras, n_gramas_comparacion)
    
    # Guardar el contenido original y procesado en la sesión
    request.session['texto_original'] = contenido
    request.session['texto_procesado'] = ' '.join(resultado['palabras_limpias'])
    
    return render(request, 'resultado.html', {
        'texto': texto_obj,
        'palabras_comunes': resultado['palabras_comunes'],
        'ngramas_comunes': resultado['ngramas_comunes'],
        'ngramas_probabilidades': resultado['ngramas_probabilidades'],
        'ngramas_comparacion': resultado['ngramas_comparacion'],
        'total_palabras': resultado['total_palabras'],
        'n_grama': n_grama,
        'usar_fronteras': usar_fronteras,
        'n_gramas_comparacion': resultado['n_gramas_comparacion'],
        'texto_id': texto_id
    })
    
def ver_procesamiento(request, texto_id):
    """Vista para mostrar los detalles del procesamiento aplicado"""
    texto_obj = get_object_or_404(TextoAnalizado, id=texto_id)
    
    # Leer el contenido del archivo
    try:
        with texto_obj.archivo.open('r') as archivo:
            contenido = archivo.read()
    except:
        contenido = ""
    
    # Obtener el texto original y procesado
    texto_original = contenido
    palabras_limpias = limpiar_texto(contenido)
    texto_procesado = ' '.join(palabras_limpias)
    
    # Contar estadísticas
    palabras_originales = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]+\b', texto_original.lower())
    stopwords_eliminadas = len(palabras_originales) - len(palabras_limpias)
    
    # Encontrar símbolos eliminados
    simbolos_eliminados = set()
    for palabra in texto_original.split():
        simbolos = re.findall(r'[^\w\sáéíóúñüÁÉÍÓÚÑÜ]', palabra)
        simbolos_eliminados.update(simbolos)
    
    # Encontrar palabras con acentos en el texto original
    palabras_con_acentos = []
    for palabra in palabras_originales:
        if re.search(r'[áéíóúÁÉÍÓÚñÑüÜ]', palabra):
            palabras_con_acentos.append(palabra)
    
    return render(request, 'procesamiento.html', {
        'texto': texto_obj,
        'texto_original': texto_original,
        'texto_procesado': texto_procesado,
        'total_palabras_original': len(palabras_originales),
        'total_palabras_limpias': len(palabras_limpias),
        'stopwords_eliminadas': stopwords_eliminadas,
        'simbolos_eliminados': ', '.join(simbolos_eliminados) if simbolos_eliminados else 'Ninguno',
        'palabras_con_acentos': palabras_con_acentos[:20]
    })

def autocompletado_view(request):
    """Vista principal para el autocompletado"""
    textos = TextoAnalizado.objects.all().order_by('-fecha_subida')
    return render(request, 'autocompletado.html', {
        'textos': textos
    })

def obtener_sugerencias(request):
    """API para obtener sugerencias de autocompletado"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            texto_parcial = data.get('texto', '').strip().lower()
            texto_id = data.get('texto_id')
            n_grama = int(data.get('n_grama', 3))
            max_sugerencias = int(data.get('max_sugerencias', 5))
            usar_fronteras = data.get('fronteras', False)
            
            # Validar n_grama
            if n_grama < 2:
                n_grama = 2
            elif n_grama > 20:
                n_grama = 20
                
            # Validar max_sugerencias
            if max_sugerencias < 1:
                max_sugerencias = 1
            elif max_sugerencias > 20:
                max_sugerencias = 20
            
            if not texto_parcial:
                return JsonResponse({'error': 'Texto vacío'}, status=400)
                
            # Obtener el texto seleccionado
            texto_obj = get_object_or_404(TextoAnalizado, id=texto_id)
            
            # Leer el contenido del archivo
            try:
                with texto_obj.archivo.open('r') as archivo:
                    contenido = archivo.read()
            except:
                return JsonResponse({'error': 'Error al leer el archivo'}, status=500)
            
            # Procesar el texto
            resultado = procesar_texto_completo(contenido, n_grama, usar_fronteras)
            palabras_limpias = resultado['palabras_limpias']
            
            # Verificar si hay suficientes palabras
            if len(palabras_limpias) < n_grama:
                return JsonResponse({
                    'error': f'El texto no tiene suficientes palabras para {n_grama}-gramas. Solo tiene {len(palabras_limpias)} palabras.'
                }, status=400)
            
            # Generar n-gramas y calcular probabilidades
            ngramas_probabilidades = calcular_probabilidad_ngramas(palabras_limpias, n_grama)
            
            # Obtener el contexto (últimas n-1 palabras)
            palabras = texto_parcial.split()
            contexto = ""
            
            if n_grama > 1 and len(palabras) >= n_grama - 1:
                contexto = ' '.join(palabras[-(n_grama-1):])
            elif palabras:
                contexto = ' '.join(palabras)
            else:
                contexto = texto_parcial
            
            # Buscar sugerencias
            sugerencias = []
            for ngrama, datos in ngramas_probabilidades.items():
                if datos['contexto'] == contexto:
                    sugerencias.append({
                        'palabra': datos['palabra_objetivo'],
                        'probabilidad': datos['probabilidad'],
                        'frecuencia_ngrama': datos['frecuencia_ngrama'],
                        'frecuencia_contexto': datos['frecuencia_contexto'],
                        'ngrama_completo': ngrama
                    })
            
            # Ordenar por probabilidad descendente
            sugerencias.sort(key=lambda x: (x['probabilidad'], x['frecuencia_ngrama']), reverse=True)
            
            # Limitar a las mejores sugerencias
            sugerencias = sugerencias[:max_sugerencias]
            
            return JsonResponse({
                'sugerencias': sugerencias,
                'contexto': contexto,
                'n_grama': n_grama,
                'total_sugerencias': len(sugerencias),
                'total_ngramas_modelo': len(ngramas_probabilidades)
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def entrenar_modelo(request):
    """Vista para entrenar y visualizar el modelo de n-gramas"""
    if request.method == 'POST':
        texto_id = request.POST.get('texto_id')
        n_grama = int(request.POST.get('n_grama', 3))
        usar_fronteras = request.POST.get('fronteras', False) == 'true'
        
        # Validar n_grama
        if n_grama < 2:
            n_grama = 2
        elif n_grama > 20:
            n_grama = 20
        
        texto_obj = get_object_or_404(TextoAnalizado, id=texto_id)
        
        # Leer el contenido del archivo
        try:
            with texto_obj.archivo.open('r') as archivo:
                contenido = archivo.read()
        except:
            contenido = ""
        
        # Procesar el texto
        resultado = procesar_texto_completo(contenido, n_grama, usar_fronteras)
        palabras_limpias = resultado['palabras_limpias']
        
        # Verificar si hay suficientes palabras
        if len(palabras_limpias) < n_grama:
            return render(request, 'entrenar_modelo.html', {
                'textos': TextoAnalizado.objects.all().order_by('-fecha_subida'),
                'error': f'El texto no tiene suficientes palabras para {n_grama}-gramas. Solo tiene {len(palabras_limpias)} palabras.'
            })
        
        # Calcular probabilidades
        ngramas_probabilidades = calcular_probabilidad_ngramas(palabras_limpias, n_grama)
        
        # Preparar datos para la visualización
        ngramas_ordenados = sorted(
            ngramas_probabilidades.items(), 
            key=lambda x: x[1]['frecuencia_ngrama'], 
            reverse=True
        )[:50]
        
        return render(request, 'modelo_entrenado.html', {
            'texto': texto_obj,
            'n_grama': n_grama,
            'usar_fronteras': usar_fronteras,
            'ngramas_probabilidades': ngramas_ordenados,
            'total_ngramas': len(ngramas_probabilidades),
            'palabras_limpias': palabras_limpias,
            'max_mostrar': 50
        })
    
    textos = TextoAnalizado.objects.all().order_by('-fecha_subida')
    return render(request, 'entrenar_modelo.html', {
        'textos': textos
    })

def vista_comparacion_avanzada(request, texto_id):
    """Vista principal para comparación MLE - usa parámetros GET"""
    # Valor por defecto
    n_grama = 3
    
    # Obtener n_grama de parámetros GET
    if 'n_grama' in request.GET:
        try:
            n_grama_param = request.GET.get('n_grama', '3')
            n_grama = int(n_grama_param)
            if n_grama < 2:
                n_grama = 2
            elif n_grama > 20:
                n_grama = 20
        except (ValueError, TypeError):
            n_grama = 3
    
    # Llamar a la función de comparación
    return comparar_probabilidades(request, texto_id, n_grama)

def comparar_probabilidades(request, texto_id, n_grama=3):
    """Función helper para comparar probabilidades con/sin fronteras"""
    # Validar n_grama
    if n_grama < 2:
        n_grama = 3
    elif n_grama > 20:
        n_grama = 20
    
    texto_obj = get_object_or_404(TextoAnalizado, id=texto_id)
    
    # Leer contenido
    try:
        with texto_obj.archivo.open('r') as archivo:
            contenido = archivo.read()
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Error al leer el archivo: {str(e)}',
            'texto': texto_obj
        })
    
    try:
        # Procesar SIN fronteras
        palabras_sin_fronteras = limpiar_texto(contenido, usar_stopwords=True)
        ngramas_prob_sin = calcular_probabilidad_ngramas(palabras_sin_fronteras, n_grama) if palabras_sin_fronteras else {}
        
        # Procesar CON fronteras
        palabras_con_fronteras = limpiar_texto_con_fronteras(contenido)
        ngramas_prob_con = calcular_probabilidad_ngramas(palabras_con_fronteras, n_grama) if palabras_con_fronteras else {}
        
        # Obtener top n-gramas para comparación
        top_sin = sorted(ngramas_prob_sin.items(), 
                        key=lambda x: x[1]['frecuencia_ngrama'], 
                        reverse=True)[:15] if ngramas_prob_sin else []
        
        top_con = sorted(ngramas_prob_con.items(), 
                        key=lambda x: x[1]['frecuencia_ngrama'], 
                        reverse=True)[:15] if ngramas_prob_con else []
        
        return render(request, 'comparacion.html', {
            'texto': texto_obj,
            'n_grama': n_grama,
            'sin_fronteras': {
                'palabras': palabras_sin_fronteras,
                'total_palabras': len(palabras_sin_fronteras),
                'ngramas_probabilidades': ngramas_prob_sin,
                'top_ngramas': top_sin,
                'total_ngramas': len(ngramas_prob_sin)
            },
            'con_fronteras': {
                'palabras': palabras_con_fronteras,
                'total_palabras': len(palabras_con_fronteras),
                'ngramas_probabilidades': ngramas_prob_con,
                'top_ngramas': top_con,
                'total_ngramas': len(ngramas_prob_con)
            }
        })
    
    except Exception as e:
        return render(request, 'error.html', {
            'error': f'Error en el procesamiento: {str(e)}',
            'texto': texto_obj,
            'n_grama': n_grama
        })