import argparse, os, re, platform, glob
import matplotlib.pyplot as plt
from bandplot import plots, readdata
from bandplot import __version__

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['ytick.minor.visible'] = True
plt.rcParams["mathtext.fontset"] = 'cm'

class cla_fig:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, str):
                exec('self.%s = "%s"' %(key, value))
            else:
                exec('self.%s = %s' %(key, value))

def main():
    parser = argparse.ArgumentParser(description='Plot the band structure or DOS from vaspkit result.',
                                     epilog='''
Example:
bandplot -i BAND.dat -o BAND.png -l g m k g -d PDOS* -z
''',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', "--version",    action="version",     version="bandplot "+__version__+" from "+os.path.dirname(__file__)+' (python'+platform.python_version()+')')
    parser.add_argument('-s', "--size",       type=int,   nargs=2,  help='figure size: width, height')
    parser.add_argument('-b', "--divided",    action='store_true',  help="plot the up and down spin in divided subplot")
    parser.add_argument('-y', "--vertical",   type=float, nargs=2,  help="energy (eV) range, default: [-5.0, 5.0]")
    parser.add_argument('-g', "--legend",     type=str,             nargs='+', help="legend labels", default=[])
    parser.add_argument('-a', "--location",   type=str.lower,       choices=['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right',
                                                                             'center left', 'center right', 'lower center', 'upper center', 'center'],
                                                                    help="arrange the legend location, default: best", default='best')
    parser.add_argument('-c', "--color",      type=str,             nargs='+', help="line color: b, blue; g, green; r, red; c, cyan; m, magenta; y, yellow;"+
                                                                                    "k, black; w, white", default=[])
    parser.add_argument('-k', "--linestyle",  type=str,             nargs='+', help="linestyle: solid, dashed, dashdot, dotted or tuple; default: solid",
                                                                                    default=[])
    parser.add_argument('-w', "--linewidth",  type=str,             nargs='+', help="linewidth, default: 0.8", default=[])
    parser.add_argument('-i', "--input",      type=str,             nargs='+', help="plot figure from .dat file, default: BAND.dat", default=["BAND.dat"])
    parser.add_argument('-o', "--output",     type=str,             help="plot figure filename, default: BAND.png", default="BAND.png")
    parser.add_argument('-q', "--dpi",        type=int,             help="dpi of the figure, default: 500", default=500)
    parser.add_argument('-j', "--klabels",    type=str,             help="filename of KLABELS, default: KLABELS", default="KLABELS")
    parser.add_argument('-l', "--labels",     type=str.upper,       nargs='+', default=[], help='labels for high-symmetry points, such as X S Y K M')
    parser.add_argument('-d', "--dos",        type=str,             nargs='+', default=[], help="plot DOS from .dat file, or file list")
    parser.add_argument('-x', "--horizontal", type=float, nargs=2,  help="Density of states, electrons/eV range")
    parser.add_argument('-n', "--exchange",   action='store_true',  help="exchange the x and y axes of DOS")
    parser.add_argument('-p', "--partial",    type=str,             nargs='+', default=[], help='the partial DOS to plot, s p d')
    parser.add_argument('-e', "--elements",   type=str,             nargs='+', default=[], help="PDOS labels")
    parser.add_argument('-r', "--wratios",    type=float,           help='width ratio for DOS subplot')
    parser.add_argument('-z', "--fill",       action='store_true',  help='fill a shaded region between PDOS and axis')
    parser.add_argument('-f', "--font",       type=str,             help="font to use", default='STIXGeneral')

    args = parser.parse_args()

    labels = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', re.sub('^GA[A-Z]+$|^G$', 'Γ', i))) for i in args.labels]
    elements = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', i)) for i in args.elements]
    dosfiles = [f for i in args.dos for f in glob.glob(i)]

    color = []
    for i in args.color:
        j = i.split('*')
        if len(j) == 2:
            color = color + [j[0]] * int(j[1])
        else:
            color.append(i)

    linestyle = []
    for i in args.linestyle:
        if len(i) > 2 and i[0] == '(' and i[-1] == ')':
            linestyle.append(eval(i))
        elif len(i.split('*')) == 2:
            j = i.split('*')
            linestyle = linestyle + [j[0]] * int(j[1])
        else:
            linestyle.append(i)

    linewidth = []
    for i in args.linewidth:
        if len(i.split('*')) == 2:
            j = i.split('*')
            linewidth = linewidth + [float(j[0])] * int(j[1])
        else:
            linewidth.append(float(i))

    plt.rcParams['font.family'] = '%s'%args.font

    pltname = os.path.split(os.getcwd())[-1]
    formula = ''
    if os.path.exists('POSCAR'):
        symbol, factor = readdata.symbols('POSCAR')
        for i in range(len(symbol)):
            if factor[i] > 1:
                formula = formula + symbol[i]
                for j in str(factor[i]):
                    formula = formula + '$_'+ j + '$'
            else:
                formula = formula + symbol[i]

    legend = args.legend or [formula] or [pltname]

    fig_p = cla_fig(output=args.output, size=args.size, vertical=args.vertical, horizontal=args.horizontal,
                    color=color, linestyle=linestyle, linewidth=linewidth, location=args.location, dpi=args.dpi)
    bandfile = [f for i in args.input for f in glob.glob(i)]
    if len(bandfile) == 1:
        if not fig_p.vertical:
            fig_p.vertical = [-5.0, 5.0]
        arr, bands, ispin = readdata.bands(bandfile[0])
        ticks   = []
        klabels = []
        if os.path.exists(args.klabels):
            ticks, klabels = readdata.klabels(args.klabels)

        if len(labels) == 0:
            labels=[re.sub('GAMMA|Gamma|G', 'Γ', re.sub('Undefined|Un|[0-9]', '', i)) for i in klabels]

        if len(ticks) > len(labels):
            labels = labels + [''] * (len(ticks) - len(labels))
        elif len(ticks) < len(labels):
            labels = labels[:len(ticks)]

        if not dosfiles:
            if ispin == "Noneispin":
                plots.Noneispin(arr, bands, ticks, labels, legend, fig_p)
            elif ispin == "Ispin" and not args.divided:
                plots.Ispin(arr, bands, ticks, labels, legend, fig_p)
            elif ispin == "Ispin" and args.divided:
                plots.Dispin(arr, bands, ticks, labels, legend, fig_p)
        else:
            darr, dele, s_elements = readdata.dos(args.dos)
            index_f, labels_elements = readdata.select(s_elements, args.partial)
            if not elements:
                elements = labels_elements
            if not args.wratios:
                if not args.divided:
                    width_ratios = 0.5
                else:
                    width_ratios = 0.3
            else:
                width_ratios = args.wratios

            if ispin == "Noneispin":
                plots.NoneispinWd(arr, bands, ticks, labels, darr, dele, args.fill, index_f, elements, width_ratios, legend, fig_p)
            elif ispin == "Ispin" and not args.divided:
                plots.IspinWd(arr, bands, ticks, labels, darr, dele, args.fill, index_f, elements, width_ratios, legend, fig_p)
            elif ispin == "Ispin" and args.divided:
                plots.DispinWd(arr, bands, ticks, labels, darr, dele, args.fill, index_f, elements, width_ratios, legend, fig_p)

    elif len(bandfile) == 0:
        if dosfiles:
            if fig_p.output == "BAND.png":
                fig_p.output = "DOS.png"
            darr, dele, s_elements = readdata.dos(dosfiles)
            index_f, labels_elements = readdata.select(s_elements, args.partial)
            if not elements:
                elements = labels_elements

            plots.pdosfiles(darr, dele, args.fill, index_f, elements, legend, args.exchange, fig_p)
        else:
            print('No .dat file!')

    if len(bandfile) == 2:
        if not fig_p.vertical:
            fig_p.vertical = [-5.0, 5.0]
        arr = [''] * 2
        bands = [''] * 2
        ispin = [''] * 2
        arr[0], bands[0], ispin[0] = readdata.bands(bandfile[0])
        arr[1], bands[1], ispin[1] = readdata.bands(bandfile[1])
        ticks   = []
        klabels = []
        if os.path.exists(args.klabels):
            ticks, klabels = readdata.klabels(args.klabels)

        if len(labels) == 0:
            labels=[re.sub('GAMMA|Gamma|G', 'Γ', re.sub('Undefined|Un|[0-9]', '', i)) for i in klabels]

        if len(ticks) > len(labels):
            labels = labels + [''] * (len(ticks) - len(labels))
        elif len(ticks) < len(labels):
            labels = labels[:len(ticks)]

        if len(legend) < 3:
            legend = legend + [''] * (3 - len(legend))

        if all(x == "Noneispin" for x in ispin):
            plots.Noneispin2(arr, bands, ticks, labels, legend, fig_p)
        elif all(x == "Ispin" for x in ispin):
            plots.Dispin2(arr, bands, ticks, labels, legend, fig_p)

def pmain():
    parser = argparse.ArgumentParser(description='Plot the phonon band structure or DOS from phonopy results.',
                                     epilog='''
Example:
pbandplot -i BAND.dat -o BAND.png -l g m k g -d projected_dos.dat -g \$\\pi^2_4\$ -e Si C O
''',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-v', "--version",    action="version",     version="bandplot "+__version__+" from "+os.path.dirname(__file__)+' (python'+platform.python_version()+')')
    parser.add_argument('-s', "--size",       type=float, nargs=2,  help='figure size: width, height')
    parser.add_argument('-b', "--broken",     type=float, nargs=2,  help='broken axis: start, end')
    parser.add_argument('-r', "--hratios",    type=float,           help='height ratio for broken axis, default: 0.2', default=0.2)
    parser.add_argument('-y', "--vertical",   type=float, nargs=2,  help="frequency (THz) range")
    parser.add_argument('-g', "--legend",     type=str,   nargs=1,  help="legend labels")
    parser.add_argument('-a', "--location",   type=str.lower,       choices=['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right',
                                                                             'center left', 'center right', 'lower center', 'upper center', 'center'],
                                                                    help="arrange the legend location, default: best", default='best')
    parser.add_argument('-c', "--color",      type=str,             nargs='+', help="line color: b, blue; g, green; r, red; c, cyan; m, magenta; y, yellow;"+
                                                                                    "k, black; w, white", default=[])
    parser.add_argument('-k', "--linestyle",  type=str,             nargs='+', help="linestyle: solid, dashed, dashdot, dotted or tuple; default: solid",
                                                                                    default=[])
    parser.add_argument('-w', "--linewidth",  type=str,             nargs='+', help="linewidth, default: 0.8", default=[])
    parser.add_argument('-i', "--input",      type=str,             help="plot figure from .dat file, default: BAND.dat", default="BAND.dat")
    parser.add_argument('-o', "--output",     type=str,             help="plot figure filename, default: BAND.png", default="BAND.png")
    parser.add_argument('-q', "--dpi",        type=int,             help="dpi of the figure, default: 500", default=500)
    parser.add_argument('-j', "--bandconf",   type=str,             help="filename of band setting file, default: band.conf", default="band.conf")
    parser.add_argument('-l', "--labels",     type=str.upper,       nargs='+', default=[], help='labels for high-symmetry points, such as X S Y K M')
    parser.add_argument('-d', "--dos",        type=str,             help="plot Phonon DOS from .dat file")
    parser.add_argument('-x', "--horizontal", type=float, nargs=2,  help="Phonon density of states range")
    parser.add_argument('-n', "--exchange",   action='store_true',  help="exchange the x and y axes of Phonon DOS")
    parser.add_argument('-e', "--elements",   type=str,             nargs='+', default=[], help="PDOS labels")
    parser.add_argument('-p', "--wratios",    type=float,           help='width ratio for DOS subplot, default 0.5', default=0.5)
    parser.add_argument('-z', "--fill",       action='store_true',  help='fill a shaded region between PDOS and axis')
    parser.add_argument('-f', "--font",       type=str,             help="font to use", default='STIXGeneral')

    args = parser.parse_args()

    labels = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', re.sub('^GA[A-Z]+$|^G$', 'Γ', i))) for i in args.labels]
    elements = [re.sub("'|‘|’", '′', re.sub('"|“|”', '″', i)) for i in args.elements]
    color  = []
    for i in args.color:
        j = i.split('*')
        if len(j) == 2:
            color = color + [j[0]] * int(j[1])
        else:
            color.append(i)

    linestyle = []
    for i in args.linestyle:
        if len(i) > 2 and i[0] == '(' and i[-1] == ')':
            linestyle.append(eval(i))
        elif len(i.split('*')) == 2:
            j = i.split('*')
            linestyle = linestyle + [j[0]] * int(j[1])
        else:
            linestyle.append(i)

    linewidth = []
    for i in args.linewidth:
        if len(i.split('*')) == 2:
            j = i.split('*')
            linewidth = linewidth + [float(j[0])] * int(j[1])
        else:
            linewidth.append(float(i))

    plt.rcParams['font.family'] = '%s'%args.font
    pltname = os.path.split(os.getcwd())[-1]
    s_ele = []
    formula = ''
    if os.path.exists('POSCAR-unitcell'):
        symbol, factor = readdata.symbols('POSCAR-unitcell')
        for i in range(len(symbol)):
            if factor[i] > 1:
                s_ele = s_ele + [symbol[i]] * factor[i]
                formula = formula + symbol[i]
                for j in str(factor[i]):
                    formula = formula + '$_'+ j + '$'
            else:
                s_ele = s_ele + [symbol[i]]
                formula = formula + symbol[i]

    if not elements and s_ele:
        elements = s_ele

    legend = args.legend or [formula] or [pltname]

    broken = args.broken
    height_ratio = args.hratios
    if height_ratio >= 1 or height_ratio <= 0:
        height_ratio = 0.2

    width_ratios = args.wratios
    if width_ratios >= 1 or width_ratios <= 0:
        width_ratios = 0.5

    fig_p = cla_fig(output=args.output, size=args.size, vertical=args.vertical, horizontal=args.horizontal,
                    color=color, linestyle=linestyle, linewidth=linewidth, location=args.location, dpi=args.dpi)
    if os.path.exists(args.input):
        arr, fre, ticks = readdata.pbands(args.input)
        klabels = []
        if os.path.exists(args.bandconf):
            klabels = readdata.bandset(args.bandconf)
        if len(labels) == 0:
            labels=[re.sub('^GA[A-Z]+$|^G$', 'Γ', i) for i in klabels]
        if len(ticks) > len(labels):
            labels = labels + [''] * (len(ticks) - len(labels))
        elif len(ticks) < len(labels):
            labels = labels[:len(ticks)]
        if args.dos is None:
            if args.broken is None:
                plots.Nobroken(arr, fre, ticks, labels, legend, fig_p)
            else:
                plots.Broken(arr, fre, ticks, labels, broken, height_ratio, legend, fig_p)
        elif os.path.exists(args.dos):
            darr, dele = readdata.pdos(args.dos)
            if args.broken is None:
                plots.NobrokenWd(arr, fre, ticks, labels, darr, dele, args.fill, elements, width_ratios, legend, fig_p)
            else:
                plots.BrokenWd(arr, fre, ticks, labels, broken, height_ratio, darr, dele, args.fill, elements, width_ratios, legend, fig_p)

    else:
        if args.dos and os.path.exists(args.dos):
            darr, dele = readdata.pdos(args.dos)
            plots.dosfile(darr, dele, args.fill, elements, legend, args.exchange, fig_p)
        else:
            print('No .dat file!')

