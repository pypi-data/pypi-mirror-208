# asimtote.ios.converters.router
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



import netaddr

from deepops import deepget

from ...diff import Convert
from ..utils import VRF_GLOBAL



# --- converter classes ---



# =============================================================================
# ip[v6] route ...
# =============================================================================



class Cvt_IPRoute(Convert):
    cmd = "ip-route", None, None, None

    def _cmd(self, vrf, net, r):
        n = netaddr.IPNetwork(net)

        return ("ip route"
                + ((" vrf " + vrf) if vrf else "")
                + " " + str(n.network) + " " + str(n.netmask)
                + ((" " + r["interface"]) if "interface" in r else "")
                + ((" " + r["router"]) if "router" in r else "")
                + ((" %d" % r["metric"]) if "metric" in r else "")
                + ((" tag %d" % r["tag"]) if "tag" in r else ""))

    def remove(self, old, c, vrf, net, id):
        return "no " + self._cmd(vrf, net, old)

    def update(self, old, upd, new, c, vrf, net, id):
        return self._cmd(vrf, net, new)


class Cvt_IPv6Route(Convert):
    cmd = "ipv6-route", None, None, None

    def _cmd(self, vrf, net, r):
        return ("ipv6 route"
                + ((" vrf " + vrf) if vrf else "")
                + " " + net
                + ((" " + r["interface"]) if "interface" in r else "")
                + ((" " + r["router"]) if "router" in r else "")
                + ((" " + str(r["metric"])) if "metric" in r else "")
                + ((" tag " + str(r["tag"])) if "tag" in r else ""))

    def remove(self, old, c, vrf, net, id):
        return "no " + self._cmd(vrf, net, old)

    def update(self, old, upd, new, c, vrf, net, id):
        return self._cmd(vrf, net, new)



# =============================================================================
# route-map ...
# =============================================================================



class Cvt_RtMap(Convert):
    cmd = "route-map", None
    block = "rtmap-del"

    def remove(self, old, c, rtmap_name):
        return "no route-map " + rtmap_name


class Context_RtMap(Convert):
    context = Cvt_RtMap.cmd


class Cvt_RtMap_Entry(Context_RtMap):
    cmd = None,
    block = "rtmap-del"

    def remove(self, old, c, seq):
        rtmap_name, = c
        return "no route-map %s %d" % (rtmap_name, seq)


class Cvt_RtMap_Entry_Action(Context_RtMap):
    cmd = None, "action"
    block = "rtmap-add"

    def update(self, old, upd, new, c, seq):
        rtmap_name, = c
        return "route-map %s %s %d" % (rtmap_name, new, seq)


class Context_RtMap_Entry(Context_RtMap):
    context = Context_RtMap.context + Cvt_RtMap_Entry.cmd

    # route-map entries require you to know the action type ('permit' or
    # 'deny') when modifying them, which are in the dictionary element
    # underneath, in our configuration model
    def enter(self, rtmap_name, seq, rtmap_dict):
        return ["route-map %s %s %d" % (rtmap_name, rtmap_dict["action"], seq)]


class Cvt_RtMap_MatchCmty_Exact_del(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "community", "exact-match"
    block = "rtmap-del"
    trigger_blocks = { "rtmap-add-cmty" }

    # if removing the exact-match option, we need to clear the list and
    # recreate it without it
    def remove(self, old, c):
        if self.get_ext(old):
            l = self.enter(*c, old)
            l.append(" no match community")
            return l


class _AbsCvt_RtMap_MatchCmty(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "community", "communities", None


class Cvt_RtMap_MatchCmty_del(_AbsCvt_RtMap_MatchCmty):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c, cmty):
        l = self.enter(*c, old)
        l.append(" no match community " + cmty)
        return l


class Cvt_RtMap_MatchCmty_add(_AbsCvt_RtMap_MatchCmty):
    block = "rtmap-add-cmty"

    def update(self, old, upd, new, c, cmty):
        # TODO: need to handle applying 'exact-match' when list is the
        # same; will rework these to use context_offset to see if that
        # makes it easier (as we need the action from a higher context
        # but would like to set a lower context)
        l = self.enter(*c, new)
        exact_match = deepget(new, "match", "community", "exact-match")
        l.append(" match community %s%s"
                     % (cmty, " exact-match" if exact_match else ""))
        return l

    def trigger(self, new, c, *args):
        return self.update(None, new, new, c, *args)


class _AbsCvt_RtMap_MatchIPAddr(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "ip-address"

class Cvt_RtMap_MatchIPAddr_del(_AbsCvt_RtMap_MatchIPAddr):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c):
        l = self.enter(*c, old)
        for addr in sorted(self.get_ext(rem)):
            l.append(" no match ip address " + addr)
        return l

class Cvt_RtMap_MatchIPAddr_add(_AbsCvt_RtMap_MatchIPAddr):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        for addr in sorted(self.get_ext(upd)):
            l.append(" match ip address " + addr)
        return l


class _AbsCvt_RtMap_MatchIPPfxLst(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "ip-prefix-list"

class Cvt_RtMap_MatchIPPfxLst_del(_AbsCvt_RtMap_MatchIPPfxLst):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c):
        l = self.enter(*c, old)
        for pfx in sorted(self.get_ext(rem)):
            l.append(" no match ip address prefix-list " + pfx)
        return l

class Cvt_RtMap_MatchIPPfxLst_add(_AbsCvt_RtMap_MatchIPPfxLst):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        for pfx in sorted(self.get_ext(upd)):
            l.append(" match ip address prefix-list " + pfx)
        return l


class _AbsCvt_RtMap_MatchIPv6Addr(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "ipv6-address"

class Cvt_RtMap_MatchIPv6Addr_del(_AbsCvt_RtMap_MatchIPv6Addr):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c):
        l = self.enter(*c, old)
        for addr in sorted(self.get_ext(rem)):
            l.append(" no match ipv6 address " + addr)
        return l

class Cvt_RtMap_MatchIPv6Addr_add(_AbsCvt_RtMap_MatchIPv6Addr):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        for addr in sorted(self.get_ext(upd)):
            l.append(" match ipv6 address " + addr)
        return l


class _AbsCvt_RtMap_MatchIPv6PfxLst(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "ipv6-prefix-list"

class Cvt_RtMap_MatchIPv6PfxLst_del(_AbsCvt_RtMap_MatchIPv6PfxLst):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c):
        l = self.enter(*c, old)
        for pfx in sorted(self.get_ext(rem)):
            l.append(" no match ipv6 address prefix-list " + pfx)
        return l

class Cvt_RtMap_MatchIPv6PfxLst_add(_AbsCvt_RtMap_MatchIPv6PfxLst):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        for pfx in sorted(self.get_ext(upd)):
            l.append(" match ipv6 address prefix-list " + pfx)
        return l


class _AbsCvt_RtMap_MatchTag(Context_RtMap_Entry):
    cmd = tuple()
    ext = "match", "tag"

class Cvt_RtMap_MatchTag_del(_AbsCvt_RtMap_MatchTag):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c):
        l = self.enter(*c, old)
        for tag in sorted(self.get_ext(rem)):
            l.append(" no match tag " + str(tag))
        return l

