Welcome to Syris's documentation!
=================================

*syris* (**sy**\ nchrotron **r**\ adiation **i**\ maging **s**\ imulation) is a
framework for simulations of X-ray absorption and phase contrast dynamic imaging
experiments, like time-resolved radiography, tomography or laminography. It
includes X-ray sources, various sample shape creation possibilities, complex
refractive index lookup options, motion model and indirect detection model
(scintillator combined with a conventional camera). Phase contrast is simulated
by the Angular spectrum method, which enables one to include various optical
elements in the simulation, e.g. gratings and X-ray lenses.

Compute-intensive algorithms like Fourier transforms, sample shape creation and
free-space propagation are implemented by using OpenCL, which enables one to
execute the code on graphic cards.

There are numerous examples of how to use *syris* described below which ship
directly with the code. Enjoy!


Application Programming Interface
=================================

.. toctree::
   :maxdepth: 2

   api/config
   api/imageprocessing
   api/geometry
   api/materials
   api/opticalelements
   api/math
   api/physics
   api/experiments

   api/bodies
   api/devices
   api/gpu


Usage
=====

.. toctree::
   :maxdepth: 2

   usage/examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
