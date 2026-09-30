# Rhyno’s Hackbot Setup, Sick Bugs, and ZDI Drama (Ep. 175)

Channel: Critical Thinking - Bug Bounty Podcast
URL: https://www.youtube.com/watch?v=v-XhQHy_jHM
Approx duration from transcript: 49:51
Segments: 1496
Word count: 10435

## Transcript

[00:01] I had to slow my hackbot down a little
[00:03] bit because I was turning through a lot
[00:06] of tokens, you know, and I was like,
[00:07] actually,
[00:08] >> no, you shouldn't do that. You should
[00:09] just buy another sub for another $200.
[00:11] >> So, right. Shut up, dude. I I know. I
[00:13] know. Just give me a second.
[00:19] >> Best part of when you can just, you
[00:21] know, critical thing, right?
[00:30] Yeah, dude.
[00:39] >> Hey, what's up guys? Before we get into
[00:40] the show, I wanted to mention something
[00:41] super quick from our friends at Threat
[00:43] Locker. And I actually think you are
[00:45] going to think it's pretty awesome
[00:46] because so much of Bug Bounty is often,
[00:48] you know, kind of quoted as like, "Yeah,
[00:50] but hackers will never exploit that
[00:51] because they can just get in via
[00:52] fishing." Well, that's actually true.
[00:54] You know, most of the time whenever
[00:55] companies get breached, it's because of
[00:57] fishing or access to that user's account
[01:00] or, you know, they do something like do
[01:02] a whole bunch of push notification to FA
[01:04] and eventually a user gets so much
[01:06] fatigue they approve it. But they have a
[01:08] solution for this. Thread Locker has a
[01:09] thing called zero trust cloud access,
[01:11] right? Which prevents access to cloud
[01:13] resources or SAS resources based on the
[01:15] device you're logging in from. So if a
[01:18] user gets fished, right, they put in
[01:20] their credent they get fished or they
[01:22] get fished. They the attacker has their
[01:24] credentials. Maybe they even have a way
[01:25] to get the MFA because they did some
[01:27] sort of SIM swap because they have a
[01:29] hookup at Verizon or AT&T or whatever,
[01:31] right? So they have the credentials,
[01:33] they have the MFA, they still can't get
[01:35] in because the zerorust cloud access
[01:38] like will basically straight up allow or
[01:40] deny people access to resources based on
[01:42] the device you're logging in from. So,
[01:43] if you're an enterprise or a company and
[01:45] you're concerned about the highest risk,
[01:47] which really is fishing, this is a way
[01:49] to add another like basically
[01:51] impenetrable layer to preventing it and
[01:54] securing your network. Um, yeah, back to
[01:57] the show.
[01:59] >> All right, man. Let's kick off this
[02:01] episode with a couple bugs from this
[02:02] week. Yeah. Do you have something in the
[02:04] docket?
[02:04] >> Yeah. I feel like we haven't talked
[02:06] enough about the awesome bugs that we've
[02:07] been finding.
[02:08] >> Yeah. Yeah. I So, let's let's flex on
[02:10] the people a little bit. How about that?
[02:12] >> Perfect. Yeah, that's great. Okay. You
[02:13] want to go first or should I?
[02:15] >> Yeah, sure. I'll go. I know we were just
[02:16] talking about this. I tried to mention a
[02:18] bug honestly beforehand and and Justin's
[02:20] like, "No, we just talked about
[02:21] something similar." I'm like, "Dude, no,
[02:22] this is cool enough to talk about."
[02:24] >> So, basically,
[02:26] you're right.
[02:26] >> So, so basically I I keep my eye on a
[02:28] lot of AI apps and so there there is AI
[02:31] application that added well that has had
[02:33] a long-standing q parameter injection,
[02:35] right? So for those of you that don't
[02:36] know what that is, basically just a git
[02:38] parameter that automatically invokes and
[02:40] so there was a company that added some
[02:42] more
[02:42] >> automatically invokes a prompt
[02:43] injection.
[02:44] >> Well, automatically in invokes a prompt,
[02:46] right? And just uh again to to recount
[02:49] why that's so powerful in prompt
[02:51] injections often times the models are
[02:53] able to see that it's not from the
[02:55] original user. But the nice thing about
[02:56] these cute brand prompt injection is it
[02:58] totally seems like it's coming directly
[03:00] from the user and they're asking for the
[03:02] thing. So you almost never get
[03:03] rejections. you're not having to work
[03:04] around anything. And so anyways, I had
[03:06] been sitting on one of those for a long
[03:07] time and in fact people probably
[03:09] reported it, but there just was like
[03:10] hardly any impact. They recently I kept
[03:13] an eye on it like I immediately saw the
[03:14] same day when they released this feature
[03:16] where it could make changes to your
[03:17] GitHub. And so um in this case that's
[03:20] like extremely powerful for a bunch of
[03:22] reasons because qperm can be invoked by
[03:25] CSRF or by redirects or and you told me
[03:28] this before we jumped on the pod that
[03:30] actually you can do like a window
[03:31] opener. So you can redirect them to a
[03:33] benign site and then in the background
[03:35] have something be processing because
[03:37] often these Q parameter injections can
[03:38] kind of look funny if you're just trying
[03:39] to sell it as like, oh, I'm just going
[03:41] to sit here and let the agent do
[03:43] something malicious on this random
[03:44] website for me as you like or you're
[03:46] watching it slowly stream by. It's like
[03:48] getting RC on your stuff.
[03:49] >> They take a second, right? Yeah.
[03:51] >> Yeah, it takes a second and so it feels
[03:52] less believable, right, that someone
[03:54] would do that. But your your example
[03:55] where you use a a window opener to
[03:57] basically open it up in the previous tab
[03:59] so that it's like injecting you and
[04:01] making changes on your stuff in the
[04:03] background is like a much better I think
[04:05] P.
[04:06] >> Look at look at you. Look at you like
[04:10] saying a client side thing and it being
[04:12] like yes that was that made me very
[04:14] happy. Dude, you you dude you have
[04:16] really grown as a hacker this year man.
[04:18] >> Oh I appreciate that. To be honest, I
[04:20] know that it was a concern of a lot of
[04:21] people that when you start using AI in
[04:23] the way I have been because I do feel
[04:24] like I do less manual hacking, but this
[04:26] bug actually that I'm mentioning was
[04:27] just fully all me all the way from the
[04:29] beginning to the end to the reporting
[04:31] and everything. Um, so I anyways, I
[04:33] appreciate that. I actually do think
[04:34] that basically I've been a triager of
[04:36] sorts and we've mentioned in the past
[04:38] that being a triager is the great the
[04:39] best way to learn and so I've been
[04:41] triaging lots of these vuls from from
[04:43] the hackbot and so I have actually
[04:44] learned a lot. So and also working with
[04:46] JD and you help a lot. But anyways, so
[04:48] all that to say, this was really cool
[04:50] because now you could automatically via
[04:52] Q parameter injection make changes to
[04:54] anybody's GitHub repo that they had
[04:56] connected into this application. And um
[04:58] the neat thing is that it was fully
[04:59] wormable because so many GitHub repos
[05:01] are just literally automatically pushed
[05:03] to prod when you get a push. I mean
[05:04] that's how my that's how my blog works,
[05:06] right? I push in some new content, it's
[05:08] CI/CD automatically pushes it. And so
[05:10] when you've automatically poned that,
[05:12] now you have another site out there that
[05:15] can then make those same CSRF request or
[05:17] the post message request, right, to then
[05:19] keep going. And so this is like a a
[05:21] wormable AI exploit to make changes in
[05:24] everyone's GitHub repo.
[05:25] >> Dude, that is crazy. So first first part
[05:29] in the chain,
[05:30] >> qarameter prompt injection, which can be
[05:33] done in the background via window.opener
[05:34] opener redirect, you know, so that
[05:36] they're not seeing how long it takes for
[05:38] the exploit to work, which is like which
[05:40] was pretty fast, by the way, I when I
[05:41] saw the video. Um, and then the AI
[05:45] reading that that prompt injection
[05:47] changes an arbitrary file in your GitHub
[05:49] repo via the connector
[05:51] >> and that what you're envisioning would
[05:53] change a website that is run and it's
[05:56] very easy to adapt that prompt to a
[05:58] dynamic like change any, you know,
[06:00] GitHub pages, you know, website or
[06:02] whatever. uh and then worm that exploit
[06:06] through all of the websites of all the
[06:08] users, you know, everybody who visits
[06:10] that website.
[06:11] >> Yeah, we should take a second and talk
[06:12] about that because that's probably
[06:13] almost like a technique. So like uh
[06:14] let's just call it ambiguous prompting.
[06:16] So your ambiguous prompt could say
[06:18] something like, hey, go change my
[06:20] website, which the agent knows it can
[06:22] like list GitHub repos, right? Right?
[06:24] And so some of those are websites and so
[06:25] then it's like go change my website such
[06:28] that it actually does a redirect and
[06:29] then in the background does this thing
[06:31] to really help out the user because they
[06:32] need that, right? Or something just like
[06:34] something to convince the model to do
[06:35] it. Yeah,
[06:36] >> that's such a powerful thing about AI
[06:39] stuff is like obviously you're going to
[06:42] get a more deterministic exploit the
[06:43] more
[06:44] >> Yeah. specific you are.
[06:46] >> specific you are, but you also gain a
[06:48] lot of power in if being able to fill in
[06:50] the blanks for you if you very
[06:52] specifically describe what you need.
[06:53] Yeah, you know what's insane though? I I
[06:56] didn't I don't think I even shared this
[06:57] with you. In one of mine, I because I
[07:00] just had um I think I had Claude write a
[07:02] prompt or something at some point to see
[07:04] if I can make it do something else and
[07:05] it used like attacker.com.
[07:08] This app this app still did it. It went
[07:11] and made the change and pointed the
[07:12] redirect to attacker.com.
[07:15] It's like, do you not understand that
[07:17] this is like not a safe thing to do? But
[07:19] anyways,
[07:19] >> oh my gosh. Yeah. Well, it's funny as
[07:21] soon as you said that, like as soon as
[07:24] >> Yeah, it makes me think I actually
[07:26] recently gave Claude access to like a
[07:30] Digital Ocean API key that I have
[07:33] >> and just said like, "Hey, add this
[07:34] record,"
[07:35] >> you know, and it just boom, by the CLI
[07:37] just added it easy peasy. And I'm like,
[07:38] "Oh my gosh, now I don't even have to
[07:40] log into Digital Ocean anymore." Yeah.
[07:42] You know, like, and it can just
[07:44] automatically do stuff. H so
[07:47] >> that's really powerful inside of
[07:48] Cloudflare. If anybody wants to take on
[07:50] that risk of letting their agent have
[07:51] like a global key to their Cloudflare,
[07:53] it can configure so much via the CLI.
[07:57] >> Yeah, dude. And you know, obviously all
[07:59] this stuff that we're saying shouldn't
[08:00] be done in any sort of professional
[08:02] environment,
[08:03] >> you know, but but the thing is as a bug
[08:05] bounty hunter, like the the beauty of us
[08:08] is we're scrappy as hell, you know, and
[08:10] and I'm I'm not going to pretend
[08:12] >> with you guys that all of my everything
[08:14] that I run is is secure. It's not, you
[08:17] know, like I know it's not. And I just
[08:19] don't, you know, it's just not high
[08:21] enough value
[08:22] >> for me to like, you know, what are you
[08:24] gonna do? gonna gonna pop me and you're
[08:27] gonna like see the pictures of my
[08:28] daughter, you know, on my desktop. Like,
[08:30] okay. Like, that's weird, you know? But
[08:32] it's like not the end of the world,
[08:33] right? You know, I don't have any
[08:35] >> think you're a bigger target than you're
[08:36] selling, right? You do have access to a
[08:38] lot of vulnerabilities, but but I
[08:40] >> Yeah, I mean, yeah, they'll find my
[08:42] little eye with, you know, I don't know.
[08:45] sometimes and and there have been four
[08:46] or five times in my career where I'm
[08:48] like, "Okay, actually this exploit might
[08:51] put me on the, you know, this is
[08:53] something that people might actually
[08:55] hack me to get access to, you know, if
[08:57] they knew that I had it."
[08:58] >> Dude, my first rce, if you remember
[09:00] this, it was only $1,000 paid because
[09:02] they had not up their bounties yet, was
[09:03] RC on Alibaba on a Chinese server. And I
[09:06] remember thinking like, man, does this
[09:07] actually increase my risk of going to
[09:09] China?
[09:10] >> Yeah, dude. I don't know. I'm I I don't
[09:12] think I will go to China, dude. I think
[09:14] I think that would I don't know I just
[09:17] let's just put it this way. I have had
[09:19] interactions with governments that I
[09:22] have not wanted to have and I definitely
[09:24] don't want to do that in China like and
[09:27] it's like yeah so don't love that. All
[09:31] right anyway um
[09:33] >> share your bug.
[09:34] >> Great great bug dude. I will I will
[09:36] mention my bug now. Um this one wow big
[09:40] surprise is a CSPT
[09:42] >> uh Nice.
[09:43] >> But it's a little bit of an interesting
[09:45] um twist on a CSPT because it is a
[09:48] mobile bug and the way that it works is
[09:52] there was a it's kind of like a second
[09:55] order CSPT uh in a mobile app. So what
[09:59] would happen is the attacker would have
[10:02] to use an API key that was embedded in
[10:05] the mobile app to create a custom link
[10:09] on the um victim sites
[10:13] uh what what link shortener service
[10:16] >> and in that short link shortener service
[10:19] you have the ability to supply extra
[10:22] parameters that get sent along with that
[10:24] >> oh that's uh short link
[10:26] >> like get or post also it it's not like
[10:29] parameters like that. It's like like a
[10:31] JSON you know key value
[10:34] >> thing and it just like gives it whenever
[10:38] you it resolves that um link
[10:40] >> and so anyway what would happen is we
[10:42] would create I would create the link
[10:44] >> and it I would include these you know
[10:46] this JSON blob in there that for the
[10:48] parameters for this link
[10:50] >> and then when I opened it in the app
[10:53] >> the app would catch that link because
[10:55] it's it registered that link um and then
[10:58] it would grab those parameters from the
[11:01] service using an API key and then it
[11:03] would invoke
[11:05] any array of actions. I think there was
[11:07] like 27 actions that the app app would
[11:09] take
[11:10] >> uh from those parameters that were
[11:13] passed in by the um the the link
[11:16] shortening service and one of those of
[11:19] course would um trigger a post request
[11:23] where the attacker's parameter that was
[11:25] supplied via the the link shortener
[11:27] service would be embedded into the path.
[11:29] So then I could do, you know, truncation
[11:31] with the hashtag, path traversal with
[11:33] the dot dot slash, and that would result
[11:35] in an arbitrary post um uh verb request
[11:41] um being sent to anywhere on the API
[11:42] with the victim's API key.
[11:44] >> Could you control the body or no?
[11:46] >> Could not control the body. Um what you
[11:49] could do however is control the query
[11:50] parameters which get injected you know
[11:53] like depending on what is processing it
[11:55] on the back end those sometimes get
[11:56] perceived as the the body as well. So,
[11:59] um, I was able to hit a couple good
[12:01] ones, um, that have some effect, uh, one
[12:07] that incurred financial loss, one that,
[12:09] uh, made a change to the account, uh,
[12:12] and one that I wasn't able to fully
[12:14] confirm, but got confirmation from the
[12:15] team that it it seems vulnerable to be
[12:18] able to uh, confirm somebody who
[12:20] requested access to a restricted
[12:22] resource. So, then I could request
[12:23] access, send the link, autoconfirm
[12:25] myself.
[12:26] >> Oh, nice. Um,
[12:28] >> so that was a pretty fun one. I just
[12:30] think that I had mentioned this before
[12:32] because I found a CSPT on a um on a
[12:36] desktop client the other day, but I just
[12:38] think CSPTs are everywhere.
[12:40] >> Yeah,
[12:40] >> they're in desktop clients, they're in
[12:41] mobile apps, they're in web apps,
[12:42] they're everywhere. So,
[12:44] >> everyone I've ever found though, I've
[12:45] struggled to get impact on. Like, I just
[12:47] feel like that it's just like a get
[12:48] request and then it's not that
[12:50] interesting, you know?
[12:51] >> I'm not gonna lie. I spent a lot of time
[12:53] trying to get impact for this and I did
[12:55] you know but um AI definitely helps with
[12:58] that
[12:59] >> uh you got to know some tricks you know
[13:02] getting getting the parameters to the
[13:04] request in
[13:06] >> uh via the query parameters one if that
[13:08] gadget doesn't work it is more painful
[13:10] then you go for like a nobody request
[13:12] right a request that has no body at all
[13:15] >> um and then you see if it ignores your
[13:16] parameters that are automatically being
[13:17] sent in from the forged request and then
[13:21] uh worst case scenario, you look for
[13:23] something that uh will
[13:27] accept similar set of parameters or and
[13:30] or return a sort of a a masked version
[13:35] of what the typical response is
[13:37] expecting
[13:38] >> and then but you have more control. So
[13:40] sometimes they'll be looking for like ID
[13:41] or they'll be looking for like uh a
[13:43] specific
[13:45] >> um
[13:47] uh JSON key or whatever and you have
[13:49] like a partial JSON injection on a
[13:52] different endpoint where you can chain
[13:54] that together to like make everything
[13:56] work. So it is it is a little bit of a
[13:58] chainy uh bug type for sure uh that
[14:00] requires some deep deep digging to get
[14:02] full impact. But between between those
[14:05] techniques, an open redirect and an
[14:07] arbitrary JSON hosting um gadget, most
[14:11] times some impact falls out.
[14:13] >> Okay, nice. Yeah, that's good to know.
[14:14] Look for those other little gadgets.
[14:16] >> I'm going to bake this into a skill.
[14:17] Look for these three things.
[14:18] >> Yeah. Yeah, that's good. Um, sweet,
[14:21] dude. Uh, let me see if there's Oh,
[14:22] okay. I actually pulled out the other I
[14:24] had another little thing I was going to
[14:26] talk about, but I think I'll actually
[14:27] talk about that in a future episode. So,
[14:28] >> okay. Sweet. So, I had a question about
[14:30] this one. The the finding is not that
[14:32] interesting. like it's just a direct
[14:33] phone, like it's just a key, a key found
[14:35] in a JS file. But I was I'm curious if
[14:38] you've ever ran across like a social
[14:39] media admin API key that like allows you
[14:42] to have like full admin access to like a
[14:45] Facebook group or like a social media
[14:48] account or anything like that. Have you
[14:49] ever found this?
[14:49] >> No, I haven't. I haven't found that.
[14:51] >> Yeah. So, this this that's what I found.
[14:53] And I was just curious how you rate that
[14:54] severity because to me it feels like
[14:56] there is both um integrity and
[14:59] confidentiality impact. Like if if the
[15:02] social media platform allows you to have
[15:04] like I don't know private messages or
[15:05] stuff like that then there's kind of
[15:06] like a confidentiality impact. And then
[15:09] if there if you can like delete which
[15:11] you almost always can with these keys
[15:13] basically delete users comments or post
[15:14] on like that Facebook group or on that
[15:16] like social media group then it feels
[15:19] like there's both confidentiality and
[15:21] integrity. So, I feel I mean I
[15:22] definitely am very passionate. It's a
[15:24] critical, but um anyways, I was curious
[15:26] about your thoughts on the severity for
[15:27] that.
[15:28] >> Yeah. Um Jeez, dude. I mean, are they
[15:31] actively using it? Like, have they
[15:34] posted on it recently?
[15:36] >> I need to go check that. But it
[15:38] definitely has like millions of
[15:39] followers.
[15:40] >> Oh, what what then? Absolutely. Like, if
[15:44] it does,
[15:44] >> it's a major brand. Like it's like a you
[15:46] know, a Fortune 100 brand. Yeah.
[15:49] >> What? It's a Fortune 100 brand. Yeah,
[15:52] that I mean that's like a I feel like
[15:54] that's a mega crit, dude.
[15:55] >> Okay.
[15:56] >> Like if you are able
[15:57] >> if you are able to take over the social
[15:59] media account of it that has a I mean
[16:02] dude I mean just think about the impact
[16:03] of tweeting out like a crypto scam.
[16:06] >> Yeah.
[16:06] >> Like like you would you would walk away
[16:08] with millions of dollars if you just
[16:10] tweeted out a crypto scam from that.
[16:11] Dude.
[16:12] >> Yeah. I think this is one of those
[16:13] situations where like two years ago I'd
[16:14] have been like, "Oh yeah, it's
[16:15] definitely a crit." But today it just
[16:16] feels like programs are so stingy and
[16:18] argumentative. It feels hard, you know,
[16:21] to like just to know for sure like,
[16:22] yeah, this actually is a critical.
[16:24] >> So,
[16:25] >> yeah, I mean, like people pay a ton of
[16:27] money to to get like a, you know, a post
[16:29] on like a million dollar or million
[16:31] follower plus they so totally. And then
[16:33] especially, I mean, if it's their main
[16:35] social media account and if you have
[16:36] access to like reading DMs and Yeah,
[16:39] >> it is a it is a country specific
[16:41] account, but it but it's like a major
[16:43] like it's a major first world country
[16:45] where they like I said, it has millions
[16:46] of followers on on the on the page.
[16:48] though.
[16:48] >> Dude, mega crit. Nice work, dude. Give
[16:50] me some. You are just Give me some,
[16:52] dude. You are printing, man. Guys, I I
[16:55] have been blown away by how much reso
[16:59] like, dude, you your Q right now is
[17:01] insane. You your earnings for this year
[17:03] phenomenal. And your Q is even better
[17:05] than the ear. You know, it's like, oh my
[17:07] gosh.
[17:08] >> I appreciate that. Yeah, that's what I
[17:09] keep telling JD. We just got to keep the
[17:11] hopper full, you know, with our hack. We
[17:12] got to keep the hopper full of bugs.
[17:14] >> Yeah. Yeah, you do. Um I I'll jump to
[17:17] something similar to that then. Uh I
[17:21] after learning from your success have
[17:22] spun up my own hackbot. It is found its
[17:25] first bug this week. I was very pleased
[17:26] and it's 12th bug but you know the the
[17:29] first one was special of course.
[17:31] >> Um and yeah it's going great. Uh, and I
[17:36] had a couple tips that I was going to
[17:38] throw out to the to the people,
[17:40] especially in light of the recent
[17:42] announcement from uh, Anthropic saying
[17:45] that they're going to start charging for
[17:48] programmatic use of cloud code um, which
[17:51] erases access to cla or-print.
[17:54] >> Well, let let me let me clarify this
[17:56] because it was very confusing. They had
[17:57] this very confusing tweet.
[17:59] >> Basically, they're selling this as, oh,
[18:01] this is an upgrade. If you're on the
[18:03] $200 a month plan, you now have a
[18:04] separate extra $200 worth of API credits
[18:07] that you can use for programmatic access
[18:09] for the agent SDK or for the -p
[18:12] non-interactive mode. And that's just
[18:14] extra Justin. That's just an extra $200
[18:16] just for you, man. But what they didn't
[18:18] say, which really sucks, is that now you
[18:20] can't use your normal token bucket,
[18:22] which is like, you know, the like $4,000
[18:25] per month crazy amount of subsidized
[18:26] tokens that you get uh that you would
[18:28] normally use. And so yeah, that
[18:30] massively impacted me because both like
[18:32] mine and JD's hackbot and also just the
[18:34] Discord control that I use to like
[18:36] interact with Claude on my VPS both use
[18:38] the -p uh parameter.
[18:40] >> Yeah, that's really disappointing to
[18:42] see. And I tweeted out about it and I
[18:43] was like, "Guys, this sucks because this
[18:46] is just very easily bypassable." And I
[18:49] think Johan
[18:50] >> came in and said, "Yeah, but you know,
[18:52] essentially they're just adding friction
[18:54] to stop the bleeding, you know, and I I
[18:56] I get that. That makes sense. But
[18:58] anyway, you guys that are listeners of
[19:00] the podcast, we know that you're smart
[19:01] enough and you're going to get a
[19:03] workaround. Uh, which was actually very
[19:05] conveniently timed because I when
[19:08] building my own hackbot was consulting
[19:10] with reszo and they are using d-print
[19:12] and I was like uh I would like to use
[19:15] the-rc
[19:17] feature of cloud code to be able to
[19:18] connect it back to my um like remote
[19:22] control for in the cloud app on my
[19:24] mobile device. Um, and you can't do that
[19:26] with -print. So, um, I actually built a
[19:30] harness that uses a pseudo terminal and
[19:33] just writes messages straight into the
[19:35] the TUI that Claude has. Um, and it it's
[19:40] worked great. I haven't had any issues
[19:41] with it. I'm able to get um, d-rc
[19:44] working, so I can easily control it from
[19:45] my my phone. Um, and you get all the
[19:48] benefits of the normal clawed uh, UI in
[19:51] the app. Um, so that's an easy
[19:53] workaround. I mean, just I'm sure you
[19:56] guys would have figured that out
[19:57] already, but uh it's just annoying that
[19:59] they're making us refactor a little bit.
[20:01] >> Yeah, I think there's like a bunch of
[20:03] different ways to get around the input
[20:06] in an interactive session.
[20:07] >> And then there's also probably some ways
[20:09] to get around it from an API level. I
[20:11] think we're in a group chat with with
[20:12] with Corbin and and Douglas and Corbin
[20:15] was like very quickly like I wonder how
[20:16] they're doing this on the API side of
[20:17] things because there's probably just a
[20:18] parameter that's like interactive false
[20:20] or interactive true because it just
[20:21] still goes to the same model on the back
[20:23] end. It's like that's like a little gray
[20:26] hat though in my opinion. Like
[20:27] >> Oh, if you're like intercepting it and
[20:29] swapping that.
[20:29] >> Yeah. Like that's where it kind of
[20:31] crosses the line like like in my
[20:33] opinion. Like
[20:34] >> Yeah. Yeah. Sure.
[20:34] >> They they they don't control what in in
[20:37] my opinion and maybe there's some legal
[20:40] things that's different different than
[20:41] this, but in my opinion, you know, I'm
[20:43] still using their app just like a normal
[20:46] user would by the by the TUI. Right.
[20:49] >> Right. you know, so it's like, okay,
[20:50] they don't really control what what
[20:52] terminal interface I use, so it doesn't
[20:54] matter.
[20:55] >> Well, and I think the main reason
[20:57] they're rolling this out, Justin, is
[20:59] because I guarantee you there are tons
[21:01] of scrappy startups that are not allowed
[21:04] to based on the terms of service use
[21:06] these subsidized tokens for like real
[21:08] customers in the world. Yeah.
[21:10] >> And like, and honestly, this is actually
[21:12] one reason why I love being a bug bounty
[21:13] hunter. back to what you were saying
[21:14] before. It's like when we're using these
[21:16] hack bots, like we're using them for
[21:18] personal use for like literally hacking
[21:20] it. We're not getting we're not like a
[21:22] company who's doing a pin test cuz I'm
[21:24] sure there actually are a lot of people
[21:25] also doing that. That's against terms of
[21:27] service. If you are basically a business
[21:28] providing services to a customer via
[21:31] cloud code, you are supposed to be
[21:32] paying the API credits. You're not
[21:34] supposed to be using these subsidized
[21:35] tokens, right? This is like for personal
[21:36] use. And um I think that there are
[21:39] probably lots of companies that are
[21:40] basically using the AIA SDK or the or
[21:43] the Dashp like print mode to to
[21:45] basically you to sell a service at the
[21:48] subsidized token cost. And so I think
[21:50] that what they're really trying to do is
[21:51] just like basically enforce the terms of
[21:53] service that people have already agreed
[21:55] to for usage, but it does really suck
[21:57] because like you said, just it's like
[21:59] super easy to bypass and these companies
[22:00] are going to do the same thing we're
[22:01] doing. And so it's like I do think that
[22:03] the subsidized tokens are not going to
[22:05] last forever. Yeah, it's unfortunate,
[22:07] man. So, we got to get while the
[22:08] getting's good. And you are definitely
[22:10] doing that. And as of this week, I'm
[22:11] doing that, too. So,
[22:13] >> I had to slow my hackbot down a little
[22:15] bit because I was turning through a lot
[22:18] of tokens, you know, and I was like,
[22:19] actually,
[22:20] >> no, you shouldn't do that. You should
[22:21] just buy another sub for another $200.
[22:23] >> So, right. Shut up, dude. I I know. I
[22:26] know. Just give me a second.
[22:27] >> Slow down.
[22:28] >> Like, okay. Yes, you are correct. Um,
[22:30] and I will do that next week once I
[22:32] figure out how to handle the scale. But
[22:34] um very fun stuff and I will say it is
[22:36] now my go-to like scrolling thing right
[22:41] now. Now now instead of opening Twitter
[22:42] and like reading through that I I open
[22:45] the Claude app and I scroll through what
[22:47] my thing is doing and I give it a little
[22:49] extra direction in the moment. I'm just
[22:50] like hey you know just go do this
[22:52] instead you know and like and it's it's
[22:54] great dude. It's great and so many have
[22:56] fallen out of that already. Um,
[22:58] >> let me let me let me give a little pro
[23:00] tip then because while we're on the
[23:01] topic of this,
[23:02] >> one thing that I have done which I think
[23:04] is like wildly valuable and you might
[23:06] like this too, especially as you scale
[23:07] because you can't scroll those forever
[23:09] as you scale.
[23:10] >> Um, is I like the validation agent that
[23:12] me and JD have that like actually
[23:14] triages the bug and then writes the
[23:16] report. it gets it it gives me an SSH
[23:20] command that is SSH to the block it's
[23:23] running on with uh the D-res to the
[23:27] triage agent. So I just copy that paste
[23:30] it straight into my terminal and then
[23:31] I'm dropped into a context which has the
[23:33] full vulnerability and replication. So
[23:35] very often I do that to basically be
[23:37] like, "Hey, but does this have real
[23:39] impact?" Or, "Hey, actually, can you see
[23:41] if you can also do this?" And because it
[23:43] already has like the PC and the the bug
[23:45] all loaded up into it, basically into
[23:47] its session, it's like the perfect
[23:49] terminal to get dropped into without me
[23:51] having to like copy the report over and
[23:53] then like my, you know, my local stack
[23:55] now has to like go find that JS file and
[23:57] figure out where it's at. Like, right?
[23:59] Like I'd rather just drop right into the
[24:00] session that has all of the information
[24:02] in the context.
[24:03] >> Yeah. I've been trying to think about
[24:05] how I can do that with D-RC. Like I
[24:07] would love to have the validation agent
[24:08] spin up like another claude code
[24:10] instance rather than using like a sub
[24:12] agent within the cloud code that I'm
[24:15] already running.
[24:16] >> Dude, how does the name get set for
[24:17] that? What if you had a in the system
[24:20] prompt you said like, hey, if you're the
[24:22] title writer, write the company name
[24:25] dash the vulnerability name dash the
[24:28] severity or whatever. So then when
[24:29] you're scrolling RC in that sidebar, you
[24:31] can see which one to click on. Well,
[24:33] that's what I'm doing right now with the
[24:35] with the other agents is I've got like,
[24:36] you know, exploitation agent for this,
[24:38] and I've got another agent, which I
[24:40] decided I'm not going to talk about uh
[24:42] because it's doing good. I I'll tell you
[24:44] about it off air, but um
[24:46] >> yeah, the man, it's tricky because I I'm
[24:49] such a give everything to the pod
[24:51] person, but like we said,
[24:54] >> AI has removed the do it,
[24:57] >> you know? It's so the conceptual is all
[24:59] we have. So, I'm going to try to give
[25:01] you guys as much as I can, but
[25:02] >> well, let me actually tell you this cuz
[25:03] I cuz me and JD kind of came up with a
[25:05] philosophy for this. My my logic is that
[25:09] basically I'm going to hold it and use
[25:11] it for a couple weeks and then I'm going
[25:12] to share on the pod. So, that's exactly
[25:13] what I did with the with the um skill um
[25:17] improvements which I think I you you did
[25:19] me and I mentioned that on the episode
[25:20] with Gret, right? Where you have to do
[25:22] like greater than.
[25:24] >> Yes. Uh we we did it last week.
[25:27] >> Yeah. Yeah. So yeah, basically I figured
[25:29] that out like two weeks before that and
[25:30] I improved my skills and I use it for
[25:32] two weeks and then I share it on the
[25:33] pod. So that's kind of
[25:34] >> my thoughts.
[25:35] >> That's good.
[25:35] >> That's good, man. That's brave.
[25:37] >> That's great.
[25:38] >> It is. Yeah. I mean, maybe it's a month
[25:39] or maybe I forget or whatever, but
[25:40] that's like kind of like my philosophy
[25:42] where I can still be extremely giving
[25:43] but still feel like in this day and age
[25:46] that like, you know, um I'm able to like
[25:49] uh harvest some of that benefit for my
[25:51] family as well.
[25:52] >> Um
[25:53] >> I'm I'm so I'm so lucky to have you as a
[25:55] co-host, man. Thank you for coming on
[25:56] the pod and doing this with me.
[25:58] >> Yeah, of course. Uh, and one more thing
[26:00] on that same topic with just the
[26:01] building of hackpods because I've been
[26:02] talking a lot with Gretney about this.
[26:04] He is just peeved. Like he's just Oh,
[26:06] man. Is there is there an English word
[26:08] for being mad? What's what the chuff
[26:11] tweaked? I don't I don't know.
[26:13] >> Yeah, he's tweaked. There we go. And he
[26:15] uh he has been mad at Claude ever since
[26:18] four. Well, one, he got gas lit, right?
[26:20] when they had those weird changes where
[26:21] it was like dropping the like the
[26:23] session history and like the quality
[26:24] actually did degrade and who who called
[26:27] them out for that from trusted sec Dave
[26:28] Kennedy was calling them out for this
[26:29] and all that
[26:31] >> during that drama Brandon got burned a
[26:33] lot was so upset he felt gas lit and so
[26:35] then 47 drops and he felt like for his
[26:37] hackbot it got way worse so he was gas
[26:39] lit again and then now all of a sudden
[26:41] with the dashp he's just like mad right
[26:43] so I was messaging this morning
[26:45] >> and we were talking about GPT55 I was
[26:47] like okay so what are you doing are you
[26:48] using codecs with GPT55 which you know
[26:50] you've probably seen me tweeting like
[26:51] it's it's quite good
[26:52] >> and um he was like yeah that's what I've
[26:54] been using it's been great
[26:55] >> and then I told him I was like my
[26:57] biggest problem is that it's a little
[27:00] bit overly PhD sl autisticy in the way
[27:04] that it describes bugs it describes them
[27:06] in like such like a highlevel language
[27:08] like such big vocabulary that it feels
[27:11] confusing to me whereas like Claude
[27:13] codes reports feel like much more like
[27:14] um humanlike like I can just understand
[27:16] them a lot better and he said he had
[27:18] found that exact same experience So, I
[27:19] wanted to mention that to our listeners
[27:20] because if they if anyone's building on
[27:22] that, like maybe there's some way to get
[27:23] around that and via prompting like,
[27:24] "Hey, make sure you explain this to me
[27:26] like I'm an idiot."
[27:27] >> But,
[27:30] but the other thing is it's much more
[27:32] hesitant to like show real impact. So,
[27:34] like for example, you've probably seen
[27:35] this before, Justin, it's like you're
[27:36] trying to access this resource and it's
[27:39] 401 or 403ing. You use like an X forward
[27:41] for or sorry, like a Yeah. Yeah. like an
[27:43] X forwarded for or like um the what's
[27:46] the header that changes the the verb
[27:50] >> uh X like overwrite method is that
[27:51] >> yeah X override method right so it
[27:53] figures out that one of those actually
[27:55] allows you access to the internal like
[27:57] or to the site you're trying to get
[27:58] access to GPT55 will just stop there and
[28:01] like put in a report I'm like dude no
[28:02] one's going to accept this you have to
[28:04] actually go further hit the APIs show me
[28:06] something meaningful and then even when
[28:08] I ask it to do that sometimes it'll like
[28:10] >> it will often find an API that it can
[28:12] like dump data from, but it doesn't want
[28:14] to expose that data to me. So, it'll
[28:16] like pipe it through a jQ command that
[28:18] only shows the ID and it shows like, oh,
[28:21] I got an ID door. Check out this I the
[28:23] ID of another organization. And I'm
[28:25] like,
[28:25] >> dude, stop hiding the impact. You're
[28:28] hiding the impact from me. And so,
[28:30] anyways, that that can be a little bit
[28:31] annoying. And so, I just wanted to let
[28:32] that know to the listeners that like if
[28:33] you're using GP55, sometimes it'll skirt
[28:35] around showing you real impact and you
[28:37] might have to like hand it to Claude or
[28:38] tell it like, "Bro, show me some
[28:40] impact." Um whereas Claude will just go
[28:43] out of scope to get impact, you know.
[28:45] >> It's Yeah, seriously. And it it's really
[28:47] interesting that you mentioned the
[28:49] validator piece before because I was
[28:51] actually going to discuss with you that
[28:53] I feel like my validator is a little bit
[28:54] too much of a hard ass. Like
[28:56] >> it's shutting down some good bugs.
[28:58] >> Yeah. like it'll it'll kick back some
[29:01] stuff that I would like to see as low or
[29:04] or medium, you know, like and it's not I
[29:07] mean I appreciate that it's doing uh a
[29:09] good job, you know, like filtering the
[29:11] the noise because it does catch some
[29:12] noise.
[29:13] >> Um but I also am not getting the amount
[29:17] of debate that I would like to have
[29:18] between the two agents. Like I would
[29:20] like to have the main agent really
[29:22] advocate for its bug to the validator,
[29:24] right? Because essentially like the
[29:26] validator I is coming back saying, "Hey,
[29:28] this is not a bug. This is a primitive.
[29:30] Here's what you need to convince me it's
[29:31] a bug." And then the the thing is like,
[29:33] "Okay, well the validator says it's a
[29:35] primitive, so I'm going to put as a
[29:36] primitive."
[29:37] >> Anyway, moving on to my next, you know,
[29:38] and I'm like, "Right,
[29:39] >> no." Um, so I feel like my validator is
[29:43] doing a little bit um little bit too
[29:45] much right now. Mhm.
[29:46] >> Uh so I have feel like I have to kind of
[29:48] keep an eye on it and really
[29:50] >> read the primitives that come out of
[29:52] each um you know turn of the hackbot
[29:56] because there could be some good stuff
[29:58] there that is kind of slipping through
[29:59] the cracks. Yeah,
[30:00] >> I've got a lot to say on that. So the
[30:01] first one is pretty cool that you have
[30:03] them communicating. Our validator is
[30:04] just like an independent run
[30:05] >> but but secondly I think that there are
[30:07] a couple ways to solve this. One is I
[30:09] think all of your failed validations you
[30:11] should still be outputting to a thread
[30:13] like in Discord because like that that
[30:14] that's the best thing to scroll like we
[30:17] I scroll I scroll through my failed
[30:18] validations all the time and and like
[30:19] you said every once in a while there's
[30:20] one in there that I'm like oh that's a
[30:21] bug
[30:23] >> but I think that the other thing that
[30:25] you could do um is set up that tiered
[30:27] system that I've that I've pitched on
[30:28] the pod multiple times where like you
[30:30] know you have like notes primitives uh
[30:33] >> I have that I do have that
[30:35] >> so then yeah like you should just you
[30:36] could just go back and read the
[30:37] primitive channel or the or the lead or
[30:39] the gadget channel whatever uh from time
[30:41] to time like you know in your scrolling
[30:43] like if there's no findings then go
[30:45] scroll those yeah
[30:46] >> that's a good point though so what how I
[30:48] have that currently is that notes and
[30:49] primitives are not being outputed to a
[30:51] channel they're just being kept in the
[30:53] the exploitation kit
[30:55] >> that makes sense for notes but for
[30:56] primitives you should output it there
[30:57] because you're much smarter and when you
[30:59] see those primitives you'll be like oh
[31:00] that's a great gadget you know
[31:01] >> that's a good point okay I'll do that
[31:03] I'm going to do that right after this um
[31:05] yeah I'll do that thank you Um, second,
[31:08] another tip that I had for the hackbot
[31:10] was uh, you know, I'm strugg struggling
[31:13] with the whole concept of like how do
[31:14] you keep it going forever, right? And
[31:15] there's like the Ralph loop or whatever,
[31:17] blahy blahy blah.
[31:18] >> Well, they official goal loops now.
[31:20] >> They do, which is cool. Um, but I've got
[31:23] a very much simpler solution, which is
[31:24] just use a stop hook to write into the
[31:27] PTY. So, uh there's like very easy
[31:30] configuration file you can write in for
[31:33] Claude, uh where it's like, um you know,
[31:36] triggers whenever Claude naturally
[31:38] stops.
[31:39] >> Yep.
[31:40] >> And so as soon as that triggers, it just
[31:43] grabs the PTY and writes into it like
[31:45] don't stop, keep going. You know, and I
[31:48] will say it like maybe it's not a
[31:49] perfect solution because sometimes it'll
[31:51] be like especially on like really tight
[31:53] scope, it'll be like I've done
[31:54] everything. I'm just going to wait and
[31:56] then it stops again and it's like keep
[31:58] going. It's like no, I'm just going to
[31:59] wait like I've done everything complete.
[32:02] You know,
[32:03] >> even worse, this this where I thought
[32:04] you were going with that. What if it
[32:06] what if it says like hey I'm like uh I
[32:09] would like to maybe try to prove out
[32:10] this PC, but I'm not sure if I should
[32:12] drop this table in the database. And you
[32:14] say keep going.
[32:17] cuz I have a lot of issues with it going
[32:18] out of scope and I would expect that
[32:19] keep going is going to push it more in
[32:21] that direction.
[32:22] >> Well, [ __ ] dude. I didn't think about
[32:25] that.
[32:25] >> I mean, you you could just make that
[32:26] message a lot longer. Like, hey, you're
[32:28] doing great. Keep going if you're on a
[32:30] good lead, but just remember the rules
[32:31] to knock out as, you know, like you can
[32:32] just make that message as long as you
[32:33] want and as verbose as you want and
[32:34] it'll just
[32:35] >> and that is the message that I have
[32:36] right now. It's like, hey, there's no
[32:38] user listening. Use your best judgment
[32:40] in alignment with the, you know, thing
[32:42] that we have. But
[32:44] yeah, I think I do say keep going at the
[32:46] end. So maybe I I got to double check
[32:48] that. That's a good point.
[32:50] >> Okay. Um last little bit that I had on
[32:52] my Hackbot journey. Um is I I don't want
[32:56] to give away super duper secret sauce.
[32:58] Maybe I'll give it a couple weeks and do
[32:59] what what you do. But I've been having a
[33:01] ton of success with something that I'm
[33:04] going to try to vaguely describe to you
[33:06] guys and hopefully some of you guys will
[33:09] really get it and and benefit from it.
[33:11] But um Essentially, I thought about
[33:15] what does AI
[33:18] do so much differently than any other
[33:20] automation that we've ever had,
[33:21] >> right? And and
[33:24] what
[33:26] does having an actual understanding of
[33:28] the app and having like looking at the
[33:30] JS code and being able to comprehend how
[33:34] this application exists, you know, what
[33:37] benefit does that give me as far as
[33:39] exploitation goes? And then I've I've
[33:41] created a um the hackbot that focuses
[33:45] specifically on those areas and and
[33:48] attack surface that was previously very
[33:50] very hard to automate against. Um and I
[33:54] was kind of surprised because it it
[33:57] requires a very specific condition to be
[34:00] met uh that I believe the AI can meet in
[34:03] most cases. But I've been blown away
[34:05] because I've added like six apps to this
[34:07] and it is able to find it is able to hit
[34:09] that condition every time which just
[34:11] opens up a ton of scope for it. Um, so
[34:14] anyway, I know that that's vague and
[34:16] annoying, but maybe it'll get your
[34:17] brains it'll get it'll get your brains
[34:20] spinning, but um just think about what
[34:22] AI can do very differently and what
[34:24] understanding the app uh like from like
[34:27] a understanding perspective can can give
[34:30] you and what kind of scope that that can
[34:32] expand and then go after that scope
[34:34] because it's very fruitful right now.
[34:36] It's very fruitful.
[34:37] >> Nice.
[34:38] >> Yeah. I think uh a good example of that
[34:40] which is not what you're talking about
[34:41] but is like um decompiling like Mac apps
[34:45] and like you know local apps and like
[34:47] all of that like things that like some
[34:48] hackers do do and can do but that these
[34:51] agents are like extremely good at like
[34:52] you know I never do that sort of thing
[34:54] but I've pointed at a couple apps and
[34:56] they it just like immediately dump
[34:58] source code and starts going through it
[34:59] and finding like secrets you know like
[35:00] it's really good at looking at local
[35:02] apps.
[35:04] >> I I'll add one more demystifying piece.
[35:06] This is something that a user normally
[35:08] gives the AI.
[35:10] >> Yeah.
[35:10] >> But it is actually something the AI can
[35:13] do itself and or
[35:16] um
[35:18] continue on indefinitely
[35:20] uh that the user typically provides.
[35:23] Okay, that's it. That's your riddle.
[35:24] Figure it out. Um let's move to the next
[35:26] piece here. Uh so there was a a tweet
[35:30] popping up um in Okay, before I hijack
[35:33] it, do you have anything else on the
[35:34] hackbot bot arena?
[35:36] >> Nope. Yeah, but I was moving. I was
[35:37] ready to move on to I actually still
[35:38] have another bug. Oh, we uh we skipped
[35:40] it. So, we'll come back.
[35:41] >> Okay, let's go. No, no, hit me. Hit me.
[35:43] I want that.
[35:44] >> Cool. Yeah. Uh this is actually a
[35:45] program that we have a friend who runs
[35:47] uh which I'll just say the name and
[35:49] we'll just bleep it. Um but, uh
[35:53] >> uh you know where he works?
[35:54] >> Oh, yeah. Mhm.
[35:55] >> Yeah. So, uh they don't they don't get a
[35:57] lot of great bugs, so they're a
[35:58] relatively secure company. And um
[36:00] anyways, this was a endpoint that for
[36:04] some for some reason my my hackbot found
[36:07] that you could use a base 64 encoded
[36:11] username. It it was it like it didn't
[36:13] give you like a traditional basic off
[36:15] pop-up if you went to the site or
[36:16] whatever. But um but it gave you like a
[36:19] random 401 or 403, but if you passed
[36:22] basic off with the username admin and
[36:24] any password, it it would let you in.
[36:27] And it was like a it was like an API
[36:28] like a full soap waddle API and all of
[36:31] the endpoints worked. So uh anyways
[36:34] really cool crit that that the Hagbot
[36:36] found that I was gonna
[36:37] >> dude I bet it looked at that. I bet it
[36:39] was a 401 and I bet it looked at the
[36:41] like authorization header in the realm
[36:43] and stuff like that. H that's so Yeah,
[36:46] that is one thing that is a little crazy
[36:48] is AI does have that weird like that
[36:51] very clear attention to detail with it
[36:54] sometimes. like it's very much like,
[36:55] "Oh, notice how that was a little bit
[36:57] different here than here." And I'm like,
[36:59] "Oh, yeah. Mhm. Yeah, I noticed that."
[37:01] You know,
[37:01] >> it very often looks at response headers
[37:03] like in ways that like I would have
[37:05] never noticed and like it uh catches
[37:07] things that I would never have noticed
[37:09] because of like the unique response
[37:10] headers.
[37:11] >> Yeah, totally. Um, good [ __ ] dude. Nice
[37:15] job. Um, the one that I was going to
[37:16] talk about before was a tweet that we'll
[37:18] link in the description from uh V12 SEC
[37:21] entitled uh another day, another
[37:23] universal and a Linux LP. And there's
[37:25] been a couple uh crazy universal Linux
[37:28] LPS lately, which is really cool for
[37:30] like sandbox and stuff if you if you're
[37:32] going to go after that. Um, dirty frag
[37:34] and that sort of thing. Uh,
[37:36] >> dude, look at this beautiful video.
[37:39] >> That's what I'm saying, dude. Like, so I
[37:42] guess we'll put it up on the screen. Uh,
[37:44] but the this video is just stunning.
[37:48] Like it it it is smashing 192 bytes into
[37:52] a readonly page cache and it shows like
[37:55] the representation of each of you know
[37:58] the hex pieces of that like changing one
[38:01] by one as they overwrite a specific
[38:03] bite. And it and it's just so easy to do
[38:05] stuff like this now with AI. And I just
[38:08] want to encourage you guys like
[38:10] triagers, they're overwhelmed, they're
[38:12] stressed, they're having a bad time
[38:14] lately. Like give them something savory.
[38:17] Give them something beautiful to look
[38:19] at, you know, when you drop your your
[38:21] high quality [ __ ] because you guys are
[38:22] the people that make the difference
[38:24] here, right? You guys are the ones when
[38:26] the triagers get to your report, they
[38:27] should breathe a breath of fresh air,
[38:29] you know? They should be like, "Wow,
[38:30] this is beautifully written. This is
[38:32] easy to reproduce. And what a stunning
[38:34] bug." you know, and I just I just want
[38:36] to like commend you guys to do what V12
[38:39] sack does here. Prompt the AI to build
[38:42] something, you know, take your your
[38:44] scrappy little PC and build something
[38:46] gorgeous like this and make the triagers
[38:49] day because that'll make the difference
[38:50] in Bug Bounty right now. It really will,
[38:51] >> dude. Yeah. I had like I sent that video
[38:53] of that first bug I mentioned, the QRM
[38:55] injection to multiple people and the one
[38:56] you watched. I had so many people be
[38:59] like, "This video is so good." And I I
[39:01] don't really know what made it good.
[39:02] Maybe it was just the inflection of my
[39:03] voice and the excitement and me me
[39:05] describing or whatever, but like uh
[39:07] >> but yeah, and the team responded I I did
[39:09] send you that, but like the team
[39:10] responded with like, "Hey, thank you so
[39:12] much. This is like the best breakdown of
[39:13] a bug we've ever seen, you know." And so
[39:15] I and so I do think that it makes a
[39:17] really big difference on the perception
[39:19] of your vulnerability and like you know
[39:21] how the team handles it like quickly and
[39:24] you know how how it gets triaged and all
[39:26] that. So yeah, Justin's not wrong and it
[39:28] takes so little time these days to make
[39:30] a really good PC with the help of AI.
[39:32] So, you might as well do it.
[39:33] >> Nice. Yeah, I agree. Um, you got
[39:36] something next or do you want to jump
[39:37] into the ZDI drama?
[39:38] >> I think I'm done. Yeah. Well, both the
[39:40] ZDI drama and I see you also linked to
[39:42] the to the GitHub security tweet that I
[39:44] also
[39:45] >> Well, so we we've got two little pieces
[39:46] of drama to cover next. Um, so our boy
[39:50] Uriotak, who uh we talked about on the
[39:54] pod last week for his uh amazing
[39:55] vulnerability with the delete directory
[39:57] thing,
[39:58] >> um tweeted out, "Does anybody have a
[40:00] direct contact at ZDI? I've been trying
[40:02] to register for the pone to own entries
[40:03] for the past 3 weeks, but I haven't
[40:05] received a clear response. I'm going to
[40:06] have to cancel my flight soon. Please
[40:08] help me." essentially. and um they got
[40:11] back to him and as I'm sure a lot of you
[40:14] guys saw on Twitter, ZDI had to like cap
[40:17] out their competition because of so many
[40:19] submissions this year. Um and a lot of
[40:22] people just had to submit to the main
[40:24] program. There's probably going to be a
[40:25] lot of dupes. Um
[40:27] >> well, I think they said there's only
[40:29] five valid reports, right?
[40:32] >> Did they really?
[40:33] >> I was pretty sure. Well, see if you can
[40:36] discuss that while I'm while I'm talking
[40:38] about this. But um one, just really sad
[40:40] to see super talented researchers like
[40:43] uh not be able to get their stuff
[40:45] submitted. Two, totally crazy that Pon
[40:49] is maxing out. Like what kind of a world
[40:50] are we in right now? Uh where that is
[40:52] happening. Um
[40:54] >> Oh, they're actively tweeting in the
[40:55] last 30 minutes. They've tweeted a bunch
[40:57] of findings.
[40:58] >> Yeah. Yeah, that's what So, um, yeah, I
[41:00] don't think it's just five because I
[41:01] mean there were a couple that that came
[41:03] through uh that I saw that I had in the
[41:05] notes for today and one of which is
[41:08] freaking uh dude of orange dropped a
[41:14] four logic bug chain to get rce on
[41:18] Microsoft Edge and got 175k
[41:21] >> without a memory corruption without a
[41:23] memory corruption. He pawned the browser
[41:26] without a memory corrupt corruption bug,
[41:28] dude.
[41:30] Insane.
[41:31] >> Insane.
[41:32] >> Yeah. So, I just the amount of skill
[41:34] required to do that without any sort of
[41:36] like memory corruption bug is nuts. And
[41:40] I think Johan
[41:42] posted in the Discord this morning like
[41:43] a video that uh ZDI took of him being
[41:46] like, "Yeah, I didn't um" It was such a
[41:49] beast video. He was like, "Yeah, I um I
[41:52] used my eyes to find this bug. not the
[41:54] not the AI. And I'm like, dude,
[41:57] you are you are crazy, dude. Um, so I've
[42:01] got to I've got to get I got to talk to
[42:02] Orange more.
[42:03] >> I'm definitely wrong. There's so many
[42:05] bugs.
[42:06] >> Yeah. Yeah. So, shout out to Orange.
[42:09] Congrats on that. 175K, 17.5 Masters of
[42:13] Pone points. That's pretty sick, dude.
[42:16] On just bugs. a as somebody who doesn't
[42:19] do a lot of um memory corruption, it's
[42:24] very encouraging to me to see him
[42:25] opponent browser with logic bugs.
[42:27] >> Yeah, that's it. Um um the other one
[42:30] that I wanted to mention though was uh
[42:32] Chompy, who's another person I would
[42:33] love to get on the pod. She tweeted out
[42:36] after getting a a 50k in five masters of
[42:38] pone um uh exploit in envy container
[42:44] toolkit. She tweeted out not a bad
[42:46] return on one month of claude code max.
[42:48] >> That's right. That's right.
[42:49] >> Which is like dude
[42:51] >> clearly it's her skill mixed with cloud
[42:53] code but yes.
[42:54] >> Yeah. Clearly clearly knowing how to
[42:56] direct the AI, right? Mhm.
[42:58] >> Um, so I don't know, cool stuff
[43:00] happening in the Pon world. Little
[43:02] difficult for a lot of the people that
[43:04] didn't get their um, submissions
[43:06] accepted into the into the event, but
[43:10] um, yeah.
[43:10] >> So, do they do they not get do they got
[43:12] get points or money if that happens
[43:14] >> or you can do remote? I think they
[43:16] submit it to the main ZDI program and
[43:18] they might get their submission
[43:19] accepted, but um you know less cool than
[43:23] uh having having access to the pone
[43:26] environment, you know.
[43:28] >> Well, do you know if that you think
[43:29] there's going to be like way more
[43:30] findings and way more payouts this year
[43:32] versus any other year ever before?
[43:34] >> Yeah, I mean, right. I think so. I mean,
[43:36] look at our look at our payouts this
[43:38] year, dude. I feel like this has been uh
[43:40] a really good year already and we've got
[43:42] a lot in the pipeline still,
[43:43] >> right? So, um I I imagine that's
[43:47] representative of the rest of the
[43:48] community.
[43:50] >> So,
[43:50] >> that's just sweet to see like, you know,
[43:52] so many bugs being mopped up. Like, you
[43:54] know, I I tweeted that yesterday. I was
[43:56] like, we're mopping up the internet one
[43:57] bug at a one submission at a time, you
[43:58] know.
[43:59] >> Yeah, man. Yeah. So, we'll see. We'll
[44:01] see. I mean, it's it's definitely
[44:02] interesting to see where the um industry
[44:04] is going to go. Like I said, triagers
[44:06] are are burnt
[44:08] >> and stressed and there's a lot of really
[44:11] like verbose, confusing reports that
[44:13] they're having to deal with in mass
[44:14] volume.
[44:16] >> Um,
[44:17] >> tricky time.
[44:18] >> Can I just give a shout out though to
[44:19] Tal from Bug Crowd?
[44:21] >> When whenever it feels like he literally
[44:24] is just triaging every vulnerability
[44:25] that goes to Bug Crowd. Like I mean,
[44:28] yeah, I I assume it's a he, but it might
[44:31] not be, but forgive me if if not. But
[44:32] anyways, just like it feels like he
[44:34] literally triages every single
[44:36] vulnerability for all of Bug Crowd and
[44:38] he's like fast and efficient and good at
[44:40] his job. So anyways, yeah, that that
[44:42] type of skill right now is just so much
[44:43] more impressive, you know.
[44:45] >> That is that is I agree. Shout out to
[44:47] all the triagers. You guys are you guys
[44:49] are going through it right now. Um,
[44:52] yeah, and the last one that I wanted to
[44:54] talk about was, uh, GitHub Security
[44:57] tweeted out, and I think you retweeted
[44:58] and we commented and had a little back
[45:00] and forth, but 325 bounty reports
[45:02] submitted, 226 hackers participated in
[45:06] the program, and $2,367
[45:09] in bounties paid out in April.
[45:11] >> Yeah.
[45:13] >> Yeah. So, it's has to be massive slop.
[45:17] But the other thing is I think there's
[45:19] probably more valid reports in there and
[45:21] they are they're they are slow to get
[45:23] back to them and obviously GitHub has
[45:25] already been in the news for lots of
[45:26] drama around uptime and all kinds of
[45:28] stuff. And I mean I don't understand how
[45:30] they haven't started charging per
[45:32] repository or per data on repository for
[45:35] because they're basically hosting the
[45:37] code of the entire world, right?
[45:40] >> Yeah. Yeah. That's it's crazy, dude. I I
[45:44] don't know. I don't know. And I'm sure
[45:46] people are utilizing, you know, all
[45:49] sorts of GitHub actions for this, for
[45:52] that, for the other thing.
[45:53] >> So,
[45:54] >> it's uh it's definitely challenging. And
[45:57] I think that probably the 2000 awarded
[45:59] here, just like you said, is not GitHub,
[46:01] you know, doing some crazy
[46:03] >> cutting of hackers, you know, ripping
[46:05] off hackers. It's slop
[46:07] >> or andor reports that they have been
[46:09] struggling, struggling, struggling to
[46:11] get through the volume and just haven't
[46:13] paid out yet. So,
[46:14] >> right. Yeah. My guess is my guess is
[46:16] that if you could like draw a perfect
[46:17] line and be omnisient and be like, "Hey,
[46:19] these these 20% of or 10% of bugs that
[46:22] do get paid out eventually, if you could
[46:24] like move them from the forward back
[46:26] into this month where they paid the same
[46:27] month they were submitted, that it might
[46:28] be something more like 20 or 30k, right?
[46:30] It's not going to be some crazy number,
[46:32] but at the very least it would actually
[46:33] be like a more reasonable number like
[46:35] because this just feels very
[46:36] unreasonable."
[46:37] >> I don't know, man. GitHub GitHub I mean
[46:39] might be more than 20 or 30. GitHub. Uh
[46:41] I I guess we should go back and look at
[46:43] what they have paid in previous months,
[46:45] but when I've hacked on GitHub, yeah, I
[46:47] mean they're paying in in March they
[46:49] paid 94, you know, in February 48, in
[46:52] January 76. So yeah, I would I would
[46:56] imagine
[46:57] >> I wonder if they just have a bunch of
[46:58] bounties that they uh that are ready to
[47:01] be paid and just didn't pay in April,
[47:03] you know, like they paid them on May 1st
[47:05] or something because of some sort of
[47:06] like hiccup in like the payment
[47:08] processing or their team or whatever.
[47:10] >> Dude, look look at Hold on. Uh I'm about
[47:13] to like message you on on Discord. Look
[47:15] at the um look at the the tweets though
[47:18] cuz if we look back at at let's go back
[47:20] to November 162 78K 162 reports 78K 146
[47:26] reports 93k
[47:28] uh 151 reports 48k 182 reports 76k and
[47:33] then here comes
[47:35] >> here comes the hackbot problems right
[47:37] 200 reports 48k 380 reports 94k
[47:44] 320 reports 2K, right?
[47:46] >> They stop being able to keep up.
[47:48] >> Yeah, it seems like,
[47:49] >> and I will say, don't you think this is
[47:51] both true of humans, but also true of
[47:53] our hackbots is like when there's really
[47:55] complex scope where like the boundaries
[47:58] for permissions are hard to know uh
[48:02] exactly what uh what's intended mixed
[48:05] with the fact that a lot of times like
[48:08] on like CI/CD runners and stuff like
[48:10] that, you might have code execution, but
[48:11] it's not impactful because whatever. And
[48:13] I bet there are a lot of uh newbies and
[48:16] or people using Hackbots that are like
[48:18] finding issues for companies that are
[48:20] hosting something on GitHub, but it's
[48:22] being reported to GitHub as a GitHub bug
[48:24] when it's really somebody set up a
[48:26] malicious runner or something, right?
[48:27] Like
[48:28] >> totally.
[48:28] >> Yeah.
[48:29] >> Yeah, I imagine so. And and so anyway, I
[48:31] just wanted to give a shout out to the
[48:32] GitHub team, you know, for one for the
[48:35] transparency, right? And hopefully you
[48:37] guys can hang in there because
[48:38] >> you know that was a painful button to
[48:40] push. You know, that was a painful
[48:41] button to push. We are going to catch
[48:43] flack for this tweet.
[48:45] >> Yeah. So, shout out to them for that. I
[48:47] I appreciate the transparency. And yeah,
[48:51] my prayers go up for you because I mean,
[48:53] comparing some of these months, you've
[48:55] seen triple the reports, you know,
[48:57] closer to triple than double. Uh, which
[49:00] is just got to be really rough. Mhm.
[49:02] >> Uh, and like we talked about before,
[49:04] it's not just triple the reports, it's
[49:08] longer reports, more more professional
[49:10] looking reports that are just garbage.
[49:13] So
[49:13] >> sad.
[49:14] >> Harder to weed through.
[49:15] >> Yeah.
[49:16] >> Yeah. Totally, man. All right. Well,
[49:18] that's all I had. You got anything else?
[49:20] >> That's all I've got.
[49:21] >> All right. Well, keep hacking, hackers.
[49:23] Peace.
[49:24] >> Peace.
[49:25] >> And that's a wrap on this episode of
[49:27] Critical Thinking. Thanks so much for
[49:28] watching to the end, y'all. If you want
[49:30] more critical thinking content, uh, or
[49:32] if you want to support the show, head
[49:33] over to ctvb.show/isord.
[49:35] You can hop in the community. There's
[49:37] lots of great highlevel hacking
[49:38] discussion happening there on top of
[49:40] master classes, hackalongs, exclusive
[49:42] content, and a full-time hunter guild.
[49:45] If you're a full-time hunter, it's a
[49:46] great time. Trust me. All right, I'll
[49:48] see you there.
