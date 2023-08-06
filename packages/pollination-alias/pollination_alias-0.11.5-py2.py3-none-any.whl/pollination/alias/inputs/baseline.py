from pollination_dsl.alias import InputAlias


"""Alias for ASHRAE Climate Zone inputs."""
climate_zone_input = [
    InputAlias.str(
        name='climate_zone',
        description='Text indicating the ASHRAE climate zone. This can be a single '
        'integer (in which case it is interpreted as A) or it can include the '
        'A, B, or C qualifier (eg. 3C). The "LB Import STAT" component can '
        'typically be used to get the ASHRAE climate zone for a given TMY '
        'weather location. Otherwise, global maps of ASHRAE climate zones '
        'are published in the latest ASHRAE 90.1 standard.',
        platform=['grasshopper']
    )
]


"""Alias for Building Type input."""
building_type_input = [
    InputAlias.str(
        name='building_type',
        description='Text for the building type that the Model represents. This '
        'is used to determine the baseline window-to-wall ratio and HVAC system. '
        'The "HB Building Programs" component provides a full list of '
        'building programs that this recipe can accept.',
        platform=['grasshopper']
    )
]


"""Alias for Energy Cost input."""
energy_costs_input = [
    InputAlias.str(
        name='energy_costs',
        description='A text string of energy cost parameters to customize the cost '
        'assumptions used to calculate the Performance Cost Index (PCI). '
        'Each cost value should be per kWh of energy use, whether that is '
        'electricity, natural-gas, etc. Cost values can be in any currency '
        'as long as it is consistent across the energy sources. The default '
        'values are in USD $/kWh and represent an average across the USA. '
        'Note that not all of the energy sources need to be specified for '
        'this input to be valid. For example, if the input model contains '
        'no district heating or cooling, something like the following would '
        'be acceptable: --electricity-cost 0.24 --natural-gas-cost 0.08. '
        '(Default: --electricity-cost 0.15 --natural-gas-cost 0.06 '
        '--district-cooling-cost 0.04 --district-heating-cost 0.08)',
        default='--electricity-cost 0.15 --natural-gas-cost 0.06 '
        '--district-cooling-cost 0.04 --district-heating-cost 0.08',
        platform=['grasshopper']
    )
]
