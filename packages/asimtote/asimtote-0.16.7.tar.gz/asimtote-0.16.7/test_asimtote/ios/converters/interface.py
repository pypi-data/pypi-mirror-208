# (asimtote) test_asimtote.ios.converters.interface
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from .cvtunittest import CiscoIOS_Convert_unittest



class TestAsimtote_CiscoIOS_Convert_Interface(CiscoIOS_Convert_unittest):
    # =========================================================================
    # interface ...
    # =========================================================================


    def test_Interface_add_phy(self):
        # check physical interfaces are created not shut down (which is
        # the default for a startup-config; it's different for a
        # running-config but that's not what we're treating the
        # configurations as)

        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no shutdown
""")


    # -------------------------------------------------------------------------


    def test_Interface_add_vlan(self):
        # check non-physical interfaces are created

        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
interface Vlan100
""")

        self.compare("""
interface Vl100
!
interface Vl100
 no shutdown
""")


    # -------------------------------------------------------------------------


    def test_Interface_remove_phy(self):
        # check physical interfaces are not removed (as they can't be)

        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("")

        self.compare("")


    # -------------------------------------------------------------------------


    def test_Interface_remove_vlan(self):
        # check non-physical interfaces are removed

        self.old_cfg.parse_str("""
interface Vlan100
""")

        self.new_cfg.parse_str("")

        self.compare("""
no interface Vl100
""")


    # =========================================================================
    # interface ...
    #  [no] shutdown
    # =========================================================================


    def test_Interface_Shut_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 shutdown
""")

        self.compare("""
interface Eth1/1
 shutdown
""")


    # -------------------------------------------------------------------------


    def test_Interface_Shut_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 shutdown
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no shutdown
""")


    # =========================================================================
    # interface ...
    #  vrf forwarding ...
    # =========================================================================


    def test_Interface_VrfFwd_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF
""")

        self.compare("""
interface Eth1/1
 vrf forwarding TestVRF
""")


    # -------------------------------------------------------------------------


    def test_Interface_VrfFwd_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no vrf forwarding
""")


    # =========================================================================
    # interface ...
    #  ip address ...
    #  ipv6 address ...
    #  ipv6 nd prefix ...
    #  standby ... ip ... [secondary]
    #  standby ... ipv6 ...
    #  vrf forwarding ...
    # =========================================================================


    # check interface VRF change triggers re-application of IP details


    def test_Interface_VrfFwd_IP_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
 ipv6 address 10::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
 standby 10 ip 10.0.0.11
 standby 10 ip 10.0.0.12 secondary
 standby 20 ipv6 10::11/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF
 ip address 10.0.0.1 255.255.255.0
 ipv6 address 10::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
 standby 10 ip 10.0.0.11
 standby 10 ip 10.0.0.12 secondary
 standby 20 ipv6 10::11/64
""")

        self.compare("""
interface Eth1/1
 vrf forwarding TestVRF
!
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
!
interface Eth1/1
 ipv6 address 10::1/64
!
interface Eth1/1
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
!
interface Eth1/1
 standby 10 ip 10.0.0.11
!
interface Eth1/1
 standby 10 ip 10.0.0.12 secondary
!
interface Eth1/1
 standby 20 ipv6 10::11/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_VrfFwd_IP_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF
 ip address 10.0.0.1 255.255.255.0
 ipv6 address 10::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
 standby 10 ip 10.0.0.11
 standby 10 ip 10.0.0.12 secondary
 standby 20 ipv6 10::11/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
 ipv6 address 10::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
 standby 10 ip 10.0.0.11
 standby 10 ip 10.0.0.12 secondary
 standby 20 ipv6 10::11/64
""")

        self.compare("""
interface Eth1/1
 no vrf forwarding
!
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
!
interface Eth1/1
 ipv6 address 10::1/64

interface Eth1/1
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
!
interface Eth1/1
 standby 10 ip 10.0.0.11
!
interface Eth1/1
 standby 10 ip 10.0.0.12 secondary
!
interface Eth1/1
 standby 20 ipv6 10::11/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_VrfFwd_IP_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF1
 ip address 10.0.0.1 255.255.255.0
 ipv6 address 10::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
 standby 10 ip 10.0.0.11
 standby 10 ip 10.0.0.12 secondary
 standby 20 ipv6 10::11/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF2
 ip address 10.0.0.1 255.255.255.0
 ipv6 address 10::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
 standby 10 ip 10.0.0.11
 standby 10 ip 10.0.0.12 secondary
 standby 20 ipv6 10::11/64
""")

        self.compare("""
interface Eth1/1
 vrf forwarding TestVRF2
!
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
!
interface Eth1/1
 ipv6 address 10::1/64

interface Eth1/1
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
!
interface Eth1/1
 standby 10 ip 10.0.0.11
!
interface Eth1/1
 standby 10 ip 10.0.0.12 secondary
!
interface Eth1/1
 standby 20 ipv6 10::11/64
""")


    # =========================================================================
    # interface ...
    #  arp timeout ...
    # =========================================================================


    def test_Interface_ARPTime_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 arp timeout 900
""")

        self.compare("""
interface Eth1/1
 arp timeout 900
""")


    # -------------------------------------------------------------------------


    def test_Interface_ARPTime_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 arp timeout 900
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no arp timeout
""")


    # -------------------------------------------------------------------------


    def test_Interface_ARPTime_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 arp timeout 900
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 arp timeout 600
""")

        self.compare("""
interface Eth1/1
 arp timeout 600
""")


    # =========================================================================
    # interface ...
    #  cdp enable
    # =========================================================================


    def test_Interface_CDPEna_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 cdp enable
""")

        self.compare("""
interface Eth1/1
 cdp enable
