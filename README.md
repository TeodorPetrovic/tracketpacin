# tracketpacin

Dynamic, randomized Cisco Packet Tracer lab generator for CCNA study. Every run produces a unique `.pkt` file with fresh IP addressing, VLAN IDs, topology variants, and objectives, so you never practice the same lab twice.

I put this together in a few hours while studying for my CCNA. It's not polished and there will be rough edges. The generated instructions or objectives might occasionally contradict each other or not line up perfectly with the topology. If something looks off, it probably is. It can also be a good sign that your studies are working. PRs welcome, or just fix it and keep labbing.


---

## Features

- **16 scenario types** covering core CCNA topics: VLANs, DHCP, OSPF, NAT/PAT, ACLs, STP, EtherChannel, IPv6, QoS, port security, static routing, NTP/syslog, SNMP, FHRP, and more
- **Randomized parameters** — subnets, VLAN IDs, loopbacks, FHRP groups, and topology variants change on every generation
- **Composite labs** — combine multiple topics into a single integrated topology
- **Objectives & instructions** — each lab comes with a Markdown file of objectives tailored to the generated addressing
- **Interactive TUI** — menu-driven mode for browsing and selecting scenarios without memorizing CLI flags
- **Topic-based selection** — pick scenarios by CCNA topic (e.g. `--topics nat,ospf,acl`)
- **Direct `.pkt` output** — generates Packet Tracer binary files using Twofish EAX encryption (modern format)

## Requirements

- **Python 3.10+**
- **Cisco Packet Tracer** (to open generated `.pkt` files)
- A Twofish implementation for PKT encoding (auto-installed if missing):
  - `twofish`, `pycryptodome`, or `twofish-py`

## Quick Start

```bash
# Clone the repo
git clone https://github.com/alexsvobo/tracketpacin.git
cd tracketpacin

# Launch interactive mode (no arguments needed)
python main.py

# Or generate a lab directly
python main.py --scenario ospf_validation
```

## Usage

### Interactive Mode

Run with no arguments or use the `-i` flag to launch the interactive menu:

```bash
python main.py
python main.py -i
```

The TUI lets you browse all scenarios, pick by topic, generate random selections, configure output settings, and build — all without touching CLI flags.

### CLI Mode

```bash
# List all available scenarios
python main.py --list

# List available CCNA topics
python main.py --list-topics

# Generate a single scenario
python main.py -s ospf_validation -o ospf_lab.xml

# Generate multiple scenarios as a composite topology
python main.py -s nat_pat -s ntp_syslog --size large

# Pick one scenario per topic
python main.py --topics nat,acl,ipv6 -o mixed_topics.xml

# Random scenarios with a seed for repeatability
python main.py -r 3 --seed 1234 -o random_lab.xml
```

### CLI Flags

| Flag | Description |
|------|-------------|
| `-s`, `--scenario` | Scenario to include (repeatable) |
| `-r`, `--random N` | Add N random non-repeating scenarios |
| `--seed` | Seed for reproducible randomization |
| `-o`, `--output` | Output XML path (PKT derived automatically) |
| `--topics` | Select by CCNA topic (comma-separated or repeatable) |
| `--size` | Topology size: `small`, `medium`, `large` |
| `--pkt-output` | Custom PKT output path |
| `--skip-pkt` | Skip PKT encoding (XML only) |
| `--legacy-pkt` | Use legacy encoding (pre-PT 7.3 compatibility) |
| `--no-instructions` | Skip writing objectives markdown |
| `--print-instructions` | Print objectives to stdout |
| `--list` | List scenarios and exit |
| `--list-topics` | List topics and exit |
| `-i`, `--interactive` | Launch interactive menu |

## Available Scenarios

| Scenario | Topics | Description |
|----------|--------|-------------|
| `redundant_access` | VLAN, DHCP, FHRP, Switching | Resilient access pod with multiple topology variants |
| `branch_single_vlan` | VLAN, DHCP, Switching | Single-VLAN branch office |
| `ospf_validation` | OSPF, Routing | OSPF adjacency and SPF tuning |
| `dual_core_distribution` | VLAN, FHRP, Switching, Redundancy | Dual-core campus with failover |
| `campus_branch_wan` | WAN, Routing, DHCP | Campus-to-branch WAN connectivity |
| `nat_static_dynamic` | NAT, Routing | Static + dynamic NAT with pool |
| `nat_pat` | NAT, Routing | PAT / overload NAT |
| `ntp_syslog` | NTP, Syslog, Management | Centralized time and logging |
| `snmp_monitoring` | SNMP, Management | SNMP polling and traps |
| `qos_policy` | QoS, Switching | Voice/video traffic prioritization |
| `port_security` | Port Security, Switching | Sticky MAC and violation handling |
| `portfast_bpduguard` | STP, PortFast, BPDU Guard | Access port hardening |
| `static_routing` | Static Routing, WAN | Static routes across a WAN |
| `etherchannel_lacp` | EtherChannel, Switching, Redundancy | LACP port-channel bundling |
| `acl_filtering` | ACL, Security, Routing | Standard/extended ACL filtering |
| `ipv6_basics` | IPv6, Routing | IPv6 addressing and SLAAC |

## Project Structure

```
tracketpacin/
├── main.py            # CLI entry point
├── interactive.py     # Interactive TUI mode
├── core.py            # Lab class — device/link management, XML generation
├── scenarios.py       # Scenario library, parameter generators, builders
├── layouts.py         # Topology layout functions for each scenario variant
├── profiles.py        # Device configuration profiles (startup configs)
├── ptexplorer.py      # PKT/PKA ↔ XML encoder/decoder
├── lab_model.py       # Backward-compatibility wrapper
├── test.xml           # Packet Tracer XML template (device cloning source)
└── examples/          # Sample PT labs used as additional template sources
```

## How It Works

1. **Scenario selection** — pick scenarios by name, topic, or random draw
2. **Parameter generation** — each scenario randomizes IPs, VLANs, loopbacks, and topology variants
3. **Topology building** — devices and links are placed into a `Lab` object with logical positions
4. **XML export** — devices are cloned from `test.xml` templates to produce valid Packet Tracer XML
5. **PKT encoding** — the XML is compressed and encrypted into a `.pkt` binary using Twofish EAX (via `ptexplorer.py`)
6. **Objectives** — a Markdown file is generated with step-by-step build instructions tailored to the generated addressing

## Any enjoyment of this project is owed to

- [axcheron/ptexplorer](https://github.com/axcheron/ptexplorer) — original PKT/PKA encoder/decoder
- [prathamps](https://github.com/prathamps) — updated ptexplorer to support modern Packet Tracer files (Twofish EAX)
- [David Bombal](https://davidbombal.com/) — CCNA teachings and lab inspiration
- [Jeremy's IT Lab](https://www.jeremysitlab.com/) — CCNA course material and lab foundations
- [tracketpacer](https://www.tracketpacer.com/) — the namesake
- [Cisco Systems](https://www.cisco.com/)
## License

MIT



