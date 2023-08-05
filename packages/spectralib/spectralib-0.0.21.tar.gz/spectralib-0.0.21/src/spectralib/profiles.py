import numpy as np
import scipy.stats as stats
import scipy.special as sp
import random
import matplotlib.pyplot as plt


def gaussian(length, mean, std_dev):
    x = np.linspace(-5 * std_dev, 5 * std_dev, length)
    y = np.exp(-(x - mean) ** 2 / (2 * std_dev ** 2))
    return y
def exponential_decay(length, tau):
    x = np.linspace(0, 5 * tau, length)
    y = np.exp(-x / tau)
    return y
def log_normal(length, mean, std_dev):
    x = np.linspace(0, 10 * std_dev, length)
    y = (1 / (x * std_dev * np.sqrt(2 * np.pi))) * np.exp(-(np.log(x) - mean) ** 2 / (2 * std_dev ** 2))
    return y
def lorentzian(length, x0, gamma):
    x = np.linspace(x0 - 10 * gamma, x0 + 10 * gamma, length)
    y = (1 / np.pi) * (gamma / ((x - x0) ** 2 + gamma ** 2))
    return y
def weibull(length, k, lambd):
    x = np.linspace(0, 5 * lambd, length)
    y = (k / lambd) * ((x / lambd) ** (k - 1)) * np.exp(-((x / lambd) ** k))
    return y
def gompertz(length, eta, b):
    x = np.linspace(0, 5, length)
    y = eta * b * np.exp(-b * x) * np.exp(-eta * (np.exp(-b * x) - 1))
    return y
def rayleigh(length, sigma):
    x = np.linspace(0, 5 * sigma, length)
    y = (x / sigma ** 2) * np.exp(-x ** 2 / (2 * sigma ** 2))
    return y
def gamma_distribution(length, k, theta):
    x = np.linspace(0, 5 * k * theta, length)
    y = stats.gamma.pdf(x, k, scale=theta)
    return y
def cauchy(length, x0, gamma):
    x = np.linspace(x0 - 10 * gamma, x0 + 10 * gamma, length)
    y = 1 / (np.pi * gamma * (1 + ((x - x0) / gamma) ** 2))
    return y
def chi_squared(length, k):
    x = np.linspace(0, 5 * k, length)
    y = stats.chi2.pdf(x, k)
    return y
def inverse_gaussian(length, mu, lambd):
    x = np.linspace(0, 5 * mu, length)
    y = (np.sqrt(lambd / (2 * np.pi * x ** 3))) * np.exp(-(lambd * (x - mu) ** 2) / (2 * mu ** 2 * x))
    return y
def pareto(length, xm, alpha):
    x = np.linspace(xm, 5 * xm, length)
    y = (alpha * xm ** alpha) / (x ** (alpha + 1))
    return y
def maxwell_boltzmann(length, a):
    x = np.linspace(0, 5 * a, length)
    y = np.sqrt(2 / np.pi) * (x ** 2) * np.exp(-x ** 2 / (2 * a ** 2)) / a ** 3
    return y
def laplace(length, mu, b):
    x = np.linspace(mu - 5 * b, mu + 5 * b, length)
    y = (1 / (2 * b)) * np.exp(-abs(x - mu) / b)
    return y
def erlang(length, k, lambd):
    x = np.linspace(0, 5 * k / lambd, length)
    y = (lambd ** k) * (x ** (k - 1)) * np.exp(-lambd * x) / np.math.factorial(k - 1)
    return y
def rice(length, v, s):
    x = np.linspace(0, 5 * (v + s), length)
    y = (x / s**2) * np.exp(-(x**2 + v**2) / (2 * s**2)) * np.i0(x * v / s**2)
    return y
def airy(length, x0):
    x = np.linspace(-5, 5, length) + x0
    y = sp.airy(x)[0]
    return y
def bessel(length, n):
    x = np.linspace(0, 20, length)
    y = sp.jn(n, x)
    return y
