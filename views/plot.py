import plotly.graph_objects as go
from views.style import colors


def render_analytics_plot(df, symbol, avgs=None):

    """
    Render analytics plot from dataframe.

    ...

    Attributes
    ----------
    df : pd.DataFrame
        pandas dataframe with historical lines. Should contain columns:
            - dateTime: datetime
            - open: float
            - high: float
            - low: float
            - close: float
            - buy: float
            - sell: float
    symbol: str
        name of the symbol we are plotting
    avgs: dict
        dict whose keys are columns of df representing moving averages
        and values are trace colors

    """

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["dateTime"],
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                increasing_line_color="cyan",
                decreasing_line_color="yellow",
                name="candle",
            )
        ]
    )

    df_buy = df.loc[df["buy"] > 0]

    for i, _ in df_buy.iterrows():
        fig.add_vline(x=df_buy["dateTime"].loc[i], line_width=2, line_dash="dash", line_color="red")

    df_sell = df.loc[df["sell"] > 0]

    for i, _ in df_sell.iterrows():
        fig.add_vline(
            x=df_sell["dateTime"].loc[i], line_width=2, line_dash="dash", line_color="green"
        )

    if avgs:
        for avg_col in avgs:
            fig.add_trace(
                go.Scatter(
                    x=df["dateTime"],
                    y=df[avg_col],
                    mode="lines",
                    name=avg_col,
                    line=dict(width=5, color=avgs[avg_col]),
                )
            )

    fig.update_layout(
        {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
        }
    )

    fig.update_layout(
        title={
            "text": symbol,
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    fig.update_layout(xaxis_rangeslider_visible=False)

    return fig
