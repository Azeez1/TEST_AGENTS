"""Build PDF from cleaned slide images + copy Monday LinkedIn post to clipboard."""
import os, glob, re, subprocess
import img2pdf

SRC_DIR = r'C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\tmp_slides_cleaned'
OUT_PDF = r'C:\Users\sabaa\ONEDRIVE\DESKTOP\TEST_AGENTS\MARKETING_TEAM\outputs\social_media\natural_body_teardown_carousel.pdf'
KEEP = [1, 4, 5, 6, 8, 10, 13, 14]

def nat_key(p):
    m = re.search(r'(\d+)', os.path.basename(p))
    return int(m.group(1)) if m else 0

paths = sorted(glob.glob(os.path.join(SRC_DIR, 'image*.png')), key=nat_key)
paths = [p for p in paths if nat_key(p) in KEEP]
paths.sort(key=lambda p: KEEP.index(nat_key(p)))

with open(OUT_PDF, 'wb') as f:
    f.write(img2pdf.convert(paths))
print(f'PDF built: {OUT_PDF} ({os.path.getsize(OUT_PDF)/1024/1024:.1f} MB, {len(paths)} pages)')

POST = """Most "hidden revenue" content is a scam.

So I tested it. Publicly.

I spent a weekend tearing down a $3M med spa chain using only data anyone can pull off Google. Then I sent the analysis to the owner.

No invoice. No login. No conversation with them before I did it.

What I found was roughly $500K in hidden annual revenue sitting inside a business that already looks successful on every scoreboard that matters.

6 locations across Atlanta. Best of Georgia 2025. First LED Platinum-certified spa in the U.S. A brand people drive across town to visit.

And three operational gaps quietly leaking the kind of money most owners chase with ad spend.

Gap 1 \u2014 Rebooking.
Top-performing med spa clinics rebook 68% of patients automatically. Industry average sits at 38%. The math on a predictable Botox cycle (3\u20134 months) and facial cycle (monthly) means every dormant patient represents recurring revenue that walks itself back in \u2014 but only if the system remembers to ask.

Gap 2 \u2014 Cross-Location Intelligence.
When your day spa client in Marietta doesn't know your med spa in Alpharetta exists, you didn't lose a sale. You built the bridge and forgot to light it. 15 minutes of drive time separates a $40 facial from a $1,500 annual med spa LTV.

Gap 3 \u2014 Reputation at Scale.
80% of med spa patients read reviews before booking. One unanswered negative review on the wrong location becomes the deciding factor for a prospect who was two clicks from converting. Six locations means six digital storefronts that all need to tell the same story.

Total software cost to close all three: under $350 per month.
Total revenue protected and generated: north of $500K per year.

The uncomfortable part:
None of this required new marketing. None of it required a website rebuild. None of it required "AI transformation."

It required looking at the operation the way an outsider sees it \u2014 which is harder than it sounds when you built it yourself.

This is the analysis I run for free before I pitch anyone.
If I can find $500K in gaps from the outside, the inside view usually surfaces more.

If you run a multi-location operation and you've been too close to see the leaks \u2014 that's the job.

Eight slides below. Swipe."""

proc = subprocess.run(['clip'], input=POST.encode('utf-16-le'), shell=True)
print(f'Clipboard copy: {"OK" if proc.returncode == 0 else "FAILED"}')
print(f'Chars copied: {len(POST)}')
