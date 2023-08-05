# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hyperbolic3d']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'pyvista>=0.32.1,<0.33.0']

extras_require = \
{'docs': ['sphinx>=5.3.0,<6.0.0',
          'sphinx-rtd-theme>=1.1.1,<2.0.0',
          'sphinxcontrib-napoleon>=0.7,<0.8',
          'sphinxcontrib-restbuilder>=0.3,<0.4']}

setup_kwargs = {
    'name': 'pyhyperbolic3d',
    'version': '0.1.0',
    'description': "Hyperbolic meshes for 'PyVista'",
    'long_description': "# PyHyperbolic3D\n\n<!-- badges: start -->\n[![Documentation status](https://readthedocs.org/projects/pyhyperbolic3d/badge/)](https://pyhyperbolic3d.readthedocs.io/en/latest/index.html)\n<!-- badges: end -->\n\nPython stuff for drawing 3D hyperbolic polyhedra with 'PyVista'.\n\n```\npip install pyhyperbolic3d\n```\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/icosahedron.png)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/icosahedron_slider.gif)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/icosahedron_colored.gif)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/BarthHyperbolicpolyhedron.gif)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/PentagrammicPrism.gif)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/GreatDeltoidalIcositetrahedron.gif)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/gircope.gif)\n\n![](https://github.com/stla/PyHyperbolic3D/raw/main/examples/griddip.gif)\n\n#### `gyrotube(A, B, s, r, npoints=300):`\n\nTubular hyperbolic segment.\n\n##### Parameters\n- **`A,B`** points (lists or arrays)\n\n  The two endpoints of the segment.\n\n- **`s`** positive float\n\n   Curvature parameter.\n   \n- **`r`** positive float\n\n   Radius of the tube.\n   \n- **`npoints`** integer\n\n   Number of points along the segment. The default is 300.\n\n##### Returns\nA PyVista mesh ready for inclusion in a plotting region.\n\n___\n\n#### `gyrotriangle(A, B, C, s, depth=5, tol=1e-6):`\n\nHyperbolic triangle.\n\n##### Parameters\n- **`A,B,C`** points (lists or arrays)\n\n  The vertices of the triangle.\n\n- **`s`** positive float\n\n   Curvature parameter.\n   \n- **`depth`** integer\n\n   The number of recursive subdivions. The default is 5.\n\n- **`tol`** small positive float\n\n   The tolerance used to merge duplicated points in the mesh.\nThe default is 1e-6.\n\n##### Returns\nA PyVista mesh ready for inclusion in a plotting region.\n\n\n",
    'author': 'Stéphane Laurent',
    'author_email': 'laurent_step@outook.fr',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/stla/PyHyperbolic3D',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
