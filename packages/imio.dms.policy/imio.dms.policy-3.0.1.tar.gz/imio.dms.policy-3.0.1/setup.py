from setuptools import setup, find_packages

version = '3.0.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='imio.dms.policy',
      version=version,
      description="DMS policy containing all packages required for dms to work",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='Plone Python IMIO',
      author='IMIO',
      author_email='support@imio.be',
      url='http://svn.communesplone.org/svn/communesplone/imio.dms.policy',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['imio', 'imio.dms'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'Pillow',
          'imio.dms.mail',
          'imio.pyutils',
          'Products.CPUtils',
          'Products.DocFinderTab',
          'collective.behavior.internalnumber',
          'collective.ckeditor',
          'collective.contact.importexport',
          'collective.externaleditor',
          'collective.iconifieddocumentactions',
          'collective.messagesviewlet',
          'collective.monitor',
          'collective.usernamelogger',
          'communesplone.layout',
          'imio.transmogrifier.contact',
          'imio.transmogrifier.iadocs',
          'plonetheme.imioapps',
          'five.z2monitor',
          'Products.PloneHotfix20210518',
          'Products.ZNagios',
          'zc.z3monitor'
      ])
