#!/usr/bin/env python3
import smtplib

HOST = 'mail.ana-hn.org'
USER = 'enfermeria@ana-hn.org'
PASS = 'Test-123'

def print_banner(text):
    print("\n" + "="*10, text, "="*10)

def test_starttls():
    print_banner("STARTTLS / 587")
    try:
        s = smtplib.SMTP(HOST, 587, timeout=10)
        s.set_debuglevel(1)
        # forzamos el EHLO con el nombre real del servidor
        s.ehlo(HOST)
        s.starttls()
        s.ehlo(HOST)
        s.login(USER, PASS)
        print("✅ Autenticación STARTTLS OK")
    except Exception as e:
        print("❌ FALLÓ STARTTLS:", e)
    finally:
        s.quit()

def test_ssl():
    print_banner("SSL / 465")
    try:
        s = smtplib.SMTP_SSL(HOST, 465, timeout=10)
        s.set_debuglevel(1)
        # igualmente forzamos EHLO
        s.ehlo(HOST)
        s.login(USER, PASS)
        print("✅ Autenticación SSL OK")
    except Exception as e:
        print("❌ FALLÓ SSL:", e)
    finally:
        s.quit()

if __name__ == "__main__":
    test_starttls()
    test_ssl()
