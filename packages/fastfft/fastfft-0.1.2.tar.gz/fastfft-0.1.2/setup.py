# from setuptools import find_packages, setup, Extension
# from Cython.Build import cythonize
# import os
# import json
# import numpy as np
#
# with open("README.md", 'r') as f:
#     long_description = f.read()
#
#
# def read_pipenv_dependencies(fname):
#     """Get from Pipfile.lock default dependencies."""
#     filepath = os.path.join(os.path.dirname(__file__), fname)
#     with open(filepath) as lockfile:
#         lockjson = json.load(lockfile)
#         return [dependency for dependency in lockjson.get('default')]
#
#
# ext_modules = [
#     Extension("maxim_fft",
#               sources=["src/__init__.pyx"],
#               )
# ]
#
# setup(
#     name="fastfft",
#     setup_requires=["cython", "numpy"],
#     version="0.1.1",
#     packages=find_packages(),
#     python_requires='>=3.8',
#     author="Maxim Movshin",
#     description="Discrete Fourier transform implementation by the analog of the Cooley-Tukey algorithm.",
#     long_description=long_description,
#     long_description_content_type='text/markdown',
#     url="https://github.com/BSaaber/fastfft",
#     ext_modules=cythonize(ext_modules),
#     include_dirs=np.get_include(),
#     install_requires=[
#         *read_pipenv_dependencies('Pipfile.lock'),
#     ]
# )




from setuptools import find_packages, setup

import numpy as np
from Cython.Build import cythonize


with open("README.md", 'r') as f:
    long_description = f.read()


setup(
    name="fastfft",
    version="0.1.2",
    packages=find_packages(),
    author="Maxim Movshin",
    description="Discrete Fourier transform implementation by the analog of the Cooley-Tukey algorithm.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/BSaaber/fastfft",
    ext_modules=cythonize(["src/__init__.pyx"]),
    include_dirs=np.get_include(),
    install_requires=[
        'numpy>=1.19.2',
        'PyObjC;platform_system=="Darwin"',
        'PyGObject;platform_system=="Linux"',
        'playsound==1.2.2'
    ]
)
