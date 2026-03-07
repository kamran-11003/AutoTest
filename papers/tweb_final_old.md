# Tweb Final Old

**Source:** tweb_final_old.pdf  
**Converted:** 2026-01-26 09:23:42

---

## Page 1

Delft University of Technology
Crawling Ajax-based web applications through dynamic analysis of user interface state
changes
Mesbah, A; van Deursen, A.; Lenselink, S
DOI
10.1145/2109205.2109208
Publication date
2012
Document Version
Accepted author manuscript
Published in
ACM Transactions on the Web
Citation (APA)
Mesbah, A., van Deursen, A., & Lenselink, S. (2012). Crawling Ajax-based web applications through
dynamic analysis of user interface state changes. ACM Transactions on the Web, 6(1), 1-30.
https://doi.org/10.1145/2109205.2109208
Important note
To cite this publication, please use the final published version (if applicable).
Please check the document version above.
Copyright
Other than for strictly personal use, it is not permitted to download, forward or distribute the text or part of it, without the consent
of the author(s) and/or copyright holder(s), unless the work is under an open content license such as Creative Commons.
Takedown policy
Please contact us and provide details if you believe this document breaches copyrights.
We will remove access to the work immediately and investigate your claim.
This work is downloaded from Delft University of Technology.
For technical reasons the number of authors shown on this cover page is limited to a maximum of 10.

## Page 2

0
Crawling AJAX-based Web Applications through
Dynamic Analysis of User Interface State Changes
ALIMESBAH,UniversityofBritishColumbia
ARIEVANDEURSEN,DelftUniversityofTechnology
STEFANLENSELINK,DelftUniversityofTechnology
Using JavaScript and dynamic DOM manipulation on the client-side of web applications is becoming a
widespread approach for achieving rich interactivity and responsiveness in modern web applications. At
the same time, such techniques, collectively known as Ajax, shatter the metaphor of web ‘pages’ with
unique URLs, on which traditional web crawlers are based. This paper describes a novel technique for
crawling Ajax-based applications through automatic dynamic analysis of user interface state changes in
web browsers. Our algorithm scans the DOM-tree, spots candidate elements that are capable of changing
thestate,fireseventsonthosecandidateelements,andincrementallyinfersastatemachinemodellingthe
various navigational paths and states within an Ajax application. This inferred model can be used, for
instance,inprogramcomprehension,analysisandtestingofdynamicwebstates,orforgeneratingastatic
versionoftheapplication.Inthispaper,wediscussoursequentialandconcurrentAjaxcrawlingalgorithms.
WepresentouropensourcetoolcalledCrawljax,whichimplementstheconceptsandalgorithmsdiscussed
in this paper. Additionally, we report a number of empirical studies in which we apply our approach to a
numberofopen-sourceandindustrialwebapplicationsandelaborateontheobtainedresults.
CategoriesandSubjectDescriptors:H.5.4[Information Interfaces and Presentation]:Hypertext/Hy-
permedia—Navigation;H.3.3[InformationSearchandRetrieval]:Searchprocess;D.2.2[SoftwareEn-
gineering]:DesignToolsandTechniques
GeneralTerms:Design,Algorithms,Experimentation.
AdditionalKeyWordsandPhrases:Crawling,ajax,web2.0,hiddenweb,dynamicanalysis,domcrawling
ACMReferenceFormat:
Mesbah,A.,vanDeursen,A.,andLenselink,S.2011.CrawlingAJAX-basedWebApplicationsthrough
DynamicAnalysisofUserInterfaceStateChangesACMTrans.Web0,0,Article0(2011),30pages.
DOI=10.1145/0000000.0000000http://doi.acm.org/10.1145/0000000.0000000
1. INTRODUCTION
Thewebasweknowitisundergoingasignificantchange.Atechnologythathasgained
a prominent position lately, under the umbrella of Web 2.0, is AJAX (Asynchronous
JAVASCRIPT and XML) [Garrett 2005], in which the combination of JAVASCRIPT and
Document Object Model (DOM) manipulation, along with asynchronous server com-
Thisisasubstantiallyrevisedandexpandedversionofourpaper‘CrawlingAJAXbyInferringUserInter-
faceStateChanges’,whichappearedintheProceedingsofthe8thInternationalConferenceonWebEngi-
neering(ICWE),IEEEComputerSociety,2008[Mesbahetal.2008].
Authors’address:A.MesbahiswiththedepartmentofElectricalandComputerEngineering,Universityof
BritishColumbia,2332MainMall,V6T1Z4Vancouver,BC,Canada.E-mail:amesbah@ece.ubc.ca
A. van Deursen and S. Lenselink are with the Faculty of Electrical Engineering, Mathematics and Com-
puter Science, Delft University of Technology, Mekelweg 4, 2628CD Delft, The Netherlands. E-mail:
arie.vandeursen@tudelft.nlandS.R.Lenselink@student.tudelft.nl
Permissiontomakedigitalorhardcopiesofpartorallofthisworkforpersonalorclassroomuseisgranted
withoutfeeprovidedthatcopiesarenotmadeordistributedforprofitorcommercialadvantageandthat
copiesshowthisnoticeonthefirstpageorinitialscreenofadisplayalongwiththefullcitation.Copyrights
forcomponentsofthisworkownedbyothersthanACMmustbehonored.Abstractingwithcreditisper-
mitted.Tocopyotherwise,torepublish,topostonservers,toredistributetolists,ortouseanycomponent
ofthisworkinotherworksrequirespriorspecificpermissionand/orafee.Permissionsmayberequested
fromPublicationsDept.,ACM,Inc.,2PennPlaza,Suite701,NewYork,NY10121-0701USA,fax+1(212)
869-0481,orpermissions@acm.org.
(cid:13)c 2011ACM1559-1131/2011/-ART0$10.00
DOI10.1145/0000000.0000000 http://doi.acm.org/10.1145/0000000.0000000
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 3

0:2 Mesbahetal.
municationisusedtoachieveahighlevelofuserinteractivity.Highlyvisibleexamples
includeGmailandGoogleDocs.
Withthisnewchangeindevelopingwebapplicationscomesawholesetofnewchal-
lenges, mainly due to the fact that AJAX shatters the metaphor of a web ‘page’ upon
whichmanywebtechnologiesarebased.Amongthesechallengesarethefollowing:
Searchability. ensuring that AJAX sites are crawled and indexed by the general
search engines, instead of (as is currently often the case) being ignored by them
becauseoftheuseofclient-sidescriptinganddynamicstatechangesintheDOM;
Testability. systematicallyexercisingdynamicuserinterface(UI)elementsandan-
alyzing AJAX statestofindabnormalitiesanderrors;
One way to address these challenges is through the use of a crawler that can au-
tomatically walk through different states of a highly dynamic AJAX site and create a
modelofthenavigationalpathsandstates.
Generalwebsearchengines,suchasGoogleandBing,coveronlyaportionoftheweb
calledthepubliclyindexablewebthatconsistsofthesetofwebpagesreachablepurely
by following hypertext links, ignoring forms [Barbosa and Freire 2007] and client-
side scripting. The web content behind forms and client-side scripting is referred to
as the hidden-web, which is estimated to comprise several millions of pages [Barbosa
and Freire 2007]. With the wide adoption of AJAX techniques that we are witnessing
today this figure will only increase. Although there has been extensive research on
crawling and exposing the data behind forms [Barbosa and Freire 2007; de Carvalho
and Silva 2004; Lage et al. 2004; Ntoulas et al. 2005; Raghavan and Garcia-Molina
2001],crawlingthehidden-webinducedasaresultofclient-sidescriptinghasgained
verylittleattentionsofar.
Crawling AJAX-based applications is fundamentally more difficult than crawling
classical multi-page web applications. In traditional web applications, states are ex-
plicit, and correspond to pages that have a unique URL assigned to them. In AJAX
applications, however, the state of the user interface is determined dynamically,
through changes in the DOM that are only visible after executing the corresponding
JAVASCRIPT code.
In this paper, we propose an approach to analyze these user interface states auto-
matically. Our approach is based on a crawler that can exercise client-side code and
identifyclickableelements(whichmaychangewitheveryclick)thatchangethestate
within the browser’s dynamically built DOM. From these state changes, we infer a
state-flowgraph,whichcapturesthestatesoftheuserinterfaceandthepossibletran-
sitionsbetweenthem.Theunderlyingideashavebeenimplementedinanopensource
tool called CRAWLJAX.1 To the best of our knowledge, CRAWLJAX is the first and cur-
rently the only available tool that can detect dynamic contents of AJAX-based web
applicationsautomaticallywithoutrequiringspecificURLsforeachwebstate.
Theinferredmodelcanbeused,forinstance,toexposeAJAXsitestogeneralsearch
engines or to examine the accessibility [Atterer and Schmidt 2005] of different dy-
namic states. The ability to automatically exercise all the executable elements of an
AJAX sitegivesusapowerfultestmechanism. CRAWLJAX hassuccessfullybeenused
for conducting automated model-based and invariant-based testing [Mesbah and van
Deursen 2009], security testing [Bezemer et al. 2009], regression testing [Roest et al.
2010],andcross-browsercompatibilitytesting[MesbahandPrasad2011]ofAJAXweb
applications.
Wehaveperformedanumberofempiricalstudiestoanalyzetheoverallperformance
ofourapproach.Weevaluatetheeffectivenessinretrievingrelevantclickablesandas-
1http://crawljax.com
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 4

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:3
sess the quality and correctness of the detected states and edges. We also examine
the performance of our crawling tool as well as the scalability in crawling AJAX ap-
plications with a large number of dynamic states and clickables. The experimental
benchmarksspanfromopensourcetoindustrialwebapplications.
Thispaperisarevisedandextendedversionofouroriginalpaperin2008[Mesbah
et al. 2008]. The extensions in this paper are based on three years of tool usage and
refinements.Inaddition,wereportonournewmulti-threaded,multi-browsercrawling
approachaswellasanew(industrial)empiricalstudy,evaluatingitsinfluenceonthe
runtimeperformance.Theresultsofourstudyshowthatbyusing5browsersinstead
of1,wecanachieveadecreaseofupto65%incrawlingruntime.
Thepaperisfurtherstructuredasfollows.Westartout,inSection2byexploringthe
difficultiesofcrawlingAJAX.InSection3wepresentadetaileddiscussionofourAJAX
crawlingalgorithmandtechnique.InSection4,weextendoursequentialcrawlingap-
proach to a concurrent multiple-browser crawling algorithm. Section 5 discusses the
implementation of our tool CRAWLJAX. In Section 6, the results of applying our tech-
niques to a number of AJAX applications are shown, after which Section 7 discusses
the findings and open issues. We conclude with a survey of related work, a summary
ofourkeycontributionsandsuggestionsforfuturework.
2. CHALLENGESOFCRAWLINGAJAX
AJAX-based web applications have a number of properties that make them very chal-
lengingtocrawlautomatically.
2.1. Client-sideExecution
ThecommongroundforallAJAXapplicationsisaJAVASCRIPTengine,whichoperates
between the browser and the web server [Mesbah and van Deursen 2008]. This en-
gine typically deals with server communication and user interface modifications. Any
search engine willing to approach such an application must have support for the exe-
cutionofthescriptinglanguage.Equippingacrawlerwiththenecessaryenvironment
complicates its design and implementation considerably. The major search engines
such as Google and Bing currently have little or no support for executing scripts and
thusignorecontentproducedby JAVASCRIPT,2 duetoscalabilityandsecurityissues.
2.2. StateChangesandNavigation
Traditional web applications are based on the multi-page interface paradigm consist-
ingofmultiplepageseachhavingauniqueURL.InAJAXapplications,noteverystate
changenecessarilyhasanassociatedREST-based[FieldingandTaylor2002]URI.Ul-
timately, an AJAX application could consist of a single-page with a single URL [Mes-
bah and van Deursen 2007]. This characteristic makes it difficult for a search engine
toindexandpointtoaspecificstateinan AJAX application.Crawlingtraditionalweb
pagesconstitutesextractingandfollowingthehypertextlinks(thesrcattributeofan-
chortags)oneachpage.In AJAX,hypertextlinkscanbereplacedbyeventswhichare
handled by JAVASCRIPT; i.e., it is not possible any longer to navigate the application
bysimplyextractingandretrievingtheinternalhypertextlinks.
2.3. DynamicDocumentObjectModel(DOM)
Crawlingandindexingtraditionalwebapplicationsconsistsoffollowinglinks,retriev-
ingandsavingtheHTMLsourcecodeofeachpage.ThestatechangesinAJAXapplica-
tions are dynamically represented through the run-time changes on the DOM-tree in
the browser. This means that the initial HTML source code retrieved from the server
2http://code.google.com/web/ajaxcrawling/docs/getting-started.html
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 5

