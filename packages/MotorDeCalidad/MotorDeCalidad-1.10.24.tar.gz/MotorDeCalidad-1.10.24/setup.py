from setuptools import setup
setup(name='MotorDeCalidad',
version='1.10.24',
description='Paquete demo de Motor de Calidad',
author='Enzo Ipanaque',
author_email='enzo.ipanaque@ms-peru.com',
long_description=open('README.md').read(),
long_description_content_type='text/markdown',
license='Management Solutions',
packages=['motordecalidad'],
py_modules=['functions','constants','rules','utilities'],
zip_safe=False)