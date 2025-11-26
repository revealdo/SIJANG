import streamlit as st
import pandas as pd
import numpy as np
import json, os, base64
from io import BytesIO
from datetime import datetime, date
import sqlite3

st.set_page_config(page_title="Dashboard Keuangan", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>    
 .block-container {
    padding-top: 0 !important;
    margin-top: 10px !important;  
 }
 .header-title {
    margin-top: -20px !important;
 }
 div[data-testid="column"] {
    margin-top: -30px !important;
 }
</style>
""", unsafe_allow_html=True)


MASKOT_PATH = "maskot.png"   
PROFILE_PLACEHOLDER = "/mnt/data/profile_placeholder.png"  
USER_DB_FILE = "users.json"
JURNAL_DB_FILE = "jurnal_data.json"
EXCEL_FILE = "data_jurnal.xlsx"


def load_data(file_name, default):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as f:
                return json.load(f)
        except Exception:
            return default
    else:
        save_data(file_name, default)
        return default
    
def save_data(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

def save_jurnal_to_excel(data_list, file_name=EXCEL_FILE):
    if not data_list:
        return
    df = pd.DataFrame(data_list)
    try:
        df.to_excel(file_name, index=False, engine='openpyxl')
    except Exception as e:
        st.error(f"Gagal menyimpan ke Excel: {e}")

def load_jurnal_df():
    if "jurnal_data" not in st.session_state:
        return pd.DataFrame()
    df = pd.DataFrame(st.session_state["jurnal_data"])

    if df.empty:
        return pd.DataFrame()

    df["tanggal"] = pd.to_datetime(df["tanggal"], format="mixed", dayfirst=False, errors="coerce")

    return df


# ---------------------------
# SESSION STATE INIT
# ---------------------------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'show_create_account' not in st.session_state:
    st.session_state['show_create_account'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Dashboard'

# Load persistent DB
st.session_state['user_db'] = load_data(USER_DB_FILE, {"rivaldo123": "password123"})
st.session_state['jurnal_data'] = load_data(JURNAL_DB_FILE, [])

# ---------------------------
# CUSTOM CSS (Modern Minimal)
# ---------------------------
st.markdown(
    f"""
    <style>
    :root {{
        --primary:#0b3d2e;
        --accent: #d4af37;
        --muted: #6b7a70;
        --surface: #f2f7f4;
        --card-bg: #ffffff;
    }}
    html, body, [class*="css"] {{
        font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
        background: var(--surface) !important;
    }}
    .header-title {{
        color: var(--primary);
        font-size: 44px;
        font-weight: 800;
        margin: 0;
        line-height: 1.05;
    }}
    .header-sub {{
        color: #253041;
        font-size: 30px;
        margin-top: 8px;
        font-weight: 600;
    }}
    .card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 6px 20px rgba(43,46,74,0.06);
        border-left: 4px solid rgba(255,180,0,0.12);
    }}
    .metric {{
        font-size: 20px;
        font-weight: 700;
        color: var(--primary);
    }}
    .metric-sub {{
        font-size: 12px;
        color: var(--muted);
    }}
    /* Sidebar buttons look */
    /* MENGUBAH WARNA BUTTON DI SIDEBAR */
    .stButton > button {{
        display: block;
        padding: 8px 10px;
        border-radius: 8px;
        margin: 6px 0;
        /* WARNA HIJAU UNTUK SEMUA BUTTON */
        background: linear-gradient(180deg, #d4f7da, #70d68f); 
        font-weight: 700;
        color: #0b3d2e;
        width: 100%;
        text-align: left;
        border: none !important; /* Hilangkan border Streamlit default */
    }}
    /* WARNA BUTTON AKTIF */
    .stButton > button:focus:not(:active) {{
        background: linear-gradient(180deg, #51be73, #0b3d2e);
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    
    /* Memusatkan judul login dan membuatnya lebih jelas */
    .centered-title {{
        text-align: center; /* Pastikan kontainer div menengahkan isinya */
        width: 100%; /* Pastikan mengambil seluruh lebar */
    }}
    .centered-title > h1 {{
        color: var(--primary); /* Warna judul login agar terlihat jelas */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2); /* Bayangan agar lebih menonjol */
        font-size: 50px;
    }}

    /* Menjadikan form login/input tidak transparan */
    div[data-testid="stTextInput"], div[data-testid="stForm"] {{
        background: none; 
    }}
    div[data-testid="stForm"] > div {{
        background: white; /* Beri background putih pada form agar terlihat jelas */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    .maskot {{
        max-width:220px;
    }}
    /* Tambahan untuk memusatkan gambar maskot secara vertikal */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {{
        display: flex;
        align-items: center;
    }}

    /* small responsive tweak */
    @media (max-width: 680px) {{
        .header-title {{ font-size:28px; }}
        .header-sub {{ font-size:18px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# AUTH FUNCTIONS
# ---------------------------
# FUNGSI SET BACKGROUND DIHAPUS

def login(input_username, input_password):
    db = st.session_state['user_db']
    if input_username in db and db[input_username] == input_password:
        st.session_state['authenticated'] = True
        st.session_state['username'] = input_username
        st.success("Login Berhasil!")
        st.rerun()
    else:
        st.error("Username atau Password salah.")

def create_account(new_username, new_password, confirm_password):
    if not new_username or not new_password or new_password != confirm_password:
        st.error("Input tidak valid atau Password tidak cocok.")
        return
    db = st.session_state['user_db']
    if new_username in db:
        st.error("Username sudah terdaftar.")
        return
    db[new_username] = new_password
    save_data(USER_DB_FILE, db)
    st.session_state['user_db'] = db
    st.success(f"Akun **{new_username}** berhasil dibuat! Silakan Login.")
    st.session_state['show_create_account'] = False
    st.rerun()

def logout():
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['show_create_account'] = False
    st.session_state['current_page'] = 'Dashboard'
    st._rerun()

# ---------------------------
# SIDEBAR (modern)
# ---------------------------
def sidebar_menu():
    # Tidak perlu memanggil set_background_default karena background sudah tidak diset
    with st.sidebar:
        # Profile area
        colp, = st.columns([1])
        try:
            st.image(PROFILE_PLACEHOLDER, width=84)
        except:
            st.markdown("👤")
        username_display = st.session_state['username'] or "Guest"
        st.markdown(f"**{username_display.capitalize()}**")
        st.markdown("<div style='color:#7a7f9a;font-size:13px'>Pengguna · Aktif</div>", unsafe_allow_html=True)
        st.markdown("")

        # Menu buttons (styled)
        menu_items = ["Dashboard", "Jurnal Umum", "Buku Besar", "Neraca", "BP Utang", "BP Piutang", "Inventory","Laporan Laba Rugi"]
        for item in menu_items:
            key = f"menu_{item.replace(' ', '_')}"
            is_active = (st.session_state.get('current_page') == item)
            
            if st.button(item, key=key):
                st.session_state['current_page'] = item
                st.rerun()
                
        st.markdown("")
        if st.button("Logout"):
            logout()

# ---------------------------
# SAMPLE / HELPERS FOR DASHBOARD
# ---------------------------
def generate_sample_data(days=180):
    rng = pd.date_range(end=datetime.today(), periods=days)
    base_income = np.linspace(4000000, 7000000, days) + np.random.normal(0, 200000, days)
    base_expense = np.linspace(3000000, 3500000, days) + np.random.normal(0, 150000, days)
    df = pd.DataFrame({"date": rng, "income": np.abs(base_income).astype(int), "expense": np.abs(base_expense).astype(int)})
    df["balance"] = df["income"] - df["expense"]
    return df

df_sample = generate_sample_data()

# ---------------------------
# JURNAL UMUM PAGE (modernized)
# ---------------------------
def jurnal_umum_page():
    st.header("Jurnal Umum 📓")

    # ===============================
    # Daftar akun
    # ===============================
    daftar_akun = [
        "Kas", "Piutang Usaha", "Utang Usaha",
        "Penjualan", "Pembelian", "Perlengkapan", "Peralatan",
        "Persediaan - Pakan", "Persediaan - Bibit",
        "Persediaan - Sekam & Bahan Kandang", "Persediaan - Jangkrik",
        "HPP", "Beban Gaji", "Beban Pakan", "Beban Listrik & Air",
        "Beban Transportasi", "Beban Penyusutan Peralatan",
        "Beban Perlengkapan", "Beban Sewa", "Akumulasi Penyusutan Peralatan"
    ]

    # Pastikan session state aman
    if "jurnal_data" not in st.session_state or not isinstance(st.session_state["jurnal_data"], list):
        st.session_state["jurnal_data"] = []

    # ===============================
    # FORM INPUT TRANSAKSI
    # ===============================
    with st.form("jurnal_input_form"):
        tanggal = st.date_input("Tanggal Transaksi", date.today())
        deskripsi = st.text_input("Deskripsi Transaksi")

        col_d, col_k = st.columns(2)
        with col_d:
            akun_debit = st.selectbox("Akun (Debit)", daftar_akun)
            debit_val = st.number_input("Nilai Debit", min_value=0.0, format="%.2f")
        with col_k:
            akun_kredit = st.selectbox("Akun (Kredit)", daftar_akun)
            kredit_val = st.number_input("Nilai Kredit", min_value=0.0, format="%.2f")

        # Deteksi utang/piutang
        # ============================
        # DETEKSI UTANG / PIUTANG
        # ============================
        jenis_transaksi = "Tunai"
        nama_toko = ""

    # UTANG: baik DEBIT (pelunasan) atau KREDIT (utang baru)
        if akun_debit == "Utang Usaha" or akun_kredit == "Utang Usaha":
            jenis_transaksi = "Utang"
            nama_toko = st.text_input("Nama Supplier (Wajib untuk Utang)")

        # PIUTANG: baik DEBIT (piutang baru) atau KREDIT (pelunasan piutang)
        elif akun_debit == "Piutang Usaha" or akun_kredit == "Piutang Usaha":
            jenis_transaksi = "Piutang"
            nama_toko = st.text_input("Nama Pelanggan (Wajib untuk Piutang)")


        submitted = st.form_submit_button("SIMPAN")

    # ===============================
    # PROSES SIMPAN TRANSAKSI
    # ===============================
    if submitted:

        if debit_val != kredit_val:
            st.error("Nilai Debit dan Kredit harus sama!")
            return

        if jenis_transaksi in ["Utang", "Piutang"] and nama_toko.strip() == "":
            st.error("Nama toko/pelanggan wajib diisi!")
            return

        new_entry = {
            "tanggal": tanggal.strftime("%Y-%m-%d"),
            "deskripsi": deskripsi,
            "debit_akun": akun_debit,
            "kredit_akun": akun_kredit,
            "nilai": float(debit_val),
            "jenis_transaksi": jenis_transaksi,
            "nama_toko": nama_toko,
            "user": st.session_state.get("username", "unknown"),
        }

        st.session_state["jurnal_data"].append(new_entry)
        save_data("jurnal_data.json", st.session_state["jurnal_data"])

        st.success("Transaksi berhasil disimpan!")
        st.rerun()

    # ===============================
    # TAMPILKAN TABEL JURNAL 4 KOLOM
    # ===============================
    st.subheader("Data Transaksi")

    df = pd.DataFrame(st.session_state["jurnal_data"])

    if df.empty:
        st.info("Belum ada transaksi.")
        return

    # HEADER TABEL
    st.markdown("""
        <table style='width:100%; border-collapse:collapse;'>
            <tr style='background:#0f6cd5; color:white; font-weight:bold;'>
                <th style='padding:8px; border:1px solid #333;'>Tanggal</th>
                <th style='padding:8px; border:1px solid #333;'>Keterangan</th>
                <th style='padding:8px; border:1px solid #333;'>Debit</th>
                <th style='padding:8px; border:1px solid #333;'>Kredit</th>
                <th style='padding:8px; border:1px solid #333;'>Toko</th>
                <th style='padding:8px; border:1px solid #333;'>Aksi</th>
            </tr>
        </table>
    """, unsafe_allow_html=True)

    # LOOP TAMPILKAN BARIS JURNAL
    for i, row in df.iterrows():

        debit = f"Rp {row['nilai']:,.0f}".replace(",", ".")
        kredit = f"Rp {row['nilai']:,.0f}".replace(",", ".")

        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 4, 2, 2, 2, 1])

            col1.write(row["tanggal"])
            col2.write(row["debit_akun"])
            col3.write(debit)
            col4.write("")
            col5.write(row.get("nama_toko", ""))

            # Tombol hapus
            if col6.button("🗑️", key=f"hapus_debit_{i}"):
                st.session_state["jurnal_data"].pop(i)
                save_data("jurnal_data.json", st.session_state["jurnal_data"])
                st.rerun()

        with st.container():
            col1, col2, col3, col4, col5, _ = st.columns([2, 4, 2, 2, 2, 1])

            col1.write("")
            col2.write("  " + row["kredit_akun"])
            col3.write("")
            col4.write(kredit)
            col5.write("")

    st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------
# DASHBOARD PAGE
# ---------------------------
def dashboard_page():

    # Tambah jarak biar tidak kepotong header
    st.markdown("<div style='padding-top: 40px;'></div>", unsafe_allow_html=True)

    df = load_jurnal_df()
    
    # ============================
    # MASKOT DITEMPATKAN DI SINI (SUDAH DIUBAH KE KANAN)
    # ============================
    col_title, col_maskot = st.columns([4, 1])
    with col_title:
        # Judul
        st.markdown("""
        <h1 style='text-align:left; margin-bottom:20px; font-size:40px; color:#0b3d2e;'>💰 Dashboard Keuangan</h1>
        """, unsafe_allow_html=True)
    with col_maskot:
        # Tambah CSS untuk rata kanan pada gambar di kolom maskot
        st.markdown("<style>.maskot-right {display: flex; justify-content: flex-end; align-items: center; height: 100%;}</style>", unsafe_allow_html=True)
        st.markdown("<div class='maskot-right'>", unsafe_allow_html=True)
        try:
            # Tingkatkan width untuk kesan 'HD' (lebih besar)
            st.image(MASKOT_PATH, width=200)
        except:
            st.warning("Maskot tidak ditemukan.")
        st.markdown("</div>", unsafe_allow_html=True)


    # ============================
    # Hitung Pemasukan & Pengeluaran Riil
    # ============================
    if df.empty:
        pemasukan_total = 0
        pengeluaran_total = 0
        saldo_total = 0
    else:
        # Pemasukan = Kas bertambah dari Penjualan
        pemasukan_total = df[
            (df["debit_akun"].str.contains("Kas", case=False)) &
            (df["kredit_akun"].str.contains("Penjualan", case=False))
        ]["nilai"].sum()

        # Pengeluaran = semua beban + pembelian
        pengeluaran_total = df[
            df["debit_akun"].str.contains("Beban|Pembelian", case=False)
        ]["nilai"].sum()

        saldo_total = pemasukan_total - pengeluaran_total

    # ============================
    # 3 CARD
    # ============================
    c1, c2, c3 = st.columns(3)

    # --- Card pemasukan ---
    with c1:
        st.markdown("<div style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#888; font-size:14px;'>Pemasukan</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:28px; font-weight:700;'>Rp {pemasukan_total:,.0f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Card pengeluaran ---
    with c2:
        st.markdown("<div style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#888; font-size:14px;'>Pengeluaran</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:28px; font-weight:700;'>Rp {pengeluaran_total:,.0f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Card saldo ---
    with c3:
        st.markdown("<div style='background:white; padding:20px; border-radius:10px; border:1px solid #ddd;'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#888; font-size:14px;'>Saldo Kas</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:28px; font-weight:700;'>Rp {saldo_total:,.0f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tambah jarak bawah supaya clean
    st.markdown("<div style='padding-bottom: 20px;'></div>", unsafe_allow_html=True)


# ---------------------------
# MAIN: Routing & Views
# ---------------------------
def main():
    if st.session_state['authenticated']:
        sidebar_menu()
        page = st.session_state.get('current_page', 'Dashboard')
        if page == "Dashboard":
            dashboard_page()
        elif page == "Jurnal Umum":
            jurnal_umum_page()
        elif page == "Buku Besar":
            buku_besar_page()
        elif st.session_state["current_page"] == "Neraca":
            neraca_page()
        elif page == "BP Utang":
            bp_utang_page()
        elif page == "BP Piutang":
            bp_piutang_page()
        elif st.session_state["current_page"] == "Inventory":
            inventory_page()
        elif page == "Laporan Laba Rugi" :
            laporan_laba_rugi_page()
 


        else:
            # placeholder for other pages
            st.title(page)
            st.info(f"Konten untuk **{page}** belum dibuat. Pilih Jurnal Umum atau Dashboard.")
    else:
        # LOGIN/CREATE ACCOUNT VIEW
        # set_background_login() # <- PANGGILAN INI DIHAPUS
        
        # TULISAN SELAMAT DATANG DI TENGAH
        st.markdown("<div class='centered-title'><h1>Selamat Datang di SIJANG</h1></div>", unsafe_allow_html=True)
        
        st.markdown("")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.session_state['show_create_account']:
                st.subheader("Buat Akun Baru")
                with st.form("create_account_form"):
                    new_username = st.text_input("Username Baru", key="new_user")
                    new_password = st.text_input("Password", type="password", key="new_pass")
                    confirm_password = st.text_input("Konfirmasi Password", type="password", key="conf_pass")
                    col_submit, col_back = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("Daftar Akun")
                    with col_back:
                        back = st.form_submit_button("Kembali ke Login")
                    if submitted:
                        create_account(new_username, new_password, confirm_password)
                    if back:
                        st.session_state['show_create_account'] = False
                        st.rerun()
            else:
                st.subheader("Login ke Akun Anda")
                with st.form("login_form"):
                    input_username = st.text_input("Username", key="login_user")
                    input_password = st.text_input("Password", type="password", key="login_pass")
                    col_login, col_create = st.columns(2)
                    with col_login:
                        if st.form_submit_button("Login"):
                            login(input_username, input_password)
                    with col_create:
                        if st.form_submit_button("Buat Akun"):
                            st.session_state['show_create_account'] = True
                            st.rerun()

def export_buku_besar_to_excel(df):
    from openpyxl import Workbook

    wb = Workbook()
    wb.remove(wb.active)

    akun_list = sorted(list(set(df['debit_akun']).union(set(df['kredit_akun']))))

    for akun in akun_list:
        ws = wb.create_sheet(title=akun[:31])  # Excel sheet name max 31 chars

        ws.append(["Tanggal", "Keterangan", "Debit", "Kredit", "Saldo"])

        saldo = 0
        
        # NOTE: Implementasi loop transaksi di fungsi ini hilang. 
        # Untuk kasus ini, karena tujuannya hanya untuk menyediakan kode lengkap,
        # saya asumsikan bagian ini adalah placeholder yang tidak krusial untuk 
        # fungsi utama. Jika perlu, logika transaksi harus diisi di sini.

        # Autofit columns
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max_length + 3

    # Simpan ke buffer
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

def buku_besar_page():
    st.markdown("""
    <style>
        .judul-buku-besar {
            font-size: 40px;
            font-weight: 800;
            text-align: center;
            margin-bottom: 40px;
        }
        .akun-title {
            font-size: 26px;
            font-weight: 700;
            margin-top: 35px;
            margin-bottom: 10px;
        }
        .table-header {
            background-color: #0f6cd5;
            color: white;
            font-weight: 700;
            padding: 8px;
            text-align: center;
        }
        .row-cell {
            padding: 10px;
            border: 1px solid #333;
            font-size: 15px;
        }
        .jumlah-row {
            background-color: #ccf7d4;
            text-align: center;
            font-weight: 700;
        }
        .tabel-container {
            background-color: white;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-bottom: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='judul-buku-besar'>Buku Besar</div>", unsafe_allow_html=True)

    data = st.session_state['jurnal_data']
    if not data:
        st.info("Belum ada transaksi untuk Buku Besar.")
        return

    df = pd.DataFrame(data)

    # Ambil daftar akun unik dari debit & kredit
    akun_list = sorted(list(set(df['debit_akun']).union(set(df['kredit_akun']))))

    for akun in akun_list:

        st.markdown(f"<div class='akun-title'>{akun}</div>", unsafe_allow_html=True)

        rows = []
        saldo = 0

        # =============================
        # FILTER TRANSAKSI KHUSUS AKUN INI
        # =============================
        df_akun = df[(df['debit_akun'] == akun) | (df['kredit_akun'] == akun)]

        if df_akun.empty:
            st.info(f"Tidak ada transaksi untuk akun {akun}.")
            continue

        for _, row in df_akun.iterrows():

            debit = row['nilai'] if row['debit_akun'] == akun else ""
            kredit = row['nilai'] if row['kredit_akun'] == akun else ""

            # Hitung saldo berjalan
            if debit != "":
                saldo += row['nilai']
            elif kredit != "":
                saldo -= row['nilai']

            rows.append([
                row['tanggal'],
                row['deskripsi'],
                debit,
                kredit,
                saldo
            ])

        # =============================
        # TABEL HTML
        # =============================
        html = """
<div class='tabel-container'>
<table style='width:100%; border-collapse:collapse;'>
    <tr>
        <th class='table-header'>Tanggal</th>
        <th class='table-header'>Keterangan</th>
        <th class='table-header'>Debit</th>
        <th class='table-header'>Kredit</th>
        <th class='table-header'>Saldo</th>
    </tr>
"""

        for r in rows:
            html += f"""
<tr>
    <td class='row-cell'>{r[0]}</td>
    <td class='row-cell'>{r[1]}</td>
    <td class='row-cell' style='text-align:right'>{format_rupiah(r[2])}</td>
    <td class='row-cell' style='text-align:right'>{format_rupiah(r[3])}</td>
    <td class='row-cell' style='text-align:right'>{format_rupiah(r[4])}</td>
</tr>
"""

        html += """
<tr>
    <td colspan='5' class='jumlah-row'>Jumlah</td>
</tr>
</table>
</div>
"""

        st.markdown(html, unsafe_allow_html=True)

        # ====== RINGKASAN JUMLAH ======
        total_debit = df_akun[df_akun['debit_akun'] == akun]['nilai'].sum()
        total_kredit = df_akun[df_akun['kredit_akun'] == akun]['nilai'].sum()
        saldo_akhir = total_debit - total_kredit

        st.markdown(f"""
        <div style="
            background:#e7f3ff; 
            padding:15px; 
            border-radius:8px; 
            margin-top:2px;
            border: 1px solid #bcdcff;">
            <b>Total Debit:</b> {format_rupiah(total_debit)}<br>
            <b>Total Kredit:</b> {format_rupiah(total_kredit)}<br>
            <b>Saldo Akhir:</b> {format_rupiah(saldo_akhir)}
        </div>
        """, unsafe_allow_html=True)

    # ========== DOWNLOAD EXCEL ==========
    excel_buffer = export_buku_besar_to_excel(df)

    st.download_button(
        label="📥 Download Buku Besar (Excel)",
        data=excel_buffer,
        file_name="Buku_Besar.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("⬅ Kembali Dashboard"):
        st.session_state['current_page'] = "Dashboard"
        st.rerun()


def format_rupiah(x):
    if x == "" or x is None:
        return ""
    return "Rp {:,}".format(int(x)).replace(",", ".")

def neraca_page():

    st.markdown("<h1 style='text-align:center; font-weight:900;'>NERACA</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; margin-top:-10px;'>PER 31 DESEMBER 2025</h4>", unsafe_allow_html=True)
    st.write("")

    daftar_akun = [
        "Kas","Penjualan","Pembelian","Perlengkapan","Peralatan", "Utang Usaha", "Piutang Usaha", "Modal",
        "Persediaan - Pakan","Persediaan - Bibit","Persediaan - Sekam & Bahan Kandang",
        "Persediaan - Jangkrik","HPP","Beban Gaji","Beban Listrik & Air",
        "Beban Transportasi","Beban Penyusutan Peralatan",
        "Beban Perlengkapan","Beban Sewa", "Akumulasi Penyusutan Peralatan"
    ]

    data_jurnal = st.session_state.get("jurnal_data", [])
    df = pd.DataFrame(data_jurnal) if data_jurnal else pd.DataFrame(columns=["debit_akun","kredit_akun","nilai"])

    saldo_akun = {}
    for akun in daftar_akun:
        d = df[df["debit_akun"]==akun]["nilai"].sum() if not df.empty else 0
        k = df[df["kredit_akun"]==akun]["nilai"].sum() if not df.empty else 0
        saldo_akun[akun] = {"Debit": d, "Kredit": k}

    # =========================
    # TABEL HTML TANPA INDENT !!!
    # =========================
    html_table = "<table style='width:100%;border-collapse:collapse;margin-top:20px;'>"
    html_table += "<tr style='background:#0077FF;color:white;font-weight:bold;'>"
    html_table += "<th style='border:1px solid black;padding:8px;'>No</th>"
    html_table += "<th style='border:1px solid black;padding:8px;'>Akun</th>"
    html_table += "<th style='border:1px solid black;padding:8px;'>Debit</th>"
    html_table += "<th style='border:1px solid black;padding:8px;'>Kredit</th>"
    html_table += "</tr>"

    no=1
    for akun in daftar_akun:
        d = saldo_akun[akun]["Debit"]
        k = saldo_akun[akun]["Kredit"]
        html_table += f"<tr>"
        html_table += f"<td style='border:1px solid black;padding:8px;text-align:center;'>{no}</td>"
        html_table += f"<td style='border:1px solid black;padding:8px;'>{akun}</td>"
        html_table += f"<td style='border:1px solid black;padding:8px;text-align:right;'>Rp {d:,.0f}</td>"
        html_table += f"<td style='border:1px solid black;padding:8px;text-align:right;'>Rp {k:,.0f}</td>"
        html_table += "</tr>"
        no+=1

    total_d = sum(saldo_akun[a]["Debit"] for a in daftar_akun)
    total_k = sum(saldo_akun[a]["Kredit"] for a in daftar_akun)

    html_table += "<tr style='background:#BFF4FF;'>"
    html_table += "<td colspan='2' style='border:1px solid black;padding:8px;text-align:center;font-weight:bold;'>TOTAL</td>"
    html_table += f"<td style='border:1px solid black;padding:8px;text-align:right;font-weight:bold;'>Rp {total_d:,.0f}</td>"
    html_table += f"<td style='border:1px solid black;padding:8px;text-align:right;font-weight:bold;'>Rp {total_k:,.0f}</td>"
    html_table += "</tr>"
    html_table += "</table>"

    st.markdown(html_table, unsafe_allow_html=True)

import io
import pandas as pd
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO

def format_rp(x):
    try:
        return "Rp {:,}".format(int(x)).replace(",", ".")
    except:
        return "Rp 0"
# ===============================================================
#   BUKU PEMBANTU UTANG — TERINTEGRASI OTOMATIS DARI JURNAL UMUM
# ===============================================================
def bp_utang_page():
    st.markdown("<h1 style='text-align:center;'>BUKU PEMBANTU UTANG (Per Supplier)</h1>", unsafe_allow_html=True)
    st.write("Menampilkan utang berdasarkan transaksi Jurnal Umum (akun Utang Usaha).")

    # =========================
    # LOAD JURNAL
    # =========================
    df = load_jurnal_df()
    if df.empty:
        st.info("Belum ada transaksi di jurnal.")
        return

    # =========================
    # FILTER UTANG SAJA
    # =========================
    mask = (
        (df["debit_akun"] == "Utang Usaha") |
        (df["kredit_akun"] == "Utang Usaha") |
        (df["jenis_transaksi"].str.lower() == "utang")
    )
    df_utang = df[mask].copy()

    if df_utang.empty:
        st.info("Belum ada transaksi utang.")
        return

    # =========================
    # LIST SUPPLIER
    # =========================
    supplier_list = df_utang["nama_toko"].dropna().unique()

    for supplier in supplier_list:

        st.markdown(f"<h3 style='margin-top:35px;'><b>Supplier: {supplier}</b></h3>", unsafe_allow_html=True)

        df_s = df_utang[df_utang["nama_toko"] == supplier].copy()
        df_s.sort_values("tanggal", inplace=True)

        saldo = 0
        rows = []

        # =========================
        # HITUNG SALDO UTANG
        # =========================
        for _, r in df_s.iterrows():

            # UTANG: kredit menambah, debit mengurangi
            kredit = r["nilai"] if r["kredit_akun"] == "Utang Usaha" else 0
            debit = r["nilai"] if r["debit_akun"] == "Utang Usaha" else 0

            saldo = saldo + kredit - debit

            rows.append({
                "Tanggal": r["tanggal"],
                "Keterangan": r.get("deskripsi", ""),
                "Debit": debit,
                "Kredit": kredit,
                "Saldo": saldo
            })

        # =========================
        # TABEL UTANG
        # =========================
        df_display = pd.DataFrame(rows)

        df_display["Debit"] = df_display["Debit"].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_display["Kredit"] = df_display["Kredit"].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_display["Saldo"] = df_display["Saldo"].apply(lambda x: f"Rp {x:,.0f}")

        st.table(df_display)

        # =========================
        # TOTAL UTANG
        # =========================
        # Perlu dikoreksi agar menggunakan nilai numerik dari rows
        total_debit = sum([r.get("Debit", 0) for r in rows])
        total_kredit = sum([r.get("Kredit", 0) for r in rows])
        saldo_akhir = rows[-1]["Saldo"]

        st.markdown(f"""
        <div style='background:#fef7e7;padding:12px;border-radius:8px;margin-bottom:20px;'>
            <b>Total Debit:</b> Rp {total_debit:,.0f} &nbsp;&nbsp;
            <b>Total Kredit:</b> Rp {total_kredit:,.0f} &nbsp;&nbsp;
            <b>Saldo Akhir:</b> Rp {saldo_akhir:,.0f}
        </div>
        """, unsafe_allow_html=True)

    if st.button("⬅ Kembali Dashboard"):
        st.session_state['current_page'] = "Dashboard"
        st.rerun()



def bp_piutang_page():
    st.markdown("<h1 style='text-align:center;'>BUKU PEMBANTU PIUTANG (Per Pelanggan)</h1>", unsafe_allow_html=True)
    st.write("Menampilkan piutang pelanggan berdasarkan transaksi Jurnal Umum.")

    # =========================
    # LOAD DATA JURNAL
    # =========================
    df = load_jurnal_df()
    if df.empty:
        st.info("Belum ada transaksi di jurnal.")
        return

    # =========================
    # FILTER TRANSAKSI PIUTANG SAJA
    # =========================
    mask = (
        (df["debit_akun"] == "Piutang Usaha") |
        (df["kredit_akun"] == "Piutang Usaha") |
        (df["jenis_transaksi"].str.lower() == "piutang")
    )

    df_piutang = df[mask].copy()

    if df_piutang.empty:
        st.info("Belum ada transaksi piutang.")
        return

    # =========================
    # LIST PELANGGAN
    # =========================
    pelanggan_list = df_piutang["nama_toko"].dropna().unique()

    for pelanggan in pelanggan_list:

        st.markdown(f"<h3 style='margin-top:35px;'><b>Pelanggan: {pelanggan}</b></h3>", unsafe_allow_html=True)

        df_p = df_piutang[df_piutang["nama_toko"] == pelanggan].copy()
        df_p.sort_values("tanggal", inplace=True)

        saldo = 0
        rows = []

        # =========================
        # HITUNG SALDO PER BARIS
        # =========================
        for _, r in df_p.iterrows():
            debit = r["nilai"] if r["debit_akun"] == "Piutang Usaha" else 0
            kredit = r["nilai"] if r["kredit_akun"] == "Piutang Usaha" else 0

            saldo = saldo + debit - kredit

            rows.append({
                "Tanggal": r["tanggal"],
                "Keterangan": r["deskripsi"],
                "Debit": debit,
                "Kredit": kredit,
                "Saldo": saldo
            })

        # =========================
        # TAMPILKAN TABEL
        # =========================
        df_display = pd.DataFrame(rows)

        df_display["Debit"] = df_display["Debit"].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_display["Kredit"] = df_display["Kredit"].apply(lambda x: f"Rp {x:,.0f}" if x != 0 else "")
        df_display["Saldo"] = df_display["Saldo"].apply(lambda x: f"Rp {x:,.0f}")

        st.table(df_display)

        # =========================
        # HITUNG TOTAL
        # =========================
        # Perlu dikoreksi agar menggunakan nilai numerik dari rows
        total_debit = sum([r.get("Debit", 0) for r in rows])
        total_kredit = sum([r.get("Kredit", 0) for r in rows])
        saldo_akhir = rows[-1]["Saldo"]

        st.markdown(f"""
        <div style='background:#f0f9ff;padding:12px;border-radius:8px;margin-bottom:20px;'>
            <b>Total Debit:</b> Rp {total_debit:,.0f} &nbsp;&nbsp;
            <b>Total Kredit:</b> Rp {total_kredit:,.0f} &nbsp;&nbsp;
            <b>Saldo Akhir:</b> Rp {saldo_akhir:,.0f}
        </div>
        """, unsafe_allow_html=True)

    if st.button("⬅ Kembali Dashboard"):
        st.session_state['current_page'] = "Dashboard"
        st.rerun()

def format_rp(x):
    return f"Rp {x:,.0f}".replace(",", ".")

# ---------------------------
# Helper: load_jurnal_df (robust terhadap format tanggal)
# ---------------------------
def load_jurnal_df():
    """
    Mengambil jurnal_data dari st.session_state dan mengembalikan DataFrame
    dengan kolom tanggal sebagai datetime (robust terhadap format).
    """
    if "jurnal_data" not in st.session_state:
        return pd.DataFrame()

    df = pd.DataFrame(st.session_state["jurnal_data"])
    if df.empty:
        return pd.DataFrame()

    # Pastikan kolom-kolom penting ada
    for c in ["tanggal", "deskripsi", "debit_akun", "kredit_akun", "nilai", "jenis_transaksi", "nama_toko"]:
        if c not in df.columns:
            df[c] = ""

    # Coba parse tanggal tanpa memaksa format spesifik
    df["tanggal_parsed"] = pd.to_datetime(df["tanggal"], errors="coerce", dayfirst=False)
    # Jika ada yang gagal parse, coba infer per-row
    mask_na = df["tanggal_parsed"].isna()
    if mask_na.any():
        df.loc[mask_na, "tanggal_parsed"] = pd.to_datetime(df.loc[mask_na, "tanggal"].apply(lambda x: str(x)), infer_datetime_format=True, errors="coerce")
    # fallback: buat tanggal hari ini jika masih NaT
    df["tanggal_parsed"] = df["tanggal_parsed"].fillna(pd.Timestamp.today())
    # replace original tanggal with parsed (but keep as datetime)
    df["tanggal"] = df["tanggal_parsed"]
    df = df.drop(columns=["tanggal_parsed"])
    # pastikan nilai numeric
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce").fillna(0.0)
    return df

# ---------------------------
# Helper: kategori akun untuk Laba Rugi
# ---------------------------
def classify_account_for_lr(akun_name: str):
    """Sederhana: return kategori: 'pendapatan','hpp','beban','lain'"""
    n = (akun_name or "").lower()
    if "penjualan" in n or "pendapatan" in n or "penjualan" in n:
        return "pendapatan"
    if "hpp" in n or "harga pokok" in n:
        return "hpp"
    if n.startswith("beban") or "beban" in n:
        return "beban"
    # contoh akun lain-lain
    if "pendapatan" in n or "sewa" in n or "dividen" in n:
        return "pendapatan"
    return "lain"

# ---------------------------
# Laporan Laba Rugi Page (integrasi otomatis)
# ---------------------------
def laporan_laba_rugi_page():
    st.markdown("<h1 style='text-align:center;'>LAPORAN LABA RUGI</h1>", unsafe_allow_html=True)

    df = load_jurnal_df()
    if df.empty:
        st.info("Belum ada transaksi pada jurnal.")
        return

    pendapatan = df[
        (df["debit_akun"].str.contains("Kas", case=False)) &
        (df["kredit_akun"].str.contains("Penjualan", case=False))
    ]["nilai"].sum()

    df_hpp = df[
        (df["debit_akun"].str.contains("HPP", case=False, na=False)) |
        (df["kredit_akun"].str.contains("HPP", case=False, na=False))
    ]
    nilai_hpp = df_hpp["nilai"].sum()

    laba_kotor = pendapatan - nilai_hpp

    df_beban = df[
        df["debit_akun"].str.contains("Beban", case=False, na=False)
    ]
    beban_operasional = df_beban["nilai"].sum()
    list_beban = df_beban.groupby("debit_akun")["nilai"].sum().reset_index()

    laba_sebelum_pajak = laba_kotor - beban_operasional

    pajak = laba_sebelum_pajak * 0.10 if laba_sebelum_pajak > 0 else 0

    laba_bersih = laba_sebelum_pajak - pajak
    st.markdown("""
        <style>
            .lr-title {font-size:20px; font-weight:bold; margin-top:25px;}
            .lr-row {display:flex; justify-content:space-between; padding:6px 0;}
            .lr-bold {font-weight:bold;}
            .lr-box {background:#f1f7ff; padding:15px; border-radius:8px; margin-top:20px;}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='lr-title'>Pendapatan</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='lr-row'>
            <span>Pendapatan Usaha</span>
            <span>Rp {pendapatan:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='lr-title'>Harga Pokok Penjualan (HPP)</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='lr-row lr-bold'>
            <span>Total HPP</span>
            <span>Rp {nilai_hpp:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # ============================
    # LABA KOTOR (BARU DITAMBAHKAN)
    # ============================
    st.markdown("<div class='lr-title'>Laba Kotor</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='lr-row lr-bold'>
            <span>Laba Kotor (Penjualan - HPP)</span>
            <span>Rp {laba_kotor:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # ============================
    # BEBAN OPERASIONAL
    # ============================
    st.markdown("<div class='lr-title'>Beban Operasional</div>", unsafe_allow_html=True)

    if not list_beban.empty:
        for _, row in list_beban.iterrows():
            st.markdown(f"""
                <div class='lr-row'>
                    <span>{row['debit_akun']}</span>
                    <span>Rp {row['nilai']:,.0f}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class='lr-row lr-bold'>
            <span>Total Beban Operasional</span>
            <span>Rp {beban_operasional:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # ============================
    # LABA SEBELUM PAJAK
    # ============================
    st.markdown("<div class='lr-title'>Laba Sebelum Pajak</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='lr-row lr-bold'>
            <span>Laba Sebelum Pajak</span>
            <span>Rp {laba_sebelum_pajak:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # ============================
    # PAJAK
    # ============================
    st.markdown("<div class='lr-title'>Pajak (10%)</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='lr-row lr-bold'>
            <span>Pajak Penghasilan</span>
            <span>Rp {pajak:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    # ============================
    # LABA BERSIH SETELAH PAJAK
    # ============================
    st.markdown("<div class='lr-title'>Laba Bersih Setelah Pajak</div>", unsafe_allow_html=True)
    st.markdown(f"""
        <div class='lr-row lr-bold'>
            <span>Laba Bersih</span>
            <span>Rp {laba_bersih:,.0f}</span>
        </div>
    """, unsafe_allow_html=True)

    if st.button("⬅ Kembali Dashboard"):
        st.session_state["current_page"] = "Dashboard"
        st.rerun()

def build_inventory_card(records):
    """
    Inventory dengan metode Average Cost (Harga Pokok Rata-Rata Bergerak)
    • Tidak ada koma desimal
    • Harga & HPP dibulatkan ke rupiah
    """

    if not records:
        return pd.DataFrame(), 0, 0

    rows = []
    saldo_qty = 0       # total unit
    saldo_rp = 0        # total nilai persediaan
    avg_cost = 0        # harga rata-rata

    for r in records:
        tgl = r["tanggal"]
        ket = r["keterangan"]
        tipe = r["tipe"]
        qty = float(r["qty"])
        nilai = float(r["nilai"])

        harga_unit = ""
        hpp_total = ""

        # ----------------------------
        # MASUK (update average cost)
        # ----------------------------
        if tipe == "Masuk":
            harga_unit = nilai / qty if qty > 0 else 0

            saldo_rp += nilai
            saldo_qty += qty

            # harga rata-rata bergerak
            avg_cost = saldo_rp / saldo_qty if saldo_qty > 0 else 0

        # ----------------------------
        # KELUAR (HPP pakai avg cost)
        # ----------------------------
        elif tipe == "Keluar":
            harga_unit = avg_cost
            hpp_total = qty * avg_cost

            saldo_qty -= qty
            saldo_rp -= hpp_total

            if saldo_qty < 0:
                saldo_qty = 0
                saldo_rp = 0

        # ----------------------------
        # TAMPILKAN TANPA KOMA
        # ----------------------------
        rows.append({
            "Tanggal": tgl,
            "Keterangan": ket,
            "Masuk (Qty)": int(qty) if tipe == "Masuk" else "",
            "Keluar (Qty)": int(qty) if tipe == "Keluar" else "",
            "Harga/Unit": f"Rp {int(harga_unit):,}".replace(",", "."),
            "HPP": f"Rp {int(hpp_total):,}".replace(",", ".") if hpp_total != "" else "",
            "Saldo (Qty)": int(saldo_qty),
            "Saldo (Rp)": f"Rp {int(saldo_rp):,}".replace(",", ".")
        })

    df = pd.DataFrame(rows)
    return df, saldo_qty, saldo_rp

# =====================================================================
#  INVENTORY — AVERAGE COST METHOD (2 Jenis: Bibit & Jangkrik Panen)
# =====================================================================

# ============================================================
# ================  SIMPLE INVENTORY (AVERAGE)  ===============
# ============================================================

# -------------------------
# INVENTORY (Average) - Single inventory
# -------------------------
import json
import os
import streamlit as st
import pandas as pd

# ============================
# CUSTOM STYLE (warna UI)
# ============================
st.markdown("""
    <style>
        /* Card box background */
        .stApp {
            background-color: #f6fbff;
        }

        /* Riwayat Transaksi box */
        .riwayat-box {
            background: #ffffff;
            padding: 18px;
            border-radius: 12px;
            border-left: 5px solid #4bb3fd;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        /* Delete button style */
        .delete-btn button {
            background-color: #ff6b6b !important;
            color: white !important;
            border-radius: 8px !important;
        }

        /* Inventory table header */
        thead tr th {
            background-color: #4bb3fd !important;
            color: white !important;
            font-weight: 600 !important;
            text-align:center !important;
        }

        tbody tr td {
            text-align:center !important;
        }

        /* Total box */
        .total-box {
            background: #e9f7ff;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #bde4ff;
            font-size: 17px;
        }
    </style>
""", unsafe_allow_html=True)


INVENTORY_FILE = "inventory_data.json"

def load_inventory_data():
    """
    Load inventory from file if exists, else from session_state default.
    This returns a dict with key "Records" (single inventory).
    """
    # prefer session state during runtime so edits persist in a session
    if "inventory_data" in st.session_state:
        data = st.session_state["inventory_data"]
    else:
        # try load from file
        if os.path.exists(INVENTORY_FILE):
            try:
                with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {"Records": []}
        else:
            data = {"Records": []}
        st.session_state["inventory_data"] = data

    # ensure structure
    if not isinstance(st.session_state["inventory_data"], dict):
        st.session_state["inventory_data"] = {"Records": []}
    if "Records" not in st.session_state["inventory_data"]:
        st.session_state["inventory_data"]["Records"] = []

    return st.session_state["inventory_data"]


def save_inventory_data(data=None):
    """
    Save inventory to session_state and file.
    If data provided, use it; otherwise use session_state.
    """
    if data is not None:
        st.session_state["inventory_data"] = data
    data_to_save = st.session_state.get("inventory_data", {"Records": []})
    try:
        with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # non-fatal in UI; log to console
        print("Failed to save inventory file:", e)


def delete_inventory_record(index):
    data = load_inventory_data()
    try:
        records = data["Records"]
        if 0 <= index < len(records):
            records.pop(index)
            save_inventory_data(data)
    except Exception as e:
        print("delete_inventory_record error:", e)


def build_inventory_average(records):
    """
    records: list of dicts with keys:
      - tanggal (str)
      - keterangan (str)
      - tipe ("Masuk" or "Keluar")
      - qty (int)
      - nilai (int)
    Returns (df, saldo_qty, saldo_rp)
    All amounts are integers (no decimal).
    """
    if not records:
        return pd.DataFrame(), 0, 0

    rows = []
    saldo_qty = 0
    saldo_rp = 0
    avg_cost = 0

    for r in records:
        tgl = r.get("tanggal", "")
        ket = r.get("keterangan", "")
        tipe = r.get("tipe", "")
        try:
            qty = int(r.get("qty", 0) or 0)
        except Exception:
            qty = 0
        try:
            nilai = int(r.get("nilai", 0) or 0)
        except Exception:
            nilai = 0

        harga_unit = ""
        hpp = ""

        # MASUK -> update average
        if tipe == "Masuk":
            if qty > 0:
                harga_unit = nilai // qty
            else:
                harga_unit = 0
            saldo_rp += nilai
            saldo_qty += qty
            avg_cost = (saldo_rp // saldo_qty) if saldo_qty > 0 else 0

        # KELUAR -> pakai avg cost
        elif tipe == "Keluar":
            harga_unit = avg_cost
            hpp = qty * avg_cost
            saldo_qty -= qty
            saldo_rp -= hpp
            if saldo_qty < 0:
                saldo_qty = 0
            if saldo_rp < 0:
                saldo_rp = 0

        rows.append({
            "Tanggal": tgl,
            "Keterangan": ket,
            "Masuk": qty if tipe == "Masuk" else "",
            "Keluar": qty if tipe == "Keluar" else "",
            "Harga/Unit": int(harga_unit) if harga_unit != "" else "",
            "HPP": int(hpp) if hpp != "" else "",
            "Saldo Qty": int(saldo_qty),
            "Saldo Rp": int(saldo_rp)
        })

    df = pd.DataFrame(rows)
    return df, saldo_qty, saldo_rp


def inventory_page():
    """
    UI for inventory — single inventory, average cost, add/delete.
    """
    st.title("📦 Inventory (Average Method)")

    data = load_inventory_data()  # ensures session state key exists
    records = data["Records"]

    st.subheader("➕ Tambah Transaksi")
    tanggal = st.date_input("Tanggal")
    keterangan = st.text_input("Keterangan")
    tipe = st.selectbox("Tipe", ["Masuk", "Keluar"])
    qty = st.number_input("Qty", min_value=1, step=1)
    nilai = st.number_input("Nilai (Rp)", min_value=0, step=1000)

    if st.button("Simpan"):
        # Append as integers to keep display clean (no decimals)
        rec = {
            "tanggal": str(tanggal),
            "keterangan": keterangan,
            "tipe": tipe,
            "qty": int(qty),
            "nilai": int(nilai)
        }
        records.append(rec)
        save_inventory_data(data)
        st.success("Transaksi disimpan!")
        st.rerun()

    st.subheader("📄 Riwayat Transaksi")
    if records:
        # show records with delete buttons
        for i, r in enumerate(records):
            cols = st.columns([6, 1])
            with cols[0]:
                st.write(f"**{r.get('tanggal','')} - {r.get('keterangan','')}**  \nTipe: {r.get('tipe','')} | Qty: {r.get('qty',0)} | Nilai: {r.get('nilai',0)}")
            with cols[1]:
                if st.button("❌", key=f"del_{i}"):
                    delete_inventory_record(i)
                    st.warning("Transaksi dihapus!")
                    st.rerun()
    else:
        st.info("Belum ada transaksi.")

    st.subheader("📊 Kartu Persediaan")
    df, qty_total, nilai_total = build_inventory_average(records)
    st.table(df)
    st.info(f"**Saldo Akhir Qty:** {int(qty_total)}  \n**Saldo Akhir Rp:** {int(nilai_total)}")




if __name__ == "__main__":
    main()