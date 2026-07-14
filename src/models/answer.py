from pydantic import Field
from src.models.query import DataQuerySchema

class AnswerSchema(DataQuerySchema):
    response_template: str = Field(
        description="Template kalimat balasan untuk menjawab pertanyaan pengguna (misal: 'Berikut adalah data total profit...'). Tidak perlu menyertakan nilai asli jika belum diketahui."
    )