class Cvt_RtMap_MatchTag_add(_AbsCvt_RtMap_MatchTag):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        for tag in sorted(self.get_ext(upd)):
            l.append(" match tag " + str(tag))
        return l


class _AbsCvt_RtMap_SetCmty(Context_RtMap_Entry):
    cmd = tuple()
    ext = "set", "community", "communities"

class Cvt_RtMap_SetCmty_del(_AbsCvt_RtMap_SetCmty):
    block = "rtmap-del"

    def truncate(self, old, rem, new, c):
        l = self.enter(*c, old)
        for cmty in sorted(self.get_ext(rem)):
            l.append(" no set community " + cmty)
        return l

class Cvt_RtMap_SetCmty_add(_AbsCvt_RtMap_SetCmty):
    block = "rtmap-add"

    # TODO: need to handle case where list is the same but 'additive'
    # is only addition or removal
    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        for cmty in sorted(self.get_ext(upd)):
            l.append(" set community "
                     + cmty
                     + (" additive" if "additive" in new["set"]["community"]
                            else ""))
        return l


class _AbsCvt_RtMap_SetIPNxtHop(Context_RtMap_Entry):
    cmd = tuple()
    ext = "set", "ip-next-hop"

    def _cmd(self, nexthop):
        addr = nexthop["addr"]
        vrf = None
        if "vrf" in nexthop:
            vrf = ("vrf " + nexthop["vrf"]) if nexthop["vrf"] else "global"

        return "set ip" + ((" " + vrf) if vrf else "") + " next-hop " + addr

class Cvt_RtMap_SetIPNxtHop_del(_AbsCvt_RtMap_SetIPNxtHop):
    block = "rtmap-del"

    def remove(self, old, c):
        # we must remove all the 'set ip next-hop' commands individually
        l = self.enter(*c, old)
        for nexthop in self.get_ext(old):
            l.append(" no " + self._cmd(nexthop))
        return l

class Cvt_RtMap_SetIPNxtHop_add(_AbsCvt_RtMap_SetIPNxtHop):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        # the 'set ip ... next-hop' commands are an ordered list and, if
        # anything has changed, we need to destroy the old one and
        # create the new one from scratch
        l = self.enter(*c, new)
        if old:
            for old_nexthop in self.get_ext(old):
                l.append(" no " + self._cmd(old_nexthop))
        for new_nexthop in self.get_ext(new):
            l.append(" " + self._cmd(new_nexthop))
        return l


class Cvt_RtMap_SetIPNxtHopVrfy(Context_RtMap_Entry):
    cmd = tuple()
    ext = "set", "ip-next-hop-verify-availability"

    def remove(self, old, c):
        l = self.enter(*c, old)
        l.append(" no set ip next-hop verify-availability")
        return l

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)
        l.append(" set ip next-hop verify-availability")
        return l


class _AbsCvt_RtMap_SetIPNxtHopVrfyTrk(Context_RtMap_Entry):
    cmd = tuple()
    ext = "set", "ip-next-hop-verify-availability-track", None

    def _cmd(self, seq, nexthop):
        return ("set ip next-hop verify-availability %s %s track %d"
                     % (nexthop["addr"], seq, nexthop["track-obj"]))

