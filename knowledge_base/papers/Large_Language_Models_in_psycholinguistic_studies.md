---
title: Large Language Models in psycholinguistic studies
authors: Fritz Guenther, Giovanni Cassani
year: None
keywords: Language Models, Large Language Models, computational modelling
created: 2025-11-28 15:38:20
---

# Large Language Models in psycholinguistic studies

## 基本信息

- **作者**: Fritz Guenther, Giovanni Cassani
- **年份**: None
- **關鍵詞**: Language Models, Large Language Models, computational modelling

## 摘要

We are currently witnessing a veritable explosion of studies employing Large Language
Models (LLMs) in the cognitive sciences. Here, we focus on their use in psycholinguistics,
that is, for the study of human language processing. LLMs are primarily trained to predict
upcoming or masked words in a given context. We briefly describe the transformer
architecture which endows LLMs with impressive abilities to achieve this objectives, and
review how the components of this architecture are of interest to psycholinguistics. We
then review how LLMs are applied in research, focusing on (1) measuring
surprisal/probabilities of a word given a context; (2) extracting representations/embeddings
these models produce, and (3) prompting/probing these models to produce an output,
treating them similarly to human participants.
Keywords: Language Models; Large Language Models; computational modelling;
psycholinguistics

## 研究背景

## 研究方法

## 主要結果

## 討論與結論

## 個人評論

## 相關文獻

## 完整內容

LLMS IN PSYCHOLINGUISTICS 1
Large Language Models in psycholinguistic studies
Fritz Günther1 and Giovanni Cassani2
1Department of Psychology, Humboldt-Universität zu Berlin, Germany
2Department Cognitive Science and Artificial Intelligence, Tilburg University, The
Netherlands
Corresponding author:
Fritz Günther
Unter den Linden 6, 10099 Berlin
fritz.guenther@hu-berlin.de
Author Note
Fritz Günther received funding from the German Research Foundation (DFG),
Emmy-Noether grant “What’s in a name?” (project number 459717703).

LLMS IN PSYCHOLINGUISTICS 2
Abstract
We are currently witnessing a veritable explosion of studies employing Large Language
Models (LLMs) in the cognitive sciences. Here, we focus on their use in psycholinguistics,
that is, for the study of human language processing. LLMs are primarily trained to predict
upcoming or masked words in a given context. We briefly describe the transformer
architecture which endows LLMs with impressive abilities to achieve this objectives, and
review how the components of this architecture are of interest to psycholinguistics. We
then review how LLMs are applied in research, focusing on (1) measuring
surprisal/probabilities of a word given a context; (2) extracting representations/embeddings
these models produce, and (3) prompting/probing these models to produce an output,
treating them similarly to human participants.
Keywords: Language Models; Large Language Models; computational modelling;
psycholinguistics

LLMS IN PSYCHOLINGUISTICS 3
Large Language Models in psycholinguistic studies
Key points
• Large Language Models (LLMs) are neural networks trained on large corpora with
the objective to predict words in context. To that end, they make use of the
transformer architecture, which is described here briefly
• While LLMs have a wide range of scientific and applied use cases, this chapter
focuses on studies using LLMs to understand human language processing
• We identify three ways in which LLMs have been utilized for that purpose, and
review some studies for each: (1) measuring surprisal/probabilities of a word given a
context; (2) extracting representations/embeddings these models produce for their
objective, and (3) prompting/probing these models to produce an output, treating
them similarly to human participants
• For prompting, we also explore how these models have been used in the role of
informants or research assistants
Introduction
Over the last years we have witnessed a veritable explosion of research on Large
Language Models (LLMs), which was further boosted by their public exposition following
the release of LLM-based chatbot applications such as ChatGPT. The current chapter
provides an overview of their application in psycholinguistic research, that is, the
employment of LLMs for the purpose of studying human language behavior and language
processing. With this specific focus, we purposefully leave aside an overwhelming number
of studies on LLMs; especially related research lines that focus more on LLM behavior,
such as examinations whether LLMs behave in a human-like manner (e.g. Dentella et al.,
2023; Mahowald et al., 2024), or studies that use methods from psychology to investigate
the language behavior of LLMs (e.g. Binz & Schulz, 2023).

