from os import listdir
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from PIL import Image

mapper_chart_synthetic = {
    "Scatter": "gra.sca",
    "Grouped horizontal bar": "gra.his",
    "Grouped vertical bar": "gra.his",
    "Horizontal box": "gra.oth",
    "Vertical box": "gra.oth",
    "Stacked horizontal bar": "gra.his",
    "Stacked vertical bar": "gra.his",
    "Line": "gra.lin",
    "Pie": "gra.oth",
    "Donut": "gra.oth",
}

mapper_chart_2020 = {
    "area": "gra.oth",
    "heatmap": "gra.oth",
    "horizontal_bar": "gra.his",
    "horizontal_interval": "gra.oth",
    "line": "gra.lin",
    "manhattan": "gra.oth",
    "map": "gra.oth",
    "pie": "gra.oth",
    "scatter": "gra.sca",
    "scatter-line": "gra.sca",
    "surface": "gra.oth",
    "venn": "gra.oth",
    "vertical_bar": "gra.his",
    "vertical_box": "gra.oth",
    "vertical_interval": "gra.oth",
}


def load_synthetic_data(base_path: Path, chart_synthetic_path: str) -> pd.DataFrame:
    imgs = []
    img_paths = []
    widths = []
    heights = []
    originals = []
    labels = []

    for json_file in tqdm(listdir(base_path / chart_synthetic_path / "json_gt")):
        json_file_route = base_path / chart_synthetic_path / "json_gt" / json_file
        original_mod = pd.read_json(json_file_route)["task1"]["output"]["chart_type"]

        if not json_file_route.exists():
            continue
        image_name = json_file.replace("json", "png")
        img_path = base_path / chart_synthetic_path / "train" / image_name

        if not img_path.exists():
            print("does not exist", img_path)
            continue

        originals.append(original_mod)
        imgs.append(image_name)
        img_paths.append(str(Path(chart_synthetic_path) / "train" / image_name))
        labels.append(mapper_chart_synthetic[original_mod])

        img = Image.open(img_path)
        width, height = img.size
        widths.append(width)
        heights.append(height)

    df_synthetic = pd.DataFrame(
        list(zip(imgs, img_paths, widths, heights, labels, originals)),
        columns=["img", "img_path", "width", "height", "label", "original"],
    )
    df_synthetic["source"] = "chart-synthetic"
    df_synthetic["is_gt"] = True
    df_synthetic["caption"] = ""

    return df_synthetic


def load_icpr_data(base_path: Path, chart_icpr2020_path: str) -> pd.DataFrame:
    df_icpr = None
    for i in tqdm(listdir(base_path / chart_icpr2020_path)):
        route_image_class = base_path / chart_icpr2020_path / i
        images = listdir(route_image_class)
        image_paths = [base_path / chart_icpr2020_path / i / j for j in images]

        widths = []
        heights = []
        for img_path in image_paths:
            img = Image.open(img_path)
            width, height = img.size
            widths.append(width)
            heights.append(height)

        str_rel_img_paths = [str(Path(chart_icpr2020_path) / i / j) for j in images]
        df_actual = pd.DataFrame(
            {
                "img": images,
                "img_path": str_rel_img_paths,
                "width": widths,
                "height": heights,
            }
        )
        df_actual["original"] = i
        df_actual["label"] = df_actual.apply(
            lambda x: mapper_chart_2020[x.original], axis=1
        )
        df_icpr = pd.concat([df_icpr, df_actual])
    df_icpr["source"] = "chart-icpr2020"
    df_icpr["caption"] = ""
    df_icpr["is_gt"] = True

    return df_icpr


def main():
    base_path = Path("/media/cumulus/curation_data")
    chart_synthetic_path = "chart_synthetic_1"
    chart_icpr2020_path = "chart_icpr2020/ICPR2020_CHARTINFO_UB_PMC_TRAIN_v1.21/images"

    df_synthetic = load_synthetic_data(base_path, chart_synthetic_path)
    df_icpr = load_icpr_data(base_path, chart_icpr2020_path)

    df = pd.concat([df_synthetic, df_icpr])
    df.to_parquet("./chart_synth.parquet")


if __name__ == "__main__":
    main()
