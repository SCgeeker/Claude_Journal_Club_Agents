---
title: Understanding Mixed-Effects Models Through Data Simulation
authors: Lisa M. DeBruine, Dale J. Barr
year: 2021
keywords: 
created: 2025-11-28 14:46:43
---

# Understanding Mixed-Effects Models Through Data Simulation

## 基本信息

- **作者**: Lisa M. DeBruine, Dale J. Barr
- **年份**: 2021
- **關鍵詞**: 

## 摘要

Experimental designs that sample both subjects and stimuli from a larger population need to account for random effects
of both subjects and stimuli using mixed-effects models. However, much of this research is analyzed using analysis of
variance on aggregated responses because researchers are not confident specifying and interpreting mixed-effects models.
This Tutorial explains how to simulate data with random-effects structure and analyze the data using linear mixed-effects
regression (with the lme4 R package), with a focus on interpreting the output in light of the simulated parameters. Data
simulation not only can enhance understanding of how these models work, but also enables researchers to perform
power calculations for complex designs. All materials associated with this article can be accessed at https://osf.io/3cz2e/.
Keywords
simulation, mixed-effects models, power, lme4, R, open materials
Received 6/2/19; Revision accepted 9/5/20
In this article, we walk through the simulation and analy- to be able to make general statements about phenomena
sis of multilevel data with crossed random effects of that go beyond the particular participants and particular
subjects and stimuli. The article’s target audience is stimuli that they happen to have chosen for the specific
researchers who work with experimental designs that study. Traditionally, people speak of such designs as
sample subjects and stimuli, such as is the case for a having crossed random factors of participants and stimuli,
large amount of experimental research in face percep- and think of the goal of inference as being simultaneous
tion, psycholinguistics, and social cognition. Simulation generalization to both populations. However, it may be
is useful not only for understanding how models work, more intuitive to construe the goal as generalizing to a
but also for estimating power when planning a study or single population of events called encounters: That is,
performing a sensitivity analysis. The Tuto

## 研究背景

## 研究方法

## 主要結果

## 討論與結論

## 個人評論

## 相關文獻

## 完整內容

