# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Document parsing and chunking utilities."""
from abc import ABC, abstractmethod
from collections import defaultdict
import copy
from dataclasses import dataclass
from functools import lru_cache
import json
import mlflow
from pathlib import Path
from pydantic import BaseModel
import tiktoken
import time
from typing import Any, IO, Iterator, List, Optional, Tuple, Union, Callable
import re

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders import UnstructuredFileIOLoader
from langchain.text_splitter import TextSplitter

from azureml.rag.models import init_llm
from azureml.rag.utils.logging import get_logger


logger = get_logger(__name__)


def merge_dicts(dict1, dict2):
    """Merge two dictionaries recursively."""
    result = defaultdict(dict)

    for d in (dict1, dict2):
        for key, value in d.items():
            if isinstance(value, dict) and key in result:
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return dict(result)


class LazyDocument(ABC):
    """Lazy Document"""
    document_id: str

    def __init__(self, document_id: str):
        """Initialize Lazy Document"""
        self.document_id = document_id

    @abstractmethod
    def modified_time(self) -> Any:
        """Get the modified time of the document"""
        pass

    @abstractmethod
    def load_data(self) -> str:
        """Load the data of the document"""
        pass

    @abstractmethod
    def get_metadata(self) -> dict:
        """Get the metadata of the document"""
        pass

    @property
    def page_content(self) -> str:
        """Get the page content of the document"""
        return self.load_data()

    @property
    def metadata(self) -> dict:
        """Get the metadata of the document"""
        return self.get_metadata()


class StaticDocument(LazyDocument):
    """Static Document holds data in-memory"""
    data: str
    _metadata: dict

    def __init__(self, document_id: str, data: str, metadata: dict, mtime=None):
        """Initialize Static Document"""
        super().__init__(document_id)
        self.data = data
        self._metadata = metadata
        self.mtime = mtime

    def modified_time(self) -> Any:
        """Get the modified time of the document"""
        self.mtime

    def load_data(self) -> str:
        """Load the data of the document"""
        return self.data

    def get_metadata(self) -> dict:
        """Get the metadata of the document"""
        return {**self._metadata, 'stats': self.document_stats()}

    def document_stats(self) -> dict:
        """Get the stats of the document"""
        return {
            'tiktokens': _tiktoken_len(self.data),
            'chars': len(self.data),
            'lines': len(self.data.splitlines()),
        }

    def __repr__(self):
        """Get the representation of the document"""
        return f"StaticDocument(id={self.document_id}, mtime={self.mtime}, metadata={self._metadata})"


@dataclass
class DocumentSource:
    """Document Source"""
    path: Path
    filename: str
    url: str
    mtime: float

    def get_metadata(self) -> dict:
        """Get the metadata of the document source"""
        return {
            "filename": self.filename,
            "url": self.url,
            "mtime": self.mtime,
        }


@dataclass
class ChunkedDocument:
    """Chunked Document"""
    chunks: List[Document]
    source: DocumentSource
    metadata: dict

    @property
    def page_content(self):
        """Get the page content of the chunked document"""
        return "\n\n".join([chunk.page_content for chunk in self.chunks])

    def get_metadata(self):
        """Get the metadata of the chunked document"""
        return merge_dicts(self.metadata, {'source': self.source.get_metadata()})


# TODO: This should be embeddings model dependent
enc = tiktoken.get_encoding("gpt2")


def _tiktoken_len(text: str) -> int:
    return len(enc.encode(text=text, disallowed_special=(), allowed_special="all"))


@lru_cache(maxsize=1)
def _init_nltk():
    import nltk
    nltk.download("punkt")


class MarkdownBlock(BaseModel):
    """Markdown Block"""

    header: Optional[str]
    content: str

    @property
    def header_level(self) -> int:
        """Get the header level of the block"""
        if self.header is None:
            return 0
        return self.header.count("#", 0, self.header.find(' '))


