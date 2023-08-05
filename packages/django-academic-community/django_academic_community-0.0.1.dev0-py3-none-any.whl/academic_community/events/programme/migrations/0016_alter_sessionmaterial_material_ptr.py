import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("uploaded_material", "0001_initial"),
        ("programme", "0015_contribution_license"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sessionmaterial",
            name="material_ptr",
            field=models.OneToOneField(
                auto_created=True,
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                parent_link=True,
                primary_key=True,
                serialize=False,
                to="uploaded_material.material",
            ),
            preserve_default=False,
        ),
    ]
