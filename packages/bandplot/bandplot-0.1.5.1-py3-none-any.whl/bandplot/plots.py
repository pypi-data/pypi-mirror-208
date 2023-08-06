import matplotlib.pyplot as plt

# bandplot

def Noneispin(arr, bands, ticks, labels, legend, fig_p):
    plt.figure(figsize=fig_p.size)
    color = fig_p.color or ['r']
    linestyle = fig_p.linestyle or ['-']
    linewidth = fig_p.linewidth or [0.8]
    plt.plot(arr, bands.T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    plt.tick_params(axis='y', which='minor', color='gray')
    plt.axhline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0],arr[-1]
        for i in ticks[1:-1]:
            plt.axvline(i, linewidth=0.4, linestyle='-.', c='gray')
    plt.xticks(ticks,labels)
    plt.legend([legend[0]], frameon=False, prop={'size':'medium'}, loc=fig_p.location)
    plt.xlim(arr[0], arr[-1])
    plt.ylim(fig_p.vertical)
    plt.ylabel('Energy (eV)')
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def Noneispin2(arr, bands, ticks, labels, legend, fig_p):
    plt.figure(figsize=fig_p.size)
    color = fig_p.color or ['r', 'k']
    linestyle = fig_p.linestyle or ['-', '-.']
    linewidth = fig_p.linewidth or [0.8, 0.8]
    if len(color) == 1:
        color = [color[0], 'k']
    if len(linestyle) == 1:
        linestyle = [linestyle[0], '-.']
    if len(linewidth) == 1:
        linewidth = [linewidth[0], 0.8]
    f = plt.plot(arr[0], bands[0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    plt.tick_params(axis='y', which='minor', color='gray')
    plt.axhline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0][0],arr[0][-1]
        for i in ticks[1:-1]:
            plt.axvline(i, linewidth=0.4, linestyle='-.', c='gray')
    plt.xticks(ticks,labels)
    plt.xlim(arr[0][0], arr[0][-1])
    plt.ylim(fig_p.vertical)
    plt.ylabel('Energy (eV)')
    ax = plt.axes()
    g = ax.plot(arr[1], bands[1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    ax.set_xlim(arr[1][0], arr[1][-1])
    ax.set_ylim(fig_p.vertical)
    ax.axis('off')
    L = plt.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'medium'})
    plt.gca().add_artist(L)
    plt.legend([f[0], g[0]], [legend[1], legend[2]], frameon=False, prop={'size':'medium'}, loc=fig_p.location)
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def Noneispin3(arr, bands, ticks, labels, legend, fig_p):
    plt.figure(figsize=fig_p.size)
    color = fig_p.color or ['r', 'k', 'b']
    linestyle = fig_p.linestyle or ['-', '-.', ':']
    linewidth = fig_p.linewidth or [0.8, 0.8, 0.8]
    if len(color) < 3:
        color = color + [''] * (3 - len(color))
    if len(linestyle) < 3:
        linestyle = linestyle + ['-'] * (3 - len(linestyle))
    if len(linewidth) < 3:
        linewidth = linewidth + [0.8] * (3 - len(linewidth))
    f = plt.plot(arr[0], bands[0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    plt.tick_params(axis='y', which='minor', color='gray')
    plt.axhline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0][0],arr[0][-1]
        for i in ticks[1:-1]:
            plt.axvline(i, linewidth=0.4, linestyle='-.', c='gray')
    plt.xticks(ticks,labels)
    plt.xlim(arr[0][0], arr[0][-1])
    plt.ylim(fig_p.vertical)
    plt.ylabel('Energy (eV)')
    ax = plt.axes()
    g = ax.plot(arr[1], bands[1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    ax.set_xlim(arr[1][0], arr[1][-1])
    ax.set_ylim(fig_p.vertical)
    ax.axis('off')
    af = plt.axes()
    h = ax.plot(arr[2], bands[2].T, color=color[2], linewidth=linewidth[2], linestyle=linestyle[2])
    af.set_xlim(arr[2][0], arr[2][-1])
    af.set_ylim(fig_p.vertical)
    af.axis('off')
    L = plt.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'medium'})
    plt.gca().add_artist(L)
    plt.legend([f[0], g[0], h[0]], [legend[1], legend[2], legend[3]], frameon=False, prop={'size':'medium'}, loc=fig_p.location)
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def Ispin(arr, bands, ticks, labels, legend, fig_p):
    plt.figure(figsize=fig_p.size)
    color = fig_p.color or ['r', 'k']
    linestyle = fig_p.linestyle or ['-', '-.']
    linewidth = fig_p.linewidth or [0.8, 0.8]
    if len(color) == 1:
        color = [color[0], 'k']
    if len(linestyle) == 1:
        linestyle = [linestyle[0], '-.']
    if len(linewidth) == 1:
        linewidth = [linewidth[0], 0.8]
    p_up = plt.plot(arr, bands[0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    p_do = plt.plot(arr, bands[1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    plt.legend([p_up[0], p_do[0]], ['up', 'down'], frameon=False, prop={'style':'italic', 'size':'medium'}, loc=fig_p.location,
                alignment='left', title=legend[0], title_fontproperties={'size':'medium'})
    plt.tick_params(axis='y', which='minor', color='gray')
    plt.axhline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0],arr[-1]
        for i in ticks[1:-1]:
            plt.axvline(i, linewidth=0.4, linestyle='-.', c='gray')

    plt.xlim(arr[0], arr[-1])
    plt.ylim(fig_p.vertical)
    plt.xticks(ticks,labels)
    plt.ylabel('Energy (eV)')
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def Dispin(arr, bands, ticks, labels, legend, fig_p):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_p.size)
    fig.subplots_adjust(wspace=0.0)
    color = fig_p.color or ['r', 'k']
    linestyle = fig_p.linestyle or ['-', '-.']
    linewidth = fig_p.linewidth or [0.8, 0.8]
    if len(color) == 1:
        color = [color[0], 'k']
    if len(linestyle) == 1:
        linestyle = [linestyle[0], '-.']
    if len(linewidth) == 1:
        linewidth = [linewidth[0], 0.8]
    ax1.plot(arr, bands[0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    ax2.plot(arr, bands[1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    L = ax1.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'medium'})
    ax1.add_artist(L)
    ax1.legend(['up'], frameon=False, prop={'style':'italic', 'size':'medium'}, loc=fig_p.location)
    ax2.legend(['down'], frameon=False, prop={'style':'italic', 'size':'medium'}, loc=fig_p.location)
    ax1.tick_params(axis='y', which='minor', color='gray')
    ax2.tick_params(axis='y', which='minor', color='gray')

    ax1.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.set_yticklabels([])
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0],arr[-1]
        for i in ticks[1:-1]:
            ax1.axvline(i, linewidth=0.4, linestyle='-.', c='gray')
            ax2.axvline(i, linewidth=0.4, linestyle='-.', c='gray')

    ax1.set_xlim(arr[0], arr[-1])
    ax1.set_ylim(fig_p.vertical)
    ax2.set_xlim(arr[0], arr[-1])
    ax2.set_ylim(fig_p.vertical)
    if len(labels) > 0:
        ax1.set_xticks(ticks,labels[:-1]+[''])
    else:
        ax1.set_xticks(ticks,labels)
    ax2.set_xticks(ticks,labels)
    ax1.set_ylabel('Energy (eV)')
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def Dispin2(arr, bands, ticks, labels, legend, fig_p):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_p.size)
    fig.subplots_adjust(wspace=0.0)
    color = fig_p.color or ['r', 'r', 'k', 'k']
    linestyle = fig_p.linestyle or ['-', '-', '-.', '-.']
    linewidth = fig_p.linewidth or [0.8, 0.8, 0.8, 0.8]
    if len(color) < 4:
        color = color + [''] * (4 - len(color))
    if len(linestyle) < 4:
        linestyle = linestyle + ['-'] * (4 - len(linestyle))
    if len(linewidth) < 4:
        linewidth = linewidth + [0.8] * (4 - len(linewidth))
    f1 = ax1.plot(arr[0], bands[0][0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    f2 = ax2.plot(arr[0], bands[0][1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    L = ax1.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'medium'})
    ax1.add_artist(L)
    ax1.tick_params(axis='y', which='minor', color='gray')
    ax2.tick_params(axis='y', which='minor', color='gray')

    ax1.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.set_yticklabels([])
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0][0],arr[0][-1]
        for i in ticks[1:-1]:
            ax1.axvline(i, linewidth=0.4, linestyle='-.', c='gray')
            ax2.axvline(i, linewidth=0.4, linestyle='-.', c='gray')

    ax1.set_xlim(arr[0][0], arr[0][-1])
    ax1.set_ylim(fig_p.vertical)
    ax2.set_xlim(arr[0][0], arr[0][-1])
    ax2.set_ylim(fig_p.vertical)
    if len(labels) > 0:
        ax1.set_xticks(ticks,labels[:-1]+[''])
    else:
        ax1.set_xticks(ticks,labels)
    ax2.set_xticks(ticks,labels)
    ax1.set_ylabel('Energy (eV)')

    ax1_f = fig.add_subplot(1,2,1)
    g1 = ax1_f.plot(arr[1], bands[1][0].T, color=color[2], linewidth=linewidth[2], linestyle=linestyle[2])
    ax1_f.set_xlim(arr[1][0], arr[1][-1])
    ax1_f.set_ylim(fig_p.vertical)
    ax1_f.axis('off')
    ax2_f = fig.add_subplot(1,2,2)
    g2 = ax2_f.plot(arr[1], bands[1][1].T, color=color[3], linewidth=linewidth[3], linestyle=linestyle[3])
    ax2_f.set_xlim(arr[1][0], arr[1][-1])
    ax2_f.set_ylim(fig_p.vertical)
    ax2_f.axis('off')

    ax1.legend([f1[0], g1[0]], [legend[1], legend[2]], frameon=False, prop={'size':'medium'}, loc=fig_p.location,
                alignment='left', title='up', title_fontproperties={'style':'italic', 'size':'medium'})
    ax2.legend([f2[0], g2[0]], [legend[1], legend[2]], frameon=False, prop={'size':'medium'}, loc=fig_p.location,
                alignment='left', title='down', title_fontproperties={'style':'italic', 'size':'medium'})
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def Dispin3(arr, bands, ticks, labels, legend, fig_p):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=fig_p.size)
    fig.subplots_adjust(wspace=0.0)
    color = fig_p.color or ['r', 'r', 'k', 'k', 'b', 'b']
    linestyle = fig_p.linestyle or ['-', '-', '-.', '-.', ':', ':']
    linewidth = fig_p.linewidth or [0.8] * 6
    if len(color) < 6:
        color = color + [''] * (6 - len(color))
    if len(linestyle) < 6:
        linestyle = linestyle + ['-'] * (6 - len(linestyle))
    if len(linewidth) < 6:
        linewidth = linewidth + [0.8] * (6 - len(linewidth))
    f1 = ax1.plot(arr[0], bands[0][0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    f2 = ax2.plot(arr[0], bands[0][1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    L = ax1.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'medium'})
    ax1.add_artist(L)
    ax1.tick_params(axis='y', which='minor', color='gray')
    ax2.tick_params(axis='y', which='minor', color='gray')

    ax1.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.set_yticklabels([])
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0][0],arr[0][-1]
        for i in ticks[1:-1]:
            ax1.axvline(i, linewidth=0.4, linestyle='-.', c='gray')
            ax2.axvline(i, linewidth=0.4, linestyle='-.', c='gray')

    ax1.set_xlim(arr[0][0], arr[0][-1])
    ax1.set_ylim(fig_p.vertical)
    ax2.set_xlim(arr[0][0], arr[0][-1])
    ax2.set_ylim(fig_p.vertical)
    if len(labels) > 0:
        ax1.set_xticks(ticks,labels[:-1]+[''])
    else:
        ax1.set_xticks(ticks,labels)
    ax2.set_xticks(ticks,labels)
    ax1.set_ylabel('Energy (eV)')

    ax1_f = fig.add_subplot(1,2,1)
    g1 = ax1_f.plot(arr[1], bands[1][0].T, color=color[2], linewidth=linewidth[2], linestyle=linestyle[2])
    ax1_f.set_xlim(arr[1][0], arr[1][-1])
    ax1_f.set_ylim(fig_p.vertical)
    ax1_f.axis('off')
    ax2_f = fig.add_subplot(1,2,2)
    g2 = ax2_f.plot(arr[1], bands[1][1].T, color=color[3], linewidth=linewidth[3], linestyle=linestyle[3])
    ax2_f.set_xlim(arr[1][0], arr[1][-1])
    ax2_f.set_ylim(fig_p.vertical)
    ax2_f.axis('off')

    ax1_g = fig.add_subplot(1,2,1)
    h1 = ax1_f.plot(arr[2], bands[2][0].T, color=color[4], linewidth=linewidth[4], linestyle=linestyle[4])
    ax1_g.set_xlim(arr[2][0], arr[2][-1])
    ax1_g.set_ylim(fig_p.vertical)
    ax1_g.axis('off')
    ax2_g = fig.add_subplot(1,2,2)
    h2 = ax2_f.plot(arr[2], bands[2][1].T, color=color[5], linewidth=linewidth[5], linestyle=linestyle[5])
    ax2_g.set_xlim(arr[2][0], arr[2][-1])
    ax2_g.set_ylim(fig_p.vertical)
    ax2_g.axis('off')
    ax1.legend([f1[0], g1[0], h1[0]], [legend[1], legend[2], legend[3]], frameon=False, prop={'size':'medium'}, loc=fig_p.location,
                alignment='left', title='up', title_fontproperties={'style':'italic', 'size':'medium'})
    ax2.legend([f2[0], g2[0], h2[0]], [legend[1], legend[2], legend[3]], frameon=False, prop={'size':'medium'}, loc=fig_p.location,
                alignment='left', title='down', title_fontproperties={'style':'italic', 'size':'medium'})
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def NoneispinWd(arr, bands, ticks, labels, darr, dele, index_f, elements, legend, fig_p):
    fig, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1-fig_p.width_ratios, fig_p.width_ratios], figsize=fig_p.size)
    fig.subplots_adjust(wspace=0.0)
    color = fig_p.color or ['r']
    linestyle = fig_p.linestyle or ['-']
    linewidth = fig_p.linewidth or [0.8]

    ax1.plot(arr, bands.T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    num = len(index_f)
    p_dos = []
    if num + 1 > len(color):
        color = color + [''] * (num + 1 - len(color))

    if num + 1 > len(linestyle):
        linestyle = linestyle + ['-'] * (num + 1 - len(linestyle))

    if num + 1 > len(linewidth):
        linewidth = linewidth + [0.8] * (num + 1 - len(linewidth))

    for i in range(num):
        if color[i+1]:
            ax2.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=linewidth[i+1], linestyle=linestyle[i+1], color=color[i+1])
            if fig_p.fill:
                plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, color=color[i+2], alpha=fig_p.fill)
        else:
            ax2.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=linewidth[i+1], linestyle=linestyle[i+1])
            if fig_p.fill:
                plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, alpha=fig_p.fill)

    ax1.legend([legend[0]], frameon=False, prop={'size':'small'}, loc=fig_p.location)
    ax1.tick_params(axis='y', which='minor', color='gray')
    ax2.minorticks_on()
    ax2.tick_params(axis='both', which='minor', color='gray')
    ax2.set_yticklabels([])
    ax2.legend(p_dos, elements, frameon=False, prop={'size':'small'}, loc=fig_p.location, alignment='left', title="Density of states", title_fontproperties={'size':'small'})
    ax1.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axvline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0],arr[-1]
        for i in ticks[1:-1]:
            ax1.axvline(i,linewidth=0.4,linestyle='-.',c='gray')

    ax1.set_xlim(arr[0], arr[-1])
    ax1.set_ylim(fig_p.vertical)
    ax2.set_xlim(fig_p.horizontal)
    ax2.set_ylim(fig_p.vertical)
    ax1.set_xticks(ticks,labels)
    ax2.tick_params(axis='x', labelsize='x-small', labelcolor='dimgray', labelrotation=-90, pad=1.5)
    ax1.set_ylabel('Energy (eV)')
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def IspinWd(arr, bands, ticks, labels, darr, dele, index_f, elements, legend, fig_p):
    fig, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1-fig_p.width_ratios, fig_p.width_ratios], figsize=fig_p.size)
    fig.subplots_adjust(wspace=0.0)
    color = fig_p.color or ['r', 'k']
    linestyle = fig_p.linestyle or ['-', '-.']
    linewidth = fig_p.linewidth or [0.8, 0.8]
    if len(color) == 1:
        color = [color[0], 'k']
    if len(linestyle) == 1:
        linestyle = [linestyle[0], '-.']
    if len(linewidth) == 1:
        linewidth = [linewidth[0], 0.8]
    p_up = ax1.plot(arr, bands[0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    p_do = ax1.plot(arr, bands[1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    ax1.legend([p_up[0], p_do[0]], ['up', 'down'], frameon=False, prop={'style':'italic', 'size':'small'}, loc=fig_p.location, alignment='left', title=legend[0], title_fontproperties={'size':'small'})
    num = len(index_f)
    p_dos = []
    if num + 2 > len(color):
        color = color + [''] * (num + 2 - len(color))

    if num + 2 > len(linestyle):
        linestyle = linestyle + ['-'] * (num + 2 - len(linestyle))

    if num + 2 > len(linewidth):
        linewidth = linewidth + [0.8] * (num + 2 - len(linewidth))

    for i in range(num):
        if color[i+2]:
            p_dos = p_dos + ax2.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=linewidth[i+2], linestyle=linestyle[i+2], color=color[i+2])
            if fig_p.fill:
                plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, color=color[i+2], alpha=fig_p.fill)
        else:
            p_dos = p_dos + ax2.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=linewidth[i+2], linestyle=linestyle[i+2])
            if fig_p.fill:
                plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, alpha=fig_p.fill)

    ax1.tick_params(axis='y', which='minor', color='gray')
    ax2.minorticks_on()
    ax2.tick_params(axis='both', which='minor', color='gray')
    ax2.axvline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.set_yticklabels([])
    ax2.legend(p_dos, elements, frameon=False, prop={'size':'small'}, loc=fig_p.location, alignment='left', title="Density of states", title_fontproperties={'size':'small'})
    ax1.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axhline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0],arr[-1]
        for i in ticks[1:-1]:
            ax1.axvline(i,linewidth=0.4, linestyle='-.', c='gray')

    ax1.set_xlim(arr[0], arr[-1])
    ax1.set_ylim(fig_p.vertical)
    ax2.set_xlim(fig_p.horizontal)
    ax2.set_ylim(fig_p.vertical)
    ax1.set_xticks(ticks,labels)
    ax2.tick_params(axis='x', labelsize='x-small', labelcolor='dimgray', labelrotation=-90, pad=1.5)
    ax1.set_ylabel('Energy (eV)')
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def DispinWd(arr, bands, ticks, labels, darr, dele, index_f, elements, legend, fig_p):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, width_ratios=[0.5*(1-fig_p.width_ratios), 0.5*(1-fig_p.width_ratios), fig_p.width_ratios], figsize=fig_p.size)
    fig.subplots_adjust(wspace=0.0)
    color = fig_p.color or ['r', 'k']
    linestyle = fig_p.linestyle or ['-', '-.']
    linewidth = fig_p.linewidth or [0.8, 0.8]
    if len(color) == 1:
        color = [color[0], 'k']
    if len(linestyle) == 1:
        linestyle = [linestyle[0], '-.']
    if len(linewidth) == 1:
        linewidth = [linewidth[0], 0.8]
    ax1.plot(arr, bands[0].T, color=color[0], linewidth=linewidth[0], linestyle=linestyle[0])
    ax2.plot(arr, bands[1].T, color=color[1], linewidth=linewidth[1], linestyle=linestyle[1])
    L = ax1.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'small'})
    ax1.add_artist(L)
    ax1.legend(['up'], frameon=False, prop={'style':'italic', 'size':'small'}, loc=fig_p.location)
    ax2.legend(['down'], frameon=False, prop={'style':'italic', 'size':'small'}, loc=fig_p.location)
    ax1.tick_params(axis='y', which='minor', color='gray')
    ax2.tick_params(axis='y', which='minor', color='gray')
    ax3.minorticks_on()
    ax3.tick_params(axis='both', which='minor', color='gray')
    num = len(index_f)
    p_dos = []
    if num + 2 > len(color):
        color = color + [''] * (num + 2 - len(color))

    if num + 2 > len(linestyle):
        linestyle = linestyle + ['-'] * (num + 2 - len(linestyle))

    if num + 2 > len(linewidth):
        linewidth = linewidth + [0.8] * (num + 2 - len(linewidth))

    for i in range(num):
        if color[i+2]:
            p_dos = p_dos + ax3.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=linewidth[i+2], linestyle=linestyle[i+2], color=color[i+2])
            if fig_p.fill:
                plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, color=color[i+2], alpha=fig_p.fill)
        else:
            p_dos = p_dos + ax3.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=linewidth[i+2], linestyle=linestyle[i+2])
            if fig_p.fill:
                plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, alpha=fig_p.fill)

    ax3.axvline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.set_yticklabels([])
    ax3.set_yticklabels([])
    ax3.legend(p_dos, elements, frameon=False, prop={'size':'small'}, loc=fig_p.location, alignment='left', title="Density of states", title_fontproperties={'size':'small'})

    ax1.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax2.axhline(linewidth=0.4, linestyle='-.', c='gray')
    ax3.axhline(linewidth=0.4, linestyle='-.', c='gray')
    if len(ticks) > 2:
        ticks[0],ticks[-1] = arr[0],arr[-1]
        for i in ticks[1:-1]:
            ax1.axvline(i,linewidth=0.4,linestyle='-.',c='gray')
            ax2.axvline(i,linewidth=0.4,linestyle='-.',c='gray')

    ax1.set_xlim(arr[0], arr[-1])
    ax1.set_ylim(fig_p.vertical)
    ax2.set_xlim(arr[0], arr[-1])
    ax2.set_ylim(fig_p.vertical)
    ax3.set_xlim(fig_p.horizontal)
    ax3.set_ylim(fig_p.vertical)
    if len(labels) > 0:
        ax1.set_xticks(ticks,labels[:-1]+[''])
    else:
        ax1.set_xticks(ticks,labels)
    ax2.set_xticks(ticks,labels)
    ax3.tick_params(axis='x', labelsize='x-small', labelcolor='dimgray', labelrotation=-90, pad=1.5)
    ax1.set_ylabel('Energy (eV)')
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

