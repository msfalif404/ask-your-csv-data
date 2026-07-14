from pydantic import BaseModel, Field
from typing import Literal

class IntentRouterSchema(BaseModel):
    intent: Literal["answer_question", "visualization", "out_of_domain"] = Field(
        description="Pilih 'visualization' jika minta grafik. Pilih 'answer_question' jika bertanya soal nilai/insight data. Pilih 'out_of_domain' jika pertanyaan pengetahuan umum atau sama sekali tidak terkait data bisnis."
    )
