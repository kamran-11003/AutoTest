# Issta24-Guardian

**Source:** issta24-guardian.pdf  
**Converted:** 2026-01-26 09:23:23

---

## Page 1

Guardian: A Runtime Framework for LLM-Based UI Exploration
DezhiRan HaoWang ZiheSong
KeyLabofHCST(PKU),MOE;SCS, PekingUniversity UniversityofTexasatDallas
PekingUniversity Beijing,China Richardson,USA
Beijing,China tony.wanghao@stu.pku.edu.cn zihe.song@utdallas.edu
dezhiran@pku.edu.cn
MengzhouWu YuanCao YingZhang
PekingUniversity PekingUniversity KeyLabofHCST(PKU);NERCofSE,
Beijing,China Beijing,China PekingUniversity
wmz@stu.pku.edu.cn cao_yuan21@stu.pku.edu.cn Beijing,China
zhang.ying@pku.edu.cn
WeiYang TaoXie
UniversityofTexasatDallas KeyLabofHCST(PKU),MOE;SCS,
Richardson,USA PekingUniversity
wei.yang@utdallas.edu Beijing,China
taoxie@pku.edu.cn
Abstract
executionoftheinvalidatedUIactions,andpromptstheLLMto
Testsforfeature-basedUItestinghavebeenindispensableforen- re-planwiththenewUIactionspace.WeinstantiateGuardian
suringthequalityofmobileapplications(appsforshort).Thehigh withChatGPTandconstructabenchmarknamedFestiValwith58
manuallaborcoststocreatesuchtestshaveledtoastronginterest tasksfrom23highlypopularapps.EvaluationresultsonFestiVal
inautomatedfeature-basedUItesting,whereanapproachautomati- showthatGuardianachieves48.3%successrateand64.0%average
callyexplorestheAppunderTest(AUT)tofindcorrectsequences completionproportion,outperformingstate-of-the-artapproaches
ofUIeventsachievingthetargettestobjective,givenonlyahigh- with154%and132%relativeimprovementwithrespecttothetwo
leveltestobjectivedescription.Giventhatthetaskofautomated metrics,respectively.
feature-basedUItestingresemblesconventionalAIplanningprob-
CCSConcepts
lems,largelanguagemodels(LLMs),knownfortheireffectiveness
inAIplanning,couldbeidealforthistask.However,ourstudy •Softwareanditsengineering→Softwaretestinganddebug-
revealsthatLLMsstrugglewithfollowingspecificinstructionsfor ging;Runtimeenvironments;•Computingmethodologies
UItestingandreplanningbasedonnewinformation.Thislimita- →Naturallanguageprocessing.
tionresultsinreducedeffectivenessofLLM-drivensolutionsfor
Keywords
automatedfeature-basedUItesting,despitetheuseofadvanced
promptingtechniques. UITesting,MobileTesting,AndroidTesting,LargeLanguageMod-
Towardaddressingtheprecedinglimitation,weproposeGuardian, els,RuntimeSystem,SequentialPlanning
aruntimesystemframeworktoimprovetheeffectivenessofauto-
ACMReferenceFormat:
matedfeature-basedUItestingbyoffloadingcomputationaltasks
DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,
fromLLMswithtwomajorstrategies.First,GuardianrefinesUI
WeiYang,andTaoXie.2024.Guardian:ARuntimeFrameworkforLLM-
actionspacethattheLLMcanplanover,enforcingtheinstruc- BasedUIExploration.InProceedingsofthe33rdACMSIGSOFTInternational
tion following of the LLM by construction. Second, Guardian SymposiumonSoftwareTestingandAnalysis(ISSTA’24),September16–20,
deliberatelycheckswhetherthegraduallyenrichedinformation 2024,Vienna,Austria.ACM,NewYork,NY,USA,13pages.https://doi.org/
invalidatespreviousplanningbytheLLM.Guardianremovesthe 10.1145/3650212.3680334
invalidatedUIactionsfromtheUIactionspacethattheLLMcan
plan over, restores the state of the AUT to the state before the 1 Introduction
Toensurethehighqualityofmobileapplications(appsforshort),
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor
feature-basedUItesting[61]focusesonvalidatingthecorefunc-
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcitation
tionalitiesoftheAppUnderTest(AUT),andisindispensable[27,
onthefirstpage.Copyrightsforcomponentsofthisworkownedbyothersthanthe 30,31,46]yetoftenincurssignificantmanualcosts[31,50,61,62].
author(s)mustbehonored.Abstractingwithcreditispermitted.Tocopyotherwise,or
Toreducemanualcosts,itisalong-soughtgoaltoautomatically
republish,topostonserversortoredistributetolists,requirespriorspecificpermission
and/orafee.Requestpermissionsfrompermissions@acm.org. generatefeature-basedUItestsdirectlyfromtestobjectives[27],
ISSTA’24,September16–20,2024,Vienna,Austria denotedasautomatedfeature-basedUItestinginthispaper.Given
©2024Copyrightheldbytheowner/author(s).PublicationrightslicensedtoACM.
anAUTandatestobjectiveasinputs,automatedfeature-based
ACMISBN979-8-4007-0612-7/24/09
https://doi.org/10.1145/3650212.3680334 UItestingexplorestheAUTtofindasequenceofUIactions(i.e.,

## Page 2

ISSTA’24,September16–20,2024,Vienna,Austria DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,WeiYang,andTaoXie
UIevents)toachievethetestobjective.Inparticular,automated
ØHistory 1 ØUI action 1 You are an expert at UI exploration.
feature-basedUItestingsequentiallyselectsoneUIactiononaUI Ø Ø H H i i s s t t o o r r y y 2 3 Ø Ø U U I I a a c c t t i i o o n n 2 3 Ø Ø U U I I a a c c t t i i o o n n 1 2 Ø Ø H H i i s s t t o o r r y y 1 2
s a C c c o r t n e io e s n e n q , o u t n r e i n g th g tl e e y r , n s a e t u h w t e om U U I a I t s a e c c d r t e i f o e e n n at o u u n n re t t - i h l b e a th s A e e U d t T e U s , I t a t n o e d b st j s i e n e c l g t e i c v is t e s in i t s h h e a e c r n h e e n i x e t v t ly e U d a I . q q q q Ø T T T … . a a a .… s s … s k k k … … X Y Z … .… Co ü ü ü ü nt Ø e - I I I x - n n n - t s s - s … - t t t - r r … r - u u u - . - c c c … - t t t - i i i … - o o o -- … n n n - - … A B C -- En P g r in o e m e p ri t n g Ø Ø q q q q U ... I T T … T … a a a a . c s s … s .… t k k k i … o … X Y Z n … 3 . ü ü ü ü - Ø Ø I I I - n n n - s s - s - t H t t . - . r r r - … i u u u - s - c c c t … - o t t t - . i i i - r o … o o - y - n n n … - 3 - A B C -- Full W C o o r m kl p o u a t d a s tion 😵💫
sequentialplanningproblem[7,57,63],whichhasbeeneffectively Domain-Specific Instructions Prompts LLMs
(Domain Knowledge)
tackledbylargelanguagemodels(LLMs)[14,18,52,57,70,75].
Offload computation from
DespitethepromisingeffectivenessofLLMsforsequentialplan- LLMs to an external system
n ba in se g d p U ro I b te le s m tin s g ,s [ t 5 a 2 te , - 7 o 0 f , - 7 th 5] e- a a r r e t s a h p o p w ro n a t c o h a e c s h o i f ev L e LM low -ba e s ff e e d ct f i e v a e t n u e r s e s - a o c R t b t h e t io a e fi i n n n C i o s n a p n g a r t e t e c h d e x e u t o c t U v o e e I d r q Ø Ø T H H a i i s s s k t t o o N X r r e y y w ü A B C Ø o Ø In nt s U e U t x r I I u t a a c c c t t t io i i o o n n n A X Y En P g r in o e m e p ri t n g Y Ø o q u a U T re I a a s a k c n t X e io x p n e 1 ü rt a I t Ø n U s I t H e ru x i p s c t l t o o io r r a y n t i o 1 A n. C W o R m o e p r d k u u l t o c a e a t d d io s n 😌
accordingtoourempiricalinvestigation(Section4.2)andonemay New Context Remained Instructions Prompts
hypothesizetwolikelycontributingfactorsfortheloweffectiveness.
Figure1:ComputationOffloadingfromLLMstoexternal
First,LLMsmaystruggletocomprehendthecontentorenviron-
systems.
ment(i.e.,theUIelements)withintheiroperationalscope.Second,
LLMsmaynotbeskilledatformulatingplanningstrategiesspecific
tosuchexplorationtasks(i.e.,feature-basedUItesting). possessastatisticallowerboundonhallucinationrates,indepen-
Toempiricallyinvestigatetheprecedinghypothesizedcontribut- dentoftheirarchitectureorthequalityoftheirtrainingdata.This
ingfactors,inthispaper,weconductapreliminarystudy(Section2) makesthempronetogeneratinginaccurateinformation,which
toproducetwofindings.First,interestingly,ourstudyresults(Sec- canunderminetheirreliabilityincriticaltasks.Last,LLMshave
tion 2.1) contradict the first hypothesized factor, revealing that been empirically demonstrated to be less effective in following
LLMsare,infact,quitecapableofcomprehendingUIcontent.LLMs multipleorfine-grainedinstructions[20,22,56].Thislimitation
correctlyselectUIactionswithover95%accuracy,evenamidst becomesevenmoresignificantinscenariosinvolvinglongcontexts,
distractingelements.Second,ourstudyresults(Section2.2)show wherethemodels’abilitytoaccuratelyfollowinstructionstendsto
thattheprimarycauseoffailureinexistingapproachesisthesec- decline[26,32].
ondfactor:inadequateplanningstrategies.Thisissueencompasses Tofundamentallytackletheprecedingtheoreticalandempiri-
twomajoraspectsofchallengesdiscussedbelow,asrevealedinour callimitationsofpromptengineering,weintroducecomputation
analysis(whosedetailsareinSection2.2). offloading[9,51]toLLM-basedUIexploration,inspiredbythein-
Challenges.Failingtofollowdomain-specifictaskinstructions.While sightthatsometasksandinstructionsinautomatedfeature-based
LLMscanbeexpertsinunderstandingUIcontent,LLMslackdo- UItestingcanbeformulatedastaskscomputableinanexternal
mainknowledgeinUIexploration[63,70]andexistingapproaches system.Thesetasksrepresentrefinementstrategiesoftheaction
incorporateUI-testing-specificinstructionsintopromptstohelp. spacebasedonhistoricalexploration.Forexample,theinstruction
However,LLMsfailtofollowtheseinstructions,leadingtolowef- ofavoidingrepetitiveactionselectionusedbyDroidbot-GPT[70]
fectiveness.Asdetailedinourpreliminarystudy,despiteDroidbot- canbewrittenasafunctionthatremovesUIactionsiftheyappear
GPT[70]usingexplicitinstructionpromptstoavoidselectingal- inhistoricalactions.AsshowninFigure1,byoffloadingsuchcom-
readyselectedactions,36%oftheplannedactionsaresimplyre- putationtasksfromLLMstoexternalsystems,wecanreducethe
peatinghistoricalactions. taskcomplexityaswellasthelengthofcontexts,whichcircumvent
Failingtoreplanbasedonnewinformation.Thetaskofautomated thetheoreticallimitationscausedbycomputationalcomplexityand
UItestinginvolveshighlydynamic,real-timeexplorationofthe empiricallimitationscausedbymultipleinstructionsfollowingand
AUT,giventhefactthatthesamefunctionalitycanbeimplemented longcontexthandling.
invariouswaysindifferentapps.Asexplorationprogresses,newly ToeffectivelyoffloadthecomputationworkloadsfromLLMs,in
uncoveredinformationcaninvalidatepreviouslyplannedUIactions. thispaper,weproposeGuardian,thefirstandgeneralruntime
Figure5presentsanexampleontheQuizletapp,whereanLLMis frameworkforLLM-basedUIexploration.Figure2presentsthesys-
instructedtoactivatethenightmode.Onthefrontpage,theLLM temarchitecture,consistingofadomainknowledgeloader,memory,
choosestoclickthesearchbuttontopursueashortcutsettingof andexecutionengine.Thedomainknowledgeloaderconsistsof
thenightmode.Whilefindingthatthesearchtabcannotachieve optimizers,validators,anderrorhandlers.Theoptimizersrefine
itspreviousplanningpurpose,theLLMfailstoreplanwiththenew theactionspace,thevalidatorsassesstheneedforreplanning,and
information,stuckinrepeatingclickingthesearchtab. theerrorhandlersresettheAUTforreplanning.Thisapproachis
Addressingtheprecedingchallengeswithadvancedprompten- closelytiedtothenatureofUIexploration,whereinstructionscan
gineeringisnotsufficient,basedonboththeoreticalandempiri- beoffloadedtotheruntimeframeworkandviewedasconstraints
calevidence.First,empiricalfindings[11,44]suggestthattrans- ontheactionspace.Byexternallyexecutingtheseconstraints,disal-
formerLLMsoftenreducemulti-stepcompositionalreasoninginto lowedactionsareremovedfromthecontext,ensuringthatthenew
linearizedsubgraphmatching,ratherthandevelopingsystematic contextadherestotheinstructions,thusmakingtheactionspace
problem-solvingskills.Thisimpliesthat,intaskslikeUItesting, moreconciseandthesetofinstructionsmoremanageable.Imple-
wheremulti-stepreasoningiscrucial,theperformanceofLLMsis mentingthissteprequiresspecificprograms,correspondingtothe
likelytodeclineastaskcomplexityincreases[11].Second,stud- driversinourexecutionengine.Thememorycomponentiscrucial
ies[23]haveshownthatpretrainedlanguagemodelsinherently forbothrefiningtheactionspaceandfacilitatingreplanning.The
memorycomponentkeepsarecordofblockedactions,aidinginthe

