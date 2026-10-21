GAME PRINTER + PENGHUBUNG TIKTOK LIVE

PENTING:
- Koneksi event TikTok LIVE menggunakan pustaka pihak ketiga TikTokLive (tidak resmi), bukan API resmi TikTok.
- Koneksi hanya bisa aktif saat akun sedang LIVE dan TikTok mengizinkan koneksi. Kompatibilitas dapat berubah.
- Jangan masukkan password atau cookie TikTok ke program ini. Username publik saja.
- Program ini hanya membaca event LIVE; tidak mengirim komentar/like/gift dan tidak mengontrol mesin printer fisik.

CARA MENJALANKAN DI WINDOWS:
1. Ekstrak ZIP ke folder.
2. Pastikan Python 3.10+ terpasang dan pilihan "Add Python to PATH" dicentang.
3. Klik dua kali start_windows.bat dan tunggu sampai muncul Uvicorn running.
4. Buka Chrome dan masuk ke http://127.0.0.1:8000
5. Masukkan username TikTok yang sedang LIVE tanpa @, lalu klik Hubungkan.
6. Komentar memicu mesin jika opsi komentar dicentang. Like memicu cetak setiap jumlah ambang yang ditentukan. Gift memicu cetak otomatis.

CARA MENJALANKAN DI MAC/LINUX:
Jalankan ./start.sh lalu buka http://127.0.0.1:8000

TES:
Tombol Tes komentar / Tes like / Tes gift hanya mensimulasikan event di browser. Itu bukan bukti koneksi TikTok aktif.

TENTANG ANDROID:
File HTML yang dibuka langsung dari folder HP tidak dapat menjalankan bridge Python ini. Untuk event TikTok sungguhan, jalankan server di komputer atau hosting/server yang selalu aktif, lalu akses frontend dari perangkat yang bisa menjangkau server tersebut. Untuk penggunaan produksi, pertimbangkan penyedia WebSocket/API LIVE yang resmi/andal dan patuhi ketentuan TikTok.
