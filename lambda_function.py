import json
from decimal import Decimal
import boto3 # type: ignore 
from botocore.exceptions import ClientError # type: ignore

# Traductor de Decimal a JSON (Indispensable para DynamoDB)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TablaInventario') 

def lambda_handler(event, context):
    route_key = event.get('routeKey', '')
    status_code = 200
    response_body = ""
    headers = {"Content-Type": "application/json"}

    try:
        # --- (GET) ---
        if route_key == "GET /productos":
            scan_result = table.scan()
            response_body = scan_result.get('Items', [])

        # ---(POST) ---
        elif route_key == "POST /productos":
            body = json.loads(event.get('body', '{}'))
            table.put_item(Item=body)
            response_body = f"Éxito: Producto {body['id_producto']} procesado."

        # --- EDITAR PARCIAL (PUT) ---
        elif route_key == "PUT /productos":
            body = json.loads(event.get('body', '{}'))
            # Actualizamos solo la cantidad del producto específico
            table.update_item(
                Key={'id_producto': body['id_producto']},
                UpdateExpression="set cantidad = :c, nombre = :n",
                ExpressionAttributeValues={':c': body['cantidad'], ':n': body['nombre']}
            )
            response_body = f"Éxito: Producto {body['id_producto']} actualizado."

        # --- (DELETE)
        elif route_key == "DELETE /productos":
            body = json.loads(event.get('body', '{}'))
            table.delete_item(Key={'id_producto': body['id_producto']})
            response_body = f"Éxito: Producto {body['id_producto']} eliminado."

        else:
            status_code = 404
            response_body = "Ruta no encontrada"

    except Exception as e:
        status_code = 400
        response_body = str(e)

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body, cls=DecimalEncoder),
        'headers': headers
    }