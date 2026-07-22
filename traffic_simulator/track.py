from typing import List, Union
from .constants import PartIndex, SegmentIndex, SegmentTypes, COUNTER
import numpy as np
import pandas as pd

class RoadSegment:
    """Represents a single part of the road."""
    def __init__(self, position: int, segment_type: str) -> None: 
        self.position = position
        self.segment_type = segment_type
        data = SegmentTypes.SEGMENTS[segment_type]
        
        self._SPEED = data[SegmentIndex.SPEED]
        self._length = data[SegmentIndex.LENGTH]
        self._ICON = data[SegmentIndex.ICON]
        self._COLOR = data[SegmentIndex.COLOR]
    
        self.next = None  # Links to the next segment
        
    # ================================================================
    #    Properties Functions
    # ================================================================
    @property
    def segment_speed(self) -> int:
        return self._SPEED
    
    @property
    def segment_length(self) -> int:
        return self._length
    
    @property
    def segment_icon(self) -> str:
        return self._ICON
    
    @property
    def segment_color(self) -> str:
        return self._COLOR

class Track:
    """Manages the linked list of road segments."""
    def __init__(self) -> None:
        """Road generator for cars road."""
        self.head = None  # Start of the road
        # Interactives
        self.number_of_segments = 0
        self.length = 0

        # Interactive objects
        self.road_map = []
        self.lines_dict = {}

        # Track generation
        self._get_segments(predetermined=True if input("Predetermined road[y/Enter]: ") == "y" else False)
        self._segments = self._generate_linked_road()

        self.segment_positions = self.segments[PartIndex.ZONES]
        self.segment_speeds = self.segments[PartIndex.MAX_SPEEDS]
        self.segment_lengths = self.segments[PartIndex.LENGTH]

        self._r = self.length / (np.pi * 2)
        
    # ================================================================
    #    Properties Functions
    # ================================================================   
    @property
    def r(self) -> float:
        return self._r

    @property
    def segments(self) -> np.ndarray:
        return self._segments

    # ================================================================
    #    Node Creation Functions
    # ================================================================
    def add_segment(self, segment_type: str) -> None:
        """Adds a double node to the road. First node is always a road type segment and the other is by choice.
        
        Parameters
        __________
        segment_type: str
            Can be of values: road, road work, speed up, speed down.
            
        Raises
        ______
        TypeError
            If input is not of type str.
        ValueError
            If input is not of right value.
        """
        
        position = COUNTER + 1
        self.number_of_segments += 1
        
        if type(segment_type) is not str:
            raise TypeError("Input variable segment_type must be of type str.")
            
        if segment_type not in SegmentTypes.SEGMENTS.keys():
            raise ValueError("""Input variable segment_type must be one of "road", "road work", "speed up", "speed down".""")
        
        if not self.head:
            self.head = RoadSegment(position=position, segment_type=segment_type)
            return
            
        current = self.head

        while current.next:
            position+=1
            current = current.next 
        current.next = RoadSegment(position=position, segment_type=segment_type) 
        return
        

    def _generate_linked_road(self) -> np.ndarray:
        """Generates a linked road.
        
        Returns
        _______
        segments: np.ndarray
            Data for all the parts of shape (2, number_of_segments).
        """
        if self.number_of_segments==0:
            raise ValueError("No existing nodes.")

        
        segments = np.zeros((3, self.number_of_segments))      
        current = self.head
        
        for counter in range(self.number_of_segments):

            self.road_map.append(f"{current.segment_type}: {current.segment_icon}")
            
            self.length += current.segment_length
            
            segments[PartIndex.LENGTH, counter] = current.segment_length
            segments[PartIndex.ZONES, counter] = self.length
            segments[PartIndex.MAX_SPEEDS, counter] = current.segment_speed
            self.lines_dict[counter] = (self.length-current.segment_length, self.length, current.segment_color)

            current = current.next
        print(f"Road length: {self.length}")
        print("Linked Road: " + " -> ".join(self.road_map))
        
        return segments
        
    def _get_segments(self, predetermined: bool = False) -> None:

        print("Choose from the segment types to create a road: ")
        df = pd.DataFrame.from_dict(
            {key: values[:-1] for key, values in SegmentTypes.SEGMENTS.items()},
            orient="index",
            columns=["Speed Limit", "Length", "Symbol"],
        )
        print(df)

        if not predetermined:
            road = input("1. segment: ")

            while road=="" or road not in SegmentTypes.SEGMENTS.keys():
                road = input("Invalid option. Choose again: ")

            self.add_segment(road)

            while road!="":
                road = input("(ENTER to exit): ")

                while road not in SegmentTypes.SEGMENTS.keys():
                    road = input("Invalid option. Choose again: ")

                self.add_segment(road)

        else:
            self.add_segment("road")
            self.add_segment("city")
            self.add_segment("highway")
            self.add_segment("school")
            self.add_segment("school")
            self.add_segment("school")
            self.add_segment("school")
            self.add_segment("construction")
            self.add_segment("city")

    # ========================================================================================
    #    Active Functions
    # ========================================================================================        
    def change_speed_limit(self, segment : int, new_speed : float) -> None:
        """Change speed limit in one segment on the road."""
        
        if segment >= self.number_of_segments or segment < 0 or type(segment)!=int:
            raise ValueError(f"Value must be of type int between 0 and {self.number_of_segments}.")
        if type(new_speed)==str:
            raise TypeError("new_speed input must be of type int, double or float.")
        
        self._segments[PartIndex.MAX_SPEEDS][segment] = new_speed