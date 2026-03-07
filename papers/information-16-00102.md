# Information-16-00102

**Source:** information-16-00102.pdf  
**Converted:** 2026-01-26 09:23:16

---

## Page 1

Article
Using Large Language Model to Fill in Web Forms to Support
Automated Web Application Testing
Feng-KaiChen1,Chien-HungLiu2 andShingchernD.You2,*
1 Qnap,NewTaipeiCity221,Taiwan;timtim8361@gmail.com
2 DepartmentofComputerScienceandInformationEngineering,NationalTaipeiUniversityofTechnology,
Taipei106,Taiwan;cliu@ntut.edu.tw
* Correspondence:scyou@ntut.edu.tw;Tel.:+886-2-2771-2171(ext.4234)
Abstract: Web applications, widely used by enterprises for business services, require
extensivetestingtoensurefunctionality. Performingformtestingwithrandominputdata
often takes a long time to complete. Previously, we introduced a model for automated
testingofwebapplicationsusingreinforcementlearning.Themodelwastrainedtofillform
fieldswithfixedinputvaluesandclickbuttons. However,theperformanceofthismodel
was limited by a fixed set of input data and the imprecise detection of successful form
submission. Thispaperproposesamodeltoaddresstheselimitations. First,weusealarge
languagemodelwithdatafakerstogenerateawidevarietyofinputdata. Additionally,
whetherformsubmissionissuccessfulispartiallydeterminedbyGPT-4o. Experiments
showthatourmethodincreasesaveragestatementcoverageby2.3%overtheprevious
modeland7.7%to11.9%comparedtoQExplore,highlightingitseffectiveness.
Keywords: largelanguagemodel;prompttuning;webapptesting;webcrawler;GPT-4o
1. Introduction
WiththeriseoftheInternet,manyservicesarenowofferedaswebapplications. Asof
2021,therewere1.88billionwebsites,andapproximately79%ofcompaniesworldwide
havetheirownwebsites[1]. Webapplicationsvarywidelyinstructureandfunctionality,
AcademicEditors:KaushikRoyand
dependingontheirpurposes. Asimplewebpagemightbeasurveywithonlyafewbutton
ValerieL.Shalin
elements,whileahighlycomplexapplicationcouldincluderegistrationforms,multi-step
Received:16December2024
forms,andinteractiveformswithdynamiccontent. Sinceeachwebsiterequirestesting
Revised:18January2025
beforegoingliveandfurthertestingwitheveryupdate,thechallengeofhowtoeffectively
Accepted:31January2025
Published:5February2025 testwebapplicationshasbecomeacriticalissueforthesecompanies.
Broadlyspeaking,webapplicationtestingcanbeperformedmanuallyorautomatically.
Citation: Chen,F.-K.;Liu,C.-H.;You,
S.D.UsingLargeLanguageModelto Manualtestinginvolveshumantestersinteractingwiththewebapplication,suchasfilling
FillinWebFormstoSupport outforms, toidentifypotentialsoftwaredefects. Thesetestersneedextensivesoftware
AutomatedWebApplicationTesting. testing knowledge and a thorough understanding of the application. The advantage
Information2025,16,102. https://
ofmanualtestingisitsabilitytotestspecificscenariosandcatchdetailedissues,suchas
doi.org/10.3390/info16020102
identifyinginvalidinputvaluesforwebforms.However,manualtestingistime-consuming
Copyright:©2025bytheauthors. andcostly,especiallyforlargeandcomplexapplications.
LicenseeMDPI,Basel,Switzerland.
Automatedtesting,ontheotherhand,doesnotrequirehumantesters. Usingweb
Thisarticleisanopenaccessarticle
crawlers,thetestingplatformcanexplorewebapplications,automaticallyfilloutencoun-
distributedunderthetermsand
teredforms,andgeneratevisualstatediagramsforanalysis. Thisapproachreducesthe
conditionsoftheCreativeCommons
Attribution(CCBY)license manual workload, making it especially attractive for large-scale or frequently updated
(https://creativecommons.org/ applications.
licenses/by/4.0/).
Information2025,16,102 https://doi.org/10.3390/info16020102

## Page 2

Information2025,16,102 2of21
However,automatedtestingalsofacessomechallengesduringimplementation.When
webcrawlersencounterformsthatrequireinputvalues, theplatformneedstoprovide
suitableinputvaluesforeachfield. Thereareusuallytwomethodstogeneratetheseinput
values [2]. The first method is to use a “Monkey” approach, which involves randomly
selectingpredefinedinputdata. Thismethodisrelativelysimpleandrequirestestersonly
tosetupasetofinputvalues.However,sincetheMonkeyapproachlacksknowledgeabout
theformfields,itsrandomtrialscanbeextremelyslow. Thesecondmethodinvolvesusing
anagenttoselectinputvalues,eitherpredefinedorartificiallygenerated. Thismethodis
moreefficientbutmuchmoredifficulttoimplement,especiallyinmakingtheagentsmart
enoughtounderstandthecontentofthefieldstobefilled.
Previously,weproposedthemodifiedUsingAgentstoAutomaticallyChooseInput
Data(mUSAGI)model,whichusesreinforcementlearningtotrainanagentforautomated
testing of web applications (cf. Section 3 for a more detailed description) [3]. While
mUSAGIcansuccessfullytestwebapplicationsaftertraining,ithasseverallimitations.
Onelimitationisthatthetypesofinputvaluesarefixedtosixtypes,withonevaluepertype.
Anotherlimitationisthatthedeterminationofwhetheraformissuccessfullysubmitted
reliessolelyonpagecomparisonresults,whichsometimesleadstomisclassification. To
addresstheseissues,wemadethefollowingmodifications:
1. WeuseGoogle’sT5(text-to-texttransfertransformer)model[4]withprompttuning[5,6]
toclassifythecategoryofafield. Then,weuseaMocker[7]togeneratethevalue
forthefield. Thisapproachensuresthattheinputvaluesarenotconfinedtoprede-
finedvalues.
2. Toimprovetheaccuracyofdeterminingwhetheraformissuccessfullysubmitted,
we use GPT-4o [8] to assist in the decision-making process, in addition to page
comparison.
Therestofthepaperisorganizedasfollows. Section2brieflyreviewsrelatedwork.
Section 3 describes the mUSAGI approach. Section 4 details the proposed approach.
Section5coverstheexperimentsandresults. Finally,Section6presentstheconclusionand
futurework.
2. RelatedWork
Wangetal.[9]introducedanefficientmethodforautomaticallygeneratinglinearly
independentpathsinwhite-boxtesting. Theirapproachinvolvestransformingthesource
codeintoastronglyconnectedgraphandthenapplyinganalgorithmtoidentifythese
paths. Pleasenotethatthemethoddiscussedinthispaperdoesnotrequireanyspecific
analysisofthesourcecodepriortotesting.
Malhotraetal.[10]proposedamethodforautomaticallyfillingoutwebformsbasedon
Bayesianinference. Thismethodselectsfieldvaluesbygeneratinginstancetemplatesand
checkingtheirinformativeness. ItusesBayesiannetworksforvalueselectiontoimprove
predictionaccuracyandcomputationalefficiency. Thesetemplatesareappliedtothefilling
of multi-attribute forms. The method was tested using the multi-field search interface
ontheRuneberg.orgwebsite. Experimentalresultsshowthatthismethodoutperforms
theexistingTermFrequency–InverseDocumentFrequency(TF-IDF)methodintermsof
accuracy, discrimination, and computation time. It effectively extracts deep web data,
reducesthenumberofformsubmissions,andimprovestheefficiencyandeffectivenessof
dataretrieval.
Sunmanetal.[11]proposedasemi-automatedmethodandtoolcalledAWET,which
combinesexploratorytesting(ET)withcrawler-basedautomatedtestingforwebapplica-
tiontesting.ThistoolinvolvesmanuallyrecordingasetoftestcasesthroughETbeforehand.
Thesetestcasesarethenusedasabasisforexploringandgeneratingtestcasesfortheweb

## Page 3

Information2025,16,102 3of21
application. ExperimentalresultsshowthatAWETsignificantlyoutperformstheexisting
Crawljax[12]toolintermsoftestcoverageonfivedifferentwebapplications. Additionally,
itcancompletetheexploratorytestrecordingwithin15minandsignificantlyreducethe
overalltestingtime.
Crawljax is a widely utilized crawler that serves as a foundational tool for many
researchers. Forexample, NegardandStroul[13]createdanintuitive,human-readable
scriptinglanguageforCrawljax,designedtodescribeusertestingscenariosandenhance
automatedtesting. Wuetal.[14]expandedthecapabilitiesofCrawljaxbyenablingitto
rememberuserprofilesassociatedwithinputsforfutureuse. Additionally,theyconducted
perturbationonthestoredprofiledatatoassesshowanapplicationundertestcanidentify
illegalinputdata.
Groce[15]utilizedanadaptation-basedprogramming(ABP)approachthatincorpo-
ratesreinforcementlearningtoautomaticallygeneratetestinputs. Thismethodinvolves
callingtheABPlibrarytogeneratetestinputsforaJavaprogramundertest(PUT),aiming
touncovernewbehaviorsofthePUTandoptimizerewardsbasedonincreasedtestcover-
age. Theexperimentalresultsshowthatthisapproachishighlycompetitivecomparedto
randomtestingandshapeabstractiontechniquesfortestingcontainerclasses.
Lin et al. [16] introduced a natural-language method for testing web applications
usingcrawlingtechniques. Thismethodinvolvesextractingandrepresentingtheattributes
ofaDocumentObjectModel(DOM)[17]elementanditsnearbylabelsasavector. This
vector is then converted into a multi-dimensional real-number vector through various
natural-languageprocessingalgorithms,suchasbag-of-words. Byanalyzingthesemantic
similaritybetweenthetrainingcorpusandthetransformedvector,themethodidentifies
aninputtopicfortheDOMelement. Theinputvaluefortheelementisthenselectedfrom
apre-establisheddatabankbasedontheidentifiedtopic. Experimentalresultsindicatethat
thisapproachperformsaswellasorbetterthantraditionalrule-basedtechniques.
Qietal.[18]proposedakeyword-guidedexplorationstrategyfortestingwebpages,
whichachieveshigherfunctionalitycoveragethangenericexplorationstrategies. However,
thisapproachisnotfullyautomatedasitrequiresapredefinedsetofkeywords.
Liuetal.[19]introducedamethodknownasGUIDEfortestingwebapplicationsusing
userdirections. GUIDEpromptstheuserforinputwhenencounteringinputfieldsonweb
pages. TestresultsshowthatGUIDEcandiscovermorecodecomparedtotraditionalweb
crawlers,butitstillreliesonhumaninterventionforprovidinginputs. Thisresearchseeks
toemployreinforcementlearningtotrainanagentthatcanprovideinputsautonomously,
aidingwebcrawlersindiscoveringmorecode.
Carino and Andrews [20] introduced a method for testing application GUIs using
antcolonyoptimization(ACO).Theirapproach,namedAntQ,integratesanantcolony
algorithm with Q-learning. AntQ generates event sequences that navigate through the
GUIsandutilizestheresultingstatechangesasobjectives. Testresultsdemonstratethat
AntQ surpasses random testing and conventional ant colony algorithms in identifying
statementsandfaults.
NguyenandMaag[21]usedasupportvectormachine(SVM)todetectthesearchbar
(orsearchfunction)inwebpagesandperformtestingonthesearchingfunctionalityto
achievethegoalofcodelesstesting. Asawebpagehasawidevarietyofelementsand
functions,theirapproachhasonlylimitedusage.
Kimetal.[22]proposedamethodthatusesreinforcementlearningtoreplacehuman-
designedmetaheuristicalgorithmsinsearch-basedsoftwaretesting(SBST).SBSTalgorithms
seektogenerateoptimaltestdatabasedonfeedbackfromafitnessfunction. Theyusedthe
doubledeepQ-networks(DDQN)algorithmtotrainareinforcementlearningagent. The

