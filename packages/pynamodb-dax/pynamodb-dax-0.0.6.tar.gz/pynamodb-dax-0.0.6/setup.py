from setuptools import setup, find_packages


install_requires = [
    'botocore>=1.12.54',
    'python-dateutil>=2.1,<3.0.0',
    'amazon-dax-client>=1.1.7',
    'typing-extensions>=4; python_version<"3.11"',
]

setup(
    name='pynamodb-dax',
    version=__import__('pynamodb').__version__,
    packages=find_packages(),
    url='https://github.com/thanakijwanavit/PynamoDB',
    author='Nic Wanavit (fork)',
    author_email='nwanavit@gmail.com',
    description='fork to pynamodb for supporting dax',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    zip_safe=False,
    license='MIT',
    keywords='python dynamodb amazon dax',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    extras_require={
        'signals': ['blinker>=1.3,<2.0']
    },
    package_data={'pynamodb': ['py.typed']},
)
