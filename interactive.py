"""
Interactive terminal UI for Packet Tracer lab generation.

Launch with:  python main.py -i   OR   python main.py --interactive
"""

import os
import random
import shutil
import sys

import scenarios

# ── ANSI helpers ──────────────────────────────────────────────────────────────

_COLOR_SUPPORT = None


def _has_color():
    global _COLOR_SUPPORT
    if _COLOR_SUPPORT is None:
        if os.environ.get('NO_COLOR'):
            _COLOR_SUPPORT = False
        elif sys.platform == 'win32':
            _COLOR_SUPPORT = os.environ.get('WT_SESSION') or os.environ.get('TERM_PROGRAM') or True
        else:
            _COLOR_SUPPORT = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return bool(_COLOR_SUPPORT)


def _ansi(code, text):
    if _has_color():
        return f'\033[{code}m{text}\033[0m'
    return text


def _bold(text):    return _ansi('1', text)
def _dim(text):     return _ansi('2', text)
def _cyan(text):    return _ansi('36', text)
def _green(text):   return _ansi('32', text)
def _yellow(text):  return _ansi('33', text)
def _red(text):     return _ansi('31', text)
def _magenta(text): return _ansi('35', text)


# ── Drawing helpers ───────────────────────────────────────────────────────────

def _term_width():
    return shutil.get_terminal_size((80, 24)).columns


def _banner():
    w = min(_term_width(), 60)
    title = 'Packet Tracer Lab Generator'
    pad = max(0, w - len(title) - 4)
    left = pad // 2
    right = pad - left
    lines = [
        _cyan('╔' + '═' * (w - 2) + '╗'),
        _cyan('║') + ' ' * left + _bold(title) + ' ' * right + _cyan('║'),
        _cyan('╚' + '═' * (w - 2) + '╝'),
    ]
    return '\n'.join(lines)


def _header(text):
    return '\n' + _bold(_cyan(f'─── {text} ───'))


def _menu_item(number, label, description=''):
    num_str = _bold(_cyan(f'  [{number}]'))
    if description:
        return f'{num_str} {label}  {_dim(description)}'
    return f'{num_str} {label}'


def _success(text): print(_green(f'  ✓ {text}'))
def _warn(text):    print(_yellow(f'  ⚠ {text}'))
def _error(text):   print(_red(f'  ✗ {text}'))
def _info(text):    print(f'  {_dim(text)}')


def _prompt(text, default=None):
    if default is not None:
        display = f'{text} [{_cyan(str(default))}]: '
    else:
        display = f'{text}: '
    try:
        value = input(display).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    return value if value else (str(default) if default is not None else '')


def _prompt_int(text, default=None, valid_range=None):
    while True:
        raw = _prompt(text, default)
        if raw is None:
            return None
        try:
            val = int(raw)
        except ValueError:
            _error(f'Enter a number.')
            continue
        if valid_range and val not in valid_range:
            _error(f'Choose between {valid_range.start} and {valid_range.stop - 1}.')
            continue
        return val


def _confirm(text, default=True):
    hint = 'Y/n' if default else 'y/N'
    raw = _prompt(f'{text} ({hint})', '')
    if raw is None:
        return False
    if not raw:
        return default
    return raw.lower().startswith('y')


def _clear():
    if sys.platform == 'win32':
        os.system('cls')
    else:
        os.system('clear')


# ── Scenario listing ──────────────────────────────────────────────────────────

def _scenario_entries():
    """Return list of (key, meta) excluding the composite placeholder."""
    return [(k, v) for k, v in scenarios.SCENARIO_LIBRARY.items() if k not in scenarios._INTERNAL_SCENARIOS]


def _print_scenario_table(entries, selected_keys=None):
    selected_keys = selected_keys or set()
    for i, (key, meta) in enumerate(entries, 1):
        tags = ', '.join(meta.get('tags', []))
        marker = _green('●') if key in selected_keys else _dim('○')
        num = _bold(f'{i:>3}')
        name = _cyan(key)
        desc = meta.get('title', '')
        tag_str = _dim(f'({tags})') if tags else ''
        print(f'  {marker} {num}  {name:<28s} {desc}  {tag_str}')


