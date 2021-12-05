import conventer


class Pass():
    def __init__(self, name, cathegory, height,
                 heels_type, connects_with, link,
                 x_coord, y_coord, connect_1_type, connect_1_name,
                 connect_2_type, connect_2_name) -> None:

        self.name = name
        self.cathegory = cathegory
        self.height = int(height)
        self.heels_type = heels_type
        self.connects_with = connects_with
        self.link = link
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.connect_1_type = connect_1_type
        self.connect_1_name = connect_1_name
        self.connect_2_type = connect_2_type
        self.connect_2_name = connect_2_name


class Land():
    def __init__(self, name, l_type, connections, prev_land, passed, left) -> None:
        self.l_type = l_type
        self.name = name
        self.connections = connections
        self.prev_land = prev_land
        self.passed = passed
        self.left = left
        self.x_coord = 0
        self.y_coord = 0
    
    def __lt__(self, other):
        return self.passed < other.passed
    
    def __eq__(self, other):
        return self.name == other.name and self.l_type == other.l_type
    
    def __str__(self) -> str:
        return self.l_type+"."+self.name


class Connection():
    def __init__(self, land: Land, pass_obj: str, distanse=0.001) -> None:
        self.land = land
        self.pass_obj = pass_obj
        self.distanse = distanse


def are_lands_equal(land1: Land, land2: Land):
    return land1.l_type == land2.l_type and land1.name == land2.name


def are_passes_equal(pass_obj_1: Land, pass_obj_2: Land):
    return pass_obj_1.name == pass_obj_2.name


def find_land_if_exist(land, lands):
    equal_lands = [x for x in lands if are_lands_equal(x, land)]
    if len(equal_lands):
        this_land_in_lands = equal_lands[0]
    else:
        this_land_in_lands = land
        lands.append(land)

    return this_land_in_lands


def convent_pass_to_lands(pass_obj: Pass, lands: list):
    land1 = find_land_if_exist(Land(pass_obj.connect_1_name,
                                    pass_obj.connect_1_type, [], None, 0, 0), lands)
    land2 = find_land_if_exist(Land(pass_obj.connect_2_name,
                                    pass_obj.connect_2_type, [], None, 0, 0), lands)
    for land in (land1, land2):

        if are_lands_equal(land, land1):
            land.connections.append(Connection(land2, pass_obj))
        else:
            land.connections.append(Connection(land1, pass_obj))
        # lands.append(land)

    return lands


def distance_between(x1, y1, x2, y2):
    return ((x1-x2)**2+(y1-y2)**2)**0.5*80

def dist_betw(obj1, obj2):
    x1 = obj1.x_coord
    y1 = obj1.y_coord
    x2 = obj2.x_coord
    y2 = obj2.y_coord    
    return ((x1-x2)**2+(y1-y2)**2)**0.5*80

def calculate_land_coonnections_len(lands):

    for land in lands:
        number_of_connections = len(land.connections)
        if number_of_connections == 1:
            land.connections[0].distanse = 0.001
            land.x_coord = land.connections[0].pass_obj.x_coord
            land.y_coord = land.connections[0].pass_obj.y_coord
        elif number_of_connections > 1:
            sum_x = 0
            sum_y = 0
            for connection in land.connections:
                sum_x += connection.pass_obj.x_coord
                sum_y += connection.pass_obj.y_coord
            # if land.x_coord == 0:
            land.x_coord = sum_x/number_of_connections
            # if land.y_coord == 0:
            land.y_coord = sum_y/number_of_connections
            # print(land.name, land.x_coord, land.y_coord)
    for land in lands:
        for connection in land.connections:
            connection.distanse = distance_between(connection.land.x_coord,
                                                   connection.land.y_coord,
                                                   connection.pass_obj.x_coord,
                                                   connection.pass_obj.y_coord) + \
                + distance_between(land.x_coord,
                                   land.y_coord,
                                   connection.pass_obj.x_coord,
                                   connection.pass_obj.y_coord)
    return lands


class Graph:
    def __init__(self, cathegory) -> None:
        self._cathegory = cathegory

    def generate(self):
        """
        Генерирует список объектов типа Land. Land — в данном случае — не только долина, 
        но и река/ледник т.п., то есть место, куда выходит перевал
        """
        json_passes_reader = conventer.PointsConventer()
        points_json = json_passes_reader.get_passes_of_cathegory(
            self._cathegory)
        passes = []
        for pt in points_json:
            ps = Pass(*(["0"])*12)
            for key in pt:
                ps.__setattr__(key, pt[key])
                # print(key, pt[key])
            passes.append(ps)
        lands = []
        for pass_obj in passes:
            lands = convent_pass_to_lands(pass_obj, lands)
        lands = calculate_land_coonnections_len(lands)
        for land in lands:
            for connection in land.connections:
                pass
                # print(land.l_type+"."+land.name, "соединяется через", connection.pass_obj.name, "с",
                #       connection.land.l_type+"."+connection.land.name, "расстоянием", connection.distanse)
        
        # print(len(lands))
        return lands

