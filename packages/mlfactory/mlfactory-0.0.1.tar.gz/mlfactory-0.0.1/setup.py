import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='mlfactory',  
     version='0.0.1',
     author="Homagni Saha",
     author_email="homagnisaha@gmail.com",
     description="Collection of several machine learning modules which can be applied to diverse projects",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/Homagn/mlfactory",
     packages=setuptools.find_packages(exclude=["mlfactory/applications/superglue_inference/models/weights","mlfactory/applications/segmentation_finetune/CFExp"]),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
