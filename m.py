import src.ChromaDataBase as CD
from pprint import pprint

db = CD.ChromaDB()


pprint(db.search("Стек протоколов TCP/IP"))
