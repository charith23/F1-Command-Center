import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import time
import base64

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="F1 Command Center", initial_sidebar_state="collapsed")

# --- CUSTOM CSS FOR FOOLPROOF LOCK & CLEAN UI ---
st.markdown("""
    <style>
    /* HIDE DEFAULT HEADER */
    [data-testid="stHeader"] { display: none !important; }
    
    /* REMOVE DEFAULT TOP PADDING */
    .block-container { padding-top: 0rem !important; }
    
    /* PURE WHITE BACKGROUND */
    .stApp { background-color: #FFFFFF; }
    .stApp, p, span, h1, h2, h3, h4, label { color: #111111 !important; }

    /* ========================================================
       🔥 FIX 1: THE 100% BULLETPROOF HEADER LOCK
       ======================================================== */
    .main .block-container > div:nth-child(1) {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        background-color: #FFFFFF !important;
        z-index: 999999 !important;
        border-bottom: 2px solid #EEEEEE !important;
        padding: 10px 5% 0px 5% !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05) !important;
    }

    /* Push the SECOND container (Main Body) down */
    .main .block-container > div:nth-child(2) {
        margin-top: 90px !important;
    }

    /* ========================================================
       🔥 FIX 2: NAV TEXT & RADIO DOTS
       ======================================================== */
    div[data-testid="stRadio"] div[role='radiogroup'] { 
        flex-direction: row; 
        gap: 30px; 
    }
    div[data-testid="stRadio"] div[role='radiogroup'] > label > div:first-child,
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { 
        display: none !important; 
    }
    div[data-testid="stRadio"] div[role='radiogroup'] > label {
        background-color: transparent !important;
        cursor: pointer;
        padding-bottom: 5px;
        border-bottom: 3px solid transparent;
        border-radius: 0px;
        margin-top: 15px; 
    }
    div[data-testid="stRadio"] div[role='radiogroup'] > label p {
        color: #111111 !important; 
        font-weight: 800 !important;
        font-size: 16px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stRadio"] div[role='radiogroup'] > label:hover p { color: #FF1801 !important; }
    div[data-testid="stRadio"] div[role='radiogroup'] > label[data-checked="true"] { border-bottom: 3px solid #FF1801 !important; }
    div[data-testid="stRadio"] div[role='radiogroup'] > label[data-checked="true"] p { color: #FF1801 !important; }
    
    /* ========================================================
       🔥 FIX 3: F1 PREMIUM RED BUTTON FOR QUALIFYING
       ======================================================== */
    div.stButton > button {
        background-color: #FF1801 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        height: 55px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button * {
        color: #FFFFFF !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        letter-spacing: 1px !important;
    }
    div.stButton > button:hover {
        background-color: #D31200 !important;
        box-shadow: 0px 4px 15px rgba(255, 24, 1, 0.4) !important;
        transform: translateY(-2px);
    }
    
    .js-plotly-plot .plotly .main-svg { background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)


# --- HELPER FUNCTION TO LOAD LOCAL IMAGES IN HTML ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    return ""

# ==========================================
# 📌 CONTAINER 1: TOP NAVIGATION BAR
# ==========================================
with st.container():
    # Columns allocation: Logo | Nav Menu | Branding
    col_logo, col_nav, head_col2 = st.columns([1, 5, 4])

    with col_logo:
        logo_path = "assets/f1_logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=90)
        else:
            st.markdown("<h2 style='color:#FF1801; margin:0;'>F1</h2>", unsafe_allow_html=True)

    with col_nav:
        menu = st.radio("Menu", [
            "ANALYSIS", 
            "QUALIFYING", 
            "DRIVERS", 
            "TEAMS",
            "SCHEDULE"
        ], label_visibility="collapsed", horizontal=True)

    with head_col2:
        # 🔥 Font size increased to 28px and weight 900 for a solid heading look
        st.markdown("""
            <h1 style='text-align: right; color: #FF1801; margin: 0; font-weight: 900; font-size: 28px; letter-spacing: 1px; line-height: 1.2;'>
                F1 COMMAND CENTER
            </h1>
        """, unsafe_allow_html=True)

# ==========================================
# 📊 CONTAINER 2: MAIN BODY
# ==========================================
with st.container():
    
    circuits_data = {
        "Australian GP (Melbourne)": {"type": "Street", "dist": "5.278 km", "img": "assets/melbourne.png", "base_lap": 77.5},
        "Chinese GP (Shanghai)": {"type": "Balanced", "dist": "5.451 km", "img": "assets/shanghai.png", "base_lap": 94.0},
        "Japanese GP (Suzuka)": {"type": "High Speed Cornering", "dist": "5.807 km", "img": "assets/suzuka.png", "base_lap": 88.0},
        "Bahrain GP (Sakhir)": {"type": "Rear Limited", "dist": "5.412 km", "img": "assets/bahrain.png", "base_lap": 90.0},
        "Saudi Arabian GP (Jeddah)": {"type": "High Speed Street", "dist": "6.174 km", "img": "assets/jeddah.png", "base_lap": 87.5},
        "Miami GP (Miami)": {"type": "Street", "dist": "5.412 km", "img": "assets/miami.png", "base_lap": 87.0},
        "Canadian GP (Montreal)": {"type": "Low Downforce", "dist": "4.361 km", "img": "assets/montreal.png", "base_lap": 71.0},
        "Monaco GP (Monte Carlo)": {"type": "High Downforce", "dist": "3.337 km", "img": "assets/monaco.png", "base_lap": 71.5},
        "Spanish GP (Barcelona)": {"type": "Balanced", "dist": "4.657 km", "img": "assets/barcelona.png", "base_lap": 73.0},
        "Austrian GP (Spielberg)": {"type": "Power Track", "dist": "4.318 km", "img": "assets/austria.png", "base_lap": 64.5},
        "British GP (Silverstone)": {"type": "High Speed", "dist": "5.891 km", "img": "assets/silverstone.png", "base_lap": 86.0},
        "Belgian GP (Spa)": {"type": "Power Track", "dist": "7.004 km", "img": "assets/spa.png", "base_lap": 104.0},
        "Hungarian GP (Budapest)": {"type": "High Downforce", "dist": "4.381 km", "img": "assets/hungary.png", "base_lap": 76.5},
        "Dutch GP (Zandvoort)": {"type": "High Downforce", "dist": "4.259 km", "img": "assets/zandvoort.png", "base_lap": 70.5},
        "Italian GP (Monza)": {"type": "Extreme Speed", "dist": "5.793 km", "img": "assets/monza.png", "base_lap": 80.5},
        "Spanish GP (Madrid)": {"type": "Street", "dist": "TBD", "img": "assets/madrid.png", "base_lap": 85.0},
        "Azerbaijan GP (Baku)": {"type": "Street/Power", "dist": "6.003 km", "img": "assets/baku.png", "base_lap": 101.0},
        "Singapore GP (Marina Bay)": {"type": "High Downforce Street", "dist": "4.940 km", "img": "assets/singapore.png", "base_lap": 90.0},
        "United States GP (Austin)": {"type": "Balanced", "dist": "5.513 km", "img": "assets/austin.png", "base_lap": 94.5},
        "Mexico City GP (Mexico)": {"type": "High Altitude", "dist": "4.304 km", "img": "assets/mexico.png", "base_lap": 77.0},
        "São Paulo GP (Brazil)": {"type": "Balanced", "dist": "4.309 km", "img": "assets/brazil.png", "base_lap": 70.0},
        "Las Vegas GP (Vegas)": {"type": "Extreme Speed Street", "dist": "6.201 km", "img": "assets/vegas.png", "base_lap": 93.0},
        "Qatar GP (Lusail)": {"type": "High Speed Cornering", "dist": "5.419 km", "img": "assets/qatar.png", "base_lap": 83.5},
        "Abu Dhabi GP (Yas Marina)": {"type": "Balanced", "dist": "5.281 km", "img": "assets/abudhabi.png", "base_lap": 83.0}
    }
# ==========================================
    # 📊 VIEW 1: ANALYSIS (Fully Dynamic & Statistical)
    # ==========================================
    if menu == "ANALYSIS":
        st.markdown("<h2 style='font-weight: bold; color: #111;'>Race Intelligence & Statistics</h2>", unsafe_allow_html=True)

        # 1. Unified Data & Dynamic Calculation Logic (Fixes NameError & RUS bias)
        d_base = [
            {"name": "ANT", "team": "Mercedes", "base": 85, "vmax_base": 315},
            {"name": "RUS", "team": "Mercedes", "base": 88, "vmax_base": 314},
            {"name": "LEC", "team": "Ferrari", "base": 88, "vmax_base": 312},
            {"name": "NOR", "team": "McLaren", "base": 89, "vmax_base": 310},
            {"name": "VER", "team": "Red Bull Racing", "base": 82, "vmax_base": 305}
        ]

        def get_dynamic_analysis(track_type):
            # 2026 Season Performance Weights
            weights = {"Mercedes": 1.35, "Ferrari": 1.15, "McLaren": 1.10, "Red Bull Racing": 0.82}
            probs = []
            for d in d_base:
                # Probability Logic factoring in 2026 Technical Regulations
                score = d['base'] * weights.get(d['team'], 1.0)
                if "Street" in track_type or "High Speed" in track_type: score += 10
                score += np.random.randint(-1, 2)
                
                # V-Max Logic (Varies by track type)
                vmax = d['vmax_base']
                if "Power" in track_type: vmax += 10
                elif "Street" in track_type: vmax -= 15
                
                probs.append({"Driver": d['name'], "Raw": score, "Team": d['team'], "VMax": vmax})
            
            df = pd.DataFrame(probs)
            df['Probability'] = (df['Raw'] / df['Raw'].sum() * 100).round(1)
            return df.sort_values('Probability', ascending=True)

        # 2. Control Layout
        col_ctrl, col_main = st.columns([1, 3])
        with col_ctrl:
            st.caption("SELECT CIRCUIT")
            selected_track = st.selectbox("Circuit", list(circuits_data.keys()), label_visibility="collapsed")
            track_info = circuits_data[selected_track]
            
            # Data recalculation on change
            prob_data = get_dynamic_analysis(track_info['type'])
            top_d = prob_data.iloc[-1] 

        # 3. DYNAMIC STAT CARDS (Revanth Style - No Sodi)
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center; color:#111;'><h4>{top_d['Driver']}</h4><p>Win Favorite</p></div>", unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center; color:#111;'><h4>{top_d['Probability']}%</h4><p>Confidence Level</p></div>", unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center; color:#111;'><h4>{top_d['VMax']} km/h</h4><p>Predicted V-Max</p></div>", unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center; color:#111;'><h4>{track_info['type']}</h4><p>Layout Category</p></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 4. Visualization Layout
        c1, c2 = st.columns([1.2, 1.8])
        with c1:
            # Map Display
            img_path = track_info['img']
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            
            # STRATEGY INSIGHT (Fixed: No more black box)
            # st.markdown(f"""
            # <div style='background-color: #111; color: white; padding: 20px; border-radius: 10px; border-left: 5px solid #FF1801; margin-top:10px;'>
            #     <p style='margin:0; font-size:14px;'><b>Strategy Insight:</b> {top_d['Team']} dominance is expected here. Current 2026 regs give them a 1.35x efficiency multiplier on {track_info['type']} tracks.</p>
            # </div>
            # """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"<h3 style='text-align: center; font-size:18px; color:#000;'>Win Probability Share</h3>", unsafe_allow_html=True)
            
            top_5_prob = prob_data.iloc[-5:] 
            
            fig_donut = px.pie(
                top_5_prob, 
                values='Probability', 
                names='Driver', 
                hole=0.6, 
                color_discrete_sequence=['#FF1801', '#FF4D3D', '#FF7E70', '#FFAEAB', '#F9D5D3']
            )
            
            # 🔥 FIX: weight property should be integer or 'bold'
            fig_donut.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400,
                annotations=[dict(
                    text='WIN %', 
                    x=0.5, y=0.5, 
                    font_size=24, 
                    showarrow=False, 
                    font_family="sans-serif", 
                    font_weight=900, # <--- Removed quotes ('900' -> 900)
                    font_color="#000000"
                )]
            )
            
            fig_donut.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont=dict(color="#FFF", size=12, weight='bold'),
                marker=dict(line=dict(color='#FFF', width=2))
            )
            
            st.plotly_chart(fig_donut, use_container_width=True)

            # 🔥 REAL PLOTLY HEATMAP (Replaces the "SA" box)
            st.markdown("#### 🌡️ Sector Dominance Heatmap")
            
            # Generating realistic 2026 sector data
            # Rows: Drivers, Cols: Sectors
            drivers_list = ['ANT', 'RUS', 'LEC', 'NOR', 'VER']
            sectors = ['Sector 1 (Speed)', 'Sector 2 (Technical)', 'Sector 3 (Traction)']
            
            # Base data + random noise for realistic telemetry feel
            heat_vals = [
                [98, 92, 95], # ANT (Merc) - Fast & Traction
                [95, 90, 92], # RUS (Merc)
                [90, 98, 88], # LEC (Ferrari) - Technical king
                [88, 85, 90], # NOR (McLaren)
                [82, 80, 75]  # VER (Red Bull) - Struggling
            ]
            
            fig_heat = px.imshow(
                heat_vals,
                labels=dict(x="Circuit Sectors", y="Driver", color="Efficiency"),
                x=sectors,
                y=drivers_list,
                color_continuous_scale='Reds',
                aspect="auto"
            )
            
            fig_heat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                height=300,
                xaxis=dict(tickfont=dict(color="#000", weight="bold")),
                yaxis=dict(tickfont=dict(color="#000", weight="bold"))
            )
            
            st.plotly_chart(fig_heat, use_container_width=True)
            st.caption("Deep Red indicates 95%+ efficiency in specific telemetry sectors.")

        
            
    # ==========================================
    # ⏱️ VIEW 2: QUALIFYING PREDICTOR
    # ==========================================
    elif menu == "QUALIFYING":
        st.markdown("<h2 style='font-weight: bold; color: #111;'>Qualifying Simulator (Q1, Q2, Q3)</h2>", unsafe_allow_html=True)
        
        drivers_base = [
            {"name": "VER", "full_name": "Max Verstappen", "team": "Red Bull Racing", "base": 90, "type_bonus": "High Speed Cornering"},
            {"name": "LAW", "full_name": "Liam Lawson", "team": "Red Bull Racing", "base": 70, "type_bonus": "Balanced"},
            {"name": "LEC", "full_name": "Charles Leclerc", "team": "Ferrari", "base": 88, "type_bonus": "Street"},
            {"name": "HAM", "full_name": "Lewis Hamilton", "team": "Ferrari", "base": 85, "type_bonus": "Balanced"},
            {"name": "NOR", "full_name": "Lando Norris", "team": "McLaren", "base": 89, "type_bonus": "High Downforce"},
            {"name": "PIA", "full_name": "Oscar Piastri", "team": "McLaren", "base": 86, "type_bonus": "High Speed"},
            {"name": "RUS", "full_name": "George Russell", "team": "Mercedes", "base": 85, "type_bonus": "Power Track"},
            {"name": "ANT", "full_name": "Kimi Antonelli", "team": "Mercedes", "base": 72, "type_bonus": "Balanced"},
            {"name": "ALO", "full_name": "Fernando Alonso", "team": "Aston Martin", "base": 80, "type_bonus": "Street"},
            {"name": "STR", "full_name": "Lance Stroll", "team": "Aston Martin", "base": 65, "type_bonus": "Balanced"},
            {"name": "GAS", "full_name": "Pierre Gasly", "team": "Alpine", "base": 70, "type_bonus": "Balanced"},
            {"name": "COL", "full_name": "Franco Colapinto", "team": "Alpine", "base": 68, "type_bonus": "Street"},
            {"name": "ALB", "full_name": "Alex Albon", "team": "Williams", "base": 75, "type_bonus": "Extreme Speed"},
            {"name": "SAI", "full_name": "Carlos Sainz", "team": "Williams", "base": 78, "type_bonus": "Balanced"},
            {"name": "HUL", "full_name": "Nico Hülkenberg", "team": "Audi", "base": 72, "type_bonus": "High Downforce"},
            {"name": "BOR", "full_name": "Gabriel Bortoleto", "team": "Audi", "base": 60, "type_bonus": "Balanced"},
            {"name": "OCO", "full_name": "Esteban Ocon", "team": "Haas", "base": 68, "type_bonus": "Power Track"},
            {"name": "BEA", "full_name": "Oliver Bearman", "team": "Haas", "base": 62, "type_bonus": "Balanced"},
            {"name": "LIN", "full_name": "Arvid Lindblad", "team": "Racing Bulls", "base": 55, "type_bonus": "Balanced"},
            {"name": "TBA", "full_name": "TBA", "team": "Racing Bulls", "base": 50, "type_bonus": "Balanced"}
        ]

        def format_lap_time(seconds):
            m = int(seconds // 60)
            s = int(seconds % 60)
            ms = int(round((seconds % 1) * 1000))
            return f"{m}:{s:02d}.{ms:03d}"

        selected_track = st.selectbox("Select Circuit to Simulate Qualifying", list(circuits_data.keys()))
        track_info = circuits_data[selected_track]
        base_lap = track_info["base_lap"]
        track_type = track_info["type"]
        
        st.markdown("---")

        if st.button("🏁 SIMULATE QUALIFYING SESSION", use_container_width=True):
            progress_text = "Cars on track..."
            my_bar = st.progress(0, text=progress_text)
            
            q_results = []
            for d in drivers_base:
                skill_factor = (100 - d['base']) / 100.0  
                track_bonus = 0.02 if track_type in d['type_bonus'] else 0.0
                random_factor = np.random.uniform(-0.3, 0.6)
                lap_time = base_lap + (skill_factor * 2.5) - track_bonus + random_factor
                
                q_results.append({
                    "Driver": d['full_name'],
                    "Team": d['team'],
                    "RawTime": lap_time,
                    "Lap Time": format_lap_time(lap_time)
                })
            
            df_q = pd.DataFrame(q_results)
            df_q = df_q.sort_values(by="RawTime").reset_index(drop=True)
            df_q.index += 1 
            
            time.sleep(0.5)
            my_bar.progress(33, text="Q1 Complete... 5 cars knocked out.")
            time.sleep(0.5)
            my_bar.progress(66, text="Q2 Complete... 5 more cars knocked out.")
            time.sleep(0.5)
            my_bar.progress(100, text="Q3 Complete! Pole position secured.")
            time.sleep(0.5)
            my_bar.empty() 
            
            col_q3, col_q2, col_q1 = st.columns(3)
            
            with col_q3:
                st.markdown("<h4 style='color:#FF1801;'>🏆 Q3 (Top 10)</h4>", unsafe_allow_html=True)
                st.dataframe(df_q.iloc[0:10][["Driver", "Team", "Lap Time"]], use_container_width=True)
                
            with col_q2:
                st.markdown("<h4>🟡 Q2 Dropouts (11-15)</h4>", unsafe_allow_html=True)
                st.dataframe(df_q.iloc[10:15][["Driver", "Team", "Lap Time"]], use_container_width=True)
                
            with col_q1:
                st.markdown("<h4>🔴 Q1 Dropouts (16-20)</h4>", unsafe_allow_html=True)
                st.dataframe(df_q.iloc[15:20][["Driver", "Team", "Lap Time"]], use_container_width=True)
                
            st.success(f"Pole Position: **{df_q.iloc[0]['Driver']} ({df_q.iloc[0]['Team']})** with a time of {df_q.iloc[0]['Lap Time']} at {selected_track}")


   
 
    # ==========================================
    # 🏎️ VIEW 3: DRIVERS (Statistical Scouting Report)
    # ==========================================
    elif menu == "DRIVERS":
        st.markdown("<h2 style='font-weight: 900; color: #111;'>2026 Driver Intelligence Report</h2>", unsafe_allow_html=True)

        # 1. TOP STATISTICAL STACKS (Revanth Style)
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>K. ANTONELLI</h4><p style='color:#666;'>Standings Leader (78 pts)</p></div>", unsafe_allow_html=True)
        with s2:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>98%</h4><p style='color:#666;'>Avg. Form Index</p></div>", unsafe_allow_html=True)
        with s3:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>M. VERSTAPPEN</h4><p style='color:#666;'>Performance Variance High</p></div>", unsafe_allow_html=True)
        with s4:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>+0.250s</h4><p style='color:#666;'>Avg. Qualifying Gap</p></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. PERFORMANCE ANALYSIS CHARTS
        # PART 3.2: PERFORMANCE ANALYSIS CHARTS
        c1, c2 = st.columns([1.5, 1.5])
        
        with c1:
            st.markdown("### 📊 Points vs. Recent Form")
            df_perf_plot = pd.DataFrame({
                'Driver': ['VER', 'LAW', 'LEC', 'HAM', 'NOR', 'PIA', 'RUS', 'ANT'],
                'Points': [18, 4, 52, 48, 40, 35, 65, 78],
                'Form': [65, 55, 88, 85, 82, 80, 95, 98]
            })
            fig_p = px.scatter(df_perf_plot, x='Points', y='Form', text='Driver', size='Form', color='Form', color_continuous_scale='Reds')
            
            # 🔥 PITCH BLACK TEXT FIX
            fig_p.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                height=400,
                xaxis=dict(
                    tickfont=dict(color="#000000", size=12, weight='bold'),
                    title_font=dict(color="#000000", size=14, weight='bold'),
                    gridcolor='#EEE'
                ),
                yaxis=dict(
                    tickfont=dict(color="#000000", size=12, weight='bold'),
                    title_font=dict(color="#000000", size=14, weight='bold'),
                    gridcolor='#EEE'
                )
            )
            fig_p.update_traces(textfont=dict(color="#000000", weight='bold'))
            st.plotly_chart(fig_p, use_container_width=True)

        with c2:
            st.markdown("### ⏱️ Qualifying Consistency")
            df_c = pd.DataFrame({'Driver': ['ANT', 'RUS', 'LEC', 'HAM', 'NOR'], 'Consistency': [95, 92, 89, 87, 85]})
            fig_c = px.bar(df_c, x='Consistency', y='Driver', orientation='h', color='Consistency', color_continuous_scale='Blues')
            
            # 🔥 PITCH BLACK TEXT FIX
            fig_c.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                height=400, 
                showlegend=False,
                xaxis=dict(
                    tickfont=dict(color="#000000", size=12, weight='bold'),
                    title_font=dict(color="#000000", size=14, weight='bold'),
                    gridcolor='#EEE'
                ),
                yaxis=dict(
                    tickfont=dict(color="#000000", size=12, weight='bold'),
                    title_font=dict(color="#000000", size=14, weight='bold')
                )
            )
            st.plotly_chart(fig_c, use_container_width=True)

        # with c2:
        #     st.markdown("### ⏱️ Qualifying Consistency")
        #     df_c = pd.DataFrame({'Driver': ['ANT', 'RUS', 'LEC', 'HAM', 'NOR'], 'Consistency': [95, 92, 89, 87, 85]})
        #     fig_c = px.bar(df_c, x='Consistency', y='Driver', orientation='h', color='Consistency', color_continuous_scale='Blues')
        #     fig_c.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400, showlegend=False,
        #                         xaxis=dict(tickfont=dict(color="#000")), yaxis=dict(tickfont=dict(color="#000")))
        #     st.plotly_chart(fig_c, use_container_width=True)

        st.markdown("---")
        
        # 3. DRIVER SCOUTING RADAR 
        st.markdown("### 📇 Driver Intelligence Profiles")
        scout1, scout2 = st.columns([1.5, 1.5])
        with scout1:
            st.markdown("#### 🛡️ Skill Radar: K. ANTONELLI")
            sc_data = pd.DataFrame({'Metric': ['Qualifying Pace', 'Race Craft', 'Tyre Mgmt', 'Consistency', 'Aggression'], 'Score': [98, 92, 85, 95, 90]})
            fig_r = px.line_polar(sc_data, r='Score', theta='Metric', line_close=True)
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, tickfont=dict(color="#000")), 
                                angularaxis=dict(tickfont=dict(color="#000"))), showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)

        with scout2:
            st.markdown("#### 🏎️ Telemetry Insights")
            st.success("**Technical Observation:** Mercedes PU efficiency giving Antonelli a 0.150s advantage in S3.")
            st.metric("Predicted Pole Prob.", "82%")
            st.metric("Race Win Confidence", "75%")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- DRIVER LIST (PROFILES) ---
        # 🚀 CLEANED UP: NO REDUNDANT SCATTER CALLS HERE
        drivers = [
            {"first": "Max", "last": "VERSTAPPEN", "team": "Red Bull Racing", "num": "1", "color": "linear-gradient(135deg, #3671C6 0%, #1A3A68 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/M/MAXVER01_Max_Verstappen/maxver01.png"},
            {"first": "Liam", "last": "LAWSON", "team": "Red Bull Racing", "num": "30", "color": "linear-gradient(135deg, #3671C6 0%, #1A3A68 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LIALAW01_Liam_Lawson/lialaw01.png"},
            {"first": "Charles", "last": "LECLERC", "team": "Ferrari", "num": "16", "color": "linear-gradient(135deg, #E80020 0%, #7A0011 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CHALEC01_Charles_Leclerc/chalec01.png"},
            {"first": "Lewis", "last": "HAMILTON", "team": "Ferrari", "num": "44", "color": "linear-gradient(135deg, #E80020 0%, #7A0011 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LEWHAM01_Lewis_Hamilton/lewham01.png"},
            {"first": "Lando", "last": "NORRIS", "team": "McLaren", "num": "4", "color": "linear-gradient(135deg, #FF8000 0%, #B35900 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANNOR01_Lando_Norris/lannor01.png"},
            {"first": "Oscar", "last": "PIASTRI", "team": "McLaren", "num": "81", "color": "linear-gradient(135deg, #FF8000 0%, #B35900 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OSCPIA01_Oscar_Piastri/oscpia01.png"},
            {"first": "Fernando", "last": "ALONSO", "team": "Aston Martin", "num": "14", "color": "linear-gradient(135deg, #229971 0%, #0F593F 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/F/FERALO01_Fernando_Alonso/feralo01.png"},
            {"first": "Lance", "last": "STROLL", "team": "Aston Martin", "num": "18", "color": "linear-gradient(135deg, #229971 0%, #0F593F 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/L/LANSTR01_Lance_Stroll/lanstr01.png"},
            {"first": "Alex", "last": "ALBON", "team": "Williams", "num": "23", "color": "linear-gradient(135deg, #005AFF 0%, #002B7A 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/A/ALEALB01_Alexander_Albon/alealb01.png"},
            {"first": "Carlos", "last": "SAINZ", "team": "Williams", "num": "55", "color": "linear-gradient(135deg, #005AFF 0%, #002B7A 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/C/CARSAI01_Carlos_Sainz/carsai01.png"},
            {"first": "Esteban", "last": "OCON", "team": "Haas", "num": "31", "color": "linear-gradient(135deg, #333333 0%, #111111 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/E/ESTOCO01_Esteban_Ocon/estoco01.png"},
            {"first": "Oliver", "last": "BEARMAN", "team": "Haas", "num": "87", "color": "linear-gradient(135deg, #333333 0%, #111111 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/O/OLIBEA01_Oliver_Bearman/olibea01.png"},
            {"first": "George", "last": "RUSSELL", "team": "Mercedes", "num": "63", "color": "linear-gradient(135deg, #00A19B 0%, #004D4A 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/G/GEORUS01_George_Russell/georus01.png"},
            {"first": "Kimi", "last": "ANTONELLI", "team": "Mercedes", "num": "12", "color": "linear-gradient(135deg, #00A19B 0%, #004D4A 100%)", "img": "https://ui-avatars.com/api/?name=Kimi+Antonelli&background=004D4A&color=fff&size=200&rounded=true"},
            {"first": "Pierre", "last": "GASLY", "team": "Alpine", "num": "10", "color": "linear-gradient(135deg, #0090FF 0%, #004B87 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/P/PIEGAS01_Pierre_Gasly/piegas01.png"},
            {"first": "Franco", "last": "COLAPINTO", "team": "Alpine", "num": "43", "color": "linear-gradient(135deg, #0090FF 0%, #004B87 100%)", "img": "https://ui-avatars.com/api/?name=Franco+Colapinto&background=004B87&color=fff&size=200&rounded=true"},
            
            {"first": "Nico", "last": "HÜLKENBERG", "team": "Audi", "num": "27", "color": "linear-gradient(135deg, #E60000 0%, #660000 100%)", "img": "https://media.formula1.com/d_driver_fallback_image.png/content/dam/fom-website/drivers/N/NICHUL01_Nico_Hulkenberg/nichul01.png"},
            {"first": "Gabriel", "last": "BORTOLETO", "team": "Audi", "num": "TBA", "color": "linear-gradient(135deg, #E60000 0%, #660000 100%)", "img": "https://ui-avatars.com/api/?name=Gabriel+Bortoleto&background=660000&color=fff&size=200&rounded=true"},
            
            {"first": "Arvid", "last": "LINDBLAD", "team": "Racing Bulls", "num": "TBA", "color": "linear-gradient(135deg, #6692FF 0%, #1D439B 100%)", "img": "https://ui-avatars.com/api/?name=Arvid+Lindblad&background=1D439B&color=fff&size=200&rounded=true"},
            {"first": "TBA", "last": "TBA", "team": "Racing Bulls", "num": "TBA", "color": "linear-gradient(135deg, #6692FF 0%, #1D439B 100%)", "img": "https://ui-avatars.com/api/?name=T+B+A&background=1D439B&color=fff&size=200&rounded=true"}
        ]
        
        for i in range(0, len(drivers), 2):
            col1, col2 = st.columns(2)
            with col1:
                d1 = drivers[i]
                img_style = 'height: 160px; margin-top: 10px; border-radius: 50%;' if 'ui-avatars' in d1['img'] else 'height: 220px; margin-top: -20px; margin-right: -20px;'
                st.markdown(f"""
                <div style="background: {d1['color']}; border-radius: 12px; padding: 25px; margin-bottom: 20px; height: 200px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); display: flex; justify-content: space-between; overflow: hidden;">
                    <div style="z-index: 2;">
                        <h3 style="margin: 0; font-weight: 400; font-size: 22px; color: #FFFFFF !important;">{d1['first']}</h3>
                        <h2 style="margin: 0; font-weight: 900; font-size: 32px; color: #FFFFFF !important;">{d1['last']}</h2>
                        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; color: #FFFFFF !important;">{d1['team']}</p>
                        <h1 style="margin: 10px 0 0 0; font-size: 50px; color: transparent; -webkit-text-stroke: 1.5px rgba(255,255,255,0.6);">{d1['num']}</h1>
                    </div>
                    <div style="z-index: 1;">
                        <img src="{d1['img']}" style="{img_style}">
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if i + 1 < len(drivers):
                    d2 = drivers[i+1]
                    img_style2 = 'height: 160px; margin-top: 10px; border-radius: 50%;' if 'ui-avatars' in d2['img'] else 'height: 220px; margin-top: -20px; margin-right: -20px;'
                    st.markdown(f"""
                    <div style="background: {d2['color']}; border-radius: 12px; padding: 25px; margin-bottom: 20px; height: 200px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); display: flex; justify-content: space-between; overflow: hidden;">
                        <div style="z-index: 2;">
                            <h3 style="margin: 0; font-weight: 400; font-size: 22px; color: #FFFFFF !important;">{d2['first']}</h3>
                            <h2 style="margin: 0; font-weight: 900; font-size: 32px; color: #FFFFFF !important;">{d2['last']}</h2>
                            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; color: #FFFFFF !important;">{d2['team']}</p>
                            <h1 style="margin: 10px 0 0 0; font-size: 50px; color: transparent; -webkit-text-stroke: 1.5px rgba(255,255,255,0.6);">{d2['num']}</h1>
                        </div>
                        <div style="z-index: 1;">
                            <img src="{d2['img']}" style="{img_style2}">
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


   # ==========================================
    # 🏎️ VIEW 4: TEAMS UI
    # ==========================================
    elif menu == "TEAMS":
        st.markdown("<h2 style='font-weight: 900; color: #111;'>2026 Constructor Intelligence</h2>", unsafe_allow_html=True)

        # PART 4.1: CONSTRUCTOR PERFORMANCE STACKS
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>MERCEDES</h4><p style='color:#666;'>Dominant PU Efficiency</p></div>", unsafe_allow_html=True)
        with t2:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>FERRARI</h4><p style='color:#666;'>Highest Mechanical Grip</p></div>", unsafe_allow_html=True)
        with t3:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>RED BULL</h4><p style='color:#666;'>Reliability Concerns (2026)</p></div>", unsafe_allow_html=True)
        with t4:
            st.markdown("<div style='background:#F1F3F4; padding:15px; border-radius:10px; text-align:center;'><h4>AUDI</h4><p style='color:#666;'>Entering Mid-Field Struggle</p></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # PART 4.2: POWER RANKINGS & COMPARISON
        col_rank, col_desc = st.columns([1.8, 1.2])
        
        with col_rank:
            st.markdown("### 💠 Constructor Power Profile")
            team_analysis = pd.DataFrame({
                'Team': ["Mercedes", "Ferrari", "McLaren", "Red Bull", "Williams"],
                'Engine': [98, 92, 88, 78, 85],
                'Aero': [95, 90, 92, 80, 75]
            })
            
            # Radar chart for Engine Efficiency comparison
            fig_team = px.line_polar(team_analysis, r='Engine', theta='Team', line_close=True, color_discrete_sequence=['#FF1801'])
            
            # 🔥 PITCH BLACK LABELS FIX
            fig_team.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, tickfont=dict(color="#000000", size=10, weight="bold")),
                    angularaxis=dict(tickfont=dict(color="#000000", size=12, weight="bold"))
                ),
                height=450,
                margin=dict(l=50, r=50, t=30, b=30)
            )
            st.plotly_chart(fig_team, use_container_width=True)

        with col_desc:
            st.markdown("### 🛠️ Technical Outlook")
            st.info("""
            **Mercedes HPP:** Leading the grid with an estimated 20hp advantage under the 2026 ERS regulations.
            
            **Red Bull Ford:** Currently struggling with energy deployment issues during long-run simulations.
            """)
            st.metric("Grid Reliability Avg.", "88%", "-4% vs 2025")
            st.metric("Development Pace Index", "High (Mercedes)")

        st.markdown("---")
        st.markdown("### 🏎️ Grid Entry: Constructor Profiles")
        teams_data = [
            {"name": "Alpine", "color": "linear-gradient(135deg, #15151E 40%, rgba(0,144,255,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Alpine&background=0090FF&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/alpine.png"},
            {"name": "Aston Martin", "color": "linear-gradient(135deg, #15151E 40%, rgba(34,153,113,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Aston+Martin&background=229971&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/aston-martin.png"},
            {"name": "Audi", "color": "linear-gradient(135deg, #15151E 40%, rgba(230,0,0,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Audi&background=E60000&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/kick-sauber.png"},
            {"name": "Cadillac", "color": "linear-gradient(135deg, #15151E 40%, rgba(85,85,85,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Cadillac&background=555555&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mercedes.png"},
            {"name": "Ferrari", "color": "linear-gradient(135deg, #15151E 40%, rgba(232,0,32,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Ferrari&background=E80020&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/ferrari.png"},
            {"name": "Haas", "color": "linear-gradient(135deg, #15151E 40%, rgba(255,255,255,0.2) 100%)", "logo": "https://ui-avatars.com/api/?name=Haas&background=333333&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/haas.png"},
            {"name": "McLaren", "color": "linear-gradient(135deg, #15151E 40%, rgba(255,128,0,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=McLaren&background=FF8000&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mclaren.png"},
            {"name": "Mercedes", "color": "linear-gradient(135deg, #15151E 40%, rgba(0,161,155,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Mercedes&background=00A19B&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/mercedes.png"},
            {"name": "Racing Bulls", "color": "linear-gradient(135deg, #15151E 40%, rgba(102,146,255,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Racing+Bulls&background=6692FF&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/rb.png"},
            {"name": "Red Bull Racing", "color": "linear-gradient(135deg, #15151E 40%, rgba(54,113,198,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Red+Bull&background=3671C6&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/red-bull-racing.png"},
            {"name": "Williams", "color": "linear-gradient(135deg, #15151E 40%, rgba(0,90,255,0.3) 100%)", "logo": "https://ui-avatars.com/api/?name=Williams&background=005AFF&color=fff&rounded=true&bold=true", "car": "https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/2024/williams.png"},
        ]

        cols = st.columns(4)
        for i, team in enumerate(teams_data):
            with cols[i % 4]:
                st.markdown(f"""
                <div style="background: {team['color']}; border-radius: 10px; padding: 15px; margin-bottom: 20px; height: 190px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <img src="{team['logo']}" style="width: 28px; height: 28px; border-radius: 50%;">
                        <div style="color: #FFFFFF !important; margin: 0; font-size: 17px; font-weight: 900; font-family: sans-serif; letter-spacing: 0.5px;">{team['name']}</div>
                    </div>
                    <img src="{team['car']}" style="width: 100%; object-fit: contain; margin-top: 10px;">
                </div>
                """, unsafe_allow_html=True)
                
    # ==========================================
    # 📅 VIEW 5: SCHEDULE UI
    # ==========================================
    elif menu == "SCHEDULE":
        st.markdown("<h1 style='font-weight: 900; font-size: 40px;'>F1 2026 CALENDAR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 18px; color: #555; margin-bottom: 30px;'>Explore the 24-race calendar for the 2026 FIA Formula One World Championship.</p>", unsafe_allow_html=True)
        
        schedule_data = [
            {"rnd": 1, "country": "Australia", "flag": "🇦🇺", "name": "FORMULA 1 AUSTRALIAN GRAND PRIX 2026", "date": "06 - 08 MAR", "img": "assets/melbourne.png"},
            {"rnd": 2, "country": "China", "flag": "🇨🇳", "name": "FORMULA 1 CHINESE GRAND PRIX 2026", "date": "13 - 15 MAR", "img": "assets/shanghai.png"},
            {"rnd": 3, "country": "Japan", "flag": "🇯🇵", "name": "FORMULA 1 JAPANESE GRAND PRIX 2026", "date": "27 - 29 MAR", "img": "assets/suzuka.png"},
            {"rnd": 4, "country": "Bahrain", "flag": "🇧🇭", "name": "FORMULA 1 BAHRAIN GRAND PRIX 2026", "date": "10 - 12 APR", "img": "assets/bahrain.png"},
            {"rnd": 5, "country": "Saudi Arabia", "flag": "🇸🇦", "name": "FORMULA 1 SAUDI ARABIAN GRAND PRIX 2026", "date": "17 - 19 APR", "img": "assets/jeddah.png"},
            {"rnd": 6, "country": "Miami", "flag": "🇺🇸", "name": "FORMULA 1 MIAMI GRAND PRIX 2026", "date": "01 - 03 MAY", "img": "assets/miami.png"},
            {"rnd": 7, "country": "Canada", "flag": "🇨🇦", "name": "FORMULA 1 CANADIAN GRAND PRIX 2026", "date": "22 - 24 MAY", "img": "assets/montreal.png"},
            {"rnd": 8, "country": "Monaco", "flag": "🇲🇨", "name": "FORMULA 1 GRAND PRIX DE MONACO 2026", "date": "05 - 07 JUN", "img": "assets/monaco.png"},
            {"rnd": 9, "country": "Spain", "flag": "🇪🇸", "name": "FORMULA 1 SPANISH GRAND PRIX 2026", "date": "12 - 14 JUN", "img": "assets/barcelona.png"},
            {"rnd": 10, "country": "Austria", "flag": "🇦🇹", "name": "FORMULA 1 AUSTRIAN GRAND PRIX 2026", "date": "26 - 28 JUN", "img": "assets/austria.png"},
            {"rnd": 11, "country": "Great Britain", "flag": "🇬🇧", "name": "FORMULA 1 BRITISH GRAND PRIX 2026", "date": "03 - 05 JUL", "img": "assets/silverstone.png"},
            {"rnd": 12, "country": "Belgium", "flag": "🇧🇪", "name": "FORMULA 1 BELGIAN GRAND PRIX 2026", "date": "17 - 19 JUL", "img": "assets/spa.png"},
            {"rnd": 13, "country": "Hungary", "flag": "🇭🇺", "name": "FORMULA 1 HUNGARIAN GRAND PRIX 2026", "date": "24 - 26 JUL", "img": "assets/hungary.png"},
            {"rnd": 14, "country": "Netherlands", "flag": "🇳🇱", "name": "FORMULA 1 DUTCH GRAND PRIX 2026", "date": "21 - 23 AUG", "img": "assets/zandvoort.png"},
            {"rnd": 15, "country": "Italy", "flag": "🇮🇹", "name": "FORMULA 1 ITALIAN GRAND PRIX 2026", "date": "04 - 06 SEP", "img": "assets/monza.png"},
            {"rnd": 16, "country": "Madrid", "flag": "🇪🇸", "name": "FORMULA 1 MADRID GRAND PRIX 2026", "date": "11 - 13 SEP", "img": "assets/madrid.png"},
            {"rnd": 17, "country": "Azerbaijan", "flag": "🇦🇿", "name": "FORMULA 1 AZERBAIJAN GRAND PRIX 2026", "date": "24 - 26 SEP", "img": "assets/baku.png"},
            {"rnd": 18, "country": "Singapore", "flag": "🇸🇬", "name": "FORMULA 1 SINGAPORE GRAND PRIX 2026", "date": "09 - 11 OCT", "img": "assets/singapore.png"},
            {"rnd": 19, "country": "United States", "flag": "🇺🇸", "name": "FORMULA 1 UNITED STATES GRAND PRIX 2026", "date": "16 - 18 OCT", "img": "assets/austin.png"},
            {"rnd": 20, "country": "Mexico", "flag": "🇲🇽", "name": "FORMULA 1 GRAN PREMIO DE LA CIUDAD DE MÉXICO", "date": "23 - 25 OCT", "img": "assets/mexico.png"},
            {"rnd": 21, "country": "Brazil", "flag": "🇧🇷", "name": "FORMULA 1 SÃO PAULO GRAND PRIX 2026", "date": "30 OCT - 01 NOV", "img": "assets/brazil.png"},
            {"rnd": 22, "country": "Las Vegas", "flag": "🇺🇸", "name": "FORMULA 1 LAS VEGAS GRAND PRIX 2026", "date": "06 - 08 NOV", "img": "assets/vegas.png"},
            {"rnd": 23, "country": "Qatar", "flag": "🇶🇦", "name": "FORMULA 1 QATAR GRAND PRIX 2026", "date": "19 - 21 NOV", "img": "assets/qatar.png"},
            {"rnd": 24, "country": "Abu Dhabi", "flag": "🇦🇪", "name": "FORMULA 1 ABU DHABI GRAND PRIX 2026", "date": "04 - 06 DEC", "img": "assets/abudhabi.png"}
        ]

        cols = st.columns(3)
        for idx, race in enumerate(schedule_data):
            with cols[idx % 3]:
                base64_img = get_base64_image(race['img'])
                img_tag = f'<img src="data:image/png;base64,{base64_img}" style="position: absolute; bottom: 15px; right: 15px; width: 100px; opacity: 0.8; filter: brightness(0) invert(1);">' if base64_img else ''
                
                st.markdown(f"""
                <div style="background-color: #0F0F12; border-radius: 12px; padding: 20px; margin-bottom: 20px; height: 230px; position: relative; border: 1px solid #222; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);">
                    <div style="font-size: 11px; color: #888; font-weight: 800; letter-spacing: 1px;">ROUND {race['rnd']}</div>
                    <div style="font-size: 26px; font-weight: 900; color: white; margin-top: 5px; display: flex; align-items: center; gap: 8px;">
                        <span>{race['flag']}</span> {race['country']}
                    </div>
                    <div style="font-size: 11px; color: #aaa; margin-top: 5px; text-transform: uppercase;">{race['name']}</div>
                    <div style="position: absolute; bottom: 20px; left: 20px; font-size: 18px; font-weight: 800; color: white;">{race['date']}</div>
                    {img_tag}
                </div>
                """, unsafe_allow_html=True)    
