import ipaddress
import json
import os
import random
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set

import layouts
from core import Lab
from profiles import VLAN_NAME_POOL


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
        'admin_ipv6': _host_ipv6(network, 100),
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


def params_exercise_1(ctx: ParameterContext):
    """Stable addressing plan for the first learner-facing activity."""
    return {
        'left_lan_cidr': '192.168.10.0/24',
        'right_lan_cidr': '192.168.20.0/24',
        'transit_cidr': '10.0.0.0/30',
        'left_router_ip': '192.168.10.1',
        'right_router_ip': '192.168.20.1',
        'left_pc_ip': '192.168.10.10',
        'right_pc_ip': '192.168.20.10',
        'transit_left_ip': '10.0.0.1',
        'transit_right_ip': '10.0.0.2',
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
    if meta.get('preformatted_objectives'):
        return objectives  # already formatted and grouped -- don't sample
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
    """Build the instruction-note text for embedding inside a Packet Tracer note.

    Each line is hard-wrapped at 90 columns using ``textwrap.fill``.
    Continuation lines MUST be indented — Packet Tracer renders column-0
    continuations as a single flat line.  Matches the proven format from
    lab_model.py.
    """
    if not instances:
        return ''

    import textwrap
    rng = rng or random.Random()

    def append_wrapped(buf, text, initial='', subsequent=None, width=90):
        if not text:
            return
        init = initial or ''
        sub = subsequent if subsequent is not None else init
        filled = textwrap.fill(text, width=width, initial_indent=init,
                               subsequent_indent=sub)
        buf.extend(filled.splitlines())

    lines = ['Lab Objectives']
    for idx, ctx in enumerate(instances, start=1):
        meta = ctx['meta']
        params = ctx['params']
        title = _format_template(meta.get('title') or ctx['name'], params)
        append_wrapped(lines, f'{idx}. {title}', subsequent='   ')
        objectives_list = _sample_objectives(meta, params, rng)
        if meta.get('preformatted_objectives'):
            for objective in objectives_list:
                append_wrapped(lines, objective, initial='  - ', subsequent='    ')
        else:
            for objective in objectives_list:
                append_wrapped(lines, objective, initial='  - ', subsequent='    ')
        if meta.get('instructions'):
            if meta.get('preformatted_instructions'):
                instructions = meta.get('instructions') or ''
            else:
                instructions = _format_template(meta['instructions'], params)
            append_wrapped(lines, 'Notes: ' + instructions, subsequent='       ')
        lines.append('')
    return '\n'.join(line for line in lines if line).strip()


def _ctx_rng(ctx):
    return ctx.rng if ctx else random.Random()


def scenario_redundant_access(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice([
        ('Single Edge Uplinks', layouts._redundant_variant_single_edge),
        ('Dual Edge Mesh', layouts._redundant_variant_dual_edge_mesh),
        ('Collapsed Distribution', layouts._redundant_variant_collapsed_distribution),
    ])
    params['topology_variant'] = variant_label
    builder(lab, params, rng)


def scenario_branch_single_vlan(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice([
        ('Compact Pod', layouts._branch_variant_compact),
        ('Layered Distribution', layouts._branch_variant_layered),
        ('Dual Access Rings', layouts._branch_variant_dual_access),
    ])
    params['branch_variant'] = variant_label
    builder(lab, params, rng)


def scenario_ospf_validation(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice([
        ('Dual Router Shared LAN', layouts._ospf_variant_direct_hosts),
        ('Dual Router Access Fanout', layouts._ospf_variant_access_switch),
    ])
    params['ospf_variant'] = variant_label
    builder(lab, params, rng)


def scenario_dual_core_distribution(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice([
        ('Full Mesh Cores', layouts._dual_core_variant_mesh),
        ('Collapsed Core Stack', layouts._dual_core_variant_collapsed),
        ('DMZ Ring', layouts._dual_core_variant_dmz_ring),
    ])
    params['dual_core_variant'] = variant_label
    builder(lab, params, rng)


def scenario_campus_branch_wan(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    variant_label, builder = rng.choice([
        ('Direct WAN Link', layouts._campus_branch_variant_direct),
        ('WAN Access Switch', layouts._campus_branch_variant_wan_access),
        ('Dual Branch Sites', layouts._campus_branch_variant_dual_branch),
    ])
    params['campus_branch_variant'] = variant_label
    builder(lab, params, rng)


def scenario_nat_static_dynamic(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._nat_edge_lab(lab, params, rng)


def scenario_nat_pat(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._nat_edge_lab(lab, params, rng)


def scenario_ntp_syslog(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._simple_access_lab(lab, params, rng, router_label='MgmtRouter', switch_label='MgmtSwitch',
                               host_labels=['SyslogClient', 'AdminPC'], server_label='NTP-Syslog-Server')


def scenario_snmp_monitoring(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._simple_access_lab(lab, params, rng, router_label='SNMPRouter', switch_label='MonitoringSwitch',
                               host_labels=['ManagedHost', 'AdminPC'], server_label='SNMP-Manager')


def scenario_qos_policy(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._simple_access_lab(lab, params, rng, router_label='QoSEdge', switch_label='AccessSwitch',
                               host_labels=['VoicePhone', 'VideoClient', 'DataPC'])


def scenario_port_security(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._simple_access_lab(lab, params, rng, router_label='AccessRouter', switch_label='PortSecSwitch',
                               host_labels=['EmployeePC', 'RogueDevice'])


def scenario_portfast_bpduguard(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._simple_access_lab(lab, params, rng, router_label='EdgeRouter', switch_label='AccessSwitch',
                               host_labels=['UserPC', 'TestSwitch'])


def scenario_static_routing(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._static_routing_lab(lab, params, rng)


def scenario_exercise_1(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._exercise_1_static_routing_lab(lab, params, rng)


def scenario_etherchannel(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._etherchannel_lab(lab, params, rng)


def scenario_acl_filtering(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._acl_filtering_lab(lab, params, rng)


def scenario_ipv6_basics(lab, params, ctx=None):
    rng = _ctx_rng(ctx)
    layouts._simple_access_lab(lab, params, rng, router_label='IPv6Router', switch_label='IPv6Switch',
                               host_labels=['IPv6Client', 'IPv6Admin'], server_label='IPv6Server')


SCENARIO_LIBRARY = {
    'composite_topics': {
        'title': 'Composite Multi-Topic Lab',
        'description': 'Combined topics in a single integrated topology.',
        'tags': ['composite'],
        'topics': ['composite'],
        'objectives': [],
        'instructions': 'Each scenario section below lists the devices and addressing you need to configure. Use the site labels in the topology to locate each group of devices.',
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
            'Create VLANs {vlan_a_id} ({vlan_a_name}) and {vlan_b_id} ({vlan_b_name}) on all switches and '
            'configure trunks between them.',
            'Configure DHCP pools on ServicesRouter: VLAN {vlan_a_id} scope {vlan_a_scope}, '
            'VLAN {vlan_b_id} scope {vlan_b_scope}. Set the default gateway for each pool.',
            'Set SVI or sub-interface gateways: VLAN {vlan_a_id} = {vlan_a_gateway}, '
            'VLAN {vlan_b_id} = {vlan_b_gateway}.',
            'Configure HSRP/VRRP group {fhrp_group_a} for VLAN {vlan_a_id} and group {fhrp_group_b} '
            'for VLAN {vlan_b_id}. Set virtual IPs to the gateway addresses above.',
            'Add ip helper-address {router_mgmt_ip} on VLANs that need DHCP relay.',
            'Assign management IP {core_mgmt_ip} to CoreSwitch and {edge_mgmt_ip} to EdgeSwitch on {mgmt_cidr}.',
            'Configure a loopback interface on ServicesRouter with IP {loopback_ip}/32 and ping it from a host.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Create the VLANs, assign switchports, set up trunks, '
            'configure DHCP and FHRP, then test host-to-host reachability across VLANs. '
            'Topology variant: {topology_variant}.'
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
            'Create VLAN {branch_vlan_id} ({branch_vlan_name}) on BranchSwitch and assign host-facing ports to it.',
            'Configure a DHCP pool on BranchRouter for {branch_vlan_cidr}: '
            'default gateway {branch_gateway}, address range {branch_scope}. '
            'Exclude {branch_reserved} from the pool for infrastructure.',
            'Set BranchRouter G0/0/0 (or the sub-interface for VLAN {branch_vlan_id}) to {branch_gateway}.',
            'Assign management IP {branch_switch_ip} to BranchSwitch SVI or management interface.',
            'Configure a loopback on BranchRouter with IP {branch_loopback_ip}/32.',
            'Connect a host to BranchSwitch, confirm it gets a DHCP lease, and ping {branch_gateway}.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Set up the VLAN, DHCP pool, and IP addressing from scratch. '
            'Topology variant: {branch_variant}.'
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
            'Assign IP {ospf_r1_lan_ip} to RouterA G0/0/0 and {ospf_r2_lan_ip} to RouterB G0/0/0 (subnet {ospf_lan_net}).',
            'Assign IP {ospf_r1_p2p_ip} to RouterA G0/0/1 and {ospf_r2_p2p_ip} to RouterB G0/0/1 (subnet {ospf_p2p_net}).',
            'Create a loopback interface on RouterA with IP {ospf_loopback_ip}/32.',
            'Enable OSPF process {ospf_process_id} on both routers. Advertise all connected networks in area 0.',
            'Set the point-to-point link network type to point-to-point on both ends.',
            'Change the OSPF cost on one interface so traffic prefers the alternate path, then check '
            'the routing table to confirm the change took effect.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All interfaces start unconfigured. Assign IPs, enable OSPF, bring up adjacencies, '
            'and test end-to-end reachability. Variant: {ospf_variant}.'
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
            'Create VLANs {vlan_a_id} and {vlan_b_id} on all switches. Configure trunk links between cores and edges.',
            'Configure SVIs on CoreA: VLAN {vlan_a_id} = {vlan_a_gateway}, VLAN {vlan_b_id} = {vlan_b_gateway}. '
            'Mirror the SVIs on CoreB with the same subnets.',
            'Set up HSRP/VRRP group {fhrp_group_a} on VLAN {vlan_a_id} and group {fhrp_group_b} on VLAN {vlan_b_id}. '
            'Make CoreA the active gateway and CoreB the standby.',
            'Assign management IPs: CoreA = {core_mgmt_ip}, CoreB = {core_b_mgmt_ip}, '
            'EdgeA = {edge_mgmt_ip}, EdgeB = {edge_b_mgmt_ip} on {mgmt_cidr}.',
            'Assign edge switch access ports to the correct VLANs for hosts.',
            'Prune trunks so only VLANs {vlan_a_id} and {vlan_b_id} are allowed on uplinks.',
            'Shut down one core uplink and confirm hosts still reach their gateway via the standby.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Build the VLAN, trunk, FHRP, and management config from scratch. '
            'Variant: {dual_core_variant}.'
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
            'Assign {campus_wan_ip} to CampusRouter WAN interface and {branch_wan_ip} to BranchEdgeRouter WAN interface '
            '(subnet {wan_cidr}).',
            'Configure static or default routes on both routers so campus subnets {vlan_a_cidr}/{vlan_b_cidr} '
            'and branch subnet {branch_vlan_cidr} can reach each other across the WAN.',
            'Create VLANs {vlan_a_id}/{vlan_b_id} on campus switches and VLAN {branch_vlan_id} on the branch switch. '
            'Configure trunks and access ports.',
            'Set up DHCP pools: campus VLANs with gateways {vlan_a_gateway}/{vlan_b_gateway}, '
            'branch VLAN with gateway {branch_gateway}.',
            'Ping from a campus host to a branch host to confirm end-to-end WAN reachability.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Build WAN addressing, VLANs, routing, and DHCP from scratch. '
            'Variant: {campus_branch_variant}.'
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
            'Assign {nat_inside_gw} to {router_name} G0/0/0 (inside) and {nat_inside_wan_ip} to {router_name} G0/0/1 (WAN). '
            'Assign {nat_outside_wan_ip} to ISPRouter G0/0/1.',
            'Mark {router_name} G0/0/0 as "ip nat inside" and G0/0/1 as "ip nat outside".',
            'Create a NAT pool named PUBLICPOOL using range {nat_public_start} to {nat_public_end} with the '
            'appropriate mask.',
            'Write an ACL that matches inside hosts on {nat_inside_cidr} and bind it to the NAT pool.',
            'Add a static NAT entry mapping DMZServer\'s inside address to one of the pool addresses.',
            'From an inside host, ping {outside_server_name} and run "show ip nat translations" on {router_name} '
            'to confirm dynamic translations are being created.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Configure IP addressing, NAT inside/outside, '
            'the dynamic pool, static entry, and test reachability.'
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
            'Assign {nat_inside_gw} to {router_name} G0/0/0 (inside LAN) and {nat_inside_wan_ip} to {router_name} '
            'G0/0/1 (WAN). Assign {nat_outside_wan_ip} to ISPRouter G0/0/1.',
            'Mark {router_name} G0/0/0 as "ip nat inside" and G0/0/1 as "ip nat outside".',
            'Write an ACL matching {nat_inside_cidr} and configure PAT with '
            '"ip nat inside source list <ACL> interface G0/0/1 overload".',
            'Set default gateway {nat_inside_gw} on all inside hosts (or configure DHCP to hand it out).',
            'From two different inside hosts, ping {outside_server_name}, then run "show ip nat translations" '
            'on {router_name} to confirm both hosts share the same public IP with different port numbers.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Set up IP addressing, NAT overload, and routing from scratch, '
            'then test translations.'
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
            'Assign {router_mgmt_ip} to {router_name} G0/0/0. '
            'Set NTP-Syslog-Server IP to {server_ip} with gateway {router_mgmt_ip}.',
            'On {router_name}, configure "ntp server {server_ip}" and "logging host {server_ip}".',
            'Set "service timestamps log datetime msec" and "logging trap informational" on {router_name}.',
            'On each host, set the default gateway to {router_mgmt_ip} and confirm they can ping {server_ip}.',
            'Shut/no-shut an interface on {router_name} to generate a syslog event, then check '
            'the server received it.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Set up IP addressing, NTP, and syslog from scratch.'
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
            'Assign {router_mgmt_ip} to {router_name} G0/0/0. '
            'Set SNMP-Manager IP to {server_ip} with gateway {router_mgmt_ip}.',
            'Configure an SNMPv2c community string (e.g. "YOURSTRING") on {router_name} with read-only access.',
            'Configure "snmp-server host {server_ip} version 2c YOURSTRING" to send traps to the manager.',
            'Enable SNMP link-up/link-down traps with "snmp-server enable traps".',
            'From SNMP-Manager, confirm you can reach {router_mgmt_ip} (basic connectivity test for polling).',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Set up IP addressing and SNMP from scratch.'
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
            'Assign {router_mgmt_ip} to {router_name} G0/0/0. '
            'Set VoicePhone, VideoClient, and DataPC IPs within {mgmt_cidr} with gateway {router_mgmt_ip}.',
            'Create a class-map matching voice traffic (DSCP EF or CoS 5) and another for video (DSCP AF41).',
            'Build a policy-map that gives voice strict priority and video a bandwidth guarantee. '
            'Leave all other traffic as best-effort.',
            'Apply the policy-map to the {switch_name} uplink interface with "service-policy output".',
            'Set the DSCP or CoS values on VoicePhone and VideoClient traffic manually or via '
            'an MLS QoS trust command on their switch ports.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Configure addressing, class-maps, policy-maps, and apply them.'
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
            'Assign {router_mgmt_ip} to {router_name} G0/0/0. '
            'Set EmployeePC and RogueDevice IPs within {mgmt_cidr} with gateway {router_mgmt_ip}.',
            'On {switch_name}, set host-facing ports to access mode.',
            'Enable port security on EmployeePC\'s switchport: maximum 1 MAC, sticky learning, violation shutdown.',
            'Ping {router_name} from EmployeePC to generate traffic and let the MAC learn. '
            'Verify with "show port-security interface <port>".',
            'Disconnect EmployeePC and connect RogueDevice to that same secured port. '
            'The port should go err-disabled because the MAC differs.',
            'Recover the err-disabled port: "shutdown" then "no shutdown". '
            'Optionally change the violation mode to restrict and reconnect RogueDevice to observe the counter increment.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Set up addressing and port security from scratch.'
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
            'Assign {router_mgmt_ip} to {router_name} G0/0/0. '
            'Set UserPC IP within {mgmt_cidr} with gateway {router_mgmt_ip}.',
            'On {switch_name}, enable PortFast on all host-facing access ports '
            '("spanning-tree portfast" per interface or globally with "spanning-tree portfast default").',
            'Enable BPDU Guard on the same ports ("spanning-tree bpduguard enable").',
            'Connect TestSwitch (another switch) to one of those ports. Observe that the port goes err-disabled '
            'because TestSwitch sends BPDUs.',
            'Recover the port: "shutdown", "no shutdown". Optionally configure errdisable recovery for bpduguard.',
            'Confirm UserPC\'s port stays up and transitions to forwarding quickly thanks to PortFast.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Set up addressing, PortFast, and BPDU Guard from scratch.'
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
            'Assign {wan_a_ip} to RouterA G0/0/1 and {wan_b_ip} to RouterB G0/0/1 (WAN subnet {wan_cidr}).',
            'Assign {lan_a_gateway} to RouterA G0/0/0 (LAN A: {lan_a_cidr}) and {lan_b_gateway} to '
            'RouterB G0/0/0 (LAN B: {lan_b_cidr}).',
            'On RouterA, add a static route for {lan_b_cidr} via {wan_b_ip}. '
            'On RouterB, add a static route for {lan_a_cidr} via {wan_a_ip}.',
            'Set SiteAHost default gateway to {lan_a_gateway} and SiteBHost default gateway to {lan_b_gateway}.',
            'Ping from SiteAHost ({lan_a_host}) to SiteBHost ({lan_b_host}) to verify end-to-end connectivity.',
        ],
        'objective_sample_min': 3,
        'objective_sample_max': 5,
        'instructions': (
            'All devices start unconfigured. Assign IPs and static routes from scratch.'
        ),
        'builder': scenario_static_routing,
        'param_generator': params_static_routing,
    },
    'exercise_1': {
        'title': 'Exercise 1 - Static Routing Between Two Routers',
        'description': (
            'Configure R1 and R2 with LANs {left_lan_cidr} and {right_lan_cidr}, '
            'then route between them over {transit_cidr}.'
        ),
        'tags': ['routing', 'static_routing', 'beginner'],
        'topics': ['static_routing', 'routing'],
        'objectives': [
            'Configure R1 G0/0/0 as {left_router_ip}/24 and R1 G0/0/1 as {transit_left_ip}/30.',
            'Configure R2 G0/0/0 as {right_router_ip}/24 and R2 G0/0/1 as {transit_right_ip}/30.',
            'Configure PC1 as {left_pc_ip}/24 with default gateway {left_router_ip}.',
            'Configure PC2 as {right_pc_ip}/24 with default gateway {right_router_ip}.',
            'Add a static route on R1 to {right_lan_cidr} via {transit_right_ip}.',
            'Add a static route on R2 to {left_lan_cidr} via {transit_left_ip}.',
            'Verify end-to-end connectivity by pinging PC2 from PC1.',
        ],
        'objective_sample_min': 7,
        'objective_sample_max': 7,
        'instructions': (
            'Configure the two routers and two PCs from the three instruction tabs. '
            'The learner snapshot starts with blank router configurations and the '
            'activity assessment checks the addressing, routes, and device settings.'
        ),
        'builder': scenario_exercise_1,
        'param_generator': params_exercise_1,
    },
    'etherchannel_lacp': {
        'title': 'EtherChannel (LACP)',
        'description': 'Bundle links between DistributionSwitch and AccessSwitchA using Port-Channel {portchannel_id}.',
        'tags': ['switching', 'redundancy'],
        'topics': ['etherchannel', 'switching', 'redundancy'],
        'objectives': [
            'On {dist_switch_name}: create interface port-channel {portchannel_id}, then assign '
            'Gi1/0/1 and Gi1/0/2 to channel-group {portchannel_id} mode active.',
            'On {access_switch_name}: create interface port-channel {portchannel_id}, then assign '
            'Gi1/0/1 and Gi1/0/2 to channel-group {portchannel_id} mode active.',
            'Assign management SVI IPs: {dist_switch_name} = {switch_a_ip}, {access_switch_name} = {switch_b_ip} '
            'on {mgmt_cidr}.',
            'Set HostA IP to {host_a_ip} and HostB IP to {host_b_ip} with the correct default gateway.',
            'Run "show etherchannel summary" on both switches to confirm the port-channel is up (SU/P flags).',
            'Ping from HostA ({host_a_ip}) to HostB ({host_b_ip}) to verify reachability over the bundle.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Configure the EtherChannel, VLANs, and IPs from scratch.'
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
            'Assign {router_client_ip} to {router_name} G0/0/0 (client LAN: {client_cidr}) and '
            '{router_server_ip} to {router_name} G0/0/1 (server LAN: {server_cidr}).',
            'Set ClientPC IP to {client_ip} with gateway {router_client_ip}. '
            'Set AdminPC IP to {admin_ip} with gateway {router_client_ip}.',
            'Set AppServer IP to {server_ip} with gateway {router_server_ip}.',
            'Write an extended ACL that permits AdminPC ({admin_ip}) to reach AppServer ({server_ip}) '
            'but denies ClientPC ({client_ip}) from reaching AppServer.',
            'Apply the ACL inbound on the client-side interface (G0/0/0) or outbound on the server-side '
            'interface (G0/0/1).',
            'Test: ping AppServer from AdminPC (should work) and from ClientPC (should fail). '
            'Run "show access-lists" to check hit counts.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Set up addressing, write the ACL, apply it, and test.'
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
            'On {router_name}, enable IPv6 routing with "ipv6 unicast-routing".',
            'Assign {router_ipv6} to {router_name} G0/0/0 and bring up the interface.',
            'Set IPv6Server address to {server_ipv6} with default gateway {router_ipv6} '
            '(or configure it for SLAAC).',
            'Set IPv6Client address to {client_ipv6} with default gateway {router_ipv6} '
            '(or configure it for SLAAC).',
            'Set IPv6Admin address to {admin_ipv6} with default gateway {router_ipv6} '
            '(or configure it for SLAAC).',
            'Ping from IPv6Client to IPv6Server using their IPv6 addresses to confirm connectivity.',
            'Ping from IPv6Admin to {router_ipv6} to verify admin host reachability.',
            'Run "show ipv6 neighbors" on {router_name} to see the neighbor discovery table.',
        ],
        'objective_sample_min': 4,
        'objective_sample_max': 6,
        'instructions': (
            'All devices start unconfigured. Configure IPv6 addressing and routing from scratch.'
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
    excluded_set = set(excluded) | _INTERNAL_SCENARIOS
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
        if key in _INTERNAL_SCENARIOS:
            continue
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


_INTERNAL_SCENARIOS = {'composite_topics'}


def _pick_random_scenarios(rng, excluded, request, composite_compatible_only=False):
    excluded_set = set(excluded) | _INTERNAL_SCENARIOS
    if composite_compatible_only:
        excluded_set |= COMPOSITE_INCOMPATIBLE
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
    'acl_filtering',
}

COMPOSITE_DEVICE_NAMES = {
    'router_name': 'EdgeRouter',
    'switch_name': 'AccessSwitchA',
    'dist_switch_name': 'DistributionSwitch',
    'access_switch_name': 'AccessSwitchA',
    'outside_server_name': 'InternetServer',
}

_SCENARIO_DEVICE_NAMES = {
    'port_security': {'router_name': 'AccessRouter', 'switch_name': 'PortSecSwitch'},
    'qos_policy': {'router_name': 'QoSEdge', 'switch_name': 'AccessSwitch'},
    'portfast_bpduguard': {'router_name': 'EdgeRouter', 'switch_name': 'AccessSwitch'},
    'ntp_syslog': {'router_name': 'MgmtRouter', 'switch_name': 'MgmtSwitch'},
    'snmp_monitoring': {'router_name': 'SNMPRouter', 'switch_name': 'MonitoringSwitch'},
    'ipv6_basics': {'router_name': 'IPv6Router', 'switch_name': 'IPv6Switch'},
    'acl_filtering': {'router_name': 'AccessRouter'},
    'nat_pat': {'router_name': 'EdgeRouter', 'outside_server_name': 'OutsideServer'},
    'nat_static_dynamic': {'router_name': 'EdgeRouter', 'outside_server_name': 'OutsideServer'},
    'etherchannel_lacp': {'dist_switch_name': 'DistributionSwitch', 'access_switch_name': 'AccessSwitchA'},
}


def _is_composite_compatible(name):
    return name.lower() not in COMPOSITE_INCOMPATIBLE


def _build_composite_instance(composite_details, topics, size, warnings=None):
    scenario_titles = []
    objectives = []
    seen_objectives = set()
    for detail in composite_details:
        meta = detail['meta']
        params = detail['params']
        title = _format_template(meta.get('title') or detail['name'], params)
        raw_objectives = meta.get('objectives') or []
        if not raw_objectives:
            continue  # skip placeholder entries with no objectives
        scenario_titles.append(title)
        objectives.append('')
        objectives.append(f'**{title}:**')
        for objective in raw_objectives:
            formatted = _format_template(objective, params)
            # Deduplicate identical objectives across scenarios (e.g. shared gateway assignment)
            if formatted in seen_objectives:
                continue
            seen_objectives.add(formatted)
            objectives.append(f'- {formatted}')

    topic_list = ', '.join(sorted({topic for topic in (topics or [])}))
    scenario_list = '; '.join(scenario_titles) if scenario_titles else 'Custom selection'
    description = f'Combined topics: {topic_list}.' if topic_list else 'Combined multi-topic lab.'
    instructions = (
        f'Scenarios included: {scenario_list}\n'
        f'Topology size: {size}. Use the site labels to locate each group of devices '
        f'in the shared topology. All devices start unconfigured.'
    )

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
    except Exception as exc:
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

    for scenario_name in scenario_names:
        scenario = SCENARIO_LIBRARY.get(scenario_name)
        if scenario is None:
            raise KeyError(f'Unknown scenario key: {scenario_name}')
        param_generator = scenario.get('param_generator') or (lambda _ctx: {})
        params = param_generator(ctx)
        params.update(_SCENARIO_DEVICE_NAMES.get(scenario_name, {}))
        if scenario_name.lower() in composite_set:
            if scenario_name.lower() not in composite_candidates:
                # Incompatible with shared topology — skip in composite mode
                print(f'Note: "{scenario_name}" skipped (requires a dedicated topology).')
                continue
            params.update(COMPOSITE_DEVICE_NAMES)
            composite_details.append({'name': scenario_name, 'meta': scenario, 'params': params})
            if not composite_built:
                layouts._multi_topic_lab(
                    lab,
                    {'topics': composite_topics, 'scenarios': list(composite_candidates), 'size': composite_size},
                    rng,
                )
                composite_built = True
        else:
            scenario['builder'](lab, params, ctx)
            instances.append({'name': scenario_name, 'meta': scenario, 'params': params})

    if composite_details:
        # Update switch_name per scenario based on actual host placement
        switch_map = getattr(lab, '_composite_scenario_switches', {})
        for detail in composite_details:
            actual_switch = switch_map.get(detail['name'])
            if actual_switch:
                detail['params']['switch_name'] = actual_switch

        _unify_composite_lan(composite_details)
        composite_instance = _build_composite_instance(composite_details, composite_topics, composite_size)
        instances.append(composite_instance)
    return lab, instances


def _unify_composite_lan(details):
    """Ensure all composite scenarios share the same campus LAN subnet.

    Each scenario's param_generator allocates its own /24, but in composite
    mode they all share one EdgeRouter G0/0/0 interface.  We adopt the first
    scenario's network and remap every subsequent scenario's IPs into it,
    preserving gateway (.1) and avoiding host-offset collisions.
    """
    shared_net = None
    used_offsets = {0, 255}  # reserve network and broadcast

    def _register_offsets(params, network):
        """Record all host offsets already claimed by a scenario."""
        net_base = int(network.network_address)
        for val in params.values():
            try:
                addr = ipaddress.IPv4Address(str(val))
            except (ValueError, TypeError):
                continue
            if addr in network:
                used_offsets.add(int(addr) - net_base)

    def _next_free_offset(desired):
        """Return *desired* if available, otherwise the next free offset."""
        if desired not in used_offsets:
            return desired
        # Search upward from desired, wrapping within usable range (2..254)
        candidate = desired + 1
        while candidate in used_offsets and candidate < 255:
            candidate += 1
        if candidate < 255:
            return candidate
        # Wrap around and search from 2 upward
        candidate = 2
        while candidate in used_offsets and candidate < desired:
            candidate += 1
        return candidate

    for detail in details:
        p = detail['params']

        # Identify which network this scenario's campus LAN uses
        if 'nat_inside_cidr' in p:
            original_net = ipaddress.IPv4Network(p['nat_inside_cidr'], strict=False)
        elif 'mgmt_cidr' in p:
            original_net = ipaddress.IPv4Network(p['mgmt_cidr'], strict=False)
        else:
            continue  # IPv6-only or no campus LAN params

        if shared_net is None:
            shared_net = original_net
            _register_offsets(p, original_net)
            continue

        if original_net == shared_net:
            _register_offsets(p, original_net)
            continue

        # Remap every IPv4 param that falls within original_net → shared_net
        net_base = int(original_net.network_address)
        for key, val in list(p.items()):
            try:
                addr = ipaddress.IPv4Address(str(val))
            except (ValueError, TypeError):
                continue
            if addr not in original_net:
                continue  # WAN IP, public pool, etc. — leave it alone
            offset = int(addr) - net_base
            if offset == 1:
                # Gateway — always maps to the shared .1 (same interface)
                new_offset = 1
            else:
                new_offset = _next_free_offset(offset)
            used_offsets.add(new_offset)
            p[key] = _host_ip(shared_net, new_offset)

        # Update CIDR strings
        if 'mgmt_cidr' in p:
            p['mgmt_cidr'] = str(shared_net)
        if 'nat_inside_cidr' in p:
            p['nat_inside_cidr'] = str(shared_net)

    # ── Unify WAN / outside addressing across NAT scenarios ──
    # When both nat_static_dynamic and nat_pat are active, each generates its
    # own outside /30 and public pool.  In composite mode they share one
    # EdgeRouter G0/0/1, so the second scenario must adopt the first's WAN.
    _NAT_WAN_KEYS = ('nat_outside_cidr', 'nat_inside_wan_ip', 'nat_outside_wan_ip')
    _NAT_POOL_KEYS = ('nat_public_pool', 'nat_public_start', 'nat_public_end')
    shared_wan = {}   # key → value from the first NAT scenario encountered
    shared_pool = {}  # key → value from the first NAT scenario with a pool
    for detail in details:
        p = detail['params']
        if 'nat_outside_cidr' not in p:
            continue
        if not shared_wan:
            # First NAT scenario — record its WAN and pool params
            for k in _NAT_WAN_KEYS:
                if k in p:
                    shared_wan[k] = p[k]
            for k in _NAT_POOL_KEYS:
                if k in p:
                    shared_pool[k] = p[k]
        else:
            # Subsequent NAT scenario — adopt the first's WAN addressing
            for k, v in shared_wan.items():
                p[k] = v
            # Adopt pool if this scenario references pool params
            for k, v in shared_pool.items():
                if k in p:
                    p[k] = v


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
            if meta.get('preformatted_objectives'):
                for objective in objectives:
                    lines.append(objective)
            else:
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


def derive_activity_path(output_path):
    base, _ = os.path.splitext(output_path)
    return f'{base}.pka'


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


def decode_pkt(pkt_path, xml_path, legacy=False):
    """Decode an existing PKT into normal XML for use as an answer network."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ptexplorer_path = os.path.join(script_dir, 'ptexplorer.py')
    if not os.path.exists(ptexplorer_path):
        raise FileNotFoundError('ptexplorer.py not found alongside lab_model.py; PKT import is unavailable.')
    cmd = [sys.executable, ptexplorer_path, '-d', pkt_path, xml_path]
    if legacy:
        cmd.append('--legacy')
    subprocess.run(cmd, check=True)
    print(f'Packet Tracer answer network decoded to {xml_path}')


def encode_activity(xml_path, activity_path, legacy=False):
    """Encrypt an activity XML into a Packet Tracer PKA file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ptexplorer_path = os.path.join(script_dir, 'ptexplorer.py')
    if not os.path.exists(ptexplorer_path):
        raise FileNotFoundError('ptexplorer.py not found alongside activity.py; PKA export is unavailable.')
    cmd = [sys.executable, ptexplorer_path, '-e', xml_path, activity_path]
    if legacy:
        cmd.append('--legacy')
    subprocess.run(cmd, check=True)
    print(f'Packet Tracer PKA written to {activity_path}')