LLMS IN PSYCHOLINGUISTICS 4
General mechanisms of LLMs
At their core, different LLMs share a few traits. First, they are trained using very
large amounts of text, which surpass human language experience by multiple orders of
magnitude (although, see Warstadt et al., 2023 for a systematic attempt at training LLMs
with realistic input sizes). Second, these models learn through an error-driven learning
mechanism, which at its core tries to predict (sub-)lexical tokens in context and then
adjusts the internal model representations in order to improve accuracy of the prediction.
This learning procedure implements a fundamental mechanism in human language learning
and processing (Federmeier, 2007), which has fueled the interest and relevance of these
models for psycholinguistic research.
For the purpose of this chapter, we distinguish two main classes of LLMs:
auto-regressive models and Masked Language Models (see Chang & Bergen, 2024, for an
overview of LLMs). Autoregressive models such as the Generative Pre-trained Transformer
(GPT; Radford, 2018) predict the next token in a stream of text, and hence only access the
preceding context to influence prediction. This allows them to generate text token by
token. On the other hand, Masked Language Models (MLMs) such as the Bi-directional
Encoder Representations from Transformers (BERT) model (Devlin et al., 2019), predict
tokens that have been masked by relying on both preceding and subsequent context. This
distinction is crucial when using these models in psycholinguistic studies, as the learning
mechanism influences the representations and their cognitive plausibility in specific tasks.
For example, using a MLM to study online sentence comprehension is unwarranted given
that the model expects information from (not yet presented) subsequent context.
Conversely, an auto-regressive model’s representations will only depend on the left context
and thus may not fully capture behavior where the interpretation of a word is updated
following subsequent materials, as in discourse processing.
Another important aspect of these models that bears relevance for psycholinguistic
research is the way text is fed as input. More traditional language models such as Latent

LLMS IN PSYCHOLINGUISTICS 5
Semantic Analysis (LSA, Landauer and Dumais, 1997) or word2vec (Mikolov et al., 2013)
were based on the distributional patterns of word tokens, and were thus unable to
represent words that did not appear in their training corpora with sufficient frequency.
LLMs, on the contrary, first tokenize their input using a mix of whole words – those that
are likely to be encountered often – and part-words that can be productively re-used to
encode less frequent or novel words (Gage, 1994; Kudo, 2018; Schuster & Nakajima, 2012).
For example, a very frequent word like list may be stored as token in its entirety, while a
less frequent word like unlisted might be tokenized as un, ##list, ##ed. These tokens can
be productively used to recognize other infrequent words such as enlisted or unlimited.
These sub-lexical tokens are not restricted to affixes: the driving force is how often they
can be productively re-used to minimize the number of tokens in which a word not stored
in the model’s vocabulary can be divided.
Once the input text is tokenized, each token indexes a vector representation (or
embedding). During training, the vector representation is used to make predictions and
gets updated based on prediction error, developing into a general-purpose representation
that is optimized for the prediction task and encodes the distributional properties of the
token (Lenci et al., 2022). This is in essence very similar to previous prediction- based
word embedding models such as word2vec (Mikolov et al., 2013). The novelty of LLMs,
and the aspect that made them so effective, lies in what happens in the subsequent layers
and specifically in the attention mechanism (Vaswani et al., 2017). Implementation details
aside, which vary from model to model, the general framework works as follows: Through a
series of layers, the embedding of a word is transformed following the influence that the
(representations of) co-occurring tokens exert (see Hussain et al., 2024, for a more detailed
yet psycholinguistic-friendly treatment of the attention mechanism which falls outside of
the scope of this chapter). Attention heads are also trained as part of the same error-driven
mechanism. These models thus rely on two core, intertwined components: on the one end,
the model stores a context-independent representation of each token; on the other hand, it

