""" Calculate the overlap between queries to Lucene with and without modalities 

  Case 1: Lungs radiology
    - Keyword lung and using keyword radiology as proxy for images
    - Keyword lung and specifying every type of radiology modality
    python overlap.py lung radiology rad rad.ang rad.uls rad.cmp rad.xra

    Queries:
            full-text only:          lung + radiology
            full-text + modalities:  lung + rad;rad.ang;rad.uls;rad.cmp;rad.xra
    Number of results
            full-text only:                  78
            query full-text + modalities:    359
    Intersections and Images
                            A∩B     Images(A∩B)     Images(A)       Images(B)
            total:           36     405             405             1762
            first 10:        1      27              114             161
            first 30:        4      77              177             593
            first 100:       18     330             405             1077    

  Case 2: Interactome blots
    - Keyword interactome and using keyword blot as proxy for western and 
      northern gel blots
    - Keyword interactome and specifying experimental gel images
    python overlap.py interactome blot exp.gel

    Queries:
            full-text only:          interactome + blot
            full-text + modalities:  interactome + exp.gel
    Number of results
            full-text only:                  24
            query full-text + modalities:    26
    Intersections and Images
                            A∩B     Images(A∩B)     Images(A)       Images(B)
            total:           17     137             137             194
            first 10:        5      46              47              70
            first 30:        17     137             137             194
            first 100:       17     137             137             194

  Case 3: kidney fluorescence
    - Keyword kidney and using the keyword fluorescence as proxy for a modality
      of microscopy images
    - Keyword kidney and specifying microscopy fluorescence modality
    python overlap.py kidney fluorescence mic.flu

    Queries:
            full-text only:          kidney + fluorescence
            full-text + modalities:  kidney + mic.flu
    Number of results
            full-text only:                  596
            query full-text + modalities:    342
    Intersections and Images
                            A∩B     Images(A∩B)     Images(A)       Images(B)
            total:           225    2112            2112            3047
            first 10:        1      1               29              104
            first 30:        7      27              135             198
            first 100:       34     273             458             801    

"""
from typing import List, Optional
from argparse import ArgumentParser, Namespace
from collections import Counter
from requests import get

ROOT = "https://runachay.evl.uic.edu/search-api"


