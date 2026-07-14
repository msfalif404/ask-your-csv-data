from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class QueryFilter(BaseModel):
    column: str = Field(description="Nama kolom untuk difilter")
    operator: Literal["==", "!=", ">", "<", ">=", "<=", "in"] = Field(description="Operator perbandingan")
    value: str = Field(description="Nilai filter")

class SortConfig(BaseModel):
    column: str = Field(description="Nama kolom yang akan diurutkan")
    ascending: bool = Field(default=False, description="True untuk urutan A-Z atau terkecil ke terbesar, False untuk sebaliknya")

class DataQuerySchema(BaseModel):
    metrics: List[str] = Field(description="Daftar kolom numerik untuk dihitung (contoh: ['profit', 'gmv'])")
    aggregation: Literal["sum", "mean", "count", "min", "max", "none"] = Field(description="Fungsi agregasi yang akan diterapkan pada metrics")
    group_by: Optional[List[str]] = Field(default=[], description="Daftar kolom kategorikal untuk pengelompokan data")
    filters: Optional[List[QueryFilter]] = Field(default=[], description="Kondisi filter data sebelum diagregasi")
    sort: Optional[SortConfig] = Field(default=None, description="Konfigurasi pengurutan data hasil query")
    limit: Optional[int] = Field(default=None, description="Batasi jumlah baris yang dikembalikan (contoh: 5 untuk 'Top 5')")
