"""Bowling from latest user ball-by-ball only; workbook-inspired economy percentile and defending-pressure method."""
from pathlib import Path
import numpy as np
import pandas as pd
from analytics import load,formats,exclusions,unreliable_chase_ids

SITUATIONS={'PP · Bowling first':2,'Middle · Bowling first':2,'Death · Bowling first':2,
            'PP · Defending':4,'Middle · Defending':4,'Death · Defending':4}
DATA=Path(__file__).parent/'data'

def _score_percentiles(df,balls_col='balls',runs_col='conceded',min_balls=12):
    valid=df[balls_col]>=min_balls
    eco=6*df[runs_col]/df[balls_col].replace(0,np.nan)
    # Lower economy is better; 10 points is top percentile, no observed balls = 0.
    result=pd.Series(0.0,index=df.index)
    if valid.any():
        result.loc[valid]=eco.loc[valid].rank(ascending=False,pct=True,method='average')*10
    return result

def calculate_bowling(choice='IPL + T20Is',min_pressure_balls=100,min_situation_pressure_balls=20,min_matches=9,exclude_pak_bang=True):
    d,m,c,mapping,eleven,teams=load()
    d=formats(d,choice)
    if d.empty:return pd.DataFrame(),pd.DataFrame(),d
    d=d[d.innings.isin([1,2])].copy()
    d=d.sort_values(['match_id','innings','innings_ball_num'],kind='stable')
    ex=d.extras_type.fillna('').astype(str).str.lower()
    d['legal']=(~ex.isin(['wide','overstep'])).astype(int)
    d['ex1']=pd.to_numeric(d.extras1_runs,errors='coerce').fillna(0).clip(lower=0)
    d['ex2']=pd.to_numeric(d.extras_2_runs,errors='coerce').fillna(0).clip(lower=0)
    d['team_runs']=pd.to_numeric(d.runs,errors='coerce').fillna(0).clip(lower=0)+d.ex1+d.ex2
    # Bowler charge: bat runs + wides and no-ball penalties, excluding byes/leg-byes/penalties.
    # Any 'other' extra is not assumed to be bowler charged without an explicit classification.
    d['bowler_conceded']=pd.to_numeric(d.runs,errors='coerce').fillna(0).clip(lower=0)+np.where(ex.isin(['wide','overstep']),d.ex1+d.ex2,0)
    dismiss=d.dismissal_type.fillna('').astype(str).str.lower().str.replace(' ','',regex=False).str.replace('_','',regex=False)
    not_bowler=['runout','retiredhurt','retiredout','obstructingthefield','hitwicket?','timedout']
    # Hit wicket is bowler credited; exclude only non-bowler dismissals.
    not_bowler.remove('hitwicket?')
    d['bowler_wicket']=d.is_wicket.astype(str).str.lower().eq('true') & ~dismiss.isin(not_bowler)
    grp=d.groupby(['match_id','innings'],sort=False)
    d['runs_before']=grp.team_runs.cumsum()-d.team_runs
    d['legal_before']=grp.legal.cumsum()-d.legal
    d['crr']=np.where(d.legal_before>0,6*d.runs_before/d.legal_before,np.nan)
    first=d[d.innings.eq(1)].groupby('match_id').team_runs.sum()
    d['target']=d.match_id.map(first)+1
    mm=m[['match_id','revised_target','second_inn_revised_overs']].drop_duplicates('match_id')
    d=d.merge(mm,on='match_id',how='left',validate='many_to_one')
    revised=pd.to_numeric(d.revised_target,errors='coerce')
    d['target']=revised.where(revised>0,d.target)
    allowed=pd.to_numeric(d.second_inn_revised_overs,errors='coerce').fillna(120)
    remaining=allowed-d.legal_before
    need=d.target-d.runs_before
    d['rrr']=np.where(d.innings.eq(2)&(remaining>0)&(need>0),6*need/remaining,np.nan)
    # Exact workbook direction: defending side pressured when chasing side CRR > RRR.
    d['pressure']=(~d.match_id.isin(unreliable_chase_ids()))&d.innings.eq(2)&d.crr.notna()&d.rrr.notna()&(d.crr>d.rrr)
    d['phase']=np.select([d.overid.between(1,6),d.overid.between(7,15),d.overid.between(16,20)],['PP','Middle','Death'],default='Other')
    d['situation']=d.phase+' · '+np.where(d.innings.eq(1),'Bowling first','Defending')
    d=d[d.situation.isin(SITUATIONS)].copy()
    names=d.groupby('bowler_id').bowler_name.agg(lambda s:s.mode().iat[0] if not s.mode().empty else s.iloc[0])
    overall=d.groupby('bowler_id').agg(matches=('match_id','nunique'),balls=('legal','sum'),conceded=('bowler_conceded','sum'),wickets=('bowler_wicket','sum'))
    overall['name']=names
    overall['economy']=np.where(overall.balls>0,6*overall.conceded/overall.balls,np.nan)
    overall['strike_rate']=np.where(overall.wickets>0,overall.balls/overall.wickets,np.nan)
    ps=d[d.pressure].groupby('bowler_id').agg(pressure_balls=('legal','sum'),pressure_conceded=('bowler_conceded','sum'),pressure_wickets=('bowler_wicket','sum'))
    t=overall.join(ps,how='left')
    for k in ['pressure_balls','pressure_conceded','pressure_wickets']:t[k]=t[k].fillna(0)
    t['pressure_economy']=np.where(t.pressure_balls>0,6*t.pressure_conceded/t.pressure_balls,np.nan)
    t['pressure_strike_rate']=np.where(t.pressure_wickets>0,t.pressure_balls/t.pressure_wickets,np.nan)
    t['eligible']=(t.matches>=min_matches)&(t.pressure_balls>=min_pressure_balls)&(t.balls>0)
    pak=set(mapping.loc[mapping.team_name.fillna('').str.match(r'^Pakistan(?: A| Shaheens)?$',case=False),'player_id'])
    bang=set(mapping.loc[mapping.team_name.fillna('').str.match(r'^Bangladesh(?: A| Emerging)?$',case=False),'player_id'])
    t['excluded']=t.name.str.casefold().isin(exclusions()) | (t.index.isin(pak|bang) if exclude_pak_bang else False)
    pool=t.index[t.eligible&~t.excluded]
    # Six original economy percentile situations; separate for bowling first and defending.
    for sit,weight in SITUATIONS.items():
        chunk=d[d.situation.eq(sit)].groupby('bowler_id').agg(balls=('legal','sum'),conceded=('bowler_conceded','sum'))
        a=chunk.reindex(t.index).fillna(0)
        t[f'{sit} balls']=a.balls
        t[f'{sit} economy']=np.where(a.balls>0,6*a.conceded/a.balls,np.nan)
        p=_score_percentiles(a.loc[pool],min_balls=12)
        t[f'{sit} points']=0.0
        t.loc[p.index,f'{sit} points']=p
        pressure_chunk=d[d.pressure&d.situation.eq(sit)].groupby('bowler_id').agg(balls=('legal','sum'),conceded=('bowler_conceded','sum'))
        pa=pressure_chunk.reindex(t.index).fillna(0)
        t[f'{sit} pressure balls']=pa.balls
        t[f'{sit} pressure economy']=np.where(pa.balls>0,6*pa.conceded/pa.balls,np.nan)
        pp=_score_percentiles(pa.loc[pool],min_balls=min_situation_pressure_balls)
        t[f'{sit} pressure points']=0.0
        t.loc[pp.index,f'{sit} pressure points']=pp
    t['v2_points']=sum(t[f'{sit} points']*weight for sit,weight in SITUATIONS.items())
    t['pressure_six_points']=sum(t[f'{sit} pressure points']*weight for sit,weight in SITUATIONS.items())
    t['v2_normalized']=100*t.v2_points/180
    t['pressure_six_normalized']=100*t.pressure_six_points/120  # pressure workbook covers defending innings only; maximum weighted pressure points = 3 phases × 4 × 10
    # Compare pressure economy against a chase-only baseline, matching workbook scope.
    chase=d[d.innings.eq(2)].groupby('bowler_id').agg(chase_balls=('legal','sum'),chase_runs=('bowler_conceded','sum'))
    t=t.join(chase,how='left')
    t['chase_economy']=6*t.chase_runs/t.chase_balls.replace(0,np.nan)
    t['economy_improvement_pct']=100*(t.chase_economy-t.pressure_economy)/t.chase_economy.replace(0,np.nan)
    t['overall_pressure_rating']=np.nan
    if len(pool):
        # Low economy and high improvement both better; 50/50, confidence shrinkage.
        eco=t.loc[pool,'pressure_economy'].rank(ascending=False,pct=True,method='average')*100
        # Improvement credit is earned only for a genuine reduction in economy.
        # Rank positive improvements against other positive improvements; all
        # non-positive or unavailable improvements receive zero credit.
        improvements=t.loc[pool,'economy_improvement_pct']
        lift=pd.Series(0.0,index=pool)
        positive=improvements.notna() & improvements.gt(0)
        if positive.any():
            lift.loc[improvements.index[positive]]=improvements.loc[positive].rank(ascending=True,pct=True,method='average')*100
        raw=(eco+lift)/2
        confidence=t.loc[pool,'pressure_balls']/(t.loc[pool,'pressure_balls']+60)
        t.loc[pool,'overall_pressure_rating']=50+confidence*(raw-50)
    t['pressure_rating']=.60*t.pressure_six_normalized+.40*t.overall_pressure_rating
    t['final_score_200']=2*(.50*t.v2_normalized+.50*t.pressure_rating)
    ranked=t.loc[pool].sort_values(['final_score_200','pressure_balls','name'],ascending=[False,False,True]).copy()
    ranked.insert(0,'rank',range(1,len(ranked)+1))
    return ranked,t,d

