"""Build recruiter-friendly static figures and a standalone offline HTML dashboard."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

BLUE = "#1d4ed8"
TEAL = "#0891b2"
NAVY = "#13233b"
REGION_COLORS = {"Africa":"#be5b67", "Americas":"#2b7a9b", "Asia":"#b8842e", "Europe":"#4f6bb4", "Oceania":"#477e64"}


def make_figures(df, annual, regional, changes, metrics, root: Path):
    dest = root / "reports" / "figures"
    dest.mkdir(parents=True, exist_ok=True)
    recent = regional[regional["year"] == metrics["last_year"]].sort_values("weighted_life_expectancy")
    base = regional[regional["year"] == metrics["first_year"]]
    latest = df[df["year"] == metrics["last_year"]]

    # Static high-resolution visual 1
    fig, ax=plt.subplots(figsize=(10,5.4))
    for region, data in regional.groupby("continent"):
        ax.plot(data["year"], data["weighted_life_expectancy"], marker="o", linewidth=2.2,
                markersize=3.8, label=region, color=REGION_COLORS[region])
    ax.set(title="Life expectancy by region, 1952–2007", xlabel="Observation year", ylabel="Population-weighted years")
    ax.grid(alpha=.19); ax.legend(ncol=3,frameon=False)
    fig.text(.11,.01,"Historical Gapminder panel (142 countries). Population-weighted by observed country-year population.",fontsize=9,color="#56637a")
    fig.tight_layout(rect=(0,.04,1,1)); fig.savefig(dest/"01_regional_life_expectancy.png",dpi=180,bbox_inches="tight");plt.close(fig)

    fig, ax=plt.subplots(figsize=(9.5,5.3))
    bars=ax.barh(recent["continent"], recent["weighted_life_expectancy"], color=[REGION_COLORS[c] for c in recent["continent"]])
    for bar, val in zip(bars,recent["weighted_life_expectancy"]):
        ax.text(float(val)+0.5,bar.get_y()+bar.get_height()/2,f"{val:.1f}",va="center",fontsize=10)
    ax.set_xlim(0,92);ax.set(xlabel="Population-weighted life expectancy (years)",title="Regional life expectancy in 2007")
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout();fig.savefig(dest/"02_region_comparison_2007.png",dpi=180,bbox_inches="tight");plt.close(fig)

    fig, ax=plt.subplots(figsize=(9.5,5.6))
    for continent, d in latest.groupby("continent"):
        ax.scatter(d["gdpPercap"],d["lifeExp"],s=(d["pop"]/1e6)**0.5*10+8,
                   alpha=.73, color=REGION_COLORS[continent],label=continent,edgecolors='white',linewidths=.4)
    ax.set_xscale('log'); ax.set(xlabel="GDP per capita (log scale; dataset units)",ylabel="Life expectancy (years)", title="GDP per capita and life expectancy, 2007")
    ax.legend(frameon=False,ncol=3);ax.grid(alpha=.16)
    fig.tight_layout();fig.savefig(dest/"03_gdp_life_scatter_2007.png",dpi=180,bbox_inches="tight");plt.close(fig)

    # Four independent interactive charts embedded into one offline HTML.
    fig1=go.Figure()
    for region, d in regional.groupby('continent'):
        fig1.add_trace(go.Scatter(x=d.year,y=d.weighted_life_expectancy,mode='lines+markers',
                                 name=region, line=dict(color=REGION_COLORS[region],width=2.6)))
    fig1.update_layout(title="Population-weighted life expectancy by region",xaxis_title="Year",yaxis_title="Years",
                       paper_bgcolor='white',plot_bgcolor='white',template='plotly_white',height=430,
                       margin=dict(l=40,r=25,t=60,b=40),legend=dict(orientation='h',y=-.2))

    fig2=go.Figure()
    for region,d in latest.groupby('continent'):
        fig2.add_trace(go.Scatter(x=d.gdpPercap,y=d.lifeExp,mode='markers',name=region,
           text=d.country,customdata=d['pop'],marker=dict(size=(d['pop']/1e6)**0.42*5+5,color=REGION_COLORS[region],opacity=.73),
           hovertemplate="<b>%{text}</b><br>GDP per capita: %{x:,.0f}<br>Life expectancy: %{y:.1f}<br>Population: %{customdata:,.0f}<extra></extra>"))
    fig2.update_layout(title="GDP per capita vs. life expectancy (2007)",xaxis_type='log',xaxis_title="GDP per capita (log scale)",
          yaxis_title="Life expectancy (years)",template="plotly_white",height=430,
          margin=dict(l=40,r=25,t=60,b=40),legend=dict(orientation='h',y=-.2))

    fig3=go.Figure()
    ordered=recent.sort_values('weighted_life_expectancy', ascending=False)
    fig3.add_trace(go.Bar(x=ordered.continent,y=ordered.weighted_life_expectancy,
                          marker_color=[REGION_COLORS[x] for x in ordered.continent],
                          text=ordered.weighted_life_expectancy.round(1),textposition='outside',name='2007'))
    fig3.update_layout(title="Regional comparison, 2007",yaxis_title="Population-weighted life expectancy (years)",
                       template="plotly_white",height=430,margin=dict(l=40,r=25,t=60,b=50),showlegend=False,yaxis_range=[0,91])

    top=changes.nlargest(12,'life_expectancy_change_years').sort_values('life_expectancy_change_years')
    fig4=go.Figure(go.Bar(x=top.life_expectancy_change_years, y=top.country,orientation='h',marker_color=TEAL,
                           hovertemplate="%{y}: +%{x:.1f} years<extra></extra>"))
    fig4.update_layout(title="Largest improvements, 1952–2007",xaxis_title="Increase in life expectancy (years)",
                       template="plotly_white",height=470,margin=dict(l=125,r=20,t=60,b=50))

    graphs=[]
    for idx, f in enumerate([fig1,fig2,fig3,fig4]):
        graphs.append(pio.to_html(f,full_html=False,include_plotlyjs="inline" if idx==0 else False,
                                  config={"displaylogo":False,"responsive":True}))
    cards = [
        ("Country-year rows",f"{metrics['rows']:,}"),
        ("Countries",str(metrics["countries"])),
        ("Weighted lifespan, 1952",f"{metrics['start_population_weighted_life_expectancy']:.1f} years"),
        ("Weighted lifespan, 2007",f"{metrics['end_population_weighted_life_expectancy']:.1f} years"),
    ]
    kpis=''.join(f'<article class="kpi"><span>{label}</span><strong>{value}</strong></article>' for label,value in cards)
    html=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Global Development | Historical Data Dashboard</title><style>
    body{{font-family:Inter,Segoe UI,Arial,sans-serif;background:#f5f8fc;color:#13233b;margin:0}}
    header{{background:#13233b;color:white;padding:38px max(22px,5vw);}}h1{{font-size:clamp(1.45rem,3vw,2.2rem);margin:8px 0}}
    header p{{color:#cbd8e9;line-height:1.5;max-width:850px}} .tag{{color:#8dd9e8;letter-spacing:.14em;font-size:.74rem;font-weight:700}}
    main{{max-width:1280px;padding:24px 22px 55px;margin:auto}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}}
    .kpi{{border:1px solid #dde6ef;background:white;border-radius:12px;padding:20px}}.kpi span{{display:block;color:#65758b;font-size:.86rem}}.kpi strong{{display:block;font-size:1.7rem;margin-top:8px}}
    .charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,540px),1fr));gap:18px;margin-top:20px}}
    .plot{{border:1px solid #dde6ef;background:white;padding:7px;border-radius:12px;overflow:hidden}}
    footer{{font-size:.85rem;color:#617188;line-height:1.7;margin-top:25px}}
    a{{color:#1366b7}} </style></head><body><header><div class="tag">REPRODUCIBLE ANALYTICS PORTFOLIO</div>
    <h1>Global Development & Regional Inequality</h1><p>Exploring historical patterns in life expectancy, GDP per capita, and population across 142 countries (1952–2007). Interactive charts; hover, zoom and download images using the plot toolbar.</p></header>
    <main><section class="cards">{kpis}</section><section class="charts">{''.join('<div class="plot">'+g+'</div>' for g in graphs)}</section>
    <footer><b>Source:</b> Gapminder historical panel supplied with Plotly. This dashboard describes only included countries, not every country worldwide.
    Population-weighted means depend on the dataset population figures; ecological correlations are not causal and 2007 data are not current.
    Attribution: <a href="https://www.gapminder.org/data/">Gapminder</a> / <a href="https://plotly.com/python/px-arguments/">Plotly</a>.</footer></main></body></html>"""
    (root / "dashboard" / "index.html").write_text(html,encoding="utf-8")
