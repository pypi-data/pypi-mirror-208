import logging
import math
import re
import time
from functools import reduce
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from matplotlib.animation import FuncAnimation

log = logging.getLogger(__name__)


def init_plot(rddict, fig=None, trans2D=True):
    '''非独立，初始化图片，建立坐标轴和label等'''
    dim = rddict['info']['dim']
    zshape = rddict['info']['zshape']
    zsize = reduce(lambda a, b: a * b, zshape, 1)

    axis_label = np.asarray(rddict['info'].get('axis_label', [])).flatten()
    z_label = np.asarray(rddict['info'].get('z_label', [])).flatten()
    axis_unit = np.asarray(rddict['info'].get('axis_unit', [])).flatten()
    z_unit = np.asarray(rddict['info'].get('z_unit', [])).flatten()

    fig = plt.figure() if fig is None else fig
    if zsize < 4:
        plot_shape = (1, zsize)
    else:
        n = int(np.sqrt(zsize))
        plot_shape = (math.ceil(zsize / n), n)
    if dim < 3 and zsize < 100:
        # fig.clear()
        figsize = plot_shape[1] * 8, plot_shape[0] * 6
        fig.set_size_inches(*figsize)
        axes = fig.subplots(*plot_shape)
        axes = np.array(axes).flatten()
    else:
        axes = []

    cb_list = []
    if dim == 1 and zsize < 101:
        for i in range(zsize):
            title = rddict['name'] + f' {i}' if zsize > 1 else rddict['name']
            try:
                xlabel = axis_label[0]
                ylabel = z_label[0] if len(z_label) == 1 else z_label[i]
            except:
                xlabel, ylabel = 'X', 'Y'
            try:
                xunit = axis_unit[0]
                yunit = z_unit[0] if len(z_unit) == 1 else z_unit[i]
            except:
                xunit, yunit = 'a.u.', 'a.u.'
            axes[i].set_title(title)
            axes[i].set_xlabel(f'{xlabel} ({xunit})')
            axes[i].set_ylabel(f'{ylabel} ({yunit})')
    elif dim == 2 and zsize < 101:
        for i in range(zsize):
            smp = cm.ScalarMappable(norm=None, cmap=None)
            cb = fig.colorbar(smp, ax=axes[i])  # 默认色谱的colorbar
            cb_list.append(cb)
            try:
                title = rddict['name'] + \
                    f': {z_label[i]}' if zsize > 1 else rddict['name']
            except:
                title = rddict['name'] + f' {i}' if zsize > 1 else rddict[
                    'name']
            try:
                xlabel, ylabel = axis_label[1], axis_label[0]
                if trans2D:
                    xlabel, ylabel = ylabel, xlabel
            except:
                xlabel, ylabel = 'X', 'Y'
            try:
                xunit, yunit = axis_unit[1], axis_unit[0]
                if trans2D:
                    xunit, yunit = yunit, xunit
            except:
                xunit, yunit = 'a.u.', 'a.u.'
            axes[i].set_title(title)
            axes[i].set_xlabel(f'{xlabel} ({xunit})')
            axes[i].set_ylabel(f'{ylabel} ({yunit})')
    else:
        message1 = f'dim {dim} is too large (>2)! ' if dim > 2 else f'dim={dim}; '
        message2 = f'zsize {zsize} is too large (>101)!' if zsize > 101 else f'zsize={zsize}'
        log.warning('PASS: ' + message1 + message2)
    #############################################################################################################
    try:
        tags = rddict['ParaSpace'].get('tags', [])
        _tags = [tg.strip(r'\*') for tg in tags if re.match(r'\*', tg)]
        tag = ','.join(_tags)
        if tag:
            axes[0].text(-0.1,
                         1.1,
                         'TAG: ' + tag,
                         horizontalalignment='left',
                         verticalalignment='bottom',
                         transform=axes[0].transAxes)  # fig.transFigure)#
    except:
        pass
    #############################################################################################################################
    fig.tight_layout()
    return fig, axes, cb_list


def update_plot(rddict,
                fig=None,
                axes=[],
                cb_list=[],
                remove=True,
                trans2D=True):
    '''非独立，数据画图'''
    dim = rddict['info']['dim']
    zshape = rddict['info']['zshape']
    datashape = rddict['info']['datashape']
    zsize = reduce(lambda a, b: a * b, zshape, 1)
    datashape_r = (*datashape[:dim], zsize)

    if dim == 1 and zsize < 101:
        x, z = rddict['data']
        z = z.reshape(datashape_r)
        z = np.abs(z) if np.any(np.iscomplex(z)) else z.real
        for i in range(zsize):
            _ = [a.remove() for a in axes[i].get_lines()] if remove else []
            axes[i].plot(x, z[:, i], 'C0')
            axes[i].plot(x, z[:, i], 'C0.')
    elif dim == 2 and zsize < 101:
        x, y, z = rddict['data']
        x_step, y_step = x[1] - x[0], y[1] - y[0]
        if trans2D:  # 交换x,y
            x, y = y, x
            x_step, y_step = y_step, x_step
        z = z.reshape(datashape_r)
        z = np.abs(z) if np.any(np.iscomplex(z)) else z.real
        for i in range(zsize):
            _z = z[:, :, i]
            _ = [a.remove() for a in axes[i].get_images()] if remove else []
            if trans2D:  # 转置z
                _z = _z.T
            im = axes[i].imshow(_z,
                                extent=(y[0] - y_step / 2, y[-1] + y_step / 2,
                                        x[0] - x_step / 2, x[-1] + x_step / 2),
                                origin='lower',
                                aspect='auto')
            cb_list[i].update_normal(im)  # 更新对应的colorbar
    else:
        pass
    return fig


def update(n, rd=None, fig=None, axes=[], cb_list=[]):
    if isinstance(rd, dict):
        pass
    else:
        rd = rd.plot_dict()
    try:
        _ = update_plot(rd, fig=fig, axes=axes, cb_list=cb_list, remove=True)
    except:
        fig.tight_layout()


def animate(name='S21', dim=1, zshape=1, **kw):
    from QOS.Collector import redisRecord
    rd = redisRecord(name, dim, zshape)
    fig = plt.figure(name)
    fig, axes, cb_list = init_plot(rd.plot_dict(), fig=fig)

    _kw = dict(
        frames=10000,
        interval=500,
        repeat=False,
        cache_frame_data=False,
    )
    _kw.update(kw)

    fa = FuncAnimation(fig, update, fargs=[rd, fig, axes, cb_list], **_kw)
    return fa
