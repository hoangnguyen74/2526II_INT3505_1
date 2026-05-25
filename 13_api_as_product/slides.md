# Buoi 13: API as a Product

---

## Slide 1: Title + Agenda

### Noi dung

**Buoi 13: API as a Product**

Muc tieu hom nay:
1. Hieu goc nhin **Product** khi thiet ke API
2. Biet cach **kiem tien** tu API (Freemium, Feature Gating)
3. Do luong thanh cong bang **KPIs** (MRR, Conversion, Error Rate)

Agenda:
- 5 phut: Kien thuc (4 slides)
- 10 phut: Live Demo (Sandbox, Quota, Portal)
- 5 phut: Tong ket + Thao luan

### Speaker Notes

Chao cac ban. Hom nay chung ta se chuyen goc nhin: tu "API la code" sang "API la san pham". Cac buoi truoc da day cach XAY API (FastAPI, patterns, security). Hom nay se day cach BAN no — cho developer khac dung va tra tien.

---

## Slide 2: API khong chi la code — API la san pham

### Noi dung

| Goc nhin ky thuat | Goc nhin san pham |
|-------------------|-------------------|
| Endpoint, schema, protocol | Developer experience, onboarding |
| Uptime, latency | SLA, trust, brand |
| Rate limiting | Pricing tiers, quota |
| Logs, errors | KPIs, analytics, churn |

**Vi du thuc te:**
- Stripe: $14B doanh thu 2023 — API LA business
- Twilio: SMS API — $3.8B doanh thu
- Google Maps API: $10B+ doanh thu

### Speaker Notes

Nhin bang nay: cung 1 thu nhung nhin khac nhau hoan toan. Rate limiting voi ky thuat la "bao ve server", nhung voi business la "pricing tier — tra nhieu hon thi duoc goi nhieu hon". Stripe khong ban phan mem — ho ban API. Va ho kiem $14 ty mot nam.

---

## Slide 3: Developer Experience (DX) — Yeu to quyet dinh

### Noi dung

> **Time-to-first-call** la KPI quan trong nhat khi ra mat API.

Developer khong kien nhan. Neu mat > 30 phut de chay duoc call dau tien, ho se chuyen sang doi thu.

**Checklist DX tot:**
- Sandbox: Test khong can dang ky
- Instant key: Dang ky xong, nhan key ngay, khong can phe duyet
- Auto docs: Swagger UI tu dong dong bo voi code
- Consistent errors: Moi loi cung format {error, message, hint}
- Copy-paste examples: curl, Python, JS san trong docs
- Quota headers: X-Quota-Remaining trong moi response

### Speaker Notes

Time-to-first-call: tu luc developer NGHE ve API cua ban den khi ho chay duoc 1 request thanh cong. Stripe lam duoc trong 5 phut. Neu cua ban mat 1 ngay, ban thua roi. 6 items trong checklist nay — tat ca deu da implement trong code demo. Sang demo se thay ngay.

---

## Slide 4: Kiem tien tu API — Freemium + Feature Gating

### Noi dung

**Mo hinh Freemium:**

| Plan | Gia | Quota | Tinh nang |
|------|-----|-------|-----------|
| Free | $0/thang | 100 calls/ngay | CRUD co ban, Sandbox |
| Pro | $29/thang | 10,000 calls/ngay | + Search, Analytics |
| Enterprise | $299/thang | Unlimited | + SLA 99.9%, Support |

**2 cach gioi han:**
- **Quota**: gioi han SO LUONG (Free chi 100 req/ngay)
- **Feature Gating**: gioi han TINH NANG (Search chi cho Pro+)

### Speaker Notes

Tai sao can Free tier? Day la cua vao — dung de thu hut developer. Ho dung free, thay hay, roi tu nang cap. Conversion rate chi can 2-5% la profitable. Quan trong la phan biet quota voi feature gating. Quota gioi han bao nhieu lan goi. Feature gating gioi han goi duoc cai gi. Demo se thay: Free user goi Search bi 403 — khong phai 429.

---