965119
research-article2021 AMPXXX10.1177/2515245920965119DeBruine, BarrSimulating for Linear Mixed-Effects Modeling
Special Section: Using Simulation to Convey Statistical Concepts ASSOCIATION FOR
PSYCHOLOGICAL SCIENCE
Tutorial
Advances in Methods and
Understanding Mixed-Effects Models Practices in Psychological Science
January-March 2021, Vol. 4, No. 1,
pp. 1 –15
Through Data Simulation
© The Author(s) 2021
Article reuse guidelines:
sagepub.com/journals-permissions
hDtOtpIs:: /1/d0o.1i.1o7rg7//1205.11157274/52952105924655912109965119
www.psychologicalscience.org/AMPPS
Lisa M. DeBruine and Dale J. Barr
Institute of Neuroscience & Psychology, University of Glasgow
Abstract
Experimental designs that sample both subjects and stimuli from a larger population need to account for random effects
of both subjects and stimuli using mixed-effects models. However, much of this research is analyzed using analysis of
variance on aggregated responses because researchers are not confident specifying and interpreting mixed-effects models.
This Tutorial explains how to simulate data with random-effects structure and analyze the data using linear mixed-effects
regression (with the lme4 R package), with a focus on interpreting the output in light of the simulated parameters. Data
simulation not only can enhance understanding of how these models work, but also enables researchers to perform
power calculations for complex designs. All materials associated with this article can be accessed at https://osf.io/3cz2e/.
Keywords
simulation, mixed-effects models, power, lme4, R, open materials
Received 6/2/19; Revision accepted 9/5/20
In this article, we walk through the simulation and analy- to be able to make general statements about phenomena
sis of multilevel data with crossed random effects of that go beyond the particular participants and particular
subjects and stimuli. The article’s target audience is stimuli that they happen to have chosen for the specific
researchers who work with experimental designs that study. Traditionally, people speak of such designs as
sample subjects and stimuli, such as is the case for a having crossed random factors of participants and stimuli,
large amount of experimental research in face percep- and think of the goal of inference as being simultaneous
tion, psycholinguistics, and social cognition. Simulation generalization to both populations. However, it may be
is useful not only for understanding how models work, more intuitive to construe the goal as generalizing to a
but also for estimating power when planning a study or single population of events called encounters: That is,
performing a sensitivity analysis. The Tutorial assumes the goal is to say something general about what happens
basic familiarity with R programming. when the two types of sampling units meet—when a
typical subject encounters (and responds to) a typical
stimulus (Barr, 2018).
Generalizing to a Population of Encounters
Most analyses using conventional statistical techniques,
Many research questions in psychology and neuroscience such as analysis of variance (ANOVA) and the t test, com-
are questions about certain types of events: What hap- mit the fallacy of treating stimuli as fixed rather than
pens when people encounter particular types of stimuli? random. For example, imagine that a sample of partici-
For example, do people recognize abstract words faster pants are rating the trustworthiness of a sample of faces
than concrete words? What impressions do people form and the goal is to determine whether the faces of people
about a target person’s personality on the basis of the born on even-numbered days look more trustworthy than
person’s vocal qualities? Can people categorize emotional
expressions more quickly on the faces of social in-group
Corresponding Author:
members than on the faces of out-group members? How
Lisa M. DeBruine, Institute of Neuroscience & Psychology, University of
do brains respond to threatening versus nonthreatening
Glasgow
stimuli? In all of these situations, researchers would like E-mail: lisa.debruine@glasgow.ac.uk
Creative Commons CC BY: This article is distributed under the terms of the Creative Commons Attribution 4.0 License
(https://creativecommons.org/licenses/by/4.0/) which permits any use, reproduction and distribution of the work without further permission
provided the original work is attributed as specified on the SAGE and Open Access pages (https://us.sagepub.com/en-us/nam/open-access-at-sage).

2 DeBruine, Barr
those born on odd-numbered days. Obviously, they do not. this complexity is specific to mixed-effects modeling,
At the extreme, imagine that only a single face is sampled some of it is simply hidden away from users of traditional
from each category, but 100 people rate each face. If the techniques by graphical user interfaces and function
analysis treats the sample of faces as fixed, or a perfect defaults. The novice mixed-effects modeler is suddenly
representation of the larger population of faces on Earth, confronted with the need to make decisions about how
a significant difference in one direction or the other is to specify categorical predictors, which random effects
almost guaranteed. There is sufficient power to detect even to include or exclude, which of the statistics in the volu-
tiny differences in apparent trustworthiness, so this result minous output to attend to, and whether and how to
will be highly replicable with large samples of raters. As reconfigure the optimizer function when a convergence
the number of faces in the sample is increased, the problem error or singularity warning appears.
gets better (the sample means are more likely to approxi- We are optimistic that the increasing adoption of the
mate the population means), but if the number of raters is mixed-effects approach will improve the generalizability
increased (and thus power to detect small differences in and thus reproducibility of studies in psychology and
the sample means is also increased), it gets worse again. related fields. Models that account for subjects and stim-
The problem, and the solutions to the problem, has uli (or other factors) as nonessential, exchangeable fea-
been known in psycholinguistics for more than 50 years tures of an experiment will better characterize the
(Clark, 1973; Coleman, 1964), and most psycholinguistic uncertainty in the resulting estimates and, thus, improve
journals require authors to demonstrate generalizability the generality of inferences drawn from them (Yarkoni,
of findings over stimuli as well as over subjects. Even 2020). That said, we empathize with the frustration—and
so, the quasi-F statistics for ANOVA (F′ and min F′) that sometimes, exasperation—expressed by many novices
Clark proposed as a solution were widely recognized as when they attempt to grapple with these models in their
unreasonably conservative (Forster & Dickinson, 1976), research. A profitable way to build understanding and
and until fairly recently, most psycholinguists performed confidence is through data simulation. If you can create
separate by-subjects (F ) and by-items analyses (F ), data sets by sampling from a population for which you
1 2
declaring an effect significant only if it was significant know the ground truth about the population parameters
for both analyses. This F × F approach has been widely you are interested in (e.g., mean and standard deviation
1 2
used, despite the fact that Clark had already shown it to of each group), you can check how often and under
be invalid, since both F statistics have higher than nomi- what circumstances a statistical model will give you the
nal false-positive rates in the presence of a null effect— correct answer. Knowing the ground truth also allows
F because of unmodeled stimulus variance and F you to experiment with various modeling choices and
1 2
because of unmodeled subject variance. observe their impact on a model’s performance.
Recently, psycholinguists have adopted linear mixed-
effects modeling as the standard for statistical analysis, Disclosures
given its numerous advantages over ANOVA, including
the ability to simultaneously model subject and stimulus The code to reproduce the analyses reported in this
variation, to gracefully deal with missing data or unbal- article is publicly available via OSF and can be accessed
anced designs, and to accommodate arbitrary types of at https://osf.io/3cz2e. The OSF project page also
continuous and categorical predictors or response vari- includes appendices with the code for extended exam-
ables (Baayen et al., 2008; Locker et al., 2007). This ples. The repository links to a Web app that performs
development has been facilitated by the lme4 package data simulation without requiring knowledge of R code.
for R (Bates et al., 2015), which provides powerful func- The app allows users to change parameters and inspect
tionality for model specification and estimation. Appro- the results of linear mixed-effects models and ANOVAs,
priately specified mixed-effects models yield major as well as calculate power and false-positive rates for
improvements in power over quasi-F approaches and these analyses.
avoid the increased false-positive rate associated with
separate F and F (Barr et al., 2013). Simulating Data With Crossed
1 2
Despite mixed-effects modeling becoming the de facto
Random Factors
standard for analysis in psycholinguistics, the approach
has yet to take hold in other areas where stimuli are Data simulation can play a powerful role in statistics
routinely sampled, despite repeated calls for improved education, enhancing understanding of the use and
analyses in social psychology (Judd et al., 2012) and interpretation of statistical models and the assumptions
neuroimaging (Bedny et al., 2007; Westfall et al., 2017). behind them. The data-simulation approach to learning
One of the likely reasons for the limited uptake outside about statistical models differs from the standard
of psycholinguistics is that mixed-effects models expose approach in most statistics textbooks, which present the
the analyst to a level of statistical and technical complexity learner with a step-by-step analysis of a sample of data
far beyond most researchers’ training. Although some of from some population of interest. Such exercises usually

Simulating for Linear Mixed-Effects Modeling 3
culminate in inferences about characteristics of the pop- by varying the effect size while holding the sample size
ulation of interest from model estimates. Although this and desired power constant—for instance, to determine
reflects the typical uncertain situation of the analyst, the the minimum effect size that your analysis can detect
learner cannot fully appreciate the performance of the with 80% power and an N of 200 per group. You can
model without knowing the ground truth. In a data- also set the population effect size to zero and calculate
simulation approach, the learner starts out knowing the the proportion of significant results to check if your
ground truth about the population and writes code to analysis procedure inflates the rate of false positives.
simulate the process of taking and analyzing samples For most traditional statistical procedures, such as the
from that population. Giving learners knowledge of the t test or ANOVA, there are analytic procedures for esti-
underlying population parameters as well as the ability mating power. Westfall et al. (2014) presented analytic
to explore how population parameters are reflected in power curves for simple mixed-effects designs such as
model estimates can yield powerful insight into the the one described in this Tutorial (a corresponding app
appropriate specification of models and the interpreta- is available at https://jakewestfall.shinyapps.io/crossed
tion of statistical output. power). But even when analytic solutions exist, simula-
Data simulation also has a wide variety of scientific tion can still be useful to estimate power or false-positive
uses, one of which is to estimate properties of statistical rates, because real psychological data nearly always
models in situations in which algorithms for computing deviate from the statistical assumptions behind tradi-
those properties are unknown or can be applied only tional procedures. For instance, most statistical proce-
with difficulty. For instance, Forster and Dickinson dures used in psychology assume a continuous and
(1976) used Monte Carlo simulation to explore the unbounded dependent variable, but it is often the case
behavior of the quasi-F statistics for ANOVA (F′ and min that researchers use discrete (e.g., Likert) response
F′) under various conditions. In a Monte Carlo simula- scales. When assumptions are not met, power simula-
tion, the long-run properties of a process are estimated tions can provide a more reliable estimate than analytic
by generating and analyzing many simulated data sets— procedures.
usually, thousands or tens of thousands of them. In this Tutorial, we simulate data from a design with
One of the most important applications of Monte crossed random factors of subjects and stimuli, fit a
Carlo simulation is in the estimation of power for com- model to the simulated data, and then see whether the
plex models. The notion of power arises most frequently resulting sample estimates are similar to the population
in the context of study planning, when a power analysis values we specified when simulating the data. In this
is used to determine the target N for a study. Power is hypothetical study, subjects classify the emotional
the probability that a specified statistical test will gener- expressions of faces as quickly as possible, and we use
ate a significant result for a sample of data of a specified their response time (RT) as the primary dependent vari-
size taken from a population with a specified effect. If able. Let us imagine that the faces are of two types:
you can characterize the population parameters, you can either from the subject’s in-group or from an out-group.
repeatedly simulate and analyze data from this popula- For simplicity, we further assume that each face appears
tion. The proportion of times that this procedure pro- only once in the stimulus set. The key question is
duces a significant result provides an estimate of the whether there is any difference in classification speed
power of your test given your assumed sample size and between the two types of faces. Because many of the
effect size. You can adjust any parameters in this simula- technical terms used in discussing linear mixed-effects
tion in order to estimate other parameters. Instead of models will be unfamiliar to readers, we provide a glos-
estimating power, you can perform a sensitivity analysis sary of terms in Box 1.
Box 1. Glossary of Terms
Term Explanation
Crossed random factors Refers to a design with multiple random factors, such as subjects and items, the
levels of which are crossed (e.g., each subject encounters each stimulus)
Data-generating process (DGP) The mathematical model capturing assumptions about the processes giving rise to
the data
Fixed effect An effect whose value is constant across realizations of the experiment
Random effect An effect whose value varies across potential realizations of the experiment (e.g.,
because of sampling)
Random intercept A random effect capturing the deviation of a sampling unit (subject or item) from
the model intercept
Random slope A random effect capturing the deviation of a sampling unit (subject or item) from
the model slope
Variance components Parameters describing the distribution of random effects in the population

4 DeBruine, Barr
Required software Table 1. The Target Data Structure
This Tutorial and associated materials use the following
row subj_id item_id category RT
open-source research software: R (R Core Team, 2018),
1 1 1 ingroup 750.2
lme4 (Bates et al., 2015), lmerTest (Kuznetsova et al.,
2 1 2 ingroup 836.1
2017), broom.mixed (Bolker & Robinson, 2019), afex
. . . . . . . . . . . . . . .
(Singmann et al., 2019), tidyverse (Wickham, 2017); faux
49 1 49 outgroup 811.9
(DeBruine, 2020), and papaja (Aust & Barth, 2018).
50 1 50 outgroup 801.8
To run the code, you will need to have some add-on
51 2 1 ingroup 806.7
packages available:
52 2 2 ingroup 805.9
# load required packages . . . . . . . . . . . . . . .
" " # model specification / 5000 100 50 outgroup 859.9
library( lme4 )
estimation Note: See the text for an explanation of the terms in this table.
" " # provides p-values
library( lmerTest )
in the output
" " # data wrangling and subjects, but also whether they are within or between
library( tidyverse )
stimulus items. Recall that a within-subjects factor is one
visualisation
for which each and every subject receives all of the
Because the code uses random-number generation, levels, and a between-subjects factors is one for which
if you want to reproduce the exact results below you each subject receives only one of the levels. Likewise, a
will need to set the random-number seed at the top of within-items factor is one for which each stimulus
your script and ensure that you are using R Version 3.6.0 receives all of the levels. For our current example, the
or higher: in-group/out-group factor ( ) is within sub-
category
jects but between items, given that each stimulus item
# ensure this script returns the same
is either in-group or out-group.
results on each run
set.seed(8675309)
Specify the fixed-effects parameters. Now that we
If you change the seed or are using a lower version of have an appropriate structure for our simulated data set,
R, your exact numbers will differ, but the procedure will we need to generate the RT values. For this, we need to
still produce a valid simulation. establish an underlying statistical model. In this and the
next section, we build up a statistical model step by step,
defining variables in the code that reflect our choices for
Establishing the data-generating parameters
parameters. For convenience, Table 2 lists all of the vari-
The first thing to do is to set up the parameters that gov- ables in the statistical model and their associated variable
ern the process we assume to give rise to the data, the names in the code.
data-generating process, or DGP. Let us start by defining Let us start with a basic model and build up from
the sample size: In this hypothetical study, each of 100 there. We want a model of RT for subject s and item i
subjects will respond to all 50 stimulus items (25 in-group that looks something like the following:
and 25 out-group), for a total of 5,000 observations.
RT =β +β X +e . (1)
si 0 1 i si
Specify the data structure. We want the resulting data
to be in long format, with each row representing a single According to the formula, response RT for subject s
si
observation (i.e., a single trial; see Table 1). The variable and item i is defined as the sum of an intercept term β ,
0
runs from to and indexes the subject which in this example is the grand mean RT for the
subj_id 1 100
number; runs from to and indexes the population of stimuli; plus β , the mean RT difference
item_id 1 50 1
item number; is whether the face is in-group between in-group and out-group stimuli, multiplied by
category
or out-group (Items 1–25 always in-group and Items 26–50 predictor variable X to obtain the offset for item i; plus
i
always out-group); and is the participant’s RT for that random noise e . To make β equal the grand mean and
RT si 0
trial. Each trial is uniquely identified by the combination β equal the mean out-group minus the mean in-group
1
of the and labels. RT, we code the item-category variable X as −0.5 for the
subj_id item_id i
Note that for independent variables in designs in in-group category and +0.5 for the out-group category.
which subjects and stimuli are crossed, one cannot think In the model formula, we use Greek letters (β , β ) to
0 1
of factors as being solely “within” or “between” because represent population parameters that are being directly
there are two sampling units; one must ask not only estimated by the model. In contrast, Roman letters rep-
whether independent variables are within or between resent the remaining variables: observed variables whose

Simulating for Linear Mixed-Effects Modeling 5
Table 2. Variables in the Data-Generating Model and each subject s in terms of a random effect T , where the
0s
Associated R Code first subscript, 0, indicates that the deflection goes with the
intercept term, β . This random-intercept term captures
Model Code 0
the value that must be added or subtracted to the intercept
variable variable Description
for subject s, which in this case corresponds to how much
RT si RT Reaction time for subject s responding slower or faster this subject is relative to the average RT of
to item i
800 ms. Just as it is unrealistic to expect the same intercept
X Condition for item i (−0.5 = in-group,
i X_i for every subject, it is also unrealistic to assume the same
0.5 = out-group)
intercept for every stimulus; it will be easier to categorize
β Intercept; grand-mean RT
0 beta_0 emotional expressions on some faces than on others, and
β Slope; mean effect of the in-group/
1 beta_1 we can incorporate this assumption by including by-item
out-group manipulation
τ 0 tau_0 Standard deviation of the by-subject random intercepts O 0i , with the subscript 0 reminding us
random intercepts that it is a deflection from the β term, and the i indexing
0
τ Standard deviation of the by-subject each of the 50 stimulus items (faces). Each face is assigned
1 tau_1
random slopes a unique random intercept that characterizes how much
ρ rho Correlation between the by-subject slower or faster responses to this particular face tend to be
random intercepts and slopes relative to the average RT of 800 ms. Adding these terms
ω Standard deviation of the by-item
0 omega_0 to our model yields
random intercepts
σ Standard deviation of the residuals
sigma RT =β +T +O +β X +e . (2)
T Random intercept for subject s si 0 0s 0i 1 i si
0s T_0s
T Random slope for subject s
1s T_1s Now, whatever values of T and O we end up with in
O Random intercept for item i 0s 0i
0i O_0i our sampled data set will depend on the luck of the draw,
e Residual for the trial involving
si e_si that is, on which subjects and stimuli we happened to
subject s and item i
have sampled from their respective populations. We
assume that these values, unlike fixed effects, will differ
across different realizations of the experiment with differ-
values are determined by sampling (e.g., RT , T , e ) or
si 0s si ent subjects and/or stimuli. In practice, we often reuse the
fixed by the experimental design (X).
i same stimuli across many studies, but we still need to treat
Although this model is incomplete, we can go ahead and
the stimuli as sampled if we want to be able to generalize
choose parameters for β and β . For this example, we set
0 1 our findings to the whole population of stimuli.1
a grand mean of 800 ms and a mean difference of 50 ms:
It is an important conceptual feature of mixed-effects
models that they do not directly estimate the individual
# set fixed effect parameters
beta_0 < - 800 # intercept; i.e., the random effects (T 0s and O 0i values), but rather, they
estimate the random-effects parameters that characterize
grand mean
< # slope; i.e, effect of the distributions from which these effects are drawn.2 It
beta_1 - 50
is this feature that enables generalization beyond the
category
particular subjects and stimuli in the experiment. We
You will need to use disciplinary expertise and/or assume that each T comes from a normal distribution
0s
pilot data to choose these parameters for your own with a mean of zero and unknown standard deviation,
projects; by the end of this Tutorial, you will understand τ ( in the code). The mean of zero reflects the
0 tau_0
how to extract those parameters from an analysis. assumption that each random effect is a deflection from
The parameters β and β are fixed effects: They char- the grand mean. Similarly, for the by-item random inter-
0 1
acterize the population of events in which a typical cepts, we assume the O values to be sampled from a
0i
subject encounters a typical stimulus. Thus, we set the normal distribution also with a mean of zero and with
mean RT for a “typical” subject encountering a “typical” an unknown standard deviation, ω ( ). In our
0 omega_0
stimulus to 800 ms and assume that responses are typi- simulation, we set the by-subject random-intercept stan-
cally 50 ms slower for out-group than for in-group faces. dard deviation to 100, and the by-item random-intercept
standard deviation to 80:
Specify the random-effects parameters. This model is
completely unrealistic, however, because it does not allow # set random effect parameters
for any individual differences among subjects or stimuli. < # by-subject random
tau_0 - 100
Subjects are not identical in their response characteristics: intercept sd
Some will be faster than average, and some slower. We < # by-item random
omega_0 - 80
can characterize the difference from the grand mean for intercept sd

6 DeBruine, Barr
There is still a deficiency in our data-generating The response time for subject s on item i, RT , is decom-
si
model related to β , the fixed effect of category. Cur- posed into a population grand mean, β ; a by-subject
1 0
rently, our model assumes that each and every subject random intercept, T ; a by-item random intercept, O ;
0s 0i
is exactly 80 ms faster to categorize emotions on in- a fixed slope, β ; a by-subject random slope, T ; and a
1 1s
group faces than on out-group faces. Clearly, this trial-level residual, e . Our data-generating process is
si
assumption is totally unrealistic; some participants will fully determined by seven population parameters, all
be more sensitive to in-group/out-group differences than denoted by Greek letters: β , β , τ , τ , ρ, ω , and σ (see
0 1 0 1 0
others are. We can capture this analogously to the way Table 2). In the next section, we apply this data-generating
in which we captured variation in the intercept, namely, process to simulate the sampling of subjects, items, and
by including by-subject random slopes T : trials (encounters).
1s
RT =β +T +O +(β +T )X +e . (3)
si 0 0s 0i 1 1s i si
Simulating the sampling process
The random slope T is an estimate of how much
1s Let us first define parameters related to the number of
subject s’s difference in RT when categorizing in-group
observations. In this example, we simulate data from 100
versus out-group faces differs from the population mean
subjects responding to 25 in-group faces and 25 out-
effect, β , which we already set to 50 ms. Given how we
1 group faces. There are no between-subjects factors, so
coded the X variable, the mean effect for subject s is
i we can set to 100. We set and
given by the β + T term. So, a participant who is 90 ms n_subj n_ingroup
1 1s to the number of stimulus items in each
faster on average to categorize in-group than out-group n_outgroup
condition:
faces would have a random slope T of 40 (β + T = 50 +
1s 1 1s
40 = 90). As we did for the random intercepts, we assume # set number of subjects and items
that the T effects are drawn from a normal distribution, < # number of subjects
1s n_subj - 100
with a mean of zero and standard deviation of τ ( < # number of ingroup stimuli
1 tau_1 n_ingroup - 25
in the code). For this example, we assume the standard < # number of outgroup
n_outgroup - 25
deviation is 40 ms. stimuli
But note that we are sampling two random effects for
each subject s, a random intercept T and a random Simulate the sampling of stimulus items. We need to
0s
slope T . It is possible for these values to be positively create a table listing each item i, which category it is in,
1s
or negatively correlated, in which case we should not and its random effect, O :
0i
sample them independently. For instance, perhaps peo-
# simulate a sample of items
ple who are faster than average overall (negative random
# total number of items = n_ingroup +
intercept) also show a smaller than average effect of the
n_outgroup
in-group/out-group manipulation (negative random
<
slope) because they allocate less attention to the task. items - data.frame(
= +
We can capture this by allowing for a small positive cor- item_id seq_len(n_ingroup n_outgroup),
= " "
relation between the two factors, , which we assign category rep(c( ingroup ,
rho " "
to be .2. outgroup ), c(n_ingroup, n_outgroup)),
= = +
Finally, we need to characterize the trial-level noise O_0i rnorm(n n_ingroup
= =
in the study (e ) in terms of its standard deviation. We n_outgroup, mean 0, sd omega_0)
si
simply assign this parameter value, , to be twice )
sigma
the size of the by-subject random-intercept standard For the first variable in the data set, , we
item_id
deviation: have used to assign a unique integer to
seq_len()
each of the 50 stimulus faces; these IDs function like
# set more random effect and error
names. The variable designates whether the
parameters category
face is in-group or out-group; the first 25 items are in-
< # by-subject random slope sd
tau_1 - 40 group, and the last 25 are out-group. Finally, we sample
< # correlation between
rho - .2 the values of O from a normal distribution using the
intercept and slope 0i
function, with a mean of 0 and standard devi-
< # residual (error) sd rnorm()
sigma - 200 ation of ω .
0
To summarize, we established a reasonable statistical Let us introduce a numeric predictor to represent
model underlying the data having the form what category each stimulus item i belongs to (i.e., for
the X in our model). Because we predict that responses
i
RT =β +T +O +(β +T )X +e . (4) to in-group faces will be faster than responses to
si 0 0s 0i 1 1s i si

Simulating for Linear Mixed-Effects Modeling 7
Table 3. The Resulting Sample of Items random effects. This will be slightly more complicated
than what we just did, because we cannot simply sample
item_id category O_0i X_i the T values from a univariate distribution using
0s rnorm()
independently from the T values. Instead, we must sam-
1 ingroup –79.7 -0.5 1s
ple < T , T > pairs—one pair for each subject—from a
2 ingroup 57.7 -0.5 0s 1s
bivariate normal distribution. To do this, we use the
3 ingroup –49.4 -0.5
4 ingroup 162.4 -0.5 mvrnorm() function, a multivariate version of rnorm()
5 ingroup 85.2 -0.5 from the MASS package that comes preinstalled with R.
6 ingroup 79.0 -0.5 We need only this one function from MASS, so we can call
. . . . . . . . . . . . it directly using the syntax instead
package::function()
44 outgroup 54.7 0.5 of loading the library (specifically,
MASS::mvrnorm()
45 outgroup –20.2 0.5 instead of .3 We specify the three param-
library(MASS))
46 outgroup –12.1 0.5 eters describing the distribution of the < T ,T > pairs—
0s 1s
47 outgroup –70.0 0.5 two variances and a correlation—by entering them into a
48 outgroup –158.2 0.5 2 × 2 variance-covariance matrix using the
matrix()
49 outgroup 19.0 0.5 function, and then passing this matrix to
mvrnorm()
50 outgroup 2.9 0.5 using the argument. This requires converting
Sigma
Note: See the text for an explanation of the terms in the column heads. the standard deviations into variances (by squaring
them) and calculating the covariance, which is the
product of the correlation and two standard deviations
out-group faces, we set in-group to −0.5 and out-group
(i.e., ρ × τ × τ ):
to +0.5: 0 1
# simulate a sample of subjects
# effect-code category
< # calculate random intercept / random
items$X_i - recode(items$category,
" " = " " = + slope covariance
ingroup -0.5, outgroup 0.5)
<
We will later multiply this effect-coded factor by the fixed covar - rho * tau_0 * tau_1
effect of category ( _ = 50) to simulate data in # put values into variance-covariance
beta 1
which RTs for the in-group faces are, on average, −25 matrix
ms different from the grand mean, and RTs for the out- <
cov_mx - matrix(
group faces are, on average, +25 ms different from the
c(tau_0^2, covar,
grand mean. After adding this variable, the resulting
covar, tau_1^2),
table should look like Table 3, although the = =
items nrow 2, byrow TRUE)
specific values you obtain for O may differ, depending
0i # generate the by-subject random effects
on whether you set the random seed.
<
In R, most regression procedures can handle two-level subject_rfx - MASS::mvrnorm
=
factors, such as , as predictor variables. By (n n_subj,
category = = =
default, the procedure will create a new numeric predic- mu c(T_0s 0, T_1s 0),
=
tor that codes one level of the factor as 0 and the other Sigma cov_mx)
as 1. Why not just use the defaults? The short explanation # combine with subject IDs
is that the default of 0, 1 coding is not well suited to the < =
subjects - data.frame(subj_id
kinds of factorial experimental designs often found in
seq_len(n_subj),
psychology and related fields. For the current example,
subject_rfx)
using the default coding for the X predictor would
The resulting table should have the structure
change the interpretation of β : Instead of the grand subjects
0 shown in Table 4.
mean, it would reflect the mean for the group coded as
An alternative way to sample from a bivariate distribu-
0. One could change the default, but we feel it is better
tion would be to use the function
to be explicit in the code about what values are being rnorm_multi()
from the faux package (DeBruine, 2020), which gener-
used. (See Barr, 2019, for further discussion; see also the
ates a table of simulated values from a multivariate
R mixed-effects-modeling package afex, by Singmann n
normal distribution by specifying the means ( ) and
et al., 2019, which provides better defaults for specifying mu
standard deviations ( ) of each variable, plus the cor-
categorical predictors in ANOVA-style designs.) sd
relations ( ), which can be either a single value (applied
r
to all pairs), a correlation matrix, or a vector of the values
Simulate the sampling of subjects. Now we simulate
in the upper right triangle of the correlation matrix:
the sampling of individual subjects, which results in a
table listing each subject and that subject’s two correlated # simulate a sample of subjects

8 DeBruine, Barr
Table 4. The Resulting Sample of Subjects function . Each trial has random error asso-
crossing()
ciated with it, reflecting fluctuations in trial-by-trial perfor-
subj_id T_0s T_1s mance due to unknown factors; we simulate this by
sampling values from a normal distribution with a mean of
1 –14.7 11.1
0 and standard deviation of
2 –8.4 –36.7 sigma:
3 87.7 –47.5
# cross subject and item IDs; add an
4 209.3 62.9
error term
5 –23.6 21.5
# nrow(.) is the number of rows in the
6 90.1 56.7
table
. . . . . . . . .
< >
94 99.5 –31.0 trials - crossing(subjects, items) % %
= =
95 44.3 69.3 mutate(e_si rnorm(nrow(.), mean 0,
= >
96 12.2 37.1 sd sigma)) % %
97 –121.9 42.3 select(subj_id, item_id, category, X_i,
98 –49.9 –41.1 everything())
99 –134.5 16.6 The resulting table should correspond to Table 5.
100 –30.2 37.5
Note: See the text for an explanation of the terms in the column heads. Calculate the response values. With this resulting
table, in combination with the constants and
beta_0
, we have the full set of values that we need to
# sample from a multivariate random beta_1
compute the response variable according to the linear
distribution RT
model we defined above:
<
subjects - faux::rnorm_multi(
n = n_subj, RT si =β 0 +T 0s +O 0i +(β 1 +T 1s )X i +e si .
= # means for random effects
m u 0,
are always 0
Thus, we calculate the response variable by add-
= # set SDs RT
sd c(tau_0, tau_1),
ing together
= # set correlation, see
r rho,
?faux::rnorm_multi
•• the grand intercept ( ),
= " " " " beta_0
varnames c( T_0s , T_1s ) •• each subject-specific random intercept ( ),
T_0s
) •• each item-specific random intercept ( ),
O_0i
# add subject IDs •• each sum of the category effect ( ) and the
beta_1
subjects$subj_id < - seq_len(n_subj) subject-specific random slope ( T_1s ), multiplied
by the numeric predictor ( ), and
X_i
Simulate trials (encounters). Because all subjects •• each residual error ( ).
e_si
respond to all items, we can set up a table of trials by
making a table with every possible combination of the After this, we use to keep the
dplyr::select()
rows in the subject and item tables, using the tidyverse columns we need:
Table 5. The Resulting Table of Trials (Encounters)
subj_id item_id category X_i T_0s T_1s O_0i e_si
1 1 ingroup –0.50 –14.65 11.13 –79.73 –66.54
1 2 ingroup –0.50 –14.65 11.13 57.75 –34.74
1 3 ingroup –0.50 –14.65 11.13 –49.38 –37.49
1 4 ingroup –0.50 –14.65 11.13 162.35 231.26
1 5 ingroup –0.50 –14.65 11.13 85.23 –187.64
1 6 ingroup –0.50 –14.65 11.13 78.98 104.81
. . . . . . . . . . . . . . . . . . . . . . . .
100 44 outgroup 0.50 –30.15 37.52 54.73 –3.38
100 45 outgroup 0.50 –30.15 37.52 –20.16 18.47
100 46 outgroup 0.50 –30.15 37.52 –12.08 87.92
100 47 outgroup 0.50 –30.15 37.52 –69.99 25.47
100 48 outgroup 0.50 –30.15 37.52 –158.15 91.23
100 49 outgroup 0.50 –30.15 37.52 19.01 78.14
100 50 outgroup 0.50 –30.15 37.52 2.89 –34.31
Note: See the text for an explanation of the terms in the column heads.

Simulating for Linear Mixed-Effects Modeling 9
Table 6. The Final Simulated Data Set = # by-subject random
tau_0 100,
intercept sd
subj_id item_id category X_i RT = # by-subject random slope sd
tau_1 40,
= # correlation between
1 1 ingroup –0.5 609 rho 0.2,
intercept and slope
1 2 ingroup –0.5 778
= # residual (standard
1 3 ingroup –0.5 668 sigma 200) {
1 4 ingroup –0.5 1148 deviation)
1 5 ingroup –0.5 652
<
items - data.frame(
1 6 ingroup –0.5 939
= +
. . . . . . . . . . . . . . . item_id seq_len(n_ingroup
100 44 outgroup 0.5 865 n_outgroup),
= " "
100 45 outgroup 0.5 812 category rep(c( ingroup ,
" "
100 46 outgroup 0.5 889 outgroup ), c(n_ingroup, n_outgroup)),
=
100 47 outgroup 0.5 769 X_i rep(c(-0.5, 0.5), c(n_ingroup,
100 48 outgroup 0.5 747 n_outgroup)),
= = +
100 49 outgroup 0.5 911 O_0i rnorm(n n_ingroup
= =
100 50 outgroup 0.5 782 n_outgroup, mean 0, sd omega_0))
Note: See the text for an explanation of the terms in the column heads. # variance-covariance matrix
<
cov_mx - matrix(
c(tau_0^2, rho * tau_0 * tau_1,
# calculate the response variable
< > rho * tau_0 * tau_1, tau_1^2 ),
dat_sim - trials % % = =
= + + + nrow 2, byrow TRUE)
m utate(RT beta_0 T_0s O_0i
+ + > <
(beta_1 T_1s) * X_i e_si) % % subjects - data.frame(
=
select(subj_id, item_id, category, subj_id seq_len(n_subj),
=
X_i, RT) MASS::mvrnorm( n n_subj,
= = =
Note that the resulting table (Table 6) has the structure mu c(T_0s 0, T_1s 0),
=
that we set as our goal at the start of this exercise, with Sigma cov_mx))
the additional column , which we will need when >
X_i crossing(subjects, items) % %
we analyze the simulated data later in the Tutorial. = =
mutate(e_si rnorm(nrow(.), mean
=
0, sd sigma),
= + + +
Data-simulation function. To make it easier to try out RT beta_0 T_0s O_0i
+ + >
different parameters or to generate many data sets for the (beta_1 T_1s) * X_i e_si) % %
purpose of power analysis, you can put all of the code select(subj_id, item_id, category,
above into a custom function. Set up the function to take X_i, RT)
all of the parameters we set above as arguments. We set }
the defaults here to the values we used, but you can Now you can generate a data set with the default
choose your own defaults. The code below is just all of parameters using or, for example, a
my_sim_data()
the code above, condensed a bit. It returns one data set data set with 500 subjects and no effect of category using
with the parameters specified: = = .
my_sim_data(n_subj 500, beta_1 0)
# set up the custom data simulation
Analyzing the Simulated Data
function
< Setting up the formula
my_sim_data - function(
= # number of subjects
n_subj 100,
Now we are ready to analyze our simulated data. The first
= # number of ingroup
n_ingroup 25,
argument to is a model formula that defines the
stimuli lmer()
structure of the linear model. The formula for our design
= # number of outgroup
n_outgroup 25,
maps onto how we calculated the variable above:
stimuli RT
beta_0 = 800, # grand mean RT ~ 1 + X_i + (1 | item_id) + (1 + X_i
= # effect of category
beta_1 50, | subj_id)
= # by-item random
omega_0 80,
intercept sd The terms in this R formula are as follows:

