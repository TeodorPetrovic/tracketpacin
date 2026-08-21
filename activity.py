"""Packet Tracer activity (PKA) assembly helpers.

Packet Tracer activities are encrypted XML documents containing three normal
Packet Tracer snapshots plus activity metadata.  The topology generator owns
the normal snapshot; this module adds the activity wrapper and keeps the
template-specific metadata that Packet Tracer expects.
"""

import copy
import html
import json
import os
import re
import xml.etree.ElementTree as ET


DEFAULT_ASSESSMENT_CHECKS = {
    'power', 'links', 'port-up', 'ip', 'subnet', 'gateway', 'routes'
}


def _clone(element):
    return copy.deepcopy(element)


def _text(element):
    return (element.text or '').strip() if element is not None else ''


def _set_text(parent, tag, value):
    element = parent.find(tag)
    if element is None:
        element = ET.SubElement(parent, tag)
    element.text = '' if value is None else str(value)
    return element


def _write_config(engine, section_name, config_text):
    section = engine.find(section_name)
    if section is None:
        section = ET.SubElement(engine, section_name)
    section.clear()
    if config_text is None:
        return
    for line in str(config_text).strip('\n').splitlines():
        ET.SubElement(section, 'LINE').text = line


def _load_initial_configs(path):
    if not path:
        return {}
    with open(path, 'r', encoding='utf-8') as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError('Initial config JSON must be an object keyed by device name.')
    return data


def _apply_initial_configs(snapshot, initial_configs):
    devices = snapshot.findall('./NETWORK/DEVICES/DEVICE')
    for device in devices:
        engine = device.find('ENGINE')
        if engine is None:
            continue
        name = _text(engine.find('NAME'))
        spec = initial_configs.get(name, initial_configs.get('*'))
        if spec is None:
            continue
        if isinstance(spec, str):
            spec = {'running_config': spec}
        if not isinstance(spec, dict):
            raise ValueError(f'Initial config for {name!r} must be a string or object.')
        if 'running_config' in spec:
            _write_config(engine, 'RUNNINGCONFIG', spec['running_config'])
        if 'startup_config' in spec:
            _write_config(engine, 'STARTUPCONFIG', spec['startup_config'])
        if spec.get('clear_startup_config'):
            _write_config(engine, 'STARTUPCONFIG', '')


def _clear_initial_configs(snapshot):
    """Create a learner-ready blank state while retaining device hardware."""
    for device in snapshot.findall('./NETWORK/DEVICES/DEVICE'):
        engine = device.find('ENGINE')
        if engine is None:
            continue
        type_element = engine.find('TYPE')
        device_type = (_text(type_element) if type_element is not None else '').lower()
        if any(kind in device_type for kind in ('router', 'switch', 'server')):
            _write_config(engine, 'RUNNINGCONFIG', '')
            _write_config(engine, 'STARTUPCONFIG', '')
            # IOS text is not the only place Packet Tracer stores an
            # interface address.  Remove template/default IPv4 values from
            # native PORT records as well, otherwise a supposedly blank
            # learner state can still start with (for example) 1.1.1.50.
            for port in engine.findall('.//PORT'):
                port_type = (_text(port.find('TYPE')) or '').lower()
                if not any(kind in port_type for kind in ('copper', 'fastethernet', 'serial')):
                    continue
                for tag in ('IP', 'SUBNET', 'PORT_GATEWAY', 'PORT_DNS'):
                    element = port.find(tag)
                    if element is not None:
                        element.text = ''
        elif device_type.startswith('pc'):
            # PCs store IPv4 configuration on their wired port, not in IOS
            # configuration blocks. Clear it too so the learner starts at 0%.
            for port in engine.findall('.//PORT'):
                port_type = (_text(port.find('TYPE')) or '').lower()
                if 'copper' not in port_type and 'fastethernet' not in port_type:
                    continue
                for tag in ('IP', 'SUBNET', 'PORT_GATEWAY', 'PORT_DNS'):
                    element = port.find(tag)
                    if element is not None:
                        element.text = ''
                dhcp = port.find('PORT_DHCP_ENABLE')
                if dhcp is not None:
                    dhcp.text = 'false'


