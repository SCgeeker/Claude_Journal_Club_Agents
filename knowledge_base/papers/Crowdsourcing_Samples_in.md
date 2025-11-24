---
title: Crowdsourcing Samples in
authors: Jesse Chandler, Neil Stewart, Gabriele Paolacci, Cognitive Science, Amazon Mechanical, Crowdsourcing Samples, Data Collection
year: N/A
keywords: 
created: 2025-11-23 18:14:49
---

# Crowdsourcing Samples in

## 基本信息

- **作者**: Jesse Chandler, Neil Stewart, Gabriele Paolacci, Cognitive Science, Amazon Mechanical, Crowdsourcing Samples, Data Collection
- **年份**: N/A
- **關鍵詞**: 

## 摘要

None

## 研究背景

## 研究方法

## 主要結果

## 討論與結論

## 個人評論

## 相關文獻

## 完整內容

Review
Crowdsourcing Samples in
Cognitive Science
Neil Stewart,1,* Jesse Chandler,2,3 and Gabriele Paolacci4
Crowdsourcing data collection from research participants recruited from
online labor markets is now common in cognitive science. We review who
is in the crowd and who can be reached by the average laboratory. We discuss
reproducibility and review some recent methodological innovations for online
experiments. We consider the design of research studies and arising ethical
issues. We review how to code experiments for the web, what is known about
video and audio presentation, and the measurement of reaction times. We
close with comments about the high levels of experience of many participants
and an emerging tragedy of the commons.
Data Collection Marketplaces
Online labor markets have become enormously popular as a source of research participants
in the cognitive sciences. These marketplaces match researchers with participants who
complete research studies in exchange for money. Originally, these marketplaces fulfilled the
demand for large-scale data generation, cleaning, and transformation jobs that require
human intelligence. However, one such marketplace, Amazon Mechanical Turk (MTurk),
became a popular source of convenience samples for cognitive science research (MTurk
terms are listed in Box 1). Based upon searches of the full article text, we find that in 2017,
24% of articles in Cognition, 29% of articles in Cognitive Psychology, 31% of articles in
Cognitive Science, and 11% of articles in Journal of Experimental Psychology: Learning,
Memory, and Cognition mention MTurk or another marketplace, all up from 5% or fewer five
years ago.
Although researchers have used the internet to collect convenience samples for decades [1],
MTurk allowed an exponential-like growth of online experimentation by solving several
logistical problems inherent to recruiting research participants online. Marketplaces like
MTurk aggregate working opportunities and workers, ensuring that there is a critical mass
of available participants, which increases the speed at which data can be collected.
Moreover, these marketplaces incorporate reputation systems that incentivize conscientious
participation, as well as a secure payment infrastructure that simplifies participant
compensation. Although marketing research companies provide similar services, they are
often prohibitively expensive [2,3]. Online labor markets allow participants to be recruited
directly for a fraction of the cost.
Academic interest in MTurk began in computer science, which used crowdsourcing to perform
human intelligence tasks (HITs) such as transcription, developing training data sets, validating
machine learning algorithms, and to engage in human factors research [4]. From there, MTurk
diffused to subdisciplines of psychology such as decision making [5] and personality and social
psychology [6]. Use of MTurk then radiated out to other social science disciplines such as
economics [7], political science [2], and sociology [8], and to applied fields such as clinical
science [9], marketing [10], accounting [11], and management
Trends
In
[12].
the next few years we estimate
nearly half of all cognitive science
research articles will involve samples
of participants from Amazon Mechan-
ical Turk and other crowdsourcing
platforms.
We review the technical aspects of
programming for the web and the
resources available to experimenters.
Crowdsourcing of participants offers a
ready and very different complement
to the traditional college student sam-
ples, and much is now known about
the reproducibility of findings with
crowdsourced samples.
The population which we are sampling
from is surprisingly small and highly
experienced in cognitive science
experiments, and this non-naïveté
affects responses to frequently used
measures.
The larger sample sizes that crowd-
sourcing affords bode well for addres-
sing aspects of the replication crisis,
but a possible tragedy of the commons
looms now that cognitive scientists
increasingly share the same
participants.
1Warwick Business School, University
of Warwick, Coventry, CV4 7AL, UK
2Mathematica Policy Research, Ann
Arbor, MI, 48103, USA
3Research Center for Group
Dynamics, University of Michigan, Ann
Arbor, MI 48106, USA
4Rotterdam School of Management,
Erasmus University Rotterdam, 3062
PA, Rotterdam, The Netherlands
*Correspondence:
Neil.Stewart@wbs.ac.uk (N. Stewart).
736 Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10 http://dx.doi.org/10.1016/j.tics.2017.06.007
© 2017 The Author(s). Published by Elsevier Ltd. This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).

