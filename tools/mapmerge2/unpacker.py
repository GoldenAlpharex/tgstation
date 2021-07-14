import os
import io
import bidict
import random
import sys
# tools_file = os.path.join(os.getcwd(), "tools/mapmerge2")
# sys.path.append(tools_file)
from dmm import *
import dmm
# sys.path.pop()
# from . import dmm as dmm_module
# from .dmm import *
from collections import namedtuple

DMMU_HEADER = "//MAP CONVERTED BY unpacker.py THIS HEADER COMMENT PREVENTS RECONVERSION, DO NOT REMOVE"
ENCODING = 'utf-8'

Coordinate = namedtuple('Coordinate', ['x', 'y', 'z'])


class DMMU(dmm.DMM):
    """Class storing everything needed to convert a .dmm file into an unpacked .dmmu format."""
    __slots__ = ['key_length', 'size', 'dictionary', 'grid', 'header']

    def __init__(self, key_length, size):
        self.key_length = key_length
        self.size = size
        self.dictionary = bidict.bidict()
        self.grid = {}
        self.header = None

    @staticmethod
    def from_file(fname):
        """Method that parses through a given .dmm file (fname) and returns an object of type DMMU."""
        with open(fname, 'r', encoding=ENCODING) as f:
            return dmm._parse(f.read(), DMMU)

    @staticmethod
    def from_bytes(bytes):
        """Method that parses through a bytes object (bytes) and returns an object of type DMMU."""
        return dmm._parse(bytes.decode(ENCODING), DMMU)

    def to_file(self, fname, *, tgm = False):
        """Method that saves the current DMMU object into a .dmmu file."""
        self._presave_checks()
        with open(fname, 'w', newline='\n', encoding=ENCODING) as f:
            save_dmmu(self, f)

    def to_bytes(self, *, tgm = False):
        """Method that saves the current DMMU object into a bytes file I guess, I actually have no clue how this works."""
        self._presave_checks()
        bio = io.BytesIO()
        with io.TextIOWrapper(bio, newline='\n', encoding=ENCODING) as f:
            save_dmmu(self, f)
            f.flush()
            return bio.getvalue()

    def __repr__(self):
        return f"DMMU(size={self.size}, key_length={self.key_length}, dictionary_size={len(self.dictionary)})"

    @staticmethod
    def get_paths_from_user():
        """Function that gets the user to provide an existing map source path and that allows them to specify or not a custom output path and name.

        Returns:
        * map_src_path: str - Assured to be a valid path to an existing .dmm file.
        * map_dst_path: str - The destination of the unpacked (.dmmu) map, by default it will be \"MapTools/output/ORIGINAL_MAP_NAME.dmmu\"

        Returns nothing if any exception occurs during the process."""
        try:
            require_absolute_path = True if input("Is this map located outside of the current repository? [Y/n] ") == "Y" else False
            map_src_path: str
            origin_directory = os.getcwd()
            while True :
                if (require_absolute_path) :
                    map_src_path = input("Absolute path to the .dmm file (including the file and its extension):\n  ")
                else :
                    map_src_path = os.path.join(os.getcwd(), input("Relative path to the .dmm file, starting from the first folder it enters in the repo, with file name and extension:\n  "))
                    os.chdir(origin_directory)

                if (os.path.splitext(map_src_path)[1] == ".dmm" and os.path.exists(map_src_path)) :
                    break
                else :
                    print("Invalid path, please try again.")

            custom_output = True if input("Do you want the output to be in a specific location? (Default is in tools/MapTools/output) [Y/n] ") == "Y" else False
            map_dst_path: str
            if (custom_output) :
                map_dst_path = input("Absolute path to the destination: ")
            else :
                map_dst_path = os.path.join(origin_directory, "tools/MapTools/output/")

            if (not os.path.exists(map_dst_path)) :
                os.mkdir(map_dst_path)

            custom_name = True if input("Do you want the output to have a specific name? (Default is the name of the original map) [Y/n] ") == "Y" else False
            map_dst_name: str
            if (custom_name) :
                map_dst_name = input("File name: ")
            else :
                map_dst_name = os.path.splitext(os.path.split(map_src_path)[1])[0]
            map_dst_path = os.path.join(map_dst_path, map_dst_name) + ".dmmu"

            return map_src_path, map_dst_path

        except Exception as e:
            print(e)


def save_dmmu(dmmu: DMMU, output):
    """Function that saves a DMMU object (dmmu) into a file by writing to it.

    Arguments:
    * dmmu: DMMU - The DMMU object to save.
    * output - The file that the DMMU object is saved into/as.
    """
    output.write(f"{DMMU_HEADER}\n")
    if dmmu.header:
        output.write(f"{dmmu.header}\n")

    max_x, max_y, max_z = dmmu.size
    for z in range(1, max_z + 1):
        output.write("\n")
        for x in range(1, max_x + 1):
            for y in range(1, max_y + 1):
                output.write(f"({x},{y},{z}) = (\n")
                write_tile(dmmu.dictionary[dmmu.grid[x, y, z]], output)
                output.write(")\n")


def write_tile(content, output):
    """Write the content of a tile (content) to a file (output)"""
    for index, thing in enumerate(content):
        in_quote_block = False
        in_varedit_block = False
        for char in thing:
            if in_quote_block:
                if char == '"':
                    in_quote_block = False
                output.write(char)
            elif char == '"':
                in_quote_block = True
                output.write(char)
            elif not in_varedit_block:
                if char == "{":
                    in_varedit_block = True
                    output.write("{\n\t")
                else:
                    output.write(char)
            elif char == ";":
                output.write(";\n\t")
            elif char == "}":
                output.write("\n\t}")
                in_varedit_block = False
            else:
                output.write(char)
        if index < len(content) - 1:
            output.write(",\n")


def main():
    map_src_path, map_dst_path = DMMU.get_paths_from_user()
    map_packed: DMMU
    map_packed = DMMU.from_file(map_src_path)
    map_packed.to_file(map_dst_path)



if __name__ == "__main__" :
	main()
