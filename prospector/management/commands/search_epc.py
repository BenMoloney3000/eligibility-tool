import json
import pprint

from django.core.management.base import BaseCommand

from prospector.apis import epc
from prospector.apis.epc.epc import _process_results


class Command(BaseCommand):
    help = "EPC API lookup"

    def add_arguments(self, parser):
        parser.add_argument("postcode", nargs=1, help="Postcode")
        parser.add_argument(
            "--json",
            action="store_true",
            default=False,
            help="Return raw json response",
        )
        pass

    def handle(self, *args, **options):
        postcode = options["postcode"][0]

        results = epc.domestic_search(postcode)

        if options["json"]:
            return json.dumps(
                results.json(),
                indent=4,
                sort_keys=True,
            )
        else:
            for epc_data in _process_results(results.json()["rows"]):
                pprint.pprint(vars(epc_data), indent=4, sort_dicts=True)
