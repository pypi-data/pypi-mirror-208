from setuptools import setup, find_packages


setup(name='FunPayAPI',
      version="1.0.5",
      description='Прослойка между FunPayAPI и клиентом.',
      author='Woopertail',
      author_email='woopertail@gmail.com',
      url='https://github.com/woopertail/FunPayAPI',
      packages=find_packages("."),
      license='GPL2',
      keywords='funpay bot api tools',
      install_requires=['requests==2.28.1', 'beautifulsoup4', 'requests_toolbelt==0.10.1'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
      ]
)