## Page 3

Guardian:ARuntimeFrameworkforLLM-BasedUIExploration ISSTA’24,September16–20,2024,Vienna,Austria
• ApubliclyavailableruntimeframeworkGuardian[45]for
effectivelyoffloadingcomputationsfromLLMswithdomain
LLM AUT knowledge.
• Extensive evaluations demonstrating the effectiveness of
GUARDIAN
Guardian.
Execution Engine
2 PreliminaryStudy
LLM Driver UI Driver
Parser WhileLLM-basedapproacheshavebeensuccessfullyappliedto
sequentialplanningproblems[52,70,74,75],ourevaluationin
Section4.2showsthatReAct[75],Reflexion[52],andDroidbot-
Memory
GPT[70],threestate-of-the-artLLM-basedapproaches,allexhibit
Blocked Action Space History Context loweffectivenesswhenappliedtoautomatedfeature-basedUItest-
LLM Perceptible Context ing.Thisobservationleadsustoinvestigatetheunderlyingcauses
oftheirloweffectiveness.Weproposetwoprimaryhypotheses
toexplaintheloweffectivenessobserved:First,LLMsmaylack
Domain Knowledge Loader
thecapabilitytounderstandUIcontent,whichisessentialforsuc-
Optimizer Validator
cessfulautomatedfeature-basedUItesting.Second,LLMsmight
Error Handler comprehendUIcontentadequately,butthepromptingstrategies
employedinexistingLLM-basedapproachesmaynotbefunction-
ingaseffectivelyasintended.
Domain Knowledge
Consequently,wefurtherconductadetailedanalysistoinvesti-
gatethefollowingtworesearchquestions:
Figure2:SystemArchitectureofGuardian.
• RQ1:HoweffectivecanLLMscomprehendUIcontent?
• RQ2:Howeffectivearethepromptingstrategiesinexisting
adjustmentoftheactionspace.Additionally,thememorycompo- approachesintermsofachievingtheirintendedoutcomes?
nentmaintainsahistoricalcontextthatincludesallUIstatesvisited
andLLMperceptiblecontext—therefinedcontextthatLLMcan 2.1 RQ1:UIComprehensionCapabilityofLLMs
accessbasedontheinformationavailableatthetimeofplanning.
Thissectioninvestigatestherootcauseofthelimitedeffectiveness
Thishistoricaldataisessentialforeffectivelyreplanningallowing
ofLLM-basedapproachesinautomatedfeature-basedUItesting,
theframeworktorestorepreviousstatesandadjustthecourseof
specificallyfocusingonwhetherthisproblemstemsfromLLMs’
actionasneeded.Theexecutionengineincludesaparser,anLLM
inadequatecomprehensionofUIcontent.Forinstance,Droidbot-
driver,andaUIdriver.TheLLMdrivermanagestheinteraction
GPT’sinitialevaluationonsimpleropen-sourceappsmaynotade-
withtheLLM,receivingitsresponses,whiletheUIdriverisrespon-
quatelyrepresentitsperformancewithmorecomplex,industrial
sibleforexecutingactionsontheAUTandcollectingtheUIaction
apps.Toaddressthisproblem,ourexperimentsaredesignedtoas-
spacedata.TheparserplaysakeyroleinprocessingboththeLLM
sessboththecomprehensioncapabilityofLLMsforUIcontentand
responsesandtheUIactionspaceinformation,coordinatingwith
theirrobustnessagainsttheincreasingcomplexityofUIelements.
thememorycomponenttomanagetheflowofinstructionsand ExperimentSetup.Ourexperimentalframeworkcentersaround
ensuretheyareappliedcorrectlywithintherefinedactionspace. theUIactionselectiontaskontheMoTIFdataset[5].Inthistask,
ToevaluatetheeffectivenessofGuardian,weinstantiateGuardian
LLMsarepromptedtoselectoneandonlyoneUIelementfroma
withChatGPT[40]andconstructabenchmarknamedFestiValin-
listthatwouldfulfillagivenlow-levelinstruction.Theinstructions,
cluding58feature-basedUItestsfrom23highlypopularindustrial
derivedfromnaturallanguagedescriptionsaccompanyingtheMo-
Androidapps[66]thatarewidelyusedinpreviouswork[5,10,65–
TIFdataset,arecarefullyselectedtoexcludevagueannotationslike
67].WecompareGuardianwiththreestate-of-the-artLLM-based
“clickabutton”.Fromthe28tasksintheMoTIFdataset,weextract
approachesincludingDroidbot-GPT[70],ReAct[75],andReflex-
60specificinstructionsforourexperimentaldataset.Thelengthof
ion[52].EvaluationresultsonFestiValshowthatGuardiansuc-
candidateUIelementstoselectfromrangesfrom3to109,withthe
cessfullygenerates48.3%fullycorrecttestsandcompletes64.0%of
averagelengthbeing28.5andthestandarddeviationbeing20.2.
atestonaverage,substantiallyoutperformingthestate-of-the-art
TofurthertesttheLLMs’robustness,weaugmenttheUIele-
baseline approaches with respect to the two metrics with 154%
mentlistwithirrelevantelementssourcedfromdifferentmobile
and132%relativeimprovement,respectively.Wealsoconductde-
applications,therebycreatingamorechallengingandnoisyenvi-
tailedexperimentstoinvestigatetheeffectivenessoftheindividual
ronmentfortheLLMstonavigate.Supposethelengthofcandidate
algorithmdesignsandtheircontributionstotheeffectivenessof UIelementstoselectfromis𝑛.Weadd50%,100%,and200%noisy
Guardian.
UIelements.Inotherwords,afteraddingthenoisyUIelements
Insummary,thispapermakesthefollowingmaincontributions:
underthethreeconditions,thelengthofcandidateUIelementsto
• Anempiricalstudyrevealingthepoorplanningstrategies selectfrombecomes1.5𝑛,2𝑛,3𝑛,respectively.
of LLM-based approaches in automated feature-based UI StudyresultsofUIcomprehensioncapability.Table1shows
testing. theUIactionselectionaccuracyofdifferentmodels.Inour60-task

## Page 4

