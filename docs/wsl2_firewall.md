

```shell
iex "New-NetFireWallRule -DisplayName 'WSL 2 Firewall Unlock' -Direction Outbound -LocalPort 3306 -Action Allow -Protocol TCP";
iex "New-NetFireWallRule -DisplayName 'WSL 2 Firewall Unlock' -Direction Inbound -LocalPort 3306 -Action Allow -Protocol TCP";
netsh interface portproxy add v4tov4 listenport=3306 listenaddress=* connectport=3306 connectaddress=172.24.196.30
```
