# Generated by Django 3.1.6 on 2021-02-06 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Facturacion', '0003_auto_20210203_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='cabeceracomandamodel',
            name='cabeceraEstado',
            field=models.CharField(db_column='cabecera_estado', default='ABIERTO', max_length=50, verbose_name='Estado del pedido'),
        ),
    ]