""")


    # -------------------------------------------------------------------------


    def test_Interface_CDPEna_remove_ena(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 cdp enable
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("")


    # -------------------------------------------------------------------------


    def test_Interface_CDPEna_remove_noena(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 no cdp enable
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 cdp enable
""")


    # =========================================================================
    # interface ...
    #  channel-group ...
    # =========================================================================


    def test_Interface_ChnGrp_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 channel-group 10 mode active
""")

        self.compare("""
interface Eth1/1
 channel-group 10 mode active
""")


    # -------------------------------------------------------------------------


    def test_Interface_ChnGrp_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 channel-group 10 mode active
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no channel-group
""")


    # -------------------------------------------------------------------------


    def test_Interface_ChnGrp_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 channel-group 10 mode active
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 channel-group 20
""")

        self.compare("""
interface Eth1/1
 channel-group 20
""")


    # =========================================================================
    # interface ...
    #  description ...
    # =========================================================================


    def test_Interface_Desc_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 description Test Interface Description
""")

        self.compare("""
interface Eth1/1
 description Test Interface Description
""")


    # -------------------------------------------------------------------------


    def test_Interface_Desc_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 description Test Interface Description
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no description
""")


    # -------------------------------------------------------------------------


    def test_Interface_Desc_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 description Test Interface Description 1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 description Test Interface Description 2
""")

        self.compare("""
interface Eth1/1
 description Test Interface Description 2
""")


    # =========================================================================
    # interface ...
    #  encapsulation ...
    # =========================================================================


    def test_Interface_Encap_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1.100
""")

        self.new_cfg.parse_str("""
interface Eth1/1.100
 encapsulation dot1q 100
""")

        self.compare("""
interface Eth1/1.100
 encapsulation dot1q 100
""")


    # -------------------------------------------------------------------------


    def test_Interface_Encap_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1.100
 encapsulation dot1q 100
""")

        self.new_cfg.parse_str("""
interface Eth1/1.100
""")

        self.compare("""
interface Eth1/1.100
 no encapsulation dot1q 100
""")


    # -------------------------------------------------------------------------


    def test_Interface_Encap_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1.100
 encapsulation dot1q 100
""")

        self.new_cfg.parse_str("""
interface Eth1/1.100
 encapsulation dot1q 200 native
""")

        self.compare("""
interface Eth1/1.100
 encapsulation dot1q 200 native
""")


    # =========================================================================
    # interface ...
    #  ip access-group ...
    # =========================================================================


    def test_Interface_IPAccGrp_add_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip access-group 101 in
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip access-group 101 in
 ip access-group 102 out
""")

        self.compare("""
interface Eth1/1
 ip access-group 102 out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAccGrp_add_both(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip access-group 101 in
 ip access-group 102 out
""")

        self.compare("""
interface Eth1/1
 ip access-group 101 in
!
interface Eth1/1
 ip access-group 102 out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAccGrp_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip access-group 101 in
 ip access-group 102 out
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip access-group 101 in
""")

        self.compare("""
interface Eth1/1
 no ip access-group out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAccGrp_remove_both(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip access-group 101 in
 ip access-group 102 out
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip access-group in
!
interface Eth1/1
 no ip access-group out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAccGrp_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1.100
 ip access-group 101 in
""")

        self.new_cfg.parse_str("""
interface Eth1/1.100
 ip access-group 102 in
""")

        self.compare("""
interface Eth1/1.100
 ip access-group 102 in
""")


    # =========================================================================
    # interface ...
    #  ip address ...
    # =========================================================================


    def test_Interface_IPAddr_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
""")

        self.compare("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAddr_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip address
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAddr_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip address 20.0.0.1 255.255.255.0
""")

        self.compare("""
interface Eth1/1
 ip address 20.0.0.1 255.255.255.0
""")


    # =========================================================================
    # interface ...
    #  ip address ... secondary
    # =========================================================================


    def test_Interface_IPAddrSec_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
 ip address 20.0.0.1 255.255.0.0 secondary
""")

        self.compare("""
interface Eth1/1
 ip address 20.0.0.1 255.255.0.0 secondary
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAddrSec_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
 ip address 20.0.0.1 255.255.0.0 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
""")

        self.compare("""
interface Eth1/1
 no ip address 20.0.0.1 255.255.0.0 secondary
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPAddrSec_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
 ip address 21.0.0.1 255.255.0.0 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip address 10.0.0.1 255.255.255.0
 ip address 22.0.0.1 255.255.0.0 secondary
""")

        self.compare("""
interface Eth1/1
 no ip address 21.0.0.1 255.255.0.0 secondary
!
interface Eth1/1
 ip address 22.0.0.1 255.255.0.0 secondary
