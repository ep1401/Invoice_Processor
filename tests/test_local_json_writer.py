import json

from app.services.storage.local_json_writer import LocalJsonResultWriter


def test_writer_saves_json_file_with_expected_name(tmp_path, sample_processing_result):
    writer = LocalJsonResultWriter(tmp_path)

    output_path = writer.save(sample_processing_result)

    assert tmp_path.exists()
    assert output_path.endswith("INV-1001__Invoice_1.json")


def test_writer_saves_valid_json_content(tmp_path, sample_processing_result):
    writer = LocalJsonResultWriter(tmp_path)

    output_path = writer.save(sample_processing_result)

    with open(output_path, "r", encoding="utf-8") as file:
        saved = json.load(file)

    assert saved["InvoiceID"] == "INV-1001"
    assert saved["FileName"] == "Invoice 1.pdf"
    assert abs(saved["InvoicePreTaxTotals"] - 17.90) < 0.01
    assert len(saved["InvoiceLineItems"]) == 2


def test_writer_sanitizes_filename_components(tmp_path, sample_processing_result):
    sample_processing_result.InvoiceID = "INV/1001:*?"
    sample_processing_result.FileName = "Invoice 1 (final).pdf"

    writer = LocalJsonResultWriter(tmp_path)
    output_path = writer.save(sample_processing_result)

    assert output_path.endswith("INV_1001__Invoice_1__final.json")