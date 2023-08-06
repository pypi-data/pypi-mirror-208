"""
Fit/predict interface for ST-polynomial decomposition distortion correction.

By Edo van Veen @ Nynke Dekker Lab, TU Delft (2021)
"""
import naclib.stpol


class DistortionCorrection:
    """Class for...

    Parameters
    ----------
    max_iter : int (optional)
        Maximum number of iterations. Default: 10000.
    conv_threshold : float (optional)
        The iteration is considered converged when the mean error reaches this value. Default: 1e-6.
    div_threshold : float (optional)
        The iteration is considered diverged when the mean error reaches this value. Default: 1e-2.
    """

    def __init__(self, max_iter=10000, conv_threshold=1e-6, div_threshold=1e-2):
        self.max_iter = max_iter
        self.conv_threshold = conv_threshold
        self.div_threshold = div_threshold
        self.j_max = 0
        self.stpol = None
        self.a_S = {}
        self.a_T = {}

    def fit(self, locations, distortions):
        """Fit distortion correction model using a distortion field in the unit circle.

        Parameters
        ----------
        locations : np.array of floats
            x and y coordinates of the distortion map coordinates, shape (N, 2).
        distortions : np.array of floats
            x and y components of the distortion vectors at the coordinates given by locs, shape (N, 2).
        """
        j_max = naclib.stpol.get_highest_converging_j_max(locations, distortions,
                                                          mean_error_convergence=self.conv_threshold,
                                                          mean_error_divergence=self.div_threshold,
                                                          max_iter=self.max_iter)
        if j_max == 0:
            raise ValueError("No converging distortion correction field found.")
        self.j_max = j_max
        self.stpol = naclib.stpol.STPolynomials(j_max_S=self.j_max, j_max_T=self.j_max)
        self.a_S, self.a_T = self.stpol.get_decomposition(locations, distortions,
                                                          mean_error_convergence=self.conv_threshold,
                                                          mean_error_divergence=self.div_threshold,
                                                          max_iter=self.max_iter,
                                                          verbose=False)

    def predict(self, locations):
        """Generate a correction field at input locations.

        Parameters
        ----------
        locations : np.array of floats
            x and y coordinates of coordinates to be distortion corrected, shape (N, 2).

        Returns
        -------
        np.array of floats
            x and y components of the distortion correction vectors at the coordinates given by locations, shape (N, 2).
        """
        if self.stpol is None:
            return RuntimeError("Cannot run prediction before fitting.")
        return self.stpol.get_field(locations, self.a_S, self.a_T)
