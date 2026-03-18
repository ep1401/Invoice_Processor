import pytest

from app.services.tax_repository import TaxRepository


def test_get_tax_rate_returns_expected_rate(tax_csv_path):
    repo = TaxRepository(tax_csv_path)

    assert repo.get_tax_rate("Fresh Produce") == 0.0
    assert repo.get_tax_rate("Prepared Food") == 0.0825
    assert repo.get_tax_rate("Office Supplies") == 0.065


def test_get_tax_rate_unknown_category_raises_value_error(tax_csv_path):
    repo = TaxRepository(tax_csv_path)

    with pytest.raises(ValueError, match="Unknown tax category"):
        repo.get_tax_rate("Does Not Exist")


def test_get_all_categories_returns_loaded_categories(tax_csv_path):
    repo = TaxRepository(tax_csv_path)

    categories = repo.get_all_categories()

    assert "Fresh Produce" in categories
    assert "Prepared Food" in categories
    assert "Office Supplies" in categories