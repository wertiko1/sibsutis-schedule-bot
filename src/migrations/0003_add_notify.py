from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    operations = [
        ops.AddField(
            model_name="User",
            name="notify",
            field=fields.BooleanField(default=True),
        ),
    ]
