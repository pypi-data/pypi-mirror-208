# -*- coding: utf-8 -*-

import json

import numpy as np
from pymatgen.core.lattice import Lattice
from pymatgen.core.structure import Structure
from pymatgen.electronic_structure.bandstructure import BandStructureSymmLine
from pymatgen.electronic_structure.core import Orbital, Spin
from pymatgen.electronic_structure.dos import CompleteDos, Dos
from pymatgen.phonon.bandstructure import PhononBandStructureSymmLine
from pymatgen.phonon.dos import PhononDos


def get_dos_data(dos_json: str):
    with open(dos_json, "r") as file:
        dos = json.load(file)

    if dos["DosInfo"]["Project"]:
        return get_complete_dos(dos)
    else:
        return get_total_dos(dos)


def get_total_dos(dos: dict) -> Dos:
    energies = np.asarray(dos["DosInfo"]["DosEnergy"])
    if dos["DosInfo"]["SpinType"] == "none":
        densities = {Spin.up: np.asarray(dos["DosInfo"]["Spin1"]["Dos"])}
    else:
        densities = {
            Spin.up: np.asarray(dos["DosInfo"]["Spin1"]["Dos"]),
            Spin.down: np.asarray(dos["DosInfo"]["Spin2"]["Dos"]),
        }

    efermi = dos["DosInfo"]["EFermi"]

    return Dos(efermi, energies, densities)


def get_complete_dos(dos: dict) -> CompleteDos:
    total_dos = get_total_dos(dos)

    structure = get_structure(dos["AtomInfo"])
    N = len(structure)

    pdos = [{} for i in range(N)]
    number_of_spin = 1 if dos["DosInfo"]["SpinType"] == "none" else 2

    for i in range(number_of_spin):
        spin_key = "Spin" + str(i + 1)
        spin = Spin.up if i == 0 else Spin.down
        project = dos["DosInfo"][spin_key]["ProjectDos"]
        for p in project:
            atom_index = p["AtomIndex"] - 1
            o = p["OrbitIndex"] - 1
            orbit_name = Orbital(o)

            if orbit_name in pdos[atom_index].keys():
                pdos[atom_index][orbit_name].update({spin: p["Contribution"]})
            else:
                pdos[atom_index][orbit_name] = {spin: p["Contribution"]}

    pdoss = {structure[i]: pd for i, pd in enumerate(pdos)}

    return CompleteDos(structure, total_dos, pdoss)


def get_structure(atominfo) -> Structure:
    lattice = np.asarray(atominfo["Lattice"]).reshape(3, 3)
    elements = []
    positions = []
    for atom in atominfo["Atoms"]:
        elements.append(atom["Element"])
        positions.extend(atom["Position"])

    coords = np.asarray(positions).reshape(-1, 3)
    is_direct = atominfo["CoordinateType"] == "Direct"
    return Structure(lattice, elements, coords, coords_are_cartesian=(not is_direct))


def get_structure_from_json(jsonfile: str) -> Structure:
    with open(jsonfile, "r") as file:
        j = json.load(file)
    return get_structure(j["AtomInfo"])


def remove_extra_kpoint(band_data, symmetry_kPoints_index, number_of_band):
    keep_data = []
    for i in range(len(symmetry_kPoints_index) - 1):
        if i == 0:
            start_index = symmetry_kPoints_index[i] - 1
            end_index = symmetry_kPoints_index[i + 1]
        else:
            start_index = symmetry_kPoints_index[i] + 1
            end_index = symmetry_kPoints_index[i + 1]

        tmp = band_data[start_index * number_of_band : end_index * number_of_band]
        keep_data.extend(tmp)
    return keep_data


