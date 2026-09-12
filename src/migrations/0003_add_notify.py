from tortoise import fields
from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    operations = [
        ops.AddField(
            model_name="User",
            field_name="notify",
            field_object=fields.BooleanField(default=True),
        ),
    ]
