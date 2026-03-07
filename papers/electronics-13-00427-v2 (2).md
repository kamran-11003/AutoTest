# Electronics-13-00427-V2 (2)

**Source:** electronics-13-00427-v2 (2).pdf  
**Converted:** 2026-01-26 09:22:54

---

## Page 1

electronics
Article
A Reinforcement Learning Approach to Guide Web Crawler to
Explore Web Applications for Improving Code Coverage
Chien-HungLiu1,* ,ShingchernD.You1 andYing-ChiehChiu2
1 DepartmentofComputerScienceandInformationEngineering,NationalTaipeiUniversityofTechnology,
Taipei106344,Taiwan;scyou@ntut.edu.tw
2 PhisonElectronicsCorp.,No.1,QunYiRd.,Jhunan,MiaoliCounty350,Taiwan;andrew_chiu@phison.com
* Correspondence:cliu@ntut.edu.tw
Abstract:Webcrawlersarewidelyusedtoautomaticallyexploreandtestwebapplications.However,
navigating the pages of a web application can be difficult due to dynamic page generation. In
particular,theinputsforthewebformfieldscanaffecttheresultingpagesandsubsequentnavigation.
Therefore,choosingtheinputsandtheorderofclicksonawebpageisessentialforaneffectiveweb
crawlertoachievehighcodecoverage.Thispaperproposesasetofactionstoquicklyfillinwebform
fieldsandusesreinforcementlearningalgorithmstotrainaconvolutionalneuralnetwork(CNN).The
trainedagent,namediRobot,canautonomouslyselectactionstoguidethewebcrawlertomaximize
codecoverage. Weexperimentallycompareddifferentreinforcementlearningalgorithms,neural
networks,andactions.TheresultsshowthatourCNNnetworkwiththeproposedactionsperforms
betterthanotherneuralnetworksintermsofbranchcoverageusingtheDeepQ-learning(DQN)or
proximalpolicyoptimization(PPO)algorithm.Furthermore,comparedtopreviousstudies,iRobot
canincreasebranchcoveragebyabout1.7%whilereducingtrainingtimeto12.54%.
Keywords:webcrawler;reinforcementlearning;softwaretesting;codecoverage
Citation:Liu,C.-H.;You,S.D.;Chiu, 1. Introduction
Y.-C.AReinforcementLearning Crawl-basedapproachesarecommonlyusedforautomaticallycrawlingandtesting
ApproachtoGuideWebCrawlerto webapplications. Ithasbeenappliedtovarioustypesofwebapplicationtesting, such
ExploreWebApplicationsfor asregressiontesting,compatibilitytesting,andsecuritytestingforwebapplications[1].
ImprovingCodeCoverage.Electronics
Particularly,theapproachusesacrawlersuchasCrawljax[2]thatcandynamicallyinteract
2024,13,427. https://doi.org/
withawebapplication,exercisetheuserinterfaceelementsofthewebapplication,and
10.3390/electronics13020427
generateastate-basedmodelrepresentingpotentialuserinteractionstovalidatedesired
AcademicEditor:Mohamed propertiesoftheapplication[3].
WiemMkaouer Whilecrawl-basedapproachesholdpromisefortestingwebapplications,theinput
data required by the crawler to explore dynamic web applications is often generated
Received:2November2023
randomly or prepared manually, leading to inefficiency and high costs. This becomes
Revised:17January2024
particularlychallengingwhenconsideringtheimportanceofcodecoverageinsoftware
Accepted:17January2024
testing of an application under test (AUT). Code coverage is a key metric in software
Published:19January2024
testing, indicating the extent to which the source code of the AUT is executed during
testing. AccordingtoWikipedia,“Aprogramwithhightestcoveragehasmoreofitssource
codeexecutedduringtesting,whichsuggestsithasalowerchanceofcontainingundetected
Copyright: © 2024 by the authors. softwarebugscomparedtoaprogramwithlowtestcoverage”[4]. Specifically,statement
Licensee MDPI, Basel, Switzerland. and branch coverage aretwo widely-used metrics insoftware testing, representingthe
Thisarticleisanopenaccessarticle percentageofexecutedstatementsorbranchesofcontrolstructuresintheAUT.Branch
distributed under the terms and coverageisthepercentageofbranches(decisionpoints)thatareexecutedbyatestsuite.
conditionsoftheCreativeCommons Branchcoverageisstrongerandsubsumesstatementcoverage.Addressinghowtogenerate
Attribution(CCBY)license(https:// andselecttestinputsforawebcrawlertoenhancecodecoverageoftheexploredAUT
creativecommons.org/licenses/by/ becomesasignificantchallengeinthiscontext.
4.0/).
Electronics2024,13,427.https://doi.org/10.3390/electronics13020427 https://www.mdpi.com/journal/electronics

## Page 2

EElleeccttrroonniiccss 22002244,, 1133,, xx FFOORR PPEEEERR RREEVVIIEEWW 22 ooff 2233
E lectronics 2024, 13, x FOR PEER REVIEW 2 of 23
Electronics2024,13,427 2of22
ggeenneerraattee aanndd sseelleecctt tteesstt iinnppuuttss ffoorr aa wweebb ccrraawwlleerr ttoo eennhhaannccee ccooddee ccoovveerraaggee ooff tthhee eexxpplloorreedd
generate and select test inputs for a web crawler to enhance code coverage of the explored
AAUUTT bbeeccoommeess aa ssiiggnniifificcaanntt cchhaalllleennggee iinn tthhiiss ccoonntteexxtt..
AUT becomes a significant challenge in this context.
CC
CC
oo
oo
nn
nn
ss
ss
idi
ii
d
dd
ee
ee
rr
rr
a a
aa
w w
ww
ee
ee
bb
bb
a a
aa
pp
pp
pp
pp llill icii
c
cc
aa
aa ttitt
oi
ii
o
oo
nn
nn
w w
ww
iti
ii
ht
tt
h
hh
t
thtt
h
hh
ee
ee
s s
ss
imi
ii
m
mm
pp
pp
lel
ll
e
ee
p p
pp
aa
aa
gg
gg
ee
ee
i ni
ii
n
nn
F F
FF iigii
g
gg
uu
uu rrerr
e
ee
1 1
11
..
..
TT
TT
hh
hh
ee
ee
pp
pp
aa
aa
gg
gg
ee
ee
hh
hh
aa
aa
ss
ss tttt
ww
ww
oo
oo uuuu ssss eeee
rr
rr
--
--
iinii n nn ttett e ee rr ra r a aa cc ct c it tt ni ii n nn gg gg e e el e el ll e em e m mm eenee n nn tst tt :s ss : :: a a aa nn nn a a aa gg gg ee ee i inii n nn pp pp uu uu tt tt f fiififi ee ee ldl ll d dd a a aa nn nn dd dd a a aa nn nn i inii n nn iitii titt ai ii a aa lll ll yl ll y yy d d dd isi ii sass a ab a b bb lel ll edee d dd N N NN EE EE XX XX TT TT b b bb uu uu tttt tttt oo on o n n. n . .. W W WW hh hh ee ee nn nn t t tt hh hh ee ee
uu uu ss ss ee ee rr rr e e ee nn nn tet tt e er e sr rr s ss a a aa v v va v alaa ildll i ii d dd a ga aa eg gg e ev e av vv la au a l ll eu uu ,e ee t, ,h , t te t h hh Ne ee NENN XE EE TX XX bT TT u b bb ttu uu ott tttt no oo in ns n ei ii s sn s ae ee bn nn la aa eb bb dl ll e ee sd do d ts ss ho oo a t tt t h hh tahaa t te t t tt uh hh se ee e uruu scss eaee rnrr c cc na aa an nn v ninn ga aa av vv tei ii g gg ta ao a t tt etee h t tt eo oo
nt tt hehh xe ee t n nn pe ee ax xx gt tt e p pp ba aa gygg e ee c blbb iycyy k c cc ilnll i ii cgcc k kk ti ii hn nn eg gg b t tt h hu h e et e t bobb nu uu tt tttt (Fo oo in nn g u( (( F FF rieii g gg 2u uu )r r. r e ee I 2f22 ) )) t. .. h I II ef ff t tu t h hh se ee e ru uu sess e en e r rr t e e ee rn nn st tt eaee rnrr s ss i a aa nn nn v ai ii n nn liv vd v a aa al ll i ii gd dd e a aa vg gg ae ee l uv vv ea aa ,l ll u uu sue ee , ,c , shss u uu ac cc sh hh
− a aa s s1 s −(−− F1 11 i g( (( FuFF irii g ge g u uu 3r rr )e ee o 3r33 ) )) a o oo nr rr o na aa - ninn no oo tnenn g- -- i ie i n nn r,t tt e ee ag gg ne ee er rr ,r,, r a ao a n nn r me ee r rr er rr so oo sr rr a gm mm ee ee is ss s s ss pa aa rg gg oe ee m i ii spss tp pp erdrr o oo ,m mm anp pp dt tt e ee td dh d ,e,, a aN a n nn Ed dd X t tt Th hh e eb e uN NN ttE EE oXnXX T TT re bmbb u uu att tttt ino oo sn nn
drr iee smm abaa lie inn dss . dd Tio issaa nbb all vee idd g.. a TT teoo t hnn iaa svv piigg aaa gtt eee , ti t thh iii sss spp uaa fgg fiee c,, i eiitn t it iss i fssut u hffiffi ecc cii ree ann wtt lii eff r tthe h nee t ce crr ras aww all vee arr l iee dnntv tee arr lss u ae a vf v oaa rllii tdd h evvaa all guu eee
remains disabled. To navigate this page, it is sufficient if the crawler enters a valid value
ffi f eoo lrr d tthh anee d aagg thee e fifi neelc ldd li caa knn sdd t htthh eee Nnn E cc Xllii Tcckk bss u tt thh teo e nNN ,EE asXXTt T w bb ouu utttt soo enn r-,, i aa nss t e tt rww acoo t iuu nss geere r-- lie inn mttee err naa tcc sttio inn fgg t h ee ellee pmm aeg enn ett wss oo ilff l tt bhh eee
for the age field and then clicks the NEXT button, as two user-interacting elements of the
pppeaargfgoeer mwweiilldll .bbHee oppweerreffvooerrmrm,eferddo..m HHtoohwweeepvveeerrrs,,p fferrcootmimv e tthhoeef tppeeestrrissnppgee,ccttthiivveeev ooaflfi dtteesasttniindnggi,,n ttvhhaeel i dvvaaalligidde aavnnadldu ieinnsvvaaanllididd
page will be performed. However, from the perspective of testing, the valid and invalid
tahaggeeee svvsaaellnuuteeiass l aacnnoddm ttbhhieen aeetssissoeennnottiifaatllh cceooammgbbeiiinnnaapttuiiootnna noodff ttchhlieec kaaggeeev eiinnnpptuuotft NaannEddX ccTlliibcckuk t eetovvneennmtt uoofsf tNNbEEeXXexTTe bbrcuuistttteoodnn
age values and the essential combination of the age input and click event of NEXT button
tmomeuunsssttu bbreee etehxxaeetrrctchiisseeecddo tdtooe eethnnassutuhrreea ntthhdaaletts tththheee ccioonddpeue ttthhagaatet hhvaaanlnuddelleeisss attdhheeeq iiunnapptuueltty aacggoeev vvearaelluduee( iii.ses . a,aeddxeeeqqcuuuaatetteedll)yy.
must be exercised to ensure that the code that handles the input age value is adequately
Tcchooevvreeerrfeoedrde ,((iit..oee..a,, ceehxxieeeccvuuettbeededt))t..e TTrhhcoeedrreeeffocoorreve,,e ttrooa g aaecc,hhtihieeevvceer babweettttleeerrr mccooaddyeen cceooevvdeetrroaaggineet,,e ttrhhaeec t ccwrraaiwtwhlletehrr e mmpaaayyg ennveeeieadd
covered (i.e., executed). Therefore, to achieve better code coverage, the crawler may need
mttoou iilntnitpteelrreaasccett q wwuiiettnhhc ttehhseeo ppfaauggseee r vvaiiacat mimonuusllt,tiisppulleceh sseeaqqsuu<eenangcceeess= oo2ff 5 uu,ssNeerrE aXaccTtt:iioocnlniscs,k, ssauubcclehh = aasst r <<u aeagg>ee; =<= 22a55g,,e NN=EE−XX1TT,::
to interact with the page via multiple sequences of user actions, such as < age = 25, NEXT:
NccllEiiccXkkTaa:bbcllleiec k== a ttbrrulueee= >>f;; a <<l s aaegg>ee; ==< −−a11g,,e NN=EE“XXSTtTr::i nccgllii”cc,kkNaabbEllXee T ==: fcfaalillcsskeea >>b;;l e<< =aaggfaeel s==e ““>SStitnrriinnogrgd””e,, rNNtoEEXXcoTTv:: e ccrlliiaccskkmaabballneey ==
clickable = true >; < age = −1, NEXT: clickable = false >; < age = “String”, NEXT: clickable =
pffraaollsgseer a >>m iinmn oionrrgddeelorr g ttiooc sccoionvvetehrr e aassso mmuraacnneyyc oppdrreooggarsraapmmomsmsiiibnnlgge. llooggiiccss iinn tthhee ssoouurrccee ccooddee aass ppoossssiibbllee..
false > in order to cover as many programming logics in the source code as possible.
FFF iig igg uuu rre ree 1 11 ... A AA s ss iim imm ppp lle lee w ww eee bbb p pp aaa ggg eee i in inn t th thh eee i niinn itiiti t aiiaa lll s ss tta taa tte tee ...
Figure 1. A simple web page in the initial state.
FFiigguurree 22.. AA ssiimmppllee wweebb ppaaggee iinn aa ssttaattee aafftteerr rreecceeiivviinngg aa vvaalliidd iinnppuutt..
FFiigguurree 22.. AA ssiimmppllee wweebb ppaaggee iinn aa ssttaattee aafftteerr rreecceeiivviinngga av vaalliidd iinnppuutt..
FFiigguurree 33.. AA ssiimmppllee wweebb ppaaggee iinn aa ssttaattee aafftteerr rreecceeiivviinngg aann iinnvvaalliidd iinnppuutt..
Figure 3. A simple web page in a state after receiving an invalid input.
Figure3.Asimplewebpageinastateafterreceivinganinvalidinput.
EExxiissttiinngg wweebb ccrraawwlleerrss rreellyy oonn rraannddoommllyy ggeenneerraatteedd oorr mmaannuuaallllyy pprreeppaarreedd iinnppuuttss,,
EExxiissttiinnggw weebbc rcarwawlelresrrse rlyeloyn orna nrdaonmdolymglyen geeranteerdatoerdm oarn muaalnlyupalrleyp aprreedpainrpedu tsin,pleuatds-,
lleeaaddiinngg ttoo iinneeffifficciieennccyy aanndd hhiigghh ccoossttss iinn eexxpplloorriinngg aanndd tteessttiinngg ddyynnaammiicc wweebb aapppplliiccaattiioonnss..
ilnegadtoinign etoffi icnieenfficcyieanncdy haingdh hcoigshts cionsetsx pinlo erxinpgloarnindgt easntdin tgesdtyinnga mdyicnawmebica wpepbli caaptpiolnicsa.tTiohniss.
TThhiiss ssttuuddyy iiss mmoottiivvaatteedd bbyy tthhee nneeeedd ffoorr aann iimmpprroovveedd aapppprrooaacchh,, uuttiilliizziinngg aa rreeiinnffoorrcceemmeenntt
sTtuhdisy sitsumdyo tiisv matoetdivbaytetdh ebnye tehde fnoereadn fiomr panro ivmedpraopvperdo aacphp,ruotaiclihz,i nugtilaizrieningf ao rrceeimnfeonrctelemaernn-t
lleeaarrnniinngg ((RRLL)) [[55]] aaggeenntt ccaappaabbllee ooff pprroovviiddiinngg iinnppuutt aaccttiioonnss ttoo gguuiiddee wweebb ccrraawwlleerrss iinn iinntteerr--
ilnegar(nRiLn)g[ (5R]La)g [e5n]t acgaepnatb claepoafbplero ovfi dpirnogviidnipnugt iancptiuotn ascttoiognus itdoe gwueidbec wraewbl ecrrsawinleinrst eirna icntitnegr-
aaccttiinngg wwiitthh wweebb ppaaggeess.. TThhee ggooaall iiss ttoo aauuttoommaattee aanndd eennhhaannccee tthhee eexxpplloorraattiioonn ooff wweebb aappppllii--
wacitthinwg ewbitpha wgeesb. Tphageegso. aTlhies gtooaalu itso tmo aatuetaonmdaeten hanandc eenthhaenecxep tlhoer aetxiopnloorfatwioenb oafp wpleibca atpiopnlsi-
ccaattiioonnss uunnddeerr tteesstt eeffifficciieennttllyy,, uullttiimmaatteellyy iinnccrreeaassiinngg ccooddee ccoovveerraaggee dduurriinngg ccrraawwlliinngg aanndd
ucnatdioernst eustndefefirc tieesntt leyffi, ucliteinmtlayt,e luyltiinmcaretealsyin ignccroedaesincogv ceordage ecdovuerrinaggec rdauwrilningg caranwdltihnegr eabnyd
tthheerreebbyy aacchhiieevviinngg bbeetttteerr tteesstt aaddeeqquuaaccyy..
atchheireevbiyn gacbheitetverintges bteattdeerq tueasct ya.dequacy.
To realize this objective, an RL agent, which we call iRobot, is utilized to select a
sequenceofactionstoguidecrawlers’interactionswithwebpages,aimingtomaximize
thecodecoverageoftheAUT.Specifically,adesignofactionsisproposedforiRobottofill