ISSTA’24,September16–20,2024,Vienna,Austria DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,WeiYang,andTaoXie
Table1:EffectivenessofUIContentComprehension.
300
Model Original +50%Noise +100% +200% 250
Seq2Act 80.0% - - -
GPT-3.5 96.7% 96.7% 96.7% 93.3% 200
GPT-4 98.3% 96.7% 96.7% 96.7%
150
assessment,GPT-3.5achievedanaccuracyof96.7%,whileGPT-4 100
achievedanimpressiveaccuracyof98.3%,1.23timestheperfor-
manceoftheleadingnon-LLM-basedapproachSeq2Act,whichis 50
fine-tunedontheMoTIFdataset.Ourinspectionoftheonlyfailed
0
caseofGPT-4furtherconfirmsthehigheffectivenessofLLMsfor 0 1 2 3 4 5+
UIcomprehension.Theground-truthUIelementinthefailedtaskis # of Repetition
asearchFieldgivenbytheMoTIFdataset.GPT-4selecteda“wrong”
UIelement,thesearchicon,differentfromtheground-truthUI
element.However,clickingoneitherofthetwoUIelementsonthe
appcanachievetheinstruction“openthesearchfieldicon”.Con-
sequently,wesuspectthatthefailedcaseisnotduetothelimited
effectivenessofLLMs,butthelimitationoftheMoTIFdataset.
IntermsofrobustnessagainstnoisyUIelementsandscaleof
UIelementcandidates,LLMsshowedarelativelysmalldecreasein
performance,droppingfrom96.7%to93.3%accuracyevenwiththe
additionof200%noisyelements.Thisslightdecline,considering
thepotentialsemanticrelevanceoftheaddednoisyelements,un-
derscorestheLLMs’resiliencetoincreasedUIcontentcomplexity.
Answer to RQ1: LLMs demonstrate expert-level comprehen-
sionofUIcontentandmaintainrobustperformance,indicating
thatUIcomprehensionabilityisnotthelimitingfactorinthe
effectivenessofcurrentLLM-basedapproaches.
2.2 RQ2:UnintendedOutcomesagainst
PromptingStrategies
AcknowledgingtheeffectivenessofLLMsinunderstandingUIcon-
tent,ournextfocusshiftstoexaminingtheeffectivenessofcomplex
promptingstrategies.Specifically,weaimtoassesswhetherthese
strategiesareaccuratelyfollowedbyLLMsandiftheyindeedyield
theintendedoutcomes.Thisinvestigationisconductedthrougha
combinationofquantitativeandqualitativeanalysestoprovidea
comprehensiveunderstandingoftheefficacyofpromptingstrate-
giesinthecontextofautomatedfeature-basedUItesting.
ExperimentSetup.Theexperimentsetupforthisresearchques-
tionisthesameasthesetupinSection4.1.
Quantitativeanalysisofinstructionfollowing.Ouranalysis
beginswithDroidbot-GPT,designedtofollowaspecificinstruction:
theLLMshouldnotselectanyUIactionsthathavealreadybeen
choseninprevioustrials.Droidbot-GPTpresentstheLLMwith
a list of previously selected UI actions and instructs it to avoid
them.Compliancewiththisinstructionisassessedbytrackingthe
numberoftimeseachUIelementisselected;anyrepeatedselection
ofaUIelementisconsideredaviolation.
Unfortunately,asdepictedinFigure3,violationsofthisinstruc-
tionarefrequent.Outof449differentUIelements,288UIaction
selections(approximately64%ofallselections)adheretothein-
struction.Therearenumerousinstancesofviolations:88UIaction
selections(20%)involveaUIelementbeingselectedmorethan
twice.
stnemele
IU
detceles
fo
#
Figure3:ViolationsagainstNoRepetitiveUIAction.
start the app AccuWeather
click view "Open navg. drawer"
click view with text "Settings"
click view with text "F, mph, in"
click view with text "F, mph, in"
click view with text "F, mph, in"
click view with text "Manage Notif"
click view with text "Locations"
go back
click view with text "Locations"
click view with text "Edit Location"
click view with text "Locations"
click view with text "Manage Notif"
click view with text "Locations"
Figure4:ActionSelectionofDroidbot-GPTonAccuWeather.
Figure4presentsanexampleofsuchviolations.Notonlydoes
ChatGPTviolatetheinstructionofnotselectinganalreadyselected
UIelement,buttheviolationhappenscontinuouslytwotimeswhen
clickingviewwithtext“F,mph,in”,andhappenscontinuallythree
timeswhenclickingviewwithtext“Locations”.
Consequently,thepromptingstrategyofDroidbot-GPTdoes
notactuallyworkasintended,explainingthepooreffectivenessof
Droidbot-GPTonFestiVal.
Qualitativeanalysisofplanadaptation.Amongtheleading
approaches,Reflexionuniquelyincorporatesamechanismtoan-
alyzeandadaptfrompreviousfailedtrials.Thisabilitytomodify
strategiesbasedonpastfailurescontributessignificantlytoitshigh
successrate.Giventhatasinglefunctionalitycanbeimplemented
invariouswaysacrossdifferentapplications[31],thecapacityto
adjustinitialplansinresponsetonewinsightsgainedfrominterac-
tionwiththeApplicationUnderTest(AUT)isvitalforenhancing
thesuccessofautomatedfeature-basedUItesting.
However,theobservedunintendedbehaviorsinDroidbot-GPT
raisequestionsabouttheefficacyofReflexion’sreflectionmech-
anism. Unlike the straightforward quantification possible with
Droidbot-GPT’sinstructionadherence,evaluatingReflexion’sadap-
tivestrategiesrequiresamorenuancedapproach.Therefore,we
conductedamanualinspectionofasampleofReflexion’slogs.In
onenotableinstancewiththeQuizletapp,followingafailedtrial,
Reflexiongeneratedaspecificreflection:

## Page 5

Guardian:ARuntimeFrameworkforLLM-BasedUIExploration ISSTA’24,September16–20,2024,Vienna,Austria
LLM Expected Open Search Click Night Turn on AUT LLM
Sequence: Search Page Night Mode Mode Entry Night Mode 4 Execute UI Action Action Parse LLM Response
Mapper
5 Validate
UI Action
Prompts: Validator
T N O u i t g h rn h e t r o M i n n o fo d … e. R N a ig n h d t o M m o E d x e p E lo n r t a r t y ion for Heuristic b L a L s M ed -
Rule
Reflection
1 3
A Se c q tu u a e l n ce: Sea O rc p h e P n a ge Nig S h e t a M rch o de Can M no o t d F e i n E d n t N ry ight Stuc S k t f e o p r s M … any Refine Yes Send
Action Is valid? Prompts
Space ! to LLM
New Prompts:
Restore
State
No
Turn on 6 Replanner
N S d e o ig a e h r s c t n h M ’ t B w o u d t o t e r o . k n . Add action into "
Other info…
Blocked Prompt
2 Generate Prompts for !′
Actions ! Generator
Back to Add Prompts to Open Search Fall into Same
Home Page Avoid Search Button Page Again Trace Again… Figure6:WorkflowofGuardianinoneround.OnlyoneUI
actionisexecutedinStep4andvalidatedinStep5.Guardian
Figure5:Amotivatingexampleofenforcinginstructionfol-
repeatstheworkflowtillthetestobjectivereached.
lowingandplanadjustmentwithUIactionspacerefinement.
LLMblindlyandrandomlyexploresthesearchpage,stuckonthe
searchpageformanystepsleadingtoloweffectiveness.
Reflection:Inmypreviousattempts,Ifailedtorealizethatthe
Inthesubsequenttrial,withoutadvancedpromptingstrategy[52],
necessaryUIelementmaynotbeincludedinthegivenlist.This
theLLMisinstructednottoclickonsearchbuttonagain.Unfor-
ledtoarepetitiveandineffectiveapproach.NextPlan:Ishould
tunately,duetotheinstructionviolationagainstthesenegation
seekadditionalinformationoradifferentsetofUIelementsto
instructions,theLLMignoresthe“searchbuttondoesn’twork”in-
identify the night mode toggle or switch. This could involve
struction,goesintothesearchpageandgetsstuckonthesearch
checkingtheapp’ssettingsmenu,searchingforuserguidesor
pageagain,leadingtotheloweffectiveness.
tutorials,orreachingouttocustomersupportforguidance...
Inthefirst failurecase, Guardiancanidentifythe planning
DespiteReflexion’smechanismtogeneratealternativestrategies
whenthesearchtabtheLLMchosendoesnotmatchtheUIstate
followingafailedattempt,insubsequenttrialstheLLMrepeatedly
afterclickingthesearchtab,andthenrestoretheAUTtothehome
selectsthesameUIactionthatledtothepreviousfailure.This
page.Inthesecondfailurecase,Guardianrefinestheactionspace
behaviorindicatesaviolationoftheintendedreflectionprocessand
byremovingthesearchtabfromtheactionspace,ensuringthe
resultsinrepeatedunsuccessfulattemptstocompletethetask.This
LLMnottoenterthesearchpageagain.
patternhighlightsacriticalgapintheLLM’sabilitytoeffectively
adaptandlearnfrompastinteractions,underminingthepotential 3 GuardianApproach
benefitsofReflexion’sadaptiveplanningcapability.
3.1 SystemArchitectureof Guardian
Answer to RQ2: Prompting-based strategies, including both
explicitinstructionsandadaptivemechanisms,failtoconsistently Figure2presentsthesystemarchitectureofGuardian.Guardian
guideLLMstofollowtheoutlinedinstructionsoradaptations. takesatestobjective,anAUT,andanLLMasinputs.Toimprovethe
Thisinconsistencyisthekeyfactorcontributingtotheobserved effectivenessofautomatedfeature-basedUItesting,Guardiancon-
loweffectiveness.
sistsofthreemodules:DomainKnowledgeLoader,MemoryModule,
andExecutionEngine.
2.3 MotivatingExample
3.1.1 DomainKnowledgeLoader. Asshowninourpreliminary
Inthissection,weuseamotivatingexampletoillustratewhyex- study (detailed in Section 2.2), encoding domain knowledge in
istingapproachesfail,andhowthefailurecanbeovercomeby promptsmaynotworkasintended.Consequently,insteadoftun-
transforming the instructions into action space refinement and ingpromptsfordomainknowledgeincorporation,Guardianuses
replanningwithrestoration. thedomainknowledgeloadertoincorporatethedomainknowledge.
ConsiderthetaskofenablingnightmodeintheQuizletapp,as Specifically,thedomainknowledgeloadertransformsthedomain
depictedinFigure5.Initially,theLLMconceivesaplan,hypothe- knowledgeintoalgorithmsoftheactionspaceoptimizer,theval-
sizingthattheapp’ssearchfunctioncanbeusedtoenablenight idator,andtheerrorhandler.Thesealgorithmsrefinetheaction
modequickly.Actingonthisplan,theLLMselectsthesearchtab spaceoftheLLM(detailedinSection3.2.2)orchangethestateof
(theuppersequenceofUIscreensinFigure5).However,itsoon planning(detailedinSection3.2.4)toenforcetheLLM’sexploration
discoversthattheappdoesn’tsupportaquicksettingfornight toconformtothedomainknowledge,improvingtheeffectiveness
modethroughthesearchtab.Withoutareplanningstrategy,the ofLLM-basedUIexploration.Table2presentstheconcretedomain

## Page 6

