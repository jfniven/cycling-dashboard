import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(layout="wide")

@st.cache_data
def get_data():

    DATA_FILENAME = Path(__file__).parent/'data/clean_cycle_data.feather'
    df = pd.read_feather(DATA_FILENAME)

    df = df.query("ymd >= '2020-01-01'")
    return df


@st.cache_data
def get_weather_data():
    
    DATA_FILENAME = Path(__file__).parent/'data/weather_data.csv'
    df = pd.read_csv(DATA_FILENAME)

    df = df.query("ymd >= '2020-01-01'").sort_values(by=["ymd"])
    return df


@st.cache_data
def convert_for_download(df):
    return df.to_csv(index=False).encode("utf-8")


@st.cache_data
def trip_counts(df, group_cols=[]):

    return df.groupby(by=group_cols, as_index=False).agg(total_trips=("trips", "sum"))


df = get_data()
df_weather = get_weather_data()

# df["y"] = df["y"].astype("str")

df_ymd = trip_counts(df, ["ymd", "ym", "y", "m", "weekday"])
df_yw = trip_counts(df, ["y", "week"])
df_ym = trip_counts(df, ["ym", "m", "y"])
df_y = trip_counts(df, ["y"])

df_combined_ymd = pd.merge(df_ymd, df_weather, on="ymd")

df_channel_ymd = trip_counts(df, ["channel", "ymd", "ym", "y", "m", "weekday"])
df_channel_yw = trip_counts(df, ["channel", "y", "week"])
df_channel_ym = trip_counts(df, ["channel", "ym", "m", "y"])
df_channel_y = trip_counts(df, ["channel", "y"])

df_channel_combined = pd.merge(df_channel_ymd, df_weather, on="ymd")

df_direction_ymd = trip_counts(df, ["channel", "direction", "weekday"])
df_direction_h = trip_counts(df, ["channel", "direction", "hour"])

###### Define constants
# Date range of data
min_date = df.ymd.min()
max_date = df.ymd.max()

# Channel names
channels = sorted(df.channel.unique().tolist())
channel_color_dict = dict(zip(channels,px.colors.qualitative.Alphabet[0:len(channels)]))

####### Plots
st.subheader(f"Overall network counts")

date_format = st.radio(
    "Select date group format",
    ["Daily", "Monthly", "Yearly"],
    key="count_totals",
    index=1,
    horizontal=True,
)

if date_format == "Daily":
    df_plot = df_ymd
    x_var = "ymd"
    x_label = "Date"
elif date_format == "Weekly":
    df_plot = df_yw
    x_var = "week"
    x_label = "Week Number"
elif date_format == "Monthly":
    df_plot = df_ym
    x_var = "ym"
    x_label = "Month"
else:
    df_plot = df_y
    x_var = "y"
    x_label = "Year"

fig_total_counts = px.bar(df_plot, x=x_var, y="total_trips")

# Axis formatting
fig_total_counts.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text =x_label,
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = f"Overall {date_format.lower()} count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    autosize=False,
    width=1000,
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

config = {
    'staticPlot': True,
    "toImageButtonOptions": {"format": "png", "filename": "count_totals", "scale": 5}
}

col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col2:
    st.plotly_chart(
        fig_total_counts, on_select="ignore", use_container_width=True, config=config
    )

#########################################################################################
# Temperature

####### Plots
st.divider()

st.subheader(
    f"Overall daily count vs. mean daily temperature (days with no precipitation)"
)

fig_temp_counts = px.scatter(
    df_combined_ymd.query(
        "y>= 2024 & total_rain == 0 & total_snow == 0 & total_precip == 0 & snow_on_ground == 0"
    ),
    x="mean_temp",
    y="total_trips",
)

# Axis formatting
fig_temp_counts.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text = "Mean daily temperature",
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = f"Overall daily count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    autosize=False,
    width=1000,
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

config = {
    "toImageButtonOptions": {"format": "png", "filename": "count_totals", "scale": 5}
}

col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col2:
    st.plotly_chart(
        fig_temp_counts, on_select="ignore", use_container_width=True, config=config
    )

# # ##########################################################################################
# # # Rain

# # ####### Plots
# # st.divider()

# # st.subheader(f"Count Totals vs. Rain")

# # fig_rain_counts = px.scatter(
# #     df_combined_ymd.query("y>= 2024 & total_rain != 0 & mean_temp >=0"),
# #     x="total_rain",
# #     y="total_trips",
# #     color="mean_temp",
# # )

