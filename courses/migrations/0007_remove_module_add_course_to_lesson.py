from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_alter_module_lesson_ids'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='module_ids',
        ),
        migrations.RemoveField(
            model_name='lesson',
            name='module',
        ),
        migrations.AddField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.course'),
        ),
        migrations.RemoveField(
            model_name='practiceset',
            name='module',
        ),
        migrations.AddField(
            model_name='practiceset',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='practice_sets', to='courses.course'),
        ),
        migrations.DeleteModel(
            name='Module',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='lesson_number',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ['course', 'lesson_number']},
        ),
    ] 