def _device_summary(snapshot):
    result = []
    for device in snapshot.findall('./NETWORK/DEVICES/DEVICE'):
        engine = device.find('ENGINE')
        if engine is None:
            continue
        type_element = engine.find('TYPE')
        result.append({
            'name': _text(engine.find('NAME')),
            'model': type_element.get('model', '') if type_element is not None else '',
            'custom_model': type_element.get('customModel', '') if type_element is not None else '',
            'device_type': _text(type_element) if type_element is not None else '',
            'power': _text(engine.find('POWER')),
        })
    return result


def _node_element(name, node_id=None, *, head=True, check_type='0', eclass='8',
                  node_value='', components='', points='', translate=False):
    attrs = {
        'checkType': str(check_type),
        'eclass': str(eclass),
        'headNode': 'true' if head else 'false',
        'incorrectFeedback': '',
        'nodeValue': str(node_value),
        'obfuscateName': 'false',
        'overrideDBGrading': 'false',
        'variableEnabled': 'false' if head else 'true',
        'variableName': '',
    }
    if translate:
        attrs['translate'] = 'true'
    node = ET.Element('NODE')
    ET.SubElement(node, 'NAME', attrs).text = name
    ET.SubElement(node, 'ID', {'translate': 'true'} if translate else {}).text = node_id or name
    ET.SubElement(node, 'COMPONENTS').text = components
    ET.SubElement(node, 'POINTS').text = str(points)
    return node


def _build_initial_setup(snapshot):
    root = ET.Element('INITIALSETUP')
    network = _node_element('Network', 'Network', translate=False)
    for info in _device_summary(snapshot):
        device_node = _node_element(info['name'], info['name'], translate=True)
        device_node.append(_node_element(
            'Device Model', 'Device Model', head=False, node_value=info['model'], points='1'
        ))
        device_node.append(_node_element(
            'Power', 'Power', head=False, eclass='4', components='Physical',
            node_value='1' if info['power'].lower() == 'true' else '0', points='1'
        ))
        network.append(device_node)
    root.append(network)
    ET.SubElement(root, 'LOAD_INIT_TREE').text = 'true'
    return root


def _build_config_assessment(engine):
    """Build the IOS configuration branch used by Packet Tracer grading."""
    config_outer = _node_element('IOS Configuration', 'IOS Configuration')
    config_inner = _node_element('IOS Configuration', 'IOS Configuration')

    for section_name, display_name in (
        ('RUNNINGCONFIG', 'Running Configuration'),
        ('STARTUPCONFIG', 'Startup Configuration'),
    ):
        section = _node_element(display_name, display_name)
        lines_node = _node_element('LINES', 'LINES')
        lines = engine.findall(f'{section_name}/LINE')
        for index, line in enumerate(lines):
            value = line.text or ''
            leaf = _node_element(
                f'{index:03d} {value}',
                f'{index:03d}{value}',
                head=False,
                node_value=value,
                components='Other',
                points='1',
            )
            name_element = leaf.find('NAME')
            name_element.set('obfuscateName', 'true')
            name_element.set('variableEnabled', 'false')
            lines_node.append(leaf)
        section.append(lines_node)
        config_inner.append(section)
    config_outer.append(config_inner)
    return config_outer


def _set_node_value(node, value):
    name = node.find('NAME')
    if name is not None:
        name.set('nodeValue', '' if value is None else str(value))


def _select_node(node, selected=True):
    """Mark a native assessment node as checked in Packet Tracer's tree."""
    name = node.find('NAME')
    if name is not None:
        name.set('checkType', '2' if selected else '0')


def _named_node(parent, name):
    return next((child for child in parent.findall('NODE') if _text(child.find('NAME')) == name), None)


def _clone_node(parent, name):
    node = _named_node(parent, name)
    return _clone(node) if node is not None else None


def _prune_children(node):
    for child in list(node.findall('NODE')):
        node.remove(child)


