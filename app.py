import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Set page configuration
st.set_page_config(layout="wide", page_title="Germany Power System Data Analysis", page_icon=":chart_with_upwards_trend:")

st.title('Open Power System Data Analysis for Germany')
st.markdown("""
This project explores daily time series of `Open Power System Data (OPSD) for Germany`, focusing on electricity consumption, wind, and solar power production from 2006-2017.
""")

# --- Data Loading and Preparation ---
@st.cache_data
def load_data():
    opsd_daily = pd.read_csv('opsd_germany_daily.csv', index_col=0, parse_dates=True)
    opsd_daily['Year'] = opsd_daily.index.year
    opsd_daily['Month'] = opsd_daily.index.month
    opsd_daily['Weekday Name'] = opsd_daily.index.day_name()
    return opsd_daily

opsd_daily = load_data()

st.header('1. Data Overview')
st.write("Here's a glimpse of the prepared data:")
min_date = opsd_daily.index.min().date()
max_date = opsd_daily.index.max().date()

overview_dates = st.date_input("Select Date Range for Table", [min_date, max_date], min_value=min_date, max_value=max_date, key='overview_date')
if len(overview_dates) == 2:
    mask = (opsd_daily.index.date >= overview_dates[0]) & (opsd_daily.index.date <= overview_dates[1])
    st.dataframe(opsd_daily.loc[mask].head())
else:
    st.dataframe(opsd_daily.head())

# --- Visualizing Time Series Data ---
st.header('2. Visualizing Time Series Data')
st.subheader('Daily Time Series Over Time')

col1, col2 = st.columns(2)
with col1:
    ts_col = st.selectbox("Select Column to Plot", ['Consumption', 'Solar', 'Wind', 'Wind+Solar'], key='ts_col_line')
with col2:
    ts_dates = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date, key='ts_date_line')

if len(ts_dates) == 2:
    ts_data = opsd_daily.loc[str(ts_dates[0]):str(ts_dates[1])]
else:
    ts_data = opsd_daily

fig, ax = plt.subplots(figsize=(12, 6))
ts_data[ts_col].plot(linewidth=0.5, ax=ax)
ax.set_ylabel('Daily Totals (GWh)')
ax.set_title(f'Daily {ts_col} (2006-2017)')
st.pyplot(fig)

st.markdown("With so many data points, the line plot is crowded. Let's look at Solar and Wind production too, as scatter plots.")

sc_cols, sc_dates = st.columns(2)
with sc_cols:
    cols_plot = st.multiselect("Select Columns for Scatter Plots", ['Consumption', 'Solar', 'Wind', 'Wind+Solar'], default=['Consumption', 'Solar', 'Wind'], key='scat_cols')
with sc_dates:
    scatter_dates = st.date_input("Select Date Range for Scatter", [min_date, max_date], min_value=min_date, max_value=max_date, key='scat_date')

if len(scatter_dates) == 2:
    scat_data = opsd_daily.loc[str(scatter_dates[0]):str(scatter_dates[1])]
else:
    scat_data = opsd_daily

if not cols_plot:
    st.warning("Please select at least one column for scatter plots.")
else:
    fig, axes = plt.subplots(len(cols_plot), 1, figsize=(12, 3 * len(cols_plot)), sharex=True)
    if len(cols_plot) == 1:
        axes = [axes]
    for i, col in enumerate(cols_plot):
        axes[i].plot(scat_data[col], marker='.', alpha=0.5, linestyle='None')
        axes[i].set_ylabel('Daily Totals (GWh)')
        axes[i].set_title(col)
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("**Observations:**\n1. Electricity consumption is highest in winter, lowest in summer.\n2. Solar power production is highest in summer, lowest in winter.\n3. Wind power production is highest in winter, lowest in summer.\n4. There's a strong increasing trend in wind power production.\n5. All three time series exhibit clear seasonality.")

st.subheader('Weekly Seasonality (Detailed View)')
import datetime
ws_cols, ws_dates = st.columns(2)
with ws_cols:
    ws_col = st.selectbox("Select Column", ['Consumption', 'Solar', 'Wind', 'Wind+Solar'], key='ws_col')
