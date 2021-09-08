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

### Generators and Fluxes that inherit AxionFlux

### Detection Classes and Event Rates

## Production and Detection Cross Sections

## Decay Modes

## Crystal Scattering

# Examples