def _print_topic_table():
    topic_map = scenarios._list_topics()
    for topic, scen_names in sorted(topic_map.items()):
        names = ', '.join(sorted(scen_names))
        print(f'  {_cyan(topic):<24s} {_dim(names)}')


# ── Screens ───────────────────────────────────────────────────────────────────

def _screen_pick_scenarios(entries, selected):
    """Allow user to toggle scenarios by number.  Returns updated set."""
    selected = set(selected)
    while True:
        print(_header('Select Scenarios'))
        _print_scenario_table(entries, selected)
        print()
        _info('Enter numbers separated by commas to toggle, or:')
        _info(f'{_cyan("a")}=select all  {_cyan("n")}=clear all  {_cyan("d")}=done  {_cyan("q")}=cancel')
        raw = _prompt('Toggle #')
        if raw is None or raw.lower() == 'q':
            return None
        if raw.lower() == 'd':
            return selected
        if raw.lower() == 'a':
            selected = {k for k, _ in entries}
            continue
        if raw.lower() == 'n':
            selected.clear()
            continue
        for part in raw.replace(' ', ',').split(','):
            part = part.strip()
            if not part:
                continue
            try:
                idx = int(part) - 1
                if 0 <= idx < len(entries):
                    key = entries[idx][0]
                    if key in selected:
                        selected.discard(key)
                    else:
                        selected.add(key)
                else:
                    _error(f'{part} is out of range.')
            except ValueError:
                # Maybe they typed a scenario name
                norm = scenarios.normalize_scenario_key(part)
                if norm in scenarios.SCENARIO_LIBRARY:
                    if norm in selected:
                        selected.discard(norm)
                    else:
                        selected.add(norm)
                else:
                    _error(f'Unknown: {part}')
    return selected


def _screen_pick_by_topic(entries):
    """Let user type topics and get auto-selected scenarios."""
    print(_header('Available Topics'))
    _print_topic_table()
    print()
    raw = _prompt('Enter topics (comma-separated)')
    if not raw:
        return set()
    parts = [t.strip().lower().replace(' ', '_') for t in raw.split(',') if t.strip()]
    rng = random.Random()
    try:
        picks = scenarios._pick_topic_scenarios(rng, parts, set())
    except ValueError as exc:
        _error(str(exc))
        return set()
    print()
    for p in picks:
        _success(f'{p}')
    return set(picks)


def _screen_random():
    """Pick N random scenarios."""
    count = _prompt_int('How many random scenarios?', default=3, valid_range=range(1, 18))
    if count is None:
        return set()
    rng = random.Random()
    try:
        picks = scenarios._pick_random_scenarios(rng, set(), scenarios.RandomScenarioRequest(count=count),
                                                 composite_compatible_only=count > 1)
    except ValueError as exc:
        _error(str(exc))
        return set()
    print()
    for p in picks:
        _success(f'{p}')
    return set(picks)


