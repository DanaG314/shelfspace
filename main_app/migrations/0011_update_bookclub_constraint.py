from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('main_app', '0010_remove_bookdetails_table'),
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE main_app_bookclub
            DROP CONSTRAINT main_app_bookclub_current_book_id_1a5c584c_fk_main_app_book_id;
            
            ALTER TABLE main_app_bookclub
            ADD CONSTRAINT main_app_bookclub_current_book_id_1a5c584c_fk_main_app_book_id
            FOREIGN KEY (current_book_id) REFERENCES main_app_book(id)
            ON DELETE SET NULL;
            """,
            """
            ALTER TABLE main_app_bookclub
            DROP CONSTRAINT main_app_bookclub_current_book_id_1a5c584c_fk_main_app_book_id;
            
            ALTER TABLE main_app_bookclub
            ADD CONSTRAINT main_app_bookclub_current_book_id_1a5c584c_fk_main_app_book_id
            FOREIGN KEY (current_book_id) REFERENCES main_app_book(id);
            """
        ),
    ]