Across fields, research using online labor markets has typically taken the form of short,
cross-sectional surveys conducted across the entire crowd population or on a specific
geographic subpopulation (e.g., US residents). However, online labor markets are fairly
flexible, and allow creative and sophisticated research methods (Box 2) limited only by
the imaginations of researchers and their willingness to learn basic computer programming
(Box 3). Accurate timing allows a wide range of paradigms from cognitive science to be
implemented online (Box 4). Recently, several new tools (e.g., TurkPrime) and competitor
marketplaces have developed more advanced sampling features while lowering technical
barriers substantially.
MTurk is by far the dominant player in academic research and has been extensively validated.
However, early evaluations of competitor platforms such as Clickworker [13], Crowdworks [14],
Crowdflower [15], Microworkers [13,16,17], and Prolific (which focuses on academic research
specifically) [17] have been encouraging, and are plausible alternatives for researchers.
Who Is in the Crowd?
Who is in the crowd we are sampling from? Crowds are defined by their openness to virtually
anyone who wishes to participate [18]. Because crowds are not selected purposefully, they do
not represent any particular population and tend to vary in terms of national representation:
MTurk consists mostly of Americans and Indians; Prolific and Clickworker have larger European
populations; Microworkers claims a large South-East Asian population [19], and CrowdWorks
has a primarily Japanese population
Box
[14].
1. MTurk Terms
Approval/rejection: once a worker completes a HIT, a requester can choose whether to approve the HIT (and
compensate the worker with the reward) or reject the HIT (and not compensate the worker).
Block: a requester can ‘block’ workers and disqualify them from any future task they post. Workers are banned from
MTurk after an unspecified number of blocks.
Command line tools: a set of instructions that can be input in Python to send instructions to MTurk via its application
programming interface (API) [90].
HIT approval ratio: the ratio between the number of approved tasks and the number of total tasks completed by a
worker in her history. Until a worker completes 100 HITs, this is set at a 100% approval ratio on MTurk.
Human intelligence task (HIT): a task posted on MTurk by a requester for completion by a worker.
Qualifications: requirements that a requester sets for workers to be eligible to complete a given HIT. Some
qualifications are assigned by Amazon and are available to all requesters. Requesters can also create their own
qualifications.
Requesters: people or companies who post HITs on MTurk for workers to complete.
Reward: the compensation promised to workers who successfully complete a HIT.
Turkopticon: a website where workers rate requesters based on several criteria.
TurkPrime: one among the websites that augments or automates the use of several MTurk features [77].
Worker file: a comma-separated values (CSV) file downloadable by the requester with a list of all workers who have
completed at least one task for the requester.
Workers: people who subscribe to MTurk to complete HITs in exchange for compensation.
Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10 737

Box 2. Innovative MTurk Research
Infant Attention
Parents have been recruited on MTurk to record the gaze patterns of their infants using a webcam while the infants
views video clips [78,79]. Some participants were excluded because of technical issues (e.g., the webcam recording
became desynchronized from the video) or because the webcam recording was of insufficient quality to view the eyes of
the infant. However, it was possible to identify the features of videos that attracted infant attention, including singing,
camera zooms, and faces.
Economic Games
Many economic games have been run on MTurk, including social dilemma games and the prisoner's dilemma [69]. The
innovation here was to have remotely located participants playing live against one another, where one person's decision
affects the outcome that another receives, and vice versa. Software platforms to implement economic games include
Lioness [80] and NodeGame [81].
Crowd Creativity
Several researchers have assembled groups of workers to engage in iterative creative tasks [82]. More recently, workers
have collaboratively written short stories, and changes in the task structure influence the end-results [83]. The innovation
here was using microtasks to decompose tasks into smaller subtasks and explore how changes to the structure of
these tasks changes group output.
Transactive Crowds
Several researchers have looked at how crowds can be used to supplement or replace individual cognitive abilities. For
example, MTurk workers have provided cognitive reappraisals in response to the negative thoughts of other workers
[84], and an app has been developed to allow people with visual impairments to upload images and receive near real-
time descriptions of their contents [85]. The innovation here was to allow workers to engage in tasks in contexts that are
unsupervised, have little structure, and occur in near real-time.
Workers as Field Researchers
Meier et al. [86] asked participants take pictures of their thermostats and upload them to determine whether they were
set correctly. The innovation here was using workers to collect field data about their local environment and relay it back
to the researchers.
Mechanical Diary
Mechanical Turk allows researchers to recontact workers multiple times, allowing longitudinal research. Boynton and
Richman [87] used this functionality to conduct a 2 week daily diary study of alcohol consumption.
Time of Day
It is also easier to test workers at different times of day (e.g., 03:00 h), without the disruption of a visit to the laboratory.
Using judgments from a line bisection task, Dorrian et al. [88] found that spatial attention moved rightwards in peak
compared to off-peak times of day, but only for morning types not evening types.
Crowds as Research Assistants
Online labor markets were originally created to facilitate human computation tasks such as content coding for which
academics have traditionally relied upon research assistants. Crowds often produce responses that are equivalent or
superior to the judgments of experts. For example, Benoit et al. [89] used MTurk to rate the ideology of statements from
political texts: they found that 15 workers produce ratings of equivalent quality to five political science PhD students and
faculty. Importantly, crowds can return data exceptionally quickly: workers were able to content code 22 000 sentences
in under 5 h for $360.
738 Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10

