from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model
from .models import Bendung, Kemantren, Role, DebitAir
User = get_user_model()
from datetime import timedelta
from django.template.loader import get_template
import json
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import Bendung
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import date
import math
import pdfkit

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login_view(request):
    msg = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            msg = "Username atau Password salah"
    return render(request, 'index.html', {'msg': msg})

@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    this_month = today.month
    this_year = today.year
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month = last_month_date.month
    last_month_year = last_month_date.year

    tahun = request.GET.get('tahun', str(this_year))
    id_bendung = request.GET.get('bendung') if user.is_superuser else None
    debit_saat_ini = 0
    h_avg_saat_ini = 0
    perubahan_persen = 0
    data_grafik = []

    # Dropdown tahun dari 2020 hingga 2 tahun ke depan
    tahun_list = list(range(2020, this_year + 3))

    if user.is_superuser:
        # Data kartu: debit hari ini
        debit_hari_ini = DebitAir.objects.filter(tanggal=today)
        total_h_avg = sum(d.h_avg for d in debit_hari_ini)
        h_avg_saat_ini = round(total_h_avg / len(debit_hari_ini), 3) if debit_hari_ini else 0
        total = sum(d.debit_total for d in debit_hari_ini)
        debit_saat_ini = round(total / len(debit_hari_ini), 3) if debit_hari_ini else 0

        # Bulan ini & bulan lalu
        debit_bulan_ini = DebitAir.objects.filter(tanggal__month=this_month, tanggal__year=this_year)
        debit_bulan_lalu = DebitAir.objects.filter(tanggal__month=last_month, tanggal__year=last_month_year)

        rata_bulan_ini = sum(d.debit_total for d in debit_bulan_ini) / len(debit_bulan_ini) if debit_bulan_ini else 0
        rata_bulan_lalu = sum(d.debit_total for d in debit_bulan_lalu) / len(debit_bulan_lalu) if debit_bulan_lalu else 0

        # Data grafik berdasarkan filter tahun dan bendung
        for bulan in range(1, 13):
            queryset = DebitAir.objects.filter(tanggal__year=tahun, tanggal__month=bulan)
            if id_bendung:
                queryset = queryset.filter(bendungan_id=id_bendung)
            rata = sum(d.debit_total for d in queryset) / len(queryset) if queryset else 0
            data_grafik.append(round(rata, 3))

        bendung_list = Bendung.objects.all()

    else:
        tempat = getattr(user.role, 'tempat', None)

        # Data kartu
        debit = DebitAir.objects.filter(tanggal=today, bendungan=tempat).first()
        h_avg_saat_ini = round(debit.h_avg, 3) if debit else 0
        if debit:
            debit_saat_ini = round(debit.debit_total, 2)

        debit_bulan_ini = DebitAir.objects.filter(
            bendungan=tempat, tanggal__month=this_month, tanggal__year=this_year
        )
        debit_bulan_lalu = DebitAir.objects.filter(
            bendungan=tempat, tanggal__month=last_month, tanggal__year=last_month_year
        )

        rata_bulan_ini = sum(d.debit_total for d in debit_bulan_ini) / len(debit_bulan_ini) if debit_bulan_ini else 0
        rata_bulan_lalu = sum(d.debit_total for d in debit_bulan_lalu) / len(debit_bulan_lalu) if debit_bulan_lalu else 0

        # Data grafik otomatis berdasarkan role user
        for bulan in range(1, 13):
            queryset = DebitAir.objects.filter(tanggal__year=tahun, tanggal__month=bulan, bendungan=tempat)
            rata = sum(d.debit_total for d in queryset) / len(queryset) if queryset else 0
            data_grafik.append(round(rata, 3))

        bendung_list = None  # tidak diperlukan

    # Hitung perubahan persen
    if rata_bulan_lalu != 0:
        perubahan_persen = round(((rata_bulan_ini - rata_bulan_lalu) / rata_bulan_lalu) * 100, 2)
    elif rata_bulan_ini > 0:
        perubahan_persen = 100.0
    else:
        perubahan_persen = 0.0

    return render(request, 'dashboard.html', {
        'debit_saat_ini': debit_saat_ini,
        'perubahan_persen': perubahan_persen,
        'data_grafik': data_grafik,
        'tahun': tahun,
        'id_bendung': id_bendung,
        'bendung_list': bendung_list,
        'tahun_list': tahun_list,
        'h_avg_saat_ini': h_avg_saat_ini,
    })

