from datetime import datetime
import math

class Drone:
    def __init__(self, id, max_weight, battery, speed, start_pos):
        self.id = id
        self.max_weight = max_weight  # kg cinsinden
        self.battery = battery  # mAh cinsinden
        self.speed = speed  # m/s cinsinden
        self.start_pos = start_pos  # (x, y) koordinatları
        self.current_pos = start_pos
        self.current_battery = battery
        self.route = []
        self.current_weight = 0
        self.deliveries_completed = 0
        self.energy_consumed = 0
        self.rule_violations = 0
        
    def can_carry(self, weight):
        return self.current_weight + weight <= self.max_weight
    
    def calculate_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def calculate_energy_consumption(self, distance, weight):
        # Basit bir enerji tüketim modeli
        base_consumption = distance * 0.1  # her metre için 0.1 mAh
        weight_factor = weight * 0.2  # her kg için 0.2 mAh/metre
        return base_consumption + (distance * weight_factor)
    
    def can_reach(self, delivery_point):
        distance = self.calculate_distance(self.current_pos, delivery_point.pos)
        energy_needed = self.calculate_energy_consumption(distance, delivery_point.weight)
        return energy_needed <= self.current_battery
    
    def deliver(self, delivery_point):
        if not self.can_carry(delivery_point.weight) or not self.can_reach(delivery_point):
            return False
        
        distance = self.calculate_distance(self.current_pos, delivery_point.pos)
        energy_consumed = self.calculate_energy_consumption(distance, delivery_point.weight)
        
        self.current_pos = delivery_point.pos
        self.current_battery -= energy_consumed
        self.energy_consumed += energy_consumed
        self.route.append(delivery_point.id)
        self.deliveries_completed += 1
        
        # Delivery sonrası ağırlık güncellemesi (paketin teslim edildiği varsayılır)
        self.current_weight = 0  
        
        return True
    
    def reset(self):
        self.current_pos = self.start_pos
        self.current_battery = self.battery
        self.route = []
        self.current_weight = 0
        self.deliveries_completed = 0
        self.energy_consumed = 0
        self.rule_violations = 0


class DeliveryPoint:
    def __init__(self, id, pos, weight, priority, time_window):
        self.id = id
        self.pos = pos  # (x, y) koordinatları
        self.weight = weight  # kg cinsinden
        self.priority = priority  # 1: düşük, 5: yüksek
        self.time_window = time_window  # (başlangıç, bitiş) saatleri
        self.is_delivered = False
        
    def __lt__(self, other):
        # Priority queue için karşılaştırma operatörü
        return self.priority > other.priority


class NoFlyZone:
    def __init__(self, id, coordinates, active_time):
        self.id = id
        self.coordinates = coordinates  # [(x1,y1), (x2,y2), ... ]
        self.active_time = active_time  # (başlangıç, bitiş) saatleri
        # Merkez noktasını hesapla
        self.center = (
            sum(x for x, _ in coordinates) / len(coordinates),
            sum(y for _, y in coordinates) / len(coordinates)
        )
        
    def is_active(self, current_time):
        return self.active_time[0] <= current_time <= self.active_time[1]
    
    def contains_point(self, point):
        """
        Ray casting algoritması ile bir noktanın poligon içinde olup olmadığını kontrol eder
        """
        x, y = point
        n = len(self.coordinates)
        inside = False
        
        p1x, p1y = self.coordinates[0]
        for i in range(1, n + 1):
            p2x, p2y = self.coordinates[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def intersects_path(self, start_pos, end_pos, steps=10):
        """
        İki nokta arasındaki yolun poligon ile kesişip kesişmediğini kontrol eder
        """
        # Performans optimizasyonu: Kaba kutu kontrolü ile hızlı eleme
        min_x = min(p[0] for p in self.coordinates) - 5  # 5 metrelik tolerans
        max_x = max(p[0] for p in self.coordinates) + 5
        min_y = min(p[1] for p in self.coordinates) - 5
        max_y = max(p[1] for p in self.coordinates) + 5
        
        # Yol kutunun dışındaysa hızlı dönüş
        path_min_x = min(start_pos[0], end_pos[0])
        path_max_x = max(start_pos[0], end_pos[0])
        path_min_y = min(start_pos[1], end_pos[1])
        path_max_y = max(start_pos[1], end_pos[1])
        
        if (path_max_x < min_x or path_min_x > max_x or
            path_max_y < min_y or path_min_y > max_y):
            return False
        
        # İki nokta arasında bir dizi nokta oluştur ve her birinin poligon içinde olup olmadığını kontrol et
        for i in range(steps + 1):
            t = i / steps
            x = start_pos[0] * (1 - t) + end_pos[0] * t
            y = start_pos[1] * (1 - t) + end_pos[1] * t
            if self.contains_point((x, y)):
                return True
        return False