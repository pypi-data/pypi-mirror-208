from abc import abstractmethod
from pydantic import BaseModel
import json

class BaseModelWithExample(BaseModel):
    @abstractmethod
    def get_example(self) -> str:
        pass

class DBConfig(BaseModelWithExample):
  host: str
  user: str
  password: str
  port: int = 5432
  ssl: bool = False

  @classmethod
  def get_example(cls) -> str:
    return json.dumps(DBConfig(host="host", user="user", password="password").dict(), indent=2)

class GGAPIConfig(BaseModelWithExample):
  api_key: str

  @classmethod
  def get_example(cls) -> str:
    return json.dumps(GGAPIConfig(api_key="qwerty1234").dict(), indent=2)
  
class HashID(BaseModelWithExample):
  hash: str

  @classmethod
  def get_example(cls) -> str:
    return json.dumps(HashID(hash="qwerty1234").dict(), indent=2)