def hyperbolic_secant(length, x0, a):
    x = np.linspace(-5 * a, 5 * a, length) + x0
    y = 1 / np.cosh(x / a)
    return y
def raised_cosine(length, x0, a):
    x = np.linspace(x0 - 5 * a, x0 + 5 * a, length)
    y = (1 + np.cos((x - x0) * np.pi / a)) / 2
    return y
def blackman(length):
    x = np.linspace(0, 1, length)
    y = 0.42 - 0.5 * np.cos(2 * np.pi * x) + 0.08 * np.cos(4 * np.pi * x)
    return y
def sinc(length, x0, a):
    x = np.linspace(x0 - 5 * a, x0 + 5 * a, length)
    y = np.sinc(x / a)
    return y
def sine_cardinal(length, x0, a):
    x = np.linspace(x0 - 5 * a, x0 + 5 * a, length)
    y = np.sin(np.pi * (x - x0) / a) / (np.pi * (x - x0) / a)
    return y
def gaussian_pulse(length, x0, a, f):
    x = np.linspace(x0 - 5 * a, x0 + 5 * a, length)
    y = np.exp(-a * (x - x0) ** 2) * np.cos(2 * np.pi * f * (x - x0))
    return y
def exponential_pulse(length, x0, a, f):
    x = np.linspace(x0, x0 + 5 * a, length)
    y = np.exp(-a * (x - x0)) * np.cos(2 * np.pi * f * (x - x0))
    return y
def triangular_pulse(length, x0, width):
    x = np.linspace(x0 - width, x0 + width, length)
    y = np.maximum(1 - abs(x - x0) / width, 0)
    return y
def sawtooth_pulse(length, x0, width):
    x = np.linspace(x0 - width, x0 + width, length)
    y = (2 * abs(x - x0) / width) % 2 - 1
    return y
def cosine_pulse(length, x0, width):
    x = np.linspace(x0 - width, x0 + width, length)
    y = 0.5 * (1 + np.cos(np.pi * (x - x0) / width)) * (abs(x - x0) <= width)
    return y
def hyperbolic_tangent(length, x0, a):
    x = np.linspace(x0 - 5 * a, x0 + 5 * a, length)
    y = np.tanh((x - x0) / a)
    return y
def bi_exponential_decay(length, tau1, tau2):
    x = np.linspace(0, 5 * max(tau1, tau2), length)
    y = (np.exp(-x / tau1) - np.exp(-x / tau2)) / (tau1 - tau2)
    return y
def stretched_exponential(length, tau, beta):
    x = np.linspace(0, 5 * tau, length)
    y = np.exp(-(x / tau) ** beta)
    return y
def double_gaussian(length, mean1, std_dev1, mean2, std_dev2):
    x = np.linspace(-5 * max(std_dev1, std_dev2), 5 * max(std_dev1, std_dev2), length)
    y = np.exp(-(x - mean1) ** 2 / (2 * std_dev1 ** 2)) + np.exp(-(x - mean2) ** 2 / (2 * std_dev2 ** 2))
    return y
def gaussian_mixture(length, mean1, std_dev1, mean2, std_dev2, w1, w2):
    x = np.linspace(-5 * max(std_dev1, std_dev2), 5 * max(std_dev1, std_dev2), length)
    y = w1 * np.exp(-(x - mean1) ** 2 / (2 * std_dev1 ** 2)) + w2 * np.exp(-(x - mean2) ** 2 / (2 * std_dev2 ** 2))
    return y
def poisson(length, lambd):
    x = np.arange(length)
    y = np.exp(-lambd) * np.power(lambd, x) / np.vectorize(np.math.factorial)(x)
    return y
def negative_binomial(length, r, p):
    x = np.arange(length)
    y = sp.comb(x + r - 1, x) * (p ** r) * ((1 - p) ** x)
    return y
def beta_distribution(length, alpha, beta):
    x = np.linspace(0, 1, length)
    y = (x ** (alpha - 1)) * ((1 - x) ** (beta - 1)) / sp.beta(alpha, beta)
    return y
