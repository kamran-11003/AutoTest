# Ase2024-Marg

**Source:** ASE2024-MARG.pdf  
**Converted:** 2026-01-26 09:22:30

---

## Page 1

2024 39th IEEE/ACM International Conference on Automated Software Engineering (ASE)
Can Cooperative Multi-Agent Reinforcement Learning Boost
Automatic Web Testing? An Exploratory Study
YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,∗
1ResearchInstituteofTrustworthyAutonomousSystems,SouthernUniversityofScienceandTechnology
2DepartmentofComputerScienceandEngineering,SouthernUniversityofScienceandTechnology
Shenzhen,China
{12431253,wangsn,12110608,12112016,12112045}@mail.sustech.edu.cn
liuyp1@sustech.edu
Abstract ACMReferenceFormat:
Reinforcement learning (RL)-based web GUI testing techniques
YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,Yepang
Liu1,2,.2024.CanCooperativeMulti-AgentReinforcementLearningBoost
haveattractedsignificantattentioninbothacademiaandindustry
duetotheirabilitytofacilitateautomaticandintelligentexploration
AutomaticWebTesting?AnExploratoryStudy.In39thIEEE/ACMInter-
nationalConferenceonAutomatedSoftwareEngineering(ASE’24),October
ofwebsitesundertest.Yet,theexistingapproachesthatleverage
27-November1,2024,Sacramento,CA,USA.ACM,NewYork,NY,USA,
asingleRLagentoftenstruggletocomprehensivelyexplorethe
13pages.https://doi.org/10.1145/3691620.3694983
vaststatespaceoflarge-scalewebsiteswithcomplexstructures
anddynamiccontent.Observingthisphenomenonandrecognizing
thebenefitofmultipleagents,weexploretheuseofMulti-Agent 1 Introduction
RL(MARL)algorithmsforautomaticwebGUItesting,aimingto Webapplicationsofferusersconvenientbrowser-basedaccessto
improvetestefficiencyandcoverage.However,howtosharein- softwareservicesacrossdifferentplatforms[49]andarewidely-
formationamongdifferentagentstoavoidredundantactionsand usedforvariouspurposes.Itisessentialtoensurethesoftware
achieveeffectivecooperationisanon-trivialproblem.Toaddress qualityofwebapplications.AutomaticwebGUItestingaimsat
the challenge, we propose the first MARL-based web GUI test- exploringagivenwebsiteundertest(WUT)withouthumaninter-
ingsystem,MARG,whichcoordinatesmultipletestingagentsto ventiontoachieveacomprehensivefunctionalcoverageanddetect
efficientlyexploreawebsiteundertest.Tosharetestingexperi- potentialmisbehavioursofthewebsite[11].Byemployingvarious
enceamongdifferentagents,wehavedesignedtwodatasharing meta-heuristicstrategies,atestingagentcanautonomouslyexplore
schemes:onecentralizedschemewithasharedQ-tabletofacilitate thewebsitetomeetthepre-definedtestingobjectives.
efficientcommunication,andanotherdistributedschemewithdata Reinforcementlearning(RL)isapopulartechniquefordriving
exchangetodecreasetheoverheadofmaintainingQ-tables.We theGUItestingofwebapplications[11].Forexample,WebExplor
haveevaluatedMARGonninepopularreal-worldwebsites.When [52]formulateswebtestingasaMarkovdecisionprocess(MDP)
configuringwithfiveagents,MARGachievesanaverageincrease andsolvesitwithavalue-basedRLalgorithm,Q-learning.Byem-
of4.34and3.89timesinthenumberofexploredstates,aswellasa ployingacuriosity-basedrewardfunction,theQ-learningalgorithm
correspondingincreaseof4.03and3.76timesinthenumberofde- guidesWebExplor toefficientlyexplorediversebehaviorsofthe
tectedfailures,respectively,whencomparedtotwostate-of-the-art WUT.QExplore[38]isanotherQ-learning-basedwebGUItesting
approaches.Additionally,comparedtoindependentlyrunningthe technique,whichadoptsadifferentstaterepresentationmethod
samenumberofagents,MARGcanexplore36.42%moreunique thanWebExplor.TheeffectivenessofRL-basedwebGUItestingap-
webstates.TheseresultsdemonstratetheusefulnessofMARLin proachesmostlyreliesontheexplorationabilitiesoftheRLagents
enhancingtheefficiencyandperformanceofwebGUItestingtasks. inthedynamicwebGUIcontextswiththegoalofachievinghigher
coverageanddetectingmorefaults.Besidestheoutstandingre-
Keywords sultsachievedonwebGUItesting,RLalgorithmsalsooutperform
WebTesting,Multi-AgentReinforcementLearning,AutomaticGUI traditionaltestingapproachesformanyothertypesofsoftware
Testing,InformationSharing applications,suchasmobileapps[19,20,35,44,45]anddesktop
applications[7,10,25,26].
Recently,Fanetal.conductedalarge-scaleempiricalstudyto
∗YepangLiuisthecorrespondingauthorofthepaper.
analyzetheperformanceofQ-learning-basedwebGUItestingap-
proaches[11].TheyinvestigatedthecombinationsofvariousRL
Permissiontomakedigitalorhardcopiesofallorpartofthisworkforpersonalor componentsandQ-learningparameters,withatotalof216differ-
classroomuseisgrantedwithoutfeeprovidedthatcopiesarenotmadeordistributed
forprofitorcommercialadvantageandthatcopiesbearthisnoticeandthefullcitation entconfigurations.Theirempiricalfindingsrevealthatnoneof
onthefirstpage.Copyrightsforcomponentsofthisworkownedbyothersthanthe theexploredRLconfigurationscanfitallthewebsitesusedinthe
author(s)mustbehonored.Abstractingwithcreditispermitted.Tocopyotherwise,or
study.Moreover,theyshowedthatQ-learningcanquicklyreacha
republish,topostonserversortoredistributetolists,requirespriorspecificpermission
and/orafee.Requestpermissionsfrompermissions@acm.org. saturationstatuswhenexploringsmall-sizedwebsites,whereasex-
ASE’24,October27-November1,2024,Sacramento,CA,USA ploringlarge-scalewebsitesinevitablyrequiresmuchmoretesting
©2024Copyrightheldbytheowner/author(s).PublicationrightslicensedtoACM. resources.Theirresearchcallsfortheenhancementonthecurrent
ACMISBN979-8-4007-1248-7/24/10
https://doi.org/10.1145/3691620.3694983 single-agentRL-basedGUItestingtechniques.
14

## Page 2

ASE’24,October27-November1,2024,Sacramento,CA,USA YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,
Observingthepotentialperformanceupperboundofasingle- Action selection
agentapproach,weinthispaperexploretheuseofmultipleagents
forefficientandeffectivewebGUItesting.However,designinga Reward Agent /
GUI info Testing Tool UI event
practicallyusefulmulti-agentsystemtoachieveacomprehensive
perception execution
testingofwebapplicationsisanon-trivialtask.Astraightforward State/Observation Action
solutionistorunmultiplesingle-agentprocessesinparallel,aspro-
Environment /
posedin𝐺𝑇𝑃𝑄𝐿[32].Giventheinherentrandomnessbroughtby
Website
an𝜀-greedystrategy[42],itispossibleformultipleagentstocover
Figure1:AwebtestingloopundertheMDPformulation
differentfunctionalpointsinthesamewebsite.However,aswewill
showinamotivationalstudy(Section3),underthissimplesetting,
onlyasmallamountofwebstatescanbeexclusivelyvisitedbyeach
singleagent(i.e.,theagentsvisitalargenumberofidenticalstates), Thecontributionsofthispaperaresummarizedasfollows:
leadingtoinsignificantperformanceimprovementandwasteof • WeproposeanewwebGUItestingapproachthatemploysasyn-
testingresources.Toaddresstheproblem,𝐺𝑇𝑃𝑄𝐿synchronizesthe
chronousMARLtodrivemultipleQ-learningagentstocollabo-
Q-modelsofparallelQ-learningagentsattheendofeachepochto rativelytestwebapplications.Tothebestofourknowledge,we
facilitateinformationcommunication.Nevertheless,thecomplexi- makethefirstattemptindevisingefficientagentcommunication
tiesofepochdivision,thelackofcommunicationsamongagents mechanismstoenableeffectivemulti-agentwebGUItesting.
withineachepoch,andtheoverheadofmodelsynchronizationmay
• WehaveimplementedourapproachinaprototypesystemMARG
diminishthepracticalutilityofthetool.Amoreeffectiveagent
withtwotypesofdatasharingschemestosupportbothcentral-
cooperationmechanismisneededtomitigatetheredundanciesin
izedanddecentralizedsettings,whichcanprovidereferencesfor
thewebpageexplorationofmultipleagentsandimprovetheoverall
futureresearchendeavors.
performanceofwebGUItesting.
Motivatedbytheintrinsiclimitationsofexistingsingle-agent • WehaveevaluatedMARGusingreal-worldcommercialwebsites.
RL-basedtestingapproaches,andtheweaknessesofthenaivepar- OurexperimentsshowthatMARGcansignificantlyoutperform
allelismapproach,westronglyadvocatethenecessityofanefficient twostate-of-the-artRL-basedmethods,WebExplorandQExplore,
multi-agentreinforcementlearning(MARL)basedapproachforim- aswellasanon-cooperativemulti-agenttestingapproachthat
provingtheefficiencyandeffectivenessofwebGUItesting.Tothis runsQ-learningagentsinparallel.
end,wemadethefirstattemptofutilizingMARLalgorithmsforco- Theremainderofthispaperisorganizedasfollows.Section2
ordinatingmultipleQ-learningtestingagentstocollectivelyexplore introducesbackgroundknowledgeaboutRLforGUItestingand
thesameWUT.Ourprototypetool,namedMARG,isanMARL- MARLalgorithm.InSection3,wedemonstratethelimitationof
basedwebGUItestingsystemthatallowsaconfigurablenumberof single-agent RL-based approaches to motivate the necessity of
Q-learningagentstosimultaneouslytestthesamewebsitewithout MARL-basedwebGUItesting.Section4depictsthedetaileddesign
humanintervention.Specifically,MARGadoptsaclient-serverar- ofourproposedmulti-agentapproach.Section5presentstheex-
chitecture,inwhichtheagentsinteractwithdifferentwebpagesand perimentalsetupforevaluatingourapproachandtheresultsare
thecontrollercoordinatesthetestingprocess.Tofacilitatetheex- discussedinSection6.WereviewtherelatedworkinSection7and
changeofexperiencesamongvariousQ-learningagentswithinthe finallyconcludethepaperinSection8.
MARLsystem,wehavedevelopedtwodatasharingschemes.These
schemesoperateunderbothcentralizedanddecentralizedsettings, 2 Preliminaries
allowingagentstoshareQ-valuesderivedfromtheirpolicies.
2.1 ReinforcementLearningforGUITesting
WehaveimplementedMARGandevaluateditonninecommer-
cialwebsites(suchasYouTubeandGitHub).BycomparingMARG Formally,anMDPinstanceisdefinedbya5-tuple⟨S,A,P,R,𝛾⟩[5].
againsttwostate-of-the-artRL-basedtechniques,WebExplor[52] InthecontextofwebGUItesting,wecallthesoftwareundertest,
andQExplore[38],weshowthatanMARL-basedapproachthat i.e., the website, as an environment while the testing process is
leverages plain Q-learning algorithms can already significantly carriedoutbyanagent.Theinteractionbetweentheenvironment
outperformexistingsingle-agenttechniquesthatleverageextra andtheagentisdepictedinFigure1.Inthe5-tuple,astate𝑠 ∈S
methods(suchasusingaDFAtoprovidehigh-levelguidance[52] representshowthetestingagentobservesinformationfromthe
andacontextualdatainputmethodtogeneratetextualinputs[38]) currentwebpage.Ateachstate,theactionspaceAencompasses
beyondRL.Whenrunningfiveagents,MARGcanexplore4.34and human-likeinteractionswiththewebGUIelements,suchasclick-
3.89timesmorestates,anddetect4.03and3.76timesmorefail- ingbuttonsorlinks,fillinginputboxes,andsoon.Afteranaction
ures,respectively,thanWebExplorandQExplore.Itcanalsoexplore 𝑎∈Aisperformed,therewillbeatransformationofwebpagesthat
36.42%morestatesthananon-cooperativeapproachthatsimply followsthetransitionfunctionP :S×A→S,whichdependson
runsfiveparallelQ-learningagents.Additionally,byincreasing thefunctionalitiesandbusinesslogicofthewebsite.Afteranaction
thenumberofagents,whichcanbeconstrainedbycomputational isappliedattime𝑡,theagentwillbeprovidedwithanimmediate
resources, the performance of MARG can be further increased. reward𝑟 𝑡 basedonapredefinedrewardfunctionRtoguidebetter
Thesepromisingresultsdemonstratethegreatpotentialofapply- GUIexploration.Suchrewardistypicallydesignedbasedonstate
ingMARLtoboosttheperformanceofwebGUItesting. changes[25,26]ortheexecutionfrequenciesofactions[35,52].
Additionally,italsoneedstodefineadiscountfactor 𝛾 ∈ [0,1].
15

