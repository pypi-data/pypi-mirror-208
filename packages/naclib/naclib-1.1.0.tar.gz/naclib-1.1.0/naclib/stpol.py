"""
Main ST-polynomial decomposition functionality.

By Edo van Veen @ Nynke Dekker Lab, TU Delft (2021)
"""
from zernike import RZern
import numpy as np


# Index and normalization conversions.
def nmu2nm(n, mu):  # Use an extra minus sign for mu, to correct for sin/cos swapped definition between papers.
    """Convert an (n, mu) pair to an (n, m) pair."""
    return n, int((n + mu) / 2)


def nm2nmu(n, m):  # Use an extra minus sign for mu, to correct for sin/cos swapped definition between papers.
    """Convert an (n, m) pair to an (n, mu) pair."""
    return n, -int(n - 2 * m)


def Nnmu(n, mu):
    """Calculate N_{n, mu}."""
    if mu == 0:
        return np.sqrt(n + 1)
    else:
        return np.sqrt(2 * n + 2)


def get_Rzern(j_max):
    """Get an Rzern object from the zernike library."""
    n_max = None
    for n in range(0, j_max):
        j = RZern.nm2noll(n=n, m=n)
        if j >= j_max:
            n_max = n
            break
    return RZern(n_max)


def inprod(A, B):
    """Inner product between fields A (shape (n_locs, 2)) and B (shape (n_locs, 2))."""
    n_locs = A.shape[0]
    prod = np.sum([np.dot(A[k, :], B[k, :]) for k in range(n_locs)]) / n_locs
    return prod


def gramschmidt(V):
    """Transform field basis V (shape (n_basis, n_locs, 2)) into orthonormal basis U; also return transformation
    matrix M (shape (n_basis, n_basis))."""

    # Allocate arrays.
    U = np.zeros(V.shape)
    M = np.zeros((V.shape[0], V.shape[0]))

    # Get initial values.
    norm0 = np.sqrt(inprod(V[0, :, :], V[0, :, :]))
    M[0, 0] = norm0
    U[0, :, :] = V[0, :, :] / norm0

    # Iterate.
    for i in range(1, V.shape[0]):
        U[i, :, :] = V[i, :, :]
        for j in range(0, i):
            M[i, j] = inprod(U[i, :, :], U[j, :, :])
            U[i, :, :] = U[i, :, :] - M[i, j] * U[j, :, :]
        norm = np.sqrt(inprod(U[i, :, :], U[i, :, :]))
        if norm < 1e-13:
            return None, None
        M[i, i] = norm
        U[i, :, :] = U[i, :, :] / norm

    # Done.
    return U, M


def get_highest_converging_j_max(locs, D, mean_error_convergence=1e-6, mean_error_divergence=1e-2, max_iter=10000):
    """Get the highest value of j_max (up to 45) for which the ST polynomial decomposition converges.

    Parameters
    ----------
    locs : np.array of floats
        x and y coordinates of the distortion map coordinates, shape (N, 2).
    D : np.array of floats
        x and y components of the distortion vectors at the coordinates given by locs, shape (N, 2).
    mean_error_convergence : float (optional)
        The iteration is considered converged when the mean error reaches this value. Default: 1e-6.
    mean_error_divergence : float (optional)
        The iteration is considered diverged when the mean error reaches this value. Default: 1e-2.
    max_iter : int (optional)
        Maximum number of iterations. Default: 10000.

    Returns
    -------
    j_max_best : int
        Highest converging maximum term for S- and T-polynomials.
    """
    j_max_best = 0
    for j_max in [3, 6, 10, 15, 21, 28, 36, 45]:
        stpol = STPolynomials(j_max_S=j_max, j_max_T=j_max)
        a_S, a_T, MSE = stpol.get_decomposition(locs, D,
                                                max_iter=max_iter,
                                                mean_error_convergence=mean_error_convergence,
                                                mean_error_divergence=mean_error_divergence,
                                                return_error=True, verbose=False)
        if MSE[-1] < mean_error_divergence:
            j_max_best = j_max
    return j_max_best


