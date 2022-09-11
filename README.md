# Exchange To Google Calendar sync tool
This tool allows to sync calendar events between Exchange calendar and Google Calendar


## Running from Docker 

```shell
docker run --rm -it --env EXCHANGE_EMAIL=<your@email.com> --env EXCHANGE_PASS=<your_password> --network=host -v $(pwd):/app/ andrewshipilo/exchange-to-gcal:latest
```


