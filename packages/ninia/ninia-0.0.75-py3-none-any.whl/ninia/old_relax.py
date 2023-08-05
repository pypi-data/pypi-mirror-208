"""
Alex Summers
The current function of this script is to create a Relax object to handle relevant information
and create a generic input file and bash script for use with Quantum Espresso.
For more information see the GitHub repository at https://github.com/ajsummers/ninia.
"""


import pkg_resources
import warnings
import sys
import os
import re

from fnmatch import filter as flt  # Native filter() function is used as well
import pandas as pd
import numpy as np


starting_dir = os.getcwd()

# Pull in molar mass data from separate csv file
mm_data = pkg_resources.resource_stream(__name__, 'data/mm_of_elements.csv')
molarmass_df = pd.read_csv(mm_data, encoding=sys.stdout.encoding, index_col=0)


class Relax:

    def __init__(self, prefix=None, functional=None):

        # TODO - class parameters prefix, functional, and pseudo_dir not getting set if None type

        if prefix is None:
            warnings.warn('Prefix not defined. Setting to "untitled".', UserWarning)
        self.prefix = prefix

        if functional is None:
            warnings.warn('Functional not defined. Using BEEF-vdW by default.', UserWarning)
            self.functional = 'beef'
        else:
            self.functional = functional

        # TODO - Add additional checks for pseudopotential directory?
        # Initialize class parameters

        self.pseudo_dir = None

        self.geometry = None
        self.output_dir = None
        self.pseudo_dir = None
        self.input_dir = None
        self.nstep = None

        self.num_atoms = None
        self.num_elem = None
        self.ecutwfc = None
        self.ecutrho = None

        self.conv_thr = None
        self.mixing_beta = None
        self.electron_maxstep = None

        self.atomic_species = None
        self.cell_parameters = None
        self.atomic_positions = None
        self.k_points = None

        self.job_type = None
        self.partition = None

        self.memory = None
        self.cpus = None
        self.hours = None
        self.nk = 1

        self.locked = False
        self.catkit = True

    def get_position_info_(self, ase_object):

        atomic_positions = ''
        positions = ase_object.get_positions().tolist()
        symbols = ase_object.get_chemical_symbols()
        unique_symbols = list(set(symbols))
        atom_count = len(positions)

        if self.locked is False:
            locked = np.zeros((atom_count, 3))
        elif len(self.locked) != atom_count:
            raise ValueError('Locked dimensions do not match position dimensions.')
        else:
            locked = self.locked

        for atom_set in zip(symbols, positions, locked):
            atomic_positions += f'   {atom_set[0]}\t{np.round(atom_set[1][0], 8):.8f}'
            atomic_positions += f'\t{np.round(atom_set[1][1], 8):.8f}\t{np.round(atom_set[1][2], 8):.8f}'
            atomic_positions += f' {atom_set[2][0]:1.0f} {atom_set[2][1]:1.0f} {atom_set[2][2]:1.0f}\n'

        self.num_atoms = atom_count
        self.num_elem = len(unique_symbols)
        self.atomic_positions = atomic_positions

        return unique_symbols

    def get_species_info_(self, species_list):

        os.chdir(self.pseudo_dir)
        list_upf = flt(os.listdir('.'), '*.[Uu][Pp][Ff]')
        species_string = ''

        for species in species_list:

            r = re.compile(rf'{species}[_|.]\S+\Z', flags=re.IGNORECASE)
            match = list(filter(r.match, list_upf))[0]
            mw_species = molarmass_df.loc[species][0]

            species_string += f'   {species}\t{mw_species}\t{match}\n'

        os.chdir(starting_dir)
        self.atomic_species = species_string

    def get_cell_parameters_(self, ase_object):

        supercell = ase_object.get_cell()
        if not self.catkit:
            supercell[2][2] = 2 * np.max(ase_object.get_positions().T[2])
        cell_parameters = ''

        for dimension in supercell:
            cell_parameters += f'{dimension[0]:.14f}\t{dimension[1]:.14f}\t{dimension[2]:.14f}\n'

        self.cell_parameters = cell_parameters

    @staticmethod
    def check_directory_(directory):

        if not os.path.isdir(directory):
            raise NotADirectoryError(f'{directory} is not a valid directory.')

    def set_prefix_(self):

        # TODO - test if this actually omits repeat input files

        os.chdir(self.input_dir)
        if not (os.path.isfile(f'{self.prefix}.i')):
            os.chdir(self.output_dir)
            if (os.path.isdir(f'{self.prefix}.save')) or (os.path.isfile(f'{self.prefix}.wfc1')):
                self.prefix += '_1'

            i = 1
            while (os.path.isdir(f'{self.prefix}.save')) or (os.path.isfile(f'{self.prefix}.wfc1')):
                i += 1
                self.prefix = f'{self.prefix.rstrip("0123456789")}{i}'

            os.chdir(starting_dir)
            return True

        else:
            os.chdir(starting_dir)
            return False

    def set_directories(self, inputdir=None, outputdir=None, pseudodir=None):

        if (self.pseudo_dir is None) and (pseudodir is None):
            warnings.warn('Pseudopotential directory still not specified. Loading '
                          'geometry will likely result in an error.', UserWarning)
        elif (self.pseudo_dir is None) and (pseudodir is not None):
            self.check_directory_(pseudodir)
            self.pseudo_dir = pseudodir
        elif (self.pseudo_dir is not None) and (pseudodir is not None):
            print(f'Changing pseudodirectory to {pseudodir}.')
            self.check_directory_(pseudodir)
            self.pseudo_dir = pseudodir

        if inputdir is not None:
            self.check_directory_(inputdir)
            self.input_dir = inputdir
        else:
            self.input_dir = starting_dir

        if outputdir is not None:
            self.check_directory_(outputdir)
            self.output_dir = outputdir

    def load_geometry(self, ase_object):

        self.geometry = ase_object
        species_list = self.get_position_info_(self.geometry)
        self.get_species_info_(species_list)
        self.get_cell_parameters_(self.geometry)

    def set_parameters(self, ecutwfc=None, ecutrho=None, conv_thr=None, mixing_beta=None, k_points=None,
                       electron_maxstep=None, functional=None, nstep=None, locked=None, catkit=False):

        if (self.functional is None) and (functional is None):
            warnings.warn('Functional is still not specified. Creating input will likely result in an error.',
                          UserWarning)
        elif (self.functional is None) and (functional is not None):
            self.functional = functional
        elif (self.functional is not None) and (functional is not None):
            print(f'Changing functional to {functional}')

        if (self.ecutwfc is None) and (ecutwfc is None):
            self.ecutwfc = 30.0
        elif ecutwfc is not None:
            self.ecutwfc = ecutwfc

        if (self.ecutrho is None) and (ecutrho is None):
            self.ecutrho = 4 * self.ecutwfc
        elif ecutrho is not None:
            self.ecutrho = ecutrho

        if (self.conv_thr is None) and (conv_thr is None):
            self.conv_thr = '1.0d-8'
        elif conv_thr is not None:
            self.conv_thr = str(conv_thr).replace('e', 'd')

        if (self.mixing_beta is None) and (mixing_beta is None):
            self.mixing_beta = '0.7d0'
        elif mixing_beta is not None:
            self.mixing_beta = str(mixing_beta).replace('e', 'd')

        if (self.k_points is None) and (k_points is None):
            self.k_points = ' 4 4 4 0 0 0'
        elif k_points is not None:
            k_string = ''
            for point in k_points:
                k_string += f' {point}'
            self.k_points = k_string

        if (self.electron_maxstep is None) and (electron_maxstep is None):
            self.electron_maxstep = 100
        elif electron_maxstep is not None:
            self.electron_maxstep = electron_maxstep

        if (self.nstep is None) and (nstep is None):
            self.nstep = 100
        elif nstep is not None:
            self.nstep = nstep

        if (self.locked is None) and (locked is None):
            self.locked = False
        elif locked is not None:
            self.locked = locked

        self.catkit = catkit

    def create_input(self):  # Note - removed 'repeat' parameter. What was this for?

        if self.set_prefix_():

            runtime_error = ''
            runtime_error += ' self.geometry' if not self.geometry else ''
            runtime_error += ' self.prefix' if not self.prefix else ''
            runtime_error += ' self.output_dir' if not self.output_dir else ''
            runtime_error += ' self.pseudo_dir' if not self.pseudo_dir else ''
            runtime_error += ' self.input_dir' if not self.input_dir else ''
            runtime_error += ' self.num_atoms' if not self.num_atoms else ''
            runtime_error += ' self.num_elem' if not self.num_elem else ''
            runtime_error += ' self.ecutwfc' if not self.ecutwfc else ''
            runtime_error += ' self.functional' if not self.functional else ''
            runtime_error += ' self.conv_thr' if not self.conv_thr else ''
            runtime_error += ' self.mixing_beta' if not self.mixing_beta else ''
            runtime_error += ' self.atomic_species' if not self.atomic_species else ''
            runtime_error += ' self.cell_parameters' if not self.cell_parameters else ''
            runtime_error += ' self.atomic_positions' if not self.atomic_positions else ''
            runtime_error += ' self.k_points' if not self.k_points else ''

            if runtime_error is not '':
                raise RuntimeError(f'Missing{runtime_error}')

            input_template = pkg_resources.resource_string(__name__, 'input/relax.i').decode(sys.stdout.encoding)
            compiled_fstring = compile(input_template, '<fstring_from_file', 'eval')
            formatted_relax = eval(compiled_fstring)

            os.chdir(self.input_dir)
            with open(f'{self.prefix}.i', 'w+') as f:
                f.write(formatted_relax)

            os.chdir(starting_dir)
            print(f'Created input file {self.prefix}.i')

        else:

            print(f'Muted redundant input file {self.prefix}.i')

    def create_job(self, job_type=None, partition=None, memory=None, cpus=None, hours=None):

        if job_type is None:
            self.job_type = 'pbs.sh'
        else:
            self.job_type = job_type

        if partition is None:
            self.partition = 'general'
        else:
            self.partition = partition

        if memory is None:
            self.memory = 50
        else:
            self.memory = memory

        if cpus is None:
            self.cpus = 8
        else:
            self.cpus = cpus

        if hours is None:
            self.hours = 100
        else:
            self.hours = hours

        bash_template = pkg_resources.resource_string(__name__, f'input/{self.job_type}').decode(sys.stdout.encoding)
        compiled_bash_fstring = compile(bash_template, '<fstring_from_file', 'eval')
        formatted_bash_relax = eval(compiled_bash_fstring)

        os.chdir(self.input_dir)
        if not (os.path.isfile(f'{self.prefix}.sh')):

            with open(f'{self.prefix}.sh', 'w+') as f:
                f.write(formatted_bash_relax)

            os.chdir(starting_dir)
            print(f'Created bash file {self.prefix}.sh')

        else:

            print(f'Muted redundant bash file {self.prefix}.sh')