""")


    # =========================================================================
    # interface ...
    #  ip flow monitor ...
    # =========================================================================


    def test_Interface_IPFlowMon_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip flow monitor TestFlowMonIn input
 ip flow monitor TestFlowMonOut output
""")

        self.compare("""
interface Eth1/1
 ip flow monitor TestFlowMonIn input
!
interface Eth1/1
 ip flow monitor TestFlowMonOut output
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPFlowMon_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip flow monitor TestFlowMonIn input
 ip flow monitor TestFlowMonOut output
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip flow monitor TestFlowMonIn input
!
interface Eth1/1
 no ip flow monitor TestFlowMonOut output
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPFlowMon_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip flow monitor TestFlowMonIn1 input
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip flow monitor TestFlowMonIn2 input
""")

        self.compare("""
interface Eth1/1
 no ip flow monitor TestFlowMonIn1 input
 ip flow monitor TestFlowMonIn2 input
""")


    # =========================================================================
    # interface ...
    #  ip helper-address ...
    # =========================================================================


    def test_Interface_IPHlprAddr_add_new(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 ip helper-address 10.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_add_multi(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
 ip helper-address 20.0.0.1
""")

        self.compare("""
interface Eth1/1
 ip helper-address 10.0.0.1
!
interface Eth1/1
 ip helper-address 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_add_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
 ip helper-address 20.0.0.1
""")

        self.compare("""
interface Eth1/1
 ip helper-address 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_add_global(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address global 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 ip helper-address global 10.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_add_vrf(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address vrf TestVRF 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 ip helper-address vrf TestVRF 10.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
 ip helper-address 20.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no ip helper-address 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
 ip helper-address 20.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip helper-address 10.0.0.1
!
interface Eth1/1
 no ip helper-address 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip helper-address 20.0.0.1
""")

        self.compare("""
interface Eth1/1
 no ip helper-address 10.0.0.1
!
interface Eth1/1
 ip helper-address 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPHlprAddr_trigger_vrf(self):
        # the helper address itself does not change but the VRF does,
        # requiring us to remove and re-add the helper address to avoid
        # it being altered to reference the previous VRF

        self.old_cfg.parse_str("""
interface Eth1/1
 ip helper-address 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 vrf forwarding TestVRF
 ip helper-address 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no ip helper-address 10.0.0.1
!
interface Eth1/1
 vrf forwarding TestVRF
!
interface Eth1/1
 ip helper-address 10.0.0.1
""")


    # =========================================================================
    # interface ...
    #  ip igmp version ...
    # =========================================================================


    def test_Interface_IPIGMPVer_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip igmp version 3
""")

        self.compare("""
interface Eth1/1
 ip igmp version 3
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPIGMPVer_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip igmp version 3
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip igmp version
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPIGMPVer_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip igmp version 2
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip igmp version 3
""")

        self.compare("""
interface Eth1/1
 ip igmp version 3
""")


    # =========================================================================
    # interface ...
    #  ip multicast boundary ...
    # =========================================================================


    def test_Interface_IPMcastBdry_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip multicast boundary TestMulticastACL
""")

        self.compare("""
interface Eth1/1
 ip multicast boundary TestMulticastACL
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPMcastBdry_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip multicast boundary TestMulticastACL
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip multicast boundary
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPMcastBdry_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip multicast boundary TestMulticastACL1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip multicast boundary TestMulticastACL2
""")

        self.compare("""
interface Eth1/1
 ip multicast boundary TestMulticastACL2
""")


    # =========================================================================
    # interface ...
    #  ip ospf ... area ...
    # =========================================================================


    def test_Interface_IPOSPFArea_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf 1 area 1.0.0.0
""")

        self.compare("""
interface Eth1/1
 ip ospf 1 area 1.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFArea_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf 1 area 1.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf 1 area 1.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFArea_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf 1 area 1.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf 1 area 2.0.0.0
""")

        self.compare("""
interface Eth1/1
 ip ospf 1 area 2.0.0.0
""")


    # =========================================================================
    # interface ...
    #  ip ospf authentication ...
    # =========================================================================


    def test_Interface_IPOSPFAuth_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf authentication message-digest
 """)

        self.compare("""
interface Eth1/1
 ip ospf authentication message-digest
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFAuth_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf authentication message-digest
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf authentication
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFAuth_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf authentication message-digest
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf authentication null
""")

        self.compare("""
interface Eth1/1
 ip ospf authentication null
""")


    # =========================================================================
    # interface ...
    #  ip ospf cost ...
    # =========================================================================


    def test_Interface_IPOSPFCost_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf cost 10
""")

        self.compare("""
interface Eth1/1
 ip ospf cost 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFCost_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf cost 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf cost
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFCost_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf cost 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf cost 20
""")

        self.compare("""
interface Eth1/1
 ip ospf cost 20
""")


    # =========================================================================
    # interface ...
    #  ip ospf dead-interval ...
    # =========================================================================


    def test_Interface_IPOSPFDeadIvl_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf dead-interval 30
""")

        self.compare("""
interface Eth1/1
 ip ospf dead-interval 30
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFDeadIvl_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf dead-interval 30
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf dead-interval
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFDeadIvl_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf dead-interval 30
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf dead-interval 40
""")

        self.compare("""
interface Eth1/1
 ip ospf dead-interval 40
""")


    # =========================================================================
    # interface ...
    #  ip ospf hello-interval ...
    # =========================================================================


    def test_Interface_IPOSPFHelloIvl_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf hello-interval 10
""")

        self.compare("""
interface Eth1/1
 ip ospf hello-interval 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFHelloIvl_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf hello-interval 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf hello-interval
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFHelloIvl_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf hello-interval 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf hello-interval 20
""")

        self.compare("""
interface Eth1/1
 ip ospf hello-interval 20
""")


    # =========================================================================
    # interface ...
    #  ip ospf message-digest-key ...
    # =========================================================================


    def test_Interface_IPOSPFMsgDigKey_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf message-digest-key 10 md5 TestOSPFKey1
 ip ospf message-digest-key 20 md5 TestOSPFKey2
""")

        self.compare("""
interface Eth1/1
 ip ospf message-digest-key 10 md5 TestOSPFKey1
!
interface Eth1/1
 ip ospf message-digest-key 20 md5 TestOSPFKey2
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFMsgDigKey_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf message-digest-key 10 md5 TestOSPFKey
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf message-digest-key 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFMsgDigKey_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf message-digest-key 10 md5 TestOSPFKey1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf message-digest-key 10 md5 TestOSPFKey2
""")

        self.compare("""
interface Eth1/1
 ip ospf message-digest-key 10 md5 TestOSPFKey2
""")


    # =========================================================================
    # interface ...
    #  ip ospf network ...
    # =========================================================================


    def test_Interface_IPOSPFNet_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf network point-to-point