## Page 4

Information2025,16,102 4of21
rewardiscomputedbasedonafitnessfunction. Experimentalresultsdemonstratethatthis
approachiseffectivefortrainingfunctionswritteninC.
Zhengetal.[23]introducedWebExplor,anautomatedtestingmethodforwebapplica-
tionsthatusesarewardfunctionanddeterministicfiniteautomaton(DFA)toexplorenew
webpages. TheDFAtracksvisitedstates,andifnonewstatesarefound,WebExplorselects
a path and continues exploring. Tests show that WebExplor identifies more faults and
operatesfasterthannewertechniques.However,itsuseofQ-learning,basedonapplication
states,limitsknowledgetransferbetweendifferentapplications. Incontrast,theapproach
discussedhereemploysreinforcementlearningtoenableknowledgetransferfromone
applicationundertest(AUT)toanother.
Sherin et al. [24] proposed an exploration strategy for dynamic web applications
calledQExplore. InspiredbyQ-learning, thismethodsystematicallyexploresdynamic
webapplicationsbyguidingthesearchprocess,reducingoreliminatingtheneedforprior
knowledgeofthewebapplication. Q-learningisareinforcementlearningmethodthat
learnstheoptimalstrategyinanunknownenvironmentthroughtrial-and-errorinteractions.
QExploreusesarewardfunctiontoguidetheexplorationprocessandconstructsastate
graph during exploration. Experimental results show that QExplore achieves higher
coverage and more diverse DOM states compared to Crawljax and WebExplor. It also
results in more crawl paths, error states, and different DOM states, demonstrating its
superiorperformanceintestingdynamicwebapplications.
Liuetal.[25]presentedareinforcementlearningmethodforworkflow-guidedexplo-
ration,aimedatmitigatingtheoverfittingissuewhentrainingareinforcementlearning(RL)
agentforweb-basedtaskslikebookingflights. Byemulatingexpertdemonstrations,this
methodincorporateshigh-levelworkflowstoconstrainallowableactionsateachtimestep,
therebypruningineffectiveexplorationpaths. Thisenablestheagenttoidentifysparse
rewardsmoreswiftlywhileavoidingoverfitting. Experimentalresultsdemonstratethat
thisapproachachievesahighersuccessrateandsignificantlyenhancessampleefficiency
comparedtoexistingmethods.
Mridha et al. [26] conducted a comprehensive literature review of automated web
testingoverthepastdecade,examining26recentlypublishedpapers. Thereviewedap-
proachesarebroadlycategorizedintomodel-basedandmodel-freestrategies.Inmodel-free
strategies,crawlersaregenerallyemployedtointeractwiththeAUT,executingactionson
encounteredwebpages. Notably,noneofthereviewedpapersincorporatedanylanguage
models.
Liuetal.[27]proposedamethodcalledQTypist,appliedtographicaluserinterface
(GUI)testinginAndroid.Byusingapre-trainedlargelanguagemodeltoautomaticallygen-
eratesemanticinputtext,itenhancesthecoverageandeffectivenessofmobileGUItesting.
ExperimentalresultsshowthatQTypistachievedapassrateof87%on106applications,
whichis93%higherthanthebestbaselinemethod.
3. ReviewofmUSAGIMethod
Figure1providesanoverviewofmUSAGI,integratingthefunctionsofbothacrawler
and an agent. In this model, the crawler is Crawljax (version: v3.7), and the agent is a
feedforwardnetworktrainedusingtheDQNalgorithm[28]. Theoperatingprinciplein-
volvesusingthecrawlertothoroughlyexplorewebapplications,identifyingandcollecting
allinputpages,whicharepagescontainingforms. Thesecollectedinputpagesarethen
passedtotheagentthroughthelearningpool. Theagentinteractswiththeformsavailable
inthelearningpoolandthenpassestheresultsbacktothecrawler. Thisprocessenables
thecrawlertoautomaticallyperformappropriateactionsbasedondifferentinputpages
andconstructadirectivetree.

## Page 5

Information 2025, 16, x FOR PEER REVIEW 5 of 21
Information2025,16,102 5of21
Figure1.TheoverviewofmUSAGI.
Figure 1. The overview of mUSAGI.
ThemUSAGImodelleveragestheopen-sourcecrawlerCrawljaxforinteractingwith
dynaTmheic mwUebSpAaGgeIs m. Aocdceolr ldeivnegrtaogtehse thCer aowplejanx-swoeubrsciete c[r1a2w],l“eCr rCarwalwjalxjacxa nfoerx ipnltoerreaacntiyng with
d(yenveanmsiicn wglee-bppaaggeedsy. nAacmcoicrdJaivnagS ctroi ptth-be aCserda)wwljeabx awpepblisciattei o[n12th],r o“uCgrhawanljaexv ecnatn-d erixvpelnore any
dynamic crawling engine”. Therefore, we believe this tool should be sufficient for our
(even single-page dynamic JavaScript-based) web application through an event-driven
implementation. Infact,itiscommontouseCrawljaxasabuildingblockforconducting
dynamic crawling engine.” Therefore, we believe this tool should be sufficient for our im-
experiments[13,14].
plementation. In fact, it is common to use Crawljax as a building block for conducting
InmUSAGI,theagentistrainedusingareinforcementlearningalgorithm. Unlikethe
experiments [13,14].
RLmodelsreviewedinSection2,whichusethesameAUTfortrainingandtesting,the
In mUSAGI, the agent is trained using a reinforcement learning algorithm. Unlike
mUSAGImodelistrainedononeAUTandtestedondifferentAUTs. Theoverallprocess
thinec lRuLd emstohdreeelsm raeivniestwepesd: cinol lSeectcitoino,nt r2a,i nwinhgi,cahn udstee stthineg s,abmrieefl yAdUeTsc rfoibre dtrabienloinwg. and testing,
the mUSAGI model is trained on one AUT and tested on different AUTs. The overall pro-
1. Collection: In this step, we aim to gather as many input pages as possible. Each
cess includes three main steps: collection, training, and testing, briefly described below.
inputpageservesasanexamplefortheagenttolearnfrom. Whenencounteringan
1. Cionlpluecttpioagne: ,Iwn ethuisse srtaenpd, owmea acitmion tso( gMaothnkeer ya)st omdaenteyr minipnuett hpeavgaelsu eass fpoorsinsipbulte.fi Eeladcsh input
p(aeg.ge. ,sEemrvaeils, Nasa mane ,ePxaasmswpolred f)oarn tdhteh aengecnlitc ktoth leea“rsnu bfmroimt”.b Wutthoenn. encountering an input
2. Training: Usingtheinputpagescollectedinthepreviousstep,wetrainanagentwith
page, we use random actions (Monkey) to determine the values for input fields (e.g.,
reinforcementlearning,definingspecificrewards. Theagent’senvironmentprovides
Email, Name, Password) and then click the “submit” button.
tagsandtextsofthefields. Theactionsinvolveselectingvaluestofillaformfield
2. Training: Using the input pages collected in the previous step, we train an agent with
fromalist. Rewardsarecomputedbasedonwhethertheagentselectsthecorrect
reinforcement learning, defining specific rewards. The agent’s environment provides
actionaccordingtotheexample. ThetrainingalgorithmusedisdeepQ-learning[28].
tags and texts of the fields. The actions involve selecting values to fill a form field
Thetrainedmodelisthenstored.
from a list. Rewards are computed based on whether the agent selects the correct
3. Testing: Inthisstep,weusethetrainedagenttotestanotherwebapplication,referred
atcotioasn tahcecoArUdTin.gT htoe tthraei nexinagmapnlde. tTeshtein tgraaipnpinligca atligonosriathremd uifsfeerde nist ,daelelopw Qin-gleaforrniang [28].
Tcheert tarianilneevdel mofogdeenle irsa ltihzaetnio snt.oIrfetdh.e Istanbulmiddleware[29]supportstheAUT,the
3. Tmesotdinegl:r eInpo trhtissc sotdeep,c wovee ruasgee tahned traadinireedct aivgeetnrte eto. Otetshte arwnoisteh,eorn wlyetbh eapdpirleicctaivtieontr,e reeferred
tois arse pthoret eAdU. T. The training and testing applications are different, allowing for a cer-
tTaihne lsetvrueclt uorfe goefntehreadliizraetcitoivne. tIrfe ethien cIlsutdaensbruolo mtniodddelse,wdairreec t[i2v9e]s ,saunpdpionrptus ttphaeg AesU, T, the
as shmoowdneli nreFpigourtrse c2o.dTeh ceodviereractgivee asnodn ae adcihrepcatitvheo tfrethee. Otretheecrownissiset, oofnalys ethqeu ednicreecotfive tree
actioisn sre(vpaolruteesdfi. lledandbuttonsclicked,etc.) thatenablethecrawlertonavigatefrom
the home page to different target pages. The directive tree can be used to calculate the
The structure of the directive tree includes root nodes, directives, and input pages, as
numberofinputpages,inputpagedepth,andinputpagecoverage(ICI)breadth. Theroot
shown in Figure 2. The directives on each path of the tree consist of a sequence of actions
nodeisavirtualnodethatdoesnotcontainspecificinformationandonlyconnectstothe
(values filled and buttons clicked, etc.) that enable the crawler to navigate from the home
initialpagecrawledbythecrawler. Directivenodesrecordthecurrentusagescenariosand
pcaogrere tsop odnidffienrgenopt etraartgioent speaxgpelosr. eTdhbey dthireeacgtievnet .tDreuer icnagnt hbeec uraswedlin tgo pcraolcceuslsa,tief tthhees anmuember of
ininppuutt ppaaggeesi,s iennpcuout nptaegreed daegpatihn,, tahnedc rianwpluetr pwailglep ecrofvoremraignete (rIaCctIi)v beroepaedrtahti.o Tnhseb arsoeodt onnode is a
vtihrteuaaclt inonodseeq tuheantc edsoienst hneodt irceocntitvaeinn osdpeesc.iIfincp uintfpoargmeantoidoens arencdo rdondleyt aciloendniencfotsr mtoa titohne initial
paabgoeu ctrtahwepleadg ebsy. the crawler. Directive nodes record the current usage scenarios and cor-
responding operations explored by the agent. During the crawling process, if the same
input page is encountered again, the crawler will perform interactive operations based on
the action sequences in the directive nodes. Input page nodes record detailed information
about the pages.

## Page 6

