import random
import copy

def is_valid_assignment(drone, delivery, no_fly_zones, current_time):
    """
    Bir drone'a bir teslimat atamasının geçerli olup olmadığını kontrol eder
    """
    # Drone paketin ağırlığını taşıyabilmeli
    if not drone.can_carry(delivery.weight):
        return False
    
    # Drone teslimat noktasına ulaşabilmeli
    if not drone.can_reach(delivery):
        return False
    
    # Uçuş yasağı bölgelerine dikkat edilmeli
    for zone in no_fly_zones:
        if zone.is_active(current_time) and zone.intersects_path(drone.current_pos, delivery.pos):
            return False
    
    return True

def backtracking_search(drones, deliveries, no_fly_zones, current_time):
    """
    Backtracking ile CSP çözümü
    """
    # Öncelik sırasına göre teslimatları sırala
    sorted_deliveries = sorted(deliveries, key=lambda d: d.priority, reverse=True)
    
    assignments = {}  # {drone_id: [delivery_ids]}
    for drone in drones:
        assignments[drone.id] = []
    
    def backtrack(index):
        if index == len(sorted_deliveries):
            return True
        
        delivery = sorted_deliveries[index]
        
        # Tüm drone'ları dene
        for drone in drones:
            drone_copy = copy.deepcopy(drone)
            
            # Eğer drone şu anda boşta ise ve atama geçerliyse
            if is_valid_assignment(drone_copy, delivery, no_fly_zones, current_time):
                # Atamayı yap
                drone_copy.deliver(delivery)
                assignments[drone.id].append(delivery.id)
                
                # Diğer teslimatlar için recursive olarak devam et
                if backtrack(index + 1):
                    # Gerçek drone'u güncelle
                    drone.current_pos = drone_copy.current_pos
                    drone.current_battery = drone_copy.current_battery
                    drone.current_weight = drone_copy.current_weight
                    drone.route = drone_copy.route
                    drone.deliveries_completed = drone_copy.deliveries_completed
                    drone.energy_consumed = drone_copy.energy_consumed
                    return True
                
                # Eğer çözüm bulunamazsa, atamayı geri al
                assignments[drone.id].pop()
        
        return False
    
    success = backtrack(0)
    return assignments if success else None