class MarkdownHeaderSplitter(TextSplitter):
    """Split text by markdown headers."""

    def __init__(self, remove_hyperlinks: bool = True, remove_images: bool = True, **kwargs: Any):
        """Initialize Markdown Header Splitter"""
        from langchain.text_splitter import TokenTextSplitter
        self._remove_hyperlinks = remove_hyperlinks
        self._remove_images = remove_images
        self._sub_splitter = TokenTextSplitter(**kwargs)
        super().__init__(**kwargs)

    def split_text(self, text: str) -> List[str]:
        """Split text into multiple components."""
        blocks = self.get_blocks(text)
        return [block.content for block in blocks]

    def create_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            for md_block in self.get_blocks(text):
                # TODO: Handle chunk being much smaller than ideal
                # Add to list for concat with other chunk? Make deep linking much harder,
                # could concat sections but still chunk other sections separately if large enough?
                if self._length_function(md_block.content) > self._chunk_size:
                    logger.info(f"Splitting section in chunks: {md_block.header}")
                    chunks = self._sub_splitter.split_text(md_block.content)
                else:
                    chunks = [md_block.content]

                metadata = _metadatas[i]
                metadata['markdown_heading'] = {
                    'heading': re.sub(
                        r"#",
                        "",
                        md_block.header if md_block.header is not None else metadata['source']['filename']
                    ).strip(),
                    'level': md_block.header_level
                }
                if len(chunks) > 0:
                    for c in chunks:
                        new_doc = Document(
                            page_content=c, metadata=copy.deepcopy(metadata)
                        )
                        documents.append(new_doc)
        return documents

    def get_blocks(self, markdown_text: str) -> List[MarkdownBlock]:
        """Parse blocks from markdown text."""
        lines = markdown_text.split("\n")

        block_header = None
        block_text = ""

        blocks = []
        for line in lines:
            header_match = re.match(r"^#+\s", line)
            if header_match:
                if block_header is not None:
                    if block_text == "":
                        continue
                    blocks.append((block_header, block_text))

                block_header = line
                block_text = ""
            else:
                block_text += line + "\n"
        blocks.append((block_header, block_text))

        if block_header is not None:
            # TODO: Add all parent headers to chunk_prefix to provide more context?
            # Inspired by: openai-cookbook - Question_answering_using_embeddings.ipynb
            markdown_tups = [
                MarkdownBlock(header=heading, content=heading + '\n' + MarkdownHeaderSplitter._clean_markdown(content))
                for heading, content in blocks
            ]
        else:
            markdown_tups = [
                MarkdownBlock(header=key, content=re.sub("\n", "", value))
                for key, value in blocks
            ]

        return markdown_tups

    @staticmethod
    def _clean_markdown(text: str) -> str:
        # Remove html tags
        # If there's a <!-- comment -->, remove it, otherwise remove each <> pairing
        # TODO: Consider keeping some info from `<img src="img/img_name.PNG" alt="my img desc"/>`?`
        # Finding the image and doing img2text could be useful for linking back to the image,
        # would ideally know the text came from an image to link back to it (or inline it) in a particular way.
        text = re.sub(r"<!-- (.*?)->|<.*?>", "", text)
        # Cleanup whole line comments
        text = re.sub(r"<!-+\s*$", "", text)
        # Strip surrounding whitespace
        text = text.strip()
        return text


def get_langchain_splitter(file_extension: str, arguments: dict) -> TextSplitter:
    """Get a text splitter for a given file extension."""
    use_nltk = False
    if "use_nltk" in arguments:
        use_nltk = arguments['use_nltk'] is True
        del arguments["use_nltk"]
    use_rcts = False
    if "use_rcts" in arguments:
        use_nltk = arguments['use_rcts'] is True
        del arguments['use_rcts']

    # Handle non-natural language splitters
    if file_extension == ".py":
        from langchain.text_splitter import PythonCodeTextSplitter
        return PythonCodeTextSplitter.from_tiktoken_encoder(**arguments)

    # If configured to use NLTK for splitting on sentence boundaries use that for non-code text formats
    if use_nltk:
        _init_nltk()
        from langchain.text_splitter import NLTKTextSplitter

        return NLTKTextSplitter(
            length_function=_tiktoken_len,
            **arguments
        )

    # TODO: Support NLTK for splitting text as default?
    # Though want to keep MD specific splitting, only using NLTK on large chunks of plain text.

    # Finally use any text format specific splitters
    formats_to_treat_as_txt_once_loaded = ['.pdf', '.ppt', '.pptx', '.doc', '.docx', '.xls', '.xlsx']
    if file_extension == ".txt" or file_extension in formats_to_treat_as_txt_once_loaded:
        from langchain.text_splitter import TokenTextSplitter
        return TokenTextSplitter(**arguments)
    elif file_extension == ".html" or file_extension == ".htm":
        from langchain.text_splitter import TokenTextSplitter
        return TokenTextSplitter(**arguments)
    elif file_extension == ".md":
        if use_rcts:
            logger.info('Using MarkdownTextSplitter')
            from langchain.text_splitter import MarkdownTextSplitter
            return MarkdownTextSplitter.from_tiktoken_encoder(**arguments)
        else:
            logger.info('Using MarkdownHeaderSplitter')
            return MarkdownHeaderSplitter.from_tiktoken_encoder(remove_hyperlinks=True, remove_images=True, **arguments)
    else:
        raise ValueError(f"Invalid file_extension: {file_extension}")


