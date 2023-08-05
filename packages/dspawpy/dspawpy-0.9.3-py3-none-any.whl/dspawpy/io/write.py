"""
Functions to write files
"""

import json
import os

import numpy as np

from dspawpy.io.read import _get_lammps_non_orthogonal_box, load_h5


def _write_xyz_traj(
    structures,
    xyzfile="aimdTraj.xyz",
):
    r"""保存xyz格式的轨迹文件

    Parameters
    ----------
    structures: list
        pymatgen的Structures列表
    xyzfile : str
        写入xyz格式的轨迹文件，默认为aimdTraj.xyz

    Example
    -------
    >>> from dspawpy.io.write import write_xyz_traj
    >>> write_xyz_traj(datafile='aimd.h5', ai=[1,2,3], index=1, xyzfile='aimdTraj.xyz')
    Reading E:\Dev\dspawpy\test\new\aimd.h5 ...
    """
    if not isinstance(structures, list):  # single Structure
        structures = [structures]
    with open(xyzfile, "w") as f:
        # Nstep
        for _, structure in enumerate(structures):
            # 原子数不会变，就是不合并的元素总数
            eles = [s.species_string for s in structure.sites]
            f.write("%d\n" % len(eles))
            # lattice
            lm = structure.lattice.matrix
            f.write(
                'Lattice="%f %f %f %f %f %f %f %f %f" Properties=species:S:1:pos:R:3 pbc="T T T"\n'
                % (
                    lm[0, 0],
                    lm[0, 1],
                    lm[0, 2],
                    lm[1, 0],
                    lm[1, 1],
                    lm[1, 2],
                    lm[2, 0],
                    lm[2, 1],
                    lm[2, 2],
                )
            )
            # position and element
            poses = structure.cart_coords
            for j in range(len(eles)):
                f.write(
                    "%s %f %f %f\n" % (eles[j], poses[j, 0], poses[j, 1], poses[j, 2])
                )

    print(f"{xyzfile} 文件已保存！")


def _write_dump_traj(
    structures,
    dumpfile="aimdTraj.dump",
):
    r"""保存为lammps的dump格式的轨迹文件，暂时只支持正交晶胞

    Parameters
    ----------
    structures: list
        pymatgen的Structures列表
    dumpfile : str
        dump格式的轨迹文件名，默认为aimdTraj.dump

    Example
    -------
    >>> from dspawpy.io.write import write_dump_traj
    >>> write_dump_traj(datafile='aimd.h5', ai=[1,2,3], index=1, dumpfile='aimdTraj.dump')
    Reading E:\Dev\dspawpy\test\new\aimd.h5 ...
    """
    if not isinstance(structures, list):  # single Structure
        structures = [structures]
    with open(dumpfile, "w") as f:
        for n, structure in enumerate(structures):
            lat = structure.lattice.matrix
            eles = [s.species_string for s in structure.sites]
            poses = structure.cart_coords

            box_bounds = _get_lammps_non_orthogonal_box(lat)
            f.write("ITEM: TIMESTEP\n%d\n" % n)
            f.write("ITEM: NUMBER OF ATOMS\n%d\n" % (len(eles)))
            f.write("ITEM: BOX BOUNDS xy xz yz xx yy zz\n")
            f.write(
                "%f %f %f\n%f %f %f\n %f %f %f\n"
                % (
                    box_bounds[0][0],
                    box_bounds[0][1],
                    box_bounds[0][2],
                    box_bounds[1][0],
                    box_bounds[1][1],
                    box_bounds[1][2],
                    box_bounds[2][0],
                    box_bounds[2][1],
                    box_bounds[2][2],
                )
            )
            f.write("ITEM: ATOMS type x y z id\n")
            for i in range(len(eles)):
                f.write(
                    "%s %f %f %f %d\n"
                    % (
                        eles[i],
                        poses[i, 0],
                        poses[i, 1],
                        poses[i, 2],
                        i + 1,
                    )
                )
    print(f"{dumpfile} 文件已保存！")


