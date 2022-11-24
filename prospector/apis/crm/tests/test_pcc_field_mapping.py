import csv
import logging
import os
import typing

from collections import OrderedDict
from itertools import product
from typing import Optional
from inspect import signature
from enum import Enum

from functools import reduce
from operator import concat

import pytest
from pytest_harvest import create_results_bag_fixture

from prospector.apis.crm import crm, mapping
from prospector.apps.questionnaire import enums


results_bag = create_results_bag_fixture("store", name="results_bag")


@pytest.fixture()
def logger(request):
    return logging.getLogger(request.module.__name__)


def parametrize(func, name):
    """ Parametrize a function by it's siguture.

    Note this will get called during pytest collection (not test runs).
    """
    sig = signature(func, follow_wrapped=True)

    def _type_values(type_class):
        values = None
        type_values = {
            bool: [True, False],
            Enum: lambda x: [*x],  # unpack the Enum options
            type(None): [None],
        }

        if typing.get_origin(type_class) == typing.Literal:
            # Handle Literals
            values = list(typing.get_args(type_class))
        else:
            matched_types = [
                k for k in type_values.keys() if issubclass(type_class, k)
            ]
            assert len(matched_types) == 1, "No unique type match"
            matched_type = matched_types[0]
            values = type_values[matched_type]

        return values(type_class) if callable(values) else values

    def _unpack_types(annotation):
        origin = typing.get_origin(annotation)
        types = []
        if origin == typing.Union:
            # Resolve all types in Union
            types = reduce(
                concat,
                map(_type_values, typing.get_args(annotation))
            )
        else:
            __import__('pdb').set_trace()
            pass
        return types


    sig_types = {
        k: _unpack_types(v.annotation)
        for k, v in sig.parameters.items()
    }
    return (
        name,  # ','.join(sig.parameters),
        [
            {k: v for k, v in zip(sig.parameters, o)}
            for o in product(
                *[
                    sig_types[param]
                    for param in sig.parameters
                ]
            )
        ],
    )


def test_get_signature():
    def my_func(
        foo: Optional[bool] = None,
        bar: Optional[bool] = None,
        baz: Optional[bool] = None,
    ):
        pass

    sig, argvalues = parametrize(my_func, name="func_args")
    assert sig == "func_args"
    assert len(argvalues) == 27

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

    option_name = mapping.infer_pcc_primaryheatingfuel(**infer_args)

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



@pytest.mark.django_db
@pytest.mark.parametrize(
    *parametrize(mapping.infer_pcc_primaryheatingdeliverymethod, name="func_args")
)
def test_infer_pcc_primaryheatingdeliverymethod(
    func_args,
    answers,
    logger,
    results_bag,
    request,
):
    answers = answers(**func_args)
    option_name = mapping.infer_pcc_primaryheatingdeliverymethod(**func_args)

    # Test no unmapped option_names
    assert option_name is not None
    # Test all option names map to option values
    option_value = crm.option_value("pcc_primaryheatingdeliverymethod", option_name)
    assert type(option_value) is int

    logger.debug(
        "option_name: '{}' option_value: '{}'".format(option_name, option_value)
    )
    results_bag.infer_pcc_primaryheatingdeliverymethod= {
        "path": os.path.join(
            os.path.dirname(os.path.abspath(request.module.__file__)),
            "generated_mapping",
        ),
        "mapping": ((option_name, option_value), func_args),
    }


@pytest.fixture()
def pcc_mapping(
    func_args,
    answers,
    logger,
    results_bag,
    request,
):
    def assert_mapping(mapping_name):
        mapping_func = getattr(mapping, mapping_name)

        # Round trip through a model instance to check our assumptions
        answers_record = answers(**func_args)
        answers_fields = {
            k: getattr(answers_record, k) for k in func_args.keys()
        }
        assert answers_fields == func_args
        try:
            option_name, option_value = mapping_func(**answers_fields)
        except Exception as e:
            logger.error("mapping_func exception %s", str(e))
            # raise e
        else:
            # Test no unmapped option_names
            # assert option_name is not None
            # assert type(option_value) is int
            logger.info(
                "option_name: '{}' option_value: '{}'".format(option_name, option_value)
            )
            setattr(results_bag, mapping_name, {
                "path": os.path.join(
                    os.path.dirname(os.path.abspath(request.module.__file__)),
                    "generated_mapping",
                ),
                "mapping": ((option_name, option_value), func_args),
            })
    return assert_mapping


@pytest.mark.django_db
@pytest.mark.parametrize(
    *parametrize(mapping.infer_pcc_boilertype, name="func_args")
)
def test_infer_pcc_boilertype(
    pcc_mapping
):
    pcc_mapping("infer_pcc_boilertype")


@pytest.mark.django_db
@pytest.mark.parametrize(
    *parametrize(mapping.infer_pcc_heatingcontrols, name="func_args")
)
def test_infer_pcc_heatingcontrols(
    pcc_mapping
):
    pcc_mapping("infer_pcc_heatingcontrols")
