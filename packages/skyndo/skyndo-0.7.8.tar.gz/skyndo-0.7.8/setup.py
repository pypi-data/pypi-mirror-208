from setuptools import setup, find_packages

setup(
    name='skyndo',
    version='0.7.8',
    packages=['skyndo'],
    include_data=True,
    data_files = [
        ('data', ['skyndo/data/model.pkl']),
    ],
    install_requires=[
        'pandas',
        'scikit-learn',
        'numpy'],
    author='Nishan Obeyesekera',
    author_email='nishandhanu21@gmail.com',
    description='A package to predict the class of astronomical objects for given parameters using a Random Forest model',
    url='https://github.com/NishanD21/Astronomical-Objects-Classification/tree/main/skyndo',
)