## Page 3

CanCooperativeMulti-AgentReinforcementLearningBoostAutomaticWebTesting?AnExploratoryStudy ASE’24,October27-November1,2024,Sacramento,CA,USA
Lowervaluesof𝛾 prioritizeimmediaterewards,whilehigherval- 3 MotivationalStudy
uesconsiderlong-termrewards.Withsuchaformulation,thegoal Recently,anempiricalstudyconductedbyFanetal.analyzedthe
ofanRLagentistolearntomaximizetheaccumulatedrewards effectivenessofQ-learning-basedwebGUItestingapproaches[11].
duringitsexplorationintheenvironment:𝑟1+𝛾1𝑟2+𝛾2𝑟3+···.
The study pointed out a performance limit for single-agent Q-
learning approaches: it is difficult for a single agent to achieve
2.2 Multi-AgentReinforcementLearning highfunctionalcoveragefortheWUT,especiallywhenthetesting
resourcesareconstrained.Totacklethisproblem,i.e.,improving
AnMARLsystemcanbecompetitiveorcooperative[50].Incom-
efficiencyandachievinghighercoverage,apossiblesolutionisto
petitiveMARL,theagentshaveconflictingobjectives,inwhich
runmultipletestingagentssimultaneously.Toinvestigatethefeasi-
thegrossrewardamongagentsisusuallyzero-summed[23].Most
bilityoftheideaandunderstandthechallengesduringtheprocess,
researchworkoncompetitiveMARLfocusesontwo-playergames,
weperformedapilotstudytoseewhethertheparallelismofagents
suchasAlphaGo[39,40],arepresentativebreakthroughinthe
caneffectivelyimprovethetestcoverageofwebapplications.
gameofGo.IncooperativeMARL,agentscollaborateandcoordi-
•Implementation:AccordingtotheQ-learning-basedwebGUI
natetheiractionstoachieveacommongoal,thusmaximizingthe
testingframeworkproposedinFanetal.’swork[11],weimple-
overallteamreward.Thisisapplicableinteam-basedrobotics[9],
mentedourownwebtestingagentsontopofSelenium[2].Specif-
trafficmanagement[4],etc.DuringwebGUItesting,thetesting
ically,followingFanetal.’sapproach,weabstractedawebstate
agentsshouldbecoordinatedtomaximizetestefficiencyandcol-
asthesetofallGUIelementsonthecorrespondingwebpageand
laborativelyexploreasmanydiversifiedwebpagesaspossible.As
selectedactionsaccordingtoan𝜀-greedyscheme.TheQ-learning
such,itisatypicalapplicationscenarioofcooperativeMARL.
agentswillobtainanumericalrewardbasedoncuriosity,whichhas
AkeychallengeofimplementinganefficientMARL-basedsys-
beenshowntobeaneffectivechoicefordefiningrewardfunctions
temistoproperlydesignthesystem’sinformationstructureandthe
inexistingstudies[7,10,38,44,52].
communicationmechanismbetweenagents.Generally,anMARL
•Setup:Forthepilotstudy,weranourimplementedQ-learning
systemcanbeclassifiedintothreetypesaccordingtotheircommu- agentsonacomplexcommercialwebsite1.Thiscommercialwebsite
nicationstylesasshowninFigure2,namely,fullydecentralized,
isawebportalthatcontainsmorethanonehundredhyperlinks,
decentralizedwithnetworkedagents,andcentralizedsettings[50]:
eachleadingtoanewsubpageprovidingdifferentwebservices.
Moreover,mostofthesesubpagesdonotrequireuserloginbefore
(a) Inafullydecentralizedsetting(Figure2a),agentsautonomously
visiting, making the background status identical for all parallel
makedecisionsandinteractwiththeenvironmentbasedon
agents.Besides,thiswebsitehasasufficientnumberofdifferent
theirindividualobservationsandtheirownpolicies.Thisdecen-
webstates,whichallowsthemeasurementandcomparisonofthe
tralizedarchitecturesimplifiessystemdesignandreducesthe
testingadequacyachievedbyeachagent,aswellasassessingtheir
complexityofcoordination.However,thelackofinformation
collectiveperformance.Fortheexperiment,weranthreetesting
exchangepreventsagentsfromutilizingeachother’sknowledge
agentsinparallelfortwohoursandcomparedtheirvisitedstates
andexperience,whichlimitstheoverallperformance[43].
attheend.
(b) Whentheagentsareconnectedthroughatime-varyingcom-
•Result:Figure3presentsthenumberofvisitedstatesachieved
municationnetwork,itbecomespossibletodisseminatelocal
by each of the three Q-learning agents. It shows that within a
informationofanagentovertheentirenetwork[24,46,51].It
two-hourtestingperiod,thethreeagentsdiscovered564different
iscalledadecentralizedsettingwithnetworkedagents(Figure
web states, while each contributed to 59%, 76%, and 71% of the
2b).However,withinthisinformationstructure,noteverypair
totalstates,respectively.Besides,fromtheVenndiagram,wecan
ofagentsisrequiredtoexchangeinformationateveryinstant.
maketwomoreobservations.First,amongthe564webstates,36%
(c) Insituationswhereitisnecessaryforallagentstoconsistently (=(93+72+39)/564)ofthemwerediscoveredexclusivelybyasingle
share information, a central controller can be employed, re- agent.Second,42%(=236/564)ofthestateswerevisitedbyallthree
sulting in the centralized setting (Figure 2c). This controller agents.Fromtheaboveobservations,wecanseethatitisindeed
aggregatesinformationfromtheagentsandmakesdecisions feasibletoleverageamulti-agentapproachtoimprovethecoverage
forallagentsonbehalfoftheentireMARLsystem[13–16]. ofwebGUItesting,soastoincreasethepossibilityofdetecting
potentialfaults.However,withouteffectiveagentcommunications,
FortheRLagentsinanMARLsystem,theyshallupdatetheir therewouldaconsiderableamountofredundantexplorationamong
ownpoliciesbasedontheirobservedstatetransitions.Thiscan theparallelagents,resultinginthewasteoftestingresources.
bedoneinasynchronousmanner,wheretheagentstemporarily •Conclusion:Basedontheaboveanalysis,itisevidentthatreduc-
halttheirexplorations,sequentiallyupdatetheirpolicies,andthen ingtheredundanciesinthestatesvisitedbythetestingagentshas
resumethenextexplorationstep.Incomparison,inanasynchro- agreatpotentialofimprovingtheoverallperformanceofwebGUI
nous MARL system, agents update their policies independently testing.Motivatedbythis,inourwork,wewillfocusonharnessing
andasynchronouslywithoutwaitingforotheragentstoupdate multi-agentapproachesforwebGUItestinganddevisingpractical
theirs [30]. In web GUI testing, the RL agents explore different strategiestofacilitatethecooperationamongthetestingagents,
pathsandinteractwiththewebapplicationusingtheirdedicated enablingthemtoefficientlyshareinformationandcollaboratively
browserinstances.Insuchascenario,asynchronousexploration explorediversifiedwebpagestoquicklyachievehightestcoverage.
allowstheagentstocoverawiderrangeofthewebapplication’s
functionalitiesandachieveabetteroverallcoverage. 1Forcommercialreasons,thewebsiteisanonymized.
16

## Page 4

