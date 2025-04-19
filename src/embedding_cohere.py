import time
import cohere
# co = cohere.Client('Gv9P2p1ZNgrp2bUdBK4pfNdpZcLPXuc0AHtAer5z')

# response = co.embed(
#   model='embed-v4.0',
#   texts=["hi", "hello"],
#   input_type='classification',
#   truncate='NONE'
# )

# print('Embeddings: {}'.format(response.embeddings), sep='\n')

from typing import List

class EmbeddingClient:
    
    def __init__(self):
        self.model='embed-v4.0'
        self.client = cohere.Client('Gv9P2p1ZNgrp2bUdBK4pfNdpZcLPXuc0AHtAer5z')
        
    def get_text_embedding(self, texts: List[str]):
        response = self.client.embed(
            model=self.model,
            texts=texts,
            input_type='search_document'
            )
        time.sleep(0.6 * 4)
        return response.embeddings
    
    def get_query_embedding(self, texts: List[str]):
        response = self.client.embed(
            model=self.model,
            texts=texts,
            input_type='search_document'
            )
        return response.embeddings

if __name__ == "__main__":
    a = EmbeddingClient()
    print(a.get_text_embedding(["ads"]))
    