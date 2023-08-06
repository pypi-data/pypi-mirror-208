from setuptools import setup

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

install_requires = [
    'numpy',
    'scikit-image',
    'torch',
    'torchvision',
    'opencv-python',
    'matplotlib',
    'pandas',
    'seaborn'
]

setup(
    name='brinthan_psd',
    version='0.0.1.1',
    description='PSD calc',
    py_modules=["brinthan_psd"],
    package_dir={'': 'src'},
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Brinthan K',
    author_email='kanesalingambrinthan187@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='DeepParticleSD, PSD, Deep Learning, Particle Size Distribution',
    install_requires=install_requires
    )
