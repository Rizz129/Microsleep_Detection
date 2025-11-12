import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mediapipe as mp
import numpy as np
import pygame

# Parameter Smoothing (Perbaikan Noise)
EMA_ALPHA = 0.35 

# ==========================
# KONFIGURASI
# ==========================
DEFAULT_ALARM_FILEPATH = "red-alert_nuclear_buzzer-99741.mp3" # Pastikan file ini ada di direktori Anda!

RESOLUSI = {
    "240p": (320, 240),
    "360p": (480, 360),
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080)
}

# ==========================
# FUNGSI EAR
# ==========================
def calculate_EAR(eye):
    """Menghitung Eye Aspect Ratio (EAR) dari 6 titik landmark mata."""
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)


class FaceApp(tk.Tk):
    def __init__(self, mixer_initialized):
        super().__init__()
        self.title("🎯 DROWSINESS DETECTION SYSTEM")
        self.geometry("700x650")
        
        self.smoothed_ear = 0.0
        
        self.log_available = mixer_initialized
        self.running = False
        self.start_time = time.time()
        
        # Status Variables
        self.drowsy_count = 0
        self.last_face_detected_time = time.time()
        self.face_detected = False
        self.was_sleepy = False
        self.is_alarming = False
        self.popup = None
        self.popup_close_time = None
        self.is_compact = False
        
        # Mediapipe Init
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(144, 238, 144)) 
        self.mp_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_mesh.FaceMesh(refine_landmarks=True, static_image_mode=False, max_num_faces=1) 
        
        # Variables
        self.mode = tk.StringVar(value="User")
        self.res_var = tk.StringVar(value="480p")
        self.ear_threshold = tk.DoubleVar(value=0.23)
        self.sleep_time_set = tk.DoubleVar(value=1.2)
        self.reset_timeout = tk.DoubleVar(value=5.0)
        self.alarm_path = tk.StringVar(value=DEFAULT_ALARM_FILEPATH)
        
        # Build UI
        self.build_ui()
        
        # ====================================================================
        # PERBAIKAN: Memindahkan trace_add dan update_input_states ke akhir __init__
        # Hal ini menjamin bahwa metode update_input_states telah sepenuhnya dibuat
        # dan terasosiasi dengan instance 'self' sebelum dipanggil/direferensikan.
        # ====================================================================
        self.mode.trace_add("write", self.update_input_states)
        self.update_input_states()
        self.update_timer()
        
    # ==========================
    # UI BUILD - SOFT GRADIENT THEME
    # ==========================
    def build_ui(self):
        # Skema Warna Baru (Soft Blue/Green)
        bg_dark_soft = "#2c3e50"
        bg_card_soft = "#34495e"
        accent_soft = "#2980b9"
        highlight_soft = "#1abc9c"
        text_light = "#ecf0f1"
        
        self.configure(bg=bg_dark_soft)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Dark.TFrame', background=bg_dark_soft)
        style.configure('Card.TFrame', background=bg_card_soft)
        style.configure('Dark.TLabel', background=bg_dark_soft, foreground=text_light, font=('Segoe UI', 10))
        style.configure('Card.TLabel', background=bg_card_soft, foreground=text_light, font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=bg_dark_soft, foreground=highlight_soft, font=('Segoe UI', 20, 'bold'))
        
        main_container = tk.Frame(self, bg=bg_dark_soft)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # ========== HEADER ==========
        header_frame = tk.Frame(main_container, bg=bg_dark_soft)
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="👁 DROWSINESS DETECTION SYSTEM", 
                  style='Title.TLabel').pack(side=tk.LEFT)
        
        # Mode Switch Button
        self.mode_btn = tk.Button(header_frame, text="👤 USER MODE", 
                                  command=self.toggle_mode,
                                  bg=highlight_soft, fg='black', font=('Segoe UI', 10, 'bold'),
                                  relief='flat', padx=20, pady=8, cursor='hand2')
        self.mode_btn.pack(side=tk.RIGHT)
        
        # ========== TOP SECTION: STATUS & METRICS ==========
        top_section = tk.Frame(main_container, bg=bg_dark_soft)
        top_section.pack(fill='x', pady=(0, 15))
        
        # Status Display (Left)
        status_card = tk.Frame(top_section, bg=bg_card_soft, relief='flat', bd=0)
        status_card.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10))
        
        tk.Label(status_card, text="STATUS", bg=bg_card_soft, fg='#bbb', 
                 font=('Segoe UI', 9)).pack(pady=(15, 5))
        self.status_label = tk.Label(status_card, text="IDLE", 
                                     bg='#555', fg=text_light,
                                     font=('Segoe UI', 18, 'bold'), 
                                     pady=15)
        self.status_label.pack(fill='x', padx=15, pady=(0, 15))
        
        # Metrics (Right)
        metrics_card = tk.Frame(top_section, bg=bg_card_soft, relief='flat', bd=0)
        metrics_card.pack(side=tk.RIGHT, fill='both', expand=True, padx=(10, 0))
        
        # Timer
        timer_frame = tk.Frame(metrics_card, bg=bg_card_soft)
        timer_frame.pack(fill='x', pady=15, padx=15)
        tk.Label(timer_frame, text="⏱", bg=bg_card_soft, fg=highlight_soft, 
                 font=('Segoe UI', 16)).pack(side=tk.LEFT, padx=(0, 10))
        self.timer_label = tk.Label(timer_frame, text="00:00:00", 
                                     bg=bg_card_soft, fg=text_light,
                                     font=('Segoe UI', 20, 'bold'))
        self.timer_label.pack(side=tk.LEFT)
        
        # Counter
        counter_frame = tk.Frame(metrics_card, bg=bg_card_soft)
        counter_frame.pack(fill='x', pady=(0, 15), padx=15)
        tk.Label(counter_frame, text="💤", bg=bg_card_soft, fg=highlight_soft,
                 font=('Segoe UI', 16)).pack(side=tk.LEFT, padx=(0, 10))
        self.counter_label = tk.Label(counter_frame, text="0 deteksi",
                                     bg=bg_card_soft, fg=highlight_soft,
                                     font=('Segoe UI', 16, 'bold'))
        self.counter_label.pack(side=tk.LEFT)
        
        # ========== SETTINGS PANEL (COLLAPSIBLE) ==========
        self.settings_panel = tk.Frame(main_container, bg=bg_card_soft, relief='flat')
        self.settings_panel.pack(fill='x', pady=(0, 15))
        
        # Settings Header
        settings_header = tk.Frame(self.settings_panel, bg=accent_soft, cursor='hand2')
        settings_header.pack(fill='x')
        settings_header.bind('<Button-1>', lambda e: self.toggle_settings())
        
        tk.Label(settings_header, text="⚙ PENGATURAN DETEKSI", 
                 bg=accent_soft, fg='white', font=('Segoe UI', 11, 'bold'),
                 anchor='w').pack(side=tk.LEFT, padx=15, pady=10)
        
        self.settings_arrow = tk.Label(settings_header, text="▼", 
                                     bg=accent_soft, fg='white', font=('Segoe UI', 10))
        self.settings_arrow.pack(side=tk.RIGHT, padx=15)
        
        # Settings Content
        self.settings_content = tk.Frame(self.settings_panel, bg=bg_card_soft)
        self.settings_content.pack(fill='x', padx=20, pady=15)
        
        self.locked_inputs = []
        
        # Grid Settings
        settings_grid = tk.Frame(self.settings_content, bg=bg_card_soft)
        settings_grid.pack(fill='x')
        
        def create_setting(parent, row, col, label, var, values=None):
            frame = tk.Frame(parent, bg=bg_card_soft)
            frame.grid(row=row, column=col, padx=10, pady=8, sticky='ew')
            
            tk.Label(frame, text=label, bg=bg_card_soft, fg='#aaa',
                     font=('Segoe UI', 9)).pack(anchor='w')
            
            if values:
                widget = ttk.Combobox(frame, textvariable=var, values=values,
                                     width=18, state='readonly')
            else:
                widget = ttk.Entry(frame, textvariable=var, width=20)
            
            widget.pack(fill='x', pady=(3, 0))
            self.locked_inputs.append(widget)
            return widget
        
        # Configure grid columns
        settings_grid.columnconfigure(0, weight=1)
        settings_grid.columnconfigure(1, weight=1)
        
        create_setting(settings_grid, 0, 0, "📹 Resolusi Kamera", 
                       self.res_var, list(RESOLUSI.keys()))
        create_setting(settings_grid, 0, 1, "👁 EAR Threshold", 
                       self.ear_threshold)
        create_setting(settings_grid, 1, 0, "⏲ Min Pejam (detik)", 
                       self.sleep_time_set)
        create_setting(settings_grid, 1, 1, "🔄 Reset Timeout (detik)", 
                       self.reset_timeout)
        
        # Alarm File Selection
        alarm_frame = tk.Frame(self.settings_content, bg=bg_card_soft)
        alarm_frame.pack(fill='x', pady=(15, 0))
        
        tk.Label(alarm_frame, text="🔊 File Alarm (MP3)", bg=bg_card_soft, 
                 fg='#aaa', font=('Segoe UI', 9)).pack(anchor='w')
        
        alarm_input_frame = tk.Frame(alarm_frame, bg=bg_card_soft)
        alarm_input_frame.pack(fill='x', pady=(3, 0))
        
        self.alarm_entry = ttk.Entry(alarm_input_frame, textvariable=self.alarm_path)
        self.alarm_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=(0, 10))
        self.locked_inputs.append(self.alarm_entry)
        
        self.alarm_btn = tk.Button(alarm_input_frame, text="📂 Pilih", 
                                   command=self.select_alarm_file,
                                   bg=accent_soft, fg='white', relief='flat',
                                   padx=15, pady=5, cursor='hand2')
        self.alarm_btn.pack(side=tk.RIGHT)
        self.locked_inputs.append(self.alarm_btn)
        
        # ========== CONTROL BUTTONS ==========
        control_frame = tk.Frame(main_container, bg=bg_dark_soft)
        control_frame.pack(fill='x', pady=(0, 15))
        
        btn_style = {'font': ('Segoe UI', 11, 'bold'), 'relief': 'flat',
                     'cursor': 'hand2', 'padx': 30, 'pady': 12}
        
        self.start_btn = tk.Button(control_frame, text="▶ MULAI DETEKSI",
                                   command=self.start_detection,
                                   bg='#27ae60', fg='white', **btn_style)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 5))
        
        self.stop_btn = tk.Button(control_frame, text="⏹ STOP",
                                  command=self.stop_detection,
                                  bg='#e74c3c', fg='white', **btn_style)
        self.stop_btn.pack(side=tk.LEFT, expand=True, fill='x', padx=5)
        
        self.reset_btn = tk.Button(control_frame, text="🔄 RESET",
                                   command=self.reset_counter,
                                   bg='#f1c40f', fg='black', **btn_style)
        self.reset_btn.pack(side=tk.LEFT, expand=True, fill='x', padx=(5, 0))
        
        # ========== LOG SECTION ==========
        self.log_frame = tk.Frame(main_container, bg=bg_card_soft, relief='flat')
        self.log_frame.pack(fill='both', expand=True)
        
        log_header = tk.Frame(self.log_frame, bg=accent_soft)
        log_header.pack(fill='x')
        tk.Label(log_header, text="📋 SYSTEM LOG", bg=accent_soft, fg='white',
                 font=('Segoe UI', 10, 'bold'), anchor='w').pack(side=tk.LEFT, 
                                                                 padx=15, pady=8)
        
        self.log_box = tk.Text(self.log_frame, height=6, bg='#1c2833', fg='#76d7c4',
                              font=('Consolas', 9), relief='flat', padx=10, pady=10)
        self.log_box.pack(fill='both', expand=True, padx=2, pady=(0, 2))
        
        # Initial log
        if self.log_available:
            self.log(f"Sistem siap. Alarm: {self.alarm_path.get()}")
        else:
            self.log("ERROR: Pygame mixer gagal diinisialisasi")
        
        self.compact_hide_widgets = [self.settings_panel, control_frame, self.log_frame]

    # ==========================
    # TOGGLE FUNCTIONS
    # ==========================
    def toggle_mode(self):
        current = self.mode.get()
        if current == "User":
            self.mode.set("Engineer")
            self.mode_btn.config(text="🔧 ENGINEER MODE", bg='#3498db')
        else:
            self.mode.set("User")
            self.mode_btn.config(text="👤 USER MODE", bg='#1abc9c')

    def toggle_settings(self):
        if self.settings_content.winfo_viewable():
            self.settings_content.pack_forget()
            self.settings_arrow.config(text="▶")
        else:
            self.settings_content.pack(fill='x', padx=20, pady=15)
            self.settings_arrow.config(text="▼")

    # ==========================
    # INPUT LOCK/UNLOCK
    # ==========================
    def update_input_states(self, *args):
        # Metode ini harus didefinisikan sebelum dipanggil di __init__
        current_mode = self.mode.get()
        state = tk.NORMAL if current_mode == "Engineer" else tk.DISABLED
        
        for widget in self.locked_inputs:
            if isinstance(widget, ttk.Combobox):
                widget.config(state='readonly' if current_mode == "Engineer" else 'disabled')
            elif isinstance(widget, tk.Button):
                widget.config(state=state)
            else:
                widget.config(state=state)
        
        if current_mode == "User":
            self.log("Mode User: Pengaturan dikunci")
        else:
            self.log("Mode Engineer: Pengaturan dapat diubah")

    # (Fungsi selebihnya log, update_timer, counter, alarm, pop-up, dan deteksi loop tetap sama)
    
    # ... (Sisa fungsi lainnya: select_alarm_file, log, update_timer, reset_counter, update_counter, check_face_timeout, start_alarm, stop_alarm, start_detection, stop_detection, show_popup, close_popup, detect_loop) ...
    # Agar kode tidak terlalu panjang, saya asumsikan sisa fungsinya sama seperti yang terakhir Anda berikan
    
    def select_alarm_file(self):
        if not self.running:
            filepath = filedialog.askopenfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
                title="Pilih File Alarm (MP3)"
            )
            if filepath:
                self.alarm_path.set(filepath)
                self.log(f"Alarm diubah: {filepath}")
        else:
            messagebox.showwarning("Deteksi Berjalan", 
                                 "Tidak dapat mengubah alarm saat deteksi aktif")

    def log(self, msg):
        timestamp = time.strftime('%H:%M:%S')
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")

    def update_timer(self):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            s = elapsed % 60
            self.timer_label.config(text=f"{h:02}:{m:02}:{s:02}")
        self.after(1000, self.update_timer)

    def reset_counter(self):
        self.drowsy_count = 0
        self.counter_label.config(text="0 deteksi")
        self.log("Counter direset")

    def update_counter(self):
        self.drowsy_count += 1
        self.counter_label.config(text=f"{self.drowsy_count} deteksi")
        self.log(f"Microsleep terdeteksi! Total: {self.drowsy_count}")

    def check_face_timeout(self):
        if self.face_detected:
            self.last_face_detected_time = time.time()
            self.face_detected = False
        else:
            time_since_last_face = time.time() - self.last_face_detected_time
            if time_since_last_face > self.reset_timeout.get() and self.drowsy_count > 0:
                self.log(f"Counter direset (timeout {self.reset_timeout.get()}s)")
                self.reset_counter()

    def start_alarm(self):
        if not self.log_available:
            return
        
        if not self.is_alarming:
            self.is_alarming = True
            try:
                pygame.mixer.music.load(self.alarm_path.get())
                pygame.mixer.music.play(-1)
                self.log("Alarm dimulai")
            except pygame.error as e:
                self.log(f"ERROR: Gagal memutar alarm - {e}")
                self.is_alarming = False
            except Exception as e:
                 self.log(f"ERROR: Gagal memuat/memutar alarm - {e}")
                 self.is_alarming = False

    def stop_alarm(self):
        if self.is_alarming:
            pygame.mixer.music.stop()
            self.is_alarming = False
            self.log("Alarm dihentikan")

    def start_detection(self):
        try:
            ear = self.ear_threshold.get()
            sleep = self.sleep_time_set.get()
            reset = self.reset_timeout.get()
            if not (0.05 < ear < 0.5) or sleep <= 0 or reset <= 0:
                 messagebox.showerror("Parameter Error", "Pastikan nilai EAR Threshold (0.05-0.5), Min Pejam, dan Reset Timeout valid.")
                 return
        except tk.TclError:
            messagebox.showerror("Input Error", "Pastikan semua input parameter berupa angka.")
            return

        if self.log_available and not self.alarm_path.get():
             messagebox.showwarning("Alarm Not Set", "File alarm belum dipilih.")
        
        if not self.running:
            self.start_time = time.time()
            self.running = True
            threading.Thread(target=self.detect_loop, daemon=True).start()
            self.start_btn.config(state=tk.DISABLED)
            self.log("Deteksi dimulai")

    def stop_detection(self):
        self.running = False
        self.stop_alarm()
        cv2.destroyAllWindows()
        self.status_label.config(text="STOPPED", bg='#555')
        self.start_btn.config(state=tk.NORMAL)
        self.log("Deteksi dihentikan")

    def show_popup(self):
        if self.popup is not None:
            return

        self.popup = tk.Toplevel(self)
        self.popup.title("⚠ PERINGATAN")
        self.popup.geometry("600x280")
        self.popup.configure(bg="#c0392b")
        self.popup.attributes('-topmost', True) 

        tk.Label(self.popup, text="🚨 MICROSLEEP TERDETEKSI 🚨",
                 font=("Segoe UI", 26, "bold"), fg="white", bg="#c0392b").pack(pady=(30, 10))

        tk.Label(self.popup, text=f"Total Deteksi: {self.drowsy_count} kali",
                 font=("Segoe UI", 16), fg="white", bg="#c0392b").pack(pady=10)

        tk.Label(self.popup, text="Segera beristirahat dan minum air putih!",
                 font=("Segoe UI", 14), fg="white", bg="#c0392b").pack(pady=20)

        self.popup.protocol("WM_DELETE_WINDOW", lambda: None) 

    def close_popup(self):
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None
            self.stop_alarm()

    def detect_loop(self):
        width, height = RESOLUSI[self.res_var.get()]
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise IOError("Tidak dapat membuka kamera. Pastikan tidak sedang digunakan oleh aplikasi lain.")
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        except Exception as e:
            self.log(f"ERROR: Gagal membuka kamera - {e}")
            self.running = False
            self.start_btn.config(state=tk.NORMAL)
            self.after(0, lambda: messagebox.showerror("Camera Error", f"Gagal inisialisasi kamera: {e}"))
            return

        closed_time = 0.0
        last_frame_time = time.time()
        
        frame_count = 0
        fps_start_time = time.time()
        current_fps = 0.0
        
        self.face_detected = False
        ear_threshold_val = self.ear_threshold.get()
        sleep_time_val = self.sleep_time_set.get()

        while self.running:
            now = time.time()
            dt = now - last_frame_time
            last_frame_time = now
            
            frame_count += 1
            if now - fps_start_time >= 1:
                current_fps = frame_count / (now - fps_start_time)
                fps_start_time = now
                frame_count = 0

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            results = self.face_mesh.process(rgb)

            ear = 1.0
            face_found = False

            if results.multi_face_landmarks:
                face_found = True
                self.face_detected = True
                lm = results.multi_face_landmarks[0].landmark

                left_idx = [33, 160, 158, 133, 153, 144]
                right_idx = [263, 387, 385, 362, 380, 373]

                h, w, _ = frame.shape
                left_eye_norm = np.array([(lm[i].x * w, lm[i].y * h) for i in left_idx])
                right_eye_norm = np.array([(lm[i].x * w, lm[i].y * h) for i in right_idx])
                
                try:
                    ear = (calculate_EAR(left_eye_norm) + calculate_EAR(right_eye_norm)) / 2.0
                    
                    if self.smoothed_ear == 0.0:
                        self.smoothed_ear = ear
                    else:
                        self.smoothed_ear = EMA_ALPHA * ear + (1 - EMA_ALPHA) * self.smoothed_ear
                    ear = self.smoothed_ear
                    
                except:
                    face_found = False

            self.after(0, self.check_face_timeout)

            if face_found:
                if ear < ear_threshold_val:
                    closed_time += dt
                else:
                    closed_time = 0.0

                sleepy = closed_time >= sleep_time_val

                if sleepy:
                    self.after(0, lambda: self.status_label.config(text="⚠ MICROSLEEP!", bg='#e74c3c'))
                    self.after(0, self.start_alarm)

                    if not self.was_sleepy:
                        self.after(0, self.update_counter)
                        self.was_sleepy = True
                        if self.mode.get() == "User":
                            self.after(0, self.show_popup)

                else:
                    self.after(0, lambda: self.status_label.config(text="✓ NORMAL", bg='#27ae60'))
                    self.was_sleepy = False
                    
                    if self.is_alarming:
                        self.after(0, self.stop_alarm)

                    if self.popup is not None and self.popup_close_time is None and not self.was_sleepy:
                        self.popup_close_time = time.time() + 3.0

                if self.popup is not None and self.popup_close_time is not None:
                    if time.time() >= self.popup_close_time:
                        self.after(0, self.close_popup)
                        self.popup_close_time = None

            else:
                closed_time = 0.0
                self.after(0, lambda: self.status_label.config(text="⚠ NO FACE", bg='#f39c12'))
                self.was_sleepy = False
                self.after(0, self.stop_alarm)
                self.after(0, self.close_popup)

            if self.mode.get() == "Engineer":
                if face_found and results.multi_face_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, results.multi_face_landmarks[0],
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        self.drawing_spec, self.drawing_spec)
                    
                    for point in left_eye_norm.astype(int):
                        cv2.circle(frame, tuple(point), 2, (0, 0, 255), -1)
                    for point in right_eye_norm.astype(int):
                        cv2.circle(frame, tuple(point), 2, (0, 0, 255), -1)

                    ear_color = (0, 255, 0) if ear >= ear_threshold_val else (0, 0, 255)
                    
                    cv2.putText(frame, f"EAR: {ear:.3f} | Time: {closed_time:.2f}s",
                                 (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ear_color, 2)
                    
                    cv2.putText(frame, f"FPS: {current_fps:.1f}",
                                 (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                    
                    cv2.putText(frame, f"Count: {self.drowsy_count}",
                                 (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    cv2.imshow("Engineer Monitor", frame)
                else:
                    cv2.putText(frame, "NO FACE DETECTED", (50, height // 2), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    cv2.imshow("Engineer Monitor", frame)
            else:
                try:
                    cv2.destroyWindow("Engineer Monitor")
                except:
                    pass

            if cv2.waitKey(1) == 27:
                break

            time.sleep(0.005)

        cap.release()
        cv2.destroyAllWindows()
        self.after(0, self.stop_detection)

if __name__ == "__main__":
    mixer_status = False
    try:
        pygame.mixer.init()
        mixer_status = True
    except pygame.error as e:
        temp_root = tk.Tk()
        temp_root.withdraw()
        tk.messagebox.showerror("Pygame Error", 
                                 f"Gagal inisialisasi Pygame: {e}\nAlarm dinonaktifkan.")
        temp_root.destroy()
    
    app = FaceApp(mixer_initialized=mixer_status)
    app.mainloop()
