from .models import ParityData


def get_addresses_for_postcode(postcode: ParityData.postcode):
    db_objects = ParityData.objects.filter(postcode=postcode)
    return db_objects


# For testing, use runscript command
def run():
    print(get_addresses_for_postcode("PL1 3JP"))