Box 3. Coding for Crowdsourcing
MTurk is accessible through a graphical user interface (GUI) that can perform most of platform functions either directly or
through downloading, modifying and reuploading worker files. MTurk can also be accessed by command line tools that
can simplify tasks such as contacting workers in bulk or assigning variable bonuses. More recently, TurkPrime has
developed an alternative GUI that offers an extended set of features.
It is possible to code and field simple survey experiments entirely within the MTurk platform using HTML5, but
functionality is limited. Most researchers create a HIT with a link to an externally hosted survey and a text box in
which the worker can paste a confirmation code upon completing the study. Simple surveys might be conducted using
a variety of online platforms, such as Google forms or www.surveymonkey.co.uk, which require no programming skills.
Surveys with more complex designs (e.g., complex randomization of blocks and items) may benefit from using Qualtrics,
which also requires minimal programming skill. Researchers can also direct users to specialized platforms designed to
program reaction-time experiments or group interactions.
Researchers with complex designs or who wish to include a high degree of customization can program their own
surveys. Early web-based experiments were often coded in Java or Flash, but these languages are now largely obsolete,
being unavailable on some platforms and switched off by default and having warning messages on others. Most web
experiments are now developed using HTML5, JavaScript (which is not Java), and CSS – the three core technologies
behind most Web pages. Broadly, HTML5 provides the content, the CSS provides the styling, and JavaScript provides
the interaction. Directly coding using these technologies provides considerable flexibility, allowing presentation of
animations, video, and audio content [91,92]. There are also advanced libraries and platforms to assist, including www.
jsPsych.org which requires minimal programming [93], the online platform www.psiturk.org [94], www.psytoolkit.org
which allows online or offline development [95,96], and Flash-based scriptingRT [97].
Web pages are not displayed in the same way across all common browsers, and so far not all browsers support all of the
features of HTML5, JavaScript, and CSS. Further, the variety of browsers, browser versions, operating systems,
hardware, and platforms (e.g., PC, tablet, phone) is considerable. It is certainly important to test a web-based
experiment across many platforms, especially if the exact details of presentation and timing are important. Libraries
such as jQuery can help to overcome some of the cross-platform difficulties.
Box 4. Online Reaction Times
Many cognitive science experiments require accurate measurement of reaction times. Originally these were recorded
using specialist hardware, but the advent of the PC allowed recording of millisecond-accurate reaction times. It is now
possible to measure reaction times sufficiently accurately in web experiments using HTML5 and Javascript. Alter-
natively, MTurk currently permits the downloading of software which allows products such as Inquisit Web to be used to
record reaction times independently of the browser.
Reimers and Stewart [91] tested 20 different PCs with different processors and graphics cards, as well as a variety of MS
Windows operating systems and browsers using the Black Box Toolkit. They compared tests of display duration and
response timing using web experiments coded in Flash and HTML5. The variability in display and response times was
mainly due to hardware and operating system differences, and not to Flash/HTML5 differences. All systems presented a
stimulus intended to be 150 ms for too long, typically by 5–25 ms, but sometimes by 100 ms. Furthermore, all systems
overestimated response times by between 30–100 ms and had trial-to-trial variability with a standard deviation of 6–
17 ms (see also [35]). If video and audio must be synchronized, this might be a problem. There are large stimulus onset
asynchronies of (cid:1)40 ms across different hardware and browsers, with audio lagging behind video [92]. Results for older
Macintosh computers are similar [98].
The measurement error added by running cognitive science experiments online is, perhaps surprisingly, not that
important [99]. Reimers and Stewart simulated a between-participants experiment comparing two conditions with a
known 50 ms effect size. Despite the considerable variability introduced by the (simulated) hardware differences across
(simulated) participants, only 10% more participants are necessary to maintain the same power as in the counterfactual
experiment with zero hardware bias and variability [91]. In the more usual within-participants experiment, where the
constant biasing of response times cancels the difference between conditions, there is no effective loss from hardware
differences (see also [100]). Accuracy is higher using the Web Audio API [92]. Reaction-time data have been collected
and compared in the lab and online, with similar results for lexical decision and word-identification times, and Stroop,
flanker, Simon, Posner cuing, visual search, and attentional blink experiments [36,37,101,102].
Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10 739

The most popular (and thus best-understood) crowdsourced population, US MTurk workers, is
more diverse than college student samples or other online convenience samples [2,20],
although not representative of the US population as a whole. It is biased in ways that might
be expected of internet users. Direct comparisons of MTurk samples to representative samples
suggest that workers tend to be younger and more educated, but report lower incomes and are
more likely to be unemployed or underemployed. European- and Asian-Americans are over-
represented, and Hispanics of all races and African Americans are under-represented. Workers
are also less religious and more liberal than the population as a whole (for large-scale
comparisons to the US adult population see [21,22]).
Although representativeness is typically discussed in terms of demographic differences, MTurk
workers may also have a different psychological profile to that of respondents from other
commonly used samples. Workers tend to score higher on learning goal orientation [23] and
need for cognition [2]. They also display a cluster of inter-related personality and social-cognitive
differences: workers report more social anxiety [9,24] and are more introverted than both college
students [23,25,26] and the population as a whole [21]. They are also less tolerant of physical and
psychological discomfort than college students [24,27,28], and more neurotic than other samples
[21,23,25,26]. Workers also tend to score higher on traits associated with autism spectrum
disorders, which tend to be correlated with the other dispositions mentioned here [29].
Sampling from the Crowd
Who is in your sample? In the same way as workers who opt into a crowd are not representative
of any particular population, workers who complete any given study may not be representative
of the worker population as a whole. Instead, they represent some subset of the worker
population that decides to complete a given task. Sometimes large differences in sample
composition are observed, even between studies with several thousand respondents [29].
Because of the potential differences, we make reporting recommendations (Box 5). Several
Box 5. Crowdsourcing Checklist for Authors, Reviewers, and Editors
Research studies need to adequately describe their methods, including the sample they use, to maximize the
replicability of their results. We highlight features below that are unique or have increased relevance for MTurk. The
list is intended to be suggestive, not mandatory, but it is probably not sufficient simply to report that a study was ‘run on
MTurk’.
Collected automatically by MTurk or set by the experimenter:
(i) Qualifications required to take the HIT: country of residence, minimum HIT approval ratio or number of previously
completed HITs, and any other custom qualifications. The sample that completes a HIT can differ dramatically
depending on the qualifications used. For example, country of residence and HIT approval ratio have large effects
on the resulting data quality [17,29].
(ii) Properties of the HIT preview which affect which workers take the HIT: reward offered, any bonus pay, and stated
duration. Participant experience in the study begins with the decision to accept a HIT. If study materials are
archived in a repository, a copy of the HIT title and text description should be included.
(iii) The actual duration of the HIT (perhaps median or range) and actual bonus pay.
(iv) Time of day and date for batches of HITs posted. Worker characteristics vary dynamically across time [21,30].
Collected by the experimenter:
(i) Whether workers were prevented from repeating different studies in the same package of studies. Most traditional
subject pools prevent repeated participation by default. MTurk does not, and repeated participation affects
participant responses.
(ii) Attrition rates (because many people can preview the study before accepting the HIT). Attrition rates for MTurk
studies are often assumed to be zero, but are usually higher [103].
(iii) IP addresses, for identifying (reasonably rare [21]) cases of multiple submissions and cases where responses may
not have been independent (e.g., two respondents in the same room).
(iv) Browser agent strings, which contain information about the platform and browser used to complete the study.
(v) Demographics: because samples are not selected randomly by MTurk, the demographics of previous studies on
the platform may not be appropriate.
(vi) Whether participants discovered the experiment on a site outside MTurk, and the URL where they found it, such
that participant discussions about the experiment can be monitored [21].
740 Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10

