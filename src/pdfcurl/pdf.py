from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.fft import fft

# ============================================================
# DATA MODELS
# ============================================================


@dataclass(slots=True)
class Pattern:
    x: np.ndarray
    y: np.ndarray


@dataclass(slots=True)
class Composition:
    """
    Simple elemental composition:
    Z-weighted normalization proxy (PDFgetX3-style abstraction)
    """

    elements: dict[str, float]  # element -> stoichiometric fraction


@dataclass(slots=True)
class Experiment:
    wavelength: float
    composition: Composition


@dataclass(slots=True)
class PDFConfig:
    qmax: float
    qmin: float = 0.0
    rmax: float = 50.0
    rstep: float = 0.01
    lorch: bool = True
    nq: int = 4096


@dataclass(slots=True)
class PDFResult:
    q: np.ndarray
    fq: np.ndarray
    gr: np.ndarray
    r: np.ndarray


# ============================================================
# BASIC UTILITIES
# ============================================================


def tth_to_q(tth_deg: np.ndarray, wavelength: float) -> np.ndarray:
    theta = np.deg2rad(tth_deg / 2.0)
    return 4.0 * np.pi * np.sin(theta) / wavelength


def interpolate(x: np.ndarray, y: np.ndarray, x_new: np.ndarray) -> np.ndarray:
    return np.interp(x_new, x, y)


# ============================================================
# FORM FACTOR MODEL (SIMPLIFIED PDFGETX3 STYLE)
# ============================================================


def atomic_form_factor_z_approx(z: float, q: np.ndarray) -> np.ndarray:
    """
    Very simplified analytic approximation:
    PDFgetX3 uses tabulated Cromer-Mann coefficients internally,
    but structurally only <f> and <f^2> matter.

    Here we approximate decay:
        f(q) ~ Z * exp(-alpha q^2)
    """
    alpha = 0.02
    return z * np.exp(-alpha * q**2)


def compute_fq_f2(composition: Composition, q: np.ndarray):
    """
    Returns:
        f_mean, f2_mean
    """
    total = sum(composition.elements.values())

    f = np.zeros_like(q)
    f2 = np.zeros_like(q)

    for el, frac in composition.elements.items():
        z = float("".join([c for c in el if c.isdigit()])) or 10.0

        fi = atomic_form_factor_z_approx(z, q)

        f += frac * fi
        f2 += frac * fi**2

    f /= total
    f2 /= total

    return f, f2


# ============================================================
# BACKGROUND (PDFGETX3 STYLE: NUMERICAL, NOT PHYSICAL)
# ============================================================


def remove_smooth_background(q: np.ndarray, iq: np.ndarray) -> np.ndarray:
    """
    PDFgetX3 idea: remove low-frequency background numerically.
    We approximate with moving average.
    """
    window = max(51, len(q) // 50)

    kernel = np.ones(window) / window
    smooth = np.convolve(iq, kernel, mode="same")

    return iq - smooth


# ============================================================
# NORMALIZATION
# ============================================================


def normalize_iq(iq: np.ndarray, f2: np.ndarray) -> np.ndarray:
    """
    S(Q) normalization:
        S(Q) = I(Q) / <f^2>
    """
    eps = 1e-12
    return iq / (f2 + eps)


# ============================================================
# F(Q)
# ============================================================


def compute_fq(q: np.ndarray, sq: np.ndarray) -> np.ndarray:
    """
    F(Q) = Q * (S(Q) - 1)
    """
    return q * (sq - 1.0)


# ============================================================
# LORCH WINDOW
# ============================================================


def lorch_window(q: np.ndarray, qmax: float) -> np.ndarray:
    """
    Standard PDFgetX3 Lorch damping function
    """
    x = np.pi * q / qmax
    return np.sinc(x / np.pi)


# ============================================================
# G(R)
# ============================================================


def compute_gr(fq: np.ndarray, q: np.ndarray, rmax: float):
    dq = q[1] - q[0]
    n = len(fq)

    fft_fq = fft(fq, n)

    r = np.linspace(0.0, rmax, n)

    gr = -(2.0 / np.pi) * dq * np.imag(fft_fq)

    return r, gr


# ============================================================
# MAIN PIPELINE
# ============================================================


def compute_pdf(
    pattern: Pattern,
    exp: Experiment,
    config: PDFConfig,
) -> PDFResult:

    # 1. Q-space conversion
    q = tth_to_q(pattern.x, exp.wavelength)

    # 2. interpolate to uniform grid
    q_grid = np.linspace(0, config.qmax, config.nq)
    iq = interpolate(q, pattern.y, q_grid)

    # 3. background removal (PDFGETX3 style)
    iq = remove_smooth_background(q_grid, iq)

    # 4. form factors
    f, f2 = compute_fq_f2(exp.composition, q_grid)

    # 5. normalization → S(Q)
    sq = normalize_iq(iq, f2)

    # 6. F(Q)
    fq = compute_fq(q_grid, sq)

    # 7. optional Lorch window
    if config.lorch:
        fq *= lorch_window(q_grid, config.qmax)

    # 8. G(R)
    r, gr = compute_gr(fq, q_grid, config.rmax)

    return PDFResult(
        q=q_grid,
        fq=fq,
        gr=gr,
        r=r,
    )


if __name__ == "__main__":
    pattern = Pattern()
    exp = Experiment()
    config = PDFConfig()

    pdf = compute_pdf(pattern=pattern, exp=exp, config=config)

    import matplotlib.pyplot as plt

    plt.plot(pdf.q, pdf.gr)
    plt.show()
