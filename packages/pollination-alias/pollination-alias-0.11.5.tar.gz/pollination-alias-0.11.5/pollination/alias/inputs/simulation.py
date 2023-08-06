from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler, ItemType


"""Alias for inputs that expect a simulation parameter .json file as the recipe input."""
energy_simulation_parameter_input = [
    InputAlias.any(
        name='sim_par',
        description='A SimulationParameter object that describes all of the setting for '
        'the energy simulation. If None, some default simulation parameters will '
        'automatically be used. This can also be the path to a SimulationParameter '
        'JSON file.',
        optional=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='energy_sim_par_to_json'
            ),
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='HBSimulationParameterToJSON'
            )
        ]
    ),
    # Rhino alias
    InputAlias.linked(
        name='sim_par',
        description='This input links to SimulationParameter setting in Rhino.',
        platform=['rhino'],
        handler=[
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='RhinoSimulationParameterToJSON'
            )
        ]
    )
]


"""Alias for inputs that expect a measures input."""
measures_input = [
    InputAlias.list(
        name='measures',
        items_type=ItemType.Generic,
        description='An optional list of measures to apply to the OpenStudio model '
        'upon export. Use the "HB Load Measure" component to load a measure into '
        'Grasshopper and assign input arguments. Measures can be downloaded from the '
        'NREL Building Components Library (BCL) at (https://bcl.nrel.gov/).',
        default=[],
        optional=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='measures_to_folder'
            )
        ]
    )
]


"""Alias for inputs that expect a IDF string input."""
idf_additional_strings_input = [
    InputAlias.list(
        name='add_str',
        items_type=ItemType.String,
        description='THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS. '
        'An additional text string to be appended to the IDF before '
        'simulation. The input should include complete EnergyPlus objects '
        'following the IDF format. This input can be used to include '
        'EnergyPlus objects that are not currently supported by honeybee.',
        default=[],
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='list_to_additional_strings'
            )
        ]
    )
]


"""Alias for inputs that expect a IDF file input."""
additional_idf_input = [
    InputAlias.list(
        name='add_str',
        items_type=ItemType.String,
        description='THIS OPTION IS JUST FOR ADVANCED USERS OF ENERGYPLUS. '
        'An additional text string to be appended to the IDF before '
        'simulation. The input should include complete EnergyPlus objects '
        'following the IDF format. This input can be used to include '
        'EnergyPlus objects that are not currently supported by honeybee.',
        default=[],
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='list_to_additional_idf'
            )
        ]
    )
]


"""Alias for inputs that expect visualization variables."""
viz_variables_input = [
    InputAlias.list(
        name='viz_vars',
        items_type=ItemType.String,
        description='A list of text for EnergyPlus output variables to be visualized '
        'on the geometry in an output HTML report. If unspecified, no report is '
        'produced. For example, "Zone Air System Sensible Heating Rate".',
        default=[],
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='viz_variables_to_string'
            )
        ]
    )
]


"""Alias for energy standards and building vintages."""
proposed_standard_input = [
    InputAlias.str(
        name='proposed_std',
        description='Text to set the efficiency standard to be used for the proposed '
        'building. When specified, this will automatically override the efficiencies '
        'of all HVAC equipment for the proposed standard. Note that '
        'providing a standard here will cause the OpenStudio translation '
        'process to perform an additional sizing calculation with EnergyPlus, '
        'which is needed since the default efficiencies of equipment vary '
        'depending on their size. The "HB Building Vintages" component has a full '
        'list of supported HVAC efficiency standards. You can also choose  '
        'from the following:DOE_Ref_Pre_1980, DOE_Ref_1980_2004, ASHRAE_2004, '
        'ASHRAE_2007, ASHRAE_2010, ASHRAE_2013, ASHRAE_2016, ASHRAE_2019',
        default='',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.simulation',
                function='standard_to_str'
            )
        ]
    )
]