ASE’24,October27-November1,2024,Sacramento,CA,USA YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,
Agent1 … AgentN Agent3 … CentralController
Agent1
Agent2
AgentN
Agent2
Agent1 Agent2 … AgentN
Observation Observation Observation Observation Observation Observation
Environment Environment Environment
(a)Fullydecentralizedsetting (b)Decentralizedsettingwithnetworkedagents (c)Centralizedsetting
Figure2:ThreerepresentativeinformationstructuresinMARL[50]
beenshowntobemoreeffective[11].Itprovidesthebenefitof
93 RLAgent 2
simplifyingthestatespacewhileretainingessentialinformation.
(428states)
30 Moreover, it aligns withthe state-action pairsin the tabularQ-
learningframework.
RLAgent1 39 236 During testing, the state transition function P is implicit as
(330states) 69 theagentlacksdirectaccesstonavigationinformation.Instead,
25 theagentlearnsanapproximatePbyobservingstatetransitions
RLAgent3 throughinteractionswiththewebsite.Whenanagentinthemulti-
72 (402states)
agentsystemexecutesanaction𝑎∈A𝑠 basedonthestate𝑠 ∈S,
Figure3:TheVenndiagramofthesetsofwebstatesvisited thewebpageundergoeschanges,resultinginanewstate𝑠′ ∈ S
bythethreeQ-learning-basedtestingagents andanimmediatereward𝑟 basedontherewardfunctionR:
1
𝑟 =R(𝑎)= (1)
4 Approach Count(𝑎)
4.1 ProblemFormulation Thiscuriosityrewardfunctionhasbeendemonstratedtobeeffec-
MARLcanbeformulatedasamulti-agentextensionoftheMDPde-
tive[11,38,52],whereCount(𝑎)representsthenumberoftimes
theaction𝑎hasbeenappliedwithinthemulti-agentsystemduring
scribedinSection2.1,asdenotedby⟨𝑁,S,{O𝑖},{A𝑖},P,R,𝛾⟩[48],
thetestingsession.
where𝑖 ∈{1,...,𝑁}correspondstothe𝑖-thagentinthesystemof
𝑁 agents.TheOstandsforobservation,whichreferstotheinfor-
4.2 AnOverviewof MARG
mationthatanagentperceivesabouttheenvironment.Typically,
thestatespaceSisdefinedbytheCartesianproductofobservation Figure4showstheoverviewof MARG.Inthissystem,eachagent
spaceofeachagent,i.e.,S = O1×O2×···×O𝑁 .However,this canperformautomaticGUItestingoftheWUTonitsownbrowser
formulationpresentsthechallengeofstateexplosion,particularly instance.Eachtestingstepofanindividualagentisdividedinto
inthecontextofwebGUItesting,aswebpagestatesexhibithigh fourphases:❶GUIinformationperception,❷policyoptimization,
variability. ❸actionselection,and❹UIeventexecution.ThephasesofGUI
InanasynchronousMARLsystem,itisessentialtoconsider informationperceptionandUIeventexecutionareperformedby
whichinformationtheagentsneedtocommunicateinorderto theInteractioncomponent,whichishandledindependentlybyeach
achievebettercooperationandcoordination.Insteadofcoordinat- agent.Ontheotherhand,thephasesofpolicyoptimizationand
ingthejointexplorationstatusamongallagents,theemphasis actionselectionaregroupedasaDecision-makingcomponentman-
should be placed on exchanging their historical experiences to agedbyacontrollerthatfacilitatesexperiencesharing.Toachieve
avoidredundantexploration.Therefore,wedefinethestatespace reliableandasynchronousinformationtransmissionbetweenthe
inourproblemas:S=O1∪O2∪···∪O𝑁 .Suchasettingallows agentsandthecontroller,oursystememploysaclient-serverarchi-
theMARLalgorithmtoprioritizethedecisionsthatagentsshould tecture[21]andutilizestheHTTPprotocol[12]fordatatransfer.
makewhenobservingspecificwebpages,withoutconsideringthe Duringatestingsession,eachagentindependentlydetectsin-
statesoftheotheragentsatthesametime.Inotherwords,thestate teractableelementsonitsobservedwebpage.Suchelementscanbe
spaceinourproblemconsistsofallstatesobservedbyalltheagents clickablebuttonsorlinks,textboxesormultiple-selectionboxes.
inthesystem.Tosimplifypresentation,wewillusethesymbol𝑠 Theseelementsformtheactionspace,which,combinedwiththe
torepresentboththeconceptsofstateandobservation. webpage’sURL,servesastheagent’sstate,asdefinedinSection4.1.
WeextractvalidUIeventssetasarepresentationofthestate Additionally,theagentdiscernsthecategoriesofthecurrenttest-
𝑠 = (URL,𝐸1,𝐸2,...,𝐸 𝑛),whichalsorepresentstheactionspace ingstep,generatescorrespondingrequestmessages,andsendsthe
A𝑠 = {𝐸1,𝐸2,...,𝐸 𝑛}withinthisobservedstate.Here,𝐸 𝑘 isaUI messagestothecontroller(i.e.,theserver).Differentcategories
eventand𝑛isthenumberofuniqueUIeventsthatcanbetriggered ofstepscorrespondtodifferentprocessinglogics,whichwillbe
onagivenwebpage.Thisabstractionmethodborrowstheidea elaboratedinSection4.3.Withtherequestsfromtheagent,the
of combined state representation employed by WebExplor [52], controllerobtainstransitioninformationforupdatingglobaldata
whilewereplaceitstagsequenceasthesetofactions,whichhas andoptimizingstrategybasedonextendedQ-learningalgorithms.
17

## Page 5

CanCooperativeMulti-AgentReinforcementLearningBoostAutomaticWebTesting?AnExploratoryStudy ASE’24,October27-November1,2024,Sacramento,CA,USA
❶GUIinfoperception
Testing Stage
Classifier
Request Message Request Message
Generator Parser
Centralized Q-learning
with shared Q-table
Local Data Global Data
Memory Memory
Interaction ResponseMessage ResponseMessage
Parser Generator Decision-making
❹UIeventexecution
Client / Agent Server / Controller
Distributed Q-learning
State with data exchange
Send message ❷Policyoptimization
Historical data Update global data
Reward
Record local data Update global data
❸Actionselection Action
Send message
Figure4:AnoverviewofMARG
Meanwhile,thecurrentGUIinformation,includingstateandaction ontheGUIinformationandcalculatestheactionexecutioncount
space,willbeusedtoselectanappropriateaction.Thedetailed tocomputereward𝑟 usingEquation(1),thetuple(𝑠,𝑎,𝑠′,𝑟)can
algorithmswillbeintroducedinSection4.4.Subsequently,thecon- updatethepolicyfunction.Theprocessofactionselectionand
trollerwillsendaresponsemessagetothecorrespondingagent, responsemessagegenerationisthesameasthatintheinitialstage.
whichcontainstheselectedactionalongwithothernecessaryin- •FailureStageencompassessituationswheretheagentencounters
formation.Uponreceivingtheresponse,theagentexecutesthe obstaclespreventingsmoothtestingprogress.Itmayoccurwhen
selectedaction,whichisaUIevent,updatesitslocaldatamemory, thewebpage1)lacksinteractiveelements,2)isinaccessibledueto
andproceedstothenextstep. brokenlinks,servererrors,oraccessrestrictions,3)isfromexternal
websitesthatarenotwithinthedefinedtestingdomain.Inthese
situations,theagentshareswiththecontrollerthepreviousstate
4.3 TestingStagesandMessages
andactionthatresultedincurrentwebpage,withoutproviding
DuringthecontinuousinteractionwiththeWUT,atestingagent detailedinformationaboutthewebpageitself.Thus,thecontroller
oftenfacesdifferentstagesthatshouldbehandledwithdifferent canpenalizetheQ-valuestoindicatethatexecutingtheactionin
methods.Forexample,atthebeginningofatestingsession,asthe thatstateisunfavorable.Differentfromtheactionselectionprocess
agentdoesnotpossessanyknowledgeaboutthewebsite,itcannot innormalstage,insuchcases,thecontrollerreturnsaURLwith
properlyupdateitsactionpolicy.Asanotherexample,whensome lowestvisitcountfortheagenttorestartfrom.Thishelpstheagent
exceptionalsituationsoccur(e.g.,crashes),theagentshouldhave recoverfromabnormalstatusandfacilitatesfurtherexploration.
meanstorecoverfromtheerroneousstatus.InMARG,ateachstep •StagnationStageoccurswhentheagentbecomestrappedina
inthetestingloop,theagentwillrecognizeitscurrentstage.There localloop,meaningthatithasexecutedactionsmorethanthreshold
arefourstagesdefinedinMARG:initial,normal,failure,andstag- timeswithouttriggeringanewstate.Similartothefailurestage,the
nationstages.Basedonthestage,theagentsendsacorresponding agentwillrestartthetestingprocessfromtheleastvisitedwebpage.
messagetothecontrollertoobtainoptimalactioninthecurrent Additionally,thisstageinvolvesacompletestatetransition,thus
step. The classification of stages, request message formats, and theinformationshowninTable1shouldalsobesynchronizedto
expectedresponsemessagecontentareshowninTable1. thecontrollerforpolicyoptimization.
•InitialStagereferstothebeginningofthetestingprocess.With Theadvantageofthisclassificationmethodisthatthecontroller
nopriorvisitedstatesorappliedactions,theagentsimplyneeds onlyneedstodeterminethedecisioncategoryoftheagentbasedon
toprovidethecontrollerwiththestateandactionspaceofthe thetypeofrequestmessage,withouthavingtoretainexcessively
currentwebpage.Afterreceivingtheinitialrequestmessage,the detailedlocalinformationoftheagent.Thissimplifiesthetaskof
controllercheckstheglobalstatelisttodetermineifthestatehas thecontroller,enablingittohandleandrespondtotherequest
appearedinthetestinghistoryoftheentiresystem.Ifthestate messagesfromagentsmoreefficiently.
exists,itscorrespondingindexisretrieved.Otherwise,thestateis
addedtotheglobalstatelistalongwithitsactionspaceinformation. 4.4 Multi-AgentQ-Learning
Then,thesystemretrievesthecorrespondingindexandfeedsit
As mentioned above, the controller is responsible for two key
intothepolicyfunctiontoobtainanaction.Finally,thecontroller phases:policyoptimizationandactionselection.Forsingle-agent
encapsulatesthestateindexandtheselectedactionintoaresponse GUItesting,previousstudies[10,19,25,35,38,44,52]havedemon-
message,andreturnsittotheagent. stratedtheeffectivenessoftheQ-learning[47]algorithminupdat-
•NormalStagereferstoanormalinteractionduringtesting,which ingtheactionpolicy:
involvesacompletestatetransition.AsshowninTable1,agent
𝑄(𝑠,𝑎)←𝑄(𝑠,𝑎)+𝛼[𝑟𝑡+𝛾 max 𝑄(𝑠′,𝑎′)−𝑄(𝑠,𝑎)] (2)
sendstheindexofpreviousstateandactionthatnavigatetothe 𝑎′∈A𝑠′
currentstate,alongwithGUIinformationofcurrentwebpage,to Whenitcomestoactionselection,𝜀-greedyiswidelyemployed
thecontroller.Afterthecontrolleracquiresthestateindexbased tostrikeabalancebetweenexplorationandexploitation[25,35,44].
18

## Page 6