I Innffoorrmmaattiioonn 22002255 , , 1166 , , 1 x 0 F 2 OR PEER REVIEW 6 6 o o f f 2 2 1 1
Figure2.Illustrationofadirectivetree.
Figure 2. Illustration of a directive tree.
ThemUSAGImodelwassuccessfulbuthadsomelimitations,listedasfollows:
The mUSAGI model was successful but had some limitations, listed as follows:
1. Lack of diverse input data: In this model, the actions for filling fields are limited
1. Lack of diverse input data: In this model, the actions for filling fields are limited to
tothefollowingvalues: Email,Number,Password,RandomString,Date,andFull
the following values: Email, Number, Password, Random String, Date, and Full
Name. Withsuchalimitedsetofvalues,othertypesoffieldsmaynotbecorrectly
Name. With such a limited set of values, other types of fields may not be correctly
filled. Thislackofdiversityininputvaluesneedstobeaddressed. Thisisparticularly
filled. This lack of diversity in input values needs to be addressed. This is particularly
importantintestingwebapplications,wherealmosteveryAUTcontainsmultiple
important in testing web applications, where almost every AUT contains multiple
forms. Enhancingthediversityofinputdatacanensurethatsoftwaretestingcovers
forms. Enhancing the diversity of input data can ensure that software testing covers
moreforms,therebyimprovingtheAUT’sreliabilityandstability.
more forms, thereby improving the AUT’s reliability and stability.
2. Long training time: In our previous method, Monkey was used to randomly fill
2. Long training time: In our previous method, Monkey was used to randomly fill form
formfieldsandcollectwebformsfortrainingtheagent. However,theagentinitially
fields and collect web forms for training the agent. However, the agent initially re-
requiresmanyattemptstoguessthecorrectfieldvalue,resultinginconsiderabletime
quires many attempts to guess the correct field value, resulting in considerable time
spentcollectingtrainingsamples(forms). Thispaperproposesadifferentapproachto
spent collecting training samples (forms). This paper proposes a different approach
reducethetrainingtime.
to reduce the training time.
3. Imprecise determination of form submission status. The previous method relied
3. Imprecise determination of form submission status. The previous method relied on
on DOM similarity to determine if a web form was successfully submitted. If the
DOM similarity to determine if a web form was successfully submitted. If the simi-
similaritybetweenthepostsubmissionpageandstoredpageswaslessthan95%,the
larity between the postsubmission page and stored pages was less than 95%, the form
formwasconsideredsuccessfullysubmitted;otherwise,itwasdeemedafailure. The
was considered successfully submitted; otherwise, it was deemed a failure. The
thresholdof95%wasexperimentallydetermined[3]. However,somewebapplica-
threshold of 95% was experimentally determined [3]. However, some web applica-
tionsonlydisplayasmallpieceofconfirmationtextuponsuccessfulsubmission. In
tions only display a small piece of confirmation text upon successful submission. In
suchcases,theoverallDOMsimilarityremainsveryhigh,possiblyover95%,leading
such cases, the overall DOM similarity remains very high, possibly over 95%, leading
tofalsenegativeswheresuccessfulsubmissionsareincorrectlymarkedasfailures.
to false negatives where successful submissions are incorrectly marked as failures.
Thismistakecausestheagenttorepeatedlytestthesamesuccessfulpage,lowering
This mistake causes the agent to repeatedly test the same successful page, lowering
efficiency. Therefore,morereliablemethodsareneededtoaccuratelydetermineform
efficiency. Therefore, more reliable methods are needed to accurately determine form
submissionstatustoimproveefficiency.
submission status to improve efficiency.
4. ProposedApproach
4. Proposed Approach
Figure3providesanoverviewofthemethodproposedinthispaper. Weadoptthe
Figure 3 provides an overview of the method proposed in this paper. We adopt the
samemodularstructureasmUSAGIbutreplacetheagentwithFormAgentandswitch
same modular structure as mUSAGI but replace the agent with FormAgent and switch
fromreinforcementlearningtoalargelanguagemodel(LLM).Thischangeenhancesthe
from reinforcement learning to a large language model (LLM). This change enhances the
system’sflexibilityandefficiency,leveragingtheadvantagesofLLMsinnaturallanguage
system’s flexibility and efficiency, leveraging the advantages of LLMs in natural language
processingtohandlecomplexwebstructuresandinputdata.
processing to handle complex web structures and input data.

## Page 7

Information 2025, 16, x FOR PEER REVIEW 7 of 21
I nformation2025,16,102 7of21
FFiigguurree 33.. TThhee pprrooppoosseedd aapppprrooaacchh.. TThhee sseeccttiioonn ttoo ddeessccrriibbee eeaacchh bbooxx iiss ggiivveenn..
4.1. OverviewofProposedApproach
4.1. Overview of Proposed Approach
FFiirrsstt,, CCrraawwlljjaaxxc crraawwlslst htheew webebp apgaegseusn udnerdteers tt.esDt.u Drinugritnhgis tphriso cpersosc,eCsrsa, wClrjaaxwnljoatxo nnolyt
tornalvye trrsaevsethrseews tehbep wagebes pbaugteasl bsouta anlasloy zaensaalynzderse acnodrd rsetchoerdstsa ttheeo sfteaatech opf eaagcehi npadgeeta iinl. dWethaeinl.
thecrawlingalgorithmdetectsthatallstatesofthewebapplicationhavebeentraversed
When the crawling algorithm detects that all states of the web application have been trav-
andprocessed,Crawljaxsavesallpagescontainingforms(i.e.,inputpages).
ersed and processed, Crawljax saves all pages containing forms (i.e., input pages).
Next, theseinputpagesaresenttoFormAgent. ThemaintaskofFormAgentisto
Next, these input pages are sent to FormAgent. The main task of FormAgent is to
analyzeandprocesstheinputelementswithintheseinputpages. Theseinputelements
analyze and process the input elements within these input pages. These input elements
containrichstructuredinformation,whichiscrucialforthesubsequentclassificationand
contain rich structured information, which is crucial for the subsequent classification and
inputdatagenerationprocess.
input data generation process.
After extracting the input elements from the input pages, FormAgent passes this
After extracting the input elements from the input pages, FormAgent passes this in-
informationtotheValueGenerator.TheValueGeneratorusesthepowerfulnaturallanguage
formation to the ValueGenerator. The ValueGenerator uses the powerful natural language
processingcapabilitiesoftheT5model[4]toclassifytheseinputelements,determiningthe
processing capabilities of the T5 model [4] to classify these input elements, determining
categoryofeachinputelement,suchasemailaddress,phonenumber,etc.Thisclassification
the category of each input element, such as email address, phone number, etc. This classi-
processmakesthesubsequentvaluegenerationeasier.
fication process makes the subsequent value generation easier.
OncetheT5Modelcompletesthetask,thecategoryinformationishandedoverto
Once the T5 Model completes the task, the category information is handed over to
DataFaker,usingtheopen-sourceMocker[7].DataFaker’staskistogenerateanappropriate
DataFaker, using the open-source Mocker [7]. DataFaker’s task is to generate an appropri-
input value based on the category of the field. For instance, for an email address field,
ate input value based on the category of the field. For instance, for an email address field,
DataFakergeneratesacorrectlyformattedemailaddress. Theseautomaticallygenerated
DataFaker generates a correctly formatted email address. These automatically generated
dataarethenusedtointeractwiththeencounteredformandtoconstructaportionofa
data are then used to interact with the encountered form and to construct a portion of a
directive.
directive.
Finally, FormAgent checks these directives to ensure their validity. This includes
Finally, FormAgent checks these directives to ensure their validity. This includes ver-
verifyingwhetherbuttonsareclicked,allinputfieldshavedataentered,andwhetherthe
ifying whether buttons are clicked, all input fields have data entered, and whether the
directivescansuccessfullysubmittheform. Thisvalidationensuresthatthedirectivescan
directives can successfully submit the form. This validation ensures that the directives can
becorrectlyexecutedinpractice.Ifthedirectivesareconfirmedtobevalid,theyarehanded
be correctly executed in practice. If the directives are confirmed to be valid, they are
back to the crawler to further search for deeper input pages, ensuring comprehensive
handed back to the crawler to further search for deeper input pages, ensuring compre-
coverageandtestingofthewebapplication.
hensive coverage and testing of the web application.
4.2. FormAgent
4.2. FormAgent
The FormAgent determines whether a form should be interacted with and if the
The FormAgent determines whether a form should be interacted with and if the en-
encounteredformisnew. Foranewform,theValueGeneratorisused. Forapreviously
countered form is new. For a new form, the ValueGenerator is used. For a previously in-
interactedform,storedvaluesareused. Todetermineifawebpagecontainsaform,we
teracted form, stored values are used. To determine if a webpage contains a form, we scan
scantheentireDOMstructuretoidentifyelementswiththeHTMLtag“input”. Wethen
the entire DOM structure to identify elements with the HTML tag “input.” We then filter

## Page 8

Information2025,16,102 8of21
filteroutelementswhoseparentisa“form”elementtoaccuratelyidentifyformstructures
onthewebpage. Ifoneormorequalifyingelementsarefound,weclassifythepageasan
“inputpage”.
Afterconfirmingawebpageasaninputpage,thesystemcomparesitwiththealready
discoveredinputpagelisttoensureuniquenessandavoidduplicates. Ifnoduplicatesare
found,thepageisaddedtothelist. Duringthecomparisonprocess,specialattentionis
giventovariableelements,whicharedynamicwebelementsthatchangeovertime. These
elementsmustberemovedbeforecomparisontoensureaccuracy.
4.3. ValueGeneratorandPromptTuning
4.3.1. T5Model
Gur et al. investigated how well LLMs understand HTML [30]. They compared
variousmodels,includingBERT[31],LaMDA[32],andT5[4]. ByfinetuningtheT5model
withHTMLdata,theyfoundthatT5excelledintaskssuchasclassifyingHTMLelements,
generatingdescriptions,andnavigatingwebpages. Specifically,theWebC-T5-3Bmodel
achieved90.3%accuracyinthesemanticclassificationofHTMLelements,demonstrating
strong performance. This model was chosen for its excellent performance and lower
resourcerequirements,makingitmorepracticalforreal-worldapplications. Thischoice
underscoresthebalancebetweenmodelperformanceandresourceefficiency.
4.3.2. PredefinedCategories
SinceDataFakerneedstoknowthecategoryoffakedata(valueforfillingonefield)to
begenerated,itisnecessarytoclassifyeachfield’scategory. Tosimplifytraining(prompt
tuning),wecollected75webpagesfrom20websiteslistedonStatista[33]andcountedthe
categoriesofthefieldsonthesewebsites. Table1showssomeresults.
Table1.Thecategoriesextractedfrompopularwebpages.
Category Count Category Count
FirstName 19 Province 1
LastName 20 Region 1
Email 18 Number 25
Gender 1 Country 1
String 32 DisplayName 1
UserName 12 Address 11
FullName 9 Suburb 3
PostalCode 8 CompanyName 1
StoreName 1 CardNumber 1
PhoneNumber 7 ExpirationDate 1
StreetAddress 8 CVV 1
City 5 Date 6
State 1
Inthispaper,inputelementsonwebpagesthatmatchthecategoriesinTable1are
manually labeled. The resultant dataset is then used to prompt-tune the T5 model to
predictcategories(seeSection4.3.3). ThissetupensuresthattheT5modeloutputsonlythe
predefinedcategories,enhancingtheoverallstabilityandreliabilityofthesystem. Ifan
inputelementdoesnotmatchanyofthepredefinedcategories,theT5modelmaychoose
thecategorymostcloselyrelatedtothepredefinedones,asitislimitedtoselectingonly
fromthelist. Therefore,theMockercanstillproducevaluesforformfilling.
NotethatTable1doesnotincludethe“Password”categorybecausepasswordscannot
be randomly generated. Randomly generating passwords could lead to login failures,

## Page 9

