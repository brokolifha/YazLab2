import random
import copy
import numpy as np

def initialize_population(drones, deliveries, no_fly_zones, current_time, population_size=50):
    """
    Genetik algoritma için başlangıç popülasyonunu oluşturur
    """
    population = []
    
    for _ in range(population_size):
        # Rastgele bir rota oluştur
        individual = {}
        available_deliveries = list(range(len(deliveries)))
        
        for drone in drones:
            individual[drone.id] = []
            drone_copy = copy.deepcopy(drone)
            
            # Teslimatları rastgele sırala
            random.shuffle(available_deliveries)
            
            for delivery_idx in available_deliveries[:]:
                delivery = deliveries[delivery_idx]
                
                # Eğer drone bu teslimatı yapabilirse
                if drone_copy.can_carry(delivery.weight) and drone_copy.can_reach(delivery):
                    # Uçuş yasağı bölgelerini kontrol et
                    valid_path = True
                    for zone in no_fly_zones:
                        if zone.is_active(current_time) and zone.intersects_path(drone_copy.current_pos, delivery.pos):
                            valid_path = False
                            break
                    
                    if valid_path:
                        # Teslimatı drone'a ata
                        drone_copy.deliver(delivery)
                        individual[drone.id].append(delivery_idx)
                        available_deliveries.remove(delivery_idx)
        
        population.append(individual)
    
    return population

def calculate_fitness(individual, drones, deliveries, no_fly_zones, current_time):
    """
    Bir bireyin uygunluk değerini hesaplar:
    fitness = teslimat sayısı × 100 - (enerji tüketimi × 0.2) - (kural ihlalleri × 2000)
    """
    total_deliveries = 0
    total_energy = 0
    total_violations = 0
    
    drone_copies = {drone.id: copy.deepcopy(drone) for drone in drones}
    
    # Performans optimizasyonu: Ağır hesaplamaları minimize et
    for drone_id, delivery_indices in individual.items():
        if not delivery_indices:  # Boş teslimat listesi kontrolü
            continue
            
        drone = drone_copies[drone_id]
        
        # Yolu önceden kontrol ederek gereksiz hesaplamaları önle
        current_pos = drone.current_pos
        
        for idx in delivery_indices:
            if idx >= len(deliveries):  # Geçersiz indeksleri atla
                total_violations += 1
                continue
                
            delivery = deliveries[idx]
            
            # Drone'un teslimat yapabilme durumunu kontrol et
            if not drone.can_carry(delivery.weight) or not drone.can_reach(delivery):
                total_violations += 1
                continue
            
            # Uçuş yasağı bölgelerini kontrol et
            valid_path = True
            for zone in no_fly_zones:
                if zone.is_active(current_time) and zone.intersects_path(drone.current_pos, delivery.pos):
                    valid_path = False
                    total_violations += 1
                    break
            
            if not valid_path:
                continue
            
            # Teslimatı yap
            drone.deliver(delivery)
            total_deliveries += 1
            total_energy += drone.energy_consumed
    
    # Uygunluk hesaplama
    fitness = (total_deliveries * 100) - (total_energy * 0.2) - (total_violations * 2000)
    return fitness

def crossover(parent1, parent2):
    """
    İki ebeveyn arasında çaprazlama yapar
    """
    child = {}
    
    # Her drone için çaprazlama yap
    for drone_id in parent1.keys():
        # Rastgele bir kesim noktası seç
        if len(parent1[drone_id]) > 0 and len(parent2[drone_id]) > 0:
            cut_point = random.randint(0, min(len(parent1[drone_id]), len(parent2[drone_id])))
            
            # İlk ebeveynden ilk kısmı, ikinci ebeveynden ikinci kısmı al
            child[drone_id] = parent1[drone_id][:cut_point] + parent2[drone_id][cut_point:]
            
            # Tekrar eden teslimatları kontrol et ve kaldır
            delivery_set = set()
            unique_deliveries = []
            
            for delivery_idx in child[drone_id]:
                if delivery_idx not in delivery_set:
                    delivery_set.add(delivery_idx)
                    unique_deliveries.append(delivery_idx)
            
            child[drone_id] = unique_deliveries
        else:
            # Eğer bir ebeveynin bu drone için teslimatı yoksa, diğerini kopyala
            child[drone_id] = parent1[drone_id].copy() if parent1[drone_id] else parent2[drone_id].copy()
    
    return child

def mutation(individual, mutation_rate=0.1):
    """
    Bireyde mutasyon gerçekleştirir
    """
    mutated = copy.deepcopy(individual)
    
    for drone_id, deliveries in mutated.items():
        if deliveries and random.random() < mutation_rate:
            # Rastgele bir teslimat seç ve değiştir
            if len(deliveries) > 1:
                idx1 = random.randint(0, len(deliveries) - 1)
                idx2 = random.randint(0, len(deliveries) - 1)
                while idx1 == idx2:
                    idx2 = random.randint(0, len(deliveries) - 1)
                
                # İki teslimatın yerini değiştir
                deliveries[idx1], deliveries[idx2] = deliveries[idx2], deliveries[idx1]
    
    return mutated

def genetic_algorithm(drones, deliveries, no_fly_zones, current_time, generations=100, population_size=50):
    """
    Genetik algoritma ile en uygun rota planını belirler
    """
    # Başlangıç popülasyonunu oluştur
    population = initialize_population(drones, deliveries, no_fly_zones, current_time, population_size)
    
    best_individual = None
    best_fitness = float('-inf')
    
    for gen in range(generations):
        # Tüm bireylerin uygunluk değerlerini hesapla
        fitness_values = [calculate_fitness(ind, drones, deliveries, no_fly_zones, current_time) for ind in population]
        
        # En iyi bireyi bul
        current_best_idx = np.argmax(fitness_values)
        current_best_individual = population[current_best_idx]
        current_best_fitness = fitness_values[current_best_idx]
        
        if current_best_fitness > best_fitness:
            best_individual = copy.deepcopy(current_best_individual)
            best_fitness = current_best_fitness
        
        # Yeni popülasyon oluştur
        new_population = []
        
        # Elit bireyleri doğrudan yeni popülasyona aktar (en iyi %10)
        elite_count = max(1, int(0.1 * population_size))
        elite_indices = np.argsort(fitness_values)[-elite_count:]
        for idx in elite_indices:
            new_population.append(copy.deepcopy(population[idx]))
        
        # Geri kalan popülasyonu çaprazlama ve mutasyon ile oluştur
        while len(new_population) < population_size:
            # Turnuva seçimi ile ebeveyn seç
            parent1_idx = random.randint(0, len(population) - 1)
            parent2_idx = random.randint(0, len(population) - 1)
            
            # Daha yüksek uygunluk değerine sahip ebeveynleri seç
            if fitness_values[parent1_idx] < fitness_values[parent2_idx]:
                parent1 = population[parent2_idx]
                parent2 = population[parent1_idx]
            else:
                parent1 = population[parent1_idx]
                parent2 = population[parent2_idx]
            
            # Çaprazlama
            child = crossover(parent1, parent2)
            
            # Mutasyon
            child = mutation(child)
            
            new_population.append(child)
        
        population = new_population
        
        # İlerlemeyi göster
        if gen % 10 == 0:
            print(f"Generation {gen}: Best Fitness = {best_fitness}")
    
    return best_individual, best_fitness