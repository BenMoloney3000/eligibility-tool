import csv
import logging
import os
from collections import OrderedDict
from itertools import product

import pytest
from pytest_harvest import create_results_bag_fixture

from prospector.apis.crm import crm
from prospector.apps.questionnaire import enums


results_bag = create_results_bag_fixture("store", name="results_bag")


@pytest.fixture()
def logger(request):
    return logging.getLogger(request.module.__name__)


def _write_field_mapping_csv(path, field_names, rows):
    with open(path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


@pytest.fixture(scope="session", autouse=True)
def store(request):
    # setup: init the store
    store = OrderedDict()
    yield store

    # teardown: here you can collect all
    if "results_bag" not in store:
        return

    # collect test results
    # TODO: maybe check the type of result (currently we presume everything the
    # a lookup field.

    op_field_names = [
        "option_name",
        "option_value",
    ]

    fields = {}
    for test, results in dict(store["results_bag"]).items():
        rows = []
        for field, results in results.items():
            if field not in fields:
                fields[field] = {
                    "ip_field_names": [],
                    "op_field_names": op_field_names,
                    "base_path": results["path"],
                    "rows": [],
                }

            ops, ips = results["mapping"]
            option_name, option_value = ops

            ip_field_names = list(
                # ordered set
                dict.fromkeys(list(ips.keys()) + fields[field]["ip_field_names"])
            )

            fields[field]["ip_field_names"] = ip_field_names
            fields[field]["rows"].append(
                {
                    "option_name": option_name,
                    "option_value": option_value,
                    **ips,
                }
            )

    # write field mapping results to csv files
    for crm_field_name, field_mapping in fields.items():
        field_names = [
            *field_mapping["ip_field_names"],
            *field_mapping["op_field_names"],
        ]
        rows = field_mapping["rows"]
        print(crm_field_name)
        path = os.path.join(
            field_mapping["base_path"],
            "{}.csv".format(crm_field_name),
        )

        _write_field_mapping_csv(path, field_names, rows)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "on_mains_gas,storage_heaters_present,other_heating_fuel,expected",
    [
        (*v, None)
        for v in product(  # TODO: expected not used
            (None, True, False),
            (None, True, False),
            ("", *enums.NonGasFuel),
        )
    ],
)
def test_infer_pcc_primaryheatingfuel(
    answers,
    on_mains_gas,
    storage_heaters_present,
    other_heating_fuel,
    expected,
    logger,
    results_bag,
    request,
):
    answers = answers(
        on_mains_gas=on_mains_gas,
        storage_heaters_present=storage_heaters_present,
        other_heating_fuel=other_heating_fuel,
    )

    infer_args = {
        "on_mains_gas": answers.on_mains_gas,
        "storage_heaters_present": answers.storage_heaters_present,
        "other_heating_fuel": answers.other_heating_fuel,
    }

    option_name = crm.infer_pcc_primaryheatingfuel(**infer_args)

    # Test no unmapped option_names
    assert option_name is not None
    # Test all option names map to option values
    option_value = crm.option_value("pcc_primaryheatingfuel", option_name)
    assert type(option_value) is int

    logger.debug(
        "option_name: '{}' option_value: '{}'".format(option_name, option_value)
    )
    results_bag.infer_pcc_primaryheatingfuel = {
        "path": os.path.join(
            os.path.dirname(os.path.abspath(request.module.__file__)),
            "generated_mapping",
        ),
        "mapping": ((option_name, option_value), infer_args),
    }