def _replace_config_lines(config_node, lines):
    """Use the template's native IOS Configuration node, but only grade task lines."""
    prototype = None
    for candidate in config_node.iter('NODE'):
        candidate_name = _text(candidate.find('NAME'))
        if candidate.find('NAME') is not None and not candidate.findall('NODE') \
                and not candidate_name.startswith('Entire Config'):
            prototype = candidate
            break
    for section_name in ('Running Configuration', 'Startup Configuration'):
        section = _named_node(config_node, section_name)
        if section is None:
            continue
        lines_node = _named_node(section, 'LINES')
        if lines_node is None:
            continue
        for child in list(section.findall('NODE')):
            if child is not lines_node:
                section.remove(child)
        _prune_children(lines_node)
        for index, value in enumerate(lines, start=1):
            leaf = _clone(prototype) if prototype is not None else _node_element(
                f'{index:03d} {value}', f'{index:03d}{value}', head=False,
                node_value=value, components='Other', points='1',
            )
            name = leaf.find('NAME')
            if name is not None:
                name.text = f'{index:03d} {value}'
                name.set('nodeValue', value)
                name.set('obfuscateName', 'true')
                name.set('variableEnabled', 'false')
            identifier = leaf.find('ID')
            if identifier is not None:
                identifier.text = f'{index:03d}{value}'
            points = leaf.find('POINTS')
            if points is not None:
                points.text = '1'
            lines_node.append(leaf)


def _router_targets(engine):
    current_interface = None
    interfaces = {}
    routes = []
    task_lines = []
    for line_element in engine.findall('RUNNINGCONFIG/LINE'):
        raw = line_element.text or ''
        stripped = raw.strip()
        if stripped.startswith('interface '):
            current_interface = stripped.split(None, 1)[1]
            interfaces[current_interface] = {'ip': '', 'mask': '', 'up': False}
            task_lines.append(stripped)
        elif current_interface and stripped.startswith('ip address '):
            fields = stripped.split()
            if len(fields) >= 4:
                interfaces[current_interface]['ip'] = fields[2]
                interfaces[current_interface]['mask'] = fields[3]
            task_lines.append(raw)
        elif current_interface and stripped == 'no shutdown':
            interfaces[current_interface]['up'] = True
            task_lines.append(raw)
        elif stripped.startswith('ip route '):
            routes.append(stripped)
            task_lines.append(stripped)
    return interfaces, routes, task_lines


def _connection_map(snapshot):
    """Return native link expectations keyed by device and interface."""
    devices = snapshot.findall('./NETWORK/DEVICES/DEVICE')
    names = [
        _text(device.find('ENGINE/NAME'))
        for device in devices
    ]
    result = {name: {} for name in names}
    links = snapshot.findall('./NETWORK/LINKS/LINK')
    for link in links:
        cable = link.find('CABLE')
        if cable is None:
            continue
        from_index = cable.findtext('FROM')
        to_index = cable.findtext('TO')
        from_port = cable.findtext('PORT')
        # PT9 stores the second endpoint as another PORT element. Older
        # formats use the same CABLE block with FROM/TO device references.
        ports = cable.findall('PORT')
        if len(ports) >= 2:
            from_port, to_port = ports[0].text, ports[1].text
        else:
            to_port = cable.findtext('TO_PORT') or ''
        try:
            from_name = names[int(from_index)]
            to_name = names[int(to_index)]
        except (TypeError, ValueError, IndexError):
            continue
        if from_name in result:
            result[from_name][from_port] = (to_name, to_port)
        if to_name in result:
            result[to_name][to_port] = (from_name, from_port)
    return result


def _wired_ipv4(engine):
    for port in engine.findall('.//PORT'):
        if 'copper' in (_text(port.find('TYPE')) or '').lower():
            return _text(port.find('IP'))
    return ''


