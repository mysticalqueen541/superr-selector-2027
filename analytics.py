"""SUPERR SELECTOR calculations. Pressure flags use only original ball_by_ball.csv and match metadata."""
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent / 'data'
REF = Path(__file__).resolve().parent / 'reference' / 'rr'
MIN_SITUATION_PRESSURE_BALLS = 20
WEIGHTS = {'PP · Setting':2, 'PP · Chasing':4, 'Middle · Setting':1,
           'Middle · Chasing':2, 'Death · Setting':3, 'Death · Chasing':6}
# Exclusions are sourced exclusively from data/exclusions.csv.
# Retirement exclusion requires BOTH retired_t20i AND retired_ipl.
# This review is dated 2026-11-14; future IPL 2027 auction status is not yet confirmed.

@__import__('streamlit').cache_data(show_spinner=False)
def load():
    d = pd.read_csv(DATA/'ball_by_ball.csv', low_memory=False)
    m = pd.read_csv(DATA/'matches.csv')
    c = pd.read_csv(DATA/'competitions.csv')
    mapping = pd.read_csv(DATA/'competition_team_player_mapping.csv')
    eleven = pd.read_csv(DATA/'playing_eleven.csv')
    teams = pd.read_csv(DATA/'teams.csv')
    for frame in (d,):
        frame['runs'] = pd.to_numeric(frame['runs'],errors='coerce').fillna(0)
        frame['striker_id'] = pd.to_numeric(frame['striker_id'],errors='coerce')
        frame['legal_bat_ball'] = ~frame['extras_type'].fillna('').astype(str).str.lower().eq('wide')
        frame['bat_runs'] = frame['runs'].where(frame['legal_bat_ball'],0)
        frame['bat_ball'] = frame['legal_bat_ball'].astype(int)
        frame['boundary_runs'] = np.where(frame['is_four'].astype(str).str.lower().eq('true'),4,
                                    np.where(frame['is_six'].astype(str).str.lower().eq('true'),6,0))
        frame['boundary'] = (frame['boundary_runs']>0).astype(int)
    meta = m[['match_id','comp_id']].drop_duplicates('match_id').merge(
        c[['comp_id','comp_name','match_format']],on='comp_id',how='left')
    d=d.merge(meta,on='match_id',how='left',validate='many_to_one')
    return d,m,c,mapping,eleven,teams

def formats(df,choice):
    ipl = df['comp_name'].fillna('').str.match(r'^IPL\s+20\d\d$',case=False)
    intl = df['match_format'].fillna('').eq('T20I')
    if choice=='IPL': return df[ipl].copy()
    if choice=='T20Is': return df[intl].copy()
    return df[ipl|intl].copy()

def score_band(sr):
    if pd.isna(sr): return 0  # No deliveries faced in this situation: no points
    if sr < 101:return 1
    if sr < 121:return 4
    if sr < 141:return 6
    if sr < 161:return 8
    if sr < 181:return 9
    return 10

def bonus_band(ratio):
    # Sheet3 of V2 workbook: 0.001→1, .11→4, .21→8, .41→12, .61→20.
    # Continuous thresholds avoid Excel VLOOKUP's unscored rounding gaps.
    if not np.isfinite(ratio) or ratio<0.001:return 0
    if ratio<0.11:return 1
    if ratio<0.21:return 4
    if ratio<0.41:return 8
    if ratio<0.61:return 12
    return 20

def exclusions():
    p=DATA/'exclusions.csv'
    if p.exists():
        e=pd.read_csv(p)
        # Enforce both retirement flags in code; do not trust a manually edited 'exclude' cell.
        t20=e['retired_t20i'].astype(str).str.lower().isin(['true','1','yes'])
        ipl=e['retired_ipl'].astype(str).str.lower().isin(['true','1','yes'])
        return set(e.loc[t20 & ipl,'player_name'].astype(str).str.casefold())
    return set()

