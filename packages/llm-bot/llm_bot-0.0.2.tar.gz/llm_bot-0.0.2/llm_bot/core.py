# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from pathlib import Path
import pickle
import tarfile
from typing import Dict, List, Tuple, Union

import faiss
from faiss import IndexFlat
from langchain.chat_models.openai import ChatOpenAI
from langchain.docstore.document import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import requests

CONTEXT_INDEX_FILENAME = "index.faiss"
CONTEXT_STORE_FILENAME = "store.pickle"
CHAT_INDEX_FILENAME = "chat_index.faiss"
CHAT_STORE_FILENAME = "chat_store.pickle"


class BaseLLMBot(ABC):
    def __init__(
        self,
        text_chunk_size: int = 1000,
        text_chunk_overlap: int = 250,
        text_separators: List[str] = [" ", ".", ",", ";", ":", "!", "?", "\n"],
        temperature: float = 0,
    ):
        self._store: FAISS = None
        self._chat_store: FAISS = None
        self._chat = ChatOpenAI(temperature=temperature)
        self._text_chunk_size = text_chunk_size
        self._text_chunk_overlap = text_chunk_overlap
        self._text_separators = text_separators

    @abstractmethod
    def train(self, *args, **kwargs) -> None:
        """
        Builds the index and the vector store from the given data.
        """

    @abstractmethod
    def add_to_index(self, *args, **kwargs) -> None:
        """
        Adds the given data to the index and the vector store.
        """

    def fetch_from_index(
        self, query: str, n_results: int, index: str = "context"
    ) -> List[Document]:
        """
        Fetches the most relevant documents from the index.

        Args:
            query (str): The query to search for.
            n_results (int): The number of results to return.

        Returns:
            List[Document]: The most relevant documents.
        """
        if index == "context":
            docs: List[Document] = self._store.similarity_search(query, k=n_results)
        elif index == "chat_history":
            if self._chat_store is None:
                raise ValueError("No chat history available.")
            docs: List[Document] = self._chat_store.similarity_search(
                query, k=n_results
            )
        else:
            raise ValueError(f"Invalid index '{index}'.")
        return docs

    def save(self, path: Union[str, Path]) -> None:
        """
        Saves the index and the vector store to the given path.

        Args:
            path (Union[str, Path]): The path to save the index and vector store to.
        """
        # Assert that the path exists
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Save the indexes
        index_fname = str(path / CONTEXT_INDEX_FILENAME)
        faiss.write_index(self._store.index, index_fname)
        if self._chat_store is not None:
            chat_index_fname = str(path / CHAT_INDEX_FILENAME)
            faiss.write_index(self._chat_store.index, chat_index_fname)

        # Save the vector stores
        index = self._store.index
        self._store.index = None
        store_fname = str(path / CONTEXT_STORE_FILENAME)
        with open(store_fname, "wb") as f:
            pickle.dump(self._store, f)
        self._store.index = index
        if self._chat_store is not None:
            index = self._chat_store.index
            self._chat_store.index = None
            chat_store_fname = str(path / CHAT_STORE_FILENAME)
            with open(chat_store_fname, "wb") as f:
                pickle.dump(self._chat_store, f)
            self._chat_store.index = index

    def download(self, url: str, path: Union[str, Path]) -> None:
        """
        Downloads the model (index + vector store) from a given URL and extracts it to the given
        path.

        Args:
            url (str): The URL to download the model from.
            path (Union[str, Path]): The path to extract the model to.
        """
        # Assert that the path exists
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        # Download the model
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Determine compression format based on file extension
        filename = Path(url).name
        if filename.endswith(".tar.gz"):
            mode = "r|gz"
        elif filename.endswith(".tar.bz2"):
            mode = "r|bz2"
        elif filename.endswith(".tar.xz"):
            mode = "r|xz"
        elif filename.endswith(".tar"):
            mode = "r|"
        else:
            raise ValueError(f"Unknown compression format for file: {filename}")

        # Extract the model
        with tarfile.open(fileobj=response.raw, mode=mode) as tar:
            tar.extractall(path=path)

        # Assert that we have the correct files. If we don't, then we need to delete the files
        index_fname = path / CONTEXT_INDEX_FILENAME
        store_fname = path / CONTEXT_STORE_FILENAME
        try:
            assert index_fname.exists() and store_fname.exists()
        except AssertionError as exc:
            index_fname.unlink(missing_ok=True)
            store_fname.unlink(missing_ok=True)
            raise AssertionError(
                f"Either {index_fname} or {store_fname} does not exist."
            ) from exc

    def load(self, path: Union[str, Path]) -> None:
        """
        Loads the index and the vector store from the given path.

        Args:
            path (Union[str, Path]): The path to load the index and vector store from.
        """
        # Assert that the path exists
        path = Path(path)
        assert path.exists(), f"Path {path} does not exist."

        # Assert that both files exist
        index_fname = path / CONTEXT_INDEX_FILENAME
        store_fname = path / CONTEXT_STORE_FILENAME
        assert (
            index_fname.exists() and store_fname.exists()
        ), f"Either {index_fname} or {store_fname} does not exist."

        # Load the index
        index: IndexFlat = faiss.read_index(str(index_fname))

        # Load the vector store
        with open(store_fname, "rb") as f:
            self._store: FAISS = pickle.load(f)
        self._store.index = index

        # Load chat stuff if it exists
        chat_index_fname = path / CHAT_INDEX_FILENAME
        chat_store_fname = path / CHAT_STORE_FILENAME
        if chat_index_fname.exists() and chat_store_fname.exists():
            chat_index: IndexFlat = faiss.read_index(str(chat_index_fname))
            with open(chat_store_fname, "rb") as f:
                self._chat_store: FAISS = pickle.load(f)
            self._chat_store.index = chat_index

    def build_messages(
        self,
        personality_prompt: str,
        user_message: str,
        use_chat_history: bool = True,
        chat_history_prompt: str = "Aqui está o histórico da conversa até agora:",
        number_of_chat_history_docs: int = 2,
        use_context: bool = True,
        context_prompt: str = "Aqui estão pedaços de informação que você pode usar:",
        number_of_context_docs: int = 2,
    ) -> Tuple[List[BaseMessage], List[str]]:
        """
        Builds a list of messages to send to the chatbot.

        Args:
            personality_prompt (str): The prompt to use for the personality.
            user_message (str): The message from the user.
            use_chat_history (bool, optional): Whether to use the chat history. Defaults to True.
            chat_history_prompt (str, optional): The prompt to use for the chat history. Defaults
                to "Aqui está o histórico da conversa até agora:".
            use_context (bool, optional): Whether to search for context documents in the vector
                store. Defaults to True.
            context_prompt (str, optional): The prompt to use for the context documents. Defaults
                to "Aqui estão pedaços de informação que você pode usar:".
            number_of_context_docs (int, optional): The number of context documents to use. Defaults
                to 2.

        Returns:
            Tuple[List[BaseMessage], List[str]]: A tuple containing the list of messages to send to
                the chatbot and the list of sources of the context documents.
        """
        # Start list of messages with the personality prompt
        messages: List[BaseMessage] = [SystemMessage(content=personality_prompt)]

        # If we are using context, search for context documents and add them to the prompt
        sources: List[str] = []
        if use_context:
            messages.append(SystemMessage(content=context_prompt))
            docs = self.fetch_from_index(
                query=user_message, n_results=number_of_context_docs, index="context"
            )
            sources = list(set([doc.metadata["source"] for doc in docs]))
            for doc in docs:
                messages.append(SystemMessage(content=f"- {doc.page_content}"))

        # If chat history is provided, add messages for it
        if use_chat_history:
            if self._chat_store:
                messages.append(SystemMessage(content=chat_history_prompt))
                docs = self.fetch_from_index(
                    query=user_message,
                    n_results=number_of_chat_history_docs,
                    index="chat_history",
                )
                for doc in docs:
                    messages.append(SystemMessage(content=f"- {doc.page_content}"))
                self._chat_store.add_texts(
                    texts=[f"User: {user_message}"],
                    metadatas=[{"source": "user"}],
                )
            else:
                embedding = OpenAIEmbeddings()
                self._chat_store = FAISS.from_texts(
                    texts=[f"User: {user_message}"],
                    embedding=embedding,
                    metadatas=[{"source": "user"}],
                )

        # Add the user message
        messages.append(HumanMessage(content=user_message))

        return messages, sources

    def chat(self, messages: List[BaseMessage]) -> str:
        """
        Sends the given messages to the chatbot and returns the response.

        Args:
            messages (List[BaseMessage]): The messages to send to the chatbot.
        """
        # Send the messages to the chatbot
        ai_message = self._chat(messages)

        # Get the response, add to index and return
        response = ai_message.content
        if self._chat_store:
            self._chat_store.add_texts(
                texts=[f"Bot: {response}"],
                metadatas=[{"source": "bot"}],
            )
        else:
            embedding = OpenAIEmbeddings()
            self._chat_store = FAISS.from_texts(
                texts=[f"Bot: {response}"],
                embedding=embedding,
                metadatas=[{"source": "bot"}],
            )
        return response