def _add_connectivity_pdus(snapshot, tests):
    """Add Packet Tracer User-Created PDU tests to the answer network.

    Packet Tracer's Connectivity Test tab is driven by PDU records in the
    answer snapshot's SCENARIOSET. Comparison nodes alone only create labels;
    these records provide the actual source, destination, ICMP type, and
    successful-test condition used by the activity wizard.
    """
    if not tests:
        return
    scenarios = snapshot.find('SCENARIOSET')
    if scenarios is None:
        scenarios = ET.SubElement(snapshot, 'SCENARIOSET')
    scenario = scenarios.find('SCENARIO')
    if scenario is None:
        scenario = ET.SubElement(scenarios, 'SCENARIO')
    for child in list(scenario.findall('PDU')):
        scenario.remove(child)

    devices = {}
    for device in snapshot.findall('./NETWORK/DEVICES/DEVICE'):
        engine = device.find('ENGINE')
        if engine is None:
            continue
        name = _text(engine.find('NAME'))
        ref = _text(engine.find('SAVE_REF_ID'))
        devices[name] = {
            'ref': ref,
            'ip': _wired_ipv4(engine),
        }

    for index, test in enumerate(tests):
        if not isinstance(test, dict):
            continue
        source_name = test.get('source') or ''
        destination_name = test.get('destination') or ''
        source = devices.get(source_name)
        destination = devices.get(destination_name)
        if not source or not destination:
            continue
        pdu = ET.SubElement(scenario, 'PDU')
        ET.SubElement(pdu, 'TYPE', {'patterned': 'no'}).text = '0'
        ET.SubElement(pdu, 'CUSTOM_TYPE')
        ET.SubElement(pdu, 'SOURCE').text = source['ref']
        ET.SubElement(pdu, 'PORT')
        ET.SubElement(pdu, 'DESTINATION', {'device': destination['ref']})
        ET.SubElement(pdu, 'COLOR').text = str(-2167107 if index % 2 == 0 else -5727659)
        ip_header = ET.SubElement(pdu, 'PDU')
        ET.SubElement(ip_header, 'TYPE').text = 'CIpHeader'
        ET.SubElement(ip_header, 'SRCADDR').text = source['ip']
        ET.SubElement(ip_header, 'DSTADDR').text = destination['ip']
        ET.SubElement(ip_header, 'PROTOCOL')
        ET.SubElement(ip_header, 'TTL').text = '255'
        icmp = ET.SubElement(ip_header, 'PDU')
        ET.SubElement(icmp, 'TYPE').text = 'CIcmpMessage'
        ET.SubElement(icmp, 'ICMPTYPE').text = '8'
        ET.SubElement(icmp, 'CODE').text = '0'
        ET.SubElement(icmp, 'ID').text = '0'
        ET.SubElement(icmp, 'SEQ').text = str(index)
        ET.SubElement(icmp, 'CHK').text = '0'
        ET.SubElement(ip_header, 'TOS').text = '0'
        ET.SubElement(pdu, 'TEST_CONDITION').text = '3'
        ET.SubElement(pdu, 'POINTS').text = '1'
        ET.SubElement(pdu, 'PDU_SIZE').text = '0'
        ET.SubElement(pdu, 'START').text = '0'


def _router_assessment(prototype, engine, connections=None, checks=None):
    checks = set(checks or DEFAULT_ASSESSMENT_CHECKS)
    device_node = _clone(prototype)
    _prune_children(device_node)
    _select_node(device_node)
    for name in ('Device Model', 'Power'):
        child = _clone_node(prototype, name)
        if child is not None:
            if name == 'Power' and 'power' in checks:
                _select_node(child)
            device_node.append(child)

    interfaces, routes, task_lines = _router_targets(engine)
    ports_prototype = _named_node(prototype, 'Ports')
    if ports_prototype is not None:
        ports = _clone(ports_prototype)
        _prune_children(ports)
        if checks.intersection({'links', 'port-up', 'ip', 'subnet'}):
            _select_node(ports)
        for interface_name, values in interfaces.items():
            interface = _named_node(ports_prototype, interface_name)
            if interface is None:
                continue
            interface_copy = _clone(interface)
            _prune_children(interface_copy)
            if checks.intersection({'links', 'port-up', 'ip', 'subnet'}):
                _select_node(interface_copy)
            link = None
            if connections and interface_name in connections:
                peer_name, peer_port = connections[interface_name]
                link = next((candidate for candidate in interface.findall('NODE')
                             if _text(candidate.find('NAME')).startswith('Link to ')), None)
                if link is not None:
                    link = _clone(link)
                    link_name = link.find('NAME')
                    link_name.text = f'Link to {peer_name}'
                    link_name.set('nodeValue', '')
                    if 'links' in checks:
                        _select_node(link)
                    connects = next((candidate for candidate in link.findall('NODE')
                                     if _text(candidate.find('NAME')).startswith('Connects to ')), None)
                    if connects is not None:
                        connects_name = connects.find('NAME')
                        connects_name.text = f'Connects to {peer_port}'
                        connects_name.set('nodeValue', f'Connects to {peer_port}')
                        if 'links' in checks:
                            _select_node(connects)
                    interface_copy.append(link)
            leaf_name = 'Port Up' if _named_node(interface, 'Port Up') is not None else 'Port Status'
            for leaf_name in (leaf_name, 'IP Address', 'Subnet Mask'):
                leaf = _clone_node(interface, leaf_name)
                if leaf is None:
                    continue
                expected = {
                    'Port Up': '1' if values['up'] else '0',
                    'Port Status': '1' if values['up'] else '0',
                    'IP Address': values['ip'],
                    'Subnet Mask': values['mask'],
                }[leaf_name]
                _set_node_value(leaf, expected)
                if {
                    'Port Up': 'port-up',
                    'Port Status': 'port-up',
                    'IP Address': 'ip',
                    'Subnet Mask': 'subnet',
                }[leaf_name] in checks:
                    _select_node(leaf)
                interface_copy.append(leaf)
            ports.append(interface_copy)
        device_node.append(ports)

    config_prototype = _named_node(prototype, 'IOS Configuration')
    if config_prototype is not None:
        config = _clone(config_prototype)
        _replace_config_lines(config, task_lines)
        device_node.append(config)

    routes_prototype = _named_node(prototype, 'Routes')
    if routes_prototype is not None:
        routes_node = _clone(routes_prototype)
        _prune_children(routes_node)
        if 'routes' in checks:
            _select_node(routes_node)
        static_route = _named_node(routes_prototype, 'Static Routes')
        if static_route is not None:
            route_leaf = _clone(static_route)
            # Keep this visible as a native routing assessment item; the
            # exact route is also graded through the IOS task lines above.
            route_leaf.find('NAME').text = 'Static Routes'
            _set_node_value(route_leaf, '1' if routes else '0')
            if 'routes' in checks:
                _select_node(route_leaf)
            points = route_leaf.find('POINTS')
            if points is not None:
                points.text = '1'
            routes_node.append(route_leaf)
        device_node.append(routes_node)
    return device_node


