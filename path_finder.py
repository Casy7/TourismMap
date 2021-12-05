from functools import total_ordering
import graph_builder
from queue import Queue, PriorityQueue

class PathFindingAlgorithm:
    def __init__(self, cathegory, start_land_name, end_land_name) -> None:
        self._cathegory = cathegory
        self._start_land_name = start_land_name
        self._end_land_name = end_land_name
        self._path = self.findOptimalPath()
        self._total_distanse = 0.0
    
    @property
    def path(self):
        return self._path
    
    def find_land_by_name(self, land_name, lands):
        for land in lands:
            if land.l_type+"."+land.name == land_name:
                return land
    
    def findOptimalPath(self):
        graph_generator = graph_builder.Graph(cathegory=self._cathegory)
        graph = graph_generator.generate()
        start_land_name = self._start_land_name
        start_land = self.find_land_by_name(start_land_name, graph)
        end_land_name = self._end_land_name
        end_land = self.find_land_by_name(end_land_name, graph)
        
        # Дальше сам алгоритм

        frontier = PriorityQueue()
        frontier.put(start_land, 0)
        came_from = {}
        visited = []
        start_land.prev_land= None

        while not frontier.empty():
            current = frontier.get()

            if current == end_land:
                break
            connections = [x.land for x in current.connections]
            for next in connections:
                if next not in visited:
                    priority = graph_builder.distance_between(end_land.x_coord, end_land.y_coord, next.x_coord, next.y_coord)
                    next.passed+=priority
                    next.prev_land = current
                    frontier.put(next, priority)
                    visited.append(current)
                    
        way = []
        way.append(end_land)
        prev_land = end_land.prev_land
        while prev_land.__str__() != start_land_name:
            way.append(prev_land)
            prev_land = prev_land.prev_land
        way.append(start_land)  
        way = way[::-1]
        for land in way:
            print(land)
        self._path = way
        return way

    def __str__(self) -> str:
        out_str = ""
        way = self._path
        total_dist = 0
        for land_index in range(len(self._path)-1):
            land = way[land_index]
            next_land = way[land_index+1]
            out_str+=land.__str__()
            
            out_str+= " -> ("
            for connection in land.connections:
                if connection.land == next_land:
                    total_dist += graph_builder.dist_betw(land, connection.pass_obj)
                    out_str+= str(round(graph_builder.dist_betw(land, connection.pass_obj), 3))
                    out_str+="км) -> "
                    pass_obj = connection.pass_obj
                    out_str += pass_obj.name + " ("+pass_obj.cathegory+", "+pass_obj.height+") -> ("
                    total_dist += graph_builder.dist_betw(connection.pass_obj, next_land)
                    out_str+= str(round(graph_builder.dist_betw(connection.pass_obj, next_land), 3))
                    out_str+="км) -> "
                    break
        print("Итого: "+str(round(total_dist, 3))+"км")
            
                    
            
        out_str+=self._path[-1].__str__()
        return out_str
    