class Cvt_RtMap_SetIPNxtHopVrfy_del(_AbsCvt_RtMap_SetIPNxtHopVrfyTrk):
    block = "rtmap-del"

    def remove(self, old, c, nexthop_seq):
        return self.enter(*c, old) + [
                   " no "
                       + self._cmd(nexthop_seq,
                                   self.get_ext(old, nexthop_seq))]

class Cvt_RtMap_SetIPNxtHopVrfy_add(_AbsCvt_RtMap_SetIPNxtHopVrfyTrk):
    block = "rtmap-add"

    def update(self, old, upd, new, c, nexthop_seq):
        # individual entries (ordered by sequence number) can be replaced but
        # the old entry must be removed first, before the new one added
        l = self.enter(*c, new)
        if old:
            l.append(" no "
                     + self._cmd(nexthop_seq, self.get_ext(old, nexthop_seq)))
        l.append(" " + self._cmd(nexthop_seq, self.get_ext(new, nexthop_seq)))
        return l


class _AbsCvt_RtMap_SetIPv6NxtHop(Context_RtMap_Entry):
    cmd = tuple()
    ext = "set", "ipv6-next-hop"

    def _cmd(self, nexthop):
        addr = nexthop["addr"]
        return "set ipv6 next-hop " + addr

class Cvt_RtMap_SetIPv6NxtHop_del(_AbsCvt_RtMap_SetIPv6NxtHop):
    block = "rtmap-del"

    def remove(self, old, c):
        # we must remove all the 'set ipv6 next-hop' commands individually
        l = self.enter(*c, old)
        for nexthop in self.get_ext(old):
            l.append(" no " + self._cmd(nexthop))
        return l

class Cvt_RtMap_SetIPv6NxtHop_add(_AbsCvt_RtMap_SetIPv6NxtHop):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        # the 'set ip ... next-hop' commands are an ordered list and, if
        # anything has changed, we need to destroy the old one and
        # create the new one from scratch
        l = self.enter(*c, new)
        if old:
            for old_nexthop in self.get_ext(old):
                l.append(" no " + self._cmd(old_nexthop))
        for new_nexthop in self.get_ext(new):
            l.append(" " + self._cmd(new_nexthop))
        return l


class _AbsCvt_RtMap_SetLocalPref(Context_RtMap_Entry):
    cmd = tuple()
    ext = "set", "local-preference"

class Cvt_RtMap_SetLocalPref_del(_AbsCvt_RtMap_SetLocalPref):
    block = "rtmap-del"

    def remove(self, old, c):
        return self.enter(*c, old) + [" no set local-preference"]

class Cvt_RtMap_SetLocalPref_add(_AbsCvt_RtMap_SetLocalPref):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        return self.enter(*c, new) + [
                   " set local-preference " + str(self.get_ext(new))]


class _AbsCvt_RtMap_SetVRF(Context_RtMap_Entry):
    # this handles both 'set global' and 'set vrf ...'
    cmd = tuple()
    ext = "set", "vrf"

    def _cmd(self, entry):
        vrf = self.get_ext(entry)
        return "set " + (("vrf " + vrf) if vrf else "global")

class Cvt_RtMap_SetVRF_del(_AbsCvt_RtMap_SetVRF):
    block = "rtmap-del"

    def remove(self, old, c):
        return self.enter(*c, old) + [" no " + self._cmd(old)]

class Cvt_RtMap_SetVRF_add(_AbsCvt_RtMap_SetVRF):
    block = "rtmap-add"

    def update(self, old, upd, new, c):
        l = self.enter(*c, new)

        # if there's a previous setting, and we're changing from global
        # to a VRF, or vice-versa, we need to clear the old setting
        # first
        if old and (bool(self.get_ext(old)) != bool(self.get_ext(new))):
            l.append(" no " + self._cmd(old))

        l.append(" " + self._cmd(new))
        return l



# =============================================================================
# router bgp ...
# =============================================================================



class Cvt_RtrBGP(Convert):
    cmd = "router", "bgp", None

    def remove(self, old, c, asn):
        return "no router bgp " + asn

    def add(self, new, c, asn):
        return "router bgp " + asn


class Context_RtrBGP(Convert):
    context = "router", "bgp", None

    def enter(self, asn):
        return ["router bgp " + asn]


class Cvt_RtrBGP_BGPRtrID(Context_RtrBGP):
    cmd = "router-id",

    def remove(self, old, c):
        return self.enter(*c) + [" no bgp router-id"]

    def update(self, old, upd, new, c):
        return self.enter(*c) + [" bgp router-id " + new]


class Cvt_RtrBGP_Nbr(Context_RtrBGP):
    cmd = "neighbor", None

    def remove(self, old, c, nbr):
        # when removing a neighbor that is a peer-group, we need to
        # state that
        return self.enter(*c) + [
                   "  no neighbor "
                       + nbr
                       + (" peer-group" if old.get("type") == "peer-group"
                              else "")]

    def add(self, new, c, nbr):
        # we only explicitly need to add a neighbor if it's a peer-group
        # (normally, a neighbor is created implicitly by configuring
        # settings for it, starting by putting it in a peer-group or
        # its remote-as)
        if new.get("type") == "peer-group":
            return self.enter(*c) + ["  neighbor %s peer-group" % nbr]