LLMS IN PSYCHOLINGUISTICS 6
learns a set of attention weights, or parameters, that productively modify the
context-independent representation to make the model better at predicting the next or
masked token (Cassani et al., 2024).
Overall, LLMs have been shown to capture relevant aspects of natural languages at
different levels of analysis. The first analyses focused on syntactic abilities (Hewitt &
Manning, 2019; Linzen & Baroni, 2021; Rogers et al., 2020), whereas more recent analyses
are shifting their attention towards semantics (Cassani et al., 2024; Cevoli et al., 2022;
Haber & Poesio, 2024). Given the wide context they can consider while contextualising
representations, these models have also been applied to study discourse-level phenomena
(Gao & Feng, 2025; Long et al., 2024). Finally, when trained on speech rather than text,
they show learning of phonetics and phonology (Pouw et al., 2024; Shen et al., 2024).
Using LLMs for psycholinguistic studies
There are different ways in which researchers can interact with LLMs and derive
data and measurements from them. Here, we will examine the main options:
surprisal/probabilities, representations/embeddings, and probing/prompting
Surprisal/probabilities
At their very core, LLMs are trained to predict words in context. Thus, at each
point in a text, they produce a conditional probability of a token given the current context.
In auto-regressive models such as GPT (Radford, 2018), this is the text preceding a token;
in MLMs such as BERT (Devlin et al., 2019), it is the text preceding and following a
token. The exact number of tokens considered as context further depends on the specific
model. Oftentimes, researchers use the negative logarithm of that conditional probability –
called surprisal – for empirical research. An important hyper-parameter that characterizes
many LLMs bears relevance about surprisal estimates:temperature, which affects the
entropy of the probability distribution an LLM outputs for a given prediction (i.e., makes
it “sharper” or “flatter”). Liu et al. (2024) show that LLMs surprisal estimates better fit
reading times if temperature is appropriately scaled, highlighting the many degrees of

LLMS IN PSYCHOLINGUISTICS 7
freedom these models give and that researchers have to grapple with when using these tools
to study human language processing.
Due to its close alignment with the concept of surprisal from the predictive
processing literature (Frank et al., 2015), LLM-based surprisal values can serve as a
valuable predictor in studies on sentence and text processing (Wilcox et al., 2020): They
can be derived at scale, and are more differentiated than traditional measures such as
human-sourced cloze values or predictability ratings, or corpus-sourced transitional word
probabilities derived from observed word sequences (which are very often zero).
Accordingly, several studies have used LLM-based surprisal values to predict reading times
in self-paced reading times (de Varda, Marelli, & Amenta, 2024), eye-movement patterns
(de Varda, Marelli, & Amenta, 2024), or EEG components such as the N400 (de Varda,
Marelli, & Amenta, 2024; Michaelov et al., 2022, 2024). Results on (i) which LLMs
perform best, (ii) if they outperform human ratings, and (iii) to what extent this differs
between different task setups and outcome metrics are currently still mixed (de Varda,
Marelli, & Amenta, 2024; Michaelov et al., 2022, 2024). Interestingly, a common pattern
seems to be that more complex LLMs tend to provide poorer surprisal predictors for
human processing data (de Varda, Marelli, & Amenta, 2024; Oh & Schuler, 2023).
Surprisal has also been studied as a possible operationalisation of syntactic
complexity and acceptability, assuming that more complex and ungrammatical
constructions will elicit higher surprisal estimates in LLMs in critical regions (Gulordava
et al., 2018; Linzen & Baroni, 2021) or for the whole construction (Hu et al., 2024; see
however Leivada et al., 2024). However, a recent large scale benchmark with syntactic
complex sentences found that LLMs systematically underestimates processing costs for
syntactically complex sentences (Huang et al., 2024), inviting caution in establishing simple
linking hypotheses between LLMs’ outputs and cognitive processes relating to syntax.