ISSTA’24,September16–20,2024,Vienna,Austria DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,WeiYang,andTaoXie
Algorithm1MainAlgorithmof Guardian Table2:DomainKnowledgeBorrowedfromExistingWork.
Require: anLLM𝐿𝐿𝑀,appundertest𝐴𝑈𝑇
1:
O←𝑁𝑢𝑙𝑙 ⊲actionspace KnowledgeSource DomainKnowledge
2: B←∅ ⊲blockedactionset AutomatedUITesting
3: H ← [] ⊲explorationhistoryofUIstates
4:
whilenotachievetestobjectivedo TimeMachine[10] AvoidingExplorationLoops
5:
O←𝐴𝑈𝑇.𝑑𝑢𝑚𝑝_ℎ𝑖𝑒𝑟𝑎𝑟𝑐ℎ𝑦() Vet[67] AvoidingExplorationTarpits
6: 𝑆 ←𝐴𝑈𝑇.𝑔𝑒𝑡_𝑠𝑡𝑎𝑡𝑒() LLMAgents
7 8 : : H O′ .𝑎 ← 𝑝𝑝 [ 𝑒 ] 𝑛𝑑(O) ⊲step 1 R D e ro fl i e d x b i o o t n -G [5 P 2 T ] [70] Alte A r v n o a i t d iv in e g P A la c n ti n o i n ng R a e f p t e e t r it F i a o i n lure
9:
for𝑎∈Odo
10:
if (𝑎,𝑆)∉Bthen
11:
O′.𝑎𝑝𝑝𝑒𝑛𝑑(𝑎) ⊲step 2
12:
𝑝𝑟𝑜𝑚𝑝𝑡 ←𝑃𝑟𝑜𝑚𝑝𝑡𝐶𝑜𝑛𝑠𝑡𝑟𝑢𝑐𝑡(𝑂′,𝐻)
Prompts:
13:
𝑟𝑒𝑠𝑝𝑜𝑛𝑠𝑒 ←𝐿𝐿𝑀.𝑐𝑎𝑙𝑙(𝑝𝑟𝑜𝑚𝑝𝑡) ⊲step 3
Turn on
14:
𝑎𝑐𝑡𝑖𝑜𝑛←𝑀𝑎𝑝𝑝𝑖𝑛𝑔(𝑟𝑒𝑠𝑝𝑜𝑛𝑠𝑒,O′) N
O
i
t
g
h
h
e
t
r
M
in
o
fo
d
…
e.
15:
𝐴𝑈𝑇.𝑒𝑥𝑒𝑐𝑢𝑡𝑒(𝑎𝑐𝑡𝑖𝑜𝑛) ⊲step 4
16:
O←𝐴𝑈𝑇.𝑑𝑢𝑚𝑝_ℎ𝑖𝑒𝑎𝑟𝑎𝑟𝑐ℎ𝑦 ⊲step 5
17:
𝑅𝑒𝑓𝑙𝑒𝑐𝑡𝑃𝑟𝑜𝑚𝑝𝑡 ←(𝑝𝑟𝑜𝑚𝑝𝑡,𝑎𝑐𝑡𝑖𝑜𝑛,O)
Open Search Cannot Find
18: 𝐿𝑀𝐶ℎ𝑒𝑐𝑘 ←𝐿𝐿𝑀.𝑐𝑎𝑙𝑙(𝑅𝑒𝑓𝑙𝑒𝑐𝑡𝑃𝑟𝑜𝑚𝑝𝑡) ⊲LLM-based Search Page Night Mode Night Mode Entry
reflection,returnTrueifconsideredinvalidated
19: ifO ∈H then Swipe
20:
𝐻𝑒𝑢𝑟𝑖𝑠𝑡𝑖𝑐𝐶ℎ𝑒𝑐𝑘 ←𝑇𝑟𝑢𝑒 ⊲actionleadstoaloopor
unresponsiveUIstate.
else
21:
22:
𝐻𝑒𝑢𝑟𝑖𝑠𝑡𝑖𝑐𝐶ℎ𝑒𝑐𝑘 ←𝐹𝑎𝑙𝑠𝑒
23:
if𝐻𝑒𝑢𝑟𝑖𝑠𝑡𝑖𝑐𝐶ℎ𝑒𝑐𝑘∨𝐿𝑀𝐶ℎ𝑒𝑐𝑘then
24:
B.𝑎𝑑𝑑((𝑎𝑐𝑡𝑖𝑜𝑛,𝑆)) ⊲step 6
25:
𝐴𝑈𝑇.𝑟𝑒𝑠𝑡𝑜𝑟𝑒 ⊲step 6
R
R
e
e
m
st
o
o
v
re
e
t
S
o
e a
H
r
o
c
m
h B
e
u
P
t
a
t
g
o
e
n Acco
O
u
p
n
e
t
n
P age Ex
M
p
u
lo
lt
r
i
a
-S
ti
t
o
e
n
p
… Ni
T
g
u
h
r
t
n
M
O
o
n
d e
else
26:
27:
B.𝑎𝑑𝑑(𝑎𝑐𝑡𝑖𝑜𝑛) ⊲blockrepeatingactions Figure7:RunningExampleofGuardian.
theUIhierarchy,andthecorrespondingUItransitionafterexecut-
knowledgeborrowedfromexistingwork[10,52,67,70]andusedfor
ingtheLLM’splannedUIactionontheAUT.Theblockedaction
thecurrentimplementationofGuardian.First,TimeMachine[10]
space,i.e.,B,storestheactionsthatareblockedaccordingtothe
andVet[67]reportedthataneffectivestrategyofautomatedUItest-
domainknowledge(detailedinSections3.2.2and3.2.4).Eachitem
ingshouldavoidexplorationloopsandtarpits,whereautomated
inBisatuple(UIaction𝑥,UIstate𝑠).EachUIactionisuniquely
UItestingtoolsrepetitivelyexploreasmallfraction(oftheapp
identifiedusingitstextualattributesobtainedfromtheXMLfileof
functionality)thatisalreadyvisitedbefore.Basedontheseinsights,
theUIhierarchy,andeachUIstateisidentifiedusingtheUIlayout
werefinetheactionspacebyremovingUIactions(fromtheaction
ignoringthetextfield(usedbypreviouswork[55,67]).OnUIstate
space)thatleadtoexplorationtarpits(detailedinSection3.2.2)and
𝑠,GuardianblocksUIaction𝑥 if(𝑥,𝑠) ∈B.
replanwhenalooporanexplorationtarpitisencountered(detailed
inSection3.2.4).Second,inthedesignofLLMagents,Droidbot- 3.1.3 ExecutionEngine. Theexecutionengineproxiestheinterac-
GPT[70]proposedtoavoidselectinganalreadyselectedUIaction, tionbetweentheLLMandtheAUT.OntheLLMside,theexecution
andReflexion[52]proposedtousetheself-reflectionmechanism engineprovidestheLLMwithpromptsdescribinginstructionsand
ofLLMstore-generateplanning.Basedontheseinsights,werefine therefinedactionspace,receivestheLLM’soutput,andparsesthe
theactionspacetoavoidselectingrepeatedUIactions(detailedin LLM’soutputintoanexecutableUIaction.OntheAUTside,the
Section3.2.2)andreplanwhentheLLMdeterminesthatthecurrent executiondriverexecutesUIactionsontheAUT,dumpstheUI
planisinvalidatedbysubsequentexplorationfeedback(detailedin hierarchyfilerepresentingthescreenoftheAUT,andparsesthe
Section3.2.4). UIhierarchyfiletoobtainthecurrentactionspaceontheAUT.
3.1.2 MemoryModule. Thememorymodulestoresthehistory
3.2 Workflowof Guardian
context,blockedactionsdeterminedbythedomainknowledge,and
theLLMperceptiblecontextwhichistheworkingmemoryofthe 3.2.1 WorkflowOverview. Figure6presentsGuardian’sone-round
LLM. ThehistorycontextstoresalltheUIcontextsencountered workflowofassistingtheLLMingeneratingoneUIactionandAl-
duringtheexplorationontheAUT.EachUIcontextcontainsan gorithm1illustratesthedetailsofeachstepintheworkflow.The
Activityname,aUIhierarchy,theplannedUIactionbytheLLMon workflowisrepeateduntilthetestobjectiveisreached.

## Page 7

Guardian:ARuntimeFrameworkforLLM-BasedUIExploration ISSTA’24,September16–20,2024,Vienna,Austria
Refiningactionspace.Ineachroundduringtheautomatedfeature-
You are a UI testing expert helping me <test
basedUItesting,GuardianfirstenumeratesalistofavailableUI objective> on <app name>.
actionspresentinthecurrentAUTinterfacetoformulatetheac- You have selected <validated UI action history>.
tionspaceO(step 1).Guardianthenrefinestheactionspaceby Currently we have <Action space size> UI actions:
removingtheblockedactionsonthecurrentUIstateaccording index-0: a Button (a11y information: scroll to see
to B,yieldingarefinedactionspace O′ (step 2,elaboratedin more options) to swipe
Section3.2.2). index-1: a View (resource_id widget_form_edittext,
PromptingtheLLMwithrefinedactionspace.Withthere- text password) to text
fined action space
O′
, Guardian generates prompts and sends ...
the prompt to the LLM to obtain the LLM’s response (step 3). Your task is to select one UI action that helps
GuardianparsestheLLM’sresponseintoanexecutableUIaction, achieve the <test objective>. First, think
andexecutestheUIactionontheAUT(step 4). about which UI action satisfies our need, and
Replanningviastaterestoration.AfterexecutingtheUIaction, then select only one UI action by its
GuardianobtainstheUIstateontheAUTtovalidatewhetherthe identifier.
UIactionyieldsexpectedoutcomes(step 5).IftheUIactionisvali-
dated,Guardianentersthenextiteration.Otherwise,theUIaction Figure8:PromptDesignofUIRepresentation.
isinvalidatedandGuardiandeliberatelyreplansbyrestoringthe
AUTstateandaddingtheUIactionalongwiththecorrespondingUI GuardiansupportsfourprimarytypesofUIactions:
statetotheblockedactionsetB(step 6),detailedinSection3.2.4). • Click:clickonthecenterpointofagivenUIelement.
GuardianiteratestheworkflowshowninFigure6untilthetest • LongClick:pressonthecenterpointoftheUIelementfor
objectiveisreached. onesecond.
• Swipe:querytheLLMforthedirectionanddistanceofthe
3.2.2 RefiningtheActionSpace. Ineachiterationwithinautomated
swipe,andthenperformtheswipeoperation.
feature-basedUItesting,aUIactionischosenfromasetdenoted • Text:generateanadditionalquerytotheLLMforgenerating
asUIactionspace.ThisspaceincludesallpossibleUIactionsforthe
anappropriatestringinput,whichisthenenteredintothe
currentiteration.Asshowninourpreliminarystudy(Section2.1),
givenUIelement.
LLMsareexpertsatselectingaUIactionfromtheUIactionspace.
Consequently,GuardianconvertsUItestingspecificinstructions 3.2.4 ReplanningviaStateRestoration. Afterexecutingtheplanned
tothetasksthattheLLMisanexpertat,i.e.,selectingaUIaction UIactionontheAUT,Guardianvalidateswhethertheprevious
fromanactionspace.Inparticular,Guardianmaintainsablocked UIactionyieldsexpectedoutcomes.IftheUIactiondoesnotyield
UI action set B, and refines the action space O according to B expectedoutcomes,GuardianinvalidatestheUIactionforthe
(Lines9-11inAlgorithm1). Guardianusesthedomainknowledge giventestobjectiveandreplansaUIaction.Inspiredbythedomain
presentedinTable2tomaintainB.First,inspiredbyDroidbot- knowledgefromReflexion[52]andautomatedUItestingtools[10,
GPT[70],weblockaUIactionifithasalreadybeenchoseninthe 67](listedinTable2),GuardianemploysacombinationofLLM
sameUIstateinpreviousiterations(Line27inAlgorithm1).Second, feedbackandheuristicrulestovalidatewhethertheoutcomeofa
inspiredbyTimeMachine[10]andVet[67],weblockaUIaction UIactionisexpectedbasedonitspriorplanning.
ifitleadstoanexplorationlooporanunresponsiveUIstate(i.e.,a LLM-basedreflection(Lines16-18inAlgorithm1).Inspired
tarpit)(Lines19-22inAlgorithm1,detailedinSection3.2.4).Third, byReflexion[52],afterexecutingaUIaction,Guardianconsults
inspiredbyReflexion[52],anyUIactioninvalidatedbytheLLM’s theLLMtodeterminewhethertheresultmatchestheexpected
reflectionisalsoblocked(Lines16-18inAlgorithm1,detailedin outcome,basedontheinitialplan(includingboththepromptand
Section3.2.4).ThelowerpartofFigure7showsarunningexample theLLM’sresponse)andthepost-executionUIscreen.Aresponse
ofblockingthesearchtabwithGuardian,effectivelyaddressing of“No”fromtheLLMindicatesthattheactionisinvalidated.
thelimitationsofexistingapproachesdepictedinFigure5. Heuristicrulecheck(Lines19-22inAlgorithm1).Inspiredby
TimeMachine[10]andVet[67],Guardianevaluatestheaction’s
3.2.3 PromptandParserDesign. AfterobtainingthesafeUIaction resultsagainstknownexplorationpitfallsincludingunresponsive-
space𝑂′
,GuardianproceedstoarticulatetherefinedUIaction ness[67],repetitiveexploration[67],andexplorationloops[10].
space,thetestobjective,thecurrentplan,andthetaskinstructions AnactionisinvalidatedifiteitherfailstoaltertheUIscreenor
withinaprompt,asillustratedinFigure8. leadstoapreviouslyvisitedscreenwithinthesametrial.
GuardianalsoallocatesauniqueidentifiertoeachUIaction IfaUIactionisidentifiedasinvalidatedbyeitherLLM-based
within𝑂′
bysortingtheUIactionlistandenumeratingeachaction reflection or the heuristic rule check (Line 23 in Algorithm 1),
basedonitsindexinthelist,subsequentlyassigningtheidentifier Guardianaddsittotheblockactionset(Line24inAlgorithm1).
“index-i”tothei-thUIaction.Theseuniqueidentifiersarecrucial WhenaUIactionisinvalidated,Guardianautomaticallyrestores
forextractingtheselectedUIactionfromtheLLM’sresponsewith theUIstatetothestatebeforetheinvalidatedUIactionisexecuted
regularexpressions.ThedescriptionofeachUIactionincludesits (Line25inAlgorithm1).Actionsleadingtounresponsivenessre-
eventtype,resource-id,textualrepresentation,andaccessibility quirenofurthersteps.Foractionsresultinginareturntoaprevi-
information(asretrievedbyUIAutomator[16]),providedthese ouslyvisitedUIscreen,Guardianreplaysprecedingactionsup
attributesareavailable. tothepointjustbeforetheinvalidatedaction.Ifinvalidatedby