file_extension_splitters = {
    ".txt": lambda **kwargs: get_langchain_splitter(".txt", kwargs),
    ".md": lambda **kwargs: get_langchain_splitter(".md", kwargs),
    ".html": lambda **kwargs: get_langchain_splitter(".html", kwargs),
    ".htm": lambda **kwargs: get_langchain_splitter(".htm", kwargs),
    ".py": lambda **kwargs: get_langchain_splitter(".py", kwargs),
    ".pdf": lambda **kwargs: get_langchain_splitter(".pdf", kwargs),
    ".ppt": lambda **kwargs: get_langchain_splitter(".ppt", kwargs),
    ".pptx": lambda **kwargs: get_langchain_splitter(".pptx", kwargs),
    ".doc": lambda **kwargs: get_langchain_splitter(".doc", kwargs),
    ".docx": lambda **kwargs: get_langchain_splitter(".docx", kwargs),
    ".xls": lambda **kwargs: get_langchain_splitter(".xls", kwargs),
    ".xlsx": lambda **kwargs: get_langchain_splitter(".xlsx", kwargs),
}


# TODO: Change to be classes referenced in a map?
def extract_text_document_title(text: str, file_name: str) -> Tuple[str, str]:
    """Extract a title from a text document."""
    file_extension = Path(file_name).suffix
    if file_extension == ".md":
        # TODO: More targeted parsing?
        # text.find("title: ") or re.match(r"^#\s", text), If neither of these use file_name
        # Also pull out titleSuffix when parsing 'title: '?
        from bs4 import BeautifulSoup
        import markdown
        html_content = markdown.markdown(text)
        soup = BeautifulSoup(html_content, 'html.parser')
        title = ""
        clean_title = ""
        try:
            title = next(soup.stripped_strings)
            for entry in title.split("\n"):
                if entry.startswith("title") and not entry.startswith("titleSuffix"):
                    clean_title += entry[len('title: '):].rstrip()
                    break
        except StopIteration:
            title = file_name
        return title, (clean_title if len(clean_title) > 0 else file_name)
    elif file_extension == ".py":
        import ast

        def _get_topdocstring(text):
            tree = ast.parse(text)
            docstring = ast.get_docstring(tree)  # returns top docstring
            return docstring

        docstring = _get_topdocstring(text)
        if docstring:
            title = f"{file_name}: {docstring}"
        else:
            title = file_name
        return f"Title: {title}", title
    elif file_extension == ".html" or file_extension == ".htm":
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(text, "html.parser")
        try:
            title = next(soup.stripped_strings)
        except StopIteration:
            title = file_name
        return f"Title: {title}", title
    else:
        title = None
        first_text_line = None
        title_prefix = "title: "
        for line in text.splitlines():
            if line.startswith(title_prefix):
                title = line[len(title_prefix):].strip()
                break
            if first_text_line is None and any([c.isalnum() for c in line]):
                first_text_line = line.strip()

        if title is None:
            title = first_text_line if first_text_line is not None else file_name

        return f"Title: {title}", title


