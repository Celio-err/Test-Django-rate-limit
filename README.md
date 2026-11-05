Ida ne'e mak estrutura kodigu ne'ebe ita sei muda ka konfigura bazeia ba endeseru tarjetu nian.


BASE_URL = "https://www.example.com"          # muda ba domain tarjetu
LOGIN_PATH = "https://www.example.com/login/"                 # muda ba login page ka admin panel
USERNAME_TO_TEST = "admin"                   # username ezemplu ne'ebe mak sei utiliza ba teste
NUM_ATTEMPTS = 50                            # Total teste ne'ebe sei aplika ba login page nian.

 print("\n=== REZULTADU ===")
    if blocked_detected:
        print(" Protesaun ba brute-force detekta ona. Sistema fo limitasaun ba koko login.")
    else:
        print("  La iha isu blokeia ruma depoisde"
              f"{NUM_ATTEMPTS} teste. Bele melloria tan protesaun"
              "hanesan django-axes ka rate limiting iha level web server (nginx).")
