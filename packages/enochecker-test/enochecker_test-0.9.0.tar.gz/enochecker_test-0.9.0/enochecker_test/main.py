import argparse
import logging
import os
import sys

import jsons
import pytest
import requests
from enochecker_core import CheckerInfoMessage
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def run_tests(host, port, service_address, test_methods):
    s = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
    )
    s.mount("http://", HTTPAdapter(max_retries=retry_strategy))
    r = s.get(f"http://{host}:{port}/service")
    if r.status_code != 200:
        raise Exception("Failed to get /service from checker")
    print(r.content)
    info: CheckerInfoMessage = jsons.loads(
        r.content, CheckerInfoMessage, key_transformer=jsons.KEY_TRANSFORMER_SNAKECASE
    )
    logging.info(
        "Testing service %s, flagVariants: %d, noiseVariants: %d, havocVariants: %d, exploitVariants: %d",
        info.service_name,
        info.flag_variants,
        info.noise_variants,
        info.havoc_variants,
        info.exploit_variants,
    )

    test_args = [
        f"--checker-address={host}",
        f"--checker-port={port}",
        f"--service-address={service_address}",
        f"--flag-variants={info.flag_variants}",
        f"--noise-variants={info.noise_variants}",
        f"--havoc-variants={info.havoc_variants}",
        f"--exploit-variants={info.exploit_variants}",
        "--durations=0",
        "-v",
    ]

    if test_methods is None or len(test_methods) == 0:
        test_args.append(os.path.join(os.path.dirname(__file__), "tests.py"))
    else:
        for method in test_methods:
            test_args.append(
                os.path.join(os.path.dirname(__file__), "tests.py") + "::" + method
            )

    sys.exit(pytest.main(test_args))


def main():
    parser = argparse.ArgumentParser(
        prog="enochecker_test",
        description="Utility for testing checkers that implement the enochecker API",
    )
    parser.add_argument(
        "-a",
        "--checker-address",
        help="The address on which the checker is listening (defaults to the ENOCHECKER_TEST_CHECKER_ADDRESS environment variable)",
        default=os.environ.get("ENOCHECKER_TEST_CHECKER_ADDRESS"),
    )
    parser.add_argument(
        "-p",
        "--checker-port",
        help="The port on which the checker is listening (defaults to ENOCHECKER_TEST_CHECKER_PORT environment variable)",
        choices=range(1, 65536),
        metavar="{1..65535}",
        type=int,
        default=os.environ.get("ENOCHECKER_TEST_CHECKER_PORT"),
    )
    parser.add_argument(
        "-A",
        "--service-address",
        help="The address on which the service is listening (defaults to ENOCHECKER_TEST_SERVICE_ADDRESS environment variable)",
        default=os.environ.get("ENOCHECKER_TEST_SERVICE_ADDRESS"),
    )
    parser.add_argument(
        "testcase",
        help="Specify the tests that should be run in the syntax expected by pytest, e.g. test_getflag. If no test is specified, all tests will be run.",
        nargs="*",
    )

    args = parser.parse_args()

    if not args.checker_address:
        parser.print_usage()
        raise Exception(
            "Missing enochecker address, please set the ENOCHECKER_TEST_CHECKER_ADDRESS environment variable"
        )
    if not args.checker_port:
        parser.print_usage()
        raise Exception(
            "Missing enochecker port, please set the ENOCHECKER_TEST_CHECKER_PORT environment variable"
        )
    if not args.service_address:
        parser.print_usage()
        raise Exception(
            "Missing service address, please set the ENOCHECKER_TEST_SERVICE_ADDRESS environment variable"
        )

    logging.basicConfig(level=logging.INFO)
    run_tests(
        args.checker_address, args.checker_port, args.service_address, args.testcase
    )
