from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for electricity emissions inputs that can accept a Location."""
electricity_emissions_input = [
    InputAlias.any(
        name='elec_emissions',
        description='Either a ladybug Location object in the USA, which will be '
        'used to determine the subregion of the electrical grid or a number '
        'for the electric grid carbon emissions in kg CO2/MWh. The following '
        'rules of thumb may be used as a guide. (Default: 400).\n'
        '800 kg/MWh - for an inefficient coal or oil-dominated grid\n'
        '400 kg/MWh - for the US (energy mixed) grid around 2020\n'
        '100-200 kg/MWh - for grids with majority renewable/nuclear composition\n'
        '0-100 kg/MWh - for grids with nuclear or renewables and storage',
        default=400,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.emissions',
                function='location_to_electricity_emissions'
            )
        ]
    )
]
