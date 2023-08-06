# (asimtote) test_asimtote.ios.converters.lists
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



import unittest

from .cvtunittest import CiscoIOS_Convert_unittest



class TestAsimtote_CiscoIOS_Convert_Lists(CiscoIOS_Convert_unittest):
    # =========================================================================
    # ip access-list standard ...
    # =========================================================================


    # on IOS standard access lists can be reordered after entry, so we
    # have to confirm this is handled correctly (not replacing lists
    # when the rules have changed order but sematically mean the same
    # thing)


    def test_IPACL_Std_add(self):
        # confirm rules are canonicalised and new ACL created

        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
ip access-list standard TestStdACL
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny host 30.0.0.1
""")

        self.compare("""
ip access-list standard TestStdACL
 permit 10.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny 30.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_IPACL_Std_remove(self):
        self.old_cfg.parse_str("""
ip access-list standard TestStdACL
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny host 30.0.0.1
""")

        self.new_cfg.parse_str("")

        self.compare("""
no ip access-list standard TestStdACL
""")


    # -------------------------------------------------------------------------


    def test_IPACL_Std_update_rule(self):
        self.old_cfg.parse_str("""
ip access-list standard TestStdACL
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny host 30.0.0.1
""")

        self.new_cfg.parse_str("""
ip access-list standard TestStdACL
 permit host 40.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny host 30.0.0.1
""")

        self.compare("""
no ip access-list standard TestStdACL
!
ip access-list standard TestStdACL
 permit 20.0.0.0 0.0.0.255
 deny 30.0.0.1
 permit 40.0.0.1
""")


    # -------------------------------------------------------------------------


    def test_IPACL_Std_update_reorder_no_change(self):
        # check the order of rules doesn't matter, as long as the
        # semantics of the list are preserved

        self.old_cfg.parse_str("""
ip access-list standard TestStdACL
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny host 30.0.0.1
""")

        self.new_cfg.parse_str("""
ip access-list standard TestStdACL
 deny host 30.0.0.1
 permit 20.0.0.0 0.0.0.255
 permit host 10.0.0.1
""")

        self.compare("""
""")


    # -------------------------------------------------------------------------


    def test_IPACL_Std_update_reorder_change(self):
        # a rule with an overlapping address is moved, requiring the
        # list to be recreated, so rules are reordered in blocks

        self.old_cfg.parse_str("""
ip access-list standard TestStdACL
 permit host 10.0.0.1
 permit 20.0.0.0 0.0.0.255
 deny host 30.0.0.1
 !
 permit host 20.0.0.100
""")

        self.new_cfg.parse_str("""
ip access-list standard TestStdACL
 deny host 30.0.0.1
 permit 20.0.0.0 0.0.0.255
 !
 permit host 20.0.0.100
 permit host 10.0.0.1
""")

        self.compare("""
no ip access-list standard TestStdACL
!
ip access-list standard TestStdACL
 permit 20.0.0.0 0.0.0.255
 deny 30.0.0.1
 !
 permit 10.0.0.1
 permit 20.0.0.100
""")


    # =========================================================================
    # ip access-list extended ...
    # =========================================================================


    def test_IPACL_Ext_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
ip access-list extended TestExtACL
 permit ip host 10.0.0.1 any
 permit tcp 20.0.0.0 0.0.0.255 range 100 200 host 30.0.0.1 eq 300 established
 permit udp any lt 400 50.0.0.0 0.255.255.255 gt 500
 permit icmp any any echo
""")

        self.compare("""
ip access-list extended TestExtACL
 permit ip host 10.0.0.1 any
 permit tcp 20.0.0.0 0.0.0.255 range 100 200 host 30.0.0.1 eq 300 established
 permit udp any lt 400 50.0.0.0 0.255.255.255 gt 500
 permit icmp any any echo
""")


    # -------------------------------------------------------------------------


    def test_IPACL_Ext_remove(self):
        self.old_cfg.parse_str("""
ip access-list extended TestExtACL
 permit ip host 10.0.0.1 any
 permit tcp 20.0.0.0 0.0.0.255 range 100 200 host 30.0.0.1 eq 300 established
 permit udp any lt 400 50.0.0.0 0.255.255.255 gt 500
 permit icmp any any echo
""")

        self.new_cfg.parse_str("")

        self.compare("""
no ip access-list extended TestExtACL
""")


    # -------------------------------------------------------------------------


    def test_IPACL_Ext_update_rule(self):
        self.old_cfg.parse_str("""
