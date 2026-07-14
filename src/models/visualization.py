from pydantic import Field
from typing import Literal, Optional
from src.models.query import DataQuerySchema

class VisualizationSchema(DataQuerySchema):
    chart_type: Literal["line", "bar", "scatter", "histogram", "pie", "box"] = Field(
        description="Tipe visualisasi yang paling cocok untuk menampilkan data"
    )
    x_axis: str = Field(description="Nama kolom untuk sumbu X (atau kategori pada pie chart)")
    y_axis: str = Field(description="Nama kolom untuk sumbu Y (metrik atau values pada pie chart)")
    color: Optional[str] = Field(None, description="Kolom untuk legend atau pengelompokan warna (opsional)")
    
    title: str = Field(description="Judul utama grafik")
    x_axis_title: Optional[str] = Field(None, description="Label untuk sumbu X")
    y_axis_title: Optional[str] = Field(None, description="Label untuk sumbu Y")
    
    insight_text: str = Field(description="Satu kalimat pengantar yang akan ditampilkan sebelum grafik diberikan")
