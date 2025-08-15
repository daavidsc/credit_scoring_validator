# utils/response_collector.py

import json
import os
from typing import Dict, List, Any
from utils.logger import setup_logger

logger = setup_logger("response_collector", "results/logs/response_collector.log")

class ResponseCollector:
    """Centralized collector for all API responses across all analysis modules"""
    
    def __init__(self, output_dir="results/responses"):
        self.output_dir = output_dir
        self.all_responses = []
        os.makedirs(output_dir, exist_ok=True)
    
    def add_response(self, module_name: str, input_data: Dict, output_data: Dict, metadata: Dict = None):
        """Add a single API response to the collection"""
        response_record = {
            "module": module_name,
            "input": input_data,
            "output": output_data,
            "metadata": metadata or {},
            "timestamp": None  # Could add timestamp here
        }
        self.all_responses.append(response_record)
        logger.debug(f"Added response from {module_name} (total: {len(self.all_responses)})")
    
    def add_responses_batch(self, module_name: str, responses: List[Dict]):
        """Add a batch of responses from a module"""
        for response in responses:
            # Handle different response formats
            if "input" in response and "output" in response:
                self.add_response(module_name, response["input"], response["output"], response.get("metadata", {}))
            else:
                # For legacy format, treat the whole response as output
                self.add_response(module_name, {}, response, {})
        
        logger.info(f"Added {len(responses)} responses from {module_name}")
    
    def save_all_responses(self, filename="all_responses.jsonl"):
        """Save all collected responses to a single file"""
        output_path = os.path.join(self.output_dir, filename)
        with open(output_path, "w") as f:
            for response in self.all_responses:
                f.write(json.dumps(response) + "\n")
        
        logger.info(f"Saved {len(self.all_responses)} total responses to {output_path}")
        return output_path
    
    def get_responses_by_module(self, module_name: str) -> List[Dict]:
        """Get all responses from a specific module"""
        return [r for r in self.all_responses if r.get("module") == module_name]
    
    def get_all_responses(self) -> List[Dict]:
        """Get all collected responses"""
        return self.all_responses
    
    def get_response_count(self) -> int:
        """Get total number of responses collected"""
        return len(self.all_responses)
    
    def get_module_counts(self) -> Dict[str, int]:
        """Get response counts by module"""
        counts = {}
        for response in self.all_responses:
            module = response.get("module", "unknown")
            counts[module] = counts.get(module, 0) + 1
        return counts
    
    def clear(self):
        """Clear all collected responses"""
        self.all_responses = []
        logger.info("Cleared all collected responses")

# Global response collector instance
global_collector = ResponseCollector()

def get_collector() -> ResponseCollector:
    """Get the global response collector instance"""
    return global_collector

def reset_collector():
    """Reset the global response collector"""
    global global_collector
    global_collector.clear()
