# Email/SMTP Setup für n8n Alerts

## Option A: Gmail (Empfohlen, 5 min)

### Step 1: Google Account 2FA aktivieren
```
1. https://myaccount.google.com/security
2. Enable 2-Step Verification
```

### Step 2: App Password generieren
```
1. https://myaccount.google.com/apppasswords
2. Select: Mail, Windows Computer
3. Copy 16-character Password (abcd efgh ijkl mnop)
```

### Step 3: In .env speichern
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=smartops@mbergsch.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_FROM_EMAIL=smartops@mbergsch.com
SMTP_FROM_NAME=Hermes
```

### Step 4: In n8n testen
```
Credentials → New → Email
Host: smtp.gmail.com
Port: 587
User: smartops@mbergsch.com
Password: (App Password)
TLS: True
```

---

## Option B: Brevo (Kostenlos 300 Emails/Tag)

```
1. https://www.brevo.com/de → Sign Up
2. Dashboard → SMTP Credentials
3. Copy Host, Port, User, Password
```

---

## In n8n verwenden

```
Node: Email
To: smartops@mbergsch.com
Subject: Alert
Message: Text from previous node
```

---

**Empfehlung:** Gmail (simplest)
