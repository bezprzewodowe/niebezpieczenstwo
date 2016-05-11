### probe.py
parsuje pliki *.cap oraz *.pcap do bazy danych mysql (pliki w formacie *.pcapng można przerobić przy pomocy komendy `editcap -F libpcap -T ether a.pcapng a.pcap`)

### geo.py
pobiera pozycję GPS dla wcześniej pozyskanych (przy pomocy `probe.py`) SSIDów za pośrednictwem serwisu wigle.net, a następnie również ustala fizyczne adresy za pomocą maps.google.pl

### probe.php
skrypt do prezentacji treści z bazy danych
