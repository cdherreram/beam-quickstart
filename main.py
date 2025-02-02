#  Copyright 2021 Israel Herraiz
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import apache_beam as beam
import argparse

from apache_beam.options.pipeline_options import PipelineOptions

def sanitizar_palabra(palabra):
    para_quitar = [',', '.', '-', ':', ' ', "'", '"']

    for simbolo in para_quitar:
        palabra = palabra.replace(simbolo, '')

    palabra = palabra.lower()
    palabra = palabra.replace("á", "a")
    palabra = palabra.replace("é", "e")
    palabra = palabra.replace("í", "i")
    palabra = palabra.replace("ó", "o")
    palabra = palabra.replace("ú", "u")

    return palabra

def main():
    parser = argparse.ArgumentParser(description="Nuestro primer pipeline")
    parser.add_argument("--entrada", help="Fichero de entrada")
    parser.add_argument("--salida", help="Fichero de salida")
    parser.add_argument("--n_palabras", type=int, help="Número de palabras en la salida")

    our_args, beam_args = parser.parse_known_args()

    run_pipeline(our_args, beam_args)

def run_pipeline(custom_args, beam_args):
    entrada = custom_args.entrada
    salida = custom_args.salida
    n_palabras = custom_args.n_palabras    
    opts = PipelineOptions(beam_args)

    with beam.Pipeline(options = opts) as p:
        # Extraer cada línea 
        lineas: PCollection[str] = p | "Leer entrada" >> beam.io.ReadFromText(entrada)
        palabras  = lineas | "Pasamos a palabras" >> beam.FlatMap(lambda l:l.split())
        limpiadas = palabras | "Limpiar palabras" >> beam.Map(sanitizar_palabra)
        contadas: PCollection[Tuple[str,int]] = limpiadas | "Contamos" >> beam.combiners.Count.PerElement()
        palabras_top_lista: PCollection[Tuple[str,int]] = contadas | "Ranking" >> beam.combiners.Top.Of(n_palabras, key=lambda kv:kv[1])
        palabras_top = palabras_top_lista | "Desenvuelve lista" >> beam.FlatMap(lambda x: x)
        formateado: PCollection[str] = palabras_top | "Formatear" >> beam.Map(lambda kv: '%s,%d' % (kv[0],kv[1]))
        #formateado | beam.Map(print) #Si queremos imprimir
        formateado | "Escribir salida" >> beam.io.WriteToText(salida,)

if __name__ == "__main__":
    main()