def write_VESTA(in_filename: str, data_type, out_filename="DS-PAW.vesta"):
    """从包含电子体系信息的json或h5文件中读取数据并写入VESTA格式的文件中

    Parameters
    ----------
    in_filename : str
        包含电子体系信息的json或h5文件路径
    data_type: str
        数据类型，支持 "rho", "potential", "elf", "pcharge", "boundcharge"
    out_filename : str
        输出文件路径, 默认 "DS-PAW.vesta"

    Returns
    --------
    out_filename : file
        VESTA格式的文件

    Examples
    --------
    >>> from dspawpy.io.write import write_VESTA
    >>> write_VESTA("DS-PAW.json", "rho")
    """
    if in_filename.endswith(".h5"):
        data = load_h5(in_filename)
        if data_type.lower() == "rho" or data_type.lower() == "boundcharge":
            _write_VESTA_format(data, ["/Rho/TotalCharge"], out_filename)
        elif data_type.lower() == "potential":
            _write_VESTA_format(
                data,
                [
                    "/Potential/TotalElectrostaticPotential",
                ],
                out_filename,
            )
        elif data_type.lower() == "elf":
            _write_VESTA_format(data, ["/ELF/TotalELF"], out_filename)
        elif data_type.lower() == "pcharge":
            _write_VESTA_format(data, ["/Pcharge/1/TotalCharge"], out_filename)
        else:
            raise NotImplementedError("仅支持rho/potential/elf/pcharge/boundcharge")

    elif in_filename.endswith(".json"):
        with open(in_filename, "r") as fin:
            data = json.load(fin)
        if data_type.lower() == "rho" or data_type.lower() == "boundcharge":
            _write_VESTA_format_json(
                data["AtomInfo"], [data["Rho"]["TotalCharge"]], out_filename
            )
        elif data_type.lower() == "potential":
            _write_VESTA_format_json(
                data["AtomInfo"],
                [
                    data["Potential"]["TotalElectrostaticPotential"],
                ],
                out_filename,
            )
        elif data_type.lower() == "elf":
            _write_VESTA_format_json(
                data["AtomInfo"], [data["ELF"]["TotalELF"]], out_filename
            )
        elif data_type.lower() == "pcharge":
            _write_VESTA_format_json(
                data["AtomInfo"], [data["Pcharge"][0]["TotalCharge"]], out_filename
            )
        else:
            raise NotImplementedError("仅支持rho/potential/elf/pcharge/boundcharge")

    else:
        raise NotImplementedError("仅支持json或h5格式文件")