## Page 3

Electronics2024,13,427 3of22
allinputfieldsofawebformusingasingleactiontosimulatethebehaviorofhumantester
andhelpthetrainingconvergefaster. Additionally,thedesignofactionsenablesiRobotto
automaticallyselectbothvalidorinvalidvaluesforinputfieldstoincreasecrawlingcode
coverage,ratherthanrandomlygeneratinginputvaluesormanuallyselectingtheinputs
inadvance. Furthermore,aconvolutionalneuralnetwork(CNN)isalsopresentedtotrain
theiRobot. Specifically,theCNNtakestheDocumentObjectModel(DOM)sourcecode
ofawebpageasinputandgeneratescorrespondingactionstoguidethewebcrawlerin
exploringtheAUT.Moreover,anenvironmenthasbeenspecificallydesignedforiRobotto
supportdifferentreinforcementlearningalgorithmsandneuralnetworkssothatwecan
studytheireffectsonimprovingthecodecoverageofthecrawler.
Toevaluatetheeffectivenessoftheproposedapproach,severalexperimentsarecon-
ductedusingthedesignofactionsandCNNnetwork. Theexperimentalresultsindicate
thattheproposedapproachispromising. Theenvironmentsupportingmultiplereinforce-
mentlearningalgorithmsandneuralnetworksprovestobeuseful. Additionally,thestudy
demonstratestheeffectivenessofthedesignofactioncombinedwithourCNNnetworkin
helpingthecrawlerachievehighercodecoveragecomparedtoearlierwork[6].
Therestofthepaperisorganizedasfollows: Section2brieflyreviewsrelatedwork.
Section3presentstheproposedapproachandthedesignofiRobot. Section4describesand
discussestheexperimentalresults. Concludingremarksandfutureworkarepresented
inSection5.
2. RelatedWork
Reinforcementlearningtechniqueshavebeensuccessfullyappliedtovariousfields[7–10].
Insoftwaretesting,Waqaretal.[11]proposedareinforcementlearning-basedmethodology
fortestsuiteprioritization.Theirresultsshowpromiseindetectingfaultsinregressiontesting.
However,theapplicationofRLtowebapplicationtestingisstillinitsearlystages.Existing
researchisstillverylimited.Thestudiesrelatedtothisworkarebrieflyreviewedbelow.
Linetal.[12]proposedanatural-languageapproachforcrawling-basedwebapplica-
tiontesting. Basically,themethodextractsandrepresentstheattributesofaDOMelement
and its nearby labels as a vector. The vector is transformed into a multi-dimensional
real-numbervectorbyusingaseriesofnatural-languageprocessingalgorithmssuchas
bag-of-words. Theapproachthenusesthesemanticsimilaritybetweenthetrainingcorpus
and the transformed vector to identify an input topic for the DOM element. Based on
theidentifiedtopic,theinputvalueoftheelementcanbeselectedfromapre-established
databank. Theexperimentalresultsshowthattheproposedapproachhascomparableor
betterperformancecomparedtotraditionalrule-basedtechniques.
Groce [13] used an adaptation-based programming (ABP) approach that utilizes
reinforcementlearningtoautomaticallygeneratingtestinputs. Specifically,theapproach
generatestestinputsforaJavaprogramundertest(PUT)bycallingtheABPlibraryto
exposenewbehaviorofthePUT,withthegoalofoptimizingtherewardbasedonincreases
intestcoverage.Comparedwithrandomtestingandshapeabstractionfortestingcontainer
classes,theexperimentalresultsshowthattheproposedapproachisquitecompetitive.
Carino and Andrews [14] proposed an automated approach based on ant colony
optimization(ACO)totestapplicationGUIs. Specifically,theapproachpresentsanant
colonyalgorithmcombinedwithQ-learning,calledAntQ.Itgenerateseventsequencesto
traversetheGUIsandusesthenumberofGUIstatechangescausedbytheeventsasthe
optimizationgoal. Theexperimentalresultsshowthat,comparedwithrandomtestingand
thenormalantcolonyalgorithm,AntQcanachievebetterstatementcoverageandexhibits
betterfault-findingability.
Kimetal.[15]proposedanapproachusingreinforcementlearningtoreplacehuman
designedmetaheuristicalgorithmsinsearch-basedsoftwaretesting(SBST)method. Ba-
sically,theSBSTalgorithmstrytofindanoptimalsolutionfortestdatagenerationbased
onfeedbackfromthefitnessfunction. Theresearchersformulateasearch-basedtestdata
generationproblemasanRLenvironmentandtrainanRLagentusingdoubledeepQ-

## Page 4

Electronics2024,13,427 4of22
networks(DDQN).Thefitnessvalueisusedastherewardfortheagent. Therefore,when
theagentmakesanactionbycreatinganewcandidatesolutiontomaximizethecumulative
reward,thefitnessvalueofthesolutioncanbeminimized. Theexperimentalresultsshow
thattheproposedapproachisfeasibleandcanachieve100%branchcoveragefortraining
functionswritteninClanguage.
Liu et al. [16] proposed an incremental and interactive web crawler called GUIDE
that can be guided by user-supplied directives to iteratively explore a web application.
Specifically,GUIDEactivelyaskstheuserfordirectivestoexplorewebpageswhenitfinds
aninputfieldratherthanpassivelyacceptingtheuser’sinstructions. Theexperimental
resultsshowthatGUIDEcanincreasecodecoveragecomparedtotraditionalwebcrawlers.
However,GUIDEstillrequireshumaninterventiontoprovideinputsduringcrawling.This
workisanattempttousereinforcementlearningtechniquestotrainanagenttoprovide
inputsandguidewebcrawlerstoachievebettercodecoverage.
Zhengetal.[17]presentedanautomaticend-to-endwebtestingframeworknamed
WebExplortoenableadaptiveexplorationofwebapplications. Inparticular,WebExplor
adoptsreinforcementlearningtogeneratedifferentactionsequencestodiscovernewweb
pages. Acuriosity-drivenrewardfunctionandaDFAareusedtoprovidelow-leveland
high-level guidance for RL exploration, respectively. The DFA is a deterministic finite
automatonthatrecordsglobalvisitinformationduringexploration. IfWebExplorcannot
discoveranewstatewithinacertainamountoftime,itselectsapathfromtheDFAbased
on curiosity and resumes exploration. The experimental results show that WebExplor
cansignificantlyimprovefaultdetectionrate,codecoverage,andefficiencycomparedto
state-of-the-arttechniques.
Liuetal.[18]proposedanRLapproachforworkflow-guidedexploration. Theap-
proach aims to alleviate the overfitting problem when training an RL agent to perform
web-basedtasks[19]suchasbookingaflightbymimickingexpertdemonstrations. Par-
ticularly,theapproachincludeshigh-levelworkflowsthatcanlimittheallowableactions
ateachtimestepbypruningthosebadexplorationdirections. Thisallowstheagentto
discoversparserewardsfasterwhileavoidingoverfitting. Theexperimentalresultsshow
thattheproposedapproachcanachievehighersuccessratesandsignificantlyimprove
sampleefficiencycomparedtoexistingmethods.
Sunman et al. [20] propose a semi-automatic method and tool called AWET that
combinesexploratorytesting(ET)withcrawler-basedautomatedtestingandapplyitto
webapplicationtesting. ThetoolrecordsasetoftestcasesbyperformingETmanually
beforehand,andthenusesthesetestcasesasthebasistoexploreandgeneratetestcasesfor
awebapplication.
Liuetal.[21]proposedamodel-basedrepresentationalstatetransfer(RESTful)API
testingmodeltodynamicallyupdatethebuiltpropertygraph. Theyclaimedthattheir
modelcoulddetectmorelinesofcodeandmorebugsthanstate-of-the-artmethods.Yandra-
pallyetal.[22]appliedamodel-basedtestgenerationtechniquetoanalyzepagefragments
finely and to create test oracles. Their experiments showed that their approach outper-
formed feeding the whole webpage. Sherin et al. [23] proposed a Q-learning inspired
dynamicexplorationapproachthatusesguidedsearchestosystematicallyexploredynamic
webapplicationswithlittlepriorknowledgeabouttheapplications. Theirresultsshow
thatQExploreoutperformstheCrawljaxandWebExplortoolsinachievinghighercoverage
andmorediverseDOM.
Another attempt is the earlier work by authors of this paper [6], which proposes
areinforcementlearningagenttrainedwithDQNtoguidecrawlerstoexplorewebap-
plications to increase code coverage. The experimental results show that the agent can
guide the crawler to achieve better code coverage than traditional web crawlers. This
paperisanextensionofthisearlierworkwithanewdesignofactions,statemodel,and
rewardfunctiontofurtherimprovethecodecoverageofwebcrawlers. Additionally,an
environmentisdesignedtosupportagenttrainingusingdifferentreinforcementlearning
algorithmsandneuralnetworks.

## Page 5

