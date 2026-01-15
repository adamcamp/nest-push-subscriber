# Deprecated in favor of Go version which is about 10x faster https://github.com/adamcamp/camera-event-handler
# nest-push-subscriber
Pushes Nest events to OpenHAB

1. Create Pub/Sub subscription
2. Add OpenHAB item
3. Configure Cloudflare tunnel with zero trust service auth
4.  Create Cloud Run Function to subscribe to pub/sub and push to openhab
