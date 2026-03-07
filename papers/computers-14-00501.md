# Computers-14-00501

**Source:** computers-14-00501.pdf  
**Converted:** 2026-01-26 09:22:44

---

## Page 1

Article
AutoQALLMs: Automating Web Application Testing Using
Large Language Models (LLMs) and Selenium
SindhupriyaMallipeddi1,MuhammadYaqoob1 ,JavedAliKhan1,* ,TahirMehmood2 ,AlexiosMylonas1
andNikolaosPitropakis3
1 CybersecurityandComputingSystemsResearchGroup,DepartmentofComputerScience,Universityof
Hertfordshire,HatfieldAL109AB,UK;sm23ahb@herts.ac.uk(S.M.);m.yaqoob3@herts.ac.uk(M.Y.)
2 SchoolofInformationTechnology,UNITARInternationalUniversity,PetalingJaya47301,Selangor,Malaysia
3 DepartmentofInformationTechnology,CybersecurityandComputerScience,TheAmericanCollegeof
Greece,15342Athens,Greece;npitropakis@acg.edu
* Correspondence:j.a.khan@herts.ac.uk
Abstract
Modernwebapplicationschangefrequentlyinresponsetouserandmarketneeds,making
theirtestingchallenging. Manualtestingandautomationmethodsoftenstruggletokeep
up with these changes. We propose an automated testing framework, AutoQALLMs,
thatutilisesvariousLLMs(LargeLanguageModels),includingGPT-4,Claude,andGrok,
alongsideSeleniumWebDriver,BeautifulSoup,andregularexpressions. Thisframework
enablesone-clicktesting,whereusersprovideaURLasinputandreceivetestresultsas
output,thuseliminatingtheneedforhumanintervention. ItextractsHTML(Hypertext
Markup Language) elements from the webpage and utilises the LLMs API to generate
Selenium-basedtestscripts. Regularexpressionsenhancetheclarityandmaintainability
ofthesescripts. Thescriptsareexecutedautomatically,andtheresults,suchaspass/fail
statusanderrordetails,aredisplayedtothetester. Thisstreamlinedinput–outputprocess
formsthecorefoundationoftheAutoQALLMsframework. Weevaluatedtheframework
on 30 websites. The results show that the system drastically reduces the time needed
to create test cases, achieves broad test coverage (96%) with Claude 4.5 LLM, which
is competitive with manual scripts (98%), and allows for rapid regeneration of tests in
AcademicEditor:WenbingZhao
responsetochangesinwebpagestructure. Softwaretestingexpertfeedbackconfirmedthat
Received:12October2025
theproposedAutoQALLMsmethodforautomatedwebapplicationtestingenablesfaster
Revised:10November2025
regressiontesting,reducesmanualeffort,andmaintainsreliabletestexecution. However,
Accepted:14November2025
some limitations remain in handling complex page changes and validation. Although
Published:18November2025
Claude 4.5 achieved slightly higher test coverage in the comparative evaluation of the
Citation: Mallipeddi,S.;Yaqoob,M.;
proposed experiment, GPT-4 was selected as the default model for AutoQALLMs due
Khan,J.A.;Mehmood,T.;Mylonas,A.;
Pitropakis,N.AutoQALLMs: toitscost-efficiency,reproducibility,andstablescriptgenerationacrossdiversewebsites.
AutomatingWebApplicationTesting Futureimprovementsmayfocusonincreasingaccuracy,addingself-healingtechniques,
UsingLargeLanguageModels(LLMs) andexpandingtomorecomplextestingscenarios.
andSelenium.Computers2025,14,501.
https://doi.org/10.3390/
Keywords: testing;webapplication;LLM;GPT;selenium
computers14110501
Copyright:©2025bytheauthors.
LicenseeMDPI,Basel,Switzerland.
Thisarticleisanopenaccessarticle 1. Introduction
distributedunderthetermsand
Software testing plays a pivotal role in evaluating the quality and correctness of
conditionsoftheCreativeCommons
Attribution(CCBY)license softwaresystemsthroughoutthedevelopmentlifecycle[1]. Itensuresthatapplications
(https://creativecommons.org/ functionasintendedandmeetuserexpectations. Softwaretestingcanconsumeover50%
licenses/by/4.0/).
Computers2025,14,501 https://doi.org/10.3390/computers14110501

## Page 2

Computers2025,14,501 2of26
of total development costs, especially in complex modern applications [1]. Web appli-
cationsareparticularlychallengingtotestduetotheirdynamiccontent, asynchronous
interactions,andfrequentinterfacechanges,asetofproblemswellestablishedinthefield’s
literature[2–4]. Asthesesystemsevolverapidlytomeetchanginguserdemands,testing
methodologies must also adapt to maintain reliability and efficiency [3,5]. Inadequate
softwaretestingcanleadtocriticalsystemfailuresandwidespreadvulnerabilities,empha-
sisingtheneedforreliable,automatedsolutions[6,7]. Thesecaseshighlighttheneedfor
moreeffectivetestingmethodsthatcanbeappliedinreal-worldsystemswithlimitedtime
andresources.
Modernwebapplicationsarecharacterisedbycomplexstructures,dynamiccontent,
andasynchronousinteractions[8]. Thesefeaturespresentsignificanttestingchallenges
thathavebeenreportedintheliterature[2,9]. Thiscomplexitymakesitchallengingtotest
effectivelyusingtraditionalmanualmethods[8]. Whenrelyingonmanualtesting,develop-
ersandQAengineersmustspendadditionaltimeandeffortontestdesignandexecution,
thereby increasing the organisation’s overall testing costs [10]. This makes traditional
manualtestingslowanddifficult. Automatedtesting[11],codelesstesting[12],andmodel-
based testing using machine learning have been proposed to improve this process[3].
However,thesemethodshavecertainlimitations,includingdifficultiesintrainingmodels
onlargedatasetsandconcernsregardingthequalityoftheresultingproduct.
LLMshavebeenwidelyusedinthesoftwaredevelopmentlifecycle[6],includingcode
generation[13],requirementsengineering[14],vulnerabilitydetection[15],andtestcase
creation[10,16,17]. Recently,theuseofLLMsinsoftwaretestinghasbecomeasignificant
andrapidlyexpandingfieldofresearch,withtheliteraturemappingthecurrentlandscape
of tools and techniques [18]. Tools such as GPTDroid and PENTESTGPT demonstrate
thatLLMscanperformautomatedtestingwithminimalhumanassistance[19,20]. This
demonstratesthatLLMscanbeintegratedintoautomatedandcontext-sensitivetesting
systemsforimprovedqualitywithreducedresourcesandlowercosts. However,todate,
accordingtoourknowledge,thereislittleworkthatusesLLMsincompletetestingpipelines
forwebapplications. AfewstudieshaveutilisedLLMsinconjunctionwithwebscraping
orregularexpressions;however,theseapproachesdonotencompassfullautomationor
scriptrefinement[16]. Thereexistsaresearchgapconcerningautomatedsystemscapable
ofdynamicallyadaptingtochangesinpagestructurewhilepreservingscriptreadability.
ThisstudyintroducesatestautomationframeworkcalledAutoQALLMsthatutilises
GPT-4alongsideSeleniumWebDriver,BeautifulSoup,andregularexpressions. Thepro-
posed approach reads the HTML of any webpage, finds the elements, and uses GPT-4,
Claude4.5andGroktogenerateSeleniumscripts. Regularexpressionsareusedtorefine
and adapt the scripts even when the webpage structure changes. Unlike conventional
methodsthatrelyonstaticscriptsandrequireupdatesforeveryUIchange,thisapproach
dynamicallyadaptstothestructureofwebpagesusingDOM(DocumentObjectModel)
parsing and pattern-based matching, reducing manual effort and improving resilience
to UI changes [3,4]. Unlike GPTDroid, which is designed for mobile testing [20], Auto-
QALLMsaretailoredforwebapplicationtesting. WhileGPTDroidfocusesonextracting
UI trees and generating scripts for native mobile apps, AutoQALLMs target dynamic
webpages by parsing the DOM using BeautifulSoup and refining scripts with regular
expressions. Additionally,AutoQALLMssupportzero-shotprompt-basedtestgeneration
(enabling HTML-to-Selenium translation without prior examples or fine-tuning) using
GPT-4, Claud 4.5, and Grok, eliminating the need for intermediate instrumentation or
mobile-specifictools. Toourknowledge,thisisthefirststudytointegrateLLMswithDOM
parsingandregex-basedscriptenhancement,creatingafullyautomated,browser-oriented
testingframework.

## Page 3

