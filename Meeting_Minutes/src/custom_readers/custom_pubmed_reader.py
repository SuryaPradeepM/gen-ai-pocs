"""Load Pubmed Papers & optionally get pdf url as well (if available)

Source: https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/readers/llama-index-readers-papers/llama_index/readers/papers/pubmed/base.py

Changes made to grab URLs of articles (& optionally PDFs if available) along with Document(text)
"""

import time
import xml.etree.ElementTree as xml
from datetime import datetime
from typing import List, Optional

import requests
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from loguru import logger


class CustomPubmedReader(BaseReader):
    """Pubmed Reader.

    Gets a search query, return a list of Documents of the top corresponding scientific papers on Pubmed.
    """

    def __init__(self):
        pass

    def load_data_bioc(
        self,
        search_query: str,
        max_results: Optional[int] = 5,
    ) -> List[Document]:
        """Search for a topic on Pubmed, fetch the text of the most relevant full-length papers.
        Uses the BoiC API, which has been down a lot.

        Args:
            search_query (str): A topic to search for (e.g. "Alzheimer's").
            max_results (Optional[int]): Maximum number of papers to fetch.

        Returns:
            List[Document]: A list of Document objects.
        """

        pubmed_search = []
        parameters = {"tool": "tool", "email": "email", "db": "pmc"}
        parameters["term"] = search_query
        parameters["retmax"] = max_results
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params=parameters,
        )
        root = xml.fromstring(resp.content)

        for elem in root.iter():
            if elem.tag == "Id":
                _id = elem.text
                try:
                    resp = requests.get(
                        f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{_id}/ascii"
                    )
                    info = resp.json()
                    title = "Pubmed Paper"
                    try:
                        title = next(
                            [
                                p["text"]
                                for p in info["documents"][0]["passages"]
                                if p["infons"]["section_type"] == "TITLE"
                            ]
                        )
                    except KeyError:
                        pass
                    paper_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{_id}/"
                    pubmed_search.append(
                        {
                            "title": title,
                            "url": paper_url,
                            "date": info["date"],
                            "documents": info["documents"],
                        }
                    )
                    self.paper_urls.append(paper_url)
                except Exception:
                    logger.warning(f"Unable to parse PMC{_id} or it does not exist")

        # Then get documents from Pubmed text, which includes abstracts
        pubmed_documents = []
        for paper in pubmed_search:
            for d in paper["documents"]:
                text = "\n".join([p["text"] for p in d["passages"]])
                pubmed_documents.append(
                    Document(
                        text=text,
                        extra_info={
                            "Title of this paper": paper["title"],
                            "URL": paper["url"],
                            "Date published": datetime.strptime(
                                paper["date"], "%Y%m%d"
                            ).strftime("%m/%d/%Y"),
                        },
                    )
                )

        return pubmed_documents

    def fetch_papers(
        self,
        search_query: str,
        max_results: Optional[int] = 5,
    ) -> List[dict]:
        """Search for a topic on Pubmed, fetch the text of the most relevant full-length papers.

        Args:
            search_query (str): A topic to search for (e.g. "Alzheimer's").
            max_results (Optional[int]): Maximum number of papers to fetch.

        Returns:
            List[dict]: A list of papers

            Sample Output:
            [
                {
                    "journal": "Infection and Drug Resistance",
                    "pdf_available": True, # -> Flag to indicate if "url" points to a pdf
                    "text": "pmc Infect Drug Resist Infect Drug Resist idr In ...",
                    "title": "Antimicrobial susceptibility patterns of pathogens isolated from "
                    "pregnant women in KwaZulu-Natal Province: 2011 - 2016",
                    "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11143980/pdf", # -> Redirects to the actual pdf url
                },
                ...,
            ]
        """
        logger.debug(
            f"Searching PubMed with query: {search_query}\nMax Results: {max_results}"
        )
        pubmed_search, paper_urls = [], []
        parameters = {"tool": "tool", "email": "email", "db": "pmc"}
        parameters["term"] = search_query
        parameters["retmax"] = max_results
        resp = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params=parameters,
            verify=True,
        )
        root = xml.fromstring(resp.content)

        for elem in root.iter():
            if elem.tag == "Id":
                _id = elem.text
                url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?id={_id}&db=pmc"
                logger.debug(f"Parsing url: {url}")
                try:
                    resp = requests.get(
                        url,
                        verify=True,
                    )
                    info = xml.fromstring(resp.content)

                    raw_text = ""
                    title = ""
                    journal = ""
                    for element in info.iter():
                        if element.tag == "article-title":
                            title = element.text
                        elif element.tag == "journal-title":
                            journal = element.text

                        if element.text:
                            raw_text += element.text.strip() + " "

                    paper_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{_id}/"
                    pubmed_search.append(
                        {
                            "title": title,
                            "journal": journal,
                            "url": paper_url,
                            "text": raw_text,
                        }
                    )
                    paper_urls.append(paper_url)
                    time.sleep(1)  # API rate limits
                except Exception as e:
                    logger.warning(f"Unable to parse PMC{_id} or it does not exist:", e)

        # Then get documents from Pubmed text, which includes abstracts
        # pubmed_documents = []
        # for paper in pubmed_search:
        #     pubmed_documents.append(
        #         Document(
        #             text=paper["text"],
        #             extra_info={
        #                 "Title of this paper": paper["title"],
        #                 "Journal it was published in:": paper["journal"],
        #                 "URL": paper["url"],
        #             },
        #         )
        #     )

        # return pubmed_documents

        for paper in pubmed_search:
            paper["url"], paper["pdf_available"] = self._check_pdf_url(paper.get("url"))
        return pubmed_search

    @staticmethod
    def _check_pdf_url(url: str) -> str:
        """Check if the PDF version of the paper exists and return the URL.

        Args:
            url (str): The original URL of the paper.

        Returns:
            str: The URL of the PDF version if it exists, otherwise the original URL.
            bool: Boolean indicating whether PDF available?
        """
        pdf_url = url + "pdf"
        try:
            resp = requests.head(pdf_url, verify=True)
            if resp.status_code != 404:
                return pdf_url, True
        except requests.RequestException as exp:
            # TODO: test if any PMC article doesn't have pdf
            logger.warning(f"PDF unavailable for url: {url} | Exception: {exp}")
        except Exception as exp:
            logger.warning(f"Couldn't access: {url} | Exception: {exp}")

        return url, False

    def get_pdf_urls(self, paper_urls: list, try_pdf: bool = True) -> List[str]:
        """Retrieve the stored URLs of the most relevant papers.

        Returns:
            List[str]: A list of URLs.
        """
        if try_pdf:
            # gets pdf if pdf if available on pubmed for the paper
            return [self._check_pdf_url(url) for url in paper_urls]
        return paper_urls


if __name__ == "__main__":
    reader = CustomPubmedReader()
    papers = reader.fetch_papers("Disease burden of Asthma in India")
    print(papers)
    documents = reader.load_data_bioc("Alzheimer's")
