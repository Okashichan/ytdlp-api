# ytdlp-api
Simple as **** yt-dlp API wrapper 

## Building

```
docker build -t ytdlp-api .
docker run -d -t --restart=always --name ytdlp-api -p 1337:1337 ytdlp-api
```