# Calculate derivatives from https://doi.org/10.1364/OE.26.018878
# Use equations 44-51
# Convert U to Z with equations 6-7
# Checked results with https://doi.org/10.1364/OE.15.018014
def get_Z_derivatives(j_max):
    """Calculate Zernike polynomial derivatives, from https://doi.org/10.1364/OE.26.018878 eqs 44-51."""
    z = get_Rzern(j_max)

    dU_dx = dict()  # Key is (n, m) pair, value is dU_j/dx in terms of U coefficients starting at j=0
    dU_dy = dict()  # Key is (n, m) pair, value is dU_j/dy in terms of U coefficients starting at j=0
    Nj = np.zeros(j_max + 1)
    Nj[1] = Nnmu(*z.noll2nm(k=1))
    Nj[2] = Nnmu(*z.noll2nm(k=2))
    Nj[3] = Nnmu(*z.noll2nm(k=3))

    dU_dx[(0, 0)] = np.zeros(j_max + 1)
    dU_dy[(0, 0)] = np.zeros(j_max + 1)
    dU_dx[(1, 0)] = np.zeros(j_max + 1)
    dU_dy[(1, 1)] = np.zeros(j_max + 1)
    dU_dx[(1, 1)] = np.zeros(j_max + 1)
    dU_dx[(1, 1)][1] = 1
    dU_dy[(1, 0)] = np.zeros(j_max + 1)
    dU_dy[(1, 0)][1] = 1

    for j in range(4, j_max + 1):

        # Make new entry in dictionaries.
        n, mu = z.noll2nm(k=j)
        n, m = nmu2nm(n, mu)
        dU_dx[(n, m)] = np.zeros(j_max + 1)
        dU_dy[(n, m)] = np.zeros(j_max + 1)
        Nj[j] = Nnmu(n, mu)

        # Go over each exception.
        # See https://doi.org/10.1364/OE.26.018878
        # Equations 44-51
        if m == 0:
            dU_dx[(n, 0)][z.nm2noll(*nm2nmu(n - 1, 0))] = n
            dU_dy[(n, 0)][z.nm2noll(*nm2nmu(n - 1, n - 1))] = n
        elif m == n:
            dU_dx[(n, n)][z.nm2noll(*nm2nmu(n - 1, n - 1))] = n
            dU_dy[(n, n)][z.nm2noll(*nm2nmu(n - 1, 0))] = -1 * n
        elif n % 2 == 1 and m == (n - 1) / 2:
            dU_dx[(n, m)][z.nm2noll(*nm2nmu(n - 1, m - 1))] = n
            dU_dx[(n, m)] = dU_dx[(n, m)] + dU_dx[(n - 2, m - 1)]
            dU_dy[(n, m)][z.nm2noll(*nm2nmu(n - 1, n - m - 1))] = n
            dU_dy[(n, m)][z.nm2noll(*nm2nmu(n - 1, n - m))] = -1 * n
            dU_dy[(n, m)] = dU_dy[(n, m)] + dU_dy[(n - 2, m - 1)]
        elif n % 2 == 1 and m == (n - 1) / 2 + 1:
            dU_dx[(n, m)][z.nm2noll(*nm2nmu(n - 1, m))] = n
            dU_dx[(n, m)][z.nm2noll(*nm2nmu(n - 1, m - 1))] = n
            dU_dx[(n, m)] = dU_dx[(n, m)] + dU_dx[(n - 2, m - 1)]
            dU_dy[(n, m)][z.nm2noll(*nm2nmu(n-1, n-m-1))] = n
            dU_dy[(n, m)] = dU_dy[(n, m)] + dU_dy[(n - 2, m - 1)]
        elif n % 2 == 0 and m == n / 2:
            dU_dx[(n, m)][z.nm2noll(*nm2nmu(n - 1, m))] = 2 * n
            dU_dx[(n, m)] = dU_dx[(n, m)] + dU_dx[(n - 2, m - 1)]
            dU_dy[(n, m)][z.nm2noll(*nm2nmu(n - 1, n - m - 1))] = 2 * n
            dU_dy[(n, m)] = dU_dy[(n, m)] + dU_dy[(n - 2, m - 1)]
        else:
            dU_dx[(n, m)][z.nm2noll(*nm2nmu(n - 1, m))] = n
            dU_dx[(n, m)][z.nm2noll(*nm2nmu(n - 1, m - 1))] = n
            dU_dx[(n, m)] = dU_dx[n, m] + dU_dx[(n - 2, m - 1)]
            dU_dy[(n, m)][z.nm2noll(*nm2nmu(n - 1, n - m - 1))] = n
            dU_dy[(n, m)][z.nm2noll(*nm2nmu(n - 1, n - m))] = -1 * n
            dU_dy[(n, m)] = dU_dy[n, m] + dU_dy[(n - 2, m - 1)]

    # Normalize to Z, convert to Zhao's index convention.
    dZ_dx = dict()  # Key is j, value is dZ_j/dx in terms of Z coefficients starting at j=1
    dZ_dy = dict()  # Key is j, value is dZ_j/dy in terms of Z coefficients starting at j=1
    for j in range(1, j_max + 1):
        n, mu = z.noll2nm(j)
        n, m = nmu2nm(n, mu)
        dZ_dx[j] = dU_dx[(n, m)][1:] / Nj[1:] * Nj[j]
        dZ_dy[j] = dU_dy[(n, m)][1:] / Nj[1:] * Nj[j]

    return dZ_dx, dZ_dy


