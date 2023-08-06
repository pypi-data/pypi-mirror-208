import setuptools 

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
      name='mml_qae',
      version='1.0.1.4',
      description='The packages for the machine learning(just easily learn!) are always hard to study, and difficult to use. Now you have the MyMachineLearning_Quicker_and_Easier! It can maybe help you to use machine learning.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='ETRO_secondleader',
      author_email='ETRO_gfyx@163.com',
      url='https://www.python.org', 
      packages=setuptools.find_packages(),
     ) 