class HTMLBot(BaseLLMBot):
    def train(self, documents_path: Union[str, Path]) -> None:
        """
        Trains the bot using the given documents.

        Args:
            documents_path (Union[str, Path]): The path to the documents to use for training.
            text_chunk_size (int, optional): The size of the text chunks to use for training.
                Defaults to 1000.
            text_chunk_overlap (int, optional): The overlap between text chunks. Defaults to 250.
            text_separators (List[str], optional): The list of text separators to use for splitting
                the text into chunks. Defaults to [" ", ".", ",", ";", ":", "!", "?", "\n"].
        """
        # Import stuff (importing here avoids unnecessary dependencies)
        from langchain.document_loaders import BSHTMLLoader

        # Assert that the path exists
        documents_path = Path(documents_path)
        assert documents_path.exists(), f"Path {documents_path} does not exist."

        # Load the knowledge base
        loaders: List[BSHTMLLoader] = []
        for html_file in documents_path.glob("**/*.html"):
            loaders.append(BSHTMLLoader(html_file))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._text_chunk_size,
            chunk_overlap=self._text_chunk_overlap,
            separators=self._text_separators,
        )
        docs: List[Document] = []
        for loader in loaders:
            docs.extend(loader.load_and_split(text_splitter=text_splitter))

        # Create the vector store
        embedding = OpenAIEmbeddings()
        self._store = FAISS.from_documents(documents=docs, embedding=embedding)

    def add_to_index(self, html_files: List[Union[str, Path]]) -> None:
        """
        Adds the given HTML files to the index.

        Args:
            html_files (List[Union[str, Path]]): The HTML files to add to the index.
        """
        # Import stuff (importing here avoids unnecessary dependencies)
        from langchain.document_loaders import BSHTMLLoader

        # Assert that all files exist
        html_files: List[Path] = [Path(html_file) for html_file in html_files]
        for html_file in html_files:
            assert html_file.exists(), f"File {html_file} does not exist."

        # Load the files
        loaders: List[BSHTMLLoader] = []
        for html_file in html_files:
            loaders.append(BSHTMLLoader(html_file))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._text_chunk_size,
            chunk_overlap=self._text_chunk_overlap,
            separators=self._text_separators,
        )
        docs: List[Document] = []
        for loader in loaders:
            docs.extend(loader.load_and_split(text_splitter=text_splitter))

        # Add the documents to the index
        if self._store:
            self._store.add_documents(documents=docs)
        else:
            embedding = OpenAIEmbeddings()
            self._store = FAISS.from_documents(documents=docs, embedding=embedding)