def _screen_configure(selected_keys, entries):
    """Configure size & output, then generate."""
    ordered = [k for k, _ in entries if k in selected_keys]
    print(_header('Generation Settings'))
    print()
    print(f'  Scenarios: {_cyan(", ".join(ordered))}')
    print()

    # Size
    size = _prompt('Topology size (small/medium/large)', 'medium')
    if size not in ('small', 'medium', 'large'):
        _warn(f'Invalid size "{size}", defaulting to medium.')
        size = 'medium'

    # Output
    default_name = ordered[0] if len(ordered) == 1 else 'generated_lab'
    output_pkt = _prompt('Output .pkt filename', os.path.join('generated', f'{default_name}.pkt'))
    if not output_pkt:
        output_pkt = os.path.join('generated', f'{default_name}.pkt')
    if not output_pkt.lower().endswith('.pkt'):
        output_pkt += '.pkt'

    base, _ = os.path.splitext(output_pkt)
    output_xml = f'{base}.xml'
    output_md = f'{base}_objectives.md'

    # Objectives
    write_objectives = _confirm('Write objectives markdown?', default=True)

    # Legacy PKT
    legacy = False
    if _confirm('Use legacy PKT encoding?', default=False):
        legacy = True

    # Summary
    print(_header('Review'))
    print(f'  Scenarios:   {_cyan(", ".join(ordered))}')
    print(f'  Size:        {_cyan(size)}')
    print(f'  PKT output:  {_cyan(output_pkt)}')
    print(f'  XML output:  {_dim(output_xml)}')
    if write_objectives:
        print(f'  Objectives:  {_cyan(output_md)}')
    if legacy:
        print(f'  Encoding:    {_yellow("legacy")}')
    print()

    if not _confirm('Generate this lab?', default=True):
        return False

    # ── Generate ──────────────────────────────────────────────────────
    print()
    rng = random.Random()

    composite = ordered if len(ordered) > 1 else None
    topics = None
    if composite:
        topic_set = set()
        for k in ordered:
            topic_set.update(t.lower() for t in scenarios.SCENARIO_LIBRARY.get(k, {}).get('topics', []))
        topics = sorted(topic_set)

    try:
        lab, instances = scenarios.build_lab_from_scenarios(
            ordered, rng,
            composite_scenarios=composite,
            composite_topics=topics,
            composite_size=size,
        )
    except Exception as exc:
        _error(f'Build failed: {exc}')
        return False

    warnings = scenarios.validate_lab(lab)
    note_text = scenarios.render_note_text(instances, rng=rng)
    lab.set_instruction_note_text(note_text)

    try:
        output_dir = os.path.dirname(os.path.abspath(output_xml))
        os.makedirs(output_dir, exist_ok=True)
        lab.to_packettracer_xml(output_xml)
        _success(f'XML  → {output_xml}')
    except Exception as exc:
        _error(f'XML export failed: {exc}')
        return False

    try:
        scenarios.encode_pkt(output_xml, output_pkt, legacy=legacy)
        _success(f'PKT  → {output_pkt}')
    except Exception as exc:
        _error(f'PKT encoding failed: {exc}')

    if write_objectives:
        try:
            objectives = scenarios.render_objectives_markdown(instances, warnings=warnings, rng=rng)
            with open(output_md, 'w', encoding='utf-8') as f:
                f.write(objectives)
            _success(f'Docs → {output_md}')
        except Exception as exc:
            _error(f'Objectives failed: {exc}')

    if warnings:
        print()
        for w in warnings:
            _warn(w)

    return True


# ── Main loop ─────────────────────────────────────────────────────────────────

def run():
    """Main interactive loop."""
    _clear()
    print(_banner())
    print()

    entries = _scenario_entries()
    selected = set()

    while True:
        # Show current selection if any
        if selected:
            ordered = [k for k, _ in entries if k in selected]
            print(f'\n  Selected: {_green(", ".join(ordered))}')

        print(_header('Main Menu'))
        print(_menu_item(1, 'Browse & pick scenarios'))
        print(_menu_item(2, 'Pick by topic'))
        print(_menu_item(3, 'Random surprise'))
        if selected:
            print(_menu_item(4, _green('Generate lab'), f'{len(selected)} scenario(s) ready'))
            print(_menu_item(5, 'Clear selection'))
        print(_menu_item(0, 'Quit'))
        print()

        choice = _prompt('Choice')
        if choice is None or choice == '0':
            print(_dim('\nBye!\n'))
            return

        if choice == '1':
            result = _screen_pick_scenarios(entries, selected)
            if result is not None:
                selected = result
        elif choice == '2':
            picks = _screen_pick_by_topic(entries)
            if picks:
                selected |= picks
        elif choice == '3':
            picks = _screen_random()
            if picks:
                selected |= picks
        elif choice == '4' and selected:
            if _screen_configure(selected, entries):
                print()
                if not _confirm('Generate another lab?', default=False):
                    print(_dim('\nDone!\n'))
                    return
                selected = set()
        elif choice == '5' and selected:
            selected.clear()
            _success('Selection cleared.')
        else:
            _error('Invalid choice.')
