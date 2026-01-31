import plotly.graph_objects as go


def price_with_sma(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["close"], name="Close"))
    for col in ["sma20", "sma50", "sma200"]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col.upper()))
    fig.update_layout(height=450, margin=dict(l=10,r=10,t=40,b=10))
    return fig


def rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["rsi14"], name="RSI(14)"))
    fig.add_hline(y=70, line_dash="dash")
    fig.add_hline(y=30, line_dash="dash")
    fig.update_layout(height=260, margin=dict(l=10,r=10,t=40,b=10))
    return fig