def _pc_assessment(prototype, engine, checks=None):
    checks = set(checks or DEFAULT_ASSESSMENT_CHECKS)
    device_node = _clone(prototype)
    _prune_children(device_node)
    _select_node(device_node)
    for name in ('Device Model', 'Power'):
        child = _clone_node(prototype, name)
        if child is not None:
            if name == 'Power' and 'power' in checks:
                _select_node(child)
            device_node.append(child)
    port = next((p for p in engine.findall('.//PORT')
                 if 'copper' in (_text(p.find('TYPE')) or '').lower()), None)
    ports_prototype = _named_node(prototype, 'Ports')
    if port is None or ports_prototype is None:
        return device_node
    ports = _clone(ports_prototype)
    _prune_children(ports)
    if checks.intersection({'port-up', 'ip', 'subnet'}):
        _select_node(ports)
    fastethernet = _named_node(ports_prototype, 'FastEthernet0')
    if fastethernet is not None:
        fastethernet_copy = _clone(fastethernet)
        _prune_children(fastethernet_copy)
        if checks.intersection({'port-up', 'ip', 'subnet'}):
            _select_node(fastethernet_copy)
        for leaf_name, tag in (
            ('Port Up', 'POWER'),
            ('IP Address', 'IP'),
            ('Subnet Mask', 'SUBNET'),
        ):
            leaf = _clone_node(fastethernet, leaf_name)
            if leaf is None:
                continue
            expected = _text(port.find(tag))
            if tag == 'POWER':
                expected = '1' if expected.lower() == 'true' else '0'
            _set_node_value(leaf, expected)
            if {
                'Port Up': 'port-up',
                'IP Address': 'ip',
                'Subnet Mask': 'subnet',
            }[leaf_name] in checks:
                _select_node(leaf)
            fastethernet_copy.append(leaf)
        ports.append(fastethernet_copy)
    device_node.append(ports)
    gateway = _clone_node(prototype, 'Default Gateway')
    if gateway is not None:
        _set_node_value(gateway, _text(port.find('PORT_GATEWAY')))
        if 'gateway' in checks:
            _select_node(gateway)
        device_node.append(gateway)
    return device_node