design features contribute to these differences. For example, researchers set (or forget to set)
qualification requirements on MTurk such as worker nationality (which correlates with English
language comprehension [25,29]), or level of experience and worker reputation (which
correlates with attentiveness [15]).
Other decisions that are not explicitly part of the design of a HIT design can inadvertently influence
sample composition. Research studies are usually available on a ‘first come first served’ basis.
Consequently, survey respondents will vary in characteristics such as personality, ethnicity,
mobile phone use, and level of worker experience as a function of the time of day that a task
is posted [21,30]. Sample composition will also change as sample size increases because HITs
that request fewer workers will fill up more quickly. In particular, small samples tend to over-
represent the savviest workers – who take advantage of software and online communities to
quickly find available work. Workers have self-organized into communities, and those workers
tend to earn more [31]. Small studies that do not restrict workers from completing more than one
study contain a large proportion of non-unique workers (that is, will tend to attract the same group
of workers [32]). Sometimes events beyond researcher control will affect the sample. Studies that
are publicized on online forums (e.g., Reddit) may also return disproportionately young and male
samples [33]. The workers who complete a survey early are also different from workers who
complete later, leading samples to change across data collection [21,30].
Importantly, sampling may occur differently between different marketplaces, depending on
how the marketplaces are designed. MTurk makes tasks available to all eligible participants in
reverse, but other services have sampling policies that prioritize workers with specific char-
acteristics (e.g., experience) above and beyond what is requested by researchers – something
that should be made as clear as possible by service providers.
Reproducibility
Science must be reproducible. We first discuss whether the results obtained from the crowd-
sourced convenience samples can be reproduced in other populations. We then consider
crowdsourcing in the light of the replication crisis.
Reproducible Results
Crowdsourced samples can be used along-side traditional university panel samples. That is, in
addition to our ‘WEIRD’ (Western, educated, industrialized, rich, and democratic) convenience
samples of university students [34], we also have a second and very different convenience
sample of MTurkers (although they too are WEIRD). Numerous studies have found comparable
results when using these different samples. Classical experiments in judgment and decision
making have been consistently replicated [2,5,7], and the psychometric properties of individual
difference scales such as the big five are usually excellent [6,23]. Phenomena observed within
many commonly used cognitive psychology paradigms are also observed within MTurk worker
populations [35–38].
More recent and ambitious efforts that have examined the replicability of research findings
using batteries of experimental studies administered to large samples of MTurk workers and
other individuals have found similarly consistent results. In the many-labs project, the pattern of
effects and null effects for 13 social psychology and decision-making coefficients corre-
sponded perfectly between concurrently collected student and MTurk samples [39]. Similarly
high replication rates have been observed within batteries of cognitive psychology experiments
[36,40]. More than 90% (33/36) of correlations between attitudes and personality measures did
not differ across an MTurk sample and a representative sample collected for the American
National Election Studies [41]. In political science, 82% (32 of 39) of effects and null effects
observed in a high-quality probability sample replicated in an MTurk sample, and the effect
Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10 741

