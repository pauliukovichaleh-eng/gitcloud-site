// Usługa „Dyżurny admin” (decyzje #902, #903, nazwa #904): teksty strony /dyzurny/ w trzech językach.
// Cena ryczałtowa za zakres, bez stawki godzinowej. Przykład z życia tylko z własnej infrastruktury, bez nazw klientów i pracodawcy.
import type { Lang } from './index';

const pl = {
  name: 'Dyżurny admin',
  kw: 'nocny dyżur dla serwera Proxmox i OPNsense',
  crumb: 'usługi',
  tag: 'Usługa · abonament',
  lead: 'Dla małej firmy z serwerem Proxmox i zaporą OPNsense. Alarmy w nocy obsługuje program dyżurny: znane usterki naprawia sam, przed każdą zmianą robi kopię, a to, czego nie może rozstrzygnąć, wysyła mi jako kartę z wyborem na telefon.',
  status: 'Działa na mojej infrastrukturze od października 2026. Zestaw dla firm od 14 listopada 2026, instalacja sprawdzona na czystym Debianie 12',
  doH: 'Co robi',
  does: [
    ['Nocny dyżur', 'Alarmy Netdata: usługi hosta i maszyn, dyski, pamięć, restart po aktualizacji jądra, strony i certyfikaty. Każdy alarm ma przepis: co sprawdzić, co zrobić, kiedy uznać za naprawiony.'],
    ['Zabezpieczenie zmian', 'Przed zmianą kopia maszyny. Jeśli po zmianie usługa nie wstanie albo zniknie łączność, system sam wraca do stanu sprzed zmiany.'],
    ['Przegląd tygodniowy', 'Pakiety z lukami bezpieczeństwa, prognoza zajętości dysku i pamięci, usługi, które przestały działać, wiek kopii zapasowych.'],
    ['Decyzje kartą', 'Gdy przepis nie wystarcza albo zmiana jest ryzykowna, dostaję kartę: co się stało, co już zrobione, 2 do 4 możliwych kroków. Wybieram i odpowiadam za decyzję ja.'],
  ],
  next: 'Od listopada 2026 dyżurny obsługuje też alarmy z zapory OPNsense i błędy z dzienników Loki.',
  rulesH: 'Zasady dyżurnego',
  rules: [
    ['Sam', ['sprawdza alarm jeszcze raz na żywej metryce', 'restartuje usługę, która padła (poza siecią, SSH i klastrem Proxmox)', 'sprawdza usługi w maszynach Proxmox i na OPNsense', 'testuje strony, porty i certyfikaty']],
    ['Tylko w oknie nocnym', ['cięższe kroki, które mogą na chwilę przerwać pracę', 'okno ustalamy razem, domyślnie 02:00-05:00']],
    ['Tylko za zgodą', ['restart serwera po aktualizacji', 'ograniczanie maszyn, które zjadają pamięć', 'wszystko, czego przepis nie obejmuje']],
    ['Nigdy', ['nie usuwa danych', 'nie zmienia sieci ani zapory', 'nie dotyka kluczy i płatności', 'nie pisze do ludzi w Twoim imieniu']],
  ] as [string, string[]][],
  rulesNote: 'Przepis, który w ciągu doby dwa razy nie pomógł, nie jest powtarzany: sprawa trafia do mnie. Każdy krok zapisuje się w dzienniku na Twoim serwerze (90 dni).',
  repH: 'Raport co tydzień',
  repP: 'W poniedziałek o 7:00 przychodzi e-mail po polsku, na jedną stronę. Przykład:',
  repNote: 'Jeśli Netdata przestanie odpowiadać, dostaję wiadomość od razu, a raport mówi o przerwie wprost: tydzień bez przeglądów nie udaje spokojnego tygodnia.',
  shH: 'GitCloud Shield: tarcza w abonamencie',
  shP: 'Własny system bezpieczeństwa GitCloud, w cenie abonamentu. Sprawdza wiadomości i pocztę, zanim ktoś je otworzy, i ocenia bezpieczeństwo serwera w skali 0 do 100.',
  shDoes: [
    ['Poczta i komunikatory', 'Phishing, oszustwa („własny kurier”, płatność „przed wysyłką”, kod BLIK lub SMS), podróbki banków, OLX, InPost i gov.pl. Ostrzeżenie przychodzi bez treści i bez linków.'],
    ['Załączniki', '„faktura.pdf.exe”, programy, obrazy dysków, strony logowania, makra. Treść sprawdza antywirus ClamAV, zainfekowany plik trafia do kwarantanny.'],
    ['Blokada w sieci', '515 tys. domen phishingowych (CERT Polska i otwarte listy) zablokowanych na DNS zapory: fałszywa strona nie otworzy się na żadnym urządzeniu w firmie.'],
    ['Ocena 0 do 100', 'Zapora, fail2ban, integralność plików, kopie, aktualizacje i tarcza w jednym widoku z listą „do naprawy”. Spadek oceny to alarm dla dyżurnego.'],
  ],
  shStats: [
    ['515 tys.', 'domen phishingowych w blokadzie, aktualizacja co godzinę'],
    ['1 z 1057', 'wiadomości z miesiąca oznaczona jako groźna: prawdziwe oszustwo na OLX'],
  ],
  howH: 'Jak to działa',
  flow: [
    ['Alarm', 'Netdata wykrywa: usługa stoi, dysk się kończy, certyfikat wygasa.'],
    ['Dyżurny', 'Sprawdza metrykę jeszcze raz i dobiera przepis do alarmu.'],
    ['Działanie', 'Kopia, naprawa, kontrola. Brak poprawy oznacza cofnięcie.'],
    ['Karta na telefon', 'Co się stało, co zrobione, co wybrać dalej.'],
  ],
  flowAlt: 'Alarm bez przepisu albo zmiana bez możliwości cofnięcia: od razu karta do mnie, bez działania.',
  flowAria: 'Schemat: alarm, dyżurny, działanie, karta na telefon',
  stayH: 'Co zostaje u Ciebie',
  stay: [
    'Dyżurny to usługa systemd na Twoim serwerze, kod w Pythonie leży otwarty w /opt/dyzurny.',
    'Dane, dzienniki i kopie zostają na Twoim sprzęcie.',
    'Na zewnątrz wychodzą tylko e-maile: prośba o decyzję do mnie i raport tygodniowy do Ciebie.',
    'Ustawienia w jednym pliku: /etc/dyzurny/dyzurny.toml.',
    'Wyłączenie i usunięcie jednym poleceniem: install.sh --uninstall.',
  ],
  exH: 'Przykład z życia',
  exP: 'Środowisko: jeden serwer Proxmox z kontenerami i maszynami wirtualnymi, zapora OPNsense, monitoring Netdata. Stan na 12 listopada 2026:',
  exStats: [
    ['1', 'podsumowanie rano zamiast powiadomień w nocy'],
    ['02:00-05:00', 'okno aktualizacji i restartów, kontrola po każdym kroku'],
  ],
  exCases: [
    'Usługa nie wstała po aktualizacji: restart, kontrola metryki, alarm zamknięty bez budzenia kogokolwiek.',
    'Prognoza „dysk pełny za kilka dni”: dyżurny sprawdził miejsce od razu. To był chwilowy skok plików tymczasowych, miejsca było dość. Opisał to i niczego nie usuwał.',
    'Nowe jądro po aktualizacji: restart hosta tylko w oknie nocnym i za zgodą, potem kontrola, czy zamknięcie było czyste i czy usługi wróciły.',
  ],
  priceH: 'Cena',
  prices: [
    ['1500 zł', 'wdrożenie', 'Jeden serwer Proxmox i zapora OPNsense, tydzień konfiguracji i testów.'],
    ['390 zł / mies.', 'abonament', 'Dyżur, przeglądy tygodniowe i do 2 godzin pracy nad decyzjami w miesiącu.'],
    ['+150 zł / mies.', 'kolejny serwer', 'Każdy następny serwer pod tym samym dyżurem.'],
  ],
  priceNote: 'Cena stała za zakres, ustalona na piśmie przed startem. Umowa i faktura na życzenie.',
  startH: 'Jak zacząć',
  steps: [
    ['Napisz', 'Ile masz serwerów i co na nich działa.'],
    ['Diagnoza', 'Sprawdzam środowisko, cena i zakres na piśmie.'],
    ['Wdrożenie', 'Tydzień: instalacja zestawu w jeden wieczór, przepisy pod Twoje usługi, test alarmów.'],
    ['Abonament', 'Dyżur co noc, raport co tydzień.'],
  ],
  btn: 'Napisz wiadomość',
  copyAria: 'Skopiuj adres e-mail',
  faqH: 'Pytania',
  faq: [
    ['Co, jeśli dyżurny nie zna alarmu?', 'Nic nie zmienia, tylko wysyła mi kartę. Po rozwiązaniu dopisuję przepis, więc następnym razem poradzi sobie sam.'],
    ['Czy program może coś zepsuć?', 'Zasady są zapisane w kodzie: nie usuwa danych, nie zmienia sieci ani zapory, cięższe kroki tylko w oknie, restart serwera tylko za zgodą. Zmiany konfiguracji robię z kopią i automatycznym cofnięciem.'],
    ['Co, jeśli padnie sam monitoring?', 'Dyżurny sprawdza Netdatę przed każdym przeglądem. Gdy nie odpowiada, od razu dostaję e-mail, a raport tygodniowy pokazuje przerwę.'],
    ['Czy to zastępuje kopie zapasowe?', 'Nie. Przegląd sprawdza, czy kopie są świeże, a ich brak jest alarmem.'],
    ['Czy wszystko odbywa się zdalnie?', 'Tak. Nie wykonuję napraw sprzętu ani wizyt na miejscu.'],
  ],
  back: 'Strona główna',
  more: 'Usługa dyżurnego admina',
};
type D = typeof pl;

