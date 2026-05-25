# Buoi 13: API as a Product — Kich ban & Noi dung

> Thoi luong: 20 phut | Doi tuong: SV UET da hoc FastAPI, API patterns
> Slides: 8 slides (xem slides.md) | Demo: 3 kich ban (xem demo.ps1)

---

## Chuan bi truoc buoi hoc

- [ ] Terminal 1: `cd 13_api_as_product && py -m uvicorn main:app --reload`
- [ ] Browser tab 1: http://localhost:8000/docs (Swagger UI)
- [ ] Browser tab 2: mo `portal.html` (double-click file)
- [ ] Terminal 2: san sang chay `PowerShell -ExecutionPolicy Bypass -File demo.ps1`
- [ ] Test nhanh: `Invoke-RestMethod http://localhost:8000/sandbox/products` — phai tra JSON

---

## Phan 1: Slides (0:00 — 5:00)

### [Slide 1] Title + Agenda (0:00 — 0:30)

**Noi:**
> "Hom nay la buoi cuoi — ta se chuyen goc nhin. Cac buoi truoc day CACH XAY API. Hom nay day CACH BAN no. 3 thu can biet: Developer Experience, cach kiem tien, va do luong thanh cong."

Agenda nhanh: 5 phut kien thuc, 10 phut live demo, 5 phut thao luan.

---

### [Slide 2] API = Product (0:30 — 2:00)

**Kien thuc nen:**
API khong chi la endpoint va schema. Khi ban API cho nguoi khac dung, no tro thanh san pham — can thiet ke nhu san pham: co gia, co ho tro, co analytics.

**Noi:**
> "Nhin bang nay: cung 1 thu nhung goc nhin khac. Rate limiting voi ky thuat la 'bao ve server'. Voi business la 'pricing tier — tra nhieu thi goi nhieu'. Stripe kiem 14 ty do mot nam chi bang ban API. Twilio, Google Maps tuong tu — API LA core business."

**Diem nhan:** Stripe, Twilio la nhung cong ty ma SAN PHAM CHINH la API.

---

### [Slide 3] Developer Experience (2:00 — 3:30)

**Kien thuc nen:**
Time-to-first-call = thoi gian tu khi developer biet API cua ban den khi ho chay duoc 1 request thanh cong. Stripe dat duoc < 5 phut. Neu cua ban mat 1 ngay, developer se bo di.

**Noi:**
> "DX la yeu to quyet dinh. Developer khong kien nhan. 6 items trong checklist nay la tieu chuan. Dac biet Sandbox — cho nguoi ta thu TRUOC khi dang ky. Instant key — khong can cho admin phe duyet. Quota headers — developer biet con bao nhieu quota MA KHONG CAN goi endpoint rieng."

**Tip:** Chi vao tung item va noi "tat ca 6 items nay deu da implement trong code demo — se thay ngay."

---

### [Slide 4] Monetization (3:30 — 5:00)

**Kien thuc nen:**
- Freemium: Free tier la "cua vao" (acquisition). Chi can 2-5% convert len Paid la profitable.
- Feature Gating khac Quota: Quota gioi han BAO NHIEU (100 req/ngay). Feature Gating gioi han GOI DUOC CAI GI (Search chi cho Pro+).

**Noi:**
> "Tai sao can Free tier? Day la marketing — developer dung thu, thay hay, tu nang cap. Conversion 2-5% la du. Quan trong la phan biet 2 cach chan: Quota la gioi han so luong — 100 req/ngay. Feature Gating la gioi han tinh nang — Search chi cho Pro. Trong demo se thay Free user goi Search bi 403, khong phai 429."

**Transition sang demo:**
> "OK, kien thuc du roi. Bay gio thay no chay that."

---

## Phan 2: Live Demo (5:00 — 15:00)

### [Slide 6] Live Demo title card

**2 cach chay demo:**
- **Tu dong:** `PowerShell -ExecutionPolicy Bypass -File demo.ps1` (nhan Enter giua cac phan)
- **Thu cong:** copy tung lenh tu ben duoi

---

### Demo A: Developer Journey (5:00 — 9:00)

**Muc tieu:** Cho lop thay hanh trinh cua developer tu zero den API call thanh cong.

**Buoc 1 — Sandbox** (30 giay)
```powershell
Invoke-RestMethod http://localhost:8000/sandbox/products
```
> "Khong can key, khong can dang ky. Ai cung goi duoc. Data co [DEMO] prefix de phan biet. Va luon co CTA: 'POST /register de lay key that'."

**Buoc 2 — Xem gia** (30 giay)
```powershell
Invoke-RestMethod http://localhost:8000/plans
```
> "3 tier: Free mien phi, Pro $29, Enterprise $299. Free la cua vao."

**Buoc 3 — Dang ky** (30 giay)
```powershell
$reg = Invoke-RestMethod -Method POST http://localhost:8000/developers/register `
  -ContentType "application/json" `
  -Body '{"name":"Demo User","email":"demo@test.com","plan":"free"}'
$key = $reg.api_key
Write-Host "Key: $key"
```
> "Nhan key NGAY. Khong can cho phe duyet. Time-to-first-call < 1 phut."

**Buoc 4 — Goi API + Quota headers** (30 giay)
```powershell
$resp = Invoke-WebRequest -Uri http://localhost:8000/api/v1/products `
  -Headers @{"X-API-Key" = $key} -UseBasicParsing
