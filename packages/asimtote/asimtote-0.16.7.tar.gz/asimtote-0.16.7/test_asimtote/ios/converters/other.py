# (asimtote) test_asimtote.ios.converters.other
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from .cvtunittest import CiscoIOS_Convert_unittest



class TestAsimtote_CiscoIOS_Convert_Other(CiscoIOS_Convert_unittest):
    # =========================================================================
    # hostname ...
    # =========================================================================


    def test_Hostname_add(self):
        self.old_cfg.parse_str("""
""")

        self.new_cfg.parse_str("""
hostname TestRouter
""")

        self.compare("""
hostname TestRouter
""")


    # -------------------------------------------------------------------------


    def test_Hostname_remove(self):
        self.old_cfg.parse_str("""
hostname TestRouter
""")

        self.new_cfg.parse_str("")

        self.compare("""
no hostname
""")


    # -------------------------------------------------------------------------


    def test_Hostname_update(self):
        self.old_cfg.parse_str("""
hostname TestRouter
""")

        self.new_cfg.parse_str("""
hostname NewTestRouter
""")

        self.compare("""
hostname NewTestRouter
""")


    # =========================================================================
    # no spanning-tree ...
    # =========================================================================


    def test_NoSTP_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
no spanning-tree vlan 100,200
""")

        self.compare("""
no spanning-tree vlan 100
no spanning-tree vlan 200
""")


    # -------------------------------------------------------------------------


    def test_NoSTP_remove(self):
        self.old_cfg.parse_str("""
no spanning-tree vlan 100,200
""")

        self.new_cfg.parse_str("")

        self.compare("""
spanning-tree vlan 100
spanning-tree vlan 200
""")


    # =========================================================================
    # spanning-tree vlan ... priority ...
    # =========================================================================


    def test_STPPri_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
spanning-tree vlan 100 priority 8192
""")

        self.compare("""
spanning-tree vlan 100 priority 8192
""")


    # -------------------------------------------------------------------------


    def test_STPPri_remove(self):
        self.old_cfg.parse_str("""
spanning-tree vlan 100 priority 8192
""")

        self.new_cfg.parse_str("")

        self.compare("""
no spanning-tree vlan 100 priority
""")


    # -------------------------------------------------------------------------


    def test_STPPri_update(self):
        self.old_cfg.parse_str("""
spanning-tree vlan 100 priority 8192
""")

        self.new_cfg.parse_str("""
spanning-tree vlan 100 priority 16384
""")

        self.compare("""
spanning-tree vlan 100 priority 16384
""")


    # =========================================================================
    # track ... interface ...
    # =========================================================================


    def test_TrackInterface_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
track 10 interface Eth1/1 line-protocol
""")

        self.compare("""
track 10 interface Eth1/1 line-protocol
""")


    # -------------------------------------------------------------------------


    def test_TrackInterface_remove(self):
        self.old_cfg.parse_str("""
track 10 interface Eth1/1 line-protocol
""")

        self.new_cfg.parse_str("")

        self.compare("""
no track 10
""")


    # -------------------------------------------------------------------------


    def test_TrackInterface_update_interface(self):
        self.old_cfg.parse_str("""
track 10 interface Eth1/1 line-protocol
""")

        self.new_cfg.parse_str("""
track 10 interface Eth2/1 line-protocol
""")

        self.compare("""
track 10 interface Eth2/1 line-protocol
""")


    # -------------------------------------------------------------------------


    def test_TrackInterface_update_type(self):
        # confirm that change a tracking object type results in the old
        # object being deleted first (as we can't just directly change
        # one)

        self.old_cfg.parse_str("""
track 10 interface Eth1/1 line-protocol
""")

        self.new_cfg.parse_str("""
track 10 list boolean and
""")

        self.compare("""
no track 10
!
track 10 list boolean and
""")


    # =========================================================================
    # track ... list ...
    # =========================================================================


    def test_TrackList_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
track 10 list boolean and
""")

        self.compare("""
track 10 list boolean and
""")


    # -------------------------------------------------------------------------


    def test_TrackList_remove(self):
        self.old_cfg.parse_str("""
track 10 list boolean and
""")

        self.new_cfg.parse_str("")

        self.compare("""
no track 10
""")


    # -------------------------------------------------------------------------


    def test_TrackList_update(self):
        self.old_cfg.parse_str("""
track 10 list boolean and
""")

        self.new_cfg.parse_str("""
track 10 list boolean or
""")

        self.compare("""
track 10 list boolean or
""")


    # =========================================================================
    # track ... route ...
    # =========================================================================


    def test_TrackRoute_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
