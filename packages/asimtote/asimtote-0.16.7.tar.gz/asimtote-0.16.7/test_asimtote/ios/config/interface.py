# (asimtote) test_asimtote.ios.config.interface
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from asimtote.ios import CiscoIOSConfig



class TestAsimtote_CiscoIOS_Config_Interface(unittest.TestCase):
    def setUp(self):
        # create a starting blank configuration for each test
        self.cfg = CiscoIOSConfig()


    def test_Int_lo(self):
        self.cfg.parse_str("""
interface Loopback100
""")

        # loopback interfaces default to 'no shutdown'
        self.assertEqual(self.cfg, {
            "interface": {
                "Lo100": {
                    "shutdown": False
                }
            }
        })


    def test_Int_eth(self):
        self.cfg.parse_str("""
interface Ethernet1/10
""")

        # physical interfaces default to 'no shutdown' when reading in a
        # startup configuration (which we are), so confirm that
        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False
                }
            }
        })


    def test_Int_eth_sub(self):
        self.cfg.parse_str("""
interface Ethernet1/10.100
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10.100": {
                    "shutdown": False
                }
            }
        })


    def test_Int_vlan(self):
        self.cfg.parse_str("""
interface Vlan100
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Vl100": {
                    "shutdown": False
                }
            }
        })


    def test_Int_ARPTime(self):
        self.cfg.parse_str("""
interface Ethernet1/10
 arp timeout 900
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "arp-timeout": 900
                }
            }
        })


    def test_Int_CDPEna_yes(self):
        self.cfg.parse_str("""
interface Ethernet1/10
 cdp enable
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "cdp-enable": True
                }
            }
        })


    def test_Int_CDPEna_no(self):
        self.cfg.parse_str("""
interface Ethernet1/10
 no cdp enable
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "cdp-enable": False
                }
            }
        })


    def test_Int_ChnGrp_no_mode(self):
        self.cfg.parse_str("""
interface Eth1/10
 channel-group 100
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "channel-group": (100, None)
                }
            }
        })


    def test_Int_ChnGrp_mode(self):
        self.cfg.parse_str("""
interface Eth1/10
 channel-group 100 mode auto
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "channel-group": (100, " mode auto")
                }
            }
        })


    def test_Int_Desc(self):
        self.cfg.parse_str("""
interface Eth1/10
 description Test Description
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "description": "Test Description"
                }
            }
        })


    def test_Int_Encap_ntv(self):
        self.cfg.parse_str("""
interface Eth1/10
 encapsulation dot1q 100 native
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "encapsulation": "dot1q 100 native"
                }
            }
        })


    def test_Int_Encap_tag(self):
        self.cfg.parse_str("""
interface Eth1/10
 encapsulation dot1q 100
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "encapsulation": "dot1q 100"
                }
            }
        })


    def test_Int_IPAccGrp(self):
        # check both directions supported and can replace existing entry
        # correctly
        self.cfg.parse_str("""
interface Eth1/10
 ip access-group InACL1 in
 ip access-group InACL2 in
 ip access-group OutACL out
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-access-group": {
                        "in": "InACL2",
                        "out": "OutACL"
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # ip address ...
    # -------------------------------------------------------------------------


    def test_Int_IPAddr(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip address 10.0.0.1 255.255.255.0
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-address": "10.0.0.1 255.255.255.0"
                }
            }
        })


    def test_Int_IPAddr_Sec(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip address 10.0.0.1 255.255.255.0 secondary
 ip address 20.0.0.1 255.255.0.0 secondary
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-address-secondary": {
                        "10.0.0.1 255.255.255.0",
                        "20.0.0.1 255.255.0.0"
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # ...
    # -------------------------------------------------------------------------


    def test_Int_IPFlowMon(self):
        # check both directions supported and can replace existing entry
        # correctly
        self.cfg.parse_str("""
interface Eth1/10
 ip flow monitor FlowIn input
 ip flow monitor FlowIn2 input
 ip flow monitor FlowOut output
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-flow-monitor": {
                        "input": "FlowIn2",
                        "output": "FlowOut"
                    }
                }
            }
        })


    def test_Int_IPHlprAddr(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip helper-address 10.0.0.1
 ip helper-address global 20.0.0.1
 ip helper-address vrf TestVRF 30.0.0.1
""")

        # the key for the dictionary of helpers is the original string
        # specification - it's unused in the actual configuration but
        # needed to manage the dictionary
        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-helper-address": {
                        "10.0.0.1": {
                            "addr": "10.0.0.1"
                        },
                        "global 20.0.0.1": {
                            "addr": "20.0.0.1",
                            "global": None
                        },
                        "vrf TestVRF 30.0.0.1": {
                            "addr": "30.0.0.1",
                            "vrf": "TestVRF"
                        }
                    }
                }
            }
        })


    def test_Int_IPIGMPVer(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip igmp version 3
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-igmp-version": 3
                }
            }
        })


    def test_Int_IPMcastBdry(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip multicast boundary MulticastACL
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-multicast-boundary": "MulticastACL"
                }
            }
        })


    # -------------------------------------------------------------------------
    # ip ospf ...
    # -------------------------------------------------------------------------


    def test_Int_IPOSPFArea(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf 10 area 10.0.0.0
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "area": {
                            "process": 10,
                            "id": "10.0.0.0"
                        }
                    }
                }
            }
        })


    def test_Int_IPOSPFAuth(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf authentication message-digest
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "authentication": "message-digest"
                    }
                }
            }
        })


    def test_Int_IPOSPFCost(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf cost 50
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "cost": 50
                    }
                }
            }
        })


    def test_Int_IPOSPFDeadIvl(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf dead-interval 50
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "dead-interval": 50
                    }
                }
            }
        })


    def test_Int_IPOSPFHelloIvl(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf hello-interval 10
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "hello-interval": 10
                    }
                }
            }
        })


    def test_Int_IPOSPFMsgDigKey(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf message-digest-key 10 md5 OSPFMD5Key10
 ip ospf message-digest-key 20 md5 OSPFMD5Key20
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "message-digest-key": {
                            10: "OSPFMD5Key10",
                            20: "OSPFMD5Key20"
                        }
                    }
                }
            }
        })


    def test_Int_IPOSPFNet(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip ospf network point-to-point
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-ospf": {
                        "network": "point-to-point"
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # ip pim ...
    # -------------------------------------------------------------------------


    def test_Int_IPPIMMode(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip pim sparse-mode
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-pim": {
                        "mode": "sparse"
                    }
                }
            }
        })


    def test_Int_IPPIMBSRBdr(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip pim bsr-border
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-pim": {
                        "bsr-border": True
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # ...
    # -------------------------------------------------------------------------


    def test_Int_IPPolicyRtMap(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip policy route-map TestRtMap
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-policy-route-map": "TestRtMap"
                }
            }
        })


    def test_Int_IPProxyARP_yes(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip proxy-arp
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-proxy-arp": True
                }
            }
        })


    def test_Int_IPProxyARP_no(self):
        self.cfg.parse_str("""
interface Eth1/10
 no ip proxy-arp
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-proxy-arp": False
                }
            }
        })


    def test_Int_IPVerifyUni(self):
        self.cfg.parse_str("""
interface Eth1/10
 ip verify unicast source reachable-via rx 100 allow-default
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ip-verify-unicast": (
                        "source reachable-via rx 100 allow-default")
                }
            }
        })


    # -------------------------------------------------------------------------
    # ipv6 ...
    # -------------------------------------------------------------------------


    def test_Int_IPv6Addr(self):
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 address 10::1/64
 ipv6 address 20::1/126
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-address": { "10::1/64", "20::1/126" }
                }
            }
        })


    def test_Int_IPv6MultBdry_Num(self):
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 multicast boundary scope 8
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-multicast-boundary-scope": 8
                }
            }
        })


    def test_Int_IPv6MultBdry_Name(self):
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 multicast boundary scope organization-local
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-multicast-boundary-scope": 8
                }
            }
        })


    def test_Int_IPv6NDPfx_secs(self):
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 nd prefix 10::/64 2000 1000
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-nd-prefix": {
                        "10::/64": {
                            "preferred-lifetime": 1000,
                            "valid-lifetime": 2000
                        }
                    }
                }
            }
        })


    def test_Int_IPv6NDPfx_at_full(self):
        # check the 'at' dates are correctly parsed
        # canonical form
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 nd prefix 10::/64 at 22 Feb 2022 22:00 1 Jan 2021 1:00 no-autoconfig
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-nd-prefix": {
                        "10::/64": {
                            "preferred-until": "1 jan 2021 1:00",
                            "valid-until": "22 feb 2022 22:00",
                            "no-autoconfig": True
                        }
                    }
                }
            }
        })


    def test_Int_IPv6NDPfx_at_us(self):
        # check the US format dates are correctly parsed and canonicalised
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 nd prefix 10::/64 at Feb 22 2022 22:00 Jan 1 2021 1:00
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-nd-prefix": {
                        "10::/64": {
                            "preferred-until": "1 jan 2021 1:00",
                            "valid-until": "22 feb 2022 22:00"
                        }
                    }
                }
            }
        })


    def test_Int_IPv6PIMBSRBdr(self):
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 pim bsr border
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-pim": {
                        "bsr-border": True
                    }
                }
            }
        })


    def test_Int_IPv6PIMPolicyRtMap(self):
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 policy route-map TestRtMap
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-policy-route-map": "TestRtMap"
                }
            }
        })


    def test_Int_IPv6TrafFilt(self):
        # check both directions supported and can replace existing entry
        # correctly
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 traffic-filter InACL1 in
 ipv6 traffic-filter InACL2 in
 ipv6 traffic-filter OutACL out
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-traffic-filter": {
                        "in": "InACL2",
                        "out": "OutACL"
                    }
                }
            }
        })


    def test_Int_IPv6VerifyUni(self):
        # check both directions supported and can replace existing entry
        # correctly
        self.cfg.parse_str("""
interface Eth1/10
 ipv6 verify unicast source reachable-via rx allow-default TestACL
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ipv6-verify-unicast": (
                        "source reachable-via rx allow-default TestACL")
                }
            }
        })


    # -------------------------------------------------------------------------
    # ...
    # -------------------------------------------------------------------------


    def test_Int_MPLSIP(self):
        self.cfg.parse_str("""
interface Eth1/10
 mpls ip
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "mpls-ip": True
                }
            }
        })


    def test_Int_MTU(self):
        self.cfg.parse_str("""
interface Eth1/10
 mtu 9000
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "mtu": 9000
                }
            }
        })


    # -------------------------------------------------------------------------
    # ospfv3 ...
    # -------------------------------------------------------------------------


    def test_Int_OSPFv3Area(self):
        # check multiple protocols supported and can replace existing
        # entry correctly
        self.cfg.parse_str("""
interface Eth1/10
 ospfv3 11 ipv4 area 4.1.0.0
 ospfv3 12 ipv4 area 4.2.0.0
 ospfv3 20 ipv6 area 6.0.0.0
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ospfv3": {
                        "area": {
                            "ipv4": {
                                "process": 12,
                                "id": "4.2.0.0"
                            },
                            "ipv6": {
                                "process": 20,
                                "id": "6.0.0.0"
                            }
                        }
                    }
                }
            }
        })


    def test_Int_OSPFv3Cost(self):
        self.cfg.parse_str("""
interface Eth1/10
 ospfv3 cost 50
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ospfv3": {
                        "cost": 50
                    }
                }
            }
        })


    def test_Int_OSPFv3DeadIvl(self):
        self.cfg.parse_str("""
interface Eth1/10
 ospfv3 dead-interval 50
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ospfv3": {
                        "dead-interval": 50
                    }
                }
            }
        })


    def test_Int_OSPFv3HelloIvl(self):
        self.cfg.parse_str("""
interface Eth1/10
 ospfv3 hello-interval 10
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ospfv3": {
                        "hello-interval": 10
                    }
                }
            }
        })


    def test_Int_OSPFv3Net(self):
        self.cfg.parse_str("""
interface Eth1/10
 ospfv3 network point-to-point
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ospfv3": {
                        "network": "point-to-point"
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # ...
    # -------------------------------------------------------------------------


    def test_Int_ServPol(self):
        self.cfg.parse_str("""
interface Eth1/10
 ospfv3 network point-to-point
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "ospfv3": {
                        "network": "point-to-point"
                    }
                }
            }
        })


    def test_Int_Shutdown_yes(self):
        self.cfg.parse_str("""
interface Eth1/10
 shutdown
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": True,
                }
            }
        })


    def test_Int_Shutdown_no(self):
        self.cfg.parse_str("""
interface Eth1/10
 no shutdown
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                }
            }
        })


    # -------------------------------------------------------------------------
    # standby ...
    # -------------------------------------------------------------------------


    def test_Int_StandbyIP(self):
        # check multiple groups are supported and new addresses replace
        # the existing one
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 ip 10.0.0.1
 standby 100 ip 10.0.0.2
 standby 200 ip 20.0.0.1
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: { "ip": "10.0.0.2" },
                            200: { "ip": "20.0.0.1" }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyIPSec(self):
        # check multiple groups are supported and secondary addresses
        # are additive
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 ip 11.0.0.1 secondary
 standby 100 ip 12.0.0.1 secondary
 standby 200 ip 21.0.0.1 secondary
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: {
                                "ip-secondary": { "11.0.0.1", "12.0.0.1" }
                            },
                            200: {
                                "ip-secondary": { "21.0.0.1" }
                            }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyIPv6(self):
        # check multiple groups are supported and addresses are additive
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 ipv6 11::1/64
 standby 100 ipv6 12::1/126
 standby 200 ipv6 21::1/112
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: {
                                "ipv6": { "11::1/64", "12::1/126" }
                            },
                            200: {
                                "ipv6": { "21::1/112" }
                            }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyPreempt(self):
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 preempt
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: {
                                "preempt": True
                            }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyPri(self):
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 priority 50
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: {
                                "priority": 50
                            }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyTimers(self):
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 timers 10 30
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: {
                                "timers": "10 30"
                            }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyTrack(self):
        self.cfg.parse_str("""
interface Eth1/10
 standby 100 track 10 decrement 50
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "group": {
                            100: {
                                "track": {
                                    10: "decrement 50"
                                }
                            }
                        }
                    }
                }
            }
        })


    def test_Int_StandbyVer(self):
        self.cfg.parse_str("""
interface Eth1/10
 standby version 2
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "standby": {
                        "version": 2
                    }
                }
            }
        })


    def test_Int_StormCtrl(self):
        self.cfg.parse_str("""
interface Eth1/10
 storm-control multicast level 10
 storm-control broadcast level 20.5
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "storm-control": {
                        "multicast": 10,
                        "broadcast": 20.5
                    }
                }
            }
        })


    # -------------------------------------------------------------------------
    # switchport ...
    # -------------------------------------------------------------------------


    def test_Int_SwPort_yes(self):
        self.cfg.parse_str("""
interface Eth1/10
 switchport
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport": True
                }
            }
        })


    def test_Int_SwPort_no(self):
        self.cfg.parse_str("""
interface Eth1/10
 no switchport
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport": False
                }
            }
        })


    def test_Int_SwPortNoNeg(self):
        self.cfg.parse_str("""
interface Eth1/10
 switchport nonegotiate
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport-nonegotiate": True
                }
            }
        })


    def test_Int_SwPortTrkNtv(self):
        self.cfg.parse_str("""
interface Eth1/10
 switchport trunk native vlan 100
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport-trunk-native": 100
                }
            }
        })


    def test_Int_SwPortTrAlw_none(self):
        self.cfg.parse_str("""
interface Eth1/10
 switchport trunk allowed vlan none
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport-trunk-allow": set()
                }
            }
        })


    def test_Int_SwPortTrAlw_Rplc(self):
        # check list can be replaced
        self.cfg.parse_str("""
interface Eth1/10
 switchport trunk allowed vlan 100
 switchport trunk allowed vlan 200
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport-trunk-allow": { 200 }
                }
            }
        })


    def test_Int_SwPortTrAlw_Add(self):
        # check list can be replaced
        self.cfg.parse_str("""
interface Eth1/10
 switchport trunk allowed vlan 100
 switchport trunk allowed vlan add 200
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False,
                    "switchport-trunk-allow": { 100, 200 }
                }
            }
        })


    def test_Int_SwPortTrAlw_All(self):
        # check 'allow all' means no list
        self.cfg.parse_str("""
interface Eth1/10
 switchport trunk allowed vlan all
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False
                }
            }
        })


    def test_Int_SwPortTrAlw_AllReplc(self):
        # check 'allow all' removes any existing list
        self.cfg.parse_str("""
interface Eth1/10
 switchport trunk allowed vlan 100
 switchport trunk allowed vlan all
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Eth1/10": {
                    "shutdown": False
                }
            }
        })


    def test_Int_PcMinLinks(self):
        # check 'allow all' removes any existing list
        self.cfg.parse_str("""
interface Po10
 port-channel min-links 2
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Po10": {
                    "shutdown": False,
                    "port-channel-min-links": 2
                }
            }
        })


    def test_Int_VRFFwd(self):
        # check 'allow all' removes any existing list
        self.cfg.parse_str("""
interface Po10
 vrf forwarding TestVRF
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Po10": {
                    "shutdown": False,
                    "vrf-forwarding": "TestVRF"
                }
            }
        })


    def test_Int_XConn(self):
        # check 'allow all' removes any existing list
        self.cfg.parse_str("""
interface Po10
 xconnect 10.0.0.1 100 encapsulation mpls
""")

        self.assertEqual(self.cfg, {
            "interface": {
                "Po10": {
                    "shutdown": False,
                    "xconnect": "10.0.0.1 100 encapsulation mpls"
                }
            }
        })
