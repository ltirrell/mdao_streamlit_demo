import altair as alt
import pandas as pd
import streamlit as st


def combine_pairs(x):
    sorted_strings = sorted(
        [f"[{x['TO_ADDRESS_LABEL']}]", f"[{x['FROM_ADDRESS_LABEL']}]"]
    )
    return "-".join(sorted_strings)


def get_popular(df, size=10, by_date=False):
    if by_date:
        return (
            df.groupby(["DATETIME"])
            .apply(
                lambda x: (
                    x.groupby("LABEL")
                    .sum()
                    .sort_values("TX_COUNT", ascending=False)
                    .head(size)
                )
            )
            .reset_index()
        )
    else:
        return (
            df.groupby("LABEL")
            .TX_COUNT.sum()
            .sort_values(ascending=False)
            .reset_index()
            .head(size)
        )


@st.cache(allow_output_mutation=True)
def load_data():
    # Read in Flipside data of solana swaps from the last 30 days
    q = "6392e078-4836-4cd8-9551-a3346b2cae06"
    url = f"https://api.flipsidecrypto.com/api/v2/queries/{q}/data/latest"
    df = pd.read_json(url)

    # we'll only look at address labels
    df = df[
        [
            "DATETIME",
            "FROM_ADDRESS_LABEL",
            "TO_ADDRESS_LABEL",
            "TOTAL_SWAP_FROM",
            "TOTAL_SWAP_TO",
            "TX_COUNT",
        ]
    ]

    # add pair
    df["PAIR"] = df.apply(combine_pairs, axis=1)

    to_df = (
        df.groupby(["DATETIME", "TO_ADDRESS_LABEL"])
        .TX_COUNT.sum()
        .reset_index()
        .rename(columns={"TO_ADDRESS_LABEL": "LABEL"})
    )
    from_df = (
        df.groupby(["DATETIME", "FROM_ADDRESS_LABEL"])
        .TX_COUNT.sum()
        .reset_index()
        .rename(columns={"FROM_ADDRESS_LABEL": "LABEL"})
    )
    total_df = (
        pd.concat([to_df, from_df]).groupby(["DATETIME", "LABEL"]).sum().reset_index()
    )
    pair_df = (
        df.groupby(["DATETIME", "PAIR"])
        .TX_COUNT.sum()
        .reset_index()
        .rename(columns={"PAIR": "LABEL"})
    )

    d = {
        "Most popular swapped asset": {
            "data": total_df,
            "by_date": pd.DataFrame(),
            "total": pd.DataFrame(),
        },
        "Most popular swapping pairs": {
            "data": pair_df,
            "by_date": pd.DataFrame(),
            "total": pd.DataFrame(),
        },
    }

    return d


def plot_total(source, title, label):
    source["Rank"] = source.index + 1
    chart = (
        alt.Chart(source, title=title)
        .mark_bar()
        .encode(
            alt.X(
                "LABEL:N",
                axis=alt.Axis(domain=False, tickSize=0),
                sort=alt.EncodingSortField(
                    field="TX_COUNT", op="count", order="ascending"
                ),
                title=None,
            ),
            alt.Y("TX_COUNT:Q", title="Transactions"),
            alt.Color(
                "LABEL:N",
                scale=alt.Scale(scheme="category20b"),
                title=label,
                sort=alt.EncodingSortField(
                    field="TX_COUNT", op="sum", order="descending"
                ),
            ),
            tooltip=["Rank", "LABEL", "TX_COUNT"],
        )
        .interactive()
        .properties(height=500)
    )
    return chart


def plot_by_date(source, title, label):
    selection = alt.selection_multi(fields=["LABEL"], bind="legend")

    chart = (
        alt.Chart(source, title=title)
        .mark_bar()
        .encode(
            alt.X(
                "DATETIME:T",
                axis=alt.Axis(domain=False, tickSize=0),
                title=None,
            ),
            alt.Y("TX_COUNT:Q", title="Transactions (normalized)", stack="normalize"),
            alt.Color(
                "LABEL:N",
                scale=alt.Scale(scheme="category20b"),
                title=label,
                sort=alt.EncodingSortField(
                    field="TX_COUNT", op="sum", order="descending"
                ),
            ),
            order=alt.Order("TX_COUNT", sort="ascending"),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
            tooltip=["DATETIME", "LABEL", "TX_COUNT"],
        )
        .add_selection(selection)
        .properties(height=500)
    )
    return chart


data_dict = load_data()

st.title("Popular Swaps on Solana")
st.caption("Looking at the most popular swapped tokens and token pairs in the last 30 days")

st.header("Popular tokens")
"Let's look at the most popular tokens that were swapped. Choose a number with the slider:"

number_of_tokens = st.slider("How many popular tokens do you want to see?", 5, 25, 10)

for k, v in data_dict.items():
    v["total"] = get_popular(v["data"], size=number_of_tokens)
    v["by_date"] = get_popular(v["data"], size=number_of_tokens, by_date=True)
# create plots
for k, v in data_dict.items():
    title = k
    if "pair" in k:
        label = "Pair"
    else:
        label = "Asset"
    v["plot_total"] = plot_total(v["total"], title, label)
    v["plot_by_date"] = plot_by_date(v["by_date"], f"{title}, by date", label)


st.altair_chart(
    data_dict["Most popular swapped asset"]["plot_total"], use_container_width=True
)
st.altair_chart(
    data_dict["Most popular swapping pairs"]["plot_total"], use_container_width=True
)

st.header("Swaps by date")
st.write("Lets see how many transactions involve the most popular assets each day:")
st.altair_chart(
    data_dict["Most popular swapped asset"]["plot_by_date"], use_container_width=True
)

with st.expander("Expand for more"):
    st.header("Most popular daily swapping pairs")
    "Choose which pairs you want to see"
    which_pairs = st.multiselect(
        "Which pairs do you want to see?",
        data_dict["Most popular swapping pairs"]["by_date"].LABEL.unique(),
        data_dict["Most popular swapping pairs"]["by_date"].LABEL.unique(),
    )
    for k, v in data_dict.items():
        title = k
        if "pair" in k:
            label = "Pair"
        else:
            label = "Asset"
        v["plot_by_date"] = plot_by_date(
            v["by_date"][v["by_date"].LABEL.isin(which_pairs)], f"{title}, by date", label
        )

    st.altair_chart(
        data_dict["Most popular swapping pairs"]["plot_by_date"], use_container_width=True
    )
