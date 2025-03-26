import os
from typing import Dict, Any
from .gcp_storage import storage_manager

# Constants for GCP Storage paths
DICT_BASE_PATH = "dict"
VIDEO_DIVISION_RANDOM_PATH = os.path.join(DICT_BASE_PATH, "video_division_random.json")
VIDEO_ID2IMG_ID_PATH = os.path.join(DICT_BASE_PATH, "video_id2img_id.json")
AUDIO_ID2IMG_ID_PATH = os.path.join(DICT_BASE_PATH, "audio_id2img_id.json")
MAP_KEYFRAMES_PATH = os.path.join(DICT_BASE_PATH, "map_keyframes.json")
ID2IMG_FPS_PATH = os.path.join(DICT_BASE_PATH, "id2img_fps.json")
SCENE_ID2INFO_PATH = os.path.join(DICT_BASE_PATH, "scene_id2info.json")
FPS_PATH = os.path.join(DICT_BASE_PATH, "fps.json")
VIDEO_DIVISION_TAG_PATH = os.path.join(DICT_BASE_PATH, "video_division_tag.json")

def load_video_division_random() -> Dict[str, Any]:
    """Load video division random data from GCP Storage."""
    return storage_manager.load_json_with_cache(VIDEO_DIVISION_RANDOM_PATH)

def load_video_id2img_id() -> Dict[str, Any]:
    """Load video ID to image ID mapping from GCP Storage."""
    return storage_manager.load_json_with_cache(VIDEO_ID2IMG_ID_PATH)

def load_audio_id2img_id() -> Dict[str, Any]:
    """Load audio ID to image ID mapping from GCP Storage."""
    return storage_manager.load_json_with_cache(AUDIO_ID2IMG_ID_PATH)

def load_map_keyframes() -> Dict[str, Any]:
    """Load keyframe mapping data from GCP Storage."""
    return storage_manager.load_json_with_cache(MAP_KEYFRAMES_PATH)

def load_id2img_fps() -> Dict[str, Any]:
    """Load image ID to FPS mapping from GCP Storage."""
    return storage_manager.load_json_with_cache(ID2IMG_FPS_PATH)

def load_scene_id2info() -> Dict[str, Any]:
    """Load scene ID to info mapping from GCP Storage."""
    return storage_manager.load_json_with_cache(SCENE_ID2INFO_PATH)

def load_fps() -> Dict[str, Any]:
    """Load FPS data from GCP Storage."""
    return storage_manager.load_json_with_cache(FPS_PATH)

def load_video_division_tag() -> Dict[str, Any]:
    """Load video division tag data from GCP Storage."""
    return storage_manager.load_json_with_cache(VIDEO_DIVISION_TAG_PATH) 