""")

        self.compare("""
interface Eth1/1
 ip ospf network point-to-point
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFNet_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf network point-to-point
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip ospf network
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPOSPFNet_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip ospf network point-to-point
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip ospf network broadcast
""")

        self.compare("""
interface Eth1/1
 ip ospf network broadcast
""")


    # =========================================================================
    # interface ...
    #  ip pim ...-mode
    # =========================================================================


    def test_Interface_IPPIMMode_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip pim sparse-mode
""")

        self.compare("""
interface Eth1/1
 ip pim sparse-mode
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPPIMMode_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip pim sparse-mode
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip pim sparse-mode
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPPIMMode_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip pim sparse-mode
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip pim dense-mode
""")

        self.compare("""
interface Eth1/1
 ip pim dense-mode
""")


    # =========================================================================
    # interface ...
    #  ip pim bsr-border
    # =========================================================================


    def test_Interface_IPPIMBSRBdr_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip pim bsr-border
""")

        self.compare("""
interface Eth1/1
 ip pim bsr-border
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPPIMBSRBdr_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip pim bsr-border
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip pim bsr-border
""")


    # =========================================================================
    # interface ...
    #  ip policy route-map ...
    # =========================================================================


    def test_Interface_IPPolicyRtMap_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip policy route-map TestRouteMap
""")

        self.compare("""
interface Eth1/1
 ip policy route-map TestRouteMap
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPPolicyRtMap_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip policy route-map TestRouteMap
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip policy route-map
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPPolicyRtMap_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip policy route-map TestRouteMap1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip policy route-map TestRouteMap2
""")

        self.compare("""
interface Eth1/1
 ip policy route-map TestRouteMap2
""")


    # =========================================================================
    # interface ...
    #  ip proxy-arp
    # =========================================================================


    def test_Interface_IPProxyARP_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 no ip proxy-arp
""")

        self.compare("""
