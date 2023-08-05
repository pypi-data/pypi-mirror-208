from .add_vpsd_components    import add_vpsd_components
from .compute_vpsd           import compute_vpsd
from .fit_vpsd_coefficients  import fit_vpsd_coefficients
from .get_stellar_parameters import get_stellar_parameters
from .plot_vpsd_components   import plot_vpsd_components

class _Star_classes(add_vpsd_components,
                    compute_vpsd,
                    get_stellar_parameters,
                    plot_vpsd_components):
    pass