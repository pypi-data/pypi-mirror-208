![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/achadwick/python-colorsysx/python-package.yml?branch=main)
![GitHub](https://img.shields.io/github/license/achadwick/python-colorsysx)

# colorsysX

🎨👁️ _Extra, human-relevant, colour spaces derived from RGB_

This package extends the standard Python library's `colorsys` module
with a few additional, useful, colour spaces. The models of colour
provided here are simple, but relevant to human vision and the perceived
lightness of different colour hues.

## Colour models

* **YUV** (specifically, YPbPr): a luma and colour difference model.
* **HCY**: a cylindrical hue, relative chroma, and luma model.
* **GLHS**: a _generalized_ lightness/hue/saturation model.

[YUV][1] has a perceptually relevant lightness term. It can preserve
absolute chroma when manipulating luma.

[HCY][2] is intuitive to use, and its lightness term is the same as
YUV's. It's particularly useful when manipulating colours to meet WCAG
2.2 or draft 3.0 WCAG contrast criteria.

[GLHS][3] is a generalization of the cylindrical coordinate spaces
provided in `colorsysx` and `colorsys`. It can be parameterised to
provide any of the other similar models.

## Interface conventions

```python
from colorsysx import rgb_to_hcy, hcy_to_rgb

h, c, y = rgb_to_hcy(0.5, 0.7, 0.93)
r, g, b = hcy_to_rgb(h, c, y)
```

The conversion functions are named like the builtin `colorsys` module's
functions, and share a very similar interface. For each colour system
ABC, this package provides two functions:

    rgb_to_abc() → a, b, c
    abc_to_rgb() → r, g, b

All inputs and outputs are tuples of 3 floats in the range [0.0, 1.0].
Unlike `colorsysx`, the functions accept optional weighting parameters,
which can be used to tune the colour model being used.

[1]: https://en.wikipedia.org/wiki/YUV#Related_color_models
[2]: https://chilliant.com/rgb2hsv.html
[3]: https://doi.org/10.1006/cgip.1993.1019
