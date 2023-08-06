"""Plotting module. Development plots only.
"""

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import uuid
import datetime as dt
import pendulum

from sunpeek.common.utils import ROOT_DIR

try:
    from plotly import graph_objects as go
    from plotly.subplots import make_subplots

    PLOTS_AVAILABLE = True
except ModuleNotFoundError:
    warnings.warn('module plotly not found, install it to use development plots')
    PLOTS_AVAILABLE = False


def plot_all(pc_output, mode='screen', use_safety=True, write_image=False, anonymize=False):
    assert mode in ['screen', 'presentation']
    if not PLOTS_AVAILABLE:
        raise ModuleNotFoundError('module plotly not found, install it to use development plots')
    if pc_output.n_intervals == 0:
        print('Nothing to plot, no PC intervals found.')
        return

    figures = dict(
        square=plot_square(pc_output, mode=mode, use_safety=use_safety, write_image=write_image, anonymize=anonymize),
        time=plot_time(pc_output, mode=mode, use_safety=use_safety, write_image=write_image, anonymize=anonymize),
        sums=plot_sums(pc_output, mode=mode, write_image=write_image, anonymize=anonymize),
    )

    return figures


def plot_square(pc_output, mode, use_safety=False, write_image=False, anonymize=False):
    """Plot measured vs. estimated power in intervals + trendline.
    """
    if not PLOTS_AVAILABLE:
        raise ModuleNotFoundError('module plotly not found, install it to use development plots')
    if pc_output.n_intervals == 0:
        print('Nothing to plot, no PC intervals found.')
        return

    measured = pc_output.tp_sp_measured.magnitude
    estimated = pc_output.tp_sp_estimated_safety.magnitude if use_safety else pc_output.tp_sp_estimated.magnitude
    slope = pc_output.target_actual_slope_safety.magnitude if use_safety else pc_output.target_actual_slope.magnitude
    font_size = 24 if mode == 'presentation' else 14

    fig = go.Figure()
    fig.add_scatter(x=estimated, y=measured,
                    name=f"Interval averages ("
                         f"{pendulum.duration(seconds=pc_output.interval_length.total_seconds()).in_words(locale='en')}"
                         f")",
                    mode='markers', marker_size=10, marker_opacity=0.8)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.01,
        xanchor="right",
        x=1
    ))

    # Linear trendline with 0 intercept
    # rng = [estimated.min(), estimated.max()]
    # fig.add_scatter(x=rng, y=slope * np.array(rng),
    #                 name=f'y = {slope:.3f} x',
    #                 mode='lines', line_color='grey', line_width=3)

    # Bisection line
    # axis_range = [np.min([estimated.min(), measured.min()]).round(-2) - 100,
    #               np.max([estimated.max(), measured.max()]).round(-2)]
    # axis_range = [350, 700]
    # axis_range = [300, 600]
    axis_range = [250, 650]
    tick0 = 300

    fig.add_scatter(x=axis_range, y=axis_range, name='', showlegend=False,
                    mode='lines',
                    # line_dash='dash',
                    line_color='grey', line_width=0.5)
    fig.update_layout(
        # title=dict(text=_get_title(pc_output, anonymize),
        #            xanchor='left', yanchor='top',
        #            font_size=font_size + 1,
        #            ),
        # margin=dict(l=250, r=20, t=70, b=150),
        width=1000,
        height=1000,
        autosize=False,
        xaxis=dict(
            type='linear',
            constrain="domain",
            title="<b>Estimated</b> power [W/m²]",
            linecolor="#BCCCDC",
            range=axis_range,
            title_font_size=font_size,
            tickfont_size=font_size,
            tick0=tick0,
            dtick=100,
            # tickvals=tickvals,
            # ticktext=ticktext,
        ),
        yaxis=dict(
            type='linear',
            constrain="domain",
            title="<b>Measured</b> power [W/m²]",
            title_font_size=font_size,
            title_standoff=30,
            linecolor="#BCCCDC",
            range=axis_range,
            scaleanchor="x",
            scaleratio=1,
            autorange=False,
            tickfont_size=font_size,
            tick0=tick0,
            dtick=100,
            # tickvals=tickvals,
            # ticktext=ticktext,
        ),
        legend_font_size=font_size,
    )

    # fig.update_xaxes(
    #     showspikes=True,
    #     spikecolor="grey",
    #     spikesnap="cursor",
    #     spikemode="across",
    #     spikedash="solid",
    # )
    # fig.update_yaxes(
    #     showspikes=True,
    #     spikecolor="grey",
    #     spikesnap="cursor",
    #     spikemode="across",
    #     spikedash="solid",
    # )

    _show(fig)
    if write_image:
        fig.write_image(_get_filename('square', pc_output))

    return fig