Electronics 2024, 13, x FOR PEER REVIEW 5 of 23
the crawler to achieve better code coverage than traditional web crawlers. This paper is an
extension of this earlier work with a new design of actions, state model, and reward func-
tion to further improve the code coverage of web crawlers. Additionally, an environment
is designed to support agent training using different reinforcement learning algorithms
and neural networks.
Electronics2024,13,427 5of22
3. The Proposed Approach
This section describes the proposed approach, including an overview of the proposed
3. TheProposedApproach
approach for web application exploration, the design of actions, the state model, the re-
Thissectiondescribestheproposedapproach,includinganoverviewoftheproposed
ward function, the neural network architecture, and the design of environment to support
approach for web application exploration, the design of actions, the state model, the
different RL algorithms.
rewardfunction,theneuralnetworkarchitecture,andthedesignofenvironmenttosupport
differentRLalgorithms.
3.1. Overview of the Proposed Approach
3.1. OFviegruvireew 4o sfhthoewPsr aop socshedemAaptpirco daciahgram of the proposed approach. The iRobot interacts
with an environment consisting of a (modified) Crawljax and the web application under
Figure4showsaschematicdiagramoftheproposedapproach. TheiRobotinteracts
test (i.e., WebApp). At each time step 𝑡, iRobot receives the current state of the environ-
withanenvironmentconsistingofa(modified)Crawljaxandthewebapplicationunder
ment 𝑠 and the reward 𝑟 from the environment. The iRobot then selects an action 𝑎
test(i.e.,𝑡WebApp). Ateach𝑡timestept,iRobotreceivesthecurrentstateoftheenvironment𝑡
from a set of available actions based on 𝑟 according to the reinforcement learning algo-
s
t
andthereward r
t
fromtheenvironmen𝑡t. TheiRobotthenselectsanaction a
t
froma
rithm and sends 𝑎 to guide Crawljax to explore the WebApp. The exploration of the
setofavailableactio𝑡nsbasedonr
t
accordingtothereinforcementlearningalgorithmand
s
W
en
e
d
b
s
Aap
t
p
to
c
g
a
u
u
i
s
d
e
e
d
C
b
r
y
a w
𝑎
l𝑡j a
c
x
a
t
n
o
c
e
h
x
a
p
n
lo
g
r
e
e
t
t
h
h
e
e W
sta
e
t
b
e
A
o
p
f
p
t
.
h
T
e
h
e
e
n
e
v
x
i
p
ro
lo
n
r
m
at
e
io
n
n
t t
o
o
f t
𝑠
h𝑡e+1W
a
e
n
b
d
A p
g
p
en
c
e
a
r
u
a
s
t
e
e
d
a
bnyewa
t
craenwachrdan 𝑟 g𝑡e+1t,h beosttha toefo wfthhieche navreir orentmurennetdt otos
t
i
+
R
1
oabnodt. gTehnee rpartoecaesnse wwilrle wcoanrtdinru
t+
e
1
u,nbotitlh a
opfrwedheifichneadr etirmeteu srtneepd isto reiRacohbeodt.. TThhee gporoalc eosfs thwei lplrcoocnetsisn uise tuo ntrtialina piRreodbeofit ntoe dmtaimximesizteep a
icsurmeauclhaetidv.e Trehweagroda lporofpthoertipornoacle tsos cisodtoe ctroavienraiRgoe boof tthtoe mWaexbiAmpipze. a cumulative reward
proportionaltocodecoverageoftheWebApp.
F F i i g g u u r r e e 4 4 . .S Scchheemmaattiiccd diiaaggrraammo offt thheep prrooppoosseedda apppprrooaacchh..
3.2. TheDesignofActions
3.2. The Design of Actions
Inreinforcementlearning,theagentselectsanactionfromasetofavailableactionsand
In reinforcement learning, the agent selects an action from a set of available actions
sendstheselectedactiontotheenvironment. Usually,thesetofavailableactionsisfinite
and sends the selected action to the environment. Usually, the set of available actions is
sothatreinforcementlearningalgorithmscanconverge. However,thiscanbeachallenge
finite so that reinforcement learning algorithms can converge. However, this can be a chal-
whendesigningactionstoexplorewebapplications,asawebpagecancontainvarious
lenge when designing actions to explore web applications, as a web page can contain var-
inputfields,buttons,andhyperlinksthatuserscaninteractwith. Also,thenumberofinput
ious input fields, buttons, and hyperlinks that users can interact with. Also, the number of
fields,buttons,andhyperlinksineachgeneratedwebpageofagivenwebapplicationis
input fields, buttons, and hyperlinks in each generated web page of a given web applica-
oftendifferent. Therefore,identifyingafinitesetofactionsrequiredtotraintheRLagentto
tion is often different. Therefore, identifying a finite set of actions required to train the RL
interactwithawebapplicationisnottrivial.
agent to interact with a web application is not trivial.
Forcrawlingandtestingofwebapplications,intheearlierworkofthispaper[6],asetof
For crawling and testing of web applications, in the earlier work of this paper [6], a
primitiveactionsincludingclicking,changingfocus,andenteringtextwithdifferentvalues
wseats oufs perdi,maistisvheo awcntioinnsT ainbclelu1d.iInngt chliisckaicntigo,n chdaensigginn,gn fo+c2usa,c atinodn senwteerreinugs teedx,tw whitehre dniffisertehnet
nvuamlubeesr woafst eussteidn,p aust svhaoluwens iuns Tedabtloe e1x. pInlo trheisth aectaiponp ldiceastiigonn, unn +d 2e ractetisot.nSs pweecrifei cuaslleyd,,a wahnedre
0
an 1 iasr tehcel incukmanbderc ohfa tnegste -infopcuuts vaacltuioens su,sreedsp toec etxivpelloyr,ew thheil eapap 2 ltiocaat n io + n 2 , uanredeinr pteustt.a Scptieocnisficwailtlhy,
a𝑎s0s oacniadte d𝑎 1i napreu tclviacklu aesndv
1
c,h.a.n.,gve
n
-.foUcusisn gactthioisnss,e treosfpaeccttiiovnesl,yi, twishsiluef f𝑎ic2i etnot t𝑎o𝑛+p2e,r aforrem intphuet
aacctitoionnssr ewqiuthir eadsstoociinatteerda citnwpuitth vaawlueebs p𝑣a1g, e…,s,u 𝑣ch𝑛 . aUsscilnicgk itnhgisb suettt oonf saocrtihoynps,e irtl iinsk ssu,ffichcainegnitn tgo
tpheerffoocrums otfhwe iadcgtieotsn,sa nredqpuoirpeudl attoin ignatellraincpt uwtiftihel das wweitbh paasgeet,o sfupcrhe- daesf icnleicdkvinaglu besu.ttons or
However,formostwebapplicationuserscenarios,theusertypicallyfillsinallinput
fieldsofawebpageform(suchasregisteringauseraccount)andthensubmitstheform.
Whenutilizingclick,change-focus,andinput-textactionsastheavailablesetofactionsin
theenvironment,theagentrequiresnumerousactionstonavigate,complete,andsubmit
theform. Consequently,theactionsearchspacecanbehuge.
TonarrowtheactionsearchspacetoimproveRLagenttraining,thispaperproposesa
newdesignofactionsforexploringandtestingwebapplications. Specifically,theproposed
designmainlyfocusesonactionsrelatedtoinputfieldsandbuttonclicks,asthewebcrawler

## Page 6

