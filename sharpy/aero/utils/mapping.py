import numpy as np
import sharpy.utils.algebra as algebra


def aero2struct_force_mapping(aero_forces,
                              struct2aero_mapping,
                              zeta,
                              pos_def,
                              psi_def,
                              master,
                              conn,
                              cag=np.eye(3)):

    n_node, _ = pos_def.shape
    n_elem, _, _ = psi_def.shape
    struct_forces = np.zeros((n_node, 6))

    nodes = []

    for i_elem in range(n_elem):
        for i_local_node in range(3):

            i_global_node = conn[i_elem, i_local_node]
            if i_global_node in nodes:
                continue

            nodes.append(i_global_node)
            for mapping in struct2aero_mapping[i_global_node]:
                i_surf = mapping['i_surf']
                i_n = mapping['i_n']
                _, n_m, _ = aero_forces[i_surf].shape

                # i_master_elem, master_elem_local_node = master[i_global_node, :]

                crv = psi_def[i_elem, i_local_node, :]
                cab = algebra.crv2rotation(crv)
                cbg = np.dot(cab.T, cag)

                for i_m in range(n_m):
                    chi_g = zeta[i_surf][:, i_m, i_n] - np.dot(cag.T, pos_def[i_global_node, :])
                    struct_forces[i_global_node, 0:3] += np.dot(cbg, aero_forces[i_surf][0:3, i_m, i_n])
                    struct_forces[i_global_node, 3:6] += np.dot(cbg, aero_forces[i_surf][3:6, i_m, i_n])
                    struct_forces[i_global_node, 3:6] += np.dot(cbg, np.cross(chi_g, aero_forces[i_surf][0:3, i_m, i_n]))

    # for i_global_node in range(n_node):
        # for mapping in struct2aero_mapping[i_global_node]:
            # i_surf = mapping['i_surf']
            # i_n = mapping['i_n']
            # _, n_m, _ = aero_forces[i_surf].shape

            # i_master_elem, master_elem_local_node = master[i_global_node, :]

            # crv = psi_def[i_master_elem, master_elem_local_node, :]
            # cab = algebra.crv2rotation(crv)
            # cbg = np.dot(cab.T, cag)

            # for i_m in range(n_m):
                # chi_g = zeta[i_surf][:, i_m, i_n] - np.dot(cag.T, pos_def[i_global_node, :])
                # struct_forces[i_global_node, 0:3] += np.dot(cbg, aero_forces[i_surf][0:3, i_m, i_n])
                # struct_forces[i_global_node, 3:6] += np.dot(cbg, aero_forces[i_surf][3:6, i_m, i_n])
                # struct_forces[i_global_node, 3:6] += np.dot(cbg, np.cross(chi_g, aero_forces[i_surf][0:3, i_m, i_n]))
    return struct_forces
