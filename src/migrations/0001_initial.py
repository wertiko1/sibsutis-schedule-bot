from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name="User",
            fields=[
                ("user_id", fields.BigIntField(primary_key=True)),
                ("group_id", fields.CharField(max_length=16, null=True)),
                ("group_name", fields.CharField(max_length=32, null=True)),
            ],
            options={"table": "users", "app": "models", "pk_attr": "user_id"},
            bases=["Model"],
        ),
    ]
