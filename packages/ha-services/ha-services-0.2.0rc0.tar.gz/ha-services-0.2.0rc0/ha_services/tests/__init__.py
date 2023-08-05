import os
import unittest.util

from ha_services.log_setup import basic_log_setup


# Hacky way to expand the failed test output:
unittest.util._MAX_LENGTH = os.environ.get('UNITTEST_MAX_LENGTH', 300)


# Display DEBUG logs in tests:
basic_log_setup(debug=True)