sizes observed across the two samples did not differ from each other in six of the seven
remaining conditions [3]. A more recent study examining 37 coefficients reported a replication
rate of 68% and a cross study correlation of effect sizes of r = 0.83 after correcting for
measurement error [104].
Reproducibility and the Replication Crisis
Many scientists are concerned that there is a ‘replication crisis’ in science, and recently much
effort has gone into fixing research practices [42]. While some researchers are, anecdotally,
somewhat skeptical about online studies, we do not see crowdsourcing as a cause or fix for the
replication crisis. We now consider issues regarding the speed of data collection and sample
size.
It is unclear what effect the ease and speed of running studies on crowdsourcing platforms will
have on reproducibility. On one hand, it could be argued that the ease with which studies can
be run encourages more ‘bad’ (i.e., likely false) ideas to be tested, filling up the file drawer [43]
while also increasing false positives. It could also be argued that the ease of starting and
stopping data collection could influence decisions to continue or extend a study (p-hacking
[44], but see [45]; or take a Bayesian approach [46] but see [47]). On the other hand, lowering
the time and resource costs of being wrong could make it easier for researchers – particularly
those with limited access to participants or facing looming tenure deadlines – to let go of ideas
that are less promising. Further, unlike traditional studies that might collect only a few partic-
ipants per day, data-peeking imposes real-time costs on MTurk for little gain in understanding
how a study is unfolding. Whatever portion of data-peeking is motivated by excitement, rather
than by deliberate attempts at data manipulation, should simply go away if the sole benefit is a
few hours advance notice about the likely outcome of the study. The availability of crowd-
sourced samples cannot be a cause per se of questionable research practices – as with any
tool, it is the responsibility of the researcher to use it in a methodologically sound way.
The efficiency of crowdsourcing also allows larger samples – and we need larger sample sizes
because much research is underpowered [48]. Underpowered studies are likely to uninten-
tionally produce false positives [49,50] and, as sample sizes increase, results become less
sensitive to some forms of researcher degrees of freedom [49]. Large samples are also
important if the field is to move towards estimation of effect sizes [51], rather than merely
null hypothesis significance testing. For example, to estimate a medium effect size and exclude
small and large effects from the confidence intervals, we need samples of at least 1000 (http://
datacolada.org/20). Crowdsourcing can deliver these sample sizes.
The availability of crowdsourced samples may also increase attempts to reproduce results
observed by others. The speed and cost advantages of using crowds lower the investment
required to replicate a study. The ability to recruit large samples also benefits replications, which
typically require more participants than the study they seek to replicate [52]. Perhaps most
importantly, a crowd provides a standardized common sample that all researchers can use.
Failed replications are inherently ambiguous: either the finding in the original study is ‘true’, or
the replication is ‘true’, or the replication differed in a crucial but overlooked way [53–55]. As a
result, failed replications inevitably lead to speculation about possibly overlooked differences
between the original study and the replication attempt, and often lead to follow-up studies by
either the original or replicating authors to rule out potential explanations. The ability to share
exact materials and recruit samples drawn from the same population (Box 5) reduces the
number of potential differences between studies considerably (but with the potential for further
complications, see A Tragedy of the Commons, below), simplifying this exercise for everyone
involved.
742 Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10

Design and Ethics for Crowdsourcing
Running experiments on crowdsourcing platforms is not the same as running experiments in
the laboratory with university participants. Crowdsourcing tasks tend to be of short duration
(but there are exceptions [56]). Participants are seldom taking part under exam conditions (with
nearly one third being not alone and one fifth reporting watching TV [33]). There is almost no
opportunity for participants to interact with the experimenter or ask questions, which means
that the experimental task needs to enable correct completion by design without lengthy
instructions.
There are also ethical issues to consider. Is ‘Click here to continue’ good enough for informed
consent? Do participants understand that they can withdraw from the study at any time? It is
arguably easier to close a browser window than to leave a laboratory with an experimenter
present, but, anecdotally, workers differ in their beliefs about the consequences of abandoning
a HIT. Do participants have a way to request deletion of their data? This may be more difficult if
they do not have a ready way to revisit old experiments. Remember that WorkerIDs are not
anonymous [57], therefore avoid posting them with data.
There have been calls for ethical rates of pay [25,58]. The decision to increase worker pay is
primarily an ethical one. In general, data quality – defined as providing reliable self-report and
larger experimental effect sizes – is usually not sensitive to compensation level [6,36,59], at least
for American workers [60]. However, paying more will definitely increase the speed of data
collection [2,59] and may reduce participant attrition [36]. Payment may also induce workers to
spend longer on tasks which require sustained effort, and they will thus perform better when
performance is correlated with effort [61,62]. One potential downside of higher pay rates is that
they may also attract the most keen and active participants, crowding out less-experienced
workers [21] and shrinking the population being sampled [32].
A Tragedy of the Commons?
Amazon reports more than 500 000 registered workers on MTurk, but, as with many online
communities, the number of active workers at any given time is much smaller – at least one
order of magnitude smaller [58]. The pool of workers available to a researcher is further limited,
particularly when the sample drawn from the pool is small, because some workers are more
likely to complete a study than other workers. A capture–recapture analysis using data from
seven laboratories across the world estimated that the average laboratory samples from a
population of about 7300 MTurk workers, with substantial overlap between the populations
accessed by different laboratories [32]. This creates the very real possibility of exhausting the
pool of available workers for a particular line of research.
Unlike traditional subject pools, there are no restrictions on how many surveys a worker may
complete or how long they may remain in the pool. Many workers consider MTurk to be like a
job, spending many hours per week completing surveys. The median MTurker reports partici-
pating in about 160 academic studies in the previous month [63], and many would complete
more if they could [64]. Workers remain in the pool as long as they like, with about half of the
workers being replaced every 7 months [32], but some remain in the pool for years. The lack of
restrictions on worker productivity and tenure leads to a small group of workers who are
responsible for a large fraction of the observations obtained on MTurk research studies [33].
Researchers have also raised concerns about workers sharing knowledge about experiments
with each other on forums or online discussion boards. About 60% of workers use forums and
(cid:1)10% can directly contact at least one other MTurk worker [65]. To date, most available
evidence suggests that this is rare. Perhaps 10% of workers are referred to HITs from sources
outside of MTurk (mostly Reddit [21]). Within these communities there are strong norms about
Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10 743