class Context_RtrBGP_Nbr(Context_RtrBGP):
    context = Context_RtrBGP.context + Cvt_RtrBGP_Nbr.cmd

    # we're going to use these classes directly under the 'router,bgp,
    # ASN,neighbor,NBR' context and the 'router,bgp,ASN,vrf,VRF,
    # address-family,AF,neighbor,NBR' context but we also need access to
    # the NBR parameter for the commands (since they start 'neighbor
    # NBR ...')
    #
    # setting context_offset to -1 causes the neighbor to be supplied as
    # a local argument to the converter and gives a variable length
    # context, depending on whether the configuration is at the global
    # or address-family level
    context_offset = -1


class Cvt_RtrBGP_Nbr_FallOver(Context_RtrBGP_Nbr):
    cmd = "fall-over",

    def remove(self, old, c, nbr):
        return self.enter(*c) + [" no neighbor %s fall-over" % nbr]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   " neighbor %s fall-over %s"
                       % (nbr,
                          ("bfd " + new["bfd"]) if "bfd" in new
                               else "route-map " + new["route-map"])]


class Cvt_RtrBGP_Nbr_Pwd(Context_RtrBGP_Nbr):
    cmd = "password",

    def remove(self, old, c, nbr):
        return self.enter(*c) + [" no neighbor %s password" % nbr]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   " neighbor %s password %d %s"
                       % (nbr, new["encryption"], new["password"])]


class Cvt_RtrBGP_Nbr_PrGrpMbr(Context_RtrBGP_Nbr):
    # this converter is used to add or remove a neighbor to/from a
    # peer-group
    cmd = "peer-group",
    trigger_blocks = { "bgp-nbr-activate" }

    def remove(self, old, c, nbr):
        return self.enter(*c) + ["  no neighbor %s peer-group %s" % (nbr, old)]

    def add(self, new, c, nbr):
        return self.enter(*c) + ["  neighbor %s peer-group %s" % (nbr, new)]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   "  no neighbor %s peer-group %s" % (nbr, old),
                   "  neighbor %s peer-group %s" % (nbr, new)]


class Cvt_RtrBGP_Nbr_RemAS(Context_RtrBGP_Nbr):
    cmd = "remote-as",

    # removing a remote AS actually removes the neighbor, so we deal
    # with that in the context, above - we just handle add/update here

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [" neighbor %s remote-as %s" % (nbr, new)]


class Cvt_RtrBGP_Nbr_UpdSrc(Context_RtrBGP_Nbr):
    cmd = "update-source",

    def remove(self, old, c, nbr):
        return self.enter(*c) + [" no neighbor %s update-source" % nbr]

    def update(self, old, upd,new, c, nbr):
        return self.enter(*c) + [" neighbor %s update-source %s" % (nbr, new)]


# router bgp ... address-family ... [vrf ...]


# working out the address-family line is complicated and we do it in
# several places, so separate it into a function

def _RtrBGP_AF_cmd(vrf, af):
    # address families in the global routing table as in a VRF called
    # VRF_GLOBAL as a special case so everything lines up at the same
    # level in the inventory
    return (" address-family "
            + af
            + ((" vrf " + vrf) if vrf != VRF_GLOBAL else ""))


class Cvt_RtrBGP_AF(Context_RtrBGP):
    cmd = "vrf", None, "address-family", None

    def remove(self, old, c, vrf, af):
        return self.enter(*c) + [" no" + _RtrBGP_AF_cmd(vrf, af)]

    def add(self, new, c, vrf, af):
        return self.enter(*c) + [_RtrBGP_AF_cmd(vrf, af)]


class Context_RtrBGP_AF(Context_RtrBGP):
    context = Context_RtrBGP.context + Cvt_RtrBGP_AF.cmd

    def enter(self, *c):
        c_super, (vrf, af) = c[:-2], c[-2:]
        return super().enter(*c_super) + [_RtrBGP_AF_cmd(vrf, af)]


class Cvt_RtrBGP_AF_MaxPaths(Context_RtrBGP_AF):
    cmd = "maximum-paths",

    def remove(self, old, c):
        return self.enter(*c) + ["  no maximum-paths %d" % old]

    def update(self, old, upd, new, c):
        return self.enter(*c) + ["  maximum-paths %d" % new]


class Cvt_RtrBGP_AF_MaxPathsIBGP(Context_RtrBGP_AF):
    cmd = "maximum-paths-ibgp",

    def remove(self, old, c):
        return self.enter(*c) + ["  no maximum-paths ibgp %d" % old]

    def update(self, old, upd, new, c):
        return self.enter(*c) + ["  maximum-paths ibgp %d" % new]


# 'redistribute' is a single line command but operates more as a
# context and so is handled as one, although, unlike the 'neighbor ...'
# commands does not need to be handled different from global vs VRF
# address families, so we don't need two versions
#
# entering 'redistribute ...' will enable redistribution and 'no
# redistribute ...' will turn it off again
#
# configuring 'route-map' or 'metric' will turn these settings on, and
# enable redistribution at the same time (if it is not already)
#
# 'no redistribute ... route-map/metric' will turn them off, but leave
# redistribution itself on


# classes to cover the redistribution contexts


