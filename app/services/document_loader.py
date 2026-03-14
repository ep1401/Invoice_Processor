from dataclasses import dataclass


@dataclass
class LoadedDocument:
    file_name: str
    file_bytes: bytes


class DocumentLoader:
    def load_from_bytes(self, file_bytes: bytes, file_name: str) -> LoadedDocument:
        if not file_name:
            raise ValueError("file_name is required.")

        if not file_bytes:
            raise ValueError("file_bytes is empty.")

        if not file_name.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")

        return LoadedDocument(
            file_name=file_name,
            file_bytes=file_bytes,
        )