import os
from .error import ArSiteMakerError

def check_args(glb_path,marker_path, url):
    if not os.path.exists(glb_path):
        raise ArSiteMakerError(f"glb file not found {glb_path}")
    if os.path.splitext(glb_path)[1] != ".glb" :
        raise ArSiteMakerError("ar_site_marker supports only .glb file")
    if marker_path is None and url is None:
        raise ArSiteMakerError("Please specify --marker_path or --url")
    if marker_path is not None and url is not None :
        print("Warning : your option --marker_path will be ignored")
        return
    if marker_path is not None:
        if not os.path.exists(marker_path):
            raise ArSiteMakerError(f"marker image not found {marker_path}")