Computers2025,14,501 3of26
With the proposed approach, we aim to answer three research questions: (i) How
canLLMsbecombinedwithwebscrapingandSeleniumtocreatetestscripts? (ii)Can
LLMs turn HTML into working Selenium scripts using zero-shot prompts? (iii) Can
AutoQALLMsoutperformmanualorsemi-automatedtestingincodecoverageandfault
detection? OurresultsdemonstratethatLLMscanbeadaptedtoconvertHTMLintovalid
Seleniumscriptswithoutrequiringhuman-writtencode. TheproposedAutoQALLMsare
testedacrossvariouswebsites,andexpertfeedbackindicatesthattheyimprovecoverage,
faultdetection,andthetimerequiredtogeneratescriptscomparedtotraditionalmethods.
OurkeycontributionisthedevelopmentofaframeworkthatextractsHTMLfroma
webpageandparsestheDOMusingBeautifulSoup. Wecomposestructuredpromptsto
directLLMs(GPT-4,Claude4.5,andGrok)ingeneratingSelenium-basedtestscripts. Addi-
tionally,wehaveimplementedaregex-drivenrefinementmodulethatenhancestherobust-
nessofthesescriptsbyidentifyingelementpatterns,therebyimprovingtheiradaptability
tochangesintheuserinterface(UI).Anothercontributionistheintegrationofthesecom-
ponentsintoadynamictestautomationflowthatsupportszero-shottestcasegenerationto
eliminatetheneedformanuallywrittentemplatesorpriortraining. Wealsoconductedex-
tensiveevaluationsacross30websitestomeasureAutoQALLMs’performanceintermsof
coverage,executiontime,andfaultdetection. Furthermore,wegatheredandincorporated
expertfeedbackfromsoftwaretesterstovalidatethesystem’spracticalityandtounder-
standitsstrengthsandlimitationsinreal-worldtestingenvironments.AutoQALLMs’code
ismadeavailableforfuturework(https://github.com/Sindhupriya2797/AutoQALLMs).
We developed AutoQALLMs, a fully automated framework that transforms web
content into executable Selenium test scripts using LLM intelligence. We designed the
frameworktoperformzero-shottestgenerationbyextractingHTMLfromanygivenweb-
page,parsingitsDOMstructurewithBeautifulSoup,andconstructingstructuredprompts
thatguideLLMtoproducecontext-awareSeleniumscripts. Wefurtherimplementeda
regex-drivenrefinementmodulethatidentifiesandoptimiseselementpatternstoimprove
thesyntacticvalidityandadaptabilityofscriptswhentheuserinterfaceorDOMchanges.
Throughthisdesign,weintegratedparsing,generation,andrefinementintoasinglework-
flowthatsupportsend-to-end,self-adjustingautomationfromHTMLextractiontotest
executionandreporting.
Wealsodevisedanevaluationframeworktovalidatethescalabilityandpracticalityof
AutoQALLMs. Wetestedtheframeworkacross30diversewebapplicationsandmeasured
performanceusingquantitativemetricssuchascoverage,generationtime,executionspeed,
andfaultdetection. Wefurthercollectedexpertfeedbackfromprofessionaltesterstoassess
qualitativeattributes,includingreadability,adaptability,maintainability,andscalability.
OurresultsshowthatAutoQALLMsgenerateaccurateSeleniumscriptswithinseconds,
achieve coverage levels close to manual testing, and significantly reduce human effort.
Withthesecontributions,wepresentapracticalandintelligentapproachtoAI-assisted
webtestingthatadvancestheroleofLLMsinautomatedqualityassurance.
Theremainderofthispaperisorganisedasfollows: Section2presentsrelatedwork
insoftwaretesting,includingmanual,ML-based,andLLM-basedapproaches. Section3
describesthearchitectureandmethodologyoftheAutoQALLMsframework. Section4
outlines the experimental setup, evaluation metrics, and testing procedures. Section 5
presentstheresults,expertfeedback,andcomparativeanalysis. Finally,Section6concludes
thestudyanddiscusseslimitationsaswellaspotentialdirectionsforfutureresearch.

## Page 4

Computers2025,14,501 4of26
2. RelatedWork
2.1. ManualTesting
Manual testing involvestesters actingas endusers, manually executingtest cases,
andusingallavailableprogramfeaturestoidentifyproblemsandensurethesoftwaremeets
standards[6,7].Thisprocessisoftenthefirststepforanynewapplicationbeforeautomation
isconsidered,asithelpsdeterminewhetherautomatedtestingisworthwhile[7]. Testers
manuallyfollowtestplans,executetestcases,andcaptureevidence,suchasscreenshots,
comparing actual results with expected results to detect discrepancies and unexpected
behaviour[21,22].
Althoughmanualtestingiseffectiveinuncoveringdetailedissues,suchasinvalidin-
putvaluesorunexpecteduserinterfacebehaviours,itistime-consuming,tedious,andcan
beerror-prone, especiallyforcomplexapplicationswithmanytestcases[8,22]. Theex-
tensiveeffortandcostrequiredformanualtesting,particularlyinlarge-scaleregression
scenariosorsystems,hasledtoagrowingdemandforautomatedtestingsolutions[10,23].
However,automatedtestingdoesnotfullyreplacemanualmethods,ashumaninvolve-
mentremainsnecessaryforevaluationofcertaintestingtasks,especiallythosethatinvolve
nuancedordynamicuserinteractions[23]. Theselimitshaveledtothesearchformore
rapidandautomatedmethodsthatrequirelesshumanwork.
2.2. MLandDLBasedTesting
Manual testing is time-consuming and repetitive, and earlier automated systems
couldnotlearnoradapttonewelements[4]. Someapproachesutilisedsupportvector
machine(SVM)modelswithSeleniumandBeautifulSouptopredicttestcasesbasedon
HTMLelementpatterns;however,theywerelimitedtostaticcontentandrequiredmanual
setup [4]. A mapping study showed that most ML-based testing research focused on
testcasegenerationandbugprediction,withfewerstudiesonGUIandsecuritytesting
andlimitedindustrialvalidation[1]. OtherworksappliedMLfortestsuiterefinement,
faultlocalisation,risk-basedtesting,andtestoracleautomation,thoughmanyrequired
domain-specificdataandexpertinput[5].
Indevelopingtheirframework,ref.[4]consideredaMultinomialNaiveBayesclassifier
followedbySVMasthebestmodelforassigningtestcases.Clusteringtechniqueshavebeen
usedtogrouptestcaseswithsimilarbehaviours,helpingrefinetestsuitesbyidentifying
redundanttests[1]. Forexample,rule-basedMLsystems,suchasRUBAR,wereapplied
forfaultlocalisation. Atthesametime,separaterisk-basedmodelsusedfaultprediction
datatoprioritisetestingandreduceexecutioncosts[5]. Thesestudiesdemonstratehow
classical ML models improve accuracy, reduce manual effort, and support intelligent
decision-makinginthesoftwaretestinglifecycle.
Although deep learning models have improved visual testing and automated UI
testcasegeneration,theyoftenrequirelargelabelleddatasetsandstrugglewithvisually
complexorchanginginterfaces[24]. Otherapproachesutiliseddeeparchitectures,suchas
LSTM,CNN,anddeepbeliefnetworks,fortestgenerationandbugprediction. However,
thesemethodsfacedsignificanthurdles. Aprimaryissuewastheneedformassive,high-
qualitydatasetsfortraining,whichwereoftenunavailable[25]. Thesedifficultieslimited
the practical application of many early deep learning techniques in real-world CI/CD
pipelines[25]. Earlierdeepneuralnetworktestingmethods,likeDeepXplore,focusedon
neuroncoverageandsuccessfullyuncoveredcorner-casebugs. Still,theywerelimitedto
gradient-basedtransformationsandlackedflexibilityforbroaderautomationscenarios[26].
Duetotheselimitations,MLandDLmodelswereunabletogeneratecompleteSelenium
scriptsoradapttonewtasksusingnaturallanguage. TheprimaryadvantageofLLMs
overearliermodelsistheirabilitytoperformcomplexgenerationtasks,suchasgenerating

## Page 5

Computers2025,14,501 5of26
codefromnatural-languageprompts,withoutrequiringextensive,task-specifictraining
datasets. Toaddressthisgap,webeganexploringtheuseofLLMsbyprovidingprompts
togenerateSeleniumcode,therebyenablingmoreflexibleandend-to-endtestautomation.
2.3. LLM-BasedTesting
LLMsforsoftwaretestingareabroadandactiveresearcharea,withrecentliterature
providingacomprehensivelandscapeofthevarioustasks,models,andpromptingtech-
niquescurrentlybeingexplored[18]. Intothisbroaderlandscape,webapplicationtesting
hasbeenspecificallyidentifiedasapromisingfuturedirection[9]. Followingthistrend,
LLMshaverecentlybeenappliedtodifferentareasofsoftwaretestingtoreducemanualef-
fortandsupportadaptivetestgeneration. GPT-4wasintegratedwithSeleniumWebDriver
in a feedback loop to parse the DOM, generate interaction steps, and adjust test flows
basedonupdatedpagestructure,allowingfullydynamicGUItestingwithoutpre-recorded
data[27]. Anotherapproachcomparedmanualscripting,GitHubCopilot,andtwoChat-
GPTvariantsforgeneratingwebE2EtestscriptsusingGherkininputs. Thestudyfound
thatChatGPTMax(multi-turn)withGPT-4versionconsistentlyreduceddevelopmenttime
andrequiredfewermanualcorrections[16].
ForJavaScriptunittestgeneration,thepapertoolTESTPILOTwasevaluatedacross
25npmpackages. WhiletheLLM-generatedtestsproducednatural-lookingcodewith
meaningful assertions, they also achieved significantly higher code coverage than the
state-of-the-arttraditionaltool[17]. System-leveltestcasegenerationwasexploredthrough
US2Test,aPython-basedtoolthatcombinedGPT-4withuserstoriesfromRedmine.Thetool
employedblack-boxtechniques,includingequivalenceclassandboundaryvalueanalysis,
anddemonstrateda60%reductionindesigneffortinagovernmentsetting[28].
LLMs were also used for visual testing, where a framework generated assertions
andbugreportsbyanalysingUIscreenshotsandhistoricalbugdata. ThisenabledA/B
comparisonsandvisualregressiontesting,thoughitlackedlogicalDOMinteractions[22].
Beyondtestgeneration,LLMsarealsobeingappliedtothecriticalproblemoftestmainte-
nanceandrobustness. Akeychallengeis“locatorfragility”,wheretestsbreakbecauseUI
elementschangebetweensoftwareversions. TheVONSimiloLLMframeworkaddresses
thisbyusinganLLMtosemanticallycompareandselectthemostlikelycorrectelement
fromalistofcandidates,significantlyreducinglocalisationfailures[29].
Anotherstudyproposedamodularframework,T5-GPT,whichcombinedCrawljax,
aT5classifier,adatafaker,andGPT-4otoautomatewebforminteractionandvalidation.
Themodelimprovedformcoveragebuthaddifficultyhandlingcomplexinputsandlong
executiontimes[8]. Amulti-agentLLMframeworkwasintroducedforgeneratingtest
cases,executingthem,visualisingcallgraphs,andcreatingPDFreportsusingtoolssuchas
GeminiandAudioWebClient. Althoughitachievedhightestcoverage,itwaslimitedto
backendlogicandunit-leveltesting[23]. MobileGUItestingwasreframedasaquestion-
answeringtaskusingGPTDroid,whichappliedmemory-awarepromptsandGUIcontext
extractiontosimulateuseractions. Themodelimprovedcoverageandbugdetectionbut
struggledwithappsrequiringgesturesorbackendvalidation[20]. Incybersecuritytesting,
PENTESTGPTutilisedLLMsforinteractivepenetrationtesting,featuringseparatemodules
for reasoning, command generation, and output parsing. It achieved strong results in
OWASPbenchmarksandCTFtasks,althoughitrequiredhuman-in-the-loopsupportand
prompttuning[19].
These studies show that LLMs have expanded the scope of automated testing by
supportingvisualtesting,system-levelplanning,andcodegeneration. However,many
tools are limited to specific domains, lack complete test automation pipelines, or still
rely on manual oversight. To better handle the challenges of dynamic navigation and

## Page 6

Computers2025,14,501 6of26
complexinteractions,otherresearchhasfocusedoncreatingintermediaterepresentations
of web applications to guide LLMs. For instance, ref. [30] introduced a system that
buildsscreentransitiongraphstomodelsitenavigationandstategraphsforconditional
forms, using these structures to generate more robust test cases. The choice of model
and prompt structure is also crucial, as demonstrated by large-scale empirical studies.
Lietal. [31]conductedastudycomparing11LLMsforwebformtesting,concludingthat
GPT-4significantlyoutperformedothermodelsandthatprovidingacleanlyparsedHTML
structureinthepromptwasmoreeffectivethanusingrawHTML.Amorerecentparadigm
leverages Large Vision-Language Models (LVLMs), which analyse not just the HTML
codebutalsovisualscreenshotsofthewebpage. Forexample,ref.[32]proposedVETL,
atechniquethatusesanLVLM’ssceneunderstandingcapabilitiestogeneraterelevanttext
inputsandidentifythecorrectGUIelementstointeractwith,evenwhenHTMLattributes
areunclear. Incontrast,weproposedanAutoQALLMsapproachthatutilisesLLMsina
structuredmanner,experimentingwithvariousLLMs,includingGPT-4,Claude,andGrok,
withDOMparsing,prompting,andSeleniumtogeneratereliableandreusabletestscripts
formodern,dynamicwebapplications. Table1comparestheexistingtoolsandmethods
withtheapproachproposedinthisstudy.
Table1.MethodologicalComparisonofTestAutomationApproaches.
Methodological
Reference Approach Technique KeyFindings
Comparison
Combineswebscraping,ML
automaticallygenerateand
ML-drivenweb BeautifulSoup+ classification,andtest
[4] classifytestcasesusingML
UItesting ML+Selenium execution;lacksadaptability
modelsforeachwebelement.
toliveDOMchanges.
Codelessarchitectureto UsesSVMfortestprediction;
Codelessweb predictandautomate limitedreal-time
[3] Selenium+SVM
testingusingML functionaltestingusing responsivenessandDOM
trainingdata. parsing.
Noimplementation;
Multivocal Reviewed55LLM-powered
AItoolsurvey literaturesynthesisoftools
[33] Literature testtools,highlightinggaps
andtaxonomy highlightsneedfor
Review infull-pipelineautomation.
integratedAIpipelines.
Adaptivechatbottesting
UsesAIforconversational
Chatbottesting ML/NLP-based throughAI,butwithlimited
[34] flowadaptation;lacksfull
automation adaptation scalabilityandneedfor
webexecutionsupport.
refinement.
Generatestestsviafew-shot
Unittest Generatedunittestswith
GPT-3.5 prompting;limitedtounit
[17] generationusing highcoveragewithout
(TESTPILOT) testingwithnoweb
LLM fine-tuning.
interaction.
IntegratesLLMwith
SimulatedGUItestingusing
GUIwebtesting GPT-4+ SeleniumforGUInavigation;
[27] LLMs,partialautomation,
usingGPT-4 Selenium lacksself-healingand
butrequiredvalidation.
optimisation.
ChatGPT+ AcceleratedE2Escript Mapsuserstoriestoscripts
E2ESelenium
[16] Copilot+ writing,butrequiredmanual viaNLP;manualrefinement
testusingLLMs
Selenium refinement. isneededpost-generation.
UsesLLMandmemory
AndroidGUI Outperformedbaselinesin
GPT-4+memory promptcycles;excelsin
[20] testingusing activitycoverage,limitedto
prompting mobileappsbutisnot
LLM Android.
generalisedfortheweb.
Visualvalidationusing
Enhancedvisualvalidation,
VisualUIA/B LLM+visualdiff screenshots;lacksDOM
[32] butlackedHTMLscript
testingwithLLM validation parsingandtestflow
generation.
generation.
Template-drivenautomation Template-basedautomation
Framework- Selenium+
frameworkwithlimited requiresmanualdefinition
[11] basedwebtest DBUnit+Razor
adaptabilitytodynamicweb andlacksLLM-driven
automation templates
content. adaptability.

## Page 7

Computers2025,14,501 7of26
Table1.Cont.
Methodological
Reference Approach Technique KeyFindings
Comparison
Manualtestdesignfromuser
Real-worldpublicsector storiesusingGPT-4;unlike
LLM-based GPT-4+US2Test
testingtoolachieved100% AutoQALLMs,noDOM
[28] systemtest +Black-box
suitecoverageandsaved60% parsingorscriptexecution.
generation techniques
manualeffort. Focusesongeneratingtest
casesformanualvalidation.
UsesT5forfieldclassification
T5classifier+ ProposedT5-GPTmodel andGPT-4forvalidation;
Automatedform
GPT-4o+ improvingcoverageand unlikeAutoQALLMs,it
[8] testingusing
Crawljax+ forminteractionover doesn’tgenerateSelenium
LLMs
Mocker RL-basedsystems. scripts,focusingon
form-fillingautomation.
3. Methodology
The proposed AutoQALLMs automate the web application testing in four stages:
(i)HTMLExtraction,(ii)LLMs-basedtestscriptgeneration,(iii)Regex-basedscriptclean-
ingandoptimisation,and(iv)testexecutionandreporting. Thesestagesformamodular
andscalableframeworkthatautomaticallygeneratesSeleniumscriptsfromwebcontent.
ThearchitecturalchoicetouseapowerfulLLMlikeGPT-4,Claude,andGrokinconjunction
withstructuredparsingofHTMLissupportedbyrecentempiricalstudies,whichhave
foundthiscombinationtobehighlyeffectivefortestgenerationcomparedtootherLLMs
andlessstructuredinputs[31]. Thisapproachimprovesthespeedandaccuracyofweb
applicationtesting. Eachstageoperatesasanindependentunitwithdefinedinputsand
outputs,enablingiterativedevelopmentandpracticaldeployment. Below,theproposed
methodologyiselaboratedwithvariousfunctionsdevelopedforGPT-4.Moreover,thecom-
pleteimplementationofvariousLLMs,includingGPT-4,Claude,andGrok,isavailable
onGitHub(https://github.com/Sindhupriya2797/AutoQALLMs).
3.1. Step1: HTMLExtraction
TheproposedAutoQALLMsapproachextractsHTMLwhentheuser(softwaretester)
enterstheURLofthewebapplicationtobetested,asshowninFigure1. ThisURLprovides
therawHTMLcontentneededforLLM-basedtesting. Thesystemcallsthefetch_html(url)
function,whichusestherequestslibrarytosendanHTTPGETrequest. Thecommand
response=requests.get(url)fetchesthewebpagecontentandresponse.raise_for_status()
handlesHTTPerrorssuchas404or500toensurereliabilityduringdatacollection.
AfterretrievingtheHTML,thecontentisparsedusingBeautifulSoupwithBeauti-
fulSoup(response.text,’html.parser’). ThisconvertstheunstructuredHTMLintoawell-
organisedDOMtree. TheDOMenablesstructuredaccesstowebpageelements,suchas
buttons,links,andformfields. Thisrepresentationisessentialforthenextstage,where
theLLMsgeneratetestcasesbasedonacontextualunderstandingoftheUI.Afterparsing,
the AutoQALLMs extract content using the parse_html (soup) function. This function
isolatesapredefinedsetofHTMLtagsrelevantforwebUItesting. Itspecificallytargets:
(a) The<title>tagprovidesthetitleofthewebpagetoverifythatthecorrectpagehas
beenloadedandisdisplayedasexpectedinthebrowser.
(b) Anchor(<a>)tagswithvalid href attributes.Thesecontainhyperlinksfornavigation.
(c) Header tags from <h1> to <h6>, which capture the semantic layout and hierar-
chy of the content. These are useful for validating content structure and screen
readeraccessibility.
(d) Image(<img>)tagsthatincludesrcattributes,representingembeddedmediathat
shouldbeloadedandvisible.

## Page 8

Computers2025,14,501 8of26
(e) Form(<form>)forverifyingformsubmissionstructure(attributessuchasaction,
method,andname)
(f) Input (<input>) for capturing interactive input fields with attributes (type, id,
name,placeholder).
(g) Button(<button>)forclickableelementsthattriggeractionsorsubmissions.
(h) Select(<select>)forvalidatingdropdownoptionsanduserselections.
Figure1.AutoQALLMsWebTestingframework:LLM-GeneratedTestCaseExtraction,Processing,
andExecutionwithBeautifulSoup,Regex,andSelenium.
Thissubsetwasselectedasitrepresentsboththefundamentalandinteractiveelements
requiredtoverifyawebpage’sstructureandbehaviour.Itincludestagsforverifyingapage’s
identity(<title>),navigationalintegrity(<a>),contenthierarchy(<h1>–<h6>),andmedia
rendering(<img>),aswellasinteractivecomponentssuchasforms(<form>),inputfields
(<input>),buttons(<button>),anddropdowns(<select>).Together,theseelementscapturethe
corestaticanddynamicaspectsofmodernwebinterfaces,enablingcomprehensivevalidation
ofuserinteractionssuchasdataentry,submission,andoptionselection.
These extracted elements are assembled into a Python dictionary using key-value
mappings,whereeachcategoryisstoredasalistofvalues. Arepresentativesampleoutput
wouldresemblethefollowing:
{
"title": "Example Web Page",
"links":"[
"https://example.com/about",
"https://example.com/contact"
],
"headings":"{
"h1":"["Welcome"]"
"h2":"["About Us"]
},
"images":"[
"/images/banner.png"

## Page 9

Computers2025,14,501 9of26
" ],
"forms":"[
{
"action":"/submit-form",
"method": "post",
"id": "contactForm",
"name": "contact_form"
}
],
"inputs": [
{
"type": "text",
"name": "username",
"id": "userField",
"placeholder": "Enter your name"
},
{
"type": "email",
"name": "email",
"id": "emailField",
"placeholder": "Enter your email"
}
],
"buttons": [
{
"text": "Submit",
"type": "submit",
"id": "submitBtn",
"name": "submit_button"
}
],
"selects": [
{
"name": "country",
"id": "countrySelect",
"options": ["India", "United Kingdom", "United States"]
}
]
}
Theparsedoutputislightweightandsemanticallyrich,capturingkeyaspectsofthe
page’suserinterfacewhileremainingeasytointerpret. Itservesasthedirectinputforthe
nextstage,whereLLMpromptsareconstructedandtestscriptsaregeneratedusingthe
GPT-4,Claude,andGrokAPIs(ApplicationProgrammingInterface). Toensurethereliable
executionoftheHTMLextractionphase,exceptionhandlingisimplemented.Ifthenetwork
requestfails,theURLisinvalid,ortheresponsecannotbeparsed,thesystemcatchesthe
error,logsaclearmessage,andstopsfurtherprocessing. Thispreventsincompleteorfaulty
HTMLdatafromaffectinglaterstages,helpingtomaintaintheaccuracyandconsistency
oftheoveralltestautomationworkflow. Step1involvesacquiringthewebpagecontent
via HTTP requests and then using BeautifulSoup to parse its structure, identifying key
elements. Thisstepisfundamentalforsettinguptheautomatedgenerationoftestcases.

