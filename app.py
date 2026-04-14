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
st.dataframe(opsd_daily.head())

# --- Visualizing Time Series Data ---
st.header('2. Visualizing Time Series Data')
st.subheader('Daily Consumption Over Time')
fig, ax = plt.subplots(figsize=(12, 6))
opsd_daily['Consumption'].plot(linewidth=0.5, ax=ax)
ax.set_ylabel('Daily Totals (GWh)')
ax.set_title('Daily Electricity Consumption (2006-2017)')
st.pyplot(fig)

st.markdown("With so many data points, the line plot is crowded. Let's look at Solar and Wind production too, as scatter plots.")

cols_plot = ['Consumption', 'Solar', 'Wind']
fig, axes = plt.subplots(len(cols_plot), 1, figsize=(12, 9), sharex=True)
for i, col in enumerate(cols_plot):
    axes[i].plot(opsd_daily[col], marker='.', alpha=0.5, linestyle='None')
    axes[i].set_ylabel('Daily Totals (GWh)')
    axes[i].set_title(col)
plt.tight_layout()
st.pyplot(fig)

st.markdown("**Observations:**\n1. Electricity consumption is highest in winter, lowest in summer.\n2. Solar power production is highest in summer, lowest in winter.\n3. Wind power production is highest in winter, lowest in summer.\n4. There's a strong increasing trend in wind power production.\n5. All three time series exhibit clear seasonality.")

st.subheader('Weekly Seasonality in 2017 Consumption')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(opsd_daily.loc['2017-01':'2017-02', 'Consumption'], marker='o', linestyle='-')
ax.set_ylabel('Daily Consumption (GWh)')
ax.set_title('Jan-Feb 2017 Electricity Consumption (with Weekly Gridlines)')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
st.pyplot(fig)
st.markdown("As suspected, consumption is highest on weekdays and lowest on weekends. We also see drastic decreases during holidays.")

# --- Explore Seasonality with Box Plots ---
st.header('3. Exploring Seasonality with Box Plots')

st.subheader('Yearly Seasonality by Month')
fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
for i, name in enumerate(['Consumption', 'Solar', 'Wind']):
    sns.boxplot(data=opsd_daily, x='Month', y=name, ax=axes[i])
    axes[i].set_ylabel('GWh')
    axes[i].set_title(name)
    if axes[i] != axes[-1]:
        axes[i].set_xlabel('')
plt.tight_layout()
st.pyplot(fig)
st.markdown("Electricity consumption is generally higher in winter, though lower in Dec/Jan due to holidays. Wind has more outliers due to extreme weather.")

st.subheader('Weekly Seasonality by Weekday')
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=opsd_daily, x='Weekday Name', y='Consumption', ax=ax)
ax.set_title('Electricity Consumption by Day of Week')
ax.set_ylabel('Consumption (GWh)')
ax.set_xlabel('Day of Week')
st.pyplot(fig)
st.markdown("As expected, consumption is significantly higher on weekdays than on weekends.")

# --- Resampling ---
st.header('4. Resampling Data')
st.subheader('Weekly Mean Resampling of Solar Production')

data_columns = ['Consumption', 'Wind', 'Solar', 'Wind+Solar']
opsd_weekly_mean = opsd_daily[data_columns].resample('W').mean()

start, end = '2017-01', '2017-06'
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(opsd_daily.loc[start:end, 'Solar'], marker='.', linestyle='-', linewidth=0.5, label='Daily')
ax.plot(opsd_weekly_mean.loc[start:end, 'Solar'], marker='o', markersize=8, linestyle='-', label='Weekly Mean Resample')
ax.set_ylabel('Solar Production (GWh)')
ax.legend()
ax.set_title('Daily vs. Weekly Mean Solar Production (Jan-Jun 2017)')
st.pyplot(fig)
st.markdown("Weekly mean resampling smooths out daily fluctuations, making trends clearer.")

st.subheader('Monthly Sums of Electricity Data')
opsd_monthly = opsd_daily[data_columns].resample('ME').sum(min_count=28)
st.dataframe(opsd_monthly.head())

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(opsd_monthly['Consumption'], color='black', label='Consumption')
opsd_monthly[['Wind', 'Solar']].plot.area(ax=ax, linewidth=0)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.legend()
ax.set_ylabel('Monthly Total (GWh)')
ax.set_title('Monthly Electricity Consumption & Production')
st.pyplot(fig)
st.markdown("Monthly view shows clear yearly seasonality and the steady growth of wind power production.")

