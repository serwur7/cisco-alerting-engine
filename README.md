\# Cisco IOS XE Event-Driven Alerting Engine (mini-xMatters)



\## 1. Opis Projektu

Projekt realizuje zadanie z sekcji \*\*Monitoring i Analiza Sieci\*\* w ramach przedmiotu DevNet Cisco Associate. Narzędzie stanowi autonomiczny, bezagentowy system ciągłego monitorowania infrastruktury sieciowej (Network Observability Core). 



W nowoczesnych środowiskach NetDevOps, natychmiastowa informacja o awarii interfejsu (np. link-flap lub awaria sprzętowa) decyduje o dotrzymaniu umów SLA. Aplikacja eliminuje potrzebę manualnej weryfikacji stanu sieci lub podatnego na opóźnienia odpytywania SNMP. Wykorzystuje zaawansowany protokół \*\*RESTCONF\*\* oraz model danych \*\*IETF (ietf-interfaces)\*\* do wykrywania incydentów w czasie rzeczywistym i natychmiastowego eskalowania ich drogą mailową za pomocą protokołu \*\*SMTP\*\*.



\## 2. Architektura i Przepływ Danych (Dataflow)

1\. \*\*Pętla Monitorująca (Polling):\*\* Skrypt w zdefiniowanym interwale (domyślnie 30s) wysyła zapytania HTTP GET do interfejsu RESTCONF urządzenia Cisco.

2\. \*\*Analiza Stanu (State Management):\*\* Skrypt przechowuje stan interfejsów w pamięci lokalnej. Algorytm porównuje stan historyczny $T\_{-1}$ ze stanem aktualnym $T\_{0}$.

3\. \*\*Eskalacja (Alerting):\*\* W przypadku wykrycia przejścia interfejsu w stan `down`, uruchamiany jest wątek komunikacyjny ze strukturą serwerów SMTP, generujący dedykowaną depeszę alarmową o priorytecie CRITICAL.

4\. \*\*Logowanie (Persistence):\*\* Wszystkie zdarzenia (sukcesy, błędy połączeń, zmiany stanów) są asynchronicznie zapisywane do rotowanego pliku logów `network\_monitor.log`.



\## 3. Wykorzystane Technologie i API

\* \*\*Język programowania:\*\* Python 3.x

\* \*\*API Sieciowe:\*\* RESTCONF (Port TCP 443)

\* \*\*Model danych YANG:\*\* `ietf-interfaces:interfaces-state`

\* \*\*Protokół komunikacji alarmowej:\*\* SMTP ze wsparciem dla szyfrowania TLS

\* \*\*Środowisko testowe:\*\* Cisco DevNet Sandbox (Always-On IOS XE Recommended Track)



\## 4. Instalacja i Wdrożenie



\### Wymagania sprzętowo-programowe

\* Python 3.8 lub nowszy

\* Pakiet instalacyjny `pip`



\### Instrukcja krok po kroku

1\. Pobierz lub sklonuj zawartość folderu projektowego.

2\. Zainstaluj bibliotekę odpowiedzialną za obsługę zapytań HTTP API:

&#x20;  ```bash

&#x20;  pip install requests