LLMS IN PSYCHOLINGUISTICS 8
Representations/embeddings
Throughout the layers of an LLM, each processed word will be represented by a
high-dimensional activation vector that closely resembles distributional semantic vectors or
word embeddings from previous generations of (distributional) language models such as
LSA, GloVe, word2vec, or fastText (Lenci et al., 2022). Notably, already these previous
models have been highly successful in operationalizing semantics for psycholinguistic
studies (Günther et al., 2019; Kumar, 2021). In most cases, these vectors are used to
measure the semantic similarity between words, typically as their cosine similarity.
One interesting point of divergence between LLMs and previous generations of
distributional semantic/embedding models is that the latter (except for specifically crafted
exceptions; Schütze, 1998) produce type-level semantic representations (i.e., one fixed and
static vector for the word tomato), while LLMs produce token-level contextualized
semantic representations for each individual instance of a word (i.e., the vectors for tomato
in I went to my garden and plucked a tomato and I was cooking some pasta with a tasty
tomato sauce will be different). This opens up the opportunity to investigate critical
phenomena such as polysemy, meaning ambiguity, and meaning modulations in context at
scale (Apidianaki, 2023; Cassani et al., 2024; Haber & Poesio, 2024). Notably, although
static type-level representations are available in the very first layers of LLMs, these tend to
not perform very well; better results for tasks relating to lexical semantics are often
obtained by averaging the contextualized token-level representations from a number of
different sentences (Cassani et al., 2024; Lenci et al., 2022).
Since LLMs are actually trained to predict tokens rather than natural words, they
can also be used to obtain representations at the sub-lexical level and provide
representations for out-of-vocabulary words and non-words, as the vector sum of their
contained tokens. Similarly, they can be used to obtain representations at the supra-lexical
level (sentences or texts), by adding up the (contextualized) vectors of the words they
include, or by directly extracting sentence embeddings for models that encode them (Devlin

LLMS IN PSYCHOLINGUISTICS 9
et al., 2019). Combining these two possibilities, de Varda, Gatti, et al. (2024) found that
human-produced definitions for given word but also non-word targets are semantically more
similar to the target they were produced for than the definitions provided for other targets.
Representations for lexical elements at different scales can be also productively used
to study how a certain behavior is produced, and whether the internal mechanisms and
representations used by LLMs can inform our understanding of language processing in
humans. For example, LLMs’ representations have been related to brain imaging data
(Schrimpf et al., 2021), although see Guest and Martin (2023) for common pitfalls in this
endeavor and how to properly use computational models to develop theories about human
cognitive processes.
Prompting/probing
Finally, users can interact with LLMs via prompting, which is the interaction the
wider public is accustomed to through chatbots like chatGPT. Here, the LLM produces the
token with the highest probability given the prompt, adds this token to the context, and
repeats that process until it produces a designated <end> token. This ability to generate
text allows psycholinguists and other researchers to elicit responses to instructions from
these models as if they were human participants (Duan et al., 2024). As noted above, this
is commonly used to directly compare the language behavior of LLMs to that of humans
(Cai et al., 2024; Dentella et al., 2023).
However, prompting can also be used in psycholinguistic studies that specifically
examine human language behavior, especially to assist researchers in labour-intensive tasks.
For example, many psycholinguistic studies rely on carefully controlled word
stimulus sets with specific semantic characteristics, such as word similarities, concreteness
scores, valence scores, or sensorimotor associations (Brysbaert et al., 2014; Hill et al., 2015;
Lynott et al., 2020; Warriner et al., 2013). Especially over the last decade, these scores
have typically been obtained in large-scale rating studies that require many participants
and are thus very resource-intensive. However, recent studies have shown that the same

LLMS IN PSYCHOLINGUISTICS 10
ratings collected via prompting LLMs – which are far more economical to collect at scale –
are well aligned with human ratings (Amouyal et al., 2024; Heyman & Heyman, 2024; Kauf
et al., 2024; Martínez, Molero, et al., 2024; Trott, 2024). This allows psycholinguistic
researchers to obtain these measures for example for rare words, more complex expressions,
under-resourced languages, or specific semantic dimensions for which no ratings exist yet
(Martínez, Conde, et al., 2024; Martínez, Molero, et al., 2024; Trott, 2024).
As another example, careful data annotation – such as annotating and coding open
participant responses – usually requires a lot of investment from several annotators.
Gilardi et al. (2023) demonstrate that ChatGPT outperforms paid crowd workers on
several text-annotation tasks, such as scoring their relevance to a specific topic or
evaluating their sentiment. On the other hand, Ettinger et al. (2023) report that
annotations usually performed by trained experts, such as annotations of sentence meaning
structure, are only partially correct and still prone to many errors when performed by
LLMs. Thus, LLMs are currently probably best used as screening tools for initial response
coding, that can then be cross-checked by trained experts. Prompting can also be helpful
for other tasks typically performed by research assistants, such as the generation of
linguistic stimuli for experimental studies (as has already successfully been done in other
areas of psychological research; e.g., Bitew et al., 2023; Hommel et al., 2022;
Laverghetta Jr. et al., 2024; Säuberli & Clematide, 2024).
Finally, collecting LLM responses via prompting can also have practical benefits as
an (almost) risk- and cost-free method for pilot testing behavioral experiments, for example
to adjust instructions and to prepare analysis protocols in advance (Heyman & Heyman,
2024). On the other hand, Heyman and Heyman (2024) also warn that this might be used
for data fabrication, either by researchers or by participants in online studies.
One important aspect to consider in this process is however whether the model
being used is open or not, as this can have profound impact on reproducibility in science.
Using closed models (often newer, commercially used models) for annotation or norm

