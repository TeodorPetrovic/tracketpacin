import argparse
import random
import sys

import scenarios


def main():
    epilog = """Examples:
  # List scenarios and topics
  python main.py --list
  python main.py --list-topics

  # Generate a single scenario
  python main.py --scenario ospf_validation --output ospf_lab.xml

  # Generate multiple scenarios (composite topology)
  python main.py --scenario nat_pat --scenario ntp_syslog --size large

  # Pick one scenario per topic
  python main.py --topics nat,acl,ipv6 --output mixed_topics.xml

  # Add random scenarios with a seed for repeatability
  python main.py --random 3 --seed 1234 --output random_lab.xml

  # Use a JSON recipe file
  python main.py --recipe recipes/ccna_mix.json --output recipe_lab.xml

  # Write objectives to a custom path and skip PKT export
  python main.py --scenario qos_policy --instructions-output qos.md --skip-pkt

  # Launch interactive mode (also runs when called with no arguments)
  python main.py -i
"""
    parser = argparse.ArgumentParser(
        description='Generate Packet Tracer labs from modular scenario profiles.',
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('-s', '--scenario', action='append', dest='scenarios', help='Scenario name to include (repeatable).')
    parser.add_argument('-r', '--random', type=int, metavar='N', help='Append N random non-repeating scenarios.')
    parser.add_argument('--seed', type=int, help='Seed for the random scenario picker.')
    parser.add_argument('-o', '--output', default='generated_lab.xml', help='Destination Packet Tracer XML path.')
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
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Launch interactive menu (also activates when no arguments are given).')
    args = parser.parse_args()

    # If no meaningful arguments were given, launch interactive mode
    no_action = (
        not args.scenarios and not args.random and not args.recipe
        and not args.list and not args.list_topics and not args.topics
    )
    if args.interactive or no_action:
        import interactive
        interactive.run()
        return

    if args.list:
        print('Available scenarios:')
        for key, meta in scenarios.SCENARIO_LIBRARY.items():
            if key in scenarios._INTERNAL_SCENARIOS:
                continue
            tags = f" ({', '.join(meta.get('tags', []))})" if meta.get('tags') else ''
            print(f' - {key}{tags}: {meta["description"]}')
        return

    if args.list_topics:
        topic_map = scenarios._list_topics()
        print('Available topics:')
        for topic, scenario_names in sorted(topic_map.items()):
            print(f' - {topic}: {", ".join(sorted(scenario_names))}')
        return

    if args.seed is not None:
        random.seed(args.seed)
    rng = random.Random(args.seed)

    recipe_plan = scenarios.RecipePlan()
    if args.recipe:
        try:
            recipe_plan = scenarios.load_recipe_plan(args.recipe)
        except (OSError, ValueError) as exc:
            parser.error(f'Failed to load recipe: {exc}')

    selected = []
    selected_set = set()

    def _add_selection(key, raw_display=None):
        if key not in scenarios.SCENARIO_LIBRARY:
            display = raw_display or key
            parser.error(f'Unknown scenario: {display}')
        if key not in selected_set:
            selected.append(key)
            selected_set.add(key)

    for recipe_name in recipe_plan.explicit:
        _add_selection(recipe_name)

    if args.scenarios:
        for raw in args.scenarios:
            key = scenarios.normalize_scenario_key(raw)
            _add_selection(key, raw_display=raw)

    topics_requested = []
    composite_topic_picks = []
    if args.topics:
        for entry in args.topics:
            parts = [part.strip() for part in entry.split(',') if part.strip()]
            topics_requested.extend(parts)
    topics_requested = scenarios._normalize_topics(topics_requested)
    if topics_requested:
        try:
            topic_picks = scenarios._pick_topic_scenarios(rng, topics_requested, selected_set)
            for pick in topic_picks:
                _add_selection(pick)
            if len(topics_requested) > 1:
                composite_topic_picks = list(topic_picks)
        except ValueError as exc:
            parser.error(str(exc))

    random_requests = list(recipe_plan.random_requests)
    if args.random:
        random_requests.append(scenarios.RandomScenarioRequest(count=args.random))

    total_expected = len(selected) + sum(r.count for r in random_requests)
    composite_only = total_expected > 1

    try:
        for request in random_requests:
            if request.count <= 0:
                continue
            picks = scenarios._pick_random_scenarios(rng, selected_set, request,
                                                     composite_compatible_only=composite_only)
            for name in picks:
                _add_selection(name)
    except ValueError as exc:
        parser.error(str(exc))

    if not selected:
        parser.error('Specify scenarios via --scenario, --random, or --recipe.')

    lab, instances = scenarios.build_lab_from_scenarios(
        selected,
        rng,
        composite_scenarios=composite_topic_picks or None,
        composite_topics=topics_requested or None,
        composite_size=args.size,
    )
    warnings = scenarios.validate_lab(lab)
    note_text = scenarios.render_note_text(instances, rng=rng)
    lab.set_instruction_note_text(note_text)
    lab.to_packettracer_xml(args.output)

    need_objectives = not args.no_instructions or args.print_instructions
    if need_objectives:
        objectives_text = scenarios.render_objectives_markdown(instances, warnings=warnings, rng=rng)
        if not args.no_instructions:
            destination = args.instructions_output or scenarios.derive_objectives_path(args.output)
            with open(destination, 'w', encoding='utf-8') as handle:
                handle.write(objectives_text)
            print(f'Lab objectives written to {destination}')
        if args.print_instructions:
            print('\n' + objectives_text)

    if not args.skip_pkt:
        pkt_destination = args.pkt_output or scenarios.derive_pkt_path(args.output)
        try:
            scenarios.encode_pkt(args.output, pkt_destination, legacy=args.legacy_pkt)
        except Exception as exc:
            raise RuntimeError(f'Failed to encode PKT via ptexplorer.py: {exc}') from exc


if __name__ == '__main__':
    main()
