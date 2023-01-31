""" Test helpers reading bounding box data created from FigSplit"""

from pathlib import Path
from pytest import approx
from biosearch_core.bbox_reader import BoundingBoxMapper


def test_load():
    """Test loading bounding boxes from sample data"""
    base_path = Path("./tests/sample_data").resolve()
    reader = BoundingBoxMapper(base_path=base_path)

    img_paths = [
        "doc_from_cord_1/pdfname/3_1/001.jpg",
        "doc_from_cord_1/pdfname/3_1/002.jpg",
        "doc_from_cord_1/pdfname/3_1/003.jpg",
        "doc_from_cord_1/pdfname/3_1/004.jpg",
        "doc_from_cord_1/pdfname/3_1/005.jpg",
        "doc_from_cord_1/pdfname/3_1/006.jpg",
        "doc_from_cord_1/pdfname/3_1/007.jpg",
        "doc_from_cord_1/pdfname/3_1/008.jpg",
        "doc_from_cord_1/pdfname/4_1/001.jpg",
        "doc_from_cord_1/pdfname/4_1/002.jpg",
        "doc_from_cord_1/pdfname/4_1/003.jpg",
        "doc_from_cord_1/pdfname/5_1/001.jpg",
        "doc_from_cord_1/pdfname/5_1/002.jpg",
        "doc_from_cord_1/pdfname/6_1/001.jpg",
        "doc_from_cord_1/pdfname/6_1/002.jpg",
        "doc_from_cord_1/pdfname/6_1/003.jpg",
        "doc_from_cord_1/pdfname/6_1/004.jpg",
        "doc_from_tinman_1/otherpdfname/3_1/001.jpg",
        "doc_from_tinman_1/otherpdfname/3_1/002.jpg",
        "doc_from_tinman_1/otherpdfname/3_1/003.jpg",
        "doc_from_tinman_1/otherpdfname/3_2/001.jpg",
        "doc_from_tinman_1/otherpdfname/3_2/002.jpg",
        "doc_from_tinman_1/otherpdfname/3_2/003.jpg",
    ]
    reader.load(img_paths)

    assert len(reader.errors) == 0
    assert len(reader.mapping.keys()) == len(img_paths)
    assert reader.mapping[img_paths[0]] == approx([0.6, 22.1, 901.7, 213.1])
    assert reader.mapping[img_paths[1]] == approx([31.4, 836.1, 976.0, 264.2])
    assert reader.mapping[img_paths[2]] == approx([149.2, 237.5, 797.8, 262.4])
    assert reader.mapping[img_paths[3]] == approx([216.0, 1100.9, 410.5, 208.4])
    assert reader.mapping[img_paths[4]] == approx([970.8, 0.6, 438.4, 566.1])
    assert reader.mapping[img_paths[5]] == approx([981.3, 755.4, 443.6, 595.1])
    assert reader.mapping[img_paths[6]] == approx([1392.3, 751.9, 464.5, 598.6])
    assert reader.mapping[img_paths[7]] == approx([1398.1, 0.6, 458.7, 556.8])
    assert reader.mapping[img_paths[17]] == approx([0.5, 0.5, 514.0, 90.50])
    assert reader.mapping[img_paths[18]] == approx([78.0, 190.0, 156.0, 53.5])
    assert reader.mapping[img_paths[19]] == approx([255.0, 198.0, 227.5, 45.5])
    assert reader.mapping[img_paths[20]] == approx([0.5, 22.0, 346.0, 330.5])
    assert reader.mapping[img_paths[21]] == approx([347.0, 54.5, 135.5, 283.0])
    assert reader.mapping[img_paths[22]] == approx([510.0, 53.5, 251.5, 284.5])

    assert reader.mapping[img_paths[22]] != approx([520.0, 53.5, 251.5, 284.5])
