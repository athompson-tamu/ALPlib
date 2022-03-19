# Welcome to ALPlib.

### This is a python library for performing physics calculations for axion-like-particles (ALPs).
### Examples and usage instructions incoming.


# Required tools
* python >3.7
    * numpy
    * scipy
    * mpmath
    * numba (coming soon)



# Classes and Methods

## Constants and Conventions
* Global constants (SM parameters, unit conversions, etc.) are stored in `constants.py` and have the naming convention `GLOBAL_CONSTANT_NAME`
* All units in alplib are in MeV, cm, kg, and s by default unless specifically stated, for example densities given in g/cm^2.

## The Material class
The `Material` class is a container for the physical constants and parameters pertaining to the materials used in experimental beam targets and detectors.
There are a number of material parameters stored in a JSON dictionary in `data/mat_params.json`, named according to the chemical name of the material, e.g. 'Ar' or 
'CsI'. One would initialize a detector or beam target, for instance, in the following way;
```
target_DUNE = Material('C')
det_DUNE = Material('Ar')
```
Further specifications for the volumes of the target/detector can also be specified for each instance that you may be interested in. The optional parameters
`fiducial_mass` (in kg)
```
det_DUNE = Material('Ar', fiducial_mass=50000)
```

## The AxionFlux super class
The class `fluxes.AxionFlux` is a super-class that can be inherited by any class that models a specific instance of a source of axion flux. It's most basic members are the `axion_energy` and `axion_flux` arrays, which together make a list of pairs of energies (in MeV) and event weights (in counts/second). Any class that inherits `AxionFlux` should populate `axion_energy` and `axion_flux` during its simulation routine - this flux class can then be passed to event generators (e.g. `fluxes.PhotonEventGenerator()`) to generate scattering or decay event weights at a detector module.

`AxionFlux` also has a default propagate method (which can be modified depending on the specific instance of the class inheriting `AxionFlux`) that looks at `AxionFlux.lifetime()` to propagate the flux weights to the detector. 



### Generators and Fluxes that inherit AxionFlux

### Detection Classes and Event Rates

## Production and Detection Cross Sections

## MatrixElement and Monte Carlo Methods
The super class `MatrixElement2` and its inheritors offers a way to embed any 2->2 scattering process 1 2 -> 3 4. One simply needs to input the masses `m1`, `m2`, `m3`, `m4`, and the `__call__` method will return the squared matrix element as a function of the Mandelstam variables `s` and `t`. Below we outline the monte carlo simulation algorithm for 2-to-2 scattering as an example;

![](/documentation/alplib_mc_notes1.png)

![](/documentation/alplib_mc_notes2.png)

As an example, in `generators.py` we call the class `Scatter2to2MC` from `cross_section_mc.py`. Generating samples should look like this;
```
mc.lv_p1 = LorentzVector(Ea0, 0.0, 0.0, np.sqrt(Ea0**2 - self.mx**2))
mc.lv_p2 = LorentzVector(self.det_m, 0.0, 0.0, 0.0)
mc.scatter_sim()

cosines, dsdcos = mc.get_cosine_lab_weights()
e3, dsde = mc.get_e3_lab_weights()
```
where we have made use of the `LorentzVector` class.

## Decay Modes

## Crystal Scattering

# Examples
