import io
from os.path import abspath, dirname, join
from setuptools import setup,find_packages


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(
  name = 'lazyearth',                # Name project the same with folder
  packages = ['lazyearth'],          # Name project the same with folder
  version = '1.0.32',                 # version
  license='MIT', 
  description = 'Python earth science package',    #Show on PyPi
  long_description=DESCRIPTION,
  author = 'Tun Kedsaro',            #          
  author_email = 'Tun.k@ku.th',      #
  url = 'https://github.com/Tun555/lazyearth',  #
  download_url = 'https://github.com/Tun555/lazyearth/archive/refs/tags/v0.0.15.zip',                                      #  
  keywords = ['geo','oepn data cube','earth'],      # When someone search
  # Dont add any library bz It's gonna error waiting
  include_package_data=True,         # Create another file (models)
  install_requires=[                 # Package that use
        'numpy',
        'matplotlib'
    ],  
  classifiers=[    
    'Development Status :: 1 - Planning',  
    'Intended Audience :: Education', 
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Version pathon that we test    
    'Programming Language :: Python :: 3.8',
  ],
)