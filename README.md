<div align="center">
  <h1>🤖 Discord Bot by staleforge</h1>
  <h3>made by staleforge ~2023 | staleforge.dev</h3>
</div>

---

*(Polska wersja poniżej / Polish version below)*

## 🇬🇧 English Version

### About The Project
This project is a comprehensive and multi-functional Discord Bot originally created in **2023** as a portfolio showcase. It features a complete suite of administration, moderation, logging, and entertainment systems built on a modular `Cog` architecture using the `nextcord` library. 

⚠️ **IMPORTANT NOTE:** The codebase you are seeing here is **NOT** the raw code from 2023. What you are looking at is a **completely refactored, modernized, anonymized, and secured version** of that original bot, rewritten to adhere to modern professional engineering standards and prepared for public GitHub presentation. 
*Additionally, please note that this version of the bot is slightly less advanced than its final 2023 iteration. Unfortunately, the ultimate, most updated version from that time was lost, and I was only able to recover and restore this earlier build.*

### 🔮 Future Roadmap: Open Source AI Library
I am currently planning to expand the core concepts of this bot into a fully open-source Python library! This upcoming library will allow any developer to easily implement:
* Advanced and highly customizable Embed messages.
* Fully functional Ticket systems out-of-the-box.
* **Seamless AI Integration** to automate ticket responses, analyze messages, and manage communities efficiently.

### 📸 Proof of Creation (2023)
*(Screenshots showing the original file creation and modification timestamps from late 2023, prior to this modern refactoring)*  
<p align="center">
  <img src="screenshot.png" alt="2023 Creation Proof 1" width="600"/>
  <br><br>
  <img src="screenshot2.png" alt="2023 Creation Proof 2" width="600"/>
</p>

### Key Features
- **🎫 Advanced Ticket System** - Full UI-based ticket creation with role constraints, transcript logging, and modular operator assignment.
- **🎨 Interactive Embed Editor** - Allows server administrators to construct, edit, and push completely customized embed messages directly through Discord UI Modals.
- **📊 Polling & Giveaways** - Highly interactive and automated voting and giveaway systems.
- **📣 Promotions & Announcements** - Timed promotions automatically alerting members when a sale starts and ends.
- **🛡️ Secure Verification** - Captcha-style Math verification modals stopping basic bot accounts from entering the server.
- **📝 Comprehensive Logging** - Complete surveillance of message edits, deletions, channel modifications, permission updates, and more.
- **🐳 Dockerized** - Shipped with a `Dockerfile` for instantaneous remote deployments.

### 🐳 Deployment (Production via Docker)
The fastest and most reliable way to host this bot is using Docker.

1. **Configure the environment:** 
   Rename `.env.example` to `.env` (or create a new one) and fill out your `DISCORD_BOT_TOKEN` and Channel IDs.
2. **Build the Docker Image:**
   ```bash
   docker build -t staleforge-bot .
   ```
3. **Run the Container in Background:**
   ```bash
   docker run -d --name my-discord-bot --env-file .env staleforge-bot
   ```
   *To view logs, you can use: `docker logs -f my-discord-bot`*

---

## 🇵🇱 Polska Wersja

### O Projekcie
Ten projekt to kompleksowy i wielofunkcyjny Bot Discord, pierwotnie stworzony jeszcze w **2023 roku** jako część portfolio (showcase). Zawiera pełny pakiet systemów administracyjnych, moderacyjnych, logujących oraz rozrywkowych, zbudowanych w oparciu o modularną architekturę `Cog` przy użyciu biblioteki `nextcord`.

⚠️ **WAŻNA UWAGA:** Kod źródłowy, który tutaj widzisz, **NIE JEST** surowym kodem z 2023 r. To na co właśnie patrzysz to w **pełni zrefaktoryzowana, zmodernizowana, zanonimizowana i zabezpieczona wersja** oryginalnego bota, przepisana zgodnie z profesjonalnymi standardami inżynierii oprogramowania i dostosowana pod publiczną prezentację na GitHubie.
*Dodatkowa informacja: Zaprezentowana tutaj wersja bota jest nieco uboższa od jej finalnej postaci z tamtego okresu. Niestety, ostateczna i najbardziej ulepszona wersja bota z 2023 roku przepadła, a mi udało się odkopać i odrestaurować tylko ten nieco starszy build.*

### 🔮 Plany na przyszłość: Biblioteka AI Open Source
Obecnie planuję rozwinąć główne koncepcje tego bota w pełnoprawną, otwartą bibliotekę Python! Nadchodząca biblioteka (dostępna dla wszystkich użytkowników) pozwoli każdemu programiście na łatwe zaimplementowanie:
* Zaawansowanych i wysoce konfigurowalnych wiadomości Embed.
* W pełni funkcjonalnych systemów Ticketów (gotowych do użycia).
* **Bezproblemowej integracji ze sztuczną inteligencją (AI)** do automatyzacji odpowiedzi w ticketach, analizy wiadomości i efektywnego zarządzania społecznością.

### 📸 Dowód Powstania (2023)
*(Zrzuty ekranu z eksploratora plików pokazujące daty modyfikacji i utworzenia plików w 2023 roku, przed obecną refaktoryzacją)*  
<p align="center">
  <img src="screenshot.png" alt="Dowód z 2023 r. - cz. 1" width="600"/>
  <br><br>
  <img src="screenshot2.png" alt="Dowód z 2023 r. - cz. 2" width="600"/>
</p>

### Główne Funkcje
- **🎫 Zaawansowany System Ticketów** - Tworzenie biletów pomocy (UI), ograniczenia ról, logowanie transkryptów i modularne przypisywanie operatorów.
- **🎨 Interaktywny Edytor Embedów** - Pozwala administratorom serwera na budowanie, edycję i wysyłanie całkowicie spersonalizowanych wiadomości embed bezpośrednio przez Modale w UI Discorda.
- **📊 Ankiety i Konkursy (Giveaways)** - Wysoce interaktywne i zautomatyzowane systemy głosowania oraz losowań.
- **📣 Promocje i Ogłoszenia** - Czasowe promocje automatycznie informujące użytkowników o rozpoczęciu i zakończeniu wyprzedaży.
- **🛡️ Bezpieczna Weryfikacja** - Modale weryfikacyjne z zadaniami matematycznymi w stylu Captcha, zatrzymujące podstawowe boty przed wejściem na serwer.
- **📝 Kompleksowe Logowanie** - Pełny nadzór nad edycjami wiadomości, ich usuwaniem, modyfikacjami kanałów, aktualizacjami uprawnień i wiele więcej.
- **🐳 Docker** - Dostarczany z plikiem `Dockerfile` dla natychmiastowych, zdalnych wdrożeń.

### 🐳 Wdrożenie (Produkcja z użyciem Dockera)
Najszybszym i najbardziej niezawodnym sposobem na hostowanie tego bota jest użycie Dockera.

1. **Skonfiguruj środowisko:** 
   Zmień nazwę pliku `.env.example` na `.env` (lub po prostu utwórz nowy plik `.env`) i uzupełnij swój `DISCORD_BOT_TOKEN` oraz ID kanałów.
2. **Zbuduj obraz Docker:**
   ```bash
   docker build -t staleforge-bot .
   ```
3. **Uruchom kontener w tle:**
   ```bash
   docker run -d --name my-discord-bot --env-file .env staleforge-bot
   ```
   *Aby sprawdzić logi kontenera, wpisz: `docker logs -f my-discord-bot`*

---
<div align="center">
  <b>staleforge.dev</b>
</div>