@login_required
def daftar_kemantren(request):
    kemantren_list = Kemantren.objects.all()
    return render(request, 'kemantren.html', {'kemantren_list': kemantren_list})

@login_required
def tambah_kemantren(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')

        Kemantren.objects.create(
            nama = nama,
        )

        return JsonResponse({'message': 'Data kemantren berhasil ditambahkan!'})
    return HttpResponseBadRequest('Invalid request')

@login_required
def edit_kemantren(request, id):
    kemantren = get_object_or_404(Kemantren, id=id)

    if request.method == 'POST':
        kemantren.nama = request.POST.get('nama')
        kemantren.save()
        return JsonResponse({'message': 'Data kemantren berhasil diperbarui!'})
    return HttpResponseBadRequest('Invalid request')

@login_required
@csrf_exempt
def hapus_kemantren(request, id):
    if request.method == 'DELETE':
        kemantren = get_object_or_404(Kemantren, id=id)
        kemantren.delete()
        return JsonResponse({'message': 'Data kemantren berhasil dihapus'})
    return HttpResponseBadRequest('Invalid request')

@login_required
def daftar_bendung(request):
    bendung_list = Bendung.objects.select_related('kemantren').all()
    kemantren_list = Kemantren.objects.all()
    return render(request, 'bendung.html', {
        'bendung_list': bendung_list,
        'kemantren_list': kemantren_list
    })

@login_required
def tambah_bendung(request):
    if request.method == 'POST':
        nama_sta = request.POST.get('nama_sta')
        nomor_sta = request.POST.get('nomor_sta')
        sungai = request.POST.get('sungai')
        ca = request.POST.get('ca')
        desa = request.POST.get('desa')
        kecamatan = request.POST.get('kecamatan')
        kabupaten = request.POST.get('kabupaten')
        provinsi = request.POST.get('provinsi')
        koordinat_ls = request.POST.get('koordinat_ls')
        koordinat_bt = request.POST.get('koordinat_bt')
        kemantren_id = request.POST.get('kemantren')

        kemantren = get_object_or_404(Kemantren, id=kemantren_id)

        Bendung.objects.create(
            nama_sta=nama_sta,
            nomor_sta=nomor_sta,
            sungai=sungai,
            ca=ca,
            desa=desa,
            kecamatan=kecamatan,
            kabupaten=kabupaten,
            provinsi=provinsi,
            koordinat_ls=koordinat_ls,
            koordinat_bt=koordinat_bt,
            kemantren=kemantren
        )

        return JsonResponse({'message': 'Data bendung berhasil ditambahkan!'})
    return HttpResponseBadRequest('Invalid request')

@login_required
def edit_bendung(request, id):
    bendung = get_object_or_404(Bendung, id=id)

    if request.method == 'POST':
        bendung.nama_sta = request.POST.get('nama_sta')
        bendung.nomor_sta = request.POST.get('nomor_sta')
        bendung.sungai = request.POST.get('sungai')
        bendung.ca = request.POST.get('ca')
        bendung.desa = request.POST.get('desa')
        bendung.kecamatan = request.POST.get('kecamatan')
        bendung.kabupaten = request.POST.get('kabupaten')
        bendung.provinsi = request.POST.get('provinsi')
        bendung.koordinat_ls = request.POST.get('koordinat_ls')
        bendung.koordinat_bt = request.POST.get('koordinat_bt')
        kemantren_id = request.POST.get('kemantren')
        bendung.kemantren = get_object_or_404(Kemantren, id=kemantren_id)
        bendung.save()
        return JsonResponse({'message': 'Data bendung berhasil diperbarui!'})
    return HttpResponseBadRequest('Invalid request')

@login_required
@csrf_exempt
def hapus_bendung(request, id):
    if request.method == 'DELETE':
        bendung = get_object_or_404(Bendung, id=id)
        bendung.delete()
        return JsonResponse({'message': 'Data bendung berhasil dihapus'})
    return HttpResponseBadRequest('Invalid request')

@login_required
def role_list(request):
    roles = Role.objects.select_related('tempat').all()
    bendung_list = Bendung.objects.all()
    return render(request, 'role.html', {
        'role_list': roles,
        'bendung_list': bendung_list
    })

@login_required
def tambah_role(request):
    if request.method == 'POST':
        nama_role = request.POST.get('nama_role')
        id_tempat = request.POST.get('tempat')
        tempat = get_object_or_404(Bendung, id=id_tempat)

        Role.objects.create(nama_role=nama_role, tempat=tempat)

        return JsonResponse({'message': 'Role berhasil ditambahkan'})
    return HttpResponseBadRequest('Invalid request')

@login_required
def edit_role(request, id):
    role = get_object_or_404(Role, id=id)
    if request.method == 'POST':
        role.nama_role = request.POST.get('nama_role')
        id_tempat = request.POST.get('tempat')
        role.tempat = get_object_or_404(Bendung, id=id_tempat)
        role.save()
        return JsonResponse({'message': 'Role berhasil diperbarui'})
    return HttpResponseBadRequest('Invalid request')

@login_required
@csrf_exempt
def hapus_role(request, id):
    if request.method == 'DELETE':
        role = get_object_or_404(Role, id=id)
        role.delete()
        return JsonResponse({'message': 'Role berhasil dihapus'})
    return HttpResponseBadRequest('Invalid request')

@login_required
@csrf_exempt
def tambah_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        jenis_kelamin = request.POST.get('jenis_kelamin')
        jabatan = request.POST.get('jabatan')
        unit_kerja_id = request.POST.get('unit_kerja')
        email = request.POST.get('email')
        no_hp = request.POST.get('no_hp')
        role_id = request.POST.get('role')

        # Cek apakah username sudah ada
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username sudah digunakan'}, status=400)

        try:
            User.objects.create(
                username=username,
                password=make_password(password),  # amankan password
                nama=nama,
                jenis_kelamin=jenis_kelamin,
                jabatan=jabatan,
                unit_kerja_id=unit_kerja_id,
                email=email,
                no_hp=no_hp,
                role_id=role_id
            )
            return JsonResponse({'message': 'User berhasil ditambahkan'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return HttpResponseBadRequest('Invalid request')

@login_required
def user_list_view(request):
    users = User.objects.filter(is_superuser=False)
    kemantren_list = Kemantren.objects.all()
    role_list = Role.objects.all()
    return render(request, 'user.html', {
        'user_list': users,
        'kemantren_list': kemantren_list,
        'role_list': role_list
    })

@login_required
@csrf_exempt
def edit_user(request, id):
    if request.method == 'POST':
        try:
            user = User.objects.get(id=id)
            username = request.POST.get('username')
            
            # Cek jika username berubah dan sudah dipakai user lain
            if user.username != username and User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username sudah digunakan'}, status=400)

            user.username = username
            if request.POST.get('password'):
                user.password = make_password(request.POST.get('password'))
            user.nama = request.POST.get('nama')
            user.jenis_kelamin = request.POST.get('jenis_kelamin')
            user.jabatan = request.POST.get('jabatan')
            user.unit_kerja_id = request.POST.get('unit_kerja')
            user.email = request.POST.get('email')
            user.no_hp = request.POST.get('no_hp')
            user.role_id = request.POST.get('role')
            user.save()

            return JsonResponse({'message': 'User berhasil diperbarui'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return HttpResponseBadRequest('Invalid request')

@login_required
@csrf_exempt
def hapus_user(request, id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(id=id)
            user.delete()
            return JsonResponse({'message': 'User berhasil dihapus'})
        except:
            return JsonResponse({'error': 'User gagal dihapus'}, status=500)
    return HttpResponseBadRequest('Invalid request')

@login_required
def daftar_debit_air(request):
    now = timezone.now()
    periode = request.GET.get('periode', f"{now.year}-{now.month:02d}")  # format: YYYY-MM
    opsi = request.GET.get('opsi', 'Full')
    id_bendung = request.GET.get('bendung')

    try:
        tahun, bulan = map(int, periode.split('-'))
    except:
        tahun = now.year
        bulan = now.month

    debit_air_qs = DebitAir.objects.all()

    if id_bendung:
        debit_air_qs = debit_air_qs.filter(bendungan_id=id_bendung)

    debit_air_qs = debit_air_qs.filter(tanggal__month=bulan, tanggal__year=tahun)

    if opsi == 'Tanggal 1-15':
        debit_air_qs = debit_air_qs.filter(tanggal__day__lte=15)
    elif opsi == 'Tanggal 16-31':
        debit_air_qs = debit_air_qs.filter(tanggal__day__gte=16)

    debit_air_qs = debit_air_qs.order_by('tanggal')
    bendung_list = Bendung.objects.all()
    
    context = {
        'data_debit': debit_air_qs,
        'bulan': int(bulan),
        'tahun': int(tahun),
        'opsi': opsi,
        'id_bendung': int(id_bendung) if id_bendung else None,
        'bendung_list': bendung_list
    }
    return render(request, 'debit_air.html', context)

def rumus_q_limpas(h):
    """Rumus untuk Q limpasan (h_07, h_12, h_17)"""
    return round(1 * 46.8 * ((2/3) * h) * math.sqrt(9.81 * ((2/3) * h)), 3)

def rumus_q_kiri(h):
    """Rumus untuk Q pintu kiri"""
    return round(1.71 * 2 * (h ** 1.5), 3)

def rumus_q_kanan(h):
    """Rumus untuk Q pintu kanan"""
    return round(1.71 * 0.6 * (h ** 1.5), 3)

@login_required
@csrf_exempt
def tambah_debit_air(request):
    if request.method == 'POST':
        try:
            data = request.POST
            tanggal = data.get('tanggal')
            id_bendung = data.get('bendungan')
            bendungan = get_object_or_404(Bendung, id=id_bendung)

            # H
            h_07 = float(data.get('h_07', 0))
            h_12 = float(data.get('h_12', 0))
            h_17 = float(data.get('h_17', 0))

            h_kiri_07 = float(data.get('h_kiri_07', 0))
            h_kiri_12 = float(data.get('h_kiri_12', 0))
            h_kiri_17 = float(data.get('h_kiri_17', 0))

            h_kanan_07 = float(data.get('h_kanan_07', 0))
            h_kanan_12 = float(data.get('h_kanan_12', 0))
            h_kanan_17 = float(data.get('h_kanan_17', 0))

            # Q (menggunakan rumus yang sesuai)
            q_07 = rumus_q_limpas(h_07)
            q_12 = rumus_q_limpas(h_12)
            q_17 = rumus_q_limpas(h_17)

            q_kiri_07 = rumus_q_kiri(h_kiri_07)
            q_kiri_12 = rumus_q_kiri(h_kiri_12)
            q_kiri_17 = rumus_q_kiri(h_kiri_17)

            q_kanan_07 = rumus_q_kanan(h_kanan_07)
            q_kanan_12 = rumus_q_kanan(h_kanan_12)
            q_kanan_17 = rumus_q_kanan(h_kanan_17)

            # Simpan ke DB
            DebitAir.objects.create(
                tanggal=tanggal,
                bendungan=bendungan,
                h_07=h_07, q_07=q_07,
                h_12=h_12, q_12=q_12,
                h_17=h_17, q_17=q_17,
                h_kiri_07=h_kiri_07, q_kiri_07=q_kiri_07,
                h_kiri_12=h_kiri_12, q_kiri_12=q_kiri_12,
                h_kiri_17=h_kiri_17, q_kiri_17=q_kiri_17,
                h_kanan_07=h_kanan_07, q_kanan_07=q_kanan_07,
                h_kanan_12=h_kanan_12, q_kanan_12=q_kanan_12,
                h_kanan_17=h_kanan_17, q_kanan_17=q_kanan_17,
            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid method'})

@login_required
def edit_debit_air(request, id):
    debit = get_object_or_404(DebitAir, id=id)
    bendung_list = Bendung.objects.all()

    if request.method == 'POST':
        try:
            debit.tanggal = request.POST.get('tanggal')
            debit.bendungan_id = request.POST.get('bendungan')

            # Muka air limpasan
            debit.h_07 = float(request.POST.get('h_07') or 0)
            debit.h_12 = float(request.POST.get('h_12') or 0)
            debit.h_17 = float(request.POST.get('h_17') or 0)
            debit.q_07 = rumus_q_limpas(debit.h_07)
            debit.q_12 = rumus_q_limpas(debit.h_12)
            debit.q_17 = rumus_q_limpas(debit.h_17)

            # Debit Pintu Kiri
            debit.h_kiri_07 = float(request.POST.get('h_kiri_07') or 0)
            debit.q_kiri_07 = rumus_q_kiri(debit.h_kiri_07)

            debit.h_kiri_12 = float(request.POST.get('h_kiri_12') or 0)
            debit.q_kiri_12 = rumus_q_kiri(debit.h_kiri_12)

            debit.h_kiri_17 = float(request.POST.get('h_kiri_17') or 0)
            debit.q_kiri_17 = rumus_q_kiri(debit.h_kiri_17)

            # Debit Pintu Kanan
            debit.h_kanan_07 = float(request.POST.get('h_kanan_07') or 0)
            debit.q_kanan_07 = rumus_q_kanan(debit.h_kanan_07)

            debit.h_kanan_12 = float(request.POST.get('h_kanan_12') or 0)
            debit.q_kanan_12 = rumus_q_kanan(debit.h_kanan_12)

            debit.h_kanan_17 = float(request.POST.get('h_kanan_17') or 0)
            debit.q_kanan_17 = rumus_q_kanan(debit.h_kanan_17)

            debit.save()

            return JsonResponse({'status': 'success', 'message': 'Data berhasil diubah'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return render(request, 'edit_debit_air.html', {
        'debit': debit,
        'bendung_list': bendung_list
    })

@login_required
@csrf_exempt
def hapus_debit_air(request, id):
    debit = get_object_or_404(DebitAir, id=id)
    debit.delete()
    return HttpResponse(status=200)

@login_required
def cetak_debit_air_pdf(request):
    now = timezone.now()
    periode = request.GET.get('periode', f"{now.year}-{now.month:02d}")
    opsi = request.GET.get('opsi', 'Full')
    id_bendung = request.GET.get('bendung')

    try:
        tahun, bulan = map(int, periode.split('-'))
    except:
        tahun = now.year
        bulan = now.month

    debit_air_qs = DebitAir.objects.all()

    if id_bendung:
        debit_air_qs = debit_air_qs.filter(bendungan_id=id_bendung)

    debit_air_qs = debit_air_qs.filter(tanggal__month=bulan, tanggal__year=tahun)

    if opsi == 'Tanggal 1-15':
        debit_air_qs = debit_air_qs.filter(tanggal__day__lte=15)
    elif opsi == 'Tanggal 16-31':
        debit_air_qs = debit_air_qs.filter(tanggal__day__gte=16)

    debit_air_qs = debit_air_qs.order_by('tanggal')

    bendung_obj = None
    if id_bendung:
        bendung_obj = get_object_or_404(Bendung, id=id_bendung)

    bulan_indo = [
        '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    nama_bulan = bulan_indo[bulan]

    context = {
        'data_debit': debit_air_qs,
        'bulan': int(bulan),
        'tahun': int(tahun),
        'opsi': opsi,
        'bendung': bendung_obj,
        'nama_bulan': nama_bulan,
    }

    template = get_template('debit_air_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="debit_air.pdf"'

    # Create PDF
    pisa_status = pisa.CreatePDF(
        src=html,
        dest=response,
        encoding='utf-8'
    )

    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat membuat PDF', status=500)
    return response

@login_required
def logout_view(request):
    return render(request, 'logout.html')

@login_required
def logout_session(request):
    logout(request)
    return redirect('index')