## Page 8

ISSTA’24,September16–20,2024,Vienna,Austria DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,WeiYang,andTaoXie
LLMfeedback,particularlyfor“click”actions,Guardiantriggersa • Droidbot-GPT[70]isanLLM-basedUInavigationapproach.
“back”actionontheAUTtoreverttothepreviousstate.Theupper TakingatestobjectiveandthecurrentUIscreenoftheAUT
partofFigure7showsarunningexampleofinvalidatingthesearch asinputs,Droidbot-GPTiterativelyselectsthemostproper
tabandrestorestheAUTtothehomepage,effectivelyaddressing UIactiontoachievethetestobjective,withexplicitdomain
thelimitationsofexistingapproachesdepictedinFigure5.Oncethe knowledgeoutlinedintheprompt.
UIstateisrestored,Guardianinitiatesthenextiteration,where
Notethatallofthestate-of-the-artapproachesusepromptengi-
theLLMispresentedwitharefinedUIactionspace(detailedin
neering[33]toinstructtheLLMtofollowtheirdesignedstrategies.
Section3.2.2),excludingthepreviouslyinvalidatedUIaction.
ForReActandReflexion,weimplementthemfortheautomated
feature-basedUItestingtaskbasedontheircodewrittenforWeb-
4 Evaluation
Shop[73],awebsimulationenvironmentresemblingmobileapps.
Toassesstheeffectivenessof Guardiananditsindividualalgo- WeusethesamepromptdesignfordescribingtheUIcontent(de-
rithms,weconductcomprehensiveevaluationstoanswerthefol- tailedinSection3)asGuardian.Amajordifferenceinourim-
lowingresearchquestions: plementationofReActandReflexionisthatwemanuallyblock
the“back”actiononthefrontpage.Otherwisethetwoapproaches
• RQ3:HoweffectiveisGuardiancomparedtostate-of-the-
willdeterministicallyfailtofinishanytaskbyrepeatedlyclicking
artapproaches?
the“back”buttononthefrontpage.ForDroidbot-GPT,weuseits
• RQ4:Howeffectiveisactionspacerefinementinimproving
publiclyavailableimplementation[69].
theeffectivenessofautomatedfeature-basedUItesting?
Wealsocomparetheeffectivenessofnon-LLM-basedapproaches
• RQ5:Howeffectiveisreplanningviarestorationinimprov-
usedbytheMoTIFdataset,includingSeq2Seq[53],MOCA[54],
ingtheeffectivenessofautomatedfeature-basedUItesting?
andSeq2Act[27].Wesimplyusethereleasedparametersofthese
• RQ6:HoweffectiveisGuardianon“unseendata”?
modelsalongwithMoTIF.
EvaluationMetrics.Weevaluatetheeffectivenessbycomparing
4.1 EvaluationSetup
theground-truthUIactionsequencewiththeUIactionsequence
Testplatform.AllexperimentsareconductedontheofficialAn- generatedbyanapproach.Weusesuccessrate(SR)andaverage
droidx64emulatorsrunningAndroid6.0onaserverwithfour completionproportion(ACP),whicharecommonlyusedforevaluat-
AMDEPYC7H1264-CoreProcessors.Eachemulatorisallocated ingtheeffectivenessofautomatedfeature-basedUItesting[5,70].
with4dedicatedCPUcores,2GBRAM,and2GBinternalstorage. Weusesubsequence[71]whencomputingtheaveragecompletion
Wemanuallywriteauto-loginscriptsforappsrequiringaloginto proportionandsuccessrateforallapproachesinthesameway.Sup-
accessthefeaturesusedintheevaluation.Eachofthesescriptsis posethattheground-truthUIactionsequenceis𝐺𝑇 = [𝑎 1 ,...,𝑎 𝑛],
executedonlyoncebeforethecorrespondingappstartstobetested andthegeneratedUIactionsequenceis𝐺𝑒𝑛 = [𝑎 1 ,...,𝑎 𝑚].We
ineachtestrun. checkwhether𝐺𝑇 isasubsequence[71]of𝐺𝑒𝑛.If𝐺𝑇 isasub-
Benchmark.WereuseanexistingbenchmarkMoTIF[5]andcol- sequenceof𝐺𝑒𝑛,thenthetaskistreatedasasuccess.Notethat
lectadditionaltasksonpopularindustrialapps[66]toconstruct thedesignchoiceofusingsubsequencedoesnotrequiretheUI
theFestiVal(FEature-baSedUItesTIngeVALuation)benchmark actiontobeadjacentinGenbutrequiresonlytheorderstobe
forthestudy.TheMoTIFdataset[5]consistsof344vision-language thesame,ignoringtheimpactofloopsandirrelevantUIactions.
navigationtaskson125mobileapps.Thevision-languagenaviga- The𝑆𝑅 = #ofsuccessfultasks measuresthepercentageofsuccess-
#ofalltasks
tiontasksaresimilartofeature-basedUItesting.Weinstallthe ful tasks. Let us denote𝐺𝑇 𝑖 = [𝑎 1 ,..,𝑎 𝑖] to be the prefix of𝐺𝑇
providedAPKsonemulatorsandexecutetheground-truthtasks with the first 𝑖 UI actions. The average completion proportion
ontheAUT.IftheAPKcanbeinstalledandtheexecutiontrace 𝐴𝐶𝑃 =max𝑛 𝑖 ∀𝑖 ∈ [1,..,𝑛]∧𝐺𝑇 𝑖 isasubsequenceof𝐺𝑒𝑛.
isthesameastheprovidedUIhierarchytraces,weaddittoFes-
tiVal. We obtain 28 tasks runnable on our test platform. Since 4.2 RQ3.Effectivenessof Guardian
thetaskcomplexitycollectedfromtheMoTIFdatasetisrelatively
Inthissection,weevaluatetheoveralleffectivenessof Guardian
low(consistingof2-4UIactionspertask),wecollect30additional
forautomatedfeature-basedUItestingandanalyzetherootcauses
tasks(consistingof4-13UIactionspertask)onpopularindustrial
leadingtofailuresinusingLLMsforautomatedfeature-basedUI
apps[48,65–67].Finally,weobtain58tasksfrom23popularmobile
testing.
appsforevaluation.
Prompting-basedLLMapproaches.Weusethefollowingthree
4.2.1 MainResults. Table3presentstheoveralleffectivenessof
state-of-the-artLLMapproachesthataredesignedfororcanbe
Guardian and prompting-based state-of-the-art approaches. It
adaptedforautomatedfeature-basedUItesting.
demonstratesthatLLM-basedapproachessignificantlyoutperform
• ReAct[75]directsLLMstoproducebothverbalreasoning theirnon-LLM-basedcounterpartsinautomatedfeature-basedUI
tracesandactionsrelatedtoagiventaskinaninterleaved testing.Itisimportanttohighlightthatthenon-LLM-basedmeth-
manner,enablingthemodeltoengageindynamicreasoning. ods,whicharetrainedontheMoTIFdataset,onlymanagetoattain
• Reflexion [52] utilizes verbal reinforcement learning to successratesinthesingledigits.Thisresultunderlinestheinher-
enableagentstolearnfrompriorfailures,mirroringtheiter- entcomplexityandchallengesposedbyautomatedfeature-based
ativelearningprocessobservedinhumanstacklingcomplex UItesting,suggestingthattraditionalapproachesmaystruggleto
tasks. effectivelynavigatethisdomain.

## Page 9

