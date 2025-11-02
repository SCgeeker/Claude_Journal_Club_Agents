---
title: Multimodal Language Models Show Evidence of Embodied Simulation
authors: R. Jones, Sean Trott
year: 2024
keywords: ["grounding", "multimodal language models", "embodiment"]
created: 2025-10-29 16:40:18
---

# Multimodal Language Models Show Evidence of Embodied

## 基本信息

- **作者**: R. Jones, Multimodal Language, Introduction Winterand, Models Show, Sean Trott
- **年份**: N/A
- **關鍵詞**: 

## 摘要

Multimodallargelanguagemodels(MLLMs)aregainingpopularityaspartialsolutionstothe“symbolgrounding
problem”facedbylanguagemodelstrainedontextalone. However,littleisknownaboutwhetherandhowthese
multiplemodalitiesareintegrated. Wedrawinspirationfromanalogousworkinhumanpsycholinguisticsonembodied
simulation,i.e.,thehypothesisthatlanguagecomprehensionisgrounded insensorimotorrepresentations. Weshow
thatMLLMsaresensitivetoimplicit visualfeatureslikeobjectshape(e.g.,“Theeggwasintheskillet”impliesa
fryingeggratherthanoneinashell). ThissuggeststhatMLLMsactivateimplicitinformationaboutobjectshape
whenitisimpliedbyaverbaldescriptionofanevent. Wefindmixedresultsforcolorandorientation,andruleout
thepossibilitythatthisisduetomodels’insensitivitytothosefeaturesinourdatasetoverall. Wesuggestthatboth
humanpsycholinguisticsandcomputationalmodelsoflanguagecouldbenefitfromcross-pollination,e.g.,withthe
potentialtoestablishwhethergroundedrepresentationsplayafunctional roleinlanguageprocessing.
Keywords:grounding,multimodallanguagemodels,embodiment

## 研究背景

## 研究方法

## 主要結果

## 討論與結論

## 個人評論

## 相關文獻

## 完整內容

