"""
Anomaly detection blocks solve the problem of determining elements of a
timeseries that don't follow the general pattern of the other elements.
"""

# Local
from ...toolkit.hoist_module_imports import hoist_module_imports
from . import (
    pointwise_bounded_bats,
    pointwise_bounded_hw_additive,
    pointwise_bounded_hw_multiplicative,
    srom_anomaly_ensembler,
    srom_anomaly_graph_lasso,
    srom_anomaly_pca,
    srom_anomaly_robust_pca,
    srom_bayesian_gmm_outlier,
    srom_covariance_anomaly,
    srom_extended_isolation_forest,
    srom_extended_mincovdet,
    srom_extended_spad,
    srom_gaussian_graphical_model,
    srom_generalized_anomaly_model,
    srom_gmm_outlier,
    srom_graph_pgscps,
    srom_graph_quic,
    srom_hbos,
    srom_hotelling_t2,
    srom_kde,
    srom_lof_nearest_neighbor,
    srom_mssa,
    srom_nearest_neighbor_anomaly_model,
    srom_oob,
    srom_pca_q,
    srom_pca_t2,
    srom_random_partition_forest,
    srom_spad,
    srom_zero_r_anomaly_detector,
)

# Block classes hoisted to the top level
# NOTE: These must come after the module imports so that the block modules
#   themselves can be tracked cleanly for optional modules
hoist_module_imports(globals())
