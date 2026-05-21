# Business Model Canvas — Product API

> Áp dụng Business Model Canvas (Osterwalder) cho một API as a Product.

---

## 1. Customer Segments (Phân khúc khách hàng)

| Segment | Mô tả | Plan phù hợp |
|---------|-------|--------------|
| **Indie Developer** | Cá nhân build side project, startup sơ khai | Free |
| **SMB / Startup** | Công ty nhỏ cần data product nhanh, không muốn tự xây | Pro |
| **Enterprise** | Tập đoàn, cần SLA, compliance, account manager | Enterprise |
| **Educational** | Giảng viên, sinh viên dùng cho khóa học, demo | Free / Pro |

---

## 2. Value Propositions (Đề xuất giá trị)

### Developer Experience (DX)
- **Time-to-first-call < 5 phút**: Đăng ký → nhận key → gọi API ngay, không cần phê duyệt
- **Sandbox miễn phí**: Test trước khi đăng ký — giảm rào cản thử nghiệm
- **Tài liệu tự động**: Swagger UI tại `/docs`, luôn đồng bộ với code

### Technical Value
- REST API chuẩn, HATEOAS, consistent error format
- Response time < 100ms (SLA)
- Quota headers giúp client tự quản lý rate limiting

### Business Value
- Giảm cost tự xây data pipeline
- Pay-as-you-grow: bắt đầu $0, trả nhiều hơn khi scale
- SLA cam kết uptime cho production workload

---

## 3. Channels (Kênh tiếp cận)

```
Awareness      → GitHub README, Dev.to blog, YouTube tutorial
Consideration  → Developer Portal (portal.html), Sandbox demo
Conversion     → Free plan (no friction), pricing page
Retention      → Email newsletter, changelogs, Discord community
```

---

## 4. Customer Relationships (Quan hệ khách hàng)

| Plan | Relationship Type | Cụ thể |
|------|-------------------|--------|
| Free | Self-service | Docs, Swagger UI, community forum |
| Pro | Automated + Personal | Email support 24h, usage alerts |
| Enterprise | Dedicated | Account manager, SLA review monthly |

---

## 5. Revenue Streams (Nguồn doanh thu)

### Mô hình Freemium + Subscription

```
Free          →  $0/tháng   →  100 calls/ngày     (acquisition funnel)
Pro           →  $29/tháng  →  10,000 calls/ngày  (main revenue)
Enterprise    →  $299/tháng →  Unlimited           (high-value)
```

### Mô hình Pay-per-call (thay thế)
```
0 – 1,000 calls/tháng    →  $0
1,001 – 100,000 calls    →  $0.001/call
> 100,000 calls          →  $0.0005/call (volume discount)
```

### KPIs doanh thu
- **MRR** (Monthly Recurring Revenue) = Σ(developers × plan_price)
- **ARPU** (Average Revenue Per User) = MRR / active_developers
- **Churn Rate** = developers hủy plan / tổng developers (tháng)
- **Conversion Rate** = Free → Paid (benchmark: 2–5% là tốt)

---

## 6. Key Resources (Nguồn lực chính)

| Resource | Mô tả |
|----------|-------|
| **API Backend** | FastAPI server, infrastructure, uptime |
| **Data** | Product catalog, chất lượng data = giá trị cốt lõi |
| **Developer Portal** | Docs, sandbox, analytics dashboard |
| **Brand & Trust** | Reputation, SLA track record |
| **Developer Community** | Forum, Discord, testimonials |

---

## 7. Key Activities (Hoạt động chính)

- **API Development**: Thêm endpoints, maintain backward compatibility
- **Data Quality**: Cập nhật, validate data liên tục
- **Developer Support**: Giải đáp câu hỏi, fix bugs nhanh
- **Marketing**: Blog, tutorials, conference talks
- **Analytics**: Theo dõi KPIs, A/B test pricing

---

## 8. Key Partnerships (Đối tác chính)

| Partner | Vai trò |
|---------|---------|
| Cloud Provider (AWS/GCP) | Infrastructure, uptime |
| Payment Gateway (Stripe) | Thu phí subscription |
| Monitoring (Datadog) | SLA tracking, alerting |
| Auth Provider (Auth0) | SSO cho enterprise customers |

---

## 9. Cost Structure (Cơ cấu chi phí)

```
Infrastructure     ~40%   (servers, CDN, database)
Engineering        ~35%   (development, maintenance)
Support & Sales    ~15%   (customer success, enterprise deals)
Marketing          ~10%   (content, ads, conferences)
```

### Unit Economics
```
Free user cost      ≈ $0.20/tháng  (infra + support)
Pro user revenue    = $29/tháng → margin ~$27 (93%)
Enterprise revenue  = $299/tháng → margin ~$250 (84%)
```

---

## 10. KPIs Tổng hợp

### Acquisition
| KPI | Mô tả | Target |
|-----|-------|--------|
| Registered Developers | Tổng số đăng ký | +20%/tháng |
| Time-to-first-call | Thời gian từ đăng ký → call đầu tiên | < 5 phút |
| Sandbox → Register Rate | % người dùng sandbox đăng ký | > 30% |

### Engagement
| KPI | Mô tả | Target |
|-----|-------|--------|
| Active Developers | Gọi API trong 30 ngày | > 60% của tổng |
| Call Volume | Tổng API calls/tháng | +15%/tháng |
| Error Rate | % requests lỗi | < 1% |

### Revenue
| KPI | Mô tả | Target |
|-----|-------|--------|
| MRR | Monthly Recurring Revenue | +10%/tháng |
| Free→Paid Conversion | % Free users nâng cấp | 3–5% |
| Churn Rate | % users hủy paid plan/tháng | < 3% |
| P99 Latency | 99th percentile response time | < 200ms |

---

## Chiến lược ra mắt API (Launch Strategy)

### Phase 1 — Private Beta (Tuần 1–4)
- Mời 50 developers thử nghiệm
- Thu thập feedback về DX
- Fix critical bugs, cải thiện docs

### Phase 2 — Public Beta (Tháng 2–3)
- Mở đăng ký tự do Free plan
- Publish trên GitHub, Dev.to, Hacker News
- Target: 500 registered developers

### Phase 3 — GA + Paid Plans (Tháng 4+)
- Ra mắt Pro & Enterprise
- Email campaign với Free users có usage cao
- Target: 2–5% conversion → Paid
