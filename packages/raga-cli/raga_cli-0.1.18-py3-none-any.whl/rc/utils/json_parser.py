
import json
import yaml

from rc.utils.config import get_config_value

def get_dict_value(data, key, default=None):
    current_value = data       
    if isinstance(current_value, dict):
        if key in current_value:
            current_value = current_value[key]
        else:
            return default
    elif isinstance(current_value, list):
        try:
            index = int(key)
            current_value = current_value[index]
        except (ValueError, IndexError):
            return default
    else:
        return default
    return current_value

def filter_annotation(annotation, class_maps):
    filtered_annotation = {"confidence":1, "roi_embedding":[]}
    
    bbox = annotation.get("bbox")
    if bbox is not None:
        filtered_annotation["bbox"] = bbox
    
    category_id = annotation.get("category_id")
    if category_id is not None and category_id in class_maps:
        filtered_annotation["class"] = class_maps[category_id]
    else:
        filtered_annotation["class"] = ""
    
    return filtered_annotation

def convert_bbox(image, detections):
    from rc.cli.utils import calculate_coordinates
    height = image["height"]
    width = image["height"]
    temp_detections = []
    for detection  in detections:
        detection['bbox'] = calculate_coordinates(detection['bbox'], width, height)
        temp_detections.append(detection)
    return temp_detections
    
    


def get_annotations_by_image_id(annotations, class_maps):
    annotations_dict = {}
    
    for annotation in annotations:
        image_id = annotation.get('image_id')
        if image_id:
            if image_id not in annotations_dict:
                annotations_dict[image_id] = []
            annotations_dict[image_id].append(filter_annotation(annotation, class_maps))
    
    return annotations_dict


def merge_images_annotations(images, annotations, class_maps):
    merged_data = []
    annotations_by_image_id = get_annotations_by_image_id(annotations, class_maps)
    
    for image in images:
        image_id = image['id']
        if image_id in annotations_by_image_id:
            image['detections'] = convert_bbox(image, annotations_by_image_id[image_id])
        else:
            image['detections'] = []
        merged_data.append(image)
    
    return merged_data



def convert_to_result_json_format(data, dataset, model_name):
    from rc.cli.utils import datetime_to_units
    new_data = []

    for item in data:
        new_item = {
            "projectId": int(get_config_value('project_id')),
            "inputs": [item["file_name"]],
            "attributes": {"weather":"--"},
            "capture_time": datetime_to_units(item["date_captured"], unit='seconds'),
            "source": dataset,
            "event_index": None,
            "output_type": "",
            "model_id": model_name,
            "outputs": [
                {
                    "frame_id": 1,
                    "detections": item["detections"]
                }
            ],
            "image_embedding": [],
            "caption": ""
        }
        new_data.append(new_item)
    return new_data

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
            