def pdosfiles(darr, dele, index_f, elements, legend, fig_p):
    plt.figure(figsize=fig_p.size)
    plt.minorticks_on()
    plt.tick_params(axis='both', which='minor', color='gray')
    num = len(index_f)
    p_dos = []
    color = fig_p.color
    linestyle = fig_p.linestyle
    linewidth = fig_p.linewidth
    if num > len(color):
        color = color + [''] * (num - len(color))

    if num > len(linestyle):
        linestyle = linestyle + ['-'] * (num - len(linestyle))

    if num > len(linewidth):
        linewidth = linewidth + [0.8] * (num - len(linewidth))

    if fig_p.exchange:
        for i in range(num):
            if color[i]:
                p_dos = p_dos + plt.plot(darr[index_f[i][0]], dele[index_f[i][0]].T[index_f[i][1]], linewidth=linewidth[i], linestyle=linestyle[i], color=color[i])
                if fig_p.fill:
                    plt.fill_between(darr[index_f[i][0]], dele[index_f[i][0]].T[index_f[i][1]], 0, color=color[i], alpha=fig_p.fill)
            else:
                p_dos = p_dos + plt.plot(darr[index_f[i][0]], dele[index_f[i][0]].T[index_f[i][1]], linewidth=linewidth[i], linestyle=linestyle[i])
                if fig_p.fill:
                    plt.fill_between(darr[index_f[i][0]], dele[index_f[i][0]].T[index_f[i][1]], 0, alpha=fig_p.fill)

        plt.tick_params(axis='y', labelsize='medium', labelcolor='dimgray')
        plt.xlim(fig_p.vertical)
        plt.ylim(fig_p.horizontal)
        plt.xlabel('Energy (eV)')
        plt.ylabel('Density of states, electrons/eV')
    else:
        for i in range(num):
            if color[i]:
                p_dos = p_dos + plt.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=0.8, linestyle=linestyle[i], color=color[i])
                if fig_p.fill:
                    plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, color=color[i], alpha=fig_p.fill)
            else:
                p_dos = p_dos + plt.plot(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], linewidth=0.8, linestyle=linestyle[i])
                if fig_p.fill:
                    plt.fill_between(dele[index_f[i][0]].T[index_f[i][1]], darr[index_f[i][0]], 0, alpha=fig_p.fill)

        plt.tick_params(axis='x', labelsize='medium', labelcolor='dimgray')
        plt.ylim(fig_p.vertical)
        plt.xlim(fig_p.horizontal)
        plt.ylabel('Energy (eV)')
        plt.xlabel('Density of states, electrons/eV')

    L = plt.legend([], frameon=False, loc='lower left', title=legend[0], title_fontproperties={'size':'medium'})
    plt.gca().add_artist(L)
    plt.axvline(linewidth=0.4, linestyle='-.', c='gray')
    plt.axhline(linewidth=0.4, linestyle='-.', c='gray')
    plt.legend(p_dos, elements, frameon=False, prop={'size':'medium'}, loc=fig_p.location)
    plt.savefig(fig_p.output, dpi=fig_p.dpi, transparent=True, bbox_inches='tight')