class TextBot(BaseLLMBot):
    def train(self, texts: List[str], metadatas: List[Dict[str, str]]):
        """
        Trains the bot using the given texts.

        Args:
            texts (List[str]): The texts to use for training.
            metadatas (List[Dict[str, str]]): The metadata for each text.
        """
        # Assert that lengths match
        assert len(texts) == len(
            metadatas
        ), "Lengths of texts and metadatas do not match."

        # Build documents
        docs: List[Document] = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._text_chunk_size,
            chunk_overlap=self._text_chunk_overlap,
            separators=self._text_separators,
        )
        for text, metadata in zip(texts, metadatas):
            docs_texts = text_splitter.split_text(text=text)
            for doc_text in docs_texts:
                docs.append(Document(page_content=doc_text, metadata=metadata))

        # Create the vector store
        embedding = OpenAIEmbeddings()
        self._store = FAISS.from_documents(documents=docs, embedding=embedding)

    def add_to_index(self, texts: List[str], metadatas: List[Dict[str, str]]):
        """
        Adds the given texts to the index.

        Args:
            texts (List[str]): The texts to add to the index.
            metadatas (List[Dict[str, str]]): The metadata for each text.
        """
        # Assert that lengths match
        assert len(texts) == len(
            metadatas
        ), "Lengths of texts and metadatas do not match."

        # Build documents
        docs: List[Document] = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._text_chunk_size,
            chunk_overlap=self._text_chunk_overlap,
            separators=self._text_separators,
        )
        for text, metadata in zip(texts, metadatas):
            docs_texts = text_splitter.split_text(text=text)
            for doc_text in docs_texts:
                docs.append(Document(page_content=doc_text, metadata=metadata))

        # Add the documents to the index
        if self._store:
            self._store.add_documents(documents=docs)
        else:
            embedding = OpenAIEmbeddings()
            self._store = FAISS.from_documents(documents=docs, embedding=embedding)