ip access-list extended TestExtACL
 permit ip host 10.0.0.1 any
 permit tcp 20.0.0.0 0.0.0.255 range 100 200 host 30.0.0.1 eq 300 established
 permit udp any lt 400 50.0.0.0 0.255.255.255 gt 500
 permit icmp any any echo
""")

        self.new_cfg.parse_str("""
ip access-list extended TestExtACL
 permit ip host 80.0.0.1 any
 permit tcp 20.0.0.0 0.0.0.255 range 100 200 host 30.0.0.1 eq 300 established
 permit udp any lt 400 50.0.0.0 0.255.255.255 gt 500
 permit icmp any any echo
""")

        self.compare("""
no ip access-list extended TestExtACL
!
ip access-list extended TestExtACL
 permit ip host 80.0.0.1 any
 permit tcp 20.0.0.0 0.0.0.255 range 100 200 host 30.0.0.1 eq 300 established
 permit udp any lt 400 50.0.0.0 0.255.255.255 gt 500
 permit icmp any any echo
""")


    # =========================================================================
    # ipv6 access-list ...
    # =========================================================================


    def test_IPv6ACL_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
ipv6 access-list TestExtACL
 permit ipv6 host 10::1 any
 permit tcp 20::/64 range 100 200 host 30::1 eq 300 established
 permit udp any lt 400 50::/32 gt 500
 permit icmp any any echo
""")

        self.compare("""
ipv6 access-list TestExtACL
 permit ipv6 host 10::1 any
 permit tcp 20::/64 range 100 200 host 30::1 eq 300 established
 permit udp any lt 400 50::/32 gt 500
 permit icmp any any echo
""")


    # -------------------------------------------------------------------------


    def test_IPv6ACL_remove(self):
        self.old_cfg.parse_str("""
ipv6 access-list TestExtACL
 permit ipv6 host 10::1 any
 permit tcp 20::/64 range 100 200 host 30::1 eq 300 established
 permit udp any lt 400 50::/32 gt 500
 permit icmp any any echo
""")

        self.new_cfg.parse_str("")

        self.compare("""
no ipv6 access-list TestExtACL
""")


    # -------------------------------------------------------------------------


    def test_IPv6ACL_update_rule(self):
        self.old_cfg.parse_str("""
ipv6 access-list TestExtACL
 permit ipv6 host 10::1 any
 permit tcp 20::/64 range 100 200 host 30::1 eq 300 established
 permit udp any lt 400 50::/32 gt 500
 permit icmp any any echo
""")

        self.new_cfg.parse_str("""
ipv6 access-list TestExtACL
 permit ipv6 host 80::1 any
 permit tcp 20::/64 range 100 200 host 30::1 eq 300 established
 permit udp any lt 400 50::/32 gt 500
 permit icmp any any echo
""")

        self.compare("""
no ipv6 access-list TestExtACL
!
ipv6 access-list TestExtACL
 permit ipv6 host 80::1 any
 permit tcp 20::/64 range 100 200 host 30::1 eq 300 established
 permit udp any lt 400 50::/32 gt 500
 permit icmp any any echo
""")


    # =========================================================================
    # ip as-path access-list ...
    # =========================================================================


    def test_IPASPathACL_add(self):
        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
ip as-path access-list 100 permit ^100(_100)*$
ip as-path access-list 100 permit ^100(_100)*(_200)*$
""")

        self.compare("""
ip as-path access-list 100 permit ^100(_100)*$
ip as-path access-list 100 permit ^100(_100)*(_200)*$
""")


    # -------------------------------------------------------------------------


    def test_IPASPathACL_remove(self):
        self.old_cfg.parse_str("""
ip as-path access-list 100 permit ^100(_100)*$
ip as-path access-list 100 permit ^100(_100)*(_200)*$
""")

        self.new_cfg.parse_str("")

        self.compare("""
no ip as-path access-list 100
""")


    # -------------------------------------------------------------------------


    def test_IPASPathACL_update(self):
        self.old_cfg.parse_str("""
ip as-path access-list 100 permit ^100(_100)*$
ip as-path access-list 100 permit ^100(_100)*(_200)*$
""")

        self.new_cfg.parse_str("""
ip as-path access-list 100 permit ^100(_100)*$
ip as-path access-list 100 permit ^100(_100)*(_300)*$
""")

        self.compare("""
