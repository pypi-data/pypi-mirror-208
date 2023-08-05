"""
Functions to build structures
"""

from typing import List, Union

import numpy as np
from pymatgen.core import Structure

from dspawpy.io.read import get_lines_without_comment, get_sinfo


def build_Structures_from_datafile(
    datafile: Union[str, List[str]], si=None, ele=None, ai=None
) -> List[Structure]:
    r"""读取一/多个h5/json文件，返回pymatgen的Structures列表

    Parameters
    ----------
    datafile : str or list
        - h5/json/as/hzw/cif/poscar/cssr/xsf/mcsqs/prismatic/yaml/fleur-inpgen文件路径;
        - 若给定字符串列表，将依次读取数据并合并成一个Structures列表
        - 文件类型依据后缀名判断，请勿使用不规范的后缀名
    si: int, list or str
        构型编号，从 1 开始
        - si=1, 读取第一个构型
        - si=[1,2], 读取第一个和第二个构型
        - si=':', 读取所有构型
        - si='-3:', 读取最后三个构型
    ele: str or list
        元素符号，如['H','O']
    ai: int or list
        原子编号，从 1 开始，用法同si

    Returns
    -------
    List[Structure] : pymatgen Structures 列表

    Examples
    --------

    >>> from dspawpy.io.structure import build_Structures_from_datafile

    读取单个文件生成 Structures 列表，目前支持 h5/json/as/hzw/cif/poscar/cssr/xsf/mcsqs/prismatic/yaml/fleur-inpgen 格式，文件格式根据后缀名判断，请勿使用不规范的后缀名

    >>> pymatgen_Structures = build_Structures_from_datafile(datafile='relax.h5')
    Reading E:\Dev\dspawpy\test\relax.h5 ...
    >>> pymatgen_Structures
    [Structure Summary
    Lattice
        abc : 3.2024004097211822 3.20240519054306 18.40999985
    angles : 90.0 90.0 119.99975020767022
    volume : 163.50740406185463
        A : 3.2024004097211822 0.0 0.0
        B : -1.6011905042240808 2.773371228955793 0.0
        C : 0.0 0.0 18.40999985
        pbc : True True True
    PeriodicSite: Mo (1.5977, 0.9224, 9.2050) [0.6652, 0.3326, 0.5000]
    ...
    PeriodicSite: S (1.5977, 2.7673, 10.7755) [1.0000, 1.0000, 0.5853]]

    注意pymatgen_Structures是由多个 Structure 对象组成的列表，每个 Structure 对象分别对应一个构型。如果只有一个构型，也会返回列表，请使用 pymatgen_Structures[0] 获取 Structure 对象

    当datafile为列表时，将依次读取多个文件，合并成一个Structures列表

    >>> pymatgen_Structures = build_Structures_from_datafile(datafile=['aimd1.h5','aimd2.h5'])
    """
    dfs = []
    if isinstance(datafile, list):  # 续算模式，给的是多个文件
        dfs = datafile
    else:  # 单次计算模式，处理单个文件
        if datafile.split(".")[-1] in [
            "h5",
            "json",
            "as",
            "hzw",
            "cif",
            "poscar",
            "cssr",
            "xsf",
            "mcsqs",
            "prismatic",
            "yaml",
            "fleur-inpgen",
        ]:
            df = datafile
        else:
            raise NotImplementedError(f"{datafile}文件类型暂时无法读取")
        dfs.append(df)

    # 读取结构数据
    pymatgen_Structures = []
    for df in dfs:
        structure_list = _get_structure_list(df, si, ele, ai)
        pymatgen_Structures.extend(structure_list)

    return pymatgen_Structures


def _get_structure_list(df: str, si=None, ele=None, ai=None) -> List[Structure]:
    """get pymatgen structures from single datafile

    Parameters
    ----------
    df : str
        datafile

    Returns
    -------
    List[Structure] : list of pymatgen structures

    Examples
    --------
    >>> from dspawpy.analysis.aimdtools import get_structure_list
    >>> structure_list = get_structure_list(df='aimd.h5')
    """

    # create Structure structure_list from aimd.h5
    fmt = df.split(".")[-1]
    if fmt == "as":
        strs = [_from_dspaw_as(df)]
    elif fmt == "hzw":
        print("build from hzw file may lack mag & fix info!")
        strs = [_from_hzw(df)]
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
        strs = [Structure.from_file(df)]
    else:
        assert df.endswith(".h5") or df.endswith(".json"), "expecting h5/json file"

        Nstep, elements, positions, lattices, D_mag_fix = get_sinfo(
            datafile=df, si=si, ele=ele, ai=ai
        )  # returned positions, not scaled-positions
        strs = []
        for i in range(Nstep):
            if D_mag_fix:
                strs.append(
                    Structure(
                        lattices[i],
                        elements,
                        positions[i],
                        coords_are_cartesian=True,
                        site_properties={k: v[i] for k, v in D_mag_fix.items()},
                    )
                )
            else:
                strs.append(
                    Structure(
                        lattices[i],
                        elements,
                        positions[i],
                        coords_are_cartesian=True,
                    )
                )
    return strs


