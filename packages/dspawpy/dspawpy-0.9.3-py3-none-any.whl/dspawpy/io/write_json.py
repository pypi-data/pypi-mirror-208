# -*- coding: utf-8 -*-


def write_atoms(fileobj, atom_info):
    fileobj.write("DS-PAW Structure\n")
    fileobj.write("  1.00\n")
    lattice = atom_info["Lattice"]

    fileobj.write("%10.6f %10.6f %10.6f\n" % (lattice[0], lattice[1], lattice[2]))
    fileobj.write("%10.6f %10.6f %10.6f\n" % (lattice[3], lattice[4], lattice[5]))
    fileobj.write("%10.6f %10.6f %10.6f\n" % (lattice[6], lattice[7], lattice[8]))

    elements = [atom["Element"] for atom in atom_info["Atoms"]]
    elements_set = []
    elements_number = {}
    for e in elements:
        if e in elements_set:
            elements_number[e] = elements_number[e] + 1
        else:
            elements_set.append(e)
            elements_number[e] = 1

    for e in elements_set:
        fileobj.write("  " + e)
    fileobj.write("\n")

    for e in elements_set:
        fileobj.write("%5d" % (elements_number[e]))
    fileobj.write("\n")
    if atom_info["CoordinateType"] == "Direct":
        fileobj.write("Direct\n")
    else:
        fileobj.write("Cartesian\n")
    for atom in atom_info["Atoms"]:
        fileobj.write("%10.6f %10.6f %10.6f\n" % tuple(atom["Position"]))
    fileobj.write("\n")


def write_VESTA_format(atom_info: dict, data: list, filename="DS-PAW.vesta"):
    with open(filename, "w") as file:
        write_atoms(file, atom_info)
        for d in data:
            file.write("%5d %5d %5d\n" % tuple(atom_info["Grid"]))
            i = 0
            while i < len(d):
                for j in range(10):
                    file.write("%10.5f " % d[i])
                    i += 1
                    if i >= len(d):
                        break
                file.write("\n")

            file.write("\n")