class TextFileIOLoader(BaseLoader):
    """Load text files."""

    def __init__(self, file: IO, document_source: DocumentSource, metadata: dict, summarize_config: Optional[dict] = None):
        """Initialize a text file loader."""
        self.file = file
        self.document_source = document_source
        self.summarize_config = summarize_config
        self.metadata = metadata

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        text = self.file.read()
        title, clean_title = extract_text_document_title(text, self.document_source.filename)
        self.metadata = {**self.metadata, "source": {"title": clean_title}}
        chunk_prefix = title + "\n\n"
        if self.summarize_config:
            chunk_prefix += f"Summary: {TextFileIOLoader.summarize_text(text, self.summarize_config)}" + "\n\n"
        return ChunkedDocument(
            chunks=[Document(page_content=text, metadata=self.metadata)],
            source=self.document_source,
            metadata={"chunk_prefix": chunk_prefix, **self.metadata}
        )

    def load(self) -> List[Document]:
        """Load file contents into Document."""
        chunked_doc = self.load_chunked_document()
        docs = []
        for chunk in chunked_doc.chunks:
            chunk.metadata["chunk_prefix"] = chunked_doc.metadata["chunk_prefix"]
            chunk.metadata["source"] = {**chunked_doc.source.get_metadata(), **chunk.metadata["source"]}
            docs.append(chunk)
        return docs

    @staticmethod
    def summarize_text(text: str, summarize_config: dict) -> str:
        """Summarize text using OpenAI's LLM."""
        from langchain.chains.summarize import load_summarize_chain
        from langchain.prompts import PromptTemplate
        from langchain.text_splitter import NLTKTextSplitter
        from openai import APIError
        import re

        _init_nltk()

        llm = init_llm(summarize_config)

        prompt_template = """Write an informative and concise summary of the following text.
        Include the most relevant details near the top of the summary.
        Make the summary objective and to the point. Do not start the summary with "the text describes" or "the text explains":
        {text}:
        """
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

        summary_splitter = NLTKTextSplitter(
            chunk_size=2500,
            length_function=_tiktoken_len
        )
        texts = summary_splitter.split_text(text)
        docs = [Document(page_content=t) for t in texts]
        chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=PROMPT)
        try:
            doc_summary = chain.run(docs)
            # take only first 3 sentences from summary
            doc_summary = ' '.join(re.split(r'(?<=[.!])\s', doc_summary)[:3])
        except APIError as e:
            if "The response was filtered due to the prompt triggering Azure OpenAI’s content management policy" in str(e):
                print("Caught OpenAI API error: " + str(e))
                print("Falling back to no summary")
                doc_summary = ""
            else:
                raise e
        except ValueError as e:
            if "A single document was so long it could not be combined with another document, we cannot handle this." in str(e) or \
                    "A single document was longer than the context length, we cannot handle this." in str(e):
                print("Can't summarize document as it is too long: " + str(e))
                print("Falling back to no summary")
                doc_summary = ""
            else:
                raise e
        except TypeError as e:
            # TODO: Temp work around until this releases: https://github.com/openai/openai-python/pull/356
            if "string indices must be integers" in str(e):
                print("Caught OpenAI API error: " + str(e))
                print("Falling back to no summary")
                doc_summary = ""
            else:
                raise e
        except Exception as e:
            if "This model's maximum context length is" in str(e):
                print("Caught OpenAI API error: " + str(e))
                print("Falling back to no summary")
                doc_summary = ""
            else:
                raise e
        return doc_summary


class UnstructuredHTMLFileIOLoader(UnstructuredFileIOLoader):
    """Loader that uses unstructured to load HTML files."""

    def __init__(self, file, document_source: DocumentSource, metadata: dict, summarize_config: Optional[dict] = None, mode="single", **unstructured_kwargs: Any):
        """Initialize a text file loader."""
        self.metadata = metadata
        self.document_source = document_source
        self.summarize_config = summarize_config
        super().__init__(file=file, mode=mode, **unstructured_kwargs)

    def load(self) -> List[Document]:
        """Load file contents into Documents."""
        docs = super().load()
        # TODO: Extract html file title and add to metadata
        if self.summarize_config:
            # TODO: Summarize each doc and add to metadata
            pass
        return docs

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        return ChunkedDocument(
            chunks=self.load(),
            source=self.document_source,
            metadata=self.metadata
        )

    def _get_elements(self) -> List:
        from unstructured.partition.html import partition_html

        return partition_html(file=self.file, **self.unstructured_kwargs)

    def _get_metadata(self):
        return self.metadata


