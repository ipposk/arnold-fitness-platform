import boto3
import os
import json
from typing import Dict, List

class DynamoDBContextStorage:
    def __init__(self, table_name: str = None, region_name: str = None):
        self.table_name = table_name or os.environ.get("DYNAMODB_TABLE_NAME", "PentestSessions")
        self.region_name = region_name or os.environ.get("AWS_REGION", "eu-west-1")
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
        self.table = self.dynamodb.Table(self.table_name)

    def save_context(self, test_id: str, context: Dict) -> None:
        self.table.update_item(
            Key={"test_id": test_id},
            UpdateExpression="SET #ctx = :c",
            ExpressionAttributeNames={"#ctx": "context"},
            ExpressionAttributeValues={":c": json.dumps(context)}
        )

    def get_context(self, test_id: str) -> Dict:
        # Recupera il context e deserializza
        resp = self.table.get_item(Key={"test_id": test_id})
        item = resp.get("Item")
        if not item:
            return None
        context = json.loads(item["context"])
        return {"test_id": test_id, "context": context}

    def delete_context(self, test_id: str):
        # Cancella la sessione
        self.table.delete_item(Key={"test_id": test_id})
