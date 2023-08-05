import numpy as np
import pandas as pd
from scipy import ndimage as nd

"""
Conducting acoustic measurements over large areas often requires significant numbers of conditions, or measurement 
sites. In effort to understand the acoustic area where airmen operate during routine maintenance, a measurement was 
conducted on a single engine fighter aircraft. Due to the complexity of the measurement array, fewer sites were used 
than required to completely characterize this region. In order to complete the analysis, a series of Python scripts 
were developed to use nearest-neighbor interpolation of the sparse matrix, which was subsequently smoothed using a 
bi-linear interpolation. 

This collection of functions grew out of this research. If you intend to use this work, please reference: 
Mobley, Frank S., Alan T. Wall, and Stephen C. Campbell. "Translating jet noise measurements to near-field level 
maps with nearest neighbor bilinear smoothing interpolation." The Journal of the Acoustical Society of America 150.2 
(2021): 687-693.
"""


def bi_linear_smoothing(starting_mesh, measured_data, measured_x_index, measured_y_index,
                        tolerance: float = 1e-4, maximum_iterations: int = 1000,
                        verbose_info: bool = True):
    """
    This computes the bilinear average of the mesh until the RMSE reaches the
    tolerance passed as an argument.

    Parameters
    ----------
    :param verbose_info: bool
        Flag detailing whether information is printed to the Python console during execution of the algorithm
    :param starting_mesh : double array-like
        the starting dense matrix determined from the nearest neighbor
    :param tolerance : double
        The minimum error level to finish the averaging
    :param measured_data : DataFrame
        A data frame with the X, Y, La values for each of the measured points
    :param measured_x_index : array-like double
        The X indices for where to insert the measured levels
    :param measured_y_index : array-like double
        The X indices for where to insert the measured levels
    :param maximum_iterations: int
        The maximum number of iterations that we want to iterate through before returning an error.

    Returns
    -------
    The dense matrix smoothed


    """

    zz = starting_mesh.copy()

    #   Perform the iterative smoothing
    rmse = 100
    i = 0

    zz_last = zz.copy()

    while rmse > tolerance and i < maximum_iterations:
        #   Replace the data with the measured information
        zz[measured_y_index, measured_x_index] = measured_data

        if verbose_info:
            print('Starting iteration {}'.format(i + 1))

        #   Loop through the array and create an approximate of the interpolation
        if verbose_info:
            print('iterating over the surface')

        npts = 3
        for xidx in range(zz.shape[0]):
            for yidx in range(zz.shape[1]):

                #   Add the central point
                nn_mean = 0

                #   Set the count for the points in the average
                n = 0

                #   Determine the span in each direction
                span = int((npts - 1) / 2)

                #   Try to determine the value for the lower index of the y-axis
                ylo = yidx - span
                if ylo < 0:
                    ylo = 0

                yhi = yidx + span
                if yhi >= zz.shape[1]:
                    yhi = zz.shape[1] - 1

                #   Now the x-axis
                xlo = xidx - span
                if xlo < 0:
                    xlo = 0
                xhi = xidx + span
                if xhi >= zz.shape[0]:
                    xhi = zz.shape[0] - 1

                for p in range(ylo, yhi + 1):
                    for q in range(xlo, xhi + 1):
                        nn_mean += zz[q, p]
                        n += 1

                zz[xidx, yidx] = nn_mean / n

        #   Compute the error between this and the previous surface
        rmse = np.std(np.std(zz - zz_last, axis=1))

        if verbose_info:
            print('RMSE:{:.5f}\n***************************'.format(rmse))

        #   Copy the current surface to the previous surface
        zz_last = zz.copy()
        i += 1
    return zz, i, rmse