Information 2025, 16, x FOR PEER REVIEW 9 of 21
Information 2025, 16, x FOR PEER REVIEW 9 of 21
I nformation2025,16,102 9of21
causing infinite loops or stalls. Therefore, this paper sets a fixed password to ensure
ccaauussiinnggi ninfifinnitietelo looposposr ostra lsltsa.lTlsh. eTrehfeorreef,otrhei,s tphaips epraspetesra sfiextse da pfiaxseswd opradstsoweonrsdu rteos menosoutrhe
smooth login and operation of the web application during testing and tuning.
lsomgionoathn dloogpine raantido nopoefrtahteiown eobf athpep wliceabti aopnpdliucraitniognt edsutirnignga ntedsttiunngi nagn.d tuning.
4.3.3. ValueGenerator and Prompt Tuning of T5 Model
44..33..33.. VVaalluueeGGeenneerraattoorr aanndd PPrroommppttT Tuunnininggo offT T55M Mooddeell
In this section, we will explain how to perform prompt tuning on the T5 model. First,
IInn tthhiiss sseeccttiioonn,, wwee wwilil lelxepxlpaliani nhohwo wto ptoerpfoerrmfo rpmropmrpotm tupntitnugn oinng thoen Tt5h me oTd5eml. Foidrestl.,
we used the forms mentioned in Section 4.3.2 as the training data source. For each form’s
Fwires tu,swede tuhsee dfotrhmesf omremnstimoneendti ionn SeedcitnioSne 4c.t3io.2n a4s. 3th.2e atrsatihneintgra dinaitnag soduartcaes. oFuorrc eea.cFho rfoeramch’s
input elements, we extracted necessary information such as labels, placeholders, and
fionrpmu’ts einlepmuetnetlse,m ween tesx,twraecetexdtr ancetceedssnaercye sisnafroyrminaftoiormn astuiochn sausc lhabaesllsa, bpellasc,ephlaocldeherosl,d aenrsd,
names. This information serves as the basis for classification. We then manually defined
annadmnesa.m Tehsi.s iTnhfoisrminaftoiromn asteirovness earsv tehsea bsatshise fboar scilsasfosirficclaatsiosinfi. cWateio tnh.enW meatnhuenallmy adneufianlelyd
categories for each input element based on this information, ultimately generating a struc-
dceafitengeodriceast efogro eriaecshf oinrpeuatc heleinmpeuntte bleamseedn otnb atsheids ionnfotrhmisaitniofonr,m ulattiimona,teullyt igmeanteerlaytignegn ear sattriuncg-
tured JavaScript Object Notation (JSON) file, as shown in Figure 4.
atusrtreudc JtauvreadScJraivpat SOcbrijpecttO NbojetcattiNono t(aJStiOonN()J SfiOleN, a)sfi slhe,oawsns hino wFinguinreF 4ig. ure4.
Figure 4. The JSON file for prompt tuning.
FFiigguurree 44.. TThhee JJSSOONN fifillee ffoorr pprroommpptt ttuunniinngg..
After obtaining the pre-trained LLM, it is necessary to adapt the model to predict the
AAfftteerr oobbttaaiinniinngg tthhee pprree--ttrraaiinneedd LLLLMM,, iitt iiss nneecceessssaarryy ttoo aaddaapptt tthhee mmooddeell ttoo pprreeddiicctt tthhee
defined categories. To achieve this, we can use either fine tuning or prompt tuning. Fine
ddeefifinneedd ccaatteeggoorriieess.. TToo aacchhiieevvee tthhiiss,, wwee ccaann uussee eeiitthheerr fifinnee ttuunniinngg oorr pprroommpptt ttuunniinngg.. FFiinnee
tuning involves modifying the language model’s parameters by using a specific dataset to
ttuunniinngg iinnvvoollvveess mmooddiiffyyiinngg tthhee llaanngguuaaggee mmooddeell’’ss ppaarraammeetteerrssb byy uussiinngg aa ssppeecciifificc ddaattaasseett ttoo
adjust its internal weights. This precise adjustment enables the model to tailor its outputs,
aaddjjuusstt iittss iinntteerrnnaall wweeiigghhttss.. TThhiiss pprreecciissee aaddjjuussttmmeenntt eennaabblleess tthhee mmooddeell ttoo ttaaiilloorr iittss oouuttppuuttss,,
making them suitable for a particular application. However, there are some downsides to
mmaakkiinngg tthheemm ssuuiittaabbllee ffoorr aa ppaarrttiiccuullaarr aapppplliiccaattiioonn.. HHoowweevveerr,, tthheerree aarree ssoommee ddoowwnnssiiddeess ttoo
using fine tuning.
uussiinngg fifinnee ttuunniinngg..
First, as fine tuning essentially involves training, all the weights in the pre-trained
FFiirrsstt,, aass fifinnee ttuunniinngg eesssseennttiiaallllyy iinnvvoollvveess ttrraaiinniinngg,, aallll tthhee wweeiigghhttss iinn tthhee pprree--ttrraaiinneedd
model need to be adjusted, as shown on the left side of Figure 5. This leads to longer
mmooddeell nneeeedd ttoo bbee aaddjjuusstteedd,, aass sshhoowwnn oonn tthhee lleefftt ssiiddee ooff FFigiguurree 55.. TThhiiss lleeaaddss ttoo lloonnggeerr
training times and higher computing costs [34]. Second, the fine-tuning process must use
ttrraaiinniinngg ttiimmeess aanndd hhiigghheerr ccoommppuutitningg cocostsst s[3[43]4. ]S.eScoencodn, dth,et hfienefi-ntuen-tiunngi npgropcerossc emssusmt uusste
a lower learning rate to avoid overwriting the pre-learned features too quickly [35]; oth-
uas leowaleorw leearrlneianrgn irnagte rtaot eavtooiadv ooviderowvreirtwinrgi ttihneg pthree-lperaer-nleeadr nfeeadtufreeast utoreos qtuooickqluyi c[k35ly]; [o3t5h]-;
erwise, catastrophic forgetting might occur. Additionally, fine-tuned models tend to be
oetrhweirswe,i scea,tcaasttarsotprohpich ifcorfgoergtteinttgin mgmigihgth otcoccucru. rA. Adddditiitoionnalallyly, ,fifinnee--ttuunneedd mmooddeellss tteenndd ttoo bbee
less robust, as the model is retrained to be tailored to a specific application.
lleessss rroobbuusstt,, aass tthhee mmooddeell iiss rreettrraaiinneeddt toob beet taailiolorreeddt tooa as sppeeccifiificca apppplilcicaatitoionn..
FFigiguurree 55. .DDiffifefererennccee bbeetwtweeeenn mmooddeel lfifinnee ttuunniningg ((leleftf)t )aanndd pprorommppt ttutunniningg (r(rigighht)t.) .TThhee slsalasshh lilninee wwitihth
aar F rri orgow uwr i e ni n5 dd. i ciDcaai t ff etes es r ( e fi(fin nnc e ee) )b tuteut n wninieng eg n oo f m fppo aad rra eam lm fi e nette eer trs us ( n(wwin eeg igi g( h lhe tts fs) t). ) . and prompt tuning (right). The slash line with
arrow indicates (fine) tuning of parameters (weights).

## Page 10

Information 2025, 16, x FOR PEER REVIEW 10 of 21
Information2025,16,102 10of21
Prompt tuning [5] is a technique that allows LLMs to generalize more easily to down-
Prompttuning[5]isatechniquethatallowsLLMstogeneralizemoreeasilytodown-
stream tasks, as shown on the right side of Figure 5. Unlike fine tuning, prompt tuning
streamtasks,asshownontherightsideofFigure5. Unlikefinetuning,prompttuning
freezes the parameters of the pre-trained model and trains a small model in front of it.
freezestheparametersofthepre-trainedmodelandtrainsasmallmodelinfrontofit. This
This approach significantly reduces the number of trainable parameters for each down-
approachsignificantlyreducesthenumberoftrainableparametersforeachdownstream
stream task, thereby lowering computing costs. Additionally, there are open-source tools
task,therebyloweringcomputingcosts. Additionally,thereareopen-sourcetoolsavailable
available for prompt tuning [6]. Consequently, we utilize this technique in our implemen-
for prompt tuning [6]. Consequently, we utilize this technique in our implementation.
tation. Essentially, the ValueGenerator in Figure 3 represents this part of the model.
Essentially,theValueGeneratorinFigure3representsthispartofthemodel.
In our implementation, prompt tuning is accomplished using Open Prompt [6]. This
Inourimplementation,prompttuningisaccomplishedusingOpenPrompt[6]. This
framework is designed to simplify and facilitate prompt engineering for natural language
frameworkisdesignedtosimplifyandfacilitatepromptengineeringfornaturallanguage
processing tasks. Open Prompt includes the following components:
processingtasks. OpenPromptincludesthefollowingcomponents:
1. Template: A key element of learning, it provides prompts by wrapping the original
1. Template: Akeyelementoflearning,itprovidespromptsbywrappingtheoriginal
text in text or software-encoded templates, usually containing context markers.
textintextorsoftware-encodedtemplates,usuallycontainingcontextmarkers.
2. PromptModel: This component is used for training and inference. It includes a Pre-
2. PromptModel: Thiscomponentisusedfortrainingandinference. ItincludesaPre-
trained Language Model (PLM), a Template object, and an optional Verbalizer object.
trainedLanguageModel(PLM),aTemplateobject,andanoptionalVerbalizerobject.
Users can combine these modules flexibly and design their interactions. The main
Userscancombinethesemodulesflexiblyanddesigntheirinteractions.Themaingoal
goal is to allow training through a unified API without needing specific implemen-
istoallowtrainingthroughaunifiedAPIwithoutneedingspecificimplementations
tations for different PLMs, enabling more flexible usage.
fordifferentPLMs,enablingmoreflexibleusage.
3. PromptDataset: This component is used to load training data.
3. PromptDataset: Thiscomponentisusedtoloadtrainingdata.
During the prompt-tuning phase, we used the prompts shown in Figure 6 with Open
Duringtheprompt-tuningphase,weusedthepromptsshowninFigure6withOpen
Prompt. The prompts include keywords such as placeholder, text_a, soft, and mask. The
Prompt. Thepromptsincludekeywordssuchasplaceholder,text_a,soft,andmask. The
placeholder allows dynamic insertion of required data into the prompt, making it flexible
placeholderallowsdynamicinsertionofrequireddataintotheprompt,makingitflexible
to adjust the model’s input content. Text_a is the name specified when inserting data into
toadjustthemodel’sinputcontent. Text_aisthenamespecifiedwheninsertingdatainto
the program, helping to identify and replace text at specific positions. Soft indicates a soft
the program, helping to identify and replace text at specific positions. Soft indicates a
prompt, followed by text intended to initialize the soft prompt, allowing the model to start
softprompt,followedbytextintendedtoinitializethesoftprompt,allowingthemodelto
learning from meaningful text rather than random vectors. This initialization strategy en-
startlearningfrommeaningfultextratherthanrandomvectors. Thisinitializationstrategy
ables quicker convergence to the (sub)optimal state. After tuning, the model is used to
enablesquickerconvergencetothe(sub)optimalstate. Aftertuning,themodelisusedto
determine the categories of input fields.
determinethecategoriesofinputfields.
FFiigguurree 66.. TThhee uusseedd pprroommpptt ttoo OOppeenn PPrroommpptt..
4.3.4. DataFaker
4.3.4. DataFaker
The DataFaker block utilizes the mocker-data-generator tool, which simplifies the
The DataFaker block utilizes the mocker-data-generator tool, which simplifies the
creationoflargeamountsofmockdata[7]. Itemploysschema-basedfakedatagenerators
creation of large amounts of mock data [7]. It employs schema-based fake data generators
likeFakerJs,ChanceJs,CasualJs,andRandExpJstoproducetestdata. Thistoolsupports
like FakerJs, ChanceJs, CasualJs, and RandExpJs to produce test data. This tool supports
TypeScripttypesandcangeneratediversedatatomeetvarioustestingneeds. Userscan
TypeScript types and can generate diverse data to meet various testing needs. Users can
customizedatamodelsandcombinemultiplefakedatageneratorstocreatecomplexdata
customize data models and combine multiple fake data generators to create complex data
structures. Experimentalresultsshowthatthistoolcanefficientlygeneratelargeamounts
structures. Experimental results show that this tool can efficiently generate large amounts
ofdata,aidingindatasimulationduringdevelopmentandtestingprocesses.
of data, aiding in data simulation during development and testing processes.
4.4. SubmitButtonChecker
4.4. Submit Button Checker
In our previous work, one action was to “click” buttons. Through reinforcement
In our previous work, one action was to “click” buttons. Through reinforcement learn-
learning, the agent learned when to click a submit button. In the current model, since
ing, the agent learned when to click a submit button. In the current model, since reinforce-
reinforcement learning has been removed, determining whether the currently focused
ment learning has been removed, determining whether the currently focused component is
componentisasubmitbuttonbecomesanissue. Crawljaxgeneratesformtasksinatop-
a submit button becomes an issue. Crawljax generates form tasks in a top-down manner
downmanneraccordingtotheHTMLstructure. Withoutspecialarrangement,theform