interface Eth1/1
 no ip proxy-arp
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPProxyARP_remove_yes(self):
        # proxy-arp enabled is the default

        self.old_cfg.parse_str("""
interface Eth1/1
 ip proxy-arp
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("")


    # -------------------------------------------------------------------------


    def test_Interface_IPProxyARP_remove_no(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 no ip proxy-arp
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 ip proxy-arp
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPProxyARP_update_yes(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 no ip proxy-arp
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip proxy-arp
""")

        self.compare("""
interface Eth1/1
 ip proxy-arp
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPProxyARP_update_no(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip proxy-arp
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 no ip proxy-arp
""")

        self.compare("""
interface Eth1/1
 no ip proxy-arp
""")


    # =========================================================================
    # interface ...
    #  ip verify unicast ...
    # =========================================================================


    def test_Interface_IPVerifyUni_add_rx(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip verify unicast source reachable-via rx
""")

        self.compare("""
interface Eth1/1
 ip verify unicast source reachable-via rx
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPVerifyUni_add_acl(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ip verify unicast source reachable-via rx 100
""")

        self.compare("""
interface Eth1/1
 ip verify unicast source reachable-via rx 100
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPVerifyUni_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ip verify unicast source reachable-via rx
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ip verify unicast
""")


    # =========================================================================
    # interface ...
    #  ipv6 address ...
    # =========================================================================


    def test_Interface_IPv6Addr_add_first(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.compare("""
interface Eth1/1
 ipv6 address 100::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_add_only(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 address 200::1/64
""")

        self.compare("""
interface Eth1/1
 ipv6 address 200::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_add_multi(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 address 200::1/64
""")

        self.compare("""
interface Eth1/1
 ipv6 address 100::1/64
!
interface Eth1/1
 ipv6 address 200::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_remove_only(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 address 100::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 address 200::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.compare("""
interface Eth1/1
 no ipv6 address 200::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_remove_multi(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 address 200::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 address 100::1/64
!
interface Eth1/1
 no ipv6 address 200::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_update_addremove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 address 200::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 200::1/64
 ipv6 address 300::1/64
""")

        self.compare("""
interface Eth1/1
 no ipv6 address 100::1/64
!
interface Eth1/1
 ipv6 address 300::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6Addr_update_multi(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 address 200::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 300::1/64
 ipv6 address 400::1/64
""")

        self.compare("""
interface Eth1/1
 no ipv6 address 100::1/64
!
interface Eth1/1
 no ipv6 address 200::1/64
!
interface Eth1/1
 ipv6 address 300::1/64
!
interface Eth1/1
 ipv6 address 400::1/64
""")


    # =========================================================================
    # interface ...
    #  ipv6 multicast boundary scope ...
    # =========================================================================


    def test_Interface_IPv6MultBdry_add_numeric(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope 5
""")

        self.compare("""
interface Eth1/1
 ipv6 multicast boundary scope 5
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6MultBdry_add_named(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope site-local
""")

        self.compare("""
interface Eth1/1
 ipv6 multicast boundary scope 5
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6MultBdry_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope 5
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 multicast boundary scope
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6MultBdry_update_diff(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope 5
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope 8
""")

        self.compare("""
interface Eth1/1
 ipv6 multicast boundary scope 8
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6MultBdry_update_equiv(self):
        # confirm no change - just number for name

        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope 8
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 multicast boundary scope organization-local
""")

        self.compare("")


    # =========================================================================
    # interface ...
    #  ipv6 nd prefix ...
    # =========================================================================


    def test_Interface_IPv6NDPfx_add_lifetime(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 604800 86400
""")

        self.compare("""
interface Eth1/1
 ipv6 nd prefix 100::/64 604800 86400
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6NDPfx_add_at(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
""")

        self.compare("""
interface Eth1/1
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6NDPfx_remove_lifetime(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 604800 86400
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.compare("""
interface Eth1/1
 no ipv6 nd prefix 100::/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6NDPfx_remove_at(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
""")

        self.compare("""
interface Eth1/1
 no ipv6 nd prefix 100::/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6NDPfx_update_at(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 at 11 feb 2020 12:00 12 mar 2020 10:00
""")

        self.compare("""
interface Eth1/1
 ipv6 nd prefix 100::/64 at 11 feb 2020 12:00 12 mar 2020 10:00
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6NDPfx_update_convert(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 604800 86400
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
""")

        self.compare("""
interface Eth1/1
 ipv6 nd prefix 100::/64 at 1 feb 2020 12:00 2 mar 2020 10:00
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6NDPfx_update_canonical(self):
        # no change as only affecting the case of the date and prefix
        # and leading zeros on the month
        # TODO: hours/minutes canoni

        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100:abcd::/64 at 1 Feb 2020 12:00 2 Mar 2020 10:00
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 address 100::1/64
 ipv6 nd prefix 100:ABCD::/64 at 01 feb 2020 12:00 02 mar 2020 10:00
""")

        self.compare("")


    # =========================================================================
    # interface ...
    #  ipv6 pim bsr-border
    # =========================================================================


    def test_Interface_IPv6PIMBSRBdr_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 pim bsr border
""")

        self.compare("""
interface Eth1/1
 ipv6 pim bsr border
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6PIMBSRBdr_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 pim bsr border
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 pim bsr border
""")


    # =========================================================================
    # interface ...
    #  ipv6 policy route-map ...
    # =========================================================================


    def test_Interface_IPv6PolicyRtMap_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 policy route-map TestRouteMap
""")

        self.compare("""
interface Eth1/1
 ipv6 policy route-map TestRouteMap
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6PolicyRtMap_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 policy route-map TestRouteMap
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 policy route-map
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6PolicyRtMap_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 policy route-map TestRouteMap1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 policy route-map TestRouteMap2
""")

        self.compare("""
interface Eth1/1
 ipv6 policy route-map TestRouteMap2
""")


    # =========================================================================
    # interface ...
    #  ipv6 traffic-filter ...
    # =========================================================================


    def test_Interface_IPv6TrafFilt_add_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
 ipv6 traffic-filter TestACL2 out
""")

        self.compare("""
interface Eth1/1
 ipv6 traffic-filter TestACL2 out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6TrafFilt_add_both(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
 ipv6 traffic-filter TestACL2 out
""")

        self.compare("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
!
interface Eth1/1
 ipv6 traffic-filter TestACL2 out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6TrafFilt_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
 ipv6 traffic-filter TestACL2 out
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
""")

        self.compare("""
interface Eth1/1
 no ipv6 traffic-filter out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6TrafFilt_remove_both(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 traffic-filter TestACL1 in
 ipv6 traffic-filter TestACL2 out
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 traffic-filter in
!
interface Eth1/1
 no ipv6 traffic-filter out
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6TrafFilt_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1.100
 ipv6 traffic-filter TestACL1 in
""")

        self.new_cfg.parse_str("""
interface Eth1/1.100
 ipv6 traffic-filter TestACL2 in
""")

        self.compare("""
interface Eth1/1.100
 ipv6 traffic-filter TestACL2 in
""")


    # =========================================================================
    # interface ...
    #  ipv6 verify unicast ...
    # =========================================================================


    def test_Interface_IPv6VerifyUni_add_rx(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 verify unicast source reachable-via rx
""")

        self.compare("""
interface Eth1/1
 ipv6 verify unicast source reachable-via rx
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6VerifyUni_add_acl(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ipv6 verify unicast source reachable-via rx TestACL
""")

        self.compare("""
interface Eth1/1
 ipv6 verify unicast source reachable-via rx TestACL
""")


    # -------------------------------------------------------------------------


    def test_Interface_IPv6VerifyUni_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ipv6 verify unicast source reachable-via rx
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ipv6 verify unicast
""")


    # =========================================================================
    # interface ...
    #  mpls ip
    # =========================================================================


    def test_Interface_MPLSIP_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 mpls ip
""")

        self.compare("""
interface Eth1/1
 mpls ip
""")


    # -------------------------------------------------------------------------


    def test_Interface_MPLSIP_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 mpls ip
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no mpls ip
""")


    # =========================================================================
    # interface ...
    #  mtu
    # =========================================================================


    def test_Interface_MTU_add_plain(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 mtu 9000
""")

        self.compare("""
interface Eth1/1
 mtu 9000
""")


    # -------------------------------------------------------------------------


    def test_Interface_MTU_add_chngrp(self):
        # MTU set on interface that is a member of a channel-group
        # should be ignored (as set on port-channel interface)

        self.old_cfg.parse_str("""
interface Eth1/1
 channel-group 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 channel-group 10
 mtu 9000
""")

        self.compare("")


    # -------------------------------------------------------------------------


    def test_Interface_MTU_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 mtu 9000
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no mtu
""")


    # -------------------------------------------------------------------------


    def test_Interface_MTU_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 mtu 9000
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 mtu 5000
""")

        self.compare("""
interface Eth1/1
 mtu 5000
""")


    # =========================================================================
    # interface ...
    #  ospfv3 ... area ...
    # =========================================================================


    def test_Interface_OSPv3FArea_add_first(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
""")

        self.compare("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPv3FArea_add_extra(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
 ospfv3 1 ipv6 area 1.0.0.0
""")

        self.compare("""
interface Eth1/1
 ospfv3 1 ipv6 area 1.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPv3FArea_add_multi(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
 ospfv3 2 ipv6 area 2.0.0.0
""")

        self.compare("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
!
interface Eth1/1
 ospfv3 2 ipv6 area 2.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Area_remove_only(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ospfv3 1 ipv4 area 1.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Area_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
 ospfv3 2 ipv6 area 2.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
""")

        self.compare("""
interface Eth1/1
 no ospfv3 2 ipv6 area 2.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Area_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
 ospfv3 2 ipv6 area 2.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ospfv3 1 ipv4 area 1.0.0.0
!
interface Eth1/1
 no ospfv3 2 ipv6 area 2.0.0.0
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Area_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 1.0.0.0
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 1 ipv4 area 2.0.0.0
""")

        self.compare("""
interface Eth1/1
 ospfv3 1 ipv4 area 2.0.0.0
""")


    # =========================================================================
    # interface ...
    #  ospfv3 cost ...
    # =========================================================================


    def test_Interface_OSPFv3Cost_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 cost 10
""")

        self.compare("""
interface Eth1/1
 ospfv3 cost 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Cost_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 cost 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ospfv3 cost
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Cost_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 cost 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 cost 20
""")

        self.compare("""
interface Eth1/1
 ospfv3 cost 20
""")


    # =========================================================================
    # interface ...
    #  ospfv3 dead-interval ...
    # =========================================================================


    def test_Interface_OSPFv3DeadIvl_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 dead-interval 30
""")

        self.compare("""
interface Eth1/1
 ospfv3 dead-interval 30
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3DeadIvl_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 dead-interval 30
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ospfv3 dead-interval
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3DeadIvl_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 dead-interval 30
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 dead-interval 40
""")

        self.compare("""
interface Eth1/1
 ospfv3 dead-interval 40
""")


    # =========================================================================
    # interface ...
    #  ospfv3 hello-interval ...
    # =========================================================================


    def test_Interface_OSPFv3HelloIvl_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 hello-interval 10
""")

        self.compare("""
interface Eth1/1
 ospfv3 hello-interval 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3HelloIvl_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 hello-interval 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ospfv3 hello-interval
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3HelloIvl_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 hello-interval 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 hello-interval 20
""")

        self.compare("""
interface Eth1/1
 ospfv3 hello-interval 20
""")


    # =========================================================================
    # interface ...
    #  ospfv3 network ...
    # =========================================================================


    def test_Interface_OSPFv3Net_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 network point-to-point
""")

        self.compare("""
interface Eth1/1
 ospfv3 network point-to-point
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Net_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 network point-to-point
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no ospfv3 network
""")


    # -------------------------------------------------------------------------


    def test_Interface_OSPFv3Net_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 ospfv3 network point-to-point
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 ospfv3 network broadcast
""")

        self.compare("""
interface Eth1/1
 ospfv3 network broadcast
""")


    # =========================================================================
    # interface ...
    #  service-policy ...
    # =========================================================================


    def test_Interface_ServPol_add_lanqueue(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy
""")

        self.compare("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy
""")


    # -------------------------------------------------------------------------


    def test_Interface_ServPol_add_police(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 service-policy input TestServicePolicy
""")

        self.compare("""
interface Eth1/1
 service-policy input TestServicePolicy
""")


    # -------------------------------------------------------------------------
    def test_Interface_ServPol_add_both(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
 service-policy type lan-queuing output TestServicePolicy2
""")

        self.compare("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
!
interface Eth1/1
 service-policy type lan-queuing output TestServicePolicy2
""")


    # -------------------------------------------------------------------------


    def test_Interface_ServPol_add_extra(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
 service-policy type lan-queuing output TestServicePolicy2
""")

        self.compare("""
interface Eth1/1
 service-policy type lan-queuing output TestServicePolicy2
""")


    # -------------------------------------------------------------------------


    def test_Interface_ServPol_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
 service-policy type lan-queuing output TestServicePolicy2
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
""")

        self.compare("""
interface Eth1/1
 no service-policy type lan-queuing output TestServicePolicy2
""")


    # -------------------------------------------------------------------------


    def test_Interface_ServPol_remove_both(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 service-policy type lan-queuing input TestServicePolicy1
 service-policy type lan-queuing output TestServicePolicy2
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no service-policy type lan-queuing input TestServicePolicy1
!
interface Eth1/1
 no service-policy type lan-queuing output TestServicePolicy2
""")


    # =========================================================================
    # interface ...
    #  standby ... ip ...
    # =========================================================================


    def test_Interface_StandbyIP_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 82 ip 20.0.0.1
""")

        self.compare("""
interface Eth1/1
 standby 81 ip 10.0.0.1
!
interface Eth1/1
 standby 82 ip 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIP_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 82 ip 20.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 82 ip
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIP_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 82 ip 20.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip
!
interface Eth1/1
 no standby 82 ip
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIP_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 20.0.0.1
""")

        self.compare("""
interface Eth1/1
 standby 81 ip 20.0.0.1
""")


    # =========================================================================
    # interface ...
    #  standby ... ip ... secondary
    # =========================================================================


    def test_Interface_StandbyIPSec_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
 standby 81 ip 30.0.0.1 secondary
""")

        self.compare("""
interface Eth1/1
 standby 81 ip 20.0.0.1 secondary
!
interface Eth1/1
 standby 81 ip 30.0.0.1 secondary
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPSec_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
 standby 81 ip 30.0.0.1 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip 30.0.0.1 secondary
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPSec_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
 standby 81 ip 30.0.0.1 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip 20.0.0.1 secondary
!
interface Eth1/1
 no standby 81 ip 30.0.0.1 secondary
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPSec_update(self):
        # change a secondary address

        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 30.0.0.1 secondary
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip 20.0.0.1 secondary
!
interface Eth1/1
 standby 81 ip 30.0.0.1 secondary
""")


    # =========================================================================
    # interface ...
    #  standby ... ip ...
    #  standby ... ip ... secondary
    # =========================================================================


    def test_Interface_StandbyIPandSec_update_promote(self):
        # promote a secondary address to primary
        #
        # this requires that the secondary is removed first

        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 20.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip 20.0.0.1 secondary
!
interface Eth1/1
 standby 81 ip 20.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPandSec_update_demote(self):
        # demote the primary address to a secondary (adding a new
        # primary, but this is not checked for)
        #
        # this requires that the new primary is installed first and then
        # the old one added as a secondary

        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 20.0.0.1
 standby 81 ip 10.0.0.1 secondary
""")

        self.compare("""
interface Eth1/1
 standby 81 ip 20.0.0.1
!
interface Eth1/1
 standby 81 ip 10.0.0.1 secondary
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPandSec_update_swap(self):
        # swap the primary and a secondary address
        #
        # this requires that the old secondary is removed first, then
        # the primary changed and then the old primary configured as the
        # secondary

        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 ip 20.0.0.1 secondary
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 20.0.0.1
 standby 81 ip 10.0.0.1 secondary
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip 20.0.0.1 secondary
!
interface Eth1/1
 standby 81 ip 20.0.0.1
!
interface Eth1/1
 standby 81 ip 10.0.0.1 secondary
""")


    # =========================================================================
    # interface ...
    #  standby ... ipv6 ...
    # =========================================================================


    def test_Interface_StandbyIPv6_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ipv6 10::1/64
 standby 81 ipv6 20::1/64
 standby 82 ipv6 30::1/64
""")

        self.compare("""
interface Eth1/1
 standby 81 ipv6 10::1/64
!
interface Eth1/1
 standby 81 ipv6 20::1/64
!
interface Eth1/1
 standby 82 ipv6 30::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPv6_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ipv6 10::1/64
 standby 81 ipv6 20::1/64
 standby 82 ipv6 30::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ipv6 10::1/64
 standby 82 ipv6 30::1/64
""")

        self.compare("""
interface Eth1/1
 no standby 81 ipv6 20::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPv6_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ipv6 10::1/64
 standby 81 ipv6 20::1/64
 standby 82 ipv6 30::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no standby 81 ipv6 10::1/64
!
interface Eth1/1
 no standby 81 ipv6 20::1/64
!
interface Eth1/1
 no standby 82 ipv6 30::1/64
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyIPv6_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ipv6 10::1/64
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ipv6 20::1/64
""")

        self.compare("""
interface Eth1/1
 no standby 81 ipv6 10::1/64
!
interface Eth1/1
 standby 81 ipv6 20::1/64
""")


    # =========================================================================
    # interface ...
    #  standby ... preempt
    # =========================================================================


    def test_Interface_StandbyPreempt_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 preempt
""")

        self.compare("""
interface Eth1/1
 standby 81 preempt
""")


    # -------------------------------------------------------------------------



    def test_Interface_StandbyPreempt_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 preempt
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 preempt
""")


    # =========================================================================
    # interface ...
    #  standby ... priority ...
    # =========================================================================


    def test_Interface_StandbyPri_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 priority 200
""")

        self.compare("""
interface Eth1/1
 standby 81 priority 200
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyPri_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 priority 200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 priority
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyPri_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 priority 200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 priority 210
""")

        self.compare("""
interface Eth1/1
 standby 81 priority 210
""")


    # =========================================================================
    # interface ...
    #  standby ... timers ...
    # =========================================================================


    def test_Interface_StandbyTimers_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 timers 3 10
""")

        self.compare("""
interface Eth1/1
 standby 81 timers 3 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyTimers_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 timers 3 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 timers
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyTimers_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 timers 3 10
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 timers 2 6
""")

        self.compare("""
interface Eth1/1
 standby 81 timers 2 6
""")


    # =========================================================================
    # interface ...
    #  standby ... track ...
    # =========================================================================


    def test_Interface_StandbyTrk_add_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 track 10 decrement 50
""")

        self.compare("""
interface Eth1/1
 standby 81 track 10 decrement 50
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyTrk_add_multi(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 track 10 decrement 50
 standby 81 track 20 decrement 30
""")

        self.compare("""
interface Eth1/1
 standby 81 track 10 decrement 50
!
interface Eth1/1
 standby 81 track 20 decrement 30
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyTrk_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 track 10 decrement 50
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 track 10
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyTrk_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 track 10 decrement 50
 standby 81 track 20 decrement 30
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby 81 track 10
!
interface Eth1/1
 no standby 81 track 20
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyTrk_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 track 10 decrement 50
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby 81 track 10 decrement 20
""")

        self.compare("""
interface Eth1/1
 standby 81 track 10 decrement 20
""")


    # =========================================================================
    # interface ...
    #  standby version ...
    # =========================================================================


    def test_Interface_StandbyVer_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby version 2
""")

        self.compare("""
interface Eth1/1
 standby version 2
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyVer_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
 standby version 2
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 no standby version
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyVer_update_1to2(self):
        # switching from 1 to 2, we do that BEFORE we add any new groups
        # in case they're using high numbers invalid with version 1
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 standby version 2
 standby 81 ip 10.0.0.1
""")

        self.compare("""
interface Eth1/1
 standby version 2
!
interface Eth1/1
 standby 81 ip 10.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_Interface_StandbyVer_update_2to1(self):
        # when switching from 2 to 1, we must do this AFTER we remove
        # any groups being deleted, in case they have high group numbers
        # that are incompatible with version 1

        self.old_cfg.parse_str("""
interface Eth1/1
 standby version 2
 standby 81 ip 10.0.0.1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no standby 81 ip
!
interface Eth1/1
 no standby version
""")


    # =========================================================================
    # interface ...
    #  storm-control ... level ...
    # =========================================================================


    def test_Interface_StormCtrl_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 storm-control broadcast level 5.00
 storm-control multicast level 10.00
""")

        self.compare("""
interface Eth1/1
 storm-control broadcast level 5.00
!
interface Eth1/1
 storm-control multicast level 10.00
""")


    # -------------------------------------------------------------------------


    def test_Interface_StormCtrl_remove_one(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 storm-control broadcast level 5.00
 storm-control multicast level 10.00
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 storm-control broadcast level 5.00
""")

        self.compare("""
interface Eth1/1
 no storm-control multicast level
""")


    # -------------------------------------------------------------------------


    def test_Interface_StormCtrl_remove_all(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 storm-control broadcast level 5.00
 storm-control multicast level 10.00
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no storm-control broadcast level
!
interface Eth1/1
 no storm-control multicast level
""")


    # -------------------------------------------------------------------------


    def test_Interface_StormCtrl_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 storm-control broadcast level 5.00
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 storm-control broadcast level 10.00
""")

        self.compare("""
interface Eth1/1
 storm-control broadcast level 10.00
""")


    # =========================================================================
    # interface ...
    #  switchport
    # =========================================================================


    def test_Interface_SwPort_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport
""")

        self.compare("""
interface Eth1/1
 switchport
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPort_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no switchport
""")


    # =========================================================================
    # interface ...
    #  switchport mode ...
    # =========================================================================


    def test_Interface_SwPortMode_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport mode trunk