# # # Axis formatting
# # fig_rain_counts.update_layout(
# #     xaxis=dict(
# #         title="Mean Daily Temperature",
# #         titlefont_size=20,
# #         tickfont_size=20,
# #         tickangle=0,
# #     ),
# #     yaxis=dict(
# #         title=f"Total Daily Trips",
# #         titlefont_size=20,
# #         tickfont_size=20,
# #     ),
# #     autosize=False,
# #     width=1000,
# #     height=600,
# #     margin=dict(l=0, r=0, t=0, b=0),
# #     font_color="black",
# # )

# # config = {
# #     "toImageButtonOptions": {"format": "png", "filename": "count_totals", "scale": 5}
# # }

# # col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

# # with col2:
# #     st.plotly_chart(
# #         fig_rain_counts, on_select="ignore", use_container_width=True, config=config
# #     )

# # ####################
# # # RSnow on ground

# # ####### Plots
# # st.divider()

# # st.subheader(f"Count Totals vs. Rain")

# # fig_snwgnd_counts = px.scatter(
# #     df_combined_ymd.query("y>= 2024 & snow_on_ground!= 0"),
# #     x="snow_on_ground",
# #     y="total_trips",
# #     color="mean_temp",
# # )

# # # Axis formatting
# # fig_snwgnd_counts.update_layout(
# #     xaxis=dict(
# #         title="Mean Daily Temperature",
# #         titlefont_size=20,
# #         tickfont_size=20,
# #         tickangle=0,
# #     ),
# #     yaxis=dict(
# #         title=f"Total Daily Trips",
# #         titlefont_size=20,
# #         tickfont_size=20,
# #     ),
# #     autosize=False,
# #     width=1000,
# #     height=600,
# #     margin=dict(l=0, r=0, t=0, b=0),
# #     font_color="black",
# # )

# # config = {
# #     "toImageButtonOptions": {"format": "png", "filename": "count_totals", "scale": 5}
# # }

# # col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

# # with col2:
# #     st.plotly_chart(
# #         fig_snwgnd_counts, on_select="ignore", use_container_width=True, config=config
# #     )

##########################################################################################
st.divider()

st.subheader(f"Counter histories")



fig_histories = px.scatter(
    df_channel_ymd.query("total_trips>0"), x="ymd", y="channel", color="channel",color_discrete_map=channel_color_dict
)