const en: D = {
  name: 'On-call admin',
  kw: 'night duty for a Proxmox and OPNsense server',
  crumb: 'services',
  tag: 'Service · subscription',
  lead: 'For a small business running a Proxmox server and an OPNsense firewall. Night alarms are handled by an on-call program: it fixes known faults by itself, takes a copy before every change, and sends me whatever it cannot settle as a card with options on my phone.',
  status: 'Running on my own infrastructure since October 2026. Package for businesses since 14 November 2026, install tested on a clean Debian 12',
  doH: 'What it does',
  does: [
    ['Night duty', 'Netdata alarms: host and guest services, disks, memory, reboot after a kernel update, websites and certificates. Every alarm has a recipe: what to check, what to do, when it counts as fixed.'],
    ['Safe changes', 'A copy of the machine before a change. If the service does not come back or the connection drops after it, the system returns to the state before the change by itself.'],
    ['Weekly review', 'Packages with security vulnerabilities, disk and memory forecast, services that stopped working, age of backups.'],
    ['Decisions by card', 'When a recipe is not enough or a change is risky, I get a card: what happened, what is already done, 2 to 4 possible steps. I choose and I am responsible for the decision.'],
  ],
  next: 'Since November 2026 the on-call program also handles alarms from the OPNsense firewall and errors from Loki logs.',
  rulesH: 'Rules of the on-call program',
  rules: [
    ['By itself', ['re-checks the alarm against the live metric', 'restarts a failed service (except networking, SSH and the Proxmox cluster)', 'checks services inside Proxmox machines and on OPNsense', 'tests websites, ports and certificates']],
    ['Only in the night window', ['heavier steps that may briefly interrupt work', 'we set the window together, 02:00-05:00 by default']],
    ['Only with consent', ['server reboot after an update', 'limiting machines that eat memory', 'anything a recipe does not cover']],
    ['Never', ['does not delete data', 'does not change the network or firewall', 'does not touch keys or payments', 'does not write to people on your behalf']],
  ],
  rulesNote: 'A recipe that failed twice within a day is not repeated: the case comes to me. Every step is written to a log on your server (90 days).',
  repH: 'A report every week',
  repP: 'On Monday at 7:00 you get a one-page e-mail in Polish. Example:',
  repNote: 'If Netdata stops responding, I get a message straight away and the report says so plainly: a week without checks does not pretend to be a quiet week.',
  shH: 'GitCloud Shield: included in the subscription',
  shP: 'GitCloud’s own security system, included in the subscription. It checks messages and mail before anyone opens them and scores server security from 0 to 100.',
  shDoes: [
    ['Mail and messengers', 'Phishing, scams (“my own courier”, payment “before shipping”, BLIK or SMS codes), fake banks, OLX, InPost and gov.pl. The warning arrives without the text and without links.'],
    ['Attachments', '“invoice.pdf.exe”, programs, disk images, login pages, macros. Contents are scanned by ClamAV, an infected file goes to quarantine.'],
    ['Network block', '515k phishing domains (CERT Polska and open lists) blocked on the firewall DNS: a fake site will not open on any device in the company.'],
    ['Score 0 to 100', 'Firewall, fail2ban, file integrity, backups, updates and the shield in one view with a “to fix” list. A falling score is an alarm for the on-call program.'],
  ],
  shStats: [
    ['515k', 'phishing domains blocked, updated hourly'],
    ['1 of 1057', 'messages from a month flagged as dangerous: a real OLX scam'],
  ],
  howH: 'How it works',
  flow: [
    ['Alarm', 'Netdata detects it: a service is down, a disk is filling up, a certificate expires.'],
    ['On-call', 'Checks the metric again and picks the recipe for the alarm.'],
    ['Action', 'Copy, fix, check. No improvement means rollback.'],
    ['Card on the phone', 'What happened, what was done, what to choose next.'],
  ],
  flowAlt: 'An alarm without a recipe, or a change that cannot be rolled back: a card goes straight to me, no action taken.',
  flowAria: 'Diagram: alarm, on-call, action, card on the phone',
  stayH: 'What stays with you',
  stay: [
    'The on-call program is a systemd service on your server, its Python code lies open in /opt/dyzurny.',
    'Data, logs and backups stay on your hardware.',
    'Only e-mails leave the network: a decision request to me and the weekly report to you.',
    'Settings in one file: /etc/dyzurny/dyzurny.toml.',
    'Switched off and removed with one command: install.sh --uninstall.',
  ],
  exH: 'A real example',
  exP: 'Environment: one Proxmox server with containers and virtual machines, an OPNsense firewall, Netdata monitoring. As of 12 November 2026:',
  exStats: [
    ['1', 'summary in the morning instead of notifications at night'],
    ['02:00-05:00', 'update and reboot window, a check after every step'],
  ],
  exCases: [
    'A service did not start after an update: restart, metric check, alarm closed without waking anyone.',
    'Forecast "disk full in a few days": the on-call program checked free space right away. It was a short spike of temporary files and there was enough space. It reported this and deleted nothing.',
    'A new kernel after an update: host reboot only in the night window and with consent, then a check that the shutdown was clean and services came back.',
  ],
  priceH: 'Price',
  prices: [
    ['1500 PLN', 'setup', 'One Proxmox server and an OPNsense firewall, a week of configuration and testing.'],
    ['390 PLN / month', 'subscription', 'Night duty, weekly reviews and up to 2 hours of work on decisions per month.'],
    ['+150 PLN / month', 'each extra server', 'Every further server under the same duty.'],
  ],
  priceNote: 'A fixed price for the scope, agreed in writing before the start. Contract and invoice on request.',
  startH: 'How to start',
  steps: [
    ['Write', 'How many servers you have and what runs on them.'],
    ['Assessment', 'I check the environment, price and scope in writing.'],
    ['Setup', 'One week: the package installs in one evening, then recipes for your services and alarm tests.'],
    ['Subscription', 'Duty every night, a report every week.'],
  ],
  btn: 'Send a message',
  copyAria: 'Copy e-mail address',
  faqH: 'Questions',
  faq: [
    ['What if the on-call program does not know the alarm?', 'It changes nothing and sends me a card. Once solved, I add a recipe, so next time it handles it by itself.'],
    ['Can the program break something?', 'The rules are written in the code: it does not delete data or change the network or firewall, heavier steps run only in the window, a server reboot only with consent. Configuration changes I make with a copy and automatic rollback.'],
    ['What if monitoring itself goes down?', 'The on-call program checks Netdata before every run. If it does not respond, I get an e-mail straight away and the weekly report shows the gap.'],
    ['Does it replace backups?', 'No. The review checks that backups are fresh, and a missing one is an alarm.'],
    ['Is everything done remotely?', 'Yes. I do not do hardware repairs or on-site visits.'],
  ],
  back: 'Home page',
  more: 'On-call admin service',
};

