import os
import argparse
import os
import random
import sys

import scenarios
import activity


def _ensure_parent(path):
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)


def main():
    epilog = """Examples:
  # List scenarios and topics
  python main.py --list
  python main.py --list-topics

  # Generate a single scenario
  python main.py --scenario ospf_validation --output generated/ospf_lab.xml

  # Generate multiple scenarios (composite topology)
  python main.py --scenario nat_pat --scenario ntp_syslog --size large

  # Pick one scenario per topic
  python main.py --topics nat,acl,ipv6 --output generated/mixed_topics.xml

  # Add random scenarios with a seed for repeatability
  python main.py --random 3 --seed 1234 --output generated/random_lab.xml

  # Use a JSON recipe file
  python main.py --recipe recipes/ccna_mix.json --output generated/recipe_lab.xml

  # Write objectives to a custom path and skip PKT export
  python main.py --scenario qos_policy --instructions-output generated/qos.md --skip-pkt

  # Create a Packet Tracer activity (PKA) as well as the normal PKT
  python main.py --scenario ospf_validation --activity-output generated/ospf_activity.pka

  # Use several instruction pages and override the learner's starting configs
  python main.py --scenario ospf_validation --activity-output generated/ospf.pka \
      --activity-page instructions/overview.md --activity-page instructions/tasks.md \
      --activity-initial-configs examples/activity_initial.example.json

  # Add native assessment branches for connectivity and an optional user note
  python main.py --scenario exercise_1 --activity-output generated/exercise_1.pka \
      --activity-connectivity-test PC1,PC2 --activity-connectivity-test PC2,PC1 \
      --activity-user-note

  # Use an already-configured PKT as the hidden answer network
  python main.py --scenario exercise_1 --activity-output generated/exercise_1.pka \
      --activity-answer-input generated/exercise_1_answer.pkt

  # Select only particular answer-network properties for grading
  python main.py --scenario exercise_1 --activity-output generated/exercise_1.pka \
      --activity-check ip --activity-check subnet --activity-check gateway \
      --activity-check port-up --activity-check routes

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
    parser.add_argument('--activity-output', '--pka-output', dest='activity_output',
                        help='Destination Packet Tracer Activity (PKA) path.')
    parser.add_argument('--activity-xml-output',
                        help='Optional decoded activity XML path (useful for inspection/version control).')
    parser.add_argument('--activity-template',
                        help='Decoded PKA XML template. Defaults under templates/activities/.')
    parser.add_argument('--activity-page', action='append', dest='activity_pages',
                        help='Instruction page source (Markdown or HTML); repeat for multiple pages.')
    parser.add_argument('--activity-initial-configs',
                        help='JSON mapping device names (or * ) to initial running/startup configs.')
    parser.add_argument('--activity-initial-state', choices=['blank', 'generated'], default='blank',
                        help='Activity learner state: blank configs (default) or generated configs.')
    parser.add_argument('--activity-layout', choices=['tabs', 'pages'], default='tabs',
                        help='Instruction presentation: tabbed pages (default) or sequential pages.')
    parser.add_argument('--activity-user-note', action='store_true',
                        help='Include the native User Note assessment item.')
    parser.add_argument('--activity-connectivity-test', action='append', dest='activity_connectivity_tests',
                        metavar='SOURCE,TARGET',
                        help='Add a connectivity assessment item; repeat for multiple tests.')
    parser.add_argument('--activity-check', action='append', dest='activity_checks',
                        metavar='ITEM',
                        help=('Select answer-network checks; repeatable or comma-separated: '
                              'power, links, port-up, ip, subnet, gateway, routes.'))
    parser.add_argument('--answer-output',
                        help='Optional fully configured answer PKT output.')
    parser.add_argument('--activity-answer-input', '--answer-network', dest='activity_answer_input',
                        help='Existing configured answer .pkt or normal .xml to use as the activity answer network.')
    parser.add_argument('--activity-title', default='Generated Packet Tracer Activity',
                        help='Title shown in the Packet Tracer activity window.')
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
        and not args.activity_output and not args.answer_output
        and not args.activity_answer_input
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
    _ensure_parent(args.output)
    lab.to_packettracer_xml(args.output)

    answer_xml_input = None
    if args.activity_answer_input:
        answer_input = os.path.abspath(args.activity_answer_input)
        if not os.path.exists(answer_input):
            parser.error(f'Answer network does not exist: {answer_input}')
        if answer_input.lower().endswith('.xml'):
            answer_xml_input = answer_input
        else:
            answer_base = args.activity_output or args.output
            answer_root, _ = os.path.splitext(answer_base)
            answer_xml_input = f'{answer_root}_answer_source.xml'
            _ensure_parent(answer_xml_input)
            try:
                scenarios.decode_pkt(answer_input, answer_xml_input, legacy=args.legacy_pkt)
            except Exception as exc:
                raise RuntimeError(f'Failed to decode answer network: {exc}') from exc

    need_objectives = not args.no_instructions or args.print_instructions or bool(args.activity_output)
    objectives_text = ''
    if need_objectives:
        objectives_text = scenarios.render_objectives_markdown(instances, warnings=warnings, rng=rng)
        if not args.no_instructions:
            destination = args.instructions_output or scenarios.derive_objectives_path(args.output)
            _ensure_parent(destination)
            with open(destination, 'w', encoding='utf-8') as handle:
                handle.write(objectives_text)
            print(f'Lab objectives written to {destination}')
        if args.print_instructions:
            print('\n' + objectives_text)

    if not args.skip_pkt:
        pkt_destination = args.pkt_output or scenarios.derive_pkt_path(args.output)
        _ensure_parent(pkt_destination)
        try:
            scenarios.encode_pkt(args.output, pkt_destination, legacy=args.legacy_pkt)
        except Exception as exc:
            raise RuntimeError(f'Failed to encode PKT via ptexplorer.py: {exc}') from exc

    if args.answer_output:
        _ensure_parent(args.answer_output)
        try:
            scenarios.encode_pkt(answer_xml_input or args.output, args.answer_output, legacy=args.legacy_pkt)
        except Exception as exc:
            raise RuntimeError(f'Failed to encode answer PKT via ptexplorer.py: {exc}') from exc

    if args.activity_output:
        _ensure_parent(args.activity_output)
        template_path = args.activity_template or activity.default_template_path(os.path.dirname(os.path.abspath(__file__)))
        if not template_path:
            raise RuntimeError(
                'No activity template found. Provide --activity-template with decoded PKA XML '
                '(for example, templates/activities/activity-lab.xml).'
            )
        if not os.path.exists(template_path):
            raise RuntimeError(f'Activity template does not exist: {template_path}')

        page_specs = []
        for page_path in args.activity_pages or []:
            with open(page_path, 'r', encoding='utf-8') as handle:
                page_title = os.path.splitext(os.path.basename(page_path))[0]
                page_title = page_title.lstrip('0123456789-_ ').replace('_', ' ').replace('-', ' ').strip()
                page_title = ' '.join(page_title.split()).title() or 'Instructions'
                page_specs.append({
                    'title': page_title,
                    'content': handle.read(),
                })
        if not page_specs:
            page_specs.append({
                'title': 'Instructions',
                'content': objectives_text or note_text,
            })

        activity_xml_path = args.activity_xml_output
        if not activity_xml_path:
            activity_root, _ = os.path.splitext(args.activity_output)
            activity_xml_path = f'{activity_root}.xml'
        _ensure_parent(activity_xml_path)
        activity.assemble_activity(
            args.output,
            template_path,
            activity_xml_path,
            page_specs,
            initial_configs_path=args.activity_initial_configs,
            title=args.activity_title,
            initial_state=args.activity_initial_state,
            instruction_layout=args.activity_layout,
            include_user_note=args.activity_user_note,
            connectivity_tests=[
                {
                    'name': f'{raw.split(",", 1)[0].strip()} -> {raw.split(",", 1)[1].strip()} ping',
                    'source': raw.split(',', 1)[0].strip(),
                    'destination': raw.split(',', 1)[1].strip(),
                }
                if ',' in raw else {'name': raw}
                for raw in (args.activity_connectivity_tests or [])
            ],
            answer_xml_path=answer_xml_input,
            assessment_checks=(
                [item.strip().lower() for raw in (args.activity_checks or []) for item in raw.split(',') if item.strip()]
                or None
            ),
        )
        try:
            scenarios.encode_activity(activity_xml_path, args.activity_output, legacy=args.legacy_pkt)
        except Exception as exc:
            raise RuntimeError(f'Failed to encode PKA via ptexplorer.py: {exc}') from exc


if __name__ == '__main__':
    main()