## Page 10

Computers2025,14,501 10of26
3.2. Step2: TestScriptGeneration
After the HTML is parsed and key elements are extracted, the framework enters
itssecondphase,whichservesastheintelligencelayer,whereweutilisevariousLLMs
(GPT-4,Claude,andGrok)togenerateautomationscriptsbasedonapredefinedprompt,
requiringminimalmanualeffort. Thestructureddatafromthefirstphaseispassedtothe
generate_selenium_code()function. ThisfunctionmergestheparsedHTMLcontentwith
aprompttogenerateexecutableSeleniumcode. Theprompthastwoprimarypurposes:
(1)todescribethewebcontentclearlytoLLMsand(2)toguideLLMsinproducingtest
logicthatfollowsstandardautomationpractices. Thepromptusedinthisframeworkis
depictedinBoxfollows:
PrompttogenerateSeleniumcodeusingextractedHTML
prompt = (
f"-You are a **strict code generator**. Your output must
contain ONLY executable Python code,"
f"-with no explanations, comments, or~markdown fences.\n\n"
f"-Generate Selenium Python test code for the following
parsed HTML data.\n\n"
f"-URL: {url}\n\n"
f"-Parsed Data:\n{json.dumps(parsed_data, indent=2)
[:2000]}...\n\n"
f"-Instructions:\n"
f"-Add test for javascript based webelements also"
f"-Automate each test case using Selenium 4+ syntax.\n"
f"-**Use only ’find_element(By.<LOCATOR>, value)’ and
’find_elements(By.<LOCATOR>, value)’** — never use
deprecated ’find_element_by_*’ or ’find_elements_by_*’
methods.\n"
f"-Import ’By’ from ’selenium.webdriver.common.by’ at the
top of the code.\n"
f"- Open the page using ChromeDriver (not headless) and
maximise the window.\n"
f"- Add time.sleep() where ever needed"
f"- Create 30 sequential test cases that interact with the
elements (titles, headings, images, links, forms, inputs,
buttons, and selects).\n"
f"- Each test should include realistic user actions
(typing, clicking, submitting, selecting options) with
time.sleep() between actions.\n"
f"- Log each test as ’Test X Passed/Failed’ directly in
the console.\n"
f"- Include ’driver.quit()’ at the end of the script.\n"
f"- Do NOT include markdown ("‘) or any descriptive text
before or after the code.\n"
f"- The entire output must be syntactically valid Python —
ready to run as-is.\n"
)

## Page 11