## Page 11

Information 2025, 16, x FOR PEER REVIEW 11 of 21
Information 2025, 16, x FOR PEER REVIEW 11 of 21
Information2025,16,102 11of21
according to the HTML structure. Without special arrangement, the form agent will sequen-
tially click button components from top to bottom after completing the form filling.
according to the HTML structure. Without special arrangement, the form agent will sequen-
agentInw silolmseeq wueenbt iaapllpylicclaictkiobnus,t ttohne cfiormst pbountteonnts cformompotnopentto ibs ontotot mthea fsteurbcmoimt bpuletttionng. tFhoer
tially click button components from top to bottom after completing the form filling.
feoxrammfiplllein, Fgi.gure 7 shows a form in the KeystoneJS web application. In Figure 7, there are
In some web applications, the first button component is not the submit button. For
threeI nbusottmone wcoembpaopnpelnictas:t iConresa,tteh,e Cfiarnscteblu, tatnodn Ccolomspe oWneinndtoiswn. oHtothweesvuebr,m thiteb “uxtt”o bnu.ttFoonr
example, Figure 7 shows a form in the KeystoneJS web application. In Figure 7, there are
e(cxlaomsep lwe,inFdigouwre in7 sthhoe wtospa-rfiogrhmt cinortnheer)K aepypsteoanres JSatw theeb taoppp.l iTchateiroenfo.rIen, Fifi gtuhree a7g,etnhte rceliacrkes
three button components: Create, Cancel, and Close Window. However, the “x” button
tbhurtteeonbsu tftroonmc toomp ptoo nbeontttos:mC, riet awteo,uClda ncclieclk, athned cClolosese wWininddowow b.uHttoown eavfteerr, cthoem“pxl”etbinugt ttohne
(close window in the top-right corner) appears at the top. Therefore, if the agent clicks
(fcolromse fiwlliinndg.o Cwloinsinthge thtoisp f-orirgmh tcacoursnese ra) saipgpneifiacrasnatt cthhaentgoep i.nT thheer secfroereen,,i fletahdeinagge tnhte calgiceknst
buttons from top to bottom, it would click the close window button after completing the
btou tmtoinstsafkreonmlyt ojupdtgoeb tohtet ofmor,mit aws osuulcdcecsliscfkultlhye sculbomseittweidn,d wowhilbeu itnto rneaalfitteyr, cito hmaps lnetoitn gbetehne.
form filling. Closing this form causes a significant change in the screen, leading the agent
fTohrme mfielltihnogd. Cfolor sdinegtetrhmisinfoinrgm wcahuesthesera tshieg nfoifircma nstucbhmanisgseioinn itsh esuscccreesesnf,ulle acadnin bget hfoeuangde nint
to mistakenly judge the form as successfully submitted, while in reality, it has not been.
tSoecmtiiosnta 4k.e5n. lyjudgetheformassuccessfullysubmitted,whileinreality,ithasnotbeen.
The method for determining whether the form submission is successful can be found in
Themethodfordeterminingwhethertheformsubmissionissuccessfulcanbefoundin
Section 4.5.
Section4.5.
Figure 7. A form with three buttons.
Figure7.Aformwiththreebuttons.
Figure 7. A form with three buttons.
To solve this problem, the proposed model uses GPT-4o [8] for support. Our method
integTroatseosl vtheet hfoisrmpr oeblelmemen,tth aenpdr tohpeo cseudrrmenotdlye lfoucsuesseGdP tTar-4goet[ 8e]lefmoresnut pinptoor to.uOru prrmometphto tdo
To solve this problem, the proposed model uses GPT-4o [8] for support. Our method
iqnuteegryra GtePsTt-h4eof. oSrpmeceifilecmalelyn,t waned utshee ac suyrsrteenmtl yprfoomcupste dtot agrugiedtee GlePmTe-4not ionnto hoouwr tpor oremsppotntod
integrates the form element and the currently focused target element into our prompt to
qaunedr ythGe ProTl-e4 oit. sShpoeuclidfi caaslsluy,mwee, auss eshaoswynst bemelopwro: mpttoguideGPT-4oonhowtorespond
query GPT-4o. Specifically, we use a system prompt to guide GPT-4o on how to respond
andtheroleitshouldassume,asshownbelow:
and the role it should assume, as shown below:
You are an AI web crawler assistant.
YouareanAIwebcrawlerassistant.
The user will give you some web elements.
YTohue aursee ranw AillI gwiveeb ycorauwsloemr aeswsisetbanelte. ments.
Please answer if it is a form submission button.
The user will give you some web elements.
Pleaseanswerifitisaformsubmissionbutton.
Please say only yes or no.
Please answer if it is a form submission button.
Pleasesayonlyyesorno.
Please say only yes or no.
After that, the web elements containing the button information are provided to GPT-
Afterthat,thewebelementscontainingthebuttoninformationareprovidedtoGPT-
4o, as shown in Figure 8. This way, whether the button is a submission button can be
4o, aAsfstehro twhant,i nthFe iwguerbe e8le.mTehnitss wcoanyt,awinhinetgh tehret bhuettbount tionnfoirsmaastiuobnm airses piornovbiudtetdo ntoc GanPTb-e
determined.
4doe, taesrm shinoewdn. in Figure 8. This way, whether the button is a submission button can be
determined.
FFiigguurree 88.. TThhee wweebb eelleemmeennttss sseenntt ttoo GGPPTT--44oo ffoorr ddeecciissiioonn..
F4i.g5u.rDe e8t. eTrhmei nwaetbio enleomfSenutcsc essesnftu tloS GuPbmT-i4sosi foonr decision.
4.5. Determination of Successful Submission
Whentestingwebapplications,itiscrucialtodetermineifasubmissionissuccessful.If
4.5. DeWtehrmenin taetsitoinn gof w Seubcc aepsspfulilc Satuibomnsis, siito ins crucial to determine if a submission is successful.
thesubmissionfails,theapplicationtypicallyreturnstoapreviouslydisplayedpage. From
If the submission fails, the application typically returns to a previously displayed page.
asofWtwhaerne tteessttiinngg wpeebrs appepcltiicvaet,iothnes, ciot dise crtoucrieanl dtoe rdtehteartmpiangee ifh aa ssuablrmeaisdsyiobne iesn suexccaemssinfueld. .
From a software testing perspective, the code to render that page has already been exam-
ITf htheere sfuorbem,tiesssitoinng fanielsw, tphaeg aepspisliacalwtioany stydpeisciarallbyl er.etIufrthnes stou bam pirsesvioionufsaliyl sd,itshpelateysetdin pgatgoeo.l
ined. Therefore, testing new pages is always desirable. If the submission fails, the testing
Fwroilmla att seomftpwtatorefi tlelsotiuntgt hpeerssapmecetifvoer,m thaeg caoind,eu tosi nregnddiefrfe trheantt pvaagleu ehsaos ralcrleicakdiyn gbeaedni effxearmen-t
tool will attempt to fill out the same form again, using different values or clicking a
ibnuedtt.o Tnh.eCroefnovreer, steelsyt,inifgt hneewsu pbmagiesss iiosn ailswsauycsc edsessfiurla,balen. eIwf thpea gseubwmililsaspiopne afar,ilasn, tdhae pteosrttiniogn
toofonl ewwilcl oadtteewmipllt bteo tfiesllt eodu.t the same form again, using different values or clicking a

## Page 12

Information2025,16,102 12of21
Todetermineifasubmissionissuccessful,onepossiblemethodistocheckthecode
coverage. However, the tool used to measure code coverage is language-dependent,
meaningdifferentprogramminglanguagesrequiredifferenttools.Forexample,theIstanbul
middlewarecanmeasurecodecoverageforES5andES2015+JavaScriptcodebutnotfor
otherlanguageslikePHPorPython. TocomputethecoverageofPHPcode,adifferenttool
mustbeused. Thissituationisundesirableasitcomplicatesthetestingplatform,makingit
difficulttoaccommodateapplicationswrittenindifferentlanguages.
Inourpreviousmodel(mUSAGI),weusedanalternativeapproach. Weemployeda
pagecomparisonalgorithmtodetermineifthepagethatappearedafterclickingthesubmit
buttonwassimilartoanypreviouslyencounteredpages. Ifthesimilarityscorewaslower
thanathreshold,itindicatedanewpagehadbeenencountered. Thispagewasthenstored,
andthesubmissionwasdeemedsuccessful. Otherwise,thesubmissionwasconsidered
unsuccessful,andthepagewasnotstored. Foradetaileddescriptionofthismethod,please
referto[3].
Inthepreviousmodel,thetag,class,andtextelementsintheDOMstructurewere
extracted for comparison, and the similarity threshold was set to 95%, resulting in the
highestclassificationaccuracy. Thougheffective,thismethodsometimesfails,especially
whenthescreenonlyshowsasinglelineoftextindicatingthesuccessofthesubmission.
AsshowninFigure9,aftertheformissuccessfullysubmitted,thescreenonlydisplays
asmallsegmentoftextwithagreenbackground,indicatingtotheuserthattheformwas
successfullyfilledout. Duetotheseverysubtlechanges, thesimilarityscoreisusually
above95%.Thismeansthatwhentheformissuccessfullysubmitted,thesimilarityremains
high. Therefore,suchhighsimilaritycannoteffectivelydistinguishwhethertheformwas
successfullysubmitted.
Figure9.Awebpageaftersuccessfulsubmissionwithminorchangetopagecontents.

## Page 13

Information2025,16,102 13of21
ThispaperproposesanewmethodthatusestheGPT-4omodeltoassistindetermining
whetheraformhasbeensuccessfullysubmitted. Tosavetimeandbudget,asGPT-4oisa
paidservice,themodelisonlyutilizedifthesimilarityscoreexceeds95%.
Intheoriginalpagecomparisonalgorithm,theDOMelements(tag,class,andtext)of
bothpagesarecompared. TouseGPT-4o,thedifferingpartsofthestringsarethensentto
GPT-4o,andthroughthesystemprompt,thepossibleanswersarerestrictedto“Yes”or
“No”. ThisallowsforacleardeterminationbasedonGPT-4o’sresponse. Thealgorithmfor
thispartisgiveninAlgorithm1.
Algorithm1Determinationwhetheradirectiveiseffective.
Algorithm1: Isdirectiveeffective
Input: PagebeforeSubmitPage,PageafterSubmitPage
Output: BooleanisSimilar
1: begin
2: similarity←calculatePagesSimilarity(beforeSubmitDom,afterSubmitDom)
3: ifsimilarity==100then
4: returnfalse
5: endif
6: ifsimilarity>=95then
7: beforeSubmitElements←getElements(beforeSubmitPage)
8: afterSubmitElements←getElements(afterSubmitPage)
9: isSimilar←getGptAnswer(beforeSubmitElements,afterSubmitElements)
10: returnisSimilar
11: endif
12: returntrue
13: end
14
15: proceduregetGptAnswer(beforeSubmitElements,afterSubmitElements)
16: begin
17: differentElements←getDiffElements(beforeSubmitElements,
afterSubmitElements)
18: answer←openAiApi(differentElements)
19: ifanswer==“yes”then
20: returntrue
21: elseifanswer==“no”then
22: returnfalse
23: endif
24: end
5. ExperimentsandResults
Thissectioncoverstheexperimentalenvironment,performancemetrics,experiments,
andresults. Threeexperimentswereconductedforevaluation. Thefirstexperimentevalu-
atestheusefulnessofusinganLLM(andDataFaker)tofillforms. Thesecondexperiment
assessestheeffectivenessoftheproposedapproachindetecting“click”buttonsandsuc-
cessful submissions. The third experiment compares the performance of the proposed
approachwithothermethods. Finally,thereisasubsectiondiscussingthreatstovalidity
andanotheroneforfuturework.