0:4 Mesbahetal.
1 <A href="javascript:OpenNewsPage();">...
2 <A href="#" onClick="OpenNewsPage();">...
3 <DIV onClick="OpenNewsPage();">...
5 <DIV class="news"/>
6 <SPAN id="content"/>
7 <!-- jQuery function attaching events to elements having attribute class="news".
8 The news contents are injected into the SPAN element -->
9 <script>
10 $(".news").click(function() {
11 $("#content").load("news.html");
12 });
13 </script>
Fig.1:Differentwaysofattachingeventstoelements.
doesnotrepresentthestatechanges.AnAJAXcrawlerwillneedtohaveaccesstothis
run-timedynamicdocumentobjectmodeloftheapplication.
2.4. Delta-communication
AJAX applications rely on a delta-communication [Mesbah and van Deursen 2008]
style of interaction in which merely the state changes are exchanged asynchronously
between the client and the server, as opposed to the full-page retrieval approach in
traditionalwebapplications.Retrievingandindexingthedataservedbytheserver,for
instance,throughaproxybetweentheclientandtheserver,couldhavetheside-effect
oflosingthecontextandactualmeaningofthechangesbecausemostofsuchupdates
become meaningful after they have been processed by the JAVASCRIPT engine on the
clientandinjectedintotheruntimeDOM-tree.
2.5. ClickableElementsChangingtheInternalState
ToillustratethedifficultiesinvolvedincrawlingAJAX,considerFigure1.Itisahighly
simplified example, showing different ways in which a news page can be opened. The
examplecodeshowshowin AJAX,itisnotjustthehypertextlinkelementthatforms
the doorway to the next state. Note the way events (e.g., onClick, onMouseOver) can
be attached to DOM elements at run-time. As can be seen, a DIV element (line 3) can
haveanonclickeventattachedtoitsothatitbecomesaclickableelementcapableof
changingtheinternalDOMstateoftheapplicationwhenclicked.
Eventhandlerscanalsobedynamicallyregisteredusing JAVASCRIPT.ThejQuery3
code(lines5–13)attachesafunctiontotheonClickeventlisteneroftheelementwith
classattributenews.Whenthiselementisclicked,thenewscontentisretrievedfrom
theserverandinjectedintotheSPANelementwithIDcontent.
TherearedifferentwaystoattacheventlistenerstoDOMelements.Forinstance,if
wehavethefollowinghandler:
var handler = function() { alert(’Element clicked!’) };
wecanattachittoanonClicklistenerofaDOMelementeinthefollowingways:
(1) e.onclick = handler;
(2) if(e.addEventListener) {
e.addEventListener(‘click’, handler, false)
} else if(e.attachEvent) { // IE
e.attachEvent(‘onclick’, handler)
}
3http://jquery.com
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 6

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:5
ThefirstcasepresentsthetraditionalwayofattachinghandlerstoDOMelements.
Inthiscase,wecanexaminetheDOMelementatruntimeandfindoutthatithasthe
handler attached to its onClick attribute. The second case show how handlers could
beattachedtoDOMelementsthroughtheDOMLevel2API.Inthiscase,however,by
examining the DOM element it is not possible to find information about the handler,
since the event model (DOM Level 2 Events [Pixley 2000]) maintaining the handler
registration information is separated from the DOM core model itself. Hence, auto-
matically finding these clickable elements at runtime is another non-trivial task for
an AJAX crawler.
3. AMETHODFORCRAWLINGAJAX
The challenges discussed in the previous section should make it clear that crawling
AJAXismoredemandingthancrawlingtheclassicalweb.Inthissection,weproposea
dynamicanalysisapproach,inwhichweopenthe AJAX applicationinabrowser,scan
theDOM-treeforcandidateelementsthatarecapableofchangingthestate,fireevents
onthoseelements,andanalyzetheeffectsontheDOM-tree.Basedonouranalysis,we
inferastate-flowgraphrepresentingtheuserinterfacestatesandpossibletransitions
betweenthem.
In this section, we first present the terminology used in this paper followed by a
discussionofthemostimportantcomponentsofourcrawlingtechnique,asdepictedin
Figure3.
3.1. Terminology
3.1.1. UserInterfaceStateandStateChanges. Intraditionalmulti-pagewebapplications,
eachstateisrepresentedbyaURLandthecorrespondingwebpage.InAJAXhowever,
it is the internal structure of the DOM-tree of the (single-page) user interface that
representsastate.Therefore,toadoptagenericapproachforallAJAXsites,wedefine
a state change as a change on the DOM tree caused by (1) either client-side events
handledbythe AJAX engine;(2)orserver-sidestatechangespropagatedtotheclient.
3.1.2. StateTransitionandClickable. Onthebrowser,theend-usercaninteractwiththe
web application through the user interface: click on an element, bring the mouse-
pointer over an element, and so on. These actions can cause events that, as described
above, can potentially change the state of the application. We call all DOM elements
that have event-listeners attached to them and can cause a state transition, clickable
elements. For the sake of simplicity, we use the click event type to present our ap-
proach, note, however, that other event types can be used just as well to analyze the
effectsontheDOMinthesamemanner.
3.1.3. TheState-flowGraph. TobeabletonavigateanAJAX-basedwebapplication,the
application can be modelled by recording the click trails to the various user interface
state changes. To record the states and transitions between them, we define a state-
flowgraphasfollows:
DEFINITION 1. A state-flow graph G for an AJAX site A is a labeled, directed
graph,denotedbya4tuple<r,V,E,L>where:
(1) r istherootnode(calledIndex)representingtheinitialstateafterAhasbeenfully
loadedintothebrowser.
(2) V isasetofverticesrepresentingthestates.Eachv ∈V representsaruntimeDOM
stateinA.
(3) E is a set of (directed) edges between vertices. Each (v ,v ) ∈ E represents a click-
1 2
ablecconnectingtwostatesifandonlyifstatev isreachedbyexecutingcinstate
2
v .
1
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 7

0:6 Mesbahetal.
Index
<click, xpath://DIV[1]/SPAN[4]> <mouseover, id:c_9><click, xpath://A[2]>
S_1 S_2 <click, xpath://DIV[3]/IMG[1]>
<click, id:c_3> <mouseover, xpath://SPAN[2]/A[2]>
S_4 S_3
<click, xpath://SPAN[2]/A[3]> <click, xpath://SPAN[2]/A[3]>
S_5
Fig.2:Thestate-flowgraphvisualization.
(4) L is a labelling function that assigns a label, from a set of event types and DOM
elementproperties,toeachedge.
(5) Gcanhavemulti-edgesandbecyclic.
Asanexampleofastate-flowgraph,Figure2depictsthevisualizationofthestate-
flowgraphofasimpleAJAXsite.Theedgesbetweenstatesarelabeledwithanidenti-
fication (either via its ID-attribute or via an XPath expression) of the clickable. Thus,
clicking on the //DIV[1]/SPAN[4] element in the Index state leads to the S 1 state,
fromwhichtwostatesaredirectlyreachablenamelyS 3andS 4.
Thestate-flowgraphiscreatedincrementally.Initially,itonlycontainstherootstate
andnewstatesarecreatedandaddedastheapplicationiscrawledandstatechanges
areanalyzed.
Thefollowingcomponents,alsoshowninFigure3,participateintheconstructionof
thestate-flowgraph:
—EmbeddedBrowser:Theembeddedbrowserprovidesacommoninterfaceforaccess-
ingtheunderlyingenginesandruntimeobjects,suchastheDOMandJAVASCRIPT.
—Robot: A robot is used to simulate user actions (e.g., click, mouseOver, text input)
ontheembeddedbrowser.
—Controller: The controller has access to the embedded browser’s DOM. It also con-
trols the Robot’s actions and is responsible for updating the state machine when
relevantchangesoccurontheDOM.
—DOM Analyzer: The analyzer is used to check whether the DOM-tree is changed
after an event has been fired by the robot. In addition, it is used to compare DOM-
treeswhensearchingforduplicate-statesinthestatemachine.
—FiniteStateMachine:Thefinitestatemachineisadatacomponentmaintainingthe
state-flowgraph,aswellasapointertothestatebeingcurrentlycrawled.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 8

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:7
Robot
UI
event Embedded
Browser
generate event update event
DOM event
Crawljax Controller Ajax
update Engine
Analyze Legend
Dom Access
Control flow
DOM State Event invocation
update
Analyzer Machine Data component
Processing component
Fig.3:Processingviewofthecrawlingarchitecture.
3.2. InferringtheStateMachine
Thealgorithmusedbythesecomponentstoactuallyinferthestatemachineisshown
in Algorithm 1. The main procedure (lines 1-5) takes care of initializing the various
components and processes involved. The actual, recursive, crawl procedure starts at
line6.Themainstepsofthecrawlprocedureareexplainedbelow.
ALGORITHM1:CrawlingAJAX
input :URL,tags,browserType
1 ProcedureMAIN()
2 begin
3 global browser←INITEMBEDDEDBROWSER(URL, browserType)
4 global robot←INITROBOT()
5 global sm←INITSTATEMACHINE()
6 CRAWL(null)
7 ProcedureCRAWL(Stateps)
8 begin
9 cs←sm.GETCURRENTSTATE()
10 ∆update←DIFF(ps, cs)
11 f ←ANALYSEFORMS(∆update)
12 SetC←GETCANDIDATECLICKABLES(∆update, tags, f)
13 forc∈Cdo
14 robot.ENTERFORMVALUES(c)
15 robot.FIREEVENT(c)
16 dom←browser.GETDOM()
17 ifSTATECHANGED(cs.GETDOM(), dom) then
18 xe←GETXPATHEXPR(c)
19 ns←sm.ADDSTATE(dom)
20 sm.ADDEDGE(cs, ns, EVENT(c, xe))
21 sm.CHANGETOSTATE(ns)
22 ifSTATEALLOWEDTOBECRAWLED(ns)then
23 CRAWL(cs)
24 sm.CHANGETOSTATE(cs)
25 BACKTRACK(cs)
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 9