def _build_pc_assessment(engine):
    """Build the Packet Tracer comparison nodes for a wired PC address."""
    port = None
    for candidate in engine.findall('.//PORT'):
        port_type = (candidate.findtext('TYPE') or '').lower()
        if 'copper' in port_type or 'fastethernet' in port_type:
            port = candidate
            break
    if port is None:
        return []

    nodes = []
    gateway = _text(port.find('PORT_GATEWAY'))
    if gateway:
        nodes.append(_node_element(
            'Default Gateway', 'Default Gateway', head=False, node_value=gateway,
            components='Ip', points='1', check_type='0', eclass='0',
        ))

    ports_node = _node_element('Ports', 'Ports')
    port_node = _node_element('FastEthernet0', 'FastEthernet0')
    for tag, label in (
        ('IP', 'IP Address'),
        ('SUBNET', 'Subnet Mask'),
    ):
        value = _text(port.find(tag))
        if not value:
            continue
        port_node.append(_node_element(
            label, label, head=False, node_value=value,
            components='Ip', points='1', check_type='0', eclass='0',
        ))
    ports_node.append(port_node)
    nodes.append(ports_node)
    return nodes


def _build_comparisons(snapshot, template_comparisons=None,
                       include_user_note=False, connectivity_tests=None,
                       assessment_checks=None):
    root = ET.Element('COMPARISONS')
    assessment_checks = set(assessment_checks or DEFAULT_ASSESSMENT_CHECKS)
    # Packet Tracer uses checkType=1 for the assessment root.  Leaving the
    # root at the generic unchecked value makes the wizard render the child
    # tree, but the activity evaluator treats it as a plain Network item and
    # does not enumerate the selected device leaves at assessment time.
    network = _node_element('Network', 'Network', check_type='1')
    template_network = template_comparisons.find('NODE') if template_comparisons is not None else None
    if template_network is not None:
        # These are native Packet Tracer assessment branches. Copying their
        # node attributes is important: a hand-built Network tree is shown as
        # an empty container by Packet Tracer 9.
        for generic_name in ('Instruction', 'Resource', 'ConnectivityTests', 'CodeTesting'):
            generic = _clone_node(template_network, generic_name)
            if generic is None:
                continue
            if generic_name == 'Instruction' and include_user_note:
                user_note = _named_node(generic, 'User Note')
                if user_note is not None:
                    _select_node(user_note)
            if generic_name == 'ConnectivityTests':
                _prune_children(generic)
                for index, test in enumerate(connectivity_tests or []):
                    if isinstance(test, dict):
                        label = test.get('name') or f'Connectivity test {index + 1}'
                    else:
                        label = str(test)
                    leaf = _node_element(label, str(index), head=False,
                                         node_value='1', components='Other', points='1')
                    generic.append(leaf)
            network.append(generic)

    prototypes = []
    if template_network is not None:
        prototypes = template_network.findall('NODE')
    connections = _connection_map(snapshot)
    for info in _device_summary(snapshot):
        device = next(
            (candidate for candidate in snapshot.findall('./NETWORK/DEVICES/DEVICE')
             if _text(candidate.find('ENGINE/NAME')) == info['name']),
            None,
        )
        engine = device.find('ENGINE') if device is not None else None
        prototype = None
        for candidate in prototypes:
            model_node = _named_node(candidate, 'Device Model')
            if model_node is not None and _text(model_node.find('NAME')) == info['model']:
                prototype = candidate
                break
        if prototype is None:
            prototype = next((candidate for candidate in prototypes
                              if info['device_type'].lower() in _text(candidate.find('NAME')).lower()), None)
        if engine is not None and prototype is not None:
            if info['device_type'].lower().startswith('router'):
                device_node = _router_assessment(
                    prototype, engine, connections=connections.get(info['name'], {}),
                    checks=assessment_checks,
                )
            elif info['device_type'].lower().startswith('pc'):
                device_node = _pc_assessment(prototype, engine, checks=assessment_checks)
            else:
                device_node = _clone(prototype)
                _prune_children(device_node)
                for name in ('Device Model', 'Power'):
                    child = _clone_node(prototype, name)
                    if child is not None:
                        device_node.append(child)
        else:
            device_node = _node_element(info['name'], info['name'], translate=True)
            device_node.append(_node_element(
                'Device Model', 'Device Model', head=False, node_value=info['model'], points='1'
            ))
            device_node.append(_node_element(
                'Power', 'Power', head=False, eclass='4', components='Physical',
                node_value='1' if info['power'].lower() == 'true' else '0', points='1'
            ))
        name_element = device_node.find('NAME')
        if name_element is not None:
            name_element.text = info['name']
        id_element = device_node.find('ID')
        if id_element is not None:
            id_element.text = info['name']
        model_node = _named_node(device_node, 'Device Model')
        if model_node is not None:
            _set_node_value(model_node, info['model'])
        network.append(device_node)
    root.append(network)
    return root


