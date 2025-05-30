import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import math
import random
import heapq
import copy

# Modülleri içe aktar
from models import Drone, DeliveryPoint, NoFlyZone
from pathfinding import a_star_algorithm
from csp import backtracking_search
from genetic import genetic_algorithm
from data_generator import (generate_random_drones, generate_random_deliveries, 
                           generate_random_no_fly_zones, save_data_to_file, load_data_from_file)
from visualization import plot_simulation

def run_a_star_simulation(drones, deliveries, no_fly_zones, current_time="09:00"):
    """
    A* algoritması ile bir simülasyon çalıştırır
    """
    start_time = time.time()
    
    drone_routes = {}
    assigned_deliveries = set()
    
    # Öncelik sırasına göre teslimatları sırala
    sorted_deliveries = sorted(deliveries, key=lambda d: d.priority, reverse=True)
    
    # Her drone için optimal rotaları hesapla
    for drone in drones:
        # Henüz atanmamış teslimatları filtrele
        available_deliveries = [d for d in sorted_deliveries if d.id not in assigned_deliveries]
        
        if not available_deliveries:
            break
        
        # Bu drone'a uygun teslimatları belirle (ağırlık ve batarya kısıtları)
        suitable_deliveries = []
        for delivery in available_deliveries:
            if drone.can_carry(delivery.weight) and drone.can_reach(delivery):
                suitable_deliveries.append(delivery)
        
        if not suitable_deliveries:
            continue
        
        # A* algoritması ile en uygun rotayı bul
        optimal_route = a_star_algorithm(drone, suitable_deliveries, no_fly_zones, current_time)
        
        if optimal_route:
            # Önemli değişiklik: Burada teslimat yollarını kaydet ve işaretle
            delivery_ids = []
            for i in optimal_route:
                if i < len(suitable_deliveries):
                    delivery = suitable_deliveries[i]
                    delivery_ids.append(delivery.id)
                    assigned_deliveries.add(delivery.id)
            
            drone_routes[drone.id] = delivery_ids
            
            # Debug için teslimat bilgisi
            print(f"Drone {drone.id} için bulunan teslimatlar: {delivery_ids}")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Performans metriklerini hesapla
    total_deliveries = sum(len(routes) for routes in drone_routes.values())
    completion_percentage = (total_deliveries / len(deliveries)) * 100 if deliveries else 0
    
    # Enerji tüketimini hesapla
    total_energy = 0
    for drone_id, delivery_ids in drone_routes.items():
        if not delivery_ids:  # Boş rota kontrolü
            continue
            
        drone = next((d for d in drones if d.id == drone_id), None)
        if drone is None:  # Drone bulunamadı kontrolü
            print(f"Uyarı: Drone ID {drone_id} bulunamadı!")
            continue
            
        drone_copy = copy.deepcopy(drone)
        
        for delivery_id in delivery_ids:
            try:
                # İlk olarak ID'ye göre teslimatı bul
                delivery = next((d for d in deliveries if d.id == delivery_id), None)
                
                # Eğer ID ile bulunamazsa, indeks olarak dene (A* algoritmasının döndürdüğü şekilde)
                if delivery is None and isinstance(delivery_id, int) and 0 <= delivery_id < len(deliveries):
                    delivery = deliveries[delivery_id]
                
                if delivery is not None:
                    drone_copy.deliver(delivery)
                else:
                    print(f"Uyarı: Teslimat ID/indeks {delivery_id} geçersiz!")
            except Exception as e:
                print(f"Hata: {e} (Drone {drone_id}, Teslimat {delivery_id})")
        
        total_energy += drone_copy.energy_consumed
    
    avg_energy = total_energy / max(1, len([d for d in drone_routes.values() if d]))  # Sıfıra bölme kontrolü
    
    print("\nA* Algoritması Sonuçları:")
    print(f"Tamamlanan Teslimat Yüzdesi: {completion_percentage:.2f}%")
    print(f"Ortalama Enerji Tüketimi: {avg_energy:.2f} mAh")
    print(f"Algoritma Çalışma Süresi: {execution_time:.4f} saniye")
    
    return drone_routes, execution_time, completion_percentage, avg_energy

def run_ga_simulation(drones, deliveries, no_fly_zones, current_time="09:00", generations=100):
    """
    Genetik algoritma ile bir simülasyon çalıştırır
    """
    start_time = time.time()
    
    # Genetik algoritmayı çalıştır
    best_routes, best_fitness = genetic_algorithm(drones, deliveries, no_fly_zones, current_time, generations)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Performans metriklerini hesapla
    total_deliveries = sum(len(routes) for routes in best_routes.values())
    completion_percentage = (total_deliveries / len(deliveries)) * 100
    
    # Enerji tüketimini hesapla
    total_energy = 0
    for drone_id, delivery_indices in best_routes.items():
        drone = next(d for d in drones if d.id == drone_id)
        drone_copy = copy.deepcopy(drone)
        
        for idx in delivery_indices:
            # Instead of finding by id, use the index directly
            # This fixes the StopIteration error
            if idx < len(deliveries):
                delivery = deliveries[idx]
                drone_copy.deliver(delivery)
        
        total_energy += drone_copy.energy_consumed
    
    avg_energy = total_energy / len(drones) if drones else 0
    
    print("\nGenetik Algoritma Sonuçları:")
    print(f"Tamamlanan Teslimat Yüzdesi: {completion_percentage:.2f}%")
    print(f"Ortalama Enerji Tüketimi: {avg_energy:.2f} mAh")
    print(f"Algoritma Çalışma Süresi: {execution_time:.4f} saniye")
    
    return best_routes, execution_time, completion_percentage, avg_energy