# Axis formatting
fig_histories.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text = "Date",
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
            tickformat="%b\n%Y",
        ),
        yaxis=dict(
            title=dict(
                text = "Counter",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    showlegend=True,
    legend=dict(
        title=dict(text="Route", font_size=20),
        yanchor="top",
        y=1,
        xanchor="left",
        x=1,
        font=dict(size=16),
    ),
    autosize=False,
    width=1000,
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

config = {
    "toImageButtonOptions": {
        "format": "png",
        "filename": "counter_histories",
        "scale": 5,
    }
}

col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col2:
    st.plotly_chart(
        fig_histories, on_select="ignore", use_container_width=True, config=config
    )
##########################################################################################

st.divider()

st.subheader(f"Route totals")

date_format = st.radio(
    "Select date group format",
    ["Daily", "Monthly", "Yearly"],
    key="channel_totals",
    index=1,
    horizontal=True,
)

if date_format == "Daily":
    df_plot = df_channel_ymd
    x_var = "ymd"
    x_label = "Date"
elif date_format == "Weekly":
    df_plot = df_channel_yw
    x_var = "week"
    x_label = "Week Number"
elif date_format == "Monthly":
    df_plot = df_channel_ym
    x_var = "ym"
    x_label = "Month"
else:
    df_plot = df_channel_y
    x_var = "y"
    x_label = "Year"

fig_total_counts_channel = px.line(
    df_plot,
    x=x_var,
    y="total_trips",
    color="channel",
    color_discrete_map=channel_color_dict
)

# Axis formatting
fig_total_counts_channel.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text =x_label,
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = f"Total {date_format.lower()} count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    autosize=False,
    width=1000,
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

config = {
    "toImageButtonOptions": {
        "format": "png",
        "filename": "all_route_totals",
        "scale": 5,
    }
}

col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col2:
    st.plotly_chart(
        fig_total_counts_channel,
        on_select="ignore",
        use_container_width=True,
        config=config,
    )

st.divider()
######### Channel plot
st.header(f"Individual counters")

col1, col2, col3 = st.columns(3)

with col1:
    selected_channel = st.selectbox("Select a route", channels, index=1)

    st.subheader("Counter history")
    date_format_channel = st.radio(
        "Select date group format",
        ["Daily ", "Monthly ", "Yearly "],
        index=1,
        horizontal=True,
    )

if date_format_channel == "Daily ":
    df_channel = df_channel_ymd.query("channel == @selected_channel")
    x_var = "ymd"
elif date_format_channel == "Monthly ":
    df_channel = df_channel_ym.query("channel == @selected_channel")
    x_var = "ym"
else:
    df_channel = df_channel_y.query("channel == @selected_channel")
    x_var = "y"

fig_channel_counts = px.bar(
    df_channel,
    x=x_var,
    y="total_trips",
    hover_data=x_var,
)

if date_format_channel == "Yearly ":

    # Axis formatting
    fig_channel_counts.update_layout(
        dict(
            xaxis=dict(
                title=dict(
                    text = "Date",
                    font=dict(
                        size = 20
                    )
                ),
                tickfont = dict(
                    size = 20
                ),
                tickformat="array",
                tickvals=df_channel.y.unique(),
                ticktext=df_channel.y.unique(),
            ),
            autosize=False,
            width=1000,
            height=600,
            margin=dict(l=0, r=0, t=0, b=0),
            font_color="black",
        )
    )

else:
    fig_channel_counts.update_layout(
        dict(
            xaxis=dict(
                title=dict(
                    text = "Date",
                    font=dict(
                        size = 20
                    )
                ),
                tickfont = dict(
                    size = 20
                ),
                tickformat="%b\n%Y",
            ),
            autosize=False,
            width=1000,
            height=600,
            margin=dict(l=0, r=0, t=0, b=0),
            font_color="black",
        )
    )

fig_channel_counts.update_layout(
        dict(
            yaxis=dict(
                title=dict(
                    text = f"Total {date_format.lower()} count",
                    font= dict(
                        size = 20
                    ),
                ),
                tickfont = dict(
                    size = 20
                ),
        ),
        autosize=False,
        width=500,
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        font_color="black",
        )
    )


# ####################
fig_direction_counts = px.line(
    df_direction_ymd.query("channel == @selected_channel"),
    x="weekday",
    y="total_trips",
    color="direction",
)

# Axis formatting
fig_direction_counts.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text ="Day of week",
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = f"Total {date_format.lower()} count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    autosize=False,
    width=500,
    height=400,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

fig_channel_counts.update_traces(
    # marker_color="red",
)

##################################################
# MEAN DAILY PERCENTAGES
df_week_sum = (
    df.query("channel == @selected_channel & ym >= '2024-07'")
    .groupby(by=["y", "week", "weekday"], as_index=False)
    .agg(total_trips=("trips", "sum"))
)

df_week_sum["weekly_percent"] = df_week_sum.groupby(by=["y", "week"])[
    "total_trips"
].transform(lambda x: x / x.sum())

fig_weekly = px.bar(
    df_week_sum.groupby(by=["weekday"], as_index=False).agg(
        weekly_mean=("weekly_percent", "mean")
    ),
    x="weekday",
    y="weekly_mean",
    text_auto="0.1%",
)

# Axis formatting
fig_weekly.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text = "Day of week",
                font=dict(
                    size = 20
                )
            ),
            tickangle=30,
            tickmode="array",
            tickvals=[1, 2, 3, 4, 5, 6, 7],
            ticktext=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
        ],
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = "Average percent of weekly count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
            tickformat=".0%",
    ),
    autosize=False,
    width=500,
    height=400,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

fig_weekly.update_traces(
    textposition="inside",
    textfont_size=14,
)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_channel_counts, on_select="ignore")
with col2:

    df_display = (
        df_channel_combined.query("channel == @selected_channel")
        .drop(columns=["channel", "y", "m", "weekday", "ym", "year", "month", "day"])
        .rename(columns={"ymd": "Date"})
        .set_index("Date")
    )

    df_display.columns = df_display.columns.str.title().str.replace("_", " ")
    st.write(df_display)

# ##################################################

col1, col2 = st.columns(2)

#### Directionality
with col1:
    st.subheader("Average percent of weekly count by day of week")
    st.plotly_chart(fig_weekly, on_select="ignore")

# MEAN HOURLY PERCENTAGES
df_channel_hour = df.query("channel == @selected_channel & ym >= '2024-07'")

option_map = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}

with col2:

    st.subheader("Average percent of daily count by hour of day") 
    
    selected_days = st.pills(
        "Select day(s) of the week",
        options=option_map.keys(),
        format_func=lambda option: option_map[option],
        selection_mode="multi",
        default=[1, 2, 3, 4, 5],
    )

