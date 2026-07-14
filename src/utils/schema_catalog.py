from typing import Dict, List

# Dictionary yang menyimpan seluruh metadata kolom secara terstruktur
SUPERSTORE_SCHEMA: Dict[str, str] = {
    "order_id": "ID unik pesanan/transaksi (string)",
    "gmv": "Nilai Penjualan atau Gross Merchandise Value (float)",
    "profit": "Keuntungan yang dihasilkan dari penjualan (float)",
    "profit_margin": "Persentase margin keuntungan dari gmv (float, gunakan agregasi 'mean')",
    "quantity": "Jumlah barang yang dibeli dalam satu transaksi (integer)",
    "category": "Kategori Produk utama seperti Technology, Office Supplies, Furniture (string)",
    "sub_category": "Sub-kategori spesifik produk (string)",
    "cost": "Biaya modal atau harga pokok pengadaan (float)",
    "order_date": "Tanggal pesanan dilakukan (date)",
    "ship_date": "Tanggal barang dikirim (date)",
    "customer_name": "Nama lengkap pelanggan (string)",
    "segment": "Segmen pasar pelanggan, misal: Consumer, Corporate, Home Office (string)",
    "city": "Kota tujuan pengiriman barang (string)",
    "country": "Negara tujuan pengiriman (string)",
    "region": "Wilayah geografis pengiriman, misal: Central, North, South (string)",
    "ship_mode": "Metode atau mode pengiriman (string)",
    "lon": "Koordinat garis bujur lokasi (float)",
    "lat": "Koordinat garis lintang lokasi (float)",
    "shipping_days": "Waktu yang dibutuhkan untuk pengiriman logistik dalam hari (integer/float)",
    "order_year": "Tahun transaksi pemesanan dilakukan, misal: 2023, 2024 (integer)",
    "order_month": "Bulan transaksi dilakukan, misal: January, February (string)",
    "unit_price": "Harga satuan rata-rata per barang (float)",
    "is_profitable": "Status profitabilitas transaksi bernilai 'Untung' atau 'Rugi' (string)"
}

def get_all_columns_with_descriptions() -> str:
    """Mengembalikan daftar kolom beserta deskripsinya untuk agen selector agar lebih aman/akurat."""
    lines = []
    for col, desc in SUPERSTORE_SCHEMA.items():
        lines.append(f"- {col}: {desc}")
    return "\n".join(lines)

def build_schema_context(selected_columns: List[str]) -> str:
    """Membangun teks konteks skema secara dinamis HANYA dari kolom yang dipilih (untuk Planner)."""
    if not selected_columns:
        return "Tidak ada kolom spesifik yang direferensikan."
        
    context_lines = ["Kolom yang difilter dan tersedia untuk digunakan:"]
    for col in selected_columns:
        # Jika LLM salah memberikan nama kolom, kita abaikan secara aman
        if col in SUPERSTORE_SCHEMA:
            context_lines.append(f"- {col}: {SUPERSTORE_SCHEMA[col]}")
            
    return "\n".join(context_lines)
