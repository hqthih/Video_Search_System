import os
from typing import Dict, Any
from .gcp_storage import storage_manager
from .load_metadata_from_gcp_storage import (
    load_video_division_random,
    load_video_id2img_id,
    load_audio_id2img_id,
    load_map_keyframes,
    load_id2img_fps,
    load_scene_id2info,
    load_fps,
    load_video_division_tag
)

# Use the imported functions as needed 

def GET_PROJECT_ROOT():
    print(os.getenv('ROOT_FOLDER'))
    # goto the root folder of LogBar
    current_abspath = os.path.abspath(__file__)
    while True:
        if os.path.split(current_abspath)[1] == os.getenv('ROOT_FOLDER') :
            project_root = current_abspath
            break
        else:
            current_abspath = os.path.dirname(current_abspath)
    return project_root

PROJECT_ROOT = GET_PROJECT_ROOT()