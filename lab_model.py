import argparse
import glob
import ipaddress
import json
import os
import random
import subprocess
import sys
import textwrap
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set


PROFILE_LIBRARY = {
    'mls_vlan10_20_gateway': {
        'device_type': 'switch',
        'description': (
            'Multilayer switch acting as the default gateway for VLAN 10/20 '
            'with DHCP helper addresses, cloned from DHCPwithVLANs answers.'
        ),
        'running_config': textwrap.dedent(
            """\
            !
            version 16.3.2
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname S1
            !
            !
            !
            !
            !
            !
            !
            ip cef
            ip routing
            !
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface GigabitEthernet1/0/1
            !
            interface GigabitEthernet1/0/2
             switchport access vlan 10
            !
            interface GigabitEthernet1/0/3
             switchport access vlan 20
            !
            interface GigabitEthernet1/0/4
            !
            interface GigabitEthernet1/0/5
            !
            interface GigabitEthernet1/0/6
            !
            interface GigabitEthernet1/0/7
            !
            interface GigabitEthernet1/0/8
            !
            interface GigabitEthernet1/0/9
            !
            interface GigabitEthernet1/0/10
            !
            interface GigabitEthernet1/0/11
            !
            interface GigabitEthernet1/0/12
            !
            interface GigabitEthernet1/0/13
            !
            interface GigabitEthernet1/0/14
            !
            interface GigabitEthernet1/0/15
            !
            interface GigabitEthernet1/0/16
            !
            interface GigabitEthernet1/0/17
            !
            interface GigabitEthernet1/0/18
            !
            interface GigabitEthernet1/0/19
            !
            interface GigabitEthernet1/0/20
            !
            interface GigabitEthernet1/0/21
            !
            interface GigabitEthernet1/0/22
            !
            interface GigabitEthernet1/0/23
            !
            interface GigabitEthernet1/0/24
            !
            interface GigabitEthernet1/1/1
            !
            interface GigabitEthernet1/1/2
            !
            interface GigabitEthernet1/1/3
            !
            interface GigabitEthernet1/1/4
            !
            interface Vlan1
             ip address 10.1.1.1 255.255.255.0
            !
            interface Vlan10
             mac-address 0090.219d.7001
             ip address 10.1.10.1 255.255.255.0
             ip helper-address 10.1.1.254
            !
            interface Vlan20
             mac-address 0090.219d.7002
             ip address 10.1.20.1 255.255.255.0
             ip helper-address 10.1.1.254
            !
            ip classless
            ip route 1.1.1.1 255.255.255.255 10.1.1.254 
            !
            ip flow-export version 9
            !
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            version 16.3.2
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname S1
            !
            !
            !
            !
            !
            !
            !
            ip cef
            ip routing
            !
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface GigabitEthernet1/0/1
            !
            interface GigabitEthernet1/0/2
             switchport access vlan 10
            !
            interface GigabitEthernet1/0/3
             switchport access vlan 20
            !
            interface GigabitEthernet1/0/4
            !
            interface GigabitEthernet1/0/5
            !
            interface GigabitEthernet1/0/6
            !
            interface GigabitEthernet1/0/7
            !
            interface GigabitEthernet1/0/8
            !
            interface GigabitEthernet1/0/9
            !
            interface GigabitEthernet1/0/10
            !
            interface GigabitEthernet1/0/11
            !
            interface GigabitEthernet1/0/12
            !
            interface GigabitEthernet1/0/13
            !
            interface GigabitEthernet1/0/14
            !
            interface GigabitEthernet1/0/15
            !
            interface GigabitEthernet1/0/16
            !
            interface GigabitEthernet1/0/17
            !
            interface GigabitEthernet1/0/18
            !
            interface GigabitEthernet1/0/19
            !
            interface GigabitEthernet1/0/20
            !
            interface GigabitEthernet1/0/21
            !
            interface GigabitEthernet1/0/22
            !
            interface GigabitEthernet1/0/23
            !
            interface GigabitEthernet1/0/24
            !
            interface GigabitEthernet1/1/1
            !
            interface GigabitEthernet1/1/2
            !
            interface GigabitEthernet1/1/3
            !
            interface GigabitEthernet1/1/4
            !
            interface Vlan1
             ip address 10.1.1.1 255.255.255.0
            !
            interface Vlan10
             mac-address 0090.219d.7001
             ip address 10.1.10.1 255.255.255.0
             ip helper-address 10.1.1.254
            !
            interface Vlan20
             mac-address 0090.219d.7002
             ip address 10.1.20.1 255.255.255.0
             ip helper-address 10.1.1.254
            !
            ip classless
            ip route 1.1.1.1 255.255.255.255 10.1.1.254 
            !
            ip flow-export version 9
            !
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
    },
    'edge_access_vlan10_20': {
        'device_type': 'switch',
        'description': (
            'Layer-2 access switch with VLAN 10/20 access ports and dual trunks '
            'toward the core; derived from BasicVLANs answers but normalized '
            'to the 3650 hardware layout used in test.xml.'
        ),
        'running_config': textwrap.dedent(
            """\
            !
            version 16.3.2
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname EdgeSwitch
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            spanning-tree extend system-id
            !
            vlan 10
             name VLAN0010
            vlan 20
             name VLAN0020
            !
            interface GigabitEthernet1/0/1
             switchport access vlan 10
             switchport mode access
             spanning-tree portfast
            !
            interface GigabitEthernet1/0/2
             switchport access vlan 20
             switchport mode access
             spanning-tree portfast
            !
            interface GigabitEthernet1/0/3
             switchport trunk encapsulation dot1q
             switchport mode trunk
             switchport trunk allowed vlan 10,20
            !
            interface GigabitEthernet1/0/4
             switchport trunk encapsulation dot1q
             switchport mode trunk
             switchport trunk allowed vlan 10,20
            !
            interface GigabitEthernet1/0/5
            !
            interface GigabitEthernet1/0/6
            !
            interface GigabitEthernet1/0/7
            !
            interface GigabitEthernet1/0/8
            !
            interface GigabitEthernet1/0/9
            !
            interface GigabitEthernet1/0/10
            !
            interface GigabitEthernet1/0/11
            !
            interface GigabitEthernet1/0/12
            !
            interface GigabitEthernet1/0/13
            !
            interface GigabitEthernet1/0/14
            !
            interface GigabitEthernet1/0/15
            !
            interface GigabitEthernet1/0/16
            !
            interface GigabitEthernet1/0/17
            !
            interface GigabitEthernet1/0/18
            !
            interface GigabitEthernet1/0/19
            !
            interface GigabitEthernet1/0/20
            !
            interface GigabitEthernet1/0/21
            !
            interface GigabitEthernet1/0/22
            !
            interface GigabitEthernet1/0/23
            !
            interface GigabitEthernet1/0/24
            !
            interface GigabitEthernet1/1/1
            !
            interface GigabitEthernet1/1/2
            !
            interface GigabitEthernet1/1/3
            !
            interface GigabitEthernet1/1/4
            !
            interface Vlan1
             ip address 10.1.1.2 255.255.255.0
            !
            ip default-gateway 10.1.1.254
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            line vty 5 15
             login
            !
            end
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            version 16.3.2
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname EdgeSwitch
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            spanning-tree extend system-id
            !
            vlan 10
             name VLAN0010
            vlan 20
             name VLAN0020
            !
            interface GigabitEthernet1/0/1
             switchport access vlan 10
             switchport mode access
             spanning-tree portfast
            !
            interface GigabitEthernet1/0/2
             switchport access vlan 20
             switchport mode access
             spanning-tree portfast
            !
            interface GigabitEthernet1/0/3
             switchport trunk encapsulation dot1q
             switchport mode trunk
             switchport trunk allowed vlan 10,20
            !
            interface GigabitEthernet1/0/4
             switchport trunk encapsulation dot1q
             switchport mode trunk
             switchport trunk allowed vlan 10,20
            !
            interface GigabitEthernet1/0/5
            !
            interface GigabitEthernet1/0/6
            !
            interface GigabitEthernet1/0/7
            !
            interface GigabitEthernet1/0/8
            !
            interface GigabitEthernet1/0/9
            !
            interface GigabitEthernet1/0/10
            !
            interface GigabitEthernet1/0/11
            !
            interface GigabitEthernet1/0/12
            !
            interface GigabitEthernet1/0/13
            !
            interface GigabitEthernet1/0/14
            !
            interface GigabitEthernet1/0/15
            !
            interface GigabitEthernet1/0/16
            !
            interface GigabitEthernet1/0/17
            !
            interface GigabitEthernet1/0/18
            !
            interface GigabitEthernet1/0/19
            !
            interface GigabitEthernet1/0/20
            !
            interface GigabitEthernet1/0/21
            !
            interface GigabitEthernet1/0/22
            !
            interface GigabitEthernet1/0/23
            !
            interface GigabitEthernet1/0/24
            !
            interface GigabitEthernet1/1/1
            !
            interface GigabitEthernet1/1/2
            !
            interface GigabitEthernet1/1/3
            !
            interface GigabitEthernet1/1/4
            !
            interface Vlan1
             ip address 10.1.1.2 255.255.255.0
            !
            ip default-gateway 10.1.1.254
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            line vty 5 15
             login
            !
            end
            """
        ),
    },
    'branch_router_dhcp_single_vlan': {
        'device_type': 'router',
        'description': (
            'Single-VLAN ISR router acting as DHCP server and default gateway for '
            '10.1.1.0/24, cloned from DHCPbasic answers.'
        ),
        'running_config': textwrap.dedent(
            """\
            !
            version 15.4
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname R1
            !
            !
            !
            !
            ip dhcp excluded-address 10.1.1.1 10.1.1.100
            !
            ip dhcp pool pc
             network 10.1.1.0 255.255.255.0
             default-router 10.1.1.254
             dns-server 10.1.1.254
            !
            !
            !
            no ip cef
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface Loopback0
             ip address 1.1.1.1 255.255.255.255
            !
            interface GigabitEthernet0/0/0
             ip address 10.1.1.254 255.255.255.0
             duplex auto
             speed auto
            !
            interface GigabitEthernet0/0/1
             no ip address
             duplex auto
             speed auto
             shutdown
            !
            interface Vlan1
             no ip address
             shutdown
            !
            ip classless
            !
            ip flow-export version 9
            !
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            version 15.4
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname R1
            !
            !
            !
            !
            ip dhcp excluded-address 10.1.1.1 10.1.1.100
            !
            ip dhcp pool pc
             network 10.1.1.0 255.255.255.0
             default-router 10.1.1.254
             dns-server 10.1.1.254
            !
            !
            !
            no ip cef
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface Loopback0
             ip address 1.1.1.1 255.255.255.255
            !
            interface GigabitEthernet0/0/0
             ip address 10.1.1.254 255.255.255.0
             duplex auto
             speed auto
            !
            interface GigabitEthernet0/0/1
             no ip address
             duplex auto
             speed auto
             shutdown
            !
            interface Vlan1
             no ip address
             shutdown
            !
            ip classless
            !
            ip flow-export version 9
            !
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
    },
    'campus_router_vlan10_20_dhcp': {
        'device_type': 'router',
        'description': (
            'Dual-scope DHCP router feeding VLAN 10/20 with helper routes toward '
            'the multilayer switch, based on DHCPwithVLANs answers.'
        ),
        'running_config': textwrap.dedent(
            """\
            !
            version 15.4
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname R1
            !
            !
            !
            !
            ip dhcp excluded-address 10.1.10.1 10.1.10.10
            ip dhcp excluded-address 10.1.20.1 10.1.20.10
            !
            ip dhcp pool vlan10
             network 10.1.10.0 255.255.255.0
             default-router 10.1.10.1
             dns-server 10.1.1.254
            ip dhcp pool vlan20
             network 10.1.20.0 255.255.255.0
             default-router 10.1.20.1
             dns-server 10.1.1.254
            !
            !
            !
            no ip cef
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface Loopback0
             ip address 1.1.1.1 255.255.255.255
            !
            interface GigabitEthernet0/0/0
             ip address 10.1.1.254 255.255.255.0
             duplex auto
             speed auto
            !
            interface GigabitEthernet0/0/1
             no ip address
             duplex auto
             speed auto
             shutdown
            !
            interface Vlan1
             no ip address
             shutdown
            !
            ip classless
            ip route 10.1.10.0 255.255.255.0 10.1.1.1
            ip route 10.1.20.0 255.255.255.0 10.1.1.1
            !
            ip flow-export version 9
            !
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            version 15.4
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname R1
            !
            !
            !
            !
            ip dhcp excluded-address 10.1.10.1 10.1.10.10
            ip dhcp excluded-address 10.1.20.1 10.1.20.10
            !
            ip dhcp pool vlan10
             network 10.1.10.0 255.255.255.0
             default-router 10.1.10.1
             dns-server 10.1.1.254
            ip dhcp pool vlan20
             network 10.1.20.0 255.255.255.0
             default-router 10.1.20.1
             dns-server 10.1.1.254
            !
            !
            !
            no ip cef
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface Loopback0
             ip address 1.1.1.1 255.255.255.255
            !
            interface GigabitEthernet0/0/0
             ip address 10.1.1.254 255.255.255.0
             duplex auto
             speed auto
            !
            interface GigabitEthernet0/0/1
             no ip address
             duplex auto
             speed auto
             shutdown
            !
            interface Vlan1
             no ip address
             shutdown
            !
            ip classless
            ip route 10.1.10.0 255.255.255.0 10.1.1.1
            ip route 10.1.20.0 255.255.255.0 10.1.1.1
            !
            ip flow-export version 9
            !
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
    },
    'ospf_dual_link_router': {
        'device_type': 'router',
        'description': (
            'Two-link OSPF router from Subnetting Lab 2 answers; great for '
            'routing-focused drills.'
        ),
        'running_config': textwrap.dedent(
            """\
            !
            version 15.4
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname R1
            !
            !
            !
            !
            !
            !
            !
            !
            ip cef
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface GigabitEthernet0/0/0
             ip address 192.168.1.62 255.255.255.192
             duplex auto
             speed auto
            !
            interface GigabitEthernet0/0/1
             ip address 192.168.1.65 255.255.255.192
             duplex auto
             speed auto
            !
            interface Vlan1
             no ip address
             shutdown
            !
            router ospf 1
             log-adjacency-changes
             network 0.0.0.0 255.255.255.255 area 0
            !
            ip classless
            !
            ip flow-export version 9
            !
            !
            !
            no cdp run
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            version 15.4
            no service timestamps log datetime msec
            no service timestamps debug datetime msec
            no service password-encryption
            !
            hostname R1
            !
            !
            !
            !
            !
            !
            !
            !
            ip cef
            no ipv6 cef
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            !
            spanning-tree mode pvst
            !
            !
            !
            !
            !
            !
            interface GigabitEthernet0/0/0
             ip address 192.168.1.62 255.255.255.192
             duplex auto
             speed auto
            !
            interface GigabitEthernet0/0/1
             ip address 192.168.1.65 255.255.255.192
             duplex auto
             speed auto
            !
            interface Vlan1
             no ip address
             shutdown
            !
            router ospf 1
             log-adjacency-changes
             network 0.0.0.0 255.255.255.255 area 0
            !
            ip classless
            !
            ip flow-export version 9
            !
            !
            !
            no cdp run
            !
            !
            !
            !
            !
            !
            line con 0
            !
            line aux 0
            !
            line vty 0 4
             login
            !
            !
            !
            end
            """
        ),
    },
    'overlay_acl': {
        'device_type': 'router',
        'description': 'Overlay snippet for ACL policy tasks.',
        'running_config': textwrap.dedent(
            """\
            !
            ! Overlay: ACL policy placeholder
            ! Define standard/extended ACLs and apply to interfaces as needed.
            !
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            ! Overlay: ACL policy placeholder
            ! Define standard/extended ACLs and apply to interfaces as needed.
            !
            """
        ),
    },
    'overlay_nat': {
        'device_type': 'router',
        'description': 'Overlay snippet for NAT/PAT tasks.',
        'running_config': textwrap.dedent(
            """\
            !
            ! Overlay: NAT configuration placeholder
            ! Define inside/outside interfaces and NAT rules here.
            !
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            ! Overlay: NAT configuration placeholder
            ! Define inside/outside interfaces and NAT rules here.
            !
            """
        ),
    },
    'overlay_qos': {
        'device_type': 'router',
        'description': 'Overlay snippet for QoS policy tasks.',
        'running_config': textwrap.dedent(
            """\
            !
            ! Overlay: QoS policy placeholder
            ! Define class-maps, policy-maps, and service-policy on uplinks.
            !
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            ! Overlay: QoS policy placeholder
            ! Define class-maps, policy-maps, and service-policy on uplinks.
            !
            """
        ),
    },
    'overlay_ipv6': {
        'device_type': 'router',
        'description': 'Overlay snippet for IPv6 addressing tasks.',
        'running_config': textwrap.dedent(
            """\
            !
            ! Overlay: IPv6 enablement placeholder
            ! Enable IPv6 routing and assign IPv6 addresses on interfaces.
            !
            """
        ),
        'startup_config': textwrap.dedent(
            """\
            !
            ! Overlay: IPv6 enablement placeholder
            ! Enable IPv6 routing and assign IPv6 addresses on interfaces.
            !
            """
        ),
    },
}

def _discover_template_sources():
    base_dir = os.path.dirname(__file__)
    roots = [os.path.join(base_dir, 'templates', 'packettracer'),
             base_dir, os.path.join(base_dir, 'examples')]
    patterns = []
    for root in roots:
        patterns.extend([
            os.path.join(root, '*_source.xml'),
            os.path.join(root, '*_template.xml'),
            os.path.join(root, '**', '*_source.xml'),
            os.path.join(root, '**', '*_template.xml'),
        ])
    sources = []
    for pattern in patterns:
        sources.extend(glob.glob(pattern))
    return sources


EXTRA_TEMPLATE_SOURCES = [
    os.path.join('templates', 'packettracer', 'test.xml'),
    os.path.join('templates', 'packettracer', 'router_8200_source.xml'),
    os.path.join('examples', 'DHCPbasicAnswers.xml'),
    os.path.join('examples', 'DHCPwithVLANsAnswers.xml'),
    os.path.join('examples', 'SubnettingLab2Answers.xml'),
]
EXTRA_TEMPLATE_SOURCES.extend(_discover_template_sources())


class Lab:
    """Build Packet Tracer topologies by cloning templates from test.xml."""

    def __init__(self, rng=None):
        self.devices = []
        self.links = []
        self._name_counts = {}
        self._instruction_note_text = None
        self._note_position = (1200, 140)
        self._note_mem_seed = random.randint(2582360000000, 2582369999999)
        self._site_labels = []
        self._device_lookup = {}
        self._link_cable_memory = {}
        self._occupied_positions = set()
        self._occupied_list = []
        self._min_separation = 100
        self._rng = rng or random.Random()
        self._used_macs = set()

    def unique_name(self, base):
        """Return a device name that is unique inside this lab."""
        sanitized = (base or 'Device').strip() or 'Device'
        existing = {dev['name'] for dev in self.devices}
        if sanitized not in existing:
            self._name_counts[sanitized] = 1
            return sanitized
        suffix = self._name_counts.get(sanitized, 1) + 1
        while True:
            candidate = f'{sanitized}{suffix}'
            if candidate not in existing:
                self._name_counts[sanitized] = suffix
                return candidate
            suffix += 1

    def set_instruction_note_text(self, text, position=None):
        """Store human instructions that will be embedded as a Packet Tracer note."""
        cleaned = text.strip() if text else None
        self._instruction_note_text = cleaned if cleaned else None
        if position:
            self._note_position = position

    def add_site_label(self, text, position, z=40000, cluster_id='1-1'):
        """Add a short label note to help organize large logical layouts."""
        cleaned = text.strip() if text else None
        if not cleaned:
            return
        self._site_labels.append({
            'text': cleaned,
            'position': position,
            'z': z,
            'cluster_id': cluster_id,
        })

    def add_device(self, name, device_type, position=None, profile=None):
        """Register a device, optional logical position, and config profile."""
        if any(device['name'] == name for device in self.devices):
            raise ValueError(f'Device name {name} already exists; use lab.unique_name() for collisions.')
        resolved_position = self._resolve_position(position)
        info = {
            'name': name,
            'type': device_type,
            'position': resolved_position,
            'profile': profile,
        }
        self.devices.append(info)
        self._device_lookup[name] = info
        return name

    def _resolve_position(self, position):
        if not position:
            return position
        x, y = position
        min_x = 100
        base = (max(min_x, int(x)), int(y))

        def is_clear(candidate):
            if candidate in self._occupied_positions:
                return False
            for other in self._occupied_list:
                if abs(candidate[0] - other[0]) < self._min_separation and abs(candidate[1] - other[1]) < self._min_separation:
                    return False
            return True

        if is_clear(base):
            self._occupied_positions.add(base)
            self._occupied_list.append(base)
            return base

        step = 20
        max_radius = 240
        for radius in range(step, max_radius + step, step):
            for dx in range(-radius, radius + step, step):
                for dy in range(-radius, radius + step, step):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    candidate = (max(min_x, base[0] + dx), base[1] + dy)
                    if is_clear(candidate):
                        self._occupied_positions.add(candidate)
                        self._occupied_list.append(candidate)
                        return candidate

        for dx in range(20, 121, 20):
            for dy in range(20, 121, 20):
                candidate = (max(min_x, base[0] + dx), base[1] + dy)
                if is_clear(candidate):
                    self._occupied_positions.add(candidate)
                    self._occupied_list.append(candidate)
                    return candidate

        self._occupied_positions.add(base)
        self._occupied_list.append(base)
        return base

    def _infer_cable_type(self, dev1, dev2):
        def categorize(dev_name):
            dev = self._device_lookup.get(dev_name) or {}
            dtype = (dev.get('type') or '').lower()
            if dtype.startswith('switch'):
                return 'switch'
            if dtype.startswith('router'):
                return 'router'
            if dtype.startswith('server'):
                return 'pc'
            return 'pc'

        cat1 = categorize(dev1)
        cat2 = categorize(dev2)
        if cat1 == cat2:
            return 'eCrossOver'
        return 'eStraightThrough'

    def add_link(self, dev1, port1, dev2, port2, length='5', cable_type=None):
        pair_key = frozenset({dev1, dev2})
        resolved_type = cable_type or self._infer_cable_type(dev1, dev2)
        if pair_key in self._link_cable_memory:
            resolved_type = self._link_cable_memory[pair_key]
        else:
            self._link_cable_memory[pair_key] = resolved_type

        self.links.append({
            'dev1': dev1,
            'port1': port1,
            'dev2': dev2,
            'port2': port2,
            'length': str(length),
            'cable_type': resolved_type,
        })

    def _generate_mac(self):
        while True:
            first = 0x02
            rest = [self._rng.randint(0x00, 0xFF) for _ in range(5)]
            raw = bytes([first] + rest)
            mac = ''.join(f'{b:02X}' for b in raw)
            dotted = f'{mac[0:4]}.{mac[4:8]}.{mac[8:12]}'
            if dotted not in self._used_macs:
                self._used_macs.add(dotted)
                return dotted

    def _randomize_device_macs(self, device_elem):
        for port in device_elem.findall('.//PORT'):
            mac_elem = port.find('MACADDRESS')
            bia_elem = port.find('BIA')
            if mac_elem is None and bia_elem is None:
                continue
            mac = self._generate_mac()
            if mac_elem is not None:
                mac_elem.text = mac
            if bia_elem is not None:
                bia_elem.text = mac

    def to_packettracer_xml(self, path):
        """Clone devices from test.xml so every generated file matches PT 8.2 layout."""
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'packettracer', 'test.xml')
        if not os.path.exists(template_path):
            template_path = os.path.join(os.path.dirname(__file__), 'test.xml')
        if not os.path.exists(template_path):
            raise FileNotFoundError('test.xml not found; place a Packet Tracer 8.2 file next to this script.')

        tree = ET.parse(template_path)
        root = tree.getroot()
        template_version = root.findtext('VERSION')

        network = root.find('NETWORK')
        if network is None:
            raise ValueError('NETWORK section missing in test.xml')

        devices_elem = network.find('DEVICES')
        if devices_elem is None:
            raise ValueError('DEVICES section missing in test.xml')

        template_map = self._collect_templates(devices_elem)
        self._ensure_extra_templates(template_map)
        devices_elem.clear()

        device_refs = {}
        layout_tracker = {'switch': 0, 'pc': 0, 'router': 0, 'server': 0}
        physical_tracker = {'rack': 0, 'pc': 0}

        for idx, dev_info in enumerate(self.devices):
            template = self._pick_template(dev_info['type'], template_map)
            new_device = self._deep_copy_element(template)
            self._assign_unique_save_ref(new_device)
            self._rename_device(new_device, dev_info['name'])
            self._position_device(new_device, dev_info, layout_tracker)
            self._clean_workspace(new_device, idx, physical_tracker)
            self._randomize_device_macs(new_device)
            if dev_info.get('profile'):
                self._apply_profile(new_device, dev_info)
            save_ref = self._extract_save_ref(new_device)
            device_refs[dev_info['name']] = save_ref
            devices_elem.append(new_device)

        links_elem = network.find('LINKS')
        if links_elem is None:
            links_elem = ET.SubElement(network, 'LINKS')
        links_elem.clear()

        for link in self.links:
            if link['dev1'] not in device_refs or link['dev2'] not in device_refs:
                continue  # Skip invalid references
            link_elem = ET.SubElement(links_elem, 'LINK')
            ET.SubElement(link_elem, 'TYPE').text = 'eCopper'
            cable = ET.SubElement(link_elem, 'CABLE')
            ET.SubElement(cable, 'LENGTH').text = link['length']
            ET.SubElement(cable, 'FUNCTIONAL').text = 'true'
            ET.SubElement(cable, 'FROM').text = device_refs[link['dev1']]
            ET.SubElement(cable, 'PORT').text = link['port1']
            ET.SubElement(cable, 'TO').text = device_refs[link['dev2']]
            ET.SubElement(cable, 'PORT').text = link['port2']
            ET.SubElement(cable, 'TYPE').text = link['cable_type']

        self._rebuild_physical_workspace(root, devices_elem)
        self._inject_instruction_note(root)

        if template_version:
            version_elem = root.find('VERSION')
            if version_elem is not None:
                version_elem.text = template_version

        ET.indent(tree, space=' ')
        tree.write(path, encoding='utf-8', xml_declaration=False, short_empty_elements=False)
        print(f'Packet Tracer XML written to {path} using templates from test.xml')

    def _load_template_map(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'packettracer', 'test.xml')
        if not os.path.exists(template_path):
            template_path = os.path.join(os.path.dirname(__file__), 'test.xml')
        if not os.path.exists(template_path):
            raise FileNotFoundError('test.xml not found; place a Packet Tracer 8.2 file next to this script.')
        tree = ET.parse(template_path)
        root = tree.getroot()
        network = root.find('NETWORK')
        if network is None:
            raise ValueError('NETWORK section missing in test.xml')
        devices_elem = network.find('DEVICES')
        if devices_elem is None:
            raise ValueError('DEVICES section missing in test.xml')
        template_map = self._collect_templates(devices_elem)
        self._ensure_extra_templates(template_map)
        return template_map

    def _collect_templates(self, devices_elem, template_map=None):
        if template_map is None:
            template_map = {'switch': [], 'pc': [], 'router': [], 'server': []}
        for device in devices_elem.findall('DEVICE'):
            category = self._categorize_device(device)
            if category:
                template_map[category].append(self._deep_copy_element(device))
        return template_map

    def _pick_template(self, requested_type, template_map):
        lowered = requested_type.lower()
        if lowered.startswith('switch'):
            bucket = 'switch'
        elif lowered.startswith('pc'):
            bucket = 'pc'
        elif lowered.startswith('router'):
            bucket = 'router'
        elif lowered.startswith('server'):
            bucket = 'server'
        else:
            raise ValueError(f'Unsupported device type: {requested_type}')

        templates = template_map.get(bucket, [])
        if not templates:
            raise ValueError(
                f'No templates available for {bucket}; ensure test.xml or EXTRA_TEMPLATE_SOURCES provide one.'
            )
        return templates[0]

    def _categorize_device(self, device_elem):
        dev_type = device_elem.findtext('ENGINE/TYPE', '').lower()
        if 'switch' in dev_type:
            return 'switch'
        if dev_type.startswith('pc'):
            return 'pc'
        if dev_type.startswith('server') or 'server' in dev_type:
            return 'server'
        if 'router' in dev_type:
            return 'router'
        return None

    def _ensure_extra_templates(self, template_map):
        base_dir = os.path.dirname(__file__)
        seen = set()
        for relative in EXTRA_TEMPLATE_SOURCES:
            extra_path = relative if os.path.isabs(relative) else os.path.join(base_dir, relative)
            if extra_path in seen:
                continue
            seen.add(extra_path)
            if not os.path.exists(extra_path):
                continue
            try:
                extra_tree = ET.parse(extra_path)
            except ET.ParseError:
                continue
            extra_root = extra_tree.getroot()
            network = extra_root.find('NETWORK')
            if network is None:
                continue
            devices_elem = network.find('DEVICES')
            if devices_elem is None:
                continue
            self._collect_templates(devices_elem, template_map)

    def _assign_unique_save_ref(self, device_elem):
        engine = device_elem.find('ENGINE')
        if engine is None:
            return
        save_ref = engine.find('SAVE_REF_ID')
        if save_ref is None:
            save_ref = ET.SubElement(engine, 'SAVE_REF_ID')
        unique_value = uuid.uuid4().int >> 64
        save_ref.text = f'save-ref-id:{unique_value}'

    def _rename_device(self, device_elem, new_name):
        engine = device_elem.find('ENGINE')
        if engine is None:
            return
        name_elem = engine.find('NAME')
        if name_elem is not None:
            name_elem.text = new_name
        sys_name = engine.find('SYS_NAME')
        if sys_name is not None:
            sys_name.text = new_name

    def _position_device(self, device_elem, dev_info, layout_tracker):
        workspace = device_elem.find('WORKSPACE')
        if workspace is None:
            return
        logical = workspace.find('LOGICAL')
        if logical is None:
            return
        x_elem = logical.find('X')
        y_elem = logical.find('Y')

        if dev_info.get('position'):
            x_val, y_val = dev_info['position']
        else:
            lowered = dev_info['type'].lower()
            if lowered.startswith('switch'):
                column = layout_tracker['switch']
                layout_tracker['switch'] += 1
                x_val = 220 + column * 220
                y_val = 220
            elif lowered.startswith('router'):
                column = layout_tracker['router']
                layout_tracker['router'] += 1
                x_val = 220 + column * 220
                y_val = 80
            elif lowered.startswith('server'):
                column = layout_tracker['server']
                layout_tracker['server'] += 1
                x_val = 220 + column * 220
                y_val = 380
            else:
                column = layout_tracker['pc']
                layout_tracker['pc'] += 1
                x_val = 220 + column * 220
                y_val = 520

        if x_elem is not None:
            x_elem.text = str(x_val)
        if y_elem is not None:
            y_elem.text = str(y_val)

    def _clean_workspace(self, device_elem, idx, physical_tracker):
        workspace = device_elem.find('WORKSPACE')
        if workspace is None:
            workspace = ET.SubElement(device_elem, 'WORKSPACE')
        logical = workspace.find('LOGICAL')
        if logical is None:
            logical = ET.SubElement(workspace, 'LOGICAL')
        physical = workspace.find('PHYSICAL')
        if physical is None:
            physical = ET.SubElement(workspace, 'PHYSICAL')
        physical_cpur = workspace.find('PHYSICAL_CPUR')
        if physical_cpur is None:
            physical_cpur = ET.SubElement(workspace, 'PHYSICAL_CPUR')

        for tag in ['X_PN', 'Y_PN', 'X', 'Y', 'SLOT', 'SUBSLOT', 'PARENT_PATH', 'CONTAINER_ID']:
            if physical_cpur.find(tag) is None:
                ET.SubElement(physical_cpur, tag)

        device_type = device_elem.findtext('ENGINE/TYPE', '')
        lowered = device_type.lower()
        is_pc = lowered.startswith('pc') or lowered.startswith('server')

        homerack_uuids = [
            '866b072e-a242-4700-afc2-0d37fe0a38ac',
            '0d9c4da0-a254-4b80-8ef1-0af23052ef86',
            '940bdc5d-0715-4851-9c7b-6b1143f2af14',
            '79d0e2b3-9fae-487a-bace-2862f6689a40',
        ]
        rack_uuid = 'f6f9f4d5-6f96-46ef-b2f9-2f831132fb17'

        device_uuid = str(uuid.uuid4())
        if is_pc:
            physical.text = ','.join([f'{{{u}}}' for u in homerack_uuids[:3] + [device_uuid]])
            parent_path = ','.join([f'{{{u}}}' for u in homerack_uuids[:3]])
            container_uuid = homerack_uuids[2]
            position_index = physical_tracker['pc']
            physical_tracker['pc'] += 1
            x_val = 80 + (position_index % 4) * 70
            y_val = 200 + (position_index // 4) * 55
            slot_val = str(position_index)
        else:
            sequence = homerack_uuids + [rack_uuid, device_uuid]
            physical.text = ','.join([f'{{{u}}}' for u in sequence])
            parent_path = ','.join([f'{{{u}}}' for u in homerack_uuids])
            container_uuid = rack_uuid
            position_index = physical_tracker['rack']
            physical_tracker['rack'] += 1
            x_val = 4 + (position_index % 10) * 4
            y_val = (position_index // 10) * 4
            slot_val = str(position_index)

        x_text = str(x_val)
        y_text = str(y_val)

        physical_cpur.find('X').text = x_text
        physical_cpur.find('Y').text = y_text
        physical_cpur.find('X_PN').text = x_text
        physical_cpur.find('Y_PN').text = y_text
        physical_cpur.find('SLOT').text = slot_val
        physical_cpur.find('SUBSLOT').text = '0'
        physical_cpur.find('PARENT_PATH').text = parent_path
        physical_cpur.find('CONTAINER_ID').text = f'{{{container_uuid}}}'

        mem_addr = logical.find('MEM_ADDR')
        if mem_addr is None:
            mem_addr = ET.SubElement(logical, 'MEM_ADDR')
        mem_addr.text = str(2582301551760 + idx * 100000)

        dev_addr = logical.find('DEV_ADDR')
        if dev_addr is None:
            dev_addr = ET.SubElement(logical, 'DEV_ADDR')
        dev_addr.text = str(2582299771936 + idx * 100000)

    def _rebuild_physical_workspace(self, root, devices_elem):
        physicalworkspace = root.find('PHYSICALWORKSPACE')
        if physicalworkspace is None:
            return

        homerack_uuids = [
            '866b072e-a242-4700-afc2-0d37fe0a38ac',
            '0d9c4da0-a254-4b80-8ef1-0af23052ef86',
            '940bdc5d-0715-4851-9c7b-6b1143f2af14',
            '79d0e2b3-9fae-487a-bace-2862f6689a40',
        ]
        rack_uuid = 'f6f9f4d5-6f96-46ef-b2f9-2f831132fb17'

        homerack = physicalworkspace.find('HOMERACK')
        if homerack is not None:
            homerack.text = ','.join([f'{{{u}}}' for u in homerack_uuids])

        for node in physicalworkspace.findall('.//NODE'):
            for tag in ('ICP_CSX', 'ICP_CSY'):
                tag_elem = node.find(tag)
                if tag_elem is not None:
                    node.remove(tag_elem)

        wiring_closet = self._find_node_by_name_and_type(physicalworkspace, 'Main Wiring Closet', '3')
        corporate_office = self._find_node_by_name_and_type(physicalworkspace, 'Corporate Office', '2')
        if wiring_closet is None or corporate_office is None:
            return

        wc_children = wiring_closet.find('CHILDREN')
        if wc_children is None:
            wc_children = ET.SubElement(wiring_closet, 'CHILDREN')

        rack_node = None
        for child in wc_children.findall('NODE'):
            name_text = child.findtext('NAME', '').strip()
            type_text = child.findtext('TYPE', '').strip()
            if name_text == 'Rack' and type_text == '4':
                rack_node = child
                break
        if rack_node is None:
            rack_node = ET.Element('NODE')
            ET.SubElement(rack_node, 'X').text = '0'
            ET.SubElement(rack_node, 'Y').text = '0'
            ET.SubElement(rack_node, 'TYPE').text = '4'
            ET.SubElement(rack_node, 'NAME', {'translate': 'true'}).text = 'Rack'
            ET.SubElement(rack_node, 'SX').text = '1'
            ET.SubElement(rack_node, 'SY').text = '1'
            ET.SubElement(rack_node, 'W').text = '0'
            ET.SubElement(rack_node, 'H').text = '0'
            ET.SubElement(rack_node, 'D').text = '0'
            ET.SubElement(rack_node, 'PATH', {'isanim': 'false'}).text = '../art/Background/grid_100x100.png'
            ET.SubElement(rack_node, 'CHILDREN')
            ET.SubElement(rack_node, 'MANUAL_SCALING').text = 'false'
            ET.SubElement(rack_node, 'SCALED_PIXMAP_WIDTH').text = '0'
            ET.SubElement(rack_node, 'SCALED_PIXMAP_HEIGHT').text = '0'
            ET.SubElement(rack_node, 'INIT_WIDTH').text = '0'
            ET.SubElement(rack_node, 'INIT_HEIGHT').text = '0'
            ET.SubElement(rack_node, 'INIT_DEPTH').text = '0'
            ET.SubElement(rack_node, 'INIT_SX').text = '1'
            ET.SubElement(rack_node, 'INIT_SY').text = '1'
            ET.SubElement(rack_node, 'INIT_SZ').text = '1'
            ET.SubElement(rack_node, 'BG_TILED').text = 'false'
            ET.SubElement(rack_node, 'CUSTOM_IMAGE_WIDTH').text = '-1'
            ET.SubElement(rack_node, 'CUSTOM_IMAGE_HEIGHT').text = '-1'
            ET.SubElement(rack_node, 'SCALE_FACTOR').text = '1'
            ET.SubElement(rack_node, 'UUID_STR').text = f'{{{rack_uuid}}}'
            ET.SubElement(rack_node, 'SLOT').text = '0'
            ET.SubElement(rack_node, 'SUB_SLOT').text = '0'
            wc_children.append(rack_node)

        rack_children = rack_node.find('CHILDREN')
        if rack_children is None:
            rack_children = ET.SubElement(rack_node, 'CHILDREN')
        for node in list(rack_children.findall('NODE')):
            rack_children.remove(node)

        pdu_node = ET.Element('NODE')
        ET.SubElement(pdu_node, 'X').text = '0'
        ET.SubElement(pdu_node, 'Y').text = '0'
        ET.SubElement(pdu_node, 'TYPE').text = '6'
        ET.SubElement(pdu_node, 'NAME', {'translate': 'true'}).text = 'Power Distribution Device0'
        ET.SubElement(pdu_node, 'SX').text = '0.2'
        ET.SubElement(pdu_node, 'SY').text = '0.2'
        ET.SubElement(pdu_node, 'W').text = '20'
        ET.SubElement(pdu_node, 'H').text = '20'
        ET.SubElement(pdu_node, 'D').text = '0'
        ET.SubElement(pdu_node, 'PATH', {'isanim': 'false'}).text = '../art/Background/grid_100x100.png'
        ET.SubElement(pdu_node, 'CHILDREN')
        ET.SubElement(pdu_node, 'MANUAL_SCALING').text = 'false'
        ET.SubElement(pdu_node, 'SCALED_PIXMAP_WIDTH').text = '0'
        ET.SubElement(pdu_node, 'SCALED_PIXMAP_HEIGHT').text = '0'
        ET.SubElement(pdu_node, 'INIT_WIDTH').text = '20'
        ET.SubElement(pdu_node, 'INIT_HEIGHT').text = '20'
        ET.SubElement(pdu_node, 'INIT_DEPTH').text = '0'
        ET.SubElement(pdu_node, 'INIT_SX').text = '0.2'
        ET.SubElement(pdu_node, 'INIT_SY').text = '0.2'
        ET.SubElement(pdu_node, 'INIT_SZ').text = '0.2'
        ET.SubElement(pdu_node, 'BG_TILED').text = 'false'
        ET.SubElement(pdu_node, 'CUSTOM_IMAGE_WIDTH').text = '-1'
        ET.SubElement(pdu_node, 'CUSTOM_IMAGE_HEIGHT').text = '-1'
        ET.SubElement(pdu_node, 'SCALE_FACTOR').text = '1'
        ET.SubElement(pdu_node, 'UUID_STR').text = f'{{{uuid.uuid4()}}}'
        ET.SubElement(pdu_node, 'SLOT').text = '0'
        ET.SubElement(pdu_node, 'SUB_SLOT').text = '0'
        rack_children.append(pdu_node)

        corp_children = corporate_office.find('CHILDREN')
        if corp_children is None:
            corp_children = ET.SubElement(corporate_office, 'CHILDREN')
        for node in list(corp_children.findall('NODE')):
            if node.findtext('TYPE', '').strip() == '6':
                corp_children.remove(node)

        for device in devices_elem.findall('DEVICE'):
            workspace = device.find('WORKSPACE')
            if workspace is None:
                continue
            engine = device.find('ENGINE')
            if engine is None:
                continue
            name_elem = engine.find('NAME')
            device_name = name_elem.text if name_elem is not None else 'Device'
            device_type = engine.findtext('TYPE', '')
            physical = workspace.find('PHYSICAL')
            physical_cpur = workspace.find('PHYSICAL_CPUR')
            if physical is None or physical_cpur is None or not physical.text:
                continue
            uuid_parts = [part.strip() for part in physical.text.split(',') if part.strip()]
            if not uuid_parts:
                continue
            device_uuid = uuid_parts[-1]
            x_val = physical_cpur.findtext('X', '0')
            y_val = physical_cpur.findtext('Y', '0')
            slot_val = physical_cpur.findtext('SLOT', '0')
            subslot_val = physical_cpur.findtext('SUBSLOT', '0')
            node = self._build_device_node(device_name, x_val, y_val, slot_val, subslot_val, device_uuid)
            if node is None:
                continue
            lowered = device_type.lower()
            if 'pc' in lowered or 'server' in lowered:
                corp_children.append(node)
            else:
                rack_children.append(node)

    def _inject_instruction_note(self, root):
        if not self._instruction_note_text and not self._site_labels:
            return
        physicalworkspace = root.find('PHYSICALWORKSPACE')
        if physicalworkspace is None:
            return
        notes_elem = physicalworkspace.find('NOTES')
        if notes_elem is None:
            notes_elem = ET.SubElement(physicalworkspace, 'NOTES')
        else:
            for existing in list(notes_elem.findall('NOTE')):
                notes_elem.remove(existing)
        if self._instruction_note_text:
            note_elem = ET.SubElement(notes_elem, 'NOTE', {'uuid': f'{{{uuid.uuid4()}}}'})
            x_val, y_val = self._note_position
            ET.SubElement(note_elem, 'X').text = str(x_val)
            ET.SubElement(note_elem, 'Y').text = str(y_val)
            ET.SubElement(note_elem, 'Z').text = '40000'
            ET.SubElement(note_elem, 'TEXT', {'translate': 'true'}).text = self._instruction_note_text
            ET.SubElement(note_elem, 'NOTECLUSTERID').text = '1-1'
            ET.SubElement(note_elem, 'MEM_ADDR').text = str(self._note_mem_seed)
            self._note_mem_seed += 256

        for label in self._site_labels:
            label_elem = ET.SubElement(notes_elem, 'NOTE', {'uuid': f'{{{uuid.uuid4()}}}'})
            x_val, y_val = label['position']
            ET.SubElement(label_elem, 'X').text = str(x_val)
            ET.SubElement(label_elem, 'Y').text = str(y_val)
            ET.SubElement(label_elem, 'Z').text = str(label.get('z', 40000))
            ET.SubElement(label_elem, 'TEXT', {'translate': 'true'}).text = label['text']
            cluster_id = label.get('cluster_id')
            ET.SubElement(label_elem, 'NOTECLUSTERID').text = cluster_id or ''
            ET.SubElement(label_elem, 'MEM_ADDR').text = str(self._note_mem_seed)
            self._note_mem_seed += 256

    def _find_node_by_name_and_type(self, node, target_name, target_type):
        if node is None:
            return None
        name_elem = node.find('NAME')
        type_elem = node.find('TYPE')
        if name_elem is not None and type_elem is not None:
            if (name_elem.text or '').strip() == target_name and (type_elem.text or '').strip() == target_type:
                return node
        for child in node.findall('NODE'):
            result = self._find_node_by_name_and_type(child, target_name, target_type)
            if result is not None:
                return result
        children = node.find('CHILDREN')
        if children is not None:
            for child in children.findall('NODE'):
                result = self._find_node_by_name_and_type(child, target_name, target_type)
                if result is not None:
                    return result
        return None

    def _build_device_node(self, name, x_val, y_val, slot_val, subslot_val, uuid_str):
        uuid_clean = uuid_str if uuid_str.startswith('{') else f'{{{uuid_str}}}'
        node = ET.Element('NODE')
        ET.SubElement(node, 'X').text = str(x_val)
        ET.SubElement(node, 'Y').text = str(y_val)
        ET.SubElement(node, 'TYPE').text = '6'
        ET.SubElement(node, 'NAME', {'translate': 'true'}).text = name
        ET.SubElement(node, 'SX').text = '1'
        ET.SubElement(node, 'SY').text = '1'
        ET.SubElement(node, 'W').text = '0'
        ET.SubElement(node, 'H').text = '0'
        ET.SubElement(node, 'D').text = '0'
        ET.SubElement(node, 'PATH', {'isanim': 'false'}).text = '../art/Background/grid_100x100.png'
        ET.SubElement(node, 'CHILDREN')
        ET.SubElement(node, 'MANUAL_SCALING').text = 'false'
        ET.SubElement(node, 'SCALED_PIXMAP_WIDTH').text = '0'
        ET.SubElement(node, 'SCALED_PIXMAP_HEIGHT').text = '0'
        ET.SubElement(node, 'INIT_WIDTH').text = '0'
        ET.SubElement(node, 'INIT_HEIGHT').text = '0'
        ET.SubElement(node, 'INIT_DEPTH').text = '0'
        ET.SubElement(node, 'INIT_SX').text = '1'
        ET.SubElement(node, 'INIT_SY').text = '1'
        ET.SubElement(node, 'INIT_SZ').text = '1'
        ET.SubElement(node, 'BG_TILED').text = 'false'
        ET.SubElement(node, 'CUSTOM_IMAGE_WIDTH').text = '-1'
        ET.SubElement(node, 'CUSTOM_IMAGE_HEIGHT').text = '-1'
        ET.SubElement(node, 'SCALE_FACTOR').text = '1'
        ET.SubElement(node, 'UUID_STR').text = uuid_clean
        ET.SubElement(node, 'SLOT').text = str(slot_val)
        ET.SubElement(node, 'SUB_SLOT').text = str(subslot_val)
        return node

    def _extract_save_ref(self, device_elem):
        engine = device_elem.find('ENGINE')
        if engine is None:
            raise ValueError('Device template missing ENGINE block')
        save_ref = engine.find('SAVE_REF_ID')
        if save_ref is None or not save_ref.text:
            raise ValueError('Device template missing SAVE_REF_ID; test.xml must include one')
        return save_ref.text

    def _deep_copy_element(self, elem):
        new_elem = ET.Element(elem.tag, elem.attrib)
        new_elem.text = elem.text
        new_elem.tail = elem.tail
        for child in elem:
            new_elem.append(self._deep_copy_element(child))
        return new_elem

    def _apply_profile(self, device_elem, dev_info):
        profile_spec = dev_info.get('profile')
        if not profile_spec:
            return
        profile_names = profile_spec if isinstance(profile_spec, (list, tuple)) else [profile_spec]

        profiles = []
        for profile_name in profile_names:
            profile = PROFILE_LIBRARY.get(profile_name)
            if profile is None:
                raise ValueError(f'Profile {profile_name} is not defined')
            expected = profile.get('device_type')
            if expected and not dev_info['type'].lower().startswith(expected):
                raise ValueError(f'Profile {profile_name} expects device type {expected}')
            profiles.append(profile)

        engine = device_elem.find('ENGINE')
        if engine is None:
            return

        running_blocks = [profile.get('running_config') for profile in profiles if profile.get('running_config')]
        startup_blocks = [profile.get('startup_config') for profile in profiles if profile.get('startup_config')]

        if running_blocks:
            merged_running = '\n'.join(block.strip('\n') for block in running_blocks)
            self._write_config_section(engine, 'RUNNINGCONFIG', merged_running)
        if startup_blocks:
            merged_startup = '\n'.join(block.strip('\n') for block in startup_blocks)
            self._write_config_section(engine, 'STARTUPCONFIG', merged_startup)

    def _write_config_section(self, engine_elem, section_name, config_text):
        section = engine_elem.find(section_name)
        if section is None:
            section = ET.SubElement(engine_elem, section_name)
        section.clear()
        for line in config_text.strip('\n').splitlines():
            line_elem = ET.SubElement(section, 'LINE')
            line_elem.text = line


VLAN_NAME_POOL = [
    'Users', 'Voice', 'Servers', 'Guests', 'IoT', 'Cameras', 'OT', 'Finance', 'Engineering', 'Students'
]


@dataclass
class ResourcePool:
    rng: random.Random
    used_networks: Set[ipaddress.IPv4Network] = field(default_factory=set)
    used_vlan_ids: Set[int] = field(default_factory=set)
    used_loopbacks: Set[str] = field(default_factory=set)
    used_fhrp_groups: Set[int] = field(default_factory=set)

    def allocate_network(self, mask=24, first_octet=10):
        return _pick_unique_network(self.rng, self.used_networks, mask=mask, first_octet=first_octet)

    def allocate_vlan_id(self, min_id=10, max_id=4094):
        while True:
            candidate = self.rng.randint(min_id, max_id)
            if candidate not in self.used_vlan_ids:
                self.used_vlan_ids.add(candidate)
                return candidate

    def allocate_loopback(self):
        while True:
            candidate = _random_loopback(self.rng)
            if candidate not in self.used_loopbacks:
                self.used_loopbacks.add(candidate)
                return candidate

    def allocate_fhrp_group(self, min_group=1, max_group=255):
        while True:
            candidate = self.rng.randint(min_group, max_group)
            if candidate not in self.used_fhrp_groups:
                self.used_fhrp_groups.add(candidate)
                return candidate


@dataclass
class ParameterContext:
    rng: random.Random
    pool: ResourcePool


@dataclass
class RandomScenarioRequest:
    count: int
    tags_any: Optional[Sequence[str]] = None
    tags_all: Optional[Sequence[str]] = None
    exclude: Optional[Sequence[str]] = None


@dataclass
class RecipePlan:
    explicit: List[str] = field(default_factory=list)
    random_requests: List[RandomScenarioRequest] = field(default_factory=list)


def _host_ip(network, host_index):
    return str(ipaddress.IPv4Address(int(network.network_address) + host_index))


def _host_ipv6(network, host_index):
    return str(ipaddress.IPv6Address(int(network.network_address) + host_index))


def _format_range(network, start, end):
    return f'{_host_ip(network, start)}-{_host_ip(network, end)}'


def _pick_unique_network(rng, used, mask=24, first_octet=10):
    while True:
        second = rng.randint(1, 254)
        third = rng.randint(0, 254)
        network = ipaddress.IPv4Network(f'{first_octet}.{second}.{third}.0/{mask}', strict=False)
        if network not in used:
            used.add(network)
            return network


def _random_loopback(rng):
    return f'172.{rng.randint(16, 31)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}'


def _generate_campus_core_params(ctx: ParameterContext):
    rng = ctx.rng
    pool = ctx.pool
    mgmt_net = pool.allocate_network()
    vlan_a_net = pool.allocate_network()
    vlan_b_net = pool.allocate_network()
    vlan_ids = sorted([pool.allocate_vlan_id(10, 190), pool.allocate_vlan_id(10, 190)])
    vlan_names = rng.sample(VLAN_NAME_POOL, 2)
    return {
        'vlan_a_id': vlan_ids[0],
        'vlan_b_id': vlan_ids[1],
        'vlan_a_name': vlan_names[0],
        'vlan_b_name': vlan_names[1],
        'vlan_a_cidr': str(vlan_a_net),
        'vlan_b_cidr': str(vlan_b_net),
        'vlan_a_gateway': _host_ip(vlan_a_net, 1),
        'vlan_b_gateway': _host_ip(vlan_b_net, 1),
        'vlan_a_scope': _format_range(vlan_a_net, 50, 200),
        'vlan_b_scope': _format_range(vlan_b_net, 50, 200),
        'vlan_a_reserved': _format_range(vlan_a_net, 1, 20),
        'vlan_b_reserved': _format_range(vlan_b_net, 1, 20),
        'mgmt_cidr': str(mgmt_net),
        'core_mgmt_ip': _host_ip(mgmt_net, 1),
        'edge_mgmt_ip': _host_ip(mgmt_net, 2),
        'core_b_mgmt_ip': _host_ip(mgmt_net, 3),
        'edge_b_mgmt_ip': _host_ip(mgmt_net, 4),
        'router_mgmt_ip': _host_ip(mgmt_net, 254),
        'fhrp_group_a': pool.allocate_fhrp_group(),
        'fhrp_group_b': pool.allocate_fhrp_group(),
        'loopback_ip': pool.allocate_loopback(),
    }


def _generate_branch_params(ctx: ParameterContext):
    pool = ctx.pool
    rng = ctx.rng
    branch_net = pool.allocate_network(first_octet=10)
    vlan_id = pool.allocate_vlan_id(30, 300)
    name = rng.choice([n for n in VLAN_NAME_POOL if n != 'Voice'])
    return {
        'branch_vlan_id': vlan_id,
        'branch_vlan_name': name,
        'branch_vlan_cidr': str(branch_net),
        'branch_gateway': _host_ip(branch_net, 1),
        'branch_scope': _format_range(branch_net, 50, 220),
        'branch_reserved': _format_range(branch_net, 2, 25),
        'branch_router_ip': _host_ip(branch_net, 254),
        'branch_switch_ip': _host_ip(branch_net, 2),
        'branch_loopback_ip': pool.allocate_loopback(),
    }


def params_redundant_access(ctx: ParameterContext):
    return _generate_campus_core_params(ctx)


def params_dual_core(ctx: ParameterContext):
    return _generate_campus_core_params(ctx)


def params_campus_branch(ctx: ParameterContext):
    campus_params = _generate_campus_core_params(ctx)
    branch_params = _generate_branch_params(ctx)
    wan_net = ctx.pool.allocate_network(mask=30)
    campus_params.update(branch_params)
    campus_params.update({
        'wan_cidr': str(wan_net),
        'campus_wan_ip': _host_ip(wan_net, 1),
        'branch_wan_ip': _host_ip(wan_net, 2),
    })
    return campus_params


def params_branch_single(ctx: ParameterContext):
    return _generate_branch_params(ctx)


def params_ospf(ctx: ParameterContext):
    pool = ctx.pool
    net_a = pool.allocate_network(mask=29, first_octet=192)
    net_b = pool.allocate_network(mask=30, first_octet=192)
    return {
        'ospf_lan_net': str(net_a),
        'ospf_p2p_net': str(net_b),
        'ospf_r1_lan_ip': _host_ip(net_a, 1),
        'ospf_r2_lan_ip': _host_ip(net_a, 2),
        'test_host_a_ip': _host_ip(net_a, 10),
        'test_host_b_ip': _host_ip(net_a, 11),
        'ospf_r1_p2p_ip': _host_ip(net_b, 1),
        'ospf_r2_p2p_ip': _host_ip(net_b, 2),
        'ospf_loopback_ip': pool.allocate_loopback(),
        'ospf_process_id': ctx.rng.randint(1, 200),
    }


def params_nat(ctx: ParameterContext):
    pool = ctx.pool
    inside_net = pool.allocate_network(mask=24, first_octet=10)
    outside_net = pool.allocate_network(mask=30, first_octet=198)
    public_pool = pool.allocate_network(mask=29, first_octet=203)
    return {
        'nat_inside_cidr': str(inside_net),
        'nat_inside_gw': _host_ip(inside_net, 1),
        'nat_inside_scope': _format_range(inside_net, 50, 200),
        'nat_outside_cidr': str(outside_net),
        'nat_inside_wan_ip': _host_ip(outside_net, 1),
        'nat_outside_wan_ip': _host_ip(outside_net, 2),
        'nat_public_pool': str(public_pool),
        'nat_public_start': _host_ip(public_pool, 1),
        'nat_public_end': _host_ip(public_pool, 6),
    }


def params_services_mgmt(ctx: ParameterContext):
    pool = ctx.pool
    mgmt_net = pool.allocate_network(mask=24, first_octet=10)
    return {
        'mgmt_cidr': str(mgmt_net),
        'router_mgmt_ip': _host_ip(mgmt_net, 1),
        'server_ip': _host_ip(mgmt_net, 10),
        'client_ip': _host_ip(mgmt_net, 50),
    }


def params_acl(ctx: ParameterContext):
    pool = ctx.pool
    client_net = pool.allocate_network(mask=24, first_octet=10)
    server_net = pool.allocate_network(mask=24, first_octet=10)
    return {
        'client_cidr': str(client_net),
        'server_cidr': str(server_net),
        'router_client_ip': _host_ip(client_net, 1),
        'router_server_ip': _host_ip(server_net, 1),
        'client_ip': _host_ip(client_net, 50),
        'admin_ip': _host_ip(client_net, 60),
        'server_ip': _host_ip(server_net, 10),
    }


def params_ipv6(ctx: ParameterContext):
    rng = ctx.rng
    prefix = f"2001:db8:{rng.randint(1, 0xffff):x}:{rng.randint(0, 0xffff):x}::/64"
    network = ipaddress.IPv6Network(prefix, strict=False)
    return {
        'ipv6_prefix': str(network),
        'router_ipv6': _host_ipv6(network, 1),
        'server_ipv6': _host_ipv6(network, 10),
        'client_ipv6': _host_ipv6(network, 50),
    }


def params_static_routing(ctx: ParameterContext):
    pool = ctx.pool
    lan_a = pool.allocate_network(mask=24, first_octet=10)
    lan_b = pool.allocate_network(mask=24, first_octet=10)
    wan = pool.allocate_network(mask=30, first_octet=198)
    return {
        'lan_a_cidr': str(lan_a),
        'lan_b_cidr': str(lan_b),
        'lan_a_gateway': _host_ip(lan_a, 1),
        'lan_b_gateway': _host_ip(lan_b, 1),
        'lan_a_host': _host_ip(lan_a, 50),
        'lan_b_host': _host_ip(lan_b, 50),
        'wan_cidr': str(wan),
        'wan_a_ip': _host_ip(wan, 1),
        'wan_b_ip': _host_ip(wan, 2),
    }


def params_etherchannel(ctx: ParameterContext):
    pool = ctx.pool
    mgmt_net = pool.allocate_network(mask=24, first_octet=10)
    return {
        'mgmt_cidr': str(mgmt_net),
        'switch_a_ip': _host_ip(mgmt_net, 2),
        'switch_b_ip': _host_ip(mgmt_net, 3),
        'host_a_ip': _host_ip(mgmt_net, 50),
        'host_b_ip': _host_ip(mgmt_net, 60),
        'portchannel_id': ctx.rng.randint(1, 8),
    }


class _FormatDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def _format_template(template, params):
    if not template:
        return ''
    safe_params = _FormatDict({k: str(v) for k, v in params.items()})
    return template.format_map(safe_params)


def _sample_objectives(meta, params, rng):
    objectives = list(meta.get('objectives') or [])
    if not meta.get('preformatted_objectives'):
        objectives = [_format_template(obj, params) for obj in objectives]
    if len(objectives) <= 2:
        return objectives
    sample_min = meta.get('objective_sample_min', 2)
    sample_max = meta.get('objective_sample_max', len(objectives))
    sample_max = max(sample_min, min(sample_max, len(objectives)))
    sample_min = max(1, min(sample_min, sample_max))
    count = rng.randint(sample_min, sample_max)
    return rng.sample(objectives, count)


def render_note_text(instances, rng=None):
    if not instances:
        return ''

    rng = rng or random.Random()

    def append_wrapped(buf, text, initial='', subsequent=None, width=90):
        if not text:
            return
        init = initial or ''
        sub = subsequent if subsequent is not None else init
        filled = textwrap.fill(text, width=width, initial_indent=init, subsequent_indent=sub)
        buf.extend(filled.splitlines())

    lines = ['Lab Objectives']
    for idx, ctx in enumerate(instances, start=1):
        meta = ctx['meta']
        params = ctx['params']
        title = _format_template(meta.get('title') or ctx['name'], params)
        append_wrapped(lines, f'{idx}. {title}', subsequent='   ')
        for objective in _sample_objectives(meta, params, rng):
            append_wrapped(lines, objective, initial='  - ', subsequent='    ')
        if meta.get('instructions'):
            if meta.get('preformatted_instructions'):
                instructions = meta.get('instructions') or ''
            else:
                instructions = _format_template(meta['instructions'], params)
            append_wrapped(lines, 'Notes: ' + instructions, subsequent='       ')
        lines.append('')
    return '\n'.join(line for line in lines if line).strip()


def _add_positioned_device(lab, base_label, device_type, position, profile=None):
    name = lab.unique_name(base_label)
    lab.add_device(name, device_type, position=position, profile=profile)
    return name


def _attach_host(lab, rng, parent_switch, parent_port, label, position=None, device_type='pc'):
    host = lab.unique_name(label)
    lab.add_device(host, device_type, position=position)
    lab.add_link(host, 'FastEthernet0', parent_switch, parent_port, length=str(rng.randint(5, 8)))
    return host


def _ctx_rng(ctx):
    return ctx.rng if ctx else random.Random()


def _simple_access_lab(lab, params, rng, router_label='EdgeRouter', switch_label='AccessSwitch', host_labels=None,
                       server_label=None):
    if host_labels is None:
        host_labels = ['UserPC', 'AdminPC']

    router_x = 420
    router = _add_positioned_device(lab, router_label, 'router', (router_x, 80))
    access_switch = _add_positioned_device(lab, switch_label, 'switch', (router_x, 220))

    lab.add_link(router, 'GigabitEthernet0/0/0', access_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))

    host_positions = [(router_x - 120, 520), (router_x, 520), (router_x + 120, 520)]
    rng.shuffle(host_positions)
    for idx, label in enumerate(host_labels):
        position = host_positions[idx % len(host_positions)]
        _attach_host(lab, rng, access_switch, f'GigabitEthernet1/0/{5 + idx}', label, position=position)

    if server_label:
        _attach_host(lab, rng, access_switch, 'GigabitEthernet1/0/9', server_label, position=(router_x + 140, 380), device_type='server')


def _acl_filtering_lab(lab, params, rng):
    router_x = 420
    router = _add_positioned_device(lab, 'AccessRouter', 'router', (router_x, 80))
    client_switch = _add_positioned_device(lab, 'ClientSwitch', 'switch', (router_x - 160, 220))
    server_switch = _add_positioned_device(lab, 'ServerSwitch', 'switch', (router_x + 160, 220))

    lab.add_link(router, 'GigabitEthernet0/0/0', client_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))
    lab.add_link(router, 'GigabitEthernet0/0/1', server_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))

    _attach_host(lab, rng, client_switch, 'GigabitEthernet1/0/5', 'ClientPC', position=(router_x - 220, 520))
    _attach_host(lab, rng, client_switch, 'GigabitEthernet1/0/6', 'AdminPC', position=(router_x - 100, 520))
    _attach_host(lab, rng, server_switch, 'GigabitEthernet1/0/5', 'AppServer', position=(router_x + 160, 380), device_type='server')


def _nat_edge_lab(lab, params, rng):
    campus_router = _add_positioned_device(lab, 'EdgeRouter', 'router', (180, 80))
    isp_router = _add_positioned_device(lab, 'ISPRouter', 'router', (520, 80))
    access_switch = _add_positioned_device(lab, 'InsideSwitch', 'switch', (320, 220))
    outside_server = lab.unique_name('OutsideServer')

    lab.add_site_label('Inside LAN', (160, 20))
    lab.add_site_label('ISP Edge', (520, 20))

    lab.add_link(campus_router, 'GigabitEthernet0/0/1', isp_router, 'GigabitEthernet0/0/1', length=str(rng.randint(6, 8)))
    lab.add_link(campus_router, 'GigabitEthernet0/0/0', access_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))

    inside_positions = [(280, 520), (360, 520)]
    rng.shuffle(inside_positions)
    _attach_host(lab, rng, access_switch, 'GigabitEthernet1/0/5', 'InsideHostA', position=inside_positions[0])
    _attach_host(lab, rng, access_switch, 'GigabitEthernet1/0/6', 'InsideHostB', position=inside_positions[1])
    _attach_host(lab, rng, access_switch, 'GigabitEthernet1/0/7', 'DMZServer', position=(440, 380), device_type='server')
    lab.add_device(outside_server, 'server', position=(620, 380))
    lab.add_link(outside_server, 'FastEthernet0', isp_router, 'GigabitEthernet0/0/0', length=str(rng.randint(5, 7)))


def _redundant_variant_single_edge(lab, params, rng):
    services_router = _add_positioned_device(lab, 'ServicesRouter', 'router', (180, 80), profile='campus_router_vlan10_20_dhcp')
    core_switch = _add_positioned_device(lab, 'CoreSwitch', 'switch', (360, 220), profile='mls_vlan10_20_gateway')
    edge_switch = _add_positioned_device(lab, 'EdgeSwitch', 'switch', (540, 320), profile='edge_access_vlan10_20')

    lab.add_link(services_router, 'GigabitEthernet0/0/0', core_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(3, 5)))
    lab.add_link(edge_switch, 'GigabitEthernet1/0/3', core_switch, 'GigabitEthernet1/0/1', length=str(rng.randint(3, 5)))
    lab.add_link(edge_switch, 'GigabitEthernet1/0/4', core_switch, 'GigabitEthernet1/0/2', length=str(rng.randint(3, 5)))

    _attach_host(lab, rng, edge_switch, 'GigabitEthernet1/0/1', 'UserPC', position=(560, 520))
    _attach_host(lab, rng, edge_switch, 'GigabitEthernet1/0/2', 'DMZServer', position=(640, 380), device_type='server')
    if rng.random() < 0.65:
        _attach_host(lab, rng, edge_switch, 'GigabitEthernet1/0/7', 'GuestLaptop', position=(480, 520))


def _redundant_variant_dual_edge_mesh(lab, params, rng):
    services_router = _add_positioned_device(lab, 'ServicesRouter', 'router', (160, 80), profile='campus_router_vlan10_20_dhcp')
    core_a = _add_positioned_device(lab, 'CoreSwitchA', 'switch', (340, 220), profile='mls_vlan10_20_gateway')
    core_b = _add_positioned_device(lab, 'CoreSwitchB', 'switch', (520, 220), profile='mls_vlan10_20_gateway')
    edge_a = _add_positioned_device(lab, 'EdgeSwitchA', 'switch', (320, 320), profile='edge_access_vlan10_20')
    edge_b = _add_positioned_device(lab, 'EdgeSwitchB', 'switch', (540, 320), profile='edge_access_vlan10_20')

    lab.add_link(services_router, 'GigabitEthernet0/0/0', core_a, 'GigabitEthernet1/0/24', length=str(rng.randint(3, 5)))
    lab.add_link(services_router, 'GigabitEthernet0/0/1', core_b, 'GigabitEthernet1/0/24', length=str(rng.randint(3, 5)))
    lab.add_link(core_a, 'GigabitEthernet1/0/1', core_b, 'GigabitEthernet1/0/1', length='2')
    lab.add_link(core_a, 'GigabitEthernet1/0/2', core_b, 'GigabitEthernet1/0/2', length='2')

    for edge_switch, ports in [
        (edge_a, ('GigabitEthernet1/0/5', 'GigabitEthernet1/0/7')),
        (edge_b, ('GigabitEthernet1/0/6', 'GigabitEthernet1/0/8')),
    ]:
        lab.add_link(edge_switch, 'GigabitEthernet1/0/3', core_a, ports[0], length=str(rng.randint(3, 4)))
        lab.add_link(edge_switch, 'GigabitEthernet1/0/4', core_b, ports[1], length=str(rng.randint(3, 4)))

    _attach_host(lab, rng, edge_a, 'GigabitEthernet1/0/1', 'SalesPC', position=(300, 520))
    _attach_host(lab, rng, edge_a, 'GigabitEthernet1/0/2', 'VoicePhone', position=(360, 520))
    _attach_host(lab, rng, edge_b, 'GigabitEthernet1/0/1', 'FinancePC', position=(520, 520))
    if rng.random() < 0.5:
        _attach_host(lab, rng, edge_b, 'GigabitEthernet1/0/2', 'LabPrinter', position=(580, 520))


def _redundant_variant_collapsed_distribution(lab, params, rng):
    services_router = _add_positioned_device(lab, 'ServicesRouter', 'router', (120, 80), profile='campus_router_vlan10_20_dhcp')
    distribution = _add_positioned_device(lab, 'DistributionSwitch', 'switch', (300, 220), profile='mls_vlan10_20_gateway')
    core_switch = _add_positioned_device(lab, 'CoreSwitch', 'switch', (480, 220), profile='mls_vlan10_20_gateway')
    edge_switch = _add_positioned_device(lab, 'EdgeSwitch', 'switch', (420, 330), profile='edge_access_vlan10_20')

    lab.add_link(services_router, 'GigabitEthernet0/0/0', distribution, 'GigabitEthernet1/0/24', length=str(rng.randint(3, 5)))
    lab.add_link(distribution, 'GigabitEthernet1/0/3', core_switch, 'GigabitEthernet1/0/1', length=str(rng.randint(3, 5)))
    lab.add_link(distribution, 'GigabitEthernet1/0/4', core_switch, 'GigabitEthernet1/0/2', length=str(rng.randint(3, 5)))
    lab.add_link(edge_switch, 'GigabitEthernet1/0/3', distribution, 'GigabitEthernet1/0/1', length=str(rng.randint(4, 6)))
    lab.add_link(edge_switch, 'GigabitEthernet1/0/4', distribution, 'GigabitEthernet1/0/2', length=str(rng.randint(4, 6)))

    _attach_host(lab, rng, edge_switch, 'GigabitEthernet1/0/1', 'EngineeringPC', position=(420, 520))
    _attach_host(lab, rng, edge_switch, 'GigabitEthernet1/0/2', 'IoTGateway', position=(500, 520))
    if rng.random() < 0.5:
        _attach_host(lab, rng, distribution, 'GigabitEthernet1/0/10', 'SecurityCamera', position=(280, 520))


_REDUNDANT_ACCESS_VARIANTS = [
    ('Single Edge Uplinks', _redundant_variant_single_edge),
    ('Dual Edge Mesh', _redundant_variant_dual_edge_mesh),
    ('Collapsed Distribution', _redundant_variant_collapsed_distribution),
]


def scenario_redundant_access(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice(_REDUNDANT_ACCESS_VARIANTS)
    params['topology_variant'] = variant_label
    builder(lab, params, rng)


def _branch_variant_compact(lab, params, rng):
    branch_router = _add_positioned_device(lab, 'BranchRouter', 'router', (220, 80), profile='branch_router_dhcp_single_vlan')
    access_switch = _add_positioned_device(lab, 'BranchAccessSwitch', 'switch', (420, 220), profile='edge_access_vlan10_20')
    branch_pc = lab.unique_name('BranchPC')
    branch_aux = lab.unique_name('BranchPrinter' if rng.random() < 0.5 else 'BranchPhone')

    lab.add_device(branch_pc, 'pc', position=(400, 520))
    lab.add_device(branch_aux, 'pc', position=(480, 520))

    lab.add_link(branch_router, 'GigabitEthernet0/0/0', access_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))
    lab.add_link(branch_pc, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/5', length=str(rng.randint(5, 7)))
    lab.add_link(branch_aux, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/6', length=str(rng.randint(5, 7)))

    if rng.random() < 0.45:
        branch_server = lab.unique_name('BranchServer')
        lab.add_device(branch_server, 'server', position=(560, 380))
        lab.add_link(branch_server, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/11', length=str(rng.randint(5, 8)))


def _branch_variant_layered(lab, params, rng):
    branch_router = _add_positioned_device(lab, 'BranchRouter', 'router', (140, 80), profile='branch_router_dhcp_single_vlan')
    distro_switch = _add_positioned_device(lab, 'BranchDistribution', 'switch', (320, 220), profile='mls_vlan10_20_gateway')
    access_switch = _add_positioned_device(lab, 'BranchAccessSwitch', 'switch', (520, 320), profile='edge_access_vlan10_20')
    branch_pc = lab.unique_name('FinancePC')
    voice_phone = lab.unique_name('VoicePhone')
    branch_server = lab.unique_name('BranchServer')

    lab.add_device(branch_pc, 'pc', position=(500, 520))
    lab.add_device(voice_phone, 'pc', position=(580, 520))
    lab.add_device(branch_server, 'server', position=(300, 380))

    lab.add_link(branch_router, 'GigabitEthernet0/0/0', distro_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(3, 5)))
    lab.add_link(distro_switch, 'GigabitEthernet1/0/3', access_switch, 'GigabitEthernet1/0/23', length=str(rng.randint(4, 5)))
    lab.add_link(distro_switch, 'GigabitEthernet1/0/4', access_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 5)))

    lab.add_link(branch_pc, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/5', length=str(rng.randint(5, 7)))
    lab.add_link(voice_phone, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/6', length=str(rng.randint(5, 7)))
    lab.add_link(branch_server, 'FastEthernet0', distro_switch, 'GigabitEthernet1/0/10', length=str(rng.randint(4, 6)))


def _branch_variant_dual_access(lab, params, rng):
    branch_router = _add_positioned_device(lab, 'BranchRouter', 'router', (220, 80), profile='branch_router_dhcp_single_vlan')
    access_a = _add_positioned_device(lab, 'AccessSwitchA', 'switch', (380, 220), profile='edge_access_vlan10_20')
    access_b = _add_positioned_device(lab, 'AccessSwitchB', 'switch', (560, 220), profile='edge_access_vlan10_20')
    wireless_ap = lab.unique_name('BranchAP')
    security_cam = lab.unique_name('SecurityCam')

    lab.add_device(wireless_ap, 'pc', position=(360, 520))
    lab.add_device(security_cam, 'pc', position=(600, 520))

    lab.add_link(branch_router, 'GigabitEthernet0/0/0', access_a, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))
    lab.add_link(branch_router, 'GigabitEthernet0/0/1', access_b, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))
    lab.add_link(access_a, 'GigabitEthernet1/0/3', access_b, 'GigabitEthernet1/0/3', length='3')

    _attach_host(lab, rng, access_a, 'GigabitEthernet1/0/5', 'BranchPC', position=(440, 520))
    lab.add_link(wireless_ap, 'FastEthernet0', access_a, 'GigabitEthernet1/0/6', length=str(rng.randint(5, 7)))
    lab.add_link(security_cam, 'FastEthernet0', access_b, 'GigabitEthernet1/0/8', length=str(rng.randint(5, 7)))


_BRANCH_VARIANTS = [
    ('Compact Pod', _branch_variant_compact),
    ('Layered Distribution', _branch_variant_layered),
    ('Dual Access Rings', _branch_variant_dual_access),
]


def scenario_branch_single_vlan(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice(_BRANCH_VARIANTS)
    params['branch_variant'] = variant_label
    builder(lab, params, rng)


def _ospf_variant_direct_hosts(lab, params, rng):
    router_a = _add_positioned_device(lab, 'OSPFRouterA', 'router', (260, 80))
    router_b = _add_positioned_device(lab, 'OSPFRouterB', 'router', (520, 80))
    lan_switch = _add_positioned_device(lab, 'OSPFSharedSwitch', 'switch', (380, 220), profile='edge_access_vlan10_20')
    test_host_a = lab.unique_name('TestHostA')
    test_host_b = lab.unique_name('TestHostB')

    lab.add_device(test_host_a, 'pc', position=(320, 520))
    lab.add_device(test_host_b, 'pc', position=(460, 520))

    lab.add_link(router_a, 'GigabitEthernet0/0/0', lan_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))
    lab.add_link(router_b, 'GigabitEthernet0/0/0', lan_switch, 'GigabitEthernet1/0/23', length=str(rng.randint(4, 6)))
    lab.add_link(test_host_a, 'FastEthernet0', lan_switch, 'GigabitEthernet1/0/5', length=str(rng.randint(5, 7)))
    lab.add_link(test_host_b, 'FastEthernet0', lan_switch, 'GigabitEthernet1/0/6', length=str(rng.randint(5, 7)))

    lab.add_link(router_a, 'GigabitEthernet0/0/1', router_b, 'GigabitEthernet0/0/1', length=str(rng.randint(5, 7)))


def _ospf_variant_access_switch(lab, params, rng):
    router_a = _add_positioned_device(lab, 'OSPFRouterA', 'router', (200, 80))
    router_b = _add_positioned_device(lab, 'OSPFRouterB', 'router', (560, 80))
    access_switch = _add_positioned_device(lab, 'OSPFEdgeSwitch', 'switch', (380, 220), profile='edge_access_vlan10_20')
    test_host_a = lab.unique_name('TestHostA')
    test_host_b = lab.unique_name('TestHostB')
    monitoring = lab.unique_name('MonitoringPC')

    lab.add_device(test_host_a, 'pc', position=(320, 520))
    lab.add_device(test_host_b, 'pc', position=(440, 520))
    lab.add_device(monitoring, 'pc', position=(560, 520))

    lab.add_link(router_a, 'GigabitEthernet0/0/0', access_switch, 'GigabitEthernet1/0/24', length=str(rng.randint(4, 6)))
    lab.add_link(router_b, 'GigabitEthernet0/0/0', access_switch, 'GigabitEthernet1/0/23', length=str(rng.randint(4, 6)))
    lab.add_link(test_host_a, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/5', length=str(rng.randint(5, 7)))
    lab.add_link(test_host_b, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/6', length=str(rng.randint(5, 7)))
    lab.add_link(monitoring, 'FastEthernet0', access_switch, 'GigabitEthernet1/0/7', length=str(rng.randint(5, 7)))

    lab.add_link(router_a, 'GigabitEthernet0/0/1', router_b, 'GigabitEthernet0/0/1', length=str(rng.randint(5, 7)))


_OSPF_VARIANTS = [
    ('Dual Router Shared LAN', _ospf_variant_direct_hosts),
    ('Dual Router Access Fanout', _ospf_variant_access_switch),
]


def scenario_ospf_validation(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice(_OSPF_VARIANTS)
    params['ospf_variant'] = variant_label
    builder(lab, params, rng)


def _dual_core_variant_mesh(lab, params, rng):
    services_router = _add_positioned_device(lab, 'CampusServices', 'router', (140, 80), profile='campus_router_vlan10_20_dhcp')
    core_a = _add_positioned_device(lab, 'CoreA', 'switch', (320, 220), profile='mls_vlan10_20_gateway')
    core_b = _add_positioned_device(lab, 'CoreB', 'switch', (520, 220), profile='mls_vlan10_20_gateway')
    edge_a = _add_positioned_device(lab, 'EdgeA', 'switch', (300, 320), profile='edge_access_vlan10_20')
    edge_b = _add_positioned_device(lab, 'EdgeB', 'switch', (520, 320), profile='edge_access_vlan10_20')
    server = lab.unique_name('SharedServer')
    voice_phone = lab.unique_name('VoicePhone')
    guest_pc = lab.unique_name('GuestPC')

    lab.add_device(server, 'server', position=(260, 380))
    lab.add_device(voice_phone, 'pc', position=(340, 520))
    lab.add_device(guest_pc, 'pc', position=(520, 520))

    lab.add_link(services_router, 'GigabitEthernet0/0/0', core_a, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(services_router, 'GigabitEthernet0/0/1', core_b, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(core_a, 'GigabitEthernet1/0/1', core_b, 'GigabitEthernet1/0/1', length='2')
    lab.add_link(core_a, 'GigabitEthernet1/0/2', core_b, 'GigabitEthernet1/0/2', length='2')
    lab.add_link(edge_a, 'GigabitEthernet1/0/3', core_a, 'GigabitEthernet1/0/5', length='3')
    lab.add_link(edge_a, 'GigabitEthernet1/0/4', core_b, 'GigabitEthernet1/0/5', length='3')
    lab.add_link(edge_b, 'GigabitEthernet1/0/3', core_a, 'GigabitEthernet1/0/6', length='3')
    lab.add_link(edge_b, 'GigabitEthernet1/0/4', core_b, 'GigabitEthernet1/0/6', length='3')
    lab.add_link(server, 'FastEthernet0', core_a, 'GigabitEthernet1/0/10', length='6')
    lab.add_link(voice_phone, 'FastEthernet0', edge_a, 'GigabitEthernet1/0/1', length='6')
    lab.add_link(guest_pc, 'FastEthernet0', edge_b, 'GigabitEthernet1/0/2', length='6')


def _dual_core_variant_collapsed(lab, params, rng):
    services_router = _add_positioned_device(lab, 'CampusServices', 'router', (160, 80), profile='campus_router_vlan10_20_dhcp')
    core = _add_positioned_device(lab, 'CollapsedCore', 'switch', (340, 220), profile='mls_vlan10_20_gateway')
    edge_stack = _add_positioned_device(lab, 'EdgeStack', 'switch', (520, 220), profile='mls_vlan10_20_gateway')
    access_a = _add_positioned_device(lab, 'AccessA', 'switch', (420, 320), profile='edge_access_vlan10_20')
    access_b = _add_positioned_device(lab, 'AccessB', 'switch', (580, 320), profile='edge_access_vlan10_20')
    lab_printer = lab.unique_name('LabPrinter')
    guest_pc = lab.unique_name('GuestPC')

    lab.add_device(lab_printer, 'pc', position=(420, 520))
    lab.add_device(guest_pc, 'pc', position=(580, 520))

    lab.add_link(services_router, 'GigabitEthernet0/0/0', core, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(core, 'GigabitEthernet1/0/1', edge_stack, 'GigabitEthernet1/0/1', length='2')
    lab.add_link(core, 'GigabitEthernet1/0/2', edge_stack, 'GigabitEthernet1/0/2', length='2')
    lab.add_link(edge_stack, 'GigabitEthernet1/0/3', access_a, 'GigabitEthernet1/0/24', length='3')
    lab.add_link(edge_stack, 'GigabitEthernet1/0/4', access_b, 'GigabitEthernet1/0/24', length='3')
    lab.add_link(access_a, 'GigabitEthernet1/0/1', access_b, 'GigabitEthernet1/0/1', length='3')
    lab.add_link(lab_printer, 'FastEthernet0', access_a, 'GigabitEthernet1/0/2', length='5')
    lab.add_link(guest_pc, 'FastEthernet0', access_b, 'GigabitEthernet1/0/2', length='5')


def _dual_core_variant_dmz_ring(lab, params, rng):
    services_router = _add_positioned_device(lab, 'CampusServices', 'router', (140, 80), profile='campus_router_vlan10_20_dhcp')
    core_a = _add_positioned_device(lab, 'CoreA', 'switch', (320, 220), profile='mls_vlan10_20_gateway')
    core_b = _add_positioned_device(lab, 'CoreB', 'switch', (520, 220), profile='mls_vlan10_20_gateway')
    dmz_switch = _add_positioned_device(lab, 'DMZSwitch', 'switch', (360, 320), profile='edge_access_vlan10_20')
    edge = _add_positioned_device(lab, 'EdgeAccess', 'switch', (520, 320), profile='edge_access_vlan10_20')
    dmz_server = lab.unique_name('DMZServer')
    research_pc = lab.unique_name('ResearchPC')

    lab.add_device(dmz_server, 'server', position=(320, 380))
    lab.add_device(research_pc, 'pc', position=(520, 520))

    lab.add_link(services_router, 'GigabitEthernet0/0/0', core_a, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(services_router, 'GigabitEthernet0/0/1', core_b, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(core_a, 'GigabitEthernet1/0/3', dmz_switch, 'GigabitEthernet1/0/24', length='3')
    lab.add_link(core_b, 'GigabitEthernet1/0/3', dmz_switch, 'GigabitEthernet1/0/23', length='3')
    lab.add_link(dmz_switch, 'GigabitEthernet1/0/5', edge, 'GigabitEthernet1/0/5', length='3')
    lab.add_link(dmz_switch, 'GigabitEthernet1/0/6', edge, 'GigabitEthernet1/0/6', length='3')
    lab.add_link(dmz_server, 'FastEthernet0', dmz_switch, 'GigabitEthernet1/0/2', length='5')
    lab.add_link(research_pc, 'FastEthernet0', edge, 'GigabitEthernet1/0/2', length='5')


_DUAL_CORE_VARIANTS = [
    ('Full Mesh Cores', _dual_core_variant_mesh),
    ('Collapsed Core Stack', _dual_core_variant_collapsed),
    ('DMZ Ring', _dual_core_variant_dmz_ring),
]


def scenario_dual_core_distribution(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice(_DUAL_CORE_VARIANTS)
    params['dual_core_variant'] = variant_label
    builder(lab, params, rng)


def _campus_branch_variant_direct(lab, params, rng):
    campus_router = _add_positioned_device(lab, 'CampusRouter', 'router', (180, 80), profile='campus_router_vlan10_20_dhcp')
    branch_router = _add_positioned_device(lab, 'BranchEdgeRouter', 'router', (520, 80), profile='branch_router_dhcp_single_vlan')
    campus_core = _add_positioned_device(lab, 'CampusCore', 'switch', (320, 220), profile='mls_vlan10_20_gateway')
    branch_switch = _add_positioned_device(lab, 'BranchAccessSwitch', 'switch', (520, 320), profile='edge_access_vlan10_20')
    campus_host = lab.unique_name('CampusHost')
    branch_host = lab.unique_name('BranchHost')

    lab.add_site_label('Campus', (180, 20))
    lab.add_site_label('Branch', (520, 20))

    lab.add_device(campus_host, 'pc', position=(300, 520))
    lab.add_device(branch_host, 'pc', position=(520, 520))

    lab.add_link(campus_router, 'GigabitEthernet0/0/0', campus_core, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(branch_router, 'GigabitEthernet0/0/0', branch_switch, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(campus_router, 'GigabitEthernet0/0/1', branch_router, 'GigabitEthernet0/0/1', length='8')
    lab.add_link(campus_host, 'FastEthernet0', campus_core, 'GigabitEthernet1/0/5', length='6')
    lab.add_link(branch_host, 'FastEthernet0', branch_switch, 'GigabitEthernet1/0/5', length='6')


def _campus_branch_variant_wan_access(lab, params, rng):
    campus_router = _add_positioned_device(lab, 'CampusRouter', 'router', (160, 80), profile='campus_router_vlan10_20_dhcp')
    branch_router = _add_positioned_device(lab, 'BranchEdgeRouter', 'router', (540, 80), profile='branch_router_dhcp_single_vlan')
    wan_switch = _add_positioned_device(lab, 'WANSwitch', 'switch', (360, 220), profile='edge_access_vlan10_20')
    campus_core = _add_positioned_device(lab, 'CampusCore', 'switch', (220, 220), profile='mls_vlan10_20_gateway')
    branch_switch = _add_positioned_device(lab, 'BranchAccessSwitch', 'switch', (560, 320), profile='edge_access_vlan10_20')
    telemetry = lab.unique_name('TelemetryPC')
    branch_host = lab.unique_name('BranchHost')

    lab.add_site_label('Campus', (200, 20))
    lab.add_site_label('WAN', (360, 120))
    lab.add_site_label('Branch', (560, 20))

    lab.add_device(telemetry, 'pc', position=(360, 520))
    lab.add_device(branch_host, 'pc', position=(560, 520))

    lab.add_link(campus_router, 'GigabitEthernet0/0/0', campus_core, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(campus_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/24', length='5')
    lab.add_link(branch_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/23', length='5')
    lab.add_link(branch_router, 'GigabitEthernet0/0/0', branch_switch, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(telemetry, 'FastEthernet0', wan_switch, 'GigabitEthernet1/0/5', length='6')
    lab.add_link(branch_host, 'FastEthernet0', branch_switch, 'GigabitEthernet1/0/5', length='6')


def _campus_branch_variant_dual_branch(lab, params, rng):
    campus_router = _add_positioned_device(lab, 'CampusRouter', 'router', (180, 80), profile='campus_router_vlan10_20_dhcp')
    branch_router_a = _add_positioned_device(lab, 'BranchRouterA', 'router', (520, 80), profile='branch_router_dhcp_single_vlan')
    branch_router_b = _add_positioned_device(lab, 'BranchRouterB', 'router', (640, 80), profile='branch_router_dhcp_single_vlan')
    campus_core = _add_positioned_device(lab, 'CampusCore', 'switch', (300, 220), profile='mls_vlan10_20_gateway')
    wan_switch = _add_positioned_device(lab, 'CampusWANSwitch', 'switch', (420, 220), profile='edge_access_vlan10_20')
    branch_switch_a = _add_positioned_device(lab, 'BranchSwitchA', 'switch', (520, 320), profile='edge_access_vlan10_20')
    branch_switch_b = _add_positioned_device(lab, 'BranchSwitchB', 'switch', (660, 320), profile='edge_access_vlan10_20')
    campus_host = lab.unique_name('CampusHost')
    branch_host_a = lab.unique_name('BranchHostA')
    branch_host_b = lab.unique_name('BranchHostB')

    lab.add_site_label('Campus', (200, 20))
    lab.add_site_label('Branch A', (520, 20))
    lab.add_site_label('Branch B', (660, 100))

    lab.add_device(campus_host, 'pc', position=(300, 520))
    lab.add_device(branch_host_a, 'pc', position=(520, 520))
    lab.add_device(branch_host_b, 'pc', position=(660, 520))

    lab.add_link(campus_router, 'GigabitEthernet0/0/0', campus_core, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(branch_router_a, 'GigabitEthernet0/0/0', branch_switch_a, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(branch_router_b, 'GigabitEthernet0/0/0', branch_switch_b, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(campus_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/24', length='6')
    lab.add_link(branch_router_a, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/23', length='6')
    lab.add_link(branch_router_b, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/22', length='6')
    lab.add_link(campus_host, 'FastEthernet0', campus_core, 'GigabitEthernet1/0/5', length='6')
    lab.add_link(branch_host_a, 'FastEthernet0', branch_switch_a, 'GigabitEthernet1/0/5', length='6')
    lab.add_link(branch_host_b, 'FastEthernet0', branch_switch_b, 'GigabitEthernet1/0/5', length='6')


_CAMPUS_BRANCH_VARIANTS = [
    ('Direct WAN Link', _campus_branch_variant_direct),
    ('WAN Access Switch', _campus_branch_variant_wan_access),
    ('Dual Branch Sites', _campus_branch_variant_dual_branch),
]


def scenario_campus_branch_wan(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice(_CAMPUS_BRANCH_VARIANTS)
    params['campus_branch_variant'] = variant_label
    builder(lab, params, rng)


def scenario_nat_static_dynamic(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _nat_edge_lab(lab, params, rng)


def scenario_nat_pat(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _nat_edge_lab(lab, params, rng)


def scenario_ntp_syslog(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _simple_access_lab(lab, params, rng, router_label='MgmtRouter', switch_label='MgmtSwitch',
                       host_labels=['SyslogClient', 'AdminPC'], server_label='NTP-Syslog-Server')


def scenario_snmp_monitoring(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _simple_access_lab(lab, params, rng, router_label='SNMPRouter', switch_label='MonitoringSwitch',
                       host_labels=['ManagedHost', 'AdminPC'], server_label='SNMP-Manager')


def scenario_qos_policy(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _simple_access_lab(lab, params, rng, router_label='QoSEdge', switch_label='AccessSwitch',
                       host_labels=['VoicePhone', 'VideoClient', 'DataPC'])


def scenario_port_security(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _simple_access_lab(lab, params, rng, router_label='AccessRouter', switch_label='PortSecSwitch',
                       host_labels=['EmployeePC', 'RogueDevice'])


def scenario_portfast_bpduguard(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _simple_access_lab(lab, params, rng, router_label='EdgeRouter', switch_label='AccessSwitch',
                       host_labels=['UserPC', 'TestSwitch'])


def _static_routing_lab(lab, params, rng):
    router_a = _add_positioned_device(lab, 'RouterA', 'router', (180, 80))
    router_b = _add_positioned_device(lab, 'RouterB', 'router', (520, 80))
    switch_a = _add_positioned_device(lab, 'AccessA', 'switch', (220, 220))
    switch_b = _add_positioned_device(lab, 'AccessB', 'switch', (560, 220))
    host_a = lab.unique_name('SiteAHost')
    host_b = lab.unique_name('SiteBHost')

    lab.add_device(host_a, 'pc', position=(220, 520))
    lab.add_device(host_b, 'pc', position=(560, 520))

    lab.add_link(router_a, 'GigabitEthernet0/0/0', switch_a, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(router_b, 'GigabitEthernet0/0/0', switch_b, 'GigabitEthernet1/0/24', length='4')
    lab.add_link(router_a, 'GigabitEthernet0/0/1', router_b, 'GigabitEthernet0/0/1', length='6')
    lab.add_link(host_a, 'FastEthernet0', switch_a, 'GigabitEthernet1/0/5', length='6')
    lab.add_link(host_b, 'FastEthernet0', switch_b, 'GigabitEthernet1/0/5', length='6')


def _etherchannel_lab(lab, params, rng):
    switch_a = _add_positioned_device(lab, 'SwitchA', 'switch', (260, 220), profile='edge_access_vlan10_20')
    switch_b = _add_positioned_device(lab, 'SwitchB', 'switch', (520, 220), profile='edge_access_vlan10_20')
    host_a = lab.unique_name('HostA')
    host_b = lab.unique_name('HostB')

    lab.add_device(host_a, 'pc', position=(260, 520))
    lab.add_device(host_b, 'pc', position=(520, 520))

    lab.add_link(switch_a, 'GigabitEthernet1/0/1', switch_b, 'GigabitEthernet1/0/1', length='4')
    lab.add_link(switch_a, 'GigabitEthernet1/0/2', switch_b, 'GigabitEthernet1/0/2', length='4')
    lab.add_link(host_a, 'FastEthernet0', switch_a, 'GigabitEthernet1/0/5', length='6')
    lab.add_link(host_b, 'FastEthernet0', switch_b, 'GigabitEthernet1/0/5', length='6')


def _build_access_switch_entries(lab, access_switch_x, access_profile, access_count, access_offset, access_a_y):
    if access_count == 1:
        access_positions = [0]
        access_labels = ['AccessSwitchA']
    elif access_count == 2:
        access_positions = [0, access_offset]
        access_labels = ['AccessSwitchA', 'AccessSwitchB']
    else:
        access_positions = [0, access_offset, access_offset * 2]
        access_labels = ['AccessSwitchA', 'AccessSwitchB', 'AccessSwitchC']

    access_rows = [access_a_y, access_a_y, access_a_y]
    access_switch_entries = []
    for idx, (label, offset) in enumerate(zip(access_labels, access_positions)):
        device_x = access_switch_x + offset
        device_y = access_rows[min(idx, len(access_rows) - 1)]
        device = _add_positioned_device(
            lab,
            label,
            'switch',
            (device_x, device_y),
            profile=access_profile,
        )
        access_switch_entries.append({
            'label': label,
            'device': device,
            'x': device_x,
            'row_y': device_y,
            'host_idx': 0,
            'port': 5,
        })
    access_primary = next(entry for entry in access_switch_entries if entry['label'] == 'AccessSwitchA')
    return access_switch_entries, access_primary


def _multi_topic_lab(lab, params, rng):
    topics = {topic.lower() for topic in (params.get('topics') or [])}
    scenarios = {name.lower() for name in (params.get('scenarios') or [])}
    size = (params.get('size') or 'medium').lower()

    def _grid_positions(count, start_x, start_y, x_step=120, y_step=90, cols=6):
        positions = []
        if count <= 0:
            return positions
        for idx in range(count):
            col = idx % cols
            row = idx // cols
            positions.append((start_x + col * x_step, start_y + row * y_step))
        return positions

    def _dedupe_extend(target, items):
        for item in items:
            if item not in target:
                target.append(item)

    need_nat = any(name in scenarios for name in ('nat_static_dynamic', 'nat_pat')) or 'nat' in topics
    need_branch = any(name in scenarios for name in ('static_routing', 'campus_branch_wan'))
    need_etherchannel = 'etherchannel_lacp' in scenarios or 'etherchannel' in topics
    need_wan_switch = (need_nat and need_branch) or (need_branch and size == 'large')

    campus_router_label = 'EdgeRouter'
    branch_router_label = 'BranchRouter'
    branch_switch_label = 'BranchSwitch'
    dist_switch_label = 'DistributionSwitch'
    access_switch_label = 'AccessSwitchA'

    if 'campus_branch_wan' in scenarios:
        campus_router_label = 'CampusRouter'
        branch_router_label = 'BranchEdgeRouter'
        branch_switch_label = 'BranchAccessSwitch'
    elif 'static_routing' in scenarios:
        campus_router_label = 'RouterA'
        branch_router_label = 'RouterB'
        branch_switch_label = 'AccessB'
        dist_switch_label = 'AccessA'

    if need_etherchannel:
        dist_switch_label = 'DistributionSwitch'
        access_switch_label = 'AccessSwitchA'

    layout_variant = rng.choice(['wide', 'compact', 'stacked'])
    site_order = ['campus']
    if need_wan_switch:
        site_order.append('wan')
    tail_sites = []
    if need_branch:
        tail_sites.append('branch')
    if need_nat:
        tail_sites.append('isp')
    if len(tail_sites) > 1:
        rng.shuffle(tail_sites)
    site_order.extend(tail_sites)

    site_count = max(len(site_order), 1)
    base_x = 200 + rng.randint(-20, 20)
    if site_count >= 4:
        gap = rng.randint(240, 280)
    elif site_count == 3:
        gap = rng.randint(260, 300)
    else:
        gap = rng.randint(280, 340)

    x_map = {}
    for idx, site in enumerate(site_order):
        x_map[site] = base_x + idx * gap

    campus_x = x_map.get('campus', 220)
    wan_x = x_map.get('wan', campus_x + gap)
    branch_x = x_map.get('branch', wan_x + gap)
    isp_x = x_map.get('isp', branch_x + gap)

    router_y = 60 + rng.randint(-12, 12)
    dist_y = 200 + rng.randint(-12, 12)
    access_a_y = 340 + rng.randint(-12, 12)
    access_b_y = (440 if layout_variant == 'stacked' else 340) + rng.randint(-12, 12)

    lab.add_site_label('Campus', (campus_x - 40, 20))

    dist_profile = 'edge_access_vlan10_20' if need_etherchannel else 'mls_vlan10_20_gateway'
    access_profile = 'edge_access_vlan10_20'

    router_overlays = []
    if need_nat:
        router_overlays.append('overlay_nat')
    if 'acl' in topics or 'acl_filtering' in scenarios:
        router_overlays.append('overlay_acl')
    if 'qos' in topics or 'qos_policy' in scenarios:
        router_overlays.append('overlay_qos')
    if 'ipv6' in topics or 'ipv6_basics' in scenarios:
        router_overlays.append('overlay_ipv6')

    campus_router_profile = router_overlays or None

    campus_router = _add_positioned_device(lab, campus_router_label, 'router', (campus_x + 80, router_y), profile=campus_router_profile)
    dist_switch = _add_positioned_device(lab, dist_switch_label, 'switch', (campus_x + 80, dist_y), profile=dist_profile)
    access_switch_x = campus_x
    access_count = 1
    if size == 'large':
        access_count = rng.choice([2, 3])
    elif size == 'medium':
        access_count = rng.choice([1, 2])

    access_offset = 300
    access_switch_entries, access_primary = _build_access_switch_entries(
        lab,
        access_switch_x,
        access_profile,
        access_count,
        access_offset,
        access_a_y,
    )
    access_switch = access_primary['device']

    campus_right = max(entry['x'] for entry in access_switch_entries) + 200
    wan_x = max(wan_x, campus_right + 120)
    branch_x = max(branch_x, wan_x + 160)
    isp_x = max(isp_x, branch_x + 160)

    lab.add_link(campus_router, 'GigabitEthernet0/0/0', dist_switch, 'GigabitEthernet1/0/24',
                 length=str(rng.randint(4, 6)))

    dist_uplink_port = 1
    for entry in access_switch_entries:
        target = entry['device']
        if entry['label'] == 'AccessSwitchA' and need_etherchannel:
            lab.add_link(dist_switch, f'GigabitEthernet1/0/{dist_uplink_port}', target, 'GigabitEthernet1/0/1', length='4')
            lab.add_link(dist_switch, f'GigabitEthernet1/0/{dist_uplink_port + 1}', target, 'GigabitEthernet1/0/2', length='4')
            dist_uplink_port += 2
        else:
            lab.add_link(dist_switch, f'GigabitEthernet1/0/{dist_uplink_port}', target, 'GigabitEthernet1/0/1', length='4')
            dist_uplink_port += 1

    branch_router = None
    branch_switch = None
    if need_branch:
        lab.add_site_label('Branch', (branch_x, 20))
        branch_router = _add_positioned_device(lab, branch_router_label, 'router', (branch_x, router_y))
        branch_switch = _add_positioned_device(lab, branch_switch_label, 'switch', (branch_x, dist_y))
        lab.add_link(branch_router, 'GigabitEthernet0/0/0', branch_switch, 'GigabitEthernet1/0/24',
                     length=str(rng.randint(4, 6)))

    if need_nat:
        lab.add_site_label('ISP', (isp_x, 20))
        isp_router = _add_positioned_device(lab, 'ISPRouter', 'router', (isp_x, router_y))
        isp_switch = _add_positioned_device(lab, 'ISPSwitch', 'switch', (isp_x, dist_y))
        lab.add_link(isp_router, 'GigabitEthernet0/0/1', isp_switch, 'GigabitEthernet1/0/24',
                     length=str(rng.randint(4, 6)))
        _attach_host(lab, rng, isp_switch, 'GigabitEthernet1/0/5', 'InternetServer',
                     position=(isp_x, 380), device_type='server')

        if need_wan_switch:
            lab.add_site_label('WAN', (wan_x, 120))
            wan_switch = _add_positioned_device(lab, 'WANSwitch', 'switch', (wan_x, dist_y), profile='edge_access_vlan10_20')
            lab.add_link(campus_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/24',
                         length=str(rng.randint(5, 7)))
            lab.add_link(branch_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/23',
                         length=str(rng.randint(5, 7)))
            lab.add_link(isp_router, 'GigabitEthernet0/0/0', wan_switch, 'GigabitEthernet1/0/22',
                         length=str(rng.randint(5, 7)))
            if size == 'large':
                _attach_host(lab, rng, wan_switch, 'GigabitEthernet1/0/5', 'TelemetryPC', position=(wan_x, 520))
        else:
            lab.add_link(campus_router, 'GigabitEthernet0/0/1', isp_router, 'GigabitEthernet0/0/0',
                         length=str(rng.randint(6, 8)))
    elif need_branch:
        if need_wan_switch:
            lab.add_site_label('WAN', (wan_x, 120))
            wan_switch = _add_positioned_device(lab, 'WANSwitch', 'switch', (wan_x, dist_y), profile='edge_access_vlan10_20')
            lab.add_link(campus_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/24',
                         length=str(rng.randint(5, 7)))
            lab.add_link(branch_router, 'GigabitEthernet0/0/1', wan_switch, 'GigabitEthernet1/0/23',
                         length=str(rng.randint(5, 7)))
            if size == 'large':
                _attach_host(lab, rng, wan_switch, 'GigabitEthernet1/0/5', 'TelemetryPC', position=(wan_x, 520))
        else:
            lab.add_link(campus_router, 'GigabitEthernet0/0/1', branch_router, 'GigabitEthernet0/0/1',
                         length=str(rng.randint(6, 8)))

    if 'campus_branch_wan' in scenarios and 'static_routing' in scenarios:
        lab.add_site_label('RouterA = CampusRouter', (180, 130))
        lab.add_site_label('RouterB = BranchEdgeRouter', (branch_x, 130))
    if need_etherchannel:
        pass

    host_labels = []
    server_labels = []
    scenario_hosts = {
        'qos_policy': ['VoicePhone', 'VideoClient', 'DataPC'],
        'port_security': ['EmployeePC', 'RogueDevice'],
        'portfast_bpduguard': ['UserPC', 'TestSwitch'],
        'acl_filtering': ['ClientPC', 'AdminPC'],
        'ipv6_basics': ['IPv6Client', 'IPv6Admin'],
        'ntp_syslog': ['SyslogClient', 'AdminPC'],
        'snmp_monitoring': ['ManagedHost', 'AdminPC'],
        'nat_static_dynamic': ['InsideHostA', 'InsideHostB'],
        'nat_pat': ['InsideHostA', 'InsideHostB'],
        'etherchannel_lacp': ['HostA', 'HostB'],
        'static_routing': ['SiteAHost', 'SiteBHost'],
        'campus_branch_wan': ['CampusHost', 'BranchHostA', 'BranchHostB'],
    }
    scenario_servers = {
        'acl_filtering': ['AppServer'],
        'ipv6_basics': ['IPv6Server'],
        'ntp_syslog': ['NTP-Syslog-Server'],
        'snmp_monitoring': ['SNMP-Manager'],
        'nat_static_dynamic': ['DMZServer'],
        'nat_pat': ['DMZServer'],
    }

    for scenario_name in scenarios:
        _dedupe_extend(host_labels, scenario_hosts.get(scenario_name, []))
        _dedupe_extend(server_labels, scenario_servers.get(scenario_name, []))

    if not host_labels:
        host_labels = ['UserPC', 'AdminPC']

    branch_host_set = {'SiteBHost', 'BranchHostA', 'BranchHostB'}
    branch_hosts = [label for label in host_labels if label in branch_host_set]
    campus_hosts = [label for label in host_labels if label not in branch_host_set]

    if size == 'large':
        campus_limit = 6
        extra_candidates = ['UserPC', 'AdminPC', 'GuestLaptop', 'LabPrinter', 'IoTDevice', 'GuestPC']
        remaining_slots = max(0, campus_limit - len(campus_hosts))
        if remaining_slots:
            rng.shuffle(extra_candidates)
            add_count = rng.randint(max(1, remaining_slots - 1), remaining_slots)
            for label in extra_candidates[:add_count]:
                if len(campus_hosts) >= campus_limit:
                    break
                if label not in campus_hosts:
                    campus_hosts.append(label)

    rng.shuffle(campus_hosts)
    rng.shuffle(branch_hosts)
    host_labels = campus_hosts + branch_hosts

    host_step_y = 0
    host_cols = 4
    host_band_width = 420
    host_min_step = 120
    host_max_step = 180
    access_a_row_y = 520
    access_b_row_y = 520
    access_c_row_y = 520
    host_rows = [access_a_row_y, access_b_row_y, access_c_row_y]
    for entry_idx, entry in enumerate(access_switch_entries):
        entry['host_row_y'] = host_rows[min(entry_idx, len(host_rows) - 1)]
        entry['host_cols'] = host_cols
        entry['host_step_y'] = host_step_y
        entry['server_idx'] = 0

    campus_assignable = [label for label in campus_hosts if label not in {'HostA', 'HostB'}]
    rng.shuffle(campus_assignable)
    host_to_entry = {}
    for idx, label in enumerate(campus_assignable):
        entry = access_switch_entries[idx % len(access_switch_entries)]
        host_to_entry[label] = entry
    for entry in access_switch_entries:
        entry['host_count'] = 0
    for label in campus_assignable:
        host_to_entry[label]['host_count'] += 1
    for entry in access_switch_entries:
        cols = entry['host_count'] if entry['host_count'] else host_cols
        cols = max(1, cols)
        entry['host_cols'] = cols
        if cols == 1:
            entry['host_step_x'] = host_max_step
            entry['start_x'] = entry['x']
        else:
            step_x = int(host_band_width / (cols - 1))
            step_x = max(host_min_step, min(host_max_step, step_x))
            entry['host_step_x'] = step_x
            entry['start_x'] = entry['x'] - int(((cols - 1) / 2) * step_x)

    server_positions = {}
    server_targets = {}
    server_y = (420 if layout_variant == 'compact' else 430) + rng.randint(-15, 15)
    server_labels_ordered = list(server_labels)
    rng.shuffle(server_labels_ordered)
    for idx, label in enumerate(server_labels_ordered):
        target_entry = rng.choice(access_switch_entries)
        server_targets[label] = target_entry
        slot = target_entry['server_idx']
        target_entry['server_idx'] += 1
        server_positions[label] = (
            target_entry['x'] + (slot * 100) - 50,
            server_y + rng.randint(-10, 10),
        )

    branch_positions = _grid_positions(
        max(len(branch_hosts), 1),
        branch_x - 60,
        520 + rng.randint(-15, 15),
        x_step=140,
        y_step=110,
        cols=2,
    )

    dist_port = 5
    branch_port = 5
    campus_idx = 0
    branch_idx = 0

    for label in host_labels:
        if label in {'SiteBHost', 'BranchHostA', 'BranchHostB'} and branch_switch:
            position = branch_positions[branch_idx % len(branch_positions)]
            _attach_host(lab, rng, branch_switch, f'GigabitEthernet1/0/{branch_port}', label, position=position)
            branch_port += 1
            branch_idx += 1
            continue
        if label == 'HostA':
            position = (campus_x + 80, access_a_row_y)
            _attach_host(lab, rng, dist_switch, f'GigabitEthernet1/0/{dist_port}', label, position=position)
            dist_port += 1
            campus_idx += 1
            continue
        if label == 'HostB':
            position = (access_primary['x'], access_a_row_y)
            target_port = f'GigabitEthernet1/0/{access_primary["port"]}'
            _attach_host(lab, rng, access_primary['device'], target_port, label, position=position)
            access_primary['port'] += 1
            campus_idx += 1
            continue
        target_entry = host_to_entry.get(label, access_primary)
        col = target_entry['host_idx'] % target_entry['host_cols']
        row = target_entry['host_idx'] // target_entry['host_cols']
        position = (
            target_entry['start_x'] + col * target_entry['host_step_x'],
            target_entry['host_row_y'] + row * target_entry['host_step_y'],
        )
        target_port = f'GigabitEthernet1/0/{target_entry["port"]}'
        _attach_host(lab, rng, target_entry['device'], target_port, label, position=position)
        target_entry['host_idx'] += 1
        target_entry['port'] += 1
        campus_idx += 1
    for idx, label in enumerate(server_labels):
        position = server_positions.get(label)
        target_entry = server_targets.get(label, access_primary)
        target_port = f'GigabitEthernet1/0/{target_entry["port"]}'
        _attach_host(lab, rng, target_entry['device'], target_port, label,
                     position=position, device_type='server')
        target_entry['port'] += 1


def scenario_static_routing(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _static_routing_lab(lab, params, rng)


def scenario_etherchannel(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _etherchannel_lab(lab, params, rng)


def scenario_acl_filtering(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _acl_filtering_lab(lab, params, rng)


def scenario_ipv6_basics(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    _simple_access_lab(lab, params, rng, router_label='IPv6Router', switch_label='IPv6Switch',
                       host_labels=['IPv6Client', 'IPv6Admin'], server_label='IPv6Server')


SCENARIO_LIBRARY = {
    'composite_topics': {
        'title': 'Composite Multi-Topic Lab',
        'description': 'Combined topics in a single integrated topology.',
        'tags': ['composite'],
        'topics': ['composite'],
        'objectives': [],
        'instructions': 'Use the site labels to map each topic into the shared topology.',
        'builder': lambda *_args, **_kwargs: None,
        'param_generator': lambda _ctx: {},
    },
    'redundant_access': {
        'title': 'Redundant Access Pod',
        'description': 'Variant {topology_variant}: VLAN {vlan_a_id} ({vlan_a_name}, {vlan_a_cidr}) and VLAN '
                       '{vlan_b_id} ({vlan_b_name}, {vlan_b_cidr}) share resilient access.',
        'tags': ['switching', 'redundancy', 'dhcp'],
        'topics': ['vlan', 'dhcp', 'fhrp', 'switching'],
        'objectives': [
            'Build DHCP scopes so VLAN {vlan_a_id} clients draw from {vlan_a_scope} and VLAN {vlan_b_id} '
            'clients draw from {vlan_b_scope}.',
            'Implement FHRP groups {fhrp_group_a} and {fhrp_group_b} using {router_mgmt_ip} as the helper '
            'address.',
            'Keep the management network {mgmt_cidr} reachable through {core_mgmt_ip} and {edge_mgmt_ip}.',
            'Map out the {topology_variant} cabling so you can report on uplink diversity and host placement.'
        ],
        'instructions': (
            'Gateways to hit: VLAN {vlan_a_id} -> {vlan_a_gateway}, VLAN {vlan_b_id} -> {vlan_b_gateway}. '
            'Use ServicesRouter at {router_mgmt_ip} as the DHCP helper and verify reachability of '
            'loopback {loopback_ip}. Explore the {topology_variant} wiring (single-edge, dual-edge mesh, or '
            'collapsed distribution) and fail one uplink from each edge node to observe convergence.'
        ),
        'builder': scenario_redundant_access,
        'param_generator': params_redundant_access,
    },
    'branch_single_vlan': {
        'title': 'Single-VLAN Branch',
        'description': 'Branch variant {branch_variant}: VLAN {branch_vlan_id} ({branch_vlan_name}) on {branch_vlan_cidr}.',
        'tags': ['branch', 'dhcp', 'switching'],
        'topics': ['vlan', 'dhcp', 'switching'],
        'objectives': [
            'Reserve {branch_reserved} for infrastructure and serve clients from {branch_scope}.',
            'Document DHCP bindings on BranchRouter ({branch_router_ip}) and verify BranchSwitch management '
            'at {branch_switch_ip} or the distribution layer, depending on the variant.',
            'Use loopback {branch_loopback_ip} as a reachability probe across the site.',
            'Capture the topology notes for variant {branch_variant} so engineers know which hardware chain '
            'exists on-site.',
        ],
        'instructions': (
            'Set VLAN {branch_vlan_id} gateway to {branch_gateway} and ensure all branch hosts receive '
            'leases inside {branch_scope}. Harden whichever edge ports exist in the {branch_variant} layout '
            'using PortFast/BPDU Guard and document inter-switch trunks if present.'
        ),
        'builder': scenario_branch_single_vlan,
        'param_generator': params_branch_single,
    },
    'ospf_validation': {
        'title': 'OSPF Validation',
        'description': 'Variant {ospf_variant}: OSPF process {ospf_process_id} across {ospf_lan_net} and '
                       '{ospf_p2p_net} with loopback {ospf_loopback_ip}.',
        'tags': ['routing', 'ospf'],
        'topics': ['ospf', 'routing'],
        'objectives': [
            'Address RouterA G0/0/0 as {ospf_r1_lan_ip} and RouterB G0/0/0 as {ospf_r2_lan_ip} on {ospf_lan_net}.',
            'Address RouterA G0/0/1 as {ospf_r1_p2p_ip} and RouterB G0/0/1 as {ospf_r2_p2p_ip} on {ospf_p2p_net}.',
            'Advertise loopback {ospf_loopback_ip}/32 in area 0 and capture adjacency logs on both links.',
            'Tune interface costs to force SPF to prefer the alternate link, then document the SPF event.',
        ],
        'instructions': (
            'Use process ID {ospf_process_id}, confirm TestHostA ({test_host_a_ip}) and TestHostB '
            '({test_host_b_ip}) reach loopback {ospf_loopback_ip} via both adjacencies, then adjust interface '
            'costs to observe SPF recalculation between the LAN and point-to-point links. Verify the DR/BDR '
            'behavior on the shared LAN segment in the {ospf_variant} layout.'
        ),
        'builder': scenario_ospf_validation,
        'param_generator': params_ospf,
    },
    'dual_core_distribution': {
        'title': 'Dual-Core Distribution',
        'description': 'Variant {dual_core_variant}: campus pod feeding VLAN {vlan_a_id}/{vlan_b_id} through '
                       'CoreA ({core_mgmt_ip}) and CoreB ({core_b_mgmt_ip}) or a collapsed stack.',
        'tags': ['campus', 'redundancy', 'switching'],
        'topics': ['vlan', 'fhrp', 'switching', 'redundancy'],
        'objectives': [
            'Stand up FHRP groups {fhrp_group_a}/{fhrp_group_b} and document active/standby roles.',
            'Ensure EdgeA ({edge_mgmt_ip}) and EdgeB ({edge_b_mgmt_ip}) maintain dual-uplink connectivity '
            'even during individual core failures or stacked node outages.',
            'Validate that SharedServer, VoicePhone, and GuestPC all receive addresses in their assigned '
            'VLANs {vlan_a_cidr} and {vlan_b_cidr}.',
            'Sketch the {dual_core_variant} layout so future runs can recreate the same coverage.',
        ],
        'instructions': (
            'Treat CoreA as the primary default gateway at {vlan_a_gateway}/{vlan_b_gateway} and pre-stage '
            'the alternate core/stack to take over using your chosen FHRP. Prune trunks so only VLANs '
            '{vlan_a_id}/{vlan_b_id} pass toward the edge in the {dual_core_variant} topology and record '
            'failover behavior.'
        ),
        'builder': scenario_dual_core_distribution,
        'param_generator': params_dual_core,
    },
    'campus_branch_wan': {
        'title': 'Campus-to-Branch WAN',
        'description': 'Variant {campus_branch_variant}: VLANs {vlan_a_id}/{vlan_b_id} with WAN {wan_cidr} '
                       'linking Campus ({campus_wan_ip}) to Branch ({branch_wan_ip}).',
        'tags': ['wan', 'routing', 'dhcp'],
        'topics': ['wan', 'routing', 'dhcp'],
        'objectives': [
            'Activate the WAN segment between CampusRouter and BranchEdgeRouter with IPs '
            '{campus_wan_ip}/{branch_wan_ip} (direct or via the WAN switch, depending on variant).',
            'Exchange routes so campus VLANs {vlan_a_cidr}/{vlan_b_cidr} and branch VLAN '
            '{branch_vlan_id} ({branch_vlan_cidr}) reach each other even when multiple branches exist.',
            'Harden switch access/trunk ports where applicable and confirm hosts use gateways '
            '{vlan_a_gateway}, {vlan_b_gateway}, and {branch_gateway}.',
        ],
        'instructions': (
            'Provision DHCP scopes for both campus VLANs and the branch VLAN {branch_vlan_id}. '
            'Bring up the {campus_branch_variant} WAN and test CampusHost <-> BranchHost flows. '
            'If trunks are present inside a site, limit them to required VLANs.'
        ),
        'builder': scenario_campus_branch_wan,
        'param_generator': params_campus_branch,
    },
    'nat_static_dynamic': {
        'title': 'Static + Dynamic NAT',
        'description': 'Translate {nat_inside_cidr} to public pool {nat_public_pool} across {nat_outside_cidr}.',
        'tags': ['nat', 'routing'],
        'topics': ['nat', 'routing'],
        'objectives': [
            'Configure inside interfaces for {nat_inside_cidr} and outside for {nat_outside_cidr}.',
            'Create a dynamic NAT pool from {nat_public_start}-{nat_public_end}.',
            'Add a static NAT for the DMZ server and verify reachability end-to-end.',
            'Capture translation table output during a test session for documentation.'
        ],
        'instructions': (
            'Use {nat_inside_wan_ip}/{nat_outside_wan_ip} on the WAN. Inside hosts should draw from '
            '{nat_inside_scope}. Confirm NAT translations and ACLs permit required traffic.'
        ),
        'builder': scenario_nat_static_dynamic,
        'param_generator': params_nat,
    },
    'nat_pat': {
        'title': 'PAT / Overload NAT',
        'description': 'Overload {nat_inside_cidr} onto {nat_outside_cidr} using a single outside interface.',
        'tags': ['nat', 'routing'],
        'topics': ['nat', 'routing'],
        'objectives': [
            'Configure inside/outside and PAT using the WAN interface address.',
            'Verify multiple inside hosts share a single public IP with unique ports.',
            'Identify the PAT overload interface in the running config.'
        ],
        'instructions': (
            'Inside hosts use gateway {nat_inside_gw}. Use {nat_inside_wan_ip}/{nat_outside_wan_ip} on '
            'the WAN and confirm translations with simulated traffic.'
        ),
        'builder': scenario_nat_pat,
        'param_generator': params_nat,
    },
    'ntp_syslog': {
        'title': 'NTP + Syslog Services',
        'description': 'Centralize time and logging on {server_ip} within {mgmt_cidr}.',
        'tags': ['services', 'management'],
        'topics': ['ntp', 'syslog', 'management'],
        'objectives': [
            'Point all devices at NTP server {server_ip} and verify synchronized clocks.',
            'Send syslog events to {server_ip} at informational level or higher.',
            'Generate a test log entry and confirm the timestamp matches NTP time.'
        ],
        'instructions': (
            'Set router management IP to {router_mgmt_ip}. Ensure SyslogClient and AdminPC can reach '
            'the server on {mgmt_cidr}.'
        ),
        'builder': scenario_ntp_syslog,
        'param_generator': params_services_mgmt,
    },
    'snmp_monitoring': {
        'title': 'SNMP Monitoring',
        'description': 'Monitor network devices from {server_ip} on {mgmt_cidr}.',
        'tags': ['services', 'management'],
        'topics': ['snmp', 'management'],
        'objectives': [
            'Configure SNMPv2c or SNMPv3 on the router and switch.',
            'Validate polling from the SNMP manager at {server_ip}.',
            'Record the community or user credentials used for the test.'
        ],
        'instructions': (
            'Use {router_mgmt_ip} for management and confirm SNMP traps or polls are received.'
        ),
        'builder': scenario_snmp_monitoring,
        'param_generator': params_services_mgmt,
    },
    'qos_policy': {
        'title': 'QoS Policy Enforcement',
        'description': 'Prioritize voice/video traffic on the access edge.',
        'tags': ['qos', 'switching'],
        'topics': ['qos', 'switching'],
        'objectives': [
            'Classify voice/video/data traffic and apply a policy-map on uplinks.',
            'Verify queueing behavior during congestion.',
            'Confirm data traffic remains best-effort under the policy.'
        ],
        'instructions': (
            'Mark VoicePhone and VideoClient traffic for higher priority and verify data shaping.'
        ),
        'builder': scenario_qos_policy,
        'param_generator': params_services_mgmt,
    },
    'port_security': {
        'title': 'Port Security',
        'description': 'Lock down access ports for {mgmt_cidr} edge hosts.',
        'tags': ['switching', 'security'],
        'topics': ['port_security', 'switching'],
        'objectives': [
            'Configure sticky MAC limits on access ports.',
            'Trigger and observe security violations with RogueDevice.',
            'Capture port-security status and violation counters.'
        ],
        'instructions': (
            'Apply access port security features and record violation counters.'
        ),
        'builder': scenario_port_security,
        'param_generator': params_services_mgmt,
    },
    'portfast_bpduguard': {
        'title': 'PortFast + BPDU Guard',
        'description': 'Harden access ports against accidental loops.',
        'tags': ['switching', 'stp'],
        'topics': ['stp', 'portfast', 'bpduguard'],
        'objectives': [
            'Enable PortFast on user-facing ports and BPDU Guard on edge ports.',
            'Validate err-disable behavior when TestSwitch sends BPDUs.',
            'Verify PortFast status after recovery.'
        ],
        'instructions': (
            'Document STP state changes and recovery steps after BPDU Guard events.'
        ),
        'builder': scenario_portfast_bpduguard,
        'param_generator': params_services_mgmt,
    },
    'static_routing': {
        'title': 'Static Routing Fundamentals',
        'description': 'Route {lan_a_cidr} and {lan_b_cidr} across WAN {wan_cidr} using static routes.',
        'tags': ['routing', 'wan'],
        'topics': ['static_routing', 'routing', 'wan'],
        'objectives': [
            'Address RouterA/RouterB WAN interfaces with {wan_a_ip}/{wan_b_ip}.',
            'Configure static routes so {lan_a_cidr} and {lan_b_cidr} are reachable end-to-end.',
            'Validate SiteAHost ({lan_a_host}) to SiteBHost ({lan_b_host}) connectivity.'
        ],
        'instructions': (
            'Use default gateways {lan_a_gateway} and {lan_b_gateway}. Track reachability over the WAN '
            'and record the routing table changes.'
        ),
        'builder': scenario_static_routing,
        'param_generator': params_static_routing,
    },
    'etherchannel_lacp': {
        'title': 'EtherChannel (LACP)',
        'description': 'Bundle links between DistributionSwitch and AccessSwitchA using Port-Channel {portchannel_id}.',
        'tags': ['switching', 'redundancy'],
        'topics': ['etherchannel', 'switching', 'redundancy'],
        'objectives': [
            'Create LACP Port-Channel {portchannel_id} across Gi1/0/1-2 on both switches.',
            'Assign management IPs {switch_a_ip} and {switch_b_ip} on {mgmt_cidr}.',
            'Verify HostA ({host_a_ip}) to HostB ({host_b_ip}) reachability.'
        ],
        'instructions': (
            'Keep VLANs consistent on the bundle and confirm the aggregated link comes up on both sides.'
        ),
        'builder': scenario_etherchannel,
        'param_generator': params_etherchannel,
    },
    'acl_filtering': {
        'title': 'ACL Traffic Filtering',
        'description': 'Control access between {client_cidr} and server network {server_cidr}.',
        'tags': ['security', 'routing'],
        'topics': ['acl', 'security', 'routing'],
        'objectives': [
            'Assign ClientPC {client_ip} and AdminPC {admin_ip} with gateway {router_client_ip}.',
            'Assign AppServer {server_ip} with gateway {router_server_ip}.',
            'Permit AdminPC access to AppServer while restricting ClientPC using an ACL on the router.',
            'Apply ACLs inbound or outbound and validate with pings or application traffic.',
            'Document the ACE hit counts after testing to confirm rule ordering.'
        ],
        'instructions': (
            'Document the ACL placement and test rule order impacts on reachability between the two LANs.'
        ),
        'builder': scenario_acl_filtering,
        'param_generator': params_acl,
    },
    'ipv6_basics': {
        'title': 'IPv6 Addressing Basics',
        'description': 'Configure IPv6 addressing on {ipv6_prefix}.',
        'tags': ['ipv6', 'routing'],
        'topics': ['ipv6', 'routing'],
        'objectives': [
            'Assign {router_ipv6} to the router interface and enable IPv6 routing.',
            'Address IPv6Server {server_ipv6} and IPv6Client {client_ipv6}.',
            'Verify IPv6 reachability and neighbor discovery.',
            'Confirm SLAAC or static configuration by checking interface states.'
        ],
        'instructions': (
            'Use SLAAC or static assignments for end devices and confirm IPv6-only connectivity.'
        ),
        'builder': scenario_ipv6_basics,
        'param_generator': params_ipv6,
    },
}


def load_recipe_plan(path):
    with open(path, 'r', encoding='utf-8') as handle:
        payload = json.load(handle)
    return _parse_recipe_payload(payload, source=path)


def _parse_recipe_payload(payload, source='<recipe>'):
    plan = RecipePlan()
    scenarios = payload.get('scenarios') or payload.get('components') or []
    if not isinstance(scenarios, list):
        raise ValueError(f'{source}: "scenarios" must be a list.')
    for entry in scenarios:
        if isinstance(entry, str):
            plan.explicit.append(normalize_scenario_key(entry))
        elif isinstance(entry, dict) and 'name' in entry:
            plan.explicit.append(normalize_scenario_key(entry['name']))
        else:
            raise ValueError(f'{source}: scenario entries must be strings or objects with "name".')

    random_spec = payload.get('random')
    if random_spec is not None:
        specs = random_spec if isinstance(random_spec, list) else [random_spec]
        for spec in specs:
            plan.random_requests.append(_coerce_random_spec(spec, source))
    return plan


def _normalize_tags(values):
    if values is None:
        return None
    if isinstance(values, str):
        values = [values]
    return [value.lower() for value in values]


def _normalize_topics(values):
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    normalized = []
    for value in values:
        normalized.append(value.strip().lower().replace(' ', '_'))
    return [v for v in normalized if v]


def _scenario_has_topics(name, topics):
    if not topics:
        return True
    scenario_topics = {t.lower() for t in SCENARIO_LIBRARY.get(name, {}).get('topics', [])}
    return not set(topics).isdisjoint(scenario_topics)


def _pick_topic_scenarios(rng, topics, excluded):
    picks = []
    excluded_set = set(excluded)
    for topic in topics:
        candidates = [
            name for name in SCENARIO_LIBRARY
            if name not in excluded_set and _scenario_has_topics(name, [topic])
        ]
        if not candidates:
            raise ValueError(f'No scenarios available for topic "{topic}".')
        choice = rng.choice(candidates)
        picks.append(choice)
        excluded_set.add(choice)
    return picks


def _list_topics():
    topic_map = {}
    for key, meta in SCENARIO_LIBRARY.items():
        for topic in meta.get('topics', []):
            topic_map.setdefault(topic, []).append(key)
    return topic_map


def _coerce_random_spec(spec, source):
    if isinstance(spec, int):
        if spec < 0:
            raise ValueError(f'{source}: random count must be non-negative.')
        return RandomScenarioRequest(count=spec)
    if not isinstance(spec, dict):
        raise ValueError(f'{source}: random spec must be int or dict.')
    count = spec.get('count')
    if not isinstance(count, int) or count < 0:
        raise ValueError(f'{source}: random spec requires non-negative integer "count".')
    tags_any = _normalize_tags(spec.get('tags_any'))
    tags_all = _normalize_tags(spec.get('tags_all'))
    exclude = spec.get('exclude') or []
    if isinstance(exclude, str):
        exclude = [exclude]
    exclude = [normalize_scenario_key(name) for name in exclude]
    return RandomScenarioRequest(count=count, tags_any=tags_any, tags_all=tags_all, exclude=exclude)


def _scenario_has_tags(name, tags_any=None, tags_all=None):
    tags = {tag.lower() for tag in SCENARIO_LIBRARY.get(name, {}).get('tags', [])}
    if tags_all and not set(tags_all).issubset(tags):
        return False
    if tags_any and tags.isdisjoint(tags_any):
        return False
    return True


def _pick_random_scenarios(rng, excluded, request):
    excluded_set = set(excluded)
    if request.exclude:
        excluded_set.update(request.exclude)
    candidates = [
        name for name in SCENARIO_LIBRARY
        if name not in excluded_set and _scenario_has_tags(name, request.tags_any, request.tags_all)
    ]
    if request.count > len(candidates):
        raise ValueError('Not enough scenarios available to satisfy recipe randomness constraints.')
    picks = rng.sample(candidates, request.count)
    return picks


def normalize_scenario_key(raw_name):
    return raw_name.strip().lower().replace('-', '_')


def _topics_from_scenarios(scenario_names):
    topics = []
    for name in scenario_names:
        for topic in SCENARIO_LIBRARY.get(name, {}).get('topics', []):
            if topic not in topics:
                topics.append(topic)
    return topics


COMPOSITE_INCOMPATIBLE = {
    'ospf_validation',
    'static_routing',
    'dual_core_distribution',
    'redundant_access',
    'branch_single_vlan',
    'campus_branch_wan',
}


def _is_composite_compatible(name):
    return name.lower() not in COMPOSITE_INCOMPATIBLE


def _build_composite_instance(composite_details, topics, size, warnings=None):
    scenario_titles = []
    objectives = []
    for detail in composite_details:
        meta = detail['meta']
        params = detail['params']
        title = _format_template(meta.get('title') or detail['name'], params)
        scenario_titles.append(title)
        objectives.append(f'{title}:')
        for objective in meta.get('objectives') or []:
            objectives.append(f'  - {_format_template(objective, params)}')

    topic_list = ', '.join(sorted({topic for topic in (topics or [])}))
    scenario_list = '; '.join(scenario_titles) if scenario_titles else 'Custom selection'
    description = f'Combined topics: {topic_list}.' if topic_list else 'Combined multi-topic lab.'
    instructions = (
        f'Scenarios included: {scenario_list}\n'
        f'Topology size: {size}. Use the site labels to map each topic into the shared topology.'
    )
    if warnings:
        instructions += '\nComposite notes: ' + ' '.join(warnings)

    composite_meta = dict(SCENARIO_LIBRARY.get('composite_topics', {}))
    composite_meta.update({
        'title': composite_meta.get('title') or 'Composite Multi-Topic Lab',
        'description': description,
        'objectives': objectives,
        'instructions': instructions,
        'preformatted_description': True,
        'preformatted_objectives': True,
        'preformatted_instructions': True,
    })
    return {'name': 'composite_topics', 'meta': composite_meta, 'params': {}}


def validate_lab(lab):
    warnings = []

    names = [dev.get('name') for dev in lab.devices]
    if len(names) != len(set(names)):
        warnings.append('Duplicate device names detected; check scenario builders for collisions.')

    port_usage = {}
    for link in lab.links:
        for dev_key, port_key in [(link.get('dev1'), link.get('port1')), (link.get('dev2'), link.get('port2'))]:
            if not dev_key or not port_key:
                continue
            key = (dev_key, port_key)
            if key in port_usage:
                warnings.append(f'Port {dev_key} {port_key} is used by multiple links.')
            else:
                port_usage[key] = link

    try:
        template_map = lab._load_template_map()
    except Exception as exc:  # pragma: no cover - informative failure path
        warnings.append(f'Template validation failed: {exc}')
        return warnings

    bucket_map = {}
    for dev in lab.devices:
        dtype = (dev.get('type') or '').lower()
        if dtype.startswith('switch'):
            bucket = 'switch'
        elif dtype.startswith('pc'):
            bucket = 'pc'
        elif dtype.startswith('router'):
            bucket = 'router'
        elif dtype.startswith('server'):
            bucket = 'server'
        else:
            bucket = dtype or 'unknown'
        bucket_map.setdefault(bucket, 0)
        bucket_map[bucket] += 1

    for bucket in bucket_map:
        if bucket in template_map and not template_map.get(bucket):
            warnings.append(f'No templates available for device type "{bucket}".')
    return warnings


def build_lab_from_scenarios(scenario_names, rng, composite_scenarios=None, composite_topics=None, composite_size='medium'):
    lab = Lab(rng)
    pool = ResourcePool(rng)
    ctx = ParameterContext(rng=rng, pool=pool)
    instances = []

    force_composite = not composite_scenarios and len(scenario_names) > 1
    if force_composite:
        composite_scenarios = list(scenario_names)

    composite_set = {name.lower() for name in (composite_scenarios or [])}
    composite_candidates = [name for name in composite_set if _is_composite_compatible(name)]
    composite_topics = composite_topics or _topics_from_scenarios(composite_candidates)
    composite_built = False
    composite_details = []
    composite_warnings = []

    for scenario_name in scenario_names:
        scenario = SCENARIO_LIBRARY.get(scenario_name)
        if scenario is None:
            raise KeyError(f'Unknown scenario key: {scenario_name}')
        param_generator = scenario.get('param_generator') or (lambda _ctx: {})
        params = param_generator(ctx)
        if scenario_name.lower() in composite_set:
            if scenario_name.lower() not in composite_candidates:
                composite_warnings.append(
                    f'{scenario_name} omitted (requires dedicated topology)'
                )
                continue
            composite_details.append({'name': scenario_name, 'meta': scenario, 'params': params})
            if not composite_built:
                _multi_topic_lab(
                    lab,
                    {'topics': composite_topics, 'scenarios': list(composite_candidates), 'size': composite_size},
                    rng,
                )
                composite_built = True
        else:
            scenario['builder'](lab, params, ctx)
            instances.append({'name': scenario_name, 'meta': scenario, 'params': params})

    if composite_details:
        instances = [_build_composite_instance(composite_details, composite_topics, composite_size, composite_warnings)]
    return lab, instances


def render_objectives_markdown(instances, warnings=None, rng=None):
    lines = ['# Lab Objectives', '']
    rng = rng or random.Random()
    if warnings:
        lines.append('## Warnings')
        for warning in warnings:
            lines.append(f'- {warning}')
        lines.append('')
    for idx, ctx in enumerate(instances, start=1):
        meta = ctx['meta']
        params = ctx['params']
        title = _format_template(meta.get('title') or ctx['name'], params)
        if meta.get('preformatted_description'):
            description = (meta.get('description') or '').strip()
        else:
            description = _format_template(meta.get('description', '').strip(), params)
        objectives = _sample_objectives(meta, params, rng)
        if meta.get('preformatted_instructions'):
            instructions = (meta.get('instructions') or '').strip()
        else:
            instructions = _format_template(meta.get('instructions', '').strip(), params)

        lines.append(f'## {idx}. {title}')
        if description:
            lines.append(description)
        if objectives:
            lines.append('')
            lines.append('Objectives:')
            for objective in objectives:
                lines.append(f'- {objective}')
        if instructions:
            lines.append('')
            lines.append('Notes:')
            lines.append(instructions)
        lines.append('')
    return '\n'.join(lines).strip() + '\n'


def derive_objectives_path(output_path):
    base, _ = os.path.splitext(output_path)
    return f'{base}_objectives.md'


def derive_pkt_path(output_path):
    base, _ = os.path.splitext(output_path)
    return f'{base}.pkt'


def encode_pkt(xml_path, pkt_path, legacy=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ptexplorer_path = os.path.join(script_dir, 'ptexplorer.py')
    if not os.path.exists(ptexplorer_path):
        raise FileNotFoundError('ptexplorer.py not found alongside lab_model.py; PKT export is unavailable.')
    cmd = [sys.executable, ptexplorer_path, '-e', xml_path, pkt_path]
    if legacy:
        cmd.append('--legacy')
    subprocess.run(cmd, check=True)
    print(f'Packet Tracer PKT written to {pkt_path}')


def main():
    parser = argparse.ArgumentParser(description='Generate Packet Tracer labs from modular scenario profiles.')
    parser.add_argument('-s', '--scenario', action='append', dest='scenarios', help='Scenario name to include (repeatable).')
    parser.add_argument('-r', '--random', type=int, metavar='N', help='Append N random non-repeating scenarios.')
    parser.add_argument('--seed', type=int, help='Seed for the random scenario picker.')
    parser.add_argument('-o', '--output', default=os.path.join('generated', 'generated_lab.xml'),
                        help='Destination Packet Tracer XML path (defaults under generated/).')
    parser.add_argument('--list', action='store_true', help='List available scenarios and exit.')
    parser.add_argument('--list-topics', action='store_true', help='List available CCNA topics and exit.')
    parser.add_argument('--topics', action='append', help='Add one scenario per topic (repeatable or comma-separated).')
    parser.add_argument('--instructions-output', help='Optional path for Markdown objectives/instructions.')
    parser.add_argument('--no-instructions', action='store_true', help='Skip writing objectives for the generated lab.')
    parser.add_argument('--print-instructions', action='store_true', help='Print objectives to stdout after generation.')
    parser.add_argument('--pkt-output', help='Destination Packet Tracer PKT path (defaults to matching XML name).')
    parser.add_argument('--skip-pkt', action='store_true', help='Skip automatic PKT export via ptexplorer.py.')
    parser.add_argument('--legacy-pkt', action='store_true', help='Use legacy encoding when creating the PKT file.')
    parser.add_argument('--recipe', help='Path to a JSON recipe describing scenario mixes and randomization rules.')
    parser.add_argument('--size', choices=['small', 'medium', 'large'], default='medium',
                        help='Topology size for composite multi-topic labs (small/medium/large).')
    args = parser.parse_args()

    if args.list:
        print('Available scenarios:')
        for key, meta in SCENARIO_LIBRARY.items():
            tags = f" ({', '.join(meta.get('tags', []))})" if meta.get('tags') else ''
            print(f' - {key}{tags}: {meta["description"]}')
        return

    if args.list_topics:
        topic_map = _list_topics()
        print('Available topics:')
        for topic, scenarios in sorted(topic_map.items()):
            print(f' - {topic}: {", ".join(sorted(scenarios))}')
        return

    if args.seed is not None:
        random.seed(args.seed)
    rng = random.Random(args.seed)

    recipe_plan = RecipePlan()
    if args.recipe:
        try:
            recipe_plan = load_recipe_plan(args.recipe)
        except (OSError, ValueError) as exc:
            parser.error(f'Failed to load recipe: {exc}')

    selected = []
    selected_set = set()

    def _add_selection(key, raw_display=None):
        if key not in SCENARIO_LIBRARY:
            display = raw_display or key
            parser.error(f'Unknown scenario: {display}')
        if key not in selected_set:
            selected.append(key)
            selected_set.add(key)

    for recipe_name in recipe_plan.explicit:
        _add_selection(recipe_name)

    if args.scenarios:
        for raw in args.scenarios:
            key = normalize_scenario_key(raw)
            _add_selection(key, raw_display=raw)

    topics_requested = []
    composite_topic_picks = []
    if args.topics:
        for entry in args.topics:
            parts = [part.strip() for part in entry.split(',') if part.strip()]
            topics_requested.extend(parts)
    topics_requested = _normalize_topics(topics_requested)
    if topics_requested:
        try:
            topic_picks = _pick_topic_scenarios(rng, topics_requested, selected_set)
            for pick in topic_picks:
                _add_selection(pick)
            if len(topics_requested) > 1:
                composite_topic_picks = list(topic_picks)
        except ValueError as exc:
            parser.error(str(exc))

    random_requests = list(recipe_plan.random_requests)
    if args.random:
        random_requests.append(RandomScenarioRequest(count=args.random))

    try:
        for request in random_requests:
            if request.count <= 0:
                continue
            picks = _pick_random_scenarios(rng, selected_set, request)
            for name in picks:
                _add_selection(name)
    except ValueError as exc:
        parser.error(str(exc))

    if not selected:
        parser.error('Specify scenarios via --scenario, --random, or --recipe.')

    lab, instances = build_lab_from_scenarios(
        selected,
        rng,
        composite_scenarios=composite_topic_picks or None,
        composite_topics=topics_requested or None,
        composite_size=args.size,
    )
    warnings = validate_lab(lab)
    note_text = render_note_text(instances, rng=rng)
    lab.set_instruction_note_text(note_text)
    lab.to_packettracer_xml(args.output)

    need_objectives = not args.no_instructions or args.print_instructions
    if need_objectives:
        objectives_text = render_objectives_markdown(instances, warnings=warnings, rng=rng)
        if not args.no_instructions:
            destination = args.instructions_output or derive_objectives_path(args.output)
            with open(destination, 'w', encoding='utf-8') as handle:
                handle.write(objectives_text)
            print(f'Lab objectives written to {destination}')
        if args.print_instructions:
            print('\n' + objectives_text)

    if not args.skip_pkt:
        pkt_destination = args.pkt_output or derive_pkt_path(args.output)
        try:
            encode_pkt(args.output, pkt_destination, legacy=args.legacy_pkt)
        except Exception as exc:  # pragma: no cover - informative failure path
            raise RuntimeError(f'Failed to encode PKT via ptexplorer.py: {exc}') from exc


if __name__ == '__main__':
    main()
