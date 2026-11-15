"""SUPERR SELECTOR | Rajasthan Royals batting pressure scouting dashboard."""
import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from analytics import calculate, WEIGHTS

st.set_page_config(page_title="SUPERR SELECTOR | RR Auction 2027", page_icon="🏏", layout="wide", initial_sidebar_state="expanded")
NAVY="#080F25"; PANEL="#111C37"; PANEL2="#142241"; PINK="#FF5FA9"; BLUE="#66A7FF"; WHITE="#F6F8FF"; MUTED="#A7B6D4"

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap');
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif!important}
.stApp,[data-testid="stAppViewContainer"], [data-testid="stHeader"]{background:#080F25!important;color:#F6F8FF!important}
[data-testid="stHeader"]{background:rgba(8,15,37,.95)!important}
.block-container{max-width:1600px;padding:1.5rem 2rem 4rem!important}
[data-testid="stSidebar"]{background:linear-gradient(165deg,#111D3B 0%,#09132D 100%)!important;border-right:1px solid #34446D!important}
[data-testid="stSidebar"] *{color:#EAF0FF!important}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#152443!important;border:1px solid #40517B!important}
[data-testid="stSidebar"] [data-baseweb="select"] *{color:#F6F8FF!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label{border-radius:10px;padding:8px 10px;transition:background .2s}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#223251}
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"]{background:#FF5FA9!important}
h1,h2,h3,h4{font-family:'Outfit',sans-serif!important;color:#F6F8FF!important;letter-spacing:-.025em!important}
h1{font-size:2.6rem!important;font-weight:900!important;margin-bottom:0!important}
h2{font-size:1.55rem!important}
p,li,label,[data-testid="stMarkdownContainer"]{color:#E2E9FB}
[data-testid="stMetric"]{background:linear-gradient(145deg,#18284B,#101B35)!important;border:1px solid rgba(255,95,169,.62)!important;border-radius:19px!important;padding:18px 19px!important;min-height:132px;box-shadow:0 8px 0 #060B1A,0 16px 30px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.07)!important}
[data-testid="stMetricLabel"] p{font-size:.82rem!important;color:#B3C0DD!important;font-weight:650!important}
[data-testid="stMetricValue"]{font:800 clamp(1.35rem,2vw,1.85rem) 'Outfit',sans-serif!important;color:#FFFFFF!important;letter-spacing:-.025em!important}
[data-testid="stMetricDelta"]{color:#FF91C7!important}
[data-testid="stDataFrame"]{border:1px solid rgba(255,95,169,.53)!important;border-radius:16px!important;overflow:hidden!important;box-shadow:0 9px 23px #00000045}
[data-testid="stSelectbox"]>div>div{background:#172747!important;border:1px solid #5B648C!important;border-radius:11px!important;color:#F6F8FF!important}
[data-testid="stSelectbox"] *{color:#F6F8FF!important}
[data-testid="stDownloadButton"] button{background:#FF5FA9!important;color:#0B1327!important;font-weight:800!important;border:0!important;border-radius:11px!important}
[data-testid="stPlotlyChart"]{border:1px solid rgba(255,95,169,.45);background:linear-gradient(160deg,#111D38,#0E1932);border-radius:18px;padding:12px 10px;box-shadow:0 10px 25px #00000055}
hr{border-color:#34415D!important}
.brand{font:900 27px 'Outfit',sans-serif;letter-spacing:-1px;color:#fff;line-height:1.05;margin-bottom:10px}
.brand em{color:#FF5FA9;font-style:normal}
.eyebrow{color:#FF91C7;font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase;margin-bottom:7px}
.subtitle{color:#A7B6D4;font-size:14px;margin:2px 0 18px}
.section-head{font:800 21px 'Outfit',sans-serif;color:#F6F8FF;margin:27px 0 11px;letter-spacing:-.02em}
.section-caption{color:#A7B6D4;font-size:12px;margin:-4px 0 14px}
/* Matched two-column chart heading footprints */
.chart-heading{min-height:65px;display:flex;flex-direction:column;justify-content:flex-start;margin-top:10px}
.chart-heading .section-head{margin:0 0 5px;font-size:18px;line-height:1.3}
.chart-heading .section-caption{margin:0;font-size:12px;line-height:1.35}
.rating-card{background:linear-gradient(145deg,#172746,#101A34);border:1px solid rgba(255,95,169,.72);border-radius:19px;padding:20px 23px;margin:18px 0;box-shadow:0 8px 0 #060B1A,0 18px 32px #00000040,inset 0 1px 0 #FFFFFF13}
.rating-top{display:flex;align-items:center;justify-content:space-between;gap:15px;font:700 15px 'DM Sans';color:#E7ECFA}
.rating-num{font:900 27px 'Outfit';color:#fff}
.track{height:13px;border-radius:99px;background:#283858;overflow:hidden;margin:14px 0 10px}
.fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#FF5FA9,#FF9ACB);box-shadow:0 0 14px #FF5FA970}
.fineprint{color:#A7B6D4;font-size:12px;line-height:1.7}
.player-strip{border:1px solid #34496D;border-left:3px solid #FF5FA9;border-radius:12px;background:#101D38;padding:14px 18px;color:#CBD6EC;font-size:13px;line-height:1.8;margin:8px 0 20px}
[data-testid="stAlert"]{background:#172542;border:1px solid #50638D}
@media(max-width:760px){.block-container{padding:1.2rem .8rem 3rem!important}h1{font-size:2.0rem!important}.rating-num{font-size:21px}}

[data-testid="stDataFrame"], [data-testid="stDataFrame"] > div, [data-testid="stDataFrame"] iframe,
[data-testid="stTable"], [data-testid="stTable"] table {background:#101B35!important;color:#F6F8FF!important;}
[data-testid="stDataFrame"] {border:2px solid #FF5FA9!important;box-shadow:0 8px 0 #060B1A,0 20px 35px #00000055!important;}
[data-testid="stDataFrame"] [role="grid"], [data-testid="stDataFrame"] [role="row"],
[data-testid="stDataFrame"] [role="columnheader"], [data-testid="stDataFrame"] [role="gridcell"]
{background:#101B35!important;color:#F6F8FF!important;border-color:#33466D!important;}
[data-testid="stDataFrame"] [role="columnheader"]{background:#1D2B4D!important;color:#FF91C7!important;}
/* Unified navy table, chart and card surfaces */
[data-testid="stDataFrame"] [data-testid="stDataFrameResizable"]{background:#101B35!important}
[data-testid="stDataFrame"] canvas{background:#101B35!important}
[data-testid="stPlotlyChart"]{border:2px solid rgba(255,95,169,.72)!important;box-shadow:0 8px 0 #060B1A,0 19px 33px #00000050!important}
[data-testid="stMetric"]{border:2px solid rgba(255,95,169,.72)!important}
.table-wrap{background:#101B35;border:2px solid #FF5FA9;border-radius:18px;overflow-x:auto;box-shadow:0 8px 0 #060B1A,0 19px 33px #00000050;margin:10px 0 20px}
.rr-table{width:100%;border-collapse:collapse;color:#EAF0FF;font-size:13px;min-width:900px;table-layout:auto}
.rr-table th{background:#1D2B4D;color:#FF91C7;text-align:left;font-size:12px;padding:14px 10px;white-space:normal;line-height:1.35;vertical-align:middle}
.rr-table td{background:#101B35;border-top:1px solid #2B3C60;padding:12px 10px;white-space:nowrap}
.rr-table tr:hover td{background:#1A2A4C}
.rr-table .number{text-align:right;font-variant-numeric:tabular-nums}
.score-row{display:flex;align-items:center;gap:7px;min-width:110px}
.score-track{flex:1;height:9px;background:#293A5B;border-radius:20px;overflow:hidden}
.score-fill{height:100%;background:linear-gradient(90deg,#EC4C99,#FF91C7);border-radius:20px}
.score-value{font-weight:800;color:#FFF;min-width:48px;text-align:right}

[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {background:#172747!important;color:#F6F8FF!important;}
.pressure-card{background:linear-gradient(145deg,#172746,#101A34);border:1px solid #FF5FA9;border-radius:17px;padding:19px;min-height:180px;box-shadow:0 7px 0 #060B1A,0 15px 26px #00000040;margin:8px 0 15px}.pressure-number{color:#FF91C7;font-weight:800;letter-spacing:1.6px;font-size:10px;margin-bottom:12px}.pressure-title{color:#FFFFFF;font:800 17px 'Outfit',sans-serif;margin-bottom:9px}.pressure-detail{color:#BDCAE5;font-size:13px;line-height:1.65}

/* Filter panel is a real Streamlit column, not a repositioned sidebar. */
.filter-panel{background:#111C37;border:1px solid #FF5FA9;border-radius:16px;padding:15px;margin-top:8px}
[data-testid='stVerticalBlockBorderWrapper']{border-color:#FF5FA9!important;border-radius:16px!important}
[data-testid='stSelectbox']{width:100%!important;min-width:0!important;text-align:left!important}
[data-testid='stWidgetLabel'],[data-testid='stWidgetLabel'] p{ text-align:left!important;justify-content:flex-start!important }
[data-testid='stVerticalBlockBorderWrapper'] [data-testid='stSelectbox']{margin-top:0!important}
[data-testid='stSelectbox'] [data-baseweb='select']{min-width:0!important;width:100%!important}
[data-testid='stHorizontalBlock']>[data-testid='stColumn']{min-width:0!important}
@media(max-width:1100px){.block-container{padding:1rem 1.1rem 3rem!important}.rr-table{min-width:790px}}
[data-testid="stMetricValue"]{overflow-wrap:break-word!important;white-space:normal!important;line-height:1.2!important;font-size:clamp(1.08rem,1.5vw,1.65rem)!important;max-width:100%!important}
[data-testid="stMetric"]{min-width:0!important;min-height:152px!important;display:flex!important;flex-direction:column!important;justify-content:center!important}
[data-testid="stMetricValue"]>div{white-space:normal!important;overflow-wrap:break-word!important}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{font-size:.78rem!important;line-height:1.45!important;color:#B6C5E2!important}
.delta-up{color:#47D79B!important;font-weight:800;white-space:nowrap}.delta-down{color:#FF647E!important;font-weight:800;white-space:nowrap}.delta-flat{color:#C6D2E7!important;font-weight:700;white-space:nowrap}
@media(max-width:1250px){[data-testid="stMetricValue"]{font-size:1.1rem!important}[data-testid="stMetric"]{padding:12px!important}}

/* All four headline cards share a single sizing and alignment system. */
/* Descriptions appear only when the Streamlit help (?) icon is clicked/hovered. */
[data-testid="stSidebar"] [data-testid="stTooltipIcon"]{color:#DDE7FF!important}
[data-baseweb="tooltip"], [role="tooltip"]{color:#F7F9FF!important;background:#101827!important;max-width:330px!important}
[data-baseweb="tooltip"] *, [role="tooltip"] *{color:#F7F9FF!important}


/* Standard Streamlit question-mark tooltips: black text on white, hover to reveal. */
[data-testid="stTooltipIcon"]{color:#EAF0FF!important}
[data-baseweb="tooltip"],[role="tooltip"],div[data-testid="stTooltipContent"]{background:#FFFFFF!important;color:#101010!important;max-width:330px!important}
[data-baseweb="tooltip"] *,[role="tooltip"] *,div[data-testid="stTooltipContent"] *{color:#101010!important}
/* All four summary cards use identical compact dimensions. */
.leader-card{height:112px!important;min-height:112px!important;max-height:112px!important;box-sizing:border-box!important;min-width:0!important;overflow:hidden!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;padding:11px 12px!important;margin:0!important;border:1px solid #34476D!important;border-radius:12px!important;background:#14213B!important;box-shadow:none!important}
.leader-label{font-family:'DM Sans',sans-serif!important;font-size:clamp(.73rem,.88vw,.88rem)!important;font-weight:800!important;line-height:1.16!important;letter-spacing:0!important;color:#FFFFFF!important;margin:0 0 5px!important;min-height:0!important;white-space:normal!important;overflow-wrap:normal!important}
.leader-name{font-family:'Outfit','DM Sans',sans-serif!important;font-size:clamp(.87rem,1.06vw,1.08rem)!important;font-weight:800!important;line-height:1.13!important;color:#FFFFFF!important;margin:0 0 4px!important;min-height:0!important;max-height:2.26em!important;overflow-wrap:break-word!important;white-space:normal!important}
.leader-score{font-family:'DM Sans',sans-serif!important;font-size:clamp(.82rem,.96vw,1rem)!important;font-weight:800!important;line-height:1.1!important;color:#84D9FF!important;margin:auto 0 5px!important;white-space:nowrap!important}
.leader-score span{font-size:.74rem!important;font-weight:600!important;color:#C9D5EA!important}
.summary-value{font-family:'Outfit','DM Sans',sans-serif!important;font-size:clamp(1.4rem,1.8vw,1.9rem)!important;font-weight:800!important;line-height:1.12!important;color:#84D9FF!important;margin:auto 0 7px!important;white-space:nowrap!important}
.leader-meter{height:5px!important;flex:none!important;width:100%!important;background:#2B3B59!important;border-radius:50px!important;overflow:hidden!important;margin:0 0 1px!important}
.leader-meter-fill{height:100%!important;border-radius:50px!important;background:linear-gradient(90deg,#FF4F9F,#FF94C9)!important}
/* All headings stay white; pink remains an accent for meters and borders. */
h1,h2,h3,h4,.eyebrow,.section-head,.pressure-title,.leader-label,[data-testid='stSidebar'] h3{color:#FFFFFF!important}
@media(max-width:980px){.leader-card{height:120px!important;min-height:120px!important;max-height:120px!important;padding:9px 9px!important}.leader-label{font-size:.72rem!important}.leader-name{font-size:.82rem!important}.leader-score{font-size:.79rem!important}}

/* Tooltip override comes last to defeat the legacy dark tooltip styling. */
[data-baseweb="tooltip"],[role="tooltip"],[data-testid="stTooltipContent"]{background:#FFFFFF!important;color:#101010!important}
[data-baseweb="tooltip"] *,[role="tooltip"] *,[data-testid="stTooltipContent"] *{color:#101010!important}

/* Flat, card-free charts with high-contrast text. Keep KPI cards and tables unchanged. */
[data-testid="stPlotlyChart"],[data-testid="stPlotlyChart"] > div {
  background:transparent!important;border:none!important;border-radius:0!important;
  box-shadow:none!important;padding:0!important;
}
.eyebrow,.eyebrow *,.section-head,.chart-heading .section-head,
.chart-heading .section-caption{color:#FFFFFF!important;opacity:1!important}
[data-testid="stMarkdownContainer"] .eyebrow{color:#FFFFFF!important}
</style>''', unsafe_allow_html=True)

# Controls are in the LEFT sidebar; only Format appears at the top RIGHT.
with st.sidebar:
    st.markdown('### Analysis controls')

    exclude_pak_bang=st.checkbox(
        'Exclude Pakistan & Bangladesh players', value=True,
        help='Exclude Pakistan and Bangladesh players from the shortlist. Matches played against them are still included.'
    )
    threshold=st.slider(
        'Minimum total pressure balls',min_value=50,max_value=300,value=100,step=10,
        help='A player must face at least this many pressure deliveries to qualify. This is a minimum, not a maximum.'
    )
    situation_threshold=st.slider(
        'Minimum balls per pressure situation',min_value=5,max_value=50,value=20,step=5,
        help='Pressure situations below this delivery threshold receive no situation-pressure points. The original six situation-performance scores do not change.'
    )


header_left,header_right=st.columns([4.5,1.5],gap='large',vertical_alignment='bottom')
with header_left:
    # Render the brand heading as SVG: its fill is independent of Streamlit text-theme CSS.
    st.markdown("""<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="25" viewBox="0 0 550 25" role="img" aria-label="RAJASTHAN ROYALS · TALENT INTELLIGENCE" preserveAspectRatio="xMinYMid meet" style="display:block;overflow:visible;margin-bottom:5px"><text x="0" y="17" fill="#FFFFFF" stroke="none" opacity="1" style="fill:#FFFFFF!important;paint-order:normal;font-family:Arial,sans-serif;font-size:13px;font-weight:900;letter-spacing:2px">RAJASTHAN ROYALS · TALENT INTELLIGENCE</text></svg>""", unsafe_allow_html=True)
    st.title('SUPERR SELECTOR')
with header_right:
    fmt=st.selectbox('Format',['IPL + T20Is','IPL','T20Is'],key='competition_top')
cards_slot=st.empty()
main_col=st.container()
try:
    ranked,all_players,raw,hs=calculate(fmt,threshold,exclude_pak_bang=exclude_pak_bang,min_situation_pressure_balls=situation_threshold)
    from bowling_analytics import calculate_bowling_final, SITUATIONS
    bowl_rank,bowl_all,bowl_raw=calculate_bowling_final(fmt,threshold,situation_threshold,exclude_pak_bang=exclude_pak_bang)
except Exception as exc:
    st.error('Could not process the competition datasets.')
    st.exception(exc)
    st.stop()

# The batting calculation writes pressure_flag; never read the bowling pressure column here.
all_delivery_count=len(raw)
pressure_count=int(raw['pressure_flag'].fillna(False).astype(bool).sum()) if 'pressure_flag' in raw.columns else 0
with cards_slot.container():
    card1,card2,card3,card4=st.columns(4,gap='medium')
    def count_card(label, value):
        st.markdown(f'<div class="leader-card summary-card"><div class="leader-label">{html.escape(label)}</div><div class="summary-value">{value:,}</div></div>',unsafe_allow_html=True)
    with card1: count_card('Deliveries Analyzed',all_delivery_count)
    with card2: count_card('Pressure Deliveries',pressure_count)
    def leader_card(title, data):
        if data.empty:
            st.markdown(f'<div class="leader-card"><div class="leader-label">{html.escape(title)}</div><div class="leader-name">No eligible player</div></div>', unsafe_allow_html=True)
            return
        player=html.escape(str(data.iloc[0]['name']))
        score=float(data.iloc[0]['final_score_200'])
        fill=max(0.0,min(100.0,score/200.0*100.0))
        st.markdown(f"""<div class="leader-card">
            <div class="leader-label">{html.escape(title)}</div>
            <div class="leader-name">{player}</div>
            <div class="leader-score">{score:.2f} <span>/ 200</span></div>
            <div class="leader-meter" role="img" aria-label="Rating {score:.2f} out of 200"><div class="leader-meter-fill" style="width:{fill:.2f}%"></div></div>
        </div>""", unsafe_allow_html=True)
    with card3: leader_card('Top Batter',ranked)
    with card4: leader_card('Top Bowler',bowl_rank)

with main_col:
    page=st.radio('Dashboard page',['Batters','Bowlers','Methodology'],horizontal=True,label_visibility='collapsed',key='page_navigation')

def heading(title,sub=None):
    st.markdown(f'<div class="section-head">{html.escape(title)}</div>',unsafe_allow_html=True)
    if sub: st.markdown(f'<div class="section-caption">{html.escape(sub)}</div>',unsafe_allow_html=True)

def rating_bar(score,rank,count):
    pct=float(np.clip(float(score),0,100))
    st.markdown(f'''<div class="rating-card"><div class="rating-top"><span>Rating strength</span><span class="rating-num">{float(score)*2:.2f} / 200</span></div>
        <div class="track"><div class="fill" style="width:{pct:.2f}%"></div></div>
        <div class="fineprint">Rank #{int(rank)} among {int(count):,} eligible batters &nbsp;·&nbsp; {pct:.1f}% of maximum rating</div></div>''',unsafe_allow_html=True)

def pressure_quadrant(data):
    """Compare overall and pressure SR; diagonal indicates no change."""
    q=data[(data['balls']>0)&(data['pressure_balls']>0)].copy()
    if q.empty:
        st.info('No qualified batters available for the pressure quadrant.')
        return
    q=q.head(25).copy()
    q['sr_lift']=q['pressure_sr']-q['normal_sr']
    q['ball_size']=np.sqrt(q['pressure_balls'].clip(lower=1))
    lo=float(min(q['normal_sr'].min(),q['pressure_sr'].min()))
    hi=float(max(q['normal_sr'].max(),q['pressure_sr'].max()))
    pad=max(7.0,(hi-lo)*.13)
    lo=max(0,lo-pad);hi=hi+pad
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=[lo,hi],y=[lo,hi],mode='lines',
        line=dict(color='#D9E1F1',width=1.3,dash='dash'),
        hoverinfo='skip',showlegend=False))
    fig.add_trace(go.Scatter(
        x=q['normal_sr'],y=q['pressure_sr'],mode='markers',
        customdata=np.stack([q['name'],q['pressure_balls'],q['pressure_runs'],q['sr_lift'],q['composite']],axis=-1),
        marker=dict(size=q['ball_size'],sizemode='diameter',sizeref=max(float(q['ball_size'].max()),1)/36,
            sizemin=9,opacity=.88,color=q['sr_lift'],colorscale=[
                [0,'#F15B86'],[.5,'#F8C875'],[1,'#59D7A3']],
            showscale=True,colorbar=dict(title=dict(text='SR lift',font=dict(color=WHITE,size=11)),
                tickfont=dict(color=MUTED),thickness=12,len=.76,outlinewidth=0),
            line=dict(color='#FFFFFF',width=.6)),
        hovertemplate='<b>%{customdata[0]}</b><br>Overall SR: %{x:.2f}<br>Pressure SR: %{y:.2f}'
                      '<br>SR lift: %{customdata[3]:+.2f}<br>Pressure balls: %{customdata[1]:,.0f}'
                      '<br>Pressure runs: %{customdata[2]:,.0f}<br>Combined rating: %{customdata[4]:.1f}/100 (×2 for /200)<extra></extra>',
        showlegend=False))
    fig.update_layout(height=405,template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans',color=WHITE,size=12),margin=dict(l=25,r=20,t=26,b=25),
        xaxis=dict(title='Overall strike rate',range=[lo,hi],gridcolor='#283754',zeroline=False,automargin=True),
        yaxis=dict(title='Pressure strike rate',range=[lo,hi],gridcolor='#283754',zeroline=False,automargin=True,scaleanchor='x',scaleratio=1),
        hoverlabel=dict(bgcolor=PANEL2,font=dict(color=WHITE)))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})



def chart_heading(title, subtitle):
    st.markdown('<div class="chart-heading"><div class="section-head">'+html.escape(title)+'</div><div class="section-caption">'+html.escape(subtitle)+'</div></div>', unsafe_allow_html=True)

def compact_sr_comparison(data):
    q=data.head(10).iloc[::-1].copy()
    if q.empty:return
    fig=go.Figure()
    for field,label,color in [('normal_sr','Overall SR','#7898D1'),('pressure_sr','Pressure SR','#FF67AC')]:
        fig.add_trace(go.Bar(y=q['name'],x=q[field],name=label,orientation='h',marker_color=color,
            hovertemplate='%{y}<br>'+label+': %{x:.2f}<extra></extra>'))
    fig.update_layout(height=405,barmode='group',template='plotly_dark',margin=dict(l=8,r=12,t=40,b=28),
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(family='DM Sans',color=WHITE,size=11),
        xaxis=dict(title='Strike rate',gridcolor='#283754'),
        yaxis=dict(title='',automargin=True,tickfont=dict(size=11),ticklabelstandoff=7),
        legend=dict(orientation='h',y=1.16,x=0))
    st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})

def improvement_indicator(value, suffix='', decimals=2):
    """Display-only sign, directional arrow and accessible color; no scoring effect."""
    try:
        value=float(value)
    except (TypeError, ValueError):
        return '—'
    if not np.isfinite(value):
        return '—'
    css='delta-up' if value>0 else 'delta-down' if value<0 else 'delta-flat'
    arrow='↑' if value>0 else '↓' if value<0 else '→'
    return f'<span class="{css}">{arrow} {value:+.{decimals}f}{html.escape(suffix)}</span>'

def top_ten_table(data):
    rows=[]
    for _,r in data.head(10).iterrows():
        pct=float(np.clip(float(r['composite']),0,100))
        rows.append(f"<tr><td>{int(r['rank'])}</td><td><b>{html.escape(str(r['name']))}</b></td>"
                    f"<td class='number'>{int(r['pressure_balls']):,}</td>"
                    f"<td class='number'>{int(r['pressure_runs']):,}</td>"
                    f"<td class='number'>{float(r['pressure_sr']):.2f}</td>"
                    f"<td class='number'>{float(r['normal_sr']):.2f}</td>"
                    f"<td class='number'>{improvement_indicator(r['improvement_pct'], '%')}</td>"
                    f"<td><div class='score-row'><div class='score-track'><div class='score-fill' style='width:{pct:.2f}%'></div></div>"
                    f"<span class='score-value'>{float(r['composite'])*2:.2f}/200</span></div></td></tr>")
    st.markdown('''<div class="table-wrap"><table class="rr-table"><thead><tr>
        <th>Rank</th><th>Batter</th><th>Pressure balls</th><th>Pressure runs</th>
        <th>Pressure SR</th><th>Overall SR</th><th>SR Improvement</th><th>Final score /200</th>
        </tr></thead><tbody>'''+''.join(rows)+'</tbody></table></div>',unsafe_allow_html=True)

with main_col:
    if page=='Batters':
        if 0 < len(ranked) < 10:
            st.caption(f'{len(ranked)} batters meet the selected format and pressure-ball requirements; no ineligible names are inserted.')
        if ranked.empty:
            st.info('No eligible batters at this setting. Reduce the minimum pressure-ball requirement or change the competition.')
        else:
            heading('Top 10 batters under pressure')
            top_ten_table(ranked)
            chart_left,chart_right=st.columns(2,gap='large')
            with chart_left:
                chart_heading('Strike-rate comparison','Overall vs pressure SR · Top 10')
                compact_sr_comparison(ranked)
            with chart_right:
                chart_heading('Pressure quadrant','Bubble size = pressure balls')
                pressure_quadrant(ranked.head(10))
            st.divider()
            heading('Batter spotlight','Select a ranked batter to view the same core performance metrics.')
            ids=ranked['player_id'].astype(int).tolist()
            labels={int(r.player_id):f"#{int(r['rank'])}  ·  {r['name']}" for _,r in ranked.iterrows()}
            chosen=st.selectbox('Choose a batter',ids,format_func=lambda x:labels.get(x,str(x)))
            r=ranked.set_index('player_id').loc[chosen]
            m1,m2,m3,m4=st.columns(4,gap='medium')
            m1.metric('Final score /200',f'{r.final_score_200:.2f} / 200')
            m2.metric('Pressure SR',f'{r.pressure_sr:.2f}')
            m3.metric('Pressure boundary %',f'{r.pressure_boundary_pct:.2f}%')
            m4.metric('SR Improvement',f'{r.improvement_pct:+.2f}%')
            rating_bar(r.composite,r['rank'],len(ranked))
    elif page=='Methodology':
        heading('How the rankings are built')
        pressure_cards=[
          ('01','Difficult chase','Second innings from over 7: required run rate ≥ 9 and above current run rate.'),
          ('02','Early collapse','Three or more wickets already lost in the first 10 overs.'),
          ('03','Death overs','Overs 16–20 in either innings.'),
          ('04','Knockout matches','Finals, qualifiers, eliminators and semi-finals.'),
        ]
        left,right=st.columns([1.05,1],gap='large')
        with left:
            st.markdown('### When a batting delivery counts as pressure')
            for num,title,detail in pressure_cards:
                st.markdown(f'<div class="pressure-card"><div class="pressure-number">{num}</div><div class="pressure-title">{html.escape(title)}</div><div class="pressure-detail">{html.escape(detail)}</div></div>',unsafe_allow_html=True)
        with right:
            st.markdown('### Where pressure deliveries occur')
            categories=[('Difficult chase','pressure_chase','#F45CA9'),('Early collapse','pressure_collapse','#FFB45C'),('Death overs','pressure_death','#68A7FF'),('Knockouts','pressure_knockout','#AA8BFF')]
            if all(key in raw.columns for _,key,_ in categories):
                labels=[name for name,_,_ in categories]+['Normal deliveries']
                values=[int(raw[key].fillna(False).astype(bool).sum()) for _,key,_ in categories]
                values.append(int((~raw['pressure_flag'].fillna(False).astype(bool)).sum()))
                fig=go.Figure(go.Bar(x=values,y=labels,orientation='h',marker_color=[c for _,_,c in categories]+['#61728F'],text=[f'{n:,}' for n in values],textposition='auto'))
                fig.update_layout(height=410,template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color=WHITE,size=11),margin=dict(l=5,r=10,t=20,b=30),xaxis=dict(title='Deliveries',gridcolor='#283754'),yaxis=dict(autorange='reversed',automargin=True))
                st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
            st.caption('Overlapping conditions count as one pressure delivery in the final total.')
        st.divider()
        st.markdown('### How points are combined')
        st.caption('Green ↑ means improvement; red ↓ means a decline. These indicators display existing metrics and do not add points.')
        bat_col,bowl_col=st.columns(2,gap='large')
        with bat_col:
            st.markdown('**Batters**')
            st.markdown('The six original batting situations use every ball faced, with the same strike-rate bands and weights as the V2 workbook. Separately, pressure performance is assessed by situation and overall (60/40).')
        with bowl_col:
            st.markdown('**Bowlers**')
            st.markdown('Bowling situation points follow the final economy-percentile workbook. For bowlers defending a target, **CRR > RRR** marks pressure; the analysis compares economy rates in those deliveries and across the chase.')
        st.latex(r'\mathrm{Final}_{/200}=2\left(0.70\times\mathrm{V2}_{/100}+0.30\times\mathrm{Pressure}_{/100}\right)')
        st.markdown('### Minimum sample and source coverage')
        st.markdown('At least **9 matches** and the selected pressure-ball minimum. The situation slider controls pressure-situation scoring, not the original V2 points. Combined bowling uses the final Excel workbooks and their excluded-chase audit; IPL-only and T20I-only views recalculate from deliveries.')
        st.caption('Run-rate estimates and auction eligibility require independent checks. The 70/30 combination is a scouting model, not a validated prediction.')
    elif page=='Bowlers':
        if bowl_rank.empty:
            st.warning('No bowlers meet the selected pressure-ball and match thresholds. Lower the minimum pressure balls or change the competition.')
        else:
            heading('Top 10 bowlers under pressure')
            top=bowl_rank.head(10).copy()
            top['Bowler']=top['name']
            top['Final /200']=top.final_score_200.round(2)
            top['V2 /180']=top.v2_points.round(2)
            top['Pressure /100']=top.pressure_rating.round(2)
            top['Economy']=top.economy.round(2)
            top['Pressure economy']=top.pressure_economy.round(2)
            # Exact visible column names, as requested; no truncated anonymous header row.
            top['Base Econ']=top['chase_economy'].round(2)
            top['Press. Econ']=top['Pressure economy']
            top['Economy Improvement (%)']=((top['chase_economy']-top['pressure_economy']) / top['chase_economy'].where(top['chase_economy'] > 0) * 100).round(2)
            top['Press. Balls']=top['pressure_balls'].astype(int)
            top['Wickets']=top['wickets'].astype(int)
            top['Pressure Rating']=top['Final /200']
            # Dot-ball rate is a DISPLAY-ONLY diagnostic, never an input to final_score_200.
            # For combined Excel rankings, the Excel has no per-delivery dot flags.
            # Compute these separately from the original deliveries using the same
            # defending-pressure direction (2nd innings, CRR > RRR), excluding audited
            # chases; do not pretend they are a workbook-derived measure.
            from bowling_analytics import calculate_pressure_dot_percent
            dots_by_id=calculate_pressure_dot_percent(fmt)
            top['Dot %']=top.index.map(dots_by_id)
            top['Dot %']=top['Dot %'].map(lambda x:f'{x:.1f}%' if pd.notna(x) else '—')
            # Native HTML table: explicit headers remain visible rather than getting clipped by the grid canvas.
            bowler_rows=[]
            for _,r in top.iterrows():
                cells=[html.escape(str(r['Bowler'])),f"{int(r['Press. Balls']):,}",
                       f"{r['Press. Econ']:.2f}" if pd.notna(r['Press. Econ']) else '—',
                       f"{r['Base Econ']:.2f}" if pd.notna(r['Base Econ']) else '—',
                       f"<span style='color:{'#53D6A0' if r['Economy Improvement (%)'] > 0 else '#E7EDF8'}'>{r['Economy Improvement (%)']:+.2f}%</span>" if pd.notna(r['Economy Improvement (%)']) else '—',
                       str(r['Dot %']),f"{int(r['Wickets']):,}",f"{r['Pressure Rating']:.2f}"]
                bowler_rows.append('<tr>'+''.join(f'<td>{cell}</td>' if i==4 else f'<td>{html.escape(str(cell))}</td>' for i,cell in enumerate(cells))+'</tr>')
            headers=['Bowler','Pressure Balls','Pressure Economy','Chase Economy','Economy Improvement (%)','Pressure Dot-Ball %','Total Wickets','Final Rating /200']
            st.markdown('<div class="table-wrap"><table class="rr-table"><thead><tr>'+''.join(f'<th>{html.escape(h)}</th>' for h in headers)+'</tr></thead><tbody>'+''.join(bowler_rows)+'</tbody></table></div>',unsafe_allow_html=True)
            st.caption('Economy Improvement (%) = (Chase Economy − Pressure Economy) / Chase Economy × 100. Positive means fewer runs conceded per over under pressure; negative means more. Only positive improvement earns improvement credit in Pressure Reliability. No arrows are used. Pressure Dot-Ball % is display-only and does not affect the rating.')
            import plotly.express as px
            left_chart,right_chart=st.columns(2,gap='large')
            with left_chart:
                chart_heading('Bowling score comparison','Final pressure rating /200 · Top 10')
                fig=px.bar(top.sort_values('Final /200'),x='Final /200',y='Bowler',orientation='h',color='Pressure /100',color_continuous_scale=['#4667A4','#FF5FA9'])
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#F6F8FF',height=405,margin=dict(l=10,r=15,t=35,b=30))
                st.plotly_chart(fig,use_container_width=True)
            with right_chart:
                chart_heading('Bowling performance bubble graph','Bubble size = pressure balls · lower economy is better')
                bubble=px.scatter(top,x='Base Econ',y='Press. Econ',size='Press. Balls',color='Final /200',hover_name='Bowler',
                    color_continuous_scale=['#4667A4','#FF5FA9'],size_max=45)
                bubble.update_layout(paper_bgcolor='#101B35',plot_bgcolor='#101B35',font_color='#F6F8FF',height=405,
                    margin=dict(l=10,r=15,t=35,b=30),xaxis_title='Chase economy',yaxis_title='Pressure economy')
                st.plotly_chart(bubble,use_container_width=True)
            heading('Bowler spotlight')
            selected=st.selectbox('Choose bowler',bowl_rank.index.tolist(),format_func=lambda pid:f"#{int(bowl_rank.loc[pid,'rank'])} · {bowl_rank.loc[pid,'name']}")
            b=bowl_rank.loc[selected]
            q1,q2,q3,q4=st.columns(4)
            q1.metric('Final /200',f'{b.final_score_200:.2f}')
            q2.metric('Pressure economy',f'{b.pressure_economy:.2f}')
            q3.metric('Pressure wickets',int(b.pressure_wickets))
            q4.metric('Pressure balls',int(b.pressure_balls))
            st.caption('Bowling pressure follows your final Excel: second innings only, pre-delivery CRR > RRR. Combined-format V2 and pressure figures are imported from the final workbooks; format-specific views are recalculated from deliveries. The excluded-chase audit is bundled.')
