import os

from dspawpy.diffusion.pathfinder import IDPPSolver
from dspawpy.io.write import to_file


class NEB:
    """NEB插值算法

    Parameters
    ----------
    initial_structure: Structure
        初态
    final_structure: Structure
        终态
    nimages: int
        中间构型数

    Examples
    --------
    >>> from pymatgen.core import Structure
    # 先调用pymatgen写好的from_file方法读取cif构型文件，生成structure对象
    >>> initial_structure = Structure.from_file("initial.cif")
    >>> final_structure = Structure.from_file("final.cif")
    # 初始化对象，后续可以调用两个插值算法，详见下方write_neb_structures
    >>> from dspawpy.diffusion.neb import NEB
    >>> neb = NEB(initial_structure,final_structure,10)
    """

    def __init__(self, initial_structure, final_structure, nimages):
        """

        Args:
            initial_structure:
            final_structure:
            nimages: number of images,contain initial and final structure
        """

        self.nimages = nimages
        self.iddp = IDPPSolver.from_endpoints(
            endpoints=[initial_structure, final_structure],
            nimages=self.nimages - 2,
            sort_tol=0,  # 锁定原子编号
        )

    def linear_interpolate(self):
        return self.iddp.structures

    def idpp_interpolate(
        self,
        maxiter=1000,
        tol=1e-5,
        gtol=1e-3,
        step_size=0.05,
        max_disp=0.05,
        spring_const=5.0,
    ):
        return self.iddp.run(maxiter, tol, gtol, step_size, max_disp, spring_const)


def write_neb_structures(
    structures,
    coords_are_cartesian=True,
    fmt: str = "json",
    path: str = ".",
    prefix="structure",
):
    """插值并生成中间构型文件

    Parameters
    ----------
    structures: list
        构型列表
    coords_are_cartesian: bool
        坐标是否为笛卡尔坐标
    fmt: str
        结构文件类型，支持 "json", "as", "poscar", "hzw"
    path: str
        保存路径

    Returns
    -------
    file
        保存构型文件

    Examples
    --------

    先读取as文件创建structure对象

    >>> from dspawpy.io.structure import build_Structures_from_datafile
    >>> initial_structure = build_Structures_from_datafile("structure00.as")[0]
    >>> final_structure = build_Structures_from_datafile("structure06.as")[0]

    然后，插值并生成中间构型文件

    >>> from dspawpy.diffusion.neb import NEB,write_neb_structures
    >>> neb = NEB(initial_structure,final_structure,10)
    >>> neb = NEB(init_struct,final_struct,5) # 设置插点个数
    >>> structures = neb.idpp_interpolate() # idpp插值，生成中间构型

    插值完成的构型可指定保存到neb文件夹下

    >>> write_neb_structures(structures,coords_are_cartesian=True,fmt="as",path="neb")
    """
    N = len(str(len(structures)))
    if N <= 2:
        N = 2
    for i, structure in enumerate(structures):
        path_name = str(i).zfill(N)
        os.makedirs(os.path.join(path, path_name), exist_ok=True)
        if fmt == "poscar":
            structure.to(fmt="poscar", filename=os.path.join(path, path_name, "POSCAR"))
        else:
            filename = os.path.join(
                path, path_name, "%s%s.%s" % (prefix, path_name, fmt)
            )
            to_file(
                structure, filename, coords_are_cartesian=coords_are_cartesian, fmt=fmt
            )