Guardian:ARuntimeFrameworkforLLM-BasedUIExploration ISSTA’24,September16–20,2024,Vienna,Austria
Table3:OverallEffectivenessofGuardian. Table5:EfficacyofActionSpaceRefinement.
Approaches SR(%) ACP(%) Approaches SR(%) ACP(%)
Non-LLM Droidbot-GPT 6.9 27.6
Refine-Droidbot 13.8(+100.0%) 32.1(+16.3%)
Seq2Seq[53] 8.8 19.8 UnRefine-Guardian 34.5(-28.5%) 51.9(-18.9%)
MOCA[54] 6.9 21.2 Guardian 48.3 64.0
Seq2Act[27] 1.9 5.4
Prompting-based
andconsequentlyfailstoselectthemtoachievethetask.Ifvision
ReAct[75] 13.8 25.5 modalityinformationcanbeintegrated,Guardiancanbeimproved.
Reflexion[52] 19.0 26.5 Second,Guardiansometimesignoresthescrollableelementson
Droidbot-GPT[70] 6.9 27.6 thecurrentUIscreenanddecidestogobacktothepreviousscreen
whenalltheelementsonthecurrentUIareunrelatedtothefeature.
Runtime-system-guarded
Guardiancanbenefitfromabetterdescriptionofthesemanticsof
Guardian(Ours) 48.3(+154%) 64.0(+132%) scrollableUIelements.Third,Guardiancannotdecidewhichof
theUIelementsisthemostrelatedtothegoalwhenseveralsimilar
Table4:CauseAnalysisofGuardian’sFailures. UIelementdescriptionsappear.Forexample,in𝑇 8,whentryingto
switchthetranslationlanguage,twoelementsonthescreenare
Cause #ofFailedCases relatedtothefeaturetextually.However,oneelementisforswitch-
VisionModalityInput 17(56.7%) ingthetwolanguagesfortranslation,whichisonlyweaklyrelated
Screen-levelUnderstanding 8(26.7%) tothetargetedfeature.Althoughtheelementhasa“swap”inits
Element-levelUnderstanding 5(16.7%) name,Guardianstilltendstomistakeitforthecorrectelement.
Thesecasescanbeinherentlydifficulttosolvesincehandlingthem
Notably,Reflexionstandsoutwiththehighestsuccessrateamong requiresmoreadvancedLLMsforteststepgrounding.However,
allthepreviousapproaches,achieving19.0%,whileDroidbot-GPT thesepotentialimprovementdirectionsinvolveusingadvanced
leadsintermsofaveragecompletionproportion,reaching27.6%. multi-modalmodels(fortakingvisualinputsandbetterUIcontent
Reflexionachievesthehighestsuccessrate,particularlynoteworthy comprehension)anddesigningbetterpromptingstrategies,which
asitsignificantlysurpassesReAct,despitebothemployingalmost areorthogonaltothedesignandpurposeof Guardian.
identicalpromptingstrategies.ThekeydifferentiatorisReflexion’s Answer to RQ3: Guardian substantially outperforms
additionalreflectionmechanismthatisexpectedtoadjusttheplan- prompting-basedSOTAapproacheswith154%successrateand
ningbasedonpreviousfailedtrials.Thisphenomenondemonstrates 132%averagecompletionproportionrelativeimprovement.
thenecessityofadaptingplanningstrategiesbasedongradually
enrichedinformationobtainedduringtheexplorationoftheAUT. 4.3 RQ4.EffectivenessofActionSpace
Given its deliberate and reliable replanning achieved by the Refinement
runtimesysteminsteadofexpectingthepromptstoworkforthe
LLM,Guardianachieves48.3%successrate,outperformingthe Inthissection,weevaluatetheeffectivenessaswellasthegeneral-
beststate-of-the-artapproachReflexion[52]with154%relativeim- izabilityofrefiningactionspacetoensuretheinstructionfollowing.
provement,Asfortheaveragecompletionproportion,Guardian WecompareGuardianandDroidbot-GPT,examiningtheirper-
achieves64.0%,outperformingthebeststate-of-the-artapproach formance both with and without action space refinement. The
Droidbot-GPT[70]with132%relativeimprovement.Giventhesafe comparisoninvolvesthefollowingbaselines:
UIactionspaceconstructionalgorithm,Guardianreliablyavoids • Refine-DroidbotaugmentsDroidbot-GPT[70]byincor-
selectingrepeatedUIactions,andsubstantiallyreducesthe44% poratingthesafeUIactionspacetopreventtheselectionof
repeatedUIactionsbyDroidbot-GPT(asshowninthepreliminary UIactionsalreadychoseninprevioustrials.
study).Thesubstantialimprovementdemonstratestheeffectiveness • UnRefine-Guardian operates without the safe UI ac-
of Guardian,theruntime-systemapproachtoreliablyimproving tionspace,maintainingallotherconfigurationsidenticalto
LLM-basedautomatedfeature-basedUItestinginsteadofexten- Guardian.
sivelyoptimizingthepromptdesign.
Table5presentstheexperimentalresultsontheablationstudy
4.2.2 InvestigationofFailureCasesofGuardian. Toinvestigate ontheeffectivenessofactionspacerefinementtoensureinstruction
therootcausesoffailuresof Guardian,wemanuallyinspectthe following.bothDroidbot-GPTandGuardiansubstantiallybene-
30failedtasks.Table4presentstheanalysisofrootcausesoffailed fitsfromactionspacerefinement.Specifically,Refine-Droidbot
tasks,categorizedintothreetypes.First,amongtheinvestigated demonstratesaremarkableimprovement,outperformingDroidbot-
cases,themostcommonreasonthatGuardiancannotgenerate GPTwitha100.0%increaseinsuccessrateanda16.3%increasein
thedesiredtestisthattheUIhierarchyinformationisnotenough averagecompletionproportion.Notably,Refine-Droidbotdou-
toperformthetask.Whengeneratingspecificteststepssuchas blesthesuccessrateofDroidbot-GPT,underscoringthepromising
clickingonaniconorimagebuttonwithoutaccessibilityinforma- generalizabilityofthisapproach.Conversely,theremovalofac-
tion,GuardiancannotunderstandtheintentoftheseUIelements tionspacerefinementinUnRefine-Guardianleadstoamarked

## Page 10

ISSTA’24,September16–20,2024,Vienna,Austria DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,WeiYang,andTaoXie
Table6:EfficacyofAdjustingPlanning. Table7:EffectivenessonUnseenData.
Approaches SR(%) ACP(%) Approaches SR(%) ACP(%)
StaticRe-Plan ReAct 0 9.6
C To o T T [ [ 7 6 4 8 ] ] 17.2(+ 1 9 .7 11.8%) 35.0( 1 + 1 2 . 1 1 6.2%) Dr R oi e d fl b e o x t i - o G n PT 1 8 6 .3 .7 2 2 1 8 . . 8 3
Guardian 58.3(+249.1%) 66.9(+136.4%)
DynamicRe-Plan
Droidbot-GPT 6.9 27.6 4.5 RQ6:EffectivenessonUnseenData
Replan-Droidbot 19.0(+175.4%) 34.5(+25.0%)
Guardian-NoReplan 32.8(-32.1%) 48.5(-24.2%) Guardian’sutilityisdemonstratedthroughitsabilitytoconsis-
Guardian 48.3 64.0 tentlyboosttheLLM’sperformancebeyonditsinitialconfiguration
regardlessofdatacontamination,whichisevidentinourresults
whereGuardian+LLMconsistentlyoutperformstheoriginalLLM.
decreaseinperformanceforGuardian,with28.5%reductionin
Unseen-datacollection.Forfurthervalidation,weconductaddi-
successrateand18.9%reductioninaveragecompletionproportion.
tionalexperimentstoinvestigatetheeffectivenessofGuardianon
AnswertoRQ4: Refiningactionspacesignificantlyenhances
unseendata.Werecruittwoparticipants,undergraduatestudents
instruction following, markedly boosting the effectiveness of
majoringincomputersciencefromauniversityclassinsoftware
Guardian.Thisstrategyalsoprovesbeneficialinaugmenting
engineering.Wefirsttrainthetwoparticipantsfortwohoursabout
theexistingLLM-basedapproaches.
automated feature-based UI testing and the task format of Fes-
tiVal.Wehavetwoconstraintsonthesetasks.First,performing
4.4 RQ5:EffectivenessofReplanning
thetasksrequiresloginwithnon-trivialauthenticationsuchas
Inthissection,westudytheeffectivenessofreplanningviarestora- fillingemailedverificationcode.Second,thetasksshouldcome
tion,especiallywithenrichedinformationobtainedfromexploring frompopularindustrialapps,improvingtherepresentativenessof
theAUT.Tocomprehensivelyinvestigatethisresearchquestion, theevaluation.Wegivetheparticipantsthefreedomtopickany
wecompareGuardianwiththefollowingbaselines: popularindustrialappsavailableonGooglePlay,andwriteany
tasksfortheseapps.Intheend,weobtain12taskswrittenbythese
• Guardian-NoReplanomitstheplanningadjustmental-
twoparticipants.The12taskscomefrom5highlypopularapps,
gorithm,maintainingallotherconfigurationsidenticalto
andtheaveragelengthofthese12tasksis4.2.
Guardian. Resultanalysis.Table7presentstheeffectivenessof Guardian
• Replan-DroidbotenhancesDroidbot-GPTbyincorpo-
andbaselineapproachesonunseendata.Onthe12tasks,Guardian
ratingthereplanningviarestoration.
achieves58.3%successrate,outperformingthebeststate-of-the-
• ChainofThought(CoT)[68]staticallybuildsoneUIaction
artapproachReflexionwith249.1%relativeimprovement.Asfor
sequencetoachievethetestobjectivebeforeexploringthe
averagecompletionproportion,Guardianachieves66.9%aver-
AUT.CoTexplorestheAUTtofindUIactionsthatismost
agecompletionproportion,outperformingthebeststate-of-the-art
similarwithUIactionsinthedreamedsequence.
approachReflexionwith136.4%relativeimprovement.Guardian
• TreeofThought(ToT)[74]improvesoverCoTbystatically
achievesabetterimprovementoftheLLM’seffectivenessinthe
conceivingfiveUIactionsequences,increasingthediversity
additionalexperimentsthantheevaluationresultsonFestiVal.
ofpathstothetestobjective.
Theseresultsfurthervalidatetheeffectivenessof Guardianin
NotethatbothCoTandToTdonotcreatenewplanningwiththe improvingtheLLM’sperformance.Wemanuallyinspecttofigure
graduallyenrichedinformationontheAUT.Instead,bothofthem outlikelyrootcausesofthefailedcasesandthesuspectedroot
imaginepossibleUIactionsequencesofthegiventestobjective. causesarelistedwithTable4.Specifically,failingtoincorporate
Table6presentstheexperimentalresultsfromwhichwehave visioninformationremainstheprimarylikelycauseforthefailed
threefindings.First,Replanning-equippedapproachesgenerally casesof Guardian,andthesefailedcasescanbeaddressedwith
outperformno-replanningapproaches.ToTsignificantlysurpasses multi-modalmodels[41]andareleftasfuturework.
CoT,validatingthehypothesisthatevendiversifyingtheinitial
5 Discussions
planningcanincreaseeffectiveness.Similarly,withouttheplan-
ningadjustmentalgorithm,Guardian’seffectivenesssubstantially
Inthissection,wediscussthelimitationsofthecurrentGuardian’s
drops.Second,dynamicreplanningworksbetterthanstaticreplan-
implementationandthefutureworktoimproveGuardian.
ning.WhileToTsubstantiallyoutperformsCoT,itisfarfromattain- LimitedevaluationofLLMs.Currently,weimplementandeval-
ingsimilareffectivenessasapproacheswithdynamicadjustment.
uate Guardian with only one LLM namely GPT-3.5. While in-
Third,Replanninggenerallyimproveseffectivenessacrossdiffer-
structionviolationsofLLMsarefoundtobeaprevalentissue[56],
entapproaches.TheimprovedperformanceofReplan-Droidbot
especiallyinlong-contextscenarios[32,59],whetherinstruction
overDroidbot-GPT,anditssuperioritytoReflexion[52],implying
violationsareprevalentinautomatedfeature-basedUItestingre-
thatevenexistingLLM-basedapproachesbenefitfromdynamic
mainsasopenproblem.Nevertheless,sinceGuardiandoesnot
replanning.
relyonLLM-specificdesignsforthedomainknowledge,weexpect
AnswertoRQ5: Replanningwithrestorationsubstantiallyim- thatGuardiancanbeusedforimprovingabroaderscopeofLLMs,
provestheeffectivenessofautomatedfeature-basedUItesting. leftasourfuturework.

## Page 11

