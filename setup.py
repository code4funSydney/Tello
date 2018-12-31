from setuptools import setup,find_packages
setup(
      name = 'Tello',
      version = '0.1',
      py_modules=['tello'],
      install_requires = [
          'opencv-python',
          'pillow',
          'pygame'
      ]
  )