LLMS IN PSYCHOLINGUISTICS 11
generation exposes to the risk that the model is later updated and that it is no longer
possible to reconstruct which specific version was used for generating a specific set of
stimuli or annotations, limiting the degree to which the pipeline can be reproduced and
replicated (Wulff et al., 2024). Importantly, surprisal estimates and representations can
only be obtained from open models.
Conclusion
LLMs have revolutionised many aspects of science, and given their very scope, it is
no wonder they have claimed a prominent role in computational modeling of language
(Baayen, 2024). They are powerful tools to interact with and study language in different
ways: we have reviewed three (surprisal estimates, representations, prompting) which are
most relevant to psycholinguistics and have been productively used to illuminate different
aspects of language processing at different levels of description. However, these models
come with challenges and problems (Cuskley et al., 2024). First, their training is often very
different from human language experience and is also opaque, both in terms of data and
optimization techniques, which limit their plausibility as algorithmic models of language
processing. At the same time, training an LLM from scratch is prohibitive for most
research labs. Closed models exacerbate the issue, with potential harmful consequences on
reproducibility in science. Moreover, these models have a plethora of hyper-parameters
which can profoundly influence their behavior. It can be daunting to systematically test all
possible configurations, but especially to know which ones are most relevant: LLMs vary in
their training objective, number of parameters, vocabulary size, tokenizers, training data
(both type and quantity), but researchers can further tweak their behavior acting, for
example, on temperature. To navigate this complexity, tutorials (Hussain et al., 2024) and
tools (Cassani et al., 2024; Misra, 2022) can be very useful in providing an overview of best
practices and easy access to a wide array of LLMs. However, ease of access granted by
these tools should not be mistaken for ease of use: these are complex models that require
careful consideration and solid scientific practices to produce reliable and trustworthy

LLMS IN PSYCHOLINGUISTICS 12
scientific progress.

LLMS IN PSYCHOLINGUISTICS 13
References
Amouyal, S., Meltzer-Asscher, A., & Berant, J. (2024, March). Large language models for
psycholinguistic plausibility pretesting. In Y. Graham & M. Purver (Eds.), Findings
of the association for computational linguistics: Eacl 2024 (pp. 166–181).
Association for Computational Linguistics.
https://aclanthology.org/2024.findings-eacl.12
Apidianaki, M. (2023). From word types to tokens and back: A survey of approaches to
word meaning representation and interpretation. Computational Linguistics, 49(2),
465–523. https://doi.org/10.1162/coli_a_00474
Baayen, R. H. (2024). The wompom. Corpus Linguistics and Linguistic Theory, 20(3),
615–648.
Binz, M., & Schulz, E. (2023). Using cognitive psychology to understand gpt-3. Proceedings
of the National Academy of Sciences, 120(6), e2218523120.
Bitew, S. K., Deleu, J., Develder, C., & Demeester, T. (2023). Distractor generation for
multiple-choice questions with predictive prompting and large language models.
Joint European Conference on Machine Learning and Knowledge Discovery in
Databases, 48–63.
Brysbaert, M., Warriner, A. B., & Kuperman, V. (2014). Concreteness ratings for 40
thousand generally known english word lemmas. Behavior research methods, 46,
904–911.
Cai, Z., Duan, X., Haslett, D., Wang, S., & Pickering, M. (2024). Do large language models
resemble humans in language use? Proceedings of the Workshop on Cognitive
Modeling and Computational Linguistics, 37–56.
Cassani, G., Bianchi, F., Attanasio, G., Marelli, M., & Günther, F. (2024). Meaning
Modulations and Stability in Large Language Models: An Analysis of BERT
Embeddings for Psycholinguistic Research. PsyArXiv preprint.
https://doi.org/10.31234/osf.io/b45ys

