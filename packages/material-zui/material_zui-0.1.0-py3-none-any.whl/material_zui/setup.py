from setuptools import setup
import setuptools

# with open("readme.md", "r") as fh:
#     long_description = fh.read()
with open("src/material_zui/readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='material_zui',
    version='0.0.6',
    # url='https://github.com/username/my_module',
    author='chauhmnguyen',
    author_email='chauhoangminhnguyen@gmail.com',
    description='Material Zui',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=['cv2', 'PIL'],
    classifiers=[
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
