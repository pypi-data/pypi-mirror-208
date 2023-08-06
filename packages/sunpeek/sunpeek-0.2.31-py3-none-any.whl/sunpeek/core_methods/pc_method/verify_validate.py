"""Goal of this module is to provide verficiation & validation functionality for the PC method.

Both verification and validation are based on a Plant object. A PCMethod instance is not required.
Both return True/False.

- Verification, verify_config(plant): without data. Checks plant config only.
- Validation, validate_data(plant):
    1. Verify plant configuration (as above)
    2. Validates data (checks if virtual sensors have actually been calculated etc).

# TODO return value unclear yet. Currently both (verify, validate) return True/False. No further information (cause...) 
"""
import enum
# from components.physical import Plant  # circular import
from sunpeek.common.utils import VerifyValidateMode
from sunpeek.core_methods.pc_method import equation as eq


class AvailablePCEquations(enum.IntEnum):
    one = 1
    two = 2


class AvailablePCMethods(str, enum.Enum):
    iso = 'iso'
    extended = 'extended'


def verify_config(plant,
                  equation_id: int,
                  ignore_wind: bool):
    """Verifies if plant configuration (including all components) is ok to run the PC method.

    Parameters
    ----------
    plant : Plant to check
    equation_id : int {1, 2}  Equation1 or Equation2
    ignore_wind : bool
        if True, the wind speed check is omitted.

    Raises
    ------
    AssertionError

    Returns
    -------
    Nothing

    Notes
    -----
    This method only verifies plant _configuration. It does _not_ verify if data is ok for the PC method to run.
    To do that, call validate_data().
    """
    vv = VerifyValidatePCMethod(plant, equation_id, ignore_wind,
                                VerifyValidateMode.verify)
    vv.do_assert()


# def validate_data(plant: Plant,


def validate_data(plant,
                  equation_id: int,
                  ignore_wind: bool):
    """Verifies if plant configuration is ok to run the PC method and all virtual sensors could be calculated.

    Parameters
    ----------
    plant : Plant to check
    equation_id : int {1, 2}  Equation1 or Equation2
    ignore_wind : bool
        if True, the wind speed check is omitted.

    Raises
    ------
    AssertionError

    Returns
    -------
    Nothing
    """
    vv = VerifyValidatePCMethod(plant, equation_id, ignore_wind,
                                VerifyValidateMode.validate)
    vv.do_assert()


class VerifyValidatePCMethod:
    def __init__(self, plant, equation_id, ignore_wind,
                 verify_validate: VerifyValidateMode):
        self.plant = plant

        assert equation_id in [1, 2], \
            f'Invalid value for the "equation_id" parameter: {equation_id}.'
        self.equation = eq.create_eq(equation_id)

        self.ignore_wind = ignore_wind
        self.check_mode = verify_validate

    def do_assert(self):
        """Makes sure plant configuration (including all components, optionally with data) is ok to run the PC method.

        Raises
        ------
        AssertionError

        Returns
        -------
        Nothing
        """
        # Plant
        assert self.plant.arrays, f"Plant {self.plant} has no arrays. To run the PC method, you need to add arrays to the plant."
        plant_ok, problem_slots = self.plant.verify_validate(self.check_mode, 'te_amb', 'tp')
        assert plant_ok, f"Plant {self.plant}: sensors are required to run the PC method but not available: {problem_slots}."
        if not self.ignore_wind:
            plant_ok, problem_slots = self.plant.verify_validate(self.check_mode, 've_wind')
            assert plant_ok, f"Plant {self.plant}: sensors are required to run the PC method but not available: {problem_slots}."
        # Arrays
        for array in self.plant.arrays:
            self.equation.assert_available(array, self.check_mode)
