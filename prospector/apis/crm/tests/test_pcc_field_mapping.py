import csv
import logging
import os
import typing
from collections import OrderedDict
from enum import Enum
from functools import reduce
from inspect import signature
from itertools import product
from operator import concat
from typing import Optional

import pytest
from pytest_harvest import create_results_bag_fixture

from prospector.apis.crm import crm
from prospector.apis.crm import mapping
from prospector.apps.questionnaire import enums


results_bag = create_results_bag_fixture("store", name="results_bag")


@pytest.fixture()
def logger(request):
    return logging.getLogger(request.module.__name__)


def parametrize(func, name):
    """Parametrize a function by it's siguture.

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
            matched_types = [k for k in type_values.keys() if issubclass(type_class, k)]
            assert len(matched_types) == 1, "No unique type match"
            matched_type = matched_types[0]
            values = type_values[matched_type]

        return values(type_class) if callable(values) else values

    def _unpack_types(annotation):
        origin = typing.get_origin(annotation)
        types = []
        if origin == typing.Union:
            # Resolve all types in Union
            types = reduce(concat, map(_type_values, typing.get_args(annotation)))
        else:
            __import__("pdb").set_trace()
            pass
        return types

    sig_types = {k: _unpack_types(v.annotation) for k, v in sig.parameters.items()}
    return (
        name,  # ','.join(sig.parameters),
        [
            {k: v for k, v in zip(sig.parameters, o)}
            for o in product(*[sig_types[param] for param in sig.parameters])
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

    show_none = lambda x: "None" if x is None else x

    op_field_names = [
        "option_name",
        "option_value",
        "error",
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
            option_name, option_value, error = ops

            ip_field_names = list(
                # ordered set
                dict.fromkeys(list(ips.keys()) + fields[field]["ip_field_names"])
            )

            fields[field]["ip_field_names"] = ip_field_names
            fields[field]["rows"].append(
                {
                    "option_name": option_name,
                    "option_value": show_none(option_value),
                    "error": show_none(error),
                    **{k: show_none(v) for k, v in ips.items()},
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
        answers_fields = {k: getattr(answers_record, k) for k in func_args.keys()}
        assert answers_fields == func_args

        option_name = None
        option_value = None
        error = None

        try:
            option_name, option_value = mapping_func(**answers_fields)
        except Exception as e:
            logger.error("mapping_func exception %s", str(e))
            error = str(e)
        else:
            # Test no unmapped option_names
            assert option_name is not None
            assert type(option_value) is int
        finally:
            logger.info(
                "option_name: '{}' option_value: '{}'".format(option_name, option_value)
            )
            setattr(
                results_bag,
                mapping_name,
                {
                    "path": os.path.join(
                        os.path.dirname(os.path.abspath(request.module.__file__)),
                        "generated_mapping",
                    ),
                    "mapping": ((option_name, option_value, error), func_args),
                },
            )

    return assert_mapping


@pytest.mark.django_db
@pytest.mark.parametrize(
    *parametrize(mapping.infer_pcc_primaryheatingfuel, name="func_args")
)
def test_infer_pcc_primaryheatingfuel(pcc_mapping):
    pcc_mapping("infer_pcc_primaryheatingfuel")


@pytest.mark.django_db
@pytest.mark.parametrize(
    *parametrize(mapping.infer_pcc_primaryheatingdeliverymethod, name="func_args")
)
def test_infer_pcc_primaryheatingdeliverymethod(pcc_mapping):
    pcc_mapping("infer_pcc_primaryheatingdeliverymethod")


@pytest.mark.django_db
@pytest.mark.parametrize(*parametrize(mapping.infer_pcc_boilertype, name="func_args"))
def test_infer_pcc_boilertype(pcc_mapping):
    pcc_mapping("infer_pcc_boilertype")


@pytest.mark.django_db
@pytest.mark.parametrize(
    *parametrize(mapping.infer_pcc_heatingcontrols, name="func_args")
)
def test_infer_pcc_heatingcontrols(pcc_mapping):
    pcc_mapping("infer_pcc_heatingcontrols")


@pytest.mark.django_db
@pytest.mark.parametrize(*parametrize(mapping.infer_pcc_propertytype, name="func_args"))
def test_infer_pcc_propertytype(pcc_mapping):
    pcc_mapping("infer_pcc_propertytype")


@pytest.mark.django_db
@pytest.mark.parametrize(*parametrize(mapping.infer_pcc_rooftype, name="func_args"))
def test_infer_pcc_rooftype(pcc_mapping):
    pcc_mapping("infer_pcc_rooftype")


@pytest.mark.django_db
@pytest.mark.parametrize(*parametrize(mapping.infer_pcc_walltype, name="func_args"))
def test_infer_pcc_walltype(pcc_mapping):
    pcc_mapping("infer_pcc_walltype")


@pytest.mark.django_db
@pytest.mark.parametrize(*parametrize(mapping.infer_pcc_occupierrole, name="func_args"))
def test_infer_pcc_occupierrole(pcc_mapping):
    pcc_mapping("infer_pcc_occupierrole")
