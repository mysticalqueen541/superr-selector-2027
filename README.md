# SUPERR SELECTOR — Batting + Bowling

Run `run_windows.bat` on Windows, or `pip install -r requirements.txt` followed by `streamlit run app.py`.

**Layout:** model controls in left sidebar; Format dropdown at upper right; four summary cards; Batters, Bowlers and Methodology pages.

**Scoring:** Batting is unchanged. Bowling Pressure Reliability now gives improvement credit only for strictly positive economy improvement; zero or negative improvement earns no improvement credit. The original 70/30 final weighting is unchanged. Batting original V2 uses six situations; bowling combined-format results use final Excel-derived aggregates. Pressure dot-ball percentage is display-only.

**Included workbooks:** the original user-supplied batting V2 workbook, final bowling economy workbook, final bowling pressure workbook, and excluded-chases audit, under `Excel_Workbooks/`.

**Testing:** Python syntax checked. Actual Streamlit browser rendering has not been verified here.