def _from_dspaw_as(as_file: str = "structure.as") -> Structure:
    """从DSPAW的as结构文件中读取结构信息

    Parameters
    ----------
    as_file : str
        DSPAW的as结构文件, 默认'structure.as'

    Returns
    -------
    Structure
        pymatgen的Structure对象

    Examples
    --------
    >>> from dspawpy.io.structure import from_dspaw_as
    >>> S1 = from_dspaw_as(as_file='structure00.as')
    """

    lines = get_lines_without_comment(as_file, "#")
    N = int(lines[1])  # number of atoms

    # parse lattice info
    lattice = []  # lattice matrix
    for line in lines[3:6]:
        vector = line.split()
        lattice.extend([float(vector[0]), float(vector[1]), float(vector[2])])
    lattice = np.asarray(lattice).reshape(3, 3)

    lat_fixs = []
    if lines[2].strip() != "Lattice":  # fix lattice
        lattice_fix_info = lines[2].strip().split()[1:]
        if lattice_fix_info == ["Fix_x", "Fix_y", "Fix_z"]:
            # ONLY support xyz fix in sequence, yzx will cause error
            for line in lines[3:6]:
                lfs = line.strip().split()[3:6]
                for lf in lfs:
                    if lf.startswith("T"):
                        lat_fixs.append("True")
                    elif lf.startswith("F"):
                        lat_fixs.append("False")
        elif lattice_fix_info == ["Fix"]:
            for line in lines[3:6]:
                lf = line.strip().split()[3]
                if lf.startswith("T"):
                    lat_fixs.append("True")
                elif lf.startswith("F"):
                    lat_fixs.append("False")
        else:
            raise ValueError("Lattice fix info error!")

    elements = []
    positions = []
    for i in range(N):
        atom = lines[i + 7].strip().split()
        elements.append(atom[0])
        positions.extend([float(atom[1]), float(atom[2]), float(atom[3])])

    mf_info = None
    l6 = lines[6].strip()  # str, 'Cartesian/Direct Mag Fix_x ...'
    if l6 == "Direct":
        is_direct = True
    elif l6 == "Cartesian":
        is_direct = False
    else:
        is_direct = l6.split()[0] == "Direct"
        mf_info = l6.split()[1:]  # ['Mag', 'Fix_x', 'Fix_y', 'Fix_z']
        for item in mf_info:
            assert item in [
                "Mag",
                "Mag_x",
                "Mag_y",
                "Mag_z",
                "Fix",
                "Fix_x",
                "Fix_y",
                "Fix_z",
            ], "Mag/Fix info error!"

    mag_fix_dict = {}
    if mf_info is not None:
        for mf_index, item in enumerate(mf_info):
            values = []
            for i in range(N):
                atom = lines[i + 7].strip().split()
                mf = atom[4:]
                values.append(mf[mf_index])

            if item.startswith("Fix"):  # F -> False, T -> True
                for value in values:
                    if value.startswith("T"):
                        values[values.index(value)] = "True"
                    elif value.startswith("F"):
                        values[values.index(value)] = "False"
            mag_fix_dict[item] = values

    if lat_fixs != []:
        # replicate lat_fixs to N atoms
        mag_fix_dict["LatticeFixs"] = [lat_fixs for i in range(N)]

    coords = np.asarray(positions).reshape(-1, 3)

    if mag_fix_dict == {}:
        return Structure(
            lattice, elements, coords, coords_are_cartesian=(not is_direct)
        )
    else:
        return Structure(
            lattice,
            elements,
            coords,
            coords_are_cartesian=(not is_direct),
            site_properties=mag_fix_dict,
        )


def _from_hzw(hzw_file) -> Structure:
    """从hzw结构文件中读取结构信息

    Parameters
    ----------
    hzw_file : str
        hzw结构文件，以 .hzw 结尾

    Returns
    -------
    Structure
        pymatgen的Structure对象

    Examples
    --------
    >>> from dspawpy.io.structure import from_hzw
    >>> S1 = from_hzw(hzw_file='Si.hzw')
    """
    lines = get_lines_without_comment(hzw_file, "%")
    number_of_probes = int(lines[0])
    if number_of_probes != 0:
        raise ValueError("dspaw only support 0 probes hzw file")
    lattice = []
    for line in lines[1:4]:
        vector = line.split()
        lattice.extend([float(vector[0]), float(vector[1]), float(vector[2])])

    lattice = np.asarray(lattice).reshape(3, 3)
    N = int(lines[4])
    elements = []
    positions = []
    for i in range(N):
        atom = lines[i + 5].strip().split()
        elements.append(atom[0])
        positions.extend([float(atom[1]), float(atom[2]), float(atom[3])])

    coords = np.asarray(positions).reshape(-1, 3)
    return Structure(lattice, elements, coords, coords_are_cartesian=True)
