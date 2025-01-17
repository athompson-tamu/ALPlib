# Production Cross Sections
# All cross sections in cm^2
# All energies in MeV

from .constants import *
from .fmath import *
from .decay import *
from .form_factors import *

def nuclear_ff(t, m, z, a):
    # Parameterization of the coherent nuclear form factor (Tsai, 1986)
    # t: MeV
    # m: nucleus mass
    # z: atomic number
    # a: number of nucleons
    return (2*m*z**2) / (1 + t / 164000*np.power(a, -2/3))**2




def atomic_elastic_ff(t, z):
    # Coherent atomic form factor parameterization (Tsai, 1986)
    # Fit based on Thomas-Fermi model
    # t: MeV
    # m: nucleus mass
    # z: atomic number
    b = 184*np.power(2.718, -1/2)*np.power(z, -1/3) / M_E
    return (z*t*b**2)**2 / (1 + t*b**2)**2



#### Photon coupling ####

def free_primakoff_dsigma_dt(t, s, ma, M, g):
    num = ALPHA * g**2 * (t*(M**2 + s)*ma**2 - (M * ma**2)**2 - t*((s-M**2)**2 + s*t) - t*(t-ma**2)/2)
    denom = 4*t**2 * ((M + ma)**2 - s)*((M - ma)**2 - s)
    return heaviside(num/denom, 0.0) * (num / denom)




class PrimakoffSigmaFF:
    # Primakoff scattering with Nuclear and Atomic Form factors
    def __init__(self, mat: Material):
        self.mat = mat
        self.z = mat.z[0]
        self.M = mat.m[0]
        self.helm_ff = NuclearHelmFF(mat)
        self.atomic_ff = ElectronElasticFF(mat)
    
    def dsigma_dt(self, t, s, ma, M, g):
        dsigma_dt = free_primakoff_dsigma_dt(t, s, ma, M, g)
        return dsigma_dt * (self.helm_ff(sqrt(-t)) + self.atomic_ff(sqrt(-t)))

    def __call__(self, egamma, ma, g):
        s = 2*egamma*self.M + self.M**2
        pa_cm2 = (s - self.M**2)**2 / (4*s)
        tmin = ma**2 - 2*egamma*(sqrt(pa_cm2 + ma**2) + sqrt(pa_cm2))
        tmax = ma**2 - 2*egamma*(sqrt(pa_cm2 + ma**2) - sqrt(pa_cm2))
        
        return quad(self.dsigma_dt, tmin, tmax, args=(s, ma, self.M, g,))[0]




def primakoff_dsigma_dtheta(theta, energy, z, ma, g=1):
    # Primakoff scattering production diffxs by theta (γ + A -> a + A)
    if energy < ma:
        return 0
    pa = sqrt(energy**2 - ma**2)
    t = 2*energy*(pa*cos(theta) - energy) + ma**2
    ff = 1 #_nuclear_ff(t, ma, z, 2*z)
    return ALPHA * (g * z * ff * pa**2 / t)**2 * sin(theta)**3 / 4




def primakoff_nsigma(energy, z, ma, g=1):
    # Primakoff production total xs, numerical eval. (γ + A -> a + A)
    return quad(primakoff_dsigma_dtheta, 0, pi, args=(energy,z,ma,g), limit=3)[0]




def primakoff_sigma_tsai(energy, z, a, ma, g):
    # Primakoff production total xs (γ + A -> a + A)
    # Tsai, '86 (ma << E)
    if energy < ma:
        return 0
    M_E = 0.511
    prefactor = (1 / 137 / 4) * (g ** 2)
    return prefactor * ((z ** 2) * (log(184 * power(z, -1 / 3)) \
        + log(403 * power(a, -1 / 3) / M_E)) \
        + z * log(1194 * power(z, -2 / 3)))




def primakoff_sigma(eg, g, ma, z, r0 = 2.2e-10 / METER_BY_MEV):
    # inverse-Primakoff scattering total xs (Creswick et al)
    # r0: screening parameter
    prefactor = (g * z)**2 / (2*137)
    eta2 = r0**2 * eg**2
    return heaviside(eg-ma, 0.0)*prefactor * (((2*eta2 + 1)/(4*eta2))*log(1+4*eta2) - 1)




