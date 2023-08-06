import numpy as np
import re

def klabels(KLABELS):
    with open(KLABELS, "r") as main_file:
        lines = main_file.readlines()[1:]
    LABELS = [line.split() for line in lines if len(line.split()) == 2]
    ticks  = [float(label[1]) for label in LABELS]
    labels = [label[0] for label in LABELS]
    return ticks, labels

def bandset(bandconf):
    with open(bandconf, "r") as main_file:
        lines = main_file.readlines()
    LABELS = [line for line in lines if line.strip().startswith('BAND_LABELS')]
    if LABELS:
        LABELS = LABELS[-1].split("=")[-1].replace('\\','').upper().split()
    return LABELS

def dos(DOS):
    ARR = []
    ELE = []
    s_elements = []
    for pdos in DOS:
        with open(pdos, "r") as main_file:
            lines = main_file.readlines()
        arr = []
        ele = []
        for line in lines[1:]:
            values = [float(val) for val in line.split() if val]
            if values:
                arr.append(values[0])
                ele.append(values[1:])
        ARR.append(np.array(arr))
        ELE.append(np.array(ele))
        s_elements.append([re.sub('.dat|^[A-Za-z]+_', '', pdos)] + lines[0].split()[1:])
    return ARR, ELE, s_elements

def select(s_elements, partial):
    partial = [i for i in partial if i.strip()]
    num = len(s_elements)
    if not partial:
        index = [(i, -1) for i in range(num)]
    elif partial[0] == 'all':
        index = [(i, j) for i in range(num) for j in range(1, len(s_elements[i]))]
    else:
        index = []
        for str0 in partial:
            if str0.islower():
                str_list = str0.split(',')
                for i, elem in enumerate(s_elements):
                    for j, sub_elem in enumerate(elem):
                        if j == 0 or sub_elem not in str_list:
                            continue
                        index.append((i, j))
            else:
                str_list = [i.strip() for i in str0.split('-') if i.strip()]
                if len(str_list) == 1:
                    for i, elem in enumerate(s_elements):
                        if elem[0] == str_list[0]:
                            index += [(i, j) for j in range(1, len(elem))]
                elif len(str_list) == 2:
                    for i, elem in enumerate(s_elements):
                        if elem[0] == str_list[0]:
                            index += [(i, j) for j, sub_elem in enumerate(elem)
                                      if j > 0 and sub_elem in str_list[1].split(',')]
    labels_elements = [s_elements[i[0]][0] + '-$' + s_elements[i[0]][i[1]] + '$' for i in index]
    index_f = [(i, j-1) if j > 0 else (i, j) for i, j in index]
    return index_f, labels_elements

def bands(PLOT):
    with open(PLOT, "r") as main_file:
        lines = main_file.readlines()
    str0 = lines[0].split()
    if len(str0) == 2 and str0[1] == "Energy-Level(eV)":
        nkps = re.sub(':', ' ', lines[1]).split()
        m, n = int(nkps[-2]), int(nkps[-1])
        arr = np.zeros(m)
        bands = np.zeros((n,m))
        reverse = False
        for i in lines[2:]:
            str = i.split()
            if i[0] == '#':
                j = int(str[-1])
                k = 0
            elif len(str) > 0:
                if j == 1:
                    arr[k], bands[0,k] = float(str[0]), float(str[1])
                    k += 1
                else:
                    N = j - 1
                    if k == 0:
                        if float(str[0]) == 0:
                            reverse = False
                        else:
                            reverse = True
                    if reverse:
                        K = m-k-1
                    else:
                        K = k
                    bands[N,K] = float(str[1])
                    k += 1
            else:
                pass
        return arr, bands, "Noneispin"
    elif len(str0) == 3 and str0[1] == "Spin-Up(eV)" and str0[2] == "Spin-down(eV)":
        nkps = lines[1].split()
        m, n = int(nkps[-2]), int(nkps[-1])
        arr = np.zeros(m)
        bands = np.zeros((2,n,m))
        reverse = False
        for i in lines[2:]:
            str = i.split()
            if i[0] == '#':
                j = int(str[-1])
                k = 0
            elif len(str) > 0:
                if j == 1:
                    arr[k], bands[0,0,k], bands[1,0,k] = float(str[0]), float(str[1]), float(str[2])
                    k += 1
                else:
                    N = j - 1
                    if k == 0:
                        if float(str[0]) == 0:
                            reverse = False
                        else:
                            reverse = True
                    if reverse:
                        K = m-k-1
                    else:
                        K = k
                    bands[0,N,K], bands[1,N,K] = float(str[1]), float(str[2])
                    k += 1
            else:
                pass
        return arr, bands, "Ispin"
    else:
        pass

def symbols(POSCAR):
    with open(POSCAR, "r") as main_file:
        lines = main_file.readlines()
    symbol = lines[5].split()
    factor = [int(i) for i in lines[6].split()]
    return symbol, factor

def pbands(PLOT):
    with open(PLOT, "r") as main_file:
        lines = main_file.readlines()
    ticks = [float(i) for i in lines[1].replace("#","").split()]
    arr = []
    fre = []
    k = 0
    for i in lines[2:]:
        str = i.split()
        if len(str) > 0:
            j = float(str[0])
            if j == 0.0:
                k += 1
            if k == 1:
                arr.append(j)
                fre.append(float(str[1]))
            else:
                fre.append(float(str[1]))
    arr = np.array(arr)
    fre = np.array(fre).reshape(-1,len(arr))
    return arr, fre, ticks

def pdos(DOS):
    data = np.loadtxt(DOS)
    arr = data[:, 0]
    ele = data[:, 1:]
    return arr, ele

