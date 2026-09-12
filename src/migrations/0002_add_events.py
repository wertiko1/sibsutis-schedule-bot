from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    operations = [
        ops.CreateModel(
            name="Event",
            fields=[
                ("id", fields.IntField(primary_key=True)),
                ("user_id", fields.BigIntField()),
                ("action", fields.CharField(max_length=64)),
                ("payload", fields.CharField(max_length=128, null=True)),
                ("created_at", fields.DatetimeField(auto_now_add=True)),
            ],
            options={"table": "events", "app": "models", "pk_attr": "id"},
            bases=["Model"],
        ),
    ]