## Page 14

Information2025,16,102 14of21
5.1. ExperimentalEnvironment
ThereareseveralconsiderationsforchoosingAUTs. Thisresearchfocusesonlever-
agingLLMstoautomatewebformfilling,therebyfacilitatingwebpageexplorationand
testing. Toavoidinterveningincommercialwebsites,ourAUTsarelimitedtoopen-source
web applications with rich web forms. Additionally, to ease the comparison of code
coveragewithothermethods,wechosesomewebapplicationsdevelopedwithspecific
server-sidetechnologies,suchasNode.js. Furthermore,wehavepreviouslyusedsome
AUTs,andtosaveontheinitialsetuptime,wedecidedtocontinueusingtheseAUTs.
Theexperimentswereconductedthroughcomputersimulations,withthehardware
specificationslistedinTable2. TheAUTsundertestareasfollows: TimeOff.Management
(TimeOff) [36], NodeBB [37], KeystoneJS [38], Django Blog (Django) [39], and Spring
Petclinic(Petclinic)[40],detailedinTable3. AmongtheAUTs,thefirstthreearewrittenin
Node.js,allowingustoobtaincodecoveragewithIstanbulmiddleware[29]. However,the
IstanbulmiddlewarecannotcomputethecodecoverageforDjangoBlog(writteninPython)
andSpringPetclinic(writteninJava). Weusethesetwoapplicationstodemonstratethat
othermetricscanalsobeusedtoassesstherelativeperformanceofvariousautomated
testingplatforms.
Table2.Listofexperimentalhardwarespecificationsandsoftwareversions.
Hardware/Software Specifications/Model/Version
CPU IntelXeonW-22353.80GHz
RAM 32GBDDR4
OS Ubuntu20.04
GPU NVIDIAGeForceRTX20708GBGDDR6
Selenium 3.141.0
Crawljax 3.7
Python Version: 3.7
Table3.ListofAUTs.
ApplicationName Version GitHubStarsCount LinesofCode Type
Attendance
TimeOff.Management
V0.10.0 921 2698 Management
[36]
System
NodeBB[37] V1.12.2 14k 7334 OnlineForum
KeystoneJS[38] V4.0.0-beta.5 1.1k 5267 BloggingSoftware
DjangoBlog[39] V1.0.0 26 - BloggingSoftware
VeterinaryClient
SpringPetclinic[40] V2.6.0 22.9k - Management
System
Duringtesting,thetestingengineerneedstodownloadtheAUTtothelocalcomputer.
Testinganonlinesiteisnotappropriate,asthebehaviorofthecrawlerresemblesacyber-
attack. IfIstanbulisabletomeasurethecodecoverageoftheAUT,itshouldalsobeplaced
inthesamefolderastheAUT.Then,theprogramsarewrappedbyDocker. IftheAUT
requiresspecificvaluesforcertainfields, suchasauserIDandpassword, thesevalues
canbespecifiedintheproposedmodel,alongwiththepathtotheDockercontainingthe
AUT.Oncepreparationiscomplete,executetheproposedmodelforautomatedtesting.

## Page 15

Information2025,16,102 15of21
Afterthemodelcannotfindanymorenewpages,thetestingengineercanstopthemodel
andobtainthestategraph(directivetree)fromCrawljaxtocomputetheproposedmetrics.
Alternatively,ifthecodecoverageinformationisavailable,itcanbeaccessedviaabrowser
connectedtotheAUT.
5.2. PerformanceMetrics
Thefollowingitemsareusedtomeasuretheperformanceofvarioustestingmethods:
1. Codecoverage. AccordingtoBraderetal.,“Lowcoveragemeansthatsomeofthe
logic of the code has not been tested. High coverage...nevertheless indicates that
the likelihood of correct processing is good” [41]. Therefore, a method achieving
a higher percentage of code coverage is considered better. There are two types of
codecoverage: statementcoverageandbranchcoverage. Intheexperiments,only
statementcoverageisreported,asthesetwoarehighlycorrelated. Thechoiceofa
codecoveragetoolisdependentontheprogramminglanguageinuse,asmentioned
Information 2025, 16, x FOR PEER REVIEW inSection4.5. Tosupplementthecodecoveragemetric,weintroducethreeadd1it5i oonf a2l1
metrics: the number of input pages, input page depth, and ICI breadth, detailed
below.
2
2
.
.
N
N
u
u
m
m
b
b
e
e
r
r
o
o
f
f
i
i
n
n
p
p
u
u
t
t
p
p
a
a
g
g
e
e
s
s
.
.
T
T
h
h
i
i
s
s
v
v
a
a
l
l
u
u
e
e
i
i
s
s
t
t
h
h
e
e
n
n
u
u
m
m
b
b
e
e
r
r
o
o
f
f
f
f
o
o
r
r
m
m
s
s
f
f
o
o
u
u
n
n
d
d
b
b
y
y
a
a
n
n
a
a
p
p
p
p
r
r
o
o
a
a
c
c
h
h
.
.
I
I
n
n
thedirectivetreeshowninFigure10,inputpagesarerepresentedbybluenodes. As
the directive tree shown in Figure 10, input pages are represented by blue nodes. As
Figure9hasfourbluenodes,thenumberofinputpagesinthisdirectivetreeis4.
Figure 9 has four blue nodes, the number of input pages in this directive tree is 4.
3
3
.
.
I
I
n
n
p
p
u
u
t
t
p
p
a
a
g
g
e
e
d
d
e
e
p
p
t
t
h
h
.
.
T
T
h
h
i
i
s
s
i
i
s
s
t
t
h
h
e
e
n
n
u
u
m
m
b
b
e
e
r
r
o
o
f
f
n
n
o
o
d
d
e
e
s
s
o
o
n
n
t
t
h
h
e
e
l
l
o
o
n
n
g
g
e
e
s
s
t
t
p
p
a
a
t
t
h
h
f
f
r
r
o
o
m
m
t
t
h
h
e
e
r
r
o
o
o
o
t
t
n
n
o
o
d
d
e
e
tothedeepestinputpagenode. InFigure10,thelongestpathisfromtherootnode
to the deepest input page node. In Figure 10, the longest path is from the root node
throughdirectivenode(markedasaredcircle)withID77eb5790tothefinalinput
through directive node (marked as a red circle) with ID 77eb5790 to the final input
pagewithID1068395108. Therefore,thedepthofthistreeis2. Thisvalueisusedto
page with ID 1068395108. Therefore, the depth of this tree is 2. This value is used to
measurethecapabilityofanapproachtoexploreformshiddendeeplywithintheweb
measure the capability of an approach to explore forms hidden deeply within the
application.
web application.
4. ICI breadth. This is the number of input nodes containing extensions to directive
4. ICI breadth. This is the number of input nodes containing extensions to directive
nodes. AccordingtoFigure10,therearethreeinputpagenodes,eachconnectingto
nodes. According to Figure 10, there are three input page nodes, each connecting to
directivenodes,sotheICIbreadthinthisexampleis3. ICIbreadthcanbeusedto
directive nodes, so the ICI breadth in this example is 3. ICI breadth can be used to
countthenumberofformssuccessfullysubmitted. Inmostcases,thismetricishighly
count the number of forms successfully submitted. In most cases, this metric is highly
correlatedwiththenumberofinputpages.
correlated with the number of input pages.
FFiigguurree1 100..A Ad diirreeccttiviveet trreeee..
AAnn iinnppuutt nnooddee wwiitthh aa lalarrggeerr ICICI Ibrberaedatdht hsusguggegsetss ttshatht athtet hinepiuntp puatgpea mgeaym laeyadl etaod a
tgoreaagterre antuemr nbuerm obf esrubosfesquubesnetq iunepnutt ipnapguets,p aalgl eosf ,wahllicohf swhohuiclhd bshe oeuxlpdlobreede xanpdlo treesdteadn. dA
tmesoterde .eAffemctoivree ecfrfaewctlievre schroauwldle rgsehnoerualtde gdeinveerrasete indpivuetrss teoi nepxpultosrteo aesx mplaonrey ainspmuatn pyaignepsu ats
ppaogsessibales, paos sesxibplleo,riansge mxpolroer ipnaggmeso tryeppicaaglleys rteyspuilctasl liyn rgerseualttesr icnodgere caotevrercaogdee. Tcohvereerfaogree.,
TIhCeIr befroeraed,tIhC cIabnr ebaed tahn cianndibceataonr ionfd tihcaet oeffreocfttihveeneeffsesc otifv tehnee sinspoufttsh egeinnpeurattsegde bnyer tahteed pbroy-
tphoesperdo paposperdoaacphp. roach.
5.3. Experiment One
This experiment compares the mUSAGI method with our method across five web
applications. This experiment solely uses T5 and Mocker for form filling, excluding our
proposed SubmitButtonChecker and FormSuccessEvaluator methods. Doing so ensures
the evaluation of the capability of LLM on form filling. This model is called the T5 model.
For clicking buttons and checking successful submissions, the mechanism in mUSAGI is
still relied upon.
The experimental results are given in Table 4, showing values of code coverage, num-
ber of input pages, input page depth, and ICI breadth. It is worth noting that we slightly
modified how to count the number of input pages in the experiments compared to the
method used in mUSAGI. Therefore, the values reported here cannot be directly compared
with the values provided in [3]. Note that the fractional number in the input page depth of
the mUSAGI approach is due to the experiments being repeated three times to reduce the
random fluctuations in performance caused by the use of the RL algorithm. There is no ran-
dom fluctuation in the T5 model; therefore, the experiment was not repeated.
Table 4. Results for Experiment One.

## Page 16