def epem_to_alp_photon_dsigma_de(ea, ep, g=1.0, ma=1.0, z=1):
    # e+ e- annihilation into gamma ALP via a virtual photon
    s = 2 * M_E * (M_E + ep)
    ps_cm = sqrt((s - ma**2)**2 / (4*s))
    pp_cm = sqrt(((s - 2*M_E**2)**2 - 4*M_E**4)/ (4*s))
    es_cm = sqrt(ps_cm**2 + ma**2)
    ep_cm = sqrt(pp_cm**2 + M_E**2)

    beta = sqrt(ep**2 - M_E**2) / (M_E + ep)
    gamma = power(1-beta**2, -0.5)

    costheta =  (ea/gamma - es_cm)/(beta*ps_cm)

    t = ma**2 + M_E**2 - 2 * (ep_cm * es_cm - pp_cm * ps_cm * costheta)

    m_st = z * 4*pi*ALPHA*g**2 * (2*s*M_E**4 + 2*M_E**2 * (ma**4 - s*ma**2 - 2*s*t) \
        + s*(ma**4 - 2*ma**2 * (s + t) + s**2 + 2*s*t + 2*t**2))/s**2
    
    jacobian = 2 * pp_cm / gamma / beta
    
    return heaviside(ep - max((ma**2 - M_E**2)/(2*M_E), M_E), 1.0) * jacobian * m_st / (16*pi*(s - 4*M_E**2)*s)






#### Electron coupling ####

def compton_sigma(eg, g, ma, z=1):
    # Compton scattering total cross section (γ + e- > a + e-)
    # Taken from 0807.2926. Validated.
    s = 2*eg*M_E + M_E**2
    p0 = 0.5*(2*eg*M_E + ma**2)/sqrt(s)
    k0 = (eg*M_E + M_E**2)/sqrt(s)
    p = sqrt(p0**2 - ma**2)
    k = sqrt(s) - k0
    
    prefactor = heaviside(eg-ma,0.0)*(z*ALPHA*g**2 / (8*s)) * (p/k)
    return prefactor * (-3 + (M_E**2 - ma**2)/s + s*power(ma / (2*eg*M_E),2) \
                        + (1 - (ma**2 / (eg*M_E)) + (ma**2 * (ma**2 - 2*M_E**2)/(2*power(eg*M_E,2)))) \
                            * (sqrt(s)/p)*log((2*p0*k0 + 2*p*k - ma**2)/(2*p0*k0 - 2*p*k - ma**2)))




def compton_dsigma_dea(ea, eg, g, ma, z=1):
    # Differential cross-section dS/dE_a. (γ + e- > a + e-)
    a = 1 / 137
    aa = g ** 2 / 4 / pi
    s = 2 * M_E * eg + M_E ** 2
    x = ((ma**2 / (2*eg*M_E)) - ea / eg + 1)

    xmin = ((s - M_E**2)*(s - M_E**2 + ma**2) 
            - (s - M_E**2)*sqrt((s - M_E**2 + ma**2)**2 - 4*s*ma**2))/(2*s*(s-M_E**2))
    xmax = ((s - M_E**2)*(s - M_E**2 + ma**2) 
            + (s - M_E**2)*sqrt((s - M_E**2 + ma**2)**2 - 4*s*ma**2))/(2*s*(s-M_E**2))

    thresh = heaviside(eg - ma, 0.0)*heaviside(x-xmin,0.0)*heaviside(xmax-x,0.0)
    return z * thresh * (1 / eg) * pi * a * aa / (s - M_E ** 2) * (x / (1 - x) * (-2 * ma ** 2 / (s - M_E ** 2) ** 2
                                                                * (s - M_E ** 2 / (1 - x) - ma ** 2 / x) + x))




