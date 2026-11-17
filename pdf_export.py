"""Generate a multi-page PDF of the current dashboard rankings and methodology."""
from io import BytesIO
import math
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

W,H=1000,720
BG=HexColor('#080F25')
PANEL=HexColor('#142241')
WHITE=HexColor('#F6F8FF')
MUTED=HexColor('#A7B6D4')
PINK=HexColor('#FF5FA9')
BLUE=HexColor('#84D9FF')

def export_dashboard_pdf(batters, bowlers, fmt, pressure_min, situation_min, deliveries, batting_pressure):
    buf=BytesIO()
    c=canvas.Canvas(buf,pagesize=(W,H))
    def text(x,y,s,size=12,color=WHITE,bold=False):
        c.setFillColor(color)
        c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
        c.drawString(x,y,str(s).encode('latin-1','replace').decode('latin-1'))
    def box(x,y,w,h):
        c.setFillColor(PANEL)
        c.roundRect(x,y,w,h,12,stroke=0,fill=1)
    def base(section):
        c.setFillColor(BG)
        c.rect(0,0,W,H,stroke=0,fill=1)
        text(35,670,'Superr Selector',27,WHITE,True)
        text(35,644,section,15,PINK,True)
        text(35,619,f'Format: {fmt}    Minimum pressure balls: {pressure_min}    Per situation: {situation_min}',11,MUTED)
        text(35,32,'Source: original competition CSV deliveries | Scoring: 40% situation + 60% pressure',10,MUTED)
    def fmt_num(value,digits=1):
        try:
            v=float(value)
            return f'{v:,.{digits}f}' if math.isfinite(v) else '-'
        except (TypeError,ValueError):
            return '-'
    def rankings(df,kind):
        base(kind+' dashboard')
        box(35,514,450,78)
        text(52,568,'DELIVERIES ANALYSED',11,MUTED,True)
        text(52,534,f'{deliveries:,}',24,BLUE,True)
        box(504,514,460,78)
        text(522,568,'BATTING PRESSURE BALLS',11,MUTED,True)
        text(522,534,f'{batting_pressure:,}',24,BLUE,True)
        text(35,475,'Top 10 rankings',19,WHITE,True)
        headers=['#','Player','Pressure balls','Pressure metric','Final /200']
        positions=[49,90,430,612,818]
        for x,h in zip(positions,headers):text(x,442,h,11,PINK,True)
        c.setStrokeColor(HexColor('#34446D'));c.line(40,429,957,429)
        top=df.head(10)
        for i,(_,r) in enumerate(top.iterrows()):
            y=400-i*31
            if i%2==0:box(38,y-9,921,29)
            text(49,y,i+1,11,WHITE,True)
            text(90,y,str(r.get('name',''))[:37],12,WHITE,i<3)
            text(430,y,fmt_num(r.get('pressure_balls',0),0),12,BLUE)
            metric=r.get('pressure_sr') if kind=='Batting' else r.get('pressure_economy')
            text(612,y,fmt_num(metric,2),12,WHITE)
            score=r.get('final_score_200')
            text(818,y,fmt_num(score,2),12,PINK,True)
        text(38,67,'Pressure metric: strike rate' if kind=='Batting' else 'Pressure metric: economy rate',10,MUTED)
        c.showPage()
    rankings(batters,'Batting')
    rankings(bowlers,'Bowling')
    base('Methodology and analysis settings')
    box(35,380,930,206)
    text(55,550,'Ranking approach',19,WHITE,True)
    text(55,513,'1. Situation performance: six innings-phase and innings-context scenarios.',14,WHITE)
    text(55,480,'2. Pressure performance: delivery-level pressure conditions and performance.',14,WHITE)
    text(55,447,'3. Reliability: minimum sample sizes and pressure-exposure adjustment.',14,WHITE)
    text(55,412,'Final score /200 = 2 x (0.40 x situation score + 0.60 x pressure score)',13,BLUE,True)
    text(35,337,'Format selection, retirement/nationality filters, and both sliders are reflected',13,MUTED)
    text(35,314,'in the exported rankings. The PDF is a static report, not an interactive app.',13,MUTED)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()
