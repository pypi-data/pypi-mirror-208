# (asimtote) test_asimtote.ios.config.router
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from asimtote.ios import CiscoIOSConfig, VRF_GLOBAL



class TestAsimtote_CiscoIOS_Config_Router(unittest.TestCase):
    def setUp(self):
        # create a starting blank configuration for each test
        self.cfg = CiscoIOSConfig()


    # -------------------------------------------------------------------------
    # ip[v6] route ...
    # -------------------------------------------------------------------------


    def test_IPRoute_int(self):
        self.cfg.parse_str("""
ip route 10.1.0.0 255.255.255.0 Eth1/1.100
""")

        self.assertEqual(self.cfg, {
            "ip-route": {
                None: {
                    "10.1.0.0/24": {
                        "Eth1/1.100 -": {
                            "interface": "Eth1/1.100"
                        }
                    }
                }
            }
        })


    def test_IPRoute_ip(self):
        self.cfg.parse_str("""
ip route 10.1.0.0 255.255.255.0 10.2.0.1
""")

        self.assertEqual(self.cfg, {
            "ip-route": {
                None: {
                    "10.1.0.0/24": {
                        "- 10.2.0.1": {
                            "router": "10.2.0.1"
                        }
                    }
                }
            }
        })


    def test_IPRoute_int_ip(self):
        self.cfg.parse_str("""
ip route 10.1.0.0 255.255.255.0 Vlan100 10.2.0.1
""")

        self.assertEqual(self.cfg, {
            "ip-route": {
                None: {
                    "10.1.0.0/24": {
                        "Vl100 10.2.0.1": {
                            "interface": "Vl100",
                            "router": "10.2.0.1"
                        }
                    }
                }
            }
        })


    def test_IPRoute_vrf_tag(self):
        self.cfg.parse_str("""
ip route vrf TestVRF 10.1.0.0 255.255.255.0 Vlan100 10.2.0.1 tag 100 20
""")

        self.assertEqual(self.cfg, {
            "ip-route": {
                "TestVRF": {
                    "10.1.0.0/24": {
                        "Vl100 10.2.0.1": {
                            "interface": "Vl100",
                            "router": "10.2.0.1",
                            "metric": 20,
                            "tag": 100
                        }
                    }
                }
            }
        })


    def test_IPv6Route_int(self):
        self.cfg.parse_str("""
ipv6 route 10::1/64 Eth1/1.100
""")

        self.assertEqual(self.cfg, {
            "ipv6-route": {
                None: {
                    "10::1/64": {
                        "Eth1/1.100 -": {
                            "interface": "Eth1/1.100"
                        }
                    }
                }
            }
        })


    def test_IPv6Route_ip(self):
        self.cfg.parse_str("""
ipv6 route 10::1/64 20::1
""")

        self.assertEqual(self.cfg, {
            "ipv6-route": {
                None: {
                    "10::1/64": {
                        "- 20::1": {
                            "router": "20::1"
                        }
                    }
                }
            }
        })


    def test_IPv6Route_int_ip(self):
        self.cfg.parse_str("""
ipv6 route 10::1/64 Vlan100 20::1
""")

        self.assertEqual(self.cfg, {
            "ipv6-route": {
                None: {
                    "10::1/64": {
                        "Vl100 20::1": {
                            "interface": "Vl100",
                            "router": "20::1"
                        }
                    }
                }
            }
        })


    def test_IPv6Route_vrf_tag(self):
        self.cfg.parse_str("""
ipv6 route vrf TestVRF 10::1/64 Vlan100 20::1 tag 100 20
""")

        self.assertEqual(self.cfg, {
            "ipv6-route": {
                "TestVRF": {
                    "10::1/64": {
                        "Vl100 20::1": {
                            "interface": "Vl100",
                            "router": "20::1",
                            "metric": 20,
                            "tag": 100
                        }
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # route-map ...
    # -------------------------------------------------------------------------


    def test_RtMap(self):
        self.cfg.parse_str("""
route-map TestRtMap permit 10
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit"
                    }
                }
            }
        })


    def test_RtMap_MatchCmty(self):
        # check multiple communities are supported and are additive and
        # preserve exact-match
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 match community 100:1 200:1 exact-match
 match community 300:1
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "match": {
                            "community": {
                                "communities": { "100:1", "200:1", "300:1" },
                                "exact-match": True
                            }
                        }
                    }
                }
            }
        })


    def test_RtMap_MatchIPAddr_IPAddr(self):
        # check multiple addresses are supported and are additive
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 match ip address 10.0.0.1 20.0.0.1
 match ip address 30.0.0.1
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "match": {
                            "ip-address": {
                                "10.0.0.1", "20.0.0.1", "30.0.0.1" }
                        }
                    }
                }
            }
        })


    def test_RtMap_MatchIPAddr_PfxList(self):
        # check multiple prefix lists are supported and are additive
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 match ip address prefix-list TestPfxList1 TestPfxList2
 match ip address prefix-list TestPfxList3
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "match": {
                            "ip-prefix-list": {
                                "TestPfxList1", "TestPfxList2", "TestPfxList3"
                            }
                        }
                    }
                }
            }
        })


    def test_RtMap_MatchIPv6Addr_IPAddr(self):
        # check multiple addresses are supported and are additive
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 match ipv6 address 10::1 20::1
 match ipv6 address 30::1
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "match": {
                            "ipv6-address": { "10::1", "20::1", "30::1" }
                        }
                    }
                }
            }
        })


    def test_RtMap_MatchIPv6Addr_PfxList(self):
        # check multiple lists are supported and are additive
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 match ipv6 address prefix-list TestPfxList1 TestPfxList2
 match ipv6 address prefix-list TestPfxList3
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "match": {
                            "ipv6-prefix-list": {
                                "TestPfxList1", "TestPfxList2", "TestPfxList3"
                            }
                        }
                    }
                }
            }
        })


    def test_RtMap_MatchTag(self):
        # check multiple tags are supported and are additive
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 match tag 10 20
 match tag 30
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "match": {
                            "tag": { 10, 20, 30 }
                        }
                    }
                }
            }
        })


    def test_RtMap_SetCmty(self):
        # check multiple tags are supported and are additive
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set community 100:1 200:1 additive
 set community 300:1
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "community": {
                                "communities": { "100:1", "200:1", "300:1" },
                            "additive": True
                            }
                        }
                    }
                }
            }
        })


    def test_RtMap_SeIPNxtHop(self):
        # check multiple next hops are supported and assemble a list
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set ip next-hop 10.0.0.1 20.0.0.1
 set ip next-hop 30.0.0.1
 set ip vrf TestVRF next-hop 40.0.0.1
 set ip next-hop 50.0.0.1 60.0.0.1
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "ip-next-hop": [
                                { "addr": "10.0.0.1" },
                                { "addr": "20.0.0.1" },
                                { "addr": "30.0.0.1" },
                                { "addr": "40.0.0.1", "vrf": "TestVRF" },
                                { "addr": "50.0.0.1" },
                                { "addr": "60.0.0.1" }
                            ]
                        }
                    }
                }
            }
        })


    def test_RtMap_SetIPNxtHopVrfy(self):
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set ip next-hop verify-availability
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "ip-next-hop-verify-availability": True
                        }
                    }
                }
            }
        })


    def test_RtMap_SetIPNxtHopVrfyTrk(self):
        # check multiple next hops are supported and stored against sequence
        # number
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set ip next-hop verify-availability 10.0.0.1 200 track 20
 set ip next-hop verify-availability 20.0.0.1 100 track 30
 set ip next-hop verify-availability 30.0.0.1 300 track 10
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "ip-next-hop-verify-availability-track": {
                                100: { "addr": "20.0.0.1", "track-obj": 30 },
                                200: { "addr": "10.0.0.1", "track-obj": 20 },
                                300: { "addr": "30.0.0.1", "track-obj": 10 }
                            }
                        }
                    }
                }
            }
        })


    def test_RtMap_SetIPv6NxtHop(self):
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set ipv6 next-hop 10::1 20::1
 set ipv6 next-hop 30::1
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "ipv6-next-hop": [
                                { "addr": "10::1" },
                                { "addr": "20::1" },
                                { "addr": "30::1" }
                            ]
                        }
                    }
                }
            }
        })


    def test_RtMap_SetLocalPref(self):
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set local-preference 10
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "local-preference": 10
                        }
                    }
                }
            }
        })


    def test_RtMap_SetVRF_global(self):
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set global
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "vrf": ""
                        }
                    }
                }
            }
        })


    def test_RtMap_SetVRF_vrf(self):
        self.cfg.parse_str("""
route-map TestRtMap permit 10
 set vrf TestVRF
""")

        self.assertEqual(self.cfg, {
            "route-map": {
                "TestRtMap": {
                    10: {
                        "action": "permit",
                        "set": {
                            "vrf": "TestVRF"
                        }
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # router bgp ...
    # -------------------------------------------------------------------------


    def test_RtrBGP(self):
        self.cfg.parse_str("""
router bgp 100
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100": {}
                }
            }
        })


    def test_RtrBGP_RtrID(self):
        self.cfg.parse_str("""
router bgp 100
 bgp router-id 10.0.0.1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100": {
                        "router-id": "10.0.0.1"
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # router bgp ...
    #  neighbor ...
    # -------------------------------------------------------------------------


    def test_RtrBGP_NbrFallOver(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 neighbor 10.0.0.1 fall-over route-map TestRtMap
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200",
                                "fall-over": {
                                    "route-map": "TestRtMap"
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_NbrPwd(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 neighbor 10.0.0.1 password 0 TestPassword
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200",
                                "password": {
                                    "encryption": 0,
                                    "password": "TestPassword"
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_NbrPrGrp(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor TestPeerGroup peer-group
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "TestPeerGroup": {
                                "type": "peer-group"
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_NbrPrGrpMbr(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 peer-group TestPeerGroup
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "peer-group": "TestPeerGroup"
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_NbrRemAS(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200.1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200.1"
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_NbrUpdSrc(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 neighbor 10.0.0.1 update-source Eth10/1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200",
                                "update-source": "Eth10/1"
                            }
                        }
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # router bgp ...
    #  address-family ... [vrf ...]
    # -------------------------------------------------------------------------


    def test_RtrBGP_AF_ipv4(self):
        # check IPv4 converted to unicast
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {}
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_ipv6(self):
        # check IPv4 converted to unicast
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv6
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv6 unicast": {}
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_ipv4_vrf(self):
        # check IPv4 in a VRF
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4 unicast vrf TestVRF
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            "TestVRF": {
                                "address-family": {
                                    "ipv4 unicast": {}
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_vpnv4(self):
        self.cfg.parse_str("""
router bgp 100.1
 address-family vpnv4
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "vpnv4 unicast": {}
                                }
                            }
                        }
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # router bgp ...
    #  address-family ...
    #   neighbor ...
    # -------------------------------------------------------------------------


    def test_RtrBGP_AF_NbrAct(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 activate
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "activate": True
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrAddPath_sndrcv(self):
        # check additional-paths replaces previous setting
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 additional-paths send receive
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "additional-paths": {
                                                    "send", "receive"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrAddPath_rplc(self):
        # check additional-paths replaces previous setting
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 additional-paths send
  neighbor 10.0.0.1 additional-paths receive
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "additional-paths": {
                                                    "receive"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrAddPath_dis(self):
        # check additional-paths replaces previous setting
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 additional-paths receive
  neighbor 10.0.0.1 additional-paths disable
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "additional-paths": {
                                                    "disable"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrAdvAddPath(self):
        # check options are additive
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 advertise additional-paths best 2
  neighbor 10.0.0.1 advertise additional-paths group-best all
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "advertise-additional-paths": {
                                                    "all": True,
                                                    "best": 2,
                                                    "group-best": True
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrAlwAS_plain(self):
        # check options are additive
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 allowas-in
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "allowas-in": {}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrAlwAS_num(self):
        # check options are additive
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 allowas-in 2
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "allowas-in": {
                                                    "max": 2
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrFltLst(self):
        # check filter-lists supported in both directions
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 filter-list 100 in
  neighbor 10.0.0.1 filter-list 200 out
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "filter-list": {
                                                    "in": 100,
                                                    "out": 200
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrMaxPfx(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 maximum-prefix 50 80
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "maximum-prefix": {
                                                    "max": 50,
                                                    "threshold": 80
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrNHSelf_plain(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 next-hop-self
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "next-hop-self": {}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrNHSelf_all(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 next-hop-self all
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "next-hop-self": {
                                                    "all": True
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrPfxLst(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 prefix-list TestPrefixList1 in
  neighbor 10.0.0.1 prefix-list TestPrefixList2 out
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "prefix-list": {
                                                    "in": "TestPrefixList1",
                                                    "out": "TestPrefixList2"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrRemPrivAS_plain(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 remove-private-as
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "remove-private-as": {}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrRemPrivAS_all(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 remove-private-as all
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "remove-private-as": {
                                                    "all": True
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrRtMap(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 route-map TestRtMap1 in
  neighbor 10.0.0.1 route-map TestRtMap2 out
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "route-map": {
                                                    "in": "TestRtMap1",
                                                    "out": "TestRtMap2"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrSndCmty_both(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 send-community both
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "send-community": {
                                                    "standard", "extended"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrSndCmty_add(self):
        # check types are additive
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 send-community
  neighbor 10.0.0.1 send-community extended
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "send-community": {
                                                    "standard", "extended"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_NbrSoftRecfg(self):
        self.cfg.parse_str("""
router bgp 100.1
 neighbor 10.0.0.1 remote-as 200
 address-family ipv4 unicast
  neighbor 10.0.0.1 soft-reconfiguration inbound
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "neighbor": {
                            "10.0.0.1": {
                                "remote-as": "200"
                            }
                        },
                        "vrf": {
                            VRF_GLOBAL: {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "soft-reconfiguration": (
                                                    "inbound")
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # router bgp ...
    #  address-family ... vrf ...
    #   neighbor ...
    # -------------------------------------------------------------------------


    def test_RtrBGP_AF_vrf_Nbr(self):
        # check neighbor in a VRF
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4 unicast vrf TestVRF
  neighbor 10.0.0.1 remote-as 200
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            "TestVRF": {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "remote-as": "200"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_vrf_NbrFallOver(self):
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4 unicast vrf TestVRF
  neighbor 10.0.0.1 remote-as 200
  neighbor 10.0.0.1 fall-over route-map TestRtMap
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            "TestVRF": {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "remote-as": "200",
                                                "fall-over": {
                                                    "route-map": "TestRtMap"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_vrf_NbrPrGrp(self):
        # check peer-group in a VRF
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4 unicast vrf TestVRF
  neighbor TestPeerGroup peer-group
  neighbor TestPeerGroup remote-as 200
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            "TestVRF": {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "TestPeerGroup": {
                                                "type": "peer-group",
                                                "remote-as": "200"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_vrf_NbrPrGrpMbr(self):
        # check peer-group in a VRF
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4 unicast vrf TestVRF
  neighbor TestPeerGroup peer-group
  neighbor TestPeerGroup remote-as 200
  neighbor 10.0.0.1 peer-group TestPeerGroup
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            "TestVRF": {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "TestPeerGroup": {
                                                "type": "peer-group",
                                                "remote-as": "200"
                                            },
                                            "10.0.0.1": {
                                                "peer-group": "TestPeerGroup"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrBGP_AF_vrf_NbrPwd(self):
        # check peer-group in a VRF
        self.cfg.parse_str("""
router bgp 100.1
 address-family ipv4 unicast vrf TestVRF
  neighbor 10.0.0.1 remote-as 200
  neighbor 10.0.0.1 password 0 TestPassword
""")

        self.assertEqual(self.cfg, {
            "router": {
                "bgp": {
                    "100.1": {
                        "vrf": {
                            "TestVRF": {
                                "address-family": {
                                    "ipv4 unicast": {
                                        "neighbor": {
                                            "10.0.0.1": {
                                                "remote-as": "200",
                                                "password": {
                                                    "encryption": 0,
                                                    "password": "TestPassword"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # router ospf ...
    # -------------------------------------------------------------------------


    def test_RtrOSPF(self):
        self.cfg.parse_str("""
router ospf 100
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospf": {
                    100: {}
                }
            }
        })


    def test_RtrOSPF_ID(self):
        self.cfg.parse_str("""
router ospf 100
 router-id 10.0.0.1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospf": {
                    100: {
                        "id": "10.0.0.1"
                    }
                }
            }
        })


    def test_RtrOSPF_AreaNSSA(self):
        # check NSSA parameters are additive
        self.cfg.parse_str("""
router ospf 100
 area 10.0.0.0 nssa no-redistribution
 area 10.0.0.0 nssa no-summary
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospf": {
                    100: {
                        "area": {
                            "10.0.0.0": {
                                "nssa": { "no-redistribution", "no-summary" }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrOSPF_PasvInt_simple(self):
        # check passive-interface default supported and interfaces additive
        self.cfg.parse_str("""
router ospf 100
 passive-interface default
 no passive-interface Eth10/1
 no passive-interface Eth20/1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospf": {
                    100: {
                        "passive-interface": {
                            "default": True,
                            "no-interface": { "Eth10/1", "Eth20/1" }
                        }
                    }
                }
            }
        })


    def test_RtrOSPF_PasvInt_unused(self):
        # check enabling no passive-interface on interface when already
        # default does nothing
        self.cfg.parse_str("""
router ospf 100
 no passive-interface Eth10/1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospf": {
                    100: {}
                }
            }
        })


    def test_RtrOSPF_PasvInt_reset(self):
        # check no passive-interface default resets the configuration
        self.cfg.parse_str("""
router ospf 100
 passive-interface default
 no passive-interface Eth10/1
 no passive-interface Eth20/1
 no passive-interface default
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospf": {
                    100: {}
                }
            }
        })


    # -------------------------------------------------------------------------
    # router ospfv3 ...
    # -------------------------------------------------------------------------


    def test_RtrOSPFv3(self):
        self.cfg.parse_str("""
router ospfv3 100
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {}
                }
            }
        })


    def test_RtrOSPFv3_ID(self):
        self.cfg.parse_str("""
router ospfv3 100
 router-id 10.0.0.1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "id": "10.0.0.1"
                    }
                }
            }
        })


    def test_RtrOSPFv3_AreaNSSA(self):
        # check NSSA parameters are additive
        self.cfg.parse_str("""
router ospfv3 100
 area 10.0.0.0 nssa no-redistribution
 area 10.0.0.0 nssa no-summary
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "area": {
                            "10.0.0.0": {
                                "nssa": { "no-redistribution", "no-summary" }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrOSPFv3_PasvInt_multi_af(self):
        # check passive-interface outside of an address family affects
        # defined address families only, and can set individual address
        # family configuration
        self.cfg.parse_str("""
router ospfv3 100
 address-family ipv4
 exit-address-family
 !
 address-family ipv6
 exit-address-family
 !
 passive-interface default
 no passive-interface Eth10/1
 no passive-interface Eth20/1
 !
 address-family ipv6
  no passive-interface Eth30/1
 exit-address-family
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "address-family": {
                            "ipv4": {
                                "passive-interface": {
                                    "default": True,
                                    "no-interface":  { "Eth10/1", "Eth20/1" }
                                }
                            },
                            "ipv6": {
                                "passive-interface": {
                                    "default": True,
                                    "no-interface": {
                                        "Eth10/1", "Eth20/1", "Eth30/1" }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrOSPFv3_PasvInt_diff(self):
        # check passive-interface outside of an address family affects
        # defined address families only, and can set individual address
        # family configuration
        self.cfg.parse_str("""
router ospfv3 100
 address-family ipv6
 exit-address-family
 !
 passive-interface default
 no passive-interface Eth10/1
 no passive-interface Eth20/1
 !
 address-family ipv4
  no passive-interface Eth30/1
 exit-address-family
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "address-family": {
                            "ipv4": {},
                            "ipv6": {
                                "passive-interface": {
                                    "default": True,
                                    "no-interface": { "Eth10/1", "Eth20/1" }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrOSPFv3_PasvInt_clear_af(self):
        # check passive-interface outside of an address family affects
        # defined address families only, and can set individual address
        # family configuration
        self.cfg.parse_str("""
router ospfv3 100
 address-family ipv4
 exit-address-family
 !
 address-family ipv6
 exit-address-family
 !
 passive-interface default
 no passive-interface Eth10/1
 no passive-interface Eth20/1
 !
 address-family ipv4
  no passive-interface default
 exit-address-family
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "address-family": {
                            "ipv4": {},
                            "ipv6": {
                                "passive-interface": {
                                    "default": True,
                                    "no-interface": { "Eth10/1", "Eth20/1" }
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_RtrOSPFv3_AF_ipv4(self):
        # check IPv4 supported in OSPFv3
        self.cfg.parse_str("""
router ospfv3 100
 address-family ipv4
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "address-family": {
                            "ipv4": {}
                        }
                    }
                }
            }
        })


    def test_RtrOSPFv3_AF_ipv6(self):
        # check unicast parameter is ignored
        self.cfg.parse_str("""
router ospfv3 100
 address-family ipv6 unicast
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "address-family": {
                            "ipv6": {}
                        }
                    }
                }
            }
        })


    def test_RtrOSPFv3_AF_PasvInt(self):
        # check passive-interface default supported and interfaces additive
        self.cfg.parse_str("""
router ospfv3 100
 address-family ipv6
  passive-interface default
  no passive-interface Eth10/1
  no passive-interface Eth20/1
""")

        self.assertEqual(self.cfg, {
            "router": {
                "ospfv3": {
                    100: {
                        "address-family": {
                            "ipv6": {
                                "passive-interface": {
                                    "default": True,
                                    "no-interface": { "Eth10/1", "Eth20/1" }
                                }
                            }
                        }
                    }
                }
            }
        })
