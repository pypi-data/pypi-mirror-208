import sympy as sp

from rtb_toolbox.symbols import g, t


class ForwardDynamics:
    def __init__(self, forward_kinematics):
        self.jacobian = forward_kinematics.jacobian
        self.links = forward_kinematics.links_zero_i

        self.q = sp.Matrix([link.generalized_coordinate for link in self.links])
        self.dq_dt = self.q.diff(t)
        self.d2q_dt = self.dq_dt.diff(t)

        self.len_q = len(self.q)

        self.w = self.jacobian[:3, :]

        D, C, G, taus = self.get_system_equations_of_motion()

        self.D = D
        self.C = C
        self.G = G
        self.taus = taus


    def get_system_equations_of_motion(self):
        D, P = self.get_inertia_matrix_and_potential_energy()
        C = sp.zeros(self.len_q, self.len_q)
        G = P.diff(self.q)

        taus = [sp.Symbol(f'tau_{i + 1}') for i in range(self.len_q)]
        taus = sp.Matrix(taus)

        for k in range(len(self.links)):
            qk = self.q[k]

            for i in range(len(self.links)):
                qi = self.q[i]
                dki = D[k, i]
                ckj = 0

                for j in range(len(self.links)):
                    qj = self.q[j]

                    dkj = D[k, j]
                    dij = D[i, j]

                    cijk = sp.Rational(1, 2) * (dkj.diff(qi) + dki.diff(qj) - dij.diff(qk))
                    ckj += cijk*self.dq_dt[j]

                C[k, i] = ckj

        taus = D@self.d2q_dt + C@self.dq_dt + G

        return D, C, G, taus

    def get_inertia_matrix_and_potential_energy(self):
        # translational_kinetic_energy = 0
        potential_energy = sp.zeros(1, 1)
        D = sp.zeros(self.len_q, self.len_q)
        G = sp.Matrix([0, -g, 0])

        for i in range(len(self.links)):
            m = self.links[i].mass
            I = self.links[i].inertia_tensor

            Jvi = sp.zeros(3, len(self.q))
            Jwi = sp.zeros(3, len(self.q))

            r = self.links[i].transformation_matrix[:3, 3]
            dr_dq = [r.diff(q) for q in self.q]

            for j in range(self.len_q):
                Jvi[:, j] = dr_dq[j]

            Jwi[:, :i + 1] = self.w[:, :i + 1]

            D += (m * Jvi.T @ Jvi) + (Jwi.T @ I @ Jwi)
            potential_energy += m * G.T @ r

        return D, potential_energy[0]
