"""Interact with local file elements."""

from pathlib import Path

import numpy as np
import tifffile
from tqdm import tqdm


def list_files_and_folders(local_folder: Path) -> tuple:
    """Get contents of a folder sorted into files and folders."""
    contents = local_folder.iterdir()
    files = []
    folders = []
    for element in contents:
        if element.is_file():
            files.append(element)
        elif element.is_dir():
            folders.append(element)
        else:
            raise ValueError(f"{element} is neither file nor folder?")
    return files, folders


def identify_tifs(files: list[Path]) -> list:
    """Identify files that end with .tif in a list of Path objects."""
    tif_files = []
    for file in files:
        if file.suffix in [".tif", ".tiff"]:
            tif_files.append(file)
    return tif_files


def convert_tif_folder_into_file(source_folder: Path,  tif_type: str, output_file: Path | None = None) -> Path:
    """Convert a folder full of single frame tifs into a single multi-frame tif file."""
    if not source_folder.is_dir():
        raise FileNotFoundError(f"{source_folder} does not exist.")

    if output_file is None:
        target_parent = source_folder.parent
        output_file = target_parent / f"{source_folder.name}.tif"
        print(f"No output file given - using {output_file}")
    else:
        assert output_file.suffix == ".tif"
    if output_file.is_file():
        raise FileExistsError(f"{output_file} already exists.")

    tifs = list_tifs(source_folder)
    print(f"{len(tifs)} found in {source_folder}.")
    sorted_tifs = sort_tifs(tifs, tif_type)
    print(f"Loading {sorted_tifs.size} tifs.")
    movie = load_tifs(sorted_tifs)
    print(f"Tifs loaded into movie with shape {movie.shape}.")
    print(f"Saving movie to {output_file}.")
    write_movie_to_tif(movie, output_file)
    return output_file


def list_tifs(local_folder: Path) -> list:
    """List all .tif files in a folder."""
    files, _ = list_files_and_folders(local_folder)
    tif_files = identify_tifs(files)
    return tif_files


def write_movie_to_tif(movie: np.ndarray, target_file: Path) -> None:
    """Write a 3D numpy array (frames, x, y) to a .tif file."""
    tifffile.imwrite(target_file, data=movie, bigtiff=True)


def load_tifs(tif_files: list[Path], dtype=np.uint8) -> np.ndarray:
    """Load single frame tifs into a single 3D numpy array (frames, x, y)."""
    list_of_images = []
    for file in tqdm(tif_files):
        image = tifffile.imread(file).astype(dtype)
        list_of_images.append(image)
    movie = np.stack(list_of_images, axis=0)
    return movie


def sort_tifs(tif_files: list[Path], tif_type: str) -> np.ndarray[Path]:
    """Sort tifs by file name."""
    match tif_type:
        case "leica":
            sorted_tifs = sort_leica_tifs(tif_files)
        case "basler":
            sorted_tifs = sort_basler_tifs(tif_files)
        case _:
            raise ValueError(f"{tif_type} unknown.")
    return sorted_tifs


def sort_leica_tifs(tif_files: list[Path]) -> np.ndarray[Path]:
    """
    Example file name: mapping_with_shielding_t0000_RAW_ch00.tif
    """
    file_names = [file.name for file in tif_files]
    sort_vector = np.argsort(file_names)
    sorted_files = np.asarray(tif_files)[sort_vector]
    return sorted_files


def sort_basler_tifs(tif_files: list[Path]) -> np.ndarray[Path]:
    """
    Example file name: Basler_a2A1920-160umPRO__40349470__20230509_141623734_0000.tiff
    Unfortunately, numbers are not fully zero-padded so sorting needs to be changed a little.
    """
    file_stems = [file.stem for file in tif_files]
    stem_endings = [stem.split("_")[-1] for stem in file_stems]
    stem_endings = [int(ending) for ending in stem_endings]
    sort_vector = np.argsort(stem_endings)
    sorted_files = np.asarray(tif_files)[sort_vector]
    return sorted_files


if __name__ == "__main__":
    SOURCE_FOLDER = Path("/home/mathis/Code/gitlab/labnas/data/mapping_with_shielding")
    TARGET_PARENT = Path("/home/mathis/Code/gitlab/labnas/data/")
    convert_tif_folder_into_file(SOURCE_FOLDER, TARGET_PARENT)