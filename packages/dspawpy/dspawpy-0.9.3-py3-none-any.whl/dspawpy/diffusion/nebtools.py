import json
import os

import h5py
import numpy as np
import pandas as pd

np.set_printoptions(suppress=True)  # 不使用科学计数法
import matplotlib.pyplot as plt

from dspawpy.io.read import pel_from_as
from dspawpy.io.utils import get_ele_from_h5


def get_distance(
    spo1: np.ndarray, spo2: np.ndarray, lat1: np.ndarray, lat2: np.ndarray
):
    """根据两个结构的分数坐标和晶胞计算距离

    Parameters
    ----------
    spo1 : np.ndarray
        分数坐标列表1
    spo2 : np.ndarray
        分数坐标列表2
    lat1 : np.ndarray
        晶胞1
    lat2 : np.ndarray
        晶胞2

    Returns
    -------
    float
        距离

    Examples
    --------

    先读取两个构型的分数坐标、元素列表和晶胞信息

    >>> from dspawpy.io.read import pel_from_as
    >>> spo1, ele1, lat1 = pel_from_as('structure01.as', sacled=True)
    >>> spo1
    array([[0.25      , 0.25      , 0.11784996],
           [0.75      , 0.25      , 0.11784996],
           ...，
           [0.04062186, 0.45937779, 0.43038044]])
    >>> ele1
    ['Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt']
    >>> lat1
    array([[ 5.6058,  0.    ,  0.    ],
           [ 0.    ,  5.6058,  0.    ],
           [ 0.    ,  0.    , 16.8174]])
    >>> spo2, ele2, lat2 = pel_from_as('structure02.as', sacled=True)
    >>> spo2
    array([[0.25      , 0.25      , 0.11784996],
           ...，
           [0.08124389, 0.41875557, 0.41408303]])
    >>> ele2
    ['Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt', 'Pt']
    >>> lat2
    array([[ 5.6058,  0.    ,  0.    ],
           [ 0.    ,  5.6058,  0.    ],
           [ 0.    ,  0.    , 16.8174]])

    计算两个构型的距离

    >>> from dspawpy.diffusion.nebtools import get_distance
    >>> dist = get_distance(spo1, spo2, lat1, lat2)
    >>> dist
    0.5987379724194888
    """
    diff_spo = spo1 - spo2  # 分数坐标差
    avglatv = 0.5 * (lat1 + lat2)  # 平均晶格矢量
    pbc_diff_spo = set_pbc(diff_spo)  # 笛卡尔坐标差
    # 分数坐标点乘平均晶胞，转回笛卡尔坐标
    pbc_diff_pos = np.dot(pbc_diff_spo, avglatv)  # 笛卡尔坐标差
    distance = np.sqrt(np.sum(pbc_diff_pos**2))

    return distance


def get_neb_subfolders(directory: str = "."):
    """将directory路径下的子文件夹名称列表按照数字大小排序

    仅保留形如00，01数字类型的NEB子文件夹路径

    Parameters
    ----------
    subfolders : list
        子文件夹名称列表

    Returns
    -------
    subfolders : list
        排序后的子文件夹名称列表

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import get_neb_subfolders
    >>> directory = '.' # 默认当前目录
    >>> get_neb_subfolders()
    ['00', '01', '02', '03', '04', '05', '06']
    """
    raw_subfolders = next(os.walk(directory))[1]
    subfolders = []
    for subfolder in raw_subfolders:
        try:
            assert 0 <= int(subfolder) < 100
            subfolders.append(subfolder)
        except:
            pass
    subfolders.sort()  # 从小到大排序
    return subfolders


def plot_barrier(
    datafile: str = "neb.h5",
    directory: str = None,
    ri: float = None,
    rf: float = None,
    ei: float = None,
    ef: float = None,
    method: str = "PchipInterpolator",
    figname: str = "neb_barrier.png",
    show: bool = True,
    raw=False,
    **kwargs,
):
    """调用 scipy.interpolate 插值算法，拟合NEB能垒并绘图

    Parameters
    ----------
    datafile: str
        neb.h5或neb.json文件路径
    directory : str
        NEB计算路径
    ri : float
        初态反应坐标
    rf : float
        末态反应坐标
    ei : float
        初态自洽能量
    ef : float
        末态自洽能量
    method : str, optional
        插值算法, by default 'interp1d'
    figname : str, optional
        能垒图名称, by default 'neb_barrier.png'
    show : bool, optional
        是否展示交互界面, by default True
    raw : bool, optional
        是否返回原始数据到csv

    Raises
    ------
    ImportError
        指定了scipy.interpolate中不存在的插值算法
    ValueError
        传递给插值算法的参数不符合该算法要求

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import plot_barrier
    >>> import matplotlib.pyplot as plt
    >>> plot_barrier(directory='source', method='interp1d', kind=2, figname=None, show=False)
    >>> plot_barrier(directory='source', method='interp1d', kind=3, figname=None, show=False)
    >>> plot_barrier(directory='source', method='CubicSpline', figname=None, show=False)
    >>> plot_barrier(directory='source', method='pchip', figname=None, show=False)
    >>> plt.show()
    """
    if directory is not None:
        # read data
        subfolders, resort_mfs, rcs, ens, dEs = _getef(directory)
        dire = directory

    elif datafile:
        assert os.path.exists(datafile), f"文件{datafile}不存在"
        if datafile.endswith(".h5"):
            from dspawpy.io.read import load_h5

            neb = load_h5(datafile)
            if "/BarrierInfo/ReactionCoordinate" in neb.keys():
                reaction_coordinate = neb["/BarrierInfo/ReactionCoordinate"]
                energy = neb["/BarrierInfo/TotalEnergy"]
            else:  # old version
                reaction_coordinate = neb["/Distance/ReactionCoordinate"]
                energy = neb["/Energy/TotalEnergy"]
        elif datafile.endswith(".json"):
            with open(datafile, "r") as fin:
                neb = json.load(fin)
            if "BarrierInfo" in neb.keys():
                reaction_coordinate = neb["BarrierInfo"]["ReactionCoordinate"]
                energy = neb["BarrierInfo"]["TotalEnergy"]
            else:  # old version
                reaction_coordinate = neb["Distance"]["ReactionCoordinate"]
                energy = neb["Energy"]["TotalEnergy"]
        else:
            raise TypeError("datafile 必须是 .h5 或 .json 文件格式")

        x = []
        for c in reaction_coordinate:
            if len(x) > 0:
                x.append(x[-1] + c)
            else:
                x.append(c)

        y = [x - energy[0] for x in energy]
        # initial and final info
        if ri is not None:  # add initial reaction coordinate
            x.insert(0, ri)
        if rf is not None:  # add final reaction coordinate
            x.append(rf)

        if ei is not None:  # add initial energy
            y.insert(0, ei)
        if ef is not None:  # add final energy
            y.append(ef)

        rcs = np.array(x)
        dEs = np.array(y)

        print(f"如果NEB任务不计算初末态的自洽，{datafile}中将缺失相关信息，需要手动输入")
        dire = os.getcwd()

    else:
        raise ValueError("请指定datafile或directory！")

    # import scipy interpolater
    try:
        interpolate_method = getattr(
            __import__("scipy.interpolate", fromlist=[method]), method
        )
    except:
        raise ImportError(f"无法找到 scipy.interpolate.{method} 算法！")
    # call the interpolater to interpolate with given kwargs
    try:
        inter_f = interpolate_method(rcs, dEs, **kwargs)
    except:
        raise ValueError(f"插值失败，请检查{kwargs}参数设置是否有误！")

    xnew = np.linspace(rcs[0], rcs[-1], 100)
    ynew = inter_f(xnew)

    if raw:
        pd.DataFrame({"x_raw": rcs, "y_raw": dEs}).to_csv("raw_xy.csv", index=False)
        pd.DataFrame({"x_interpolated": xnew, "y_interpolated": ynew}).to_csv(
            "raw_interpolated_xy.csv", index=False
        )

    # plot
    if kwargs:
        plt.plot(xnew, ynew, label=method + str(kwargs))
    else:
        plt.plot(xnew, ynew, label=method)
    plt.scatter(rcs, dEs, c="r")
    plt.xlabel("Reaction Coordinate (Å)")
    plt.ylabel("Energy (eV)")
    plt.legend()

    # save and show
    if figname:
        plt.tight_layout()
        plt.savefig(f"{dire}/{figname}")
        print("能垒图已保存为", os.path.abspath(f"{dire}/{figname}"))
    if show:  # 画子图的话，不应每个子图都show
        plt.show()  # show会自动清空图片


