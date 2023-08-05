
import re
from ase.build import hcp0001


class Object:

    def __init__(self, file=None, atoms=None):

        if file is None:
            self.file = None
        else:
            self.file = file

        if atoms is None:
            self.atoms = None
        else:
            self.atoms = file

    def ase_from_ouput(self, file=None):

        if file is not None:
            self.file = file

        with open(file, 'r') as f:
            handle = f.read()

        match = r'(?<=ATOMIC_POSITIONS)(.*?)(?=(End final coordinates|\n\n))'
        matches = re.findall(match, handle, flags=re.S)

        element_list, x_list, y_list, z_list = [[], [], [], []]

        last_match = matches[-1]
        formatted = '\n'.join(last_match[0].split('\n')[1:])
        num_atoms = len(formatted.split('\n')) - 1
        for line in formatted.split('\n')[:-1]:
            line_list = line.split()
            element_list.append(line_list[0])
            x_list.append(float(line_list[1]))
            y_list.append(float(line_list[2]))
            z_list.append(float(line_list[3]))

        position_list = [tuple(group) for group in zip(x_list, y_list, z_list)]
        ase_object = hcp0001('H', size=(num_atoms, 1, 1), a=2.7059, c=4.2815)
        ase_object.set_chemical_symbols(element_list)
        ase_object.set_positions(position_list)

        self.atoms = ase_object

