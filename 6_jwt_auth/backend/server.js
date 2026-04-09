const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

const JWT_SECRET = 's3cr3t_k3y_for_demo_purposes_only';
const REFRESH_SECRET = 's3cr3t_refresh_k3y_for_demo';

// Mock User Database
const users = [
  { id: 1, username: 'admin', password: 'password123', role: 'admin' },
  { id: 2, username: 'user', password: 'password123', role: 'customer'}
];

// Mock database to store valid refresh tokens
let refreshTokens = [];

// -------------------------------------------------------------
// 1. ENDPOINT: LOGIN & NHẬN TOKEN (Hạn 30s)
// -------------------------------------------------------------
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    const user = users.find(u => u.username === username && u.password === password);
    
    if (!user) return res.status(401).json({ message: "Sai tên đăng nhập hoặc mật khẩu" });
    
    // Tạo JWT Access Token: sống 30s
    const accessToken = jwt.sign(
        { userId: user.id, username: user.username, role: user.role }, 
        JWT_SECRET, 
        { expiresIn: '30s' }
    );
    
    // Tạo Refresh Token: Rất quan trọng để Login lại dễ dàng (sống 5 phút)
    const refreshToken = jwt.sign(
        { userId: user.id, username: user.username }, 
        REFRESH_SECRET, 
        { expiresIn: '5m' }
    );
    refreshTokens.push(refreshToken);
    
    res.json({ accessToken, refreshToken });
});

// -------------------------------------------------------------
// 2. ENDPOINT: CẤP LẠI TOKEN BẰNG REFRESH TOKEN
// -------------------------------------------------------------
app.post('/api/refresh', (req, res) => {
    const { token } = req.body;
    if (!token) return res.status(401).json({ message: "Thiếu Refresh Token để cấp lại" });
    if (!refreshTokens.includes(token)) return res.status(403).json({ message: "Refresh Token này đã bị thu hồi hoặc gian lận" });

    jwt.verify(token, REFRESH_SECRET, (err, user) => {
        if (err) return res.status(403).json({ message: "Phiên làm việc ngầm đã hết hạn (Qua 5 phút)" });
        
        const newAccessToken = jwt.sign(
            { userId: user.userId, username: user.username, role: user.role }, 
            JWT_SECRET, 
            { expiresIn: '30s' }
        );
        res.json({ accessToken: newAccessToken });
    });
});

// -------------------------------------------------------------
// 3. ENDPOINT: VULNERABLE ROUTE (API Đặc biệt để chứa lỗ hổng)
// -------------------------------------------------------------
app.get('/api/vulnerable/profile', (req, res) => {
    // [LỖ HỔNG LỚN 1] Mò mẫm lấy token qua Query Params ở trình duyệt URL. 
    // Hệ luỵ: Token ngập tràn bị lưu trong Lịch sử Duyệt web, Proxy log, Router ISP.
    const token = req.query.token;
    if (!token) return res.status(401).json({ message: "Không tìm thấy URL query url?token=xxx." });
    
    try {
        // [LỖ HỔNG LỚN 2] Replay Attack Alert: Bị dev vô tình config tắt mất việc check quá hạn
        const decoded = jwt.verify(token, JWT_SECRET, { ignoreExpiration: true });
        res.json({ 
            message: "[CẢNH BÁO AN NINH]. Dù Token 30s của bạn ĐÃ HOÀN TOÀN HẾT HẠN, bạn vẫn được Server tráo trở tiếp đón!!",
            data: decoded 
        });
    } catch (err) {
        res.status(401).json({ message: "Token Invalid", error: err.message });
    }
});

// -------------------------------------------------------------
// 4. ENDPOINT: SECURE ROUTE (API Đã được tối ưu Audit rủi ro)
// -------------------------------------------------------------
app.get('/api/secure/profile', (req, res) => {
    // [CÁCH GIẢI QUYẾT 1] Tuyệt đối không cho phép dùng HTTP GET query URL. 
    // Yêu cầu token phải Nằm ngầm và mã hoá an toàn trong Headers -> Authorization: Bearer
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) return res.status(401).json({ message: "Hệ thống từ chối do bạn không khai báo Bearer token trong Headers." });

    // [CÁCH GIẢI QUYẾT 2] Default verify sẽ đá văng bất cứ dấu hiệu nào quá 30 giây dù chi 1 ms.
    jwt.verify(token, JWT_SECRET, (err, decoded) => {
        if (err) return res.status(403).json({ 
            message: "Hệ thống chặn thành công Lỗ hổng Replay Attack. Token đã vô dụng!", 
            error: err.message 
        });
        
        res.json({ 
            message: "Tuyệt vời, bạn đi Cổng hợp pháp, Token còn thời hạn. Dưới đây là thông tin bảo mật.", 
            profile: decoded 
        });
    });
});

app.listen(3000, () => {
    console.log("Server Bài tập JWT đang khởi chạy tại http://localhost:3000 !");
});
