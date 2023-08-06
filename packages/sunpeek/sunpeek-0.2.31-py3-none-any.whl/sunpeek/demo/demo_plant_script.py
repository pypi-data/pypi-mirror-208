"""
This module holds an example to show the functionality of the SunPeek package and the Performance Check method.

The Python code shows how to configure the plant / collector array, call the Performance Check method (ISO 24194) and
produce some plots. 
This script is based on the FHW / Fernheizwerk plant in Graz, Austria.
The data used here (together with a detailed description) is available at https://zenodo.org/record/7741084

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Marnoch Hamilton-Jones <m.hamilton-jones@aee.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
"""

import json
import warnings
from datetime import datetime
import webbrowser

import sunpeek.demo
from sunpeek.demo.demo_plant import requires_demo_data
import sunpeek.core_methods.pc_method as pc
from sunpeek.common.unit_uncertainty import Q
from sunpeek.common import config_parser
from sunpeek.common.data_uploader import DatetimeTemplates
from sunpeek.components import CollectorTypeQDT, iam_methods
from sunpeek.components import FluidFactory, WPDFluidDefinition, ModelFactory, CoolPropFluid
from sunpeek.definitions.fluid_definitions import get_definition


def get_fluid(fluid_str='FHW'):
    """Return heat transfer fluid: 'FHW' for FHW fluid, other options to see how other fluids would behave.
    """
    if fluid_str == 'FHW':
        # FHW laboratory-tested fluid, with property models trained from csv files
        rho_model = ModelFactory(unit={'te': 'degC', 'out': 'kg m**-3'}).train(sunpeek.demo.DEMO_FLUID_RHO_PATH)
        cp_model = ModelFactory(unit={'te': 'degC', 'out': 'J g**-1 K**-1'}).train(sunpeek.demo.DEMO_FLUID_CP_PATH)
        return FluidFactory(fluid=WPDFluidDefinition('FHW, Pekasolar', rho_model, cp_model))
    # Examples of CoolProp fluids
    elif fluid_str.lower() == 'water':
        return CoolPropFluid(get_definition('water'))
    else:
        fluid = CoolPropFluid(get_definition(fluid_str), concentration=Q(40, 'percent'))

    if fluid is not None:
        return fluid
    else:
        raise ValueError(f'Unknown CoolProp fluid string "{fluid_str}".')


def get_collector():
    """Return collector definition of flat plate collector used in collector array
    """
    return CollectorTypeQDT(name="Arcon 3510",
                            manufacturer_name="Arcon-Sunmark A/S",
                            product_name="HTHEATstore 35/10",
                            licence_number='SP SC0843-14',
                            test_report_id="6P02267-C-Rev 1 (2016-07-06), 4P04266-C-Rev 2 (2015-11-10)",
                            certificate_date_issued=datetime(2016, 7, 14),
                            certificate_lab='SP Technical Research Institute of Sweden',
                            description="Cover: single-glazed & foil. Absorber: harp. Hydraulics: Non-Tichelmann",
                            test_reference_area="gross",
                            area_gr=Q(13.57, "m**2"),
                            gross_width=Q(5973, "mm"),
                            gross_length=Q(2272, "mm"),
                            gross_height=Q(145, "mm"),
                            a1=Q(2.067, "W m**-2 K**-1"),
                            a2=Q(0.009, "W m**-2 K**-2"),
                            a5=Q(7.313, "kJ m**-2 K**-1"),
                            kd=Q(0.93, ""),
                            eta0b=Q(0.745, ""),
                            f_prime=Q(0.95, ""),
                            iam_method=iam_methods.IAM_Interpolated(
                                aoi_reference=Q([10, 20, 30, 40, 50, 60, 70, 80, 90], 'deg'),
                                iam_reference=Q([1, 0.99, 0.97, 0.94, 0.9, 0.82, 0.65, 0.32, 0]))
                            )


if __name__ == '__main__':
    requires_demo_data(None)
    # STEP 1: Make Plant from Config
    with open(sunpeek.demo.DEMO_CONFIG_PATH) as f:
        conf = json.load(f)
    plant = config_parser.make_full_plant(conf=conf)
    # Define collector type
    plant.arrays[0].collector_type = get_collector()
    # Define heat transfer fluid
    plant.fluid_solar = get_fluid()
    # This is just to showcase how other fluids would be used:
    # plant.fluid_solar = get_fluid('water')
    # plant.fluid_solar = get_fluid('ASHRAE, Propylene Glycol')
    # plant.fluid_solar = get_fluid('Antifrogen L')

    # STEP 2: Submit measurement data
    # data = sunpeek.demo.DEMO_DATA_PATH_2DAYS
    data = sunpeek.demo.DEMO_DATA_PATH_1MONTH
    # data = sunpeek.demo.DEMO_DATA_PATH_1YEAR
    data_output = plant.use_csv(data, timezone='UTC', datetime_template=DatetimeTemplates.year_month_day)

    # STEP 3: Run Performance Check method & create plots
    pc_output = pc.PCMethod.create_extended(plant=plant, equation_id=2).run()
    # pc_output = pc.PCMethod.create_iso(plant=plant, equation_id=2).run()

    try:
        pc.plot_all(pc_output)
    except webbrowser.Error:
        warnings.warn('Cannot plot results, no runnable browser detected')
    except ModuleNotFoundError:
        warnings.warn('Cannot plot results, module plotly not installed')
