import numpy as np
import sympy as sp

from rtb_toolbox.link import Link
from rtb_toolbox.utils import compute_homogeneous_transformation


class ForwardKinematic:
    def __init__(self,
                 links,
        ):

        self.links = links
        self.len_links = len(self.links)

        self.generalized_coordinates = [self.links[i].generalized_coordinate for i in range(self.len_links)]

        self.links_zero_i = np.empty(self.len_links, dtype=Link)

        for i in range(1, self.len_links + 1):
            m = sp.Symbol(f'm_{i}')

            I = sp.Matrix([
                [sp.Symbol(f'I_{i}(xx)'), sp.Symbol(f'I_{i}(xy)'), sp.Symbol(f'I_{i}(xz)')],
                [sp.Symbol(f'I_{i}(xy)'), sp.Symbol(f'I_{i}(yy)'), sp.Symbol(f'I_{i}(yz)')],
                [sp.Symbol(f'I_{i}(xz)'), sp.Symbol(f'I_{i}(yz)'), sp.Symbol(f'I_{i}(zz)')],
            ])

            transformation = self.get_transformation(0, i)
            # I = R @ I @ R.T

            self.links_zero_i[i - 1] = Link(
                generalized_coordinate=self.links[i - 1].dhp[0],
                mass=m,
                transformation_matrix=transformation,
                inertia_tensor=I,
            )

        self.ee_transformation_matrix = self.get_transformation(0, self.len_links)
        self.jacobian = self.get_jacobian()

        self.lambdify_jacobian = sp.lambdify(
            [self.generalized_coordinates],
            self.jacobian,
            modules=['numpy'],
        )

        self.lambdify_ee_transformation_matrix = sp.lambdify(
            [self.generalized_coordinates],
            self.ee_transformation_matrix,
            modules=['numpy'],
        )

        self.lambdify_ee_position = sp.lambdify(
            [self.generalized_coordinates],
            self.ee_transformation_matrix[:3, 3],
            modules=['numpy'],
        )

        self.lambdify_ee_orientation = sp.lambdify(
            [self.generalized_coordinates],
            self.ee_transformation_matrix[:3, :3],
            modules=['numpy'],
        )

    def get_transformation(self, start, end):
        tf = compute_homogeneous_transformation(self.links, start, end)
        return tf

    def get_ee_transformation_matrix(self):
        return self.ee_transformation_matrix

    def compute_jacobian(self, q):
        return self.lambdify_jacobian(q)

    def compute_ee_transformation_matrix(self, q):
        return self.lambdify_ee_transformation_matrix(q)

    def compute_ee_position(self, q):
        return self.lambdify_ee_position(q)

    def compute_ee_orientation(self, q):
        return self.lambdify_ee_orientation(q)

    def get_spacial_jacobian(self):
        return self.jacobian[:3, :]

    def get_rotational_jacobian(self):
        return self.jacobian[3:, :]

    def get_jacobian(self):
        htm = self.ee_transformation_matrix

        j = sp.zeros(6, self.len_links)

        # J_vi = Z_i-1 x (P - pi-1)
        # J_wi = z_i-1

        P = htm[:3, 3]

        p_i = sp.zeros(3, 1)
        z_i = sp.Matrix([0, 0, 1])

        for i in range(self.len_links):
            p_diff = (P - p_i)

            J_vi = z_i
            J_wi = sp.zeros(3, 1)

            if self.links[i].link_type == 'R':
                J_vi = z_i.cross(p_diff)
                J_wi = z_i

            J = sp.Matrix([J_wi, J_vi])
            j[:, i] = J

            transformation = self.links_zero_i[i].transformation_matrix

            p_i = transformation[:3, 3]
            z_i = transformation[:3, 2]

        return j