def get_band_data(band_json: str) -> BandStructureSymmLine:
    with open(band_json, "r") as file:
        band = json.load(file)

    number_of_band = band["BandInfo"]["NumberOfBand"]
    number_of_kpoints = band["BandInfo"]["NumberOfKpoints"]
    if (
        band["BandInfo"]["SpinType"] == "none"
        or band["BandInfo"]["SpinType"] == "non-collinear"
    ):
        number_of_spin = 1
    else:
        number_of_spin = 2

    symmetry_kPoints_index = band["BandInfo"]["SymmetryKPointsIndex"]

    efermi = band["BandInfo"]["EFermi"]
    eigenvals = {}
    for i in range(number_of_spin):
        spin_key = "Spin" + str(i + 1)
        spin = Spin.up if i == 0 else Spin.down

        data = band["BandInfo"][spin_key]["Band"]
        band_data = np.array(data).reshape((number_of_kpoints, number_of_band)).T

        eigenvals[spin] = band_data

    kpoints = np.asarray(band["BandInfo"]["CoordinatesOfKPoints"]).reshape(
        number_of_kpoints, 3
    )

    structure = get_structure(band["AtomInfo"])
    labels_dict = {}

    for i, s in enumerate(band["BandInfo"]["SymmetryKPoints"]):
        labels_dict[s] = kpoints[symmetry_kPoints_index[i] - 1]

    # read projection data
    projections = None
    if "IsProject" in band["BandInfo"].keys():
        if band["BandInfo"]["IsProject"]:
            projections = {}
            number_of_orbit = len(band["BandInfo"]["Orbit"])
            projection = np.zeros(
                (number_of_band, number_of_kpoints, number_of_orbit, len(structure))
            )

            for i in range(number_of_spin):
                spin_key = "Spin" + str(i + 1)
                spin = Spin.up if i == 0 else Spin.down

                data = band["BandInfo"][spin_key]["ProjectBand"]
                for d in data:
                    orbit_index = d["OrbitIndex"] - 1
                    atom_index = d["AtomIndex"] - 1
                    project_data = d["Contribution"]
                    projection[:, :, orbit_index, atom_index] = (
                        np.asarray(project_data)
                        .reshape((number_of_kpoints, number_of_band))
                        .T
                    )

                projections[spin] = projection

    lattice_new = Lattice(structure.lattice.reciprocal_lattice.matrix)
    return BandStructureSymmLine(
        kpoints=kpoints,
        eigenvals=eigenvals,
        lattice=lattice_new,
        efermi=efermi,
        labels_dict=labels_dict,
        structure=structure,
        projections=projections,
    )


def get_phonon_band_data(phonon_band_json: str) -> PhononBandStructureSymmLine:
    with open(phonon_band_json, "r") as file:
        band = json.load(file)

    number_of_band = band["BandInfo"]["NumberOfBand"]
    number_of_kpoints = band["BandInfo"]["NumberOfQPoints"]

    number_of_spin = 1

    symmmetry_kpoints = band["BandInfo"]["SymmetryQPoints"]
    symmetry_kPoints_index = band["BandInfo"]["SymmetryQPointsIndex"]

    eigenvals = {}
    for i in range(number_of_spin):
        spin_key = "Spin" + str(i + 1)
        spin = Spin.up if i == 0 else Spin.down

        data = band["BandInfo"][spin_key]["Band"]
        frequencies = np.array(data).reshape((number_of_kpoints, number_of_band)).T
        eigenvals[spin] = frequencies

    kpoints = np.asarray(band["BandInfo"]["CoordinatesOfQPoints"]).reshape(
        number_of_kpoints, 3
    )

    if "SupercellAtomInfo" in band.keys():
        structure = get_structure(band["SupercellAtomInfo"])
    else:
        structure = get_structure(band["AtomInfo"])
    labels_dict = {}

    for i, s in enumerate(symmmetry_kpoints):
        labels_dict[s] = kpoints[symmetry_kPoints_index[i] - 1]

    lattice_new = Lattice(structure.lattice.reciprocal_lattice.matrix)
    return PhononBandStructureSymmLine(
        qpoints=kpoints,
        frequencies=frequencies,
        lattice=lattice_new,
        has_nac=False,
        labels_dict=labels_dict,
        structure=structure,
    )


def get_phonon_dos_data(phonon_dos_json: str) -> PhononDos:
    with open(phonon_dos_json, "r") as file:
        dos = json.load(file)

    frequencies = np.asarray(dos["DosInfo"]["DosEnergy"])
    densities = dos["DosInfo"]["Spin1"]["Dos"]
    return PhononDos(frequencies, densities)
