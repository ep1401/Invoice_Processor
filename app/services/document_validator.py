from dataclasses import dataclass


@dataclass
class InputDocument:
    file_name: str
    file_bytes: bytes


class DocumentValidator:
    def validate(self, file_bytes: bytes, file_name: str) -> InputDocument:
        if not file_name:
            raise ValueError("A file name is required.")

        if not file_name.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are supported.")

        if not file_bytes:
            raise ValueError("Uploaded file is empty.")

        return InputDocument(
            file_name=file_name,
            file_bytes=file_bytes,
        )