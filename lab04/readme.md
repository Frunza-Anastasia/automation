Care sunt avantajele utilizării Jenkins pentru automatizarea sarcinilor DevOps?

Jenkins este gratuit și open source și are foarte multe pluginuri, de exemplu pentru Git, Docker sau Kubernetes. Pașii de lucru se scriu într-un fișier Jenkinsfile, care se păstrează în repository împreună cu codul. Așa procesul poate fi refăcut oricând, la fel. Jenkins poate rula testele automat la fiecare modificare a codului, așa că erorile se găsesc repede. De asemenea, poate împărți munca între mai mulți agenți cu medii diferite și poate fi instalat oriunde: pe un server, în Docker sau în cloud.

Ce alte tipuri de agenți Jenkins există?

Pe lângă agenții SSH, folosiți în acest laborator, există agenți inbound (JNLP), care se conectează singuri la controller prin portul 50000. Există și agenți Docker, unde pentru fiecare build se creează un container temporar, și agenți Kubernetes, unde fiecare build rulează într-un pod separat. Mai sunt agenții cloud, adică mașini virtuale create la cerere în AWS, Azure sau Google Cloud, și agenții Windows. Build-urile se pot rula și pe nodul integrat, adică pe controller, dar asta nu este recomandat.

Ce probleme ați întâmpinat la configurarea Jenkins și cum le-ați rezolvat?

Prima problemă a fost că în Ubuntu din WSL comanda docker nu exista, așa că am instalat Docker. Apoi am primit eroarea „permission denied” la conectarea la Docker. Am rezolvat-o adăugând utilizatorul în grupul docker.

Cea mai mare problemă a fost că agentul rămânea offline cu eroarea „Name or service not known”. Am descoperit că în browser nu vedeam Jenkins-ul din container, ci un Jenkins mai vechi, instalat direct în Ubuntu, care ocupa portul 8080. L-am oprit cu systemctl stop jenkins și systemctl disable jenkins, apoi am configurat Jenkins-ul corect.

Altă problemă a fost că Jenkins nu accepta cheia privată SSH (eroarea „PEM problem”). Am generat o cheie nouă de tip RSA în format PEM și am adăugat-o din nou în credentials.

Am mai avut probleme și cu git push, pentru că GitHub nu mai acceptă parola contului. Am rezolvat prin configurarea unei chei SSH în contul GitHub.