0:8 Mesbahetal.
3.3. DetectingClickables
Thereisnofeasiblewayofautomaticallyobtainingalistofallclickableelementsona
DOM-tree,duetothereasonsexplainedinSection2.Therefore,ouralgorithmmakes
use of a set of candidate elements, which are all exposed to an event type (e.g., click,
mouseOver).EachelementontheDOM-treethatmeetsthelabellingrequirementsis
selectedasacandidateelement.
In automated mode, the candidate clickables are labeled as such based on their
HTML tag element name. In our implementation, all elements with a tag <A>,
<BUTTON>, or <INPUT type=‘submit’> are considered as candidate clickables, by de-
fault. The selection of candidate clickables can be relaxed or constrained by the user
aswell,bydefiningelementpropertiessuchastheXPATHpositionontheDOM-tree,
attributesandtheirvalues,andtextvalues.Forinstance,theusercouldbemerelyin-
terestedinexaminingDIVelementswithattributeclass=‘article’.Itisalsopossible
toexcludecertainelementsfromthecrawlingprocess.
Based on the given definition of the candidate clickables, our algorithm scans the
DOM-tree and extracts all the DOM elements that meet the requirements of the def-
inition(line12).Foreachextractedcandidateelement,thecrawlertheninstructsthe
robottofillinthedetecteddataentrypoints(line14)andfireanevent(line15)onthe
element in the browser. The robot is currently capable of using either self-generated
random values, or custom values provided by the user to fill in the forms (for more
detailsontheformfillingcapabilitiessee[MesbahandvanDeursen2009]).
DEFINITION 2. Let D
1
be the DOM-tree of the state before firing an event e on a
candidateclickableccandD theDOM-treeaftereisfired,thenccisaclickableifand
2
onlyifD differsfromD .
1 2
3.4. StateComparison
After firing an event on a candidate clickable, the algorithm compares the resulting
DOM-tree with the DOM-tree as it was just before the event fired, in order to deter-
minewhethertheeventresultsinastatechange(line17).
Todetectastatechange,theDOM-treesneedtobecompared.Onewayofcomparing
them is by calculating the edit distance between two DOM-trees is calculated, using
theLevenshtein[1996]method.Asimilaritythresholdτ isusedunderwhichtwoDOM
treesareconsideredclones.Thisthreshold(0.0−1.0)canbegivenasinput.Athreshold
of0meanstwoDOMstatesareseenasclonesiftheyareexactlythesameintermsof
structureandcontent.Anychangeis,therefore,seenasastatechange.
Anotherwayofcomparingthestateswehaveproposedrecently[Roestetal.2010],
is the use of a series of comparators, each capable of focusing on and comparing spe-
cific aspects of two DOM-trees. In this technique, each comparator filters out specific
parts of the DOM-tree and passes the output to the next comparator. For instance, a
Datetimecomparatorlooksforanydate/timepatternsandfiltersthose.Thisway,two
statescontainingdifferenttimestampscanbemarkedsimilarautomatically.
Ifastatechangeisdetected,accordingtoourcomparisonheuristics,wecreateanew
stateandaddittothestate-flowgraphofthestatemachine(line19).
TheADDSTATEcallworksasfollows:Inordertorecognizeanalreadymetstate,we
compare every new state to the list of already visited states on the state-flow graph.
If we recognize an identical or similar state in the state machine (based on the same
similarity notion used for detecting a new state after an event) that state is used for
addinganewedge,otherwiseanewstateiscreatedandaddedtothegraph.
As an example, Figure 4a shows the full state space of a simple application, before
any similarity comparison heuristics. In Figure 4c, the states that are identical (S 4)
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 10

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:9
Index Index Index
S_2 S_3' S_2 S_2
S_3 S_4 S_5 S_3 S_3' S_3
S_4 S_5 S_4 S_5 S_4 S_5
(a)Fullstatemachine. (b) Merging identical (c) Merging similar
states. states.
Fig.4:StateMachineOptimization.
are merged and Figure 4c presents the state space after similar states (S 3 and S 3(cid:48))
havebeenmerged.
Foreverydetectedstate,anewedgeiscreatedonthegraphbetweenthestatebefore
theeventandthecurrentstate(line20).UsingpropertiessuchastheXPATHexpres-
sion, the clickable causing the state transition is also added as part of the new edge
(line18).
Moreover, the current state pointer of the state machine is updated to this newly
addedstateatthatmoment(line21).
3.5. ProcessingDocumentTreeDeltas
After a clickable has been identified, and its corresponding state transition created,
the CRAWL procedure is recursively called (line 23) to find possible states reachable
fromthenewlydetectedstate.
Upon every new (recursive) entry into the CRAWL procedure, the first action taken
(line10)iscomputingthedifferencesbetweenthepreviousdocumenttreeandthecur-
rentone,bymeansofanenhancedDiff algorithm[Chawatheetal.1996;Mesbahand
vanDeursen2007].Theresultingdifferencesareusedtofindnewcandidateclickables,
whicharethenfurtherprocessedbythecrawler.Such“deltaupdates”maybedue,for
example,toaserverrequestcallthatinjectsnewelementsintotheDOM.
It is worth mentioning that in order to avoid a loop, a list of visited elements is
maintained to exclude already checked elements in the recursive algorithm. We use
thetagname,thelistofattributenamesandvalues,andtheXPathexpressionofeach
elementtoconductthecomparison.Additionally,adepth-levelnumbercanbedefined
toconstrainthedepthleveloftherecursivefunction.
3.6. BacktrackingtothePreviousState
Uponcompletionoftherecursivecall,thebrowsershouldbeputbackintothestateit
was in before the call, at least if there are still unexamined clickable elements left on
thatstate.
Unfortunately, navigating (back and forth) through an AJAX site is not as easy as
navigatingaclassicalmulti-pageone.AdynamicallychangedDOMstatedoesnotreg-
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 11