def get_phi_derivatives(j_max):
    """Calculate phi vector field derivatives."""
    dphi_dx = dict()  # Key is j, value is dphi_j/dx in terms of Z coefficients starting at j=1
    dphi_dy = dict()  # Key is j, value is dphi_j/dy in terms of Z coefficients starting at j=1
    dphi_dx[1] = np.zeros(j_max)
    dphi_dy[1] = np.zeros(j_max)

    dZ_dx, dZ_dy = get_Z_derivatives(j_max)

    z = get_Rzern(j_max)
    for j in range(2, j_max + 1):
        n, mu = z.noll2nm(k=j)
        m = np.abs(mu)
        if n == m:
            dphi_dx[j] = dZ_dx[j] / np.sqrt((2 * n * (n + 1)))
            dphi_dy[j] = dZ_dy[j] / np.sqrt((2 * n * (n + 1)))
        else:
            j2 = z.nm2noll(n=n - 2, m=mu)
            if (j - j2) % 2 != 0:
                j2 = z.nm2noll(n=n - 2, m=-mu)
            if (j - j2) % 2 != 0 and m != 0:
                print('could not find j prime: ', j, j2, (n, m))
            dphi_dx[j] = (dZ_dx[j] - dZ_dx[j2] * np.sqrt(n + 1) / np.sqrt(n - 1)) / np.sqrt((4 * n * (n + 1)))
            dphi_dy[j] = (dZ_dy[j] - dZ_dy[j2] * np.sqrt(n + 1) / np.sqrt(n - 1)) / np.sqrt((4 * n * (n + 1)))

    return dphi_dx, dphi_dy


def get_ST_terms(j_max):
    """Get all S/T terms for a value of j_max."""
    dphi_dx, dphi_dy = get_phi_derivatives(j_max)

    Sx = dict()  # Key is j, value is Sj_x in terms of Z coefficients starting at j=1
    Sy = dict()  # Key is j, value is Sj_y in terms of Z coefficients starting at j=1
    Tx = dict()  # Key is j, value is Tj_x in terms of Z coefficients starting at j=1
    Ty = dict()  # Key is j, value is Tj_y in terms of Z coefficients starting at j=1

    z = get_Rzern(j_max)
    for j in range(1, j_max + 1):
        n, mu = z.noll2nm(k=j)
        m = np.abs(mu)

        # Add S term.
        Sx[j] = dphi_dx[j]
        Sy[j] = dphi_dy[j]

        if m != n:
            # Add T term.
            Tx[j] = dphi_dy[j]
            Ty[j] = -1 * dphi_dx[j]

    return Sx, Sy, Tx, Ty


