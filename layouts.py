def _add_positioned_device(lab, base_label, device_type, position, profile=None):
    name = lab.unique_name(base_label)
    lab.add_device(name, device_type, position=position, profile=profile)
    return name


def _attach_host(lab, rng, parent_switch, parent_port, label, position=None, device_type='pc'):
    host = lab.unique_name(label)
    lab.add_device(host, device_type, position=position)
    lab.add_link(host, 'FastEthernet0', parent_switch, parent_port, length=str(rng.randint(5, 8)))
    return host


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
    # EtherChannel label is handled automatically via scenario_to_entry below

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

    # Build reverse mapping: host label → set of scenario names it belongs to
    host_scenarios = {}
    for scen_name, scen_hosts in scenario_hosts.items():
        if scen_name not in scenarios:
            continue  # only consider active scenarios
        for h in scen_hosts:
            host_scenarios.setdefault(h, set()).add(scen_name)

    # Group scenarios that share hosts using union-find merging.
    # Each scenario starts as its own group; shared hosts merge their groups.
    from collections import OrderedDict
    scenario_parent = {}
    def _find(s):
        while scenario_parent.get(s, s) != s:
            scenario_parent[s] = scenario_parent.get(scenario_parent[s], scenario_parent[s])
            s = scenario_parent[s]
        return s
    def _union(a, b):
        ra, rb = _find(a), _find(b)
        if ra != rb:
            scenario_parent[ra] = rb

    for h_label in campus_assignable:
        scens = host_scenarios.get(h_label, set())
        scen_list = sorted(scens)
        for i in range(1, len(scen_list)):
            _union(scen_list[0], scen_list[i])

    # Build merged groups: root scenario → list of hosts
    merged_groups = OrderedDict()
    for label in campus_assignable:
        scens = host_scenarios.get(label, set())
        if scens:
            root = _find(sorted(scens)[0])
            merged_groups.setdefault(root, []).append(label)
        else:
            merged_groups.setdefault('__ungrouped__', []).append(label)

    ungrouped = merged_groups.pop('__ungrouped__', [])

    # Assign each merged group to an access switch (round-robin by group)
    group_list = list(merged_groups.items())
    rng.shuffle(group_list)
    host_to_entry = {}
    scenario_to_entry = {}
    for group_idx, (root_scen, group_hosts) in enumerate(group_list):
        entry = access_switch_entries[group_idx % len(access_switch_entries)]
        # Map ALL scenarios in this merged group to the same entry
        for scen_name in scenarios:
            if _find(scen_name) == root_scen:
                scenario_to_entry[scen_name] = entry
        for h in group_hosts:
            host_to_entry[h] = entry
    # Spread ungrouped hosts across switches
    for idx, label in enumerate(ungrouped):
        entry = access_switch_entries[idx % len(access_switch_entries)]
        host_to_entry[label] = entry

    # EtherChannel hosts (HostA/HostB) are excluded from campus_assignable,
    # so etherchannel_lacp never enters the union-find.  Ensure it gets a
    # scenario_to_entry mapping so it receives a site label & appears in
    # _composite_scenario_switches.
    if need_etherchannel and 'etherchannel_lacp' not in scenario_to_entry:
        scenario_to_entry['etherchannel_lacp'] = access_primary

    rng.shuffle(campus_assignable)

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

    # Build reverse mapping: server label → scenario name, for affinity
    # Only consider active scenarios so we don't map to an inactive one
    server_to_scenario = {}
    for scen_name, scen_servers in scenario_servers.items():
        if scen_name not in scenarios:
            continue  # skip inactive scenarios
        for s in scen_servers:
            if s not in server_to_scenario:
                server_to_scenario[s] = scen_name

    server_positions = {}
    server_targets = {}
    server_y = (420 if layout_variant == 'compact' else 430) + rng.randint(-15, 15)
    server_labels_ordered = list(server_labels)
    rng.shuffle(server_labels_ordered)
    for idx, label in enumerate(server_labels_ordered):
        # Place server on same switch as the scenario's hosts when possible
        scen = server_to_scenario.get(label)
        if scen and scen in scenario_to_entry:
            target_entry = scenario_to_entry[scen]
        else:
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

    # Add per-scenario site labels near each scenario's access switch
    _SCENARIO_DISPLAY_NAMES = {
        'qos_policy': 'QoS',
        'port_security': 'Port Security',
        'portfast_bpduguard': 'PortFast/BPDU Guard',
        'ipv6_basics': 'IPv6',
        'acl_filtering': 'ACLs',
        'ntp_syslog': 'NTP/Syslog',
        'snmp_monitoring': 'SNMP',
        'nat_static_dynamic': 'Static NAT',
        'nat_pat': 'PAT',
        'etherchannel_lacp': 'EtherChannel',
        'static_routing': 'Static Routing',
        'campus_branch_wan': 'Campus/Branch',
    }
    label_y_offset = -30
    # Collect all scenario display names per switch entry, then emit one
    # combined label per switch so nothing overlaps.
    entry_labels = {}  # id(entry) → (entry, [display_names])
    for scen_name, entry in scenario_to_entry.items():
        display = _SCENARIO_DISPLAY_NAMES.get(scen_name, scen_name.replace('_', ' ').title())
        eid = id(entry)
        if eid not in entry_labels:
            entry_labels[eid] = (entry, [])
        entry_labels[eid][1].append(display)
    for eid, (entry, names) in entry_labels.items():
        combined = ' / '.join(names)
        lab.add_site_label(combined, (entry['x'] - 40, entry['row_y'] + label_y_offset))

    # Expose scenario→switch mapping so objectives can reference the correct switch name
    lab._composite_scenario_switches = {
        scen_name: entry['label'] for scen_name, entry in scenario_to_entry.items()
    }