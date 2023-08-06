"""Module for calculating TF-IDF"""

from typing import Any, Iterator
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)

TermFreq = dict[str, int]
DocFreq = dict[str, int]


@dataclass
class Doc:
    tf: TermFreq
    count: int


Docs = dict[Any, Doc]


class Model:
    """
    Document model for TF-IDF

    Attrs:
        docs: Docs
            documents in the model
        df: DocFreq
            all documents term frequency

    Methods:
        add_doc: Adds document to model
        remove_doc: Removes document from model
        search_query: Searches the model for documents matching the given query
        from_dict: Creates a new instance of Model from a document dictionary
        contains: Checks if a document is in the model (or use in keyword alternatively: "document in Model")

    Usage:
        >>> model = Model()
        >>> documents = {
                "fruits":
                    ["apple", "banana", "orange"],
                "vegetables":
                    ["tomato", "cucumber", "radish"],
                "pasta":
                    ["tagliatelle", "rotini", "rigatoni"],
                }

        >>> # Add documents to the model
        >>> for doc_id, doc_content in documents.items():
                model.add_doc(doc_id, doc_content)

        >>> # Or use convencience method "from_dict"
            model = Model.from_dict(from_dict)

        >>> # Remove a document from the model
        >>> doc_id = "pasta"
        >>> model.remove_doc(doc_id)

        >>> # Check if a document is in the model
        >>> if doc_id in model:
                ...

        >>> # Search the model for documents matching a query
        >>> results = model.search_query(query)
        >>> results
        [('fruits', 0.10034333188799373), ('vegetables', 0.0)]
    """

    def __init__(self):
        """
        Create a new document model for TF-IDF
        """
        self.docs: Docs = {}
        self.df: DocFreq = {}

    def add_doc(self, doc_id: Any, content: list[str] | Iterator[str]):
        """
        Add a document to the model

        Note: The content is required to be pre-tokenized

        Args:
            doc_id : Any
                identifying information of the document
            content : str
                contents of the document
        """
        self.remove_doc(doc_id)

        tf = {}
        count = 0
        logger.info("Adding doc: %s", doc_id)
        for term in content:  # type: ignore
            logger.debug("term: %s", term)
            if term in tf:
                tf[term] += 1
            else:
                tf[term] = 1
            count += 1

        for term in tf:
            if term not in self.df:
                self.df[term] = 1
            else:
                self.df[term] += 1

        self.docs[doc_id] = Doc(tf, count)

    def remove_doc(self, doc_id: Any):
        """
        Remove a document from the model

        Args:
            doc_id : Any
                identifying information of the document
        """
        logger.debug("Removing doc: %s", doc_id)
        if doc_id not in self.docs:
            return
        doc = self.docs.pop(doc_id)
        for term in doc.tf:
            if term not in self.df:
                continue
            self.df[term] -= 1
            if self.df[term] == 0:
                del self.df[term]

    def contains(self, doc_id: Any) -> bool:
        """
        Check if a document is in the model,
        or use in keyword alternatively: "document in Model"

        Args:
            doc_id : Any
                identifying information of the document

        Returns:
            bool: is the document in the model
        """
        return doc_id in self.docs

    def __contains__(self, doc_id: Any) -> bool:
        return doc_id in self.docs

    @classmethod
    def from_dict(cls, doc_dict: dict[Any, list[str]]) -> "Model":
        """
        Convenience method for creating a new Model instance from a dictionary of documents,
        populates the model with the documents provided

        Args:
            doc_dict: dict[Any, list[str]]
                a dictionary of documents {document identifying information : document content (list[str])}

        Returns: new instance of Model
        """
        model = cls()
        for doc_id, content in doc_dict.items():
            model.add_doc(doc_id, content)
        return model

    def search_query(self, query: list[str] | Iterator[str]) -> list[tuple[Any, float]]:
        """
        Search the model for documents matching the given query

        Args:
            query : str
                string to search for

        Returns:
            list[tuple[Any, float]]:
                a sorted list of documents (tuple[document id, document ranking]) by document relevance
        """
        logger.info("Searching for query: %s", query)
        result = []
        for nav_info, doc in self.docs.items():
            rank = 0
            for token in query:
                logger.debug("Computing TF-IDF for: %s", nav_info)
                rank += _compute_tf(token, doc) * _compute_idf(
                    token, len(self.docs), self.df
                )
                logger.debug("token: %s, rank: %s", token, rank)

            result.append((nav_info, rank))
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def __add__(self, other: "Model") -> "Model":
        new_model = Model()

        new_docs = self.docs | other.docs
        new_df = self.df | other.df

        duplicates = {
            key: value for key, value in other.docs.items() if key in self.docs
        }

        for doc in duplicates:
            for term in doc:
                if term in new_df:
                    new_df[term] -= 1

        new_model.docs = new_docs
        new_model.df = new_df
        return new_model


def _compute_tf(term: str, doc: Doc) -> float:
    """
    Compute the term-frequency of a term in a document

    Args:
        term : str
            term to compute the frequency for
        doc : Doc
            document to compute the frequency for

    Returns:
        float: The term-frequency of the term

    """
    n = doc.count
    m = doc.tf.get(term, 0)
    logging.debug("n = %s, m = %s", n, m)
    return m / n


def _compute_idf(term: str, n_docs: int, df: DocFreq) -> float:
    """
    Compute the inverse-term-frequency of a term in a document

    Args:
        term : str
            term to compute the frequency for
        n_docs : int
            number of documents in the model
        df : DocFreq
            document frequency

    Returns:
        float: The inverse-term-frequency of the term

    """
    m = df.get(term, 1)
    logging.debug("n = %s, m = %s", n_docs, m)
    return math.log10(n_docs / m)
