#!/bin/bash
set -e

# --- System setup ---
sudo dnf update -y
sudo dnf install -y python3 python3-pip git

# --- Install Caddy ---
sudo curl -o /usr/bin/caddy -L "https://caddyserver.com/api/download?os=linux&arch=amd64"
sudo chmod +x /usr/bin/caddy

# Create caddy user and required directories
sudo useradd --system --home /var/lib/caddy --shell /sbin/nologin caddy || true
sudo mkdir -p /etc/caddy /var/lib/caddy
sudo chown -R caddy:caddy /var/lib/caddy

# --- Caddy systemd service ---
cat > /etc/systemd/system/caddy.service << 'EOF'
[Unit]
Description=Caddy
After=network.target

[Service]
User=caddy
Group=caddy
ExecStart=/usr/bin/caddy run --environ --config /etc/caddy/Caddyfile
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile
TimeoutStopSec=5s
LimitNOFILE=1048576
PrivateTmp=true
ProtectSystem=full
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

# --- Caddyfile ---
cat > /etc/caddy/Caddyfile << 'EOF'
pgai.connerdefeo.com {
    reverse_proxy localhost:8000
}
EOF

# --- Clone and set up your app ---
cd /home/ec2-user
git clone https://github.com/yourusername/PrettyGoodAI.git
cd PrettyGoodAI/server
pip3 install -r requirements.txt
chown -R ec2-user:ec2-user /home/ec2-user/PrettyGoodAI

# --- Systemd service ---
cat > /etc/systemd/system/pgai.service << 'EOF'
[Unit]
Description=PGAI FastAPI app
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/PrettyGoodAI/server
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat > /home/ec2-user/PrettyGoodAI/server/.env << 'EOF'
TWILIO_ACCOUNT_SID=${twilio_account_sid}
TWILIO_AUTH_TOKEN=${twilio_auth_token}
TWILIO_PHONE_NUMBER=${twilio_phone_number}
EOF

# --- Start everything ---
sudo systemctl daemon-reload
sudo systemctl enable caddy
sudo systemctl enable pgai
sudo systemctl start pgai
sudo systemctl start caddy