class OverlapAnalyzer:
    """Responsible for calculating differences in the results between two queries"""

    def __init__(self, dataset: str):
        self.dataset = dataset

    def _calc_intersections(
        self, list_1: List[str], list_2: List[str], max_docs: Optional[int] = None
    ) -> List:
        if max_docs is not None:
            elems_1 = list_1[:max_docs]
            elems_2 = list_2[:max_docs]
        else:
            elems_1 = list_1
            elems_2 = list_2

        set_1 = {x["id"] for x in elems_1}
        set_2 = {x["id"] for x in elems_2}
        intersect = set_1.intersection(set_2)

        result = []
        for elem in list_1:
            if elem["id"] in intersect:
                result.append(elem)
        return result

    def _count_modalities(
        self, values: List, modalities: List[str], max_docs: Optional[int] = None
    ) -> int:
        elems = values if max_docs is None else values[:max_docs]

        count_list = []
        for elem in elems:
            count_list += elem["modalities"]
        counter = Counter(count_list)
        filtered_counter = {x: counter[x] for x in counter.keys() if x in modalities}

        result = 0
        for key in filtered_counter.keys():
            result += filtered_counter[key]
        return result

    def _recall(self, num_relevant: int, total_relevant: int) -> str:
        return str(round(num_relevant / total_relevant, 2))

    def _precision(self, num_relevant: int, total_returned: int) -> str:
        return str(round(num_relevant / total_returned, 2))

    def overlap(self, keyword: str, text_modality: str, modalities: List[str]):
        """Execute queries against Lucene and compare the overlap in results"""
        str_modalities = ";".join(modalities)
        query1 = f"q=full_text:{keyword} AND full_text:{text_modality}"
        query2 = f"q=full_text:{keyword}&modalities={str_modalities}"

        base_url = f"{ROOT}/search/?ds={self.dataset}&ft=true&from=2000-01-01&to=2020-12-31&highlight=true&max_docs=2000"
        url1 = f"{base_url}&{query1}"
        url2 = f"{base_url}&{query2}"

        res1 = get(url=url1)
        res2 = get(url=url2)
        if res1.status_code != 200 or res2.status_code != 200:
            raise Exception("The server could not process the request")
        values1 = res1.json()
        values2 = res2.json()

        cap_1 = 10
        cap_2 = 30
        cap_3 = 100

        intersections = self._calc_intersections(values1, values2)
        intersections_10 = self._calc_intersections(values1, values2, cap_1)
        intersections_30 = self._calc_intersections(values1, values2, cap_2)
        intersections_100 = self._calc_intersections(values1, values2, cap_3)

        num_intersections = len(intersections)
        num_inters_10 = len(intersections_10)
        num_inters_30 = len(intersections_30)
        num_inters_100 = len(intersections_100)

        num_images_1 = self._count_modalities(values1, modalities)
        num_images_10_1 = self._count_modalities(values1, modalities, cap_1)
        num_images_30_1 = self._count_modalities(values1, modalities, cap_2)
        num_images_100_1 = self._count_modalities(values1, modalities, cap_3)

        num_images_2 = self._count_modalities(values2, modalities)
        num_images_10_2 = self._count_modalities(values2, modalities, cap_1)
        num_images_30_2 = self._count_modalities(values2, modalities, cap_2)
        num_images_100_2 = self._count_modalities(values2, modalities, cap_3)

        num_imgs_inter = self._count_modalities(intersections, modalities)
        num_imgs_inter_10 = self._count_modalities(intersections_10, modalities, cap_1)
        num_imgs_inter_30 = self._count_modalities(intersections_30, modalities, cap_2)
        num_imgs_inter_100 = self._count_modalities(
            intersections_100, modalities, cap_3
        )

        included_10 = len(self._calc_intersections(values1[:cap_1], values2))
        included_30 = len(self._calc_intersections(values1[:cap_2], values2))
        included_100 = len(self._calc_intersections(values1[:cap_3], values2))

        print("Queries:")
        print(f"\tfull-text only:\t\t {keyword} + {text_modality}")
        print(f"\tfull-text + modalities:\t {keyword} + {str_modalities}")
        print("Number of results")
        print(f"\tfull-text only:\t\t\t {len(values1)}")
        print(f"\tquery full-text + modalities:\t {len(values2)}")
        print("Intersections and Images")
        print(
            "\t\t\tA∩B\tA⊂B\tprecision(A)\trecall(A)\tImages(A∩B)\tImages(A)\tImages(B)"
        )
        print(
            f"\tfirst {cap_1}:\t {num_inters_10}\t{included_10}\t{self._precision(included_10,cap_1)}\t\t{self._recall(included_10, len(values2))}\t\t{num_imgs_inter_10}\t\t{num_images_10_1}\t\t{num_images_10_2}"
        )
        print(
            f"\tfirst {cap_2}:\t {num_inters_30}\t{included_30}\t{self._precision(included_30,cap_2)}\t\t{self._recall(included_30, len(values2))}\t\t{num_imgs_inter_30}\t\t{num_images_30_1}\t\t{num_images_30_2}"
        )
        print(
            f"\tfirst {cap_3}:\t {num_inters_100}\t{included_100}\t{self._precision(included_100,cap_3)}\t\t{self._recall(included_100, len(values2))}\t\t{num_imgs_inter_100}\t\t{num_images_100_1}\t\t{num_images_100_2}"
        )
        print(
            f"\ttotal:\t\t {num_intersections}\t{num_intersections}\t{self._precision(num_intersections,len(values1))}\t\t{self._recall(num_intersections, len(values2))}\t\t{num_imgs_inter}\t\t{num_images_1}\t\t{num_images_2}"
        )


def parse() -> Namespace:
    """Parse from command line"""
    parser = ArgumentParser(prog="calc differences between queries")
    parser.add_argument("keyword")
    parser.add_argument("keyword_modality")
    parser.add_argument("modalities", nargs="+")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse()
    analyzer = OverlapAnalyzer(dataset="cord19")
    analyzer.overlap(args.keyword, args.keyword_modality, args.modalities)