def write_delta_rho_vesta(AB, A, B, output="delta_rho.vesta"):
    """电荷密度差分可视化

    DeviceStudio暂不支持大文件，临时写成可以用VESTA打开的格式

    Parameters
    ----------
    AB : str
        AB的电荷密度文件路径，可以是h5或json格式
    A : str
        A的电荷密度文件路径，可以是h5或json格式
    B : str
        B的电荷密度文件路径，可以是h5或json格式
    output : str
        输出文件路径，默认 "delta_rho.vesta"

    Returns
    -------
    output : file
        电荷差分（AB-A-B）后的电荷密度文件，

    Examples
    --------
    >>> from dspawpy.io.write import write_delta_rho_vesta
    >>> write_delta_rho_vesta('AB.h5', 'A.h5', 'B.h5', 'delta_rho.vesta')
    >>> write_delta_rho_vesta('AB.json', 'A.json', 'B.json', 'delta_rho.vesta')
    # 甚至可以混写
    >>> write_delta_rho_vesta('AB.h5', 'A.json', 'B.json', 'delta_rho.vesta')
    """
    print(f"读取{AB}...")
    if AB.endswith(".h5"):
        dataAB = load_h5(AB)
        rhoAB = np.array(dataAB["/Rho/TotalCharge"])
        nGrids = dataAB["/AtomInfo/Grid"]
        atom_symbol = dataAB["/AtomInfo/Elements"]
        atom_pos = dataAB["/AtomInfo/Position"]
        latticeConstantMatrix = dataAB["/AtomInfo/Lattice"]
        atom_pos = np.array(atom_pos).reshape(-1, 3)
    elif AB.endswith(".json"):
        atom_symbol = []
        atom_pos = []
        with open(AB, "r") as f1:
            dataAB = json.load(f1)
            rhoAB = np.array(dataAB["Rho"]["TotalCharge"])
            nGrids = dataAB["AtomInfo"]["Grid"]
        for i in range(len(dataAB["AtomInfo"]["Atoms"])):
            atom_symbol.append(dataAB["AtomInfo"]["Atoms"][i]["Element"])
            atom_pos.append(dataAB["AtomInfo"]["Atoms"][i]["Position"])
        atom_pos = np.array(atom_pos)

        latticeConstantMatrix = dataAB["AtomInfo"]["Lattice"]
    else:
        raise ValueError(f"file format must be either h5 or json: {AB}")

    print(f"读取{A}...")
    if A.endswith(".h5"):
        dataA = load_h5(A)
        rhoA = np.array(dataA["/Rho/TotalCharge"])
    elif A.endswith(".json"):
        with open(A, "r") as f2:
            dataA = json.load(f2)
            rhoA = np.array(dataA["Rho"]["TotalCharge"])
    else:
        raise ValueError(f"file format must be either h5 or json: {A}")

    print(f"读取{B}...")
    if B.endswith(".h5"):
        dataB = load_h5(B)
        rhoB = np.array(dataB["/Rho/TotalCharge"])
    elif B.endswith(".json"):
        with open(B, "r") as f3:
            dataB = json.load(f3)
            rhoB = np.array(dataB["Rho"]["TotalCharge"])
    else:
        raise ValueError(f"file format must be either h5 or json: {B}")

    print(f"计算电荷差分...")
    rho = rhoAB - rhoA - rhoB
    rho = np.array(rho).reshape(shape=(nGrids[0], nGrids[1], nGrids[2]))

    element = list(set(atom_symbol))
    element = sorted(set(atom_symbol), key=atom_symbol.index)
    element_num = np.zeros(len(element))
    for i in range(len(element)):
        element_num[i] = atom_symbol.count(element[i])

    latticeConstantMatrix = np.array(latticeConstantMatrix)
    latticeConstantMatrix = latticeConstantMatrix.reshape(3, 3)

    print(f"写入文件{output}...")
    with open(output, "w") as out:
        out.write("DS-PAW_rho\n")
        out.write("    1.000000\n")
        for i in range(3):
            for j in range(3):
                out.write("    " + str(latticeConstantMatrix[i, j]) + "    ")
            out.write("\n")
        for i in range(len(element)):
            out.write("    " + element[i] + "    ")
        out.write("\n")

        for i in range(len(element_num)):
            out.write("    " + str(int(element_num[i])) + "    ")
        out.write("\n")
        out.write("Direct\n")
        for i in range(len(atom_pos)):
            for j in range(3):
                out.write("    " + str(atom_pos[i, j]) + "    ")
            out.write("\n")
        out.write("\n")

        for i in range(3):
            out.write("  " + str(nGrids[i]) + "  ")
        out.write("\n")

        ind = 0
        for i in range(nGrids[0]):
            for j in range(nGrids[1]):
                for k in range(nGrids[2]):
                    out.write("  " + str(rho[i, j, k]) + "  ")
                    ind = ind + 1
                    if ind % 5 == 0:
                        out.write("\n")

    print(f"成功写入 {output}")


