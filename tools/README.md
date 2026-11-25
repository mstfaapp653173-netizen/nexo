# NEXO auto video ads — playbook

Every run makes ONE brand-new vertical video ad (1080x1920, 30fps, ~50 s, owner's choice) for NEXO, posts it as a Reel
to the Facebook Page and Instagram, and logs it in `posted.log`.

## Brand (do not change)
- Colors: Deep Navy #050B1A (bg), Dark Navy #071326 (cards), Electric Blue #0066FF, Bright Cyan #00D4FF
  (accent words, brackets), Neon Purple #7B2CFF (gradients only), White #FFFFFF, Soft Blue Gray #A9B8CC.
- Style (from the reference video): dark bg with faint rotating rings, kinetic word-by-word captions with
  key words in cyan, one big white icon in the centre framed by cyan corner brackets, ruler/timer motif,
  cards sliding up, outro = NEXO wordmark wipe + thin cyan line + slogan word by word + CTA button
  "راسلنا هسه" + "WhatsApp  07751027553" + "nexodeveloper.net" + "Connect to the Future.".
- Hook (first 3 s): warm and friendly, never aggressive or shouting.
- Language: Iraqi dialect. NEVER mention prices, discounts or offers. Never invent stats or testimonials;
  any on-screen counter must be clearly illustrative.
- Services: AI sales employee bot (Messenger, Instagram, WhatsApp — replies in a second, answers questions,
  shows products, confirms orders, 24/7) and professional websites.

## Algorithm rules (Instagram + Facebook Reels)
- Length ~50 s (owner's requirement). Script 95–115 words. Keep it moving: a new visual every 2–4 s so viewers keep watching.
- First second must make a shop owner think "this is me" (friendly, never aggressive).
- End every video and caption with a send prompt, e.g. "دزه لصاحب محل تعرفه" (DM sends are the strongest signal).
- Caption: include natural search keywords (بوت رد تلقائي، موظف مبيعات ذكي، تصميم مواقع بالعراق، مطاعم، محلات).
- Original visuals, voice and music only.
- FIRST FRAME = COVER: Facebook uses frame 0 as the Reel thumbnail. Frame 0 must already show a strong title card
  (big headline + icon, fully visible, no fade-in from an empty background). Never start on an empty background.
  For Instagram also pass thumb_offset (ms) pointing at the most readable frame.
- NO BORDER: colour/texture must reach all four edges (style_ad.make_bg is full-bleed). No progress bars,
  frames or flat bands along the edges — Facebook's quality check flags them as "video has a border".
- Caption: 10–300 characters INCLUDING hashtags (Facebook's check wants 10–400; stay well under), at most 2 line
  breaks, max 2 emojis, 4–5 hashtags.
- Burned-in captions must be large and high-contrast for the whole video (Facebook favours captioned Reels).
- NEVER post the same video twice, never re-upload or re-post an earlier video, and never reuse an earlier
  script, hook or caption. Every run = brand-new script, new scenes, new caption. Check posted.log and the
  existing files in videos/ before writing.

## Font
Arabic text uses Cairo (tools/fonts, OFL licence): render.AR = Cairo-ExtraBold, AR_BLACK for big headlines, AR_REG = Cairo-SemiBold. Cairo has no ✓, text_img draws it with a fallback font automatically.

## Voice
ElevenLabs connector, voice "علي البزاز" voice_id `7GuGTyc18I5wWanLbbNq`, model `eleven_v4`,
generations_count 1, use creative_create_flow or the flow `OlAnO6Js6QgnCkILfpfC`.
Download content_url with curl (elevenlabsusercontent.com is allowed). Get phrase timings with
`ffmpeg -af silencedetect=n=-35dB:d=0.18`. Keep the script 95–115 words (≈800 credits).
Account is on the free tier (~10k credits/month): check `account_get_usage` first; if fewer than 900 credits
remain, skip the run and report it.
If a generation fails with "busy" (nothing is charged), wait 3 minutes and try again, up to 8 attempts.
If it is still busy, create a one-time scheduled task 1 hour later that repeats this whole run, and stop.

## Ready queue
If `queue/` holds a finished video (`queue/nexo-ad-N.mp4` + `queue/nexo-ad-N.txt` caption) that is NOT in
posted.log, publish that one instead of making a new video: move it to `videos/`, post it with its caption,
log it, and delete it from queue/.

## Rendering
`tools/` holds the helpers: `render.py` (text/gradient/rounded/place/easing), `style_ad.py`
(background rings, brackets, word captions, chat/bot/site icons), `ad50.py` + `ad50b.py` (full 50 s example
with hook, phone chat demo, timer, platforms, website cards, 3 steps, outro), `music.py`
(`python3 music.py <seconds> out.wav` — original light beat). Write a new scene script per concept
(import helpers from these files), render frames to ffmpeg (libx264 -preset veryfast -crf 19 yuv420p),
then mix: music at ~0.32 ducked with sidechaincompress under the voice, light pops/whooshes, alimiter.
Check a contact sheet of frames before posting (text must not overlap, must fit the width).

## Publish
1. Commit the mp4 to `videos/nexo-ad-N.mp4` in this repo and push to `main`
   (`git -c push.negotiate=true push origin HEAD`). Wait ~90 s for GitHub Pages.
2. Public URL: `https://mstfaapp653173-netizen.github.io/nexo/videos/nexo-ad-N.mp4`
   If GitHub Pages deploy fails/404s (happened 2026-11-25), use the raw URL instead — it worked for IG, FB and Buffer:
   `https://raw.githubusercontent.com/mstfaapp653173-netizen/nexo/main/videos/nexo-ad-N.mp4`.
   Check the latest "pages build and deployment" run right after pushing, not at publish time.
3. Windsor connector:
   - Instagram `create_video_post`, account `17841480845121566`, share_to_feed true, caption.
   - Facebook `create_reel`, account `1354552747749075`, description = same caption.
4. Caption: written fresh each time in Iraqi dialect, 3–5 short lines, one emoji per line at most,
   soft CTA (راسلنا / جرّب البوت), 5–7 hashtags incl. #نيكسو #NEXO. No prices.
5. Append a line to `posted.log`: date | N | concept | ig media id | fb post id.

## Concept rotation (pick the next one not yet in posted.log; after 10, start again with fresh angles)
1. قصة زبون الساعة 2 بالليل
2. قبل وبعد: صفحة بدون بوت وصفحة ويا البوت
3. محادثة حقيقية ويا البوت خطوة بخطوة
4. 3 أخطاء تخسّرك زبائن
5. شنو الفرق بين صفحة فيسبوك وموقع؟
6. يوم بحياة صاحب مطعم
7. تحدي الثانية: منو يرد أسرع؟
8. موقعك هو محلك اللي ما يسكّر
9. أسئلة الزبائن المتكررة والبوت يجاوبها
10. كيف تبدي ويا NEXO بـ 3 خطوات

# Image posts (days without a video)
On days with no video, one brand-new image post (1080x1350 JPEG, 4:5) goes to the Facebook Page and Instagram.
- Same brand rules as above: NEXO colors, Cairo font, Iraqi dialect, NO prices/discounts/offers, no invented stats
  or testimonials, soft CTA + send prompt ("دزّ البوست لصاحب محل تعرفه") in the caption.
- Quality bar: `tools/post_example_features.py` (neon pill poster, devices, feature list, categories, CTA, trust
  badges) and `tools/post_example_chat.py`. Every element must fit inside its box; check the rendered JPEG before posting.
- EVERY post must differ from all previous ones in BOTH idea and layout. Check `tools/posted_images.log`.
  Never re-post an image, never reuse a headline or caption.
- Ready queue first: if `queue_images/` holds a JPEG + .txt caption not yet in posted_images.log, post that one.

Idea rotation (one per post, then invent new angles):
1. Features poster  2. One big question in huge type ("زبونك راسلك وما رديت؟")  3. Real-looking chat mockup
4. Before / after split  5. Checklist: "محلك يحتاج بوت إذا…"  6. Myth vs fact  7. 3 steps to start
8. Industry card: restaurants  9. Industry card: clothing shops  10. Website mockup showcase
11. Comparison: employee vs AI sales bot (no prices)  12. FAQ card (common questions answered)
13. Industry card: salons  14. "Your shop never closes" night scene  15. Tip card: how to reply faster to customers

Layout styles (rotate, never the same as the previous post): neon pill poster; minimal giant typography;
split screen; device-mockup hero; card grid; diagonal ribbons; vertical timeline; big centered icon in brackets;
chat-bubble collage; table/comparison board.

Publish: commit to `images/nexo-post-N.jpg`, push, wait ~90 s, URL
`https://mstfaapp653173-netizen.github.io/nexo/images/nexo-post-N.jpg`.
Instagram `create_image_post` (account 17841480845121566, image_url, caption) and Facebook `create_photo_post`
(account 1354552747749075, image_url, caption). Retry a failed publish after 2 minutes, up to 3 times.
Append: date | N | idea | layout | ig media id | fb post id to tools/posted_images.log.

# TikTok (via the Buffer connector)
**VIDEOS ONLY on TikTok** — owner said image posts do NOT go to TikTok (Instagram + Facebook only).
Buffer organization "My organization" id `6b0667492579815fa19d025f`, TikTok channel "nexodevloper" id
`6b0667f28541f09ecb96f105`. Publish every video there too, right after Facebook/Instagram:
`create_post` with channelId above, schedulingType "automatic", mode "shareNow", assets = [{video:{url, metadata:{thumbnailOffset:0}}}]
metadata.tiktok = {title (short, Arabic), isAiGenerated: true}.
TikTok caption: shorter than the Facebook one (max ~150 chars before hashtags), same rules (Iraqi dialect, no prices),
send prompt, 5–7 hashtags incl. #نيكسو #NEXO and one broad tag like #fyp. Check the post with get_post after ~2 minutes;
status "sent" = done, "error" = retry once after 2 minutes. Log the Buffer post id in the log line.
Free Buffer plan: max 10 scheduled posts at once — always use shareNow, never fill the queue.

# DAILY SCHEDULE (owner's instruction, 2026-11-25) — supersedes "every 2 days" / "days without a video"
- Image post EVERY DAY at 10:00 AM Baghdad → Instagram + Facebook only.
- Reel EVERY DAY at 8:00 PM Baghdad → Instagram + Facebook + TikTok.
- Never late: content is prepared a day ahead by the nightly prep task (~9:15 PM) into `queue/` (nexo-ad-N.mp4 + .txt)
  and `queue_images/` (nexo-post-N.jpg + .txt). The 10 AM / 8 PM tasks ONLY publish the oldest ready item.
- Each .txt: line 1 = "concept: ... | layout: ...", then the FB/IG caption, then a line `TIKTOK:` followed by the short TikTok caption (videos only).
- Keep at least 1 video and 2 images ready in the queues at all times.
