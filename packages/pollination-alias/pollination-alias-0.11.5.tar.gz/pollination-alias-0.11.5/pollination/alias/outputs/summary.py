from pollination_dsl.alias import OutputAlias
from queenbee.io.common import IOAliasHandler


"""Appendix G Summary output."""
parse_appendix_g_summary = [
    OutputAlias.any(
        name='g_report',
        description='A list of values related to the the PCI improvement for '
        'the latest versions of ASHRAE 90.1. All energy and energy intensity values '
        'are in kWh or kWh/m2. All PCI values are fractional and all '
        '"improvement" values are in percent (from 0 to 100).',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.summary',
                function='json_properties_from_path'
            )
        ]
    )
]


"""LEED v4 Summary output."""
parse_leed_summary = [
    OutputAlias.any(
        name='leed_summary',
        description='A list of values related to LEED "Optimize Energy Performance" '
        'points. This includes ASHRAE 90.1-2016 PCI for both cost and carbon (GHG) '
        'emissions. All energy and energy intensity values are in kWh or kWh/m2. All '
        'carbon emission values are in kg CO2. All PCI values are fractional '
        'and all "improvement" values are in percent (from 0 to 100). LEED points '
        'are reported from 0 to (16, 18, 20) depending on the input building_type.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.summary',
                function='json_properties_from_path'
            )
        ]
    )
]


"""Baseline SQL files."""
load_baseline_sqls = [
    OutputAlias.any(
        name='baseline_sqls',
        description='A List of result SQL files output by the baseline simulations. '
        'There should be one SQL for each of the 4 building orientations.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.summary',
                function='contents_from_folder'
            )
        ]
    )
]