Information2025,16,102 16of21
5.3. ExperimentOne
This experiment compares the mUSAGI method with our method across five web
applications. ThisexperimentsolelyusesT5andMockerforformfilling,excludingour
proposedSubmitButtonCheckerandFormSuccessEvaluatormethods. Doingsoensures
theevaluationofthecapabilityofLLMonformfilling. ThismodeliscalledtheT5model.
Forclickingbuttonsandcheckingsuccessfulsubmissions,themechanisminmUSAGIis
stillreliedupon.
The experimental results are given in Table 4, showing values of code coverage,
number of input pages, input page depth, and ICI breadth. It is worth noting that we
slightlymodifiedhowtocountthenumberofinputpagesintheexperimentscompared
tothemethodusedinmUSAGI.Therefore, thevaluesreportedherecannotbedirectly
comparedwiththevaluesprovidedin[3]. Notethatthefractionalnumberintheinput
pagedepthofthemUSAGIapproachisduetotheexperimentsbeingrepeatedthreetimes
toreducetherandomfluctuationsinperformancecausedbytheuseoftheRLalgorithm.
ThereisnorandomfluctuationintheT5model;therefore,theexperimentwasnotrepeated.
Table4.ResultsforExperimentOne.
CodeCoverage InputPages InputPageDepth ICIBreadth
WebApp
T5 mUSAGI T5 mUSAGI T5 mUSAGI T5 mUSAGI
TimeOff 54.67 52.51 15 9 3 3 12 9
NodeBB 44.49 41.45 7 4 2 1.3 3 2
KeystoneJS 49.48 49.20 14 14 4 3.3 5 5
Django - - 6 4 3 2 6 4
Petclinic - - 17 14 9 3.3 9 9
AstheAUTsdiffer,itisnotpossibletocombinetheirresultstocomputestatisticalpa-
rameters,suchasthestandarddeviation. ForeachindividualAUT,althoughthemUSAGI
testseachAUTthreetimes,thestandarddeviationisnotdescribedin[3]. Recallthatthere
is no random behavior in the proposed model. Therefore, only one set of values (such
as code coverage and number of input pages) per AUT is obtained. Consequently, the
experimentalresultsarenotsufficienttocarryoutmeaningfulstatisticalinferences. Hence,
onlyaveragevaluesarepresentedinTable4.
ItisobservedthatthecodecoverageoftheT5modeloutperformsthemUSAGImodel
in TimeOff, NodeBB, and KeystoneJS. When comparing the number of input pages in
Table4,itisobviousthattheT5modelhashighervaluesinthetestedAUTs. Withmore
inputpages,itisnaturaltohavehighercodecoverage. Itisworthnotingthatalthough
KeystoneJShasthesamenumberofinputpageswhentestedwithbothapproaches,theT5
modelhasahigherinputpagedepth. Therefore,itstillhasslightlyhighercodecoverage.
Inthisregard,boththe“numberofinputpages”and“inputpagedepth”valuesshouldbe
usedforbetterassessment.
Overall,withtheuseofLLMforformfilling,theperformanceimprovesonfourofthe
fiveAUTs. TheonlyAUTwithminorimprovementisKeystoneJS,whichactuallysuffers
fromtheproblemofincorrectlydetectingnewpages,asdiscussedinSection4.5.
5.4. ExperimentTwo
This experiment compares the mUSAGI method with our method across five web
applications. UnlikeExperimentOne,thisexperimentincludestheSubmitButtonChecker
and FormSuccessEvaluator blocks. This model is called the T5-GPT model. As the T5
modelshowsminorimprovementwhentestingKeystoneJS,thisexperimentwillfocuson

## Page 17

Information2025,16,102 17of21
theobservationofthisAUT.Forcompleteness,theresultsfortheremainingAUTsarealso
provided.
TheexperimentalresultsareshowninTable5, whereweobservethattheT5-GPT
modelhasamuchhighernumberofinputpagesinKeystoneJSthantheT5andmUSAGI
models (20 vs. 14). With successfully submitting more input pages, it is reasonable to
assumethattheT5-GPTmodelhashighercodecoverageinKeystoneJS.Thevalueofcode
coverageinTable5confirmstheassumption.
Table5.ResultsforExperimentTwo.
CodeCoverage InputPages InputDepth ICIBreadth
WebApp
T5-GPT T5 T5-GPT T5 T5-GPT T5 T5-GPT T5
TimeOff 54.74 54.67 14 15 3 3 14 12
NodeBB 44.52 44.49 7 7 2 2 3 3
KeystoneJS 50.86 49.48 20 14 4 4 5 5
Django - - 6 6 3 3 6 6
Petclinic - - 17 17 9 9 9 9
WhentestingtheTimeOffappwithbothmodels,Table5showsthattheT5-GPTmodel
hasaslightlylowernumberofinputpages,thesameamountofinputpagedepth,anda
higheramountofICIbreadth. ThecodecoverageshowsthattheT5-GPTmodelhasslightly
highercodecoverage. Ifcomparingmodelsonlywiththenumberofinputpagesandinput
pagedepth,wemightconcludethattheT5modelisslightlybetterthantheT5-GPTmodel.
However, it is actually not the case. Therefore, the ICI breadth is still a valid metric to
measuretheperformanceofthecomparedmodels.
Tables4and5indicatethattheT5modeloutperformstheoriginalmUSAGImodel,
primarily due to superior form-filling efficiency. The mUSAGI model, trained on one
AUTandtestedonanotheronewith250steps,struggleswhenfieldsinthetestedAUT
are absent in the training app, resulting in suboptimal action selection. Consequently,
it is less efficient in form filling compared to the T5 model. Additionally, the T5-GPT
modelincludesmechanismstoreducefalsedetectionofsuccessfulsubmissionsandbutton
elements,furtherenhancingtheefficiencyoftheproposedapproach.
5.5. ExperimentThree
ThisexperimentcomparestherelativeperformanceoftheproposedT5-only,T5-GPT,
mUSAGI, and QExplorer models. Although the source code of the Liu et al. model is
available[27],itisnotsuitableforcomparisonwithourapproach. Theirmodelisdesigned
formobileapps,whichrunonmobiledevices,whereasourmodelisintendedtotestweb
apps,whichareexecutedonserverstoprovidewebservices. Duetothisdistinction,we
cannotusetheirmodelforcomparison.
5.5.1. CodeCoverageComparisonwithQExplorerandmUSAGI
ThesourcecodeofQExplorerisalsoavailableonline. However,thiscodewasanearly
versionandhadsomecompatibilityissueswhenexecutingonourcomputers. Wespent
timemanagingthecodetowork,butweareunabletoconfirmifthisversionofthecode
wasactuallyusedintheliterature[24].
AsQExplorerisastandaloneplatform,wewerereluctanttorevisethecodetoreport
thenumberofinputpages,inputpagedepth,andICIbreadth. Afterreconsideration,we
decided to report only the results of code coverage. Therefore, only TimeOff, NodeBB,
and KeystoneJS were tested. Additionally, when using QExplorer to test NodeBB, the
toolcontinuouslyclickedonexternallinks,eventuallycausingthebrowsertorunoutof

## Page 18

Information2025,16,102 18of21
memoryandcrash. Therefore,QExplorerdoesnothavecodecoverageforNodeBB.The
experimentalresultsareshowninFigure11.ItisobservedthattheproposedT5-GPTmodel
outperformsthemUSAGImodel. ThemUSAGImodelalsooutperformsQExplorer.
Figure11.Comparisonofcodecoverage.
5.5.2. ExecutionTimeComparison
Inadditiontocodecoverage,theexecutiontimesofmUSAGI,T5-GPT,andQExplorer
arelistedinTable6. SincemUSAGIhasbothatrainingphaseandatestingphase, itis
difficulttodirectlycompareitsexecutiontimewiththeothers. Therefore,weprovideboth
times. As[3]doesnothaveanexacttestingtime,weusetheroughestimateprovidedin
thetext. TheexecutiontimeforQExplorerissetto4h,asextendingtheexecutiontime
doesnotimprovecodecoverage.
Table6.Executiontimeofvariousmodels(unit:hh:mm).
mUSAGI
WebApp T5-GPT QExplorer
Training Test
TimeOff 07:08 08:09 04:00
NodeBB 42:19 ~01:00 05:11 -
KeystoneJS 20:45 05:28 04:00
ItisimportanttonotethattheexecutiontimesoftheproposedT5-GPTandmUSAGI
modelsaremainlyaffectedbytheslowresponseofCrawljax. Oneinteractionbetween
Crawljax and the AUT can take several minutes. When analyzing the percentage of
computingtime,Crawljaxaccountsfor90.68%,GPT-4ofor1.31%,T5for0.63%,andthe
rest of the program for 7.38%. Therefore, it is apparent that Crawljax is the computing
bottleneck. In contrast, QExplorer does not rely on Crawljax to interact with the AUT.
Therefore,thecomparisonofexecutiontimesisonlyforreferenceanddoesnotreflectthe
actualcomputationalburdenoftheunderlyingalgorithmsofthestudiedapproaches.
5.6. ThreatstoValidity
Thethreatstointernalvalidityarisefromtheimplementationoftheplatformandthe
mannerinwhichtheexperimentswereconducted. Firstly, thecategoriestheT5model
cananswerarelimitedtothosegiveninTable1,makingitdifficulttofillanyfieldwithan

## Page 19

Information2025,16,102 19of21
untrainedcategory,suchas“PINnumber,”whichhasanexactnumberofdigits(typically,
six or eight). Next, because the values of the categories are generated from a Mocker,
theproposedmodelisunabletogenerateallpossibleinvalidinputsforcomprehensive
testing. Thirdly,thecategoriesarenotgeographicallysensitive. Therefore,itcannothandle
categorieswhoseformatsdependontheselectedlocations. Forexample,theUSAandUK
havedifferentpostalcodeformats. Theseissueswillbeaddressedinthenextsubsection.
ThethreatstoexternalvalidityarerelatedtotheAUTsselectedfortheexperiments.We
useonlyfiveAUTs,whichhavealimitedvarietyoffieldtypesintheirforms. Itisnecessary
totestmoreAUTstodetermineiftheobservedexperimentalresultscanbegeneralizedto
otherAUTs,andiftheperformancerankingofthestudiedmodelsremainsconsistent.
5.7. FutureDirections
Inthefuture,weplantoimprovetheperformanceoftheproposedT5-GPTmodel
withthefollowingpoints.
1. Enabling geographically sensitive values: The current model does not consider
geography-related content from URLs or pages of the AUT. By applying LLMs to
theseelements,itispossibletostoregeographicinformationintheproposedmodel,
enablingthegenerationofgeographicallysensitivevaluesbyLLMs.
2. Bettermechanismtodetectsuccessfulsubmission: Thecurrentimplementationuses
GPT-4o only if the similarity between two pages exceeds a threshold to lower the
test cost since GPT-4o is not a free service. In the future, we plan to use existing
pre-trainedLLMstodetectsuccessfulsubmissions,therebyeliminatingtheneedfora
threshold.
3. Using LLM for value generation: Data fakers limit the categories of form fields.
Instead, we can use an LLM as a value generator. To ensure the generated values
are reasonable, another LLM will act as a verifier to approve the values from the
generator.
4. TestingmoreAUTs: Currently,onlyfiveAUTsareusedtoevaluatethetestingper-
formanceoftheproposedmodel. TestingmoreAUTsfromvariouscategories,such
ase-commerceandlearningmanagementsystems,isdesirabletobetterevaluateits
usefulness.
5. Improvementofcomputationalefficiency: Thecurrentmodelservesasaproof-of-
concept,leveragingopen-sourceresourceslikeCrawljax,datafakers,andpre-trained
LLMs. Consequently,itscomputationalefficiencyisnotoptimized. Asmentioned
inSection5.5.2,Crawljax’sexecutiontimeaccountsformorethan90%ofthetotal
time. Duetoitslargecodebase,improvingCrawljax’sresponsetimeischallenging.
ApotentialfuturedirectionistointegratetheessentialCrawljaxfunctionsintothe
proposedmodeltoreduceoverallexecutiontime.
6. Conclusions
ThispaperintroducesamethodutilizingLLMstoenhancetheefficiencyofautomated
webapplicationtesting. Traditionalreinforcementlearningapproachesrelyonthelearned
agenttoprovidevaluesforformfieldsandinteractwithbuttons. Incontrast,ourmethod
integratestheT5modelwithpromptadjustmentsforvaluegenerationandusesGPT-4ofor
verifyingsuccessfulsubmissionsandidentifyingbuttonelements.Thisapproacheffectively
overcomes limitations of our previous model, such as limited input data diversity and
inaccuratedetectionofsuccessfulsubmissions.
Experimentalresultsconfirmthesuperiorityoftheproposedmethodintermsofcode
coveragecomparedtoourpreviousmodel,mUSAGI,andQExplorer.Ourmethodincreases
averagestatementcoverageby2.3%overthepreviousmodeland7.7%to11.9%compared

## Page 20