""")

        self.compare("""
track 10 ip route 10.0.0.0/24 reachability
""")


    # -------------------------------------------------------------------------


    def test_TrackRoute_remove(self):
        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
""")

        self.new_cfg.parse_str("")

        self.compare("""
no track 10
""")


    # -------------------------------------------------------------------------


    def test_TrackRoute_update(self):
        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 metric threshold
""")

        self.compare("""
track 10 ip route 10.0.0.0/24 metric threshold
""")


    # =========================================================================
    # track ...
    #  delay ...
    # =========================================================================


    def test_Track_Delay_add(self):
        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 10
 delay down 20
""")

        self.compare("""
track 10
 delay down 20
 delay up 10
""")


    # -------------------------------------------------------------------------


    def test_Track_Delay_remove_one(self):
        # removing one tracking delay requires that all delays are
        # cleared and the one to be remained re-added

        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 10
 delay down 20
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 10
""")

        self.compare("""
track 10
 no delay
 delay up 10
""")


    # -------------------------------------------------------------------------


    def test_Track_Delay_update_single(self):
        # a single delay update can be done in place

        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 10
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 20
""")

        self.compare("""
track 10
 delay up 20
""")


    # -------------------------------------------------------------------------


    def test_Track_Delay_update_one(self):
        # change one of two tracking delays can just be done in place

        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 10
 delay down 20
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 30
 delay down 20
""")

        self.compare("""
track 10
 delay up 30
""")


    # -------------------------------------------------------------------------


    def test_Track_Delay_update_removeupdate(self):
        # removing AND updating a tracking delay must be done in two
        # stages - clear the old list and then add the changed value

        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 10
 delay down 20
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 delay up 30
""")

        self.compare("""
track 10
 no delay
!
track 10
 delay up 30
""")


    # =========================================================================
    # track ...
    #  ip vrf ...
    # =========================================================================


    def test_Track_IPVRF_add(self):
        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 ip vrf TestVRF
""")

        self.compare("""
track 10
 ip vrf TestVRF
""")


    # -------------------------------------------------------------------------


    def test_Track_IPVRF_remove(self):
        # removing one tracking delay requires that all delays are
        # cleared and the one to be remained re-added

        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 ip vrf TestVRF
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
""")

        self.compare("""
track 10
 no ip vrf
""")


    # -------------------------------------------------------------------------


    def test_Track_IPVRF_update(self):
        # a single delay update can be done in place

        self.old_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 ip vrf TestVRF1
""")

        self.new_cfg.parse_str("""
track 10 ip route 10.0.0.0/24 reachability
 ip vrf TestVRF2
""")

        self.compare("""
track 10
 ip vrf TestVRF2
""")


    # =========================================================================
    # track ...
    #  ipv6 vrf ...
    # =========================================================================


    def test_Track_IPv6VRF_add(self):
        self.old_cfg.parse_str("""
track 10 ipv6 route 10::/64 reachability
""")

        self.new_cfg.parse_str("""
track 10 ipv6 route 10::/64 reachability
 ipv6 vrf TestVRF
""")

        self.compare("""
track 10
 ipv6 vrf TestVRF
""")


    # -------------------------------------------------------------------------


    def test_Track_IPv6VRF_remove(self):
        # removing one tracking delay requires that all delays are
        # cleared and the one to be remained re-added

        self.old_cfg.parse_str("""
track 10 ipv6 route 10::/64 reachability
 ipv6 vrf TestVRF
""")

        self.new_cfg.parse_str("""
track 10 ipv6 route 10::/64 reachability
""")

        self.compare("""
track 10
 no ipv6 vrf
""")


    # -------------------------------------------------------------------------


    def test_Track_IPv6VRF_update(self):
        # a single delay update can be done in place

        self.old_cfg.parse_str("""
track 10 ipv6 route 10::/64 reachability
 ipv6 vrf TestVRF1
""")

        self.new_cfg.parse_str("""
track 10 ipv6 route 10::/64 reachability
 ipv6 vrf TestVRF2
