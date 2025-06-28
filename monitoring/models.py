from django.db import models
from django.contrib.auth.models import AbstractUser

class Kemantren(models.Model):
    nama = models.CharField(max_length=100)

    def __str__(self):
        return self.nama

class Bendung(models.Model):
    nama_sta = models.CharField(max_length=100)
    nomor_sta = models.CharField(max_length=50)
    sungai = models.CharField(max_length=100)
    ca = models.CharField(max_length=50)
    desa = models.CharField(max_length=100)
    kecamatan = models.CharField(max_length=100)
    kabupaten = models.CharField(max_length=100)
    provinsi = models.CharField(max_length=100)
    koordinat_ls = models.CharField(max_length=100, null=True, blank=True)  # Koordinat Lintang Selatan
    koordinat_bt = models.CharField(max_length=100, null=True, blank=True)  # Koordinat Bujur Timur
    kemantren = models.ForeignKey(Kemantren, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama_sta

class Role(models.Model):
    nama_role = models.CharField(max_length=100)
    tempat = models.ForeignKey(Bendung, on_delete=models.CASCADE)

    def __str__(self):
        return self.nama_role

class CustomUser(AbstractUser):
    nama = models.CharField(max_length=100)
    jenis_kelamin = models.CharField(max_length=10, choices=[('Laki-laki', 'Laki-laki'), ('Perempuan', 'Perempuan')])
    jabatan = models.CharField(max_length=100, choices=[
        ('Petugas Operasional Bendung', 'Petugas Operasional Bendung'),
        ('Juru Operasional dan Pemeliharaan', 'Juru Operasional dan Pemeliharaan')
    ])
    unit_kerja = models.ForeignKey('Kemantren', on_delete=models.CASCADE, null=True, blank=True)
    no_hp = models.CharField(max_length=15)
    role = models.ForeignKey('Role', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nama

class DebitAir(models.Model):
    tanggal = models.DateField()
    
    # Muka Air Limpas dan Debit Bendung
    h_07 = models.FloatField(default=0.0)
    q_07 = models.FloatField(default=0.0)
    h_12 = models.FloatField(default=0.0)
    q_12 = models.FloatField(default=0.0)
    h_17 = models.FloatField(default=0.0)
    q_17 = models.FloatField(default=0.0)

    # Debit Pintu Intik Bendung - Jam 07.00
    h_kiri_07 = models.FloatField(default=0.0)
    q_kiri_07 = models.FloatField(default=0.0)
    h_kanan_07 = models.FloatField(default=0.0)
    q_kanan_07 = models.FloatField(default=0.0)

    # Debit Pintu Intik Bendung - Jam 12.00
    h_kiri_12 = models.FloatField(default=0.0)
    q_kiri_12 = models.FloatField(default=0.0)
    h_kanan_12 = models.FloatField(default=0.0)
    q_kanan_12 = models.FloatField(default=0.0)

    # Debit Pintu Intik Bendung - Jam 17.00
    h_kiri_17 = models.FloatField(default=0.0)
    q_kiri_17 = models.FloatField(default=0.0)
    h_kanan_17 = models.FloatField(default=0.0)
    q_kanan_17 = models.FloatField(default=0.0)

    bendungan = models.ForeignKey(Bendung, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tanggal} - {self.bendungan.nama_sta}"

    # Property untuk rata-rata H dan Q dari limpasan
    @property
    def h_avg(self):
        return round((self.h_07 + self.h_12 + self.h_17) / 3, 3)

    @property
    def q_avg(self):
        return round((self.q_07 + self.q_12 + self.q_17) / 3, 3)

    @property
    def debit_total(self):
        q_kiri_avg = (self.q_kiri_07 + self.q_kiri_12 + self.q_kiri_17) / 3
        q_kanan_avg = (self.q_kanan_07 + self.q_kanan_12 + self.q_kanan_17) / 3
        return round(self.q_avg + q_kiri_avg + q_kanan_avg, 3)
