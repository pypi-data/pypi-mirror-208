import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mtANN", 
    version="0.1.5",
    # py_modules=['mtANN','mtANN.model', 'mtANN.utils'],
    author="Yi-Xuan Xiong",
    author_email="xyxuana@mails.ccnu.edu.cn",
    description="Ensemble Multiple References for Single-cell RNA Seuquencing Data Annotation and Unseen Cells Identification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=['pandas', 'numpy',
    'scanpy','scipy','scikit-learn',
    'torch','giniclust3','rpy2'],
)