def to_file(structure, filename: str, fmt=None, coords_are_cartesian=True):
    r"""往结构文件中写入信息

    Parameters
    ----------
    structure : Structure
        pymatgen的Structure对象
    filename : str
        结构文件名
    fmt : str
        - 结构文件类型，目前支持 'json', 'as', 'hzw', 'pdb', 'xyz', 'dump', 'cif', 'poscar', 'cssr', 'xsf', 'mcsqs', 'prismatic', 'yaml', 'fleur-inpgen'
        - 若不指定，则根据文件名后缀判断
        - 'pdb', 'xyz' 和 'dump' 支持传入多个结构，structure参数可以是一个Structure对象列表；其他类型的文件只支持传入单个结构
    coords_are_cartesian : bool
        - 是否写作笛卡尔坐标，默认为True；否则写成分数坐标形式
        - 此选项暂时仅对 as 和 json 格式有效

    Examples
    --------

    如果不指定 fmt 参数，将尝试根据文件名后缀判断。

    如果要生成 as 结构文件（可用于开始新任务），可参考如下命令:

    >>> from dspawpy.io.structure import build_Structures_from_datafile
    >>> s = build_Structures_from_datafile('neb01.h5', index=1)[0]
    Reading E:\Dev\dspawpy\test\new\neb01.h5 ...
    >>> from dspawpy.io.write import to_file
    >>> to_file(s, filename='PtH.as', coords_are_cartesian=True)
    --> 成功写入文件 E:\Dev\dspawpy\test\new\PtH.as

    如果 Structure 中有磁矩或自由度信息，将会按最完整的格式统一写入，形如 Fix_x, Fix_y, Fix_z, Mag_x, Mag_y, Mag_z，自由度信息默认为 F，磁矩默认为 0.0。可视情况自行手动删除生成的 as 文件中的这些默认信息

    >>> with open('PtH.as') as f:
    ...     print(f.read())
    ...
    Total number of atoms
    3
    Lattice Fix_x Fix_y Fix_z
    5.60580000 0.00000000 0.00000000 F F F
    0.00000000 5.60580000 0.00000000 F F F
    0.00000000 0.00000000 16.81740000 F F F
    Cartesian Fix_x Fix_y Fix_z Mag
    H 2.48770271 3.85219888 6.93647446 F F F 0.0
    Pt 1.40145000 1.40145000 1.98192999 T T T 0.0
    Pt 4.20434996 1.40145000 1.98192999 T T T 0.0

    写成 json 文件，将忽略磁矩和自由度信息

    >>> to_file(s, filename='PtH.json')
    --> 成功写入文件 E:\Dev\dspawpy\test\new\PtH.json

    写成 hzw 文件，也将忽略磁矩和自由度信息

    >>> to_file(s, filename='PtH.hzw')
    --> 成功写入文件 E:\Dev\dspawpy\test\new\PtH.hzw

    写成 pdb 文件，也将忽略磁矩和自由度信息

    >>> to_file(s, filename='PtH.pdb')
    --> 成功写入文件 E:\Dev\dspawpy\test\new\PtH.pdb
    """

    if fmt is None:
        fmt = filename.split(".")[-1]

    if fmt == "json":  # 单个构型
        assert not isinstance(structure, list), "只接受单个构型"
        _to_dspaw_json(structure, filename, coords_are_cartesian)
    elif fmt == "as":
        assert not isinstance(structure, list), "只接受单个构型"
        _to_dspaw_as(structure, filename, coords_are_cartesian)
    elif fmt == "hzw":
        assert not isinstance(structure, list), "只接受单个构型"
        _to_hzw(structure, filename)
    elif fmt == "pdb":  # 可以是多个构型
        _to_pdb(structure, filename)
    elif fmt == "xyz":  # 可以是多个构型
        _write_xyz_traj(structure, filename)
    elif fmt == "dump":  # 可以是多个构型
        _write_dump_traj(structure, filename)
    elif fmt in [
        "cif",
        "poscar",
        "cssr",
        "xsf",
        "mcsqs",
        "prismatic",
        "yaml",
        "fleur-inpgen",
    ]:
        assert not isinstance(structure, list), "只接受单个构型"
        structure.to(filename, fmt=fmt)
    else:
        raise NotImplementedError(f"暂不支持写成 {fmt} 格式")

    print(f"--> 成功写入文件 {os.path.abspath(filename)} ")


