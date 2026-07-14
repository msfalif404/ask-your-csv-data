from pydantic import BaseModel, Field
from typing import List

class ColumnSelectorSchema(BaseModel):
    selected_columns: List[str] = Field(
        description="Daftar nama kolom yang relevan untuk menjawab pertanyaan pengguna secara spesifik."
    )
    reasoning: str = Field(
        description="Alasan singkat mengapa Anda memilih kolom-kolom tersebut."
    )