$resp.Headers['X-Plan']
$resp.Headers['X-Quota-Remaining']
```
> "Chu y response headers: X-Plan cho biet plan hien tai, X-Quota-Remaining cho biet con bao nhieu. Developer khong can goi endpoint rieng."

**Buoc 5 — Feature Gating** (1 phut)
```powershell
# Free user goi Search -> 403
Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key" = $key}
# -> 403 FEATURE_LOCKED

# Upgrade len Pro
Invoke-RestMethod -Method POST http://localhost:8000/developers/upgrade `
  -ContentType "application/json" `
  -Body '{"email":"demo@test.com","new_plan":"pro"}'

# Goi lai -> thanh cong
Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key" = $key}
```
> "Day la Feature Gating: 403 khong phai 429. Khong phai het quota — ma la TINH NANG bi khoa. Upgrade len Pro — goi lai thanh cong."

**Hoi lop:** "Feature Gating vs Quota — khi nao dung cai nao?"

---

### Demo B: Admin KPI Dashboard (9:00 — 12:00)

**Muc tieu:** Cho lop thay goc nhin cua API owner — do luong business.

```powershell
Invoke-RestMethod http://localhost:8000/admin/analytics `
  -Headers @{"X-Admin-Key" = "admin-secret-key"}
```

> "Day la nhung gi owner thay. registered_developers: bao nhieu nguoi dang ky. active_today: bao nhieu nguoi THAT SU dung hom nay. total_api_calls: tong luot goi. error_rate: ty le loi. monthly_recurring_revenue_usd: doanh thu hang thang — day la MRR, metric quan trong nhat cua SaaS."

```powershell
Invoke-RestMethod http://localhost:8000/admin/developers `
  -Headers @{"X-Admin-Key" = "admin-secret-key"}
```

> "Va day la breakdown theo tung developer: ai dung nhieu, ai tra tien, ai dung free. Total MRR la tong tat ca."

**Lien ket voi slide 5:** "Nho KPIs o slide truoc khong? Tat ca deu co trong response nay."

---

### Demo C: Developer Portal (12:00 — 15:00)

**Muc tieu:** Cho lop thay UI hoan chinh — khong chi la API endpoint.

**Chuyen sang browser tab portal.html:**

1. **Live Stats** (30 giay) — chi vao goc tren: "Tu cap nhat moi 5 giay tu /admin/analytics"
2. **Pricing** (30 giay) — 3 cards: "Free/Pro/Enterprise voi tinh nang va gia"
3. **Register** (1 phut) — nhap ten + email moi, bam Register: "Key hien ngay, copy duoc, curl example san"
4. **My Usage** (30 giay) — nhap email: "Thanh quota doi mau — xanh/vang/do tuy % da dung"
5. **Quick Start** (30 giay) — chuyen tabs: "Code mau curl/Python/JS — copy paste chay ngay"

> "Day la full Developer Portal. Developer khong can doc docs 100 trang. Mo portal, dang ky, copy code, chay — xong."

---

## Phan 3: Tong ket + Thao luan (15:00 — 20:00)

### [Slide 7] Developer Portal tree (15:00 — 15:30)

**Noi:**
> "Portal vua thay co day du 8 thanh phan nay. Thieu Sandbox thi mat kha nang thu truoc. Thieu Usage dashboard thi developer khong biet con bao nhieu quota."

---

### [Slide 8] Summary + Thao luan (15:30 — 20:00)

**Noi:**
> "Tong ket: API as a Product = 3 yeu to."

Chi vao cong thuc:
> "DX — lam cho de dung. Monetization — kiem tien. Analytics — do luong. Va quy tac vang: toi uu cho developer truoc, doanh thu se theo sau. Stripe thanh cong khong phai vi ho gioi nhat — ma vi ho DE DUNG nhat."

**Cau hoi thao luan:**
> "API nhom cac ban dang lam — neu ban no, cac ban se chia pricing nhu the nao? Tinh nang nao lock cho plan cao? KPI nao do truoc?"

**Gioi thieu BMC:**
> "Doc them business_model_canvas.md — co day du 9 blocks cua Business Model Canvas ap dung cho API. Co the dung lam bai tap nhom."

---

## Quick Reference — Tat ca lenh demo

```powershell
# Sandbox
Invoke-RestMethod http://localhost:8000/sandbox/products

# Plans
Invoke-RestMethod http://localhost:8000/plans

# Register
$reg = Invoke-RestMethod -Method POST http://localhost:8000/developers/register `
  -ContentType "application/json" `
  -Body '{"name":"Demo User","email":"demo@test.com","plan":"free"}'
$key = $reg.api_key

# API call + headers
Invoke-WebRequest -Uri http://localhost:8000/api/v1/products `
  -Headers @{"X-API-Key" = $key} -UseBasicParsing

# Feature Gating (403 cho Free)
Invoke-RestMethod "http://localhost:8000/api/v1/search?q=iphone" `
  -Headers @{"X-API-Key" = $key}

# Upgrade
Invoke-RestMethod -Method POST http://localhost:8000/developers/upgrade `
  -ContentType "application/json" -Body '{"email":"demo@test.com","new_plan":"pro"}'

# Admin
Invoke-RestMethod http://localhost:8000/admin/analytics -Headers @{"X-Admin-Key"="admin-secret-key"}
Invoke-RestMethod http://localhost:8000/admin/developers -Headers @{"X-Admin-Key"="admin-secret-key"}
```