# Excel was a methodology reference only. All ranking inputs come from the six raw CSVs.
def calculate_bowling_final(choice='IPL + T20Is',min_pressure_balls=100,min_situation_pressure_balls=20,min_matches=9,exclude_pak_bang=True):
    return calculate_bowling(choice,min_pressure_balls,min_situation_pressure_balls,min_matches,exclude_pak_bang)


def calculate_pressure_dot_percent(choice='IPL + T20Is'):
    """Display-only pressure dot percentage; never used in ranking arithmetic.

    Dot = legal delivery with zero runs charged to the bowler (byes/leg-byes
    do not count against bowler). Pressure = 2nd innings, pre-ball CRR > RRR.
    Uses the same selective chase exclusions as the CSV-derived rankings.
    """
    import pandas as pd
    import numpy as np
    try:
        _, players, deliveries=calculate_bowling(choice, min_pressure_balls=1,
            min_situation_pressure_balls=1,min_matches=1,exclude_pak_bang=False)
        if deliveries.empty:return pd.Series(dtype=float)
        legal_pressure=deliveries.loc[deliveries['pressure'].fillna(False).astype(bool)&deliveries['legal'].eq(1)]
        if legal_pressure.empty:return pd.Series(dtype=float)
        result=legal_pressure.groupby('bowler_id')['bowler_conceded'].agg(
            lambda runs:100.0*float(runs.eq(0).sum())/len(runs))
        return result
    except (KeyError,ValueError,TypeError,FileNotFoundError):
        return pd.Series(dtype=float)
