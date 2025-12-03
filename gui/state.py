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
        # Tracked worlds filtering
        self.tracked_world_ids: set = set()
        self.filtered_datacenter_names: List[str] = []
        self.filtered_worlds_by_datacenter: Dict[str, List[str]] = {}
    
    def set_tracked_worlds(self, tracked_world_ids: List[int]):
        """Set the list of tracked world IDs for filtering.
        
        Args:
            tracked_world_ids: List of world IDs that are being tracked
        """
        self.tracked_world_ids = set(tracked_world_ids)
        self._update_filtered_lists()
    
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
        
        # Update filtered lists based on tracked worlds
        self._update_filtered_lists()
        
        # Set default selections from filtered lists
        if self.filtered_datacenter_names and not self.selected_datacenter:
            self.selected_datacenter = self.filtered_datacenter_names[0]
        if self.selected_datacenter and not self.selected_world:
            dc_worlds = self.filtered_worlds_by_datacenter.get(self.selected_datacenter, [])
            if dc_worlds:
                self.selected_world = dc_worlds[0]
    
    def _update_filtered_lists(self):
        """Update filtered datacenter and world lists based on tracked worlds."""
        self.filtered_datacenter_names = []
        self.filtered_worlds_by_datacenter = {}
        
        if not self.tracked_world_ids:
            # No tracked worlds - show all
            self.filtered_datacenter_names = self.datacenter_names.copy()
            self.filtered_worlds_by_datacenter = self.worlds_by_datacenter.copy()
            return
        
        # Filter to only show datacenters that have tracked worlds
        for dc in self.datacenters:
            dc_name = dc.get('name', '')
            if not dc_name:
                continue
            
            # Get tracked worlds in this datacenter
            world_ids = dc.get('worlds', [])
            tracked_in_dc = []
            for wid in world_ids:
                if wid in self.tracked_world_ids:
                    world_name = self.world_id_to_name.get(wid, str(wid))
                    tracked_in_dc.append(world_name)
            
            if tracked_in_dc:
                self.filtered_datacenter_names.append(dc_name)
                self.filtered_worlds_by_datacenter[dc_name] = sorted(tracked_in_dc)
        
        self.filtered_datacenter_names = sorted(self.filtered_datacenter_names)
    
    def change_datacenter(self, datacenter: str) -> List[str]:
        """Change selected datacenter and return worlds in that datacenter.
        
        Args:
            datacenter: Datacenter name
        
        Returns:
            List of world names in the datacenter (filtered by tracked if applicable)
        """
        self.selected_datacenter = datacenter
        dc_worlds = self.get_worlds_for_datacenter(datacenter)
        
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
        """Get worlds for a datacenter (filtered by tracked worlds if applicable).
        
        Args:
            datacenter: Datacenter name, or None for current
        
        Returns:
            List of world names
        """
        dc = datacenter or self.selected_datacenter
        # Return filtered worlds if we have tracked worlds, otherwise all worlds
        if self.tracked_world_ids:
            return self.filtered_worlds_by_datacenter.get(dc, [])
        return self.worlds_by_datacenter.get(dc, [])
    
    def get_filtered_datacenter_names(self) -> List[str]:
        """Get datacenter names filtered by tracked worlds.
        
        Returns:
            List of datacenter names that contain tracked worlds
        """
        if self.tracked_world_ids:
            return self.filtered_datacenter_names
        return self.datacenter_names
