import matplotlib.pyplot as plt
import numpy as np
import sharpy.utils.settings as settings
from sharpy.utils.solver_interface import solver, BaseSolver, initialise_solver
import sharpy.utils.h5utils as h5
import sharpy.solvers.modal as modal
import sharpy.utils.cout_utils as cout
import pandas as pd

@solver
class AsymptoticStability(BaseSolver):
    """
    Calculates the asymptotic stability properties of aeroelastic systems by creating linearised systems and computing
    the corresponding eigenvalues

    Todo:
        Better integration of the linear system settings (create a loader and check that the system has not been
        previously assembled.

    Warnings:
        Currently under development. Support offered for clamped structures only.

    """
    solver_id = 'AsymptoticStability'

    def __init__(self):
        self.settings_types = dict()
        self.settings_default = dict()

        self.settings_types['print_info'] = 'bool'
        self.settings_default['print_info'] = False

        self.settings_default['sys_id'] = ''
        self.settings_types['sys_id'] = 'str'

        self.settings_types['frequency_cutoff'] = 'float'
        self.settings_default['frequency_cutoff'] = 100

        self.settings_types['export_eigenvalues'] = 'bool'
        self.settings_default['export_eigenvalues'] = True

        self.settings_types['num_evals'] = 'int'
        self.settings_default['num_evals'] = 200

        self.settings_types['postprocessors'] = 'list(str)'
        self.settings_default['postprocessors'] = list()

        self.settings_types['postprocessors_settings'] = 'dict'
        self.settings_default['postprocessors_settings'] = dict()

        self.settings = None
        self.data = None

        self.eigenvalues = None
        self.eigenvectors = None
        self.frequency_cutoff = np.inf

        self.postprocessors = dict()
        self.with_postprocessors = False

    def initialise(self, data, custom_settings=None):
        self.data = data

        if custom_settings is None:
            self.settings = data.settings[self.solver_id]
        else:
            self.settings = custom_settings

        settings.to_custom_types(self.settings, self.settings_types, self.settings_default)

        # Initialise postproc
        # initialise postprocessors
        self.postprocessors = dict()
        if len(self.settings['postprocessors']) > 0:
            self.with_postprocessors = True
        for postproc in self.settings['postprocessors']:
            self.postprocessors[postproc] = initialise_solver(postproc)
            self.postprocessors[postproc].initialise(
                self.data, self.settings['postprocessors_settings'][postproc])

    def run(self):
        """
        Assembles a linearised system in discrete-time state-space form and computes the eigenvalues

        Returns:
            eigenvalues (np.ndarray): Eigenvalues sorted and frequency truncated
            eigenvectors (np.ndarray): Corresponding mode shapes

        """
        try:
            self.frequency_cutoff = self.settings['frequency_cutoff'].value
        except AttributeError:
            self.frequency_cutoff = float(self.settings['frequency_cutoff'])

        if self.frequency_cutoff == 0:
            self.frequency_cutoff = np.inf

        # try:
        #     self.dt = self.settings['LinearUvlm']['dt'].value
        # except AttributeError:
        #     self.dt = float(self.settings['LinearUvlm']['dt'])
        #
        # # Assemble linear system
        # self.aeroelastic = LinAeroEla(self.data, self.settings)
        # self.aeroelastic.assemble_ss()

        sys_id = self.settings.get('sys_id')
        ss = self.data.linear.lsys[sys_id].ss

        # Calculate eigenvectors and eigenvalues of the full system
        eigenvalues, eigenvectors = np.linalg.eig(ss.A)

        # Convert DT eigenvalues into CT
        if ss.dt:
            eigenvalues = np.log(eigenvalues) / ss.dt

        self.eigenvalues, self.eigenvectors = self.sort_eigenvalues(eigenvalues, eigenvectors, self.frequency_cutoff)

        if self.settings['export_eigenvalues'].value:
            self.export_eigenvalues(self.settings['num_evals'].value)
        if self.settings['print_info'].value:
            mode_shape_list = []
            self.print_eigenvalues()
            self.display_root_locus()



        if self.with_postprocessors:
            for mode in range(10):
                gamma, gamma_dot, gamma_star, struct = self.reconstruct_mode(mode)
                mode_shape = {'gamma': gamma,
                              'gamma_star': gamma_star,
                              'gamma_dot': gamma_dot,
                              'struct': struct}
                mode_shape_list.append(mode_shape)

                modal_tstep = self.data.aero.timestep_info[-1].copy()
                dummy_struct = self.data.structure.timestep_info[-1].copy()
                modal_tstep.gamma = gamma
                modal_tstep.gamma_star = gamma_star
                modal_tstep.gamma_dot = gamma_dot
                self.data.aero.timestep_info.append(modal_tstep)
                self.data.structure.timestep_info.append(dummy_struct)
                # run postprocessors
                if self.with_postprocessors:
                    for postproc in self.postprocessors:
                        self.data = self.postprocessors[postproc].run(online=True)

        self.data.linear.stability = dict()
        self.data.linear.stability['eigenvectors'] = self.eigenvectors
        self.data.linear.stability['eigenvalues'] = self.eigenvalues
        # self.data.linear.stability.mode_shapes = mode_shape_list

        return self.data

    def export_eigenvalues(self, num_evals):
        evec_pd = pd.DataFrame(data=self.eigenvectors[:, :num_evals])
        eval_pd = pd.DataFrame(data=self.eigenvalues)
        evec_pd.to_csv(self.data.settings['SHARPy']['route'] + '/output/eigenvectors.csv')
        eval_pd.to_csv(self.data.settings['SHARPy']['route'] + '/output/eigenvalues.csv')


    def print_eigenvalues(self, keep_sys_id=''):
        """

        Returns:

        """
        cout.cout_wrap('Dynamical System Eigenvalues')
        if keep_sys_id == 'LinearBeam':
            uvlm_states = self.data.linear.lsys['LinearCustom'].lsys['LinearUVLM'].ss.states
            cout.cout_wrap('Structural Eigenvalues only')
        else:
            uvlm_states = 0

        for eval in range(len(self.eigenvalues)):
            if np.argmax(np.abs(self.eigenvectors[:, eval])) >= uvlm_states:
                cout.cout_wrap("\t%2d: %.3f + %.3fj" %(eval, self.eigenvalues[eval].real, self.eigenvalues[eval].imag))

    def display_root_locus(self):
        """
        Displays root locus diagrams.

        Returns the ``fig`` and ``ax`` handles for further editing.

        Returns:
            fig:
            ax:
        """

        # Title
        fig, ax = plt.subplots()

        ax.scatter(np.real(self.eigenvalues), np.imag(self.eigenvalues),
                   s=6,
                   color='k',
                   marker='s')
        ax.set_xlabel('Real, $\mathbb{R}(\lambda_i)$ [rad/s]')
        ax.set_ylabel('Imag, $\mathbb{I}(\lambda_i)$ [rad/s]')
        # ax.set_ylim([0, self.frequency_cutoff])
        ax.grid(True)
        ax.set_ylim(-10,10)
        ax.set_xlim(-10,1)
        fig.show()

        return fig, ax

    def plot_modes(self, n_modes_to_plot, start=0):
        """
        Plot the aeroelastic mode shapes for the first n_modes_to_plot

        Todo:
            Export to paraview format

        Returns:

        """

        n_aero_states = self.aeroelastic.linuvlm.Nx
        n_struct_states = self.aeroelastic.lingebm_str.U.shape[1]

        for mode_plot in range(start, start + n_modes_to_plot):
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            mode_shape = self.eigenvectors[n_aero_states:n_aero_states+n_struct_states, mode_plot]
            mode_shape = modal.scale_mode(self.data, mode_shape)
            zeta_mode = modal.get_mode_zeta(self.data, mode_shape)
            mode_frequency = np.imag(self.eigenvalues[mode_plot])

            for i_surf in range(len(zeta_mode)):
                # Plot mode
                ax.plot_wireframe(zeta_mode[i_surf][0], zeta_mode[i_surf][1], zeta_mode[i_surf][2])

                # Plot original shape
                ax.plot_wireframe(self.data.aero.timestep_info[-1].zeta[i_surf][0],
                                  self.data.aero.timestep_info[-1].zeta[i_surf][1],
                                  self.data.aero.timestep_info[-1].zeta[i_surf][2],
                                  color='k',
                                  alpha=0.5)

            ax.set_title('Mode %g, Frequency %.2f' %(mode_plot+1, mode_frequency))
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            fig.show()

    def reconstruct_mode(self, eig):
        sys_id = self.settings.get('sys_id')
        uvlm = self.data.linear.lsys[sys_id].lsys['LinearUVLM']

        # for eig in range(10):
        x_n = self.eigenvectors[:uvlm.ss.states, eig]
        forces, gamma, gamma_dot, gamma_star = uvlm.unpack_ss_vector(self.data, x_n, self.data.linear.tsaero0)
        struct_vec = self.eigenvectors[uvlm.ss.states:, eig]
            # df = pd.DataFrame(data=[gamma, gamma_star, gamma_m1]).T
            # df.to_csv(self.data.settings['SHARPy']['route'] + '/output/aero_evecs_%04d.csv' % eig)
        return gamma, gamma_dot, gamma_star, struct_vec

    @staticmethod
    def sort_eigenvalues(eigenvalues, eigenvectors, frequency_cutoff=None):
        """
        Sort continuous-time eigenvalues.

        The conjugate of complex eigenvalues is removed, then if specified, high frequency modes are truncated.
        Finally, the eigenvalues are sorted by largest to smallest real part.

        Args:
            eigenvalues (np.ndarray): Continuous-time eigenvalues
            eigenvectors (np.ndarray): Corresponding right eigenvectors
            frequency_cutoff (float): Cutoff frequency for truncation ``[rad/s]``

        Returns:

        """

        if frequency_cutoff == 0:
            frequency_cutoff = np.inf

        # Remove poles in the negative imaginary plane (Im(\lambda)<0)
        criteria_a = np.imag(eigenvalues) <= frequency_cutoff
        # criteria_b = np.imag(eigenvalues) > -1e-2
        eigenvalues_truncated = eigenvalues[criteria_a].copy()
        eigenvectors_truncated = eigenvectors[:, criteria_a].copy()

        order = np.argsort(np.abs(eigenvalues_truncated))

        return eigenvalues_truncated[order], eigenvectors_truncated[:, order]

if __name__ == '__main__':
    u_inf = 140
    try:
        data = h5.readh5('/home/ng213/code/sharpy/tests/linear/goland_wing/cases/output/goland_u%04g.data.h5' %u_inf).data
    except FileNotFoundError:
        raise FileNotFoundError('Unable to find test case')


    integr_order = 2
    predictor = True
    sparse = False

    aeroelastic_settings = {'LinearUvlm':{
        'dt': data.settings['LinearUvlm']['dt'],
        'integr_order': integr_order,
        'density': 1.020,
        'remove_predictor': predictor,
        'use_sparse': sparse,
        'ScalingDict': {'length': 1,
                        'speed': 1,
                        'density': 1},
        'rigid_body_motion': False},
        'frequency_cutoff': 0,
        'export_eigenvalues': True,
    }

    analysis = AsymptoticStability()

    analysis.initialise(data, aeroelastic_settings)
    eigenvalues, eigenvectors = analysis.run()

    fig, ax = analysis.display_root_locus()

    # analysis.plot_modes(10)