with ws_dates:
    ws_date_range = st.date_input("Select Short Date Range", [datetime.date(2017, 1, 1), datetime.date(2017, 2, 28)], min_value=min_date, max_value=max_date, key='ws_date')

if len(ws_date_range) == 2:
    ws_data = opsd_daily.loc[str(ws_date_range[0]):str(ws_date_range[1])]
else:
    ws_data = opsd_daily

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(ws_data[ws_col], marker='o', linestyle='-')
ax.set_ylabel(f'Daily {ws_col} (GWh)')
ax.set_title(f'{ws_col} with Weekly Gridlines')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
fig.autofmt_xdate()
st.pyplot(fig)
st.markdown("As suspected, consumption is highest on weekdays and lowest on weekends. We also see drastic decreases during holidays.")

# --- Explore Seasonality with Box Plots ---
st.header('3. Exploring Seasonality with Box Plots')

st.subheader('Yearly Seasonality by Month')
ym_cols, ym_dates = st.columns(2)
with ym_cols:
    bp_cols = st.multiselect("Select Columns for Monthly Boxplots", ['Consumption', 'Solar', 'Wind', 'Wind+Solar'], default=['Consumption', 'Solar', 'Wind'], key='bp_cols')
with ym_dates:
    bp_date_range = st.date_input("Select Date Range (Yearly Trends)", [min_date, max_date], min_value=min_date, max_value=max_date, key='bp_date')

if len(bp_date_range) == 2:
    bp_data = opsd_daily.loc[str(bp_date_range[0]):str(bp_date_range[1])]
else:
    bp_data = opsd_daily

if not bp_cols:
    st.warning("Please select at least one column for box plots.")
else:
    fig, axes = plt.subplots(len(bp_cols), 1, figsize=(12, 3.5 * len(bp_cols)), sharex=True)
    if len(bp_cols) == 1:
        axes = [axes]
    for i, name in enumerate(bp_cols):
        sns.boxplot(data=bp_data, x='Month', y=name, ax=axes[i])
        axes[i].set_ylabel('GWh')
        axes[i].set_title(name)
        if axes[i] != axes[-1]:
            axes[i].set_xlabel('')
    plt.tight_layout()
    st.pyplot(fig)
st.markdown("Electricity consumption is generally higher in winter, though lower in Dec/Jan due to holidays. Wind has more outliers due to extreme weather.")

st.subheader('Weekly Seasonality by Weekday')
wd_cols, wd_dates = st.columns(2)
with wd_cols:
    wd_col = st.selectbox("Select Column for Weekly Boxplot", ['Consumption', 'Solar', 'Wind', 'Wind+Solar'], key='wd_col')
with wd_dates:
    wd_date_range = st.date_input("Select Date Range (Weekly Trends)", [min_date, max_date], min_value=min_date, max_value=max_date, key='wd_date')

if len(wd_date_range) == 2:
    wd_data = opsd_daily.loc[str(wd_date_range[0]):str(wd_date_range[1])]
else:
    wd_data = opsd_daily

fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=wd_data, x='Weekday Name', y=wd_col, ax=ax)
ax.set_title(f'{wd_col} by Day of Week')
ax.set_ylabel(f'{wd_col} (GWh)')
ax.set_xlabel('Day of Week')
st.pyplot(fig)
st.markdown("As expected, consumption is significantly higher on weekdays than on weekends.")

# --- Resampling ---
st.header('4. Resampling Data')
st.subheader('Mean Resampling Comparison')

data_columns = ['Consumption', 'Wind', 'Solar', 'Wind+Solar']

res_col_sel, res_freq_sel, res_date_sel = st.columns(3)
with res_col_sel:
    res_col = st.selectbox("Select Column", data_columns, index=2, key='res_col')
with res_freq_sel:
    freq_dict = {'W': 'Weekly', 'ME': 'Monthly', 'QE': 'Quarterly'}
    res_freq = st.selectbox("Select Resampling Frequency", list(freq_dict.keys()), format_func=lambda x: freq_dict[x], key='res_freq')
with res_date_sel:
    res_date_range = st.date_input("Select Date Range", [datetime.date(2017, 1, 1), datetime.date(2017, 6, 30)], min_value=min_date, max_value=max_date, key='res_date')

opsd_resampled = opsd_daily[data_columns].resample(res_freq).mean()