def plot_time(pc_output, mode, use_safety=False, write_image=False, anonymize=False, plot_trend=True):
    """Plots ratio of measured vs. estimated power over time."""
    if not PLOTS_AVAILABLE:
        raise ModuleNotFoundError('module plotly not found, install it to use development plots')
    if pc_output.n_intervals == 0:
        print('Nothing to plot, no PC intervals found.')
        return

    estimated = pc_output.tp_sp_estimated_safety.magnitude if use_safety else pc_output.tp_sp_estimated.magnitude
    measured = pc_output.tp_sp_measured.magnitude
    ratio = measured / estimated
    # Plotting ratio against midpoint of intervals
    time_display = pc_output.datetime_intervals_start + 0.5 * pc_output.interval_length
    font_size = 24 if mode == 'presentation' else 14

    fig = go.Figure()
    fig.add_scatter(x=time_display, y=ratio,
                    mode='markers', marker_size=10, marker_opacity=0.5,
                    showlegend=False)

    if plot_trend:
        rm = pd.Series(data=ratio, index=time_display) \
            .rolling(dt.timedelta(days=45), min_periods=25, center=True, closed='both').median()
        fig.add_scatter(y=rm, x=rm.index, mode='lines', line_color='grey', line_width=5, showlegend=False)

    # print_data = lambda i: data.index[i].strftime('%Y-%m-%d')
    fig.update_layout(
        # title=dict(text=_get_title(pc_output, anonymize),
        #            xanchor='left', yanchor='top',
        #            font_size=font_size + 1,
        #            ),
        # margin=dict(l=250, r=20, t=70, b=150),
        width=2000,
        height=600,
        xaxis=dict(title="",
                   title_font_size=font_size,
                   tickfont_size=font_size,
                   linecolor="#BCCCDC"),
        yaxis=dict(title="<b>Ratio measured vs. estimated</b> power [-]",
                   # title_standoff=10,
                   title_standoff=30,
                   title_font_size=font_size,
                   tickfont_size=font_size,
                   # tickformat='.1f',
                   tickformat='0%',
                   # range=[0.5, 1.2],
                   range=[0.8, 1.2],
                   # range=[ratio.min(), np.max([1, ratio.max()])],
                   dtick=0.1,
                   linecolor="#BCCCDC")

    )
    _show(fig)
    if write_image:
        fig.write_image(_get_filename('time', pc_output))

    return fig