const ru: D = {
  name: 'Дежурный админ',
  kw: 'ночное дежурство для сервера Proxmox и OPNsense',
  crumb: 'услуги',
  tag: 'Услуга · абонемент',
  lead: 'Для небольшой фирмы с сервером Proxmox и шлюзом OPNsense. Ночные тревоги разбирает дежурная программа: известные сбои чинит сама, перед каждой правкой делает копию, а то, что решить не может, присылает мне карточкой с вариантами на телефон.',
  status: 'Работает на моей инфраструктуре с октября 2026. Набор для фирм с 14 ноября 2026, установка проверена на чистом Debian 12',
  doH: 'Что делает',
  does: [
    ['Ночное дежурство', 'Тревоги Netdata: службы хоста и машин, диски, память, перезагрузка после обновления ядра, сайты и сертификаты. На каждую тревогу есть рецепт: что проверить, что сделать, когда считать исправленным.'],
    ['Страховка изменений', 'Перед правкой копия машины. Если после неё служба не поднялась или пропала связь, система сама возвращается к состоянию до правки.'],
    ['Недельная ревизия', 'Пакеты с уязвимостями, прогноз диска и памяти, службы, которые перестали работать, возраст резервных копий.'],
    ['Решения карточкой', 'Когда рецепта мало или правка рискованная, мне приходит карточка: что случилось, что уже сделано, 2-4 возможных шага. Выбираю и отвечаю за решение я.'],
  ],
  next: 'С ноября 2026 дежурный обрабатывает и тревоги шлюза OPNsense, и ошибки из журналов Loki.',
  rulesH: 'Правила дежурного',
  rules: [
    ['Сам', ['ещё раз проверяет тревогу по живой метрике', 'перезапускает упавшую службу (кроме сети, SSH и кластера Proxmox)', 'проверяет службы в машинах Proxmox и на OPNsense', 'проверяет сайты, порты и сертификаты']],
    ['Только в ночном окне', ['тяжёлые шаги, которые могут ненадолго прервать работу', 'окно согласуем вместе, по умолчанию 02:00-05:00']],
    ['Только с согласия', ['перезагрузка сервера после обновления', 'урезание машин, которые съедают память', 'всё, чего нет в рецепте']],
    ['Никогда', ['не удаляет данные', 'не меняет сеть и файрвол', 'не трогает ключи и платежи', 'не пишет людям от вашего имени']],
  ],
  rulesNote: 'Рецепт, который за сутки дважды не помог, не повторяется: дело переходит ко мне. Каждый шаг записывается в журнал на вашем сервере (90 дней).',
  repH: 'Отчёт каждую неделю',
  repP: 'В понедельник в 7:00 приходит письмо на польском, на одну страницу. Пример:',
  repNote: 'Если Netdata перестанет отвечать, мне сразу приходит письмо, а отчёт прямо говорит о перерыве: неделя без проверок не выдаёт себя за спокойную.',
  shH: 'GitCloud Shield: щит в абонементе',
  shP: 'Своя система безопасности GitCloud, входит в абонемент. Проверяет сообщения и почту до того, как их откроют, и оценивает безопасность сервера от 0 до 100.',
  shDoes: [
    ['Почта и мессенджеры', 'Фишинг, мошенники («свой курьер», оплата «до отправки», код BLIK или SMS), подделки банков, OLX, InPost и gov.pl. Предупреждение приходит без текста и без ссылок.'],
    ['Вложения', '«faktura.pdf.exe», программы, образы дисков, страницы входа, макросы. Содержимое проверяет антивирус ClamAV, заражённый файл уходит в карантин.'],
    ['Блок в сети', '515 тыс. фишинговых доменов (CERT Polska и открытые списки) закрыты на DNS шлюза: поддельный сайт не откроется ни на одном устройстве фирмы.'],
    ['Оценка 0 до 100', 'Файрвол, fail2ban, целостность файлов, копии, обновления и щит на одной странице со списком «исправить». Падение оценки становится тревогой для дежурного.'],
  ],
  shStats: [
    ['515 тыс.', 'фишинговых доменов в блоке, обновление раз в час'],
    ['1 из 1057', 'сообщений за месяц помечено опасным: настоящее мошенничество на OLX'],
  ],
  howH: 'Как это работает',
  flow: [
    ['Тревога', 'Netdata видит: служба стоит, диск кончается, сертификат истекает.'],
    ['Дежурный', 'Ещё раз проверяет метрику и подбирает рецепт к тревоге.'],
    ['Действие', 'Копия, починка, проверка. Нет улучшения, значит откат.'],
    ['Карточка на телефон', 'Что случилось, что сделано, что выбрать дальше.'],
  ],
  flowAlt: 'Тревога без рецепта или правка без возможности отката: сразу карточка мне, без действий.',
  flowAria: 'Схема: тревога, дежурный, действие, карточка на телефон',
  stayH: 'Что остаётся у вас',
  stay: [
    'Дежурный работает службой systemd на вашем сервере, его код на Python лежит открыто в /opt/dyzurny.',
    'Данные, журналы и копии остаются на вашем железе.',
    'Наружу уходят только письма: просьба о решении мне и недельный отчёт вам.',
    'Настройки в одном файле: /etc/dyzurny/dyzurny.toml.',
    'Отключение и удаление одной командой: install.sh --uninstall.',
  ],
  exH: 'Пример из жизни',
  exP: 'Среда: один сервер Proxmox с контейнерами и виртуальными машинами, шлюз OPNsense, мониторинг Netdata. На 12 ноября 2026:',
  exStats: [
    ['1', 'сводка утром вместо уведомлений ночью'],
    ['02:00-05:00', 'окно обновлений и перезагрузок, проверка после каждого шага'],
  ],
  exCases: [
    'Служба не поднялась после обновления: перезапуск, проверка метрики, тревога закрыта, никого не будили.',
    'Прогноз «диск заполнится через несколько дней»: дежурный сразу проверил место. Это был короткий всплеск временных файлов, места хватало. Он описал это и ничего не удалял.',
    'Новое ядро после обновления: перезагрузка хоста только в ночном окне и с согласия, затем проверка, что выключение было штатным и службы вернулись.',
  ],
  priceH: 'Цена',
  prices: [
    ['1500 zł', 'внедрение', 'Один сервер Proxmox и шлюз OPNsense, неделя настройки и проверок.'],
    ['390 zł / мес.', 'абонемент', 'Дежурство, недельные ревизии и до 2 часов работы над решениями в месяц.'],
    ['+150 zł / мес.', 'следующий сервер', 'Каждый следующий сервер под тем же дежурством.'],
  ],
  priceNote: 'Фиксированная цена за объём, письменно до начала работы. Договор и счёт по запросу.',
  startH: 'Как начать',
  steps: [
    ['Напишите', 'Сколько у вас серверов и что на них работает.'],
    ['Диагностика', 'Смотрю среду, цена и объём письменно.'],
    ['Внедрение', 'Неделя: набор ставится за один вечер, потом рецепты под ваши службы и проверка тревог.'],
    ['Абонемент', 'Дежурство каждую ночь, отчёт каждую неделю.'],
  ],
  btn: 'Написать',
  copyAria: 'Скопировать адрес почты',
  faqH: 'Вопросы',
  faq: [
    ['Что, если дежурный не знает тревогу?', 'Ничего не меняет, только присылает мне карточку. После решения я дописываю рецепт, и в следующий раз он справится сам.'],
    ['Может ли программа что-то сломать?', 'Правила записаны в коде: не удаляет данные, не меняет сеть и файрвол, тяжёлые шаги только в окне, перезагрузка сервера только с согласия. Правки настроек я делаю с копией и автоматическим откатом.'],
    ['Что, если упадёт сам мониторинг?', 'Дежурный проверяет Netdata перед каждым прогоном. Если она не отвечает, мне сразу приходит письмо, а недельный отчёт показывает перерыв.'],
    ['Это заменяет резервные копии?', 'Нет. Ревизия проверяет, что копии свежие, а отсутствие копии само по себе тревога.'],
    ['Всё делается удалённо?', 'Да. Ремонт железа и выезды не делаю.'],
  ],
  back: 'Главная',
  more: 'Услуга «Дежурный админ»',
};

export const DYZ: Record<Lang, D> = { pl, en, ru };

// Przykład tygodniowego e-maila: wynik gitcloud-core gitcloud_core/dyzurny/report.py 1:1 (zawsze po polsku).
// 672 = 7 dni × 96 przeglądów (co 15 min).
export const DYZ_REPORT = `Dyżurny admin · raport · Firma Przykład · serwer pve1 · 07.11-14.11.2026

W skrócie: 672 przeglądy, alarmów: 3, zamknięte bez Państwa udziału: 2, czeka na decyzję: 1.

Czeka na decyzję:
• ram_available: czeka na decyzję (od 13.11 22:05)

Co się działo:
• 09.11 03:12 systemd_service_unit_failed_state: restart usługi → rozwiązane
• 11.11 14:40 disk_space_usage: kontrola miejsca na dysku → sprawdzone, bez zagrożenia`;
export const dyzPath = (l: Lang) => (l === 'pl' ? '/dyzurny/' : `/${l}/dyzurny/`);
