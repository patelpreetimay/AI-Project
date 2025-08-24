from pydantic import BaseModel

class Chunk(BaseModel):
    text: str
    pdf: str
    chunk_id: int