class Cvt_RtrBGP_AF_Redist_Simple(Context_RtrBGP_AF):
    cmd = "redistribute", { "static", "connected" }

    def remove(self, old, c, proto):
        return self.enter(*c) + ["  no redistribute " + proto]

    def add(self, new, c, proto):
        return self.enter(*c) + ["  redistribute " + proto]


class Cvt_RtrBGP_AF_Redist_OSPF(Context_RtrBGP_AF):
    cmd = "redistribute", { "ospf", "ospfv3" }, None

    def remove(self, old, c, proto, proc):
        return self.enter(*c) + ["  no redistribute %s %d" % (proto, proc)]

    def add(self, new, c, proto, proc):
        return self.enter(*c) + ["  redistribute %s %d" % (proto, proc)]


# context versions of above
#
# the parameter classes will be subclasses of these and use a variable
# length context because the 'simple' protocols have no additional
# arguments but the OSPF one has a process number


class Context_RtrBGP_AF_Redist_Simple(Context_RtrBGP_AF):
    context = Context_RtrBGP_AF.context + Cvt_RtrBGP_AF_Redist_Simple.cmd

    # also get the protocol from the context
    context_offset = -1

    def _redist(self, proto):
        return "redistribute " + proto


class Context_RtrBGP_AF_Redist_OSPF(Context_RtrBGP_AF):
    context = Context_RtrBGP_AF.context + Cvt_RtrBGP_AF_Redist_OSPF.cmd

    # also get the protocol and process number from the context
    context_offset = -2

    def _redist(self, proto, proc):
        return "redistribute %s %d" % (proto, proc)


# redistribution parameter classes


class Cvt_RtrBGP_AF_Redist_Simple_Metric(Context_RtrBGP_AF_Redist_Simple):
    cmd = "metric",

    def remove(self, old, c, *redist):
        return self.enter(*c) + ["  no %s metric" % self._redist(*redist)]

    def update(self, old, upd, new, c, *redist):
        return self.enter(*c) + [
                   "  %s metric %d" % (self._redist(*redist), new)]


class Cvt_RtrBGP_AF_Redist_Simple_RtMap(Context_RtrBGP_AF_Redist_Simple):
    cmd = "route-map",

    def remove(self, old, c, redist):
        return self.enter(*c) + [
                   "  no %s route-map %s" % (self._redist(redist), old)]

    def update(self, old, upd, new, c, redist):
        return self.enter(*c) + [
                   "  %s route-map %s" % (self._redist(redist), new)]


# OSPF version of the above parameter classes - these inherit from the
# OSPF context class, instead of the simple context class


class Cvt_RtrBGP_AF_Redist_OSPF_Metric(
    Context_RtrBGP_AF_Redist_OSPF, Cvt_RtrBGP_AF_Redist_Simple_Metric):

    pass


class Cvt_RtrBGP_AF_Redist_OSPF_RtMap(
    Context_RtrBGP_AF_Redist_OSPF, Cvt_RtrBGP_AF_Redist_Simple_RtMap):

    pass


# adding and removing entire neighbors as a context is only done in the
# non-global VRF (in the global VRF, neighbors are configured at the
# parent, 'router bgp' level and then only address-family specific
# parameters at that level; for VRFs, the whole neighbor, including the
# remote-as, is configured at the address-family level)

class Cvt_RtrBGP_AF_vrf_Nbr(Context_RtrBGP_AF, Cvt_RtrBGP_Nbr):
    def filter(self, c, *_):
        asn, vrf, af = c
        return vrf != VRF_GLOBAL



# this abstract class and the two that follow are used to create two
# versions of each command class below by inheriting from each
# separately - one for the global VRF and one for a different VRF
#
# this class modifies the path during construction in two different
# ways

class _AbsCvt_RtrBGP_AF_Nbr(Context_RtrBGP_AF):
    def __init__(self):
        self.add_nbr_path()
        super().__init__()

    def add_nbr_path(self):
        pass


# this class is for commands in the global VRF: the commands start with
# 'neighbor ...' but still operate in the [global] address-family
# context - as such, this just appends that to the 'cmd' attribute
#
# this is because commands in the global address-family do not add or
# delete entire neighbors (that's done at the 'router bgp' level), but
# just configured parameters about them

class _AbsCvt_RtrBGP_AF_global_Nbr(_AbsCvt_RtrBGP_AF_Nbr):
    def add_nbr_path(self):
        self.cmd = ("neighbor", None) + self.cmd

    def filter(self, c, *_):
        asn, vrf, af = c
        return vrf == VRF_GLOBAL


# on the other hand, this class is for commands in the non-global VRF:
# here the neighbor commands operate in a context of that neighbor,
# underneath the address-family - the context is extended by suffixing
# 'neighbor ...' onto it
#
# this is because, in a non-global VRF, neighbors are separate from
# those at the global level and must be created and can also be removed
# by removing the context, with 'no neighbor ...', rather than the
# individual parameters

class _AbsCvt_RtrBGP_AF_vrf_Nbr(_AbsCvt_RtrBGP_AF_Nbr):
    context_offset = -1

    def add_nbr_path(self):
        self.context = self.context + ("neighbor", None)

    def filter(self, c, *_):
        asn, vrf, af = c
        return vrf != VRF_GLOBAL


# this is the global VRF version of 'neighbor ... activate'

