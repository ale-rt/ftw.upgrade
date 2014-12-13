from ftw.builder import builder_registry
from ftw.upgrade.directory import scaffold
import inflection
import os
import shlex
import subprocess


UPGRADE_CODE = '''
from ftw.upgrade import UpgradeStep

class Upgrade(UpgradeStep):
    """{0}
    """

    def __call__(self):
        self.install_upgrade_profile()
'''

TWO_UPGRADES_CODE = UPGRADE_CODE + '''
class SecondUpgrade(UpgradeStep):
    """{0}
    """

    def __call__(self):
        self.install_upgrade_profile()
'''

class UpgradeStepBuilder(object):

    def __init__(self, session):
        self.session = session
        self.name = None
        self.directory = None
        self.title = None
        self.upgrade_code = UPGRADE_CODE

    def named(self, name):
        self.name = name
        return self

    def titled(self, title):
        self.title = title
        return self

    def within(self, directory):
        self.directory = directory
        return self

    def with_upgrade_code(self, code_string):
        self.upgrade_code = code_string
        return self

    def create(self, **kwargs):
        self.validate()
        path = os.path.join(self.directory, self.name)
        os.mkdir(path)
        with open(os.path.join(path, 'upgrade.py'), 'w+') as upgrade_file:
            upgrade_file.write(self.upgrade_code.format(self.title or self.name))
        return path

    def validate(self):
        assert self.name is not None, \
            'Upgrade step requires a name; use named()'
        assert self.directory is not None, \
            'Upgrade step requires a directory; use within()'
        assert os.path.isdir(self.directory), \
            'Path is not a directory: {0}'.format(self.directory)


builder_registry.register('upgrade step', UpgradeStepBuilder)


class UpgradeStepBuilder(object):

    def __init__(self, session):
        self.session = session
        self.destination_version = None
        self.name = None
        self.package = None
        self.profile_builder = None
        self.named('Upgrade')

    def to(self, destination):
        if hasattr(destination, 'strftime'):
            self.destination_version = destination.strftime(scaffold.DATETIME_FORMAT)
        else:
            self.destination_version = destination
        return self

    def named(self, name):
        self.name = name
        return self

    def for_profile(self, profile_builder):
        self.profile_builder = profile_builder
        if self.profile_builder.fs_version is None:
            self.profile_builder.with_fs_version(False)
        return self

    def create(self):
        if self.destination_version is None:
            raise ValueError('A destination version is required.'
                             ' Use .to(datetime(...)).')
        self._set_package()
        self._declare_zcml_directory()
        return self._create_upgrade()

    def _set_package(self):
        self.package = self.profile_builder.package.get_subpackage('upgrades')
        if self.profile_builder.name != 'default':
            self.package = self.package.get_subpackage(self.profile_builder.name)

    def _declare_zcml_directory(self):
        zcml = self.package.get_configure_zcml()

        if getattr(zcml, '_upgrade_step_declarations', None) is None:
            zcml._upgrade_step_declarations = {}

        if zcml._upgrade_step_declarations.get(self.profile_builder.name):
            return

        zcml.include('ftw.upgrade', file='meta.zcml')
        zcml.with_node('upgrade-step:directory',
                       profile=self.profile_builder.profile_name,
                       directory='.')
        zcml._upgrade_step_declarations[self.profile_builder.name] = True

    def _create_upgrade(self):
        name = self.name.replace(' ', '_').replace('\.$', '')
        step_name = '{0}_{1}'.format(self.destination_version,
                                     inflection.underscore(name))
        self.package.with_file(
            os.path.join(step_name, 'upgrade.py'),
            scaffold.PYTHON_TEMPLATE.format(
                classname=inflection.camelize(name),
                docstring=inflection.humanize(
                    inflection.underscore(name))),
            makedirs=True)
        return step_name


builder_registry.register('ftw upgrade step', UpgradeStepBuilder)


SETUP_PY_TEMPLATE = """
from setuptools import setup, find_packages

setup(name='{name}',
      version='1.0.0.dev0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages={namespaces},
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
      ])
"""

NAMESPACE_INIT_TEMPLATE = """
# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
"""

class PackageBuilder(object):

    def __init__(self, session):
        self.session = session
        self.named('test.package')
        self.build_egginfo = False

    def named(self, name):
        self.name = name
        return self

    def with_egginfo(self):
        self.build_egginfo = True
        return self

    def within(self, root_path):
        self.root_path = root_path
        return self

    def create(self):
        paths = {}
        self._create_setup_py(paths)
        self._create_package(paths)
        self._create_upgrades_directory(paths)

        if self.build_egginfo:
            self._build_egginfo()
        return paths

    def _create_setup_py(self, paths):
        setup_py_path = os.path.join(self.root_path, 'setup.py')
        paths.update({'setup.py': setup_py_path})

        with open(setup_py_path, 'w+') as setup:
            setup.write(SETUP_PY_TEMPLATE.format(
                    name=self.name,
                    namespaces=self.name.split('.')[:-1]))

    def _create_package(self, paths):
        code_directory = os.path.join(self.root_path, self.name.replace('.', '/'))
        paths.update({'code_directory': code_directory})

        os.makedirs(os.path.join(code_directory))

        path = self.root_path
        for namespace in self.name.split('.')[:-1]:
            path = os.path.join(path, namespace)
            with open(os.path.join(path, '__init__.py'), 'w+') as namespace_file:
                namespace_file.write(NAMESPACE_INIT_TEMPLATE)

        open(os.path.join(code_directory, '__init__.py'), 'w+').close()

    def _create_upgrades_directory(self, paths):
        upgrades = os.path.join(paths['code_directory'], 'upgrades')
        paths.update({'upgrades': upgrades})
        os.makedirs(upgrades)

    def _build_egginfo(self):
        buildout = os.path.join(self.root_path, 'bin', 'buildout')
        if not os.path.exists(buildout):
            raise Exception('require buildout script at {0} for building egg info.'.format(
                    buildout))

        command = '{0} setup setup.py egg_info'.format(buildout)
        proc = subprocess.Popen(shlex.split(command), cwd=self.root_path,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderrdata = proc.communicate()
        assert proc.returncode == 0, 'Failed to run {0} :\n{1}'.format(
            command, stderrdata)

builder_registry.register('package', PackageBuilder)
