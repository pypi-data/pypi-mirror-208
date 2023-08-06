import numpy as np
import sympy as sp

from rtb_toolbox.frame import z_rotation_matrix, translation_matrix, x_rotation_matrix


def near_zero(s, epsilon=1e-6):
    """
      Returns True if the value is small enough to be considered zero.

    :param s: The value to check.
    :param epsilon: The threshold.
    """
    return np.abs(s) < epsilon


def vec_to_so3(v):
    """
      Converts a 3-vector to a so(3) representation
    :param v: A 3-vector
    :return: The skew symmetric representation of v
    """
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def so3_to_vec(so3):
    """
      Converts a so(3) representation to a 3-vector
    :param so3: A 3x3 skew-symmetric matrix
    :return: The 3-vector represented by so3
    """
    return np.array([so3[2, 1], so3[0, 2], so3[1, 0]])


def se3_to_vec(se3):
    """
      Converts a 4x4 matrix in se3 into a 6-vector representing a spatial velocity
    :param se3: A 4x4 matrix in se3
    :return: A 6-vector representing a spatial velocity
    """

    return np.r_[[se3[2][1], se3[0][2], se3[1][0]], [se3[0][3], se3[1][3], se3[2][3]]]


def transform_to_rotation_and_translation(T):
    """
      Converts a homogeneous transformation matrix into a rotation matrix and a position vector
    :param T: A 4x4 homogeneous transformation matrix
    :return: A 3x3 rotation matrix and a 3-vector
    """

    return T[:3, :3], T[:3, 3]


def rotation_and_translation_to_transform(R, p):
    """
      Converts a rotation matrix and a position vector into a homogeneous transformation
      matrix
    :param R: A 3x3 rotation matrix
    :param p: A 3-vector
    :return: A 4x4 homogeneous transformation matrix
    """

    return np.r_[np.c_[R, p], [[0, 0, 0, 1]]]


def inverse_rotation(R):
    """
      Returns the inverse of a rotation matrix.

    :param R: The rotation matrix.
    :return: The inverse of rot.
    """
    return R.T


def inverse_transformation(T):
    """
      Computes the inverse of a homogeneous transformation matrix
    :param T: A 4x4 homogeneous transformation matrix
    :return: The inverse of T
    """

    R, p = transform_to_rotation_and_translation(T)
    R_inv = inverse_rotation(R)

    return rotation_and_translation_to_transform(R_inv, -(R_inv @ p))


def matrix_log3(R):
    """
      Computes the matrix log of a rotation matrix
    :param R: A 3x3 rotation matrix
    :return: The matrix log of rot
    """

    tr_r = (np.trace(R) - 1) / 2.0
    if tr_r >= 1:
        return 0, np.zeros((3, 3))
    elif tr_r <= -1:
        if not near_zero(1 + R[2][2]):
            s = (1.0 / np.sqrt(2 * (1 + R[2][2]))) * np.array([R[0][2], R[1][2], 1 + R[2][2]])
        elif not near_zero(1 + R[1][1]):
            s = (1.0 / np.sqrt(2 * (1 + R[1][1]))) * np.array([R[0][1], 1 + R[1][1], R[2][1]])
        else:
            s = (1.0 / np.sqrt(2 * (1 + R[0][0]))) * np.array([1 + R[0][0], R[1][0], R[2][0]])

        return np.pi, vec_to_so3(np.pi * s)
    else:
        theta = np.arccos(tr_r)
        return theta, theta / 2.0 / np.sin(theta) * (R - np.array(R).T)


def matrix_log6(T):
    """
    Computes the matrix log of a homogeneous transformation matrix
    :param T: A matrix in SE3
    :return: The matrix log of T
    """

    R, p = transform_to_rotation_and_translation(T)
    _, l3 = matrix_log3(R)

    if np.array_equal(l3, np.zeros((3, 3))):
        return np.r_[np.c_[np.zeros((3, 3)), p], [[0, 0, 0, 0]]]
    else:
        theta = np.arccos((np.trace(R) - 1) / 2.0)

        return np.r_[np.c_[l3, np.dot(
            np.eye(3) - l3 / 2.0 + (1.0 / theta - 1.0 / np.tan(theta / 2.0) / 2) * np.dot(l3, l3) / theta,
            p)], [[0, 0, 0, 0]]]


def compute_link_transformation(dhp, offset=0, link_type='R'):
    rz = z_rotation_matrix(dhp[0])
    tz = translation_matrix(0, 0, dhp[1])
    tx = translation_matrix(dhp[2], 0, 0)
    rx = x_rotation_matrix(dhp[3])

    if offset != 0:
        if link_type == 'R':
            rz @= z_rotation_matrix(offset)
        else:
            tz @= translation_matrix(0, 0, offset)

    return rz @ tz @ tx @ rx


def compute_homogeneous_transformation(links, start, end):
    if end == 0:
        return sp.eye(4)

    transformation_matrix = links[start].get_transformation_matrix()

    for i in range(start + 1, end):
        transformation_matrix_i = links[i].get_transformation_matrix()
        transformation_matrix = transformation_matrix @ transformation_matrix_i

    return transformation_matrix


def normalize_angle_between_limits(angle, lower_limit, upper_limit):
    """
      Normalizes an angle between two limits
    :param angle: The angle to normalize
    :param lower_limit: The lower limit
    :param upper_limit: The upper limit
    :return: The normalized angle
    """

    while angle > upper_limit:
        angle -= 2 * np.pi
    while angle < lower_limit:
        angle += 2 * np.pi

    return angle