def nearest_neighbor_dense_sampling(true_data: pd.DataFrame, out_x: np.ndarray, out_y: np.ndarray,
                                    smoothing_error_tolerance: float = 1e-5, iteration_max: int = 1000,
                                    verbose_info: bool = True):
    """
    From research in the acoustic measurement of near-field noise around fifth generation fighter aircraft (see
    Mobley, Frank S., Alan T. Wall, and Stephen C. Campbell. Translating jet noise measurements to near-field level maps
    with nearest neighbor bilinear smoothing interpolation. The Journal of the Acoustical Society of America 150.2
    (2021): 687-693) this code was created. Initially it was focused on the methods and data storage for the research
    within the paper. However, this version has been made more generic to assist in using this interpolation method
    across a wider range of data.

    To use this you must supply a DataFrame that contains the sparse matrix in column representation. You must have a
    column called 'x', 'y', and 'z'. These will be used to determine the 'measured', 'known', or 'true' points on the
    sparse surface. This object is the 'true_data' argument of the function.

    Parameters
    ----------
    :param verbose_info: bool
        A flag to determine whether debug information is shown in the Python console
    :param true_data : Pandas.DataFrame
        This is the sparse data that we want to interpolate. It must contain a column for the 'x', 'y', and 'z' data
        elements. These will be used in the replacement step.
    :param out_x : Numpy.ndarray
        This is the desired output values for the x-axis of the dense matrix surface
    :param out_y : Numpy.ndarray
        This is the desired output values for the y-axis of the dense matrix surface
    :param smoothing_error_tolerance : double
        The error tolerance that terminate the smoothing
    :param iteration_max : int
        The maximum number of iterations that are required for the construction of the dense mesh

    Returns
    -------
    tuple containing the dense matrix x, y, smoothed z, and rough z values

    """

    #   Run checks on the input surface
    if not _check_true_data_arguments(true_data):
        raise ValueError("The input true_data is not properly formed")

    #   Build the mesh of output Cartesian Locations
    xx, yy = np.meshgrid(out_x, out_y)
    zz = np.ones(xx.shape) * -999

    #   Find the index within the desired mesh where these data fall
    m_x_idx, m_y_idx = _find_true_data_indices(out_x, out_y, true_data)

    #   Update the values of the surface with the information from the true data
    zz[m_y_idx, m_x_idx] = true_data['z']

    #   Perform the nearest neighbor approximation
    invalid = np.isin(zz, -999)
    ind = nd.distance_transform_edt(invalid, return_distances=False, return_indices=True)

    #   Assign the value based on the selected indices
    zz = zz[tuple(ind)]

    #   Smooth the coarse surface
    smoothed_zz, iterations, error = bi_linear_smoothing(starting_mesh=zz,
                                                         measured_x_index=m_x_idx,
                                                         measured_y_index=m_y_idx,
                                                         measured_data=true_data['z'],
                                                         tolerance=smoothing_error_tolerance,
                                                         maximum_iterations=iteration_max,
                                                         verbose_info=verbose_info)

    return xx, yy, smoothed_zz, zz


def _check_true_data_arguments(x):
    """
    This function checks the input argument of the interpolation to ensure that it possesses all the correct
    information prior to running the analysis.

    :param x: Pandas.DataFrame
        The collection of input data that we want to ensure is the correct format prior to creating the interpolation
        grid.
    :return:
        True if the DataFrame is correctly formed, otherwise it raises ValueError exceptions.
    """

    if not isinstance(x, pd.DataFrame):
        raise ValueError("The true data input must be a Pandas.DataFrame")

    if 'x' not in x.columns.values or 'y' not in x.columns.values or 'z' not in x.columns.values:
        raise ValueError("The DataFrame must contain a column for each of the standard Cartesian coordinates")

    return True


def _find_true_data_indices(x, y, true_data):
    """
    Part of this algorithm determines where in the dense grid the true/measured data exists. Then it will replace the
    current value in the matrix with the true data. In this manner was can constrain some of the simplification of
    the system to ensure that we are close to the points that we know.

    This function will determine where in the dense matrix the true data will exist, insert the true data into the
    list, and return the indices and the new surface.
    :param x: Numpy.ndarray
        This is the single dimensioned array of the values of the function along the x-direction
    :param y: Numpy.ndarray
        This is the single dimensioned array of the values of the function along the y-direction
    :param true_data: Pandas.DataFrame
        The collection of true data. This must contain columns for the 'x', 'y', and 'z' elements of the sparse data
    :return: tuple
        The first element of the tuple is the x-direction indices of the placement for the true data, and the second
        is the y-direction indices.
    """

    measured_x_index = np.zeros(shape=(true_data.shape[0],), dtype=int)
    measured_y_index = np.zeros(shape=(true_data.shape[0],), dtype=int)

    x_idx = np.where(true_data.columns.values == 'x')[0][0]
    y_idx = np.where(true_data.columns.values == 'y')[0][0]

    #   Find the indices for the measured data
    for i in range(true_data.shape[0]):
        try:
            measured_x_index[i] = np.where(x - true_data.iloc[i, x_idx] >= 0)[0][0]
            measured_y_index[i] = np.where(y - true_data.iloc[i, y_idx] >= 0)[0][0]

        except IndexError:
            print('Error at the {}th element'.format(i))

    return measured_x_index, measured_y_index
