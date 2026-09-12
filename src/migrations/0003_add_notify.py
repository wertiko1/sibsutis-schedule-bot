from tortoise import migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    operations = [
        ops.RunSQL(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS notify BOOL NOT NULL DEFAULT TRUE",
        ),
    ]
