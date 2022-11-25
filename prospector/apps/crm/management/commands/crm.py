import argparse
import csv
import json
import sys
from uuid import UUID

from django.core.management.base import BaseCommand

from prospector.apis.crm import crm
from prospector.apps.crm.tasks import crm_create
from prospector.apps.questionnaire.models import Answers

#


def get_token(session):
    return session.token


class Command(BaseCommand):
    help = "CRM API testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--token",
            action="store_true",
            default=False,
            help="Return access token response",
        )
        parser.add_argument(
            "--entity_definitions",
            action="store_true",
            default=False,
            help="Return crm entity definitions",
        )
        parser.add_argument(
            "--pick_list",
            action="store_true",
            default=False,
            help="Return crm pick list definitions",
        )
        parser.add_argument(
            "--option_set",
            action="store_true",
            default=False,
            help="Return crm pick list definitions",
        )
        parser.add_argument(
            "--picklists_csv",
            action="store_true",
            default=False,
            help="Return picklists csv",
        )

        subparsers = parser.add_subparsers(help="commands")

        create_parser = subparsers.add_parser("create", help="CRM Create")
        create_parser.set_defaults(create=True)
        create_parser.add_argument(
            "--all",
            action="store_true",
            help="CRM create for all pending completed Answers records",
        )

        def uuid4(arg_value):
            try:
                value = UUID(arg_value, version=4)
            except Exception as e:
                raise argparse.ArgumentTypeError(e)
            return str(value)

        create_parser.add_argument(
            "--answers_uuid",
            type=uuid4,
            nargs=1,
            help="CRM create for an individual Answers record (by pk)",
        )

    def crm_request(
        self, request_function, request_function_args=[], request_function_kwargs={}
    ):
        client = crm.get_client()
        session = crm.get_authorised_session(client)
        result = request_function(
            session, *request_function_args, **request_function_kwargs
        )

        return json.dumps(
            result,
            indent=4,
            sort_keys=True,
        )

    def write_picklists_csv(self):
        picklists = crm.pcc_picklists()
        fieldnames = ["LogicalName", "Label", "Value"]
        writer = csv.DictWriter(self.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for picklist, options in picklists.items():
            for label, value in options.items():
                writer.writerow(
                    {"LogicalName": picklist, "Label": label, "Value": value}
                )

    def handle(self, *args, **options):
        if "create" in options:
            if options["answers_uuid"] is not None:
                # CRM create for an individual Answers record
                # Using celery task
                answers_uuid = options["answers_uuid"][0]
                result = crm_create.delay(answers_uuid)
                for value in result.collect():
                    print(value)
            elif "all" in options:
                # CRM create for all pending completed Answers records
                __import__("pdb").set_trace()
                pass
            sys.exit(1)

        if options["token"]:
            return self.crm_request(get_token)
        elif options["entity_definitions"]:
            return self.crm_request(crm.get_pcc_fields)
        elif options["pick_list"]:
            return self.crm_request(crm.get_pcc_picklist)
        elif options["option_set"]:
            return self.crm_request(crm.get_pcc_optionset)
        elif options["picklists_csv"]:
            return self.write_picklists_csv()
        elif options["create_raw"]:
            # CRM create for an individual Answers record
            pk = options["answers_pk"][0]
            answers = Answers.objects.get(pk=pk)
            crm_data = crm.map_crm(answers)
            return self.crm_request(
                crm.create_pcc_record, request_function_args=(crm_data,)
            )
        else:
            __import__("pdb").set_trace()
