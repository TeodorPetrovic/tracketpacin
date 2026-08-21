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
- **Activity `.pka` output** — wraps the generated topology in a PT 9 activity with starting/working/answer snapshots, no activity password, and instructions pages

## Requirements

- **Python 3.10+**
- **Cisco Packet Tracer** (to open generated `.pkt` files)
- Packet Tracer templates under `templates/packettracer/`. The included
  `emptysavefile.xml` is a Packet Tracer 9.0 base document and `test.xml`
  contains switch and PC templates; if generation
  reports `No templates available for router`, create a local source once:

  ```bash
  python ptexplorer.py -d "C:\\Program Files\\Cisco Packet Tracer 9.0.0\\saves\\01 Networking\\8200\\8200.pkt" templates/packettracer/router_8200_source.xml
  python ptexplorer.py -d "C:\\Program Files\\Cisco Packet Tracer 9.0.0\\saves\\01 Networking\\DNS\\Multilevel_DNS.pkt" templates/packettracer/server_source.xml
  ```

  The 8200 source is important because the layouts use three-part router
  interfaces such as `GigabitEthernet0/0/0`. Any local file ending in
  `_source.xml` or `_template.xml` under `templates/packettracer/` is
  discovered automatically. Adjust the Packet Tracer version/path as needed.
- A Twofish implementation for PKT encoding (auto-installed if missing):
  - `twofish`, `pycryptodome`, or `twofish-py`

## Quick Start

```bash
# Clone the repo
git clone https://github.com/alexsvobo/tracketpacin.git
cd tracketpacin

# Launch interactive mode (no arguments needed)
python main.py

# Or generate a lab directly; outputs go under generated/
python main.py --scenario ospf_validation

# Generate a normal PKT and a Packet Tracer Activity with an answer PKT
python main.py --scenario ospf_validation \
  --activity-output generated/ospf_activity.pka \
  --answer-output generated/ospf_activity_answer.pkt
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

# Generate a single scenario (XML, PKT, and objectives go under generated/)
python main.py -s ospf_validation -o generated/ospf_lab.xml

# Generate multiple scenarios as a composite topology
python main.py -s nat_pat -s ntp_syslog --size large

# Pick one scenario per topic
python main.py --topics nat,acl,ipv6 -o mixed_topics.xml

# Random scenarios with a seed for repeatability
python main.py -r 3 --seed 1234 -o generated/random_lab.xml

# Add two instruction pages to an activity
python main.py -s ospf_validation --activity-output generated/ospf.pka \
  --activity-page instructions/overview.md \
  --activity-page instructions/tasks.md \
  --activity-initial-configs examples/activity_initial.example.json
```

To build an activity from an already-configured answer PKT, use the PKT as the
answer network. The answer snapshot and assessment values are then taken from
that file:

```bash
python main.py -s exercise_1 \
  --activity-answer-input generated/exercise_1_answer.pkt \
  --activity-output generated/exercise_1_from_answer.pka \
  --activity-check ip --activity-check subnet --activity-check gateway \
  --activity-check port-up --activity-check links --activity-check routes
```

Available `--activity-check` values are `power`, `links`, `port-up`, `ip`,
`subnet`, `gateway`, and `routes`. If omitted, the default activity selection
checks all of those categories. This mirrors the checked assessment-tree
items in Packet Tracer's Activity Wizard.

### Packet Tracer Activities

The activity exporter uses a decoded `.pka` XML file as its PT-version-specific
wrapper. The supplied templates live under `templates/activities/`; the
`activity-lab.xml` template is selected automatically. Pass
`--activity-template templates/activities/subnetting_activity.xml` to use the
supplied E5 activity structure instead. The generated activity XML is written
beside the `.pka` so it can be inspected or decoded again.

The normal generated topology becomes the answer snapshot. Snapshots 0 and 1
are the learner's initial and working state. By default, device configuration
is blank in the learner state, so a new activity starts at 0% rather than 100%.
The generated assessment includes native device, interface, PC, route, and IOS
configuration items. Initial device configurations can be
overridden by a JSON file keyed by device name; `*` applies to every device:

```json
{
  "*": {"clear_startup_config": true},
  "EdgeRouter": {
    "running_config": "!\nversion 15.4\n!\nhostname EdgeRouter\n!\nend",
    "startup_config": ""
  }
}
```

Use it with:

```bash
python main.py -s ospf_validation \
  --activity-output generated/ospf.pka \
  --activity-initial-configs examples/activity_initial.example.json
```

`--activity-page` accepts Markdown or HTML and can be repeated to create
multiple instruction tabs/pages. When more than one page is supplied,
Packet Tracer's instruction tab bar is enabled by default. Use
`--activity-layout pages` for sequential instruction pages instead. The answer
snapshot is included in the activity, and `--answer-output` can also write it
as a separate fully configured `.pkt`. Activity and multiuser passwords are
cleared by the exporter.

Assessment branches are built from Packet Tracer's native device node schema,
so they appear as expandable assessment items rather than an empty Network
container. Router interfaces include IP address, subnet mask, and port status;
PCs include IP address, subnet mask, default gateway, and port status; router
task lines and static routes are also included. Connectivity tests are written
as answer-network ICMP PDU records, so they appear in Packet Tracer's
Connectivity Test tab. Add them with repeatable
`--activity-connectivity-test SOURCE,TARGET`. Add the
optional native User Note item with `--activity-user-note`.

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
| `--activity-output`, `--pka-output` | Write a Packet Tracer Activity (`.pka`) |
| `--activity-template` | Select a decoded `.pka` XML wrapper template |
| `--activity-answer-input`, `--answer-network` | Existing configured answer `.pkt` or normal `.xml` |
| `--activity-page FILE` | Add an instruction page; repeatable, Markdown or HTML |
| `--activity-layout` | `tabs` (default) or sequential `pages` |
| `--activity-connectivity-test SOURCE,TARGET` | Add a connectivity assessment item; repeatable |
| `--activity-check ITEM` | Select answer-tree categories; repeatable or comma-separated |
| `--activity-user-note` | Include the optional User Note assessment item |
| `--activity-initial-configs FILE` | JSON overrides for starting running/startup configs |
| `--activity-initial-state` | `blank` (default) or `generated` learner configs |
| `--activity-xml-output` | Choose the decoded activity XML path |
| `--answer-output` | Optional fully configured answer `.pkt` |
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
| `exercise_1` | Static Routing, Routing | Two routers, two PCs, separate LANs, and static routes |
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
├── activity.py        # Packet Tracer Activity wrapper and instruction pages
├── lab_model.py       # Backward-compatibility wrapper
├── templates/
│   ├── packettracer/  # PT base files and device/source templates
│   └── activities/    # Supplied .pka files and decoded activity templates
├── examples/          # Small user-editable config examples
├── generated/         # Normal generated labs and answer files
└── tests/artifacts/   # Diagnostic, round-trip, and compatibility outputs
```

## How It Works

1. **Scenario selection** — pick scenarios by name, topic, or random draw
2. **Parameter generation** — each scenario randomizes IPs, VLANs, loopbacks, and topology variants
3. **Topology building** — devices and links are placed into a `Lab` object with logical positions
4. **XML export** — devices are cloned from `templates/packettracer/` templates to produce valid Packet Tracer XML
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



