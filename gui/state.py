"""
Application state management.
"""

from typing import List, Dict, Optional


class AppState:
    """Manages global application state."""
    
    def __init__(self):
        """Initialize application state."""
        self.selected_datacenter: str = ""
        self.selected_world: str = ""
        self.worlds: List[str] = []
        self.datacenters: List[Dict] = []
        self.datacenter_names: List[str] = []
        self.worlds_by_datacenter: Dict[str, List[str]] = {}
        self.world_id_to_name: Dict[int, str] = {}
        self.world_name_to_id: Dict[str, int] = {}
        self.current_view: str = "dashboard"
    
    def set_datacenters(self, datacenters: List[Dict], world_id_to_name: Dict[int, str]):
        """Set datacenter information.
        
        Args:
            datacenters: List of datacenter dictionaries
            world_id_to_name: Mapping of world IDs to names
        """
        self.datacenters = datacenters
        self.world_id_to_name = world_id_to_name
        self.world_name_to_id = {name: wid for wid, name in world_id_to_name.items()}
        self.worlds = []
        self.datacenter_names = []
        self.worlds_by_datacenter = {}
        
        for dc in datacenters:
            dc_name = dc.get('name', '')
            if dc_name:
                self.datacenter_names.append(dc_name)
                # Convert world IDs to names
                world_ids = dc.get('worlds', [])
                world_names = [self.world_id_to_name.get(wid, str(wid)) for wid in world_ids]
                self.worlds_by_datacenter[dc_name] = sorted(world_names)
                self.worlds.extend(world_names)
        
        self.datacenter_names = sorted(self.datacenter_names)
        self.worlds = sorted(set(self.worlds))
        
        # Set default selections
        if self.datacenter_names and not self.selected_datacenter:
            self.selected_datacenter = self.datacenter_names[0]
        if self.selected_datacenter and not self.selected_world:
            dc_worlds = self.worlds_by_datacenter.get(self.selected_datacenter, [])
            if dc_worlds:
                self.selected_world = dc_worlds[0]
    
    def change_datacenter(self, datacenter: str) -> List[str]:
        """Change selected datacenter and return worlds in that datacenter.
        
        Args:
            datacenter: Datacenter name
        
        Returns:
            List of world names in the datacenter
        """
        self.selected_datacenter = datacenter
        dc_worlds = self.worlds_by_datacenter.get(datacenter, [])
        
        # Auto-select first world if current is not in datacenter
        if self.selected_world not in dc_worlds and dc_worlds:
            self.selected_world = dc_worlds[0]
        
        return dc_worlds
    
    def change_world(self, world: str):
        """Change selected world.
        
        Args:
            world: World name
        """
        self.selected_world = world
    
    def get_worlds_for_datacenter(self, datacenter: Optional[str] = None) -> List[str]:
        """Get worlds for a datacenter.
        
        Args:
            datacenter: Datacenter name, or None for current
        
        Returns:
            List of world names
        """
        dc = datacenter or self.selected_datacenter
        return self.worlds_by_datacenter.get(dc, [])