intentionally disclosing substantive information about a study. Although these norms are not
always followed, and people may not realize that certain information is substantive, by and large
these violations are rare, with workers using these forums primarily to share instrumental
features of tasks (e.g., well-paying HITs or bad experiences with requesters) [31,33]. Workers
can even select requesters with the help of tools like Turkopticon.
Worker experience can be a problem because experience in completing studies can influence
behavior in future studies. Measures of performance will become inflated through practice
effects. For example, the classic cognitive reflection test [66] is largely known to MTurk workers
[67]. Consequently, worker experience is correlated with performance on this test, but not on
logically equivalent novel questions [33,68]. Observed effect sizes may decrease over time
when one variable is correlated with prior experience, but another is not. For example, in a
series of experimental games conducted on MTurk, the intuitive tendencies of workers shifted
from cooperation towards the optimal game-theoretic rational response [69,70].
Familiarity with an experiment may also reduce effect sizes if information from other experi-
mental conditions contaminates judgments. In a systematic replication of 12 studies, partici-
pating twice in the same two-condition experiment reduced effect sizes, particularly for those
who were assigned to the alternative condition and when little time had elapsed between
participations [71]. Moreover, there is at least some evidence of effects that only replicate with
naïve participants [72]. Fortunately, experiments that examine many commonly used outcomes
in cognitive psychology appear to be robust to prior exposure, with task performance improving
over time, but with between-group differences persisting [40].
Participant non-naïveté may have effects on data quality that go beyond those of the task-
specific. Familiarity with attention checks may make participants very good at dealing with any
attention check (and better than University participants) – independently of familiarity with the
specific check [73]; this has led to a call for researchers to use novel attention checks or to
abandon them for this population altogether [17]. Participants can also gain familiarity with
eligibility criteria used to prescreen for admission in one study, and use this information
fraudulently to gain access to later studies with similar eligibility requirements [74]. Psychol-
ogists can contaminate the participant pool with deception manipulations which are particularly
disliked by experimental economists [75]. Even in the absence of outright deception, research
procedures that try to disguise the true purpose of an experiment may be less effective with
expert participants who are more aware of these procedures [76].
The small size of the pool of active participants and the prevalence of expert or professional
participants on online labor markets can lead to a tragedy of the commons, where studies run in
one laboratory can contaminate the pool for other laboratories running other studies. This
possibility is compounded by the difficulty requesters face in communicating with each other, or
even knowing what experiments other researchers have conducted.
Although there are real challenges in managing a shared pool, and researchers would certainly
benefit from new tools to assist in this process, the problems it poses are manageable.
Although asking workers whether they have completed similar experiments before is unlikely
to be effective [71,74], researchers can automatically prevent specific workers from completing
related studies that they have posted by using qualifications [29]. In fact, TurkPrime can prevent
any identified worker from completing a given experiment, making it possible for researchers to
share lists of workers to avoid [77]. Importantly, all the available evidence suggests that, if
anything, repeated exposure to research materials attenuates effects, but this can be offset by
increasing sample sizes and, at worst leads to a larger proportion of false negatives. Whether
744 Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10

