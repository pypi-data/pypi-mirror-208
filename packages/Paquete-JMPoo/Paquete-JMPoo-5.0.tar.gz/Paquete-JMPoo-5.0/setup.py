from setuptools import setup, find_packages

setup(
    name='Paquete-JMPoo',
    version='5.0',
    description='Un paquete de saludo y despedida',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='JMPoo',
    author_email='jmpoo@gmail.dev',
    url='https://www.jmpoo.dev',
    license_files=['LICENSE'],
    packages=find_packages(),
    scripts=[],
    test_suite='tests',
    install_requires=[paq.strip() for paq in open("requirements.txt").readlines()],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
    
