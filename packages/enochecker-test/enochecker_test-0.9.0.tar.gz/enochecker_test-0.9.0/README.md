# enochecker_test [![PyPI version](https://badge.fury.io/py/enochecker-test.svg)](https://pypi.org/project/enochecker-test) [![Build Status](https://github.com/enowars/enochecker_test/actions/workflows/pythonapp.yml/badge.svg?branch=main)](https://github.com/enowars/enochecker_test/actions/workflows/pythonapp.yml) ![Lines of code](https://tokei.rs/b1/github/enowars/enochecker_test)
Automatically test services/checker using the enochecker API

# Usage
`enochecker_test` can be used to run tests against a checker, optionally you can specify wich tests to run e.g. `enochecker_test test_getflag[0] test_exploit_per_exploit_id` will run only the first `getflag` test and all `exploit_per_exploit_id` tests.

```
usage: enochecker_test [-h] [-a CHECKER_ADDRESS] [-p {1..65535}] [-A SERVICE_ADDRESS] [testcase ...]

Utility for testing checkers that implement the enochecker API

positional arguments:
  testcase              Specify the tests that should be run in the syntax expected by pytest, e.g. test_getflag. If no test is specified, all tests will be run.

options:
  -h, --help            show this help message and exit
  -a CHECKER_ADDRESS, --checker-address CHECKER_ADDRESS
                        The address on which the checker is listening (defaults to the ENOCHECKER_TEST_CHECKER_ADDRESS environment variable)
  -p {1..65535}, --checker-port {1..65535}
                        The port on which the checker is listening (defaults to ENOCHECKER_TEST_CHECKER_PORT environment variable)
  -A SERVICE_ADDRESS, --service-address SERVICE_ADDRESS
                        The address on which the service is listening (defaults to ENOCHECKER_TEST_SERVICE_ADDRESS environment variable)
```