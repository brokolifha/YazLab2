import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

def plot_simulation(drones, deliveries, no_fly_zones, routes=None, current_time="09:00", area_size=(1000, 1000), save_path=None, show=True):
    """
    Simülasyon durumunu görselleştirir
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Alan sınırlarını belirle
    ax.set_xlim(0, area_size[0])
    ax.set_ylim(0, area_size[1])
    
    # Arka plan ve eksen başlıkları
    ax.set_facecolor('#f0f0f0')
    ax.set_title(f'Drone Filo Simülasyonu - {current_time}', fontsize=16)
    ax.set_xlabel('X Koordinatı (m)', fontsize=12)
    ax.set_ylabel('Y Koordinatı (m)', fontsize=12)
    
    # Uçuş yasağı bölgelerini çiz
    for zone in no_fly_zones:
        if zone.is_active(current_time):
            poly = patches.Polygon(zone.coordinates, closed=True, fill=True, 
                                  color='#ff6b6b', alpha=0.4, label='Uçuş Yasağı Bölgesi')
            ax.add_patch(poly)
            
            # Bölge ID'sini ekle
            centroid_x = sum(x for x, _ in zone.coordinates) / len(zone.coordinates)
            centroid_y = sum(y for _, y in zone.coordinates) / len(zone.coordinates)
            ax.text(centroid_x, centroid_y, f"NFZ-{zone.id}", ha='center', fontsize=10)
    
    # Teslimat noktalarını çiz
    for delivery in deliveries:
        if not delivery.is_delivered:
            ax.scatter(delivery.pos[0], delivery.pos[1], color='#339af0', s=100, marker='s', 
                      edgecolors='black', linewidth=1, label='Teslimat Noktası')
            ax.text(delivery.pos[0] + 10, delivery.pos[1] + 10, 
                   f"D{delivery.id} ({delivery.weight}kg, P{delivery.priority})", fontsize=8)
    
    # Drone'ları çiz
    drone_colors = plt.cm.viridis(np.linspace(0, 1, len(drones)))
    
    for i, drone in enumerate(drones):
        ax.scatter(drone.current_pos[0], drone.current_pos[1], color=drone_colors[i], s=150, marker='^', 
                  edgecolors='black', linewidth=1, label=f'Drone {drone.id}')
        ax.text(drone.current_pos[0] + 15, drone.current_pos[1] + 15, 
               f"DR{drone.id} ({drone.current_battery}mAh)", fontsize=8)
    
    # Eğer rotalar varsa, her drone için rotaları çiz
    if routes:
        for drone_id, delivery_indices in routes.items():
            if not delivery_indices:
                continue
            
            drone = next((d for d in drones if d.id == drone_id), None)
            if drone is None:
                continue
                
            points = [drone.start_pos]
            valid_deliveries = []
            
            for idx in delivery_indices:
                # Teslimatı ID olarak kabul et ve bul
                try:
                    delivery = next((d for d in deliveries if d.id == idx), None)
                    if delivery:
                        points.append(delivery.pos)
                        valid_deliveries.append(delivery)
                except:
                    # Eğer ID ile bulamazsa, indeks olarak dene
                    if isinstance(idx, int) and 0 <= idx < len(deliveries):
                        delivery = deliveries[idx]
                        points.append(delivery.pos)
                        valid_deliveries.append(delivery)
            
            # Rotayı çiz (eğer geçerli noktalar varsa)
            if len(points) > 1:
                points_array = np.array(points)
                color = drone_colors[drone_id % len(drone_colors) - 1]
                ax.plot(points_array[:, 0], points_array[:, 1], 
                       color=color, 
                       linestyle='-', marker='o', markersize=3, alpha=0.7)
                
                # Teslimat rotasını göster
                path_desc = f"Drone {drone_id} rotası: " + " → ".join([f"D{d.id}" for d in valid_deliveries])
                print(path_desc)
    
    # Lejant optimizasyonu - aynı etiketleri bir kez göster
    handles, labels = [], []
    legend_mapping = {
        'Teslimat Noktası': {'color': '#339af0', 'marker': 's', 'linestyle': ''},
        'Uçuş Yasağı Bölgesi': {'color': '#ff6b6b', 'marker': '', 'linestyle': '-'}
    }
    
    # Drone'lar için farklı renkler
    for i, drone in enumerate(drones):
        drone_label = f'Drone {drone.id}'
        legend_mapping[drone_label] = {'color': drone_colors[i], 'marker': '^', 'linestyle': ''}
    
    # Lejant öğelerini oluştur
    for label, props in legend_mapping.items():
        if props['marker']:
            handle = plt.Line2D([0], [0], marker=props['marker'], color=props['color'],
                              markerfacecolor=props['color'], markersize=8, linestyle=props['linestyle'])
        else:
            handle = plt.Line2D([0], [0], color=props['color'], linestyle=props['linestyle'], lw=2)
        
        handles.append(handle)
        labels.append(label)
    
    # Lejandı ekle
    ax.legend(handles, labels, loc='upper right')
    
    # Izgara ekle
    ax.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    if show:
        plt.show()
    
    return fig  # Return the figure object