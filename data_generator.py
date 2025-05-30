import random
import math  # Add this import
from datetime import datetime, timedelta
from models import Drone, DeliveryPoint, NoFlyZone

def generate_random_time_window(base_time_str="09:00"):
    """
    Verilen bir başlangıç saatinden itibaren rastgele bir zaman aralığı oluşturur
    """
    base_time = datetime.strptime(base_time_str, "%H:%M")
    
    # Başlangıç zamanı: temel zamandan 0-120 dk sonra
    start_minutes = random.randint(0, 120)
    start_time = base_time + timedelta(minutes=start_minutes)
    
    # Bitiş zamanı: başlangıç zamanından 30-120 dk sonra
    end_minutes = random.randint(30, 120)
    end_time = start_time + timedelta(minutes=end_minutes)  # Fix here: minutes=end_minutes
    
    return (start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))

def generate_random_drones(count, area_size=(1000, 1000)):
    """
    Rastgele drone'lar oluşturur
    """
    drones = []
    for i in range(count):
        drone_id = i + 1
        max_weight = random.uniform(1.0, 5.0)  # 1-5 kg arası
        battery = random.randint(2000, 5000)  # 2000-5000 mAh arası
        speed = random.uniform(5.0, 15.0)  # 5-15 m/s arası
        start_pos = (random.randint(0, area_size[0]), random.randint(0, area_size[1]))
        
        drones.append(Drone(drone_id, max_weight, battery, speed, start_pos))
    
    return drones

def generate_random_deliveries(count, area_size=(1000, 1000)):
    """
    Rastgele teslimat noktaları oluşturur
    """
    deliveries = []
    for i in range(count):
        delivery_id = i + 1
        pos = (random.randint(0, area_size[0]), random.randint(0, area_size[1]))
        weight = random.uniform(0.5, 3.0)  # 0.5-3 kg arası
        priority = random.randint(1, 5)  # 1-5 arası öncelik
        time_window = generate_random_time_window()
        
        deliveries.append(DeliveryPoint(delivery_id, pos, weight, priority, time_window))
    
    return deliveries

def generate_random_no_fly_zones(count, area_size=(1000, 1000), vertex_count_range=(3, 8)):
    """
    Rastgele uçuş yasağı bölgeleri oluşturur
    """
    no_fly_zones = []
    for i in range(count):
        zone_id = i + 1
        
        # Poligonun merkez noktasını belirle
        center_x = random.randint(0, area_size[0])
        center_y = random.randint(0, area_size[1])
        
        # Poligonun köşe sayısını belirle (3-8 arası)
        vertex_count = random.randint(vertex_count_range[0], vertex_count_range[1])
        
        # Poligonun köşelerini oluştur
        radius = random.randint(50, 150)  # Poligonun yarıçapı
        coordinates = []
        
        for j in range(vertex_count):
            angle = 2 * 3.14159 * j / vertex_count
            x = center_x + radius * 0.8 * random.uniform(0.8, 1.2) * math.cos(angle)
            y = center_y + radius * 0.8 * random.uniform(0.8, 1.2) * math.sin(angle)
            coordinates.append((int(x), int(y)))
        
        # Aktif zaman aralığını belirle
        active_time = generate_random_time_window()
        
        no_fly_zones.append(NoFlyZone(zone_id, coordinates, active_time))
    
    return no_fly_zones

def save_data_to_file(drones, deliveries, no_fly_zones, filename="simulation_data.txt"):
    """
    Oluşturulan verileri bir dosyaya kaydeder
    """
    with open(filename, 'w') as f:
        # Drone'ları kaydet
        f.write("DRONES\n")
        for drone in drones:
            f.write(f"{drone.id},{drone.max_weight},{drone.battery},{drone.speed},{drone.start_pos[0]},{drone.start_pos[1]}\n")
        
        # Teslimat noktalarını kaydet
        f.write("\nDELIVERY_POINTS\n")
        for delivery in deliveries:
            f.write(f"{delivery.id},{delivery.pos[0]},{delivery.pos[1]},{delivery.weight},{delivery.priority},{delivery.time_window[0]},{delivery.time_window[1]}\n")
        
        # Uçuş yasağı bölgelerini kaydet
        f.write("\nNO_FLY_ZONES\n")
        for zone in no_fly_zones:
            coords_str = ";".join([f"{x},{y}" for x, y in zone.coordinates])
            f.write(f"{zone.id},{coords_str},{zone.active_time[0]},{zone.active_time[1]}\n")

def load_data_from_file(filename="simulation_data.txt"):
    """
    Dosyadan verileri yükler
    """
    drones = []
    deliveries = []
    no_fly_zones = []
    
    current_section = None
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            
            if line == "DRONES":
                current_section = "drones"
                continue
            elif line == "DELIVERY_POINTS":
                current_section = "deliveries"
                continue
            elif line == "NO_FLY_ZONES":
                current_section = "no_fly_zones"
                continue
            elif not line:
                continue
            
            if current_section == "drones":
                parts = line.split(',')
                drone_id = int(parts[0])
                max_weight = float(parts[1])
                battery = int(parts[2])
                speed = float(parts[3])
                start_pos = (int(parts[4]), int(parts[5]))
                
                drones.append(Drone(drone_id, max_weight, battery, speed, start_pos))
            
            elif current_section == "deliveries":
                parts = line.split(',')
                delivery_id = int(parts[0])
                pos = (int(parts[1]), int(parts[2]))
                weight = float(parts[3])
                priority = int(parts[4])
                time_window = (parts[5], parts[6])
                
                deliveries.append(DeliveryPoint(delivery_id, pos, weight, priority, time_window))
            
            elif current_section == "no_fly_zones":
                parts = line.split(',')
                zone_id = int(parts[0])
                
                # Koordinatları parse et
                coords_str = ','.join(parts[1:-2])
                coords_pairs = coords_str.split(';')
                coordinates = []
                
                for pair in coords_pairs:
                    x, y = pair.split(',')
                    coordinates.append((int(x), int(y)))
                
                active_time = (parts[-2], parts[-1])
                
                no_fly_zones.append(NoFlyZone(zone_id, coordinates, active_time))
    
    return drones, deliveries, no_fly_zones