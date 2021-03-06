# Generated by Django 3.1.6 on 2021-02-03 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Facturacion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuariomodel',
            name='password',
            field=models.TextField(db_column='usu_pass', verbose_name='Contraseña del usuario'),
        ),
        migrations.AlterField(
            model_name='usuariomodel',
            name='usuarioApellido',
            field=models.CharField(db_column='usu_apellido', max_length=50, verbose_name='Apellido del usuario'),
        ),
        migrations.AlterField(
            model_name='usuariomodel',
            name='usuarioNombre',
            field=models.CharField(db_column='usu_nombre', max_length=40, verbose_name='Nombre del usuario'),
        ),
        migrations.AlterField(
            model_name='usuariomodel',
            name='usuarioTipo',
            field=models.IntegerField(choices=[(1, 'ADMINISTRADOR'), (2, 'CAJERO'), (3, 'MOZO')], db_column='usu_tipo', help_text='Tipo del usuario', verbose_name='Tipo del usuario'),
        ),
    ]
