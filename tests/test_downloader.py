"""
Unit tests for downloader helpers (no network required).
"""

import pytest

from app.services.downloader import _filename_base, _html_path, _image_path, _build_detail_html
from app.models.trademark import Trademark


def test_filename_base_strips_slashes():
    assert _filename_base("KH/49633/12") == "KH4963312"
    assert _filename_base("KH/59286/14") == "KH5928614"
    assert _filename_base("KH/83498/19") == "KH8349819"


def test_html_path_naming():
    path = _html_path("KH/49633/12")
    assert path.name == "KH4963312_1.html"


def test_image_path_naming():
    path = _image_path("KH/49633/12")
    assert path.name == "KH4963312_2.jpg"


def test_build_detail_html_contains_brand():
    tm = Trademark(
        filing_number="KH/49633/12",
        brand="MINGFAI",
        owner="Ming Fai Enterprise International Co., Ltd.",
        image_url="https://example.com/image.jpg",
    )
    html = _build_detail_html(tm)
    assert "MINGFAI" in html
    assert "KH/49633/12" in html
    assert "Ming Fai" in html
    assert "<img" in html


def test_build_detail_html_no_image():
    tm = Trademark(
        filing_number="KH/49633/12",
        brand="MINGFAI",
        owner="Owner",
        image_url=None,
    )
    html = _build_detail_html(tm)
    assert "No image available" in html
    assert "<img" not in html
