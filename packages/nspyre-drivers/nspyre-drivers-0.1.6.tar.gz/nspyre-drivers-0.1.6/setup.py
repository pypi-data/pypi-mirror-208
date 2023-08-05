# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nspyre_drivers',
 'nspyre_drivers.acton.sp2150i',
 'nspyre_drivers.agiltron',
 'nspyre_drivers.agiltron.ffsw',
 'nspyre_drivers.arduino',
 'nspyre_drivers.arduino.arduino_gpio',
 'nspyre_drivers.beaglebone',
 'nspyre_drivers.beaglebone.beaglebone_gpio',
 'nspyre_drivers.beaglebone.beaglebone_gpio.beaglebone_server',
 'nspyre_drivers.cobolt',
 'nspyre_drivers.cv2_cam',
 'nspyre_drivers.dli_pdu',
 'nspyre_drivers.dlnsec',
 'nspyre_drivers.luminox',
 'nspyre_drivers.ni',
 'nspyre_drivers.oceanoptics',
 'nspyre_drivers.oceanoptics.hr2000es',
 'nspyre_drivers.oceanoptics.hr2000es.oceandirect.sample_pack.Python.Python '
 'VVV',
 'nspyre_drivers.pi',
 'nspyre_drivers.pi.pi710',
 'nspyre_drivers.rigol',
 'nspyre_drivers.rigol.dp832',
 'nspyre_drivers.rohde_schwarz',
 'nspyre_drivers.rohde_schwarz.hmp4040',
 'nspyre_drivers.thorlabs',
 'nspyre_drivers.thorlabs.cld1010',
 'nspyre_drivers.thorlabs.fw102c',
 'nspyre_drivers.thorlabs.pm100d',
 'nspyre_drivers.ximea',
 'nspyre_drivers.zaber']

package_data = \
{'': ['*'],
 'nspyre_drivers': ['rfsoc/*'],
 'nspyre_drivers.arduino.arduino_gpio': ['pin_server/*'],
 'nspyre_drivers.oceanoptics.hr2000es': ['oceandirect/*',
                                         'oceandirect/sample_pack/*',
                                         'oceandirect/sample_pack/C/*',
                                         'oceandirect/sample_pack/CPlusPlus/*',
                                         'oceandirect/sample_pack/CSharp/*',
                                         'oceandirect/sample_pack/LabVIEW/LabVIEW '
                                         '2010/*',
                                         'oceandirect/sample_pack/LabVIEW/LabVIEW '
                                         '2020/*',
                                         'oceandirect/sample_pack/MATLAB/MATLAB '
                                         'VVV/*']}

install_requires = \
['numpy', 'pyserial', 'pyusb', 'pyvisa', 'pyvisa-py']

extras_require = \
{'beaglebone': ['requests'],
 'dli_pdu': ['beautifulsoup4', 'dlipower'],
 'nidaq': ['nidaqmx'],
 'oceanoptics': ['seabreeze'],
 'ximea': ['ximea-py'],
 'zaber': ['zaber-motion']}

setup_kwargs = {
    'name': 'nspyre-drivers',
    'version': '0.1.6',
    'description': 'A set of Python drivers for lab instrumentation.',
    'long_description': "# Drivers\nThis is a set of Python drivers for lab instrumentation. These drivers are \nassociated with [nspyre](https://nspyre.readthedocs.io/en/latest/), but are \nalso suitable for general usage. Unless otherwise specified, drivers are \nprovided under the terms of the MIT license.\n\n## Installation\n\n```bash\npip install nspyre-drivers\n```\n\nCertain drivers require extra dependencies. Those dependencies can be installed \nby specifying a tag during the install. E.g. to install the DLI pdu driver \ndependencies, use:\n\n```bash\npip install nspyre-drivers[dli_pdu]\n```\n\nA full listing of the tags is below.\n\n```\nbeaglebone\ndli_pdu\noceanoptics\nximea\nzaber\n```\n\nFor some USB drivers on Linux, you need to grant user access to the drivers in \norder for VISA to detect them:\nYou should find the udev rules file in the same folder as the driver, then, e.g.:\n\n```bash\nsudo cp src/drivers/thorlabs/cld1010/99-thorlabs-cld1010.rules /etc/udev/rules.d/\n````\n\nCreate a user group for the usb device access:\n\n```bash\nsudo groupadd usbtmc\n```\n\nAdd any relevant users to the group:\n\n```bash\nusermod -aG usbtmc <myuser>\n```\n\nReboot for the changes to take effect.\n\n## Usage\n\nAfter installation, you can use drivers with, e.g.:\n\n```python\nfrom nspyre_drivers.rohde_schwarz.hmp4040.hmp4040 import HMP4040\nwith HMP4040('TCPIP::192.168.0.10::5025::SOCKET') as power_supply:\n\t# set the power supply channel 1 to 5V\n\tpower_supply.set_voltage(1, 5.0)\n```\n\nSee the source for all of the available drivers and the import paths.\n\n## Other Drivers\n\nIn order to minimize reinventing the wheel, below is a list of other sources of \npython instrument drivers. Please contribute if you find other useful sources!\n\n[pycobolt](https://github.com/cobolt-lasers/pycobolt)\n\n## Contributing\n\nIf you want to contribute driver code, please submit it as a \n[pull request](https://nspyre.readthedocs.io/en/latest/contributing.html#forking-pull-requests). This project uses \n[poetry](https://python-poetry.org/). If your driver requires specific \ndependencies beyond those currently in use in the project, you should include \nthem in the pyproject.toml file as extras. See the poetry documentation for \nspecifics on how to declare these dependencies.\n",
    'author': 'Jacob Feder',
    'author_email': 'jacobsfeder@gmail.com',
    'maintainer': 'Jacob Feder',
    'maintainer_email': 'jacobsfeder@gmail.com',
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
