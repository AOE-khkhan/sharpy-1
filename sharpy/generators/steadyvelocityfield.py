import numpy as np

import sharpy.utils.generator_interface as generator_interface
import sharpy.utils.settings as settings


@generator_interface.generator
class SteadyVelocityField(generator_interface.BaseGenerator):
    """
    Steady Velocity Field Generator

    ``SteadyVelocityField`` class inherited from ``BaseGenerator``

    The object creates a steady velocity field with the velocity and flow direction specified by the user.

    To call this generator, the ``generator_id = SteadyVelocityField`` shall be used.
    This is parsed as the value for the ``velocity_field_generator`` key in the desired aerodynamic solver's settings.

    Args:
        in_dict (dict): Input data in the form of dictionary. See acceptable entries in the Notes below.

    Attributes:
        settings_types (dict): Acceptable data types of the input data
        settings_default (dict): Default values for input data should the user not provide them
        u_inf (float): Free stream velocity selection
        u_inf_direction (list(float)): ``x``, ``y`` and ``z`` relative contributions to the free stream velocity

    Notes:
        Acceptable key-value pairs for the input dictionary, which is parsed as the value to the
        ``velocity_field_input`` key in the settings of the desired aerodynamic solver.

        ===================  ===============  ======================================================================  ===================
        Name                 Type             Description                                                             Default
        ===================  ===============  ======================================================================  ===================
        ``u_inf``            ``float``        Free stream velocity magnitude                                          ``0``
        ``u_inf_direction``  ``list(float)``  ``x``, ``y`` and ``z`` relative components of the free stream velocity  ``[1.0, 0.0, 0.0]``
        ===================  ===============  ======================================================================  ===================

    See Also:
        .. py:class:: sharpy.utils.generator_interface.BaseGenerator

    """
    generator_id = 'SteadyVelocityField'

    def __init__(self):
        self.in_dict = dict()
        self.settings_types = dict()
        self.settings_default = dict()

        self.settings_types['u_inf'] = 'float'
        self.settings_default['u_inf'] = None

        self.settings_types['u_inf_direction'] = 'list(float)'
        self.settings_default['u_inf_direction'] = np.array([1.0, 0, 0])

        self.u_inf = 0.
        self.u_inf_direction = None

    def initialise(self, in_dict):
        self.in_dict = in_dict
        settings.to_custom_types(self.in_dict, self.settings_types, self.settings_default)

        self.u_inf = self.in_dict['u_inf']
        self.u_inf_direction = self.in_dict['u_inf_direction']

    def generate(self, params, uext):
        zeta = params['zeta']
        override = params['override']
        for i_surf in range(len(zeta)):
            if override:
                uext[i_surf].fill(0.0)
            for i in range(zeta[i_surf].shape[1]):
                for j in range(zeta[i_surf].shape[2]):
                    uext[i_surf][:, i, j] += self.u_inf*self.u_inf_direction