class Cvt_RtrBGP_AF_global_Nbr_Act(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "activate",
    block = "bgp-nbr-activate"

    def remove(self, old, c, nbr):
        return self.enter(*c) + ["  no neighbor %s activate" % nbr]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + ["  neighbor %s activate" % nbr]


# this creates the non-global VRF version of 'neighbor ... activate'
#
# this pattern continues for all commands below that exist in both the
# global or non-global VRF

class Cvt_RtrBGP_AF_vrf_Nbr_Act(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_Act):

    pass


class Cvt_RtrBGP_AF_global_Nbr_AddPath(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "additional-paths",

    def _add_paths(self, p):
        return (
            " ".join([a for a in [ "send", "receive", "disable" ] if a in p]))

    def remove(self, old, c, nbr):
        return self.enter(*c) + [
                   "  no neighbor %s additional-paths" % nbr]

    def truncate(self, old, rem, new, c, nbr):
        # we can't remove types of additional-path, only provide a
        # complete new list
        return self.update(old, None, new, c, nbr)

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   "  neighbor %s additional-paths %s"
                       % (nbr, self._add_paths(new))]


class Cvt_RtrBGP_AF_global_Nbr_AdvAddPath(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "advertise-additional-paths", None

    def remove(self, old, c, nbr, adv):
        # we can just remove any type and don't need to give the number
        # when removing 'best n'
        return self.enter(*c) + [
                   "  no neighbor %s advertise additional-paths %s"
                       % (nbr, adv)]

    def update(self, old, upd, new, c, nbr, adv):
        return self.enter(*c) + [
                   "  neighbor %s advertise additional-paths %s"
                       % (nbr, ("best %d" % new) if adv == "best" else adv)]


# Cvt_RtrBGP_AF_vrf _Nbr_AdvAddPath
# does not exist - there is no non-global VRF version of this


class Cvt_RtrBGP_AF_global_Nbr_AlwAS(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "allowas-in",

    def truncate(self, old, rem, new, c, nbr):
        # if we're truncating, we must be removing the 'max'
        return self.enter(*c) + [
                   "  neighbor %s allowas-in" % nbr]

    def remove(self, old, c, nbr):
        # removing the entire command
        return self.enter(*c) + [
                   "  no neighbor %s allowas-in" % nbr]

    def update(self, old, upd, new, c, nbr):
        # either changing the 'max' or adding a plain form
        return self.enter(*c) + [
                   "  neighbor %s allowas-in%s"
                       % (nbr, (" %d" % new["max"]) if "max" in new else "")]


class Cvt_RtrBGP_AF_vrf_Nbr_AlwAS(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_AlwAS):

    pass


# Cvt_RtrBGP_AF_global_Nbr_FallOver
# does not exist - there is no global VRF version of this (done at the
# 'router bgp' level)


class Cvt_RtrBGP_AF_vrf_Nbr_FallOver(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_Nbr_FallOver):

    pass


class Cvt_RtrBGP_AF_global_Nbr_FltLst(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "filter-list", None

    def remove(self, old, c, nbr, dir_):
        return self.enter(*c) + [
                   "  no neighbor %s filter-list %d %s" % (nbr, old, dir_)]

    def update(self, old, upd, new, c, nbr, dir_):
        return self.enter(*c) + [
                   "  neighbor %s filter-list %d %s" % (nbr, new, dir_)]


class Cvt_RtrBGP_AF_vrf_Nbr_FltLst(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_FltLst):

    pass


class Cvt_RtrBGP_AF_global_Nbr_MaxPfx(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "maximum-prefix",

    def remove(self, old, c, nbr):
        # oddly, when removing, the old maximum must be spefified but
        # not the threshold
        return self.enter(*c) + [
                   "  no neighbor %s maximum-prefix %d" % (nbr, old["max"])]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   "  neighbor %s maximum-prefix %d%s"
                       % (nbr,
                          new["max"],
                          (" %d" % new["threshold"]) if "threshold" in new
                               else "")]


class Cvt_RtrBGP_AF_vrf_Nbr_MaxPfx(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_MaxPfx):

    pass


class Cvt_RtrBGP_AF_global_Nbr_NHSelf(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "next-hop-self",

    def truncate(self, old, rem, new, c, nbr):
        # if we're truncating, we must be changing to the plain form
        return self.enter(*c) + [
                   "  neighbor %s next-hop-self" % nbr]

    def remove(self, old, c, nbr):
        # removing the entire command
        return self.enter(*c) + [
                   "  no neighbor %s next-hop-self" % nbr]

    def update(self, old, upd, new, c, nbr):
        # either updatring to 'all' or adding a plain form
        return self.enter(*c) + [
                   "  neighbor %s next-hop-self%s"
                       % (nbr, " all" if new.get("all") else "")]


class Cvt_RtrBGP_AF_vrf_Nbr_NHSelf(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_NHSelf):

    pass


# Cvt_RtrBGP_AF_global_Nbr_Pwd
# does not exist - there is no global VRF version of this (done at the
# 'router bgp' level)


class Cvt_RtrBGP_AF_vrf_Nbr_Pwd(_AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_Nbr_Pwd):
    pass


# Cvt_RtrBGP_AF_global_Nbr_PrGrpMbr
# does not exist - there is no global VRF version of this (done at the
# 'router bgp' level)


class Cvt_RtrBGP_AF_vrf_Nbr_PrGrpMbr(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_Nbr_PrGrpMbr):

    pass


class Cvt_RtrBGP_AF_global_Nbr_PfxLst(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "prefix-list", None

    def remove(self, old, c, nbr, dir_):
        return self.enter(*c) + [
                   "  no neighbor %s prefix-list %s %s" % (nbr, old, dir_)]

    def update(self, old, upd, new, c, nbr, dir_):
        return self.enter(*c) + [
                   "  neighbor %s prefix-list %s %s" % (nbr, new, dir_)]


class Cvt_RtrBGP_AF_vrf_Nbr_PfxLst(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_PfxLst):

    pass


class Cvt_RtrBGP_AF_vrf_Nbr_RemAS(_AbsCvt_RtrBGP_AF_vrf_Nbr):
    cmd = "remote-as",
    sort_key = "0_remote-as",

    def remove(self, old, c, nbr):
        return self.enter(*c) + [
                   "  no neighbor %s remote-as" % nbr]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   "  neighbor %s remote-as %s" % (nbr, new)]


class Cvt_RtrBGP_AF_global_Nbr_RemPrivAS(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "remove-private-as",

    def truncate(self, old, rem, new, c, nbr):
        # if we're truncating, we must be changing to the plain form
        return self.enter(*c) + [
                   "  neighbor %s remove-private-as" % nbr]

    def remove(self, old, c, nbr):
        # removing the entire command requires that 'all' is specified,
        # if it is enabled, otherwise nothing will be removed
        return self.enter(*c) + [
                   "  no neighbor %s remove-private-as%s"
                       % (nbr, " all" if old.get("all") else "")]

    def update(self, old, upd, new, c, nbr):
        # either updatring to 'all' or adding a plain form
        return self.enter(*c) + [
                   "  neighbor %s remove-private-as%s"
                       % (nbr, " all" if new.get("all") else "")]


class Cvt_RtrBGP_AF_vrf_Nbr_RemPrivAS(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_RemPrivAS):

    pass


class Cvt_RtrBGP_AF_global_Nbr_RtMap(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "route-map", None

    def remove(self, old, c, nbr, dir_):
        return self.enter(*c) + [
                   "  no neighbor %s route-map %s %s" % (nbr, old, dir_)]

    def update(self, old, upd, new, c, nbr, dir_):
        return self.enter(*c) + [
                   "  neighbor %s route-map %s %s" % (nbr, new, dir_)]


class Cvt_RtrBGP_AF_vrf_Nbr_RtMap(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_RtMap):

    pass


class Cvt_RtrBGP_AF_global_Nbr_SndCmty(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "send-community", None

    # the 'neighbor ... send-community' command is odd in that the
    # 'standard', 'extended' and 'both' options don't replace the
    # current setting but add or remove those communities to it
    #
    # the configuration is expressed as a set containing none, one or
    # both of 'standard' and 'extended'

    def remove(self, old, c, nbr, cmty):
       return self.enter(*c) + [
                   "  no neighbor %s send-community %s" % (nbr, cmty)]

    def update(self, old, upd, new, c, nbr, cmty):
        return self.enter(*c) + [
                   "  neighbor %s send-community %s" % (nbr, cmty)]


class Cvt_RtrBGP_AF_vrf_Nbr_SndCmty(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_SndCmty):

    pass


class Cvt_RtrBGP_AF_global_Nbr_SoftRecfg(_AbsCvt_RtrBGP_AF_global_Nbr):
    cmd = "soft-reconfiguration",

    def remove(self, old, c, nbr):
        return self.enter(*c) + [
                   "  no neighbor %s soft-reconfiguration %s" % (nbr, old)]

    def update(self, old, upd, new, c, nbr):
        return self.enter(*c) + [
                   "  neighbor %s soft-reconfiguration %s" % (nbr, new)]


class Cvt_RtrBGP_AF_vrf_Nbr_SoftRecfg(
    _AbsCvt_RtrBGP_AF_vrf_Nbr, Cvt_RtrBGP_AF_global_Nbr_SoftRecfg):

    pass



# =============================================================================
# router ospf ...
# =============================================================================



class Cvt_RtrOSPF(Convert):
    cmd = "router", "ospf", None

    def remove(self, old, proc):
        return "no router ospf " + str(proc)

    def add(self, new, proc):
        return "router ospf " + str(proc)


class Context_RtrOSPF(Convert):
    context = Cvt_RtrOSPF.cmd

    def enter(self, proc):
        return ["router ospf " + str(proc)]


class Cvt_RtrOSPF_Id(Context_RtrOSPF):
    cmd = "id",

    def remove(self, old, c):
        return self.enter(*c) + [" no router-id"]

    def update(self, old, upd, new, c):
        return self.enter(*c) + [" router-id " + new]


class Cvt_RtrOSPF_AreaNSSA(Context_RtrOSPF):
    cmd = "area", None, "nssa"

    def remove(self, old, c, area):
        return self.enter(*c) + [" no area %s nssa" % area]

    def truncate(self, old, upd, new, c, area):
        # if we're truncating, we're removing options and we do that by
        # just re-entering the command without them, same as update()
        return self.update(old, None, new, c, area)

    def update(self, old, upd, new, c, area):
        s = ""
        if "no-redistribution" in new: s += " no-redistribution"
        if "no-summary" in new: s += " no-summary"
        return self.enter(*c) + [" area %s nssa%s" % (area, s)]


# passive-interface configuration is slightly odd as the default mode is
# stored (assuming it's not the default) and then a list of exceptions
# is maintained and it can go either way


class Cvt_RtrOSPF_PasvInt_Dflt(Context_RtrOSPF):
    cmd = "passive-interface", "default"

    def remove(self, old, c):
        return self.enter(*c) + [" no passive-interface default"]

    def update(self, old, upd, new, c):
        return self.enter(*c) + [" passive-interface default"]


# ... the exception interface lists must execute after changing the
# default mode, which they will do as 'default' comes before 'interface'
# and 'no-interface'

class Cvt_RtrOSPF_PasvInt_Int(Context_RtrOSPF):
    cmd = "passive-interface",
    ext = "interface", None

    def delete(self, old, rem, new, c, int_name):
        # if we're changing the default mode, the old list of exceptions
        # will be removed by that, so we don't need to do it
        if (old or {}).get("default") == (new or {}).get("default"):
            return self.enter(*c) + [" no passive-interface " + int_name]

    def update(self, old, upd, new, c, int_name):
        return self.enter(*c) + [" passive-interface " + int_name]


class Cvt_RtrOSPF_PasvInt_NoInt(Context_RtrOSPF):
    cmd = "passive-interface",
    ext = "no-interface", None

    def delete(self, old, rem, new, c, int_name):
        # if we're changing the default mode, the old list of exceptions
        # will be removed by that, so we don't need to do it
        if (old or {}).get("default") == (new or {}).get("default"):
            return self.enter(*c) + [" passive-interface " + int_name]

    def update(self, old, upd, new, c, int_name):
        return self.enter(*c) + [" no passive-interface " + int_name]



# =============================================================================
# router ospfv3 ...
# =============================================================================



class Cvt_RtrOSPFv3(Convert):
    cmd = "router", "ospfv3", None

    def remove(self, old, c, proc):
        return "no router ospfv3 " + str(proc)

    def add(self, new, c, proc):
        return "router ospfv3 " + str(proc)


class Context_RtrOSPFv3(Convert):
    context = Cvt_RtrOSPFv3.cmd

    def enter(self, proc):
        return ["router ospfv3 " + str(proc)]


class Cvt_RtrOSPFv3_Id(Context_RtrOSPFv3):
    cmd = "id",

    def remove(self, old, c):
        return self.enter(*c) + [" no router-id"]

    def update(self, old, upd, new, c):
        return self.enter(*c) + [" router-id " + new]


class Cvt_RtrOSPFv3_AreaNSSA(Context_RtrOSPFv3):
    cmd = "area", None, "nssa"

    def remove(self, old, c, area):
        return self.enter(*c) + [" no area %s nssa" % area]

    def truncate(self, old, upd, new, c, area):
        # if we're truncating, we're removing options and we do that by
        # just re-entering the command without them, same as update()
        return self.update(old, None, new, c, area)

    def update(self, old, upd, new, c, area):
        s = ""
        if "no-redistribution" in new: s += " no-redistribution"
        if "no-summary" in new: s += " no-summary"
        return self.enter(*c) + [" area %s nssa%s" % (area, s)]


class Cvt_RtrOSPFv3_AF(Context_RtrOSPFv3):
    cmd = "address-family", None

    def remove(self, old, c, af):
        return self.enter(*c) + [" no address-family " + af]

    def add(self, new, c, af):
        return self.enter(*c) + [" address-family " + af]


class Context_RtrOSPFv3_AF(Context_RtrOSPFv3):
    context = Context_RtrOSPFv3.context + Cvt_RtrOSPFv3_AF.cmd

    def enter(self, *c):
        c_super, (af, ) = c[:-1], c[-1:]
        return super().enter(*c_super) + [" address-family " + af]


# see the Cvt_RtrOSPF_... versions above for the explanation of how
# these converters work


class Cvt_RtrOSPFv3_AF_PasvInt_Dflt(Context_RtrOSPFv3_AF):
    cmd = "passive-interface", "default"

    def remove(self, old, c):
        return self.enter(*c) + [" no passive-interface default"]

    def update(self, old, upd, new, c):
        return self.enter(*c) + [" passive-interface default"]


class Cvt_RtrOSPFv3_AF_PasvInt_Int(Context_RtrOSPFv3_AF):
    cmd = "passive-interface",
    ext = "interface", None

    def delete(self, old, rem, new, c, int_name):
        if (old or {}).get("default") == (new or {}).get("default"):
            return self.enter(*c) + [" no passive-interface " + int_name]

    def update(self, old, upd, new, c, int_name):
        return self.enter(*c) + [" passive-interface " + int_name]


class Cvt_RtrOSPFv3_AF_PasvInt_NoInt(Context_RtrOSPFv3_AF):
    cmd = "passive-interface",
    ext = "no-interface", None

    def delete(self, old, rem, new, c, int_name):
        if (old or {}).get("default") == (new or {}).get("default"):
            return self.enter(*c) + [" passive-interface " + int_name]

    def update(self, old, upd, new, c, int_name):
        return self.enter(*c) + [" no passive-interface " + int_name]
