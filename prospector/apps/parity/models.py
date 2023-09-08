from django.db import models


class ParityData(models.Model):
    org_ref = models.CharField(max_length=120)
    address_link = models.CharField(max_length=80)
    googlemaps = models.CharField(max_length=120)
    address_1 = models.CharField(max_length=120)
    address_2 = models.CharField(max_length=120)
    address_3 = models.CharField(max_length=120, blank=True, null=True)
    postcode = models.CharField(max_length=8)
    sap_score = models.DecimalField(max_digits=5, decimal_places=2)
    sap_band = models.CharField(max_length=1)
    lodged_epc_score = models.IntegerField(blank=True, null=True)
    lodged_epc_band = models.CharField(max_length=1, blank=True, null=True)
    tco2_current = models.DecimalField(max_digits=3, decimal_places=1)
    realistic_fuel_bill = models.CharField(max_length=8)
    type = models.CharField(max_length=128)
    attachment = models.CharField(max_length=128)
    construction_years = models.CharField(max_length=12)
    heated_rooms = models.IntegerField()
    wall_construction = models.CharField(max_length=128)
    wall_insulation = models.CharField(max_length=128)
    floor_construction = models.CharField(max_length=128, blank=True, null=True)
    floor_insulation = models.CharField(max_length=128, blank=True, null=True)
    roof_construction = models.CharField(max_length=128)
    roof_insulation = models.CharField(max_length=128)
    glazing = models.CharField(max_length=128)
    heating = models.CharField(max_length=128)
    boiler_efficiency = models.CharField(max_length=1)
    main_fuel = models.CharField(max_length=128)
    controls_adequacy = models.CharField(max_length=128)
    local_authority = models.CharField(max_length=128)
    ward = models.CharField(max_length=128)
    parliamentary_constituency = models.CharField(max_length=128)
    region_name = models.CharField(max_length=128)
    tenure = models.CharField(max_length=128)
    uprn = models.CharField(max_length=120, blank=True, null=True)
    lat_coordinate = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    long_coordinate = models.DecimalField(
        max_digits=10, decimal_places=8, blank=True, null=True
    )
    lower_super_output_area_code = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Parity data"