Information2025,16,102 20of21
toQExplorer. Theexperimentsalsoshowahighcorrelationbetweencodecoverageand
proposedmetrics,includingthenumberofinputpages,inputpagedepth,andICIbreadth.
Additionally,thesystem’smodularapproach,includingcomponentslikeFormAgentand
ValueGenerator,facilitatesfutureexpansionsandimprovements.
Insummary,thismethodoffersanefficientsolutionforautomatedwebapplication
testing,withpotentialforwidespreadadoptioninsoftwaredevelopment. Futurework
includesenablinggeographicallysensitivevalues,developingbettermechanismsforde-
tectingsuccessfulsubmissions,usingLLMsforvaluegeneration,testingmoreAUTs,and
improvingcomputationalefficiency.
AuthorContributions: Conceptualization,F.-K.C.,C.-H.L.,andS.D.Y.; methodology,F.-K.C.,C.-
H.L.,andS.D.Y.;software,F.-K.C.;validation,F.-K.C.,C.-H.L.,andS.D.Y.;formalanalysis,S.D.Y.;
investigation, F.-K.C., C.-H.L., and S.D.Y.; resources, C.-H.L., and S.D.Y.; data curation, F.-K.C.;
writing—originaldraftpreparation,S.D.Y.;writing—reviewandediting,C.-H.L.;visualization,F.-
K.C.;supervision,C.-H.L.,andS.D.Y.;projectadministration,C.-H.L.,andS.D.Y.;fundingacquisition,
C.-H.L.,andS.D.Y.Allauthorshavereadandagreedtothepublishedversionofthemanuscript.
Funding:ThisresearchwasfundedbyNationalScienceandTechnologyCouncil,Taiwan,withgrant
number112-2221-E-027-049-MY2andtheAPCwaswaivedbythejournaleditor.
Data Availability Statement: The conducted experiments required no additional data. The
sourcecodewillbeavailablepubliclyafterthepaperisacceptedathttps://github.com/ntutselab/
rlenvforapp(accessedon15December2024).
ConflictsofInterest:Feng-KaiChenwasemployedbythecompanyQnap.Theremainingauthors
declarethattheresearchwasconductedintheabsenceofanycommercialorfinancialrelationships
thatcouldbeconstruedasapotentialconflictofinterest.
References
1. HowManyWebsitesAreThere?Availableonline:https://www.statista.com/chart/19058/number-of-websites-online/(ac-
cessedon13January2025).
2. Liu,C.-H.;You,S.D.;Chiu,Y.-C.AReinforcementLearningApproachtoGuideWebCrawlertoExploreWebApplicationsfor
ImprovingCodeCoverage.Electronics2024,13,427.[CrossRef]
3. Lai,C.-F.;Liu,C.-H.;You,S.D.UsingWebpageComparisonMethodforAutomatedWebApplicationTestingwithReinforcement
Learning.Int.J.Eng.Technol.Innov.2024.accepted.
4. Raffel,C.;Shazeer,N.;Roberts,A.;Lee,K.;Narang,S.;Matena,M.;Zhou,Y.;Li,W.;Liu,P.J.ExploringtheLimitsofTransfer
LearningwithaUnifiedText-to-textTransformer.J.Mach.Learn.Res.2020,21,1–67.
5. Lester,B.;Al-Rfou,R.;Constant,N.ThePowerofScaleforParameter-efficientPromptTuning.arXiv2021,arXiv:2104.08691.
6. Ding,N.;Hu,S.;Zhao,W.;Chen,Y.;Liu,Z.;Zheng,H.-T.;Sun,M.Openprompt:AnOpen-SourceFrameworkforPrompt-Learning.
arXiv2021,arXiv:2111.01998.
7. Mocker-Data-Generator.Availableonline:https://github.com/danibram/mocker-data-generator(accessedon23May2024).
8. HelloGPT-4o.Availableonline:https://openai.com/index/hello-gpt-4o/(accessedon23May2024).
9. Wang,X.;Jiang,Y.;Tian,W.AnEfficientMethodforAutomaticGenerationofLinearlyIndependentPathsinWhite-boxTesting.
Int.J.Eng.Technol.Innov.2015,5,108–120.
10. Malhotra,D.;Bhatia,R.;Kumar,M.AutomatedSelectionofWebFormTextFieldValuesBasedonBayesianInferences.Int.J.Inf.
Retr.Res.2023,13,1–13.[CrossRef]
11. Sunman,N.;Soydan,Y.;Sözer,H.AutomatedWebApplicationTestingDrivenbyPre-recordedTestCases.J.Syst.Softw.2022,
193,111441.[CrossRef]
12. Crawljax.Availableonline:https://github.com/zaproxy/crawljax(accessedon25October2023).
13. Negara,N.;Stroulia,E.AutomatedAcceptanceTestingofJavascriptWebApplications.InProceedingsofthe201219thWorking
ConferenceonReverseEngineering,Kingston,ON,Canada,15–18October2012.
14. Wu,C.Y.;Wang,F.;Weng,M.H.;Lin,J.W.AutomatedTestingofWebApplicationswithTextInput.InProceedingsofthe2015
IEEEInternationalConferenceonProgressinInformaticsandComputing,Nanjing,China,18–20December2015.
15. Groce,A.CoverageRewarded:TestInputGenerationviaAdaptation-basedProgramming.InProceedingsofthe26thIEEE/ACM
InternationalConferenceonAutomatedSoftwareEngineering,Lawrence,KS,USA,6–10November2011.

## Page 21

Information2025,16,102 21of21
16. Lin,J.-W.;Wang,F.;Chu,P.UsingSemanticSimilarityinCrawling-BasedWebApplicationTesting.InProceedingsofthe2017
IEEEInternationalConferenceonSoftwareTesting,VerificationandValidation(ICST),Tokyo,Japan,13–17March2017.
17. Document Object Model (DOM) Technical Reports. Available online: https://www.w3.org/DOM/DOMTR (accessed on
20October2024).
18. Qi,X.F.;Hua,Y.L.;Wang,P.;Wang,Z.Y.LeveragingKeyword-guidedExplorationtoBuildTestModelsforWebApplications.
Inf.Softw.Technol.2019,111,110–119.[CrossRef]
19. Liu,C.-H.;Chen,W.-K.;Sun,C.-C.GUIDE:AnInteractiveandIncrementalApproachforCrawlingWebApplications.J.Super
Comput.2020,76,1562–1584.[CrossRef]
20. Carino,S.;Andrews,J.H.DynamicallyTestingGUIsUsingAntColonyOptimization.InProceedingsofthe30thIEEE/ACM
InternationalConferenceonAutomatedSoftwareEngineering,Lincoln,NE,USA,9–13November2015.
21. Nguyen,D.P.;Maag,S.CodelessWebTestingUsingSeleniumandMachineLearning.InProceedingsofthe15thInternational
ConferenceonSoftwareTechnologies,Online,7–9July2020.
22. Kim,J.;Kwon,M.;Yoo,S.GeneratingTestInputwithDeepReinforcementLearning. InProceedingsoftheIEEE/ACM11th
InternationalWorkshoponSearch-BasedSoftwareTesting(SBST),Gothenburg,Sweden,28–29May2018.
23. Zheng,Y.;Liu,Y.;Xie,X.;Liu,Y.;Ma,L.;Hao,J.;Liu,Y.AutomaticWebTestingUsingCuriosity-DrivenReinforcementLearning.
InProceedingsofthe43rdInternationalConferenceonSoftwareEngineering(ICSE),Online,22–30May2021.
24. Sherin,S.;Muqeet,A.;Khan,M.U.;Iqbal,M.Z.QExplore:AnExplorationStrategyforDynamicWebApplicationsUsingGuided
Search.J.Syst.Softw.2023,195,111512.[CrossRef]
25. Liu,E.Z.;Guu,K.;Pasupat,P.;Shi,T.;Liang,P.ReinforcementLearningonWebInterfacesUsingWorkflow-GuidedExploration.
InProceedingsoftheInternationalConferenceonLearningRepresentations,Vancouver,BC,Canada,30April–3May2018.
26. Mridha,N.F.; Joarder,M.A.AutomatedWebTestingOvertheLastDecade: ASystematicLiteratureReview. Syst. Lit. Rev.
Meta-AnalyJ.2023,4,32–44.[CrossRef]
27. Liu,Z.;Chen,C.;Wang,J.;Che,X.;Huang,Y.;Hu,J.;Wang,Q.FillintheBlank:Context-awareAutomatedTextInputGeneration
forMobileGUITesting.InProceedingsofthe2023IEEE/ACM45thInternationalConferenceonSoftwareEngineering(ICSE),
Melbourne,VIC,Australia,14–20May2023.
28. Mnih,V.;Kavukcuoglu,K.;Silver,D.;Rusu,A.A.;Veness,J.;Bellemare,M.G.;Graves,A.;Riedmiller,M.;Fidjeland,A.K.;etal.
Human-levelControlthroughDeepReinforcementLearning.Nature2015,518,529–533.[CrossRef][PubMed]
29. Istanbul.Availableonline:https://istanbul.js.org/(accessedon20October2023).
30. Gur,I.;Nachum,O.;Miao,Y.;Safdari,M.;Huang,A.;Chowdhery,A.;Narang,S.;Fiedel,N.;Faust,A.UnderstandingHTML
withLargeLanguageModels.arXiv2022,arXiv:2210.03945.
31. Devlin,J.;Chang,M.-W.;Lee,K.;Toutanova,K.Bert:Pre-trainingofdeepbidirectionaltransformersforlanguageunderstanding.
arXiv2018,arXiv:1810.04805.
32. Thoppilan,R.;DeFreitas,D.;Hall,J.;Shazeer,N.;Kulshreshtha,A.;Cheng,H.-T.;Jin,A.;Bos,T.;Baker,L.;Du,Y.;etal.Lamda:
LanguageModelsforDialogApplications.arXiv2022,arXiv:2201.08239.
33. MostPopularWebsitesWorldwideasofNovember2023,byUniqueVisitors. Availableonline: https://www.statista.com/
statistics/1201889/most-visited-websites-worldwide-unique-visits/(accessedon15January2025).
34. Fine-Tuning, vs. Prompt Engineering: How To Customize Your AI LLM. Available online: https://community.ibm.
com/community/user/ibmz-and-linuxone/blogs/philip-dsouza/2024/06/07/fine-tuning-vs-prompt-engineering-how-to-
customize?form=MG0AV3&communityKey=200b84ba-972f-4f79-8148-21a723194f7f(accessedon17January2025).
35. Prompt Tuning, vs. Fine-Tuning—Differences, Best Practices and Use Cases. Available online: https://nexla.com/ai-
infrastructure/prompt-tuning-vs-fine-tuning/?form=MG0AV3(accessedon17January2025).
36. TimeOff.Management.Availableonline:https://github.com/timeoff-management/application(accessedon20October2023).
37. NodeBB.Availableonline:https://github.com/NodeBB/NodeBB(accessedon20October2023).
38. KeystoneJS.Availableonline:https://github.com/keystonejs/keystone(accessedon25January2024).
39. DjangoBlog.Availableonline:https://github.com/reljicd/django-blog(accessedon20October2023).
40. SpringPetClinic.Availableonline:https://github.com/spring-projects/spring-petclinic(accessedon20October2023).
41. Brader,L.;Hilliker,H.;Wills,A.TestingforContinuousDeliverywithVisualStudio2012;Microsoft:Washington,DC,USA,2013;
p.30.
Disclaimer/Publisher’sNote: Thestatements, opinionsanddatacontainedinallpublicationsaresolelythoseoftheindividual
author(s)andcontributor(s)andnotofMDPIand/ortheeditor(s).MDPIand/ortheeditor(s)disclaimresponsibilityforanyinjuryto
peopleorpropertyresultingfromanyideas,methods,instructionsorproductsreferredtointhecontent.