no ip as-path access-list 100
!
ip as-path access-list 100 permit ^100(_100)*$
ip as-path access-list 100 permit ^100(_100)*(_300)*$
""")


    # =========================================================================
    # ip prefix-list ...
    # =========================================================================


    def test_IPPfxList_add(self):
        # sequence numbers are unimportant apart from the ordering

        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
ip prefix-list TestPfxList seq 10 permit 10.0.0.0/16 le 24
ip prefix-list TestPfxList seq 20 permit 20.0.0.0/24
ip prefix-list TestPfxList seq 15 permit 30.0.0.0/20 le 32
""")

        self.compare("""
ip prefix-list TestPfxList permit 10.0.0.0/16 le 24
ip prefix-list TestPfxList permit 30.0.0.0/20 le 32
ip prefix-list TestPfxList permit 20.0.0.0/24
""")


    # -------------------------------------------------------------------------


    def test_IPPfxList_remove(self):
        # sequence numbers are unimportant apart from the ordering

        self.old_cfg.parse_str("""
ip prefix-list TestPfxList seq 10 permit 10.0.0.0/16 le 24
ip prefix-list TestPfxList seq 20 permit 20.0.0.0/24
ip prefix-list TestPfxList seq 15 permit 30.0.0.0/20 le 32
""")

        self.new_cfg.parse_str("")

        self.compare("""
no ip prefix-list TestPfxList
""")


    # -------------------------------------------------------------------------


    def test_IPPfxList_update(self):
        # sequence numbers are unimportant apart from the ordering

        self.old_cfg.parse_str("""
ip prefix-list TestPfxList seq 10 permit 10.0.0.0/16 le 24
ip prefix-list TestPfxList seq 20 permit 20.0.0.0/24
ip prefix-list TestPfxList seq 15 permit 30.0.0.0/20 le 32
""")

        self.new_cfg.parse_str("""
ip prefix-list TestPfxList seq 10 permit 40.0.0.0/16 le 24
ip prefix-list TestPfxList seq 20 permit 20.0.0.0/24
ip prefix-list TestPfxList seq 15 permit 30.0.0.0/20 le 32
""")

        self.compare("""
no ip prefix-list TestPfxList
!
ip prefix-list TestPfxList permit 40.0.0.0/16 le 24
ip prefix-list TestPfxList permit 30.0.0.0/20 le 32
ip prefix-list TestPfxList permit 20.0.0.0/24
""")


    # =========================================================================
    # ipv6 prefix-list ...
    # =========================================================================


    def test_IPv6PfxList_add(self):
        # sequence numbers are unimportant apart from the ordering

        self.old_cfg.parse_str("")

        self.new_cfg.parse_str("""
ipv6 prefix-list TestPfxList seq 10 permit 10::/32 le 64
ipv6 prefix-list TestPfxList seq 20 permit 20::/64
ipv6 prefix-list TestPfxList seq 15 permit 30::/48 le 64
""")

        self.compare("""
ipv6 prefix-list TestPfxList permit 10::/32 le 64
ipv6 prefix-list TestPfxList permit 30::/48 le 64
ipv6 prefix-list TestPfxList permit 20::/64
""")


    # -------------------------------------------------------------------------


    def test_IPv6PfxList_remove(self):
        # sequence numbers are unimportant apart from the ordering

        self.old_cfg.parse_str("""
ipv6 prefix-list TestPfxList seq 10 permit 10::/32 le 64
ipv6 prefix-list TestPfxList seq 20 permit 20::/64
ipv6 prefix-list TestPfxList seq 15 permit 30::/48 le 64
""")

        self.new_cfg.parse_str("")

        self.compare("""
no ipv6 prefix-list TestPfxList
""")


    # -------------------------------------------------------------------------


    def test_IPv6PfxList_update(self):
        # sequence numbers are unimportant apart from the ordering

        self.old_cfg.parse_str("""
ipv6 prefix-list TestPfxList seq 10 permit 10::/32 le 64
ipv6 prefix-list TestPfxList seq 20 permit 20::/64
ipv6 prefix-list TestPfxList seq 15 permit 30::/48 le 64
""")

        self.new_cfg.parse_str("""
ipv6 prefix-list TestPfxList seq 10 permit 40::/32 le 64
ipv6 prefix-list TestPfxList seq 20 permit 20::/64
ipv6 prefix-list TestPfxList seq 15 permit 30::/48 le 64
""")

        self.compare("""
no ipv6 prefix-list TestPfxList
!
ipv6 prefix-list TestPfxList permit 40::/32 le 64
ipv6 prefix-list TestPfxList permit 30::/48 le 64
ipv6 prefix-list TestPfxList permit 20::/64
""")
