from tortoise import fields, models


class User(models.Model):
    user_id = fields.BigIntField(primary_key=True, description="Telegram User ID")
    group_id = fields.CharField(max_length=16, null=True, description="Group ID on sibsutis.ru")
    group_name = fields.CharField(max_length=32, null=True, description="Group display name")
    notify = fields.BooleanField(default=True, description="Schedule change notifications")

    class Meta:
        table = "users"