0:10 Mesbahetal.
ALGORITHM2:Backtracking
input :
1 ProcedureBACKTRACK(States)
2 begin
3 cs←s
4 whilecs.HASPREVIOUSSTATE()do
5 ps←cs.GETPREVIOUSSTATE()
6 ifps.HASUNEXAMINEDCANDIDATECLICKABLES() then
7 ifbrowser.history.CANGOBACK() then
8 browser.history.GOBACK()
9 else
10 browser.RELOAD()
11 ListE←sm.GETPATHTO(ps)
12 fore∈Edo
13 re←RESOLVEELEMENT(e)
14 robot.ENTERFORMVALUES(re)
15 robot.FIREEVENT(re)
16 return
17 else
18 cs←ps
isteritselfwiththebrowserhistoryengineautomatically,sotriggeringthe‘Back’func-
tion of the browser usually does not bring us to the previous state. Saving the whole
browser state is also not feasible due to many technical difficulties. This complicates
traversing the application when crawling AJAX. Algorithm 2 shows our backtracking
procedure.
The backtracking procedure is called once the crawler is done with a certain state
(line25inAlgorithm1).Algorithm2firsttriestofindtherelevantpreviousstatethat
stillhasunexaminedcandidateclickables(lines4-18inAlgorithm2).
Ifarelevantpreviousstateisfoundtobacktrackto(line6inAlgorithm2),thenwe
distinguishbetweentwosituations:
Browser History Support It is possible to programmatically register each state
change with the browser history through frameworks such as the jQuery history/re-
mote plugin4, the Really Simple History library,5 or the recently proposed HTML5
history manipulation API (e.g., history.pushState() and history.replaceState().6
If an AJAX application has support for the browser history (line 7), then for changing
the state in the browser, we can simply use the built-in history back functionality to
movebackwards(line8inAlgorithm2).
ClickingThroughFromInitialStateIncasethebrowserhistoryisnotsupported,
whichisthecasewithmany AJAX applicationscurrently,theapproachweproposeto
gettoapreviousstateisbysavinginformationabouttheclickableelements,theevent
type (e.g., click), and the order in which the events fired on the elements results in
reaching to a particular state. Once we possess such information, we can reload the
application (line 10 in Algorithm 2) and fire events on the clickable elements from
the initial state to the desired state, using the exact path taken to reach that state
(line 11 in Algorithm 2). However, as an optimization step, it is also possible to use
Dijkstra’s shortest path algorithm [Dijkstra 1959] to find the shortest element/event
4http://stilbuero.de/jquery/history/
5http://code.google.com/p/reallysimplehistory/
6www.w3.org/TR/html5/history.html
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 12

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:11
Index
E_1 E_2
S_1 S_2
E_3 E_6
S_3 S_6 3
E_4 1 E_7 E_9
S_4 S_7 2 S_9
E_5 E_8 E_10
S_5 S_8 S_10
Fig.5:Backtrackingtothepreviousrelevantstate.
path on the graph to a certain state. For every element along the path, we first check
whethertheelementcanbefoundonthecurrentDOM-treeandtrytoresolveitusing
heuristicstofindthebestmatchpossible(line13inAlgorithm2).Then,afterfillingin
the related input fields (line 14 in Algorithm 2), we fire an event on the element (line
15inAlgorithm2).
WeadoptXPathalongwithitsattributestoprovideabetter,morereliable,andper-
sistentelementidentificationmechanism.Foreachclickable,wereverseengineerthe
XPathexpressionofthatelement,whichgivesusitsexactlocationontheDOM(line18
inAlgorithm1).Wesavethisexpressioninthestatemachine(line20inAlgorithm1)
anduseittofindtheelementafterareload,persistently(line13inAlgorithm2).
Figure 5 shows an example of how our backtracking mechanism operates. Lets as-
sumethatwehavetakenthe(E 1, E 3, E 4, E 5)pathandhavelandedonstateS 5.
FromS 5,ouralgorithmknowsthattherearenocandidateclickablesleftinstatesS 4
andS 3bykeepingthetrackofexaminedelements.S 1,however,doescontainanun-
examined clickable element. The dotted blue line annotated with 1 shows our desired
path for backtracking to this relevant previous state. To go from S 5 to S 1, the algo-
rithm reloads the browser so that it lands on the index state, and from there it fires
aneventontheclickableE 1.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 13

0:12 Mesbahetal.
Robot
UI
Robot event
Embedded
UI Browser
event
update event Embedded
Browser
Crawljax
uDpOdaMte eventevent
Ajax
Controller generate event DOM upd e a v t e e nt Engine
Ajax
Engine
update
Crawling
nCordaewling
node
Analyze
Dom
State State-flow
update
DOM update Machine graph
update
AnalDyOzeMr State
update
Analyzer Machine
Fig.6:Processingviewoftheconcurrentcrawlingarchitecture.
4. CONCURRENTAJAXCRAWLING
The algorithm and its implementation for crawling AJAX as just described is sequen-
tial,depth-first,andsingle-threaded.Sincewecrawlthewebapplicationdynamically,
thecrawlingruntimeisdeterminedby:
(1) thespeedatwhichthewebserverrespondstoHTTPrequests;
(2) networklatency;
(3) the crawler’s internal processes (e.g., analyzing the DOM, firing events, updating
thestatemachine);
(4) thespeedofthebrowserinhandlingtheeventsandrequest/responsepairs,modi-
fyingtheDOM,andrenderingtheuserinterface,
We have no influence on the first two factors and we already have many optimiza-
tion heuristics for the third step (See Section 3). Therefore, in this section we focus
on the last factor, the browser. Since the algorithm has to wait some considerable
amount of time for the browser to finish its tasks after each event, our hypothesis
is that we can decrease the total runtime by adopting concurrent crawling through
multiplebrowsers.
4.1. Multi-threaded,Multi-BrowserCrawling
Figure 6 shows the processing view of our concurrent crawling. The idea is to main-
tain a single state machine and split the original controller into a new controller and
multiplecrawlingnodes.Thecontrolleristhesinglemainthreadmonitoringthetotal
crawlprocedure.Inthisnewsetting,eachcrawlingnodeisresponsibleforderivingits
correspondingrobotandbrowserinstancestocrawlaspecificpath.
ComparedwithFigure3,thenewarchitectureiscapableofhavingmultiplecrawler
instances,runningfromasinglecontroller.Allthecrawlerssharethesamestatema-
chine. The state machine makes sure every crawler can read and update the state
machineinasynchronizedway.Thisway,theoperationofdiscoveringnewstatescan
beexecutedinparallel.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 14

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:13
(cid:0)(cid:1) (cid:2)(cid:3)(cid:4)(cid:5) (cid:6)(cid:7) (cid:8)
(cid:13)(cid:14) (cid:5) (cid:3)(cid:15)
(cid:0)(cid:1) (cid:2)(cid:3)(cid:4)(cid:5) (cid:6)(cid:7) (cid:9)
(cid:16) (cid:17) (cid:8) (cid:16) (cid:17) (cid:8) (cid:8)
(cid:16) (cid:17) (cid:9) (cid:16) (cid:17) (cid:8) (cid:9)
(cid:0)(cid:1) (cid:2)(cid:3)(cid:4)(cid:5) (cid:6)(cid:7) (cid:10) (cid:0)(cid:1) (cid:2)(cid:3)(cid:4)(cid:5) (cid:6)(cid:7) (cid:12)
(cid:16) (cid:17) (cid:10) (cid:16) (cid:17) (cid:18) (cid:16) (cid:17) (cid:8) (cid:10)
(cid:0)(cid:1) (cid:2)(cid:3)(cid:4)(cid:5) (cid:6)(cid:7) (cid:11)
(cid:16) (cid:17) (cid:11) (cid:16) (cid:17) (cid:20) (cid:16) (cid:17) (cid:19) (cid:16) (cid:17) (cid:8) (cid:11)
(cid:16) (cid:17) (cid:12) (cid:16) (cid:17) (cid:8) (cid:22) (cid:16) (cid:17) (cid:21) (cid:16) (cid:17) (cid:8) (cid:12)
Fig.7:Partitioningthestatespaceformulti-threadedcrawling.
4.2. PartitionFunction
Todividetheworkoverthecrawlersinamulti-threadedmanner,apartitionfunction
must be designed. The performance of a concurrent approach is determined by the
qualityofitspartitionfunction[Garaveletal.2001].Apartitionfunctioncanbeeither
static or dynamic. With a static partition function the division of work is known in
advance,beforeexecutingthecode.Whenadynamicpartitionfunctionisused,thede-
cisionofwhichthreadwillexecuteagivennodeismadeatruntime.Ouralgorithmin-
fersthestate-flowgraphofanAJAXapplicationdynamicallyandincrementally.Thus,
duetothisdynamicnatureweadoptforadynamicpartitionfunction.
Thetaskofourdynamicpartitionfunctionistodistributetheworkequallyoverall
theparticipatingcrawlingnodes.Whilecrawlingan AJAX application,wedefinework
as: Bringing the browser back into a given state and exploring the first unexplored
candidate state from that state. Our proposed partition function operates as follows:
Afterthediscoveryofanewstate,iftherearestillunexploredcandidateclickablesleft
in the previous state, that state is assigned to another thread for further exploration.
Theprocessorchosenwillbetheonewiththeleastamountofworkleft.
Figure 7 visualizes our partition function for concurrent crawling of a simple web
application. In the Index state, two candidate clickables are detected that can lead
to: S 1 and S 11. The initial thread continues with the exploration of the states S 1,
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 15

0:14 Mesbahetal.
S 2,S 3,S 4andfinishesinS 5inadepth-firstmanner.Simultaneously,anewthread
is branched off to explore state S 11. This new thread (thread #2) first reloads the
browsertoIndexandafterthatgoesintoS 11.InstateS 2andS 6thissamebranching
mechanismhappens,whichresultsinatotalof5threads.
Now that the partition function has been introduced, the original sequential crawl-
ingalgorithm(Algorithm1)canbechangedintoaconcurrentversion.
4.3. TheConcurrentCrawlingAlgorithm
The concurrent crawling approach is shown in Algorithm 3. Here we briefly explain
the main differences with respect to the original sequential crawling algorithm, as
presentedinAlgorithm1anddiscussedinSection3.
Global State-flow Graph The first change is the separation of the state-flow graph
fromthestatemachine.Thegraphisdefinedinaglobalscope(line3),sothatitcanbe
centralized and used by all concurrent nodes. Upon the start of the crawling process,
aninitialcrawlingnodeiscreated(line5)andits RUN procedureiscalled(line6).
BrowserPoolTherobotandstatemachinearecreatedforeachcrawlingnode.Thus,
theyareplacedinthelocalscopeofthe RUN procedure(lines10-11).
Generally,eachnodeneedstoacquireabrowserinstanceandaftertheprocessisfin-
ished,thebrowseriskilled.Creatingnewbrowserinstancesisaprocess-intensiveand
time-consumingoperation.Tooptimize,anewstructureisintroduced:theBrowserPool
(line 4), which creates and maintains browsers in a pool of browsers to be re-used by
the crawling nodes. This reduces start-up and shut-down costs. The BrowserPool can
be queried for a browser instance (line 9), and when a node is finished working, the
browserusedisreleasedbacktothepool.
In addition, the algorithm now takes the desired number of browsers as input. In-
creasing the number of browsers used can decrease the crawling runtime, but it also
comeswithsomelimitationsandtrade-offsthatwewilldiscussinSection6.5.
Forward-trackingInthesequentialalgorithm,afterfinishingacrawlpath,weneed
tobringthecrawlertotheprevious(relevant)state.Intheconcurrentalgorithm,how-
ever,wecreateanewcrawlingnodeforeachpathtobeexamined(seeFigure7).Thus,
insteadofbringingthecrawlerbacktothedesiredstate(backtracking)wemusttake
thenewnodeforwardtothedesiredstate,hence,forward-tracking.
This is done after the browser is pointed to the URL (line 12). The first time the
RUNprocedureisexecuted,thereisnoforward-trackingtakingplace,sincetheevent-
path (i.e., the list of clickable items resulting to the desired state) is empty, so the
initialcrawlerstartsfromtheIndexstate.However,iftheevent-pathisnotempty,the
clickables are used to take the browser forward to the desired state (lines 13-16). At
thatpoint,the CRAWL procedureiscalled(line17).
Crawling ProcedureThefirstpartofthe CRAWL procedureisunchanged(lines21-
24). To enable concurrent nodes accessing the candidate clickables in a thread-safe
manner, the body of the for loop is synchronized around the candidate element to be
examined(line26).Toavoidexaminingacandidateelementmultipletimesbymultiple
nodes,eachnodefirstcheckstheexaminedstateofthecandidateelement(line28).If
the element has not been examined previously, the robot executes an event on the
elementinthebrowserandsetsitsstateasexamined(line31).Ifthestateischanged,
before going into the recursive CRAWL call, the PARTITION procedure is called (line
38).
Partition Procedure The partition procedure, called on a particular state cs (line
44),createsanewcrawlingnodeforeveryunexaminedcandidateclickableincs(line
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 16

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:15
ALGORITHM3:ConcurrentAJAXCrawling
input :URL,tags,browserType,nrOfBrowsers
1 ProcedureMAIN()
2 begin
3 global sfg←INITSTATEFLOWGRAPH()
4 global browserPool←INITBROWSERPOOL(nrOfBrowsers, browserType)
5 crawlingNode←CRAWLINGNODE()
6 crawlingNode.RUN(null,null)
7 ProcedureRUN(States,EventPathep)
8 begin
9 browser←browserPool.GETEMBEDDEDBROWSER()
10 robot←INITROBOT()
11 sm←INITSTATEMACHINE(sfg)
12 browser.GOTO(URL)
13 fore∈epdo
14 re←RESOLVEELEMENT(e)
15 robot.ENTERFORMVALUES(re)
16 robot.FIREEVENT(re)
17 CRAWL(s, browser, robot, sm)
18
19 ProcedureCRAWL(Stateps,EmbeddedBrowserbrowser,Robotrobot,StateMachinesm)
20 begin
21 cs←sm.GETCURRENTSTATE()
22 ∆update←DIFF(ps, cs)
23 f ←ANALYSEFORMS(∆update)
24 SetC←GETCANDIDATECLICKABLES(∆update, tags, f)
25 forc∈Cdo
26 SYNCH(c)
27 begin
28 ifcs.NOTEXAMINED(c)then
29 robot.ENTERFORMVALUES(c)
30 robot.FIREEVENT(c)
31 cs.EXAMINED(c)
32 dom←browser.GETDOM()
33 ifSTATECHANGED(cs.GETDOM(), dom) then
34 xe←GETXPATHEXPR(c)
35 ns←sm.ADDSTATE(dom)
36 sm.ADDEDGE(cs, ns, EVENT(c, xe))
37 sm.CHANGETOSTATE(ns)
38 PARTITION(cs)
39 ifSTATEALLOWEDTOBECRAWLED(ns)then
40 CRAWL(cs)
41 sm.CHANGETOSTATE(cs)
42
43 ProcedurePARTITION(Statecs)
44 begin
45 whileSIZEOF(cs.NOTEXAMINEDCLICKABLES())>0do
46 crawlingNode←CRAWLINGNODE(cs, GETEXACTPATH())
47 DISTRIBUTEPARTITION(crawlingNode)
48
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 17

0:16 Mesbahetal.
46). The new crawlers are initialized with two parameters, namely, (1) the current
state cs (2) the execution path from the initial Index state to this state. Every new
node is distributed to the work queue participating in the concurrent crawling (line
47). When a crawling node is chosen from the work queue, its corresponding RUN
procedureiscalledinordertospawnanewcrawlingthread.
5. TOOLIMPLEMENTATION
Wehaveimplementedthecrawlingconceptsinatoolcalled CRAWLJAX.Thedevelop-
ment of CRAWLJAX originally started in 2007. There have been many extension and
improvement iterations since the first release in 2008. CRAWLJAX has been used by
varioususersandappliedtoarangeofindustrialcasestudies.Itisreleasedunderthe
Apache open source license and is available for download. In 2010 alone, the tool was
downloaded more than 1000 times. More information about the tool can be found on
http://crawljax.com.
CRAWLJAX is implemented in Java. We have engineered a variety of software li-
braries and web tools to build and run CRAWLJAX. Here we briefly mention the main
modulesandlibraries.
The embedded browser interface supports three browsers currently (IE, Chrome,
Firefox)andhasbeenimplementedontopoftheSelenium2.0(WebDriver)APIs.7 The
state-flowgraphisbasedontheJGrapht8 library.
CRAWLJAX has a Plugin-based architecture. There are various extension points for
different phases of the crawling process. The main interface is Plugin, which is ex-
tended by the various types of plugin available. Each plugin interface serves as an
extension point that is called in a different phase of the crawling execution, e.g.,
preCrawlingPlugin runs before the crawling starts, OnNewStatePlugin runs when a
new state is found during crawling, PostCrawlingPlugin runs after the crawling is
finished.Moredetailsofthepluginextensionpointscanbefoundontheprojecthome-
page.9 Thereisagrowinglistofpluginsavailablefor CRAWLJAX,10 examplesofwhich
include a static mirror generator, a test suite generator, a crawl overview generator
for visualization of the crawled states, a proxy to intercept communication between
client/serverwhilecrawling,andacross-browsercompatibilitytester.
ThroughanAPI(CrawljaxConfiguration),theuserisabletoconfiguremanycrawl-
ing options such as the elements that should be examined (e.g., clicked on) during
crawling, elements that should be ignored (e.g., logout), crawling depth and time, the
maximum number of states to examine, the state comparison method, the plugins to
beused,andthenumberofdesiredbrowsersthatshouldbeusedduringcrawling.
6. EVALUATION
Since2008,weandothershaveusedCRAWLJAXforaseriesofcrawlingtasksondiffer-
enttypesofsystems.Inthissection,weprovideanempiricalassessmentofsomeofthe
key properties of our crawling technique. In particular, we address the accuracy (are
the results correct?), scalability (can we deal with realistic sites?), and performance,
focusinginparticularontheperformancegainsresultingfromconcurrentcrawling.
We first present our findings concerning accuracy and scalability, for which we
study six systems, described next (Section 6.1). For analyzing the performance gains
fromconcurrentcrawling,weapplyCRAWLJAXtoGoogle’sADSENSEapplication(Sec-
tion6.5).
7http://code.google.com/p/selenium/wiki/GettingStarted
8http://jgrapht.sourceforge.net
9http://crawljax.com/documentation/writing-plugins/
10http://crawljax.com/plugins/
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 18

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:17
TableI:Experimentalbenchmarksandexamplesoftheirclickableelements.
Case AJAXsite SampleClickableElements
C1 spci.st.ewi.tudelft. <span id="testspan2" class="testing">testing span 2</span>
nl/demo/aowe/
<a onclick="nav(’l2’); return false;" href="#">2nd
link</a>
<a title="Topics" href="#Topics" class="remoteleft left">
Topics of Interest</a>
C2 PETSTORE <a class="accordionLink" href="#" id="feline01"
onmouseout="this.className=’accordionLink’;"
onmouseover="this.className=’accordionLinkHover’;">
Hairy Cat</a>
C3 www.4launch.nl <div onclick="setPrefCookies(’Gaming’, ’DESTROY’,
’DESTROY’);
loadHoofdCatsTree(’Gaming’, 1, ’’)"><a id="uberCatLink1"
class="ubercat" href="javascript:void(0)">Gaming</a></div>
<td onclick="openurl(’..producteninfo.php?productid=
037631’,..)">Harddisk Skin</td>
C4 www. <input type="radio" value="7" name="radioTextname"
blindtextgenerator. class="js-textname iradio"id="idRadioTextname-EN-li-europan"/>
com
<a id="idSelectAllText" title="Select all" href="#">
C5 site.snc.tudelft.nl <div class="itemtitlelevel1 itemtitle"
id="menuitem189e">organisatie</div>
<a href="#" onclick="ajaxNews(’524’)">...</a>
C6 www.gucci.com <a onclick="Shop.selectSort(this); return false"
class="booties" href="#">booties</a>
<div id="thumbnail7" class="thumbnail highlight"><img
src="...001thumb.jpg" /><div
<div class="darkening">...</div>
6.1. SubjectSystems
In order to assess the accuracy (Section 6.3) and scalability (Section 6.4), we study
the six systems C1–C6 listed in Table I. For each case, we show the site under study,
as well as a selection of typical clickable elements. We selected these sites because
they adopt AJAX to change the state of the application, using JAVASCRIPT, assigning
events to HTML elements, asynchronously retrieving delta updates from the server,
andperformingpartialupdatesontheDOM-tree.
The first site C1 in our case study is an AJAX test site developed internally by our
groupusingthejQuery AJAX library.Althoughthesiteissmall,itisacasewherewe
are in full control of the AJAX features used, allowing us to introduce different types
ofdynamicallysetclickablesasshowninFigure1andTableI.
Our second case, C2, is Sun’s Ajaxified PETSTORE 2.011 which is built on Java
ServerFaces and the Dojo AJAX toolkit. This open-source web application is designed
to illustrate how the Java EE Platform can be used to develop an AJAX-enabled Web
2.0applicationandadoptsmanyadvancedrich AJAX components.
The other four cases are all real-world external public AJAX applications. Thus, we
havenoaccesstotheirsource-code.C4isanAJAX-basedapplicationthatcanfunction
as a tool for comparing the visual impression of different typefaces. C3 (online shop),
C5 (sport center), and C6 (Gucci) are all single-page commercial applications with
numerousclickablesanddynamicstates.
11http://java.sun.com/developer/releases/petstore/
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 19

