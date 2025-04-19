**<!--
  _   _ _                         _                
 | | | (_)___ ___  _ __ ___  _ __| |_   _ _ __ ___ 
 | |_| | / __/ __|| '_ ` _ \| '__| | | | | '__/ _ \
 |  _  | \__ \__ \| | | | | | |  | | |_| | | |  __/
 |_| |_|_|___/___/|_| |_| |_|_|  |_|\__,_|_|  \___|
-->**

<p align="center">
  <a href="https://github.com/MUMIT-404-CYBER/strategic">
    <img src="https://img.shields.io/badge/Chapeey-Tech-Strategic%20Shell%20Toolkit-blue?style=for-the-badge&logo=gnu-bash" alt="Chapeey-Tech Kit">
  </a>
</p>

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Ribeye&size=24&color=%2300ffea&center=true&lines=Empowering+Secure+Tunneling,+One+Script+At+A+Time" alt="Typing SVG">
</p>

<p align="center">
  <a href="https://github.com/MUMIT-404-CYBER" target="_blank">
    <img src="https://github-profile-trophy.vercel.app/?username=MUMIT-404-CYBER&theme=dark&no-frame=true&title=Stars,Commits,Issues" alt="GitHub Stats">
  </a>
</p>

---

## 🚀 Table of Contents

- [✨ About](#-about)
- [🛠️ Features](#️-features)
- [⚙️ Installation](#️-installation)
- [💻 Tested Environments](#-tested-environments)
- [🚪 Port Definitions](#-port-definitions)
- [☁️ Cloudflare Settings](#️-cloudflare-settings)
- [📡 Supported Protocols](#️-supported-protocols)
- [📞 Contact & Community](#-contact--community)

---

## ✨ About

**Chapeey-Tech Strategic Shell Toolkit** is a one-stop, automated provisioning script designed to set up versatile tunneling and VPN services on Debian/Ubuntu servers. Whether you need Xray, Shadowsocks, Trojan, VMess, or SSH-OVPN, this script installs and configures everything with optimal security defaults and lightweight performance.

---

## 🛠️ Features

- 📈 Automatic 1 GiB Swap allocation
- ⚙️ Dynamic server tuning for high throughput
- 🔒 Xray Core + V2Ray support
- 🚫 Integrated Fail2Ban and ad-blocking rules
- 🧹 Auto-log rotation (every 3 minutes)
- ⏳ User expiration management
- 📄 Detailed user account display
- 🔄 Update & rollback convenience

---

## ⚙️ Installation

> **Quickstart:**

```bash
wget --no-check-certificate https://cdn.chapeey.store/chapeey.sh \
  && chmod +x chapeey.sh \
  && ./chapeey.sh
```

> **Update Script:**

```bash
wget https://raw.githubusercontent.com/Amchapeey/strategic/main/update.sh \
  && chmod +x update.sh \
  && ./update.sh
```

---

## 💻 Tested Environments

<p align="center">
  <img src="https://img.shields.io/badge/Debian-9%20%7C%2010%20%7C%2011%20%7C%2012-purple?style=for-the-badge&logo=debian" alt="Debian">
  <img src="https://img.shields.io/badge/Ubuntu-18.04%20%7C%2020.04%20%7C%2022.04%20%7C%2024.04-red?style=for-the-badge&logo=ubuntu" alt="Ubuntu">
</p>

---

## 🚪 Port Definitions

| Service                | Port           |
|------------------------|----------------|
| Trojan WS/GRPC         | 443            |
| Shadowsocks WS/GRPC    | 443            |
| VLESS WS/GRPC          | 443            |
| VMess WS/GRPC          | 443            |
| VLESS Non-TLS          | 80             |
| VMess Non-TLS          | 80             |
| SSH WS/TLS             | 443            |
| SSH Non-TLS            | 8880           |
| OVPN SSL/TCP           | 1194           |
| SlowDNS                | 5300           |

---

## ☁️ Cloudflare Settings

> **Recommended Configuration:**

- SSL/TLS: **Full**
- SSL/TLS Recommender: **Off**
- WebSockets: **On**
- gRPC: **On**
- Always Use HTTPS: **Off**
- Under Attack Mode: **Off**

---

## 📡 Supported Protocols

This toolkit automates setup for the following tunneling and VPN services:

- Trojan (WS/gRPC)
- Shadowsocks (WS/gRPC)
- VLESS (WS/gRPC, non-TLS)
- VMess (WS/gRPC, non-TLS)
- SSH (WS/TLS & plain)
- OpenVPN (SSL/TCP)
- SlowDNS

---

## 📞 Contact & Community

<p align="center">
  <a href="https://t.me/chapeey" target="_blank">
    <img src="https://img.shields.io/badge/Telegram-Chat-blue?style=for-the-badge&logo=telegram" alt="Telegram">
  </a>
  <a href="https://wa.me/+254704348959" target="_blank">
    <img src="https://img.shields.io/badge/WhatsApp-Support-green?style=for-the-badge&logo=whatsapp" alt="WhatsApp">
  </a>
  <a href="https://www.instagram.com/amchapeey/" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-Follow-purple?style=for-the-badge&logo=instagram" alt="Instagram">
  </a>
</p>

---

<p align="center">_Crafted with ❤️ by Chapeey-Tech_</p>
