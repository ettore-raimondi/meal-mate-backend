from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "api",
            "0007_alter_foodrun_deleted_at_alter_menuitem_deleted_at_and_more",
        ),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Resturant",
            new_name="Restaurant",
        ),
        migrations.RenameField(
            model_name="foodrun",
            old_name="resturant",
            new_name="restaurant",
        ),
        migrations.RenameField(
            model_name="menuitem",
            old_name="resturant",
            new_name="restaurant",
        ),
    ]