def compton_dsigma_domega(theta, Ea, ma, ge):
    # Differential cross-section dS/dOmega_a. (γ + e- > a + e-)
    y = 2*M_E*Ea + ma**2
    pa = sqrt(Ea**2 - ma**2)
    e_gamma = 0.5*y/(M_E + Ea - pa*cos(theta))

    prefactor = ge**2 * ALPHA * e_gamma / (4*pi*2*pa*M_E**2)
    return prefactor * (1 + 4*(M_E*e_gamma/y)**2 - 4*M_E*e_gamma/y - 4*M_E*e_gamma*(ma*pa*sin(theta))**2 / y**3)




def brem_dsigma_dea_domega(Ea, thetaa, Ee, g, ma, z):
    # Differential cross section d^2 Sigma/(dE_a dOmega) for ALP bremsstrahlung (e- Z -> e- Z a)
    # Tsai, 1986
    theta_max = max(sqrt(ma*M_E)/Ee, power(ma/Ee, 3/2))
    x = Ea / Ee
    l = (Ee * thetaa / M_E)**2
    U = l*x*M_E**2 + x*M_E**2 + ((1-x)*ma**2) / x
    tmin = (U / (2*Ee*(1-x)))**2
    a = 111*power(z, -1/3)/M_E
    aPrime = 773*power(z, -2/3)/M_E

    # form factor 
    chi = z**2 * (log(power(a*M_E*(1+l),2) / (a**2 * tmin + 1)) - 1) \
        + z * (log(power(aPrime*M_E*(1+l),2) / (aPrime**2 * tmin + 1)) - 1)

    prefactor = heaviside(chi, 0.0) * heaviside(theta_max - thetaa, 0.0) * ((ALPHA * g)**2 / (4*pi**2)) * Ee / U**2

    return chi * prefactor * (x**3 - 2*(ma*x)**2 * (1-x)/U  \
                                + 2*(ma/U)**2 * (x*(ma*(1-x))**2 + M_E**2 * x**3 * (1-x)))




def brem_dsigma_dea(Ea, Ee, g, ma, z):
    # Differential cross section dSigma/dE_a for ALP bremsstrahlung (e- Z -> e- Z a)
    # Tsai, 1986
    r0 = ALPHA / M_E
    x = Ea / Ee
    f = power(ma / (x * M_E), 2) * (1 - x)
    ln_el = log(184*power(z, -1/3))
    ln_inel = log(1194*power(z, -2/3))

    prefactor = 2 * r0**2 * g**2 / 4 / pi / Ee  # divide by Ee to change dsigma/dx into dsigma/dEa
    phase_space = ((x * (1 + f/1.5)/power(1+f, 2)) * (z**2 * ln_el + z * ln_inel) \
                        + x * (z**2 + z) * ((1+f)*log(1+f)/(3*f**2) - (1 + 4*f + 2*f**2)/(3 * f * power(1+f, 2))))
    return prefactor * phase_space * heaviside(phase_space, 0.0)




def brem_sigma(Ee, g, ma, z=1):
    # Total axion bremsstrahlung production cross section (e- Z -> e- Z a)
    # Tsai 1986
    #ea_max = Ee * (1 - max(power(M_E/ma, 2), power(ma/Ee, 2)))
    ea_max = Ee * (1 - power(ma/Ee, 2))
    return heaviside(Ee-ma,0.0)*quad(brem_dsigma_dea, ma, ea_max, args=(Ee, g, ma, z,))[0]




def brem_sigma_v2(Ee, g, ma, z=1):
    # Total axion bremsstrahlung production cross section (e- Z -> e- Z a)
    # Tsai 1986
    return heaviside(Ee-ma,0.0)*quad(brem_dsigma_dea, ma, Ee*0.9999, args=(Ee, g, ma, z,))[0]




def brem_sigma_mc(Ee, g, ma, z=1, nsamples=100):
    ea_max = Ee * (1 - power(ma/Ee, 2))
    ea_rnd = np.random.uniform(ma, ea_max, nsamples)
    mc_vol = (Ee - ma)/nsamples
    return mc_vol * np.sum(brem_dsigma_dea(ea_rnd, Ee, g, ma, z))




def resonance_sigma(ee, ma, g):
    # Resonant production cross section (e- e+ -> a)
    s = 2*M_E*ee
    return (12 * pi / ma**2) * (power(W_ee(g, ma)/2, 2)/((sqrt(s) - ma)**2 + power(W_ee(g, ma)/2, 2)))




