import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mtANN", 
    version="0.1.3",
    # py_modules=['mtANN','mtANN.model', 'mtANN.utils'],
    author="Yi-Xuan Xiong",
    author_email="xyxuana@mails.ccnu.edu.cn",
    description="Ensemble Multiple References for Single-cell RNA Seuquencing Data Annotation and Unseen Cells Identification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=['pandas>=1.2.3', 'numpy>=1.19.2',
    'scanpy>=1.9.0','scipy>=1.6.1','scikit-learn>=0.24.1',
    'torch>=1.9.1','giniclust3>=1.1.0','rpy2>=3.4.1'],
)