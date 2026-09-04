from tortoise import fields, models


class Event(models.Model):
    id = fields.IntField(primary_key=True)
    user_id = fields.BigIntField(description="Telegram User ID")
    action = fields.CharField(max_length=64, description="Action name (command or callback)")
    payload = fields.CharField(max_length=128, null=True, description="Extra data")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "events"