## Slide 5: KPIs — Do luong API as a Product

### Noi dung

| Nhom | KPI | Cong thuc | Target |
|------|-----|-----------|--------|
| Acquisition | Registered Developers | Tong dang ky | +20%/thang |
| Acquisition | Time-to-first-call | Dang ky den Call 1 | < 5 phut |
| Engagement | Active Developers | Goi API trong 30 ngay | > 60% |
| Engagement | Error Rate | Errors / Total x 100 | < 1% |
| Revenue | MRR | Sum(users x plan_price) | +10%/thang |
| Revenue | Free-to-Paid Conversion | Paid / Free users | 3-5% |

### Speaker Notes

6 KPIs chinh. Acquisition do thu hut, Engagement do giữ chan, Revenue do kiem tien. Tat ca deu tinh duoc tu data — va demo se thay admin dashboard co day du cac con so nay. Chu y: MRR la Monthly Recurring Revenue — doanh thu dinh ky hang thang. Day la metric quan trong nhat cua SaaS.

---

## Slide 6: Live Demo

### Noi dung

**Demo A:** Developer Journey (4 phut)
- Sandbox (khong can key) -> Dang ky -> Goi API -> Feature Gating -> Upgrade

**Demo B:** Admin KPI Dashboard (3 phut)
- Analytics: MRR, error rate, calls by plan, top endpoints

**Demo C:** Developer Portal (3 phut)
- portal.html: live stats, pricing, register, usage dashboard

### Speaker Notes

Chuyen sang demo. Mo terminal da chuan bi san. [Chay demo.ps1 hoac goi thu cong]

Demo A la hanh trinh cua developer: tu Sandbox (khong can gi) -> dang ky (nhan key ngay) -> goi API (thay quota headers) -> thu Search (bi chan vi Free) -> upgrade len Pro -> Search thanh cong.

Demo B la goc nhin cua owner: admin dashboard thay duoc MRR, error rate, top endpoints.

Demo C la Developer Portal — UI tron ven ma developer thay khi muon dung API cua ban.

---

## Slide 7: Developer Portal — Thanh phan can co

### Noi dung

```
Developer Portal
|-- Landing page     — Value proposition
|-- Pricing page     — So sanh tier, CTA ro rang
|-- Quick start      — Lay key trong < 2 phut
|-- Sandbox          — Thu truoc khi dang ky
|-- API Reference    — Swagger UI tu dong
|-- Usage dashboard  — Quota, error rate, history
|-- Changelog        — Breaking changes
|-- Support          — Forum / email / Slack by tier
```

(Da implement day du trong portal.html)

### Speaker Notes

Slide nay tuong ung voi portal.html vua demo. Moi phan trong cay nay deu quan trong. Thieu Sandbox thi conversion giam. Thieu Usage dashboard thi developer khong biet con bao nhieu quota. Thieu Changelog thi developer mat tin tuong khi ban thay doi API.

---

## Slide 8: Tong ket + Thao luan

### Noi dung

**Cong thuc:**

```
API as a Product = DX + Monetization + Analytics
```

- **DX**: Time-to-first-call, Sandbox, Instant key, Docs
- **Monetization**: Freemium, Feature gating, Pricing tiers
- **Analytics**: KPIs — MRR, Conversion, Error rate, Active devs

> Quy tac vang: **Toi uu cho developer truoc — doanh thu theo sau.**

**Thao luan:** API nhom ban dang lam — ap dung 3 yeu to nay nhu the nao?

**Doc them:** `business_model_canvas.md` — Business Model Canvas day du 9 blocks

### Speaker Notes

Tong ket lai 1 cong thuc don gian: DX + Monetization + Analytics. Stripe thanh cong khong phai vi ho GIOI nhat — ma vi ho DE DUNG nhat. Cau hoi cho lop: "API nhom ban dang lam — neu ban no, ban se chia pricing nhu the nao? Feature nao lock cho plan cao?" Nếu co thoi gian, gioi thieu business_model_canvas.md — tài lieu tham khao ve Business Model Canvas ap dung cho API.