repeated exposure to a research paradigm can produce false positives remains an empirical
question.
Given the collective move by researchers from a large set of independent University-based
samples to one shared MTurk sample, there is also the possibility that one big event, or a
single decision by the crowd administrators, could affect the viability of data collection with
the crowd. For example, in 2016, Amazon increased the price of conducting studies
on MTurk. Similarly, Amazon has made unpredictable changes in their policy, cutting off
access for international requesters and workers. As we utilize MTurk more as a discipline, we
have increased the systemic risk we all face – although diversifying across the newer
platforms will reduce this risk.
Concluding Remarks
Crowdsourcing cognitive science offers a new route for scientific advance in this field. We need
to exploit the positive features of the platform while mitigating the weaknesses. We need to
report carefully how we have used our chosen platform, and might find it particularly useful to
pre-register aspects of our research. There will be innovations in the field as sensors extend
beyond webcams to other internet of things devices (e.g., Fitbits and GPS) and locations
outside the home and office. There will be innovations where people can contribute their
machine-recorded data, such as supermarket transactions or banking records, in exchange for
insight and control over their data. We will also need to understand how sharing a common pool
of relatively expert participants influences our findings (see Outstanding Questions).
Disclaimer Statement
N.S. has a close relative who works for Amazon, the owners of MTurk.
Acknowledgments
This work was supported by Economic and Social Research Council grants ES/K002201/1, ES/K004948/1, ES/
N018192/1, and Leverhulme Trust grant RP2012-V-022.
References
1. Gosling, S.D. and Mason, W. (2015) Internet research in psy-
chology. Annu. Rev. Psychol. 66, 877–902 http://dx.doi.org/
10.1146/ annurev-psych-010814-015321
2. Berinsky, A.J. et al. (2012) Evaluating online labor markets for
experimental research: Amazon.com's Mechanical Turk. Polit.
Anal. 20, 351–368 http://dx.doi.org/10.1093/pan/mpr057
3. Mullinix, K.J. et al. (2016) The generalizability of survey experi-
ments. J. Exp. Polit. Psychol. 2, 109–138 http://dx.doi.org/
10.1017/XPS.2015.19
4. Kittur, A. et al. (2008) Crowdsourcing user studies with Mechan-
ical Turk. In Proceedings of the SIGCHI Conference on Human
factors in Computing systems (Czerwinski, M., ed.), pp. 453–
456, ACM
5. Paolacci, G. et al. (2010) Running experiments on Amazon
Mechanical Turk. Judgm. Decis. Mak. 5, 411–419 http://
journal.sjdm.org/10/10630a/jdm10630a.pdf
6. Buhrmester, M. et al. (2011) Amazon's Mechanical Turk: A new
source of inexpensive, yet high-quality, data? Perspectives On
Psychol. Sci. 6, 3–5 http://dx.doi.org/10.1177/
1745691610393980
7. Horton, J.J. et al. (2011) The online laboratory: Conducting
experiments in a real labor market. Exp. Econ. 14, 399–425
http://dx.doi.org/10.1007/s10683-011-9273-9
8. Shank, D.B. (2016) Using crowdsourcing websites for
sociological research: The case of Amazon Mechanical Turk.
Am. Sociol. 47, 47–55 http://dx.doi.org/10.1007/s12108-015-
9266-9
9. Shapiro, D.N. et al. (2013) Using Mechanical Turk to study
clinical populations. Clinical Psychol. Sci. 1, 213–220
10.
http://
dx.doi.org/10.1177/2167702612469015
Goodman, J.K. and Paolacci, G. (2017) Crowdsourcing con-
sumer research. J. Consum. Res 44, 196–210 http://dx.doi.org/
10.1093/jcr/ucx047
11. Bentley, J.W. (2017) Challenges with Amazon Mechanical Turk
research in accounting. SSRN eLibrary.
12. Stritch, J.M. et al. (2017) The opportunities and limitations of
using Mechanical Turk (Mturk) in public administration and
management scholarship. Int. Public. Manag. J. Published
online January 19, 2017. http://dx.doi.org/10.1080/
10967494.2016.1276493
13. Lutz, J. (2016) The validity of crowdsourcing data in studying
anger and aggressive behavior a comparison of online and
laboratory data. Soc. Psychol. 47, 38–51 http://dx.doi.org/
10.1027/1864-9335/a000256
14. Majima, Y. et al. (2017) Conducting online behavioral research
using crowdsourcing services in Japan. Front. Psychol. 8, 378
http://dx.doi.org/10.3389/fpsyg.2017.00378
15. Peer, E. et al. (2014) Reputation as a sufficient condition for data
quality on Amazon Mechanical Turk. Behav. Res. Methods 46,
1023–1031 http://dx.doi.org/10.3758/s13428-013-0434-y
16. Crone, D.L. and Williams, L.A. (2016) Crowdsourcing partici-
pants for psychological research in Australia: A test of micro-
workers. Aust. J. Psychol 69, 39–47
17. Peer, E. et al. (2017) Beyond the Turk: Alternative platforms for
crowdsourcing behavioral research. Journal of Experimental
Soc. Psychol. 70, 153–163 http://dx.doi.org/10.1016/j.jesp.
2017.01.006
18. Estellés-Arolas, E. and González-Ladrzón-De-Guevara, F.
(2012) Towards an integrated crowdsourcing definition. J.
Outstanding
Inf.
Questions
How will crowdsourcing interact with
big data and the internet of things, as
cognitive scientists start to use
researchers as assistants as well as
participants?
How can we mitigate some of the aris-
ing tragedy of the commons problems
that arise from our sharing of a com-
mon population of participants?
Cognitive science relies increasingly
upon one central crowdsourcing
resource – how then can we mitigate
some of the systemic risk that follows
for the discipline?
We increasingly use paradigms best
suited for online crowdsourced testing
– how will this shape the research
direction of the field?
How will increasing non-naïveté and
the resulting reduction in effect sizes
alter our findings?
Trends in Cognitive Sciences, October 2017, Vol. 21, No. 10 745