LLMS IN PSYCHOLINGUISTICS 14
Cevoli, B., Watkins, C., Gao, Y., & Rastle, K. (2022). Shades of meaning: Natural
language models offer insights and challenges to psychological understanding of
lexical ambiguity. PsyArXiv preprint.
https://doi.org/https://doi.org/10.31234/osf.io/z8rmp
Chang, T. A., & Bergen, B. K. (2024). Language model behavior: A comprehensive survey.
Computational Linguistics, 50(1), 293–350. https://doi.org/10.1162/coli_a_00492
Cuskley, C., Woods, R., & Flaherty, M. (2024). The limitations of large language models
for understanding human language and cognition. Open Mind, 8, 1058–1083.
https://doi.org/10.1162/opmi_a_00160
Dentella, V., Günther, F., & Leivada, E. (2023). Systematic testing of three language
models reveals low language accuracy, absence of response stability, and a
yes-response bias. Proceedings of the National Academy of Sciences, 120(51),
e2309583120.
de Varda, A. G., Gatti, D., Marelli, M., & Günther, F. (2024). Meaning beyond lexicality:
Capturing pseudoword definitions with language models. Computational Linguistics,
1–31.
de Varda, A. G., Marelli, M., & Amenta, S. (2024). Cloze probability, predictability
ratings, and computational estimates for 205 english sentences, aligned with existing
eeg and reading time data. Behavior Research Methods, 56(5), 5190–5213.
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019, June). BERT: Pre-training of
deep bidirectional transformers for language understanding. In J. Burstein,
C. Doran, & T. Solorio (Eds.), Proceedings of the 2019 conference of the north
American chapter of the association for computational linguistics: Human language
technologies, volume 1 (long and short papers) (pp. 4171–4186). Association for
Computational Linguistics. https://doi.org/10.18653/v1/N19-1423
Duan, X., Li, S., & Cai, Z. G. (2024). Macbehaviour: An r package for behavioural
experimentation on large language models. arXiv preprint arXiv:2405.07495.

LLMS IN PSYCHOLINGUISTICS 15
Ettinger, A., Hwang, J. D., Pyatkin, V., Bhagavatula, C., & Choi, Y. (2023). " you are an
expert linguistic annotator": Limits of llms as analyzers of abstract meaning
representation. arXiv preprint arXiv:2310.17793.
Federmeier, K. D. (2007). Thinking ahead: The role and roots of prediction in language
comprehension. Psychophysiology, 44(4), 491–505.
Frank, S. L., Otten, L. J., Galli, G., & Vigliocco, G. (2015). The erp response to the amount
of information conveyed by words in sentences. Brain and Language, 140, 1–11.
Gage, P. (1994). A new algorithm for data compression. The C Users Journal, 12(2), 23–38.
Gao, Q., & Feng, D. (2025). Deploying large language models for discourse studies: An
exploration of automated analysis of media attitudes. PloS one, 20(1), e0313932.
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). Chatgpt outperforms crowd workers for
text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30),
e2305016120.
Guest, O., & Martin, A. E. (2023). On logical inference over brains, behaviour, and
artificial neural networks. Computational Brain & Behavior, 6(2), 213–227.
Gulordava, K., Bojanowski, P., Grave, E., Linzen, T., & Baroni, M. (2018). Colorless green
recurrent networks dream hierarchically. North American Chapter of the Association
for Computational Linguistics. https://api.semanticscholar.org/CorpusID:4460159
Günther, F., Rinaldi, L., & Marelli, M. (2019). Vector-space models of semantic
representation from a cognitive perspective: A discussion of common
misconceptions. Perspectives on Psychological Science, 14, 1006–1033.
Haber, J., & Poesio, M. (2024). Polysemy—evidence from linguistics, behavioral science,
and contextualized language models. Computational Linguistics, 50(1), 351–417.
https://doi.org/10.1162/coli_a_00500
Hewitt, J., & Manning, C. D. (2019). A structural probe for finding syntax in word
representations. Proceedings of the 2019 Conference of the North American Chapter