def resonance_peak(g, ma):
    # Returns the peak value of the resonance production cross section (e- e+ -> a)
    #return pi * g**2 / (2 * M_E)
    return 2*pi*M_E*power(g / ma, 2) / sqrt(1 - power(2*M_E/ma, 2))




def associated_dsigma_dcos_CM(costheta_cm, ep_lab, ma, g, z=1):
    # Associated production from pair annihilation (e+ e- -> \gamma a)
    # Calculated with Mathematica
    s = 2*M_E*(ep_lab + M_E)
    ea_cm = sqrt(power(s - ma**2, 2) / (4*s) + ma**2)
    ep_cm = sqrt(M_E * (ep_lab + M_E) / 2)
    pa_cm = sqrt(ea_cm**2 - ma**2)
    pp_cm = sqrt(ep_cm**2 - M_E**2)
    t = ma**2 + M_E**2 - 2 * (ep_cm * ea_cm - pp_cm * pa_cm * costheta_cm)

    u_prop = (M_E**2 + ma**2 - s - t)
    t_prop = (M_E**2 - t)
    tmast = t * (-ma**2 + s + t)

    Mt2 = -4*((-M_E**2 * (s + ma**2)) + 3*M_E**4 + tmast)/t_prop**2
    Mu2 = -4*((M_E**2 * (ma**2 - 3*s - 4*t)) + 7*M_E**4 + tmast)/u_prop**2
    MtMu = 4*((M_E**2 * (s - 2*t)) - 3*M_E**4 + tmast)/(u_prop*t_prop)

    M2 = Mt2 + Mu2 + 2*MtMu
    jacobian = 2 * ep_cm * ea_cm  # dt/dcostheta

    prefactor = z * (4*pi*ALPHA) * g**2
    
    return heaviside(ep_lab - max((ma**2 - M_E**2)/(2*M_E), M_E), 1.0) * prefactor * jacobian * M2 / (16*pi*(s - 4*M_E**2)*s)




def brem_dsigma_dea_vector(Ea, Ee, coupling, ma, z):
    # Vector bremsstrahlung from an electron/positron beam with energy Ee
    # gives dsigma/dEa in the IWW approximation where Ea is the outgoing vector energy [1712.05706]
    # takes vector coupling and mass ma, and target material proton number z
    x = Ea / Ee
    ln_el = log(184*power(z, -1/3))
    ln_inel = log(1194*power(z, -2/3))

    chi = z**2 * ln_el + z * ln_inel
    
    prefactor = chi * (4*ALPHA**2 * coupling**2) / (4*pi)  # using coupling = e * epsilon if you want a dark photon
    return (1/Ee) * prefactor * (1 - x + x**2 / 3) / ((ma**2 * (1-x) / x) + x * M_E**2)




def brem_dsigma_dx_vector(x, coupling, ma, z):
    # Vector bremsstrahlung from an electron/positron beam with energy Ee
    # gives dsigma/dx in the IWW approximation where Ea is the outgoing vector energy [1712.05706]
    # takes vector coupling and mass ma, and target material proton number z
    ln_el = log(184*power(z, -1/3))
    ln_inel = log(1194*power(z, -2/3))

    chi = z**2 * ln_el + z * ln_inel
    
    prefactor = chi * (4*ALPHA**2 * coupling**2) / (4*pi)  # using coupling = e * epsilon if you want a dark photon
    return prefactor * (1 - x + x**2 / 3) / ((ma**2 * (1-x) / x) + x * M_E**2)