def double_exponential(length, tau1, tau2):
    x = np.linspace(0, 5 * max(tau1, tau2), length)
    y = 0.5 * (np.exp(-x / tau1) + np.exp(-x / tau2))
    return y
def logistic(length, mu, s):
    x = np.linspace(mu - 5 * s, mu + 5 * s, length)
    y = np.exp(-(x - mu) / s) / (s * (1 + np.exp(-(x - mu) / s)) ** 2)
    return y
def generalized_normal(length, mu, alpha, beta):
    x = np.linspace(mu - 5 * alpha, mu + 5 * alpha, length)
    y = (beta / (2 * alpha * sp.gamma(1 / beta))) * np.exp(-(abs(x - mu) / alpha) ** beta)
    return y
def power_law(length, x_min, alpha):
    x = np.linspace(x_min, 5 * x_min, length)
    y = (alpha - 1) * (x_min ** (alpha - 1)) * (x ** (-alpha))
    return y
def students_t(length, nu):
    x = np.linspace(-5 * np.sqrt(nu / (nu - 2)), 5 * np.sqrt(nu / (nu - 2)), length)
    y = sp.gamma((nu + 1) / 2) / (np.sqrt(nu * np.pi) * sp.gamma(nu / 2)) * (1 + (x ** 2) / nu) ** (-(nu + 1) / 2)
    return y
def geometric(length, p):
    x = np.arange(1, length + 1)
    y = p * (1 - p) ** (x - 1)
    return y
def bernoulli(length, p):
    x = np.array([0, 1])
    y = np.array([1 - p, p])
    return np.repeat(x, np.ceil(length / 2))[:length], y
def gumbel(length, mu, beta):
    x = np.linspace(mu - 5 * beta, mu + 5 * beta, length)
    z = (x - mu) / beta
    y = (1 / beta) * np.exp(-(z + np.exp(-z)))
    return y
def frechet(length, alpha, s, m):
    x = np.linspace(m, m + 5 * s, length)
    z = ((x - m) / s) ** (-alpha)
    y = (alpha / s) * (z / (x - m)) * np.exp(-z)
    return y
def levy(length, c):
    x = np.linspace(0, 5 * c, length)
    y = (np.sqrt(c / (2 * np.pi * x ** 3))) * np.exp(-c / (2 * x))
    return y
def kummer(length, a, b, z):
    x = np.linspace(0, z, length)
    y = sp.hyp1f1(a, b, x)
    return y
def pearson_vii(length, mu, omega, m):
    x = np.linspace(mu - 5 * omega, mu + 5 * omega, length)
    y = (2 ** (1 - m) / (omega * sp.gamma(m))) * (1 + ((x - mu) / omega) ** 2) ** (-m)
    return y
def beta_prime(length, alpha, beta):
    x = np.linspace(0, 5 * alpha / (alpha + beta), length)
    y = (x ** (alpha - 1) * (1 + x) ** (-(alpha + beta))) / sp.beta(alpha, beta)
    return y
def skew_normal(length, mu, sigma, alpha):
    x = np.linspace(mu - 5 * sigma, mu + 5 * sigma, length)
    y = 2 * stats.norm.pdf(x, mu, sigma) * stats.norm.cdf(alpha * x)
    return y
def generalized_extreme_value(length, mu, sigma, k):
    x = np.linspace(mu - 5 * sigma, mu + 5 * sigma, length)
    z = (x - mu) / sigma
    if k == 0:
        y = (1 / sigma) * np.exp(-z) * np.exp(-np.exp(-z))
    else:
        y = (1 / sigma) * (1 + k * z) ** (-1 / k - 1) * np.exp(-(1 + k * z) ** (-1 / k))
    return y
def dirichlet(length, alpha):
    x = np.random.dirichlet(alpha, size=length)
    return x
def kumaraswamy(length, a, b):
    x = np.linspace(0, 1, length)
    y = a * b * (x ** (a - 1)) * (1 - x ** a) ** (b - 1)
    return y