Computers2025,14,501 11of26
Inresponse,LLMsgenerateastructuredPythonscriptusingSeleniumWebDriverfor
browserautomation,thefind_element()methodforDOMinteraction,andtry-exceptblocks
forerrorhandling. ThescriptbeginswithWebDriversetup,runsthroughtheteststeps,
andendswithdriver.quit()forcleanup(refertothevideointheGitHublink). Thisformat
alignswithstandardpracticesinUItesting. TheLLMsoutputoftenincludesextras,such
asmarkdownformatting(e.g.,“‘python),phraseslike“HereistheSeleniumcode,”and
explanatorycomments. Whilehelpfulforhumanreaders,theseelementsareunnecessary
forautomatedexecution. Toaddressthis,apost-processingstepisincludedtocleanand
optimisethescriptbeforerunningit,Step3oftheproposedAutoQALLMsapproach,as
showninFigure1. Byembeddingbestpracticesandtestlogicwithinanintelligentagent,
thisstepreducesmanualeffortandensuresconsistency,scalability,andquickeradaptation
toUIchanges. ItdemonstrateshowLLM-drivendevelopmentcanbeintegratedintoreal
worldtestautomation.
3.3. Step3: ScriptCleaningandOptimisation
AfterLLMsgeneratestheSeleniumtestscript,theframeworkmovestoitsthirdstage,
whichpreparestherawoutputforexecutionbycleaningthescriptusingautomatedtext
processingtools,asshowninFigure1. Thegoalistoconvertthesemi-structuredandoften
verboseoutputintoacleanPythonfilethatfollowssyntaxrulesandsoftwareengineering
bestpractices. AlthoughLLMsproducelogicalandwell-structuredcode,theyfrequently
includeadditionaltextintendedforhumanreaders. Examplesincludemarkdownmarkers
like“‘python,phrasessuchas“HereistheSeleniumcode,”andplaceholderslike“Please
replace this section...”. These elements are not suitable for automated execution and
mustberemoved. Tohandlethis,theframeworkusestheclean_selenium_code()function,
whichappliesasetofregularexpressionstoremoveunnecessarycontent. Thisisatypical
application, as regular expressions are a powerful and widely used technique for text
parsingandvalidation. Althoughtheycanbedifficultfordeveloperstoreadandmaintain,
theirutilityinprogrammatictextprocessingiswell-established[35]. Table2liststhetypes
ofcontentremovedduringthisstepandexplainswhyeachisexcluded:
Table2.PatternsremovedfromLLMsoutputandtheirjustifications.
PatternRemoved Reason
ArtefactsofLLMoutputformatting,not
Markdowncodefences(python, “‘)
requiredforscriptexecution.
LLMexplanatorynotes(e.g.,“Hereisthe Non-executableandverboseexplanations
code...”) notrelevanttoautomatedtesting.
Instructionalresiduesmeantforhuman
Promptfeedback(e.g.,“Pleasereplace...”)
readers,notpartofexecutablecode.
addclutterandreducedcodereadability
Redundantblockcomments
andmaintainability.
Theregexrulesarecarefullydesignedtoensurethatonlyexecutablecoderemainsin
thefinalscript. Byremovingnarrativecontentandpresentation-relatedsyntax,theframe-
workprovidesacleanedscriptthatisreadyforautomatedtestingwithoutcausingexecu-
tionerrorsbythePythoninterpreter. Afterthiscleaningstep,thescriptispassedthrough
a formatting stage using the autopep8 library. This tool enforces Python’s PEP 8 style
guidelines, which focus on readability, consistent indentation, and proper line spacing.
Formatting the code at this point enhances clarity for human reviewers and makes the
scriptmoreeasilyintegrableintoautomatedworkflowsorversioncontrolsystems.

## Page 12

Computers2025,14,501 12of26
Inadditiontoformattingandcontentcleanup,theframeworkusestheremove_lines_
after_quit()function. Thisstepensuresthescriptendsimmediatelyafterthedriver.quit()
command,whichmarksthecloseoftheSeleniumsession. Anylinesthatfollow,suchas
debugnotesorleftoverplaceholders,areremovedtopreventerrorsduringtestexecution.
Thecleanedcodeisthensavedasa.pyfile. Thesecleaningandoptimisationstepstogether
formastrongpost-processinglayerthatenforcespropersyntaxandfunctionalaccuracy.
Thisfinalversionofthescriptmovestothelaststageoftheframework: testexecutionand
reporting. Atthispoint,therefinedandcleanscriptinteractswithalivebrowsersession,
completingtheLLM-poweredautomationcycle.
3.4. Step4: TestExecutionandReporting
ThefinalstageoftheproposedAutoQALLMsframework,i.e.,Step4,focusesontest
executionandreporting. Itrunstheoptimised.pytestscriptonthewebapplicationand
recordstheoutcomestoverifytheapplication’sfunctionality. Executionismanagedbythe
execute_selenium_code()function,whichlaunchesabrowserusingSelenium’sChrome
WebDriver. ThebrowserisconfiguredwithChromeOptionstoopeninfull-screenmode.
Runninginnon-headlessmodeenablesreal-timeobservationofthetestflow,helpingto
identifyissuessuchasUImisalignment,loadingdelays,orunexpectedpop-ups. Thescript
thencarriesoutasequenceofactionsgeneratedbyLLMs,includingnavigatingtheDOM,
locatingelements,clickingbuttons,submittingforms,andfollowinglinks.
During execution, all test outcomes, whether passed or failed, are printed to the
consolealongwithcontextuallogmessages.Theselogsserveasalivereportingmechanism,
offeringimmediateinsightintothetestflow. Althoughthecurrentsetupusesterminal-
basedreporting,thearchitectureisflexible. Futureversionscaneasilyintegratetoolslike
PyTestpluginsorAlluretogenerateHTMLdashboards,JSONlogsforCIpipelines,orXML
reportsforsystemslikeTestRailandZephyr. Moreover,ifanerroroccurs,whetherdue
to a logic issue, an outdated selector, or an unhandled exception, detailed error traces
are captured. This final phase validates both the functionality of the web application
and the reliability of the LLM-generated test script. It completes the framework with
actionableresults,demonstratingthatLLM-driventestautomationispracticalandeffective
forreal-worldQAprocesses.
4. ExperimentalSetup
4.1. ToolsandTechnologies
AutoQALLMs combine tools, libraries, and APIs that enable intelligent, scalable,
andhigh-performancetestautomation. Table3presentsasummaryofthemaintoolsand
theirrespectivefunctions.
Table3.TechnologicalcomponentsandtheirrolesinAutoQALLMs.
Component Technology Purpose
Primaryprogramminglanguage;scriptorchestrationand
Language Python
integration
StructuredparsingofwebpageDOMtoextracttestable
HTMLParsing BeautifulSoup
elements
PerformsGETrequeststofetchHTMLcontentfromthe
HTTPCommunication requests
user-providedURL
Generatescontext-awareSeleniumtestscriptsbasedon
LLMTestGeneration OpenAIGPT-4API
HTMLstructure
CleansandrefinesLLM-generatedcodebyremoving
RegexFiltering Pythonremodule
non-functionalcontent

## Page 13

Computers2025,14,501 13of26
Table3.Cont.
Component Technology Purpose
AppliesPEP8stylingforreadableandmaintainable
CodeFormatting autopep8
Pythonscripts
ExecutesUI-levelautomationacrosswebapplications
WebAutomationEngine SeleniumWebDriver
inarealbrowser
ActsasthebridgebetweenSeleniumandtheChrome
BrowserDriver ChromeDriver
browserinstance
TriggersexecutionofsavedPythontestfilesinthe
ExecutionEnvironment osmodule(os.system)
hostterminal
Providesanefficientdebugginganddevelopment
IDE PyCharm
environment
4.2. TestingStrategy
To validate the reliability, performance, and robustness of AutoQALLMs, a multi-
layeredtestingstrategyisimplemented,comprisingunittesting,integrationtesting,func-
tionaltesting,andperformanceevaluation.
Unittestingisappliedtocorefunctionssuchasfetch_html(),parse_html(),andclean_
selenium_code(). Eachfunctionistestedindependentlytoconfirmitworkscorrectlyunder
different input conditions. Simulating edge cases, such as invalid URLs, missing tags,
ormalformedHTMLcontent,alsoverifieserrorhandling.
Integrationtestingverifiesthatmodulesworktogethersmoothly. Forexample,theflow
ofparseddatafromparse_html()togenerate_selenium_code()istestedusingwebsiteswith
differentlayouts. ThehandofffromLLMsoutputtothecleanedscriptisalsoreviewedto
ensureitmaintainslogicandfunctionality.
Functionaltestingisperformedonrealwebsitestoconfirmthatthegeneratedscripts
can interact with and validate dynamic elements. This includes checking page titles,
clickinglinks,detectingbrokenimages,andfillingoutinputforms. Thesetestsensurethe
automationmimicsrealisticuserbehaviour.
Performancetestingmeasureshowefficientlytheframeworkruns. Itassessesresponse
timeandexecutionspeedacrossdifferenttypesofwebsites,rangingfromsimplestatic
pagestocomplex,JavaScript-heavyones. Keymetricssuchasscriptgenerationtime,test
executionduration,andbrowserresponsedelaysarerecordedandanalysed.
Together, these validation steps confirm that the framework runs reliably across
variousenvironments. Theyalsodemonstratetheiradaptability,effectivenessinpractical
use,andreadinessforintegrationintocontinuoustestingpipelines.
4.3. TestSubjects
Tovalidatethereliability,performance,androbustnessofAutoQALLMs,theframe-
workwasevaluatedon30publiclyavailableautomationpracticewebsites. Thecomplete
listoftargetapplicationsisprovidedinTable4. These30websitesencompassadiverse
rangeofstructuralandfunctionalcharacteristics,ensuringacomprehensiveevaluation
of the proposed framework. The selection includes static and text-oriented pages (e.g.,
HerokuApp: iFrame,NestedFrames),interactiveandform-basedapplications(e.g.,De-
moQA: Practice Form, LetCode), and multimedia-rich or e-commerce platforms (e.g.,
DemoBlaze,OpenCart,Greencart). Acrossthesewebsites,theaveragenumberofinterac-
tivemenusornavigationcomponentsrangedfromthreetoeightperpage,dependingon
thewebsite’scomplexityandcontenttype. Staticwebsitesprimarilycomprisedtextualand
imageelements,whereasdynamicandmultimediasitesincorporatedAJAX-drivencom-
ponents,modalwindows,dynamictables,andmultipleform-inputfields. Thisdiversity

## Page 14

Computers2025,14,501 14of26
ensuresthatAutoQALLMshavebeenassessedunderheterogeneoustestingconditions,
validatingtheiradaptabilityandrobustnessacrosssimple,content-focusedpagesaswell
ascomplex,multi-componentwebinterfaces.
Table4.ListofWebApplicationsUsedforEvaluation.
WebsiteName URL
UITestingPlayground http://uitestingplayground.com/,(accessedon1November2025)
TestPages https://testpages.herokuapp.com/styled/index.html,(accessedon1November2025)
GlobalSQADemoSite https://www.globalsqa.com/demo-site/,(accessedon1November2025)
AutomationBroPractice https://practicetestautomation.com/,(accessedon28August2025)
DemoBlazeE-commerce https://www.demoblaze.com/,(accessedon2November2025)
RahulShettyAcademy https://rahulshettyacademy.com/AutomationPractice/,(accessedon25July2025)
OpenCartDemoStore https://demo.opencart.com/,(accessedon2November2025)
PHPTRAVELSDemo https://phptravels.com/demo/,(accessedon1November2025)
RahulShettyAcademy https://rahulshettyacademy.com/angularpractice/,(accessedon2July2025)
Greencart https://rahulshettyacademy.com/seleniumPractise/#/,(accessedon25July2025)
HerokuApp:JSAlerts https://the-internet.herokuapp.com/javascript_alerts,(accessedon1November2025)
HerokuApp:NestedFrames https://the-internet.herokuapp.com/nested_frames,(accessedon1November2025)
HerokuApp:iFrame https://the-internet.herokuapp.com/iframe,(accessedon2November2025)
HerokuApp:DynamicLoading https://the-internet.herokuapp.com/dynamic_loading,(accessedon1November2025)
LetCode https://letcode.in/test,(accessedon25July2025)
HerokuApp:Hovers https://the-internet.herokuapp.com/hovers,(accessedon1November2025)
HerokuApp:KeyPresses https://the-internet.herokuapp.com/key_presses,(accessedon2November2025)
DemoQA:PracticeForm https://demoqa.com/automation-practice-form,(accessedon22July2025)
DemoQA:WebTables https://demoqa.com/webtables,(accessedon25July2025)
DemoQA:Buttons https://demoqa.com/buttons,(accessedon28August2025)
DemoQA:Widgets(DatePicker) https://demoqa.com/date-picker,(accessedon28August2025)
DemoQA:Interactions(Droppable) https://demoqa.com/droppable,(accessedon28August2025)
UIPlayground:AJAXData http://uitestingplayground.com/ajax,(accessedon2November2025)
UIPlayground:ClientSideDelay http://uitestingplayground.com/clientdelay,(accessedon1November2025)
UIPlayground:DynamicTable http://uitestingplayground.com/dynamictable,(accessedon1November2025)
CosmoCodeWebTable https://cosmocode.io/automation-practice-webtable/,(accessedon23August2025)
Guru99BankingDemo https://demo.guru99.com/V4/,(accessedon1November2025)
SauceDemo https://www.saucedemo.com/,(accessedon3November2025)
ParaBank https://parabank.parasoft.com/,(accessedon2November2025)
WebDriverUniversity.com http://webdriveruniversity.com/,(accessedon2November2025)
4.4. EvaluationMetrics
ToevaluatetheperformanceoftheproposedAutoQALLMs,thefollowingmetrics
areused:
ScriptGenerationTime: Thetimetakentogeneratetestscriptsbeforeexecution. Faster
scriptgenerationreducesmanualeffortandimprovesproductivity[33].
ExecutionSpeed:Thetotaltimeneededtorunalltestcasesafterthescriptisready. Shorter
executiontimeincreasesoveralltestingefficiency[21].
TestCoverage:Testcoveragemeanshowmanyelementsonawebpage(likelinks,headings,
andimages)aretestedbythetestscriptcomparedtothetotalnumberofelementsparsed.
Morecoveragemeansbettertesting[34].