df_hour_sum = (
    df_channel_hour.query("weekday in @selected_days")
    .groupby(by=["y", "weekday", "hour", "direction"], as_index=False)
    .agg(total_trips=("trips", "sum"))
)

# Don't want to group by direction, want to normalize to total number of trips (both directions). This highlights routes with asymmetric counts.
df_hour_sum["hourly_percent"] = df_hour_sum.groupby(by=["weekday"])[
    "total_trips"
].transform(lambda x: x / x.sum())

df_hour_mean = df_hour_sum.groupby(by=["direction", "hour"], as_index=False).agg(
    hourly_mean=("hourly_percent", "mean")
)

fig_hourly = px.line(
df_hour_mean,
x="hour",
y="hourly_mean",
markers=True,
color="direction",
)

# Axis formatting
fig_total_counts.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text = "Hour of Day",
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
            tickmode="array",
            tickvals=[0, 3, 6, 9, 12, 15, 18, 21],
            ticktext=[
                "12 AM",
                "3 AM",
                "6 AM",
                "9 AM",
                "12 PM",
                "3 PM",
                "6 PM",
                "9 PM",
            ],
        ),
        yaxis=dict(
            title=dict(
                text = "Average percent of daily count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
            tickformat=".0%",
            range=[0, 0.1],
    ),
    legend=dict(
        title=dict(text="Direction", font_size=20),
        yanchor="top",
        y=1,
        xanchor="right",
        x=1,
        font=dict(size=16),
        ),
    autosize=False,
    width=500,
    height=400,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

with col2:
    st.plotly_chart(fig_hourly, on_select="ignore")

# ##############################

fig_temp_counts = px.scatter(
    df_channel_combined.query(
        "channel == @selected_channel & total_trips > 0 & y>= 2024 & total_rain == 0 & total_snow == 0 & total_precip == 0 & snow_on_ground == 0"
    ),
    x="mean_temp",
    y="total_trips",
)

# Axis formatting
fig_total_counts.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text = "Mean daily temperature",
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = "Total daily count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    autosize=False,
    width=500,
    height=400,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

config = {
    "toImageButtonOptions": {"format": "png", "filename": "count_totals", "scale": 5}
}

# ##########################################################################################
# Rain

####### Plots
st.divider()

fig_rain_counts = px.scatter(
    df_channel_combined.query(
        "channel == @selected_channel & total_trips > 0 & y>= 2024 & total_rain != 0 & mean_temp >=0"
    ),
    x="total_rain",
    y="total_trips",
    color="mean_temp",
)

# Axis formatting
fig_total_counts.update_layout(
    dict(
        xaxis=dict(
            title=dict(
                text = "Total daily rain (mm)",
                font=dict(
                    size = 20
                )
            ),
            tickfont = dict(
                size = 20
            ),
        ),
        yaxis=dict(
            title=dict(
                text = "Total daily count",
                font= dict(
                    size = 20
                ),
            ),
            tickfont = dict(
                size = 20
            ),
    ),
    coloraxis_colorbar=dict(
        title="Mean temp",
    ),
    autosize=False,
    width=1000,
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    font_color="black",
    )
)

config = {
    "toImageButtonOptions": {"format": "png", "filename": "count_totals", "scale": 5}
}

st.header("Weather")

col1, col2 = st.columns(2)

with col1:
    st.subheader(
        f"Total daily count vs. mean daily temperature (days with no precipitation since 2024)"
    )
    st.plotly_chart(
        fig_temp_counts, on_select="ignore", use_container_width=True, config=config
    )
with col2:
    st.subheader(f"Total daily counts vs. daily rain (since 2024)")
    st.plotly_chart(
        fig_rain_counts, on_select="ignore", use_container_width=True, config=config
    )


# ####### Data Exports
# csv = convert_for_download(df_ymd)

with st.sidebar:

    st.title("Historical Halifax Cycling Dashboard")

    st.markdown(
        "Created by [John Niven](https://bsky.app/profile/johnniven.bsky.social)"
    )

    st.subheader(f"Data updated {max_date}")

    # st.download_button(
    #     label="Download data",
    #     data=csv,
    #     file_name=f"daily_cycling_counts_{max_date}.csv",
    #     mime="text/csv",
    #     icon=":material/download:",
    # )

    st.markdown(
        "[View raw data](https://catalogue-hrm.opendata.arcgis.com/datasets/45d4ecb0cb48469186e683ebc54eb188_0/explore)"
    )
