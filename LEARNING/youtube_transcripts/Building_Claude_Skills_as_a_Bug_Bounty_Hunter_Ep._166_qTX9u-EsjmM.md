# Building Claude Skills as a Bug Bounty Hunter (Ep. 166)

Channel: Critical Thinking - Bug Bounty Podcast
URL: https://www.youtube.com/watch?v=qTX9u-EsjmM
Approx duration from transcript: 52:59
Segments: 1706
Word count: 11733

## Transcript

[00:01] But, as you start talking about these
[00:02] things, I just sit here and I start
[00:04] churning.
[00:05] You know, and and my brain's like, "This
[00:06] is what you're going to do right after
[00:07] you get off this freaking podcast, you
[00:09] know?" Like
[00:15] Best possible hacking when you can just,
[00:17] you know, critical thing, right?
[00:34] Some of the most fun I've had this year
[00:35] hacking already was with you guys in the
[00:38] CTBB Adobe hack-along that we did a
[00:40] couple weeks ago. And the results were
[00:43] great. We found
[00:44] four figures worth of bugs in just 2
[00:46] hours. And I just want to shout out
[00:48] Adobe for being such an amazing program,
[00:50] for sponsoring the podcast, for staying
[00:52] involved in the bug bounty community. Um
[00:54] and I just wanted to say, if you guys
[00:56] want to check out a new program, the
[00:58] Adobe program is awesome. They've got
[01:00] scope for days, guys. They've got
[01:02] binaries, they've got open-source
[01:04] projects, they've got enterprise
[01:06] products, they've got web apps, they got
[01:07] wild cards, they got mobile apps.
[01:09] Anything you would want to hack on, the
[01:10] freaking Adobe program has it. The
[01:12] bounties are competitive. And I mean,
[01:14] just look at the um look at the thanks
[01:16] tab on HackerOne, right? And filter for
[01:18] this year. There's already uh somebody
[01:20] with 620 reputation
[01:22] uh from Adobe, right? So, this guy's out
[01:25] here like, "Don't tell them about Adobe.
[01:27] I'm killing it. I don't want anybody to
[01:29] know about it." Um so, yeah. It's a
[01:32] program ripe for opportunity, especially
[01:34] in the area of AI hacking, cuz they're
[01:36] shipping a lot of AI-related code right
[01:38] now. And they really value AI
[01:39] submissions coming through the bug
[01:40] bounty program. So, if you want a new
[01:43] program to hack on, I recommend Adobe.
[01:45] They're great.
[01:47] Sup hackers, we got the This Week in Bug
[01:49] Bounty segment real quick. First item on
[01:51] the docket is Intigriti has launched
[01:53] their ambassador program. So, if you're
[01:55] deep in the uh Intigriti ecosystem and
[01:58] you want to take that a step further, I
[02:00] have it um you know, firsthand talking
[02:02] to the head of uh community over at
[02:03] Integrity that they're really trying to
[02:05] bump up uh the amount of community
[02:07] engagement and involvement that they
[02:09] have this upcoming year. So, they're
[02:11] really going to be supporting the
[02:12] Integrity ambassadors a lot. Um so, you
[02:14] can find out how to apply for that at
[02:16] integrity.com/ambassadors.
[02:18] Um you know, it's a annual thing.
[02:21] They'll give you support on, you know,
[02:23] engaging with the Integrity community
[02:25] wherever you're at in various spots
[02:26] around the world, um and give you access
[02:29] to resources that you'll need to drive
[02:31] that community. So, um really good
[02:33] opportunity. Uh I I definitely think you
[02:35] guys should take advantage of it if
[02:36] you're in the Integrity ecosystem.
[02:38] All right. Next up is Adobe and Hack the
[02:40] Bay. Um the Adobe team wanted us to let
[02:42] you know that they're going to be at
[02:44] Hack the Bay this year. That is March uh
[02:46] 23rd, I want to say. Yep. Uh 11:00 to
[02:48] 5:00 p.m. in San Francisco. So, if
[02:50] you're around and you're in the bug
[02:52] bounty world and you're going to Hack
[02:53] the Bay, your new mission
[02:56] is to go find the Adobe team and say hi.
[02:58] Tell them you heard on the CTBB podcast
[03:01] to come and say hi. That's a great way
[03:02] to support us and a great way to engage
[03:04] with a a staple program in the
[03:06] community, uh Adobe. So, if you're going
[03:08] to be at Hack the Bay, definitely go by
[03:10] and say hi to them. They'd love to meet
[03:12] you, and that's a great way to support
[03:13] the pod. Um
[03:14] last but not least, we have another
[03:16] shout-out for the bug bounty maturity
[03:18] framework. Um for any of you program
[03:20] managers that are listening, if you're
[03:22] looking to um
[03:24] understand how your bug bounty program
[03:26] is on a maturity scale from emerging to
[03:29] leading and what you need to do to take
[03:31] it to the next level with your program
[03:32] from a hacker's perspective, but also
[03:34] just from a well-run program
[03:35] perspective, then bug bounty maturity
[03:37] framework is an awesome tool that you
[03:39] guys can use um to make sure your
[03:41] hackers are getting the best experience
[03:42] and you're getting the most value out of
[03:44] your bug bounty program. I know the guy
[03:46] running it, Steve. He used to work with
[03:47] us at the pod. He's amazing and knows
[03:49] exactly what he's doing. He's like one
[03:51] of the best people to run this in the
[03:53] community that I can even possibly think
[03:54] of. So, shout out to Steve. All right,
[03:56] that's it for the Twib. Let's hit the
[03:58] show.
[04:00] All right, look dude, here's the deal.
[04:01] Last week on the pod, you
[04:04] told me that I need to be like actively
[04:06] training Claude and getting it to to do
[04:09] this stuff.
[04:10] >> no, you're triggering me. No, stop now
[04:11] already. I hate it when people use the
[04:13] word training wrong.
[04:14] Okay, all right.
[04:15] >> And it's it No, no, no, and I and I know
[04:17] you know, but listen, every normie out
[04:19] there and yeah, I'm not trying to be
[04:21] offensive or anything, but people who
[04:22] are just not in tech but people
[04:24] people say training and I'm like like,
[04:26] you know, you're they're like, "Oh, I
[04:27] trained my chat GPT to do this." Like,
[04:29] you did no training. You gave it some
[04:31] context, you gave it a prompt, you
[04:32] didn't train it.
[04:33] >> Fair.
[04:34] Fair. Let me rephrase. You guide my
[04:36] Claude, inform my Claude, equip my
[04:39] Claude with what I want it to do. Sure.
[04:42] >> Um
[04:43] and I played around with it a little bit
[04:44] more and, you know, you've been tweeting
[04:47] up a storm about Claude finding stuff
[04:49] and I have seen these findings firsthand
[04:52] and they're legit.
[04:54] Um and
[04:56] yeah, we're just kind of at a point
[04:57] where you need to be using Claude to
[04:59] hack and that's why we, you know, we
[05:01] pushed Guido and you helped them build
[05:03] the Claude skill for for um
[05:05] for Guido.
[05:07] Um so, what I want to do today is I want
[05:08] to talk a little bit more about skills,
[05:10] how to understand skills
[05:12] and I know I I know I can see your face
[05:14] right now. I know that you are a little
[05:17] uncomfortable talking about this cuz
[05:18] this is kind of the secret sauce, the
[05:19] last secret sauce
[05:21] that there is. So, let's talk
[05:23] >> I think I'm I'm hesitant on multiple
[05:24] fronts. One is I already know there's
[05:27] some hesitancy around talking about AI
[05:29] on the pod too much and Buzz Factor
[05:31] himself has already been like, "I'm so
[05:32] tired." Not not about the pod, but just
[05:34] about like the community and and X and
[05:36] everything and I know that tons of tons
[05:38] of people we know are like muting lots
[05:39] of words about Claude code and agents
[05:41] and everything else on on X and, you
[05:43] know, again, I'll say what we've said
[05:45] 100 times. It's like, this just isn't
[05:47] important enough for us to tell you. You
[05:48] know, it's kind of like when your
[05:50] parents keep telling you to pick up your
[05:51] room, it's like, well, you're going to
[05:52] have to do it when you get older, right?
[05:54] It's like Exactly. We're going to have
[05:56] to use this
[05:56] >> what they want. We're here to give the
[05:58] people what they need, you know? And
[06:00] that is that is one of the truest
[06:01] statements Justin has ever said about
[06:02] this podcast. He lives and dies by that
[06:05] mantra. So,
[06:06] Um so, yeah, and then
[06:08] >> too, man. I mean, we we we we try all
[06:11] the time. There's the pull of like, oh,
[06:13] wow, we'd get so many more views, so
[06:15] much more distribution if we would just
[06:16] talk about XYZ. Yeah. We we don't do it,
[06:19] guys. We don't freaking do it. And every
[06:21] day
[06:21] I get
[06:22] >> to do more beginner content? Yeah, yeah,
[06:24] I many many many times, you know? And
[06:26] and uh you know, I I won't do it. So,
[06:30] anyway, this is what you guys need even
[06:31] if it's not what you want.
[06:32] >> Oh, I didn't answer your question. Sorry
[06:34] to cut you off. You You said I'm
[06:35] hesitant to talk about it, and yes, I
[06:37] am. Honestly, Justin, I would not have
[06:38] talked about this or another future
[06:40] episode we have coming up in a in a in a
[06:41] few weeks or maybe maybe it's more than
[06:43] a month away, but about this sauce, like
[06:45] giving away the secret sauce for so much
[06:48] of this because I do think it's like
[06:49] it's it's an edge, it's leverage. And
[06:51] because I'm willing to scale to more
[06:53] Cloud Max subscriptions to find more
[06:54] bugs across all bug bounty programs.
[06:56] When we talk about this, it is giving
[06:57] stuff away. But, you know, we've we've
[06:59] we've wrestled with this with the
[07:00] podcast for the last, you know, 2 or 3
[07:02] years uh with the same stuff, right?
[07:04] You're often giving away techniques on
[07:05] here, and so do our guests. And so, I
[07:07] think it's like uh just a part of what
[07:08] we do. And so, yeah, we'll talk about
[07:10] it.
[07:10] >> It is. So, we'll see what we can do, and
[07:13] and we'll see how far we can get today.
[07:15] Uh and I I just I do want to like give
[07:18] you an a little bit of an out here
[07:19] though. Like,
[07:20] if I'm asking things that you really
[07:24] think are going to hack up the secret
[07:25] sauce for you, you know, like
[07:28] AI's a little bit different than talking
[07:30] about techniques cuz one of the things
[07:31] we've built this pod about on is like
[07:33] coming on here and talking about stuff
[07:35] pretty liberally. And then just betting
[07:38] that, you know, the community doesn't
[07:40] have
[07:41] the either the grit or the the patience
[07:44] or you know, whatever to actually
[07:46] implement it, right? And that's why we
[07:48] don't lose out on our bounties as much.
[07:50] We've been burned by that many times.
[07:52] And they it turns out, you know, a lot
[07:54] of you guys, the people that are the
[07:55] high-level hackers that are listening,
[07:57] will take the techniques and go do it,
[07:58] right? And that's exactly, you know,
[08:00] what we're doing. We're exchanging the
[08:02] these concepts for your trust and your
[08:04] ears, right?
[08:06] That being said, AI's a little bit
[08:07] different because if you just do the
[08:09] thing, AI you know, and tell it to do
[08:11] the thing, then AI will just do it,
[08:13] right? You don't have need any like grit
[08:14] or endurance, right? So,
[08:16] I don't know, man. It's
[08:18] I will give you an out if you if you
[08:20] want to not say some of the stuff. You
[08:22] feel free to like just shush me along a
[08:24] little bit, okay?
[08:25] >> Sure. Yep, sounds good.
[08:27] All right. So, first up, man, let's
[08:28] let's let's get into this. This is going
[08:30] to be a nuts and bolts episode.
[08:32] I've got a, you know, rubber meets the
[08:33] road question for you a little bit here.
[08:35] So, I don't use a ton of cloud skills.
[08:36] The only cloud skill I really use right
[08:38] now is the Kaito mode cloud skill. Um
[08:42] I kind of feel like cloud skills are
[08:43] limiting cloud a little bit. Like if I
[08:45] tell it, "Hey, here's my super cool
[08:47] thing to like,
[08:50] you know,
[08:51] grab all the lazy loaded JS files or
[08:53] whatever, right? From from the the JS
[08:55] that I gave you." Um and then it's like
[08:58] a little off, then cloud, you know,
[09:01] cloud's going to try to use the skill
[09:02] and he's like, "Oh, it doesn't work."
[09:03] You know, or whatever. And then it's
[09:04] going to go and get distracted or
[09:06] whatever. Whereas I feel like cloud is
[09:07] smart enough where it's like I tell it
[09:09] to go download all the lazy loaded
[09:10] files, it'll write up a little script in
[09:12] like 30 seconds to pull it down and it's
[09:14] perfectly tailored to the situation.
[09:16] Yeah. So, are we sort of hampering our
[09:18] cloud skills or our cloud when we are
[09:20] giving it cloud skills versus just
[09:22] telling it to do the thing or are we
[09:23] actually enabling them?
[09:25] Yeah, I think that it's just it really
[09:27] depends on what you're asking it to do,
[09:28] right? Like maybe lazy like loading lazy
[09:31] loaded JavaScript files is something
[09:33] that it's like really good at, right?
[09:34] But you do need skills for things it's
[09:37] not good at, like Kaito. Like the like
[09:39] you Why do Why don't you just get rid of
[09:40] your Kaito skill? It's like if you ask
[09:41] it to start in our Kaito, it's going to
[09:43] have to go into some deep research. If
[09:45] it can't find the docs online, it might
[09:47] legitimately not be able to figure it
[09:49] out. But if there's really good docs
[09:50] online, it would go find the docs, it
[09:52] would download, you know, it would
[09:53] figure out what the SDK is, it would go
[09:55] look at the GitHub open-source code, and
[09:56] it would be able to figure it out. But
[09:58] now you've wasted like, you know, half
[10:00] of your 5-hour limit for it figuring out
[10:02] how to use Kaito. And so I So I think
[10:04] that um you know, I've kind of
[10:06] categorized when it's useful to have
[10:07] skills into a couple buckets.
[10:10] The one that we're talking about right
[10:11] now is basically things it doesn't know.
[10:13] And that could be because you have a
[10:16] custom setup. Like let's say you have a
[10:17] server and it runs at a certain IP
[10:19] address, and you have a certain user on
[10:21] there, and you want things to be done a
[10:22] certain way. That's in your head.
[10:24] There's no way for Claude to figure it
[10:26] out. And so you probably need a skill or
[10:29] to update your Claude MD to say like,
[10:31] "Hey, when you're using my VPS, here's
[10:33] the password, or here's how you connect
[10:35] to it, or here's where I save things."
[10:37] Like, you know, you basically need to
[10:39] give Claude Code information it doesn't
[10:41] have. And I think that also applies to
[10:43] any kind of like groundbreaking
[10:45] techniques. You know, these models are
[10:46] trained on trillions of tokens, and your
[10:51] uh specific technique, especially if you
[10:52] got it from like last year's Def Con
[10:54] talk or something, that you're using to
[10:55] exploit some sort of like, you know,
[10:57] nested GraphQL mutation. GraphQL's maybe
[11:00] a good a bad example because Claude
[11:01] Code's so good at GraphQL. But, you
[11:03] know, there are definitely things that
[11:05] it's not as good at or that it just
[11:06] doesn't know because it's not been in
[11:08] the training data. It may very well be
[11:10] able to figure it out given enough time
[11:11] and effort, but why not just give it
[11:13] like a head start?
[11:15] Okay.
[11:15] >> So, custom
[11:18] But see, but then there's also the
[11:19] inverse of that, man. I feel like like
[11:21] just to challenge you there a little
[11:22] bit. I mean, that's that pretty much the
[11:23] exact opposite of what I just said,
[11:25] which is
[11:26] you know, if we give it skills Mhm. that
[11:29] that
[11:30] that are not applicable to all of the
[11:32] situations. Yeah. Then, you know, we're
[11:35] we're the the whole technological
[11:37] advance that we have here is that it's
[11:40] smart. Yeah. You know, like I feel like
[11:42] giving it skills is like just why didn't
[11:45] we just code it? You know?
[11:47] Uh right? Am I wrong there or is it like
[11:49] is the beauty of AI that it can actually
[11:51] go figure out the more nuanced situation
[11:53] without us having to give it
[11:54] instructions on how to deal with that?
[11:56] I mean, I think it it's definitely both.
[11:58] Like it has a lot of information baking
[12:00] in. You're not wrong You're not wrong
[12:01] about that. But then it clearly has
[12:03] limitations, right? Like using Kaito
[12:04] mode. And then it's smart enough to
[12:06] figure out some stuff, but it's not
[12:07] smart enough to figure out everything. I
[12:09] think that uh your concern can mostly be
[12:11] mitigated with like just a Claude MD
[12:14] line, like one line that says like,
[12:16] "Hey, when I ask you to do something,
[12:18] like invoke the skill to do it because
[12:20] sometimes I have certain ways I want
[12:21] things to be done. But if the skill
[12:23] isn't comprehensive enough or if it
[12:24] fails or if you try with it and it
[12:26] doesn't work, don't stop there. Use your
[12:28] own exploration and your own creativity
[12:30] to keep going. You know, try harder. Put
[12:32] the OSCP motto or straight straight in
[12:34] your thing." You know, I have POC or
[12:36] GTFO and try harder both in my Claude MD
[12:39] cuz it's like I'm not like you can't
[12:41] just say, "Oh, this looks like it might
[12:42] be vulnerable." That's That's not
[12:44] valuable to me. I want you to actually
[12:45] have a full POC that I can, you know,
[12:48] completely validate end to end to make
[12:49] sure this is an actual bug. And so I
[12:51] think that
[12:52] um you know, the limitation is mostly
[12:54] mitigated by what you're talking about,
[12:55] but there have been a lot of studies
[12:56] that have shown that like poorly written
[12:59] agent MD or Claude MD files or poorly
[13:01] written skills actually reduce the
[13:02] quality. And so I I do think people
[13:05] should be really um careful and
[13:06] particular about how they're like what
[13:08] they're adding and how they're adding
[13:10] it.
[13:11] Yeah. Yeah. I agree. It is a little
[13:13] tricky though, man, cuz I do find myself
[13:15] like I definitely just gave Claude a
[13:17] list of like things I wanted to brute
[13:19] force the other day and said like, "Hey,
[13:20] you know, brute force these in in
[13:22] Kaito." Yeah. You know, and it like made
[13:25] a bunch of replay sessions or whatever.
[13:26] It didn't actually use automate. I don't
[13:28] know, maybe I I told it to use
[13:29] PlayStations or whatever. And I was
[13:31] like, "Dang, I could have just like put
[13:32] this straight into automate myself.
[13:33] Like, what am I doing? I'm getting lazy
[13:35] as heck." Yeah.
[13:37] So, it is a little tricky. Um
[13:39] So, building off of what you just said
[13:40] though, I wanted to
[13:42] like describe something that I uh saw in
[13:46] the Kaito mode skill that you and Kaito
[13:48] built and
[13:50] ask your opinion on this as a framework
[13:52] for Kaito skill. So, what will happen in
[13:54] the Kaito skill, Kaito mode skill is if
[13:56] it can do something
[13:59] with the Kaito skill, you know,
[14:00] documentation that you guys have built
[14:02] and stuff like that, it will invoke your
[14:04] bi- your binaries or your your scripts
[14:06] or whatever that you have in place and
[14:08] it will do it with that, right? If it
[14:10] cannot do that
[14:11] it will um
[14:13] use the actual client JS library that
[14:17] the
[14:18] .ts files that run kind of this Kaito
[14:20] skill
[14:21] um is built off of and it will invoke
[14:23] those directly to accomplish its goal,
[14:25] right? And it will sometimes even do
[14:26] that if it if it's a more complicated
[14:29] action cuz it'll be like, "Oh, I'll just
[14:30] write out the script and chain multiple
[14:32] actions together, right?"
[14:33] >> Yeah. Um and then if it cannot get it
[14:35] with that, it will then
[14:38] try to use GraphQL to control
[14:40] Kaito directly. Yeah. And I think that
[14:42] sort of fallback nature, I don't know if
[14:44] you guys you coded this directly into
[14:45] the Kaito skill itself, but I think that
[14:47] sort of fallback iteration nature Mhm.
[14:50] of building a skill
[14:52] it works really well because you give it
[14:54] multiple tiers of flexibility and
[14:56] control while also abstracting away the
[14:58] tasks that you know are going to be the
[14:59] same every single time. Does that make
[15:01] sense? Yeah, I didn't think there was
[15:02] going to be anything I didn't want to
[15:03] mention, but there is something that I'm
[15:05] not willing to mention, but I have
[15:07] implemented something very similar for
[15:09] tough problems in bug bounty
[15:12] where basically it's exactly that. Like,
[15:13] I want you to try to solve the problem
[15:15] with this method, but if it doesn't work
[15:18] for some reason, then try this method.
[15:20] And if that doesn't work, then try this
[15:21] one.
[15:22] And I think you're right. That gives it
[15:23] a lot of uh flexibility and a lot of
[15:26] like a much higher odds of success. And
[15:28] no, I I didn't build that into the
[15:30] skill. It's really funny that your
[15:31] Claude code did that. Um, but
[15:33] >> wonder if that's a Claude I wonder if
[15:34] that's a Claude code like
[15:36] concept that that Anthropic built into
[15:39] Claude code. Like, "Hey, you know, if if
[15:41] the skill doesn't work, look at the
[15:42] primitives that built the skill." Yeah.
[15:44] >> And then try to use those primitives to
[15:46] accomplish the same goal. Or not. I
[15:48] don't know. I think it's probably just
[15:49] the fine-tuning on lots of data,
[15:52] especially lots of coding things where
[15:54] it tried to run something on the command
[15:55] line and it failed. And normally, you
[15:57] know, a year ago or whatever, the models
[15:59] were like fine-tuned to basically just
[16:00] like stop at that point because like
[16:02] >> Yeah. all the examples were like
[16:04] one-offs. But where people have been
[16:05] using Claude code over the course of the
[16:06] last year, they probably have a lot of
[16:07] training data for examples of it like
[16:09] failing, trying again, failing, trying
[16:11] again, and that being like the ideal
[16:12] training set because that's what we want
[16:14] as users. We just want it to work. Like,
[16:15] stop getting the error and make it work.
[16:17] Yeah. Yeah, just force it. All right.
[16:19] So, given that I I understand that. That
[16:22] makes sense.
[16:23] We're going to create skills and we are
[16:24] going to, you know, give it sort of this
[16:26] fallback architecture, which is good.
[16:29] What things do I create skills for? Is
[16:31] is kind of like my next question where I
[16:33] where I go because
[16:34] a lot of this is just like looking at at
[16:37] the JS files, looking at the HTTP
[16:39] request, and like trying things, right?
[16:41] Which is great, you know, and the kind
[16:43] of mode skill is phenomenal, by the way.
[16:44] It really is super helpful for it to
[16:45] have it like, you know, sending stuff
[16:49] uh through replay and being able to have
[16:50] introspection to it. But you know, what
[16:53] what areas should we be building skills
[16:56] in? Do you do you have any thoughts on
[16:57] >> I think when there's something very
[16:59] flexible, like making a request,
[17:01] and you have a way you want it to make a
[17:02] request, that's a great place for a
[17:04] skill, right? Like, it can use curl, it
[17:06] can use JavaScript, it can use Python,
[17:07] it can use Kaito, it can use Wget, like
[17:10] it can use Chrome DevTools, it can use
[17:12] Playwright. I think um,
[17:14] in general, anytime there is a uh way to
[17:18] do like there's a many many ways to do
[17:20] something and you want it to do a
[17:21] specific way, it's a great time to use a
[17:23] skill, right? Like you want it to use
[17:24] Cado so you can co-hack with it so you
[17:26] can see the request, so that you have
[17:27] history for screenshots, for POCs. I
[17:30] want it to do that for the same reason,
[17:31] right? There are probably lots of things
[17:33] like that. Like if it's going to SSH or
[17:36] SCP things to a certain place, it's like
[17:37] oh it needs to know what server to do
[17:39] that to. It needs to know where to save
[17:41] that thing.
[17:42] Another great example would be like
[17:43] where do you want it to take notes? Do
[17:45] you want it to save at the target level
[17:46] or at the subdomain level? Do you want
[17:48] it to save off leads and findings or
[17:50] just
[17:51] gadgets, you know, like I think these
[17:53] sort of things where the
[17:55] the total output space, especially
[17:57] across multiple sessions. So actually
[17:58] that's that's another great example.
[18:00] Let's say Justin that you were going to
[18:01] be hacking with Cloud Code a lot over
[18:03] the next week. Do you want each Cloud
[18:05] Code instance to save files in different
[18:08] folder structures? It doesn't make any
[18:10] sense, right? It's going to confuse you
[18:12] and your desk is going to or your
[18:13] desktop or like you know, your file
[18:15] system is going to be a total mess. It
[18:17] gets messy, man. Well, yeah, but it
[18:18] doesn't have to be messy. You actually
[18:20] can just use a skill or a Cloud MD like
[18:22] to actually, you know, a line in your
[18:23] Cloud MD or a paragraph in there or
[18:25] whatever to steer it to behave in the
[18:27] way you want it to. That's not
[18:28] restricting it. Like telling it where to
[18:30] save it isn't going to degrade the
[18:31] quality, right? Telling it how to make
[18:33] those requests will hopefully not
[18:35] degrade the quality. Though I do think
[18:37] it's like much better at like Bun TS
[18:38] stuff or like, you know,
[18:41] >> I think so. Yeah, and it's like really
[18:42] really good at
[18:43] >> cuz they bought Bun, right? You know,
[18:45] it's like
[18:46] yeah, clearly like they're they're, you
[18:48] know, smoking their own supply over
[18:50] there with that, I think. Well, what's
[18:52] kind of crazy is that whatever they have
[18:54] Cloud Code do is probably going to be by
[18:57] default, like if you don't steer it,
[18:58] it's probably what's going to dominate
[19:00] the market because everyone's using it
[19:02] and everyone's going to continue to use
[19:03] it and so they kind of have like really
[19:05] large influence over that, but Yeah. But
[19:08] anyways, back to your question. So I
[19:09] think that that's one way, right? It's
[19:11] like when the total problem space is
[19:12] large or the total solution space is
[19:15] large and you want it to find a solution
[19:16] a certain way, it's a good time to
[19:18] implement a skill or to update your your
[19:20] Cloud MD. The other time is when it's
[19:22] knowledge that like secret knowledge.
[19:24] Um you know, like I don't know hidden
[19:26] techniques that you that you have that I
[19:28] don't, right? Or I or you know, there
[19:30] are probably Google gadgets that are in
[19:32] my files that are not in your files. And
[19:35] so like bundling those into a skill
[19:36] makes sense. It's not on the internet.
[19:38] It's not in It's not in, you know, the
[19:41] public domain where you can go find it.
[19:43] So if it needs this this gadget, this
[19:45] Oracle for ID to username or something
[19:47] for some random bug bounty program, it
[19:49] needs to either be in the notes so it
[19:50] gets out of the context whenever
[19:52] attacking that program or it needs to be
[19:54] in a skill, right? And and you know,
[19:57] that's not going to limit it. That's
[19:58] going to make it way better cuz it has
[19:59] access to more tools, right? Um I guess
[20:02] that's another good example. Skills are
[20:03] a great like there are things that AI
[20:06] could sign up for but is really going to
[20:08] struggle to sign up for. So another
[20:09] place for an example another place for a
[20:11] skill to be implemented would would be
[20:13] like
[20:14] let's say you want it to use a specific
[20:16] piece of software that requires you
[20:17] going through enterprise sales to buy.
[20:19] Like
[20:20] like by by not having a skill there, it
[20:22] just literally can't use that product.
[20:24] But if you signed up, you've got creds,
[20:25] you've got API token and you make a
[20:26] skill and you put the token and how to
[20:28] call it in the skill, now it can use
[20:30] that. So like it's literally like a
[20:32] skill you're giving it that it could not
[20:33] have had otherwise.
[20:35] Yeah, that that makes sense. That that I
[20:37] don't struggle with at all. Like if I
[20:39] need to give it access to, you know,
[20:41] Kido or you know, whatever enterprise
[20:44] thing that I needed to have access to,
[20:46] then that makes total sense for a skill.
[20:47] What I'm kind of struggling with from
[20:49] like conceptual perspective from as an
[20:51] offensive security researcher is stuff
[20:53] like
[20:54] For example, I I thought about Well,
[20:56] totally, you could do that for sure. But
[20:58] but I'm thinking like do I create
[21:00] something like a front-end analysis
[21:02] skill where I where I like outline my
[21:04] methodology for doing front-end
[21:07] analysis, you know, and and doing
[21:11] client-side hacking essentially, right?
[21:13] Mapping out the attack surface,
[21:14] understanding, you know, everything
[21:15] about it. Or do I and and do I give it
[21:20] tools to do that, right? Like, hey,
[21:21] here's, you know, use P prettier for
[21:23] beautification, use this for source map
[21:25] enumeration, you know, that sort of
[21:26] thing. Uh
[21:28] and and will giving it that be helpful
[21:31] and is or am I just turning it into me
[21:33] and I'm losing
[21:35] the the magic of like, wow, it found
[21:38] something that, you know, like for
[21:39] example, when I talked about the the
[21:40] shift, um, you know, the shift
[21:42] vulnerability that I found. I I told it,
[21:44] hey, try some JWT attacks is what I told
[21:46] it on this target, right? And then it
[21:48] just went through and did all the JWT
[21:49] attacks, you know, that it knew and it
[21:51] found a bug and it was like a 15K crit,
[21:54] you know? So, like
[21:55] >> So, I I think there are two things here.
[21:58] The The first thing is
[21:59] >> answered this question, but yeah. No,
[22:00] no, no, no, no. Actually, I No, I All
[22:02] the stuff you said triggered completely
[22:03] new thoughts to me. The The The first
[22:05] one is that tokens are cheap for right
[22:07] now, right? They're subsidized. So, you
[22:09] always should just do both if you have
[22:10] the opportunity. I think it's amazing
[22:13] and I think that if you really wanted to
[22:14] know, you should compare it and improve
[22:16] your workflow. So, I think personally,
[22:18] you should actually hardcode your
[22:19] front-end analysis because it gives you
[22:21] more determinism, so you know that it's
[22:23] not going to miss things that you
[22:24] wouldn't have missed, right? Like Like
[22:26] because when you just let it explore by
[22:28] itself, it might not have actually
[22:30] loaded source maps. It might not have
[22:31] been able to find them. And unless
[22:32] you're literally watching it the whole
[22:33] time, which you're clearly not, you're
[22:34] doing other things, you're hacking other
[22:35] stuff. When it says it's done, you're
[22:37] just going to be like, oh, okay, I guess
[22:38] it didn't find that anything. It's like,
[22:40] no, no, no, actually, it missed this
[22:41] entire workflow that I normally do. And
[22:44] so, I think especially, you know, if you
[22:45] want to be thorough, you should outline
[22:47] your methodology and make it follow
[22:49] that. But then, I think you should do it
[22:51] a completely separate run that's like
[22:52] that has none of that and that that does
[22:54] its own thing. And then, if you have the
[22:56] opportunity, compare them and be like,
[22:57] hey, was there anything that this like
[22:59] free-roaming agent found that our
[23:01] hardcoded workflow didn't find, if so,
[23:04] how did it do that? And add that to the
[23:06] workflow. Like, what techniques did it
[23:07] use that we don't that we didn't like
[23:09] previously hard-code into the workflow?
[23:11] Mhm. That's a great point. I think I
[23:13] think that's some very helpful feedback
[23:16] to give. And so, let's get into the nuts
[23:17] and bolts of that because I think what's
[23:19] overwhelming for everybody right now is
[23:21] this is like, you know, such a new
[23:23] world, you know? And and getting
[23:26] defined
[23:27] pathways for like improvement and
[23:30] implementation of AI is really helpful.
[23:32] So, let's say let's give an example. Um
[23:34] I've got this website site.com that I I
[23:36] want to hack on. So, I spit up, you
[23:39] know, maybe I've got my tmux pane. I've
[23:40] got two windows side by side. One, I
[23:43] like clone down all of my own, you know,
[23:45] skills and and agent definitions and
[23:48] stuff like that into that that cloud
[23:50] code instance. And I say, "Boom, hack
[23:52] site.com. Here's the cookies. Here's
[23:54] whatever you need. Here's like my my,
[23:57] you know, starter pack or whatever."
[23:58] Yeah. And then the other in the other
[24:00] window, I have it I say just, "Hey, hack
[24:04] site.com." You know, very few skills,
[24:06] very few resources. And then
[24:09] do I I mean, do you think I should ask
[24:11] it for like a definitive output? Should
[24:12] I say like, "Okay, both of you guys
[24:14] output a report that contains everything
[24:16] that you found that you think might be
[24:18] of interest. And then compare the two
[24:20] and cross-correlate or Yeah. Just spell
[24:23] that out for me here. Personally, if I
[24:24] was going to do it, I would say, you
[24:26] know, what once I feel like both are
[24:27] kind of done, I would just say or or
[24:30] actually maybe while they're running cuz
[24:31] it might have to compact most multiple
[24:33] times. So, I would I would tell both
[24:35] when when you when starting them. And
[24:36] mine kind of do this naturally cuz of my
[24:37] CloudMD, but keep notes on what you're
[24:39] doing and what you tried and what was
[24:41] successful and what wasn't.
[24:42] And then and then at the end, I would
[24:44] say like, "Hey, give me a list of all
[24:45] the things you tried and, you know, you
[24:47] the workflow you went through and all
[24:48] your findings
[24:49] um to to just one of them. It doesn't
[24:51] matter which one. And then just paste
[24:52] that into the other and be like, 'Hey, I
[24:54] had another agent work. This is what it
[24:56] did. Compare it to what you did, and
[24:58] tell me about any gaps. Like, what did
[25:00] it find you didn't? What did you find it
[25:01] didn't? What did you try that it didn't?
[25:03] Vice versa. And then, when, you know,
[25:05] that after after it responds, it might
[25:07] be insightful, it might not. If it's
[25:08] insightful, say like, "Oh, okay,
[25:10] perfect. Now, add that to our workflow,
[25:11] so you don't miss that next time."
[25:13] Mhm. That's really nice because
[25:15] especially with the agent you're asking
[25:18] it of, it's got its context already.
[25:20] >> Exactly. So, it's like, "Oh, I I I did
[25:21] try that, but then I like
[25:22] cut it last minute." And then, you know,
[25:24] but if you added asked third agent to
[25:26] like, you know, I almost suggested that.
[25:29] get output from both of almost said,
[25:30] "Take read the output of both." But, no,
[25:31] it's lossy. Like, you definitely want to
[25:33] do it with the context. That's
[25:35] interesting. I bet you could also
[25:36] improve it even further, though, by
[25:38] saying, "Third agent, look at the
[25:40] context files for both of the other
[25:42] agents Yeah. and see what it tried Mhm.
[25:45] uh and compare that to the outputs of
[25:47] each. Yep. Uh and, you know, compare and
[25:49] contrast." I'm I'm very often using this
[25:52] skill that I made called session search.
[25:54] It's not a big deal, but it's just like
[25:56] a small little CLI wrapper around like a
[25:59] fast, you know, rip grep across all of
[26:02] my session logs. I think I'm up to like
[26:03] 4 GB worth of session logs in Cloud
[26:05] Code, just on my local laptop, not
[26:06] including the stuff that runs in the
[26:07] cloud.
[26:09] And um
[26:10] I'll often say like, "Hey, I was
[26:11] chatting with you about YAML parsers
[26:13] yesterday or like a few a few days ago.
[26:15] I don't know where the session is. Can
[26:16] you go find that?" Or another thing I've
[26:18] used it for, HackerOne's API token, it
[26:20] only lets you have one at a time. And a
[26:22] lot of times I'll like lose my token, I
[26:24] don't know where it's at. I should just
[26:25] put it in 1 Password. But, I but I'll be
[26:27] like, "Hey, go grep for BB scope and
[26:29] grab the token that we used in that
[26:31] command. I need to use it for something
[26:32] else, you know, or what have you."
[26:33] Do you give it access to 1 Password?
[26:36] No.
[26:37] Yeah, okay. Cuz I know some people that
[26:39] do that for like, uh you know, open claw
[26:42] or whatever, and I'm like,
[26:44] "Oh my gosh." You know, like, don't do
[26:46] that.
[26:47] Well, I mean, I do think I'm still
[26:48] running pretty risky. Like, I use
[26:49] dangerous skip permissions on
[26:51] everything. And I And I have it running
[26:52] on my local laptop with access to
[26:54] everything, but I don't give it access
[26:56] to my email or to one password, so I'm
[26:58] I'm at least a little protected. That's
[27:00] good. That's good. Um okay, so
[27:04] yes to my methodology for the purpose of
[27:08] getting to deter Yeah, determinism and
[27:11] confidence that it's doing what I want
[27:12] it to do. Yes.
[27:14] But also But tell it not to limit
[27:16] itself. Yeah, I would say just even put
[27:18] it in your skill like don't limit
[27:19] yourself to this workflow. If you find
[27:20] something interesting, go down that
[27:21] rabbit hole and then just come back to
[27:22] the workflow. Or after we're done, if
[27:24] you run through my whole workflow and
[27:26] there's stuff that you thought was cool
[27:27] or like that we should have checked that
[27:29] we didn't, add it back to the skill and
[27:31] keep going.
[27:32] Freaking crazy that we're saying that
[27:34] you thought was cool to a computer like
[27:36] that's insane, bro. Yeah, it is. Wow, we
[27:39] you just like authentically recommended
[27:42] that you ask a computer to go look into
[27:44] what it thought was cool. Like that's
[27:46] nuts, dude. And it's like you know, I'm
[27:48] obviously conflicted because I don't
[27:50] think I I I don't think that these
[27:51] models are in any way conscious, but
[27:53] they definitely emulate humans and like
[27:55] all of their thought patterns and all of
[27:56] their token outputs, so stuff like that
[27:57] just works.
[27:59] It is crazy, dude. It really is.
[28:01] Um okay.
[28:02] So, can you give us a couple So, I
[28:05] really liked the session session search
[28:08] ooh
[28:10] skill that you mentioned. Um do you have
[28:12] any other skills that you want to just
[28:14] lob up there? You don't you don't need
[28:16] to release them, just talk Yeah. Yeah,
[28:17] so one skill that is really good and you
[28:22] should not let it take away from buying
[28:23] his book, so go buy Eugene's book, but
[28:25] JDXSS Doctor created a skill that he and
[28:28] I both use called zero-day research that
[28:31] basically told it to go look at Eugene's
[28:33] book all of his content that he's put
[28:35] out online and create and create like a
[28:38] zero-day finder and it's really good at
[28:41] looking at
[28:43] source code and it's really good at
[28:44] looking at binaries like executables and
[28:46] like Mac OS DMGs and stuff.
[28:48] It's really like I don't know why, but
[28:50] like I think that it's because, you
[28:52] know, there's not a lot of the internal
[28:54] monologue of the experts, like like
[28:56] Eugene's brain, for this sort of thing
[28:58] in the training set. So, this is like
[28:59] another example where it's like kind of
[29:01] like secret knowledge that, you know,
[29:03] eventually will be baked into the model,
[29:04] but right now it's not. And so, you can
[29:07] you know, you can have it like search
[29:08] for zero days.
[29:10] That's a good one.
[29:11] Content creator {slash} report writer. I
[29:14] think everyone should have their own.
[29:15] And personally, I think that I'll just
[29:18] give you some prompting tips right now.
[29:19] Give it an example of like some of your
[29:21] best written reports, and tell it to
[29:23] keep everything super concise and super
[29:25] technical and just straightforward. Like
[29:26] don't put any flavor in it. And then
[29:28] give it exact fields that you want it to
[29:30] fill out every single time. And this
[29:32] saves me so much time. And like, you
[29:34] know, my agents at the once they find a
[29:36] finding, like I tell them to go ahead
[29:37] and and write the report and then give
[29:38] me a link to it locally. And
[29:41] they're just they're so good. Like I
[29:42] very seldom have to edit them very much
[29:44] at all. I'm usually reading them for
[29:46] accuracy, not for any kind of tone. The
[29:48] tone is just like and then I did this,
[29:50] and then I did this, and then this
[29:52] happened. It doesn't inject any flavor
[29:54] or over hypeness. It's just like, you
[29:56] know, I mean, it's very straightforward.
[29:57] And so, that can be really useful.
[29:59] Yeah, dude. I don't know, man.
[30:01] Like Richard, you can bleep bleep the
[30:03] name out here, but like I've I've looked
[30:05] at
[30:06] reports recently, and
[30:08] like that are AI generated, and I I had
[30:11] to give them a talking to about it, to
[30:13] be honest. I'm like, this is not good.
[30:15] And this is why, you know, people are
[30:18] are you know, having issues with AI
[30:22] generated reports. So, I think you
[30:23] really have to
[30:25] you know,
[30:26] I think giving that recommendation to
[30:28] anybody who is,
[30:30] you know, not at a at a higher level of
[30:32] hacking proficiency and hasn't written a
[30:34] thousand plus reports by hand, you know,
[30:37] it's a little dangerous. Let me talk
[30:39] about the ways that it falls apart, so
[30:41] people are aware. It falls apart in the
[30:43] fact that it will often blend bugs.
[30:46] Like very frequently, it tries to blend
[30:48] two or three bugs into a single report,
[30:49] which it just doesn't make sense.
[30:51] And and I'm often having to clear that
[30:53] up. The other thing is it's like it's
[30:55] understanding of threat modeling is
[30:56] still kind of bad. Um
[30:59] there was a report that um I put in
[31:02] yesterday or the day before.
[31:04] Um
[31:05] and what happened was it was access to a
[31:08] bunch of paywall uh like um free
[31:10] features or a bunch of paid features. So
[31:12] it was a bunch of paywall bypasses,
[31:13] right? And those normally aren't great
[31:14] reports, but I mean it was like 30-plus
[31:16] features. Like you could get access to
[31:18] basically any pro pro or enterprise
[31:19] feature.
[31:20] But the the agent was like in the report
[31:22] like saying like complete degradation of
[31:25] security. Like basically a lot of the
[31:26] paywall things allowed you to like
[31:28] change things about your object in this
[31:31] in this app that made it less secure.
[31:33] And so it was convinced that it was like
[31:35] bad because you could like paywall
[31:37] bypass to get like enterprise features
[31:39] to then make the product less secure.
[31:41] >> secure.
[31:42] >> Yeah, it's like it just doesn't make any
[31:43] sense. So I mean just be really careful
[31:44] and read it, but I will say I I don't
[31:46] have to edit mine very often.
[31:48] Um Yeah, it's you probably have good
[31:50] good Now I was about to say training.
[31:51] Holy crap. No, uh you have good
[31:54] guidance. Yeah, good intuition there.
[31:56] Yeah. Um some other good skills I think
[31:59] like um BB scope and um
[32:01] like H1 scope or hacker scope or
[32:03] whatever that Patrick just came out with
[32:05] can be really useful because this is
[32:07] data that the model can't get on its
[32:08] own. And um basically what is I think
[32:10] Patrick's is actually an MCP, but uh but
[32:13] what it does is it pulls like the policy
[32:14] page, which is really useful cuz I had
[32:16] previously wasn't giving that to my
[32:17] agent, so it was sometimes going out of
[32:19] scope and having issues. And so it pulls
[32:21] the policy, it pulled it pulls the
[32:23] scope, and then it pulls like um
[32:25] what are they called? Um
[32:27] disclosed public bug reports. So it kind
[32:30] of like can get a heuristic for like
[32:31] what might be vulnerable. Like What is
[32:32] that called? Uh I think it's called H1
[32:35] scope. Um we'll link it in the show
[32:37] notes, but it's by Patrick. Uh, it's a
[32:39] really nice scope. And he's And he's And
[32:40] he's updating. Like he's even doing like
[32:42] a blog series right now where he's
[32:43] already posted two blogs in the blog
[32:44] series.
[32:45] Um,
[32:46] so that is a nice one.
[32:47] >> H1 brain, maybe? Is that Is that the MCP
[32:50] server?
[32:51] >> Yeah, it is. Yeah. H1 brain. Um, I spoke
[32:54] over you, but yeah, that's what Justin
[32:55] was saying. It's called H1 brain.
[32:57] Um,
[32:57] >> Okay.
[32:58] Yeah, I think that's mostly, you know,
[33:00] the types of things.
[33:02] If you have any workflows, like I do
[33:03] think skills are really nice for Justin,
[33:06] you probably have actually a couple of
[33:07] these in your hacking workflow where
[33:08] like you very frequently want to like
[33:12] This I don't love this example, but
[33:13] basically get subdomains, pipe through
[33:15] HTTPX, then automatically fuzz, and then
[33:18] get all of those results. Anytime you
[33:19] have like a full pipeline, it's great to
[33:21] bake it into a skill so that you're not
[33:23] always having to like kick it off,
[33:24] especially if there's like contextual
[33:26] flags or contextual input where the AI
[33:29] can basically get that input for you,
[33:30] run the pipeline for you, and then tell
[33:32] you where the output is. It's just
[33:33] really nice to kind of like have like a
[33:35] faster automation or like a contextual
[33:37] wrapper for your automation.
[33:39] Yeah. And you're you're using I mean,
[33:41] skill just I just want to like clarify
[33:43] this here. Skill is being used kind of
[33:45] loosely here, right? Like it can just be
[33:47] an MD file with information. It almost
[33:50] always is. But yeah, sometimes it
[33:51] includes
[33:53] command line tools.
[33:54] >> Like
[33:54] Okay, like a command line tool bundled
[33:56] with it. And and
[33:58] in your experience, it's best to have
[34:00] Claude write that, you know, using
[34:03] like TypeScript files or something like
[34:05] >> Right. Almost al- almost always that's
[34:06] what mine are these days. Yeah. And I
[34:08] think it's just And that's just because
[34:09] that's what Claude prefers, and so uh my
[34:11] intuition says that it's going to be
[34:13] better at writing those and make less
[34:15] mistakes when it writes them. So, that's
[34:16] what I've been letting it do even though
[34:17] I'm not a huge TypeScript guy.
[34:19] So, okay, let's let's just think about
[34:22] this for a second. Like I think the
[34:23] highest value thing that somebody can do
[34:26] right now is who's actively hacking and
[34:29] using Claude uh and wants to use Claude
[34:31] to integrate, you know, into their
[34:32] workflow, is just download the the Kaito
[34:34] mode scale and just let it like you can
[34:36] just tell it, "Hey, make all these
[34:38] replay tabs like look at all the stuff
[34:40] that I've got in there." Yeah, let me
[34:41] let me give you let me give you a pro
[34:42] tip for that. Yeah.
[34:44] I don't know how you do it, but like
[34:46] let's say
[34:47] you're looking at your HTTP history and
[34:48] you're like, "Oh, I want Cloud code to
[34:49] hack on this request." What I what I
[34:51] usually do is I'll copy and paste the
[34:54] top two lines because it has the host
[34:56] and the path and then I give that to
[34:58] Cloud and say, "Hey, look at, you know,
[34:59] this request." And it then it will go
[35:01] find it based on that. Uh, I don't know
[35:04] if the ID on the left is like matches
[35:06] the ID in the database and all that. So,
[35:08] that's like kind of like a really um
[35:10] like a pro tip that people probably need
[35:12] for like helping Cloud Cloud basically
[35:13] >> it the session
[35:15] a name in Kaito.
[35:18] What do you mean What do you mean the
[35:19] session name?
[35:20] >> Like like
[35:21] >> Oh, in replay. Got you. Yeah, I know I
[35:23] I'm I'm just doing straight from my HTTP
[35:24] history a lot of times.
[35:25] >> Yeah. Okay.
[35:26] >> Yeah.
[35:27] Yeah, that makes sense. That's good.
[35:29] Yeah, so but like it What is it What are
[35:31] the other, I guess, like 80/20 pieces of
[35:33] like
[35:34] uh
[35:35] you know, you're going to get very
[35:36] outsized returns. I I've gotten very
[35:38] outsized returns by hooking it into
[35:39] Kaito. I think that's, you know,
[35:41] amazing.
[35:42] >> Yeah, so I I think I think the biggest
[35:44] second thing that everyone has to do, I
[35:47] guess it's two things. One is update
[35:49] your Cloud MD for just like contextual
[35:51] information about you because it's going
[35:52] to make it not reject you as much. Like
[35:54] you just need to say in your Cloud MD
[35:56] you don't have to tell it its name, but
[35:57] you can just say like, "Hey, I'm a bug
[35:58] bounty hunter. I do ethical testing.
[36:00] Anything I ask you to look at will be in
[36:02] scope, but make sure you like attempt to
[36:04] stay in scope because it's been going
[36:05] out of scope sometimes lately."
[36:07] Non-destructive actions.
[36:09] Yeah, yeah. Don't do not uh destructive
[36:10] actions unless it's accounts that you
[36:12] know we own because it's like, you know,
[36:13] I told you that it's two accounts that
[36:14] we own that are in Kaito or whatever.
[36:16] And and then the second big thing is
[36:19] just the note structure. And um I was
[36:22] going to do an episode where I talk
[36:24] maybe more deeply about it, but just
[36:25] right now my intuition says that the
[36:27] best way to categorize things is like
[36:29] notes, leads, and leads can be {slash}
[36:32] interesting findings {slash} whatever,
[36:34] and then gadgets or primitives. I think
[36:35] the word primitive might be more
[36:37] specific for what's in the training set,
[36:39] so maybe call it primitives. Then then
[36:41] findings, and then I have a validator. I
[36:44] think you should probably write a
[36:45] validator. Basically, the information
[36:47] you want to give the validator is things
[36:48] like, "Hey, CORS issues are often false
[36:50] positives. BXSS, unless you actually get
[36:53] a trigger to our actual like trigger
[36:55] output isn't a valid finding just
[36:57] because it bypasses the WAF."
[37:00] And when you go to validate this bug, be
[37:02] skeptical. Don't mark everything as a
[37:04] critical or a high. In general, I think
[37:06] these are lows, these are mediums, these
[37:07] are highs. I give it really give it real
[37:09] examples of these bugs. And then and
[37:11] then you have the validator there maybe
[37:12] as a skill
[37:13] or maybe as a as a sub agent or just as
[37:15] a tool.
[37:16] >> I was going to say that's probably a
[37:18] good, you know, we we were talking about
[37:20] the before we got on air, like the
[37:21] difference between skills and agents,
[37:22] and you were saying you don't use agents
[37:24] actually very much at all. That might be
[37:25] a good
[37:26] use case for an agent because you want
[37:28] it to be unbiased by the other
[37:30] information, you know? I I like that.
[37:32] Yeah. Yeah, and so in the and then so I
[37:34] have a validator and then I have what's
[37:35] called reports. So my hierarchy is
[37:37] basically notes, leads, gadgets,
[37:41] findings, reports. And it kind of flows
[37:43] in like a really nice way where there's
[37:45] more at the bottom. It should take notes
[37:46] on all kinds of stuff, and then it
[37:48] should, you know, some of those will be
[37:50] gadgets. Some of those or sorry, some of
[37:52] those will be leads or gadgets, and then
[37:53] some of those will become findings, and
[37:54] then some of those will become reports.
[37:56] And so it's like a funnel.
[37:57] Nice. I like that, dude. That's a good
[37:59] That's a good structure.
[38:00] >> Yeah, so our so our so our three-pronged
[38:01] attack based on your your question just
[38:03] to re- reframe it for everybody is
[38:04] basically you you you need a Kaito
[38:05] skill.
[38:06] You need You need a Cloud MD that talks
[38:08] about how you're doing bug bounty
[38:09] hunting, stay in scope, don't do
[38:10] destructive actions, always take notes,
[38:12] and then you need to tell it where to
[38:14] take notes, right? Write in this
[38:15] database or write in this Notion. I know
[38:17] Grapnel loves Notion, so he has it write
[38:18] to Notion. Some people love Obsidian, so
[38:20] put it in these Obsidian notes so you
[38:21] can go back and reference them.
[38:23] Um or or or actually push it to an API,
[38:25] right? Like so one thing I've been
[38:26] thinking about doing is just creating
[38:28] like a API.rez.com
[38:30] and having it right there, so that
[38:32] whether it's on my VPS or my personal
[38:33] machine, all leads and gadgets go there.
[38:36] And so now, no matter where I'm hacking
[38:38] from, I I have access to those gadgets
[38:40] and Claude has access to those gadgets.
[38:44] That's pretty freaking good, dude.
[38:46] That's pretty freaking good.
[38:48] Yeah.
[38:48] >> Yeah. Okay.
[38:49] All right. So, let's let's talk about
[38:51] orchestration a little bit. Um so, we
[38:55] another component of this is like, okay,
[38:57] obviously
[38:58] seriously, listeners, you must be using
[39:01] Claude code to pair hack with you. Like,
[39:03] that is not really something that you
[39:06] can avoid doing at this point.
[39:08] >> Yeah, I I I've I've also not posted
[39:09] about many other people who message me
[39:11] and say, "Thank you so much. Just found
[39:13] my first bug. Thank you so much. I just
[39:15] escalated my, you know, blind SSRF into
[39:17] a full read. Thank you so much. Like, I
[39:19] found 10 bugs in the last week." I'm not
[39:21] joking.
[39:22] Um actually, yeah, well, actually, I
[39:23] won't make him believe it. Basically,
[39:24] somebody you know really well
[39:25] uh messaged me and was like, "I found 10
[39:27] highs and crits in the last week by
[39:28] using Claude code."
[39:30] That's crazy, man. That's crazy. Yeah, I
[39:31] think I knew who you were talking about.
[39:32] Well, we'll compare afterwards. Um but,
[39:35] yeah,
[39:36] that's I think something everybody must
[39:38] be doing.
[39:39] Um
[39:40] one of the problems that you run into is
[39:42] how do you make it be persistent? Like,
[39:44] how do you force it? I know that you
[39:46] you've mentioned some Ralph loop or
[39:48] something like that. Um
[39:51] and I've seen I think solution by
[39:52] Karpathy at one point. Uh do you have
[39:56] any best practices you want to shout out
[39:58] there on that?
[39:59] >> Sure. This isn't any secret. In fact, I
[40:00] think I've even tweeted this. I mean,
[40:02] you can just tell it, "I'm going to bed.
[40:03] Don't ask me for any questions." Every
[40:05] time I've done that, it's ran for 4-plus
[40:07] hours. So, it's like Really?
[40:09] >> Yeah, there's there's no secret here.
[40:10] It's just you just say, "Hey, I'm
[40:12] walking away. Don't ask me for any input
[40:14] and don't stop hacking. Like, I want you
[40:16] to keep going, keep going deeper, keep
[40:18] finding more bugs. Just literally give
[40:19] it that prompt and it won't it will not
[40:20] stop for hours.
[40:23] That's very surprising.
[40:24] Really? That's interesting. Yeah, I I
[40:26] didn't expect it to be that
[40:28] straightforward cuz I thought that would
[40:29] get like compacted away or something. I
[40:31] don't know. You know, it does get
[40:32] compacted. So, I guess maybe it is
[40:33] working cuz I have a good Claude MD.
[40:35] But, you should just tell I mean, if you
[40:36] want to, you can be like, "Hey, I'm
[40:37] walking away. You're going to end up
[40:39] compacting. So, just keep good notes
[40:40] about where you were and what you were
[40:41] doing." But, in general, I think that's
[40:43] kind of already built into their compact
[40:44] um script.
[40:46] Or to their compact prompt.
[40:47] >> it. It might survive it, you know, it
[40:49] might just say like when it's
[40:50] compacting, it might be like, "Oh, I It
[40:52] writes itself a big new prompt to start.
[40:53] And so, it does survive most of the
[40:55] time. Uh this is actually a really great
[40:56] tip for the listener. I probably also
[40:58] shouldn't share, but um
[41:00] on those compaction loops,
[41:01] if when it comes out of compaction,
[41:04] it reaches a context limit before
[41:06] there's any steps in between, it can't
[41:08] like roll back or compact. That happens
[41:11] most likely when you have sub agents
[41:13] with a like a lot of sub agents. So, my
[41:15] personal fix is to tell it not to use
[41:17] more than two to three sub agents.
[41:18] Anytime it spawned four or more, I end
[41:20] up getting into um a place where it
[41:22] can't compact. And I can't go back and
[41:24] have it not compact because whenever you
[41:26] go back to redo that to like jump back a
[41:28] few loops, you have to hit like escape
[41:29] twice and you go up. And then you press
[41:31] up and you go to like a separate chat.
[41:33] But, when it's running autonomously
[41:34] overnight or whatever, you can't go up.
[41:36] And when it compacts, there's no there's
[41:38] no message to jump back to. And so, then
[41:40] you're in the situation where you have
[41:41] to detangle it. And for me, I then have
[41:43] to open a new instance and tell it to go
[41:44] read all the context from this other
[41:46] session and get all the context it needs
[41:47] to get started again. So, my in my
[41:49] experience, the best way to limit that,
[41:51] especially if you're going to run
[41:51] overnight, is to be like, "Don't use
[41:53] more than two sub agents."
[41:55] Mhm. Mhm. Okay. All right. That's a
[41:57] That's a good That's a good point. I
[41:59] think uh
[42:00] I haven't run into that issue, which
[42:01] means I'm probably not using it
[42:03] properly. Yeah, I do No, no, I think
[42:04] we're I think you you often just like
[42:06] have four separate instances. So,
[42:08] they're probably not using sub agents
[42:10] that much. And you're also interacting
[42:11] with it often. You're not like having it
[42:13] run overnight. So, those are the two
[42:14] reasons.
[42:14] >> You're running everything from Discord,
[42:16] right? You don't really interact with
[42:17] the the like Cloud Code online as often,
[42:21] right?
[42:21] >> I would say there I have basically three
[42:23] modes. Um I'm I'm okay to share this, I
[42:26] think. One is I code hack with Cloud
[42:29] Code on my desktop, and I do that a lot,
[42:31] and I do that all through iTerm, just
[42:33] through the terminal in the normal Cloud
[42:35] Code CLI. That's probably, let's say,
[42:38] 50% of my usage.
[42:40] Um and then the other 50%, yeah, I I
[42:42] have like a Discord bot that basically
[42:44] mimics Cloud Code in in like a Discord
[42:46] thread, and I use that anytime I'm doing
[42:49] stuff on my VPS.
[42:50] Um and then it's a very similar setup
[42:53] for the automated bot that I've created
[42:55] that, you know, I use with JD. And we um
[42:59] yeah, same it's all through Discord.
[43:01] It's all managed through Discord.
[43:03] Mhm. I just find it so much nicer. Like,
[43:05] I'm in Kids Car Line. I'm, you know,
[43:08] >> Yeah. I'm doing my business.
[43:10] >> that I struggle with, yeah, with my
[43:12] setup, which is just tmux four panes,
[43:14] you know, let's go. All working on
[43:16] different stuff. By the time I'm done
[43:17] prompting one of them, the other one's
[43:19] done, and I can just kind of jump jump
[43:20] jump jump jump.
[43:22] >> Um but yeah, the remote control
[43:24] functionality is is getting better, but
[43:26] it's not perfect, you know? Um so, it's
[43:30] crazy. I think I talked about it on the
[43:31] pod last week, and it's already better,
[43:33] you know? Like, they're already Yeah, oh
[43:35] yeah. Yeah, it is better. For sure. It's
[43:37] not perfect, but it is better. So, if
[43:39] anybody, I know you were asking me, and
[43:40] I didn't have a good answer to this
[43:42] before the pod started. If anyone's
[43:43] using Cloud Code in the desktop app, I
[43:45] think there's probably some like really
[43:46] big wins there. Like, I don't like that
[43:49] when you hit control O, it only shows
[43:51] you the output from the most recent
[43:52] command. You can't go up and see the
[43:53] output from like previous commands. And
[43:55] then sometimes I hit control O, and my
[43:56] computer will just like lock up because
[43:58] I think it's trying to load like a
[44:00] bajillion, you know, characters from
[44:02] like a bunch of different output over
[44:04] there. And so, yeah, um
[44:06] the Primeagen, though, is like a you
[44:08] know, if people don't know, he's like a
[44:09] software dev influencer, and he's really
[44:11] funny and really great, but he is always
[44:13] making fun of how bad their TUI is. I've
[44:15] heard that open open code is much
[44:17] better, but I
[44:19] but back whenever they like stopped
[44:21] allowing Cloud Code to be used in
[44:22] third-party services or something, I
[44:23] never I never went down that route and
[44:25] figured it out, but yeah. Yeah, the
[44:27] subsidization is OP, man. It really is.
[44:29] That's one thing that we were even
[44:30] talking about with with Shift. Like, I
[44:32] think Shift is super good in Caido,
[44:34] but the the problem is it you know,
[44:38] isn't free. And I'm just so like hooked
[44:40] on this crack of like, I don't even have
[44:42] to think about the tokens cuz Cloud
[44:43] Cloud Max is like, you know, 20 bucks,
[44:45] and then I'm I'm good, you know?
[44:48] Um, so yeah, it is it is uh it is really
[44:51] crazy that
[44:53] Cloud Code is has that market cornered
[44:55] because of the the subsidization.
[44:58] Um, all right, man. Um, let's just talk
[45:01] Well, first I I think we should go back
[45:03] and summarize everything that what we
[45:04] what we just said here. Okay? So, here's
[45:06] here's what I understand about the best
[45:08] practices that you mentioned on this
[45:10] pod, and you can interject whenever you
[45:13] want and give me your thoughts, okay?
[45:15] So, here we go. First, we need to be,
[45:17] you know, pair hacking with with Cloud.
[45:19] We have to. We must. And one of the uh
[45:23] highest value things that you can do to
[45:25] do that is get the Caido mode skill. Get
[45:27] it hooked into Caido. Get it using your
[45:28] proxy so you can see what it's doing and
[45:31] adding uh value, you know, handing
[45:32] things off to you, right? And making
[45:34] things easier for you to hack with,
[45:35] right? What What I'll often do with it,
[45:37] hand it a bunch of JavaScript files,
[45:38] recreate all of these HTTP requests in
[45:41] Caido replay sessions. Boom. You know,
[45:43] it's beautiful. Um,
[45:45] so that that's one one thing. The other
[45:47] thing is giving it a note structure that
[45:49] it can use. So, we've got notes, you got
[45:51] leads, you got um primitives, and then
[45:53] you've got reports. And and giving it
[45:55] that structure so it knows how to store
[45:59] information in a way that you can digest
[46:01] well. Yeah, for hacking locally, if
[46:02] you're hacking locally and not remotely,
[46:04] uh I didn't even think about this. I
[46:06] definitely should have mentioned it. The
[46:07] Kaito skill actually lets you pipe
[46:09] straight to the findings tab. So, you
[46:11] can just have it go So, when you're
[46:12] hacking it, you'll get the little red
[46:13] dot and then you'll know to look. Yeah.
[46:15] That's a good That's a good call as
[46:16] well.
[46:18] And then we're building skills. Skills
[46:20] are either pieces of information or
[46:22] tools or both that Claude can use and
[46:26] will rag into context as needed.
[46:28] Don't Yeah, ragging doesn't use rag
[46:31] there.
[46:32] Rag is almost
[46:33] Interesting. Yeah, I It might if you
[46:35] have above a certain amount, but I think
[46:38] like up to at least 35 or 50 or
[46:40] something, it it basically sees the
[46:42] front matter. So, you actually huge tip,
[46:44] sorry. Huge tip we should have mentioned
[46:46] already. The front matter for skills in
[46:48] the skill.md file has a description and
[46:52] a name. That's what is auto injected
[46:54] into the context when you launch Claude.
[46:57] Okay. So, if you So, if you have rules
[46:59] like use this skill when, put that in
[47:01] the description of the front matter at
[47:02] the top of the skill.md
[47:05] for your skills. And that is auto
[47:06] injected at execution time into the into
[47:10] the prompt like the system prompt that
[47:12] it uses. That's not happening at the LLM
[47:14] level, right? Like with rag. It is
[47:16] happening at load of skill level, which
[47:18] makes sense cuz that's why we see it
[47:20] load of skill, you know, okay, okay. I
[47:23] understand. Usually people say Usually
[47:24] when people say rag, they mean like
[47:26] embeddings based search. And by default
[47:29] Claude code doesn't do any embeddings
[47:31] based search that I know of.
[47:32] Okay, nice.
[47:34] So, we load these skills up. These
[47:36] skills give us information and tools to
[47:39] do things and we want to try to do this
[47:41] when Claude does not have access to
[47:45] specific pieces of information or
[47:46] specific ways that we want it done.
[47:48] That's right.
[47:49] You know, we certainly can give it
[47:53] ways to do things if we want assurance
[47:55] that it will actually try those things.
[47:56] But we should also caveat it at the end
[47:58] of whatever skills MD file or whatever
[48:00] with
[48:01] hey, but
[48:03] use your creativity as well. Don't be
[48:05] like cornered by this skill, right? Does
[48:07] that make Is that Is that accurate?
[48:08] That's exactly right. Okay. I wonder I
[48:11] wonder what the impact of these
[48:13] cumulative tips will have on everyone's
[48:16] act bots.
[48:18] Um okay, and then you know, last piece
[48:20] is like give it information
[48:23] about you and and how you need things
[48:26] done. So, you know, creds to your VPS,
[48:29] you know, to a you know, cornered little
[48:32] document root or whatever.
[48:34] Um you know, that that's sort of thing.
[48:36] And so, it knows how to like host things
[48:38] or
[48:39] um
[48:41] present information in a way that is is
[48:42] good for you, right? It's sort of
[48:44] aligned with the notes thing, but giving
[48:45] it more giving it access to things that
[48:48] you want it to be able to access for the
[48:49] specific mission. Like, okay, here are
[48:51] my creds to this, you know, app that I
[48:53] want you to hack. Here are these, you
[48:55] know, cookies that I want you to use.
[48:57] That sort of thing. Um
[48:59] and and that could be at runtime, right?
[49:02] Via the prompt or it could be in the
[49:03] skills as well. That's right.
[49:06] All right, man.
[49:07] All right, let's do this. Let's do this
[49:09] [ __ ] All right.
[49:09] >> Well, so one thing that we didn't
[49:11] mention yet that I know we talked about
[49:12] potentially mentioning is
[49:15] um agents versus folders.
[49:17] You want to talk about that? Okay, yeah.
[49:19] Yeah, let's do it. Yep. Mhm. So, in my
[49:22] opinion, you like and in most people's
[49:25] opinion, No, explain that first. What do
[49:26] you mean agents versus folders? Yeah, so
[49:29] one thing we didn't really talk about,
[49:30] but some of the major components are
[49:31] like agents, which agents, if anyone
[49:34] doesn't know, in Claude code are and
[49:37] this is probably true in Codex, I'm not
[49:39] sure, but agents are a specific system
[49:41] prompt
[49:42] with a specific set of skills or even
[49:44] tools like command line tools that it's
[49:46] like white listed to use.
[49:49] And
[49:50] um because of that, you can make like a,
[49:53] you know, pen tester agent. If if you're
[49:56] going to be using Cloud Code for lots of
[49:57] stuff, like finances and, you know, PDFs
[50:00] and other other junk, but you're also
[50:02] going to be use it for pen testing, you
[50:03] could use a pen tester agent or like bug
[50:05] bounty agent for that. Alternatively,
[50:08] and I think this is the method that I
[50:09] like slightly prefer, you can you can
[50:11] launch Cloud Code out of a folder on
[50:14] your computer and in that folder, your
[50:18] dot Cloud folder will only be loaded if
[50:20] you're in that folder. So, the way that
[50:22] Cloud Code works is you have in your
[50:24] home directory or whatever wherever you
[50:25] saved it off as like your main Cloud
[50:27] directory,
[50:28] you have a dot Cloud folder which
[50:30] includes like a Cloud MD and skills and
[50:32] agents, right? But then if you're in a
[50:33] sub folder, it looks there first and
[50:35] includes that as well as the parent
[50:37] folder. So, you know, if you put in your
[50:39] home dot Cloud MD, you know, this is my
[50:41] home, and then you put in a, you know,
[50:43] another folder in the dot Cloud Cloud
[50:45] MD, this is the folder, and then you
[50:47] were able to go and you like proxy the
[50:49] traffic, it would have both of those in
[50:50] the context if you launched it from that
[50:52] folder. So, Okay. This has this has like
[50:55] two ways that it can be used positively
[50:57] by our listeners. One is you could have
[50:59] a bug bounty folder where you are a
[51:02] hacking folder where you load all of
[51:04] your skills and your and your custom
[51:05] prompts, and if you launch it out of
[51:07] your home directory, it won't have all
[51:08] that. So, you can like use it for normal
[51:09] day-to-day stuff that's not hacking. But
[51:11] if you launch it from inside that
[51:12] folder, it will have those things. Um,
[51:14] so that's one way. The other thing you
[51:16] could do um, is have a target is like
[51:20] launch Cloud Code from a target specific
[51:22] folder and have its Cloud MD have the
[51:25] information the top level information
[51:26] about that target. So, you could have
[51:28] like a a flow where anytime you say
[51:30] like, "Okay, I want to start hacking on
[51:31] X." The first thing Cloud does is go and
[51:34] create a target folder for that target
[51:36] and then goes and pulls the policy page
[51:38] from HackerOne or whatever and puts that
[51:39] policy in the Cloud MD in that folder.
[51:41] So, then when you launch it from that
[51:42] folder later, it now has that target
[51:44] specific information loaded in
[51:46] automatically.
[51:50] Dude.
[51:51] Oh gosh, there's so much possibilities
[51:53] with this. My as you're talking my brain
[51:55] is just sitting I feel I feel like I
[51:56] kind of you know, normally I'm like
[51:58] guiding the conversation and and you
[52:00] know, leading hosting on this podcast,
[52:02] but as you start talking about these
[52:03] things, I just sit here and I start
[52:05] churning.
[52:06] You know, and and my brain's like this
[52:07] is what you're going to do right after
[52:08] you get off this freaking podcast, you
[52:10] know, like
[52:11] I was just like oh [ __ ] Okay. Oh no.
[52:14] So, anyway, thanks for thanks for
[52:16] sharing all that information. Um you
[52:18] know, there's a couple more things that
[52:19] we could do here, but I actually want
[52:21] the you know, extra 10 minutes back to
[52:24] uh to go and actually implement some of
[52:26] this stuff. So, let's let's cut it here
[52:28] and let's let's get in the HTTP
[52:29] requests. Perfect. All right. Peace,
[52:32] man. Peace.
[52:34] And that's a wrap on this episode of
[52:36] Critical Thinking. Thanks so much for
[52:37] watching to the end, y'all. If you want
[52:39] more Critical Thinking content or if you
[52:41] want to support the show, head over to
[52:42] ctbb.show/discord.
[52:44] You can hop in the community. There's
[52:45] lots of great high-level hacking
[52:47] discussion happening there on top of the
[52:49] masterclasses, hackalongs, exclusive
[52:51] content, and a full-time hunters guild
[52:53] if you're a full-time hunter. It's a
[52:55] great time, trust me. All right, I'll
[52:57] see you there.
