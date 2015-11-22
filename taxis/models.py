from django.db import models


class TaxiPickUps(models.Model):
    vendor_id = models.IntegerField(verbose_name="Vendor Id", blank=True, null=True)
    pickup_datetime = models.DateTimeField(verbose_name="Pick Up Datetime", blank=True, null=True)
    dropoff_datetime = models.DateTimeField(verbose_name="Drop Off Datetime", blank=True, null=True)
    passenger_count = models.IntegerField(verbose_name="Passenger Count", blank=True, null=True)
    trip_distance = models.FloatField(verbose_name="Trip Distance", blank=True, null=True)
    pickup_longitude = models.DecimalField(verbose_name="Pick Up Longitude", blank=True, null=True, max_digits=17, decimal_places=14)
    pickup_latitude = models.DecimalField(verbose_name="Pick Up Latitude", blank=True, null=True, max_digits=17, decimal_places=14)
    rate_code_id = models.IntegerField(verbose_name="Rate Code", blank=True, null=True)
    store_and_fwd_flag = models.CharField(verbose_name="Store n F Flag", blank=True, null=True, max_length=2)
    dropoff_longitude = models.DecimalField(verbose_name="Drop Off Longitude", blank=True, null=True, max_digits=17, decimal_places=14)
    dropoff_latitude = models.DecimalField(verbose_name="Drop Off Longitude", blank=True, null=True, max_digits=17, decimal_places=14)
    payment_type = models.IntegerField(verbose_name="Payment Type", blank=True, null=True)
    fare_amount = models.FloatField(verbose_name="Fare Amount", blank=True, null=True)
    extra = models.FloatField(verbose_name="Extra Amount", blank=True, null=True)
    mta_tax = models.FloatField(verbose_name="MTA Tax", blank=True, null=True)
    tip_amount = models.FloatField(verbose_name="Tip Amount", blank=True, null=True)
    tolls_amount = models.FloatField(verbose_name="Tolls Amount", blank=True, null=True)
    total_amount = models.FloatField(verbose_name="Total Amount", blank=True, null=True)

