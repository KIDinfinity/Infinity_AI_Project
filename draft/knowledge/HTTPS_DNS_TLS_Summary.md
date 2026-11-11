# HTTPS / DNS / 证书 / TLS 一页总结

## 核心一句话

```text
DNS 负责找到服务器
证书负责证明服务器身份
TLS 负责建立安全连接
AES 负责加密实际数据
```

---

## 整体链路

```text
浏览器
    ↓
https://workpilot.company.com
    ↓
DNS 查询
    ↓
workpilot.company.com → 47.100.1.2
    ↓
连接服务器(443端口)
    ↓
Caddy 返回 HTTPS 证书
    ↓
浏览器验证证书
    ↓
ECDHE 协商 Session Key
    ↓
AES 加密通信
    ↓
API / Web 服务
```

---

## 关键概念

### 域名（Domain）

```text
workpilot.company.com
```

只是一个方便记忆的名字。

作用：

```text
找到对应 IP
```

---

### DNS

相当于互联网电话簿。

记录：

```text
workpilot.company.com
    ↓
47.100.1.2
```

作用：

```text
域名 → IP
```

---

### IP

服务器在网络中的地址。

例如：

```text
47.100.1.2
```

浏览器最终连接的是 IP。

---

### 服务器

联网的计算机。

可能运行：

```text
Caddy
Nginx
WorkPilot API
Qdrant
MySQL
```

---

### Caddy

反向代理服务器。

职责：

```text
申请证书
续期证书
处理HTTPS
转发请求
```

例如：

```caddy
workpilot.company.com {
  reverse_proxy api:8000
}
```

---

## 证书是什么

证书不是给 IP 的。

证书属于：

```text
域名
```

例如：

```text
workpilot.company.com
```

证书中包含：

```text
域名
公钥
签发机构(CA)
有效期
```

作用：

```text
证明当前服务器
确实有资格代表这个域名
```

---

## 证书谁签发

常见 CA：

```text
Let's Encrypt
DigiCert
GlobalSign
Sectigo
```

浏览器内置了这些 CA 的根证书。

因此浏览器相信它们签发的网站证书。

---

## Caddy 如何申请证书

启动时发现配置了域名：

```text
workpilot.company.com
```

流程：

```text
Caddy
 ↓
Let's Encrypt
 ↓
验证你控制域名
 ↓
签发证书
 ↓
保存到服务器
```

---

## Let's Encrypt 如何验证域名归属

例如挑战：

```text
abc123
```

Let's Encrypt 要求：

```text
http://workpilot.company.com/.well-known/...
```

返回指定内容。

如果访问成功：

```text
证明你控制该域名
```

然后签发证书。

---

## 域名和服务器如何关联

不是服务器配置。

而是在域名服务商后台配置 DNS。

例如：

```text
阿里云 DNS

workpilot.company.com
    ↓
47.100.1.2
```

因此：

```text
域名在阿里云
服务器在 AWS
```

完全没问题。

---

## 一台服务器能有多个域名吗

可以。

```text
47.100.1.2
    ├─ api.company.com
    ├─ admin.company.com
    └─ docs.company.com
```

都能指向同一个 IP。

---

## 一台服务器能有多个 IP 吗

可以。

例如：

```text
公网IP：47.100.1.2
公网IP：47.100.1.3
私网IP：10.0.0.15
```

都属于同一台服务器。

---

## 公钥、私钥、证书关系

生成顺序：

```text
私钥
 ↓
推导出公钥
 ↓
申请证书
```

服务器保存：

```text
private.key
cert.pem
```

其中：

```text
private.key = 私钥
cert.pem    = 证书(含公钥)
```

---

## TLS 1.3 干什么

证书负责：

```text
身份认证
```

ECDHE 负责：

```text
协商 Session Key
```

AES 负责：

```text
加密真正的数据
```

---

## ECDHE 是什么

浏览器和服务器：

```text
不直接传输 Session Key
```

而是：

```text
双方交换公开参数
 ↓
各自计算
 ↓
得到相同 Session Key
```

因此：

```text
Session Key 从未在网络上传输
```

---

## 最终记忆模型

```text
域名
= 名字

DNS
= 电话簿

IP
= 地址

服务器
= 房子

Caddy
= 前台

证书
= 身份证

CA
= 公安局

ECDHE
= 安全商量密码

Session Key
= 本次会话密码

AES
= 用密码加密聊天内容
```
