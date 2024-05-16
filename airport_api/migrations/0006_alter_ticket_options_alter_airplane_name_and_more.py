# Generated by Django 5.0.6 on 2024-05-15 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airport_api', '0005_alter_order_options_alter_ticket_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ticket',
            options={'ordering': ['seat']},
        ),
        migrations.AlterField(
            model_name='airplane',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='airplanetype',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='airport',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]