def _write_atoms(fileobj, hdf5):
    fileobj.write("DS-PAW Structure\n")
    fileobj.write("  1.00\n")
    lattice = np.asarray(hdf5["/AtomInfo/Lattice"]).reshape(-1, 1)  # 将列表lattice下的多个列表整合
    fileobj.write(
        "%10.6f %10.6f %10.6f\n" % (lattice[0][0], lattice[1][0], lattice[2][0])
    )
    fileobj.write(
        "%10.6f %10.6f %10.6f\n" % (lattice[3][0], lattice[4][0], lattice[5][0])
    )
    fileobj.write(
        "%10.6f %10.6f %10.6f\n" % (lattice[6][0], lattice[7][0], lattice[8][0])
    )

    elements = hdf5["/AtomInfo/Elements"]
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
    if hdf5["/AtomInfo/CoordinateType"][0] == "Direct":
        fileobj.write("Direct\n")
    else:
        fileobj.write("Cartesian\n")
    for i, p in enumerate(hdf5["/AtomInfo/Position"]):
        fileobj.write("%10.6f" % p)
        if (i + 1) % 3 == 0:
            fileobj.write("\n")
    fileobj.write("\n")


def _write_VESTA_format(hdf5: dict, datakeys: list, filename):
    with open(filename, "w") as file:
        _write_atoms(file, hdf5)
        for key in datakeys:
            d = np.asarray(hdf5[key]).reshape(-1, 1)  # 将列表hdf5[key]下的多个列表整合
            file.write("%5d %5d %5d\n" % tuple(hdf5["/AtomInfo/Grid"]))
            i = 0
            while i < len(d):
                for j in range(10):
                    file.write("%10.5f " % d[i])
                    i += 1
                    if i >= len(d):
                        break
                file.write("\n")

            file.write("\n")


def _write_atoms_json(fileobj, atom_info):
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


def _write_VESTA_format_json(atom_info: dict, data: list, filename):
    with open(filename, "w") as file:
        _write_atoms_json(file, atom_info)
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


def _to_dspaw_as(structure, filename: str, coords_are_cartesian=True):
    """write dspaw structure file of .as type"""
    with open(filename, "w", encoding="utf-8") as file:
        file.write("Total number of atoms\n")
        file.write("%d\n" % len(structure))

        # ^ write lattice info
        if "LatticeFixs" in structure.sites[0].properties:
            lfinfo = structure.sites[0].properties["LatticeFixs"]
            if len(lfinfo) == 3:
                file.write("Lattice Fix\n")
                formatted_fts = []
                for ft in lfinfo:
                    if ft == "True":  # True
                        ft_formatted = "T"
                    else:
                        ft_formatted = "F"
                    formatted_fts.append(ft_formatted)
                for v in structure.lattice.matrix:
                    # write each element of formatted_fts in a line without [] symbol
                    file.write(f'{v} {formatted_fts}.strip("[").strip("]")\n')
            elif len(lfinfo) == 9:
                file.write("Lattice Fix_x Fix_y Fix_z\n")
                formatted_fts = []
                for ft in lfinfo:
                    if ft == "True":  # True
                        ft_formatted = "T"
                    else:
                        ft_formatted = "F"
                    formatted_fts.append(ft_formatted)
                fix_str1 = " ".join(formatted_fts[:3])
                fix_str2 = " ".join(formatted_fts[3:6])
                fix_str3 = " ".join(formatted_fts[6:9])
                v1 = structure.lattice.matrix[0]
                v2 = structure.lattice.matrix[1]
                v3 = structure.lattice.matrix[2]
                file.write(f" {v1[0]:5.8f} {v1[1]:5.8f} {v1[2]:5.8f} {fix_str1}\n")
                file.write(f" {v2[0]:5.8f} {v2[1]:5.8f} {v2[2]:5.8f} {fix_str2}\n")
                file.write(f" {v3[0]:5.8f} {v3[1]:5.8f} {v3[2]:5.8f} {fix_str3}\n")
            else:
                raise ValueError(
                    f"LatticeFixs should be a list of 3 or 9 bools, but got {lfinfo}"
                )
        else:
            file.write("Lattice\n")
            for v in structure.lattice.matrix:
                file.write("%.8f %.8f %.8f\n" % (v[0], v[1], v[2]))

        i = 0
        for site in structure:
            keys = []
            for key in site.properties:  # site.properties is a dictionary
                if key != "LatticeFixs":
                    keys.append(key)
            keys.sort()
            keys_str = " ".join(keys)  # sth like 'magmom fix
            if i == 0:
                if coords_are_cartesian:
                    file.write(f"Cartesian {keys_str}\n")
                else:
                    file.write(f"Direct {keys_str}\n")
            i += 1

            coords = site.coords if coords_are_cartesian else site.frac_coords
            raw = []
            for sortted_key in keys:  # site.properties is a dictionary
                raw_values = site.properties[sortted_key]
                # print(f'{raw_values=}')
                if isinstance(raw_values, list):  # single True or False
                    values = raw_values
                else:
                    values = [raw_values]
                for v in values:
                    if v == "True":
                        value_str = "T"
                    elif v == "False":
                        value_str = "F"
                    else:
                        value_str = str(v)
                    raw.append(value_str)

            final_strs = " ".join(raw)  # sth like '0.0 T
            file.write(
                "%s %.8f %.8f %.8f %s\n"
                % (site.species_string, coords[0], coords[1], coords[2], final_strs)
            )


