import json
import os
import re
from datetime import datetime

class ShapeStorage:
    def __init__(self, storage_file="shapes.json"):
        self.storage_file = storage_file
        self.shapes = []
        self._load_shapes()
        self.shape_pattern = re.compile(r"(?:Successfully drawn shape|Đã vẽ thành công hình)\s+([a-zA-Z0-9 áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]+)(?:,\s*(.*))?")
        self.sides_pattern_vi = re.compile(r"các cạnh:\s*([\d.]+ (?:cm|mm|m|inch|ft)(?:,\s*[\d.]+ (?:cm|mm|m|inch|ft))*)")
        self.sides_pattern_en = re.compile(r"sides:\s*([\d.]+ (?:cm|mm|m|inch|ft)(?:,\s*[\d.]+ (?:cm|mm|m|inch|ft))*)")
        self.param_pattern = re.compile(r"([a-zA-Z0-9 áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]+):\s*([\d.]+(?:\s*[a-zA-Z]+)?)")

    def _load_shapes(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.shapes = json.load(f)
            except json.JSONDecodeError:
                self.shapes = []
        else:
            self.shapes = []

    def save_shapes(self):
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self.shapes, f, ensure_ascii=False, indent=2)

    def add_shape(self, shape_name, parameters, language="vi"):
        shape_data = {
            "shape_name": shape_name,
            "parameters": parameters,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        self.shapes.append(shape_data)
        self.save_shapes()
        return shape_data

    def get_all_shapes(self):
        return self.shapes

    def get_shapes_by_name(self, shape_name):
        return [shape for shape in self.shapes if shape["shape_name"] == shape_name]

    def clear_shapes(self):
        self.shapes = []
        self.save_shapes()

    def process_and_save_shape(self, response):
        if "Successfully drawn shape" in response:
            language = "en"
        elif "Đã vẽ thành công hình" in response:
            language = "vi"
        else:
            return None

        shape_match = self.shape_pattern.search(response)
        if not shape_match:
            return None
            
        shape_name = shape_match.group(1)
        params_str = shape_match.group(2) or ""
        params = {}
        
        if language == "vi":
            sides_match = self.sides_pattern_vi.search(params_str)
        else:
            sides_match = self.sides_pattern_en.search(params_str)
        
        if sides_match:
            sides_str = sides_match.group(0)
            params_str = params_str.replace(sides_str, '', 1).strip()
            sides = sides_match.group(1).split(',')
            for i, side in enumerate(sides):
                if language == "vi":
                    params[f"cạnh {chr(97 + i)}"] = side.strip()
                else:
                    params[f"side {chr(97 + i)}"] = side.strip()
        
        param_matches = self.param_pattern.findall(params_str)
        param_counts = {}
        for param_name, param_value in param_matches:
            if param_name in param_counts:
                param_counts[param_name] += 1
                params[f"{param_name} {param_counts[param_name]}"] = param_value
            else:
                param_counts[param_name] = 1
                params[param_name] = param_value
        
        return self.add_shape(shape_name, params, language)

shape_storage = ShapeStorage()