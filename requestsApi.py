from pydantic import BaseModel
from typing import Optional

class UpdateUrlRequest(BaseModel):
    url:str 