""")

        self.compare("""
interface Eth1/1
 switchport mode trunk
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortMode_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport mode trunk
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no switchport mode
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortMode_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport mode trunk
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport mode access
""")

        self.compare("""
interface Eth1/1
 switchport mode access
""")


    # =========================================================================
    # interface ...
    #  switchport nonegotiate
    # =========================================================================


    def test_Interface_SwPortNoNeg_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport nonegotiate
""")

        self.compare("""
interface Eth1/1
 switchport nonegotiate
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortNoNeg_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport nonegotiate
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no switchport nonegotiate
""")


    # =========================================================================
    # interface ...
    #  switchport trunk native vlan ...
    # =========================================================================


    def test_Interface_SwPortTrkNtv_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk native vlan 100
""")

        self.compare("""
interface Eth1/1
 switchport trunk native vlan 100
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkNtv_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk native vlan 100
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no switchport trunk native vlan
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkNtv_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk native vlan 100
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk native vlan 200
""")

        self.compare("""
interface Eth1/1
 switchport trunk native vlan 200
""")


    # =========================================================================
    # interface ...
    #  switchport trunk allowed vlan ...
    # =========================================================================


    def test_Interface_SwPortTrkAlw_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200
""")

        self.compare("""
interface Eth1/1
 switchport trunk allowed vlan none
 switchport trunk allowed vlan add 100
 switchport trunk allowed vlan add 200
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkAlw_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no switchport trunk allowed vlan
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkAlw_truncate(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100
""")

        self.compare("""
interface Eth1/1
 switchport trunk allowed vlan remove 200
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkAlw_update_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200,300
""")

        self.compare("""
interface Eth1/1
 switchport trunk allowed vlan add 300
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkAlw_update_none(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan none
""")

        self.compare("""
interface Eth1/1
 switchport trunk allowed vlan remove 100
 switchport trunk allowed vlan remove 200
""")


    # -------------------------------------------------------------------------


    def test_Interface_SwPortTrkAlw_truncate_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 100,200
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 switchport trunk allowed vlan 200,300
""")

        self.compare("""
