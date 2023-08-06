import io
import pandas as pd

from typing import Protocol
from dataclasses import dataclass
from strenum import StrEnum


class Suffix(StrEnum):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"


class Converter(Protocol):
    def convert(self, data: list[dict]) -> bytes:
        ...


class CSVConverter(Converter):
    """Convert list[dict] to stream with CSV data"""

    def convert(self, data):
        writer = io.BytesIO()
        pd.DataFrame(data).to_csv(writer, header=True, index=False)
        return ConvertedStream(suffix=Suffix.CSV, data=writer.getvalue())


class ExcelConverter(Converter):
    """Convert list[dict] to Excel"""

    def convert(self, data):
        writer = io.BytesIO()
        pd.DataFrame(data).to_excel(writer, header=True, index=False)
        return writer.getvalue()


class JSONConverter(Converter):
    """Convert list[dict] to JSON"""

    def convert(self, data):
        writer = io.BytesIO()
        pd.DataFrame(data).to_json(writer, orient="records")
        return writer.getvalue()


@dataclass
class ConvertedStream:
    suffix: Suffix
    data: io.BytesIO


def factory(output_type: str) -> Converter:
    FACTORIES = {
        "csv": CSVConverter(),
        "json": JSONConverter(),
        "xlsx": ExcelConverter(),
    }
    return FACTORIES[output_type]


def main() -> None:
    """Simple test"""
    # create the factory
    data = [{"createdAt": 2021, "price": 10}, {"createdAt": 2022, "price": 20}]
    converter = factory(Suffix.CSV)

    # convert
    converted_data = converter.convert(data)
    print(converted_data)


if __name__ == "__main__":
    main()