if len(res_date_range) == 2:
    start_str, end_str = str(res_date_range[0]), str(res_date_range[1])
    res_data_daily = opsd_daily.loc[start_str:end_str]
    res_data_freq = opsd_resampled.loc[start_str:end_str]
else:
    res_data_daily = opsd_daily
    res_data_freq = opsd_resampled

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(res_data_daily[res_col], marker='.', linestyle='-', linewidth=0.5, label='Daily')
ax.plot(res_data_freq[res_col], marker='o', markersize=8, linestyle='-', label=f'{freq_dict[res_freq]} Mean Resample')
ax.set_ylabel(f'{res_col} (GWh)')
ax.legend()
ax.set_title(f'Daily vs. {freq_dict[res_freq]} Mean {res_col} Production')
st.pyplot(fig)
st.markdown("Weekly mean resampling smooths out daily fluctuations, making trends clearer.")

st.subheader('Monthly Sums of Electricity Data')
ms_cols, ms_dates = st.columns(2)
with ms_cols:
    ms_plot_cols = st.multiselect("Select Area Plot Columns (Production)", ['Wind', 'Solar', 'Wind+Solar'], default=['Wind', 'Solar'], key='ms_plot_cols')
    ms_line_cols = st.multiselect("Select Line Plot Columns (Consumption)", ['Consumption'], default=['Consumption'], key='ms_line_cols')
with ms_dates:
    ms_date_range = st.date_input("Select Date Range (Monthly Sums)", [min_date, max_date], min_value=min_date, max_value=max_date, key='ms_date')

opsd_monthly = opsd_daily[data_columns].resample('ME').sum(min_count=28)

if len(ms_date_range) == 2:
    start_ms, end_ms = str(ms_date_range[0]), str(ms_date_range[1])
    ms_data = opsd_monthly.loc[start_ms:end_ms]
else:
    ms_data = opsd_monthly

st.dataframe(ms_data.head())

fig, ax = plt.subplots(figsize=(12, 6))
for col in ms_line_cols:
    ax.plot(ms_data[col], color='black', label=col)
if ms_plot_cols:
    ms_data[ms_plot_cols].plot.area(ax=ax, linewidth=0)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.legend()
ax.set_ylabel('Monthly Total (GWh)')
ax.set_title('Monthly Electricity Quantities')
st.pyplot(fig)
st.markdown("Monthly view shows clear yearly seasonality and the steady growth of wind power production.")

# --- Annual Share of Wind+Solar ---
st.header('5. Wind + Solar Share of Annual Electricity Consumption')
opsd_annual = opsd_daily[data_columns].resample('YE').sum(min_count=360)
opsd_annual = opsd_annual.set_index(opsd_annual.index.year)
opsd_annual.index.name = 'Year'
opsd_annual['Wind+Solar/Consumption'] = opsd_annual['Wind+Solar'] / opsd_annual['Consumption']

min_year = int(opsd_annual.index.min())
max_year = int(opsd_annual.index.max())

year_slider = st.slider("Select Year Range for Annual Share", min_value=min_year, max_value=max_year, value=(2012, max_year), key='annual_share')

st.write(f"Annual data ({year_slider[0]} to {year_slider[1]}):")
opsd_annual_filtered = opsd_annual.loc[year_slider[0]:year_slider[1]]
st.dataframe(opsd_annual_filtered)

fig, ax = plt.subplots(figsize=(10, 5))
opsd_annual_filtered['Wind+Solar/Consumption'].plot.bar(color='C0', ax=ax)
ax.set_ylabel('Fraction')
ax.set_ylim(0, max(opsd_annual_filtered['Wind+Solar/Consumption'].max() * 1.2, 0.3) if not opsd_annual_filtered.empty else 0.3)
ax.set_title(f'Wind + Solar Share of Annual Electricity Consumption ({year_slider[0]}-{year_slider[1]})')
plt.xticks(rotation=0)
st.pyplot(fig)
st.markdown("Wind + solar production as a share of annual electricity consumption increased from about 15% in 2012 to about 27% in 2017.")

# --- Rolling Windows ---
st.header('6. Rolling Windows for Trends')