Guardian:ARuntimeFrameworkforLLM-BasedUIExploration ISSTA’24,September16–20,2024,Vienna,Austria
Costsofincorporatingdomainknowledge.Currently,weman- SequentialplanningwithLLMs.LLM-basedsequentialplan-
ually implement the domain knowledge within the Guardian ning[7,18,42,57,63,75]isanemergingfield,havingwideap-
framework.Toincorporatemoredomainknowledgeandimprove plicationssuchasrobotics[2,39],videogames[35],andvirtual
the usability of Guardian, automating the process of turning reality[58].IthasbeendemonstratedthatLLMsarepowerfulfor
domain-knowledgedescriptionintoexecutableprogramswithin planningproblems[18,57,63,75].ReAct[75]interleavesreasoning
theGuardianframeworkisneededandisapromisingdirection andactingtoenhancetheLLMplanning.Reflexion[52]deliber-
leftforfuturework. atelyreflectsonitspreviousfailedtrials.MemGPT[42]usesvirtual
Assumptionsoninputmodality.Currently,Guardianisinstan- memorytoaddressthelongcontextissue.
tiatedwithChatGPT,whichonlyacceptstextualinputs.Mobile Largelanguagemodelsforsoftwaretesting. Largelanguage
appscontainrichvisualinformationusefulforautomatedfeature- models[4]havegainedsignificantattentionandpopularityinvar-
based UI testing. How to incorporate the visual information of ious areas [24, 60] including software engineering [12, 21] and
mobileappscanbeaninterestingyetchallengingdirection,specifi- testing[64].MostexistingworkinsoftwaretestingusingLLMs
callyhowtodefinevisual-specificinstructions,whichweplanto focuses on embedding domain knowledge in prompts to adapt
exploreinourfuturework. LLMs for specific tasks. Liu et al.[34] employ LLMs for textual
AssumptionsonTestObjectives.Intheevaluation,weassume inputgenerationbytransformingthetaskintoablank-fillingprob-
eachtaskhasauniquegroundtruthUIactionsequence.However, lem.TitanFuzz[8]promptsLLMstogeneratevalidAPIsequences
inpractice,thesametestobjectiveonthesameappcanhavemore andparameterstofuzzdeep-learninglibraries.ADBGPT[13]uses
thanonepathstoaccess(denotedasalternativepaths[31]).We promptengineeringtoadaptLLMsforreproducingAndroidbug
make our best effort by adding constraints in test objectives to reports,differentfromtheexploratorynatureofautomatedfeature-
makethepathstobeunique.However,itcanbeinterestingand based UI testing. Our work in this paper focuses on improving
challengingtogenerateallpossiblepathstoachievethesametest theeffectivenessofLLMswitharuntime-systemapproach.Com-
objective,leftasourfuturework. plementingtheexistingwork,Guardianisaruntimeframework
externaltoanLLMandflexiblyincorporatesdomainknowledge,
providingastartingpointtouseexternalsystemstoassistanLLM
6 ThreatstoValidity
withsoftwareengineeringtasks.
Themainexternalthreattothevalidityconcernstherepresentative-
nessofthesubjectappsandapproachesselectedforourevaluation. 8 Conclusion
Tomitigatetheimpactofthebiasintroducedbyappselection,we
Feature-basedUItestinghasbeenextensivelyadoptedinindus-
usehighlypopularindustrialappswidelyusedbyrelatedwork
trial practices, but automated feature-based UI testing remains
tomaketheconstructedbenchmarkmorepracticalcomparedto
anopenchallenge.Despitethesuccessandtrendofusinglarge
onlyusingthetasksfromMoTIF.Tomitigatetheimpactofthe
languagemodels(LLMs)forresemblingplanningproblems,we
biasintroducedbybaselineselection,wechoosestate-of-the-art
havefoundtwomajorchallengesofexistingprompting-basedap-
approaches.
proaches:LLMs’lowabilitytofollowtask-specificinstructions,and
Thethreatstointernalvalidityareinstrumentationeffectsthat
toreplanbasedonenrichedinformation.
can bias our results, including faults in our implementation of
Toaddresstheprecedingchallenges,inthispaper,wehavepro-
Guardianandparameterselectionof Guardian.Faultsinourim-
posedGuardian,aruntimeframeworkwithtwokeydesigns.First,
plementationofGuardianmayaffecttheeffectivenessofGuardian.
Guardianrefinestheactionspacewithdomain-specificknowl-
To reduce these threats, all authors carefully test and validate
edgetoensureinstructionfollowing.Second,Guardianreplansvia
GuardianontheQuizletapptoassurethebehaviorof Guardian
restorationtopromptlyadjusttheexplorationontheAUT.Wehave
isasexpected,andwesetthetemperatureofLLMbackbonetoa
constructedabenchmarknamedFestiValcontaining58unique
lowleveltoreducetherandomnessofLLMs.
tasks.EvaluationresultsonFestiValhaveshownthatGuardian
canachieve48.3%successrateand64.0%completionrate,outper-
7 RelatedWork formingstate-of-the-artapproacheswith154%and132%relative
improvementwithrespecttothetwometrics,respectively.Fur-
AutomatedUItesting.AutomatedUItestinghasbeenahotre-
therexperimentshaveconfirmedtheeffectivenessofindividual
searchtopic[1,3,6,10,15,17,19,28,36–38,43,49,55,72,76]aswell
algorithmdesignswithinGuardian.
asanindustrypractice[38,47,77],fallingintofourmaincategories:
(1)Sometoolsgeneratetestinputsrandomlyand/orapplyevolution-
Acknowledgments
aryalgorithmsuponthesetestinputs[10,15,36,38,76].(2)Some
othertoolsconductsystematicexploration[1,3,37].(3)Model- TaoXieisthecorrespondingauthor.Thisworkwaspartiallysup-
basedtoolsandtheirvariantsuseaUItransitionmodeltodetermine portedbyNSFCunderGrantNo.62161146003,GrantNo.623B2006,
thecurrenttestprogressandtargetnot-yet-exploredfunctionali- GrantNo.2021YFF1201103,NSFgrantCCF-2146443,andtheTen-
ties[6,17,19,28,55].(4)Machine-learning-basedtools[25,29,43, centFoundation/XPLORERPRIZE.
48,49]adoptdeeplearningorreinforcementlearningtechniques
toguidetheexplorationoftheAUT.Wegaindomainknowledge References
fromexistingautomatedUItestingtools[10,67]forimplementing
[1] SaswatAnand,MayurNaik,MaryJeanHarrold,andHongseokYang.2012.Au-
Guardian. tomatedconcolictestingofsmartphoneApps.InFSE.

## Page 12