Sci. 38, 189–200 http://dx.doi.org/10.1177/
0165551512437638
19. Sulser, F. et al. (2014) Crowd-based semantic event detection
and video annotation for sports videos. In Proceedings of
the 2014 International ACM Workshop on Crowdsourcing for
Multimedia (Redi, J. and Lux, M., eds), pp. 63–68, New York,
ACM
20. Casler, K. et al. (2013) Separate but equal?. A comparison of
participants and data gathered via Amazon's MTurk, social
media, and face-to-face behavioral testing. Comput. Hum.
Behav. 29, 2156–2160
21. Casey, L. et al. (2017) Intertemporal differences among MTurk
worker demographics. SAGE Open Published online June 14,
2017. https://osf.io/preprints/psyarxiv/8352x. http://dx.doi.
org/10.1177/2158244017712774
22. Levay, K.E. et al. (2016) The demographic and political compo-
sition of Mechanical Turk samples. Sage Open Published online
March 15, 2016. http://dx.doi.org/10.1177/
2158244016636433
23. Behrend, T.S. et al. (2011) The viability of crowdsourcing for
survey research. Behav. Res. Methods 43, 800–813 http://dx.
doi.org/10.3758/s13428-011-0081-0
24. Arditte, K.A. et al. (2016) The importance of assessing clinical
phenomena in Mechanical Turk research. Psychol. Assessment
28, 684 http://dx.doi.org/10.1037/pas0000217
25. Goodman, J.K. et al. (2013) Data collection in a flat world: The
strengths and weaknesses of Mechanical Turk samples. J.
Behav. Decis. Making. 26, 213–224 http://dx.doi.org/
10.1002/bdm.1753
26. Kosara, R. and Ziemkiewicz, C. et al. (2010) Do Mechanical
Turks dream of square pie charts? In Proceedings of the 3rd
BELIV’10 Workshop Beyond Time and Errors: Novel Evaluation
Methods for Information Visualisation (Sedlmair, M., ed.), pp.
63–70, New York, ACM
27. Johnson, D.R. and Borden, L.A. (2012) Participants at your
fingertips: Using Amazon's Mechanical Turk to increase stu-
dent-faculty collaborative research. Teach. Psychol. 39, 245–
251 http://dx.doi.org/10.1177/ 0098628312456615
28. Veilleux, J.C. et al. (2014) Negative affect intensity influences
drinking to cope through facets of emotion dysregulation. Pers. Indiv. Differ. 59, 96–101 http://dx.doi.org/10.1016/j.
paid.2013.11.012
29. Chandler, J. and Shapiro, D. (2016) Conducting clinical research
using crowdsourced convenience samples. Annu. Rev. Clin.
Psycho. 12, 53–81 http://dx.doi.org/10.1146/annurev-
clinpsy-021815-093623
30. Arechar, A.A. et al. (2016) Turking overtime: How participant
characteristics and behavior vary over time and day on Amazon
Mechanical Turk. J. Econ. Sci. Assoc. 3, 1–11 http://dx.doi.org/
10.2139/ssrn.2836946 In: https://ssrn.com/abstract=2836946
31. Wang, X. et al. (2017) A community rather than a union: Under-
standing self-organization phenomenon on Mturk and how it
impacts Turkers and requesters. In Association for Computing
Machinery CHI’17 Conference, pp. 2210–2216, New York,
ACM
32. Stewart, N. et al. (2015) The average laboratory samples a
population of 7,300 Amazon Mechanical Turk workers. Judgm.
Decis. Mak. 10, 479–491 In: http://journal.sjdm.org/14/14725/
jdm14725.pdf
33. Chandler, J. et al. (2014) Nonnaïveté among Amazon Mechani-
cal Turk workers: Consequences and solutions for behavioral
researchers. Behav. Res. Methods 46, 112–130 http://dx.doi.
org/10.3758/ s13428-013-0365-7
34. Henrich, J. et al. (2010) Most people are not WEIRD. Nature 466,
http://dx.doi.org/10.1038/466029a 29–29
35. de Leeuw, J.R. and Motz, B.A. (2016) Psychophysics in a web
browser? Comparing response times collected with javascript
and psychophysics toolbox in a visual search task. Behav. Res.
Methods 48, 1–12 http://dx.doi.org/10.3758/s13428-015-
0567-2
36. Crump, M.J. et al. (2013) Evaluating Amazon's Mechanical Turk
as a tool for experimental behavioral research. PLoS One 8,
e57410
37.
http://dx.doi.org/10.1371/journal.pone.0057410
Hilbig, B.E. (2016) Reaction time effects in lab- versus web-
based research: Experimental evidence. Behav. Res. Methods
48, 1718–1724 http://dx.doi.org/10.3758/s13428-015-0678-9
38. Simcox, T. and Fiez, J.A. (2014) Collecting response times using
Amazon Mechanical Turk and Adobe Flash. Behav. Res. Meth-
ods 46, 95–111 http://dx.doi.org/10.3758/s13428-013-0345-y
39. Klein, R.A. et al. (2014) Investigating variation in replicability: A
‘many labs’ replication project. Soc. Psychol. 45, 142–152
http://dx.doi.org/10.1027/1864-9335/a000178
40. Zwaan, R.A. et al. (2017) Participant nonnaiveté and the repro-
ducibility of cognitive psychology. Psychon. Bull. Rev. In:
https://osf.io/preprints/psyarxiv/rbz29
41. Clifford, S. et al. (2015) Are samples drawn from Mechanical
Turk valid for research on political ideology? Res. Polit. 2,Pub-
lished online December 15, 2015. http://dx.doi.org/10.1177/
2053168015622072
42. Munafo, M.R. et al. (2017) A manifesto for reproducible science.
Nat. Hum. Behav. 1, 0021 http://dx.doi.org/10.1038/s41562-
016-0021
43. Rosenthal, R. (1979) The file drawer problem and tolerance for
null results. Psychol. Bull. 86, 638–641 http://dx.doi.org/
10.1037//0033-2909.86.3.638
44. Simmons, J.P. et al. (2011) False-positive psychology: Undis-
closed flexibility in data collection and analysis allows presenting
anything as significant. Psychol. Sci. 22, 1359–1366 http://dx.
doi.org/10.1177/ 0956797611417632
45. Frick, R.W. (1998) A better stopping rule for conventional sta-
tistical tests. Behav. Res. Methods, Instruments, & Computers
30, 690–697
46. Kruschke, J.K. (2011) Doing Bayesian Data Analysis: A Tutorial
with R and BUGS, Academic Press, (Burlington, MA)
47. Simonsohn, U. (2014) Posterior-hacking: Selective reporting
invalidates Bayesian results also. SSRN eLibrary. Published
online January 3, 2014. https://ssrn.com/abstract=2374040.
http://dx.doi.org/10.2139/ssrn.2374040
48. Cohen, J. (1988) Statistical Power Analysis for the Behavioral
Sciences. (2nd edn), Erlbaum, (Hillsdale, NJ)
49. Button, K.S. et al. (2013) Power failure: Why small sample size
undermine

## 引用

```

```
