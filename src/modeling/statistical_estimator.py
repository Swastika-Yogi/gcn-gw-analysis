"""Empirical (data-driven) chirp-mass estimator, as an alternative to the
physics formula in chirp_mass_estimator.py.

This does NOT derive mass from SNR/orientation - both are absent from
circulars (see chirp_mass_estimator.py's docstring and the feasibility
memo). Instead it fits log(mass) as a log-linear function of fields that
*are* in circulars (distance, and optionally FAR / classification),
against events where circulars themselves report a reference chirp mass.

This is a population-level statistical relationship (plausibly reflecting
a real detection-selection effect: louder/heavier binaries are seen
further out), not a per-event physical measurement. Report it as that.
"""


def _solve_linear_system(matrix, vector):
    """Gaussian elimination for a small square system. No numpy in this env."""
    k = len(vector)
    matrix = [row[:] for row in matrix]
    vector = vector[:]
    for i in range(k):
        pivot = matrix[i][i]
        for j in range(k):
            matrix[i][j] /= pivot
        vector[i] /= pivot
        for row in range(k):
            if row != i:
                factor = matrix[row][i]
                for j in range(k):
                    matrix[row][j] -= factor * matrix[i][j]
                vector[row] -= factor * vector[i]
    return vector


def fit_log_linear(predictor_columns, log_targets):
    """predictor_columns: list of equal-length lists (e.g. [log_distance, log_far]).
    log_targets: log(reference chirp mass) for the same events.

    Returns coefficients [intercept, b1, b2, ...] via ordinary least squares.
    """
    m = len(log_targets)
    k = len(predictor_columns) + 1
    design = [[1.0] + [col[i] for col in predictor_columns] for i in range(m)]

    normal_matrix = [[0.0] * k for _ in range(k)]
    normal_vector = [0.0] * k
    for i in range(m):
        row = design[i]
        for a in range(k):
            for b in range(k):
                normal_matrix[a][b] += row[a] * row[b]
            normal_vector[a] += row[a] * log_targets[i]

    return _solve_linear_system(normal_matrix, normal_vector)


def predict_log_linear(coefficients, predictor_values):
    """predictor_values: [x1, x2, ...] matching the columns fit was trained on."""
    return coefficients[0] + sum(
        coefficients[i + 1] * predictor_values[i] for i in range(len(predictor_values))
    )
