import heapq
import math

def calculate_edge_cost(start_pos, end_pos, package_weight, priority):
    """
    Kenar maliyet hesaplama fonksiyonu:
    distance × weight + (6 - priority) × 100
    """
    distance = math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
    return distance * package_weight + (6 - priority) * 100

def is_path_valid(start_pos, end_pos, no_fly_zones, current_time):
    """
    Verilen başlangıç ve bitiş noktaları arasındaki yolun uçuş yasağı 
    bölgelerinden geçip geçmediğini kontrol eder
    """
    for zone in no_fly_zones:
        if zone.is_active(current_time) and zone.intersects_path(start_pos, end_pos):
            return False
    return True

def heuristic(current_pos, goal_pos, no_fly_zones, current_time):
    """
    A* algoritması için sezgisel fonksiyon:
    Doğrudan mesafe + uçuş yasağı bölgelerine yakınlık cezası
    """
    direct_distance = math.sqrt((goal_pos[0] - current_pos[0])**2 + (goal_pos[1] - current_pos[1])**2)
    
    # Uçuş yasağı bölgelerine yakınlık cezası
    penalty = 0
    for zone in no_fly_zones:
        if zone.is_active(current_time):
            # Bölgeye olan en yakın mesafeyi hesapla (basitleştirilmiş)
            # Gerçek uygulamada, poligona olan en yakın mesafeyi hesaplamak için daha karmaşık bir algoritma gerekir
            min_dist = float('inf')
            for point in zone.coordinates:
                dist = math.sqrt((current_pos[0] - point[0])**2 + (current_pos[1] - point[1])**2)
                min_dist = min(min_dist, dist)
            
            # Mesafe azaldıkça cezayı artır
            if min_dist < 100:  # 100 metre yakınlık
                penalty += (100 - min_dist) * 5
    
    return direct_distance + penalty

def a_star_algorithm(drone, delivery_points, no_fly_zones, current_time):
    """
    A* algoritması ile bir drone için en uygun teslimat rotasını hesaplar.
    """
    # Debug için çıktılar ekleyelim
    print(f"A* çalıştırılıyor: {len(delivery_points)} teslimat noktası ile")
    
    if not delivery_points:
        print("  Teslimat noktası yok")
        return []
    
    open_set = []
    closed_set = set()
    
    # Başlangıç noktasını ekle
    heapq.heappush(open_set, (0, drone.current_pos, [], 0, drone.current_battery, drone.current_weight))
    
    # Sonuç için en iyi yol
    best_path = []
    most_deliveries = -1
    
    while open_set:
        # En düşük maliyetli yolu seç
        f_score, current_pos, path, g_score, remaining_battery, current_weight = heapq.heappop(open_set)
        
        # Debug çıktılarını azaltalım - çok fazla çıktı performansı etkileyebilir
        if len(path) > 0 and len(path) % 5 == 0:  # Her 5 adımda bir rapor ver
            print(f"  Şu anki yol: {path}, pil: {remaining_battery:.2f}, ağırlık: {current_weight:.2f}")
        
        # Ziyaret edilmiş noktaları kontrol et
        pos_tuple = (current_pos[0], current_pos[1])
        if pos_tuple in closed_set:
            continue
        
        closed_set.add(pos_tuple)
        
        # Eğer mevcut yol daha fazla teslimat içeriyorsa, en iyi yolu güncelle
        if len(path) > most_deliveries:
            most_deliveries = len(path)
            best_path = path.copy()
            print(f"  Yeni en iyi yol bulundu: {best_path}, teslimat sayısı: {most_deliveries}")
        
        # Tüm teslimat noktaları ziyaret edildi mi?
        if len(path) == len(delivery_points):
            print(f"  A* tüm noktaları ziyaret etti: {path}")
            return path
        
        # Teslimat değerlendirirken debugging çıktılarını optimize edelim
        for i, delivery in enumerate(delivery_points):
            if i not in path:
                # Drone'un paketin ağırlığını taşıyabilmesi gerekiyor
                if current_weight + delivery.weight > drone.max_weight:
                    continue  # Debug çıktısı yerine sessizce devam et
                
                # Debug çıktısını azaltalım
                # print(f"    Teslimat {i} değerlendiriliyor: ağırlık={delivery.weight:.2f}")
                
                # Drone'un teslimat noktasına ulaşabilmesi için yeterli pili olmalı
                distance = math.sqrt((current_pos[0] - delivery.pos[0])**2 + (current_pos[1] - delivery.pos[1])**2)
                energy_consumption = drone.calculate_energy_consumption(distance, current_weight + delivery.weight)
                
                if energy_consumption > remaining_battery:
                    # print(f"      Yetersiz pil: {energy_consumption:.2f} > {remaining_battery:.2f}")
                    continue
                
                # Yolun uçuş yasağı bölgelerinden geçmemesi gerekiyor
                valid_path = True
                for zone in no_fly_zones:
                    if zone.is_active(current_time) and zone.intersects_path(current_pos, delivery.pos):
                        valid_path = False
                        # print(f"      Uçuş yasağı bölgesi engeli")
                        break
                
                if not valid_path:
                    continue
                
                # Kenar maliyetini hesapla
                edge_cost = calculate_edge_cost(current_pos, delivery.pos, delivery.weight, delivery.priority)
                new_g_score = g_score + edge_cost
                
                # A* sezgisel değerini hesapla
                h_score = heuristic(delivery.pos, drone.start_pos, no_fly_zones, current_time)
                f_score = new_g_score + h_score
                
                # Yeni durumu open_set'e ekle
                new_path = path.copy() + [i]
                new_battery = remaining_battery - energy_consumption
                # Sadece uygun teslimatlar için bilgi ver
                print(f"      Uygun teslimat {i}: mesafe={distance:.2f}m, yeni pil: {new_battery:.2f}")
                heapq.heappush(open_set, (f_score, delivery.pos, new_path, new_g_score, new_battery, current_weight + delivery.weight))
    
    # Eğer tam bir rota bulunamazsa, en fazla teslimat içeren yolu döndür
    print(f"  A* tam bir rota bulamadı, en iyi yol: {best_path}, teslimat sayısı: {len(best_path)}")
    return best_path  # En iyi yolu döndür (boş liste yerine)