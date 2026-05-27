# Keep-Warm Configuration For Render Free Tier

Render's free tier sleeps after 15 minutes of idle. First request after sleep takes ~30 seconds to wake — Retell webhooks would time out (10s default). Fix: ping `/health` every 10 minutes to keep the service awake.

## Option 1: cron-job.org (Recommended — Free, No Account Bloat)

1. Go to https://cron-job.org → sign up (free)
2. Create new cronjob:
   - **Title**: Sterling Legal Webhook Keep-Warm
   - **URL**: `https://voice-team-webhook.onrender.com/health`
   - **Schedule**: Every 10 minutes
   - **Save**

Render service stays warm 24/7 for free. cron-job.org sends a GET to `/health` every 10 min, your webhook responds instantly with `{"ok": true}`, sleep timer resets.

## Option 2: UptimeRobot (Same Idea, Different UX)

https://uptimerobot.com → free tier supports 5-min interval pings. Same result.

## Option 3: Skip Keep-Warm

If your call volume is low (1-2/day during demo), Retell's retry logic catches most cases. The first call after a long quiet stretch may have a 30-60 second delay before calendar + email land. Subsequent calls in the same hour are instant.

## When To Upgrade To Render Starter ($7/mo)

Once you have 2+ paying clients, the $7/mo Starter plan eliminates sleep entirely. At that point you're earning $1000+/mo from the factory — the $7 is rounding error. Until then, free + keep-warm is fine.

## Verification

After setting up the cronjob, check Render's dashboard:
- Should see a `/health` request every 10 min
- Service status: "Live" (never "Sleeping")

If you see sleeps anyway, double-check the cronjob URL matches your actual Render service URL.
