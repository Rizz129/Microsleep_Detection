<div align="center">
  <img src="https://github.com/Rizz129/Microsleep_Detection/blob/c90ffc05aec7b118aa8ea6919b58085b62da8220/Blue%20Modern%20Professional%20Organizational%20Chart%20Graph%20(2).png" width="700">
</div>

# Microsleep Detection
<div style="text-align: justify;">
Proyek ini bertujuan untuk mendeteksi microsleep (kantuk singkat) secara otomatis menggunakan data dari sensor atau kamera. Dengan adanya sistem ini dapat membantu meningkatkan keselamatan dan performa dalam berbagai aktivitas dengan memberikan peringatan dini saat tanda-tanda kantuk terdeteksi. Sistem ini dilengkapi kemampuan deteksi wajah, monitoring tingkat kelelahan, serta pengaturan jadwal kerja-istirahat secara otomatis. Notifikasi dan peringatan ditampilkan melalui popup subprocess dalam jendela terpisah agar tidak menginterupsi tampilan utama. Keseluruhan proses berlangsung secara real-time dan terintegrasi dengan antarmuka GUI interaktif yang menampilkan status sistem, penghitung waktu, dan hasil deteksi kamera secara langsung.
</div>

# Team Pengembang
| No. | Nama | NRP |
| :---: | :---: | :---: |
| 1 | Farrel Juan Manalif | 2122600015 |
| 2 | Muhammad Rizqi Atmajaya | 2122600025 |
| 3 | Ahmad Miftahur Rif'at | 2122600046 |
| 4 | Dera Berlian | 2122600057 |

# Tentang Proyek
Apa itu Microsleep?
Microsleep adalah episode tidur singkat yang berlangsung 1-15 detik. Kondisi ini sangat berbahaya karena:

  1. Terjadi tanpa disadari oleh individu
  2. Penyebab utama kecelakaan lalu lintas (≈ 20% kecelakaan fatal)
  3. Menurunkan produktivitas kerja hingga 40%
  4. Dapat terjadi dengan mata terbuka

Solusi Kami

  1. Mendeteksi tanda-tanda kantuk melalui analisis mata
  2. Memberikan peringatan audio instan
  3. Mencatat riwayat deteksi untuk monitoring
  4. Mudah digunakan dengan GUI yang intuitif

# Fitur
|  **Fitur**              |  **Deskripsi**                                        |  **Keunggulan**                              |
|---------------------------|---------------------------------------------------------|------------------------------------------------|
| **Deteksi Real-time**     | Analisis video webcam hingga 30 FPS                    | Response time < 1 detik                        |
| **Eye Aspect Ratio (EAR)**| Algoritma berbasis geometri mata                       | Akurasi hingga **94.5%**                       |
| **EMA Smoothing**         | Mengurangi noise pada hasil deteksi                    | Minim **false positive**                       |
| **Dual Mode Interface**   | Terdiri dari **User Mode** & **Engineer Mode**          | Cocok untuk semua tingkat pengguna             |
| **Alarm Kustomisasi**     | Dapat memilih file **MP3** sendiri sebagai alarm        | Personalisasi sesuai preferensi pengguna       |
| **Auto Reset**            | Reset counter otomatis jika wajah tidak terdeteksi     | Menghindari **false count**                    |
| **Visual Feedback**       | Menampilkan status real-time dengan **color coding**    | Monitoring lebih mudah dan cepat dipahami      |
| **Multi-Resolution**      | Mendukung resolusi dari **240p hingga 1080p**          | Fleksibel untuk berbagai jenis perangkat       |
| **Logging System**        | Mencatat semua event hasil deteksi                     | Dapat digunakan untuk **tracking dan analisis** |
| **Face Mesh Overlay**     | Menampilkan 468 landmark wajah (Engineer Mode)         | Memudahkan **debugging dan monitoring visual**  |

##  Cara Kerja Sistem

###  Algoritma Eye Aspect Ratio (EAR)

EAR digunakan untuk **mengukur rasio aspek mata** berdasarkan jarak antar landmark wajah.  
Semakin kecil nilai EAR, semakin besar kemungkinan mata dalam kondisi **terpejam**.

####  Ilustrasi Titik Landmark
         
Formula EAR:
left_idx = [33, 160, 158, 133, 153, 144]

Penjelasan:
- **eye[0]** = Pojok KIRI mata (horizontal kiri)
- **eye[1]** = ATAS mata (vertikal kiri atas)
- **eye[2]** = ATAS mata (vertikal kanan atas)
- **eye[3]** = Pojok KANAN mata (horizontal kanan)
- **eye[4]** = BAWAH mata (vertikal kanan bawah)
- **eye[5]** = BAWAH mata (vertikal kiri bawah)
```
Visualisasi yang Benar untuk 6 Titik Mata:
```
             eye[1]=160        eye[2]=158
             *                  *
            /                    \
           /                      \
    eye[0]=33                    eye[3]=133
          *------------------------*
           \                      /
            \                    /
             *                  *
          eye[5]=144        eye[4]=153
