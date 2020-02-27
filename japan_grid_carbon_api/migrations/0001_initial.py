# Generated by Django 3.0.2 on 2020-02-27 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TEPCOEnergyData',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('datetime', models.DateTimeField()),
                ('kWh_demand', models.IntegerField()),
                ('kWh_nuclear', models.IntegerField()),
                ('kWh_fossil', models.IntegerField()),
                ('kWh_hydro', models.IntegerField()),
                ('kWh_geothermal', models.IntegerField()),
                ('kWh_biomass', models.IntegerField()),
                ('kWh_solar_output', models.IntegerField()),
                ('kWh_solar_throttling', models.IntegerField()),
                ('kWh_wind_output', models.IntegerField()),
                ('kWh_wind_throttling', models.IntegerField()),
                ('kWh_pumped_storage', models.IntegerField()),
                ('kWh_interconnectors', models.IntegerField()),
                ('kWh_total', models.IntegerField()),
                ('carbon_intensity', models.DecimalField(
                    max_digits=6, decimal_places=2)),
            ],
        ),
    ]