# --- Annual Share of Wind+Solar ---
st.header('5. Wind + Solar Share of Annual Electricity Consumption')
opsd_annual = opsd_daily[data_columns].resample('YE').sum(min_count=360)
opsd_annual = opsd_annual.set_index(opsd_annual.index.year)
opsd_annual.index.name = 'Year'
opsd_annual['Wind+Solar/Consumption'] = opsd_annual['Wind+Solar'] / opsd_annual['Consumption']

st.write("Annual data (from 2012 onwards for full data):")
st.dataframe(opsd_annual.tail(10))

fig, ax = plt.subplots(figsize=(10, 5))
opsd_annual.loc[2012 : , 'Wind+Solar/Consumption'].plot.bar(color='C0', ax=ax)
ax.set_ylabel('Fraction')
ax.set_ylim(0,0.3)
ax.set_title('Wind + Solar Share of Annual Electricity Consumption (2012-2017)')
plt.xticks(rotation=0)
st.pyplot(fig)
st.markdown("Wind + solar production as a share of annual electricity consumption increased from about 15% in 2012 to about 27% in 2017.")

# --- Rolling Windows ---
st.header('6. Rolling Windows for Trends')

st.subheader('7-day Rolling Mean of Data')
opsd_7d = opsd_daily[data_columns].rolling(7, center=True).mean()
st.dataframe(opsd_7d.head(10))
st.markdown("The 7-day rolling mean smooths daily fluctuations, showing a clearer short-term pattern.")

st.subheader('Comparing Daily, Weekly Resampled, and 7-day Rolling Mean Solar Data')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(opsd_daily.loc[start:end, 'Solar'], marker='.', linestyle='-', linewidth=0.5, label='Daily')
ax.plot(opsd_weekly_mean.loc[start:end, 'Solar'], marker='o', markersize=8, linestyle='-', label='Weekly Mean Resample')
ax.plot(opsd_7d.loc[start:end, 'Solar'], marker='.', linestyle='-', label='7-d Rolling Mean')
ax.set_ylabel('Solar Production (GWh)')
ax.legend()
ax.set_title('Solar Production: Daily vs. Resampled vs. Rolling Mean (Jan-Jun 2017)')
st.pyplot(fig)
st.markdown("Rolling mean preserves the original frequency but smooths the data, while resampling changes the frequency.")

st.subheader('Trends in Electricity Consumption (365-day Rolling Mean)')
opsd_365d = opsd_daily[data_columns].rolling(window=365, center=True, min_periods=360).mean()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(opsd_daily['Consumption'], marker='.', markersize=2, color='0.6', linestyle='None', label='Daily')
ax.plot(opsd_7d['Consumption'], linewidth=2, label='7-d Rolling Mean')
ax.plot(opsd_365d['Consumption'], color='0.2', linewidth=3, label='Trend (365-d Rolling Mean)')
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.legend()
ax.set_xlabel('Year')
ax.set_ylabel('Consumption (GWh)')
ax.set_title('Trends in Electricity Consumption')
st.pyplot(fig)
st.markdown("The 365-day rolling mean shows that long-term electricity consumption has been fairly flat, with dips around 2009 and 2012-2013.")

st.subheader('Trends in Wind and Solar Power Production (365-day Rolling Mean)')
fig, ax = plt.subplots(figsize=(12, 6))
for nm in ['Wind', 'Solar', 'Wind+Solar']:
    ax.plot(opsd_365d[nm], label=nm)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.set_ylim(0, 400)
ax.legend()
ax.set_ylabel('Production (GWh)')
ax.set_title('Trends in Electricity Production (365-d Rolling Means)')
st.pyplot(fig)
st.markdown("There's a significant increasing trend in wind power production and a smaller one in solar, reflecting Germany's renewable energy expansion.")

st.markdown("""
---
**Summary of Learnings:**
This project demonstrated how to wrangle, analyze, and visualize time series data using pandas, matplotlib, and seaborn. We gained insights into seasonality, trends, and other interesting features of electricity consumption and production in Germany.
""")
