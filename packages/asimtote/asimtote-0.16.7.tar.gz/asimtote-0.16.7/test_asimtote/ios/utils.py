# (asimtote) test_asimtote.ios.utils
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from asimtote.ios.utils import interface_canonicalize



class TestAsimtote_CiscoIOSUtils(unittest.TestCase):
    # misc

    def test_interface_canonicalize_caps(self):
        self.assertEqual(
            interface_canonicalize("EtherNET1/10"), "Eth1/10")

    def test_interface_canonicalize_num_single(self):
        self.assertEqual(
            interface_canonicalize("ethernet1"), "Eth1")

    def test_interface_canonicalize_num_1(self):
        self.assertEqual(
            interface_canonicalize("ethernet10"), "Eth10")

    def test_interface_canonicalize_num_2(self):
        self.assertEqual(
            interface_canonicalize("ethernet10/20"), "Eth10/20")

    def test_interface_canonicalize_num_3(self):
        self.assertEqual(
            interface_canonicalize("ethernet10/20/300"), "Eth10/20/300")


    # types

    def test_interface_canonicalize_Eth(self):
        self.assertEqual(
            interface_canonicalize("ethernet1/10"), "Eth1/10")

    def test_interface_canonicalize_Fa(self):
        self.assertEqual(
            interface_canonicalize("fastethernet1/100"), "Fa1/100")

    def test_interface_canonicalize_Fo(self):
        self.assertEqual(
            interface_canonicalize("fortygigabitethernet1/40"), "Fo1/40")

    def test_interface_canonicalize_Gi(self):
        self.assertEqual(
            interface_canonicalize("gigabitethernet1/1000"), "Gi1/1000")

    def test_interface_canonicalize_Hu(self):
        self.assertEqual(
            interface_canonicalize("hundredgigethernet1/100"), "Hu1/100")

    def test_interface_canonicalize_Lo(self):
        self.assertEqual(
            interface_canonicalize("loopback100"), "Lo100")

    def test_interface_canonicalize_Te(self):
        self.assertEqual(
            interface_canonicalize("tengigabitethernet1/10"), "Te1/10")

    def test_interface_canonicalize_Twe(self):
        self.assertEqual(
            interface_canonicalize("twentyfivegigethernet1/25"), "Twe1/25")

    def test_interface_canonicalize_Vl(self):
        self.assertEqual(
            interface_canonicalize("vlan100"), "Vl100")