def plot_neb_converge(
    neb_dir: str,
    image_key: str = "01",
    show: bool = True,
    image_name: str = "neb_conv.png",
    raw=False,
):
    """指定NEB计算路径，绘制NEB收敛过程图

    Parameters
    ----------
    neb_dir : str
        NEB计算路径
    image_key : str
        第几个构型，默认 "01"
    show : bool
        是否交互绘图
    image_name : str
        NEB收敛图名称，默认 "neb_conv.png"
    raw : bool
        是否输出原始数据到csv文件

    Returns
    -------
    ax1, ax2 : matplotlib.axes.Axes
        两个子图的Axes对象

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import plot_neb_converge
    >>> plot_neb_converge(neb_dir='my_neb_task', image_key='01')
    """
    assert os.path.isdir(neb_dir), f"目录{neb_dir}不存在"

    if os.path.exists(os.path.join(neb_dir, "neb.h5")):
        neb_total = h5py.File(os.path.join(neb_dir, "neb.h5"))
        # new output (>=2022B)
        if "/LoopInfo/01/MaxForce" in neb_total.keys():
            maxforce = np.array(neb_total.get("/LoopInfo/" + image_key + "/MaxForce"))
        else:  # old output
            maxforce = np.array(neb_total.get("/Iteration/" + image_key + "/MaxForce"))

        if "/LoopInfo/01/TotalEnergy" in neb_total.keys():  # new output (>=2022B)
            total_energy = np.array(
                neb_total.get("/LoopInfo/" + image_key + "/TotalEnergy")
            )
        else:  # old output
            total_energy = np.array(
                neb_total.get("/Iteration/" + image_key + "/TotalEnergy")
            )

    elif os.path.exists(os.path.join(neb_dir, "neb.json")):
        with open(os.path.join(neb_dir, "neb.json"), "r") as fin:
            neb_total = json.load(fin)
        if "LoopInfo" in neb_total.keys():
            neb = neb_total["LoopInfo"][image_key]
        else:
            neb = neb_total["Iteration"][image_key]
        maxforce = []
        total_energy = []
        for n in neb:
            maxforce.append(n["MaxForce"])
            total_energy.append(n["TotalEnergy"])

        maxforce = np.array(maxforce)
        total_energy = np.array(total_energy)

    else:
        print(
            f"请检查{os.path.join(neb_dir, 'neb.h5')}或{os.path.join(neb_dir, 'neb.h5')}是否都存在！"
        )

    x = np.arange(len(maxforce))

    force = maxforce
    energy = total_energy

    if raw:
        pd.DataFrame({"x": x, "force": force, "energy": energy}).to_csv(
            "neb_conv.csv", index=False
        )

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, force, label="Max Force", c="black")
    ax1.set_xlabel("Number of ionic step")
    ax1.set_ylabel("Force (eV/Å)")
    ax2 = ax1.twinx()
    ax2.plot(x, energy, label="Energy", c="r")
    ax2.set_xlabel("Number of ionic step")
    ax2.set_ylabel("Energy (eV)")
    ax2.ticklabel_format(useOffset=False)  # y轴坐标显示绝对值而不是相对值
    fig.legend(loc=1, bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    if image_name:
        plt.tight_layout()
        plt.savefig(image_name)
    if show:
        plt.show()

    return ax1, ax2


def printef(directory):
    """打印NEB计算时各构型的能量和受力

    Parameters
    ----------
    directory : str
        NEB计算的目录，默认为当前目录

    Returns
    -------
    打印各构型的能量和受力

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import printef
    >>> printef(directory='.')
    构型    受力(eV/Å)      反应坐标(Å)     此构型的能量(eV)        与初始构型的能量差(eV)
    00        0.1869          0.0000         -42922.7554                  0.0000
    01        0.0874          0.7076         -42922.4959                  0.2595
    02        0.0399          1.4144         -42921.9633                  0.7921
    03        0.0618          2.1067         -42922.0385                  0.7169
    04        0.0425          2.7983         -42921.9606                  0.7948
    05        0.8643          3.5299         -42922.4642                  0.2912
    06        0.0352          4.2620         -42922.7012                  0.0542
    """
    subfolders, resort_mfs, rcs, ens, dEs = _getef(directory)
    # printout summary
    print("构型\t受力(eV/Å)\t反应坐标(Å)\t此构型的能量(eV)\t与初始构型的能量差(eV)")
    for i in range(len(subfolders)):  # 注意格式化输出，对齐
        print(
            "%s\t%8.4f\t%8.4f\t%12.4f\t%20.4f"
            % (subfolders[i], resort_mfs[i], rcs[i], ens[i], dEs[i])
        )


def restart(directory: str, inputin: str, output: str):
    """将旧NEB任务归档压缩，并在原路径下准备续算

    Parameters
    ----------
    directory : str
        旧NEB任务所在路径，默认当前路径
    inputin : str
        输入参数文件名，默认input.in
    output : str
        备份文件夹路径

    Examples
    ----------
    >>> from dspawpy.diffusion.nebtools import restart
    >>> restart(directory='source', inputin='input.in', output='backup')
    """
    if output == "":
        raise ValueError("备份文件夹路径不能为空！")
    elif os.path.isdir(output):
        raise ValueError("备份文件夹已存在！")

    if directory == "":
        directory = os.getcwd()
    if inputin == "":
        inputin = "input.in"

    # 读取子文件夹名称列表，仅保留形如00，01数字文件夹路径
    subfolders = get_neb_subfolders(directory)
    # 创建备份文件夹并进入
    os.makedirs(f"{directory}/{output}")
    os.chdir(f"{directory}/{output}")
    # 将-0改成-9可提供极限压缩比
    os.environ["XZ_OPT"] = "-T0 -0"
    for subfolder in subfolders:
        # 备份
        os.system(f"mv {directory}/{subfolder} ./")
        # 准备续算用的结构文件
        os.mkdir(f"{directory}/{subfolder}")
        latestStructureFile = os.path.join(
            directory, output, subfolder, "latestStructure%s.as" % subfolder
        )
        structureFile = os.path.join(
            directory, output, subfolder, "structure%s.as" % subfolder
        )
        bk_latestStructure = f"{directory}/latestStructure{subfolder}.as"
        bk_structure = f"{directory}/structure{subfolder}.as"

        if os.path.exists(latestStructureFile):
            os.system(  # 复制到子文件夹
                f"cp {latestStructureFile} {directory}/{subfolder}/structure{subfolder}.as"
            )
            # 备份latestStructureFile到主目录
            os.system(f"cp {latestStructureFile} {bk_latestStructure}")
        elif os.path.exists(structureFile):
            print(f"未找到{latestStructureFile}，复用{structureFile}续算")
            os.system(  # 复制到子文件夹
                f"cp {structureFile} {directory}/{subfolder}/structure{subfolder}.as"
            )
        else:
            raise FileNotFoundError(f"{latestStructureFile}和{structureFile}都不存在！")
        # 备份structureFile到主目录
        if os.path.exists(structureFile):
            os.system(f"cp {structureFile} {bk_structure}")

        # 压缩和移动文件
        # 若存在latestStructure00.as和structure00.as，则压缩00文件夹并把主结构移入00文件夹
        if os.path.exists(bk_latestStructure) and os.path.exists(bk_structure):
            os.system(
                f"tar -Jcf {subfolder}.tar.xz -C {subfolder} . --remove-files && mkdir {subfolder} && mv {subfolder}.tar.xz {directory}/latestStructure{subfolder}.as {directory}/structure{subfolder}.as {subfolder}/ &"
            )
        # 若仅存在latestStructure00.as，则压缩00文件夹并把主结构移入00文件夹
        elif os.path.exists(bk_latestStructure):
            os.system(
                f"tar -Jcf {subfolder}.tar.xz {subfolder} . --remove-files && mkdir {subfolder} && mv {subfolder}.tar.xz {directory}/latestStructure{subfolder}.as {subfolder}/ &"
            )
        # 若仅存在structure00.as，则压缩00文件夹并把主结构移入00文件夹
        elif os.path.exists(bk_structure):
            os.system(
                f"tar -Jcf {subfolder}.tar.xz -C {subfolder} . --remove-files && mkdir {subfolder} && mv {subfolder}.tar.xz {directory}/structure{subfolder}.as {subfolder}/ &"
            )
        else:  # 如果都不存在，说明备份失败
            raise FileNotFoundError(f"{bk_latestStructure}和{bk_structure}都不存在！")

    # 备份neb.h5,neb.json和DS-PAW.log
    if os.path.exists(f"{directory}/neb.json"):
        os.system(
            f"mv {directory}/neb.h5 {directory}/neb.json {directory}/DS-PAW.log ./"
        )
        os.system(f"tar -Jcf neb.tar.xz neb.h5 neb.json --remove-files &")
    else:
        os.system(f"mv {directory}/neb.h5 {directory}/DS-PAW.log ./")
        os.system(f"tar -Jcf neb.tar.xz neb.h5 --remove-files &")


def set_pbc(spo):
    """根据周期性边界条件将分数坐标分量移入 [-0.5, 0.5) 区间

    Parameters
    ----------
    spo : np.ndarray or list
        分数坐标列表

    Returns
    -------
    pbc_spo : np.ndarray
        符合周期性边界条件的分数坐标列表

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import set_pbc
    >>> set_pbc([-0.6, 1.2, 2.3])
    array([0.4, 0.2, 0.3])
    """
    # wrap into [-0.5, 0.5)
    pbc_spo = np.mod(np.array(spo) + 0.5, 1.0) - 0.5

    return pbc_spo


def summary(directory: str = ".", raw=False, **kwargs):
    """NEB任务完成总结，依次执行以下步骤：

    - 1. 打印各构型受力、反应坐标、能量、与初始构型的能量差
    - 2. 绘制能垒图
    - 3. 绘制并保存结构优化过程的能量和受力收敛过程图

    Parameters
    ----------
    directory : str
        NEB路径, 默认当前路径
    raw : bool
        是否保存原始数据到csv文件
    **kwargs : dict
        传递给plot_barrier的参数

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import summary
    >>> directory = '.' # NEB计算路径，默认当前路径
    >>> summary(directory)
    # 若inifin=false，用户必须将自洽的scf.h5或system.json放到初末态子文件夹中
    """
    # 1. 绘制能垒图
    print("--> 1. 打印NEB计算时各构型的能量和受力...")
    printef(directory)

    # 2. 打印各构型受力、反应坐标、能量、与初始构型的能量差
    print("\n--> 2. 绘制能垒图...")
    plt.clf()  # 清空画布再画图
    plot_barrier(directory=directory, raw=raw, **kwargs)

    # 3. 绘制并保存结构优化过程的能量和受力收敛过程图到各构型文件夹中
    print("\n--> 3. 绘制收敛过程图到各构型文件夹中...")
    subfolders = get_neb_subfolders(directory)
    for subfolder in subfolders[1 : len(subfolders) - 1]:
        print(f"----> {subfolder}/converge.png...")
        plot_neb_converge(
            neb_dir=directory,
            image_key=subfolder,
            image_name=f"{directory}/{subfolder}/converge.png",
            raw=raw,
        )
    print("\n完成!")


def write_movie_json(preview: bool = False, directory: str = ".", step: int = -1):
    """NEB计算或者初始插值后，读取信息，保存为 neb_movie*.json 文件

    用 Device Studio 打开该文件可以观察结构等信息

    Parameters
    ----------
    preview : bool
        是否预览模式，默认否
    directory : str
        计算结果所在目录. 默认当前路径
    step: int
        离子步编号. 默认-1，读取整个NEB计算过程信息。
        0表示初插结构（未完成离子步）；
        1表示第一个离子步，以此类推。

    Returns
    ----------
    neb_movie*.json文件

    Examples
    ----------
    >>> from dspawpy.diffusion.nebtools import write_movie_json
    # NEB计算完成后要观察轨迹变化全过程，只需指定NEB计算路径即可
    >>> write_movie_json(directory='source')
    # NEB计算完成后要观察第n离子步结构，请设置step为n，注意step从1开始计数
    >>> write_movie_json(directory='source', step=1)
    # 如果您指定的step数超过NEB实际完成的离子步，将会自动修改为最后一步，实际效果等同于上一行代码
    >>> write_movie_json(directory='source', step=100)
    # 另外，如需预览初插结构，请将preview设置为True，并将directory指定为NEB计算主路径
    >>> write_movie_json(preview=True, directory='source')
    """

    if preview:  # preview mode, write neb_movie_init.json from structure.as
        print("正在根据初插结构保存neb_movie_init.json...")
        try:
            raw = _from_structures(directory)
        except FileNotFoundError:
            print("未找到初始插值结构！")
        except Exception as e:
            print("初始插值结构读取失败！", e)
    else:
        if step == 0:  # try preview mode to save time
            try:
                raw = _from_structures(directory)
            except FileNotFoundError:
                print("未找到初始插值结构，将从计算结果h5或json文件中读取！")
            except Exception as e:
                print("初始插值结构读取失败！", e)
        else:
            try:  # read from h5 file
                raw = _from_h5(directory, step)
            except FileNotFoundError:
                raw = _from_json(directory, step)
                # try:  # read from json file
                #     raw = _from_json(directory, step)
                # except json.decoder.JSONDecodeError:
                #     print("json文件格式错误！")
                # except Exception as e:
                #     print(e)
            except Exception as e:
                print("h5文件内容读取失败！", e)
    _dump_neb_movie_json(raw)


def write_xyz(preview: bool = False, directory: str = ".", step: int = -1):
    """
    将NEB结构链条写成xyz轨迹文件用于可视化

    Parameters
    ----------
    preview : bool
        是否预览模式，默认否
    directory : str
        计算结果所在目录. 默认当前路径
    step: int
        离子步编号. 默认-1，读取整个NEB计算过程信息。
        0表示初插结构（未完成离子步）；
        1表示第一个离子步，以此类推。

    Returns
    ----------
    neb_movie.xyz文件

    Examples
    ----------
    """

    if preview:  # preview mode, write neb_movie_init.xyz from structure.as
        print("正在根据初插结构保存neb_movie_init.xyz...")
        try:
            raw = _from_structures(directory)
        except FileNotFoundError:
            print("未找到初始插值结构！")
        except Exception as e:
            print("初始插值结构读取失败！", e)
    else:
        if step == 0:  # try preview mode to save time
            try:
                raw = _from_structures(directory)
            except FileNotFoundError:
                print("未找到初始插值结构，将从计算结果h5或json文件中读取！")
            except Exception as e:
                print("初始插值结构读取失败！", e)
        else:
            try:  # read from h5 file
                raw = _from_h5(directory, step)
            except FileNotFoundError:
                try:  # read from json file
                    raw = _from_json(directory, step)
                except json.decoder.JSONDecodeError:
                    print("json文件格式错误！")
                except Exception as e:
                    print(e)
            except Exception as e:
                print("h5文件内容读取失败！", e)
    _dump_neb_xyz(raw)


def _dump_neb_xyz(raw):
    """根据之前收集到的各数据列表，dump json文件到output"""
    (
        output,
        subfolders,
        step,
        MaxForces,
        TotalEnergies,
        Poses,  # Nimage x Natom x 3 , read
        Latvs,  # Nimage x 9
        Elems,  # Nimage x Natom
        Fixs,  # Natom x 3
        reactionCoordinates,
        totalEnergies,
        maxForces,
        tangents,
        iDirects,
    ) = raw

    # 写入文件
    xyzfile = output[:-5] + ".xyz"
    Nstep = len(subfolders)  # 选定离子步，展示构型链
    with open(xyzfile, "w") as f:
        # Nstep
        for n in range(Nstep):
            eles = Elems[n]  # 针对每个构型
            # 原子数不会变，就是不合并的元素总数
            f.write("%d\n" % len(eles))
            # lattice
            f.write(
                'Lattice="%f %f %f %f %f %f %f %f %f" Properties=species:S:1:pos:R:3 pbc="T T T"\n'
                % (
                    Latvs[n, 0],
                    Latvs[n, 1],
                    Latvs[n, 2],
                    Latvs[n, 3],
                    Latvs[n, 4],
                    Latvs[n, 5],
                    Latvs[n, 6],
                    Latvs[n, 7],
                    Latvs[n, 8],
                )
            )
            # position and element
            for i in range(len(eles)):
                f.write(
                    "%s %f %f %f\n"
                    % (eles[i], Poses[n, i, 0], Poses[n, i, 1], Poses[n, i, 2])
                )
    print(f"--> {os.path.abspath(xyzfile)} 写入成功！\n")


def _from_structures(directory: str):
    """从structure00.as，structure01.as，...，中读取结构信息，
    写入neb_movie_init，以便用DeviceStudio打开观察

    Parameters
    ----------
    directory : str
        NEB计算路径，默认当前路径

    Returns
    -------
    用于json文件的各个数组
    """
    output = "neb_movie_init.json"
    step = 0

    subfolders = get_neb_subfolders(directory)
    # print(subfolders)
    nimage = len(subfolders)
    reactionCoordinates = np.zeros(shape=nimage)  # optional
    totalEnergies = np.zeros(shape=nimage)  # optional
    maxForces = np.zeros(shape=nimage - 2)  # optional
    tangents = np.zeros(shape=nimage - 2)  # optional
    MaxForces = np.zeros(shape=(nimage - 2, step + 1))  # optional
    TotalEnergies = np.zeros(shape=(nimage - 2, step + 1))  # optional

    Poses = []  # nimage x Natom x 3 , read
    Elems = []  # nimage x Natom, read
    Latvs = []  # nimage x 9, read

    iDirects = []  # read coordinate type
    for i, folder in enumerate(subfolders):
        structure_path = os.path.join(directory, folder, f"structure{folder}.as")
        if not os.path.exists(structure_path):
            raise FileNotFoundError(f"请检查{structure_path}是否存在！")
        pos, ele, lat = pel_from_as(structure_path)
        Poses.append(pos)
        Elems.append(ele)
        Latvs.append(lat)
        with open(structure_path, "r") as f:
            lines = f.readlines()
            coordinateType = lines[6].split()[0]
            if coordinateType == "Direct":
                iDirect = True
            elif coordinateType == "Cartesian":
                iDirect = False
            else:
                raise ValueError(f"请检查{structure_path}中的坐标类型！")
            iDirects.append(iDirect)
    Natom = len(Elems[0])

    # reshape data
    Poses = np.array(Poses).reshape((nimage, Natom, 3))
    Elems = np.array(Elems).reshape((nimage, Natom))
    Latvs = np.array(Latvs).reshape((nimage, 9))
    Fixs = np.zeros(shape=(Natom, 3))  # optional

    return (
        output,
        subfolders,
        step,
        MaxForces,
        TotalEnergies,
        Poses,
        Latvs,
        Elems,
        Fixs,
        reactionCoordinates,
        totalEnergies,
        maxForces,
        tangents,
        iDirects,
    )


def _from_h5(directory: str, step: int):
    """从NEB路径下的h5文件读取 从第一步开始到指定step数 的结构和能量信息，
    写入json文件，以便用DeviceStudio打开观察。

    支持热读取结构信息（其他信息忽略）

    Parameters
    ----------
    directory : str
        NEB路径，默认当前路径
    step : int
        step数，默认-1，读取最后一个构型

    Returns
    -------
    用于json文件的各个数组
    """
    # ^ 前期设置
    neb_h5 = os.path.join(directory, "01", "neb01.h5")
    ele = get_ele_from_h5(hpath=neb_h5)
    Natom = len(ele)
    data = h5py.File(neb_h5)
    try:
        total_steps = np.array(data.get("/NebSize"))[0]
    except:
        print("NEB计算未正常结束，正在尝试实时读取结构信息...")
        try:
            total_steps = np.array(data.get("/Structures/FinalStep"))[0]
        except:
            raise ValueError("尚未完成第一个离子步，请检查计算是否出错，否则请耐心等待离子步完成至少一个后再尝试读取！")

    if step == -1:
        output = "neb_movie_last.json"
        step = total_steps
        print("正在读取最后一个离子步信息...")
    elif step > total_steps:
        output = "neb_movie_last.json"
        step = total_steps
        print(f"指定的step数大于NEB计算实际完成的总离子步数{total_steps}")
        print("正在读取最后一个离子步信息...")
    else:
        output = "neb_movie_{}.json".format(step)
        print(f"正在读取第{step}个离子步信息...")

    # ^ 读取前，准备好json文件所需数组框架
    subfolders = get_neb_subfolders(directory)
    nimage = len(subfolders)
    reactionCoordinates = np.zeros(shape=nimage)  # optional
    totalEnergies = np.zeros(shape=nimage)  # optional，每个构型最终能量
    maxForces = np.zeros(shape=nimage - 2)  # optional
    tangents = np.zeros(shape=nimage - 2)  # optional
    MaxForces = np.zeros(shape=(nimage - 2, step))  # optional
    TotalEnergies = np.zeros(shape=(nimage - 2, step))  # optional，中间构型每个离子步能量
    # Sposes = []  # nimage x Natom x 3 , read
    Sposes = np.empty(shape=(nimage, Natom, 3))  # nimage x Natom x 3 , read
    Elems = []  # nimage x Natom, read
    Latvs = []  # nimage x 9, read
    Fixs = []  # Natom x 3, set

    for folder in subfolders:
        """如果是首尾两个构型，最多只有scf.h5文件，没有neb.h5文件
        用户如果算NEB的时候，不计算首尾构型的自洽，
         或者在别处算完了但是没有复制到首尾文件夹中并命名为scf.h5，
          便不能使用第一个功能
        """
        if folder == subfolders[0] or folder == subfolders[-1]:
            h5_path = os.path.join(directory, folder, "scf.h5")
            spath = os.path.join(directory, folder, f"structure{folder}.as")
            assert os.path.exists(h5_path) or os.path.exists(
                spath
            ), f"请确认{h5_path}或{spath}至少存在一个！"
        else:
            h5_path = os.path.join(directory, folder, f"neb{folder}.h5")
            assert os.path.exists(h5_path), f"请确认{h5_path}是否存在！"

    # ^ 开始分功能读取数据
    for i, folder in enumerate(subfolders):
        if folder == subfolders[0] or folder == subfolders[-1]:
            h5_path = os.path.join(directory, folder, "scf.h5")
            if os.path.exists(h5_path):
                data = h5py.File(h5_path)
                # 不影响可视化，直接定为0
                if folder == subfolders[0]:
                    reactionCoordinates[i] = 0
                pos = np.array(data.get("/Structures/Step-1/Position")).reshape(
                    -1, 3
                )  # scaled
                lat = np.array(data.get("/Structures/Step-1/Lattice"))
                ele = get_ele_from_h5(hpath=h5_path)
                totalEnergies[i] = np.array(data.get("/Energy/TotalEnergy0"))
            else:
                pos, ele, lat = pel_from_as(spath, scaled=True)
        else:
            h5_path = os.path.join(directory, folder, f"neb{folder}.h5")
            data = h5py.File(h5_path)
            # reading...
            try:
                reactionCoordinates[i - 1] = np.array(data.get("/Distance/Previous"))[
                    -1
                ]
                maxForces[i - 1] = np.array(data.get("/MaxForce"))[-1]
                tangents[i - 1] = np.array(data.get("/Tangent"))[-1]
                if folder == subfolders[-2]:
                    reactionCoordinates[i + 1] = np.array(data.get("/Distance/Next"))[
                        -1
                    ]
                # read MaxForces and TotalEnergies
                nionStep = np.array(data.get("/MaxForce")).shape[0]
                assert step <= nionStep, f"总共只完成了{nionStep}个离子步!"
                for j in range(step):
                    MaxForces[i - 1, j] = np.array(data.get("/MaxForce"))[j]
                    TotalEnergies[i - 1, j] = np.array(data.get("/TotalEnergy"))[j]
                totalEnergies[i] = np.array(data.get("/Energy/TotalEnergy0"))
            except:
                pass  # 还没完成NEB计算，不影响读取结构信息用于可视化
            # read the latest structure for visualization
            pos = np.array(data.get(f"/Structures/Step-{step}/Position")).reshape(
                Natom, 3
            )  # scaled
            lat = np.array(data.get(f"/Structures/Step-{step}/Lattice"))
            ele = get_ele_from_h5(hpath=h5_path)

        Elems.append(ele)
        Sposes[i, :, :] = pos
        Latvs.append(lat)

    if os.path.exists(os.path.join(directory, "neb.h5")):
        tdata = h5py.File(os.path.join(directory, "neb.h5"))
        # atom fix, not lattice
        # ignore this trivial message because it is not necessary for the visualization
        if "/UnrelaxStructure/Image00/Fix" in tdata:
            fix_array = np.array(tdata.get("/UnrelaxStructure/Image00/Fix"))
            for fix in fix_array:
                if fix == 0.0:
                    F = False
                elif fix == 1.0:
                    F = True
                else:
                    raise ValueError("Fix值只能为0或1")
                Fixs.append(F)
        else:
            Fixs = np.full(shape=(Natom, 3), fill_value=False)
    else:
        Fixs = np.full(shape=(Natom, 3), fill_value=False)

    Elems = np.array(Elems).reshape((nimage, Natom))
    Latvs = np.array(Latvs).reshape((nimage, 9))
    Fixs = np.array(Fixs).reshape((Natom, 3))
    iDirects = [True for i in range(Natom)]  # only output direct coordinates

    return (
        output,
        subfolders,
        step,
        MaxForces,
        TotalEnergies,  #
        Sposes,
        Latvs,
        Elems,
        Fixs,
        reactionCoordinates,
        totalEnergies,
        maxForces,
        tangents,
        iDirects,
    )


def _from_json(directory: str, step: int):
    """从NEB路径下的json文件读取 从第一步开始到指定step数 的结构和能量信息，
    写入json文件，以便用DeviceStudio打开观察

    Parameters
    ----------
    directory : str
        NEB路径，默认当前路径
    step : int
        step数，默认-1，读取最后一个构型

    Returns
    -------
    用于json文件的各个数组
    """

    # ^ 前期设置
    neb_js = os.path.join(directory, "01/neb01.json")
    with open(neb_js, "r") as f:
        data = json.load(f)
    total_steps = len(data)

    if step == -1:
        output = "neb_movie_last.json"
        step = total_steps
        print("正在读取最后一个离子步信息（h5文件不存在，尝试从json文件读取数据）...")
    elif step > total_steps:
        output = "neb_movie_last.json"
        step = total_steps
        print(f"您指定的step数大于NEB计算实际完成的总离子步数{total_steps}")
        print("正在读取最后一个离子步信息（h5文件不存在，尝试从json文件读取数据）...")
    else:
        output = f"neb_movie_{step}.json"
        print(f"正在读取第{step}个离子步信息...")

    # ^ 读取前，准备好json文件所需数组框架
    subfolders = get_neb_subfolders(directory)
    nimage = len(subfolders)
    reactionCoordinates = np.zeros(shape=nimage)  # optional
    totalEnergies = np.zeros(shape=nimage)  # optional，每个构型最终能量
    maxForces = np.zeros(shape=nimage - 2)  # optional
    tangents = np.zeros(shape=nimage - 2)  # optional
    MaxForces = np.zeros(shape=(nimage - 2, step))  # optional
    TotalEnergies = np.zeros(shape=(nimage - 2, step))  # optional，中间构型每个离子步能量
    Sposes = []  # nimage x Natom x 3 , read
    Elems = []  # nimage x Natom, read
    Latvs = []  # nimage x 9, read
    Fixs = []  # Natom x 3, set

    for folder in subfolders:
        """如果是首尾两个构型，最多只有system.json文件，没有neb*.json文件
        用户如果算NEB的时候，不计算首尾构型的自洽，
         或者在别处算完了但是没有复制到首尾文件夹中并命名为system.json，
          便不能使用第一个功能
        """
        if folder == subfolders[0] or folder == subfolders[-1]:
            js_path = os.path.join(directory, folder, "system.json")
        else:
            js_path = os.path.join(directory, folder, f"neb{folder}.json")
        assert os.path.exists(js_path), f"请确认{js_path}是否存在！"

    # ^ 开始分功能读取数据
    for i, folder in enumerate(subfolders):
        if i == 0:  # 初末态在NEB计算过程中不会优化结构
            # 1. 外部自洽后移动system.json
            js_path = os.path.join(directory, folder, "system.json")
            # 2. 直接NEB计算，得到system00.json
            neb_js_path = os.path.join(directory, folder, f"system{folder}.json")
            if os.path.exists(neb_js_path):  # 优先读取neb计算得到的system00.json
                with open(neb_js_path, "r") as f:
                    data = json.load(f)

            elif os.path.exists(js_path):
                with open(js_path, "r") as f:
                    data = json.load(f)

            else:
                raise FileNotFoundError(
                    f"{os.path.abspath(js_path)}和{os.path.abspath(neb_js_path)}均不存在！"
                )

            lat = data["AtomInfo"]["Lattice"]
            Latvs.append(lat)

            Natom = len(data["AtomInfo"]["Atoms"])  # 读取原子数
            for j in range(Natom):
                pos = data["AtomInfo"]["Atoms"][j]["Position"]  # scaled
                Sposes.append(pos)

            totalEnergies[i] = data["Energy"]["TotalEnergy0"]
            reactionCoordinates[i] = 0.0

        elif i > 0 and i < nimage - 1:  # 中间构型会优化结构
            # 读取晶胞矢量、原子坐标
            relax_json = os.path.join(directory, folder, "relax.json")
            assert os.path.exists(relax_json), f"{relax_json}不存在！"

            with open(relax_json, "r") as f:
                rdata = json.load(f)

            lat = rdata[step - 1]["Lattice"]  # 第step步优化后的晶胞
            Latvs.append(lat)

            Natom = len(rdata[0]["Atoms"])
            for j in range(Natom):  # for each atom
                pos = rdata[step - 1]["Atoms"][j]["Position"]  # 第step步优化后的原子坐标
                Sposes.append(pos)  # ! 输出的都是分数坐标

            # 读取能量和反应坐标
            nj = os.path.join(directory, folder, f"neb{folder}.json")
            with open(nj, "r") as f:
                print(f"Reading {os.path.abspath(nj)}...")
                ndata = json.load(f)

            totalEnergies[i] = ndata[step - 1]["TotalEnergy"]  # 读取第step步优化后的能量

            # 读取与前一个构型相比的反应坐标
            reactionCoordinates[i - 1] = ndata[step - 1]["ReactionCoordinate"][-2]
            tangents[i - 1] = ndata[step - 1]["Tangent"]
            if folder == subfolders[-2]:  # 末态前一个构型的计算结果中读取反应坐标
                reactionCoordinates[i + 1] = ndata[step - 1]["ReactionCoordinate"][-1]
            for j in range(step):
                MaxForces[i - 1, j] = ndata[j]["MaxForce"]
                # neb01.json中不存在TotalEnergy0，暂时读取TotalEnergy
                TotalEnergies[i - 1, j] = ndata[j]["TotalEnergy"]

        else:  # 末态构型
            js_path = os.path.join(directory, folder, "system.json")
            neb_js_path = os.path.join(directory, folder, f"system{folder}.json")
            if os.path.exists(neb_js_path):  # 优先读取neb计算得到的json文件
                with open(neb_js_path, "r") as f:
                    data = json.load(f)

            elif os.path.exists(js_path):
                with open(js_path, "r") as f:
                    data = json.load(f)

            else:
                raise FileNotFoundError(
                    f"{os.path.abspath(js_path)}和{os.path.abspath(neb_js_path)}均不存在！"
                )

            lat = data["AtomInfo"]["Lattice"]
            Latvs.append(lat)

            Natom = len(data["AtomInfo"]["Atoms"])  # 读取原子数
            for j in range(Natom):
                pos = data["AtomInfo"]["Atoms"][j]["Position"]  # scaled
                Sposes.append(pos)

            energy = data["Energy"]["TotalEnergy0"]
            totalEnergies[i] = energy

    # 读取原子元素
    tneb_js = os.path.join(directory, "neb.json")
    with open(tneb_js, "r") as f:
        tdata = json.load(f)

    Natom = len(tdata["UnrelaxStructure"][0]["Atoms"])
    elems = []
    for k in range(Natom):
        ele = tdata["UnrelaxStructure"][0]["Atoms"][k]["Element"]
        elems.append(ele)

    for ni in range(nimage):
        Elems.append(elems)  # 重复nimage次，保持Elems结构一致

    for atom in range(Natom):
        fix_array = tdata["UnrelaxStructure"][1]["Atoms"][atom]["Fix"]  # (1,3)
        if fix_array == []:  # empty list
            fix_array = [0.0, 0.0, 0.0]
        for fix in fix_array:
            if fix == 0.0:
                F = False
            elif fix == 1.0:
                F = True
            else:
                raise ValueError("Fix值只能为 0.0 或 1.0")
            Fixs.append(F)

    # 累加reactionCoordinates中的元素
    for i in range(1, len(reactionCoordinates)):
        reactionCoordinates[i] += reactionCoordinates[i - 1]

    # reshape data
    Sposes = np.array(Sposes).reshape((nimage, Natom, 3))
    Elems = np.array(Elems).reshape((nimage, Natom))
    Latvs = np.array(Latvs).reshape((nimage, 9))
    Fixs = np.array(Fixs).reshape((Natom, 3))
    iDirects = [True for i in range(Natom)]  # only output direct coordinates

    return (
        output,
        subfolders,
        step,
        MaxForces,
        TotalEnergies,
        Sposes,
        Latvs,
        Elems,
        Fixs,
        reactionCoordinates,
        totalEnergies,
        maxForces,
        tangents,
        iDirects,
    )


def _dump_neb_movie_json(raw):
    """根据之前收集到的各数据列表，dump json文件到output"""
    (
        output,
        subfolders,
        step,
        MaxForces,
        TotalEnergies,
        Poses,
        Latvs,
        Elems,
        Fixs,
        reactionCoordinates,
        totalEnergies,
        maxForces,
        tangents,
        iDirects,
    ) = raw

    IterDict = {}
    for s, sf in enumerate(subfolders):
        if sf == subfolders[0] or sf == subfolders[-1]:
            continue
        else:
            Eflist = []
            for l in range(step):
                ef = {
                    "MaxForce": MaxForces[s - 1, l],
                    "TotalEnergy": TotalEnergies[s - 1, l],
                }
                Eflist.append(ef)
                iterDict = {sf: Eflist}  # construct sub-dict
                IterDict.update(iterDict)  # append sub-dict

    RSList = []
    """
    从外到内依次遍历 构型、原子（子字典）
    原子的键值对为：'Atoms': 原子信息列表
    原子信息列表是一个由字典组成的列表，每个字典对应一个原子的信息
    """
    for s, sf in enumerate(subfolders):
        pos = Poses[s]
        lat = Latvs[s]
        elem = Elems[s]
        atoms = []
        for i in range(len(elem)):
            atom = {
                "Element": elem[i],
                "Fix": Fixs[i].tolist(),
                "Mag": [],  # empty
                "Position": pos[i].tolist(),
                "Pot": "",
            }  # empty
            atoms.append(atom)
        if iDirects[s]:
            rs = {"Atoms": atoms, "CoordinateType": "Direct", "Lattice": lat.tolist()}
        else:
            rs = {
                "Atoms": atoms,
                "CoordinateType": "Cartesian",
                "Lattice": lat.tolist(),
            }
        RSList.append(rs)

    URSList = []  # DS似乎并不读取这部分信息，空置即可

    data = {
        "Distance": {"ReactionCoordinate": reactionCoordinates.tolist()},
        "Energy": {"TotalEnergy": totalEnergies.tolist()},
        "Force": {"MaxForce": maxForces.tolist(), "Tangent": tangents.tolist()},
        "Iteration": IterDict,
        "RelaxedStructure": RSList,
        "UnrelaxedStructure": URSList,
    }

    # ^ 将字典写入json文件
    with open(output, "w") as f:
        json.dump(data, f, indent=4)

    print(f"--> {os.path.abspath(output)} 写入成功！\n")


def _getef(directory: str = "."):
    """读取NEB计算时各构型的能量和受力，NEB计算可以未收敛
    但如果初末态自洽在别处完成，请手动将其移入00等文件夹中！

    Parameters
    ----------
    directory: str
        NEB计算的路径，默认当前路径

    Returns
    -------
    subfolders: list
        构型文件夹名列表
    resort_mfs: list
        构型受力的最大分量列表
    rcs: list
        反应坐标列表
    ens: list
        电子总能列表
    dEs: list
        与初始构型的能量差列表

    Examples
    --------
    >>> from dspawpy.diffusion.nebtools import getef
    >>> directory = '.'  # NEB计算的路径，默认当前路径
    >>> subfolders, resort_mfs, rcs, ens, dEs = getef(directory)
    >>> print(subfolders)
    ['00', '01', '02', '03', '04', '05', '06']
    >>> print(resort_mfs)
    [0.186876802632, 0.087370747812, 0.039940517914, 0.061764168138, 0.042459986924, 0.864285419627, 0.035218915742]
    >>> print(rcs)
    [0.         0.70762104 1.41440524 2.10669668 2.79829788 3.52986152 4.26191179]
    >>> print(ens)
    [-42922.75544084902, -42922.495919381065, -42921.96332356572, -42922.038481743206, -42921.960565486996, -42922.464230317, -42922.70115500509]
    >>> print(dEs)
    [0.         0.25952147 0.79211728 0.71695911 0.79487536 0.29121053 0.05428584]
    """

    subfolders = get_neb_subfolders(directory)
    Nimage = len(subfolders)

    ens = []
    dEs = np.zeros(Nimage)
    rcs = [0]
    mfs = []

    # read energies
    count = 1
    for i, subfolder in enumerate(subfolders):
        if i == 0 or i == Nimage - 1:
            jsf = os.path.join(directory, subfolder, f"system{subfolder}.json")
            old_jsf = os.path.join(directory, subfolder, "system.json")
            hf = os.path.join(directory, subfolder, "scf.h5")

            if os.path.exists(hf):  # 优先读取h5文件内容
                data = h5py.File(hf)
                en = np.array(data.get("/Energy/TotalEnergy0"))
                if i == 0 or i == Nimage - 1:
                    mf = np.max(np.abs(np.array(data.get("/Force/ForceOnAtoms"))))
                    mfs.append(mf)

            elif os.path.exists(jsf):  # 其次读取json文件内容
                with open(jsf, "r") as f:
                    data = json.load(f)
                en = data["Energy"]["TotalEnergy0"]
                if i == 0 or i == Nimage - 1:
                    mf = np.max(np.abs(data["Force"]["ForceOnAtoms"]))
                    mfs.append(mf)

            elif os.path.exists(old_jsf):  # 兼容老json
                with open(old_jsf, "r") as f:
                    data = json.load(f)
                en = data["Energy"]["TotalEnergy0"]
                if i == 0 or i == Nimage - 1:
                    mf = np.max(np.abs(data["Force"]["ForceOnAtoms"]))
                    mfs.append(mf)

            else:
                raise FileNotFoundError(
                    "无法找到记录构型%s的能量和受力的system.json或scf.h5文件" % subfolder
                )
            ens.append(en)

        else:
            jsf = os.path.join(directory, subfolder, f"neb{subfolder}.json")
            sysjsf = os.path.join(directory, subfolder, f"system{subfolder}.json")
            old_sysjsf = os.path.join(directory, subfolder, "system.json")
            hf = os.path.join(directory, subfolder, f"neb{subfolder}.h5")

            if os.path.exists(hf):  # 优先读取h5文件内容
                data = h5py.File(hf)
                en = np.array(data.get("/Energy/TotalEnergy0"))
                mf = np.array(data.get("/MaxForce"))[-1]
                # the key may change depends on your DS-PAW version
                if "/Distance/Previous" in data:
                    rc = np.array(data.get("/Distance/Previous"))[-1]
                elif "/ReactionCoordinate" in data:
                    rc = np.array(data.get("/ReactionCoordinate"))[-2]
                else:
                    raise KeyError("找不到/Distance/Previous或/ReactionCoordinate键！")
                rcs.append(rc)
                if count == Nimage - 2:  # before final image
                    if "/Distance/Next" in data:
                        rc = np.array(data.get("/Distance/Next"))[-1]
                    elif "/ReactionCoordinate" in data:
                        rc = np.array(data.get("/ReactionCoordinate"))[-1]
                    else:
                        raise KeyError("找不到/Distance/Next或/ReactionCoordinate键！")
                    rcs.append(rc)

            elif os.path.exists(jsf):
                if os.path.exists(sysjsf):
                    with open(sysjsf, "r") as f:
                        data = json.load(f)
                    en = data["Energy"]["TotalEnergy0"]
                elif os.path.exists(old_sysjsf):  # 兼容旧版DS-PAW
                    with open(old_sysjsf, "r") as f:
                        data = json.load(f)
                    en = data["Energy"]["TotalEnergy0"]
                else:
                    raise FileNotFoundError(f"无法找到{sysjsf}或{old_sysjsf}")

                with open(jsf, "r") as f:
                    data = json.load(f)
                Nion_step = len(data)
                # en = data[Nion_step - 1]["TotalEnergy"] # invalid
                mf = data[Nion_step - 1]["MaxForce"]  # 最后一步的最大受力
                rc = data[Nion_step - 1]["ReactionCoordinate"][0]  # 最后一步的反应坐标
                rcs.append(rc)
                if count == Nimage - 2:  # before final image
                    rc = data[Nion_step - 1]["ReactionCoordinate"][1]  # 最后一步的反应坐标
                    rcs.append(rc)

            else:
                raise FileNotFoundError(f"无法找到{hf}或{jsf}")

            ens.append(en)
            mfs.append(mf)

            # get dE
            dE = ens[count] - ens[0]
            dEs[i] = dE
            count += 1
    dEs[-1] = ens[Nimage - 1] - ens[0]

    # rcs 改成累加值
    for i in range(1, len(rcs)):
        rcs[i] += rcs[i - 1]

    rcs = np.array(rcs)

    resort_mfs = [mfs[0]]
    final_mf = mfs[1]
    for j in range(2, len(mfs)):
        resort_mfs.append(mfs[j])
    resort_mfs.append(final_mf)

    return subfolders, resort_mfs, rcs, ens, dEs