def plot_sums(pc_output, mode, write_image=False, anonymize=False):
    """Plot sums / average powers in intervals, measured vs. estimated.
    """
    if not PLOTS_AVAILABLE:
        raise ModuleNotFoundError('module plotly not found, install it to use development plots')
    if pc_output.n_intervals == 0:
        print('Nothing to plot, no PC intervals found.')
        return

    # estimated = np.mean(pc_output.tp_sp_estimated.magnitude)
    esimated_safe = np.mean(pc_output.tp_sp_estimated_safety.magnitude)
    measured = np.mean(pc_output.tp_sp_measured.magnitude)

    fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]],
                        shared_xaxes=False,
                        shared_yaxes=False, vertical_spacing=0.001)

    font_size = 18 if mode == 'presentation' else 14
    labels = ['Average power<br><b>measured</b>', 'Average power<br><b>estimated</b>']
    x = [measured, esimated_safe]
    colors = ['rgba(192, 0, 0, 0.6)', 'rgba(68, 114, 196, 0.6)']

    text = [str(np.round(val, decimals=1)) + ' W/m²' for val in x]
    fig.append_trace(go.Bar(
        x=x,
        y=labels,
        marker=dict(
            color=colors,
            line=dict(color='rgba(90, 90, 90, 1.0)', width=1),
        ),
        orientation='h',
        width=0.4,
        text=text,
        textposition="outside",
        insidetextanchor="end",
        outsidetextfont_size=font_size
    ), 1, 1)

    plant_name = '<anonymized>' if anonymize else pc_output.plant.name
    if plant_name.startswith('FHW Arcon South'):
        plant_name = 'FHW Fernheizwerk Graz, Arcon South'
    title = (f"<b>Check of Performance</b> ({pc_output.pc_method_name}. "
             f"Equation: {pc_output.equation}).<br>"
             # f"Plant name: <b>{plant_name}</b>.<br>"
             f"<b>Data from</b> {pc_output.datetime_eval_start} to "
             f"{pc_output.datetime_eval_end}.<br>"
             f"n={pc_output.n_intervals} intervals, "
             f"interval duration "
             f"{pendulum.duration(seconds=pc_output.interval_length.total_seconds()).in_words(locale='en')}."
             )
    axis_range = [0, np.max(x).round(-1) + 100]
    fig.update_layout(
        title=dict(text=title,
                   xanchor='left',
                   xref='paper',
                   x=fig.layout.xaxis.domain[0],
                   # yanchor='top',
                   yanchor='bottom',
                   y=fig.layout.height,
                   font_size=font_size + 1,
                   ),
        autosize=False,
        height=700,
        width=2400,
        # legend=dict(x=0.029, y=1.038, font_size=10),
        margin=dict(l=250, r=20, t=70, b=150),
        # paper_bgcolor='rgb(248, 248, 255)',
        # plot_bgcolor='rgb(248, 248, 255)',
        yaxis=dict(
            tickfont=dict(size=font_size),
            title_standoff=30,
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 0.85],
        ),
        # yaxis2=dict(
        #     range=axis_range,
        #     showgrid=False,
        #     showline=True,
        #     showticklabels=False,
        #     linecolor='rgba(102, 102, 102, 0.8)',
        #     linewidth=2,
        #     domain=[0, 0.85],
        # ),
        xaxis=dict(
            title=dict(text='Specific thermal power [W/m²]',
                       font_size=font_size,
                       ),
            # title='Specific thermal power [W/m²]',
            title_font_size=font_size - 1,
            tickfont=dict(size=font_size),
            range=axis_range,
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0, 0.42],
        ),
        # xaxis2=dict(
        #     zeroline=False,
        #     showline=False,
        #     showticklabels=True,
        #     showgrid=True,
        #     domain=[0.47, 1],
        #     side='top',
        #     dtick=25000,
        # ),
    )

    # Adding labels
    # x_power = np.round([measured, estimated], decimals=1)
    # for xp, yp in zip(x_power, labels):
    #     # labeling the bar net worth
    #     annotations.append(dict(xref='x1', yref='y1',
    #                             y=yp, x=xp + 10,
    #                             text=str(xp) + ' W/m²',
    #                             align="left",
    #                             font=dict(family='Arial', size=font_size,
    #                                       color='rgb(0, 0, 0)'),
    #                             showarrow=False))

    # Guarantee fulfilled statement
    ratio = measured / esimated_safe
    fulfill_txt = 'not ' if ratio < 1 else ''
    ratio_text = (f'<b>Performance Check {fulfill_txt}fulfilled:'
                  f'</b> Ratio measured / estimated power = {ratio:.1%}'
                  f'<br>Combined safety factor f<sub>safe</sub> = {pc_output.safety_combined:.2} taken into account.')
    # fig.add_annotation(dict(
    #     text=ratio_text,
    #     font_size=font_size,
    #     yref='paper',
    #     yanchor="bottom",
    #     y=-1.02,
    #     xref='paper',
    #     xanchor="left",
    #     x=0,
    #     # align='left',
    #     showarrow=False))

    # Calculate position of annotation
    fig.add_annotation(
        text=ratio_text,
        font_size=font_size,
        xref='paper',
        x=fig.layout.xaxis.domain[0],
        align='left',
        # xanchor='left',
        y=-230 / fig.layout.height,
        yref='paper',
        showarrow=False
    )

    fig.update_layout(showlegend=False)
    # fig.update_layout(legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=1.01,
    #     xanchor="right",
    #     x=1
    # ))

    _show(fig)
    if write_image:
        fig.write_image(_get_filename('sums', pc_output))

    return fig


def plot_mask(pc_output, mask):
    """Produces a subplot figure with the PC criteria mask.
    mask is usually pc_obj._mask
    """
    if not PLOTS_AVAILABLE:
        raise ModuleNotFoundError('module plotly not found, install it to use development plots')
    if pc_output.n_intervals == 0:
        print('Nothing to plot, no PC intervals found.')
        return

    subplot_cols = mask.columns
    fig = make_subplots(rows=1 + len(subplot_cols), shared_xaxes=True, subplot_titles=subplot_cols)

    t = mask.index
    for i, col in enumerate(subplot_cols):
        fig.add_scatter(x=t, y=mask[col], row=i + 1, col=1,
                        mode='lines+markers', line={'width': 1}, marker={'size': 3})
        fig.add_scatter(x=t, y=mask[col], row=i + 1, col=1,
                        mode='lines', line={'width': 0.5})

    fig.layout.update(showlegend=False)
    _show(fig)

    return fig


def _show(fig):
    fig.update_layout(dragmode='pan')
    config = {'scrollZoom': True,
              'displayModeBar': True,
              'modeBarButtonsToRemove': ['zoomIn', 'zoomOut'],
              'modeBarButtonsToAdd': ['drawline',
                                      'drawrect',
                                      'eraseshape'
                                      ]}
    fig.show(config=config)


def _get_filename(plot_name, pc_output):
    """Generate png file name from method, equation and plot name.
    """
    save_folder = Path(ROOT_DIR).parent / 'tests' / 'resources'
    m = pc_output.evaluation_mode
    e = pc_output.equation
    filename = f'{m}_eq{e}__{plot_name}__{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    return save_folder / filename