LLMS IN PSYCHOLINGUISTICS 16
of the Association for Computational Linguistics: Human Language Technologies,
Volume 1 (Long and Short Papers), 4129–4138.
Heyman, T., & Heyman, G. (2024). The impact of chatgpt on human data collection: A
case study involving typicality norming data. Behavior Research Methods, 56(5),
4974–4981.
Hill, F., Reichart, R., & Korhonen, A. (2015). Simlex-999: Evaluating semantic models
with (genuine) similarity estimation. Computational Linguistics, 41, 665–695.
Hommel, B. E., Wollang, F.-J. M., Kotova, V., Zacher, H., & Schmukle, S. C. (2022).
Transformer-based deep neural language modeling for construct-specific automatic
item generation. Psychometrika, 87(2), 749–772.
Hu, J., Mahowald, K., Lupyan, G., Ivanova, A., & Levy, R. (2024). Language models align
with human judgments on key grammatical constructions. Proceedings of the
National Academy of Sciences, 121(36), e2400917121.
Huang, K.-J., Arehalli, S., Kugemoto, M., Muxica, C., Prasad, G., Dillon, B., & Linzen, T.
(2024). Large-scale benchmark yields no evidence that language model surprisal
explains syntactic disambiguation difficulty. Journal of Memory and Language, 137,
104510.
Hussain, Z., Binz, M., Mata, R., & Wulff, D. U. (2024). A tutorial on open-source large
language models for behavioral science. Behavior Research Methods, 56(8),
8214–8237.
Kauf, C., Chersoni, E., Lenci, A., Fedorenko, E., & Ivanova, A. (2024). Log probabilities
are a reliable estimate of semantic plausibility in base and instruction-tuned
language models. Proceedings of the 7th BlackboxNLP Workshop: Analyzing and
Interpreting Neural Networks for NLP, 263–277.
Kudo, T. (2018). Subword regularization: Improving neural network translation models
with multiple subword candidates. arXiv preprint arXiv:1804.10959.

LLMS IN PSYCHOLINGUISTICS 17
Kumar, A. A. (2021). Semantic memory: A review of methods, models, and current
challenges. Psychonomic Bulletin & Review, 28(1), 40–80.
Landauer, T. K., & Dumais, S. T. (1997). A solution to plato’s problem: The latent
semantic analysis theory of acquisition, induction, and representation of knowledge.
Psychological review, 104(2), 211.
Laverghetta Jr., A., Luchini, S., Linell, A., Reiter-Palmon, R., & Beaty, R. (2024). The
creative psychometric item generator: A framework for item generation and
validation using large language models. arXiv preprint arXiv:2409.00202.
Leivada, E., Günther, F., & Dentella, V. (2024). Reply to hu et al.: Applying different
evaluation standards to humans vs. large language models overestimates ai
performance. Proceedings of the National Academy of Sciences, 121(36),
e2406752121.
Lenci, A., Sahlgren, M., Jeuniaux, P., Cuba Gyllensten, A., & Miliani, M. (2022). A
comparative evaluation and analysis of three generations of distributional semantic
models. Language resources and evaluation, 56(4), 1269–1313.
Linzen, T., & Baroni, M. (2021). Syntactic structure from deep learning. Annual Review of
Linguistics, 7(1), 195–212.
Liu, T., Škrjanec, I., & Demberg, V. (2024, August). Temperature-scaling surprisal
estimates improve fit to human reading times – but does it do so for the “right
reasons”? In L.-W. Ku, A. Martins, & V. Srikumar (Eds.), Proceedings of the 62nd
annual meeting of the association for computational linguistics (volume 1: Long
papers) (pp. 9598–9619). Association for Computational Linguistics.
https://doi.org/10.18653/v1/2024.acl-long.519
Long, Y., Luo, H., & Zhang, Y. (2024). Evaluating large language models in analysing
classroom dialogue. npj Science of Learning, 9(1), 60.

LLMS IN PSYCHOLINGUISTICS 18
Lynott, D., Connell, L., Brysbaert, M., Brand, J., & Carney, J. (2020). The Lancaster
Sensorimotor Norms: multidimensional measures of perceptual and action strength
for 40,000 English words. Behavior Research Methods, 52, 1271–1291.
Mahowald, K., Ivanova, A. A., Blank, I. A., Kanwisher, N., Tenenbaum, J. B., &
Fedorenko, E. (2024). Dissociating language and thought in large language models.
Trends in Cognitive Sciences, 28, 517–540.
Martínez, G., Conde, J., Reviriego, P., & Brysbaert, M. (2024). EXPRESS: AI-generated
estimates of familiarity, concreteness, valence and arousal for over 100,000 Spanish
words. Quarterly Journal of Experimental Psychology, 17470218241306694.
Martínez, G., Molero, J. D., González, S., Conde, J., Brysbaert, M., & Reviriego, P. (2024).
Using large language models to estimate features of multi-word expressions:
Concreteness, valence, arousal. arXiv preprint arXiv:2408.16012.
Michaelov, J. A., Bardolph, M. D., Van Petten, C. K., Bergen, B. K., & Coulson, S. (2024).
Strong prediction: Language model surprisal explains multiple n400 effects.
Neurobiology of language, 5(1), 107–135.
Michaelov, J. A., Coulson, S., & Bergen, B. K. (2022). So cloze yet so far: N400 amplitude
is better predicted by distributional information than human predictability
judgements. IEEE Transactions on Cognitive and Developmental Systems, 15(3),
1033–1042.
Mikolov, T., Sutskever, I., Chen, K., Corrado, G. S., & Dean, J. (2013). Distributed
representations of words and phrases and their compositionality. Advances in neural
information processing systems, 26.
Misra, K. (2022). Minicons: Enabling flexible behavioral and representational analyses of
transformer language models. ArXiv, abs/2203.13112.
https://api.semanticscholar.org/CorpusID:247627806

