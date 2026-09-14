

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium", app_title="Economics Calculator")


@app.cell
def _(mo):
    mo.md(
        r"""
        # Energy Project Economics Calculator

        ### This calculator determines various measures of cost-effectiveness for an energy project.

        ---
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy_financial as nf
    import numpy as np
    from matplotlib import pyplot as plt
    import matplotlib.ticker as mtick
    return mo, mtick, nf, np, plt


@app.cell
def _(mo):
    def make_label(label, info):
        """Returns a Markdown fragment that serves as a label with a pop-up information box
        to give additional explanation of the label.
        """
        tool_tip = info.replace("\n", " ")
        return f'<span data-tooltip="{tool_tip}">{mo.icon("octicon:question-16")}</span> {label}'
    return (make_label,)


@app.cell
def _(mo):
    # Input Widgets
    init_cost = mo.ui.number(start=0, stop=None, step=1, value=1000)
    life = mo.ui.slider(start=3, stop=50, value=20, debounce=True, full_width=True)
    savings_yr_1 = mo.ui.number(step=1, value=100)
    savings_esc = mo.ui.slider(start=-1.0, stop=3.0, step=0.1, value=0.5, debounce=True)
    general_inflation = mo.ui.slider(start=1.0, stop=4.0, step=0.1, value=2.5, debounce=True)
    discount_rate = mo.ui.slider(start=1.0, stop=8.0, step=0.25, value=3.0, debounce=True)
    return (
        discount_rate,
        general_inflation,
        init_cost,
        life,
        savings_esc,
        savings_yr_1,
    )


@app.cell
def _(
    discount_rate,
    general_inflation,
    init_cost,
    life,
    make_label,
    mo,
    savings_esc,
    savings_yr_1,
):
    # Create Markdown for the Calculator inputs
    if savings_esc.value > 0:
        savings_esc_text = f"{savings_esc.value}% / year more than inflation"
    elif savings_esc.value == 0:
        savings_esc_text = "at general inflation rate"
    else:
        savings_esc_text = f"{-savings_esc.value}% / year less than inflation"

    esc_info = """The savings or revenue from an energy project generally increase year-over-year. Select
    that rate of increase relative to the general rate of inflation. Experts typically forecast fuel
    prices increasing somewhat faster than general inflation.
    """
    esc_label = make_label('Savings Escalation Rate', esc_info)

    life_control = mo.hstack([mo.md('Project&nbsp;Life:'),life , mo.md(f'{life.value}&nbsp;years')], widths=[0, 1, 0])

    inputs_1 = mo.md(f"""Description of the Analysis:  
    {mo.ui.text_area(rows=2)}

    Intial Project Cost: $ {init_cost}

    {life_control}

    First Year Savings or Net Revenue: $ {savings_yr_1}

    {esc_label}: {savings_esc} {savings_esc_text}
    """)

    inputs_2 = mo.accordion(
        {
            'Advanced Inputs': mo.md(f"""
    The inflation rate below should reflect the expected average general inflation
    that will occur over the lifetime of this project.  
    General Inflation Rate: {general_inflation} {general_inflation.value}% / year

    The Discount Rate indicates how much future cash flows are reduced due to the time value
    of money. The Discount Rate should be set to the rate-of-return that can be achieved by an
    alternative investment of equivalent risk. The US Department of Energy typically uses a
    discount rate of 3%/year more than inflation, which is the default below.  
    Discount Rate: {discount_rate} {discount_rate.value}% / year more than general inflation
    """)
        }
    )
    return inputs_1, inputs_2


@app.cell
def _(
    discount_rate,
    general_inflation,
    init_cost,
    life,
    make_label,
    mo,
    nf,
    np,
    savings_esc,
    savings_yr_1,
):
    # Results calculations and display

    # create the cash flow array, including the intial cost, but zeroes for the rest of the array
    cash_arr = np.array([-init_cost.value] + [0.0] * life.value)

    # create the escalating savings array and add it into the main cash flow array
    sav_mult = (1.0 + general_inflation.value / 100.0) * (1.0 + savings_esc.value / 100.0)
    savings = np.cumprod(np.array([1.0]+[sav_mult] * (life.value - 1))) * savings_yr_1.value
    savings = np.insert(savings, 0, 0.0)   # add a zero for the year 0 value of the savings array
    cash_arr += savings

    irr = nf.irr(cash_arr)
    disc_rate_nom = (1 + discount_rate.value/100) * (1 + general_inflation.value/100) - 1.0
    npv = nf.npv(disc_rate_nom, cash_arr)
    bc = (npv + init_cost.value) / init_cost.value

    ror_info = """The project is cost-effective
    if this Rate of Return exceeds that available from an alternative investment of comparable risk. Also remember
    that most residential energy projects provide tax-free income. (This is a 'nominal' rate of return; it has not
    been reduced for general inflation.)"""
    ror_label = make_label("Rate of Return", ror_info)

    simple_pb_info = """This simple measure is the initial cost of the project divided by the first-year savings.
    It represents the number of years it would take to return the investment if the first-year savings
    continued without change.
    """
    simple_pb_label = make_label('Simple Payback', simple_pb_info)

    npv_info = """If the Net Present Value is greater than 0, the project is cost-effective.
    It is the benefits of the project minus the costs, but discounts future benefits to account
    for the time-value of money.
    """
    npv_label = make_label('Net Present Value', npv_info)

    bc_info = """The project is cost-effective if the Benefit/Cost Ratio is greater than 1.0.
    It is calculated as the sum of the benefits of the project divided by the sum of the costs,
    accounting for the time value of money.
    """
    bc_label = make_label('Benefit/Cost Ratio', bc_info)

    cum_cash_info = """This graph cumulatively adds up the cash flow of the project over its life. 
    The graph starts negative because of the cash outflow due to the inital cost of the project but then grows
    as the savings from project accumulate. No time-value of money is considered. Savings escalation
    is included.
    """
    cum_cash_label = make_label('Cumulative Cash Flow Graph', cum_cash_info)

    res_text = mo.md(f"""### {ror_label}: {irr * 100:.1f}% / year  
    ### {simple_pb_label}: {init_cost.value / savings_yr_1.value: .1f} years  
    ### {npv_label}: $ {npv: ,.0f}
    ### {bc_label}: {bc: .3g}
    ### {cum_cash_label}:
    """)
    return cash_arr, res_text


@app.cell
def _(cash_arr, life, mtick, np, plt):
    # Creation of Cumulative Cash Flow Graph

    fig, ax = plt.subplots()
    yr = range(0, life.value + 1)
    cum_cash = np.cumsum(cash_arr)
    ax.plot(yr, cum_cash)
    plt.grid()
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Cumulative Cash Flow', fontsize=14)

    ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))

    ax.xaxis.set_major_locator(mtick.MaxNLocator(integer=True))

    # Shade where cumulative cash >= 0 (above the axis)
    ax.fill_between(
        yr, cum_cash, 0,
        where=(cum_cash >= 0),
        facecolor='lightgreen',
        interpolate=True,
        alpha=0.6
    )

    # Shade where cumulative cash <= 0 (below the axis)
    ax.fill_between(
        yr, cum_cash, 0,
        where=(cum_cash <= 0),
        facecolor='lightcoral',
        interpolate=True,
        alpha=0.6
    )

    # draw the x-axis line on top
    ax.axhline(0, color='black', linewidth=0.8)
    None
    return (ax,)


@app.cell
def _(ax, inputs_1, inputs_2, mo, res_text):
    # Layout the Calculator
    inputs = mo.vstack([inputs_1, inputs_2])
    results = mo.vstack([res_text, ax])
    all = mo.hstack([inputs, results], gap=3.0, widths='equal')
    all
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ---
        If you have questions or comments, please send mail to alan@analysisnorth.com.

        This app was developed using the amazing [Marimo](https://marimo.io/) Python notebook tool. The notebook
        source code is [available here](https://github.com/alanmitchell/apps/blob/main/notebooks/econ.py).
        """
    )
    return


if __name__ == "__main__":
    app.run()
