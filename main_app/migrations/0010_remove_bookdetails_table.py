from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('main_app', '0009_remove_bookdetails_constraint'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS main_app_bookdetails;",
            """
            CREATE TABLE main_app_bookdetails (
                id bigint NOT NULL PRIMARY KEY,
                book_id bigint NOT NULL
            );
            """
        ),
    ]
