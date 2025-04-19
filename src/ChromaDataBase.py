import sys
import PyPDF2
import chromadb
from .embedding import EmbeddingClient
import uuid
from .colors import *
from concurrent.futures import ThreadPoolExecutor, as_completed
from .env import *



class ChromaDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(DATABASE_PATH)
        self.collection = self.client.get_or_create_collection("ustaff-collection")
        self.embedding = EmbeddingClient()

    def _add_chunk(self, content: str, filesrc: str) -> None:
        max_retries = 6
        for attempt in range(max_retries):
            try:
                self.collection.add(
                    documents=[content],
                    metadatas=[
                    {
                        "filesrc": filesrc,
                    }
                    ],
                    ids=[str(uuid.uuid4())],
                    embeddings=[self.embedding.get_text_embedding([f"[filename] {filesrc} [content]{content}"])[0]],
                )
                break  # Success - exit the retry loop
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    # print(f"{RED}Failed to add chunk after {max_retries} attempts: {str(e)} {RESET}", file=sys.stderr)
                    raise  # Re-raise the last exception
                # print(f"{RED} Attempt {attempt + 1} failed, retrying...{RESET}", file=sys.stderr)

    def _split_into_chunks(self, text: str, chunk_size: int = 200, overlap: int = 10) -> list[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def add_document(self, filename: str) -> None:
        """
        Add a document to the collection.
        """
        file_extension = filename.lower().split('.')[-1]

        if file_extension == 'pdf':
            content = self.extract_text_from_pdf(filename)
        elif file_extension in ['txt', 'md', 'py', 'js', 'html', 'css']:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            raise ValueError(f"Unsupported file extension: .{file_extension}")

        if content is None:
            raise ValueError(f"Failed to read content from file: {filename}")
        
        # processing content ans a raw string
        chunks = self._split_into_chunks(content)
        total_chunks = len(chunks)
        processed_chunks = 0

        def process_chunk(chunk_data):
            chunk, idx = chunk_data
            self._add_chunk(chunk, filename)
            return idx

        with ThreadPoolExecutor(max_workers=4) as executor:
            # Create futures for all chunks
            futures = {executor.submit(process_chunk, (chunk, i)): i 
                  for i, chunk in enumerate(chunks, 1)}
            
            # Process as they complete
            for future in as_completed(futures):
                processed_chunks += 1
                progress = (processed_chunks / total_chunks) * 100
                bar_length = 60
                filled_length = int(bar_length * processed_chunks // total_chunks)
                bar = "=" * filled_length + " " * (bar_length - filled_length)
                print(f"\rProgress: {YELLOW}<{bar}>{RESET} {progress:.1f}% ({processed_chunks}/{total_chunks})", 
                    end="", flush=True)

        print()  # New line after progress complete
        print(f"Document added with filename:{MAGENTA} {filename} {RESET} ({total_chunks} chunks)")
    
    def search(self, query:str, n=10):
        max_retries = 3
        results = None
        
        # Search by filename embedding with retry
        q_embedding = self.embedding.get_query_embedding([query])[0]
        for attempt in range(max_retries):
            try:
                results = self.collection.query(
                    query_embeddings=[q_embedding],
                    n_results=n,
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"{RED}Failed filename search after {max_retries} attempts: {str(e)} {RESET}", file=sys.stderr)
                    raise
                print(f"{RED}Filename search attempt {attempt + 1} failed, retrying...{RESET}", file=sys.stderr)

        return results
    
        
    def extract_text_from_pdf(self, pdf_path):
        try:
            # Open the PDF file in read-binary mode
            with open(pdf_path, "rb") as pdf_file:
                # Create a PDF reader object
                reader = PyPDF2.PdfReader(pdf_file)
                extracted_text = ""

                for page in reader.pages:
                    extracted_text += page.extract_text()
                
                return extracted_text
        except Exception as e:
            print(f"An error occurred: {e}")
            return None