def voigt_profile(length, mu, sigma, gamma):
    x = np.linspace(mu - 5 * max(sigma, gamma), mu + 5 * max(sigma, gamma), length)
    y = np.real(sp.wofz(((x - mu) + 1j * gamma) / (sigma * np.sqrt(2)))) / (sigma * np.sqrt(2 * np.pi))
    return y
def alpha_stable(length, alpha, beta, mu, sigma):
    x = np.linspace(mu - 5 * sigma, mu + 5 * sigma, length)
    y = stats.levy_stable.pdf(x, alpha, beta, loc=mu, scale=sigma)
    return y
def random_profile(length):
    profile_functions = [
        gaussian, exponential_decay, log_normal, lorentzian, weibull, gompertz,
        rayleigh, gamma_distribution, cauchy, chi_squared, inverse_gaussian,
        pareto, maxwell_boltzmann, laplace, erlang, rice, airy, bessel,
        hyperbolic_secant, raised_cosine, blackman, sinc, sine_cardinal,
        gaussian_pulse, exponential_pulse, triangular_pulse, sawtooth_pulse,
        cosine_pulse, hyperbolic_tangent, bi_exponential_decay, stretched_exponential,
        double_gaussian, gaussian_mixture, poisson, negative_binomial, beta_distribution,
        double_exponential, logistic, generalized_normal, spectralib_skew_normal, power_law,
        students_t, spectralib_levy, geometric, bernoulli, gumbel, frechet, levy,
        kummer, pearson_vii, beta_prime, skew_normal, generalized_extreme_value
    ]

    func = random.choice(profile_functions)
    args = []

    if func in [gaussian, log_normal, inverse_gaussian, maxwell_boltzmann, laplace, rice]:
        args = [length, random.uniform(-5, 5), random.uniform(0.1, 5)]
    elif func in [exponential_decay, rayleigh, students_t, spectralib_levy, levy]:
        args = [length, random.uniform(0.1, 5)]
    elif func in [lorentzian, cauchy, cosine_pulse, hyperbolic_tangent]:
        args = [length, random.uniform(-5, 5), random.uniform(0.1, 5)]
    elif func in [weibull, erlang]:
        args = [length, random.randint(1, 5), random.uniform(0.1, 5)]
    elif func in [gompertz]:
        args = [length, random.uniform(0.1, 5), random.uniform(0.1, 5)]
    elif func in [gamma_distribution, chi_squared, pareto, gumbel]:
        args = [length, random.uniform(0.1, 5), random.uniform(0.1, 5)]
    elif func in [frechet]:
        args = [length, random.uniform(0.1, 5), random.uniform(0.1, 5), random.uniform(0.1, 5)]
    elif func in [blackman]:
        args = [length]
    elif func in [airy, bessel, hyperbolic_secant, raised_cosine, sinc, sine_cardinal, gaussian_pulse, exponential_pulse, triangular_pulse, sawtooth_pulse, bi_exponential_decay, stretched_exponential, double_gaussian, gaussian_mixture, poisson, negative_binomial, beta_distribution, double_exponential, logistic, generalized_normal, spectralib_skew_normal, power_law, geometric, bernoulli, kummer, pearson_vii, beta_prime, skew_normal, generalized_extreme_value]:
        args = [length] + [random.uniform(0.1, 5) for _ in range(func.__code__.co_argcount - 1)]

    return func(*args)

def normalize_area(array):
    area = np.trapz(array)  # Calculate the area under the curve using the trapezoidal rule
    normalized_array = array / area  # Normalize the array such that the area under the curve is 1
    return normalized_array


length = 1000
rows = 9
columns = 16

fig, axes = plt.subplots(rows, columns, figsize=(24, 12))

for r in range(rows):
    for c in range(columns):
        random_1d_profile = random_profile(length)
        axes[r, c].plot(np.arange(length), random_1d_profile)
        axes[r, c].grid(True)

fig.suptitle("Random 1D Profiles", fontsize=24)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()