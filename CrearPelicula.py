import boto3
import uuid
import os
import json

def lambda_handler(event, context):
    # Entrada (json) - Mantenemos el log del evento de entrada original
    print(json.dumps(event)) 
    
    try:
        # --- LA CORRECCIÓN CLAVE ---
        # Con lambda-proxy, event['body'] viene como String plano, hay que convertirlo a diccionario
        body_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Extraemos los campos desde nuestro nuevo objeto ya parseado
        tenant_id = body_data['tenant_id']
        pelicula_datos = body_data['pelicula_datos']
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
            'body': json.dumps({
                'pelicula': pelicula,
                'response': response
            })
        }

    except Exception as e:
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
            'body': json.dumps({
                'error': type(e).__name__,
                'mensaje': f"Datos faltantes o incorrectos: {error_mensaje}"
            })
        }