st.subheader('Dynamic Rolling Mean of Data')
roll_wnd, roll_col, roll_dates = st.columns(3)
with roll_wnd:
    window_sizes = st.slider("Select Short Rolling Window (Days)", min_value=2, max_value=30, value=7, key='roll_win')
with roll_col:
    roll_col_sel = st.selectbox("Select Column for Comparison", ['Consumption', 'Solar', 'Wind', 'Wind+Solar'], index=2, key='roll_col_sel')
with roll_dates:
    roll_date_range = st.date_input("Select Short Date Range", [datetime.date(2017, 1, 1), datetime.date(2017, 6, 30)], min_value=min_date, max_value=max_date, key='roll_date')

opsd_xd = opsd_daily[data_columns].rolling(window=window_sizes, center=True).mean()
st.dataframe(opsd_xd.head())

if len(roll_date_range) == 2:
    start_str = str(roll_date_range[0])
    end_str = str(roll_date_range[1])
    roll_daily_data = opsd_daily.loc[start_str:end_str]
    roll_xd_data = opsd_xd.loc[start_str:end_str]
    # For weekly mean we recompute dynamically for the selected column over the same range
    opsd_weekly_mean = opsd_daily[data_columns].resample('W').mean()
    roll_wk_data = opsd_weekly_mean.loc[start_str:end_str]
else:
    roll_daily_data = opsd_daily
    roll_xd_data = opsd_xd
    opsd_weekly_mean = opsd_daily[data_columns].resample('W').mean()
    roll_wk_data = opsd_weekly_mean

st.subheader(f'Comparing Daily, Weekly Resampled, and {window_sizes}-day Rolling Mean {roll_col_sel} Data')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(roll_daily_data[roll_col_sel], marker='.', linestyle='-', linewidth=0.5, label='Daily')
ax.plot(roll_wk_data[roll_col_sel], marker='o', markersize=8, linestyle='-', label='Weekly Mean Resample')
ax.plot(roll_xd_data[roll_col_sel], marker='.', linestyle='-', label=f'{window_sizes}-d Rolling Mean')
ax.set_ylabel(f'{roll_col_sel} Production (GWh)')
ax.legend()
ax.set_title(f'{roll_col_sel}: Daily vs. Resampled vs. Rolling Mean')
st.pyplot(fig)
st.markdown("Rolling mean preserves the original frequency but smooths the data, while resampling changes the frequency.")

st.subheader('Long-term Trends (Large Rolling Mean)')
lt_wnd, lt_cols = st.columns(2)
with lt_wnd:
    long_window = st.slider("Select Long Window Size (Days)", min_value=30, max_value=730, value=365, step=30, key='long_win')
with lt_cols:
    trend_cols = st.multiselect("Select Trends to view", ['Consumption', 'Wind', 'Solar', 'Wind+Solar'], default=['Wind', 'Solar', 'Wind+Solar'], key='trend_cols')

opsd_longd = opsd_daily[data_columns].rolling(window=long_window, center=True, min_periods=max(1, long_window-5)).mean()

fig, ax = plt.subplots(figsize=(12, 6))
if 'Consumption' in trend_cols:
    ax.plot(opsd_daily['Consumption'], marker='.', markersize=2, color='0.6', linestyle='None', label='Daily Consumption')
    ax.plot(opsd_xd['Consumption'], linewidth=2, label=f'Short ({window_sizes}-d) Rolling Mean')

for nm in trend_cols:
    ax.plot(opsd_longd[nm], linewidth=3, label=f'{nm} Trend ({long_window}-d)')

ax.xaxis.set_major_locator(mdates.YearLocator())
if 'Consumption' not in trend_cols and len(trend_cols) > 0:
    ax.set_ylim(0, max(opsd_longd[trend_cols].max().max() * 1.2, 400))

ax.legend()
ax.set_xlabel('Year')
ax.set_ylabel('Energy (GWh)')
ax.set_title(f'Trends using {long_window}-d Rolling Means')
st.pyplot(fig)
st.markdown("There's a significant increasing trend in wind power production and a smaller one in solar, reflecting Germany's renewable energy expansion.")

st.markdown("""
---
**Summary of Learnings:**
This project demonstrated how to wrangle, analyze, and visualize time series data using pandas, matplotlib, and seaborn. We gained insights into seasonality, trends, and other interesting features of electricity consumption and production in Germany.
""")
