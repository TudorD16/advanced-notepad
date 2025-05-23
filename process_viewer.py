import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from datetime import datetime
import numpy as np
import subprocess
import json
import platform

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced System Monitor - CPU & GPU")
        self.root.geometry("1400x800")
        self.root.attributes('-topmost', True)
        
        # Culori dark cu neon
        self.bg_color = "#0a0a0a"
        self.frame_bg = "#1a1a1a"
        self.text_color = "#ffffff"
        self.neon_blue = "#00ffff"
        self.neon_pink = "#ff00ff"
        self.neon_green = "#00ff00"
        self.neon_yellow = "#ffff00"
        self.neon_red = "#ff0000"
        
        self.root.configure(bg=self.bg_color)
        
        # Date pentru grafice
        self.max_points = 120  # 2 minute de date
        self.cpu_data = deque(maxlen=self.max_points)
        self.gpu_data = deque(maxlen=self.max_points)
        self.time_data = deque(maxlen=self.max_points)
        self.timestamps = deque(maxlen=self.max_points)
        
        # Date pentru core-uri CPU
        self.cpu_cores_count = psutil.cpu_count()
        self.cpu_cores_data = [deque(maxlen=self.max_points) for _ in range(self.cpu_cores_count)]
        
        # Maxime
        self.cpu_max = 0
        self.cpu_max_time = "N/A"
        self.gpu_max = 0
        self.gpu_max_time = "N/A"
        
        # Layer info
        self.gpu_layers = 0
        self.cpu_layers = 0
        
        # GPU detection method
        self.gpu_method = self.detect_gpu_method()
        
        # Inițializare date
        for i in range(self.max_points):
            self.cpu_data.append(0)
            self.gpu_data.append(0)
            self.time_data.append(i)
            self.timestamps.append(datetime.now())
            for core_data in self.cpu_cores_data:
                core_data.append(0)
        
        self.setup_ui()
        self.start_monitoring()
    
    def detect_gpu_method(self):
        """Detect the best method to get GPU information"""
        # Try nvidia-smi first
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'nvidia-smi'
        except:
            pass
        
        # Try wmi on Windows
        if platform.system() == "Windows":
            try:
                import wmi
                return 'wmi'
            except ImportError:
                pass
        
        # Fallback to basic detection
        return 'basic'
    
    def get_gpu_info_nvidia_smi(self):
        """Get GPU info using nvidia-smi"""
        try:
            # Get GPU utilization
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,name', 
                                   '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines:
                    data = lines[0].split(', ')
                    if len(data) >= 4:
                        return {
                            'name': data[3].strip(),
                            'load': float(data[0]),
                            'memory_used': float(data[1]),
                            'memory_total': float(data[2])
                        }
        except Exception as e:
            print(f"Error getting GPU info via nvidia-smi: {e}")
        return None
    
    def get_gpu_info_wmi(self):
        """Get GPU info using WMI (Windows only)"""
        try:
            import wmi
            c = wmi.WMI()
            
            # Get GPU info
            for gpu in c.Win32_VideoController():
                if gpu.Name and 'nvidia' in gpu.Name.lower():
                    # Note: WMI doesn't provide real-time utilization, so we'll simulate
                    return {
                        'name': gpu.Name,
                        'load': np.random.uniform(10, 30),  # Simulated load
                        'memory_used': 1024,  # Simulated
                        'memory_total': 8192  # Simulated
                    }
        except Exception as e:
            print(f"Error getting GPU info via WMI: {e}")
        return None
    
    def get_gpu_info_basic(self):
        """Basic GPU detection fallback"""
        # This is a fallback that provides simulated data
        return {
            'name': 'GPU (Basic Detection)',
            'load': np.random.uniform(5, 25),  # Simulated load
            'memory_used': 512,  # Simulated
            'memory_total': 4096  # Simulated
        }
        
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titlu
        title_label = tk.Label(main_frame, text="ADVANCED SYSTEM MONITOR", 
                              font=("Arial Black", 24, "bold"),
                              bg=self.bg_color, fg=self.neon_blue)
        title_label.pack(pady=(0, 10))
        
        # Frame pentru informații principale
        info_frame = tk.Frame(main_frame, bg=self.frame_bg, relief=tk.RAISED, borderwidth=2)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # CPU Info
        cpu_frame = tk.Frame(info_frame, bg=self.frame_bg)
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(cpu_frame, text="CPU", font=("Arial", 16, "bold"),
                bg=self.frame_bg, fg=self.neon_pink).pack()
        
        self.cpu_percent_label = tk.Label(cpu_frame, text="0%", 
                                         font=("Arial", 36, "bold"),
                                         bg=self.frame_bg, fg=self.neon_pink)
        self.cpu_percent_label.pack()
        
        self.cpu_cores_label = tk.Label(cpu_frame, text="Cores: 0", 
                                       font=("Arial", 12),
                                       bg=self.frame_bg, fg=self.text_color)
        self.cpu_cores_label.pack()
        
        self.cpu_freq_label = tk.Label(cpu_frame, text="Freq: 0 MHz", 
                                      font=("Arial", 12),
                                      bg=self.frame_bg, fg=self.text_color)
        self.cpu_freq_label.pack()
        
        self.cpu_max_label = tk.Label(cpu_frame, text="Max: 0%", 
                                     font=("Arial", 10, "bold"),
                                     bg=self.frame_bg, fg=self.neon_yellow)
        self.cpu_max_label.pack()
        
        self.cpu_max_time_label = tk.Label(cpu_frame, text="at N/A", 
                                          font=("Arial", 9),
                                          bg=self.frame_bg, fg=self.text_color)
        self.cpu_max_time_label.pack()
        
        # Separator
        separator = tk.Frame(info_frame, bg=self.neon_blue, width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # GPU Info
        gpu_frame = tk.Frame(info_frame, bg=self.frame_bg)
        gpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(gpu_frame, text="GPU", font=("Arial", 16, "bold"),
                bg=self.frame_bg, fg=self.neon_green).pack()
        
        self.gpu_percent_label = tk.Label(gpu_frame, text="0%", 
                                         font=("Arial", 36, "bold"),
                                         bg=self.frame_bg, fg=self.neon_green)
        self.gpu_percent_label.pack()
        
        self.gpu_name_label = tk.Label(gpu_frame, text="GPU: N/A", 
                                      font=("Arial", 12),
                                      bg=self.frame_bg, fg=self.text_color)
        self.gpu_name_label.pack()
        
        self.gpu_memory_label = tk.Label(gpu_frame, text="Memory: 0/0 MB", 
                                        font=("Arial", 12),
                                        bg=self.frame_bg, fg=self.text_color)
        self.gpu_memory_label.pack()
        
        self.gpu_max_label = tk.Label(gpu_frame, text="Max: 0%", 
                                     font=("Arial", 10, "bold"),
                                     bg=self.frame_bg, fg=self.neon_yellow)
        self.gpu_max_label.pack()
        
        self.gpu_max_time_label = tk.Label(gpu_frame, text="at N/A", 
                                          font=("Arial", 9),
                                          bg=self.frame_bg, fg=self.text_color)
        self.gpu_max_time_label.pack()
        
        # GPU Method indicator
        self.gpu_method_label = tk.Label(gpu_frame, text=f"Method: {self.gpu_method}", 
                                        font=("Arial", 8),
                                        bg=self.frame_bg, fg=self.text_color)
        self.gpu_method_label.pack()
        
        # Separator
        separator2 = tk.Frame(info_frame, bg=self.neon_blue, width=2)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Layer Info
        layer_frame = tk.Frame(info_frame, bg=self.frame_bg)
        layer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        tk.Label(layer_frame, text="LAYERS", font=("Arial", 16, "bold"),
                bg=self.frame_bg, fg=self.neon_blue).pack()
        
        self.gpu_layers_label = tk.Label(layer_frame, text="GPU Layers: 0", 
                                        font=("Arial", 14),
                                        bg=self.frame_bg, fg=self.neon_green)
        self.gpu_layers_label.pack(pady=5)
        
        self.cpu_layers_label = tk.Label(layer_frame, text="CPU Layers: 0", 
                                        font=("Arial", 14),
                                        bg=self.frame_bg, fg=self.neon_pink)
        self.cpu_layers_label.pack(pady=5)
        
        # Frame pentru core-uri CPU
        cores_frame = tk.Frame(main_frame, bg=self.frame_bg, relief=tk.RAISED, borderwidth=2)
        cores_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(cores_frame, text="CPU CORES ACTIVITY", 
                font=("Arial", 14, "bold"),
                bg=self.frame_bg, fg=self.neon_pink).pack(pady=5)
        
        self.cores_container = tk.Frame(cores_frame, bg=self.frame_bg)
        self.cores_container.pack(fill=tk.X, padx=10, pady=10)
        
        self.core_labels = []
        self.core_bars = []
        
        # Creează widget-uri pentru fiecare core
        for i in range(self.cpu_cores_count):
            core_frame = tk.Frame(self.cores_container, bg=self.frame_bg)
            core_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            label = tk.Label(core_frame, text=f"Core {i}", 
                           font=("Arial", 10),
                           bg=self.frame_bg, fg=self.text_color)
            label.pack()
            
            # Progress bar pentru core
            bar_frame = tk.Frame(core_frame, bg=self.frame_bg, height=100, width=30)
            bar_frame.pack_propagate(False)
            bar_frame.pack()
            
            bar = tk.Frame(bar_frame, bg=self.neon_pink, width=30)
            bar.place(x=0, rely=1.0, relheight=0, anchor='sw')
            
            percent_label = tk.Label(core_frame, text="0%", 
                                   font=("Arial", 9),
                                   bg=self.frame_bg, fg=self.text_color)
            percent_label.pack()
            
            self.core_labels.append(percent_label)
            self.core_bars.append(bar)
        
        # Frame pentru grafice
        graph_frame = tk.Frame(main_frame, bg=self.frame_bg, relief=tk.RAISED, borderwidth=2)
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurare matplotlib
        plt.style.use('dark_background')
        self.fig = Figure(figsize=(14, 5), dpi=100, facecolor=self.frame_bg)
        self.ax = self.fig.add_subplot(111)
        
        self.ax.set_facecolor(self.bg_color)
        self.ax.set_xlabel('Timp (secunde)', color=self.text_color)
        self.ax.set_ylabel('Utilizare (%)', color=self.text_color)
        self.ax.set_ylim(0, 105)
        self.ax.grid(True, alpha=0.3, color=self.text_color)
        
        # Linii pentru grafice
        self.cpu_line, = self.ax.plot([], [], color=self.neon_pink, linewidth=2, 
                                      label='CPU', marker='o', markersize=4)
        self.gpu_line, = self.ax.plot([], [], color=self.neon_green, linewidth=2, 
                                      label='GPU', marker='o', markersize=4)
        
        self.ax.legend(loc='upper right', framealpha=0.8)
        
        # Canvas pentru grafic
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Toolbar pentru navigare
        toolbar_frame = tk.Frame(graph_frame, bg=self.frame_bg)
        toolbar_frame.pack(fill=tk.X, padx=10)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # Annotation pentru hover
        self.annotation = self.ax.annotate("", xy=(0,0), xytext=(20,20), 
                                         textcoords="offset points",
                                         bbox=dict(boxstyle="round", fc=self.frame_bg, alpha=0.9),
                                         arrowprops=dict(arrowstyle="->", color=self.neon_yellow))
        self.annotation.set_visible(False)
        
        # Conectare evenimente mouse
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        
        # Animație
        self.ani = animation.FuncAnimation(self.fig, self.update_graph, 
                                         interval=1000, blit=False)
        
    def on_hover(self, event):
        if event.inaxes == self.ax:
            # Găsește cel mai apropiat punct
            if len(self.cpu_data) > 0:
                x_data = list(range(len(self.cpu_data)))
                
                # Convertește coordonatele mouse-ului
                x_mouse = event.xdata
                
                if x_mouse is not None:
                    # Găsește indexul cel mai apropiat
                    idx = min(range(len(x_data)), key=lambda i: abs(x_data[i] - x_mouse))
                    
                    # Obține valorile
                    cpu_val = self.cpu_data[idx]
                    gpu_val = self.gpu_data[idx]
                    time_val = self.timestamps[idx].strftime("%H:%M:%S")
                    
                    # Actualizează annotation
                    self.annotation.xy = (x_data[idx], max(cpu_val, gpu_val))
                    text = f"Time: {time_val}\nCPU: {cpu_val:.1f}%\nGPU: {gpu_val:.1f}%"
                    self.annotation.set_text(text)
                    self.annotation.set_visible(True)
                else:
                    self.annotation.set_visible(False)
            else:
                self.annotation.set_visible(False)
        else:
            self.annotation.set_visible(False)
        
        self.canvas.draw_idle()
        
    def get_gpu_info(self):
        """Get GPU info using the detected method"""
        if self.gpu_method == 'nvidia-smi':
            return self.get_gpu_info_nvidia_smi()
        elif self.gpu_method == 'wmi':
            return self.get_gpu_info_wmi()
        else:
            return self.get_gpu_info_basic()
    
    def get_layer_info(self):
        # Simulare - în realitate ar trebui să interoghezi framework-ul ML folosit
        # Pentru demonstrație, calculăm pe baza utilizării memoriei
        gpu_info = self.get_gpu_info()
        if gpu_info and gpu_info['memory_used'] > 0:
            # Estimare layers pe GPU bazat pe memoria folosită
            self.gpu_layers = int(gpu_info['memory_used'] / 100)  # 100MB per layer (exemplu)
            # Restul pe CPU
            self.cpu_layers = max(0, 32 - self.gpu_layers)  # Presupunem 32 layers total
        else:
            self.gpu_layers = 0
            self.cpu_layers = 0
        
    def update_data(self):
        while True:
            try:
                current_time = datetime.now()
                
                # CPU Info general
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_freq = psutil.cpu_freq()
                cpu_cores = psutil.cpu_count()
                
                # CPU per core
                cpu_percent_per_core = psutil.cpu_percent(percpu=True, interval=0.1)
                
                # Update CPU labels
                self.cpu_percent_label.config(text=f"{cpu_percent:.1f}%")
                self.cpu_cores_label.config(text=f"Cores: {cpu_cores}")
                if cpu_freq:
                    self.cpu_freq_label.config(text=f"Freq: {cpu_freq.current:.0f} MHz")
                
                # Update maxim CPU
                if cpu_percent > self.cpu_max:
                    self.cpu_max = cpu_percent
                    self.cpu_max_time = current_time.strftime("%H:%M:%S")
                    self.cpu_max_label.config(text=f"Max: {self.cpu_max:.1f}%")
                    self.cpu_max_time_label.config(text=f"at {self.cpu_max_time}")
                
                # Update core-uri
                for i, (core_percent, label, bar) in enumerate(zip(cpu_percent_per_core, self.core_labels, self.core_bars)):
                    label.config(text=f"{core_percent:.0f}%")
                    # Update bar height
                    bar.place(relheight=core_percent/100)
                    # Colorare în funcție de utilizare
                    if core_percent > 80:
                        bar.config(bg=self.neon_red)
                    elif core_percent > 50:
                        bar.config(bg=self.neon_yellow)
                    else:
                        bar.config(bg=self.neon_pink)
                    
                    # Salvează datele pentru fiecare core
                    if i < len(self.cpu_cores_data):
                        self.cpu_cores_data[i].append(core_percent)
                
                # GPU Info
                gpu_info = self.get_gpu_info()
                if gpu_info:
                    gpu_percent = gpu_info['load']
                    self.gpu_percent_label.config(text=f"{gpu_percent:.1f}%")
                    self.gpu_name_label.config(text=f"GPU: {gpu_info['name'][:30]}")
                    self.gpu_memory_label.config(
                        text=f"Memorie: {gpu_info['memory_used']:.0f}/{gpu_info['memory_total']:.0f} MB"
                    )
                    
                    # Update maxim GPU
                    if gpu_percent > self.gpu_max:
                        self.gpu_max = gpu_percent
                        self.gpu_max_time = current_time.strftime("%H:%M:%S")
                        self.gpu_max_label.config(text=f"Max: {self.gpu_max:.1f}%")
                        self.gpu_max_time_label.config(text=f"at {self.gpu_max_time}")
                else:
                    gpu_percent = 0
                    self.gpu_percent_label.config(text="N/A")
                    self.gpu_name_label.config(text="GPU: Not detected")
                
                # Update layer info
                self.get_layer_info()
                self.gpu_layers_label.config(text=f"GPU Layers: {self.gpu_layers}")
                self.cpu_layers_label.config(text=f"CPU Layers: {self.cpu_layers}")
                
                # Adaugă date pentru grafice
                self.cpu_data.append(cpu_percent)
                self.gpu_data.append(gpu_percent)
                self.timestamps.append(current_time)
                
                # Efecte vizuale pentru valori mari
                if cpu_percent > 80:
                    self.cpu_percent_label.config(fg=self.neon_yellow)
                elif cpu_percent > 90:
                    self.cpu_percent_label.config(fg=self.neon_red)
                else:
                    self.cpu_percent_label.config(fg=self.neon_pink)
                    
                if gpu_percent > 80:
                    self.gpu_percent_label.config(fg=self.neon_yellow)
                elif gpu_percent > 90:
                    self.gpu_percent_label.config(fg=self.neon_red)
                else:
                    self.gpu_percent_label.config(fg=self.neon_green)
                
            except Exception as e:
                print(f"Error updating data: {e}")
                
            time.sleep(1)
    
    def update_graph(self, frame):
        x_data = list(range(len(self.cpu_data)))
        
        self.cpu_line.set_data(x_data, list(self.cpu_data))
        self.gpu_line.set_data(x_data, list(self.gpu_data))
        
        self.ax.set_xlim(0, self.max_points - 1)
        
        return self.cpu_line, self.gpu_line
    
    def start_monitoring(self):
        monitor_thread = threading.Thread(target=self.update_data, daemon=True)
        monitor_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()