""")

        self.compare("""
track 10
 ipv6 vrf TestVRF2
""")


    # =========================================================================
    # track ...
    #  object ...
    # =========================================================================


    def test_Track_ListObj_add_new(self):
        self.old_cfg.parse_str("""
track 10 list boolean and
""")

        self.new_cfg.parse_str("""
track 10 list boolean and
 object 10
 object 20
""")

        self.compare("""
track 10
 object 10
!
track 10
 object 20
""")


    # -------------------------------------------------------------------------


    def test_Track_ListObj_add_extra(self):
        self.old_cfg.parse_str("""
track 10 list boolean and
 object 10
""")

        self.new_cfg.parse_str("""
track 10 list boolean and
 object 10
 object 20
""")

        self.compare("""
track 10
 object 20
""")


    # -------------------------------------------------------------------------


    def test_Track_ListObj_remove_one(self):
        # removing one tracking delay requires that all delays are
        # cleared and the one to be remained re-added

        self.old_cfg.parse_str("""
track 10 list boolean and
 object 10
 object 20
""")

        self.new_cfg.parse_str("""
track 10 list boolean and
 object 10
""")

        self.compare("""
track 10
 no object 20
""")


    # -------------------------------------------------------------------------


    def test_Track_ListObj_remove_all(self):
        # removing one tracking delay requires that all delays are
        # cleared and the one to be remained re-added

        self.old_cfg.parse_str("""
track 10 list boolean and
 object 10
 object 20
""")

        self.new_cfg.parse_str("""
track 10 list boolean and
""")

        self.compare("""
track 10
 no object 10
!
track 10
 no object 20
""")


    # =========================================================================
    # vlan ...
    # =========================================================================


    def test_VLAN_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
vlan 100
""")

        self.compare("""
vlan 100
""")


    # -------------------------------------------------------------------------


    def test_VLAN_remove(self):
        self.old_cfg.parse_str("""
vlan 100
""")

        self.new_cfg.parse_str("")

        self.compare("""
no vlan 100
""")


    # =========================================================================
    # vlan ...
    #  name ...
    # =========================================================================


    def test_Track_VLAN_Name_add(self):
        self.old_cfg.parse_str("""
vlan 100
""")

        self.new_cfg.parse_str("""
vlan 100
 name Test Name
""")

        self.compare("""
vlan 100
 name Test Name
""")


    # -------------------------------------------------------------------------


    def test_VLAN_Name_remove(self):
        self.old_cfg.parse_str("""
vlan 100
 name Test Name
""")

        self.new_cfg.parse_str("""
vlan 100
""")

        self.compare("""
vlan 100
 no name
""")


    # -------------------------------------------------------------------------


    def test_VLAN_Name_update(self):
        self.old_cfg.parse_str("""
vlan 100
 name Test Name 1
""")

        self.new_cfg.parse_str("""
vlan 100
 name Test Name 2
""")

        self.compare("""
vlan 100
 name Test Name 2
""")


    # =========================================================================
    # vrf definition ...
    # =========================================================================


    def test_VRF_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
vrf definition TestVRF
""")

        self.compare("""