LLMS IN PSYCHOLINGUISTICS 19
Oh, B.-D., & Schuler, W. (2023). Why does surprisal from larger transformer-based
language models provide a poorer fit to human reading times? Transactions of the
Association for Computational Linguistics, 11, 336–350.
Pouw, C., Kloots, M. d. H., Alishahi, A., & Zuidema, W. (2024). Perception of phonological
assimilation by neural speech recognition models. Computational Linguistics, 1–29.
Radford, A. (2018). Improving language understanding by generative pre-training.
Rogers, A., Kovaleva, O., & Rumshisky, A. (2020). A primer in BERTology: What we
know about how BERT works (M. Johnson, B. Roark, & A. Nenkova, Eds.).
Transactions of the Association for Computational Linguistics, 8, 842–866.
https://doi.org/10.1162/tacl_a_00349
Säuberli, A., & Clematide, S. (2024). Automatic generation and evaluation of reading
comprehension test items with large language models. arXiv preprint
arXiv:2404.07720.
Schrimpf, M., Blank, I. A., Tuckute, G., Kauf, C., Hosseini, E. A., Kanwisher, N.,
Tenenbaum, J. B., & Fedorenko, E. (2021). The neural architecture of language:
Integrative modeling converges on predictive processing. Proceedings of the National
Academy of Sciences, 118(45), e2105646118.
Schuster, M., & Nakajima, K. (2012). Japanese and korean voice search. 2012 IEEE
international conference on acoustics, speech and signal processing (ICASSP),
5149–5152.
Schütze, H. (1998). Automatic word sense discrimination. Computational Linguistics,
24(1), 97–123.
Shen, G., Watkins, M., Alishahi, A., Bisazza, A., & Chrupała, G. (2024, June). Encoding
of lexical tone in self-supervised models of spoken language. In K. Duh, H. Gomez,
& S. Bethard (Eds.), Proceedings of the 2024 conference of the north american
chapter of the association for computational linguistics: Human language

LLMS IN PSYCHOLINGUISTICS 20
technologies (volume 1: Long papers) (pp. 4250–4261). Association for
Computational Linguistics. https://doi.org/10.18653/v1/2024.naacl-long.239
Trott, S. (2024). Can large language models help augment english psycholinguistic
datasets? Behavior Research Methods, 1–19.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., &
Polosukhin, I. (2017). Attention is all you need. Advances in neural information
processing systems, 30.
Warriner, A. B., Kuperman, V., & Brysbaert, M. (2013). Norms of valence, arousal, and
dominance for 13,915 english lemmas. Behavior research methods, 45, 1191–1207.
Warstadt, A., Mueller, A., Choshen, L., Wilcox, E., Zhuang, C., Ciro, J., Mosquera, R.,
Paranjabe, B., Williams, A., Linzen, T., et al. (2023). Findings of the babylm
challenge: Sample-efficient pretraining on developmentally plausible corpora.
Proceedings of the BabyLM Challenge at the 27th Conference on Computational
Natural Language Learning.
Wilcox, E. G., Gauthier, J., Hu, J., Qian, P., & Levy, R. P. (2020). On the predictive
power of neural language models for human real-time comprehension behavior.
ArXiv, abs/2006.01912.
Wulff, D. U., Hussain, Z., & Mata, R. (2024). The behavioral and social sciences need open
llms.

## 引用

```

```
