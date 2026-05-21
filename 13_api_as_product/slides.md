# Buổi 13: API as a Product

---

## API là gì trong mắt Business?

> "API is not just a technical interface — it's a **product** that developers consume."

| Góc nhìn kỹ thuật | Góc nhìn sản phẩm |
|-------------------|-------------------|
| Endpoint, schema, protocol | Developer experience, onboarding |
| Uptime, latency | SLA, trust, brand |
| Rate limiting | Pricing tiers, quota |
| Logs, errors | KPIs, analytics, churn |

**Ví dụ thực tế**: Stripe, Twilio, Google Maps API — đây là *core business*, không chỉ là infrastructure.

---

## Developer Experience (DX)

### Vì sao DX quan trọng?

> **Time-to-first-call** là KPI quan trọng nhất khi ra mắt API.

Developer không kiên nhẫn. Nếu mất > 30 phút để chạy được call đầu tiên → họ chuyển sang đối thủ.

### Checklist DX tốt

- ✅ **Sandbox**: Test không cần đăng ký, không cần credit card
- ✅ **Instant key**: Đăng ký → nhận key ngay, không approval
- ✅ **Auto docs**: Swagger UI / OpenAPI luôn đồng bộ với code
- ✅ **Consistent errors**: Mọi lỗi cùng format `{error, message, hint}`
- ✅ **Copy-paste examples**: Curl, Python, JS trong docs
- ✅ **Quota headers**: Client biết còn bao nhiêu quota mà không cần gọi endpoint riêng

---

## Monetization Models

### 1. Freemium
```
Free     → Limited quota  → Thu hút developers (acquisition)
Paid     → More quota     → Convert khi họ cần scale
```
**Ví dụ**: Stripe (không có free tier), Mapbox (free 50k/tháng), SendGrid (100 email/ngày)

### 2. Pay-per-call
```
0–1,000 calls      → $0
1,001–100,000      → $0.001/call
> 100,000          → $0.0005/call (volume discount)
```
**Ví dụ**: AWS Lambda, Google Maps API, OpenAI API

### 3. Subscription tiers
```
Pro ($29/mo)        → Fixed quota (10,000 calls/ngày)
Enterprise ($299/mo) → Unlimited + SLA + Support
```
**Ví dụ**: GitHub API, Twilio, Datadog

### 4. Feature Gating (không phải quota)
Không giới hạn số lượng — giới hạn **tính năng**:
- Free: Basic endpoints
- Pro: Advanced search, webhooks, bulk operations
- Enterprise: Custom models, dedicated infrastructure

---

## KPIs — Đo lường API as a Product

### Acquisition KPIs
| KPI | Công thức | Target |
|-----|-----------|--------|
| Registered Developers | Σ đăng ký | +20%/tháng |
| Time-to-first-call | Đăng ký → Call đầu tiên | < 5 phút |
| Sandbox conversion | Sandbox users → Register | > 30% |

### Engagement KPIs
| KPI | Công thức | Target |
|-----|-----------|--------|
| Active Developers | Gọi API trong 30 ngày | > 60% của tổng |
| API Call Volume | Tổng calls/tháng | +15%/tháng |
| Error Rate | Errors / Total calls × 100 | < 1% |

### Revenue KPIs
| KPI | Công thức | Target |
|-----|-----------|--------|
| MRR | Σ(users × plan_price) | +10%/tháng |
| Free→Paid conversion | Paid users / Free users | 3–5% |
| Churn Rate | Canceled / Total paid | < 3%/tháng |
| ARPU | MRR / Active users | Tăng theo thời gian |

---

## Developer Portal — Thành phần cần có

```
Developer Portal
├── Landing page     — Value proposition, use cases
├── Pricing page     — Tier comparison, CTA rõ ràng
├── Quick start      — Get key trong < 2 phút
├── Sandbox          — Try trước khi đăng ký
├── API Reference    — Swagger UI / Redoc tự động
├── Usage dashboard  — Quota, error rate, history
├── Changelog        — Breaking changes, deprecations
└── Support          — Forum / email / Slack by tier
```

---

## Sandbox Design

### Tại sao Sandbox quan trọng?

> Nếu developer phải đăng ký trước khi thử → conversion rate giảm đáng kể.

### Cách implement Sandbox

```python
@app.get("/sandbox/products")
def sandbox():
    return {
        "sandbox": True,           # Flag rõ ràng
        "data": DEMO_DATA,         # Data mẫu, không thật
        "note": "Đây là demo data",
        "get_real": "POST /register"  # CTA luôn có trong response
    }
```

**Best practice**:
- Sandbox data có prefix `[DEMO]` hoặc `[TEST]`
- Không lưu data sandbox vào DB thật
- Sandbox không tốn quota → developer thoải mái explore
- Có rate limit riêng để ngăn abuse

---

## Launch Strategy

### Phase 1 — Private Beta
- Mời 20–50 developers tin cậy thử nghiệm
- Thu thập feedback về DX, docs, pricing
- KPI: Time-to-first-call, error rate

### Phase 2 — Public Launch
- Publish trên GitHub, Dev.to, ProductHunt
- Free tier không cần credit card
- KPI: Đăng ký, call volume

### Phase 3 — Monetization
- Email campaign cho Free users có usage cao
- A/B test pricing (Pro $19 vs $29 vs $39)
- KPI: Conversion rate, MRR

---

## Phân tích — Stripe API as a Product

| Chiến lược | Chi tiết |
|------------|----------|
| **DX** | Dashboard tuyệt vời, docs chi tiết, test mode ngay từ đầu |
| **Pricing** | Pay-per-transaction (2.9% + $0.30), không subscription |
| **Sandbox** | Test mode hoàn toàn tách biệt production |
| **Versioning** | Header `Stripe-Version`, không break existing integrations |
| **Support** | Community (free), email (paid), Slack (enterprise) |
| **Webhook** | Delivery retry 3 ngày, signed payload, delivery history |

**Kết quả**: $14B doanh thu 2023, hàng triệu developer dùng.

---

## Tổng kết

```
API as a Product = DX + Monetization + Analytics

DX            →  Time-to-first-call, Sandbox, Docs
Monetization  →  Freemium, Pay-per-call, Feature gating
Analytics     →  KPIs: MRR, Conversion, Error rate, Active devs
```

> **Quy tắc vàng**: Tối ưu cho developer trước — doanh thu theo sau.
