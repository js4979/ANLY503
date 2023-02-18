import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import pandas as pd
import numpy as np
import re
import textwrap

pd.set_option("display.max_rows", None)

# Load data
dat_ex16 = pd.read_csv("./data/USA_ALL_export_2016_allproduct.csv")
dat_ex17 = pd.read_csv("./data/USA_ALL_export_2017_allproduct.csv")
dat_ex18 = pd.read_csv("./data/USA_ALL_export_2018_allproduct.csv")
dat_ex19 = pd.read_csv("./data/USA_ALL_export_2019_allproduct.csv")
dat_ex20 = pd.read_csv("./data/USA_ALL_export_2020_allproduct.csv")

dat_im16 = pd.read_csv("./data/USA_ALL_import_2016_allproduct.csv")
dat_im17 = pd.read_csv("./data/USA_ALL_import_2017_allproduct.csv")
dat_im18 = pd.read_csv("./data/USA_ALL_import_2018_allproduct.csv")
dat_im19 = pd.read_csv("./data/USA_ALL_import_2019_allproduct.csv")
dat_im20 = pd.read_csv("./data/USA_ALL_import_2020_allproduct.csv")

############## Data munging ##############
big_df_ex = [dat_ex16, dat_ex17, dat_ex18, dat_ex19, dat_ex20]
big_df_im = [dat_im16, dat_im17,dat_im18,dat_im19,dat_im20]
clean_df = list()

# Creaet a function for label wrapping
def customwrap(s, width=50):
    return "<br>".join(textwrap.wrap(s, width=width))


# Clean all dfs with for loop
for df in big_df_ex:
# for df in big_df_im:
    # Change column names to snake case
    col_names = df.head()
    pattern = re.compile(r"[( -.)]")
    new_names = []
    for name in col_names:
        new_names.append(pattern.sub("_", name).lower())
    # print(new_names)
    df.columns = new_names

    # Drop unwanted columns
    df = df.drop(
        [
            "classification",
            "period",
            "period_desc_",
            "aggregate_level",
            "is_leaf_code",
            "trade_flow",
            "reporter_iso",
            "2nd_partner_code",
            "2nd_partner",
            "2nd_partner_iso",
            "customs_proc__code",
            "customs",
            "mode_of_transport_code",
            "mode_of_transport",
            "alt_qty_unit_code",
            "alt_qty_unit",
            "alt_qty",
            "gross_weight__kg_",
            "cif_trade_value__us__",
            "flag",
            "netweight__kg_",
            "qty_unit_code",
            "qty_unit",
            "fob_trade_value__us__"
        ],
        axis=1,
    )
    # print(df.columns)

    df = df.drop(df.columns[[1, 2, 3, 4, 6]], axis=1)
    # print(df.columns)

    # World data
    df_world = df.loc[df["partner"] == "World"]
    # Drop last row (Total)
    df_world.drop(df_world.tail(1).index, inplace=True)
    # Convert object to int
    df_world["commodity_code"] = df_world.commodity_code.astype(np.int64)
    df_world["qty"] = df_world.qty.astype(np.float64)

    # Compute the sum of commodity quantity for all root categories
    temp = df_world.loc[df_world["commodity_code"] > 10000]
    temp["commodity_code"] = temp["commodity_code"] / 10000
    temp.commodity_code = temp.commodity_code.round()
    # print(dat_exp16_w_temp.head(10))
    # print(dat_exp16_w_temp.commodity_code.unique())
    qty_sum = temp.groupby(["commodity_code", "year"])[
        "qty", "trade_value__us__"
    ].sum()
    qty_sum = qty_sum.reset_index(drop=True)

    # Sub sum into World dataset
    df_world = df_world.loc[df_world["commodity_code"] < 100]
    df_world = df_world.reset_index(drop=True)
    df_world.drop(["qty"], axis=1, inplace=True)
    df_world["qty"] = qty_sum["qty"]
    # Drop all rows with either 0 qty or trade value
    df_world = df_world[(df_world[["trade_value__us__", "qty"]] != 0).all(axis=1)]

    # Rescale trade value
    # df_world["qty"] = round(np.log(df_world["qty"]), 2)
    df_world["trade_value__us__"] = round(df_world["trade_value__us__"] / (10**9), 0)

    df_world["world"] = "Commodity Categories"  # in order to have a single root node

    # Sort the labels by the path in reverse order to make sure the order in tooltip is correct
    df_world.sort_values(by=["commodity", "world"], inplace=True)

    # Wrap label
    df_world.commodity = df_world.commodity.map(customwrap)

    clean_df.append(df_world)
    # print(clean_df[1].head())
    # print(clean_df.tail())
    # print(clean_df.dtypes)
    # exit()
###################################

# Plot the treemap
df = pd.concat(clean_df)
# print(df.shape)
# exit()
big_list = list(df.groupby("year"))
# print(big_list[1][0]) # 2017

first_title = big_list[0][0]
traces = []
buttons = []
for i, d in enumerate(big_list):
    visible = [False] * len(big_list)
    visible[i] = True
    name = d[0]
    year = d[1].year.tolist()
    trade_value = d[1].trade_value__us__.tolist()
    customdata = np.column_stack([year, trade_value])
    hovertemplate = "Category = %{label}<br>Year = %{customdata[0]}<br>Trade value (US$ bilion) = %{customdata[1]}<br>Quantity (num. of unit) = %{value}"
    traces.append(
        px.treemap(
            d[1],
            path=["world", "commodity"],
            values="qty",
            color="trade_value__us__",
        )
        .update_traces(
            visible=True if i == 0 else False,
            customdata=customdata,
            hovertemplate=hovertemplate,
        )
        .data[0]
    )
    buttons.append(
        dict(
            label=name,
            method="update",
            args=[
                {"visible": visible},
                {
                    "title": "Treemap on Trade Value and Quantity for All Commodity Categories (US Export)"
                },
            ],
        )
    )

updatemenus = [
    {
        "active": 0,
        "buttons": buttons,
        "showactive": True,
        "x": 0.06,
        "xanchor": "left",
        "y": 1.09,
        # "yanchor": "top",
        
    }
]

fig = go.Figure(
    data=traces,
    layout=dict(updatemenus=updatemenus),
)

fig.update_layout(
    title="Treemap on Trade Value and Quantity for All Commodity Categories (US Export)",
    title_x=0.5,
    colorscale=dict(sequential="peach"), # Export
    # colorscale=dict(sequential="teal"), # Import
    coloraxis_colorbar=dict(title="Trade Value (US$ billion)"),
    annotations=[
        dict(text="Year:  ", showarrow=False, x=0, y=1.09, yref="paper", align="left")
    ],
)
# fig.data[0]['textfont']['size'] = 20
fig["layout"]["title"]["font"] = dict(size=16)
fig["layout"]["font"] = dict(size=18)
fig.show()

fig.write_html("treemap_export.html")  # , auto_open=True)