def _markdown_to_html(markdown_text, title=''):
    """Convert the small Markdown subset used by generated instructions."""
    if not markdown_text:
        return '<html><body></body></html>'
    if re.search(r'<\s*(html|!doctype|body|h[1-6]|p|ul|ol)\b', markdown_text, re.I):
        return markdown_text

    lines = markdown_text.replace('\r\n', '\n').split('\n')
    output = ['<!DOCTYPE html><html><head><meta charset="utf-8">'
              '<meta name="viewport" content="width=device-width, initial-scale=1.0">']
    if title:
        output.append(f'<title>{html.escape(title)}</title>')
    output.append('</head><body>')
    in_list = None
    paragraph = []

    def close_paragraph():
        nonlocal paragraph
        if paragraph:
            value = ' '.join(paragraph)
            value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
            value = re.sub(r'`(.+?)`', r'<code>\1</code>', value)
            output.append(f'<p>{value}</p>')
            paragraph = []

    def close_list():
        nonlocal in_list
        if in_list:
            output.append(f'</{in_list}>')
            in_list = None

    for raw in lines:
        line = raw.strip()
        if not line:
            close_paragraph()
            continue
        heading = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading:
            close_paragraph(); close_list()
            level = len(heading.group(1))
            output.append(f'<h{level}>{heading.group(2)}</h{level}>')
            continue
        item = re.match(r'^[-*]\s+(.+)$', line)
        if item:
            close_paragraph()
            if in_list != 'ul':
                close_list(); output.append('<ul>'); in_list = 'ul'
            output.append(f'<li>{item.group(1)}</li>')
            continue
        numbered = re.match(r'^\d+[.)]\s+(.+)$', line)
        if numbered:
            close_paragraph()
            if in_list != 'ol':
                close_list(); output.append('<ol>'); in_list = 'ol'
            output.append(f'<li>{numbered.group(1)}</li>')
            continue
        close_list()
        paragraph.append(line)
    close_paragraph(); close_list()
    output.append('</body></html>')
    return '\n'.join(output)


def _set_instruction_pages(activity_root, pages, title='Packet Tracer Activity', layout='tabs'):
    if layout not in {'tabs', 'pages'}:
        raise ValueError("instruction layout must be 'tabs' or 'pages'.")
    if title:
        for scenario_name in activity_root.findall('.//SCENARIOSET/SCENARIO/NAME'):
            scenario_name.text = title
    activity = activity_root.find('ACTIVITY')
    if activity is None:
        activity = ET.SubElement(activity_root, 'ACTIVITY', {
            'COUNTDOWNLEFT': '0', 'COUNTDOWNMS': '0', 'COUNTDOWN_EXPIRED': '0',
            'ELAPSED': '0', 'ENABLED': 'no', 'FORWARD_ANS_SIM_MS': '0',
            'PASS': '', 'TIMERTYPE': '0',
        })
    instructions = activity.find('INSTRUCTIONS')
    if instructions is None:
        instructions = ET.SubElement(activity, 'INSTRUCTIONS', {'enable_tab': 'false', 'layout': '0'})
    else:
        instructions.clear()
        instructions.attrib.update({
            'enable_tab': 'true' if layout == 'tabs' and len(pages) > 1 else 'false',
            'layout': '0',
        })
    for index, page in enumerate(pages, start=1):
        page_element = ET.SubElement(instructions, 'PAGE', {
            'tabify': '1' if layout == 'tabs' and len(pages) > 1 else '0',
            'title': page.get('title') or (f'Page {index}' if len(pages) > 1 else ''),
            'translate': 'true',
        })
        page_element.text = _markdown_to_html(page.get('content', ''), title=title)