Multimodal Language Models Show Evidence of Embodied
Simulation
Cameron R. Jones, Sean Trott
DepartmentofCognitiveScience,UCSanDiego
9500GilmanDrive,LaJolla,CA
cameron@ucsd.edu,sttrott@ucsd.edu
Abstract
Multimodallargelanguagemodels(MLLMs)aregainingpopularityaspartialsolutionstothe“symbolgrounding
problem”facedbylanguagemodelstrainedontextalone. However,littleisknownaboutwhetherandhowthese
multiplemodalitiesareintegrated. Wedrawinspirationfromanalogousworkinhumanpsycholinguisticsonembodied
simulation,i.e.,thehypothesisthatlanguagecomprehensionisgrounded insensorimotorrepresentations. Weshow
thatMLLMsaresensitivetoimplicit visualfeatureslikeobjectshape(e.g.,“Theeggwasintheskillet”impliesa
fryingeggratherthanoneinashell). ThissuggeststhatMLLMsactivateimplicitinformationaboutobjectshape
whenitisimpliedbyaverbaldescriptionofanevent. Wefindmixedresultsforcolorandorientation,andruleout
thepossibilitythatthisisduetomodels’insensitivitytothosefeaturesinourdatasetoverall. Wesuggestthatboth
humanpsycholinguisticsandcomputationalmodelsoflanguagecouldbenefitfromcross-pollination,e.g.,withthe
potentialtoestablishwhethergroundedrepresentationsplayafunctional roleinlanguageprocessing.
Keywords:grounding,multimodallanguagemodels,embodiment
1. Introduction WinterandBergen,2012). Whilethereisongoing
debateaboutthefunctionalrelevanceofembodied
Recent advances in Large Language Models simulation(Glenbergetal.,2008;MahonandCara-
(LLMs) have generated an explosion of inter- mazza,2008;Montero-Melisetal.,2022;Ostarek
estintheirunderlyingcapabilitiesandlimitations and Bottini, 2021), the evidence points to some
(Thirunavukarasuetal.,2023). Oneoft-citedlimita- degreeofcross-talkbetweenlinguisticandsenso-
tionofcontemporaryLLMsisthattheyaretrained rimotorneuralsystems.
onlinguisticinputalone(BenderandKoller,2020),
andthus,unlikehumans,lackaccesstoembodied
Muchofthisevidencecomesfromthesentence-
experience—seen by some as a prerequisite for picture verification task paradigm (Stanfield and
Zwaan, 2001). In this task, participants read a
languageunderstanding(Bisketal.,2020;Harnad,
shortsentence(e.g.,“Hehammeredthenailinto
1990;MolloandMillière,2023). MultimodalLarge
thewall”),thenseeapictureofanobject(e.g.,a
LanguageModels(MLLMsDriessetal.,2023;Gird-
nail)andmustdecidewhethertheobjectwasmen-
haretal.,2023;Huangetal.,2023)—whichlearnto
tionedintheprecedingsentence. Crucially,when
associatelinguisticrepresentationswithdatafrom
othermodalities—maybeapartialsolutiontothis
theimageoftheobjectmatchestheorientation(or
shape, color, etc.) implied by the sentence (e.g.,
symbol grounding problem (Harnad, 1990). Yet
the nail is horizontal rather than vertical), partici-
despiteimpressiveperformancebyMLLMs(Doso-
pants are faster and more accurate in their deci-
vitskiyetal.,2021), littleisknownabouthowdis-
sions (Stanfield and Zwaan, 2001; Pecher et al.,
tinctmodalities(e.g.,languageandvision)arein-
2009; Connell, 2007). Because the object is the
tegrated withinamodel’srepresentationalspace,
same(e.g.,anegg),humansmustbeinferringvi-
astheyappeartobeinhumans.
sualfeaturesbasedonpropertiesoftheeventitself
Weaddressthisgapbyturningtoananalogous
(e.g.,aneggcookinginaskillet).
debate about the extent to which human seman-
ticrepresentationsaregroundedinsensorimotor In the current work, we applied these method-
experience(Barsalou,1999). Theembodiedsimu- ologicalinsightstoimproveourunderstandingof
lationhypothesis(Bergen,2015;Glenberg,2010) MLLMs. We ask whether MLLM’s internal repre-
arguesthatlanguageunderstandinginvolvesthe sentationsoflinguisticinput(e.g.,"Hehammered
activation of grounded representations, i.e. that the nail into the wall") are more similar to repre-
thesameneuraltissuerecruitedtoperceiveorpar- sentations of images that match visual features
ticipateinanevent(e.g.,kickingasoccerball)is implied by that input than those that do not. To
alsoengagedtounderstandlanguageaboutthat addressthisquestion,weadaptedmaterialsfrom
event(e.g.,“Shekickedtheball”). Indeed,awide threepsycholinguisticstudiesthatprovideevidence
bodyofexperimentalevidencesuggeststhatsome forsimulationoftheimpliedorientation(Stanfield
degree of sensorimotor activation occurs during and Zwaan, 2001), shape (Pecher et al., 2009),
language processing (Zwaan and Pecher, 2012; andcolor(Connell,2007)ofobjects. Notethatthis

approachdiffersfromastandardclassificationtask: tion,convertingthemintoprobabilitiesofthemodel
ratherthanclassifyingimagesonthebasisofwhich associatingeachimagewithagivensentence:
objectstheycontain(e.g.,“acupofcoffee”)orex-
plicitfeaturesofthoseobjects(e.g.,“ablackcupof exp(S ·I )
p = i j
coffee”),weareaskingwhethertheMLLMactivates ij (cid:80)2
exp(S ·I )
implicit featuresthatcouldbeinferredfromamore k=1 i k
holisticeventrepresentation(e.g.,“Joannenever whereS istheembeddingforsentencei,I is
i j
took milk in her coffee” implies that the coffee is theembeddingforimagej,andp isthesoftmax
ij
black). probabilitythatsentenceimatcheswithimagej.
Tostatisticallyevaluatethemodel’sperformance,
weconductedat-testtocomparetheprobabilities
2. Methods
ofmatching(e.g.,p andp )againstmismatching
11 22
(e.g.,p andp )sentence-imagepairs. Asignif-
12 21
2.1. Materials icantresult,wherethematchingprobabilitiesare
greaterthanmismatchingones,wouldindicatethat
Weusedstimulifromthreeexperimentsthatmea-
the MLLM’s representations are sensitive to the
sured visual simulation in human participants.
visualpropertiesimpliedbythelinguisticinput.
Items were organized as quadruplets, consisting
ofapairofimagesandapairofsentences. Sen-
tencepairsdifferedbyimplyingthatanobjecthad
2.3. Vision-Language Models
acertainvisualproperty(shape,color,ororien-
tation). Eachoftheimagesinapairmatchedthe WeevaluatefourdifferentCLIP-basedVisionTrans-
impliedvisualfeatureinoneofthesentences(and formerswithdifferentnumbersofparametersand
thereforemismatchedtheother,seeFigure1). trainingregimesinordertotestthegeneralizability
60quadrupletsfromPecheretal.(2009)varied androbustnessofimpliedvisualfeatureeffects.
theimpliedshapeofanobject. Asentencesuch TheVisionTransformer(ViT)architectureadapts
as“Therewasanegginthe[refrigerator/skillet]”im- the Transformer to handle visual data (Dosovit-
pliedthattheeggwaseitherinitsshellorcracked skiy et al., 2021). The ViT divides an image into
open. A pair of black-and-white images of eggs fixed-size non-overlapping patches that are then
matchedoneofthesesentencesbydisplayingthe linearly embedded into input vectors. A classifi-
relevantvisualfeature. Connell(2007)collected12 cation head is attached to the output to produce
quadrupletsthatvarytheimpliedcolorofanob- the final prediction. Despite their simplicity and
ject. “Joanne[never/always]tookmilkinhercoffee” lackofinductivebiases(e.g.,convolutionallayers),
implies black/brown coffee. The images differed ViTs have achieved competitive performance on
onlyincolor. Finally,StanfieldandZwaan(2001) various visual tasks, especially when pre-trained
collected24quadrupletsofsentencesimplyingdif- onlargedatasets(Dosovitskiyetal.,2021;Schuh-
ferentorientationsofanitem,andline-drawings mannetal.,2022).
thatwererotatedtomatchtheimpliedorientation. CLIP (Contrastive Language–Image Pre-
Forinstance“Derekswunghisbatastheballap- training)employscontrastivelearningtoassociate
proached”suggestsahorizontalbat,while“Derek imageswithtextdescriptions(Radfordetal.,2021).
heldhisbathighastheballapproached”suggests ThemodeljointlytrainsaViTimageencoderand
averticalbat. a text encoder to predict the correct pairings of
(image, text) pairs. This allows CLIP to learn a
sharedsemanticspacebetweenimagesandtext.
2.2. Model Evaluation
Weevaluatefourpre-trainedCLIPmodels:
ToprobeMLLMs,weimplementedacomputational ViT-B/32: Thebasemodelfrom(Radfordetal.,
analogueofthesentence-pictureverificationtask. 2021). ViT-B/32usesapatchsizeof32pxandhas
Ourprimaryquestionwaswhetheramodel’srep- 120M parameters. It was trained on 400 million
resentation of a given linguistic input (e.g., "He 224x224pixelimage-textpairsover32epochs.
hammeredthenailintothewall")wasmoresimilar ViT-L/14: Thebest-performingmodelfrom(Rad-
toitsrepresentationofanimagethatmatchedan ford et al., 2021, described in the paper as ViT-
impliedvisualfeature(e.g. horizontalorientation) L/14@336px). ViT-L/14usesapatchsizeof14px
compared to an image that did not (e.g. a verti- and has 430M parameters. It was pre-trained in
calnail). Foreachsentence-imagepair,wefound thesamemannerasViT-B/32andthenfine-tuned
thedotproductbetweentheMLLMembeddingof at336pxforoneadditionalepoch.
the sentence and the image. This value quanti- ViT-H/14: A larger model based on the CLIP
fiesthesimilaritybetweenthelinguisticandvisual architecture (Ilharco et al., 2021). ViT-H/14 has
representationswithinthemodel. Thedotproduct 1BparametersandwastrainedontheLAION2B
valueswerethenpassedthroughasoftmaxfunc- datasetfor16epochs(Schuhmannetal.,2022).

Figure1: Thedatasetconsistedofpairsofsentencesandimages,formingquadruplets. Eachsentencein
apairimpliedthatanobjecthadacertainvisualproperty(e.g. browncolor). Eachimpliedvisualproperty
wasmatchedbyoneofthepairofimages. Theimpliedvisualpropertiesincludedshape(Left, Pecher
etal.,2009),color(Center, Connell,2007),andorientation(Right, StanfieldandZwaan,2001).
ImageBind: an MLLM that learns a joint em- manipulatedvisualfeatureslikeorientation,orthat
bedding across six modalities, including images, thesefeaturesaredifficulttoidentifyintheimage
text,audio,depth,thermal,andIMUdata(Girdhar stimuliused. Totestthispossibility,weranafollow-
etal.,2023). Internally,aTransformerarchitecture up“manipulationcheck”todeterminewhetherthe
isusedforallmodalities. Theimageandtexten- MLLMsweresensitivetoorientationandcolorwhen
codersarebasedontheViT-H/14model. theywereexplicitlymentionedinthetext. Theanal-
ysiswasvirtuallyidenticaltotheprimaryanalysis
above, except that we used a sentence template
3. Results
thatexplicitly describedspecificvisualfeaturesof
theobjectinquestion,e.g.,“Itwasa[COLOR][OB-
We tested whether MLLMs were sensitive to the
JECT]”.WethenaskedwhethertheMLLMscould
implied visual features in the sentence using a t-
successfullymatchsentenceswithexplicitvisual
test. The test compared the probability assigned
features(e.g.,“Itwasaredtrafficlight”vs. “Itwas
toimagesthatmatchedtheimpliedvisualfeatures
agreentrafficlight”).
versusthosethatdidnot. Allofthemodels,except
Allmodelstestedshowedaneffectofbothcolor
for the smallest (ViT-B/32), showed a significant
effect of shape. ImageBind showed the largest
(p<.01)andorientation(p<.01). Thatis,mod-
elsassignedhigherprobabilitytoimageswithvisual
effect: t(238)=4.65,p<0.001. ViT-B/32showed
an effect in the expected direction but it did not
featuresthatmatchedthoseexplicitlymentioned in
thesentence. ThisindicatesthattheMLLMsare
reachsignificance: t(238)=1.81,p=0.072.
sensitivetocolorandorientation,andthatstim-
TheresultsforColorweremorevaried. Neither
ulusqualityissufficienttoidentifythesefeatures.
the ViT-B/32 and ViT-L/14 models showed a sig-
nificanteffectofmatchbetweenthecolorimplied
by a sentence and the color of an image. Both 4. Discussion
ViT-H/14 (t(46) = 2.16,p < 0.05) and ImageBind
(t(46) = 2.85,p < 0.01 demonstrated sensitivity OurcentralquestionwaswhetherMLLMsshowed
toimpliedcolorpropertiesalthoughtheseeffects effects that have been taken as evidence of em-
werelessrobustthanforshape. bodiedsimulationinhumans(StanfieldandZwaan,
Noneofthemodelsshowedsignificantsensitivity 2001). WeaskedwhetherMLLMsweresensitiveto
to implied orientation from linguistic cues. The specificvisualfeatures(shape,color,andorienta-
largestnumericaleffectwasshownbyImageBind: tion)thatwereimplied butnotexplicitlymentioned
t(94)=1.09,p=0.278(seeTable4). byaverbaldescriptionofanevent. Wefoundrobust
evidence of simulation for implied shape, mixed
evidenceforsimulationofimpliedcolor,andno
3.1. Follow-up Analysis of Explicit
evidenceofsimulationforimpliedorientation.
Features
Importantly,noneofthesevisualfeatureswere
One potential explanation for the null results re- explicitlymentionedinthesentences. Thus,ifan
portedaboveisthatMLLMsareinsensitivetothe MLLMexhibitssensitivitytoimpliedshape,itsug-

Figure2: Comparisonofmeanprobabilityvaluesassignedtoimagesthateithermatched(bluebars)or
didnotmatch(redbars)impliedvisualfeaturesofasentence. FourVisionTransformerModels(ViT-B/32,
ViT-L/14,ViT-H/14,andImageBind)),wereevaluatedacrossthreedatasets(Shape,Orientation,and
Color). Errorbarsdenote95%bootstrappedconfidenceintervals.
gests that the model is activating event-specific in the relationship between images and descrip-
representationsoftheobjectsmentionedinasen- tions. Orientationcanbeinfluencedbyrotationor
tence. In humans, an analogous effect is taken viewpointsandcolorsimilarlyvarieswithlighting.
asevidenceofembodiedsimulation(Stanfieldand Implicitindicationsofthesefeaturesintextlabels
Zwaan, 2001; Bergen, 2015). The findings here maythereforebelessreliablethanindicationsof
suggest that such an effect can be produced via moreinvariantfeaturessuchasshape. Futurework
exposuretolarge-scalestatisticalassociationsbe- could ask whether color and orientation are less
tweenpatternsinimagesandpatternsintext. integrated withlinguisticrepresentationsinMLLMs,
orsimplyhardertoinferfromtextdescriptions.
Model Shape Color Orientation
Future studies could also explore whether
ViT-B/32 0.072 0.112 0.965
MLLMssimulatemodalitiesbeyondvision. There
ViT-L/14 <0.001 0.240 0.510 isevidencethathumansactivateothersensorimo-
ViT-H/14 <0.001 0.036 0.323 tor modalities, such as auditory volume (Winter
ImageBind <0.001 0.006 0.278 andBergen,2012)andmotoraction(Fischerand
Zwaan,2008),thoughevidenceforothermodalities
Table1: p-valuesfromt-testsmeasuringtheeffect
likeolfactionislimited(SpeedandMajid,2018).
ofmatchingimpliedvisualfeaturesbetweenlabels
and images. All models except ViT-B/32 show a Finally,thereisconsiderabledebatewithinpsy-
significanteffectforShape. ViT-H/14andImage- cholinguistics over whether embodied simulation
BindbothshowsignificanteffectsforColor. None playsafunctional roleinlanguagecomprehension,
ofthemodelsshowaneffectofOrientation. orwhetheritisepiphenomenal(OstarekandBot-
tini,2021;MahonandCaramazza,2008;Glenberg
ItisunclearwhyMLLMsdidnotappeartosimu- etal.,2008). Futureworkcouldcontributetothisde-
lateorientation(orcolor,insomecases). Critically, batebyusingMLLMsas“subjects”: specifically,re-
wheneitherfeaturewasexplicit inthetext,amatch searcherscould“lesion”representationsoffeatures
effectwasobtained(seeSection3.1);thissuggests like shape and ask whether this causally affects
thenulleffectswerenotduetooverallinsensitivity processing of sentences implying object shape.
tothosevisualfeatures. Instead,MLLMsappearto This would join the broader “neuroconnectionist”
activatesomeimplicitvisualfeaturesmorereadily research program that aims to unify research on
thanothers. Thisvariationcouldbedrivenbynoise humancognitionandonmodelsinspiredbycogni-

tion(Doerigetal.,2023). Louise Connell. 2007. Representing object
colour in language comprehension. Cognition,
102(3):476–485.
5. Conclusion
AdrienDoerig,RowanPSommers,KatjaSeeliger,
WefoundthatMLLMsaresensitivetowhethervi- BlakeRichards,JenannIsmael,GraceWLind-
sual features that are implied by a sentence are say,KonradPKording,TaliaKonkle,MarcelAJ
matchedinanimage,aphenomenontakenasevi- VanGerven,NikolausKriegeskorte,etal.2023.
denceofembodiedsimulationinhumans. The neuroconnectionist research programme.
NatureReviewsNeuroscience,pages1–20.
6. Ethical Considerations and
Alexey Dosovitskiy, Lucas Beyer, Alexander
Limitations Kolesnikov, Dirk Weissenborn, Xiaohua Zhai,
Thomas Unterthiner, Mostafa Dehghani,
ThestudyislimitedinthatitonlyevaluatesVision
MatthiasMinderer,GeorgHeigold,SylvainGelly,
Transformers. Other VLM architectures may pro-
Jakob Uszkoreit, and Neil Houlsby. 2021. An
duce different associations between text and im-
ImageisWorth16x16Words: Transformersfor
ages. Thenumberofitemsforsomeofthedatasets
ImageRecognitionatScale.
wassmall. Somemodelsmayhaveshownsignif-
icantmatcheffectswithalargernumberofitems. Danny Driess, Fei Xia, Mehdi SM Sajjadi, Corey
Onepotentiallimitationofthestudyisthatthetasks Lynch, Aakanksha Chowdhery, Brian Ichter,
giventohumanandLLMparticipantsarenotquite AyzaanWahid,JonathanTompson,QuanVuong,
analogous. Inthepicture-verificationtask,thepar- Tianhe Yu, et al. 2023. Palm-e: An embod-
ticipantisawarethattheimpliedvisualfeaturesare iedmultimodallanguagemodel. arXivpreprint
irrelevant: theirtaskistoidentifywhethertheobject arXiv:2303.03378.
waspresentinthesentence. Themodelscannot
be so instructed: the measure of association be- MartinHFischerandRolfAZwaan.2008. Embod-
tweenthesentenceandimagerepresentationswill iedlanguage: Areviewoftheroleofthemotor
be based on all features that were useful to the systeminlanguagecomprehension. Quarterly
modelduringCLIPpre-training. Nevertheless,the journalofexperimentalpsychology,61(6):825–
results show that models are sensitive to these 850.
impliedfeaturesevenwhentheyarenotexplicitly
mentioned. Rohit Girdhar, Alaaeldin El-Nouby, Zhuang Liu,
MannatSingh,KalyanVasudevAlwala,Armand
Joulin,andIshanMisra.2023. Imagebind: One
7. Bibliographical References embeddingspacetobindthemall. InProceed-
ingsoftheIEEE/CVFConferenceonComputer
VisionandPatternRecognition,pages15180–
15190.
Lawrence W Barsalou. 1999. Perceptual sym-
bol systems. Behavioral and brain sciences, Arthur M Glenberg. 2010. Embodiment as a uni-
22(4):577–660. fyingperspectiveforpsychology. Wileyinterdis-
ciplinaryreviews: Cognitivescience,1(4):586–
EmilyMBenderandAlexanderKoller.2020. Climb- 596.
ingtowardsnlu: Onmeaning,form,andunder-
standing in the age of data. In Proceedings of ArthurMGlenberg,MarcSato,andLuigiCattaneo.
the 58th annual meeting of the association for 2008. Use-induced motor plasticity affects the
computationallinguistics,pages5185–5198. processing of abstract and concrete language.
CurrentBiology,18(7):R290–R291.
BenjaminBergen.2015. Embodiment,simulation
and meaning. In The Routledge handbook of StevanHarnad.1990. Thesymbolgroundingprob-
semantics,pages142–157.Routledge. lem. Physica D: Nonlinear Phenomena, 42(1-
3):335–346.
YonatanBisk,AriHoltzman,JesseThomason,Ja-
cobAndreas,YoshuaBengio,JoyceChai,Mirella ShaohanHuang,LiDong,WenhuiWang,YaruHao,
Lapata,AngelikiLazaridou,JonathanMay,Alek- Saksham Singhal, Shuming Ma, Tengchao Lv,
sandrNisnevich,etal.2020.Experiencegrounds LeiCui,OwaisKhanMohammed,QiangLiu,etal.
language. In Proceedings of the 2020 Confer- 2023. Language is not all you need: Aligning
enceonEmpiricalMethodsinNaturalLanguage perceptionwithlanguagemodels. arXivpreprint
Processing(EMNLP),pages8718–8735. arXiv:2302.14045.

Gabriel Ilharco, Mitchell Wortsman, Ross Wight- TingFangTan,andDanielShuWeiTing.2023.
man, Cade Gordon, Nicholas Carlini, Rohan Large language models in medicine. Nature
Taori,AchalDave,VaishaalShankar,Hongseok medicine,pages1–11.
Namkoong,JohnMiller,HannanehHajishirzi,Ali
Bodo Winter and Benjamin Bergen. 2012. Lan-
Farhadi,andLudwigSchmidt.2021. Openclip.
guagecomprehendersrepresentobjectdistance
Ifyouusethissoftware,pleaseciteitasbelow.
bothvisuallyandauditorily. LanguageandCog-
BradfordZMahonandAlfonsoCaramazza.2008. nition,4(1):1–16.
Acriticallookattheembodiedcognitionhypoth-
Rolf A. Zwaan and Diane Pecher. 2012. Revis-
esisandanewproposalforgroundingconcep-
iting Mental Simulation in Language Compre-
tualcontent. Journalofphysiology-Paris,102(1-
3):59–70.
hension: SixReplicationAttempts. PLOSONE,
7(12):e51382.
Dimitri Coelho Mollo and Raphaël Millière. 2023.
The vector grounding problem. arXiv preprint
arXiv:2304.01481.
Guillermo Montero-Melis, Jeroen Van Paridon,
MarkusOstarek,andEmanuelBylund.2022. No
evidenceforembodiment: Themotorsystemis
notneededtokeepactionverbsinworkingmem-
ory. cortex,150:108–125.
Markus Ostarek and Roberto Bottini. 2021.
Towards strong inference in research on
embodiment–possibilities and limitations of
causalparadigms. JournalofCognition,4(1).
DianePecher,SaskiavanDantzig,RolfAZwaan,
andRenéZeelenberg.2009. Shortarticle: Lan-
guagecomprehendersretainimpliedshapeand
orientation of objects. Quarterly Journal of Ex-
perimentalPsychology,62(6):1108–1114.
Alec Radford, Jong Wook Kim, Chris Hallacy,
AdityaRamesh,GabrielGoh,SandhiniAgarwal,
GirishSastry,AmandaAskell,PamelaMishkin,
JackClark,GretchenKrueger,andIlyaSutskever.
2021.LearningTransferableVisualModelsFrom
NaturalLanguageSupervision.
Christoph Schuhmann, Romain Beaumont,
RichardVencu,CadeGordon,RossWightman,
Mehdi Cherti, Theo Coombes, Aarush Katta,
Clayton Mullis, and Mitchell Wortsman. 2022.
Laion-5b: An open large-scale dataset for
training next generation image-text models.
Advances in Neural Information Processing
Systems,35:25278–25294.
LauraJSpeedandAsifaMajid.2018.Anexception
tomentalsimulation: Noevidenceforembodied
odorlanguage. CognitiveScience,42(4):1146–
1178.
RobertAStanfieldandRolfAZwaan.2001. The
effectofimpliedorientationderivedfromverbal
context on picture recognition. Psychological
science,12(2):153–156.
Arun James Thirunavukarasu, Darren Shu Jeng
Ting, Kabilan Elangovan, Laura Gutierrez,

## 引用

```

```