## Page 15

Computers2025,14,501 15of26
Currently,AutoQALLMsdonotscanortestalltheelementsonthepage.Still,itcovers
severalcommonones,includinglinks,anchors,forms,inputs,buttons,selects,headings,
andimages,andcreates30basictestcases.
Testcoverageiscalculatedusingthefollowingformula:
(cid:18) (cid:19)
Elementstested
TestCoverage(%)= ×100
Totalelementsfound
Forexample,onthetestpagehttps://rahulshettyacademy.com/AutomationPractice/
(accessedon25July2025),thetoolfound33elements(17links,13headings,and3image).
Outofthose,30weretested. Therefore,theestimatedcoverageis:
(cid:18) (cid:19)
30
TestCoverage(%)= ×100≈90.91%
33
FailureRate: Thefailurerateisthepercentageoftestcasesthatfailduringexecution. This
canhappenduetoincorrectlocators,timingissues,orlogicerrorsinthescript[4].
Fortheproposedapproach,thefailurerateisaround20%. Thisisexpected,aszero-
shotpromptingcanoccasionallygenerateincorrectlocatorsforcomplexordynamically
loaded elements. Future work will aim to reduce this by experimenting with few-shot
learning,fine-tuningandchain-of-thoughtlearningapproaches. Moreover,theobserved
20%failureratesuggeststhatwhileAutoQALLMsarecomparativelyeffectiveforrapid,
initialtestsuitegeneration,theiroutputwouldstillrequireabriefhumanreviewbefore
being integrated into a mission-critical regression pipeline. This positions the tool as a
powerful’testaccelerator’ratherthanacompletereplacementforQAoversight.
Adaptability: The degree to which a product or system can be effectively and effi-
cientlyadaptedfordifferentorevolvinghardware,softwareorotheroperationalorusage
environments[36].
Readability: Theeasewithwhichahumanreadercancomprehendthepurpose,control
flow, and operation of source code. It is a human judgement of how easy a text is to
understand[37].
Maintainability: The degree of effectiveness and efficiency with which the intended
maintenanceengineerscanmodifyaproductorsystem. Maintainabilityiscomposedof
modularity,reusability,analysability,modifiability,andtestability[36].
Scalability: The degree to which a system, network, or process can handle a growing
amountofwork,oritspotentialtobeenlargedtoaccommodatethatgrowth[38].
The independent variables considered in this evaluation include script generation
time, execution speed, number of web elements parsed, and type of web application.
ThesevariableswerevariedacrossmultiplewebsitestoassessAutoQALLMs’performance.
Thedependentvariables,namelytestcoverage,failurerate,readability,adaptability,main-
tainability,andscalability,wereusedtomeasureperformanceoutcomes. Therelationship
betweenthesevariablesindicatesthataspagecomplexityandelementcountincreased,Au-
toQALLMsmaintainedhighcoverageandlowexecutiontime,confirmingtheirscalability
andefficiency.
5. ResultsandDiscussion
We evaluated the performance of the AutoQALLMs using 8 widely used metrics:
(i)scriptgenerationtime,(ii)executionspeed,(iii)testcoverage,(iv)failurerate,(v)adapt-
ability,(vi)readability,(vii)maintainability,and(viii)scalability. Wecomparedtheresults
withmanuallywrittenSeleniumscriptsandMonkeyTesting. Eachmethodwastestedon
30webapplications. Thetestswererepeated50times,andtheresultswereaveragedto

## Page 16

Computers2025,14,501 16of26
minimisevariation. Theevaluationfocusedonhoweachmethodperformsinstructured
testingtasksandhowsuitableeachisforreal-worlduse.
MonkeyTestingisawidelyusedtechniqueforautomatedtestingthatinvolvesgen-
eratingrandomuserinteractionsonapplicationswithoutpredefinedsteps[8,27,39]. This
methodcanhelpidentifyunexpectedissues,suchasapplicationcrashes,andisoftenused
forstresstesting[39]. However,becausetheapproach“lacksknowledgeabouttheform
fields,itsrandomtrialscanbeextremelyslow,”whichmakesitlessusefulforstructuredor
plannedautomationtasks[8].
The performance of AutoQALLMs-generated scripts, manually written scripts,
andmonkeytestingisevaluated,andtheresultsarepresentedinTable5. Thecomparison
highlightshoweachmethodperformsacrossdifferentwebapplications.
Table5.ComparativeAnalysisofTestAutomationApproaches.
Metric AutoQALLMs ManualSelenium MonkeyTesting
ScriptGenerationTime 5s 2h N/A
ExecutionSpeed Fast(20s/test) Moderate(35s/test) Variable
TestCoverage(%) 91% 98% 50–60%
FailureRate(%) 20% 10% 50%
AdaptabilitytoUIChanges Moderate High None
Readability Moderate High N/A
Maintainability High Moderate Low
Scalability VeryHigh Low N/A
5.1. EvaluationMethodologyandExpertRubric
Tovalidatetheresults,structuredfeedbackwascollectedfromfivedomainexpertsin
softwaretestingandautomationusingashortsurvey,asshowninAppendixA.Theex-
pertswereselectedfromdiverseindustriesandrolestoprovidebalancedinsights. Their
inputhelpedinterprettheobserveddifferencesintestperformanceacrossAutoQALLMs-
generatedscripts,manuallywrittenscripts,andMonkeyTesting(seeTable6).
Expert1statedthatAutoQALLMscouldcreatetestscriptswithinseconds,whereas
manualscriptingtypicallytookseveralhourstocomplete. Theexpertbelievedthisspeed
wasbeneficialformanualtesterswholackstrongcodingskills. Healsomentionedthat
AutoQALLMscangeneratemultipletestssimultaneously,makingiteasiertoscaletesting
forlargeprojects. However,theexpertpointedoutthatsomeofthegeneratedscriptswere
toogeneral. WhileAutoQALLMsmadeiteasytoregeneratebrokentestsafterUIchanges,
theexpertfeltthatmanualscriptswerestilleasiertounderstand,fix,andsharewithothers.
Expert2notedthatAutoQALLMscoveredslightlyfewerUIelements(96%)thanmanual
scripts (98%). However, the expert explained that manual scripts often included more
meaningfulchecksbasedontheapplication’slogic. Intheexpert’sview,AutoQALLMwas
goodatidentifyingwhatwasvisibleonthescreen,butitsometimesmisseddeeper,more
thoughtfulvalidations. Theexpert2feltthisshowedatrade-offbetweenmoreexhaustive
coverageanddetailedaccuracy.
Similarly, Expert 3 focused on how well the scripts handled changes to the user
interface. The expert stated that manual scripts were more effective at handling these
changesbecausehumantesterscouldwritethecodeinawaythatanticipatedupdates.
Incontrast,AutoQALLMsscriptsoftenbrokewhenthelayoutchanged.Theexpertalsosaid
MonkeyTestingdidn’tadjustatall,makingitunreliableforserioustesting. Additionally,
Expert4agreedwithmanyoftheearlierpoints,particularlyregardingthespeedatwhich
thescriptsran.TheexpertstatedthatAutoQALLMsscriptstypicallycompleteinabout20s,

## Page 17

Computers2025,14,501 17of26
whichhelpsspeedupregressiontesting. Manualscriptstooklonger(approximately35s),
primarilyduetoadditionalchecksaddedbythetester. Expert4alsoagreedwithExpert3
thatmanualscriptshandledchangesintheUIbetter. Finally,Expert5talkedaboutfailure
rates. Theexpertaddedthatmanualscriptshadthelowestfailurerate(approximately
10%)becausetesterscouldcarefullyselectthecorrectelementsandusecustomwaittimes.
AutoQALLMshadamoderatefailurerate(approximately20%);itperformedwellonstable
websitesbutstruggledwithdynamicones. MonkeyTestingfailedmostoften(around50%)
becauseitsactionswererandom. TheexpertmentionedthatAutoQALLMsscriptswere
easytoreadbutsometimeslongerandlessclearthanmanualscripts.
Table6.ExpertopinionsonAutoQALLMs,manual,andMonkeyTesting.
Expert Background OpinionHighlights
AutoQALLMscreatedtestscriptswithinseconds,
whichhelpedteamsworkinginfast-pacedagile
Expert1:Lead
Leadslarge-scaleQA projects.Italsomadeiteasiertoscaletesting
AutomationEngineer
teamsandenterprisetest acrossmultiplescenarios.However,somescripts
(23yrs,Rapidue
automation. felttoogeneral.Whileitwaseasytofixbroken
TechnologyLtd.)
testsbyregeneratingthem,manualscriptswere
stilleasiertounderstandandshare.
AutoQALLMscoveredslightlylessoftheuser
interface(96%vs.98%)andoftenmisseddeeper
Expert2:SeniorQA
Focusesonindustrial checksthatmanualtesterswouldinclude.Manual
Analyst(5yrs,Domino
deviceUItesting. scriptshadmoremeaningfulvalidations.This
PrintingSolutions)
showedatrade-offbetweenbroadcoverageand
detailedtesting.
Manualscriptsworkedbetterwhentheuser
Worksonenvironmental interfacechanged,astesterscouldplanfor
Expert3:QALead
platformtestingwith updates.AutoQALLMsscriptsoftenfailedwith
(6yrs,Recykal)
dynamicUIs. layoutchanges.MonkeyTestingdidn’tadjustatall
andwasn’treliable.
AutoQALLMsscriptsranfaster(around20s)than
Expert4:Test manualscripts(about35s),whichhelpedspeed
MaintainsSeleniumin
AutomationSpecialist uptesting.Butmanualscriptsweremoreflexible
CI/CDpipelines.
(7yrs,Recykal) whentheUIchanged.MonkeyTestingdidn’t
followaclearprocessandwasinconsistent.
Manualscriptshadthelowestfailurerate(around
10%)becausetesterscarefullypickedelementsand
setwaits.AutoQALLMshadahigherfailurerate
Expert5:UI/UX
Testsusabilityanddesign (about20%);itworkedfineonstablepagesbut
AutomationEngineer
consistency. struggledwithdynamicones.MonkeyTesting
(5yrs,Recykal)
failedoften(about50%)duetoitsrandomactions.
AutoQALLMsscriptswereeasytoreadbut
sometimestoolongorunclear.
TheexpertfeedbackconfirmedthattheAutoQALLMstestingbroughtgainsinspeed,
coverage,andscalability. However,itstillhadsomelimitationsintermsoftestaccuracy,
UIchanges,anddeepervalidation. Theselimitationsunderscorethecontinuedimportance
ofhumanoversightinautomationtestingworkflows. TheresultsindicatethatLLMscan
supportsoftwaretesting,buttheyshouldbeusedinconjunctionwithmanualreviewfor
reliableoutcomes.
TocomplementthequalitativeopinionspresentedinTable6,thesamefivedomain
expertswereaskedtoratethequalitativeattributesofthegeneratedtestscripts: readability,
adaptability, maintainability, and scalability using a five-point Likert rubric (1 = Poor,
5=Excellent). The detailed rubric and evaluation guidelines provided to experts are
presentedinAppendixA.2. TheaggregatedexpertratingsaresummarisedinTable7.

## Page 18