0:18 Mesbahetal.
TableII:Resultsofrunning CRAWLJAX on6 AJAX applications.
esaC
)etyb(ezisgnirtsMOD
selbakcilCetadidnaC
selbakcilCdetceteD
setatSdetceteD
)s(emiTlwarC
htpeD
sgaT
C1 4590 540 16 16 14 3 A,DIV,SPAN,IMG
C2 24636 1813 33 34 26 2 A,IMG
C3 262505 150 148 148 498 1 A
19247 1101 1071 5012 2 A,TD
C4 40282 3808 55 56 77 2 A,DIV,INPUT,IMG
C5 165411 267 267 145 806 1 A
32365 1554 1234 6436 2 A,DIV
C6 134404 6972 83 79 701 1 A,DIV
6.2. ApplyingCRAWLJAX
Theresultsofapplying CRAWLJAX to C1–C6 aredisplayedinTableII.Thetablelists
keycharacteristicsofthesitesunderstudy,suchastheaverageDOMsizeandthetotal
numberofcandidateclickables.Furthermore,itliststhekeyconfigurationparameters
set, most notably the tags used to identify candidate clickables, and the maximum
crawlingdepth.
The performance measurements were obtained on a a laptop with Intel Pentium M
765processor1.73GHz,with1GBRAMandWindowsXP.
6.3. Accuracy
6.3.1. Experimental Setup. Assessing the correctness of the crawling process is chal-
lenging for two reasons. First, there is no strict notion of “correctness” with respect
to state equivalence. The state comparison operator part of our algorithm (see Sec-
tion3.4)canbeimplementedindifferentways:themorestatesitconsidersequal,the
smallerandthemoreabstracttheresultingstate-flowgraphis.Thedesirablelevelof
abstraction depends on the intended use of the crawler (regression testing, program
comprehension, security testing, to name a few) and the characteristics of the system
thatisbeingcrawled.
Second, no other crawlers for AJAX are available, making it impossible to compare
our results to a “gold standard”. Consequently, an assessment in terms of precision
(percentage of correct states) and recall (percentage of states recovered) is impossible
togive.
To address these concerns, we proceed as follows. For the cases where we have full
control, C1 and C2,weinjectspecificclickableelements:
—ForC1,16elementswereinjected,outofwhich10wereonthetop-levelindexpage.
Furthermore, to evaluate the state comparison procedure, we intentionally intro-
ducedanumberofidentical(clone)states.
—For C2, we focused on two product categories, CATS and DOGS, from the five
available categories. We annotated 36 elements (product items) by modifying the
JAVASCRIPTmethodwhichturnstheitemsretrievedfromtheserverintoclickables
ontheinterface.
Subsequently,wemanuallycreateareferencemodel,towhichwecomparethederived
state-flowgraph.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 20

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:19
ToassessthefourexternalsitesC3–C6,weinspectaselectionofthestates.Foreach
site,werandomlyselect10clickablesinadvance,bynotingtheirtagnames,attributes,
and XPath expressions. After crawling of each site, we check the presence of these 10
elementsamongthelistofdetectedclickables.
In order to do the manual inspection of the results, we run CRAWLJAX with the
Mirror plugin enabled. This post-crawling plugin creates a static mirror based on the
derived state-flow graph, by writing all DOM states to file, and replacing edges with
appropriatehyperlinks.
6.3.2. Findings. Ourresultsareasfollows:
—ForC1,all16expectedclickableswerecorrectlyidentified,leadingtoaprecisionand
recallof100%forthiscase.Furthermore,theclonestatesintroducedwerecorrectly
identifiedassuch.
—For C2, 33 elements were detected correctly from the annotated 36. The three el-
ement that were not detected turn out to be invisible elements requiring multiple
clicks on a scroll bar to appear. Since our default implementation avoids clicking
the same element multiple times (see Section 3.5), these invisible elements cannot
becomevisible.Hencetheycannotbeclickedinordertoproducetherequiredstate
change when the default settings are used. Note that multiple events on the same
elementisanoptionsupportedinthelatestversionof CRAWLJAX.
—ForC3–C6,38outofthe4∗10=40,correspondingto95%ofthestateswerecorrectly
identified.Thereasonsfornotcreatingthemissingtwostatesissimilartothe C2-
case: the automatically derived navigational flow did not permit reaching the two
elementsthathadtobeclickedinordertogeneratetherequiredstates.
Basedonthesefindings,weconcludethat(1)statesdetectedby CRAWLJAX arecor-
rect;(2)duplicatestatesarecorrectlyidentifiedassuch;butthat(3)notallstatesare
necessarilyreached.
6.4. Scalability
6.4.1. ExperimentalSetup. Inordertoobtainanunderstandingofthescalabilityofour
approach, we measure the time needed to crawl, as well as a number of site char-
acteristics that will affect the time needed. We expect the crawling performance to
be directly proportional to the input size, which is composed of (1) the average DOM
string size, (2) number of candidate elements, and (3) number of detected clickables
andstates,whicharethecharacteristicsthatwemeasureforthesixcases.
Totestthecapabilityofourmethodincrawlingrealsitesandcopingwithunknown
environments, we run CRAWLJAX on four external cases C3–C6. We run CRAWLJAX
withdepthlevel2onC3andC5eachhavingahugestatespacetoexaminethescala-
bilityofourapproachinanalyzingtensofthousandsofcandidateclickablesandfind-
ingclickables.
6.4.2. Findings. Concerning the time needed to crawl the internal sites, we see that
it takes CRAWLJAX 14 and 26 seconds to crawl C1 and C2 respectively. The average
DOMsizein C2 is5timesandthenumberofcandidateelementsis3timeshigher.
In addition to this increase in DOM size and in the number of candidate elements,
the C2 site does not support the browser’s built-in Back method. Thus, as discussed
in Section 3.6, for every state change on the browser CRAWLJAX has to reload the
application and click through to the previous state to go further. This reloading and
clickingthroughnaturallyhasanegativeeffectontheperformance.
NotethattheperformanceisalsodependentontheCPUandmemoryofthemachine
CRAWLJAX is running on, as well as the speed of the server and network properties
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 21

0:20 Mesbahetal.
Fig.8:Google ADSENSE.
of the case site. C6, for instance, is slow in reloading and retrieving updates from its
server,whichincreasestheperformancemeasurementnumbersinourexperiment.
CRAWLJAX was able to run smoothly on the external sites. Except a few minor ad-
justments(seeSection7)wedidnotwitnessanydifficulties.C3withdepthlevel2was
crawled successfully in 83 minutes resulting in 19247 examined candidate elements,
1101detectedclickables,and1071detectedstates.ForC5,CRAWLJAXwasabletofin-
ish the crawl process in 107 minutes on 32365 candidate elements, resulting in 1554
detected clickables and 1234 states. As expected, in both cases, increasing the depth
levelfrom1to2expandsthestatespacegreatly.
Section6.5presentsourcasestudyconductedonGoogleADSENSE,whichshowsthe
scalabilityoftheapproachonareal-worldindustrialwebapplication.
6.5. ConcurrentCrawling
In our final experiment, the main goal is to assess the influence of the concurrent
crawlingalgorithmonthecrawlingruntime.
6.5.1. ExperimentalObject. Our experimental object for this study is Google ADSENSE
,12 an AJAX application developed by Google, which empowers online publishers to
earnrevenuebydisplayingrelevantadsontheirwebcontent.TheADSENSEinterface
isbuiltusingGWT(GoogleWebToolkit)componentsandiswritteninJava.
Figure 8 shows the index page of ADSENSE. On the top, there are four main tabs
(Home, My ads, Allow & block ads, Performance reports). On the top-left side, there
is a box holding the anchors for the current selected tab. Underneath the left-menu
box,thereisaboxholdinglinkstohelprelatedpages.Ontherightoftheleft-menuwe
canseethemaincontents,whichareloadedby AJAX calls.
6.5.2. ExperimentalDesign. Ourresearchquestionscanbepresentedasfollows:
RQ1. Does our concurrent crawling approach positively influence the perfor-
mance?
RQ2. Is there a limit on the number of browsers that can be used to reduce the
runtime?
Based on these two research questions we formulate our two null hypotheses as
follows:
H1 . Theavailabilityofmorebrowsersdoesnotimpactthetimeneededtocrawla
0
given AJAX application.
12https://www.google.com/adsense/
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 22

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:21
H2 . Thereisnolimitonthenumberofbrowsersthatcanbeaddedtoreducethe
0
runtime.
Thealternativehypothesesthatweuseintheexperimentarethefollowing:
H1. The availability of more browsers reduces the time needed to crawl a given
AJAX application.
H2. There is a limit on the number of browsers that can be added to reduce the
runtime.
Infrastructure To derive our experimental data we use the Google infrastructure,
whichoffersthepossibilitytorunourexperimentseitheronalocalworkstationoron
adistributedtestingcluster.
On the distributed testing cluster, the number of cores varies between clusters.
Newer clusters are supplied with 6 or 8 core CPU’s, while older clusters include 2
or 4 cores. The job-distributor ensures a minimum of 2 Gb of memory per job at min-
imum. The cluster is shared between all development teams, so our experiment data
weregatheredwhileotherteamswerealsousingthecluster.Topreventstarvationon
the distributed testing cluster, a maximum runtime of one hour is specified, i.e., any
testrunninglongerthananhouriskilledautomatically.
Toachievearepeatableexperiment,weinitiateanewAdsensefront-endwithaclean
databaseserverforeveryexperimentaltest.Thetest-dataisloadedintothedatabase
duringtheinitializationphaseoftheAdsensefront-end.
ToolConfigurationTocrawl ADSENSE,weconfigured CRAWLJAX 2.0 toclickonall
anchor-tagsandfillinforminputswithcustomdata.
Toinformtheuserthattheinterfaceisbeingupdated,ADSENSEdisplaysaloading-
icon. While crawling, to determine whether the interface was finished with loading
thecontentaftereachfiredevent,CRAWLJAXanalyzedtheDOM-treetocheckforthis
icon.
Due to the infrastructure we were restricted to use Linux as our operating system
andwechoseFirefox3.5asourembeddedbrowser.
Variables and Analysis The independent variable in our experiment is the num-
ber of browsers used for crawling. We use the same crawl configuration for all the
experiments. The only property that changes is the number of browsers used during
crawling:1-10.
Thedependentvariablethatwemeasureisthetimeneededtocrawlthegivencrawl
specification,calculatedfromthestartofthecrawlinguntilthe(last)browserfinishes.
Tocompare,wealsomeasuretheactualnumberofexaminedclickables,crawledstates,
edges,andpaths.
We run every experiment multiple times and take the average of the runtime. On
thedistributedclusterallresourcesareshared.Hence,togetreliabledataweexecuted
everyexperiment300times.
Sincewehave10independentsamplesofdatawith2953(seeTableIII)datapoints,
we use the One-Way ANOVA statistical method to test the first hypothesis (H1 ).
0
Levene’s test is used for checking the homogeneity of variances. Welch and Brown-
Forsytheareusedastestsofequalityofmeans[MaxwellandDelaney2004].
If H1 turns out to be true, we proceed with our second hypothesis. To test H2 , we
0
need to compare the categories to find out which are responsible for runtime differ-
ences. Thus, we use the Post Hoc Tukey test if the population variances are equal, or
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 23

0:22 Mesbahetal.
l l
l lllllllll lllllllll ll llllllllll llllllllll llllllll
l lllllllllllll lllllllllllll llllllllll llllllllllllllll lllllllllllllll lllll
lllllll lllll lllllll
l llllll lllllll lll
ll lllll lllllll lllll
l l ll ll
ll l
l l
l
l l l
l ll
ll l
l l
l ll ll l l
l ll l ll
ll ll lll
l l
l l l l
l
l
l
ll
l
l
l
1 2 3 4 5 6 7 8 9 10
06
05
04
03
02
# of Browsers
setatS
Fig. 9: Boxplots of detected states versus the number of browsers. Distributed setting
(300measurementsforeachcategoryofbrowsers).
theGames-Howelltestifthatdoesnotturnouttobethecase.WeuseSPSS13 forthe
statisticalanalysisandR14 forplottingthegraphs.
6.5.3. Results and Evaluation. We present our data and analysis on the data from the
distributed infrastructure. We obtained similar results with different configurations.
Ourexperimentaldatacanbefoundonthefollowinglink.15
Figures 9-11 depict boxplots of the detected states, detected edges, and runtime
(minutes) respectively versus the number of browsers used during crawling, on the
distributedinfrastructure.Thenumberofdetectedstatesandedgesisconstant,which
meansourmulti-browsercrawlingandstateexplorationisstable.
13http://www.spss.com
14http://www.r-project.org
15http://tinyurl.com/3d5km3b
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 24

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:23
lllllll l lll l l l lll l ll ll l lllll lllll l llllll l l l ll lll l llll l l l lllll ll lll lll l l l l l l l l ll ll ll l l l lllll l l lll l llll lllllll l l ll l l l l l l l l l l l lll lll l l l l l l l l l l l l ll l l lll ll l ll l lll l l l l ll ll l lll l l llll ll l ll l ll l ll ll l l l l ll l l l l l l l l l l l l l l l ll l ll l l llll lll l l ll ll l ll l l lll lll l l l l l
l l lll l ll l llll lll lll l llllll l l l l l lll l l ll l lllll l llll l l lll l
l ll l ll
l l l ll l ll l l l ll ll
l l l ll
l
l l l
l
l
l
ll
1 2 3 4 5 6 7 8 9 10
001
08
06
04
# of Browsers
segdE
Fig.10:Boxplotsofdetectededgesversusthenumberofbrowsers.Distributedsetting
(300measurementsforeachcategoryofbrowsers).
Table III: Descriptive statistics of the runtime (in minutes) for the 10 categories of
browsers.*95%ConfidenceIntervalforMean.
N Mean Std.Dev. Std.Err. LowerBound* UpperBound* Min Max
1 2953 7.4871 3.70372 .06816 7.3535 7.6207 2.33 22.15
2 299 5.4721 1.14160 .06602 5.3422 5.6020 2.33 10.55
3 295 5.5521 1.26716 .07378 5.4069 5.6973 3.38 11.83
4 297 5.6404 1.11101 .06447 5.5135 5.7673 3.78 11.12
5 291 5.6744 1.15004 .06742 5.5417 5.8070 3.69 10.75
6 290 5.6920 .99718 .05856 5.5767 5.8072 4.20 11.01
7 294 5.9806 1.05696 .06164 5.8593 6.1020 4.13 10.72
8 297 6.2338 1.03936 .06031 6.1151 6.3525 4.74 10.32
9 292 7.4651 1.04823 .06134 7.3444 7.5858 5.35 10.56
10 299 9.9243 1.28598 .07437 9.7779 10.0707 7.05 13.37
Total 299 17.0613 2.31540 .13390 16.7978 17.3249 10.17 22.15
Figure 11 shows that there is a decrease in the runtime when the number of
browsers is increased. Table III presents the descriptive statistics of the runtime for
the10categoriesofbrowsers.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 25

0:24 Mesbahetal.
l
l l ll ll l l lll ll l l l l l l l l l l l l l l l l l l l l l l l l l l l l l l lll l
l l ll ll lllll l
l
l l
l
1 2 3 4 5 6 7 8 9 10
02
51
01
5
# of Browsers
)m(
emitnuR
Fig. 11: Boxplots of runtime versus the number of browsers. Distributed setting (300
measurementsforeachcategoryofbrowsers).
Table IV shows the main ANOVA result. The significance value comparing the
groups is < .05. The significance value for homogeneity of variances, as shown in
Table V, is < .05, which means the variances are significantly different. The Welch
andBrown-Forsytheareboth0,sowecanrejectthefirstnullhypothesis.Thus,wecan
concludethatourconcurrentcrawlingapproachpositivelyinfluencestheperformance.
To test for the second hypothesis, we need to compare the groups to find out if the
differences between them is significant. Table VI shows our post hoc test results. a ∗
means that the difference in runtime is significant. It is evident that there is a limit
on the number of browsers that can significantly decrease the runtime. The optimal
number for our ADSENSE study is 5 browsers. By increasing the number of browsers
from 1 to 5, we can achieve a decrease of up to 65% in runtime. Increasing the num-
ber of browsers beyond 5 has no significant influence on the runtime in our current
impementation.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 26

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:25
TableIV:One-wayANOVA.
SumofSquares df MeanSquare F Sig.
BetweenGroups 35540.225 9 3948.914 2345.919 000
WithinGroups 4953.987 2943 1.683
Total 40494.212 2952
TableV:TestsforHomogeneityofVariancesandEqualityofMeans.
Method Statistic df1 df2 Sig.
Levene 55.884 9 2943 0.000
Welch 1060.017 9 1198.048 0.000
Brown-Forsythe 2355.528 9 1914.845 0.000
Table VI: Post Hoc Games-Howell multiple comparisons. * indicates the mean differ-
enceissignificantatthe0.05level.
1 2 3 4 5 6 7 8 9 10
1 - * * * * * * * * *
2 * - * * * * * * * *
3 * * - * * * * * * *
4 * * * - * * * * *
5 * * * - * * * * *
6 * * * * * -
7 * * * * * -
8 * * * * * -
9 * * * * * -
10 * * * * * -
6.6. ThreatstoValidity
As far as the repeatability of the studies is concerned, CRAWLJAX is open source and
publiclyavailablefordownload.TheexperimentalapplicationsinSection6.1arecom-
posed of open source and public domain websites. In the concurrent crawling experi-
ment (Section 6.5), the study was done at Google using Google’s ADSENSE, which is
also publicly accessible. More case studies are required to generalize the findings on
correctnessandscalability.Oneconcernwithusingpublicdomainwebapplicationsas
benchmarks is that they can change and evolve over time, making the results of the
studyirreproducibleinthefuture.
7. DISCUSSION
7.1. DetectingDOMChanges
An interesting observation in C2 in the beginning of the experiment was that every
examined candidate element was detected as a clickable. Further investigation re-
vealed that this phenomenon was caused by a piece of JAVASCRIPT code (banner),
whichconstantlychangedtheDOM-treewithtextualnotifications.Hence,everytime
aDOMcomparisonwasdone,achangewasdetected.Wehadtouseahighersimilarity
threshold so that the textual changes caused by the banner were not seen as a rele-
vant state change for detecting clickables. In CRAWLJAX, it is also possible to ignore
certainpartsoftheDOM-treethrough,forinstance,regularexpressionsthatcapture
therecurringpatterns.Howthenotionofadynamicstatechangeisdefinedcanpoten-
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 27

0:26 Mesbahetal.
tiallyinfluencethecrawlingbehaviour.Theautomaticcrawlerignoressubtlechanges
intheDOMthatwebelievearenotofsignificantimportance(suchascasesensitivity
and timestamps). We also provide the user with different mechanisms to define their
own notion of state similarity. Push-based techniques such as Comet [Russell 2006]
in whichdata is constantly pushedfrom the servercould also cause state comparison
challenges.Suchpush-basedupdatesareusuallyconfinedtoaspecificpartoftheDOM
treeandhencecanbecontrolledusingcustomDOMchangefilters.
7.2. Backandforwardtracking
Because of side effects of back-end state changes, there is no guarantee that we
reach the exact same state when we traverse a click path a second time. This non-
determinismcharacteristicisinherentindynamicwebapplications.Ourcrawleruses
thenotionofstatesimilarity,thusaslongastherevisitedstateissimilartothestate
visitedbefore,thecrawlingprocesscontinueswithoutside-effects.Inourexperiments,
wedidnotencounteranyproblemswiththisnon-deterministicbehaviour.
Whenthecrawlingapproachisusedfortestingwebapplications,onewaytoensure
that a state revisited is the same as the state previously visited (e.g., for regression
testing[Roestetal.2010]),isbybringingtheserver-sidestatetothepreviousstateas
well,whichcouldbechallenging.Moreresearchisneededtoadoptwaysofsynchroniz-
ingtheclientandserversidestateduringtesting.
CookiescanalsocausesomeproblemsincrawlingAJAXapplications.C3usesCook-
ies to store the state of the application on the client. With Cookies enabled, when
CRAWLJAXreloadstheapplicationtonavigatetoapreviousstate,theapplicationdoes
notstartintheexpectedinitialstate.Inthiscase,wehadtodisableCookiestoperform
acorrectcrawlingprocess.ThenewfeaturesofHTML5suchaswebstorage[Hickson
2011]couldpossiblycausethesameproblemsbymakingpartsoftheclient-sidestate
persistent between backtracking sessions. It would be interesting future work to ex-
plorewaystogetaroundtheseissues.
7.3. StateSpace
Thesetoffoundstatesandtheinferredstatemachineisnotcompletei.e., CRAWLJAX
creates an instance of the state machine of the AJAX application but not necessarily
the instance. Any crawler can only crawl and index a snapshot instance of a dynamic
webapplicationinagivenpointoftime.Theorderinwhichclickablesarechosencould
generatedifferentstates.Evenexecutingthesameclickabletwicefromanstatecould
theoreticallyproducetwodifferentDOMstatesdependingon,forinstance,server-side
factors.
Thenumberofpossiblestatesinthestatespaceofalmostanyrealisticwebapplica-
tionishugeandcancausethewell-knowstateexplosionproblem[Valmari1998].Just
as a traditional web crawler, CRAWLJAX provides the user with a set of configurable
optionstoconstrainthestatespacesuchasthemaximumsearchdepthlevel,thesim-
ilarity threshold, maximum number of states per domain, maximum crawling time,
andtheoptionofignoringexternallinks(i.e.,differentdomains)andlinksthatmatch
somepredefinedsetofregularexpressions,e.g.,mail:*,*.ps,*.pdf.
ThecurrentimplementationofCRAWLJAXkeepstheDOMstatesinthememory.As
an optimization step, next to the multi-browser crawling, we intend to abstract and
serializetheDOMstateintothefilesystemandonlykeepareferenceinthememory.
This saves much space in the memory and enables us to handle much more states.
With a cache mechanism, the essential states for analysis can be kept in the memory
whiletheotheronescanberetrievedfromthefilesystemwhenneededinalaterstage.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 28

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:27
7.4. DOMSettling
DeterminingwhenaDOMisfullyloadedintothebrowserafterarequestoranevent
is a very difficult task. Partially loaded DOM states can adversely influence the state
explorationaccuracyduringcrawling.Theasynchronousnatureof AJAX callsandthe
dynamicDOMupdatesmaketheproblemevenmorechallengingtohandle.Sincethe
major browsers currently do not provide APIs to determine when a DOM-tree is fully
loaded,wewaitaspecificamountoftimeaftereacheventorpagereload.Thiswaiting
timecanbeadjustedbytheuserthroughthe CRAWLJAX configurationAPI.Bychoos-
ing a high enough waiting time, we can be certain that the DOM is fully settled in
thebrowser.Asasideeffect,atoohighwaitingperiod,canmakethecrawlingprocess
slow.
An alternative way that is more reliable is when the web application provides a
completion flag in the form of a DOM element either visible or invisible to the end
user. Before continuing with its crawling operations, CRAWLJAX can be configured to
wait for that specific DOM flag to appear after each state transition. This flag-based
waitingapproachisinfactwhatweusedduringourexperimentson ADSENSE.
7.5. ApplicationsofCRAWLJAX
As mentioned in the introduction, we believe that the crawling and generating capa-
bilitiesofourapproachhavemanyapplicationsformodernwebapplications.
We believe that the crawling techniques that are part of our solution can serve as
a starting point and be adopted by general search engines to expose the hidden-web
contentinducedby JAVASCRIPT ingeneraland AJAX inparticular.
In their proposal for making AJAX applications crawlable,16 Google proposes using
URLs containing a special hash fragment, i.e., #!, for identifying dynamic content.
Googlethenusesthishashfragmenttosendarequesttotheserver.Theserverhasto
treatthisrequestinaspecialwayandsendaHTMLsnapshotofthedynamiccontent,
whichisthenprocessedbyGoogle’scrawler.Inthesameproposal,theysuggestusing
CRAWLJAXforcreatingastaticsnapshotforthispurpose.Webdeveloperscanusethe
model inferred by CRAWLJAX to automatically generate a static HTML snapshot of
theirdynamiccontent,whichthencanbeservedtoGoogleforindexing.
TheabilitytoautomaticallydetectandexercisetheexecutableelementsofanAJAX
site and navigate between the various dynamic states gives us a powerful web analy-
sisandtestautomationmechanism.Intherecentpast,wehaveappliedCRAWLJAXin
thefollowingwebtestingdomains:(1)invariant-basedtestingofAJAXuserinterfaces
[Mesbah and van Deursen 2009], (2) spotting security violations in web widget inter-
actions [Bezemer et al. 2009] (3) regression testing of dynamic and non-deterministic
webinterfaces[Roestetal.2010],and(4)automatedcross-browsercompatibilitytest-
ing[MesbahandPrasad2011].
8. RELATEDWORK
Web crawlers, also known as web spiders and (ro)bots, have been studied since the
advent of the web itself [Pinkerton 1994; Heydon and Najork 1999; Cho et al. 1998;
BrinandPage1998;Burner1997].
More recently, there has been extensive research, on the hidden-web behind forms
[Raghavan and Garcia-Molina 2001; de Carvalho and Silva 2004; Lage et al. 2004;
Ntoulas et al. 2005; Barbosa and Freire 2007; Dasgupta et al. 2007; Madhavan et al.
2008]. The main focus in this research area is to detect ways of accessing the web
contentbehinddataentrypoints.
16http://code.google.com/web/ajaxcrawling/docs/getting-started.html
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 29

0:28 Mesbahetal.
Onthecontrary,thehidden-webinducedasaresultofclient-sidescriptingingeneral
and AJAX inparticularhasgainedverylittleattentionsofar.
Alvares et al. [2004; 2006] discuss some challenges of crawling hidden content gen-
eratedwith JAVASCRIPT,butfocusonhypertextlinks.
To the best of our knowledge, our initial work on CRAWLJAX [Mesbah et al. 2008]
in 2008 was the first academic research work proposing a solution to the problem of
crawling AJAX, in the form of algorithms and an open source tool that automatically
crawlsandcreatesafinitestate-machineofthestatesandtransitions.
In 2009, Duda et al. [2009] discussed how AJAX states could be indexed. The au-
thors present a crawling and indexing algorithm. Their approach also builds finite
state models of AJAX applications, however, there is no accompanying tool available
for comparison. The main difference between their algorithm and ours seems to be in
thewayclickableelementsaredetected,whichisthrough JAVASCRIPT analysis.
TheworkofMemonetal.[2001;2003]onGUIRippingfortestingpurposesisrelated
toourworkintermsofhowtheyreverseengineeranevent-flowgraphofdesktopGUI
applicationsbyapplyingdynamicanalysistechniques.
Therealsoexistsalargebodyofknowledgetargetingchallengesinparallelanddis-
tributedcomputing.Specificallyfortheweb,ChoandGarcia-Molina[2002]discussthe
challenges of parallel crawling and propose an architecture for parallel crawling the
classicalweb.Boldietal.[2004]presentthedesignandimplementationofUbiCrawler,
adistributedwebcrawlingtool.NotethattheseworksareURL-basedandassuchnot
capableoftargetingevent-based AJAX applications.
9. CONCLUDINGREMARKS
CrawlingmodernAJAX-basedwebsystemsrequiresadifferentapproachthanthetra-
ditionalwayofextractinghypertextlinksfromwebpagesandsendingrequeststothe
server.
This paper proposes an automated crawling technique for AJAX-based web appli-
cations, which is based on dynamic analysis of the client-side web user interface in
embeddedbrowsers.Themaincontributionsofourworkare:
—Ananalysisofthekeychallengesinvolvedincrawling AJAX-basedapplications;
—A systematic process and algorithm to drive an AJAX application and infer a state
machinefromthedetectedstatechangesandtransitions.Challengesaddressedin-
cludetheidentificationofclickableelements,thedetectionofDOMchanges,andthe
constructionofthestatemachine;
—A concurrent multi-browser crawling algorithm to improve the runtime perfor-
mance;
—TheopensourcetoolcalledCRAWLJAX,whichimplementsthecrawlingalgorithms;
—Twostudies,includingseven AJAX applications,usedtoevaluatetheeffectiveness,
correctness,performance,andscalabilityoftheproposedapproach.
AlthoughwehavebeenfocusingonAJAXinthispaper,webelievethattheapproach
couldbeappliedtoanyDOM-basedwebapplication.
The fact that the tool is freely available for download will help to identify exciting
case studies. Furthermore, strengthening the tool by extending its functionality, im-
proving the accuracy, performance, and the state explosion algorithms are directions
we foresee for future work. We will conduct controlled experiments to systematically
analyze and find new ways of optimizing the back tracking algorithm and implemen-
tation.ManyAJAXapplicationsusehashfragmentsinURLsnowadays.Investigating
howsuchhashfragmentscanbeutilizedduringcrawlingisanotherinterestingdirec-
tion. Exploring the hidden-web induced by client-site JAVASCRIPT using CRAWLJAX
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 30

CrawlingAJAX-basedWebApplicationsthroughDynamicAnalysisofUserInterfaceStateChanges0:29
and continuing with automated web analysis and testing are other application do-
mainswewillbeworkingon.
REFERENCES
ALVAREZ, M., PAN, A., RAPOSO, J., AND HIDALGO, J. 2006.Crawlingwebpageswithsupportforclient-
sidedynamism.InAdvancesinWeb-AgeInformationManagement.LectureNotesinComputerScience
Series,vol.4016.Springer,252–262.
ALVAREZ, M., PAN, A., RAPOSO, J., AND VINA, A. 2004. Client-side deep web data extraction. In CEC-
EAST’04:ProceedingsoftheIEEEInternationalConferenceonE-CommerceTechnologyforDynamic
E-Business.IEEEComputerSociety,158–161.
ATTERER,R.ANDSCHMIDT,A.2005.Addingusabilitytowebengineeringmodelsandtools.InProceedings
ofthe5thInternationalConferenceeonWebEngineering(ICWE’05).Springer,36–41.
BARBOSA,L.ANDFREIRE,J.2007.Anadaptivecrawlerforlocatinghidden-webentrypoints.InWWW’07:
Proceedingsofthe16thinternationalconferenceonWorldWideWeb.ACMPress,441–450.
BEZEMER, C.-P., MESBAH, A., AND VAN DEURSEN, A. 2009. Automated security testing of web widget
interactions.InProceedingsofthe7thjointmeetingoftheEuropeanSoftwareEngineeringConference
andtheACMSIGSOFTsymposiumontheFoundationsofSoftwareEngineering(ESEC-FSE’09).ACM,
81–91.
BOLDI,P.,CODENOTTI,B.,SANTINI,M.,ANDVIGNA,S.2004.Ubicrawler:Ascalablefullydistributedweb
crawler.Software:PracticeandExperience34,8,711–726.
BRIN,S.ANDPAGE,L.1998.Theanatomyofalarge-scalehypertextualWebsearchengine.Comput.Netw.
ISDNSyst.30,1-7,107–117.
BURNER,M.1997.Crawlingtowardseternity:Buildinganarchiveoftheworldwideweb.WebTechniques
Magazine2,5,37–40.
CHAWATHE,S.S.,RAJARAMAN,A.,GARCIA-MOLINA,H.,ANDWIDOM,J.1996.Changedetectioninhier-
archicallystructuredinformation.InSIGMOD’96:Proceedingsofthe1996ACMSIGMODinternational
conferenceonManagementofdata.ACMPress,493–504.
CHO,J.ANDGARCIA-MOLINA,H.2002.Parallelcrawlers.InProceedingsofthe11thinternationalconfer-
enceonWorldWideWeb.ACM,124–135.
CHO, J., GARCIA-MOLINA, H., AND PAGE, L. 1998. Efficient crawling through URL ordering. Computer
NetworksandISDNSystems30,1-7,161–172.
DASGUPTA, A.,GHOSH, A.,KUMAR, R.,OLSTON, C.,PANDEY, S.,AND TOMKINS, A.2007.Thediscover-
abilityoftheweb.InWWW’07:Proceedingsofthe16thinternationalconferenceonWorldWideWeb.
ACMPress,421–430.
DECARVALHO,A.F.ANDSILVA,F.S.2004.Smartcrawl:anewstrategyfortheexplorationofthehidden
web.InWIDM’04:Proceedingsofthe6thannualACMinternationalworkshoponWebinformationand
datamanagement.ACMPress,9–15.
DIJKSTRA, E. W. 1959.Anoteontwoproblemsinconnexionwithgraphs.NumerischeMathematik1,1,
269–271.
DUDA,C.,FREY,G.,KOSSMANN,D.,MATTER,R.,ANDZHOU,C.2009.Ajaxcrawl:makingAjaxapplica-
tionssearchable.In25thInternationalConferenceonDataEngineering(ICDE’09).IEEE,78–89.
FIELDING, R. AND TAYLOR, R. N. 2002. Principled design of the modern Web architecture. ACM Trans.
Inter.Tech.(TOIT)2,2,115–150.
GARAVEL, H., MATEESCU, R., AND SMARANDACHE, I. 2001.Parallelstatespaceconstructionformodel-
checking.ModelCheckingSoftware2057,217–234.
GARRETT, J. February 2005. Ajax: A new approach to web applications. Adaptive path. http://www.
adaptivepath.com/publications/essays/archives/000385.php.
HEYDON, A. AND NAJORK, M. 1999.Mercator:Ascalable,extensiblewebcrawler.WorldWideWeb2,4,
219–229.
HICKSON,I.2011.W3CWebStorage.http://dev.w3.org/html5/webstorage/.
LAGE, J. P., DA SILVA, A. S., GOLGHER, P. B., AND LAENDER, A. H. F. 2004. Automatic generation of
agentsforcollectinghiddenwebpagesfordataextraction.DataKnowl.Eng.49,2,177–196.
LEVENSHTEIN,V.L.1996.Binarycodescapableofcorrectingdeletions,insertions,andreversals.Cybernet-
icsandControlTheory10,707–710.
MADHAVAN, J.,KO, D.,KOT, L.,GANAPATHY, V.,RASMUSSEN, A.,AND HALEVY, A.2008.Google’sdeep
webcrawl.Proc.VLDBEndow.1,2,1241–1252.
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

## Page 31

0:30 Mesbahetal.
MAXWELL, S. AND DELANEY, H. 2004. Designing experiments and analyzing data: A model comparison
perspective.LawrenceErlbaum.
MEMON,A.,BANERJEE,I.,ANDNAGARAJAN,A.2003.GUIripping:Reverseengineeringofgraphicaluser
interfacesfortesting.In10thWorkingConferenceonReverseEngineering(WCRE’03).IEEEComputer
Society,260–269.
MEMON, A.,SOFFA, M. L.,AND POLLACK, M. E.2001.CoveragecriteriaforGUItesting.InProceedings
ESEC/FSE’01.ACMPress,256–267.
MESBAH, A., BOZDAG, E., AND VAN DEURSEN, A. 2008.CrawlingAjaxbyinferringuserinterfacestate
changes.InProceedingsofthe8thInternationalConferenceonWebEngineering(ICWE’08).IEEECom-
puterSociety,122–134.
MESBAH, A. AND VAN DEURSEN, A.2007.Migratingmulti-pagewebapplicationstosingle-pageAjaxin-
terfaces.InProc.11thEur.Conf.onSw.MaintenanceandReengineering(CSMR’07).IEEEComputer
Society,181–190.
MESBAH, A. AND PRASAD, M. R.2011.Automatedcross-browsercompatibilitytesting.InProceedingsof
the33rdACM/IEEEInternationalConferenceonSoftwareEngineering(ICSE’11).ACM,561–570.
MESBAH,A.ANDVANDEURSEN,A.2008.Acomponent-andpush-basedarchitecturalstyleforAjaxappli-
cations.JournalofSystemsandSoftware81,12,2194–2209.
MESBAH, A. AND VAN DEURSEN, A. 2009. Invariant-based automatic testing of Ajax user interfaces. In
Proceedingsofthe31stInternationalConferenceonSoftwareEngineering(ICSE’09).IEEEComputer
Society,210–220.
NTOULAS, A.,ZERFOS, P.,AND CHO, J.2005.Downloadingtextualhiddenwebcontentthroughkeyword
queries.InJCDL’05:Proceedingsofthe5thACM/IEEE-CSjointconferenceonDigitallibraries.ACM
Press,100–109.
PINKERTON, B.1994.Findingwhatpeoplewant:Experienceswiththewebcrawler.InProceedingsofthe
SecondInternationalWorldWideWebConference.Vol.94.17–20.
PIXLEY, T. 2000.W3CDocumentObjectModel(DOM)Level2EventsSpecification.http://www.w3.org/
TR/DOM-Level-2-Events/.
RAGHAVAN,S.ANDGARCIA-MOLINA,H.2001.Crawlingthehiddenweb.InVLDB’01:Proceedingsofthe
27thInternationalConferenceonVeryLargeDataBases.MorganKaufmannPublishersInc.,129–138.
ROEST, D.,MESBAH, A.,AND VAN DEURSEN, A.2010.RegressiontestingAjaxapplications:Copingwith
dynamism. In Proceedings of the 3rd International Conference on Software Testing, Verification and
Validation(ICST’10).IEEEComputerSociety,128–136.
RUSSELL,A.2006.Comet:Lowlatencydataforthebrowser.http://alex.dojotoolkit.org/?p=545.
VALMARI,A.1998.Thestateexplosionproblem.InLNCS:LecturesonPetriNetsI,BasicModels,Advances
inPetriNets.Springer-Verlag,429–528.
Received2010;revised;accepted
ACMTransactionsontheWeb,Vol.0,No.0,Article0,Publicationdate: 2011.