def _clear_passwords(activity_root):
    # These are activity/multiuser passwords.  Configuration lines inside the
    # three snapshots are intentionally left intact because they are lab data.
    for parent_path, tag in [
        ('SCRIPT_MODULE', 'PASSWORD'),
        ('OPTIONS', 'PASS'),
        ('OPTIONS/MULTIUSER', 'MU_PASSWORD'),
    ]:
        parent = activity_root.find(parent_path)
        if parent is not None:
            element = parent.find(tag)
            if element is not None:
                element.text = ''
    _set_text(activity_root, 'USER_PROFILE_LOCKED', 'false')
    _set_text(activity_root, 'USER_PROFILE_NOGUEST', 'false')


def assemble_activity(base_xml_path, template_path, output_xml_path, pages,
                      initial_configs_path=None, title='Packet Tracer Activity',
                      initial_state='blank', instruction_layout='tabs',
                      include_user_note=False, connectivity_tests=None,
                      answer_xml_path=None, assessment_checks=None):
    """Assemble an activity XML from a generated normal Packet Tracer XML."""
    base_root = ET.parse(base_xml_path).getroot()
    if base_root.tag != 'PACKETTRACER5':
        raise ValueError(f'{base_xml_path} is not a normal Packet Tracer XML file.')
    answer_root = base_root
    if answer_xml_path:
        answer_root = ET.parse(answer_xml_path).getroot()
        if answer_root.tag != 'PACKETTRACER5':
            raise ValueError(f'{answer_xml_path} is not a normal Packet Tracer XML file.')
    activity_tree = ET.parse(template_path)
    activity_root = activity_tree.getroot()
    if activity_root.tag != 'PACKETTRACER5_ACTIVITY':
        raise ValueError(f'{template_path} is not a Packet Tracer activity XML file.')

    version = answer_root.findtext('VERSION') or base_root.findtext('VERSION') or activity_root.findtext('VERSION')
    if version:
        _set_text(activity_root, 'VERSION', version)

    snapshots = activity_root.findall('PACKETTRACER5')
    while len(snapshots) < 3:
        activity_root.append(_clone(base_root))
        snapshots = activity_root.findall('PACKETTRACER5')
    for snapshot in snapshots[:3]:
        activity_root.remove(snapshot)

    initial = _clone(base_root)
    working = _clone(base_root)
    answer = _clone(answer_root)
    if initial_state not in {'blank', 'generated'}:
        raise ValueError("initial_state must be 'blank' or 'generated'.")
    if initial_state == 'blank':
        _clear_initial_configs(initial)
        _clear_initial_configs(working)
    initial_configs = _load_initial_configs(initial_configs_path)
    _apply_initial_configs(initial, initial_configs)
    _apply_initial_configs(working, initial_configs)
    _add_connectivity_pdus(answer, connectivity_tests)
    # Insert in Packet Tracer's conventional order: initial, working, answer.
    insert_at = 1
    for snapshot in (initial, working, answer):
        activity_root.insert(insert_at, snapshot)
        insert_at += 1

    old_comparisons = activity_root.find('COMPARISONS')
    if old_comparisons is not None:
        activity_root.remove(old_comparisons)
    activity_root.insert(insert_at, _build_comparisons(
        answer,
        template_comparisons=old_comparisons,
        include_user_note=include_user_note,
        connectivity_tests=connectivity_tests,
        assessment_checks=assessment_checks,
    ))
    insert_at += 1
    old_setup = activity_root.find('INITIALSETUP')
    if old_setup is not None:
        activity_root.remove(old_setup)
    activity_root.insert(insert_at, _build_initial_setup(initial))

    _set_instruction_pages(activity_root, pages, title=title, layout=instruction_layout)
    _clear_passwords(activity_root)
    author = activity_root.find('AUTHOR')
    if author is not None:
        author.text = 'Generated by Packet Tracer Lab Generator'

    ET.indent(activity_tree, space=' ')
    activity_tree.write(output_xml_path, encoding='utf-8', xml_declaration=False, short_empty_elements=False)


def default_template_path(base_dir):
    for filename in (
        os.path.join('templates', 'activities', 'activity-lab.xml'),
        os.path.join('templates', 'activities', 'subnetting_activity.xml'),
        # Backward compatibility with the old flat layout.
        'activity-lab.xml',
        'subnetting_activity.xml',
    ):
        candidate = os.path.join(base_dir, filename)
        if os.path.exists(candidate):
            return candidate
    return None