Computers2025,14,501 18of26
Table7.ExpertEvaluationScoresforQualitativeMetrics(1–5Scale).
Metric Expert1 Expert2 Expert3 Expert4 Expert5 MeanScore
Readability 5 4 5 4 5 4.6
Adaptability 4 4 5 5 4 4.4
Maintainability 4 5 4 4 5 4.4
Scalability 5 4 5 5 4 4.6
Thequantitativeevaluationconfirmedhighconsistencyamongexperts,supporting
thereliabilityofthequalitativefeedbackandvalidatingtherobustnessofthegenerated
Seleniumscriptsacrossallfourattributes.
5.2. ModelComparision
Inadditiontotheseperformancemetrics,theanalysiswasexpandedtoincludecostef-
ficiency.Table8presentsboththecostpermilliontokensandtheestimatedcostperindivid-
ualtestscript.Acrosstheevaluatedwebsites,GPT-4averagedaboutUSD0.011[40]pertest,
comparedwithUSD0.016forClaude4.5[41]andUSD0.0006forGrokFast[42],basedon
anaveragetokenconsumptionof1800tokenspersite. Thiscost-awareevaluationquantita-
tivelysupportsGPT-4’sbalancebetweenaccuracyandaffordability,reinforcingthestudy’s
emphasisonoptimisingtrade-offsbetweenperformanceandoperationalexpenserather
thanfocusingsolelyonrawcoverage. LLMcomparisonresourcesandimplementationde-
tailsareavailableforfuturework(https://github.com/Sindhupriya2797/AutoQALLMs).
Table8.ComparativeAnalysisofModelPerformance,Coverage,andCostEfficiency.
Cost/1M
Test Avg.Gen. Avg. Cost/Test
Model Tokens
Coverage(%) Time(s) Tokens/Test (USD)
(USD)
Input:2.50
GPT-4 91 5.4 1800 0.011
Output:10.00
Claude4.5 Input:3.00
96 4.8 1800 0.016
Sonnet Output:15.00
Input:0.20
GrokFast 88 6.2 1800 0.0006
Output:0.50
Notes.Costpertestcasewascalculatedusingtheaveragetokenusageofapproximately1800tokensperwebsite
(900input+900output).Pricingreflects2025APIrates.GPT-4achievesastrongbalancebetweenaccuracyand
cost($0.01pertest),Claude4.5offersslightlyhighercoverageat 50%highercost,andGrokFastprovidesthe
lowestcostbutreducedcoverage.
During experimentation, each test case generation consumed approximately
1800tokens per website, evenly distributed between input and output tokens. The es-
timatedcostperscriptforeachmodelwascomputedusing2025APIpricingasfollows:
(cid:18) (cid:19) (cid:18) (cid:19)
InputTokens OutputTokens
Costperscript= ×InputRate + ×OutputRate
106 106
For900inputand900outputtokens:
2.50 10.00
GPT-4: (900× )+(900× ) = $0.011
106 106
3.00 15.00
ClaudeSonnet4.5: (900× )+(900× ) = $0.016
106 106
0.20 0.50
GrokFast: (900× )+(900× ) = $0.00063
106 106

## Page 19

Computers2025,14,501 19of26
Thus, theaveragecostpertestcasewasapproximately$0.01forGPT-4, $0.016for
Claude4.5,and$0.0006forGrokFast,demonstratingthatGPT-4offersastrongtrade-off
betweencostandaccuracy.
The pricing structure of each model clarifies the observed cost-performance trade-
offs. Grok Fast is designed for high-volume, low-cost tasks, with output rates nearly
twentytimescheaperthanGPT-4andthirtytimescheaperthanClaude4.5. Claude4.5
Sonnetisthemostexpensive,particularlyintermsofoutputtokens,reflectingitsempha-
sisonadvancedreasoning. GPT-4offersabalancedmiddlegroundbetweencapability
and affordability. Across all three, output tokens remain significantly more costly than
inputtokens.
ToextendtheexistingLLMcomparisons,asshowninTable8,Claude4.5achievedthe
highestcoverageandexecutionreliability,benefitingfromitsstrongercontextualreasoning
andcoherentinstruction-followingability. GPT-4,however,demonstratedthebestbalance
between syntactic accuracy, runtime stability, and execution speed, making it the most
consistent model for Selenium-based test automation. Although Grok Fast generated
outputs more quickly, its limited handling of dynamic DOM structures led to a lower
passrate.
5.3. ComputationalComplexityAnalysis
Inadditiontotheempiricalcomparisonofexecutiontime,thecomputationalcom-
plexityoftheproposedframeworkwasanalysedtoevaluateitsscalability. AutoQALLMs
operatethroughfoursequentialphases: (i)HTMLextractionandparsing,(ii)LLM-based
script generation, (iii) regex-driven code cleaning, and (iv) Selenium-based execution.
Theoveralltimecomplexitycanbeexpressedas:
T(n,m,t) =O(n+m+t) (1)
where n denotes the number of parsed HTML elements, m represents the length of the
generated script, and t corresponds to the number of executed test cases. Since HTML
parsingdominatesthetotalcomputation,theframeworkexhibitsanapproximatelylinear
growthrate:
T(n) ≈O(n) (2)
Thisindicatesthattheexecutiontimeincreasesproportionallywiththenumberof
webelements.
ManualSeleniumscripting,ontheotherhand,requiresrepetitivehumanintervention
foreveryadditionalelementandtestcase,resultinginaslower,non-scalableprocessthat
canbeapproximatedas:
T(n,h) =O(n×h) (3)
wherehisthehumaneffortfactorperelement.
Similarly,MonkeyTestingperformsrandominteractionswithacomplexityofO(r),
whereristhenumberofrandomeventsrequiredtoreachsufficientcoverage. However,
duetoitsstochasticnature,thisapproachdemandssignificantlymoreiterationstoachieve
comparableaccuracy.
Empirically, AutoQALLMs generated executable Selenium scripts within approxi-
mately20–25sperwebsite,comparedto2hformanualscripting,whilemaintaining96%
coverage. Theaverageexecutiontimepertestwasaround20s,confirmingboththelinear
timecomplexityandthesubstantialreductionincomputationalandanalyticaleffort.

## Page 20

Computers2025,14,501 20of26
5.4. ComparisonwithState-of-the-ArtApproaches
Asignificantcontributiontocodelesstestautomationwasmadeby[3],whoproposed
aframeworkcombiningSeleniumandmachinelearningtogeneratetestswithoutwriting
code. Their method relied on an SVM trained on manually annotated data to predict
actions. Still,itlackedtestingseveralbehavioursatthesametime(Testedonlyforsearch
functionality). Similarly, ref. [8] introduced a T5-GPT-based framework that combined
Crawljax, T5, and GPT-4o to automate web form interaction. Their method parsed the
DOMusingCrawljaxtoidentifyinputfieldsandusedLLMsforfieldclassificationand
valuegeneration. Whileitimprovedcoverageoverreinforcementlearningagents,itwas
limitedtoform-fillingtasksandcouldnothandlecategorieswhoseformatsdependon
theselectedlocations. InmobileGUItesting,Liuetal.[20]presentedGPTDroid,which
redefinestestingasaquestion-and-answertaskusingGPT-3.5withfunctionality-aware
prompts. ThismethodachievedhighactivitycoverageonAndroidappsbutwaslimited
to mobile domains, and it faced challenges with UI components that lacked clear text
labels. Lastly,ref. [22]proposedanLLM-poweredapproachforvisualUIandA/Btesting,
usingscreenshotcomparisonstoidentifyrenderingissues. Althougheffectiveforvisual
validation, the method lacked DOM-level analysis and did not produce an actionable
testscript.
Anotherkeypointofcomparisonistheunderlyingmethodologyusedtointerpretthe
webapplication’sstructure. WhileAutoQALLMsgeneratescriptsbyprovidingadirect,
parsed HTML summary to the LLM, the framework by [30] employs an intermediate
modellingstep. Theirapproachcreatesexplicitscreentransitiongraphsandstategraphs
tomodeltheapplication’sflowbeforegeneratingtests. Thisgraph-basedmethodologyis
specificallydesignedtoimprovetestcoveragefordynamicnavigationandcomplexcondi-
tionalforms,whichareknownchallengesformoredirectgenerationmethods. Incontrast,
AutoQALLMseliminatetheneedforhandwrittentemplatesorscreenshot-basedprompts
byutilisingvariousLLMs,includingGPT-4,Claude,andGrok,togenerateexecutableSele-
niumscriptsdirectlyfromHTML.ItintegratesBeautifulSouptoparseliveDOMstructures
andusesregularexpressionstoadaptthescriptautomaticallytostructuralchanges. Unlike
previousapproaches,AutoQALLMscoverfunctionaltesting,dynamicallyupdatesscripts,
and supports a full-cycle pipeline from generation to execution and reporting without
relying on visual UI cues or fixed form data. This enables AutoQALLMs to maintain
robustnessinfast-changingwebapplications. Basedonourunderstandingandknowledge,
wedemonstratedthecomparisonbetweentheproposedandstate-of-the-artapproachesin
Table9.
Inadditiontothemodelcomparisonsdiscussedearlier,threecomplementarycate-
gorieswereexaminedtocontextualiseexistingapproaches: bot-detectionandbehaviour
analysisframeworks,webcrawlingsystemssuchasScrapy,andNamedEntityRecognition
(NER)techniques. Behaviouranalysistools,suchasOWASPAppSensor,monitorapplica-
tionlayeractivitiestodetectanomalousorautomatedbehaviourandtriggeralertsbased
onpredefinedsensorrules[43]. Scrapyisanopen-sourcecrawlingframeworkdesignedfor
efficientextractionofstaticHTMLcontent,althoughitcannotprocessdynamicorinterac-
tivewebelements[44]. NERtechniques[45]identifyandclassifymeaningfulentitiessuch
asnames,locations,andorganisationswithinunstructuredtextusingadvancednatural
languageprocessingmodels. Table10summarisestheseapproaches,highlightingtheir
objectives,methodologies,andcorelimitationsinrelationtointelligentautomationsystems
thatintegratesemanticreasoningwithexecutablevalidation.

## Page 21

Computers2025,14,501 21of26
Table9.ComparisonofLLM-BasedTestAutomationApproaches.
KeyTechniques
Approach Domain Limitations Strengths
Used
Selenium+SVM
WebApplication Testedonlysearch Codelessprediction
[3] (ML-based
Testing functionality oftestactions
prediction)
Form-specific;
Crawljax+T5+ challengeswith Improvedform
[8] WebFormTesting
GPT-4o geo-sensitive coverageviaLLMs
fieldformats
RestrictedtoAndroid;
Highactivity
GPT-3.5+GUItree+ challengeswhen
[20] MobileGUITesting coveragefor
memoryprompts elementslack
mobileapps
textlabels
NoDOMparsing; Effectivevisual
LLM+Screenshot
[32] VisualUITesting doesnotgenerate regressionand
Comparison
testscripts A/Btesting
GPT-4+ Stilldeveloping Fullpipeline
WebApplication
AutoQALLMs(Ours) BeautifulSoup+ robustnessforhighly automation,dynamic
Testing
Regex+Selenium dynamicUIs scriptgeneration
Table10. ComparativeOverviewofBot-Detection,Scrapy,NER,andAutoQALLMsApproaches
basedonourunderstandingandknowledge.
Tool/Technique Objective Methodology Limitations Ref.
Monitors
Detectandrespondto Focusesonsecurity
application-layer
Bot-Detection/Behaviour automatedor anomalydetection;does
behaviourusing
Analysis(e.g., maliciousactivities notsupportweb [43]
predefinedsensors
OWASPAppSensor) withinweb interactionorfunctional
andtriggersalertsfor
applications. validation.
suspiciousevents.
UtilisesPython-based
crawling,rule-based TheScrapy-basedcrawler
Extractstructured XPath/CSSselectors, exhibitedasignificant
Scrapy contentfromstatic andscheduling limitationwhenanalysing [44]
HTMLpages. pipelinesfor puresingle-page
large-scaledata applications(SPAs).
extraction.
AppliesNLPmodels Itsclassificationsare
fortokenisation, probabilistic,carrying
Identifyandclassify
sequencelabelling, inherentuncertaintyabout
NamedEntity semanticentities
andcontextual theiraccuracyandthus [45]
Recognition(NER) within
embeddings(e.g., requiringconfidence
unstructuredtext.
BERT,Word2Vec)to scoresratherthanabsolute
extractentitytypes. answers.
IntegrateLLMswith
Currentlyoptimisedfor
Automateintelligent BeautifulSoup,Regex,
modernbrowsers;
webtestingthrough andSeleniumtoparse
handlingofcomplex
AutoQALLMs(Proposed) end-to-endscript DOMelements, Thisstudy
dynamicUIelements
generationand generatetestscripts,
remainsafuture
execution. andvalidate
enhancement.
functionality.
5.5. Discussion
The proposed AutoQALLMs provided a preliminary study on how LLMs can col-
laborate with tools such as DOM parsers and Selenium to automatically generate and
executetestscriptsforwebsites. Theresultsshowthatwhenprovidedwithwell-structured
promptsandthecorrectHTMLinput,LLMscangenerateSeleniumscriptsthatrunsuc-
cessfullywithoutanyhumanintervention. Thisdirectlyanswersourfirsttworesearch
questions: (i)“HowcanLLMsbecombinedwithwebscrapingandSeleniumtocreatetest
scripts?”,and(ii)“CanLLMsturnHTMLintoworkingSeleniumscriptsusingzero-shot
prompts?”UsingBeautifulSouptoextractHTMLelementsanddesigningpromptsthat
givethescripttogenerateseleniumtestscripts,AutoQALLMswereabletoconvertweb
contentintotestactions. Theuseofzero-shotpromptingalsomeantthatthesystemcould
handleneworunfamiliarpageelementswithoutrequiringretrainingofthemodel.

## Page 22

Computers2025,14,501 22of26
Forthethirdresearchquestion,whichasked“CanAutoQALLMsoutperformmanual
or semi-automated testing in code coverage and fault detection?”, the expert feedback
revealedbothstrengthsandareasforimprovement. Onthepositiveside,AutoQALLMs
achievedbroadUIcoverage(96%)thatwascompetitivewithmanualmethods(98%)and
saved significant time in writing scripts. However, there were also concerns, such as
missingdeeperlogicvalidationsandhavinglowerdebuggabilitycomparedtomanually
writtenscripts. AutoQALLMswereabletoquicklyregeneratebrokentestsandrunthem,
whichishelpfulforagileteamsandCI/CDpipelines. Thiscapabilitydirectlyaddresses
asignificant,unresolvedchallengeinthefield,asidentifiedbyrecentsurveys: thehigh
maintenancecostsoftestsuitesinthefaceoffrequentUIchanges[9]. Overall,theapproach
showspromiseinmakingautomationmoreaccessible,especiallyforteamswithlesscoding
experience,anditopensupnewdirectionsforcombininghumanexpertisewithLLM-based
automationinthefuture.
WhileAutoQALLMsareprimarilyimplementedusingGPT-4,acomparativeevalua-
tionwasconductedwithClaude4.5andGrokFasttobenchmarkperformance.Thefindings
indicatedthatClaude4.5achievedmarginallyhighertestcoverage(96%)duetoitsad-
vancedarchitectureandenhancedreasoningcapabilities. Nonetheless,GPT-4consistently
generatedsyntacticallyvalidSeleniumscriptswithfewerruntimeerrorsandexhibited
faster, more predictable generation times across diverse websites. When both cost and
stability were considered, GPT-4 emerged as the most balanced option for scalable de-
ployment: itsaveragecostpertestgenerationwaslowerthanthatofClaude4.5,andits
prompt outputs were more reproducible under identical conditions, an essential factor
forcontinuoustestingpipelines. Consequently,theframeworkcontinuestoutiliseGPT-4
asitsdefaultengine,whileClaude4.5andGrokFastserveascomparativebaselinesthat
contextualise performance-versus-cost trade-offs in LLM-driven testing. It should also
benotedthatClaude4.5representsanewermodelgenerationthanGPT-4,whichpartly
explainsitsmarginallyhighercoverage. Thisdistinctionhighlightstheneedforongoing
benchmarkingacrossfuturereleases,suchasGPT-5andClaudeNext,toensurefairand
up-to-dateevaluation.
5.6. ThreatstoValidity
AkeythreattotheinternalvalidityofAutoQALLMsisitsdependenceonLLMsfor
generatingSeleniumscripts. Whileitperformswelloverall,LLMscanlosecontextinlong
orcomplexinteractions,leadingtoincompleteorincorrecttestcases. Theoutputquality
also heavily depends on prompt design, which may affect consistency across different
environments. Moreover,wecurrentlyparseonlyasubsetoftags(e.g.,links,headings,
andimages),whichlimitstestcoverage. Thismayresultinanincompleterepresentationof
real-worldpagestructures.
ConstructvalidityislimitedbyAutoQALLMs’sabilitytoconvertnaturallanguage
intoactionableteststepsreliably. Thisdependsonthemodel’sunderstandingofdynamic
or ambiguous web structures. Prior work, such as GPTDroid [20], has demonstrated
thatLLMscanhandlefunctionality-awareprompts;however,theysometimesstruggleto
maintainreasoningovermultipleturns.
TechnicalchallengesalsoariseduringDOMscraping,especiallyforJavaScript-heavy
pagesorthosewithanti-scrapingprotections,whichcanresultintheomissionofkeyele-
ments. Toaddresstheseissues,futureworkcouldexplorememory-augmentedmodelsand
explainableAItechniquestoenhancethereasoningandtraceabilityofthegeneratedsteps.
Finally,sinceAutoQALLMscurrentlyfocusonwebGUItesting,theirgeneralizability
tootherdomains, suchasmobileappsorchatbotinterfaces, remainsanopenquestion.

## Page 23

Computers2025,14,501 23of26
Real-world testing also involves complex user behaviours, so integrating multimodal
inputsandmodellinguseractionscouldfurtherenhancetestrealismandcoverage.
6. ConclusionsandFutureWork
ThisstudydemonstratedthattheproposedAutoQALLMscanbeusedtogenerate
Seleniumtestscriptsthatarefast,scalable,andeasytomaintain. Theresultsindicatethat
AutoQALLMsscriptsachievedcompetitiveUIcoveragewhiledrasticallyreducingthetime
neededtocreateandruntests. Experts’feedbackconfirmedthatthismethodcansupport
fasterregressiontestingandmakeautomationmoreaccessible,particularlyforteamswith
less technical skill. However, the scripts sometimes failed when webpages changed or
whenmorethoroughcheckswererequired. Bycontrast,MonkeyTestingwaslessvaluable
duetoitsrandombehaviourandlimitedtestcoverage.
The comparison also showed that manual scripts had the lowest failure rates and
adapted best to UI changes; however, they required more time to write and maintain.
AutoQALLMsscriptsofferedagoodbalancebetweenspeedandreliability. Theywere
slightlymorepronetoerrors,butcouldbequicklyfixedorregenerated. Expertfeedback
confirmedthatthisapproachisbeneficialinagileenvironmentsandcanenhanceoverall
testingefficiencywhenusedinconjunctionwithhumanreview. Ourcomparativeanalysis
showedthatClaude4.5attainedmarginallyhighercoverage,butGPT-4demonstratedthe
besttrade-offbetweenaccuracy,generationcost,andstability,reaffirmingitsroleasthe
coremodelofAutoQALLMs.
Inthefuture,weplantoimprovetheaccuracyandstabilityofAutoQALLMsscripts.
Fine-tuningtheLLMsfortestautomationtasksmayhelpreduceerrors. Testingonlarger
and more complex applications will also help evaluate how well the system scales in
real-worldprojects. AnotherhelpfulstepistoconnectLLM-basedtestingwithtoolslike
JMeter or Gatling to support performance testing. Adding self-healing features could
helpthesystemadjusttoUIchangeswithoutmanualupdates. Thisisakeyareaofre-
search,withrecentapproachesusingLLMstointelligentlyre-locatewebelementsafter
a UI change, significantly improving test script robustness [29]. Future work will also
exploresemi-automatedassertiongenerationtoenablebasicbehaviouralvalidation. Byin-
ferringexpectedoutcomesfromHTML5attributesandJavaScript-basedinterfacecues,
AutoQALLMscanextendbeyondstructuraltestingtoverifyuserinteractionsandpage
responses.Furthermore,futureworkcouldincorporatevisualunderstandingbyleveraging
LargeVision-LanguageModels(LVLMs). AsdemonstratedbytheVETLframework[32],
LVLMscananalyzescreenshotstoovercomethelimitationsofambiguousHTMLandbetter
understandcomplex,dynamicuserinterfaces,representingapromisingpathtoenhance
therobustnessofAutoQALLMs. Comparingthisapproachwithtraditionalframeworks
intermsofcost, speed, andresourceusewillalsohelpguideitsuseinindustry. These
steps may lead to more reliable and intelligent testing systems with less human effort.
AutoQALLMsdemonstratethegrowingroleofLLMsinshapingthefutureofscalableand
intelligentsoftwaretesting.
AuthorContributions:Conceptualization,M.Y.andJ.A.K.;methodology,M.Y.andJ.A.K.;software,
S.M.;validation,S.M.,M.Y.andJ.A.K.;formalanalysis,S.M.,T.M.andA.M.;investigation,S.M.,A.M.
andN.P.;writing—originaldraftpreparation,S.M.,M.Y.andJ.A.K.;writing—reviewandediting,
T.M.,A.M.andN.P.;supervision,M.Y.andJ.A.K.Allauthorshavereadandagreedtothepublished
versionofthemanuscript.
Funding:Thisresearchreceivednoexternalfunding.
DataAvailabilityStatement:Theoriginalcontributionspresentedinthisstudyareincludedinthe
article.Furtherinquiriescanbedirectedtothecorrespondingauthors.

## Page 24

Computers2025,14,501 24of26
ConflictsofInterest:Theauthorsdeclarenoconflictsofinterest.
Abbreviations
Thefollowingabbreviationsareusedinthismanuscript:
LLM LargeLangugaeModel
GPT GenerativePre-trainedTransformer
DOM DocumentObjectModel
LSTM LongShortTermMemory
CNNs ConvolutionalNeuralNetworks
ML MachineLearning
DL DeepLearning
AppendixA.ExpertSurveyQuestionnaire
TocollectexpertfeedbackforvalidatingAutoQALLMs,wedesignedashortsurvey
focusedonfivekeyareas: scriptgenerationspeed,testaccuracy,coverage,adaptability,
andscalability. Thequestionnairewasdistributedviaemailandresponseswerecollected
usingGoogleForms.
AppendixA.1. SurveyQuestions
1. HowwouldyouratethespeedofscriptgenerationforAutoQALLMscomparedto
manualtesting?
2. HowreliableweretheAutoQALLMs-generatedscriptsacrossdifferenttestscenarios?
3. HowwouldyoucomparetheUIcoverageachievedbyAutoQALLMswithmanualor
monkeytesting?
4. HowadaptableweretheAutoQALLMsscriptswhenthewebUIchanged?
5. How scalable do you find AutoQALLMs for enterprise-level testing compared to
traditionalmethods?
6. DoyouseevalueinusingLLM-basedtoolslikeAutoQALLMsinreal-worldsoftware
testingworkflows?
7. Anyadditionalcomments,suggestions,orconcerns?
AppendixA.2. ExpertScoringRubric
Thefollowingrubricwassharedwithallfivedomainexpertstoensureconsistencyin
qualitativeevaluation.Eachmetric,readability,adaptability,maintainability,andscalability,
wasratedonafive-pointscale. (1=Poor,5=Excellent)basedonthefollowingdescriptions:
1. 1—Poor: Verylowquality;unclear,unstable,ornon-functional.
2. 2—Fair: Partiallyfunctionalbutlacksclarityorstability.
3. 3—Moderate: Acceptableperformance;requiresmoderaterevisionordebugging.
4. 4—Good: Clear,functional,andstablewithminorimprovementsneeded.
5. 5—Excellent: Highlyreadable,adaptable,andscalablewithminimalintervention.
References
1. Durelli,V.H.;Durelli,R.S.;Borges,S.S.;Endo,A.T.;Eler,M.M.;Dias,D.R.;Guimarães,M.P. Machinelearningappliedtosoftware
testing:Asystematicmappingstudy. IEEETrans.Reliab.2019,68,1189–1212.[CrossRef]
2. Dog˘an,S.;Betin-Can,A.;Garousi,V. Webapplicationtesting:Asystematicliteraturereview. J.Syst.Softw.2014,91,174–201.
[CrossRef]
3. Nguyen,D.P.;Maag,S. CodelesswebtestingusingSeleniumandmachinelearning. InProceedingsoftheICSOFT2020:15th
InternationalConferenceonSoftwareTechnologies,OnlineEvent,7–9July2020;pp.51–60.

## Page 25

Computers2025,14,501 25of26
4. Paul,N.;Tommy,R. AnApproachofAutomatedTestingonWebBasedPlatformUsingMachineLearningandSelenium. In
Proceedingsofthe2018InternationalConferenceonInventiveResearchinComputingApplications(ICIRCA),Coimbatore,India,
11–12July2018;pp.851–856.
5. Briand,L.C. Novelapplicationsofmachinelearninginsoftwaretesting. InProceedingsofthe2008TheEighthInternational
ConferenceonQualitySoftware,Oxford,UK,12–13August2008;pp.3–10.
6. Khaliq,Z.;Farooq,S.U.;Khan,D.A. Artificialintelligenceinsoftwaretesting:Impact,problems,challengesandprospect. arXiv
2022,arXiv:2201.05371.[CrossRef]
7. Talasbek,A. ArtificialAIinTestAutomation:SoftwareTestingopportunitieswithOpenaiTechnology-Chatgpt. SuleymanDemirel
Univ.Bull.Nat.Tech.Sci.2023,62,5–14.
8. Chen,F.K.;Liu,C.H.;You,S.D. UsingLargeLanguageModeltoFillinWebFormstoSupportAutomatedWebApplication
Testing. Information2025,16,102.[CrossRef]
9. Li,T.;Huang,R.;Cui,C.;Towey,D.;Ma,L.;Li,Y.F.;Xia,W. ASurveyonWebApplicationTesting:ADecadeofEvolution. arXiv
2024,arXiv:2412.10476.[CrossRef]
10. Ayenew,H.;Wagaw,M. SoftwareTestCaseGenerationUsingNaturalLanguageProcessing(NLP):ASystematicLiterature
Review. Artif.Intell.Evol.2024,5,1–10.[CrossRef]
11. Dawei, X.; Liqiu, J.; Xinpeng, X.; Yuhang, W. Web applicationautomatic testingsolution. InProceedings ofthe 20163rd
InternationalConferenceonInformationScienceandControlEngineering(ICISCE),Beijing,China,8–10July2016;pp.1183–1187.
12. Gatla,G.;Gatla,K.;Gatla,B.V. CodelessTestAutomationforDevelopmentQA. Am.Sci.Res.J.Eng.Technol.Sci.2023,91,28–35.
13. Jiang,J.;Wang,F.;Shen,J.;Kim,S.;Kim,S. Asurveyonlargelanguagemodelsforcodegeneration. arXiv2024,arXiv:2406.00515.
[CrossRef]
14. Khan,J.A.;Qayyum,S.;Dar,H.S. LargeLanguageModelforRequirementsEngineering:ASystematicLiteratureReview.Res.
Sq.2025.[CrossRef]
15. Zhou,X.;Cao,S.;Sun,X.;Lo,D. Largelanguagemodelforvulnerabilitydetectionandrepair:Literaturereviewandtheroad
ahead. ACMTrans.Softw.Eng.Methodol.2025,34,145.[CrossRef]
16. Leotta,M.;Yousaf,H.Z.;Ricca,F.;Garcia,B.AI-generatedtestscriptsforwebe2etestingwithChatGPTandcopilot:Apreliminary
study. InProceedingsofthe28thInternationalConferenceonEvaluationandAssessmentinSoftwareEngineering,Salerno,Italy,
18–21June2024;pp.339–344.
17. Schäfer, M.; Nadi, S.; Eghbali, A.; Tip, F. Anempiricalevaluationofusinglargelanguagemodelsforautomatedunittest
generation. IEEETrans.Softw.Eng.2023,50,85–105.[CrossRef]
18. Wang,J.;Huang,Y.;Chen,C.;Liu,Z.;Wang,S.;Wang,Q. Softwaretestingwithlargelanguagemodels:Survey,landscape,and
vision. IEEETrans.Softw.Eng.2024,50,911–936.[CrossRef]
19. Deng,G.;Liu,Y.;Mayoral-Vilches,V.;Liu,P.;Li,Y.;Xu,Y.;Zhang,T.;Liu,Y.;Pinzger,M.;Rass,S. {PentestGPT}:Evaluatingand
harnessinglargelanguagemodelsforautomatedpenetrationtesting. InProceedingsofthe33rdUSENIXSecuritySymposium
(USENIXSecurity24),Philadelphia,PA,USA,14–16August2024;pp.847–864.
20. Liu, Z.; Chen, C.; Wang, J.; Chen, M.; Wu, B.; Che, X.; Wang, D.; Wang, Q. Make llm a testing expert: Bringing human-
likeinteractiontomobileguitestingviafunctionality-awaredecisions. InProceedingsoftheIEEE/ACM46thInternational
ConferenceonSoftwareEngineering,Lisbon,Portugal,14–20April2024;pp.1–13.
21. Job,M.A. Automatingandoptimizingsoftwaretestingusingartificialintelligencetechniques. Int. J.Adv. Comput. Sci. Appl.
2021,12.[CrossRef]
22. Wang,F.;Kodur,K.;Micheletti,M.;Cheng,S.W.;Sadasivam,Y.;Hu,Y.;Li,Z. LargeLanguageModelDrivenAutomatedSoftware
ApplicationTesting. TechnicalDisclosureCommons,26March2024.Availableonline:https://www.tdcommons.org/dpubs_series/
6815(accessedon28August2025).
23. Sherifi,B.;Slhoub,K.;Nembhard,F. ThePotentialofLLMsinAutomatingSoftwareTesting: FromGenerationtoReporting.
arXiv2024,arXiv:2501.00217.[CrossRef]
24. Khaliq,Z.;Farooq,S.U.;Khan,D.A. Adeeplearning-basedautomatedframeworkforfunctionalUserInterfacetesting. Inf.Softw.
Technol.2022,150,106969.[CrossRef]
25. Ale, N.K.; Yarram, R. EnhancingTestAutomationwithDeepLearning: Techniques, ChallengesandFutureProspects. In
Proceedings of the CS & IT Conference Proceedings, 8th International Conference on Computer Science and Information
Technology(COMIT2024),Chennai,India,17–18August2024;Volume14.
26. Pei,K.;Cao,Y.;Yang,J.;Jana,S. Deepxplore:Automatedwhiteboxtestingofdeeplearningsystems. InProceedingsofthe26th
SymposiumonOperatingSystemsPrinciples,Shanghai,China,28October2017;pp.1–18.
27. Zimmermann,D.;Koziolek,A. Gui-basedsoftwaretesting:Anautomatedapproachusinggpt-4andseleniumwebdriver. In
Proceedingsofthe202338thIEEE/ACMInternationalConferenceonAutomatedSoftwareEngineeringWorkshops(ASEW),
Luxembourg,11–15November2023;pp.171–174.

## Page 26

Computers2025,14,501 26of26
28. Cavalcanti,A.R.;Accioly,L.;Valença,G.;Nogueira,S.C.;Morais,A.C.;Oliveira,A.;Gomes,S. AutomatingTestDesignUsing
LLM:ResultsfromanEmpiricalStudyonthePublicSector. InProceedingsoftheConferenceonDigitalGovernmentResearch,
PortoAlegre,Brazil,9–12June2025;Volume1.
29. Nass,M.;Alégroth,E.;Feldt,R. Improvingwebelementlocalizationbyusingalargelanguagemodel. Softw.Testing,Verif.Reliab.
2024,34,e1893.[CrossRef]
30. Le,N.K.;Bui,Q.M.;Nguyen,M.N.;Nguyen,H.;Vo,T.;Luu,S.T.;Nomura,S.;Nguyen,M.L. AutomatedWebApplicationTesting:
End-to-EndTestCaseGenerationwithLargeLanguageModelsandScreenTransitionGraphs. arXiv2025,arXiv:2506.02529.
31. Li,T.;Cui,C.;Huang,R.;Towey,D.;Ma,L. LargeLanguageModelsforAutomatedWeb-Form-TestGeneration:AnEmpirical
Study. arXiv2024,arXiv:2405.09965.[CrossRef]
32. Wang,S.;Wang,S.;Fan,Y.;Li,X.;Liu,Y. Leveraginglargevision-languagemodelforbetterautomaticwebGUItesting. In
Proceedingsofthe2024IEEEInternationalConferenceonSoftwareMaintenanceandEvolution(ICSME),Flagstaff,AZ,USA,
6–11October2024;pp.125–137.
33. Garousi,V.;Joy,N.;Keles¸,A.B. AI-poweredtestautomationtools:Asystematicreviewandempiricalevaluation. arXiv2024,
arXiv:2409.00411.[CrossRef]
34. Khankhoje,R. AI-Basedtestautomationforintelligentchatbotsystems. Int.J.Sci.Res.(IJSR)2023,12,1302–1309.[CrossRef]
35. Chapman,C.;Stolee,K.T. ExploringregularexpressionusageandcontextinPython. InProceedingsofthe25thInternational
SymposiumonSoftwareTestingandAnalysis,Saarbrücken,Germany,18–20July2016;pp.282–293.
36. ISO/IEC 25010:2011; Systems and Software Engineering—Systems and Software Quality Requirements and Evaluation
(SQuaRE)—System and Software Quality Models. ISO: Geneva, Switzerland, 2011. Available online: https://www.iso.
org/standard/35733.html(accessedon15September2025).
37. Buse,R.L.;Weimer,W.R. Learningametricforsoftwarereadability. InProceedingsofthe16thACMSIGSOFTInternational
SymposiumonFoundationsofSoftwareEngineering,Atlanta,GA,USA,9–14November2008;pp.100–109.
38. Bondi,A.B. Characteristicsofscalabilityandtheirimpactonperformance. InProceedingsofthe2ndInternationalWorkshopon
SoftwareandPerformance,Ottawa,ON,Canada,17–20September2000;pp.195–203.
39. AndroidDevelopers. UI/ApplicationExerciserMonkey.2025. Availableonline:https://developer.android.com/studio/test/
other-testing-tools/monkey(accessedon25September2025).
40. OpenAI. GPT-4-TurboPricingandTokenUsageDocumentation.2025. Availableonline:https://openai.com/pricing(accessed
on2November2025).
41. ClaudeAPIPricing. Availableonline:https://www.claude.com/pricing#api(accessedon10November2025).
42. xAIAPIModelsandPricing. Availableonline:https://docs.x.ai/docs/models(accessedon10November2025).
43. TheOWASPFoundation. OWASPAppSensorProject.2014. Availableonline:https://owasp.org/www-project-appsensor/
(accessedon5November2025).
44. Rennhard,M.;Kushnir,M.;Favre,O.;Esposito,D.;Zahnd,V. Automatingthedetectionofaccesscontrolvulnerabilitiesinweb
applications. SNComput.Sci.2022,3,376.[CrossRef]
45. Pichiyan,V.; Muthulingam,S.; Sathar,G.; Nalajala,S.; Ch,A.; Das,M.N. Webscrapingusingnaturallanguageprocessing:
Exploitingunstructuredtextfordataextractionandanalysis. ProcediaComput.Sci.2023,230,193–202.[CrossRef]
Disclaimer/Publisher’sNote: Thestatements, opinionsanddatacontainedinallpublicationsaresolelythoseoftheindividual
author(s)andcontributor(s)andnotofMDPIand/ortheeditor(s).MDPIand/ortheeditor(s)disclaimresponsibilityforanyinjuryto
peopleorpropertyresultingfromanyideas,methods,instructionsorproductsreferredtointhecontent.