def dsig_dEv_dcostheta_vector_brem_etl(Ev, costheta, ttilde, Ebeam, mV, MTarget, ZTarget, ATarget):
    #Exact Tree-Level Dark Photon Bremsstrahlung  
    #e (ep) + Z -> e (epp) + V (w) + Z
    #result it dsigma/dx/dcostheta where x=E_darkphoton/E_beam and theta is angle between beam and dark photon

    x = Ev
    Jacobian = 1.0/Ebeam

    # kinematic boundaries
    if x*Ebeam < mV:
        return 0.
    
    k = np.sqrt((x * Ebeam)**2 - mV**2)
    p = np.sqrt(Ebeam**2 - M_E**2)
    V = np.sqrt(p**2 + k**2 - 2*p*k*costheta)
    
    
    utilde = -2 * (x*Ebeam**2 - k*p*costheta) + mV**2
    
    discr = utilde**2 + 4*MTarget*utilde*((1-x)*Ebeam + MTarget) + 4*MTarget**2 * V**2
    # kinematic boundaries
    if discr < 0:
        return 0.
        
    Qplus = V * (utilde + 2*MTarget*((1-x)*Ebeam + MTarget)) + ((1-x)*Ebeam + MTarget) * np.sqrt(discr)
    Qplus = Qplus/(2*((1-x)*Ebeam + MTarget)**2-2*V**2)
    
    Qminus = V * (utilde + 2*MTarget*((1-x)*Ebeam + MTarget)) - ((1-x)*Ebeam + MTarget) * np.sqrt(discr)
    Qminus = Qminus/(2*((1-x)*Ebeam + MTarget)**2-2*V**2)
    
    Qplus = np.fabs(Qplus)
    Qminus = np.fabs(Qminus)
    
    tplus = 2*MTarget*(np.sqrt(MTarget**2 + Qplus**2) - MTarget)
    tminus = 2*MTarget*(np.sqrt(MTarget**2 + Qminus**2) - MTarget)

    # Physical region checks
    if tplus < tminus:
        return 0.
    
    tconv = (2*MTarget*(MTarget + Ebeam)*np.sqrt(Ebeam**2 + M_E**2)/(MTarget*(MTarget+2*Ebeam) + M_E**2))**2
    t = ttilde*tconv
    if t > tplus or t < tminus:
        return 0.
            
    q0 = -t/(2*MTarget)
    q = np.sqrt(t**2/(4*MTarget**2)+t)
    costhetaq = -(V**2 + q**2 + M_E**2 -(Ebeam + q0 -x*Ebeam)**2)/(2*V*q)

    # kinematic boundaries
    if np.fabs(costhetaq) > 1.:
        return 0.
    mVsq2mesq = (mV**2 + 2*M_E**2)
    Am2 = -8 * MTarget * (4*Ebeam**2 * MTarget - t*(2*Ebeam + MTarget)) * mVsq2mesq
    A1 = 8*MTarget**2/utilde
    Am1 = (8/utilde) * (MTarget**2 * (2*t*utilde + utilde**2 + 4*Ebeam**2 * (2*(x-1)*mVsq2mesq - t*((x-2)*x+2)) + 2*t*(-mV**2 + 2*M_E**2 + t)) - 2*Ebeam*MTarget*t*((1-x)*utilde + (x-2)*(mVsq2mesq + t)) + t**2*(utilde-mV**2))
    A0 = (8/utilde**2) * (MTarget**2 * (2*t*utilde + (t-4*Ebeam**2*(x-1)**2)*mVsq2mesq) + 2*Ebeam*MTarget*t*(utilde - (x-1)*mVsq2mesq))
    Y = -t + 2*q0*Ebeam - 2*q*p*(p - k*costheta)*costhetaq/V 
    W= Y**2 - 4*q**2 * p**2 * k**2 * (1 - costheta**2)*(1 - costhetaq**2)/V**2
    
    if W == 0.:
        print("x, costheta, t = ", [x, costheta, t])
        print("Y, q, p, k, costheta, costhetaq, V" ,[Y, q, p, k, costheta, costhetaq, V])
        
    # kinematic boundaries
    if W < 0:
        return 0.
    
    phi_integral = (A0 + Y*A1 + Am1/np.sqrt(W) + Y * Am2/W**1.5)/(8*MTarget**2)

    formfactor_separate_over_tsquared = Gelastic_inelastic_over_tsquared(t, ZTarget, ATarget)
    
    ans = formfactor_separate_over_tsquared*np.power(ALPHA, 3) * k * Ebeam * phi_integral/(p*np.sqrt(k**2 + p**2 - 2*p*k*costheta))
    
    return(ans*tconv*Jacobian)