def calculate(choice='IPL + T20Is', min_pressure_balls=100, min_matches=9, exclude_pak_bang=True, min_situation_pressure_balls=20):
    d,m,c,mapping,eleven,teams=load()
    d=formats(d,choice)
    # Eligible names are keyed by ID, not names (names can be ambiguous).
    if d.empty:return pd.DataFrame(),pd.DataFrame(),d,None
    names=d.groupby('striker_id')['striker_name'].agg(lambda s:s.mode().iat[0] if not s.mode().empty else s.iloc[0])
    overall=d.groupby('striker_id').agg(runs=('bat_runs','sum'),balls=('bat_ball','sum'),
      boundaries=('boundary','sum'), boundary_runs=('boundary_runs','sum'),
      matches=('match_id','nunique'))
    overall['normal_sr']=np.where(overall.balls>0,overall.runs/overall.balls*100,0)
    overall['boundary_pct']=np.where(overall.balls>0,overall.boundaries/overall.balls*100,0)
    overall['name']=names
    d['phase']=np.select([d.overid.between(1,6),d.overid.between(7,15),d.overid.between(16,20)],
                         ['PP','Middle','Death'],default='Other')
    d['context']=np.where(d.innings.isin([1,3]),'Setting','Chasing')
    d['situation']=d.phase+' · '+d.context
    phases=d[d.situation.isin(WEIGHTS)].groupby(['striker_id','situation']).agg(
        r=('bat_runs','sum'),b=('bat_ball','sum'))
    all_situation_sr=phases.assign(sr=lambda t:np.where(t.b>0,t.r/t.b*100,np.nan))['sr'].unstack()
    all_situation_sr=all_situation_sr.rename(columns={col:col+' all-ball SR' for col in all_situation_sr.columns})
    # Reconstruct PRE-DELIVERY match state from the UPDATED uploaded ball-by-ball CSV.
    # In this new CSV extras1_runs and extras_2_runs are numeric run amounts,
    # unlike the old file where extras1_runs held a categorical code.
    # Chase pressure is estimated from batter runs plus recorded extras.
    d=d.sort_values(['match_id','innings','innings_ball_num'],kind='stable').copy()
    ex=d['extras_type'].fillna('').astype(str).str.lower()
    d['legal_delivery']=(~ex.isin(['wide','overstep'])).astype(int)
    # All recorded extras contribute to innings totals; batter runs remain separate
    # for batting SR and pressure SR. Never award byes/wides to the batter.
    d['extras1_numeric']=pd.to_numeric(d['extras1_runs'],errors='coerce').fillna(0).clip(lower=0)
    d['extras2_numeric']=pd.to_numeric(d['extras_2_runs'],errors='coerce').fillna(0).clip(lower=0)
    d['estimated_team_runs']=d['runs'].clip(lower=0)+d['extras1_numeric']+d['extras2_numeric']
    grp=d.groupby(['match_id','innings'],sort=False)
    d['runs_before']=grp['estimated_team_runs'].cumsum()-d['estimated_team_runs']
    d['legal_before']=grp['legal_delivery'].cumsum()-d['legal_delivery']
    d['wickets_before']=grp['is_wicket'].transform(lambda x:x.astype(str).str.lower().eq('true').cumsum())-d['is_wicket'].astype(str).str.lower().eq('true').astype(int)
    d['crr_est']=np.where(d.legal_before>0,6*d.runs_before/d.legal_before,np.nan)
    first=d[d.innings==1].groupby('match_id')['estimated_team_runs'].sum()
    d['target_est']=d.match_id.map(first)+1
    matchinfo=m[['match_id','revised_target','second_inn_revised_overs','knock_out','stage']].drop_duplicates('match_id')
    d=d.merge(matchinfo,on='match_id',how='left',validate='many_to_one')
    d['target_est']=pd.to_numeric(d.revised_target,errors='coerce').where(pd.to_numeric(d.revised_target,errors='coerce')>0).fillna(d.target_est)
    # The match metadata stores revised overs as BALL COUNTS (e.g. 90 = 15 overs), not overs.
    allotted=pd.to_numeric(d.second_inn_revised_overs,errors='coerce').fillna(120)
    remain=allotted-d.legal_before
    need=d.target_est-d.runs_before
    d['rrr_est']=np.where((remain>0)&(need>0)&d.innings.eq(2),6*need/remain,np.nan)
    # Pressure is defined solely from original ball-by-ball and match metadata.
    d['is_knockout']=d.knock_out.astype(str).str.lower().isin(['1','true','yes']) | d.stage.fillna('').str.contains('final|qualifier|eliminator|semi',case=False,regex=True)
    # Chase rate must exceed current rate and reach at least 9.0.
    chase_pressure=(d.innings.eq(2)&d.overid.ge(7)&d.rrr_est.ge(9.0)&(d.rrr_est>d.crr_est))
    collapse=(d.overid.le(10)&d.wickets_before.ge(3))
    death=(d.overid.ge(16))
    d['pressure_flag']=chase_pressure | collapse | death | d.is_knockout
    d['pressure_chase']=chase_pressure
    d['pressure_collapse']=collapse
    d['pressure_death']=death
    d['pressure_knockout']=d.is_knockout
    # Average Entry Pressure Gap: one observation per batter/chase innings.
    # Missing/undefined entries are excluded, never filled with zero.
    chase_entries=d[d.innings.isin([2,4]) & d.legal_bat_ball].copy()
    chase_entries=chase_entries.sort_values(['match_id','innings','innings_ball_num'],kind='stable')
    chase_entries=chase_entries.drop_duplicates(['striker_id','match_id','innings'],keep='first')
    chase_entries['entry_gap']=chase_entries['rrr_est']-chase_entries['crr_est']
    entry_gap=chase_entries.groupby('striker_id').agg(entry_gap=('entry_gap','mean'),valid_entries=('entry_gap','count'))
    # Pressure deliveries remain a subset of the same original six V2 situations.
    # Group by player and situation to expose the actual pressure balls faced in each.
    pressure_situations=(d[d.pressure_flag & d.legal_bat_ball & d.situation.isin(WEIGHTS)]
        .groupby(['striker_id','situation']).agg(pressure_balls=('bat_ball','sum'),pressure_runs=('bat_runs','sum')))
    ps_balls=pressure_situations['pressure_balls'].unstack().reindex(columns=list(WEIGHTS),fill_value=0).fillna(0)
    ps_runs=pressure_situations['pressure_runs'].unstack().reindex(columns=list(WEIGHTS),fill_value=0).fillna(0)
    # Pressure situation SR is for diagnostics only; six V2 score inputs use all deliveries.
    # No situation with zero batter-faced balls receives any points.
    pressure_situation_sr=(pressure_situations.assign(pressure_sr=lambda t:np.where(
        t.pressure_balls>0,100*t.pressure_runs/t.pressure_balls,np.nan))['pressure_sr']
        .unstack().reindex(columns=list(WEIGHTS)))
    ps_balls.columns=[f'{col} pressure balls' for col in ps_balls.columns]
    ps_runs.columns=[f'{col} pressure runs' for col in ps_runs.columns]
    pressure_deliveries=d[d.pressure_flag & d.legal_bat_ball].copy()
    pressure=pressure_deliveries.groupby('striker_id').agg(
        pressure_runs=('bat_runs','sum'), pressure_balls=('bat_ball','sum'),
        pressure_boundaries=('boundary','sum'),pressure_boundary_runs=('boundary_runs','sum'))
    pressure['pressure_sr']=np.where(pressure.pressure_balls>0,pressure.pressure_runs/pressure.pressure_balls*100,0)
    pressure['pressure_boundary_pct']=np.where(pressure.pressure_balls>0,pressure.pressure_boundaries/pressure.pressure_balls*100,0)
    t=overall.join(pressure,how='left').join(pressure_situation_sr,how='left').join(all_situation_sr,how='left').join(entry_gap,how='left').join(ps_balls,how='left').join(ps_runs,how='left')
    t[list(ps_balls.columns)+list(ps_runs.columns)]=t[list(ps_balls.columns)+list(ps_runs.columns)].fillna(0)
    for col in [*pressure.columns]:
        t[col]=t[col].fillna(0)
    t['improvement_pct']=np.where(t.normal_sr>0,(t.pressure_sr/t.normal_sr-1)*100,0)
    t['improvement_ratio']=t.improvement_pct/100
    for col,weight in WEIGHTS.items():
        # All-ball situation SR, identical to original V2 batting method.
        # A situation with zero balls receives zero, not minimum 1 point.
        normal_col=f'{col} all-ball SR'
        if normal_col not in t: t[normal_col]=np.nan
        t[col+' points']=t[normal_col].apply(score_band)
    t['phase_score']=sum(t[col+' points']*w for col,w in WEIGHTS.items())
    # Original six V2 points are immutable and use ALL batter-faced deliveries.
    # The independent pressure component now contains two sub-scores:
    # 60% six pressure-situation weighted points, 40% overall pressure reliability.
    # Each pressure situation receives ZERO if its pressure balls are below the slider threshold.
    for sit, weight in WEIGHTS.items():
        pballs=t[f'{sit} pressure balls']
        psr=t[sit]
        t[f'{sit} pressure points']=np.where(
            pballs>=min_situation_pressure_balls,
            psr.apply(score_band),0).astype(int)
    t['pressure_six_score']=sum(t[f'{sit} pressure points']*w for sit,w in WEIGHTS.items())
    t['pressure_six_normalized']=100*t.pressure_six_score/180
    # Overall pressure reliability uses pressure SR and relative SR improvement,
    # ranked against the currently eligible, non-excluded candidate pool.
    t['bonus']=t.improvement_ratio.apply(bonus_band)  # historical V2 diagnostic only; NOT ranked
    t['v2_normalized']=100*t.phase_score/180
    t['eligible']=(t.matches>=min_matches)&(t.pressure_balls>=min_pressure_balls)&(t.balls>0)
    pak_ids=set(mapping.loc[mapping['team_name'].fillna('').str.match(r'^Pakistan(?: A| Shaheens)?$',case=False), 'player_id'])
    bang_ids=set(mapping.loc[mapping['team_name'].fillna('').str.match(r'^Bangladesh(?: A| Emerging)?$',case=False), 'player_id'])
    t['excluded_pakistan']=t.index.isin(pak_ids)
    t['excluded_bangladesh']=t.index.isin(bang_ids)
    t['excluded_retirement']=t['name'].str.casefold().isin(exclusions())
    t['excluded']=t['excluded_retirement'] | ((t['excluded_pakistan'] | t['excluded_bangladesh']) if exclude_pak_bang else False)
    t=t.reset_index().rename(columns={'striker_id':'player_id'})
    # Cohort-relative percentiles are recomputed for the selected competition and filters.
    # Candidate exclusion never removes opposition deliveries from match statistics.
    pool=t.loc[t.eligible & ~t.excluded].copy()
    if not pool.empty:
        # Percentile method='average' gives tied values the same result.
        # Absolute pressure SR and improvement against a player's own all-ball SR each get 50%.
        sr_pct=pool['pressure_sr'].rank(pct=True,method='average')*100
        lift_pct=pool['improvement_pct'].rank(pct=True,method='average')*100
        raw_pressure=(sr_pct+lift_pct)/2
        confidence=pool['pressure_balls']/(pool['pressure_balls']+60.0)
        pressure_rating=50+confidence*(raw_pressure-50)
        t['overall_pressure_rating']=np.nan
        t.loc[pool.index,'overall_pressure_rating']=pressure_rating
    else:
        t['overall_pressure_rating']=np.nan
    t['pressure_rating']=0.60*t.pressure_six_normalized+0.40*t.overall_pressure_rating
    t['pressure_confidence']=t.pressure_balls/(t.pressure_balls+60.0)
    t['v2_component']=0.70*t.v2_normalized
    t['pressure_component']=0.30*t.pressure_rating
    t['composite']=t.v2_component+t.pressure_component
    t['rating_pct']=t.composite
    t['final_score_200']=2*t.composite
    ranked=t[t.eligible & ~t.excluded].sort_values(
        ['improvement_pct','pressure_six_score','pressure_balls','composite','name','player_id'],
        ascending=[False,False,False,False,True,True],kind='stable').copy()
    ranked.insert(0,'rank',range(1,len(ranked)+1))
    return ranked,t,d,None