class PDFFileLoader(BaseLoader):
    """Load PDF files."""

    def __init__(self, file: IO, document_source: DocumentSource, metadata: dict, summarize_config: Optional[dict] = None):
        """Initialize a text file loader."""
        self.file = file
        self.document_source = document_source
        self.summarize_config = summarize_config
        self.metadata = metadata

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        pages = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        if self.summarize_config:
            whole_document_text = "\n\n".join([page.page_content for page in pages])
            summary = TextFileIOLoader.summarize_text(whole_document_text, self.summarize_config)
            chunk_prefix += f"\nSummary: {summary}" + "\n\n"
        return ChunkedDocument(
            chunks=pages,
            source=self.document_source,
            metadata={**self.metadata, 'chunk_prefix': chunk_prefix}
        )

    def load(self) -> List[Document]:
        """Load file contents into Documents."""
        print("Loading PDF file")
        from pypdf import PdfReader

        docs: List[Document] = list()
        reader = PdfReader(self.file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text is not None:
                metadata = {"page_number": reader.get_page_number(page), **self.metadata}
                docs.append(Document(page_content=page_text, metadata=metadata))
        return docs


class TikaLoader(BaseLoader):
    """Load various unstructured files formats using Apache Tika."""

    def __init__(self, file: IO, document_source: DocumentSource, metadata: dict, summarize_config: Optional[dict] = None):
        """Initialize a text file loader."""
        self.file = file
        self.document_source = document_source
        self.metadata = metadata
        self.summarize_config = summarize_config

    def load_chunked_document(self) -> ChunkedDocument:
        """Load file contents into ChunkedDocument."""
        doc = self.load()
        chunk_prefix = f"Title: {Path(self.document_source.filename).name}"
        if self.summarize_config:
            chunk_prefix += f"Summary: {TextFileIOLoader.summarize_text(doc[0].page_content, self.summarize_config)}" + "\n\n"
        return ChunkedDocument(
            chunks=doc,
            source=self.document_source,
            metadata={"chunk_prefix": chunk_prefix, **self.metadata}
        )

    def load(self) -> List[Document]:
        """Load from file path."""
        print(f"Loading {self.document_source.filename}")
        from tika import parser

        parsed = parser.from_file(self.file)
        content = parsed["content"]
        import re
        text = re.sub(r'\n{3,}', '\n\n', content)

        return [Document(page_content=text, metadata=self.metadata)]


file_extension_loaders = {
    ".txt": TextFileIOLoader,
    ".md": TextFileIOLoader,
    ".html": UnstructuredHTMLFileIOLoader,
    ".htm": UnstructuredHTMLFileIOLoader,
    ".py": TextFileIOLoader,
    ".pdf": PDFFileLoader,
    ".ppt": TikaLoader,
    ".pptx": TikaLoader,
    ".doc": TikaLoader,
    ".docx": TikaLoader,
    # TODO: we should probably not convert this to text and find a way to keep the table structure
    ".xls": TikaLoader,
    ".xlsx": TikaLoader,
}

SUPPORTED_EXTENSIONS = list(file_extension_loaders.keys())


def filter_extensions(sources: Iterator[DocumentSource], allowed_extensions=SUPPORTED_EXTENSIONS) -> Iterator[DocumentSource]:
    """Filter out sources with extensions not in allowed_extensions."""
    total_files = 0
    skipped_files = 0
    skipped_extensions = {}
    for source in sources:
        total_files += 1
        if allowed_extensions is not None:
            if source.path.suffix not in allowed_extensions:
                skipped_files += 1
                ext_skipped = skipped_extensions.get(source.path.suffix, 0)
                skipped_extensions[source.path.suffix] = ext_skipped + 1
                logger.debug(f'Filtering out extension "{source.path.suffix}" source: {source.filename}')
                continue
        yield source
    logger.info(f"[DocumentChunksIterator::filter_extensions] Filtered {skipped_files} files out of {total_files}", extra={'print': True})


def crack_documents(sources: Iterator[DocumentSource], summary_model_config: Optional[dict] = None, file_extension_loaders=file_extension_loaders) -> Iterator[ChunkedDocument]:
    """Crack documents into chunks."""
    total_time = 0
    files_by_extension = {
        str(ext): 0.0 for ext in file_extension_loaders.keys()
    }
    for source in sources:
        files_by_extension[source.path.suffix] += 1
        file_start_time = time.time()

        loader_cls = file_extension_loaders.get(source.path.suffix)
        mode = "r"
        if loader_cls is None:
            raise RuntimeError(f"Unsupported file extension '{source.path.suffix}': {source.filename}")
        elif loader_cls is TikaLoader or loader_cls is PDFFileLoader:
            mode = "rb"

        with open(source.path, mode=mode) as f:
            loader = loader_cls(**{
                "file": f,
                "document_source": source,
                "summarize_config": summary_model_config,
                "metadata": {}
            })
            file_pre_yield_time = time.time()
            total_time += file_pre_yield_time - file_start_time
            yield loader.load_chunked_document()
    logger.info(f"[DocumentChunksIterator::crack_documents] Total time to load files: {total_time}\n{json.dumps(files_by_extension, indent=2)}", extra={'print': True})
    mlflow.log_metrics(files_by_extension)


def split_documents(documents: Iterator[ChunkedDocument], splitter_args: dict, file_extension_splitters=file_extension_splitters) -> Iterator[ChunkedDocument]:
    """Split documents into chunks."""
    total_time = 0
    total_documents = 0
    total_splits = 0
    for document in documents:
        if len(document.chunks) < 1:
            continue
        file_start_time = time.time()
        total_documents += len(document.chunks)

        local_splitter_args = splitter_args.copy()

        document_metadata = document.get_metadata()
        chunk_prefix = document_metadata.get('chunk_prefix', '')
        if len(chunk_prefix) > 0:
            if 'chunk_size' in local_splitter_args:
                prefix_token_length = _tiktoken_len(chunk_prefix)
                if prefix_token_length > local_splitter_args['chunk_size'] // 2:
                    chunk_prefix = chunk_prefix[:local_splitter_args['chunk_size'] // 2]
                    # should we update local_splitter_args['chunk_size'] here?
                else:
                    local_splitter_args['chunk_size'] = local_splitter_args['chunk_size'] - prefix_token_length

        if 'chunk_prefix' in document_metadata:
            del document_metadata['chunk_prefix']

        # TODO: Move out as own filter
        chunk_overlap = 0
        if 'chunk_overlap' in local_splitter_args:
            chunk_overlap = local_splitter_args['chunk_overlap']

        def filter_short_docs(chunked_document):
            for doc in chunked_document.chunks:
                doc_len = len(doc.page_content)
                if doc_len < chunk_overlap:
                    logger.info(f"Filtering out doc_chunk shorter than {chunk_overlap}: {chunked_document.source.filename}")
                    continue
                yield doc

        def merge_metadata(chunked_document):
            for chunk in chunked_document.chunks:
                chunk.metadata = merge_dicts(chunk.metadata, document_metadata)
            return chunked_document

        splitter = file_extension_splitters.get(document.source.path.suffix)(**local_splitter_args)
        split_docs = splitter.split_documents(list(filter_short_docs(merge_metadata(document))))

        i = -1
        file_chunks = []
        for chunk in split_docs:
            i += 1
            if 'chunk_prefix' in chunk.metadata:
                del chunk.metadata['chunk_prefix']
            file_chunks.append(StaticDocument(document.source.filename + str(i), chunk_prefix + chunk.page_content, merge_dicts(chunk.metadata, document_metadata), document.source.mtime))

        file_pre_yield_time = time.time()
        total_time += file_pre_yield_time - file_start_time
        if len(file_chunks) < 1:
            logger.info('No file_chunks to yield, continuing')
            continue
        total_splits += len(file_chunks)
        document.chunks = file_chunks
        yield document

    logger.info(f"[DocumentChunksIterator::split_documents] Total time to split {total_documents} documents into {total_splits} chunks: {total_time}", extra={'print': True})
    mlflow.log_metrics({
        'Total Source Documents': total_documents,
        'Total Chunked Documents': total_splits,
    })


def files_to_document_source(
        files_source: Union[str, Path],
        glob: str = '**/*',
        base_url: Optional[str] = None,
        process_url: Optional[Callable[[str], str]] = None) -> Iterator[DocumentSource]:
    """Convert files to DocumentSource."""
    for file in Path(files_source).rglob(glob):
        if not file.is_file():
            continue
        relative_path = file.relative_to(files_source)
        url = str(relative_path)
        if base_url:
            url = f'{base_url}/{relative_path}'
        if process_url:
            url = process_url(url)
        yield DocumentSource(
            path=file,
            filename=str(relative_path),
            url=url,
            mtime=file.stat().st_mtime
        )


class DocumentChunksIterator:
    """Iterate over document chunks."""
    def __init__(
            self,
            files_source: Union[str, Path],
            glob: str,
            base_url: str,
            document_path_replacement_regex: Optional[str],
            # document_sources: Iterator[DocumentSource],
            file_filter: Optional[Callable[[Iterator[DocumentSource]], Iterator[DocumentSource]]]=filter_extensions,
            source_loader: Callable[[Iterator[DocumentSource]], Iterator[ChunkedDocument]]=crack_documents,
            chunked_document_processors: Optional[List[Callable[[Iterator[ChunkedDocument]], Iterator[ChunkedDocument]]]] = [
                lambda docs: split_documents(docs, splitter_args={'chunk_size': 1024, 'chunk_overlap': 0})
            ]):
        """Initialize a document chunks iterator."""
        self.files_source = files_source
        self.glob = glob
        self.base_url = base_url
        self.document_path_replacement_regex = document_path_replacement_regex

        # self.document_sources = document_sources
        self.file_filter = file_filter
        self.source_loader = source_loader

        self.chunked_document_processors = chunked_document_processors

    def __iter__(self):
        """Iterate over document chunks."""
        if self.document_path_replacement_regex:
            document_path_replacement = json.loads(self.document_path_replacement_regex)
            url_replacement_match = re.compile(document_path_replacement['match_pattern'])

            def process_url(url):
                return url_replacement_match.sub(document_path_replacement['replacement_pattern'], url)
        else:
            def process_url(url):
                return url

        source_documents = files_to_document_source(self.files_source, self.glob, self.base_url, process_url)
        if self.file_filter is not None:
            source_documents = self.file_filter(source_documents)

        document_chunks_iterator = self.source_loader(source_documents)

        if self.chunked_document_processors is not None:
            for chunked_document_processor in self.chunked_document_processors:
                document_chunks_iterator = chunked_document_processor(document_chunks_iterator)

        return document_chunks_iterator


def document_chunks_iterator(
        files_source: Union[str, Path],
        glob: str,
        allowed_extensions: Optional[List[str]],
        base_url: str,
        document_path_replacement_regex: Optional[str],
        splitter_args: dict = {},
        summary_model_config: Optional[dict] = None) -> Iterator[List[StaticDocument]]:
    """Iterate over files in a directory and yield chunks of documents."""
    import time

    # fs, uri = url_to_fs(files_source)
    # files = fs.glob(f'{uri}/{glob}')

    files = (f for f in Path(files_source).rglob(glob) if f.is_file())

    # Filter file list to only those in allowed_extensions, if provided, print files that are filtered out
    if allowed_extensions is not None:
        def filter_extensions(files):
            total_files = 0
            skipped_files = 0
            skipped_extensions = {}
            for file in files:
                total_files += 1
                if file.suffix in allowed_extensions:
                    yield file
                else:
                    skipped_files += 1
                    ext_skipped = skipped_extensions.get(file.suffix, 0)
                    skipped_extensions[file.suffix] = ext_skipped + 1
                    logger.debug(f'Filtering out extension "{file.suffix}" file: {file}')
            logger.info(f"[document_chunks_iterator::filter_extensions] Filtered {skipped_files} files out of {total_files}", extra={'print': True})
            mlflow.log_metrics(skipped_extensions)

        files = filter_extensions(files)

    if document_path_replacement_regex:
        document_path_replacement = json.loads(document_path_replacement_regex)
        url_replacement_match = re.compile(document_path_replacement['match_pattern'])

        def process_url(url):
            return url_replacement_match.sub(document_path_replacement['replacement_pattern'], url)
    else:
        def process_url(url):
            return url

    # For each file find document loader based on extension
    def crack_documents(files) -> Iterator[List[Document]]:
        total_time = 0
        files_by_extension = {
            ext: 0.0 for ext in file_extension_loaders.keys()
        }
        for file in files:
            files_by_extension[file.suffix] += 1
            file_start_time = time.time()

            relative_path = file.relative_to(files_source)
            url = relative_path
            if base_url:
                url = f'{base_url}/{relative_path}'
            if document_path_replacement_regex:
                url = process_url(url)

            loader_cls = file_extension_loaders.get(file.suffix)
            mode = "r"
            if loader_cls is None:
                raise RuntimeError(f"Unsupported file extension '{file.suffix}': {file}")
            elif loader_cls is TikaLoader or loader_cls is PDFFileLoader:
                mode = "rb"

            file_info = file.stat()
            mtime = file_info.st_mtime
            with open(file, mode=mode) as f:
                loader = loader_cls(**{
                    "file": f,
                    "file_path": file,
                    "metadata": {
                        "source": {
                            "filename": str(relative_path),
                            "url": url
                        },
                        "extension": file.suffix,
                        "mtime": mtime
                    },
                    "summarize_config": summary_model_config
                })
                file_pre_yield_time = time.time()
                total_time += file_pre_yield_time - file_start_time
                yield loader.load()
        logger.info(f"[document_chunks_iterator::crack_documents] Total time to load files: {total_time}\n{json.dumps(files_by_extension, indent=2)}", extra={'print': True})
        mlflow.log_metrics(files_by_extension)

    cracked_documents = crack_documents(files)

    # For each part of loaded document apply appropriate TextSplitter
    def split_documents(documents_per_file: Iterator[List[Document]]) -> Iterator[List[StaticDocument]]:
        total_time = 0
        total_documents = 0
        total_splits = 0
        for file_documents in documents_per_file:
            if len(file_documents) < 1:
                continue
            file_start_time = time.time()
            total_documents += len(file_documents)

            local_splitter_args = splitter_args.copy()

            chunk_prefix = file_documents[0].metadata.get('chunk_prefix', '')
            if len(chunk_prefix) > 0:
                if 'chunk_size' in local_splitter_args:
                    prefix_token_length = _tiktoken_len(chunk_prefix)
                    if prefix_token_length > local_splitter_args['chunk_size'] // 2:
                        chunk_prefix = chunk_prefix[:local_splitter_args['chunk_size'] // 2]
                    else:
                        local_splitter_args['chunk_size'] = local_splitter_args['chunk_size'] - _tiktoken_len(chunk_prefix)

            chunk_overlap = 0
            if 'chunk_overlap' in local_splitter_args:
                chunk_overlap = local_splitter_args['chunk_overlap']

            def filter_short_docs(documents):
                for doc in documents:
                    doc_len = len(doc.page_content)
                    if doc_len < chunk_overlap:
                        logger.info(f"Filtering out doc_chunk shorter than {chunk_overlap}: {doc.metadata['source']['filename']}")
                        continue
                    yield doc

            splitter = get_langchain_splitter(file_documents[0].metadata['extension'], local_splitter_args)
            split_docs = splitter.split_documents(list(filter_short_docs(file_documents)))

            i = -1
            file_chunks = []
            for chunk in split_docs:
                i += 1
                if 'chunk_prefix' in chunk.metadata:
                    del chunk.metadata['chunk_prefix']
                file_chunks.append(StaticDocument(chunk.metadata['source']['filename'] + str(i), chunk_prefix + chunk.page_content, chunk.metadata, chunk.metadata.get('mtime')))
            file_pre_yield_time = time.time()
            total_time += file_pre_yield_time - file_start_time
            if len(file_chunks) < 1:
                logger.info('No file_chunks to yield, continuing')
                continue
            total_splits += len(file_chunks)
            yield file_chunks
        logger.info(f"[document_chunks_iterator::split_documents] Total time to split {total_documents} documents into {total_splits} chunks: {total_time}", extra={'print': True})
        mlflow.log_metrics({
            'Total Source Documents': total_documents,
            'Total Chunked Documents': total_splits,
        })

    return split_documents(cracked_documents)