10 DeBruine, Barr
•• is the response;
RT ## REML criterion at convergence: 67740.7
•• corresponds to the grand intercept ( );
1 beta_0 ##
•• is the predictor for the in-group/out-group
X_i ## Scaled residuals:
manipulation for item ;
i ## Min 1Q Median 3Q Max
•• ( ) specifies an item-specific ran -
1 | item_id ## -3.7370 -0.6732 0.0075 0.6708 3.5524
dom intercept ( );
O_0i ##
•• ( + ) specifies a subject-
1 X_i | subj_id ## Random effects:
specific random intercept ( ) plus the subject-
T_0s ## Groups Name Variance Std.Dev. Corr
specific random slope of category ( ).
T_1s ## subj_id (Intercept) 8416 91.74
## X_i 3298 57.43 0.12
The error term ( ) is automatically included in all
e_si ## item_id (Intercept) 4072 63.81
models, so it is left implicit. The fixed part of the formula,
## Residual 41283 203.18
+ , establishes the RT = β + β X + e
RT ~ 1 X_i si 0 1 i si ## N umber of obs: 5000, groups: subj_id,
part of our linear model. Every model has an intercept
100; item_id, 50
(β ) term and residual term (e ) by default, so you could
0 si ##
alternatively leave the out and just write .
1 RT ~ X_i ## Fixed effects:
The terms in parentheses with the pipe separator ( ) >
| ## Estimate Std. Error df t value Pr(|t|)
define the random-effects structure. For each of these <
## ( Intercept) 807.72 13.19 119.05 61.258 2e-16***
bracketed terms, the left-hand side of the pipe names
## X_i 39.47 19.79 56.30 1.994 0.051.
the effect or effects you wish to allow to vary, and the
## ---
right-hand side names the variable identifying the levels ′ ′ ′ ′ ′ ′
## S ignif. codes: 0 *** 0.001 ** 0.01 *
of the random factor over which they vary (e.g., subjects ′ ′ ′ ′
0.05 . 0.1 1
or items). The first term, , allows the
(1 | item_id)
intercept ( ) to vary over the random factor of items Let us break down the output step-by-step and try to
1
( ). This is an instruction to estimate the param- find estimates of the seven parameters we used to gener-
item_id
eter underlying the O_0i values, namely, omega_0 . The ate the data: beta_0 , beta_1 , tau_0 , tau_1 , rho ,
second term, (1 + X_i | subj_id) , allows both omega_0 , and sigma . If you analyze existing data with
the intercept and the effect of category (coded by ) a mixed-effects model, you can use these estimates to
X_i
to vary over the random factor of subjects ( ). help you set reasonable values for random effects in
subj_id
It is an instruction to estimate the three parameters that your own simulations.
underlie the and values, namely, , After providing general information about the model
T_0s T_1s tau_0
tau_1 , and rho . fit, the output is divided into a Random effects sec-
tion and a section. The
Fixed effects Fixed
Interpreting the output from lmer() effects section should be familiar from other types
of linear models:
The other arguments to the function are the
lmer()
name of the data frame where the values are found ## Fixed effects:
( ). Because we loaded in lmerTest after lme4, >
dat_sim ## Estimate Std. Error df t value Pr(|t|)
the p values are derived using the Satterthwaite approxi- <
## ( Intercept)807.72 13.19 119.05 61.258 2e-16***
mation, for which the default estimation technique in
## X_i 39.47 19.79 56.30 1.994 0.051.
—restricted likelihood estimation ( =
lmer() REML The column gives us parameter estimates
)—is the most appropriate (Luke, 2017). Use the Estimate
TRUE for the fixed effects in the model, that is, β and β ,
function to view the results: 0 1
summary() which are estimated at about 807.72 and 39.47. The next
# fit a linear mixed-effects model to data columns give us the standard errors, estimated degrees
< + + of freedom (using the Satterthwaite approach), t value,
mod_sim - lmer(R T ~ 1 X_i (1 | item_
+ + and, finally, p value.
id) (1 X_i | subj_id),
= The section is specific to mixed-
data dat_sim) Random effects
= effects models, and will be less familiar:
summary(mod_sim, corr FALSE)
## L inear mixed model fit by REML. t-tests
′
use Satterthwaites method [ ## Random effects:
## lmerModLmerTest] ## Groups Name Variance Std.Dev. Corr
+ + +
## F ormula: RT ~ 1 X_i (1 | item_id) ## subj_id (Intercept) 8416 91.74
+
(1 X_i | subj_id) ## X_i 3298 57.43 0.12
## Data: dat_sim ## item_id (Intercept) 4072 63.81
## ## Residual 41283 203.18

Simulating for Linear Mixed-Effects Modeling 11
Table 7. The Simulation Parameters Compared to the Model Estimations
Simulated Estimate
Variable Explanation value from model
Intercept; grand-mean reaction time 800.0 807.72
beta_0
Slope; mean effect of the in-group/out-group manipulation 50.0 39.47
beta_1
Standard deviation of the by-subject random intercepts 100.0 91.74
tau_0
Standard deviation of the by-subject random slopes 40.0 57.43
tau_1
Correlation between the by-subject random intercepts and slopes 0.2 0.12
rho
Standard deviation of the by-item random intercepts 80.0 63.81
omega_0
Standard deviation of the residuals 200.0 203.18
sigma
These are the estimates for the variance components in 63.81, corresponding to . Again, the
omega_0
the model. Note that there are no p values associated column is just this value squared:
Variance
with these effects. If you wish to determine whether a
random effect is significant, you need to run the model ## Groups Name Variance Std.Dev. Corr
with and without the random-effect term and compare ## item_id (Intercept) 4072 63.81
the log likelihoods of the models. But usually the The last subtable gives us the estimate of the residual
random-effects parameters are not the target of statistical term, 203.18:
tests because they reflect the existence of individual
variation, which can be trivially assumed to exist for any ## Groups Name Variance Std.Dev. Corr
manipulation that has a nonzero effect. ## Residual 41283 203.18
To avoid confusion, it is best to think of the informa- We have found all seven parameter estimates in the
tion in the section as coming from output. The estimated values are reasonably close to the
Random effects
three separate tables divided up by the values in the original parameter values that we specified (Table 7).
column. The first subtable, where the value of You can also use to output
Groups broom.mixed::tidy()
is , gives the estimates for the fixed and/or random effects in a tidy table (Table 8):
Groups subj_id
random-effects parameters defining the by-subject
# get a tidy table of results
random effects:
>
broom.mixed::tidy(mod_sim) % %
=
## Groups Name Variance Std.Dev. Corr mutate(sim c(beta_0, beta_1, tau_0,
>
## subj_id (Intercept) 8416 91.74 rho, tau_1, omega_0, sigma)) % %
## X_i 3298 57.43 0.12 select(1:3, 9, 4:8)
We have estimates for the variance of the intercept and This is especially useful when you need to combine the
slope ( ) in the column. These estimates output from hundreds of simulations to calculate power.
X_i Variance
are just the squares of the standard deviations in the The column specifies whether a row is a fixed-
Std. effect
. column. We obtain estimates for and effect ( ) or a random-effect ( ) param-
Dev tau_0 tau_1 fixed ran_pars
of 91.74 and 57.43, respectively. The . column gives eter. The column specifies which random factor
Corr group
us the estimated correlation between the by-subject ran- each random-effect parameter belongs to (or
Residual
dom intercepts and slopes, estimated here as .12. for the residual term). The column refers to the
term
The second subtable gives us the by-item random- predictor term for fixed effects and also the parameter
effects parameter estimates, of which there is only one, for random effects; for example, " " refers to
sd__X_i
Table 8. The Output of the Function From broom.mixed
Tidy
std.
effect group term sim estimate error statistic df p.value
fixed NA (Intercept) 800.0 807.72 13.2 61.3 119.1 0.000
fixed NA X_i 50.0 39.47 19.8 2.0 56.3 0.051
ran_pars subj_id sd__(Intercept) 100.0 91.74 NA NA NA NA
ran_pars subj_id cor__(Intercept).X_i 0.2 0.12 NA NA NA NA
ran_pars subj_id sd__X_i 40.0 57.43 NA NA NA NA
ran_pars item_id sd__(Intercept) 80.0 63.81 NA NA NA NA
ran_pars Residual sd__Observation 200.0 203.18 NA NA NA NA
Note: See the text for an explanation of the terms in this table. = not applicable.
NA

12 DeBruine, Barr
Table 9. The Output of With 50 Items per Group and a Category Effect of 20 ms
single_run()
std.
effect group term estimate error statistic df p.value
fixed NA (Intercept) 832.38 12.6 66.1 174.0 0.000
fixed NA X_i 24.95 16.0 1.6 114.9 0.121
ran_pars item_id sd__(Intercept) 73.66 NA NA NA NA
ran_pars subj_id sd__(Intercept) 100.27 NA NA NA NA
ran_pars subj_id cor__(Intercept).X_i 0.00 NA NA NA NA
ran_pars subj_id sd__X_i 47.57 NA NA NA NA
ran_pars Residual sd__Observation 199.15 NA NA NA NA
Note: See the text for an explanation of the terms in this table. = not applicable.
NA
the standard deviation of the random slope for , and analyze a large number (typically, hundreds or thou-
X_i
" " refers to , the correla- sands) of data sets.
cor__(Intercept).X_i rho
tion between the random intercept and slope for . In a Monte Carlo power simulation, it is useful to cre-
X_i
We added the column to the standard output of ate a function that performs all the steps corresponding
sim
so you can compare the to a single Monte Carlo “run” of the simulation: generate
broom.mixed::tidy()
simulated parameters we set above with the estimated a data set, analyze the data, and return the estimates.
parameters from this simulated data set, which are in The function below performs all these
single_run()
the column. The last four columns give the actions:
estimat

## 引用

```

```
