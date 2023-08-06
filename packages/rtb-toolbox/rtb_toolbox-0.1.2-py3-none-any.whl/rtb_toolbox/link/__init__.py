from rtb_toolbox.utils import compute_link_transformation, np

class Link:
    def __init__(
            self,
            dhp=None,
            generalized_coordinate=None,
            offset=0,
            mass=None,
            transformation_matrix=None,
            inertia_tensor=None,
            limits=None,
            link_type='R'
    ):
        self.dhp = dhp
        self.generalized_coordinate = generalized_coordinate
        self.inertia_tensor = inertia_tensor
        self.limits = limits
        self.link_type = link_type

        if limits is None:
            self.limits = [-np.pi, np.pi]

        if generalized_coordinate is None and dhp is None:
            raise ValueError('Either generalized_coordinate or dhp must be specified')

        if dhp is None:
            if link_type == 'R':
                self.dhp = [generalized_coordinate, 0, 0, 0]
            else:
                self.dhp = [0, generalized_coordinate, 0, 0]

        if generalized_coordinate is None:
            if link_type == 'R':
                self.generalized_coordinate = dhp[0]
            elif link_type == 'P':
                self.generalized_coordinate = dhp[1]

        self.mass = mass
        self.transformation_matrix = transformation_matrix

        if transformation_matrix is None:
            self.transformation_matrix = compute_link_transformation(dhp)

    def update(self):
        self.transformation_matrix = compute_link_transformation(self.dhp, self.offset)

    def get_transformation_matrix(self):
        return self.transformation_matrix
