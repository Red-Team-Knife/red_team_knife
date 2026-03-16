import os
from mitreattack.stix20 import MitreAttackData
from loguru import logger as l

class BlueController:
    def __init__(self, json_path="data/mitre/enterprise-attack.json"):
        self.json_path = json_path
        self.mitre_data = None
        
        if os.path.exists(self.json_path):
            l.info(f"Loading MITRE dataset from {self.json_path}...")
            try:
                self.mitre_data = MitreAttackData(self.json_path)
                l.success("MITRE dataset loaded successfully.")
            except Exception as e:
                l.error(f"Error initializing MITRE dataset: {e}")
        else:
            l.error(f"Dataset not found at {self.json_path}")

    def get_mitigations_for_tool(self, tool_name, scan_results=None):
        from models.mitre_mapper import get_technique_dynamically
        
        # 1. Clean metadata (ignore keys that are not tools)
        metadata_keys = ["host", "protocol", "resource", "name", "creation_date", "creation_time"]
        if tool_name in metadata_keys:
            return None

        # 2. DYNAMIC MAPPING: Pass the tool name and the actual scan results to the AI
        tech_id = get_technique_dynamically(tool_name, scan_results)
        
        if not tech_id or not self.mitre_data:
            l.warning(f"No MITRE mapping found for tool: {tool_name}")
            return None

        # 3. Retrieve the technique object
        technique = self.mitre_data.get_object_by_attack_id(tech_id, 'attack-pattern')
        if not technique:
            l.error(f"Technique {tech_id} not found in the dataset.")
            return None

        # 4. Retrieve mitigations ('mitigates' relationship)
        mitigations = self.mitre_data.get_mitigations_mitigating_technique(technique.id)
        
        mitigation_list = []
        for m in mitigations:
            try:
                obj = m.get('object') if isinstance(m, dict) else getattr(m, 'object', m)
                
                if hasattr(obj, 'name'): name = obj.name
                elif isinstance(obj, dict): name = obj.get('name', 'Generic Mitigation')
                else: name = "Generic Mitigation"
                
                if hasattr(obj, 'description'): description = obj.description
                elif isinstance(obj, dict): description = obj.get('description', 'See MITRE documentation for details.')
                else: description = "See MITRE documentation for details."
                
                mitigation_list.append({"name": name, "description": description})
            except Exception as e:
                l.error(f"Error parsing mitigation object: {e}")

        # 5. Fallback if no direct mitigations exist
        if not mitigation_list:
            mitigation_list.append({
                "name": "Detection Strategy",
                "description": (
                    "For this technique, MITRE ATT&CK does not list direct preventive mitigations. "
                    "It is recommended to monitor system logs (IDS/IPS) to detect anomalous patterns."
                )
            })

        return {
            "tool_name": tool_name.replace("_", " ").title(),
            "technique_id": tech_id,
            "name": technique.name if hasattr(technique, 'name') else tech_id,
            "description": technique.description if hasattr(technique, 'description') else "No description available.",
            "mitigations": mitigation_list
        }
