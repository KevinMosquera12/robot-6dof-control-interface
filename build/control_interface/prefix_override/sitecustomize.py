import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/kmosprogram/Escritorio/universidad robotica/robotica/install/control_interface'