ISSTA’24,September16–20,2024,Vienna,Austria DezhiRan,HaoWang,ZiheSong,MengzhouWu,YuanCao,YingZhang,WeiYang,andTaoXie
[2] PeterAnderson,QiWu,DamienTeney,JakeBruce,MarkJohnson,NikoSün- [29] YuanchunLi,ZiyueYang,YaoGuo,andXiangqunChen.2019. Humanoid:A
derhauf,IanReid,StephenGould,andAntonvandenHengel.2018.Vision-and- deeplearning-basedapproachtoautomatedblack-boxAndroidapptesting.In
languagenavigation:Interpretingvisually-groundednavigationinstructionsin ASE.
realenvironments.InCVPR. [30] Jun-WeiLin,NavidSalehnamadi,andSamMalek.2020. Testautomationin
[3] TanzirulAzimandIulianNeamtiu.2013.Targetedanddepth-firstexploration open-sourceandroidapps:Alarge-scaleempiricalstudy.InASE.1078–1089.
forsystematictestingofAndroidApps.InOOPSLA. [31] Jun-WeiLin,NavidSalehnamadi,andSamMalek.2022.Route:Roadsnottaken
[4] TomBrown,BenjaminMann,NickRyder,MelanieSubbiah,JaredDKaplan, inuitesting.TOSEM(2022).
PrafullaDhariwal,ArvindNeelakantan,PranavShyam,GirishSastry,Amanda [32] NelsonFLiu,KevinLin,JohnHewitt,AshwinParanjape,MicheleBevilacqua,
Askell,etal.2020. Languagemodelsarefew-shotlearners. NIPS33(2020), FabioPetroni,andPercyLiang.2024.Lostinthemiddle:Howlanguagemodels
1877–1901. uselongcontexts.TACL12(2024),157–173.
[5] AndreaBurns,DenizArsan,SanjnaAgrawal,RanjithaKumar,KateSaenko,and [33] PengfeiLiu,WeizheYuan,JinlanFu,ZhengbaoJiang,HiroakiHayashi,andGra-
BryanAPlummer.2022.Adatasetforinteractivevision-languagenavigation hamNeubig.2021.Pre-train,prompt,andpredict:Asystematicsurveyofprompt-
withunknowncommandfeasibility.InECCV.Springer,312–328. ingmethodsinnaturallanguageprocessing. arXivpreprintarXiv:2107.13586
[6] WontaeChoi,GeorgeNecula,andKoushikSen.2013. GuidedGUItestingof (2021).
Androidappswithminimalrestartandapproximatelearning.InOOPSLA. [34] ZheLiu,ChunyangChen,JunjieWang,XingChe,YuekaiHuang,JunHu,and
[7] AbhishekDas,SamyakDatta,GeorgiaGkioxari,StefanLee,DeviParikh,and QingWang.2022.FillintheBlank:Context-awareautomatedtextinputgenera-
DhruvBatra.2018.Embodiedquestionanswering.InCVPR.1–10. tionformobileGUItesting.arXivpreprintarXiv:2212.04732(2022).
[8] YinlinDeng,ChunqiuStevenXia,HaoranPeng,ChenyuanYang,andLingming [35] CoreyLynchandPierreSermanet.2021.Languageconditionedimitationlearning
Zhang.2023.Largelanguagemodelsarezero-shotfuzzers:Fuzzingdeep-learning overunstructureddata.Robotics:ScienceandSystems(2021). https://arxiv.org/
librariesvialargelanguagemodels. arXiv:2212.14834[cs.SE] abs/2005.07648
[9] HoangTDinh,ChonhoLee,DusitNiyato,andPingWang.2013. Asurveyof [36] AravindMachiry,RohanTahiliani,andMayurNaik.2013.Dynodroid:Aninput
mobilecloudcomputing:architecture,applications,andapproaches. Wireless generationsystemforAndroidApps.InESEC/FSE.
communicationsandmobilecomputing13,18(2013),1587–1611. [37] RiyadhMahmood,NarimanMirzaei,andSamMalek.2014.EvoDroid:Segmented
[10] ZhenDong,MarcelBöhme,LuciaCojocaru,andAbhikRoychoudhury.2020. evolutionarytestingofAndroidApps.InFSE.
Time-traveltestingofAndroidApps.InICSE. [38] KeMao,MarkHarman,andYueJia.2016.Sapienz:Multi-objectiveautomated
[11] NouhaDziri,XimingLu,MelanieSclar,XiangLorraineLi,LiweiJiang,BillYuchen testingforAndroidapplications.InISSTA.
Lin,SeanWelleck,PeterWest,ChandraBhagavatula,RonanLeBras,etal.2024. [39] DipendraMisra,AndrewBennett,ValtsBlukis,EyvindNiklasson,MaxShatkhin,
Faithandfate:Limitsoftransformersoncompositionality.NIPS(2024). andYoavArtzi.2018.Mappinginstructionstoactionsin3Denvironmentswith
[12] AngelaFan,BelizGokkaya,MarkHarman,MityaLyubarskiy,ShubhoSengupta, visualgoalprediction.InEMNLP.AssociationforComputationalLinguistics,
ShinYoo,andJieMZhang.2023.Largelanguagemodelsforsoftwareengineering: Brussels,Belgium,2667–2678. https://doi.org/10.18653/v1/D18-1287
Surveyandopenproblems.arXivpreprintarXiv:2310.03533(2023). [40] OpenAI.2024.IntroducingtoChatGPT. https://openai.com/blog/chatgpt
[13] SidongFengandChunyangChen.2024.Promptingisallyouneed:Automated [41] OpenAI.2024.LearnhowtouseGPT-4tounderstandimages. https://platform.
Androidbugreplaywithlargelanguagemodels.InICSE.1–13. openai.com/docs/guides/vision
[14] DiFeiGao,LeiJi,LuoweiZhou,KevinQinghongLin,JoyaChen,ZihanFan,and [42] CharlesPacker,VivianFang,ShishirGPatil,KevinLin,SarahWooders,and
MikeZhengShou.2023.AssistGPT:Ageneralmulti-modalassistantthatcan JosephEGonzalez.2023.MemGPT:TowardsLLMsasoperatingsystems.arXiv
plan,execute,inspect,andlearn.(2023). preprintarXiv:2310.08560(2023).
[15] Google.2021. AndroidMonkey. https://developer.android.com/studio/test/ [43] MinxuePan,AnHuang,GuoxinWang,TianZhang,andXuandongLi.2020.
monkey Reinforcementlearningbasedcuriosity-driventestingofAndroidapplications.
[16] Google.2023.UIAutomator. https://developer.android.com/training/testing/ InISSTA.
uiautomator [44] BinghuiPeng,SriniNarayanan,andChristosPapadimitriou.2024.Onlimitations
[17] TianxiaoGu,ChengnianSun,XiaoxingMa,ChunCao,ChangXu,YuanYao, ofthetransformerarchitecture.arXivpreprintarXiv:2402.08164(2024).
QirunZhang,JianLu,andZhendongSu.2019.PracticalGUItestingofAndroid [45] DezhiRan.2024.PubliclyavailableimplementationofGuardian. https://github.
applicationsviamodelabstractionandrefinement.InICSE. com/PKU-ASE-RISE/Guardian
[18] TanmayGuptaandAniruddhaKembhavi.2023.Visualprogramming:Composi- [46] D.Ran,Y.Fu,Y.He,T.Chen,X.Tang,andT.Xie.2024. PathTowardElderly
tionalvisualreasoningwithouttraining.InCVPR. FriendlyMobileApps. Computer57,06(jun2024),29–39. https://doi.org/10.
[19] ShuaiHao,BinLiu,SumanNath,WilliamGJHalfond,andRameshGovindan. 1109/MC.2023.3322855
2014.PUMA:ProgrammableUI-automationforlarge-scaledynamicanalysisof [47] DezhiRan,ZongyangLi,ChenxuLiu,WenyuWang,WeizhiMeng,XionglinWu,
mobileApps.InMobiSys. HuiJin,JingCui,XingTang,andTaoXie.2022. Automatedvisualtestingfor
[20] QianyuHe,JieZeng,WenhaoHuang,LinaChen,JinXiao,QianxiHe,Xunzhe mobileappsinanindustrialsetting.InICSE-SEIP.
Zhou,JiaqingLiang,andYanghuaXiao.2024. CanLargeLanguageModels [48] DezhiRan,HaoWang,WenyuWang,andTaoXie.2023.Badge:PrioritizingUI
UnderstandReal-WorldComplexInstructions?.InAAAI. eventswithhierarchicalmulti-armedbanditsforautomatedUITesting.InICSE.
[21] XinyiHou,YanjieZhao,YueLiu,ZhouYang,KailongWang,LiLi,XiapuLuo, [49] AndreaRomdhana,AlessioMerlo,MarianoCeccato,andPaoloTonella.2022.
DavidLo,JohnGrundy,andHaoyuWang.2023. Largelanguagemodelsfor Deepreinforcementlearningforblack-boxtestingofAndroidapps. TOSEM
softwareengineering:Asystematicliteraturereview. arXiv:2308.10620[cs.SE] (2022).
[22] YuxinJiang,YufeiWang,XingshanZeng,WanjunZhong,LiangyouLi,FeiMi, [50] GreggRothermel,MaryJeanHarrold,JefferyVonRonne,andChristieHong.
LifengShang,XinJiang,QunLiu,andWeiWang.2023.Followbench:Amulti- 2002.Empiricalstudiesoftest-suitereduction.STVR(2002).
levelfine-grainedconstraintsfollowingbenchmarkforlargelanguagemodels. [51] MahadevSatyanarayanan,ParamvirBahl,RamónCaceres,andNigelDavies.
arXivpreprintarXiv:2310.20410(2023). 2009. ThecaseforVM-basedcloudletsinmobilecomputing. IEEEpervasive
[23] AdamTaumanKalaiandSantoshSVempala.2024.Calibratedlanguagemodels Computing(2009).
musthallucinate.InSTOC. [52] NoahShinn,FedericoCassano,EdwardBerman,AshwinGopinath,Karthik
[24] EnkelejdaKasneci,KathrinSessler,StefanKüchemann,MariaBannert,Daryna Narasimhan,andShunyuYao.2023. Reflexion:Languageagentswithverbal
Dementieva,FrankFischer,UrsGasser,GeorgGroh,StephanGünnemann,Eyke reinforcementlearning. arXiv:2303.11366[cs.AI]
Hüllermeier,StephanKrusche,GittaKutyniok,TilmanMichaeli,ClaudiaNerdel, [53] MohitShridhar,JesseThomason,DanielGordon,YonatanBisk,WinsonHan,
JürgenPfeffer,OleksandraPoquet,MichaelSailer,AlbrechtSchmidt,TinaSeidel, RoozbehMottaghi,LukeZettlemoyer,andDieterFox.2020.Alfred:Abenchmark
MatthiasStadler,JochenWeller,JochenKuhn,andGjergjiKasneci.2023.ChatGPT forinterpretinggroundedinstructionsforeverydaytasks.InCVPR.10740–10749.
forgood?Onopportunitiesandchallengesoflargelanguagemodelsforeducation. [54] KunalPratapSingh,SuvaanshBhambri,ByeonghwiKim,RoozbehMottaghi,
LearningandIndividualDifferences(2023). andJonghyunChoi.2021. Factorizingperceptionandpolicyforinteractive
[25] YavuzKoroglu,AlperSen,OzlemMuslu,YunusMete,CeydaUlker,TolgaTan- instructionfollowing.InICCV.1888–1897.
riverdi,andYunusDonmez.2018.QBE:QLearning-basedexplorationofAndroid [55] TingSu,GuozhuMeng,YutingChen,KeWu,WeimingYang,YaoYao,Geguang
applications.InICST. Pu,YangLiu,andZhendongSu.2017.Guided,stochasticmodel-basedGUItesting
[26] Tianle Li, Ge Zhang, Quy Duc Do, Xiang Yue, and Wenhu Chen. 2024. ofAndroidApps.InESEC/FSE.
Long-context llms struggle with long in-context learning. arXiv preprint [56] JiaoSun,YufeiTian,WangchunshuZhou,NanXu,QianHu,RahulGupta,
arXiv:2404.02060(2024). JohnFrederickWieting,NanyunPeng,andXuezheMa.2023.Evaluatinglarge
[27] YangLi,JiacongHe,XinZhou,YuanZhang,andJasonBaldridge.2020.Mapping languagemodelsoncontrolledgenerationtasks.arXivpreprintarXiv:2310.14542
naturallanguageinstructionstomobileUIactionsequences.InACL.Association (2023).
forComputationalLinguistics,Online. [57] DídacSurís,SachitMenon,andCarlVondrick.2023.Vipergpt:Visualinference
[28] YuanchunLi,ZiyueYang,YaoGuo,andXiangqunChen.2017. DroidBot:A viapythonexecutionforreasoning.arXivpreprintarXiv:2303.08128(2023).
lightweightUI-guidedtestinputgeneratorforAndroid.InICSE-C.

## Page 13

Guardian:ARuntimeFrameworkforLLM-BasedUIExploration ISSTA’24,September16–20,2024,Vienna,Austria
[58] FuwenTan,SongFeng,andVicenteOrdonez.2019. Text2Scene:Generating [68] JasonWei,XuezhiWang,DaleSchuurmans,MaartenBosma,EdChi,QuocLe,
compositionalscenesfromtextualdescriptions.InCVPR. andDennyZhou.2022.Chainofthoughtpromptingelicitsreasoninginlarge
[59] YiTay,MostafaDehghani,SamiraAbnar,YikangShen,DaraBahri,PhilipPham, languagemodels.arXivpreprintarXiv:2201.11903(2022).
JinfengRao,LiuYang,SebastianRuder,andDonaldMetzler.2020.Longrange [69] HaoWen,HongmingWang,JiaxuanLiu,andYuanchunLi.2023.Droidbot-GPT.
arena:Abenchmarkforefficienttransformers.arXivpreprintarXiv:2011.04006 https://github.com/GAIR-team/DroidBot-GPT
(2020). [70] HaoWen,HongmingWang,JiaxuanLiu,andYuanchunLi.2023.DroidBot-GPT:
[60] ArunJamesThirunavukarasu,DarrenShuJengTing,KabilanElangovan,Laura GPT-poweredUIautomationforAndroid.arXivpreprintarXiv:2304.07061(2023).
Gutierrez,TingFangTan,andDanielShuWeiTing.2023.Largelanguagemodels [71] Wikipedia.2024.Subsequence. https://en.wikipedia.org/wiki/Subsequence
inmedicine.NatureMedicine(2023). [72] WeiYang,MukulR.Prasad,andTaoXie.2013.Agrey-boxapproachforautomated
[61] SureshThummalapenta,SaurabhSinha,NimitSinghania,andSatishChandra. GUI-modelgenerationofmobileapplications.InFASE.
2012.Automatingtestautomation.InICSE.881–891. [73] ShunyuYao,HowardChen,JohnYang,andKarthikNarasimhan.2022.Webshop:
[62] MarkosViggiato,DalePaas,ChrisBuzon,andCor-PaulBezemer.2022.Using Towardsscalablereal-worldwebinteractionwithgroundedlanguageagents.
naturallanguageprocessingtechniquestoimprovemanualtestcasedescriptions. NIPS35(2022),20744–20757.
InICSE-SEIP.311–320. [74] ShunyuYao,DianYu,JeffreyZhao,IzhakShafran,ThomasLGriffiths,YuanCao,
[63] BryanWang,GangLi,andYangLi.2023.Enablingconversationalinteraction andKarthikNarasimhan.2023. Treeofthoughts:Deliberateproblemsolving
withmobileuiusinglargelanguagemodels.InCHI. withlargelanguagemodels.arXivpreprintarXiv:2305.10601(2023).
[64] JunjieWang,YuchaoHuang,ChunyangChen,ZheLiu,SongWang,andQing [75] ShunyuYao,JeffreyZhao,DianYu,NanDu,IzhakShafran,KarthikNarasimhan,
Wang.2023.Softwaretestingwithlargelanguagemodel:Survey,landscape,and andYuanCao.2022.React:Synergizingreasoningandactinginlanguagemodels.
vision. arXiv:2307.07221[cs.SE] arXivpreprintarXiv:2210.03629(2022).
[65] WenyuWang,WingLam,andTaoXie.2021. Aninfrastructureapproachto [76] HuiYe,ShaoyinCheng,LanboZhang,andFanJiang.2013.DroidFuzzer:Fuzzing
improvingeffectivenessofAndroidUItestingtools.InISSTA. theAndroidAppswithintent-filtertag.InMoMM.
[66] WenyuWang,DengfengLi,WeiYang,YuruiCao,ZhenwenZhang,Yuetang [77] HaibingZheng,DengfengLi,BeihaiLiang,XiaZeng,WujieZheng,Yuetang
Deng,andTaoXie.2018.AnempiricalstudyofAndroidtestgenerationtoolsin Deng,WingLam,WeiYang,andTaoXie.2017.Automatedtestinputgeneration
industrialcases.InASE. forAndroid:Towardsgettingthereinanindustrialcase.InICSE-SEIP.
[67] WenyuWang,WeiYang,TianyinXu,andTaoXie.2021. Vet:identifyingand
avoidingUIexplorationtarpits.InESEC/FSE. Received2024-04-12;accepted2024-07-03

