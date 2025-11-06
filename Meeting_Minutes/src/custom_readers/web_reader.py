"""Custom Web reader based on TrafilaturaWebReader

Source: https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/trafilatura_web/base.py

Added metadata (url, content_format: markdown) to Document
"""

from typing import List

from llama_index.core.readers.base import BasePydanticReader
from llama_index.core.schema import Document


class CustomTrafilaturaWebReader(BasePydanticReader):
    """Trafilatura web page reader.

    Reads pages from the web.
    Requires the `trafilatura` package.

    """

    is_remote: bool = True

    @classmethod
    def class_name(cls) -> str:
        """Get the name identifier of the class."""
        return "TrafilaturaWebReader"

    def load_data(
        self,
        urls: List[str],
        include_comments=True,
        output_format="markdown",
        include_tables=True,
        include_images=False,
        include_formatting=False,
        include_links=False,
        show_progress=False,
        **kwargs,
    ) -> List[Document]:
        """Load data from the urls.

        Args:
            urls (List[str]): List of URLs to scrape.
            include_comments (bool, optional): Include comments in the output. Defaults to True.
            output_format (str, optional): Output format. Defaults to 'txt'.
            include_tables (bool, optional): Include tables in the output. Defaults to True.
            include_images (bool, optional): Include images in the output. Defaults to False.
            include_formatting (bool, optional): Include formatting in the output. Defaults to False.
            include_links (bool, optional): Include links in the output. Defaults to False.
            show_progress (bool, optional): Show progress bar. Defaults to False
            kwargs: Additional keyword arguments for the `trafilatura.extract` function.

        Returns:
            List[Document]: List of documents.
        """
        import trafilatura

        if not isinstance(urls, list):
            raise ValueError(f"URLs must be a list of strings. Passed: {urls}")

        documents = []
        if show_progress:
            from tqdm import tqdm

            iterator = tqdm(urls, desc="Downloading pages")
        else:
            iterator = urls
        for url in iterator:
            downloaded = trafilatura.fetch_url(url, no_ssl=False)
            response = trafilatura.extract(
                downloaded,
                include_comments=include_comments,
                output_format=output_format,
                include_tables=include_tables,
                include_images=include_images,
                include_formatting=include_formatting,
                include_links=include_links,
                **kwargs,
            )
            metadata = {"url": url, "content_format": output_format}
            documents.append(Document(text=response, id_=url, metadata=metadata))

        return documents


if __name__ == "__main__":
    urls = ["https://www.novartis.com/stories/art-drug-design-technological-age"]
    trafilatura_web_reader = CustomTrafilaturaWebReader()
    documents = trafilatura_web_reader.load_data(
        urls=urls,
        output_format="markdown",
        include_comments=True,
        include_tables=True,
        include_images=False,
        include_formatting=True,
        include_links=False,
        show_progress=True,
    )
    print(documents[0].text)