interface Eth1/1
 switchport trunk allowed vlan remove 100
!
interface Eth1/1
 switchport trunk allowed vlan add 300
""")


    # =========================================================================
    # interface ...
    #  port-channel min-links ...
    # =========================================================================


    def test_Interface_PcMinLinks_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 port-channel min-links 2
""")

        self.compare("""
interface Eth1/1
 port-channel min-links 2
""")


    # -------------------------------------------------------------------------


    def test_Interface_PcMinLinks_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 port-channel min-links 2
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no port-channel min-links
""")


    # -------------------------------------------------------------------------


    def test_Interface_PcMinLinks_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 port-channel min-links 2
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 port-channel min-links 3
""")

        self.compare("""
interface Eth1/1
 port-channel min-links 3
""")


    # =========================================================================
    # interface ...
    #  xconnect ...
    # =========================================================================


    def test_Interface_XConn_add(self):
        self.old_cfg.parse_str("""
interface Eth1/1
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 xconnect 10.0.0.1 100 encapsulation mpls
""")

        self.compare("""
interface Eth1/1
 xconnect 10.0.0.1 100 encapsulation mpls
""")


    # -------------------------------------------------------------------------


    def test_Interface_XConn_remove(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 xconnect 10.0.0.1 100 encapsulation mpls
""")

        self.new_cfg.parse_str("""
interface Eth1/1
""")

        self.compare("""
interface Eth1/1
 no xconnect
""")


    # -------------------------------------------------------------------------


    def test_Interface_XConn_update(self):
        self.old_cfg.parse_str("""
interface Eth1/1
 xconnect 10.0.0.1 100 encapsulation mpls
""")

        self.new_cfg.parse_str("""
interface Eth1/1
 xconnect 20.0.0.1 200 encapsulation mpls
""")

        self.compare("""
interface Eth1/1
 xconnect 20.0.0.1 200 encapsulation mpls
""")
