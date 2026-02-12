import numpy as np
import matplotlib.pyplot as plt

class PiezoHarvester:
    """
    Simulates a piezoelectric energy harvesting system embedded in flooring.
    
    Attributes:
        capacitance (float): Capacitance of the piezo element (Farads).
        piezo_coeff_d33 (float): Piezoelectric charge coefficient (C/N).
        load_resistance (float): Electrical load resistance (Ohms).
    """
    
    def __init__(self, capacitance=150e-9, d33=500e-12, load_resistance=10e3):
        # PZT-5H materyali için tipik varsayılan değerler
        self.capacitance = capacitance
        self.d33 = d33
        self.load_resistance = load_resistance

    def generate_footfall_force(self, duration, sampling_rate, freq_hz, avg_force):
        """
        Generates a stochastic (randomized) footfall force profile.
        Real-world data is never perfect; we add Gaussian noise.
        """
        t = np.linspace(0, duration, int(duration * sampling_rate))
        
        # Temel sinüs dalgası (Yürüme ritmi)
        base_signal = np.abs(np.sin(np.pi * freq_hz * t))
        
        # Rastgelelik ekleme (Stochastic noise) - Standart sapma %10
        noise = np.random.normal(0, 0.1, size=len(t))
        
        # Kuvvet profili (Negatif kuvvet olamaz, mutlak değer ve max(0))
        force_profile = avg_force * (base_signal + noise)
        force_profile = np.maximum(force_profile, 0) # Kuvvet 0'ın altına düşemez
        
        return t, force_profile

    def calculate_power(self, force_profile):
        """
        Calculates Voltage and Power output based on force input.
        Simplified Model: V = Q / C = (d33 * F) / C
        Power: P = V^2 / R
        """
        # Voltaj Üretimi (V)
        voltage = (self.d33 * force_profile) / self.capacitance
        
        # Anlık Güç (W)
        power = (voltage ** 2) / self.load_resistance
        
        return voltage, power

    def run_simulation(self, duration=60):
        print(f"--- Simülasyon Başlatılıyor: {duration} saniye ---")
        
        # Parametreler
        fs = 100 # Hz
        avg_weight = 750 # N (Ortalama 76 kg insan)
        pace_freq = 1.8 # Hz (Ortalama yürüme hızı)
        
        # 1. Adım: Kuvvet Verisi Üret
        time, force = self.generate_footfall_force(duration, fs, pace_freq, avg_weight)
        
        # 2. Adım: Güç Hesapla
        voltage, power = self.calculate_power(force)
        
        # 3. Adım: İstatistikler
        total_energy = np.trapz(power, time) # Joule (Integral)
        avg_power = np.mean(power)
        peak_voltage = np.max(voltage)
        
        self._print_report(total_energy, avg_power, peak_voltage)
        self._plot_results(time, force, power, total_energy)

    def _print_report(self, energy, avg_p, peak_v):
        print("\n--- Mühendislik Raporu ---")
        print(f"Toplam Enerji Hasadı : {energy:.4f} Joules")
        print(f"Ortalama Güç Çıkışı  : {avg_p:.4f} Watts")
        print(f"Tepe Voltaj Değeri   : {peak_v:.2f} Volts")
        print("-" * 30)

    def _plot_results(self, t, force, power, total_energy):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        # Grafik 1: Uygulanan Kuvvet
        ax1.plot(t[:500], force[:500], 'tab:blue', label='Zemin Kuvveti (N)')
        ax1.set_ylabel('Kuvvet [N]', fontsize=10, fontweight='bold')
        ax1.set_title('Girdi: Yaya Trafiği Kuvvet Analizi (İlk 5 sn)', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend()
        
        # Grafik 2: Üretilen Güç
        ax2.plot(t[:500], power[:500], 'tab:orange', label='Üretilen Güç (W)')
        ax2.set_ylabel('Güç [W]', fontsize=10, fontweight='bold')
        ax2.set_xlabel('Zaman [s]', fontsize=10)
        ax2.set_title(f'Çıktı: Piezoelektrik Güç Üretimi (Top. Enerji: {total_energy:.2f} J)', fontsize=12)
        ax2.fill_between(t[:500], power[:500], color='tab:orange', alpha=0.3)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig("results_graph.png") # Grafiği dosya olarak kaydeder
print("Grafik 'results_graph.png' olarak kaydedildi.")
        plt.show()

if __name__ == "__main__":
    # Sistemi başlat ve simülasyonu çalıştır
    piezo_system = PiezoHarvester(capacitance=150e-9, load_resistance=12000)
    piezo_system.run_simulation(duration=60)