def _to_hzw(structure, filename: str):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("% The number of probes \n")
        file.write("0\n")
        file.write("% Uni-cell vector\n")

        for v in structure.lattice.matrix:
            file.write("%.6f %.6f %.6f\n" % (v[0], v[1], v[2]))

        file.write("% Total number of device_structure\n")
        file.write("%d\n" % len(structure))
        file.write("% Atom site\n")

        for site in structure:
            file.write(
                "%s %.6f %.6f %.6f\n"
                % (site.species_string, site.coords[0], site.coords[1], site.coords[2])
            )


def _to_dspaw_json(structure, filename: str, coords_are_cartesian=True):
    lattice = structure.lattice.matrix.flatten().tolist()
    atoms = []
    for site in structure:
        coords = site.coords if coords_are_cartesian else site.frac_coords
        atoms.append({"Element": site.species_string, "Position": coords.tolist()})

    coordinate_type = "Cartesian" if coords_are_cartesian else "Direct"
    d = {"Lattice": lattice, "CoordinateType": coordinate_type, "Atoms": atoms}

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(d, file, indent=4)


def _to_pdb(structures, pdb_filename: str):
    if not isinstance(structures, list):
        structures = [structures]
    with open(pdb_filename, "w", encoding="utf-8") as file:
        for i, s in enumerate(structures):
            file.write("MODEL         %d\n" % (i + 1))
            file.write("REMARK   Converted from Structures\n")
            file.write("REMARK   Converted using dspawpy\n")
            lengths = s.lattice.lengths
            angles = s.lattice.angles
            file.write(
                "CRYST1{0:9.3f}{1:9.3f}{2:9.3f}{3:7.2f}{4:7.2f}{5:7.2f}\n".format(
                    lengths[0], lengths[1], lengths[2], angles[0], angles[1], angles[2]
                )
            )
            for j, site in enumerate(s):
                file.write(
                    "%4s%7d%4s%5s%6d%4s%8.3f%8.3f%8.3f%6.2f%6.2f%12s\n"
                    % (
                        "ATOM",
                        j + 1,
                        site.species_string,
                        "MOL",
                        1,
                        "    ",
                        site.coords[0],
                        site.coords[1],
                        site.coords[2],
                        1.0,
                        0.0,
                        site.species_string,
                    )
                )
            file.write("TER\n")
            file.write("ENDMDL\n")
