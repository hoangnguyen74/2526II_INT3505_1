// Tận dụng Node V24 built-in fetch để bypass việc máy người dùng thiếu cài đặt Java
const fs = require('fs');
const https = require('https');
const path = require('path');
const yaml = require('js-yaml'); // Sẽ cần npm install js-yaml
const { execSync } = require('child_process');

async function generateOnline() {
    console.log("=== Khởi tạo Tiến trình OpenAPI Cloud Generator ===");
    console.log("[1] Biên dịch file YAML sang JSON...");
    
    // Đọc file config YAML
    const yamlContent = fs.readFileSync('product_api.yaml', 'utf8');
    const specJson = yaml.load(yamlContent);

    console.log("[2] Gửi yêu cầu uỷ thác đến Server Đám mây của OpenAPI-Generator...");
    
    const response = await fetch('https://api.openapi-generator.tech/api/gen/servers/nodejs-express-server', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            options: {
                serverPort: "3000"
            },
            spec: specJson
        })
    });

    const data = await response.json();
    if (data.link) {
        console.log("[3] Máy chủ tạo code thành công! Đang tiến hành tải Zip đính kèm: " + data.link);
        
        console.log("[4] Đang tải zip...");
        const buf = await (await fetch(data.link)).arrayBuffer();
        fs.writeFileSync(path.join(__dirname, 'backend-server.zip'), Buffer.from(buf));
        
        console.log("[5] Giải nén mã nguồn...");
        try {
            execSync(`powershell Expand-Archive -Path backend-server.zip -DestinationPath backend-server -Force`);
            fs.unlinkSync('backend-server.zip');
            console.log("🎉 Hoàn tất quá trình sinh Boilerplate Server vào mục [backend-server]!");
        } catch (e) {
            console.error("Lỗi giải nén: ", e.message);
        }

    } else {
        console.error("Sinh Lỗi từ Cloud:", data);
    }
}

generateOnline().catch(console.error);
