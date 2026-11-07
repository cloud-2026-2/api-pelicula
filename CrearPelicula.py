import boto3
import uuid
import os
import json

def lambda_handler(event, context):
    # Entrada (json) - Mantenemos el log del evento de entrada original
    print(json.dumps(event)) 
    
    try:
        # Intentamos procesar los datos de entrada
        tenant_id = event['body']['tenant_id']
        pelicula_datos = event['body']['pelicula_datos']
        nombre_tabla = os.environ["TABLE_NAME"]
        
        # Proceso
        uuidv4 = str(uuid.uuid4())
        pelicula = {
            'tenant_id': tenant_id,
            'uuid': uuidv4,
            'pelicula_datos': pelicula_datos
        }
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(nombre_tabla)
        response = table.put_item(Item=pelicula)
        
        # Formato estándar de log para éxito ("INFO")
        log_exito = {
            "tipo": "INFO",
            "log_datos": pelicula
        }
        print(json.dumps(log_exito)) # Imprime el JSON estandarizado
        
        # Salida exitosa de la función Lambda
        return {
            'statusCode': 200,
            'pelicula': pelicula,
            'response': response
        }
        
    except Exception as e:
        # Capturamos cualquier error (como el KeyError por 'pelicula_patos')
        error_mensaje = str(e)
        
        # Formato estándar de log para errores ("ERROR")
        log_error = {
            "tipo": "ERROR",
            "log_datos": {
                "mensaje": f"Error al procesar la solicitud: {type(e).__name__} - {error_mensaje}",
                "event_body": event.get('body', {})
            }
        }
        print(json.dumps(log_error)) # Imprime el JSON estandarizado de error
        
        # Salida controlada de la función Lambda para evitar el crash
        return {
            'statusCode': 400,
            'error': type(e).__name__,
            'mensaje': f"Datos faltantes o incorrectos en la solicitud: {error_mensaje}"
        }