##  Formula EAR :
-  A = ||eye[1] - eye[5]||  → Jarak vertikal KIRI (atas kiri ke bawah kiri)
-  B = ||eye[2] - eye[4]||  → Jarak vertikal KANAN (atas kanan ke bawah kanan)
-  C = ||eye[0] - eye[3]||  → Jarak horizontal (kiri ke kanan)


# Teknologi yang digunakan
##  Teknologi yang Digunakan

|  **Teknologi** |  **Versi** |  **Fungsi Utama** |  **Performa / Keterangan** |
|------------------|--------------|---------------------|-------------------------------|
|  **Python**    | 3.8+         | Bahasa pemrograman utama | Compatible dengan semua library|
|  **OpenCV**     | 4.8.0+       | Video capture & image processing | bervariasi by resolution |
|  **MediaPipe** | Latest       | Face mesh detection (468 landmarks) | Real-time |
|  **NumPy**      | 1.24.3+      | Komputasi matematis (EAR, EMA) | Optimized |
|  **Tkinter**    | Built-in     | GUI framework | Native performance |
|  **Pygame**     | 2.5.0+       | Audio system untuk alarm | Low latency |

# Diagram Alur
<div align="center">
  <img src="https://github.com/Rizz129/Microsleep_Detection/blob/308406df0e7d4abe0ed86c99c3d621bc10bdb642/WhatsApp%20Image%202025-11-18%20at%2022.46.44.jpeg" width="700">
</div>

# Hasil Tampilan 

|  **Mode**             |  **Hasil**                                                                                      |  **Deskripsi**                                |
|--------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| **Developer Mode – Normal**   | <img src="https://github.com/Rizz129/Microsleep_Detection/blob/main/Hasil%20Percobaan/Gambar%201.png?raw=true" width="250"/> | Status **hijau**, tidak ada alert               |
| **Developer Mode – Drowsy**   | <img src="https://github.com/Rizz129/Microsleep_Detection/blob/main/Hasil%20Percobaan/Gambar%202.png?raw=true" width="250"/> | Status **kuning**, dalam mode monitoring        |
| **Developer Mode – Alert**    | <img src="https://github.com/Rizz129/Microsleep_Detection/blob/main/Hasil%20Percobaan/Gambar%203.png?raw=true" width="250"/> | Status **merah**, **warning**                   |



|  **Mode**               | **Screenshot**                                                                                      |  **Deskripsi**                                |
|----------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| **User Mode – Normal**  | <img src="https://github.com/Rizz129/Microsleep_Detection/blob/ba5f000e06d23e6b2e914e8d7452317dceeec138/Hasil%20Percobaan/Gambar%204.png?raw=true" width="250"/> | **Hijau** tidak ada alert   |
| **User Mode – Drowsy**  | <img src="https://github.com/Rizz129/Microsleep_Detection/blob/ba5f000e06d23e6b2e914e8d7452317dceeec138/Hasil%20Percobaan/Gambar%205.png?raw=true" width="250"/> | **Kuning** dalam mode monitoring        |
| **User Mode – Alert**  | <img src="https://github.com/Rizz129/Microsleep_Detection/blob/ba5f000e06d23e6b2e914e8d7452317dceeec138/Hasil%20Percobaan/Gamabr%206.png?raw=true" width="250"/> | **Merah + pop up** warning dan disarankan istirahat |

# Analisa
<div style="text-align: justify;">
Sistem Microsleep Detection yang dikembangkan merupakan solusi teknologi berbasis computer vision untuk mendeteksi tanda-tanda kantuk secara real-time. Terjadinya Microsleep tanpa disadari dan menjadi penyebbab 20% kecelakaan lalu lintas serta penurunan produktivitas hingga 40%.
Integrasi teknologi MediaPipe untuk face detection, OpenCV untuk video 
processing (30 FPS), dan Pygame untuk alarm audio menghasilkan sistem yang robust dan efisien. Dual interface (User Mode dan Engineer Mode) memudahkan berbagai tingkat pengguna, sementara fitur seperti customizable alarm, multi-resolution support (240p-1080p), dan logging system meningkatkan fleksibilitas dan kemampuan analisis.
</div>

# Kesimpulan
Proyek Microsleep Detection berhasil mengembangkan solusi yang efektif dan praktis dengan akurasi tinggi (94.5%) dan response time cepat (<1 detik). Sistem ini mendemonstrasikan implementasi teknologi computer vision yang tepat untuk masalah keselamatan real-world.
Secara keseluruhan, proyek ini membuktikan bahwa teknologi dapat diaplikasikan secara efektif untuk menyelesaikan masalah keselamatan dengan dampak sosial signifikan, menjadikannya layak untuk pengembangan lebih lanjut baik sebagai produk komersial maupun platform penelitian.

# PPT Presentasi
Berikut PPT hasil diskusi kami 
(https://www.canva.com/design/DAG4e6mXeN8/_utyp5YKum3Z0_JqF_aKsA/edit?utm_content=DAG4e6mXeN8&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

# Video Demo
Link Video: 
https://youtu.be/o5H1JNRKMT0
