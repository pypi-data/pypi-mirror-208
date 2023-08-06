# (asimtote) test_asimtote.ios.config.other
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from asimtote.ios import CiscoIOSConfig



class TestAsimtote_CiscoIOS_Config_Other(unittest.TestCase):
    def setUp(self):
        # create a starting blank configuration for each test
        self.cfg = CiscoIOSConfig()


    # -------------------------------------------------------------------------
    # hostname ...
    # -------------------------------------------------------------------------


    def test_Hostname(self):
        self.cfg.parse_str("""
hostname TestRouter
""")

        self.assertEqual(self.cfg, {
            "hostname": "TestRouter"
        })


    # -------------------------------------------------------------------------
    # [no] spanning-tree ...
    # -------------------------------------------------------------------------


    def test_NoSTP(self):
        self.cfg.parse_str("""
no spanning-tree vlan 100
no spanning-tree vlan 200
""")

        self.assertEqual(self.cfg, {
            "no-spanning-tree-vlan": { 100, 200 }
        })


    def test_STPPri(self):
        self.cfg.parse_str("""
spanning-tree vlan 100 priority 8192
spanning-tree vlan 200 priority 16384
""")

        self.assertEqual(self.cfg, {
            "spanning-tree-vlan-priority": {
                100: 8192,
                200: 16384
            }
        })


    # -------------------------------------------------------------------------
    # track ...
    # -------------------------------------------------------------------------


    def test_TrackModify_NoExist(self):
        with self.assertRaises(KeyError):
            self.cfg.parse_str("""
track 100
""", explain_exception=False)


    def test_TrackModify_Exist(self):
        d = {
            "track": {
                100: {
                    "type": "interface",
                    "interface": "Loopback100",
                    "capability": "line-protocol"
                }
            }
        }

        self.cfg.update(d)

        self.cfg.parse_str("""
track 100
""")

        self.assertEqual(self.cfg, d)


    def test_TrackInt(self):
        self.cfg.parse_str("""
track 100 interface Loopback100 line-protocol
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "interface",
                    "interface": {
                        "interface": "Lo100",
                        "capability": "line-protocol"
                    }
                }
            }
        })


    def test_TrackList(self):
        self.cfg.parse_str("""
track 100 list boolean and
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "list",
                    "list": {
                        "type": "boolean",
                        "op": "and"
                    }
                }
            }
        })


    def test_TrackRoute_CIDR(self):
        self.cfg.parse_str("""
track 100 ip route 10.0.0.0/16 reachability
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "route",
                    "route": {
                        "proto": "ip",
                        "net": "10.0.0.0/16",
                        "measure": "reachability"
                    }
                }
            }
        })


    def test_TrackRoute_NetMask(self):
        self.cfg.parse_str("""
track 100 ip route 10.0.0.0 255.255.0.0 reachability
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "route",
                    "route": {
                        "proto": "ip",
                        "net": "10.0.0.0/16",
                        "measure": "reachability"
                    }
                }
            }
        })


    def test_Track_Delay(self):
        self.cfg.parse_str("""
track 100 list boolean and
 delay up 10 down 20
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "list",
                    "list": {
                        "type": "boolean",
                        "op": "and"
                    },
                    "delay": {
                            "up": 10,
                            "down": 20
                    }
                }
            }
        })


    def test_Track_IPVRF_CIDR(self):
        self.cfg.parse_str("""
track 100 ip route 10.0.0.0/8 reachability
 ip vrf TestVRF
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "route",
                    "route": {
                        "proto": "ip",
                        "net": "10.0.0.0/8",
                        "measure": "reachability"
                    },
                    "ip-vrf": "TestVRF"
                }
            }
        })


    def test_Track_IPVRF_NetMask(self):
        self.cfg.parse_str("""
track 100 ip route 10.0.0.0 255.0.0.0 reachability
 ip vrf TestVRF
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "route",
                    "route": {
                        "proto": "ip",
                        "net": "10.0.0.0/8",
                        "measure": "reachability"
                    },
                    "ip-vrf": "TestVRF"
                }
            }
        })


    def test_Track_IPv6VRF(self):
        self.cfg.parse_str("""
track 100 ipv6 route 100::/64 reachability
 ipv6 vrf TestVRF
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "route",
                    "route": {
                        "proto": "ipv6",
                        "net": "100::/64",
                        "measure": "reachability"
                    },
                    "ipv6-vrf": "TestVRF"
                }
            }
        })


    def test_Track_Obj(self):
        self.cfg.parse_str("""
track 100 list boolean and
 object 210
 object 220
""")

        self.assertEqual(self.cfg, {
            "track": {
                100: {
                    "type": "list",
                    "list": {
                        "type": "boolean",
                        "op": "and",
                    },
                    "object": { 210, 220 }
                }
            }
        })


    # -------------------------------------------------------------------------
    # vlan ...
    # -------------------------------------------------------------------------


    def test_VLAN(self):
        self.cfg.parse_str("""
vlan 100
""")

        self.assertEqual(self.cfg, {
            "vlan": {
                100: {
                    "exists": True
                }
            }
        })


    def test_VLAN_Name(self):
        self.cfg.parse_str("""
vlan 100
 name TestVLAN
""")

        self.assertEqual(self.cfg, {
            "vlan": {
                100: {
                    "exists": True,
                    "name": "TestVLAN"
                }
            }
        })


    # -------------------------------------------------------------------------
    # vrf ...
    # -------------------------------------------------------------------------


    def test_VRF(self):
        self.cfg.parse_str("""
vrf definition TestVRF
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {}
            }
        })


    def test_VRF_RD_ASN(self):
        self.cfg.parse_str("""
vrf definition TestVRF
 rd 100:200
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {
                    "rd": "100:200"
                }
            }
        })


    def test_VRF_RD_IP(self):
        self.cfg.parse_str("""
vrf definition TestVRF
 rd 10.1.2.3:200
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {
                    "rd": "10.1.2.3:200"
                }
            }
        })


    def test_VRF_RT(self):
        self.cfg.parse_str("""
vrf definition TestVRF
 route-target import 10.1.2.0:200
 route-target export 100:200
 route-target both 300:200
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {
                    "route-target": {
                        "import": { "10.1.2.0:200", "300:200" },
                        "export": { "100:200", "300:200" }
                    }
                }
            }
        })


    def test_VRF_AF_Plain(self):
        self.cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {
                    "address-family": {
                        "ipv4": {}
                    }
                }
            }
        })


    def test_VRF_AF_Uni(self):
        self.cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4 unicast
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {
                    "address-family": {
                        "ipv4": {}
                    }
                }
            }
        })


    def test_VRF_AF_RT(self):
        self.cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 10.1.2.0:200
  route-target export 100:200
  route-target both 300:200
""")

        self.assertEqual(self.cfg, {
            "vrf": {
                "TestVRF": {
                    "address-family": {
                        "ipv4": {
                            "route-target": {
                                "import": { "10.1.2.0:200", "300:200" },
                                "export": { "100:200", "300:200" }
                            }
                        }
                    }
                }
            }
        })