vrf definition TestVRF
""")


    # -------------------------------------------------------------------------


    def test_VRF_remove(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
""")

        self.new_cfg.parse_str("")

        self.compare("""
no vrf definition TestVRF
""")


    # =========================================================================
    # vrf definition ...
    #  rd ...
    # =========================================================================


    def test_VRF_RD_add(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 rd 100:200
""")

        self.compare("""
vrf definition TestVRF
 rd 100:200
""")


    # -------------------------------------------------------------------------


    def test_VRF_RD_remove(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 rd 100:200
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
""")

        self.compare("""
vrf definition TestVRF
 no rd 100:200
""")


    # -------------------------------------------------------------------------


    def test_VRF_RD_update(self):
        # change RD requires the old one is explicitly removed first

        self.old_cfg.parse_str("""
vrf definition TestVRF
 rd 100:200
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 rd 300:400
""")

        self.compare("""
vrf definition TestVRF
 no rd 100:200
 rd 300:400
""")


    # =========================================================================
    # vrf definition ...
    #  route-target ...
    # =========================================================================


    def test_VRF_RT_add(self):
        # check we can import/export/both route-targets - the results
        # will be in explicit/separate imports and exports (so a 'both'
        # will be done as an 'export' then an 'import')
        #
        # because of the sort order 'exports' will come before 'imports'

        self.old_cfg.parse_str("""
vrf definition TestVRF
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 route-target import 100:200
 route-target export 300:400
 route-target both 500:600
""")

        self.compare("""
vrf definition TestVRF
 route-target export 300:400
!
vrf definition TestVRF
 route-target export 500:600
!
vrf definition TestVRF
 route-target import 100:200
!
vrf definition TestVRF
 route-target import 500:600
""")


    # -------------------------------------------------------------------------


    def test_VRF_RT_truncate(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 route-target import 100:200
 route-target both 300:400
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 route-target import 100:200
 route-target import 300:400
""")

        self.compare("""
vrf definition TestVRF
 no route-target export 300:400
""")


    # -------------------------------------------------------------------------


    def test_VRF_RT_remove(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 route-target import 100:200
 route-target both 300:400
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
""")

        self.compare("""
vrf definition TestVRF
 no route-target export 300:400
!
vrf definition TestVRF
 no route-target import 100:200
!
vrf definition TestVRF
 no route-target import 300:400
""")


    # -------------------------------------------------------------------------


    def test_VRF_RT_update(self):
        # change RD requires the old one is explicitly removed first

        self.old_cfg.parse_str("""
vrf definition TestVRF
 route-target import 100:200
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 route-target import 300:400
""")

        self.compare("""
vrf definition TestVRF
 no route-target import 100:200
!
vrf definition TestVRF
 route-target import 300:400
""")


    # =========================================================================
    # vrf definition ...
    #  address-family ...
    # =========================================================================


    def test_VRF_AF_add(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
 !
 address-family ipv6
""")

        self.compare("""
vrf definition TestVRF
 address-family ipv4
 !
vrf definition TestVRF
 address-family ipv6
""")


    # -------------------------------------------------------------------------


    def test_VRF_AF_remove(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
""")

        self.compare("""
vrf definition TestVRF
 no address-family ipv4
""")


    # -------------------------------------------------------------------------


    def test_VRF_AF_update_unicastnone(self):
        # confirm that 'unicast' on the end of the address family is
        # superfluous

        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4 unicast
""")

        self.compare("")


    # =========================================================================
    # vrf definition ...
    #  address-family ...
    #   route-target ...
    # =========================================================================


    # see test_VRF_RT_xxx() for the explanation of some of the common
    # tests


    def test_VRF_AF_RT_add_proto(self):
        # check route-target are unique across AFs

        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
 !
 address-family ipv6
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
 !
 address-family ipv6
  route-target import 300:400
""")

        self.compare("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
!
vrf definition TestVRF
 address-family ipv6
  route-target import 300:400
""")


    # -------------------------------------------------------------------------


    def test_VRF_AF_RT_add_multi(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
  route-target export 300:400
  route-target both 500:600
""")

        self.compare("""
vrf definition TestVRF
 address-family ipv4
  route-target export 300:400
!
vrf definition TestVRF
 address-family ipv4
  route-target export 500:600
!
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
!
vrf definition TestVRF
 address-family ipv4
  route-target import 500:600
""")


    # -------------------------------------------------------------------------


    def test_VRF_AF_RT_truncate(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
  route-target both 300:400
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
  route-target import 300:400
""")

        self.compare("""
vrf definition TestVRF
 address-family ipv4
  no route-target export 300:400
""")


    # -------------------------------------------------------------------------


    def test_VRF_AF_RT_remove(self):
        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
  route-target both 300:400
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
""")

        self.compare("""
vrf definition TestVRF
 address-family ipv4
  no route-target export 300:400
!
vrf definition TestVRF
 address-family ipv4
  no route-target import 100:200
!
vrf definition TestVRF
 address-family ipv4
  no route-target import 300:400
""")


    # -------------------------------------------------------------------------


    def test_VRF_AF_RT_update(self):
        # change RD requires the old one is explicitly removed first

        self.old_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 100:200
""")

        self.new_cfg.parse_str("""
vrf definition TestVRF
 address-family ipv4
  route-target import 300:400
""")

        self.compare("""
vrf definition TestVRF
 address-family ipv4
  no route-target import 100:200
!
vrf definition TestVRF
 address-family ipv4
  route-target import 300:400
""")
