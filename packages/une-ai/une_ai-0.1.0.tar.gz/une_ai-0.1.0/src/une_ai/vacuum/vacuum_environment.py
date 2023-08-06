import numpy as np
import random
import math

from une_ai.models.grid_map import GridMap
from une_ai.models.environment import Environment

class VacuumEnvironment(Environment):

    def __init__(self, w, h):
        super().__init__('Vacuum world')
        self._w = w
        self._h = h
        self._dirt_map = GridMap(w, h)
        self._walls_map = GridMap(w, h)
        self._explored_tiles = GridMap(w, h)
        self._initialise_walls(0.01)
        self._initialise_dirt(0.01)

        self._score = 0
    
    def get_percepts(self, agent):
        # starts the percepts with current values of sensors
        percepts = agent.read_sensors()
        agent_x, agent_y = percepts['location-sensor']
        coords = {
            'center': (agent_x, agent_y),
            'north': (agent_x, agent_y-1),
            'south': (agent_x, agent_y+1),
            'west': (agent_x-1, agent_y),
            'east': (agent_x+1, agent_y)
        }

        # reset bumper sensors
        for direction in coords.keys():
            if direction != 'center':
                percepts['bumper-sensor-{0}'.format(direction)] = False
        
        # check if the agent is crashing against a wall
        cur_direction = agent.read_actuator_value('wheels-direction')
        if self.is_wall(agent_x, agent_y):
            # there is a wall!
            # set agent location sensor to past x, y
            if cur_direction == 'north':
                past_x, past_y = coords['south']
            elif cur_direction == 'south':
                past_x, past_y = coords['north']
            elif cur_direction == 'west':
                past_x, past_y = coords['east']
            elif cur_direction == 'east':
                past_x, past_y = coords['west']
            
            
            percepts['location-sensor'] = (past_x, past_y)

            # update the bumper sensor
            percepts['bumper-sensor-{0}'.format(cur_direction)] = True
        
        # now check if there is dirt in the surroundings
        for coord_name, coord in coords.items():
            try:
                is_dirty = self.is_dirty(coord[0], coord[1])
            except:
                is_dirty = False
            percepts['dirt-sensor-{0}'.format(coord_name)] = is_dirty
            
        return percepts
    
    def get_score(self):
        return self._score

    def get_width(self):
        return self._w
    
    def get_height(self):
        return self._h
    
    def set_explored(self, pos_x, pos_y):
        self._explored_tiles.set_item_value(pos_x, pos_y, True)
        
    def _initialise_walls(self, wall_density=0.01):
        total_size = self._w*self._h
        n_walls = math.floor(total_size*wall_density)
        empty_tiles = self._walls_map.find_value(False)
        walls_coords = random.sample(empty_tiles, n_walls)
        for coord in walls_coords:
            orientation = random.choice(['h', 'v'])
            length = random.choice([3, 4, 5])
            cur_x = coord[0]
            cur_y = coord[1]
            for i in range(0, length):
                if cur_x >= self._w or cur_y >= self._h:
                    #if out of bounds, end
                    break
                self._walls_map.set_item_value(cur_x, cur_y, True)
                if orientation == 'h':
                    cur_x += 1
                else:
                    cur_y += 1
    
    def _initialise_dirt(self, dirt_density=0.01):
        total_size = self._w*self._h
        n_dirt = math.floor(total_size*dirt_density)
        self._spawn_dirt(n_dirt)
            
    def _spawn_dirt(self, k=1):
        condition_func = lambda walls_map: np.logical_and(walls_map == False, self._dirt_map.get_map() == False)
        valid_coords = self._walls_map.find_value_by_condition(condition_func)
        new_coord = random.sample(valid_coords, k)
        for coord in new_coord:
            self._dirt_map.set_item_value(coord[0], coord[1], True)

    def is_dirty(self, pos_x, pos_y):
        return self._dirt_map.get_item_value(pos_x, pos_y)
    
    def is_wall(self, pos_x, pos_y):
        try:
            return self._walls_map.get_item_value(pos_x, pos_y)
        except:
            # out of bounds, it's a wall
            return True
    
    def remove_dirt(self, x, y):
        try:
            is_dirt = self.is_dirty(x, y)
            if is_dirt:
                self._score += 1
                self._dirt_map.set_item_value(x, y, False)
        except:
            # we may be out of bounds, but there is no dirt outside bounds
            pass
    
    def get_dirt_coords(self):
        return self._dirt_map.find_value(True)
    
    def get_walls_coords(self):
        return self._walls_map.find_value(True)
    
    def get_free_coords(self):
        condition_func = lambda walls_map: np.logical_and(walls_map == False, self._dirt_map.get_map() == False)
        return self._walls_map.find_value_by_condition(condition_func)
    
    def get_explored_tiles_coords(self):
        return self._explored_tiles.find_value(True)