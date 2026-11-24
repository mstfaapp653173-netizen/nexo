# NEXO auto video ads — playbook

Every run makes ONE brand-new vertical video ad (1080x1920, 30fps, 25–35 s) for NEXO, posts it as a Reel
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
- Length 25–35 s (completion rate matters most). Script 45–65 words.
- First second must make a shop owner think "this is me" (friendly, never aggressive).
- End every video and caption with a send prompt, e.g. "دزه لصاحب محل تعرفه" (DM sends are the strongest signal).
- Caption: include natural search keywords (بوت رد تلقائي، موظف مبيعات ذكي، تصميم مواقع بالعراق، مطاعم، محلات).
- Original visuals, voice and music only.
- NEVER post the same video twice, never re-upload or re-post an earlier video, and never reuse an earlier
  script, hook or caption. Every run = brand-new script, new scenes, new caption. Check posted.log and the
  existing files in videos/ before writing.

## Voice
ElevenLabs connector, voice "علي البزاز" voice_id `7GuGTyc18I5wWanLbbNq`, model `eleven_v4`,
generations_count 1, use creative_create_flow or the flow `OlAnO6Js6QgnCkILfpfC`.
Download content_url with curl (elevenlabsusercontent.com is allowed). Get phrase timings with
`ffmpeg -af silencedetect=n=-35dB:d=0.18`. Keep the script 45–65 words (≈600 credits max).
Account is on the free tier (~10k credits/month): check `account_get_usage` first; if fewer than 900 credits
remain, skip the run and report it.

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