def run_comparison(scenario_name, drone_count, delivery_count, no_fly_zone_count):
    """
    A* ve GA algoritmalarını karşılaştırır
    """
    print(f"\n=== Senaryo: {scenario_name} ({drone_count} drone, {delivery_count} teslimat, {no_fly_zone_count} no-fly zone) ===")
    
    # Veri oluştur
    area_size = (1000, 1000)
    drones = generate_random_drones(drone_count, area_size)
    deliveries = generate_random_deliveries(delivery_count, area_size)
    no_fly_zones = generate_random_no_fly_zones(no_fly_zone_count, area_size)
    
    current_time = "09:30"  # Simülasyon saati
    
    # A* algoritması ile çalıştır
    a_star_routes, a_star_time, a_star_completion, a_star_energy = run_a_star_simulation(
        copy.deepcopy(drones), copy.deepcopy(deliveries), no_fly_zones, current_time
    )
    
    # GA algoritması ile çalıştır
    ga_routes, ga_time, ga_completion, ga_energy = run_ga_simulation(
        copy.deepcopy(drones), copy.deepcopy(deliveries), no_fly_zones, current_time, generations=50
    )
    
    # Create figures but don't show them yet
    fig1 = plot_simulation(
        copy.deepcopy(drones), copy.deepcopy(deliveries), no_fly_zones, 
        a_star_routes, current_time, area_size, 
        save_path=f"{scenario_name}_a_star.png", 
        show=False  # Don't show immediately
    )
    
    fig2 = plot_simulation(
        copy.deepcopy(drones), copy.deepcopy(deliveries), no_fly_zones,
        ga_routes, current_time, area_size,
        save_path=f"{scenario_name}_ga.png",
        show=False  # Don't show immediately
    )
    
    # Performans karşılaştırma grafiği
    metrics = ['Tamamlanan Teslimat (%)', 'Ort. Enerji Tüketimi (mAh/100)', 'Çalışma Süresi (s)']
    a_star_values = [a_star_completion, a_star_energy/100, a_star_time]
    ga_values = [ga_completion, ga_energy/100, ga_time]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(metrics))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, a_star_values, width, label='A* Algoritması')
    rects2 = ax.bar(x + width/2, ga_values, width, label='Genetik Algoritma')
    
    ax.set_title(f'Algoritma Performans Karşılaştırması - {scenario_name}')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    
    # Değerleri çubukların üstüne ekle
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    
    plt.tight_layout()
    
    # Show all figures at once at the end
    plt.show()
    
    plt.savefig(f"{scenario_name}_comparison.png", dpi=300, bbox_inches='tight')
    
    # Sonuçları dosyaya kaydet
    with open(f"{scenario_name}_results.txt", 'w') as f:
        f.write(f"=== Senaryo: {scenario_name} ===\n")
        f.write(f"Drone Sayısı: {drone_count}\n")
        f.write(f"Teslimat Sayısı: {delivery_count}\n")
        f.write(f"Uçuş Yasağı Bölge Sayısı: {no_fly_zone_count}\n\n")
        
        f.write("A* Algoritması Sonuçları:\n")
        f.write(f"Tamamlanan Teslimat Yüzdesi: {a_star_completion:.2f}%\n")
        f.write(f"Ortalama Enerji Tüketimi: {a_star_energy:.2f} mAh\n")
        f.write(f"Algoritma Çalışma Süresi: {a_star_time:.4f} saniye\n\n")
        
        f.write("Genetik Algoritma Sonuçları:\n")
        f.write(f"Tamamlanan Teslimat Yüzdesi: {ga_completion:.2f}%\n")
        f.write(f"Ortalama Enerji Tüketimi: {ga_energy:.2f} mAh\n")
        f.write(f"Algoritma Çalışma Süresi: {ga_time:.4f} saniye\n")

def main():
    print("Drone Filo Optimizasyonu Simülasyonu")
    print("=====================================")
    
    # Test senaryoları
    run_comparison("Senaryo1", drone_count=5, delivery_count=20, no_fly_zone_count=2)
    run_comparison("Senaryo2", drone_count=10, delivery_count=50, no_fly_zone_count=5)

if __name__ == "__main__":
    main()