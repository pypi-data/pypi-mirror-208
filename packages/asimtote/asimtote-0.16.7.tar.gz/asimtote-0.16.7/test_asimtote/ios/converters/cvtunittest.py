# (asimtote) test_asimtote.ios.cvtunittest
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from asimtote.diff import DEBUG_CONVERT_PARAMS
from asimtote.ios import CiscoIOSConfig, CiscoIOSDiffConfig



class CiscoIOS_Convert_unittest(unittest.TestCase):
    """This class extends the standard unittest with some methods to
    make testiing Cisco IOS converters easier.
    """

    def setUp(self):
        super().__init__()

        # create starting blank 'old' and 'new' configurations for each test
        self.old_cfg = CiscoIOSConfig()
        self.new_cfg = CiscoIOSConfig()

        # create a configuration difference object to do the conversion
        self.cvt = CiscoIOSDiffConfig()


    def set_debug(self, *, dump_config=True, dump_diff=True,
                  debug_convert=DEBUG_CONVERT_PARAMS):
        """Enable several debugging options for the converter on this
        test run.  This is useful when debugging a test which is
        failing.

        The old/new configurations are printed, along with the
        calculated differences and the conversion process stages.
        """

        self.cvt.update_dump_config(dump_config)
        self.cvt.update_dump_diff(dump_diff)
        self.cvt.update_debug_convert(debug_convert)


    def _clean_config(self, cfg):
        """Cleans a configuration for comparison.  It takes a single
        large, multiline string and splits it on '\n', strips blank
        lines and leading/trailing spaces, as well as comments (lines
        beginning with '!'), returning a list of lines for direct
        comparison.
        """

        clean_cfg = []

        for line in cfg.split("\n"):
            line_stripped = line.strip()
            if line_stripped and (not line_stripped.startswith("!")):
                clean_cfg.append(line_stripped)

        return clean_cfg


    def compare(self, expected):
        """Clean and compare the 'old' and 'new' configurations with the
        supplied 'expected' configuration.  The expected configuration
        is cleaned prior to comparison so it can be more clearly
        written, using blank lines and indenting.
        """

        # get the differences, defaulting to none, and clean the output
        diffs = self.cvt.convert(self.old_cfg, self.new_cfg)[0] or ""
        convert_clean = self._clean_config(diffs)

        # clean the expected configuration and add an 'end' (which
        # convertsion will do)
        expected_clean = self._clean_config(expected)
        if expected_clean:
            expected_clean.append("end")

        self.assertEqual(convert_clean, expected_clean)
