# (asimtote) tests.ios.config.lists
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from asimtote.ios import CiscoIOSConfig



class TestAsimtote_CiscoIOS_Config_Lists(unittest.TestCase):
    def setUp(self):
        # create a starting blank configuration for each test
        self.cfg = CiscoIOSConfig()


    # -------------------------------------------------------------------------
    # ip access-list standard ...
    # -------------------------------------------------------------------------


    def test_ACLStdRule_host(self):
        # check rules are canonicalised to remove 'host'
        self.cfg.parse_str("""
access-list 10 permit host 10.0.0.1
access-list 10 permit 20.0.0.0 0.0.255.255
access-list 10 deny 30.0.0.0 0.0.0.127
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-standard": {
                "10": [
                    "permit 10.0.0.1",
                    "permit 20.0.0.0 0.0.255.255",
                    "deny 30.0.0.0 0.0.0.127"
                ]
            }
        })


    def test_IPACL_Std_num(self):
        # check standard ACLs in 'ip access-list standard' form with a
        # number and rules are canonicalised to remove 'host'
        self.cfg.parse_str("""
ip access-list standard 10
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.255.255
 deny 30.0.0.0 0.0.0.127
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-standard": {
                "10": [
                    "permit 10.0.0.1",
                    "permit 20.0.0.0 0.0.255.255",
                    "deny 30.0.0.0 0.0.0.127"
                ]
            }
        })


    def test_IPACL_Std_mix(self):
        # check standard ACLs can be built in mixed form
        self.cfg.parse_str("""
access-list 10 permit host 10.0.0.1
!
ip access-list standard 10
 permit 20.0.0.0 0.0.255.255
 deny 30.0.0.0 0.0.0.127
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-standard": {
                "10": [
                    "permit 10.0.0.1",
                    "permit 20.0.0.0 0.0.255.255",
                    "deny 30.0.0.0 0.0.0.127"
                ]
            }
        })


    def test_IPACL_Std_seq(self):
        self.cfg.parse_str("""
ip access-list standard TestACL
 20 permit 20.0.0.0 0.0.0.255
 10 permit 10.0.0.0 0.0.0.255
 30 permit 30.0.0.0 0.0.0.255
 permit 40.0.0.0 0.0.0.255
 100 permit 50.0.0.0 0.0.0.255
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-standard": {
                "TestACL": [
                    "permit 10.0.0.0 0.0.0.255",
                    "permit 20.0.0.0 0.0.0.255",
                    "permit 30.0.0.0 0.0.0.255",
                    "permit 40.0.0.0 0.0.0.255",
                    "permit 50.0.0.0 0.0.0.255"
                ]
            }
        })


    def test_IPACL_Std_name(self):
        # check standard ACLs in 'ip access-list standard' form
        self.cfg.parse_str("""
ip access-list standard TestACL
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.255.255
 deny 30.0.0.0 0.0.0.127
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-standard": {
                "TestACL": [
                    "permit 10.0.0.1",
                    "permit 20.0.0.0 0.0.255.255",
                    "deny 30.0.0.0 0.0.0.127"
                ]
            }
        })


    # -------------------------------------------------------------------------
    # ip access-list extended ...
    # -------------------------------------------------------------------------


    def test_ACLExtRule_ip(self):
        self.cfg.parse_str("""
access-list 100 permit ip any any
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "100": [
                    "permit ip any any"
                ]
            }
        })


    def test_ACLExtRule_icmp(self):
        self.cfg.parse_str("""
access-list 100 permit icmp any 10.0.0.0 0.0.0.255 echo
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "100": [
                    "permit icmp any 10.0.0.0 0.0.0.255 echo"
                ]
            }
        })


    def test_ACLExtRule_tcp(self):
        self.cfg.parse_str("""
access-list 100 permit tcp any eq 100 host 10.0.0.1 range 200 300
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "100": [
                    "permit tcp any eq 100 host 10.0.0.1 range 200 300"
                ]
            }
        })


    def test_ACLExtRule_udp(self):
        self.cfg.parse_str("""
access-list 100 permit udp host 10.0.0.1 range 200 300 20.0.0.0 0.0.0.255 gt 400
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "100": [
                    "permit udp host 10.0.0.1 range 200 300 20.0.0.0 0.0.0.255 gt 400"
                ]
            }
        })


    def test_ACLExtRule_list(self):
        self.cfg.parse_str("""
access-list 100 permit ip host 10.0.0.1 any
access-list 100 permit ip any host 20.0.0.1
access-list 100 deny ip 30.0.0.0 0.0.0.255 40.0.0.0 0.0.0.255
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "100": [
                    "permit ip host 10.0.0.1 any",
                    "permit ip any host 20.0.0.1",
                    "deny ip 30.0.0.0 0.0.0.255 40.0.0.0 0.0.0.255"
                ]
            }
        })


    def test_IPACL_Ext_name(self):
        # check standard ACLs in 'ip access-list standard' form with a
        # number and rules are canonicalised to remove 'host'
        self.cfg.parse_str("""
ip access-list extended TestACL
 permit ip host 10.0.0.1 any
 permit ip any host 20.0.0.1
 deny ip 30.0.0.0 0.0.0.255 40.0.0.0 0.0.0.255
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "TestACL": [
                    "permit ip host 10.0.0.1 any",
                    "permit ip any host 20.0.0.1",
                    "deny ip 30.0.0.0 0.0.0.255 40.0.0.0 0.0.0.255"
                ]
            }
        })


    def test_IPACL_Ext_seq(self):
        # check standard ACLs in 'ip access-list standard' form with a
        # number and rules are canonicalised to remove 'host'
        self.cfg.parse_str("""
ip access-list extended TestACL
 20 permit ip host 20.0.0.1 any
 permit ip host 30.0.0.1 any
 10 permit ip host 10.0.0.1 any
 40 permit ip host 40.0.0.1 any
 100 permit ip host 50.0.0.1 any
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "TestACL": [
                    "permit ip host 10.0.0.1 any",
                    "permit ip host 20.0.0.1 any",
                    "permit ip host 30.0.0.1 any",
                    "permit ip host 40.0.0.1 any",
                    "permit ip host 50.0.0.1 any"
                ]
            }
        })


    def test_IPACL_Ext_mix(self):
        # check extended ACLs can be built in mixed form
        self.cfg.parse_str("""
access-list 100 permit ip host 10.0.0.1 any
!
ip access-list extended 100
 permit ip any host 20.0.0.1
 deny ip 30.0.0.0 0.0.0.255 40.0.0.0 0.0.0.255
""")

        self.assertEqual(self.cfg, {
            "ip-access-list-extended": {
                "100": [
                    "permit ip host 10.0.0.1 any",
                    "permit ip any host 20.0.0.1",
                    "deny ip 30.0.0.0 0.0.0.255 40.0.0.0 0.0.0.255"
                ]
            }
        })


    # -------------------------------------------------------------------------
    # ipv6 access-list ...
    # -------------------------------------------------------------------------


    def test_IPv6ACL_ip(self):
        self.cfg.parse_str("""
ipv6 access-list TestACL
 permit ipv6 any any
""")

        self.assertEqual(self.cfg, {
            "ipv6-access-list": {
                "TestACL": [
                    "permit ipv6 any any"
                ]
            }
        })


    def test_IPv6ACL_icmp(self):
        self.cfg.parse_str("""
ipv6 access-list TestACL
 permit icmp any any
""")

        self.assertEqual(self.cfg, {
            "ipv6-access-list": {
                "TestACL": [
                    "permit icmp any any"
                ]
            }
        })


    def test_IPv6ACL_tcp(self):
        self.cfg.parse_str("""
ipv6 access-list TestACL
 permit tcp any any
""")

        self.assertEqual(self.cfg, {
            "ipv6-access-list": {
                "TestACL": [
                    "permit tcp any any"
                ]
            }
        })


    def test_IPv6ACL_udp(self):
        self.cfg.parse_str("""
ipv6 access-list TestACL
 permit udp any any
""")

        self.assertEqual(self.cfg, {
            "ipv6-access-list": {
                "TestACL": [
                    "permit udp any any"
                ]
            }
        })


    def test_IPv6ACL_list(self):
        self.cfg.parse_str("""
ipv6 access-list TestACL
 permit ipv6 host 10::1 any
 permit ipv6 any host 20::1
 deny ipv6 30::/64 40::/32
""")

        self.assertEqual(self.cfg, {
            "ipv6-access-list": {
                "TestACL": [
                    "permit ipv6 host 10::1 any",
                    "permit ipv6 any host 20::1",
                    "deny ipv6 30::/64 40::/32"
                ]
            }
        })


    def test_IPv6ACL_seq(self):
        self.cfg.parse_str("""
ipv6 access-list TestACL
 sequence 20 permit ipv6 host 20::1 any
 permit ipv6 host 30::1 any
 sequence 10 permit ipv6 host 10::1 any
 sequence 40 permit ipv6 host 40::1 any
 sequence 100 permit ipv6 host 50::1 any
""")

        self.assertEqual(self.cfg, {
            "ipv6-access-list": {
                "TestACL": [
                    "permit ipv6 host 10::1 any",
                    "permit ipv6 host 20::1 any",
                    "permit ipv6 host 30::1 any",
                    "permit ipv6 host 40::1 any",
                    "permit ipv6 host 50::1 any"
                ]
            }
        })


    # -------------------------------------------------------------------------
    # ip as-path access-list ...
    # -------------------------------------------------------------------------


    def test_IPASPathACL_list(self):
        self.cfg.parse_str("""
ip as-path access-list 100 permit ^10_
ip as-path access-list 100 deny _20$
""")

        self.assertEqual(self.cfg, {
            "ip-as-path-access-list": {
                100: [
                    ("permit", "^10_"),
                    ("deny", "_20$")
                ]
            }
        })


    # -------------------------------------------------------------------------
    # ip prefix-list ...
    # -------------------------------------------------------------------------


    def test_IPPfxList_simple(self):
        self.cfg.parse_str("""
ip prefix-list TestPfxList permit 10.0.0.0/8
""")

        self.assertEqual(self.cfg, {
            "ip-prefix-list": {
                "TestPfxList": [
                    "permit 10.0.0.0/8"
                ]
            }
        })


    def test_IPPfxList_le(self):
        self.cfg.parse_str("""
ip prefix-list TestPfxList permit 10.0.0.0/8 le 24
""")

        self.assertEqual(self.cfg, {
            "ip-prefix-list": {
                "TestPfxList": [
                    "permit 10.0.0.0/8 le 24"
                ]
            }
        })


    def test_IPPfxList_all(self):
        self.cfg.parse_str("""
ip prefix-list TestPfxList permit 0.0.0.0/0 le 32
""")

        self.assertEqual(self.cfg, {
            "ip-prefix-list": {
                "TestPfxList": [
                    "permit 0.0.0.0/0 le 32"
                ]
            }
        })


    def test_IPPfxList_list(self):
        self.cfg.parse_str("""
ip prefix-list TestPfxList permit 10.0.0.0/8
ip prefix-list TestPfxList deny 20.0.0.0/16
""")

        self.assertEqual(self.cfg, {
            "ip-prefix-list": {
                "TestPfxList": [
                    "permit 10.0.0.0/8",
                    "deny 20.0.0.0/16"
                ]
            }
        })


    def test_IPPfxList_seq(self):
        self.cfg.parse_str("""
ip prefix-list TestPfxList seq 20 permit 20.0.0.0/8
ip prefix-list TestPfxList seq 10 permit 10.0.0.0/8
ip prefix-list TestPfxList deny 30.0.0.0/8
ip prefix-list TestPfxList seq 100 permit 40.0.0.0/8
""")

        self.assertEqual(self.cfg, {
            "ip-prefix-list": {
                "TestPfxList": [
                    "permit 10.0.0.0/8",
                    "permit 20.0.0.0/8",
                    "deny 30.0.0.0/8",
                    "permit 40.0.0.0/8"
                ]
            }
        })


    # -------------------------------------------------------------------------
    # ipv6 prefix-list ...
    # -------------------------------------------------------------------------


    def test_IPv6PfxList_simple(self):
        self.cfg.parse_str("""
ipv6 prefix-list TestPfxList permit 10::/48
""")

        self.assertEqual(self.cfg, {
            "ipv6-prefix-list": {
                "TestPfxList": [
                    "permit 10::/48"
                ]
            }
        })


    def test_IPv6PfxList_le(self):
        self.cfg.parse_str("""
ipv6 prefix-list TestPfxList permit 10::/48 le 64
""")

        self.assertEqual(self.cfg, {
            "ipv6-prefix-list": {
                "TestPfxList": [
                    "permit 10::/48 le 64"
                ]
            }
        })


    def test_IPv6PfxList_all(self):
        self.cfg.parse_str("""
ipv6 prefix-list TestPfxList permit ::/0 le 128
""")

        self.assertEqual(self.cfg, {
            "ipv6-prefix-list": {
                "TestPfxList": [
                    "permit ::/0 le 128"
                ]
            }
        })


    def test_IPv6PfxList_list(self):
        self.cfg.parse_str("""
ipv6 prefix-list TestPfxList permit 10::/48
ipv6 prefix-list TestPfxList permit 20::/48
""")

        self.assertEqual(self.cfg, {
            "ipv6-prefix-list": {
                "TestPfxList": [
                    "permit 10::/48",
                    "permit 20::/48"
                ]
            }
        })


    def test_IPv6PfxList_seq(self):
        self.cfg.parse_str("""
ipv6 prefix-list TestPfxList seq 20 permit 20::/48
ipv6 prefix-list TestPfxList seq 10 permit 10::/48
ipv6 prefix-list TestPfxList permit 30::/48
ipv6 prefix-list TestPfxList seq 100 permit 40::/48
""")

        self.assertEqual(self.cfg, {
            "ipv6-prefix-list": {
                "TestPfxList": [
                    "permit 10::/48",
                    "permit 20::/48",
                    "permit 30::/48",
                    "permit 40::/48"
                ]
            }
        })