# Class that ties it all together.
class STPolynomials:
    """ST-polynomials class for calculating the ST-polynomial decomposition coefficients of a distortion map,
    and for calculating a correction field from decomposition coefficents.

    Parameters
    ----------
    j_max_S : int
        Maximum term for S-polynomials.
    j_max_T : int
        Maximum term for T-polynomials.
    """

    def __init__(self, j_max_S, j_max_T):
        """Initialize."""

        self.j_max_S = j_max_S
        self.j_max_T = j_max_T
        self.j_max_ST = max(j_max_S, j_max_T)
        self.cart = get_Rzern(self.j_max_ST)
        self.j_max = self.cart.nk
        self.Sx = dict()  # Key is j, value is Sj_x in terms of Z coefficients starting at j=1.
        self.Sy = dict()  # Key is j, value is Sj_y in terms of Z coefficients starting at j=1.
        self.Tx = dict()  # Key is j, value is Tj_x in terms of Z coefficients starting at j=1.
        self.Ty = dict()  # Key is j, value is Tj_y in terms of Z coefficients starting at j=1.

        self.Sj = []  # All j-values for S.
        self.Tj = []  # All j-values for T.

        # Fill polynomial dicts.
        Sx, Sy, Tx, Ty = get_ST_terms(self.j_max)
        for j in Sx.keys():
            if j <= j_max_S:
                self.Sx[j] = Sx[j]
                self.Sy[j] = Sy[j]
                self.Sj.append(j)
        for j in Tx.keys():
            if j <= j_max_T:
                self.Tx[j] = Tx[j]
                self.Ty[j] = Ty[j]
                self.Tj.append(j)

    def get_decomposition_noniterative(self, locs, field_D):
        """Get the decomposition coefficients for a distortion map with N points without using the iterative method
        and without Gram-Schmidt orthonormalization.

        Parameters
        ----------
        locs : np.array of floats
            x and y coordinates of the distortion map coordinates, shape (N, 2).
        field_D : np.array of floats
            x and y components of the distortion vectors at the coordinates given by locs, shape (N, 2).

        Returns
        -------
        coefs_S : dict
            Dictionary with S-polynomial indices/coefficients as key/value pairs.
        coefs_T : dict
            Dictionary with T-polynomial indices/coefficients as key/value pairs.
        """

        # Check if any coordinates in locs are outside the unit circle.
        if np.any([np.linalg.norm(loc) >= 1 for loc in locs]):
            raise Exception("Cannot calculute decomposition for coordinates outside the unit circle.")

        self.cart.make_cart_grid(locs[:, 0], locs[:, 1])
        coefs_S = {j: 0 for j in self.Sj}
        coefs_T = {j: 0 for j in self.Tj}

        # Calculate coefficients with the Frobenius inner product.
        for j in self.Sj:
            czx = self.Sx[j]
            czy = self.Sy[j]
            phi_x = self.cart.eval_grid(czx)
            phi_y = self.cart.eval_grid(czy)
            Pj = np.zeros(field_D.shape)
            Pj[:, 0] = phi_x
            Pj[:, 1] = phi_y
            coefs_S[j] = inprod(field_D, Pj)
        for j in self.Tj:
            czx = self.Tx[j]
            czy = self.Ty[j]
            phi_x = self.cart.eval_grid(czx)
            phi_y = self.cart.eval_grid(czy)
            Pj = np.zeros(field_D.shape)
            Pj[:, 0] = phi_x
            Pj[:, 1] = phi_y
            coefs_T[j] = inprod(field_D, Pj)

        return coefs_S, coefs_T

    def get_decomposition(self, locs, field_D, mean_error_convergence=1e-6, mean_error_divergence=1e-2,
                          max_iter=10000, return_error=False, verbose=True):
        """Get the optimal decomposition coefficients for a distortion map with N points by using the iterative method.

        Parameters
        ----------
        locs : np.array of floats
            x and y coordinates of the distortion map coordinates, shape (N, 2).
        field_D : np.array of floats
            x and y components of the distortion vectors at the coordinates given by locs, shape (N, 2).
        mean_error_convergence : float (optional)
            The iteration is considered converged when the mean error reaches this value. Default: 1e-6.
        mean_error_divergence : float (optional)
            The iteration is considered diverged when the mean error reaches this value. Default: 1e-2.
        max_iter : int (optional)
            Maximum number of iterations. Default: 10000.
        return_error : bool (optional)
            If True, the error is given as a third return value. Default: False.
        verbose : bool (optional)
            If True, print message on convergence or divergence. Default: True.

        Returns
        -------
        a_Stot : dict
            Dictionary with S-polynomial indices/coefficients as key/value pairs.
        a_Ttot : dict
            Dictionary with T-polynomial indices/coefficients as key/value pairs.
        """

        # Check if any coordinates in locs are outside the unit circle.
        if np.any([np.linalg.norm(loc) >= 1 for loc in locs]):
            raise Exception("Cannot calculute decomposition for coordinates outside the unit circle.")

        # Prepare.
        D_temp = np.array(field_D)
        a_Sall = []
        a_Tall = []
        mean_error = []

        # Calculate polynomial coefficients of the residual field max_iter times.
        for i in range(max_iter):
            a_Stemp, a_Ttemp = self.get_decomposition_noniterative(locs, D_temp)
            a_Sall.append(dict(a_Stemp))
            a_Tall.append(dict(a_Ttemp))
            a_Stot = {i: np.sum([a[i] for a in a_Sall]) for i in self.Sj}
            a_Ttot = {i: np.sum([a[i] for a in a_Tall]) for i in self.Tj}
            P_temp = self.get_field(locs, a_Stot, a_Ttot)
            D_temp[:, 0] = field_D[:, 0] - P_temp[:, 0]
            D_temp[:, 1] = field_D[:, 1] - P_temp[:, 1]
            magnitude = np.hypot(D_temp[:, 0], D_temp[:, 1])
            mean_error.append(np.mean(magnitude))

            if i > 1:
                if mean_error[-1] <= mean_error[-2] and \
                        np.abs(mean_error[-1] - mean_error[-2]) < mean_error_convergence and \
                        np.abs(mean_error[-1] - mean_error[-3]) < mean_error_convergence:
                    if verbose:
                        print('Convergence at iteration ', i-2, 'with mean error ', mean_error[-1])
                    break
                if mean_error[-1] > mean_error[-2] and \
                        np.abs(mean_error[-1] - mean_error[-2]) > mean_error_divergence and \
                        np.abs(mean_error[-1] - mean_error[-3]) > mean_error_divergence:
                    if verbose:
                        print('Divergence at iteration ', i, 'with mean error ', mean_error[-1])
                    a_Stot = {i: 0. for i in self.Sj}
                    a_Ttot = {i: 0. for i in self.Tj}
                    if return_error:
                        return a_Stot, a_Ttot, np.array(mean_error)
                    return a_Stot, a_Ttot
            if verbose and i == max_iter-1:
                print('Maximum number of iterations reached.')

        # Add up all S and T coefficients to get final coefficients.
        a_Stot = {i: np.sum([a[i] for a in a_Sall]) for i in self.Sj}
        a_Ttot = {i: np.sum([a[i] for a in a_Tall]) for i in self.Tj}

        if return_error:
            return a_Stot, a_Ttot, np.array(mean_error)
        return a_Stot, a_Ttot

    def get_decomposition_gramschmidt(self, locs, field_D):
        """Get the decomposition coefficients for a distortion map with N points, by using Gram-Schmidt
        orthonormalization to orthonormalize the ST polynomials on the finite grid.

        Parameters
        ----------
        locs : np.array of floats
            x and y coordinates of the distortion map coordinates, shape (N, 2).
        field_D : np.array of floats
            x and y components of the distortion vectors at the coordinates given by locs, shape (N, 2).

        Returns
        -------
        coefs_S : dict
            Dictionary with S-polynomial indices/coefficients as key/value pairs.
        coefs_T : dict
            Dictionary with T-polynomial indices/coefficients as key/value pairs.
        """

        # Get ST-polynomial fields at locs.
        n_basis = len(self.Sj) + len(self.Tj) - 1
        V = np.zeros((n_basis, field_D.shape[0], 2))
        self.cart.make_cart_grid(locs[:, 0], locs[:, 1])
        i = 0
        for j in self.Sj[1:]:  # S1 is 0, so skip
            czx = self.Sx[j]
            czy = self.Sy[j]
            phi_x = self.cart.eval_grid(czx)
            phi_y = self.cart.eval_grid(czy)
            Pj = np.zeros(field_D.shape)
            Pj[:, 0] = phi_x
            Pj[:, 1] = phi_y
            V[i, :, :] = Pj
            i = i + 1
        for j in self.Tj:
            czx = self.Tx[j]
            czy = self.Ty[j]
            phi_x = self.cart.eval_grid(czx)
            phi_y = self.cart.eval_grid(czy)
            Pj = np.zeros(field_D.shape)
            Pj[:, 0] = phi_x
            Pj[:, 1] = phi_y
            V[i, :, :] = Pj
            i = i + 1

        # Transform to orthonormal basis; .
        U, M = gramschmidt(V)
        if U is None:  # Gramschmidt was unsuccessful; return correction field 0.
            print("WARNING: j_max value too high, orthonormalization not possible.")
            return {i: 0 for i in self.Sj}, {i: 0 for i in self.Tj}

        # Calculate decomposition with the Frobenius inner product.
        coefs_U = np.zeros(n_basis)
        for j in range(n_basis):
            coefs_U[j] = inprod(field_D, U[j, :, :])

        # Transform back to ST basis.
        coefs_V = np.dot(coefs_U, np.linalg.inv(M))
        i = 0
        a_S = {1: 0.}
        for j in self.Sj[1:]:
            a_S[j] = coefs_V[i]
            i = i + 1
        a_T = dict()
        for j in self.Tj:
            a_T[j] = coefs_V[i]
            i = i + 1

        # Return coefficient dictionaries.
        return a_S, a_T

    def get_field(self, locs, coefs_S, coefs_T):
        """Get the correction field from ST-polynomial decomposition coefficients.

        Parameters
        ----------
        locs : np.array of floats
            x and y coordinates of input coordinates, shape (N, 2).
        coefs_S : dict
            Dictionary with S-polynomial indices/coefficients as key/value pairs.
        coefs_T : dict
            Dictionary with T-polynomial indices/coefficients as key/value pairs.

        Returns
        -------
        field_ST : np.array of floats
            x and y components of the correction vectors at the coordinates given by locs, shape (N, 2).
        """

        # Get Z-coefficients
        czx = np.zeros(self.j_max)
        czy = np.zeros(self.j_max)
        for j, a in coefs_S.items():
            czx = czx + a * self.Sx[j]
            czy = czy + a * self.Sy[j]
        for j, a in coefs_T.items():
            czx = czx + a * self.Tx[j]
            czy = czy + a * self.Ty[j]

        # Make field at locs.
        self.cart.make_cart_grid(locs[:, 0], locs[:, 1])
        phi_x = self.cart.eval_grid(czx, matrix=False)
        phi_y = self.cart.eval_grid(czy, matrix=False)
        field_ST = np.array([phi_x, phi_y]).swapaxes(0, 1)

        return field_ST