Electronics 2024, 13, x FOR PEER REVIEW 6 of 23
hyperlinks, changing the focus of widgets, and populating all input fields with a set of
pre-defined values.
Table 1. The action design in the authors’ earlier work.
No Action Type Input Value
Electronics2024,13,427 𝑎 0 Click − 6of22
𝑎 Change-Focus −
1
𝑎 Input 𝑣
2 1
itselfcanautom⋮ aticallynavigateandtesthy⋮p erlinks. Theproposeddesig⋮ n,specifically,
incorporates𝑎action saimedatpopulatinga
I
l
n
l
p
fi
u
el
t
d sofawebform,simulati𝑣ng thebehavior
n+2 𝑛
ofahumantesterwhotypicallyfillstheinputfieldswithtestdatabeforesubmittingthe
form. Thisactiondesigncanminimizethesizeofactionsearchspace,resultinginfaster
However, for most web application user scenarios, the user typically fills in all input
convergenceduringtraining.
fields of a web page form (such as registering a user account) and then submits the form.
When utilizing click, change-focus, and input-text actions as the available set of actions in
Table1.Theactiondesignintheauthors’earlierwork.
the environment, the agent requires numerous actions to navigate, complete, and submit
the form. Consequently, the action search space can be huge.
No ActionType InputValue
To narrow the action search space to improve RL agent training, this paper proposes
a Click −
0
a new design of actions for exploring and testing web applications. Specifically, the pro-
a Change-Focus −
posed design m1 ainly focuses on actions related to input fields and button clicks, as the
web crawler iat2self can automatically navigInapteu tand test hyperlinks. The pvr1oposed design,
specifically, in.corporates actions aimed at po.pulating all fields of a web fo.rm, simulating
. . .
. . .
the behavior of a human tester who typically fills the input fields with test data before
submitting tha ne+ f2orm. This action design caInnp mutinimize the size of action svenarch space, re-
sulting in faster convergence during training.
For example, consider the simple web page shown in Figure 5, which consists of two
For example, consider the simple web page shown in Figure 5, which consists of
input fields and one button. This web page requires at least three actions, including two
twoinputfieldsandonebutton. Thiswebpagerequiresatleastthreeactions,including
inputs and one click, for a web crawler to complete and submit the form. However, even
twoinputsandoneclick,forawebcrawlertocompleteandsubmittheform. However,
if the input values of these two fields provided by crawler are all valid, the probability
eveniftheinputvaluesofthesetwofieldsprovidedbycrawlerareallvalid,theprobability
tthhaattt thheec crarawwlelerrw wilillsl uscuccecsessfsuflulyllyco cmomplpetleetaen adnsdu bsumbimttiht ethfoer fmorims1 i/s3 1×/3 1×/ 13/3× ×1 /1/33= = 11//2277..
NNeevveerrtthheelleessss,, iiff tthhee ccrraawwlleerr hhaass aann aaccttiioonn ttoo ppooppuullaattee aallll fifieellddss wwiitthh vvaalliidd iinnppuuttss.. IItt ttaakkeess
oonnee aaccttiioonn ttoo fifillll iinn tthhee iinnppuutt fifieellddss,, aanndd oonnee aaccttiioonn ttoo cclliicckk tthhee bbuuttttoonn ttoo ccoommpplleettee aanndd
ssuubbmmiitt tthhee ffoorrmm.. TThheerreeffoorree,, tthhee pprroobbaabbiilliittyy ooff ssuucccceessssffuullllyy ccoommpplleettiinngg aanndd ssuubbmmiittttiinngg tthhee
ffoorrmm ccaann bbee iinnccrreeaasseedd ttoo 11//22 ×× 1/12/ =2 1=/41./ C4o.nCsoenqsueeqnutleyn, ttlhy,et threaitnrianingi snpgesepde oefd thoef tahgeeangt ecnant
cbaen ibnecrienacsreeda,s eadn,da tnhde tnheeunraelu nraeltwneotrwko craknc baen ebxepeexcpteedc tteod ctooncvoenrgvee rmgeorme oqrueiqckuliyck. ly.
FFiigguurree 55.. AA ssiimmppllee llooggiinn wweebbppaaggee..
AAllssoo,,a assm meenntitoionneedde aeralrileire,rb, obtohthv avlaidlidan adnidn vinavliadlivda vluaeluseosf othf ethinep iuntpfuiet lfideslndese ndeteodb teo
tbeset teedstaendd acnodv ecroevdefroerdt efostri ntegsptiunrgp pousersp.oVseersi.f yVienrgiftyhienrge tshpeo nresespsoonfsthees owfe tbhea pwpelibc aatpiopnliucantdioenr
tuesntdteori tnevsat ltiod iinnvpaulitds minapyutasl smoaiyn carlesaos ientchreeacsoed tehceo cvoedrea gcoevoefrtahgeew ofe bthcer awweble cr.raTwhelerer.f oTrhee,rien-
tfhoerep,r oinp othseed parcotpioonsedde saigctni,own edaelssiognin, cwlued ealascot iionncsluthdaet aficltliionnvsa ltihdavt afilulle isn.vNaolitde tvhaaltuaelsl.i nNpoutte
ftiheladt sanlle iendputot bfieelfdilsle ndeewdi ttho vbael ifidllveadl uweisthin voarldide rvatoluteess tinth oerhdaepr ptoy tpeastth th(ie. eh.,anpopyex pcaetpht i(oi.nes.,
onroe rerxocrecpotniodnitsio nors ).eHrroowr ecvoenrd,iintioonrds)e.r Htootwesetvaenr,u ninh aoprpdyerp attoh (toesrte xacne putinohnappaptyh ),piattihs n(ootr
necessarytofillallinputfieldswithinvalidvalues.Specifically,torevealfaults,itisnecessary
thateachinputfieldisindividuallytestedwithaninvalidvalue.
Table 2 shows the proposed design of actions for iRobot. The design consists of
8actions,whereactionsa −a arerelatedtoinputvalues,andactionsa −a areassociated
0 2 3 7
withbuttonclicks. ThisdesigncanhandledifferenttypesofAUTswithvaryingnumbersof
inputfieldsandbuttons.Itfillsallinputfieldswithvaluesinoneaction,insteadofselecting
onefieldatatime,forhigherefficiency. Italsogroupsbuttonsintoatmostfourpergroup

## Page 7

Electronics2024,13,427 7of22
toaccommodatewebpageswithmanybuttons. Iftherearelessthanfourbuttons,suchas
two,thenthereisonlyonebuttongroup,andsomeactionshavenoeffect(seealsobelow).
Table2.Theproposeddesignofactions.
No Action
Fillallinputfieldswithvalidvalues(i.e.,allvalidinputs),
a
0 ValidInputIndex++,FocusIndex++
Fillallinputfieldswithvalidvaluesexceptforthefocusedfield,
a whichisfilledwithaninvalidvalue(i.e.,singleinvalidinput),
1
ValidInputIndex++,InvalidInputIndex++,FocusIndex++
Fillthefocusedfieldwithaninvalidvalue,InvalidInputIndex++,
a
2 FocusIndex++
a ClickthefirstbuttoninGroup,FocusIndex++
3
a ClickthesecondbuttoninGroup,FocusIndex++
4
a ClickthethirdbuttoninGroup,FocusIndex++
5
a ClickthefourthbuttoninGroup,FocusIndex++
6
a GroupIndex++(i.e.,changegroup),FocusIndex++
7
Inourdesign,actiona isusedtofillallinputfieldswithvalidvalues. Actiona is
0 1
usedtofillonlyoneinputfieldwithaninvalidvalueandtheremaininginputfieldswith
valid values. Action a is used to populate the focus input field with an invalid value.
2
Combiningactiona withactionsa anda enablesiRobottosimulatethebehaviorofa
0 1 2
humantester,testingeachinputfieldseparatelywithinvalidvalues(calledinvalidinputs
below). NotethatthedesignofactionsusesFocusIndexasthecounterindexoftheinput
widgetthattheapplicationiscurrentlyfocusedon(i.e.,thewidgethasakeyboardinput
focus),andFocusIndex++setsthefocusindextothenextinputwidget. Intheproposed
actiondesign,eachactioncontainsaFocusIndex++tochangefocustothenextinputwidget
whentheactioniscompleted. Thisavoidssituationswheretheagentimmediatelyrepeats
actionsonthesameinputwidget,whichmayfurthernarrowtheactionsearchspace.
Also,webapplicationscanoftendynamicallygeneratedifferentresponsepageswhen
they receive different input data. For example, depending on the logged in user, the
responsepagemaybedifferent. Therefore,differentvalidandinvalidvaluesforaninput
field are necessary for testing purposes. By doing this, the test code coverage can also
be improved. To enable iRobot to select a different value for an input field, a counter
index for the sets of input values called InputIndex is used in the action design. If the
valuesoftheinputsetisvalid(orinvalid),theInputIndexiscalledValidInputIndex(or
InvalidInputIndex). TheideaofaninputindexissimilartothatoftheFocusIndex. Inthe
proposedactiondesign,actionsa ,a anda willpopulateinputfieldswithasetofvalid
0 1 2
(orinvalid)valuesaccordingtothevalueofValidInputIndex(orInvalidInputIndex),and
incrementtheindexvalueby1aftercompletingtheactions. ThisdesignallowsiRobotto
interactwithwebapplicationsusingdifferentvalidandinvalidinputs.
Forexample,considerthesimplewebpageshowninFigure5. Initially,letthefocus
ofwebpagebeonthefieldlabeled“Employeeemail”. SupposethatTables3and4are
thetwosetsofvalidandinvalidinputsforawebpage,respectively. Figure6a,bshowthe
inputvaluesofthewebpagewheniRobotselectsactiona withValidInputIndex=1and
0
ValidInputIndex=2,respectively. Likewise,Figure6cshowstheinputvaluesoftheweb
pagewheniRobotselectsactiona withInvalidInputIndex=1. However,ifiRobotselects
1
actiona (insteadofa )withInvalidInputIndex=1,onlythefocusfieldispopulatedwith
2 1
aninvalidvalue,asshowninFigure6d. Notethatthelabelsoftheinputfieldsinaweb
pageformwillbeextractedandclassifiedaccordingtosemanticsofthelabels. Forexample,
aninputfieldwithlabels“Employeeemail”and“Emailaddress”couldbeclassifiedinto
an“Email”category. Basedonthecategoryoftheinputfieldlabel, iRobotcanfindthe

## Page 8

Electronics2024,13,427 8of22
correspondingvaluesforaparticularinputfieldfromtheindexedsetofinvalid(orvalid)
inputs. Therefore,inFigure6d,iRobotselectsthevalue“teacher@@ntut.edu.tw”ofthe
“Email”categoryfromtheinvalidinputset{“An*rew”,“teacher@@ntut.edu.tw”,“-”,...}
forthefocusedfieldlabeled“Employeeemail”.
Table3.Anexampleoftwosetsofvalidinputs.
ValidInputIndex
CategoryofInputField
Set1 Set2
Name Andrew Peggy
Email teacher@ntut.edu.tw student@ntut.edu.tw
Password Andrew0610 ab5sRsda.ad
··· ··· ···
Table4.Anexampleoftwosetsofinvalidinputs.
InvalidInputIndex
CategoryofInputField
Set1 Set2
Name An*rew Pe@ggy
Email teacher@@ntut.edu.tw student@@ntut.edu.tw
Password - 0
Electronics 2024, 13, x FOR PEER REVIEW 9 of 23
··· ··· ···
(a) (b)
(c) (d)
Figure 6. The login webpage with input fields populated using different indexed sets: (a) action 𝑎
Figure6. Theloginwebpagewithinputfieldspopulatedusingdifferentindexedsets: (a)action0
using the value set ValidInputIndex = 1; (b) action 𝑎 using the value set ValidInputIndex = 2; (c)
a usingthevaluesetValidInputIndex=1;(b)action0a usingthevaluesetValidInputIndex=2;
a0ction 𝑎 using the value set InvalidInputIndex = 1; a0nd (d) action 𝑎 using the value set Inva-
1 2
(c)actiona usingthevaluesetInvalidInputIndex=1;and(d)actiona usingthevaluesetInvalidIn-
lidInputIn1dex = 1. 2
putIndex=1.
Foractionsrelatedtobuttonclicks, iRobotselectsabuttontoclickfromthegroup
catalogedbyacounterindexcalledGroupIndex. Theactionsa ,a ,a ,anda inTable2
3 4 5 6
areusedtoclickthefirst,second,third,andfourthbuttonintheindexedbuttongroup,
Figure 7. An example of button groups.
3.3. The Design of State Model
To represent the state of the environment in our earlier work, we used the DOM [24]
of the web application under test, the branch coverage of the application, and the index
vector (i.e., FocusIndex) of the focus widgets in the web pages of the application. To sup-
port the proposed new action design, the environment state also contains additional in-
formation from ValidInputIndex, InvalidInputIndex, and GroupIndex in addition to the
DOM, branch coverage, and focus vectors. Equation (1) is the state vector 𝑠̂ of the envi-
𝑖
ronment:
𝑠̂ 𝑖 =<𝐷𝑂𝑀(𝑠 𝑖 ),𝐶𝑉(𝑠 𝑖 ),𝐹𝐼(𝑠 𝑖 ),𝐺𝐼(𝑠 𝑖 ),𝑉𝐼𝐼(𝑠 𝑖 ),𝐼𝑣𝐼𝐼(𝑠 𝑖 )> (1)
where 𝐷𝑂𝑀(𝑠) is a vector representing the state 𝑠 (i.e., DOM) of the web application;
𝑖 𝑖
𝐶𝑉(𝑠) is a vector representing the branch coverage of the application at state 𝑠; 𝐹𝐼(𝑠)
𝑖 𝑖 𝑖
and 𝐺𝐼(𝑠) are one-hot encoding vectors representing FocusIndex and GroupIndex,
𝑖

## Page 9

Electronics 2024, 13, x FOR PEER REVIEW 9 of 23
(a) (b)
Electronics2024,13,427 9of22
respectively. Iftherearelessthanfourbuttons,suchastwo,thenthereisonlyonebutton
groupandactionsa anda havenoeffect(calledinvalidactionbelow),whilea isused
5 6 7
tochangethebuttongroup. Forinstance,letusassumethatawebpagehas11buttons. In
thedesignofactions,these11buttonswillbearrangedinto3groups,asshowninFigure7.
WhentheGroupIndexis1,actionsa ,a ,a ,anda willselectwidgetbuttons0to3toclick,
3 4 5 6
respectively. Similarly,iftheGroup Indexis2,widgetbuttons4to7are selected. Notethat
iftheGroupInde(xc)i s3andactiona isselected,this(wd)i llresultinaninvalidactionasthere
6
isnocorrespondingbuttontoclick. Aninvalidactionheremeansthattheagentchosea
Figure 6. The login webpage with input fields populated using different indexed sets: (a) action 𝑎
0
cuesritnagi nthaec vtiaolnue, bsuett VthaleidaIcntpiountInhdaesxn =o 1m; (eba)n aicntgio;ni t𝑎ne iutshienrg hthaes avnalyuee fsfeetc VtaolnidtIhnepuetnInvdireoxn =m 2e; n(ct),
0
naoctriodno e𝑎s itucshinagn gtheet hvaelustea tsee.t BInevcaaluidseIniptudtoInedsenxo t= h1e; lapntdh e(dt)r aaicntiinong o𝑎f thuseinagg etnhte, wvaeluseh oseutl dIntvray-
1 2
tloidaInvpouidtInindvexa l=i d1.a ctionsduringthetrainingprocesswiththehelpoftherewardfunction.
FFiigguurree 77.. AAnn eexxaammppllee ooff bbuuttttoonn ggrroouuppss..
3.3. TheDesignofStateModel
3.3. The Design of State Model
Torepresentthestateoftheenvironmentinourearlierwork,weusedtheDOM[24]of
To represent the state of the environment in our earlier work, we used the DOM [24]
thewebapplicationundertest,thebranchcoverageoftheapplication,andtheindexvector
of the web application under test, the branch coverage of the application, and the index
(i.e.,FocusIndex)ofthefocuswidgetsinthewebpagesoftheapplication. Tosupportthe
vector (i.e., FocusIndex) of the focus widgets in the web pages of the application. To sup-
proposednewactiondesign,theenvironmentstatealsocontainsadditionalinformation
port the proposed new action design, the environment state also contains additional in-
fromValidInputIndex,InvalidInputIndex,andGroupIndexinadditiontotheDOM,branch
formation from ValidInputIndex, InvalidInputIndex, and GroupIndex in addition to the
coverage,andfocusvectors. Equation(1)isthestatevectors oftheenvironment:
(cid:98)i
DOM, branch coverage, and focus vectors. Equation (1) is the state vector 𝑠̂ of the envi-
𝑖
ronment: s =< DOM(s ),CV(s ),FI(s ),GI(s ),VII(s ),IvII(s ) > (1)
(cid:98)i i i i i i i
where DOM(s ) is a 𝑠̂ 𝑖v = e < cto 𝐷 r 𝑂 r 𝑀 ep ( r 𝑠 e𝑖 ) s , e 𝐶 n 𝑉 ti ( n 𝑠 g𝑖 ), t 𝐹 h 𝐼 e ( s 𝑠 t𝑖 ) a , t 𝐺 e 𝐼 s (𝑠 (𝑖i ) . , e 𝑉 ., 𝐼𝐼 D (𝑠 O𝑖 ) M ,𝐼 ) 𝑣 o 𝐼𝐼 f ( t 𝑠 h𝑖 ) e > w eb applicatio ( n 1) ;
i i
CwVh ( esrie ) i𝐷s𝑂a𝑀ve(c𝑠t
𝑖
o) rirse ap rveescetnotrin rgepthreesbernatnincgh cthove esrtaagtee o𝑠f
𝑖
t(hi.ee.a,p DpOlicMat)i oonf athtes twateebs ia;pFpI( liscia ) taionnd;
G𝐶𝑉I((s𝑠i )) airse ao nvee-chtootr ernecpordeisnegntvinecgt othrser beprarnescehn ctionvgeFraogcue soInf dtheex aanpdplGicraotuiopnI nadt esxt,artees p𝑠e;c t𝐹iv𝐼(e𝑠ly),
𝑖 𝑖 𝑖
f
a
o
n
r
d
t he𝐺𝐼a(p𝑠p)l i c
a
a
r
t
e
io n
on
in
e-
s
h
t
o
a
t
t e
e
s
ni
;
c
a
o
n
d
d
in
V
g
I
v
I(
e
s
cit
)
o
a
rs
n d
re
I
p
v
r
I
e
I
s
(
e
s
in
)
ti
a
n
r
g
e v
F
e
o
c
c
to
u
r
s
s
In
re
d
p
e
r
x
e s
a
e
n
n
d
ti n
G
g
r
t
o
h
u
e
p
v
I
a
n
l
d
u
e
e
x
s
,
𝑖
ofValidInputIndexandInvalidInputIndex,respectively.
Notethat,insteadofstatementcoverage,branchcoverageisusedtoreducethesearch
spaceintheapproachsincethenumberofbranchesismuchlessthanthatofstatements.
Supposethatthenumberofbranchesinthesever-sidesourcecodeofthewebapplication
isn. Equations(2)and(3)showthecoveragevectorCV(s ):
i
CV(s ) =< b (s ),b (s ),··· ,b (s ) > (2)
i 1 i 2 i n i
(cid:40)
1 if branch jof states iscovered,
whereb = i , j = 1···n (3)
j
0 otherwise
To encode the values of ValidInputIndex and InvalidInputIndex, we first encode
theinputindexintoacategoryvector,wheretheinputindexcanbeValidInputIndexor
InvalidInputIndex. Supposethereareminputvaluesinacategoryandthej-thindexvalue

## Page 10

Electronics2024,13,427 10of22
isselected. Equations(4)and(5)showtheone-hotencodingforthecategoryvector. Here
theencodingvalueofthej-thinputinthevectoris300insteadof1,simplybecausewetry
toavoidoverlappingwiththeencodingvalueofDOM.
Category(s) =< e (s),..., e(s), ..., e (s) > (4)
1 i m
(cid:40)
300 ifi = j,
wheree = , i = 1···m (5)
i
0 otherwise
Withthevectorforeachcategoryofinputfields,thevectorsVII(s)andIvII(s)canbe
i i
encoded.Supposetheinputfieldsofawebapplicationhasncategories.Equations(6)and(7)
showthevectorrepresentationsforVII(s)andIvII(s),respectively.
i i
VII(s ) =<Category (s ), Category (s ), ..., Category (s ) > (6)
i 1 i 2 i n i
IvII(s ) =<Category (s ), Category (s ), ..., Category (s ) > (7)
i 1 i 2 i n i
3.4. TheDesignofRewardFunction
Toguidethecrawlertoexplorethewebapplicationundertestandincreasethebranch
coverageduringagenttraining,therewardfortheactioniscalculatedusingthecoverage
vector CV(s ). Basically, the more branch coverage an action can increase, the higher
i
the reward for that action. Since branch coverage monotonically increases during the
exploration of a web application, if an action changes the state of the application from
s to s , the increase in branch coverage can be computed by comparing vectors CV(s )
i j i
(cid:0) (cid:1)
andCV s . Equation(8)showstherewardfunctionforiRobotwhereK ,K ,K ,K are
j 0 1 2 3
positiveintegers.
  K
0
i
∑
=
n
1
(cid:0) b
i
(cid:0) s
j
(cid:1) −b
i
(s
i
) (cid:1) ifactionaincreasesoverallcoverage
reward(a) = −K 1 ifactionaisinvalidaction (8)
 −
−
K
K
2
i
e
f
ls
a
e
ctionachangesgroup
3
Theaboverewardfunctionwillgenerateapositiverewardonlyiftheselectedaction
can increase branch coverage. Note that coverage may increase when executing error
detectioncodeswithinvalidinputs(i.e.,takingactionsa ora ). Recallthatinvalidinputs
1 2
aretheresultoftakingactionsa anda ,andinvalidactionsareactionswithnoeffect,such
1 2
asclickingonathird(nonexistent)buttoninawebpagewithtwobuttons. Thereward
willbenegativewhentheselectedactionisaninvalidaction,theactiononlychangesthe
buttongroup,ortheactiondoesnotincreasecoverageatall. Wehaveaddedasentenceto
clarifythispointintheparagraphdiscussingthereward.
Notethat,topreventtheagentfromselectinganinvalidaction,alargenegativereward
shouldbegivenforsuchcases. Also,toreducetheprobabilitythatthecrawlerwillkeep
changingthebuttongroupwithoutfillingintheinputsorclickingthebuttons, asmall
negativerewardshouldbegivenwhenselectingsuchanaction. Additionally,toprevent
theagentfromselectingactionsthatdonotfurtherincreasebranchcoverage,aslightly
smallernegativerewardcanalsobegivenforthoseactions. Therefore,intheproposed
rewardfunction,theparametersaredeliberatelydesignedasK >K >K . Furthermore,
1 2 3
thevalueofK canbeadjustedbasedonthewebapplicationundertest,sincetheincrease
0
in branch coverage for an action is implementation dependent for the web application
undertest. Intheproposedapproach,thevaluesK = 10, K = 0.5, K = 0.35,and
0 1 2
K = 0.25wereused.
3

## Page 11

Electronics2024,13,427 11of22
3.5. TheArchitectureoftheProposedCNNNetwork
Figure8showstheconvolutionalneuralnetwork(CNN)architectureusedtotrain
iRobot. Basically, the inputs of the network include the DOM source code of the web
page under exploration, Coverage Vector, FocusIndex, GroupIndex, and InputIndex as
mentionedinSection3.4. Itisworthnotingthatdifferentwebpagescanhavedifferent
widthsandheights,anduserscanusuallyscrollrightanddowntoviewtheinformation
ofawebpage. Therefore,ifafixed-sizescreenshotisusedasCNNinput,thequalityof
differentwebpagescreenshotscanvarygreatly,whichcouldmakethewebformfeatures
difficulttorecognizeandextract. Thus,insteadofusingawebpagescreenshot,theDOM
sourcecodeofwebpageisusedasCNNinput. Specifically,theDOMsourcecodeofa
webpageisconvertedintoaone-dimensionalarraybyconcatenatingeachlineofcode.
Since the length of DOM for different web pages can still be different, in order to have
afixed-lengthinputforCNN,themaximumlengthofDOMsourcecodeisdeliberately
limitedto130,100toaccommodatemostwebpages. IftheDOMlengthofawebpageis
lessthanthemaximumlength,paddingisaddedtotheendoftheDOM.Similarly,forthe
lengthofFocusIndex(orGroupIndex),wewillidentifythemaximumnumberofinput
fields(orbuttons)inawebpagefortheapplicationundertestanduseitasthelengthof
Electronics 2024, 13, x FOR PEER REVIEW 12 of 23
theindex. Again,paddingisaddedifthenumberofinputfields(orbuttons)foraweb
pageislessthantheindexlength.
FigFuirgeu 8r.e T8h.eT choencvoonlvuotilountiaoln naelunreaul rnaeltnweotwrko arkrcahrictehcittuecrteu oref tohfet hageeangte. nt.
3.6. The IDneFsiiggnu raend8 ,ItmhpeleCmNetNatinoent owf othrek EtankveirsonthmeeDntO Mofawebpageasaninputandtreats
itasalongpicture. ThestructureoftheCNNnetworkcontains4convolutionallayers,
To enable iRobot to use different reinforcement learning algorithms and neural net-
3maxpoolinglayers,and2fullyconnectedlayers. Theconvolutionallayersareusedto
works, the approach provides an environment leveraging OpenAI Gym [25], an open-
extractfeaturesoftheDOM;themaxpoolinglayersareresponsibleforreducingthesizeof
source library that supports the development and comparison of different RL algorithms.
theDOMwhilepreservingvitalinformation;andthefullyconnectedlayersareusedto
The environment has a web driver that drives a popular open-source web crawler,
synthesizethefinaloutput. Further,inthenetworkstructure,theinformationofCoverage
Crawljax [2] to interact with the web application under test. Furthermore, the environ-
Vector,FocusIndex,GroupIndex,andInputIndexisfeddirectlytothefirstfullyconnected
ment is designed to support user-defined environment states, actions, and reward func-
layertogetherwithoutputsfromthethirdmaxpoolinglayerandthentothesecondfully
tions for reinforcement learning. In addition, the environment collects server-side code
connectedlayer. ThisenablestheagenttolearntheirimpactsonchangestotheDOMstate.
coverage of web application under test, which is used to calculate the reward for an action.
Finally,theoutputlayerproducesthevaluesof8actions. Moreover,theactivationfunction
Figure 9 shows the system architecture of the proposed environment. The iRobot can
ofeachlayerisLeakyReLU,andthelinearactivationfunctionisusedintheoutputlayer.
interact with the WebEnvironment that implements the functions of Gym.env and the
necessary APIs to provide a Gym environment for utilizing OpenAI Gym. The WebDriver
is used to drive a crawler, control the web application under test (i.e., WebApp), and ob-
tain observations from WebEnvironment. The Crawljax tool has been extended to imple-
ment the WebDriver interface. ActionStrategy is used to convert high-level actions into
low-level operations that are used by WebDriver to drive Crawljax to interact with
WebApp. Note that ActionStrategy is an abstract class and has to be inherited and instan-
tiated by ConcreteActionStrategy. This design allows the environment to easily change
actions by simply implementing another ConcreteActionStrategy. The State is used to
hold a set of environment states retrieved from WebApp by WebEnvironment through
WebDriver. Reward is responsible for calculating the reward based on the code coverage
obtained from the CodeCoverageCollector after executing an action.

## Page 12

Electronics2024,13,427 12of22
3.6. TheDesignandImplemetationoftheEnvironment
ToenableiRobottousedifferentreinforcementlearningalgorithmsandneuralnet-
works,theapproachprovidesanenvironmentleveragingOpenAIGym[25],anopen-source
librarythatsupportsthedevelopmentandcomparisonofdifferentRLalgorithms. The
environmenthasawebdriverthatdrivesapopularopen-sourcewebcrawler,Crawljax[2]
tointeractwiththewebapplicationundertest. Furthermore,theenvironmentisdesigned
tosupportuser-definedenvironmentstates,actions,andrewardfunctionsforreinforce-
ment learning. In addition, the environment collects server-side code coverage of web
applicationundertest,whichisusedtocalculatetherewardforanaction.
Figure 9 shows the system architecture of the proposed environment. The iRobot
caninteractwiththeWebEnvironmentthatimplementsthefunctionsofGym.envandthe
necessaryAPIstoprovideaGymenvironmentforutilizingOpenAIGym. TheWebDriver
isusedtodriveacrawler,controlthewebapplicationundertest(i.e.,WebApp),andobtain
observationsfromWebEnvironment. TheCrawljaxtoolhasbeenextendedtoimplement
the WebDriver interface. ActionStrategy is used to convert high-level actions into low-
leveloperationsthatareusedbyWebDrivertodriveCrawljaxtointeractwithWebApp.
NotethatActionStrategyisanabstractclassandhastobeinheritedandinstantiatedby
ConcreteActionStrategy. Thisdesignallowstheenvironmenttoeasilychangeactionsby
simply implementing another ConcreteActionStrategy. The State is used to hold a set
ofenvironmentstatesretrievedfromWebAppbyWebEnvironmentthroughWebDriver.
Electronics 2024, 13, x FOR PEERR eRwEVaIErWd isresponsibleforcalculatingtherewardbasedonthecodecoverage13o boft a23i nedfrom
theCodeCoverageCollectorafterexecutinganaction.
FigFuigruer9e. 9C. Clalassss ddiiaaggrraamm oof tfhteh reeirnefionrcfoemrceenmt leenartnlienagr ennivnigroennmveinrto. nment.
4. Experiments and Results
To evaluate the usefulness of the proposed approach and the effectiveness of the de-
sign of actions, three experiments were conducted, and the following four research ques-
tions were addressed.
RQ1. In the proposed approach, what is the most suitable neural network for web crawl-
ing?
RQ2. What is the most suitable number of episodes to train iRobot?
RQ3. Which RL algorithm achieves better code coverage in web crawling?
RQ4. Can the new iRobot improve crawling code coverage compared with our earlier
work?
We conducted three experiments to answer these questions. The first experiment ad-
dressed RQ1. The second experiment answered RQ2 and RQ3. The third experiment tack-
led RQ4. In the experiments, we used branch coverage as the performance criterion, which
is an important measure in software testing, as described in the Introduction section.
Therefore, branch coverage is a suitable and useful measure for our problem.

## Page 13

Electronics2024,13,427 13of22
4. ExperimentsandResults
Toevaluatetheusefulnessoftheproposedapproachandtheeffectivenessofthedesign
ofactions,threeexperimentswereconducted,andthefollowingfourresearchquestions
wereaddressed.
RQ1.Intheproposedapproach,whatisthemostsuitableneuralnetworkforwebcrawling?
RQ2.WhatisthemostsuitablenumberofepisodestotrainiRobot?
RQ3.WhichRLalgorithmachievesbettercodecoverageinwebcrawling?
RQ4.CanthenewiRobotimprovecrawlingcodecoveragecomparedwithourearlierwork?
We conducted three experiments to answer these questions. The first experiment
addressedRQ1. ThesecondexperimentansweredRQ2andRQ3. Thethirdexperiment
tackledRQ4. Intheexperiments,weusedbranchcoverageastheperformancecriterion,
whichisanimportantmeasureinsoftwaretesting,asdescribedintheIntroductionsection.
Therefore,branchcoverageisasuitableandusefulmeasureforourproblem.
4.1. TheExperimentalEnvironmentandSubjectApplication
For the experiments, three computers with NVIDIA graphic cards were used for
agenttraining. ThespecificationsofthecomputersarelistedinTable5. Theprogramsfor
theiRobotRLagentwerewritteninPythonwithTensorflow[26]andtheOpenAIGym
framework[25].ProgramsfortheiRobotenvironmentdescribedinSection3.6werewritten
inJavawithCrawljaxanditsplugins. Versionsofthetoolsandlearningframeworkare
listedinTable6.
Table5.Specificationsofhardwareusedintheexperiments.
CPU IntelCorei7-7700
RAM 32GB
GPU NVIDIAGeForceRTX2070
OS Ubuntu18.04
Table6.Theversionsofsoftwareusedinexperiments.
Framework Tensorflowv1.10
OpenAIStable-baselines v2.10.0
Python v3.6.5
Java v1.8.0
Crawljax zaproxyv3.7
CUDA v10.0
cuDNN v7.2.1
ThewebapplicationusedintheexperimentswasTimeOff.Management[27],anopen-
sourceapplicationforsmallormediumsizecompaniestomanageemployeeabsences. The
applicationiscomplexandcontainsmanylinksandwebformsthatrequireuserinput.
Table7showssomeessentialattributesofTimeOff.Management,includingtheversionof
theapplicationusedinexperiments,thetotallinesofcode(LOC)oftheapplication,the
numberofbranchesinthesourcecode,etc. Itwasselectedasthetargetapplicationforthe
followingreasons:
• TimeOff.Management is a popular open-source web application available for pub-
lic use. Therefore, it can be used by related studies to compare results with our
experimentalresults.
• The size of the application is moderate, suitable for verifying the feasibility of the
proposedapproachwithanacceptabletrainingtime.

## Page 14

Electronics2024,13,427 14of22
• Thewebpagesoftheapplicationcontainmanyhyperlinks,buttons,andwebforms
withvariousinputfieldsforfillingindifferentkindsofdatasuchaslogin,registration,
andemployee. Therefore,thisapplicationissuitablefortraininganRLagenttoselect
inputvalues.
Table7.Someessentialattributesofthetargetapplication.
Webapplicationname TimeOff.Management
Type Employeeabsencemanagement
NumberofstarsonGitHub 708
Version v0.10.0
Totallineofcode(LOC) 2698
Numberofbranchesincode 1036
ToexploreTimeOff.Management,thecrawlerfirstneedstoprovideappropriatevalues
Electronics 2024, 13, x FOR PEER REVIEW 15 of 23
forthevariousinputfieldsontheregistrationpage,includingcompanyname,supervisor
name,email,password,andconfirmpassword,etc.,tosuccessfullyregisteracompany,
as shown in Figure 10. Once a company is registered, the user can edit the employee
company, as shown in Figure 10. Once a company is registered, the user can edit the em-
information,configureoptionsthatincludeleavetype,bookanewleaverequest,orcheck
ployee information, configure options that include leave type, book a new leave request,
theabsencesusingacalendarview,andmore. Toimprovecrawlingcodecoverage,both
or check the absences using a calendar view, and more. To improve crawling code cover-
validandinvalidvaluesareusedfortheinputfieldsofTimeOff.Management. Also,code
age, both valid and invalid values are used for the input fields of TimeOff.Management.
coverageoftheapplicationiscollectedusingIstanbulv0.45[28]. Thetoolcancollectcode
Also, code coverage of the application is collected using Istanbul v0.45 [28]. The tool can
coverageforES5andES2015+JavaScriptcodes.
collect code coverage for ES5 and ES2015+ JavaScript codes.
FFiigguurree 1100. .TThhe erergeigsitsrtartaiotino npapgaeg oef oTfimTiemOeffO.Mff.aMnaagneamgeemnte. nt.
In the following experiments, we used two RL algorithms, DQN [29] and PPO [30] to
conduct the experiments. In addition, Monkey was used for comparison with our experi-
mental results. In the experiments, both iRobot and Monkey used the same environment.
However, Monkey selects high-level actions randomly for a given environment, while
iRobot selects actions through reinforcement learning. Also, for each RL algorithm, unless
specified otherwise, the experiment results are averages for 3 runs. Additionally,
TimeOff.Management was used to train and validate RL algorithms. We did not have a
test model since the experiences learned by an agent from crawling TimeOff.Management
may not apply to exploring other web applications, as the inputs and implementations
may be quite different.
4.2. Experiment 1
The first experiment addressed RQ1. In the experiment, we examined several neural
networks, including the proposed CNN (see Section 3.5), CNNLSTM (CNN Long Short-
Term Memory [31]), MLP (Multilayer Perceptron [32]), and MLPLSTM, to see which is the
most suitable for training iRobot to achieve higher code coverage. To simplify the discus-
sion and to make fair comparisons, the hyperparameters of the network models used de-
fault settings of the stable-baseline library without additional hyperparameter optimiza-
tion.

## Page 15

Electronics2024,13,427 15of22
Inthefollowingexperiments,weusedtwoRLalgorithms,DQN[29]andPPO[30]to
conducttheexperiments. Inaddition,Monkeywasusedforcomparisonwithourexperi-
mentalresults. Intheexperiments,bothiRobotandMonkeyusedthesameenvironment.
However, Monkey selects high-level actions randomly for a given environment, while
iRobotselectsactionsthroughreinforcementlearning. Also,foreachRLalgorithm,unless
specifiedotherwise, theexperimentresultsareaveragesfor3runs. Additionally, Time-
Off.ManagementwasusedtotrainandvalidateRLalgorithms. Wedidnothaveatest
modelsincetheexperienceslearnedbyanagentfromcrawlingTimeOff.Managementmay
notapplytoexploringotherwebapplications,astheinputsandimplementationsmaybe
quitedifferent.
4.2. Experiment1
ThefirstexperimentaddressedRQ1. Intheexperiment,weexaminedseveralneural
networks,includingtheproposedCNN(seeSection3.5),CNNLSTM(CNNLongShort-
TermMemory[31]),MLP(MultilayerPerceptron[32]),andMLPLSTM,toseewhichisthe
mostsuitablefortrainingiRobottoachievehighercodecoverage.Tosimplifythediscussion
andtomakefaircomparisons,thehyperparametersofthenetworkmodelsuseddefault
settingsofthestable-baselinelibrarywithoutadditionalhyperparameteroptimization.
Thereasonthatweevaluatedseveraldifferentneural-networkmodelsisbecausere-
searchersintheANNfieldfindithardtoprovidegoodguidelinesforchoosingarchitecture.
Infact, theyusuallydeterminethehyperparameters, suchasthenumberoflayersand
nodes,byexperiment(calledthevalidationphaseintheANNliterature). Conceptually,
dynamicwebpagesdependonthestate;therefore,astatefularchitecture(suchasLSTM)
shouldbebetterbecauseithasinternalmemory. However,ourexperimentsshowedother-
wise. Attimeofwritingofthispaper,thequestionofwhichANNmodelisbetterforform
fillingwarrantsfurtherresearch.
Basedontheresultsofthisexperiment,theneuralnetworkdeterminedtobethemost
suitablewasthenusedforsubsequentexperiments. Thenumberoftrainingstepswasset
to10,000steps,thenumberofepisodeswassetto32,andthedesignofactionsdescribed
in Section 3.2 was used. Furthermore, during model training and validation, the set of
generatedactionsequencesthatachievedthehighestbranchcoveragewhilehavingthe
shortestsequencelength,aswellastheirrewards,wasrecordedforeachepisode. Thecode
coverageachievedbysuchactionsequencesforallepisodeswasthenusedtocalculatethe
resultsoftheexperiments.
Figure11showstheexperimentalresultsfordifferentneuralnetworks. Thebranch
coverageisthecrawlingresultobtainedusingtheactionsequencegeneratedduringthe
modelvalidationprocess. ForDQN,thevalidationisperformedonlyonce. ForPPO,since
itisastochasticalgorithm,weselectthebestcrawlingresultfrom20independentvalidation
runs. Also,fortheDQNalgorithm,onlytheCNNandMLPresultswereprovided. This
is because the default policy networks available for the DQN algorithm in the OpenAI
stable-baseline[33]includeonlytheCNNandMLPnetworks.FromtheresultsinFigure11,
itcanbeseenthattheCNNnetworkcanachieveabout19–20%branchcoveragewhen
usingDQNandPPOalgorithm. Theothernetworks,however,haveevensmallercode
coverage(notgreaterthan5%). Therecouldbeseveralfactorsinfluencingthisresult,such
asusingtheDOMasinputorthestructureofthenetworkbeingused. Nevertheless,the
customdesignofourCNNnetworkperformsbetterthanothernetworks. Hence,among
thestudiedagentarchitecturesandtrainingalgorithms,theCNNagenttrainedwiththe
PPOalgorithmisbetter,ormoreefficient,becauseitreachesthehighestbranchcoverage
withthesamenumberoftrainingsteps.

## Page 16

Electronics 2024, 13, x FOR PEER REVIEW 16 of 23
The reason that we evaluated several different neural-network models is because re-
searchers in the ANN field find it hard to provide good guidelines for choosing architec-
ture. In fact, they usually determine the hyperparameters, such as the number of layers
and nodes, by experiment (called the validation phase in the ANN literature). Conceptu-
ally, dynamic webpages depend on the state; therefore, a stateful architecture (such as
LSTM) should be better because it has internal memory. However, our experiments
showed otherwise. At time of writing of this paper, the question of which ANN model is
better for form filling warrants further research.
Based on the results of this experiment, the neural network determined to be the most
suitable was then used for subsequent experiments. The number of training steps was set
to 10,000 steps, the number of episodes was set to 32, and the design of actions described
in Section 3.2 was used. Furthermore, during model training and validation, the set of
generated action sequences that achieved the highest branch coverage while having the
shortest sequence length, as well as their rewards, was recorded for each episode. The
code coverage achieved by such action sequences for all episodes was then used to calcu-
late the results of the experiments.
Figure 11 shows the experimental results for different neural networks. The branch
coverage is the crawling result obtained using the action sequence generated during the
model validation process. For DQN, the validation is performed only once. For PPO, since
it is a stochastic algorithm, we select the best crawling result from 20 independent valida-
tion runs. Also, for the DQN algorithm, only the CNN and MLP results were provided.
This is because the default policy networks available for the DQN algorithm in the
OpenAI stable-baseline [33] include only the CNN and MLP networks. From the results
in Figure 11, it can be seen that the CNN network can achieve about 19–20% branch cov-
erage when using DQN and PPO algorithm. The other networks, however, have even
smaller code coverage (not greater than 5%). There could be several factors influencing
this result, such as using the DOM as input or the structure of the network being used.
Nevertheless, the custom design of our CNN network performs better than other net-
works. Hence, among the studied agent architectures and training algorithms, the CNN
Electronics2024,13,427 agent trained with the PPO algorithm is better, or more efficient, because it reaches 1 6 th of e 2 2
highest branch coverage with the same number of training steps.
FiFgiugruer 1e11. 1C.oCmopmapraisroisno onfo rferseuslutsl tussuinsign dgidffiefrfeernetn atlgalogroitrhitmhms. s.
4.3. Experiment2
4.3. Experiment 2
The second experiment addressed RQ2 and RQ3. In the experiment, we used the
The second experiment addressed RQ2 and RQ3. In the experiment, we used the pro-
proposedCNNnetworkandchangedthenumberoftrainingepisodesfordifferentRL
posed CNN network and changed the number of training episodes for different RL algo-
algorithmstodeterminetheappropriatenumberofepisodesfortrainingiRobotwiththe
rithms to determine the appropriate number of episodes for training iRobot with the RL
RLalgorithm. Thenumberofepisodescansignificantlyaffecttrainingresultssince, in
algorithm. The number of episodes can significantly affect training results since, in the
theproposedapproach,itisusedtodeterminewhentoterminatethetrainingofagent.
Therefore,findingasuitablenumberofepisodestotrainiRobotiscrucial. Likewise,inthis
experiment,forDQN(i.e.,DQN-CNNinSection4.2),PPO(i.e.,PPO-CNNinSection4.2),
and Monkey, the number of training steps was set to 10,000 steps, and the number of
trainingepisodeswassetto16,32,48,64,and128.
ToanswerRQ2andRQ3,weevaluatedthreekindsofcodecoverageresultsachieved
bydifferentRLalgorithmswithvaryingnumbersofepisodes, including(1)thebranch
coverage obtained by the shortest action sequence generated during model validation
(calledepisode-verify);(2)thebestbranchcoverageachievedbyactionsequencesgenerated
duringmodeltrainingforoneepisode(calledepisode-best);and(3)thetotalcumulative
branch coverage achieved by action sequences generated throughout the entire model
trainingprocess(calledtraining-total).
Theresultsofepisode-verify,episode-best,andtraining-totalcanserveasvaluableref-
erencesfordesigningactionsequencestotestwebapplicationsfromdifferentperspectives.
Specifically,theresultofepisode-verifycanprovideashortactionsequenceforquickly
testingawebapplicationwhileachievingbettercodecoverage. Theresultofepisode-best
can provide a deeper or more complete action sequence than that from episode-verify
to test a web application and achieve the highest code coverage. Moreover, the result
oftraining-totalcanprovidevariousactionsequencesthattogethercanachievethebest
overallcodecoveragefortestingthefunctionalityofawebapplication.
To obtain the result of episode-verify, similar to Experiment 1, we used the result
fromonevalidationrunofDQNandthebestresultfrom20validationrunsofPPO.Since
Monkeyhasnotrainingmodel,novalidationwasrequired. Figure12showsthebranch
coverageachievedbytheshortestactionsequencesgeneratedduringthevalidationrunsfor
DQNandPPO.TheresultssuggestthatPPOisslightlybetterthanDQN.Furthermore,PPO
achievesbettercodecoverageat22.30%and23.17%for48and128episodes,respectively,
whileDQNshowsnoobvioussignificantdifferencesamongdifferentnumbersofepisodes.
Inshort,thispartofexperimentshowsthatthenumberepisodeaffectstheperformance
ofthePPOalgorithmbutnotthatoftheDQNalgorithm. Itisstilltooearlytoconclude
if higher episode numbers improve the performance of the PPO algorithm in a more
generalsetting.

## Page 17

Electronics 2024, 13, x FOR PEER REVIEW 17 of 23
proposed approach, it is used to determine when to terminate the training of agent. There-
fore, finding a suitable number of episodes to train iRobot is crucial. Likewise, in this ex-
periment, for DQN (i.e., DQN-CNN in Section 4.2), PPO (i.e., PPO-CNN in Section 4.2),
and Monkey, the number of training steps was set to 10,000 steps, and the number of
training episodes was set to 16, 32, 48, 64, and 128.
To answer RQ2 and RQ3, we evaluated three kinds of code coverage results achieved
by different RL algorithms with varying numbers of episodes, including (1) the branch
coverage obtained by the shortest action sequence generated during model validation
(called episode-verify); (2) the best branch coverage achieved by action sequences gener-
ated during model training for one episode (called episode-best); and (3) the total cumu-
lative branch coverage achieved by action sequences generated throughout the entire
model training process (called training-total).
The results of episode-verify, episode-best, and training-total can serve as valuable
references for designing action sequences to test web applications from different perspec-
tives. Specifically, the result of episode-verify can provide a short action sequence for
quickly testing a web application while achieving better code coverage. The result of epi-
sode-best can provide a deeper or more complete action sequence than that from episode-
verify to test a web application and achieve the highest code coverage. Moreover, the re-
sult of training-total can provide various action sequences that together can achieve the
best overall code coverage for testing the functionality of a web application.
To obtain the result of episode-verify, similar to Experiment 1, we used the result
from one validation run of DQN and the best result from 20 validation runs of PPO. Since
Monkey has no training model, no validation was required. Figure 12 shows the branch
coverage achieved by the shortest action sequences generated during the validation runs
for DQN and PPO. The results suggest that PPO is slightly better than DQN. Furthermore,
PPO achieves better code coverage at 22.30% and 23.17% for 48 and 128 episodes, respec-
tively, while DQN shows no obvious significant differences among different numbers of
episodes. In short, this part of experiment shows that the number episode affects the per-
formance of the PPO algorithm but not that of the DQN algorithm. It is still too early to
conclude if higher episode numbers improve the performance of the PPO algorithm in a
Electronics2024,13,427 17of22
more general setting.
25
20
)
%
Electronics 2024, 13, x FOR PEER REVIEW 18 of 23
(
e
g
a 15
r
e
v
o
imCproved from 21.53 to 28.43% when the number of training episodes increases from 16
h 10 DQN
toc 128. Monkey has a similar outcome, with code coverage increasing from 19.96 to
n
a
2r
B
8.57%. However, PPO has higher code coverage (a
P
b
P
o
O
ut 26.61%) when the number of
traini5ng episodes is 48, after which the coverage decreases. Furthermore, the results also
indicate that the branch coverage of DQN, PPO, and Monkey are very similar when the
number of episodes is 48.
0
Notably, in contrast to the results of episode-verify in which PPO has better code
16 32 48 64 128
coverage with 128 episodes, the results of episode-best suggest that both DQN and Mon-
key can achieve relatively hiEgphi scooddee coverage with 128 episodes. However, it should also
be noted that as the number of episodes increases, so does traini ng time. For example, as
Figure12.Theresultsofepisode-verifyfordifferentepisodenumbers.
Fshigouwren 1 i2n. TFhige urerseu 1lt4s, othf eep tirsaoidnei-nvge rtiifmy feo ro df iDffQerNen ti nepcriseoadsee sn upmrobpeorsr.t ionally when the number
of epFiisgoudrees1 i3nschroewassetsh. ebestbranchcoverage(i.e.,episode-best)achievedbytheaction
sequeFInti cgiesus wrgeeo n1re3trh as thneodowtiinnso gtn htehee abptie sfsootd rb eerdpaunisrcionhdg cemo-bvoeedsretal, gtMrea io(nin.ienk.ge, yfeo prpidesoirffdfoeerre-mbnetss nntu)o ma wcbheorirsesvoeef dttrh abainnyi nDthgQe Nac tainodn
sPeepPqiOsuo edwnechse.esTn hg teehnreee snruaulttmesdsb hienorw oonft heta retaptinhiseionbdgre ae ndpcuihsrocinodvgee smr aisog de64eol f otDrra Q1inN28ini.n gT ohfnoiesr edinpiffdisieocrdaeetneitss nitmuhamptr botehvreesd Mofo tnrakieny-
icfnraognm pe2pe1ri.s5foo3rdtmoes2 .w8 .T4e3lhl% ew wrhehesenun lgttshi vesenhnuo mewnb oetruhogafht t rttahimien ienb gwraeinpthcish ot hdceeos pvinerorcarpegoaess eeosdff rdoDemQsi1gN6n t oionf1 2ao8cn.teMio onenps- iasondde e xis-
keyhasasimilaroutcome,withcodecoverageincreasingfrom19.96to28.57%. However,
perimental environment. However, in terms of training-total scenario (shown below),
PPOhashighercodecoverage(about26.61%)whenthenumberoftrainingepisodesis48,
Monkey is not as effective as the RL algorithms. Overall, it is still not a promising ap-
afterwhichthecoveragedecreases. Furthermore,theresultsalsoindicatethatthebranch
proach.
coverageofDQN,PPO,andMonkeyareverysimilarwhenthenumberofepisodesis48.
31
29
)
% 27
(
e
g 25
a
r
e
v 23 DQN
o
C
h 21 PPO
c
n
a 19
r Monkey
B
17
15
16 32 48 64 128
Episode
Figure13.Theresultsofepisode-bestfordifferentepisodenumbers.
Figure 13. The results of episode-best for different episode numbers.
Notably, in contrast to the results of episode-verify in which PPO has better code
cover9a:g0e7:w12ith128episodes,theresultsofepisode-bestsuggestthatbothDQNandMonkey
canachieverelativelyhighcodecoveragewith128episodes. However,itshouldalsobe
8:52:48
noted that as the number of episodes increases, so does training time. For example, as
8:38:24
showninFigure14,thetrainingtimeofDQNincreasesproportionallywhenthenumberof
episo8d:e2s4:i0n0creases.
)
s
:m 8:09:36
:h
7:55:12
(
e
m 7:40:48
iT
7:26:24
DQN
7:12:00
6:57:36
6:43:12
16 32 48 64 128
Episode
Figure 14. The training time of DQN with for different episode numbers.

## Page 18

Electronics 2024, 13, x FOR PEER REVIEW 18 of 23
improved from 21.53 to 28.43% when the number of training episodes increases from 16
to 128. Monkey has a similar outcome, with code coverage increasing from 19.96 to
28.57%. However, PPO has higher code coverage (about 26.61%) when the number of
training episodes is 48, after which the coverage decreases. Furthermore, the results also
indicate that the branch coverage of DQN, PPO, and Monkey are very similar when the
number of episodes is 48.
Notably, in contrast to the results of episode-verify in which PPO has better code
coverage with 128 episodes, the results of episode-best suggest that both DQN and Mon-
key can achieve relatively high code coverage with 128 episodes. However, it should also
be noted that as the number of episodes increases, so does training time. For example, as
shown in Figure 14, the training time of DQN increases proportionally when the number
of episodes increases.
It is worth noting that for episode-best, Monkey performs no worse than DQN and
PPO when the number of training episodes is 64 or 128. This indicates that the Monkey
can perform well when given enough time with the proposed design of actions and ex-
perimental environment. However, in terms of training-total scenario (shown below),
Monkey is not as effective as the RL algorithms. Overall, it is still not a promising ap-
proach.
31
29
)
% 27
(
e
g 25
a
r
e
v o 23 DQN
C
h 21 PPO
c
n
a 19
r Monkey
B
17
15
16 32 48 64 128
Episode
Electronics2024,13,427 18of22
Figure 13. The results of episode-best for different episode numbers.
9:07:12
8:52:48
8:38:24
8:24:00
)
s
:m 8:09:36
:h
7:55:12
Electronics 2024, 13, x FOR PEER REVI(EW 19 of 23
e
m 7:40:48
iT
7:26:24
DQN
7F:1i2g:u00re 15 shows the total cumulative branch coverage (i.e., training-total) achieved
by th6:e5 7a:c3t6ion sequences generated during the entire model training process for different
num6b:4e3r:s1 2of training episodes. The results show that for DQN, PPO, and Monkey, the total
cumulative branc1h6 coverage3 2is always g4r8eater than6 4the cover1a2g8e obtained in one episode.
Furthermore, the results also indicate that DQN always outperforms the others in differ-
Episode
ent numbers of episodes. Particularly, the highest cumulative branch c overage of DQN is
Faibgouuret 4144..2T1h%e twraiitnhin ag ttoimtael ooff D12Q8N ewpiisthodfoers.d ifferentepisodenumbers.
Figure 14. The training time of DQN with for different episode numbers.
Overall, the answer to RQ2 is that “for different RL algorithms, the suitable number
Itisworthnotingthatforepisode-best,MonkeyperformsnoworsethanDQNand
of training episodes is different.” For DQN and Monkey, 128 episodes can yield the high-
PPOwhenthenumberoftrainingepisodesis64or128. ThisindicatesthattheMonkey
est branch coverage. However, for PPO, the training result with 48 episodes is better. Nev-
can perform well when given enough time with the proposed design of actions and
ertheless, the more training episodes are used, the longer training time is required.
experimentalenvironment. However,intermsoftraining-totalscenario(shownbelow),
Moreover, the answer to RQ3 is that “different RL algorithms can have different per-
MonkeyisnotaseffectiveastheRLalgorithms. Overall,itisstillnotapromisingapproach.
formance characteristics in different cases.” Particularly, PPO can get better code coverage
Figure15showsthetotalcumulativebranchcoverage(i.e.,training-total)achieved
for an action sequence when the validation model is used. On the other hand, both DQN
bytheactionsequencesgeneratedduringtheentiremodeltrainingprocessfordifferent
and Monkey can achieve higher code coverage for an action sequence when the training
numbersoftrainingepisodes. TheresultsshowthatforDQN,PPO,andMonkey,thetotal
model is used. Furthermore, DQN performs best on the training model when considering
cumulativebranchcoverageisalwaysgreaterthanthecoverageobtainedinoneepisode.
the total cumulative code coverage of generated action sequences. As the training-total
Furthermore,theresultsalsoindicatethatDQNalwaysoutperformstheothersindifferent
resembles the actual application of software testing, we recommend the DQN-CNN
numbersofepisodes. Particularly,thehighestcumulativebranchcoverageofDQNisabout
model with 128 training episodes.
44.21%withatotalof128episodes.
50
45
) 40
%
(
e
35
g
a 30
r
e
v 25
o
C
h
20 DQN
c
n 15
a PPO
r
B 10
Monkey
5
0
16 32 48 64 128
Episode
Figure15.Theresultsoftraining-totalfordifferentepisodenumbers.
Figure 15. The results of training-total for different episode numbers.
Overall,theanswertoRQ2isthat“fordifferentRLalgorithms,thesuitablenumber
4.4. Experiment 3
of training episodes is different”. For DQN and Monkey, 128 episodes can yield the
The third experiment addressed RQ4. In this experiment, iRobot’s results were com-
highestbranchcoverage. However,forPPO,thetrainingresultwith48episodesisbetter.
pared with those of our earlier work to evaluate iRobot’s improvement resulting from the
Nevertheless,themoretrainingepisodesareused,thelongertrainingtimeisrequired.
proposed design of actions, reward function, and environment. In our earlier work, DQN
Moreover, the answer to RQ3 is that “different RL algorithms can have different
panerdf oCrNmNan nceeucrhaal rnaecttweroisrtkic ws einred uifsfeedre tnot tcraasine st”h.e Pmaortdiecul laanrdly ,thPeP rOescualtns gweetreb eetvtearlucaotdede
cuosvinegra tghee fvoarliadnataioctnio mnosdeeqlu; eancccoerwdihnegnlyt,h weev aulsiedda ttihoen empiosdoedlei-sveursiefyd .oOutncotmheeso tfhoer riRhoabnodt,
bwoitthh tDhQe NDQaNnd–CMNoNnk meyodcaeln foacr hfaieirv ecohmigphaerriscoond. ecoverageforanactionsequencewhen
Table 8 shows the comparisons between iRobot and our earlier work, including the
number of training steps, training time, branch coverage, and differences in the target ap-
plication. The results indicate that our earlier work required 500,000 steps in a single run
to train the agent successfully, taking about 59 h and 8 min to achieve branch coverage of
16.5%. With the proposed action design, the training steps were significantly reduced to
around 2% (10,000 steps), and the training time was also substantially decreased to ap-
proximately 12.54% (7 h and 25 min). Furthermore, there was a notable 1.7% enhancement
in branch coverage, which increased from 16.5 to 18.2%.
Note that in our earlier work, in order to narrow the crawling scope for training the
agent successfully, we deliberately removed the home page (i.e., login page) of the target

## Page 19

Electronics2024,13,427 19of22
thetrainingmodelisused. Furthermore,DQNperformsbestonthetrainingmodelwhen
considering the total cumulative code coverage of generated action sequences. As the
training-total resembles the actual application of software testing, we recommend the
DQN-CNNmodelwith128trainingepisodes.
4.4. Experiment3
ThethirdexperimentaddressedRQ4. Inthisexperiment,iRobot’sresultswerecom-
paredwiththoseofourearlierworktoevaluateiRobot’simprovementresultingfromthe
proposeddesignofactions,rewardfunction,andenvironment. Inourearlierwork,DQN
andCNNneuralnetworkwereusedtotrainthemodelandtheresultswereevaluated
usingthevalidationmodel;accordingly,weusedtheepisode-verifyoutcomesforiRobot
withtheDQN–CNNmodelforfaircomparison.
Table8showsthecomparisonsbetweeniRobotandourearlierwork,includingthe
number of training steps, training time, branch coverage, and differences in the target
application. Theresultsindicatethatourearlierworkrequired500,000stepsinasinglerun
totraintheagentsuccessfully,takingabout59hand8mintoachievebranchcoverageof
16.5%. Withtheproposedactiondesign,thetrainingstepsweresignificantlyreducedto
around2%(10,000steps),andthetrainingtimewasalsosubstantiallydecreasedtoapprox-
imately12.54%(7hand25min). Furthermore,therewasanotable1.7%enhancementin
branchcoverage,whichincreasedfrom16.5to18.2%.
Table8.ComparisonsbetweeniRobotandourearlierwork.
EarlierWork iRobot
Numberoftrainingsteps 500ksteps 10ksteps
Trainingtime(hh:mm:ss) 59:08:34 7:25:55
Branchcoverage 16.5% 18.2%
Theappwasmodifiedbyremovingthe
Modificationofsubjectapplication
loginpageandcorrespondinghyperlinks Theappwasnotmodified
(TimeOff.Management)
tofacilitateagenttraining
Thefirstpageofcrawling Companyregistrationpage Homepage(i.e.,loginpage)
Notethatinourearlierwork,inordertonarrowthecrawlingscopefortrainingthe
agentsuccessfully,wedeliberatelyremovedthehomepage(i.e.,loginpage)ofthetarget
applicationandthehyperlinkstotheloginpage,andsetthefirstpageofcrawlingtothe
registrationpage. Thus,oncetheregistrationwascompletedsuccessfully,thecrawlercould
explorethetargetapplicationcontinuouslywithouttheneedtologinagain. Theproposed
designofactions,however,requiresnosuchrestrictionandenablesthetrainingtostart
fromthehomepageofthetargetwebapplication. Thisalsosuggeststhattheproposed
designofactionscanhelpsolvetheproblemofagenttraininginexperimentsandachieve
muchfasterconvergenceofthetrainingprocessthanourearlierwork.
Overall, the answer to RQ4 is, “Yes, the new iRobot indeed can improve branch
coveragebyapproximately1.7%comparedtoourearlierwork”. Furthermore,itcanmake
thetrainingprocessconvergefasterandsignificantlyreducetrainingtimeto12.54%. The
improvementinthetrainingtimeismainlyduetothedesignoftheactions. Withthenew
setofactions,iRobotcanexplorewebpagestoagreaterextentratherthanlearningwhich
valuetouseforwhichfield. Moreover,theinvalidinputshelpiRobotexecutemoreerror
detectioncodesandimprovecodecoverage.
4.5. Discussions
WhileourRLmethodcaneffectivelyguidewebcrawlerstoimprovecodecoverage
ofanapplicationundertest(AUT),ithassomelimitations. First,ourcurrentexperiments
dependoncodecoveragetotraintheagent. However,thecodecoveragetoolislanguage-

## Page 20

Electronics2024,13,427 20of22
dependent,asitneedstoinstrumentthecodeundertest. Webapplicationscanusevarious
programminglanguagessuchasnode.js,Java,php,python,ASP.NET,etc. Therefore,we
needdifferentcoveragetoolsforcrawlingwebapplicationsimplementedwithdifferent
languages. Thisobservabilityissueisamajorchallengeforconductingmoreexperiments
inthisstudy. Inthefuture,weplantousealternativemethodsbesidescodecoveragein
iRobottoexploreandtestwebapplicationswrittenindifferentprogramminglanguages.
Onepossibilityistousepagecomparison[34]tomeasurethenumberofpagesexplored.
Thiswillbepartofourfuturework.
Second,webapplicationsmaychangelaterintheevolutionormaintenancephase.
Dependingonhowthechangesareimplemented,ifthechangesonlycausesminorchanges
totheDOMoftheresponsepages,theiRobottrainingmaystillbeapplicable. Recallthat
theneuralnetwork, inasense, actsasatypeofnonlinearinterpolator. However, ifthe
changesmodifytheDOMoftheresponsepageslargely,iRobotmayneedtoberetrained
with additional actions in order to cover the new or modified code. Nevertheless, the
proposedapproachreducesthetrainingtimeto12.54%ascomparedtoourpreviousstudy
andtherebyreducesthecostofretrainingiRobotforwebapplicationsunderdevelopment
inthelaterstages.
Third, wepopulatedtheinputfieldswithtestdatabeforesubmittingformsinthe
experiments. Thisarrangementmightpreventsomecodepathsfrombeingexecutedin
web applications. In our design, iRobot has actions to fill both valid and invalid input
values. DuringtheexplorationperiodofRLtraining,iRobotchoosesactionsrandomly. It
hasacertainprobabilityofchoosingactionsa ora toprovideinvalidinputs. Therefore,it
1 2
canalsotestcoderelatedtoincorrectinputvalues,albeitnotcompletely. Totestawider
varietyofinputtypesandcombinations,weneedtoincreasetheentriesinTables3and4.
Thispartcanbeeasilyextended,thoughwedonotshowitinthispaper.
Next,weobtainedtheinputdataencodedintheactionsfromadictionarythatwe
preparedmanuallyfortheAUTunderstudy. ForotherAUTsunderstudy, weneedto
identifybothvalidandinvalidinputsfortheformfieldsoftheapplicationtopreparean
input dictionary. Although we can use the same dictionary for form fields in the same
categoryandapplyhumantesters’domainknowledgewhenpreparinginputs,thecost
canbehighforcomplexwebapplicationswithmanywebformsandfields. Moreover,we
expectthattheperformanceofiRobotwillsufferiftheinputdictionarybecomeslarge,asit
willneedmoreactionstocompletewebformssuccessfully. Inthefuture,weplantouse
existingtoolstoautomaticallygenerateinputvalues.
Finally, our study was based on only one AUT. It is crucial to know whether the
proposed approach can be applied to other AUTs. To this point, we have conducted a
preliminarystudytochecktheapplicabilityofourapproachtootherAUTs. Theresultsare
promising. Asthisworkisstillongoing,weareunabletoreportourfindingshere.
ThepresentdesignreliesonthechangeofDOMorcoveragevectortodetectpossible
changesindynamicwebpages. Generally,whenusersinputvaluesintoawebformand
clickthesubmitbutton,theDOMoftheresultingpagetypicallyundergoessomedegreeof
changetodisplaythesubmissionoutcome,eveninthecaseofinvalidinputs. Otherwise,
theuserprobablyhasnowaytoknowthesubmissionresult. ThischangeintheDOMmay
manifestasapopupalert,anerrormessage,oramodificationinthecoloroftheinvalid
formfield,achievedthroughtheexecutionofcertainsourcecode. Thisisbecause,without
changingtheDOMofresponsepage,userswillfinditdifficulttovisuallyseedifferencesin
thesubmissionresponse. However,ifthewebpageusesafront-endcodetodetectinput
errorsandtopopoutanerrormessage,iRobotwillhavenoinformationonthissituation.
Internetsecurityanddigitalprivacyhavebecomeimportantissuesine-services. In
ourcontext,weusewebcrawlerstoautomaticallyexploreandtestAUTsforcodecoverage.
We fill in fields with artificial values, not real or confidential ones. Our approach does
notgatherorindexthecontentofwebpagesacrosstheInternet,soitdoesnotraiseany
privacyissues. ForInternetsecurity,wetestAUTsinaprivateandisolatednetworkinour

## Page 21

Electronics2024,13,427 21of22
experimentalsettings. OurapproachdoesnotdependonInternetresources. Therefore,
securityconcernsareminimal.
5. ConclusionsandFutureWork
Thispaperintroducesaninnovativereinforcementlearningapproachaimedatguiding
web crawlers in automatically selecting a sequence of input actions to maximize code
coverageduringexplorationofawebapplicationundertest. Specifically,theproposed
actiondesigniscapableofemulatinghumantesterbehavior, empoweringtheagentto
efficientlypopulateinputfieldsandenhancecoveragebythecrawlingcode. Furthermore,
aconvolutionalneuralnetwork(CNN)ispresented,andvariousreinforcementlearning
algorithmsareemployedtotraintheiRobotagentinselectingactions. Experimentalresults
reveal that, with the proposed actions, the presented CNN network attains better code
coverage compared to other neural networks when utilizing DQN or PPO algorithms.
Additionally,incomparisontopreviousstudies,iRobotdemonstratesanotableincrease
in branch coverage by approximately 1.7% while concurrently achieving a significant
reductionintrainingtimeto12.54%.
Inthefuture,weplantoconductmoreexperimentswithdifferenthyperparameter
settingsfortheagentandtotestdifferenttargetapplications. Additionally,wearecurrently
investigating the use of word embedding to represent the features extracted from web
pagestotrainiRobottobetterunderstandthewebpagesandselectproperinputactions.
Next,wealsoplantoextendthisapproachbytrainingiRobotwithalargenumberofweb
pagesobtainedfromdifferentapplicationstoseeifiRobotcangainsomeknowledgefrom
previouslytrainedapplications. Finally,weplantostudytheuseofpagecomparisonto
measurethenumberofpagesexploredtoreplacethecoveragevectorincomputingrewards.
AuthorContributions:Conceptualization,C.-H.L.andS.D.Y.;methodology,C.-H.L.andS.D.Y.;soft-
ware,Y.-C.C.;validation,C.-H.L.,S.D.Y.andY.-C.C.;formalanalysis,C.-H.L.andS.D.Y.;investigation,
C.-H.L.andY.-C.C.;resources,Y.-C.C.;datacuration,Y.-C.C.;writing—originaldraftpreparation,
C.-H.L.;writing—reviewandediting,C.-H.L.andS.D.Y.;visualization,Y.-C.C.;supervision,C.-H.L.
andS.D.Y.;projectadministration,C.-H.L.andS.D.Y.;fundingacquisition,C.-H.L.andS.D.Y.All
authorshavereadandagreedtothepublishedversionofthemanuscript.
Funding:ThisresearchwasfundedinpartbytheNationalScienceandTechnologyCouncil(NSTC)
ofTaiwan,undergrantnumberNSTC112-2221-E-027-049-MY2.
DataAvailabilityStatement:Thedatapresentedinthispaperareavailableuponrequestfromthe
correspondingauthor.
ConflictsofInterest: AuthorChiu,Y.-C.wasemployedbythecompanyPhisonElectronicsCorp.
Theremainingauthorsdeclarethattheresearchwasconductedintheabsenceofanycommercialor
financialrelationshipsthatcouldbeconstruedasapotentialconflictofinterest.
References
1. Deursen,A.V.;Mesbah,A.;Nederlof,A.Crawl-basedAnalysisofWebApplications: ProspectsandChallenges. Sci. Comput.
Program.2015,97,173–180.[CrossRef]
2. Crawljax.Availableonline:https://github.com/zaproxy/crawljax(accessedon25October2023).
3. Mesbah,A.;Deursen,A.V.;Lenselink,S.CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterface
StateChanges.ACMTrans.Web2012,6,1–30.[CrossRef]
4. Wikipedia.Availableonline:https://en.wikipedia.org/wiki/Code_coverage(accessedon10January2024).
5. Sutton,R.S.;Barto,A.G.ReinforcementLearning:AnIntroduction,2nded.;MITPress:Cambridge,MA,USA,2018.
6. Ho,W.-H.TrainingaTestAgenttoIncreaseCodeCoverageBasedonDQNforWebApplications. Master’sThesis,National
TaipeiUniversityofTechnology,Taipei,Taiwan,2018.
7. Arulkumaran,K.;Deisenroth,M.P.;Brundage,M.;Bharath,A.A.DeepReinforcementLearning: ABriefSurvey. IEEESignal
Process.Mag.2017,34,26–38.[CrossRef]
8. Schmidhuber,J.DeepLearninginNeuralNetworks:AnOverview.NeuralNetw.2015,61,85–117.[CrossRef][PubMed]
9. Krizhevsky,A.;Sutskever,I.;Hinton,G.E.ImageNetClassificationwithDeepConvolutionalNeuralNetworks.Commun.ACM
2017,60,84–90.[CrossRef]

## Page 22

Electronics2024,13,427 22of22
10. Sierla,S.;Ihasalo,H.;Vyatkin,V.AReviewofReinforcementLearningApplicationstoControlofHeating,VentilationandAir
ConditioningSystems.Energies2022,15,3526.[CrossRef]
11. Waqar, M.; Imran; Zaman, M.A.; Muzammal, M.; Kim, J.TestSuitePrioritizationBasedonOptimizationApproachUsing
ReinforcementLearning.Appl.Sci.2022,12,6772.[CrossRef]
12. Lin, J.-W.; Wang, F.; Chu, P. Using Semantic Similarity in Crawling-Based Web Application Testing. In Proceedings of the
2017IEEEInternationalConferenceonSoftwareTesting,VerificationandValidation(ICST),Tokyo,Japan,13–17March2017;
pp.138–148.
13. Alex,G.CoverageRewarded:TestInputGenerationviaAdaptation-basedProgramming.InProceedingsofthe26thIEEE/ACM
InternationalConferenceonAutomatedSoftwareEngineering(ASE),Lawrence,KS,USA,6–10November2011;pp.380–383.
14. Carino,S.;Andrews,J.H.DynamicallyTestingGUIsUsingAntColonyOptimization.InProceedingsofthe30thIEEE/ACM
InternationalConferenceonAutomatedSoftwareEngineering(ASE),Lincoln,NE,USA,9–13November2015;pp.138–148.
15. Kim,J.;Kwon,M.;Yoo,S.GeneratingTestInputwithDeepReinforcementLearning. InProceedingsoftheIEEE/ACM11th
InternationalWorkshoponSearch-BasedSoftwareTesting(SBST),Gothenburg,Sweden,28–29May2018;pp.51–58.
16. Liu,C.-H.;Chen,W.-K.;Sun,C.-C.GUIDE:AnInteractiveandIncrementalApproachforCrawlingWebApplications.J.Super-
comput.2020,76,1562–1584.[CrossRef]
17. Zheng,Y.;Liu,Y.;Xie,X.;Liu,Y.;Ma,L.;Hao,J.;Liu,Y.AutomaticWebTestingUsingCuriosity-DrivenReinforcementLearning.
InProceedingsofthe43rdInternationalConferenceonSoftwareEngineering(ICSE),Madrid,Spain,22–30May2021;pp.423–435.
18. Liu,E.Z.;Guu,K.;Pasupat,P.;Shi,T.;Liang,P.ReinforcementLearningonWebInterfacesUsingWorkflow-GuidedExploration.In
ProceedingsoftheInternationalConferenceonLearningRepresentations(ICLR),Vancouver,BC,Canada,30April–3May2018.
19. Shi,T.;Karpathy,A.;Fan,L.;Hernandez,J.;Liang,P.WorldofBits:AnOpen-DomainPlatformforWeb-BasedAgents.InProceedings
ofthe34thInternationalConferenceonMachineLearning(ICML),Sydney,Australia,6–11August2017;pp.3135–3144.
20. Sunman,N.;Soydan,Y.;Sözer,H.Automatedwebapplicationtestingdrivenbypre-recordedtestcases. J.Syst. Softw. 2022,
193,111441.[CrossRef]
21. Liu,Y.;Li,Y.;Deng,G.;Liu,Y.;Wan,R.;Wu,R.;Ji,D.;Xu,S.;Bao,M.Morest:Model-basedRESTfulAPItestingwithexecution
feedback.InProceedingsofthe44thInternationalConferenceonSoftwareEngineering,Pittsburhg,PA,USA,25–27May2022;
pp.1406–1417.
22. Yandrapally, R.K.; Mesbah, A.Fragment-basedtestgenerationforwebapps. IEEETrans. Softw. Eng. 2022, 49, 1086–1101.
[CrossRef]
23. Sherin,S.;Muqeet,A.;Khan,M.U.;Iqbal,M.Z.QExplore:Anexplorationstrategyfordynamicwebapplicationsusingguided
search.J.Syst.Softw2023,195,111512.[CrossRef]
24. Document Object Model (DOM) Technical Reports. Available online: https://www.w3.org/DOM/DOMTR (accessed on
20October2023).
25. OpenAIGym.Availableonline:https://gym.openai.com/(accessedon18August2023).
26. Tensorflow.Availableonline:https://www.tensorflow.org/(accessedon15September2023).
27. TimeOff.Management.Availableonline:https://github.com/timeoff-management/application(accessedon20October2023).
28. Istanbul.Availableonline:https://istanbul.js.org/(accessedon20October2023).
29. Mnih, V.; Kavukcuoglu, K.; Silver, D.; Rusu, A.A.; Veness, J.; Bellemare, M.G.; Graves, A.; Riedmiller, M.; Fidjeland, A.K.;
Ostrovski,G.;etal.Human-levelControlthroughDeepReinforcementLearning.Nature2015,518,529–533.[CrossRef][PubMed]
30. Schulman, J.; Wolski, F.; Dhariwal, P.; Radford, A.; Klimov, O. Proximal Policy Optimization Algorithms. arXiv 2017,
arXiv:1707.06347v2.
31. Hochreiter,S.;Schmidhuber,J.LongShort-TermMemory.NeuralComput.1997,9,1735–1780.[CrossRef][PubMed]
32. MultilayerPerceptron.Availableonline:https://en.wikipedia.org/wiki/Multilayer_perceptron(accessedon1November2023).
33. OpenAIStableBaselines.Availableonline:https://github.com/hill-a/stable-baselines(accessedon1November2023).
34. PageCompare.Availableonline:https://github.com/TeamHG-Memex/page-compare(accessedon1November2023).
Disclaimer/Publisher’sNote: Thestatements, opinionsanddatacontainedinallpublicationsaresolelythoseoftheindividual
author(s)andcontributor(s)andnotofMDPIand/ortheeditor(s).MDPIand/ortheeditor(s)disclaimresponsibilityforanyinjuryto
peopleorpropertyresultingfromanyideas,methods,instructionsorproductsreferredtointhecontent.