ASE’24,October27-November1,2024,Sacramento,CA,USA YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,
Table1:AttributesintheHTTPmessagesatdifferentstagesandthecorrespondingresponses
Agent Previous Executed Current Current Current Selected
StageMessage
ID StateIndex Action Observation ActionSpace StateIndex Action
Initial ✓ ✓ ✓
Request
Normal ✓ ✓ ✓ ✓ ✓
Response - ✓ ✓ UIevent
Failure ✓ ✓ ✓
Request
Stagnation ✓ ✓ ✓ ✓ ✓
Response - ✓ restartURL
Action Space …
State
Space
…
Request Algorithm1:DistributedQ-learningforthe𝑘-thagent
Message List
(𝑠 ! ,𝑎 " ,𝑠 " ) (𝑠 ! ,𝑎 # ,𝑠 $ ) Input:Agent𝑘:previousstate𝑠,executedaction𝑎,currentstate𝑠′,
Agent 1
(𝑠 ,𝑎 ,𝑠 )
actionspaceofcurrentstateA𝑠′,reward𝑟
Agent 2 (𝑠 " ,𝑎 % ,𝑠 ! )
' $
(
%
𝑠 " ,𝑎 & ,𝑠 # )
G
hy
lo
p
b
e
a
rp
l:
a
n
r
u
am
m
e
b
t
e
e
r
rs
of
𝛼
a
,
g
𝛾
e
,
n
𝜀
ts𝑁,Q-tables𝑄1,𝑄2,...𝑄
𝑁
,and
Agent 3 Output:𝑄 𝑘 ,chosenaction𝑎′
Agent 1 1 if𝑠′notin𝑄 𝑘 then
2 initialize𝑄 𝑘(𝑠′,A𝑠′)
Agent 3
… 3 for𝑗=1,...,𝑁;𝑗≠𝑘do
4 if𝑠′in𝑄𝑗 then
5 tempQ.append(𝑄𝑗(𝑠′,A𝑠′))
Figure5:AnillustrationofthesharedQ-tablescheme
6 iftempQisemptythen
7 update𝑄 𝑘(𝑠,𝑎)usingEquation(2)
8 Choose𝑎′fromA𝑠′ usingEquation(3)on𝑄 𝑘(𝑠′,·)
Thisstrategyrandomlyselectsanactionfromtheactionspacewith 9 else
aprobabilityof𝜀,whileexploitingpriorexperiencebychoosing 10 update𝑄 𝑘(𝑠,𝑎)usingEquation(4)
thehighest-scoredactionwithaprobabilityof1−𝜀: 11 for 𝑎𝑖inA𝑠′ do
(cid:40) argmax𝑄(𝑠,𝑎′) withprobability1−𝜀, 12 𝑄 𝑠 ∗ ′ (𝑎𝑖)=Σ 𝑄𝑗∈tempQ 𝑄𝑗(𝑠′,𝑎𝑖)
𝑎∗= 𝑎′∈A𝑠 (3) 13 Choose𝑎′fromA𝑠′ usingEquation(3)on𝑄 𝑠 ∗ ′ (·)
random∈A𝑠′ withprobability𝜀.
4.4.1 CentralizedQ-learningwithasharedQ-table. Whenthereare
multipleRLagentsrelyingonacentralizedcontrollerfordecision-
allagents’experiences.Thismechanismofexperiencesharingfa-
making,itbecomesintuitivetorecordallstate-actionpairsandthe
cilitatesmutuallearningandleverageamongallagents,thereby
correspondingQ-valuesintoasharedQ-table.Figure5providesan
improvingtheoverallsystemperformanceandeffectiveness.
illustrationofhowthecontrolleroptimizestheRLpolicyusinga
sharedQ-table.Uponparsingtheresponsemessageandaccessing 4.4.2 DistributedQ-learningwithdataexchange. ThesharedQ-
theglobaldatamemory,thecontrollerobtainsa4-tuple(𝑠,𝑎,𝑠′,𝑟), tableschemeissimpleandeasytoimplement.Moreimportantly,
enablingittoupdatethevalueof𝑄(𝑠,𝑎)accordingtoEquation(2). itallowstimelyupdatesoftestingexperiencesamongallagents.
ReferringtoFigure5,assumingtherearethreeagentsinthesystem. However,itmaybecomeinefficientasthescaleoftheQ-tablegrows.
ThefirstrequestmessagefromAgent1requiresthecontrollerto Therefore,weconsideranalternativeapproach,whereeachagent
update𝑄(𝑠1,𝑎3). Suppose that the updated Q-value𝑄(𝑠1,𝑎3) is maintainsitsownQ-tableandupdatesitondemand.Thisapproach,
lowerthanitspreviousvalue,leadingto𝑄(𝑠1,𝑎5) becomingthe whichwecalleddistributedQ-learning,isshowninAlgorithm1.
highestQ-value.Consequently,whenAgent3visitsthestate𝑠1 after Whenthecontrollerreceivesamessagefromthe𝑘-thagent,it
takingaction𝑎4 instate𝑠3 ,theprobabilityofselecting𝑄(𝑠1,𝑎5) parsesthemessagetoobtainthetuple(𝑠,𝑎,𝑠′,𝑟).Then,itsearches
becomeshighest.Ifthecontrollerchoosesaction𝑎5 forAgent3, theQ-tableforagent𝑘tocheckifthereareQ-valuesforthecurrent
itwillreceivearequestmessagefromAgent3,asdepictedbythe state𝑠′.IftherearenoQ-valuesfor𝑠′,thecontrollerinitializes
fifthmessageinFigure5,whichleadstoanupdateof𝑄(𝑠1,𝑎5). 𝑄 𝑘(𝑠′,A𝑠′)withaninitialQ-value(lines1-2).
Inthisway,allagentswithinthesystemcansharetestingexperi- Next,thecontrolleroptimizesthepolicyforagent𝑘byupdating
encesthroughthesharedQ-table.Whenanagentreceivesareward 𝑄 𝑘(𝑠,𝑎).Beforecalculatingthenewvalueof𝑄 𝑘(𝑠,𝑎),thecontroller
forastate-actionpair,thecorrespondingvalueinQ-tableisupdated gathersinformationaboutthecurrentstate𝑠′ fromtheQ-tables
accordingly.Asaresult,whenotheragentsvisitthesamestate, ofotheragents.Specifically,if𝑠′ ispresentintheQ-tableofthe
theywillbeinfluencedbytheexperiencesandprioritizeactions agent𝑗 suchthat𝑗 ≠𝑘,thevalue𝑄 𝑗(𝑠′,A𝑠′)issavedintoatem-
withhigherQ-values.Inotherwords,theyexhibitapreferencefor porarytabletempQ(lines3-5).Incasenosuchstate𝑠′exists(line
actionsthathavepreviouslydemonstratedhigherrewardsacross 6),meaningthatthestate𝑠′ whichagent𝑘 iscurrentlyvisiting
19

## Page 7

CanCooperativeMulti-AgentReinforcementLearningBoostAutomaticWebTesting?AnExploratoryStudy ASE’24,October27-November1,2024,Sacramento,CA,USA
hasnotbeenvisitedbeforeinthetestingprocessoftheentiresys- Besides,toevaluatetheperformanceimprovementbroughtby
tem,thereisnoexperiencedataavailable.Therefore,agent𝑘relies thedatasharingmechanism,wealsoincludedabaselinemethod
solelyonitsownQ-tabletoestimatetheoptimalaction-valuefunc- thatrunsmultipleQ-learningagentswithoutanyinformationex-
tion,updating𝑄 𝑘(𝑠,𝑎)byfollowingtheQ-learningalgorithmin changing.WecallthisbaselineIQL𝑁 (IndependentQ-Learning[27]),
Equation(2)(line7).Additionally,thecontrollerchoosesanaction where𝑁 representsthenumberofagents.
fromitsactionspaceA𝑠′ ,byemployingthe𝜀-greedy(Equation3) Itisworthexplainingthatwedidnotrunmultipleinstances
strategyontheQ-valuesforstate𝑠′,denotedas𝑄 𝑘(𝑠′,·)(line8). ofWebExplor orQExploreinparallelforcomparisonduetotwo
Whentherewerepastexperiencesonstate𝑠′learnedbyother primaryreasons.First,themainfocusofourworkistodeviseagent
agents,theagent𝑘shouldupdateitsownpolicy.Inspiredbydouble cooperationstrategiestoimprovetheefficiencyandperformance
Q-learning[17],weupdatetheQ-valuesasfollows:
ofwebGUItesting.Hence,ouressentialtaskintheevaluationis
𝑄 𝑘(𝑠,𝑎)←𝛼[𝑟+ 𝛾
𝑙 𝑄𝑗∈
∑︁
tempQ
𝑄𝑗(𝑠′,a
𝑎
r
′
g
∈
m
A
a
𝑠′
x(𝑄 𝑘(𝑠′,𝑎′)))−𝑄 𝑘(𝑠,𝑎)] t
a
o
ge
c
n
o
t
m
c
p
o
a
o
r
p
e
e
M
ra
A
tio
R
n
G
(i
w
.e
i
.
t
,
h
th
a
e
m
IQ
u
L
lt
𝑁
i-a
a
g
p
e
p
n
r
t
o
a
a
p
ch
pr
m
oa
e
c
n
h
ti
w
on
it
e
h
d
o
a
u
b
t
o
e
v
ff
e
e
).
ct
S
i
e
v
c
e
-
+𝑄 𝑘(𝑠,𝑎) ond,bothWebExplor andQExploreleverageextramethods(e.g.,
(4) DFAorcontextualdatainputmethod)beyondRL,itwouldbeun-
where𝑙 isthelengthofthetempQtable.Itupdatesthe𝑄 𝑘(𝑠,𝑎)for fairtoMARG,inwhicheachagentonlyleveragesplainQ-learning
agent𝑘basedonreward𝑟,thediscountedfuturerewardsobtained algorithmstoguidewebpageexploration,ifwecompareitwith
fromtheotheragents’experiences,andthecurrentQ-valueitself. parallellyrunningmultipleinstancesofWebExplororQExplore.
ItcalculatestheaverageoftheQ-valuesfortheactionswiththe
highestvaluein𝑄 𝑘(𝑠′,·)amongtheotheragents’Q-tables.After 5.3 ResearchQuestions
updatingthepolicyforagent𝑘,thecontrollerwillchooseanaction ToevaluateMARG,weconductedexperimentstoinvestigatethe
tobeexecuted.Inordertomakeaninformeddecision,itrecalculates followingthreeresearchquestions:
theQ-valuesforeachactioninA𝑠′ basedontheexperiencesof
• RQ1(ToolPerformance):HowdoesMARGcomparewiththe
otheragentsonstate𝑠′(line12).Then,itutilizes𝜀-greedystrategy
state-of-the-artwebGUItestingmethods?Additionally,canco-
tochooseanactionon𝑄
𝑠
∗
′
(·)(line13).
operativeMARLtechniques(i.e.,MARG𝑁 andMARG𝑁)achieve
𝐶 𝐷
a better performance than independently executing multiple
5 ExperimentalSetup
agents(i.e.,IQL𝑁)?
5.1 ImplementationandEnvironment • RQ2(ComparisonofDataSharingSchemes):Isthereaper-
MARGcontainstwomaincomponents(Figure4):Theclient-side formancedifferencebetweenMARG𝑁 andMARG𝑁?Ifso,what
𝐶 𝐷
agentsareimplementedontopofSelenium-Java[2]forwebpage arethecontributingfactorsofthisdifference?
interactions;asfortheserverside,thecontrollerconsistsoftwo • RQ3(EffectofAgentNumbers):Howdoesthenumberof
Q-learningalgorithmsimplementedinpurePython,whilethedata agentsaffecttheperformanceof MARG?
isstoredinaMySQLdatabase.TheHTTPcommunicationisimple-
5.4 Configurations
mentedusingtheFlaskframework[1]asaRESTfulserver.
Regardingthetwomulti-agentQ-learningalgorithms,wede- Table2summarizesallcomparedapproaches.Duringtheexperi-
velopedtwoversionsofourproposedtool,namelyMARG𝑁 (i.e., ments,wefollowedthesettingsfromexistingwork[38,52],giving
𝐶
CentralizedQ-learningwithasharedQ-table)andMARG𝑁 (i.e., the same time budget of two hours to all these approaches. To
𝐷
DistributedQ-learningwithdataexchange),whichcorrespondto mitigaterandomness,werepeatedeachexperiment3timesand
thecentralizedQ-learningandthedistributedQ-learningschemes, calculatedtheaverageresults.
respectively.Here𝑁 representsthenumberofagents. TheparametersforWebExplorandQExploreweresetaccording
Weconductedalltheexperimentsonmultipledesktopdevices totherespectivepapers.AsforIQL𝑁,MARG𝑁,andMARG𝑁,we
𝐶 𝐷
withidenticalconfigurations,eachofwhichhasanInteli7-13700 settheparameters𝛼 =1,𝛾 =0.5,𝜀 =0.5.Theseparametervalues
CPUand32GBRAM.Thedevicesareconnectedwith1GbpsEther- havebeenevaluatedanddemonstratedgoodperformanceandsta-
nettoensurestablenetworkconditions.Duringtheexperiments, bilityinarecentempiricalstudy[11].InAlgorithm1,theinitial
weranallagentsinthesameMARLsystemonthesamedevicefor Q-valueissetto10.0basedonapilotexperiment.
bettercommunicationefficiency. ForRQ1andRQ2,thenumberofagentsinMARG’ssystemwas
settofive.AsforRQ3,weconductedexperimentsusingdifferent
5.2 BaselineApproaches numbersofagents,with𝑁beingsetto3,5,8,12and15,respectively.
ToevaluateMARG,wefirstselectedWebExplor[52]andQExplore
5.5 SubjectWebsites
[38],twostate-of-the-artwebGUItestingtools,asthebaseline
approaches. WebExplor [52] converts an HTML document to a Multi-agentapproachesaremoresuitablefortestinglarge-scale
sequenceoftagsandadoptsthegestaltpatternmatchingalgorithm websites(i.e.,theywouldbeanoverkillforsmall-sizedwebsites).
forstateabstraction.Itusesadeterministicfiniteautomaton(DFA) Forthisreason,weselectedeightpopularreal-worldwebsiteswith
toprovidehigh-levelguidance.QExplore[38]definesthestateof world-wideinfluencefromSemrushrankings[3]forourexperi-
awebapplicationasthesetofactions(e.g.,buttonclicks)ona ments.Inordertocomprehensivelyevaluatetheperformanceof
webpage,whichissimilartoMARG,andinvolvesacontextualdata MARGondifferenttypesofwebsites,werandomlyselectedweb-
inputmethodtogeneratetextualinputs. sitesfromdifferentcategories,withdetailsoftheeightwebsites
20

## Page 8

ASE’24,October27-November1,2024,Sacramento,CA,USA YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,
Table2:Detailsofthecomparedapproaches
Approach UniqueFeature State Reward 𝜸 𝜺 𝜶
WebExplor DFAguidance
(URL,tagsequence
√ 1 0.95 -
ofhtml_doc) Count(𝑠,𝑎,𝑠′)
QExplore Contextualdatainputmethod (𝐸1,𝐸2,...,𝐸𝑛)



𝑅
𝑅
√
m
n
C
e
a
g
o
x
u
a
1
t
n
i
t
v
(
e
𝑎)
i
i
i
f
f
f𝑠
C
C
o
o
is
u
u
n
n
n
o
t
t
(
(
t
𝑎
𝑎
v
)
)
a
=
>
lid
0
0 0.9×𝑒−|𝐴𝑠 1 ′ 0 |−1 0 1
IQL𝑁 IndependentlyrunmultipleQ-learningagents
MARG
C
𝑁 Centralizedmulti-agentQ-learningwithasharedQ-table (URL,𝐸1,𝐸2,...,𝐸𝑛) √
Cou
1
nt(𝑎)
0.5 0.5
MARG𝑁 Distributedmulti-agentQ-learningwithdataexchange
D
Table3:Detailsofsubjectwebsites (=626.1/254.4).Theincreaseintheexploredstatesandexecutedac-
tionscontributestotheimprovedtestingoutcomes:MARGdetects
Name Category URL
4.03and3.76timesmorefailuresthanthetwobaselinemethods.
WUT𝐴 Anonymous. Anonymous. WhencomparingMARG5 andMARG5 withthebaselineap-
toppr DistanceLearning https://www.toppr.com/ C D
Smadex AdvertisingandMarketing https://smadex.com/ proachIQL5,itshowsthattheperformanceof MARGsurpasses
Vuestic Education https://ui.vuestic.dev/ thatofthebaselineonmostwebsites.Forinstance,thereisa36.42%
YouTube Newspapers https://youtube.com/ (=(661.5-484.9)/484.9)improvementinthecapabilityofstateexplo-
GitHub SoftwareandDevelopment https://github.com/
rationfromtheaverageresults.Theimprovementisparticularly
GameSpot ComputerandVideoGames https://www.gamespot.com/
significantontheVuesticandTopprwebsites,exhibitinganimpres-
EatingWell FoodandBeverages https://www.eatingwell.com/
IKEA OnlineServices https://www.ikea.com/ sivegrowthof331%and550%intheexploredstates,respectively.
Wedidadeeperinvestigationtounderstandtheunderlyingrea-
sonforsuchsignificantdifferencesandfoundthatbothofthetwo
websites have numerous external links, which, due to network
listedinTable3.Wealsoincludedthewebsiteusedinthepilot
conditions,candelayagentexplorationsignificantly.Inourexper-
study(Section3),whichisanonymizedanddenotedasWUT .
𝐴 iment,such“riskyactions”canwastetimeandleadtoafailure
5.6 Metrics
stage.However,cooperativeMARLalgorithmscandecrease
theprobabilityofselectingriskyactions.Whenanagentselects
ConsideringthattheseRL-basedapproachesaredrivenbycurios- anactionthatmayresultinclickingonanexternallink,itprop-
ity,whereinthefundamentalprinciplerevolvesaroundexploring agatesthisinformationthroughQ-valueupdatestootheragents,
morewebpagestoincreasethepossibilityoffindingfailures,we greatlyreducingthechanceofre-clickingsuchlinksandthereby
evaluatedwebGUItestingapproachesfromtwoperspectives:ex- enhancingtheoverallperformanceof MARG.
plorationcapabilityandtestingeffectiveness.Intermsoftheexplo- WhileMARG5 andMARG5 demonstratedsuperiorperformance
rationcapability,weusedmetricsinspiredbytheevaluationofweb thanIQL5interm C sofstateexp D loration,IQL5executedmoreunique
crawlingmethods[29].Specifically,werecordedthenumberofex-
actionsonafewwebsites,suchasGitHub.However,theactual
ploredstates,detectedactions(includingexecutedones),andexecuted testingeffectivenessofIQL5stillfallsshortofMARG5 andMARG5,
uniqueactions.Duetothedifferentstateabstractionsamongthese
asshownbythenumberofdetectedfailures.
C D
comparedapproaches,weunifiedtheirstatesas(URL,𝐸1,𝐸2,...,𝐸 𝑛)
tostatisticallyanalyzethenumberofexploredstates.Forevaluating AnswertoRQ1:Comparedtothetwostate-of-the-arttools,
testingeffectiveness,wecollecteddetectedfailures,whichinvolves WebExplorandQExplore,MARG5 surpassesthemby4.34and
capturingandanalyzingthetriggeredcrashesandconsoleerrors 3.89times,respectively,inthenu D mberofexploredstates,lead-
duringthetestingprocess. ingtothedetectionofapproximatelythreetimesmorefailures.
Moreover,cooperativeMARLhelpsavoidunnecessaryrepetitive
6 ResultsandDiscussion behaviorsofwebtestingagents,resultingina36.42%increase
6.1 RQ1:ToolPerformance inthenumberofexploreduniquewebstates,comparedtoinde-
pendentlyrunningmultipleagents.
Theaveragedresultsamongthreerepeatedrunsaresummarized
inTable4,whereboldnumbersindicatethebestresults.Itcanbe
6.2 RQ2:ComparisonofDataSharingSchemes
observedthatrunningmultipleagentssignificantlyimprovesthe
coverageandefficiencyofthetests.Specifically,basedonaverage BasedonthedatapresentedintheTable4,distinctperformance
results,equippedwithfiveagents,MARG5 demonstratesexcellent advantagescanbeobservedforMARG5 andMARG5 acrossdiffer-
D C D
performanceacrossmostofthemetrics.Intermsofthenumber entsubjectwebsites.Tofurtherinvestigatetheimpactofthetwo
ofexploredstates,itsurpassesWebExplorandQExplorebyfactors datasharingschemesontheperformanceof MARG,wecompare
of4.34(=661.5/152.4)and3.89(=661.5/170.1),respectively.Asfor themfromtheperspectivesofcommunicationoverheadanddata
executeduniqueactions,thefactorsare3.03(=626.1/206.3)and2.46 propagationcapabilities.
21

## Page 9

CanCooperativeMulti-AgentReinforcementLearningBoostAutomaticWebTesting?AnExploratoryStudy ASE’24,October27-November1,2024,Sacramento,CA,USA
Table4:ComparisonofWebExplor,QExplore,IQL5,MARG5,andMARG5
C D
WebExplor QExplore
IQL5 MARG5 MARG5
WebExplor QExplore
IQL5 MARG5 MARG5
C D C D
ExploredStates(#) DetectedActions(#)
WUT 380.0 153.0 836.0 701.0 912.0 1334.0 1538.0 3442.7 3126.0 3169.0
𝐴
toppr 13.0 7.0 12.3 53.0 46.0 239.0 207.0 292.0 852.0 692.0
Smadex 53.0 101.0 322.3 703.3 590.7 407.0 555.0 539.3 556.7 562.3
Vuestic 83.3 26.7 42.7 273.0 283.3 347.3 194.7 264.0 1122.0 1169.3
YouTube 348.7 288.3 442.3 425.7 587.3 1946.0 1573.0 2261.0 2235.0 2382.3
GitHub 37.7 387.3 631.0 851.3 823.3 199.0 3718.3 10949.7 14611.6 14487.8
GameSpot 43.7 58.0 197.3 281.7 227.3 260.3 373.7 1132.5 1129.3 1062.7
EatingWell 381.0 427.7 1082.0 1296.7 1155.0 1319.3 1330.7 2133.3 2166.3 1909.5
IKEA 31.0 82.0 798.3 1318.7 1329 65.0 223.0 3008 2648.0 2786.3
Average 152.4 170.1 484.9 656.0 661.5 679.7 1079.3 2669.2 3160.8 3135.7
ExecutedUniqueActions(#) DetectedFailures(#)
WUT 343.5 341.0 1112.3 782.0 1168.0 13.0 8.3 28.0 30.3 42.0
𝐴
toppr 80.5 63.0 72.7 291.0 290.7 1.0 0.7 6.0 7.3 6.7
Smadex 120.0 332.0 391.3 376.3 405.3 1.0 2.0 3.0 4.0 1.7
Vuestic 201.7 89.0 145.3 616.0 695.0 6.7 4.7 25.3 29.3 39.7
YouTube 550.0 239.3 850.3 800.3 1085.7 35.3 33.0 71.0 59.3 72.7
GitHub 84.3 444.7 856.7 369.3 430.7 3.0 7.3 34.3 40.7 44.3
GameSpot 108.0 127.7 393.0 477.3 400.0 12.0 18.7 73.0 77.3 76.0
EatingWell 311.0 494.0 682.3 471.0 511.5 13.3 17.0 27.0 28.0 32.5
IKEA 58.0 160.0 874.7 596.7 648.0 3.0 3.0 31.0 32.0 39.7
Average 206.3 254.5 597.6 531.1 626.1 9.8 10.5 33.2 34.2 39.5
Tocomparethecommunicationoverhead,wecollectedthenum-
      
berofactionsexecutedbyMARGduringeachexperiment.The
      
resultsareshowninFigure6.Forinstance,inthreerepeatedexper-
      
iments,theaveragetotalnumberofactionsexecutedbytheentire
      
systemoffiveagentsinMARG5 is5,999,whilethatofMARG5
C D      
is8,219.ItcanbeobservedthatMARG5 generallyhasahigher
     
D
numberofactionexecutioncomparedtotheMARG5.Thisisbe-
     
C
causethereisonlyasingleglobalQ-tableinMARG5,wherethe      
C
controllerperformsactionselectionforeachagentandupdates  
thepolicythroughreadandwriteoperationsonthisQ-table.In
WUTA  W R S S U  6 P D G H [  9 X H V W L F  < R X 7 X E H  * L W + X E  * D P H 6 S R
 (
 W  D W L Q J : H O O  , . ( $
contrast,whenusingdistributedQ-learningwithdataexchange
(i.e.,Algorithm1),thecontrollermaintainscorrespondingQ-tables
foreachindividualagent,whichprovidesseveraladvantages:first,
regardingwriteoperations,thecontrolleronlyneedstoupdate
theQ-tableassociatedwiththeagentwithoutmodifyingotherQ-
tables;second,forreadoperations,itsolelyaccessestheQ-tablesof
otheragentsthatinvolverelevantstates,ratherthanaccessingall
Q-tables.Byreducingtheneedforglobalcommunication,MARG5
D
canperformpolicyoptimizationandactionselectionmore
efficiently,resultinginahighernumberofexecutedactions.
Tocomparethedatapropagationcapabilities,wecalculatedthe
ratioofthenumberofexploredstatestothenumberofexecuted
actions,andpresentedtheresultsinFigure7.Thehighertheratio,
thegreaterthenumberofstatesexploredunderthesamenumber
ofactions(i.e.,betterdatapropagationcapabilitiesandexploration
efficiency).Figure7showsthattheseratiosofMARG5 arehigher
C
comparedtoMARG5.ThisisbecauseMARG5 utilizesacentralized
D C
globalQ-table,whichstoresthecollectivehistoricalexperiences
of the group of agents. Therefore, for any agent, the transition
     V Q R L W F $  G H W X F H [ ( MARG5 C
MARG5
D
Figure6:ComparisonoftotalexecutedactionsofMARG5
C andMARG5
D
  
  
  
  
  
 
 
WUTA  W R S S U  6 P D G H [  9 X H V W L F  < R X 7 X E H  * L W + X E  * D P H 6 S R
 (
 W  D W L Q J : H O O  , . ( $
     R L W D 5  Q R L W F $  H W D W 6 MARGC 5
MARGD 5
Figure7:State-to-actionratiosofMARG5 andMARG5
C D
datafromotheragentscanbetreatedasifithasbeenacquiredby
itself,asagentscandirectlyaccesstheexperiencesofotheragents
throughthesharedQ-table.Onthecontrary,MARG5 exhibitsa
D
22

## Page 10

ASE’24,October27-November1,2024,Sacramento,CA,USA YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,
gradualdecreaseintheefficacyofinformationpropagationduring MARG15andMARG15withinthetwo-hourtimeframe.Wefound
C D
theinformationdisseminationprocess. thatthetotalnumberofactionsexecutedbyMARG15is72%ofthat
Apracticalimplicationoftheabovefindingisthatpractitioners by MARG15. Thisobservationsuggeststhat MAR C G𝑁 isbetter
andresearchersshouldconsiderthetrade-offbetweeninformation D D
suitedforscenariosinvolvingalargernumberofagents,es-
propagationcapabilitiesandcommunicationoverheadwhenchoos-
peciallywhentestingdynamicandcomplexwebsiteswhere
ingbetweenthecentralizedanddistributeddatasharingschemes.
efficientagentcollaborationisrequired.
Whiletheformerpossessesbetterinformationpropagationcapabil-
Lastly,wealsoattemptedtoconfigurealargernumberofagents.
ities,italsoincurshighercommunicationoverhead.Ontheother
However,thenumberofagentswillbeconstrainedbythe
hand,withinthesametimebudget,thelatterdemonstratessuperior
availablecomputationalresources.Weencounteredanout-of-
overallperformance,asindicatedbytheaverageresults.
memoryerrorwhenrunning20agentswithina2-hourtimebudget.
AnswertoRQ2:MARG
C
𝑁,withitscentralizednature,exhibits AnswertoRQ3:Asthesystemisconfiguredwithmoreagents,
superiorinformationpropagationcapabilities.However,itin- its testing performance generally improves. Due to the low
cursahighercommunicationoverheadduringthetestingpro- overhead of maintaining Q-tables, MARG𝑁 showcases supe-
cess.Incontrast,theMARG D 𝑁 algorithmexhibitsrelativelylower riorresultsthanMARG𝑁.Nevertheless,the D expansionofagent
overheadwhileupholdingagoodoverallperformance. C
numbersislimitedbytheavailablecomputationalresources.
6.3 RQ3:EffectofAgentNumbers
6.4 ThreatstoValidity
Utilizingamulti-agentsystemforwebGUItestingtasksintroduces
Theexperimentalresultsaresubjecttouncertaintiesarisingfrom
anewconfigurationitem:thenumberofagents𝑁.Weconfigured
networkissuesandinherentrandomnessinthealgorithm(e.g.,
varying𝑁 totestWUT inordertoinvestigatetheimpactofthe
𝐴 randomizationin𝜀-greedy).Toaddressthisissue,eachexperiment
numberofagentsonMARG’sperformance.Theselectionofthe
foreverysubjectwebsitewasconductedonthesamemachine,and
subjectwebsiteWUT wasbasedonitscomplexity,asshownin
𝐴 weattemptedtoensureconsistencyinnetworkconditionsduring
Table4withrelativelylargenumbersofdetectedstatesandactions.
testing.Moreover,eachexperimentwasconductedthreetimes.
AsdepictedintheFigure8,inmostcases,thetestingperfor-
Theevaluationof MARGwasconductedononlyninecommer-
manceofMARGexhibitsanupwardtrendasthenumberof
cialwebsites,whichmaynotberepresentativeofallpossibleweb
agentsincreases.However,theimprovementratiosarenotdirectly
applications.Thereisapotentialthreatthatourfindingsmaynot
proportionaltothenumberofagents.Forexample,asthenumber
generalizeacrossallreal-worldwebapplications.Tomitigatethis
ofagents𝑁 increasesfrom3to5(↑67%),8(↑167%),12(↑300%),and
threat,weselecteddifferenttypesofwebsites,manyofwhichare
15(↑400%),thequantityofexploredstatesofMARG𝑁 increases
C large-scaleandcomplex(e.g.,YouTube,GitHub,andIKEA).Ourex-
by20%,138%,140%,and146%,respectively.Similarly,theexplored
ploratorystudydemonstratesthepotentialofMARLinenhancing
statesofMARG𝑁 exhibitedincrementsof63%,138%,276%,and
D theefficiencyandperformanceofwebGUItesting.Movingfor-
211%correspondingly.Regardingtheresultsofdetectedfailures,as
ward,weplantorunoursystemonmorediversifiedandcomplex
𝑁 increasesfrom5to8,thenumberofdetectedfailuresbyMARG𝑁
D websitestofurtherassessandenhanceitsperformance.
slightlydecreases.ThisisunderstandableasMARGmayexplore
Furthermore,wefollowedanexistingempiricalstudy[11]and
different states with different numbers of agents and faults are
employedasingleconfigurationtosettheparametersoftheQ-
typicallynotevenlydistributedwithinwebapplications.When𝑁
learningalgorithmacrossalltools.Whilethisensuredconsistency,
furtherincreasesfrom8,thenumberofdetectedfailuresalsoin-
itcouldrestrictthethoroughevaluationoftoolperformancesbe-
creases.Theseresultsindicatethatincreasingthenumberofagents
causeofthepotentialimpactsofvaryingparametersettings.
generallybringsperformanceimprovement.However,duetothe
hugesearchspaceandtheinherentrandomnessinthebehaviors
7 RelatedWork
oftheRLagents,agreaternumberofagentsdoesnotalwayslead
tosignificantimprovementsintestingperformanceandtheextent 7.1 ReinforcementLearningforGUITesting
ofimprovementmayvaryacrossdifferentmetrics. RL-basedtechniquesarecapableoflearningandoptimizingtheex-
Additionally,intheFigure8,wecanobservethatasthevalue plorationstrategiesthroughcontinuousinteractionswiththeenvi-
of𝑁 variesfrom3to8,theexplorationcapabilityofMARG𝑁 in- ronment[33],whichmakesthempromisingtofacilitateintelligent
C
creasessignificantly.However,as𝑁 furtherincreasesto12and15, GUItesting.AutoBlackTest[25]isanRL-basedtestingtechniquefor
therateofimprovementinexplorationcapabilitygraduallyslows desktopapplications.IttreatsthecollectionofGUIelementsasits
down.Ontheotherhand,theexplorationcapabilityofMARG𝑁 is abstractedstateandcalculatesrewardbyGUIchanges.Bauersfeld
D
relativelystablewhen𝑁 changes.Thisindicatesthatasthenumber etal.[7]adoptedasimilarapproach,butwithaminordifference,
ofagentsreachesacertainthreshold,alongwithalargenumberof theyusedtheinverseofactionfrequenciesasareward.Thiscalcu-
exploredstatesandthesignificantlyexpandedQ-table,theinfor- lationmethodhasbeenusedinrecentworks(e.g.,WebExplor[52]
mationsharingeffectivenessofMARG𝑁 maydecline.Asdiscussed andQExplore[38]),whichtheyreferredtoas“curiosity”.Fanet
C
inSection6.2,maintainingalargeQ-tableinMARG𝑁 resultsinin- al.summarizedGUItestingtechniquesdrivenbyQ-learning[11].
C
creasedoverheadassociatedwithutilizingandupdatingtheQ-table. Theyhighlightedtheeffectivenessofconfigurationssuchasusing
Wefurtherinvestigatedthetotalnumberofexecutedactionsof elementcollectionsasstatesandcuriosityasrewards.Theyalso
23

## Page 11

CanCooperativeMulti-AgentReinforcementLearningBoostAutomaticWebTesting?AnExploratoryStudy ASE’24,October27-November1,2024,Sacramento,CA,USA
    
    
    
    
    
   
   
           
 1 X P E H U  R I  $ J H Q W V    
     H W D W 6  G H U R O S [ (
    
MARGc
MARGD     
    
    
    
    
    
           
 1 X P E H U  R I  $ J H Q W V    
(a)ExploredStates
     V Q R L W F $  G H W F H W H '
MARGc     
MARGD     
    
    
    
   
           
 1 X P E H U  R I  $ J H Q W V    
(b)DetectedActions
     V Q R L W F $  H X T L Q 8  G H W X F H [ ( MARGc
MARGD   
  
  
  
 
           
 1 X P E H U  R I  $ J H Q W V    
(c)ExecutedUniqueActions
     V H U X O L D )  G H W F H W H '
MARGc
MARGD
(d)DetectedFailures
Figure8:PerformanceofMARGwithdifferentnumbersoftestingagents
pointedoutthelimitationofasingleQ-learningagentintestinga andcollaborativewebservices.Forexample,Baietal.[6]proposed
large-scalewebsite.Toaddresstheslowexplorationchallenge,Mo- amulti-agentframework,MAST,aimingtofacilitatewebservice
bilioetal.proposed𝐺𝑇𝑃𝑄𝐿 [32],whereparallelQ-learningagents testinginacoordinatedanddistributedenvironment.Different
runindependentlyandsynchronizetheirQ-modelsperiodically. fromtheseexistingstudies,ourworkexplorestheuseofmulti-
Withthecontinuousdevelopmentofdeeplearningtechnology, agentreinforcementlearningmethodstoimprovetheefficiency
toolsthatutilizedeepreinforcementlearning(DRL)[22,30,31]for andeffectivenessofwebGUItesting.Ourmainfocusistodevise
GUItestinghaveemerged.AchallengeaddressedbyDRL-based practicalagentcooperationmechanismstoenabledatasharing
techniquesisabstractingcomplexGUIstates,a.k.a.,GUIembed- amongmultipleasynchronousRLagents.
ding.QDroid[45]createsavectoroflength4wheretheelements
holdthenumberofcomponents:Input,Navigation,ListandButton, 8 ConclusionandFutureWork
whichisaninputoftheDeepQ-Network.DQT[20]preserveswid-
TheprimarygoalofwebGUItestingistoexploredifferentpage
gets’structuralandsemanticinformationwithgraphembedding
statesandachieveahighcoveragesoastoincreasethechance
techniques,buildingafoundationforidentifyingsimilarstatesor
ofdetectingbugs.Assingle-agenttestingtechniquesstruggleto
actionsanddistinguishingdifferentones.
achievecomprehensivecoverage,whilemerelyparallelizingmul-
7.2 Multi-AgentSystems tipleagentscanleadtoredundancyinvisitedstates,ithighlights
thedemandforefficientcommunicationandcoordinationmech-
Recently,cooperativeMARLalgorithmshavegainedwideapplica-
anismsamongthetestingagents.Tothisend,wehavedesigned
tionsinvariousfields,whilemostofthemfocusonthecollaboration
MARG,thefirstautomaticwebGUItestingsystemdrivenbymulti-
ofmultipleQ-learningagents.Meloetal.[28]leveragedthecharac-
agentQ-learningalgorithms.Ourexperimentsdemonstratethat
teristicsofsparseinteractionstominimizethecouplingbetweendif-
MARGcanoutperformtwostate-of-the-artRL-basedwebtesting
ferentQ-learningagents.Specifically,eachagentemploysa“global”
techniques,WebExplorandQExplore,showingpromisingresultsof
Q-learningapproachinitsownresponsibleexplorationdomain,
MARL-basedGUItesting.
andusesa“local”Q-learningapproachwhencoordinatingwith
Inthefuture,weplantoenhanceMARGfromthreeaspects.
otheragents.Tofacilitatesuchcoordination,theyintroducedanad-
First,consideringthecomplexandhugestatespaceofdynamic
ditional“coordination”actionintheagent’sactionspace.Phamet
webpages,weplantoreplaceQ-learningalgorithmsinMARGwith
al.[36]proposedadistributedMARLalgorithmforunmannedaerial
DRLalgorithms[34]toimprovestateabstractionandvalueesti-
vehicle(UAV)teams.Thisalgorithmenablescooperativelearning
mation.Second,besidesourcurrentcollaborativestrategies,the
amongUAVstoachievecomprehensivecoverageofunknownin-
agentsinMARGcanbecoordinatedwithotheradvancedMARL
terestareaswhileminimizingtheoverlapbetweentheirfieldsof
algorithms,suchasVDN[41]orQMIX[37],toenhanceoverall
view.Forthispurpose,therewardforanindividualagentwillbe
performance.Third,theusersofcomplexwebsitesmayhavediffer-
penalizedbythenumberofoverlappingcellswiththeotheragents.
entroles(e.g.,administrators,storemanagers,andcustomersofan
Toaddresstheissueofstateexplosion,theyemployedeffective
E-commercewebsite).Testingsuchwebsiteswithmultipleagents
functionapproximationtechniquestohandletherepresentationof
ofthesamerolemaynotbeabletotriggercertainintricatebusiness
high-dimensionalstatespaces.
logic.Wealsoplantoinvestigatehowtocoordinatemultipleagents
Besidestheabovestudies,researchershavealsoexploredtesting
withdiversifiedrolestofurtherimproveMARG’sperformanceof
softwarewithmulti-agentsystems.Caietal.proposedFastbot[8],
testingwebapplicationsincomplexreal-worldscenarios.
inwhichmultipleagentsareresponsibleforconstructingaDAG
modelofanAndroidapptosupportmodel-basedtesting.Huoet
Acknowledgments
al.[18]proposedamulti-agenttestingenvironmentforwebappli-
cations.Theydividedthetaskofwebtestingintoseveralsubtasks, WewouldliketothanktheASE2024reviewersfortheirconstruc-
suchaswebpageretrieval,informationextraction,etc.Intheirsys- tivecommentsonthispaper.ThisworkissupportedbytheNa-
tem,thecoordinationandschedulingamongagentswereconducted tionalNaturalScienceFoundationofChina(GrantNos.61932021,
byseparateagents,namely,brokers.Similartaskdecomposition 62372219)andtheNationalKeyResearchandDevelopmentPro-
ideashavealsobeenappliedtotestingtasksinvolvingdynamic gramofChina(GrantNo.2019YFE0198100).
24

## Page 12

ASE’24,October27-November1,2024,Sacramento,CA,USA YujiaFan1,2,SinanWang1,ZebangFei2,YaoQin2,HuaxuanLi2,YepangLiu1,2,
References
[25] LeonardoMariani,MauroPezzè,OlivieroRiganelli,andMauroSantoro.2011.
[1] [n.d.]. Flask Documentation — flask.palletsprojects.com. https://flask. AutoBlackTest:atoolforautomaticblack-boxtesting.InProceedingsofthe33rd
palletsprojects.com/. [Accessed27-03-2024]. internationalconferenceonsoftwareengineering.1013–1015.
[2] [n.d.].SeleniumHQ/selenium:Abrowserautomationframeworkandecosystem. [26] LeonardoMariani,MauroPezzè,OlivieroRiganelli,andMauroSantoro.2014.
—github.com.https://github.com/SeleniumHQ/selenium/.[Accessed27-03-2024]. AutomatictestingofGUI-basedapplications.SoftwareTesting,Verificationand
[3] [n.d.].TopWebsitesintheWorld-MostVisited&PopularRankings-Semrush Reliability24,5(2014),341–366.
—semrush.com.https://semrush.com/website/top/. [Accessed01-04-2024]. [27] LaetitiaMatignon,GuillaumeJLaurent,andNadineLeFort-Piat.2012.Indepen-
[4] JeffreyLAdlerandVictorJBlue.2002.Acooperativemulti-agenttransporta- dentreinforcementlearnersincooperativemarkovgames:asurveyregarding
tionmanagementandrouteguidancesystem.TransportationResearchPartC: coordinationproblems.TheKnowledgeEngineeringReview27,1(2012),1–31.
EmergingTechnologies10,5-6(2002),433–454. [28] FranciscoSMeloandManuelaVeloso.2009.Learningofcoordination:Exploiting
[5] KaiArulkumaran,MarcPeterDeisenroth,MilesBrundage,andAnilAnthony sparseinteractionsinmultiagentsystems.InProceedingsofThe8thInternational
Bharath.2017. Abriefsurveyofdeepreinforcementlearning. arXivpreprint ConferenceonAutonomousAgentsandMultiagentSystems-Volume2.Citeseer,
arXiv:1708.05866(2017). 773–780.
[6] XiaoyingBai,GuilanDai,DezhengXu,andWei-TekTsai.2006.Amulti-agent [29] AliMesbah,EnginBozdag,andArieVanDeursen.2008. CrawlingAjaxby
basedframeworkforcollaborativetestingonwebservices.InTheFourthIEEE inferringuserinterfacestatechanges.In2008eighthinternationalconferenceon
WorkshoponSoftwareTechnologiesforFutureEmbeddedandUbiquitousSystems,
webengineering.IEEE,122–134.
[30] VolodymyrMnih,AdriaPuigdomenechBadia,MehdiMirza,AlexGraves,Tim-
andtheSecondInternationalWorkshoponCollaborativeComputing,Integration,
andAssurance(SEUS-WCCIA’06).IEEE,6–pp. othyLillicrap,TimHarley,DavidSilver,andKorayKavukcuoglu.2016.Asyn-
[7] SebastianBauersfeldandTanjaVos.2012.Areinforcementlearningapproach chronousmethodsfordeepreinforcementlearning.InInternationalconference
toautomatedguirobustnesstesting.InFastabstractsofthe4thsymposiumon onmachinelearning.PMLR,1928–1937.
search-basedsoftwareengineering(SSBSE2012).7–12. [31] VolodymyrMnih,KorayKavukcuoglu,DavidSilver,AndreiARusu,JoelVeness,
[8] TianqinCai,ZhaoZhang,andPingYang.2020.Fastbot:AMulti-AgentModel- MarcGBellemare,AlexGraves,MartinRiedmiller,AndreasKFidjeland,Georg
BasedTestGenerationSystemBeijingBytedanceNetworkTechnologyCo.,Ltd.. Ostrovski,etal.2015.Human-levelcontrolthroughdeepreinforcementlearning.
InProceedingsoftheIEEE/ACM1stInternationalConferenceonAutomationof nature518,7540(2015),529–533.
SoftwareTest.93–96. [32] MarcoMobilio,DiegoClerissi,GiovanniDenaro,andLeonardoMariani.2023.GUI
[9] PeterCorke,RonPeterson,andDanielaRus.2005.Networkedrobots:Flyingrobot TestingtothePowerofParallelQ-Learning.In2023IEEE/ACM45thInternational
navigationusingasensornet.InRoboticsResearch.TheEleventhInternational ConferenceonSoftwareEngineering:CompanionProceedings(ICSE-Companion).
Symposium:With303Figures.Springer,234–243. IEEE,55–59.
[10] AnnaIEsparcia-Alcázar,FranciscoAlmenar,MirellaMartínez,UrkoRueda,and [33] MiguelMorales.2020.Grokkingdeepreinforcementlearning.ManningPublica-
TVos.2016.Q-learningstrategiesforactionselectionintheTESTARautomated tions.
testingtool.6thInternationalConferenrenceonMetaheuristicsandnatureinspired [34] IanOsband,CharlesBlundell,AlexanderPritzel,andBenjaminVanRoy.2016.
computing(META2016)(2016),130–137. DeepexplorationviabootstrappedDQN.Advancesinneuralinformationprocess-
[11] YujiaFan,SiyiWang,SinanWang,YepangLiu,GuoyaoWen,andQiRong.2023.A ingsystems29(2016).
ComprehensiveEvaluationofQ-LearningBasedAutomaticWebGUITesting.In [35] MinxuePan,AnHuang,GuoxinWang,TianZhang,andXuandongLi.2020.
Reinforcementlearningbasedcuriosity-driventestingofAndroidapplications.
202310thInternationalConferenceonDependableSystemsandTheirApplications
(DSA).IEEE,12–23. InProceedingsofthe29thACMSIGSOFTInternationalSymposiumonSoftware
[12] RoyFielding,JimGettys,JeffreyMogul,HenrikFrystyk,LarryMasinter,Paul TestingandAnalysis.153–164.
Leach,andTimBerners-Lee.1999.Hypertexttransferprotocol–HTTP/1.1.Techni- [36] HuyXuanPham,HungManhLa,DavidFeil-Seifer,andAriaNefian.2018.Co-
calReport. operativeanddistributedreinforcementlearningofdronesforfieldcoverage.
[13] JakobFoerster,GregoryFarquhar,TriantafyllosAfouras,NantasNardelli,andShi- arXivpreprintarXiv:1803.07250(2018).
monWhiteson.2018.Counterfactualmulti-agentpolicygradients.InProceedings [37] TabishRashid,MikayelSamvelyan,ChristianSchroederDeWitt,GregoryFar-
oftheAAAIconferenceonartificialintelligence,Vol.32. quhar,JakobFoerster,andShimonWhiteson.2020.Monotonicvaluefunction
[14] Jakob Foerster, Nantas Nardelli, Gregory Farquhar, Triantafyllos Afouras, factorisationfordeepmulti-agentreinforcementlearning.JournalofMachine
PhilipHSTorr,PushmeetKohli,andShimonWhiteson.2017. Stabilisingex- LearningResearch21,178(2020),1–51.
periencereplayfordeepmulti-agentreinforcementlearning.InInternational [38] SalmanSherin,AsmarMuqeet,MuhammadUzairKhan,andMuhammadZohaib
conferenceonmachinelearning.PMLR,1146–1155. Iqbal.2023. QExplore:Anexplorationstrategyfordynamicwebapplications
[15] JayeshKGupta,MaximEgorov,andMykelKochenderfer.2017. Cooperative usingguidedsearch.JournalofSystemsandSoftware195(2023),111512.
multi-agentcontrolusingdeepreinforcementlearning.InAutonomousAgents [39] DavidSilver,AjaHuang,ChrisJMaddison,ArthurGuez,LaurentSifre,George
VanDenDriessche,JulianSchrittwieser,IoannisAntonoglou,VedaPanneershel-
andMultiagentSystems:AAMAS2017Workshops,BestPapers,SãoPaulo,Brazil,
May8-12,2017,RevisedSelectedPapers16.Springer,66–83. vam,MarcLanctot,etal.2016. MasteringthegameofGowithdeepneural
[16] EricAHansen,DanielSBernstein,andShlomoZilberstein.2004. Dynamic networksandtreesearch.nature529,7587(2016),484–489.
programmingforpartiallyobservablestochasticgames.InAAAI,Vol.4.709– [40] DavidSilver,JulianSchrittwieser,KarenSimonyan,IoannisAntonoglou,Aja
715. Huang,ArthurGuez,ThomasHubert,LucasBaker,MatthewLai,AdrianBolton,
[17] HadoHasselt.2010.DoubleQ-learning.Advancesinneuralinformationprocessing etal.2017. Masteringthegameofgowithouthumanknowledge. nature550,
systems23(2010). 7676(2017),354–359.
[18] QingningHuo,HongZhu,andSueGreenwood.2003.Amulti-agentsoftware [41] PeterSunehag,GuyLever,AudrunasGruslys,WojciechMarianCzarnecki,Vini-
engineeringenvironmentfortestingWeb-basedapplications.InProceedings27th ciusZambaldi,MaxJaderberg,MarcLanctot,NicolasSonnerat,JoelZLeibo,Karl
Tuyls,etal.2017.Value-decompositionnetworksforcooperativemulti-agent
AnnualInternationalComputerSoftwareandApplicationsConference.COMPAC
2003.IEEE,210–215. learning.arXivpreprintarXiv:1706.05296(2017).
[19] YavuzKoroglu,AlperSen,OzlemMuslu,YunusMete,CeydaUlker,TolgaTan- [42] RichardSSuttonandAndrewGBarto.2018.Reinforcementlearning:Anintro-
riverdi,andYunusDonmez.2018.QBE:QLearning-basedexplorationofandroid duction.MITpress.
applications.In2018IEEE11thInternationalConferenceonSoftwareTesting,Veri- [43] MingTan.1993.Multi-agentreinforcementlearning:Independentvs.cooperative
ficationandValidation(ICST).IEEE,105–115. agents.InProceedingsofthetenthinternationalconferenceonmachinelearning.
[20] YuanhongLan,YifeiLu,ZhongLi,MinxuePan,WenhuaYang,TianZhang,and 330–337.
XuandongLi.2024.DeeplyReinforcingAndroidGUITestingwithDeepRein- [44] ThiAnhTuyetVuongandShingoTakada.2018.Areinforcementlearningbased
forcementLearning.InProceedingsofthe46thIEEE/ACMInternationalConference approachtoautomatedtestingofandroidapplications.InProceedingsofthe9th
onSoftwareEngineering.1–13. ACMSIGSOFTInternationalWorkshoponAutomatingTESTCaseDesign,Selection,
[21] ScottMLewandowski.1998. Frameworksforcomponent-basedclient/server andEvaluation.31–37.
computing.ACMComputingSurveys(CSUR)30,1(1998),3–27. [45] ThiAnhTuyetVuongandShingoTakada.2019. SemanticAnalysisforDeep
[22] TimothyPLillicrap,JonathanJHunt,AlexanderPritzel,NicolasHeess,TomErez, Q-NetworkinAndroidGUITesting..InSEKE.123–170.
YuvalTassa,DavidSilver,andDaanWierstra.2015. Continuouscontrolwith [46] Hoi-ToWai,ZhuoranYang,ZhaoranWang,andMingyiHong.2018.Multi-agent
deepreinforcementlearning.arXivpreprintarXiv:1509.02971(2015). reinforcementlearningviadoubleaveragingprimal-dualoptimization.Advances
[23] MichaelLLittman.1994.Markovgamesasaframeworkformulti-agentrein- inNeuralInformationProcessingSystems31(2018).
forcementlearning.InMachinelearningproceedings1994.Elsevier,157–163. [47] ChristopherJCHWatkinsandPeterDayan.1992.Q-learning.Machinelearning
[24] SergioValcarcelMacua,JianshuChen,SantiagoZazo,andAliHSayed.2014. 8(1992),279–292.
Distributedpolicyevaluationundermultiplebehaviorstrategies. IEEETrans. [48] YaodongYangandJunWang.2020.Anoverviewofmulti-agentreinforcement
Automat.Control60,5(2014),1260–1274. learningfromgametheoreticalperspective. arXivpreprintarXiv:2011.00583
(2020).
25

## Page 13

CanCoop,erativeMulti-AgentReinforcementLearningBoostAutomaticWebTesting?AnExploratoryStudy ASE’24,October27-November1,2024,Sacramento,CA,USA
[49] ShengchengYu,ChunrongFang,YexiaoYun,andYangFeng.2021. Layout [51] KaiqingZhang,ZhuoranYang,HanLiu,TongZhang,andTamerBasar.2018.
andImageRecognitionDrivingCross-PlatformAutomatedMobileTesting.In Fullydecentralizedmulti-agentreinforcementlearningwithnetworkedagents.
2021IEEE/ACM43rdInternationalConferenceonSoftwareEngineering(ICSE). InInternationalConferenceonMachineLearning.PMLR,5872–5881.
1561–1571. https://doi.org/10.1109/ICSE43902.2021.00139 [52] YanZheng,YiLiu,XiaofeiXie,YepangLiu,LeiMa,JianyeHao,andYangLiu.
[50] KaiqingZhang,ZhuoranYang,andTamerBaşar.2021.Multi-agentreinforce- 2021.Automaticwebtestingusingcuriosity-drivenreinforcementlearning.In
mentlearning:Aselectiveoverviewoftheoriesandalgorithms. Handbookof 2021IEEE/ACM43rdInternationalConferenceonSoftwareEngineering(ICSE).
reinforcementlearningandcontrol(2021),321–384. IEEE,423–435.
26

