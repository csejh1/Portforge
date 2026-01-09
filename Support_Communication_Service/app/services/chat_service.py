import datetime
import uuid
from typing import Any, Dict, List

from botocore.exceptions import ClientError

from app.core.database import aws_manager
from app.core.config import settings

TEAM_CHATS_TABLE = "team_chats"
CHAT_ROOMS_TABLE = "chat_rooms"


def _iso_now() -> str:
    return datetime.datetime.utcnow().isoformat()


def _ddb_client_ctx():
    """
    aioboto3 client context factory (async with 사용).
    """
    return aws_manager.session.client(
        "dynamodb",
        endpoint_url=settings.DDB_ENDPOINT_URL or "http://localhost:8089",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or "dummy",
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or "dummy",
    )


async def save_chat_message(project_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save a chat message to DynamoDB with all required fields.
    Ensures: project_id, timestamp (sort key), message_id, user_id, message, created_at.
    """
    now = _iso_now()
    item = {
        "project_id": {"N": str(project_id)},
        "timestamp": {"S": payload.get("timestamp") or now},
        "message_id": {"S": payload.get("message_id") or str(uuid.uuid4())},
        "user_id": {"S": str(payload.get("user_id") or "unknown")},
        "message": {"S": payload.get("message") or payload.get("text") or ""},
        "created_at": {"S": payload.get("created_at") or now},
    }

    async with _ddb_client_ctx() as client:
        try:
            await client.put_item(TableName=TEAM_CHATS_TABLE, Item=item)
        except ClientError as e:
            raise e

    # Return a simplified dict for API responses
    return {
        "message_id": item["message_id"]["S"],
        "project_id": project_id,
        "user_id": item["user_id"]["S"],
        "message": item["message"]["S"],
        "timestamp": item["timestamp"]["S"],
        "created_at": item["created_at"]["S"],
    }


async def list_chat_messages(project_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch chat messages for a project ordered by timestamp (ascending).
    """
    async with _ddb_client_ctx() as client:
        resp = await client.query(
            TableName=TEAM_CHATS_TABLE,
            KeyConditionExpression="project_id = :pid",
            ExpressionAttributeValues={":pid": {"N": str(project_id)}},
            Limit=limit,
            ScanIndexForward=True,
        )
    items = resp.get("Items", [])
    parsed: List[Dict[str, Any]] = []
    for it in items:
        parsed.append(
            {
                "message_id": it.get("message_id", {}).get("S"),
                "project_id": project_id,
                "user_id": it.get("user_id", {}).get("S"),
                "message": it.get("message", {}).get("S"),
                "timestamp": it.get("timestamp", {}).get("S"),
                "created_at": it.get("created_at", {}).get("S"),
            }
        )
    return parsed


async def upsert_chat_room(user_id: str, room_id: int, updated_at: str | None = None) -> None:
    """
    Ensure chat_rooms_ddb contains user_id, room_id, updated_at.
    """
    async with _ddb_client_ctx() as client:
        await client.put_item(
            TableName=CHAT_ROOMS_TABLE,
            Item={
                "user_id": {"S": user_id},
                "room_id": {"N": str(room_id)},
                "updated_at": {"S": updated_at or _iso_now()},
            },
        )
