# Morpheus Web Testing A Tool For Generating Test Cases For Widget Based Web Applications

**Source:** Morpheus_Web_Testing_A_Tool_for_Generating_Test_Cases_for_Widget_Based_Web_Applications.pdf  
**Converted:** 2026-01-26 09:23:34

---

## Page 1

Morpheus Web Testing: A Tool
for Generating Test Cases for Widget
Based Web Applications
RomulodeAlmeidaNeves∗,WillianMassamiWatanabe
andRafaelOliveira
FederalTechnologicalUniversityofParana(UTFPR),Corne´lioProco´pio,Parana´,
Brazil
E-mail:romulo.neves@gmail.com
∗CorrespondingAuthor
Received07October2020;Accepted25August2021;
Publication22December2021
Abstract
Context: Widgets are reusable User Interfaces (UIs) components frequently
delivered in Web applications.In the web application, widgets implement
differentinteractionscenarios,suchasbuttons,menus,andtextinput.
Problem:Testsareperformedmanually,sothecostassociatedwithpreparing
andexecutingtestcasesishigh.
Objective:Automatetheprocessofgeneratingfunctionaltestcasesforweb
applications,usingintermediateartifactsofthewebdevelopmentprocessthat
structurewidgetsinthewebapplication.Thegoalofthisprocessistoensure
the quality of the software, reduce overall software lifecycle time and the
costsassociatedwithtests.
Method:Weelaboratedatestgenerationstrategyandimplementedthisstrat-
egyinatool,MorpheusWebTesting.MorpheusWebTestingextractswidget
information from Java Server Faces artifacts to generate test cases for JSF
JournalofWebEngineering,Vol. 21 2, 119–144.
doi: 10.13052/jwe1540-9589.2121
©2022RiverPublishers

## Page 2

120 R.deAlmeidaNevesetal.
web applications. We conducted a case study for comparing Morpheus Web
Testingwithastateofthearttool(CrawlJax).
Results: The results indicate evidence that the approach Morpheus Web
TestingmanagedtoreachgreatercodecoveragecomparedtoaCrawlJax.
Conclusion:Theachievedcoveragevaluesrepresentevidencethattheresults
obtainedfromtheproposedapproachcontributetotheprocessofautomated
testsoftwareengineeringintheindustry.
Keywords:Userinterfaces,widgets,morpheuswebtesting,codecoverage.
1 Introduction
The User Interface (UI) is an essential part of most applications in use.
Currently, there are three UI types: Graphical User Interface (GUI), used in
desktop application; Web User Interface (WUI), used in web applications;
and Handheld User Interface (HUI), used in mobile devices [21]. The UIs
are frequently composed by elements (widgets) that can be reused in dif-
ferent [19,21], such as frames, buttons, menu items, and text box [15]. On
the other hand, software testing is one of the main activities performed to
improvethequalityofthesoftwareunderdevelopment.Itsmainobjectiveis
to detect errors as early as possible in the software development cycle [16],
in order to minimize the cost of delivering fixes to the product [18,20].
Delamaro et al. (2007) state that a successful testing approach can decrease
testingeffort,contributetoimprovingproductqualityandreducethecostsof
maintenance[7].
In some development scenarios, tests are performed manually and the
cost associated with elaborating test cases is high, given the high number of
possibleuserinteractionscenarioswithapplications[17].Inthesescenarios,
the test activity can become costly and misleading [1]. Other aggravating
factors for performing the tests are the high complexity of the systems
currently developed and their continuous evolution [2,12]. Thus, software
testing automation is essential to improve the efficiency of software testing
activity and has become one of the alternatives to obtain a product with a
reducednumberofdefects[8,11]andtoreducecosts,increasetestefficiency,
ensuresoftwarequalityandreduceoverallsoftwarelifecycletime[9].
This paper has the goal of elaborating strategies for generating auto-
mated functional test cases for web applications. We elaborated a test case

## Page 3

MorpheusWebTesting 121
generation strategy that extracts widgets information from UI configuration
artifactsandusesthisinformationtogeneratefunctionaltests.Wedeveloped
a tool, Morpheus Web Testing, which implemented this strategy using two
WUI component frameworks: the JavaServer Faces (JSF) and Primefaces.
Our strategy focuses on the generation of system-level functional test cases.
Acasestudywasconductedtoevaluatehowourtestcasegenerationstrategy
performs in comparison to another state-of-art technique. Moreover, the
case study was conducted in an industrial setting, with a production ready
JSF/Primefacesbasedwebapplication.
The remainder of this article is organized as follows: Section 2 presents
relatedworks.Section3presentstheproposalofthispaper.Section4presents
the evaluation of our proposed test generation strategy. Section 5 presents
discussions. Finally, Section 6 presents final considerations, limitations of
thisworkandfutureworks.
2 Related Work
In [15], the authors presented a UI’s testing framework denominated GUI-
TAR which generates test cases based on events implemented in the UI.
The framework generates application models from Java UI artifacts which
are, then, used in the testing of the application. In the test cases generation
process, GUITAR extracts information about the structure of all windows,
widgets,aswellastheirattributesandgraphicalinterfaceevents.Theframe-
work creates a flow of events with all possible UI event interactions. These
events are used to generate UI test cases that are sequences of UI events.
GUITARalsosupportstheexecutionofthegeneratedtestcasesinaJavaUI
application.
In[14]theauthorspresentedatoolcalledAutoBlackTest.Thistoolimple-
ments a process that incrementally generates test cases as a user interacts
with the application. This generation process is divided in two steps. In
the first step, the tool generates a sequence model of events that can be
producedthroughaninteractionwiththeapplicationUIundertest.Itisworth
mentioningthatmodelgenerationoccursthroughtheuseofareinforcement
learning system called Q-learning. Lastly, in the second step, it begins the
generationofadatasetofteststhatcoversthesequencesinthemodel.
In [23], the authors presented a tool called CrawlJax. This tool performs
thetestcasegenerationprocessautomatically,analyzingstatechangesinthe
web application interface with Ajax (Asynchronous JavaScript and XML).
Thisprocessisdividedintotwosteps:(i)acrawler(controller)thatexercise

## Page 4

122 R.deAlmeidaNevesetal.
client-sidecodeandidentifiestheclickableelementsthatchangestatewithin
theDOM(DOMstandsforDocumentObjectModel)builtdynamicallyinthe
browser. Finally in the second step (ii) the creation of a graph of state flow,
called the SFG (State-Flow Graph) that captures dynamically DOM states,
theUIstates,andthepossibletransitionsmadebetweenthem.
In [6], the development of the WebMate tool is reported. WebMate is
a tool that performs test case generation for web applications. WebMate
explores the functionality of a web application that detects the differences
between web browsers and operating systems. The process test case genera-
tion in the WebMate consists of three steps: (i) the information is extracted
an URL wherein the user interacts with the application by examining all
buttons,links,forms,oranyelementmanipulatedbyeventswhichcantrigger
off interaction with the user. In (ii), usage models are extracted from the
application in a graph form, where the nodes correspond to the different
application states and the edges represent user interactions. In (iii), test are
performed in the Web application, exercising all transitions of the generated
usagemodel,verifyingthecompatibilitybetweenbrowsers,conductingcode
analysisandregressiontests.
In [24], the authors proposed an approach to obtain textual input val-
ues while testing Android apps automatically. This process consists of four
steps:(i)Descriptionmatching,inthisstepisidentifiedandmatcheddescrip-
tive labels with input fields concept extraction, input value acquisition and
input value consumption. (ii) Concept extraction, in this step, natural lan-
guage processing techniques are used for extracting the concept associated
with the label. (iii) Input value acquisition, in this step the concepts are
used to query a knowledge base for candidate input values. (iiii) Input value
consumption clustered, in this step, the UI elements are filled according to
their functionality into input and actions, filling the input elements first and
theninteractingwiththeactions.
In [10], the authors performed a survey that assists software developers
in making a decision regarding the testing tools, based on black and white
box approaches to use in web/mobile applications. Thereby a set of current
testing approaches were surveyed using four test-key factors, (i) Artificial
Intelligence(AI),(ii)Securityfocused,(iii)Fullyautomatedand(iv)Heuristic
search.
Differentlyfromthesepriorworks[5,15,23]thatusedlow-levelinterface
componentsbasedonHyperTextMarkupLanguage(HTML)togeneratetest
cases, our work extracts information from complex interface components,
widgets, as defined in the web application. Our test case generation strategy

## Page 5

MorpheusWebTesting 123
wasimplementedinatoolandusesExtensibleHyperTextMarkupLanguage
(XHTML)definedinaUIframeworkforwebdevelopment:JSFandPrime-
faces. In this context, this paper reports on a investigation of whether this
approach of using higher abstraction level components (widgets defined in
JSF/Primefacesartifacts)forgeneratingfunctionaltestcasescanenhancethe
test case generation process. We identified that the use of the higher level
interfacecomponentsintheJSF/Primefacescomponentspresentsthefollow-
ingadvantages:(i)thepossibilitytogetmoreinformationthananHTMLfile
andthuspredictandimprovetheinteractionlevelsofthecomponents,and(ii)
thepossibilityofgeneratingmoretestcaseinputsand,consequently,achieve
greatercodecoverage.
3 Test Case Generation Approach
Thispaperhadthegoalofgeneratingautomaticfunctionaltestcasesforweb
applications. In order to achieve this goal, we elaborated a test case gen-
eration strategy, which extracts widget semantic information from software
artifacts that define the UI of web applications. As a proof-of-concept, we
implementedthistestcasegenerationstrategyinatoolcalledMorpheusWeb
Testing which consists of test case generation using two frameworks that
assistdevelopersinwebapplicationbuilding:JSFandPrimefaces.
In Morpheus Web Testing, the test case generation strategy was divided
intofoursteps,asshowninFigure1.
Inthefirststep,Entry(seeFigure1(A)),MorpheusWebTestingreceives
asaninputaprojectthatusestheJSFandPrimefacesframeworks.Afterthe
project entry, the process of generating of usage model is started, extracting
and analysing the Widgets defined in the XHTML code of JSF projects as a
UI definition model (see Figure 1(B)). In this second step, web application
information about the structure of all windows, widgets as well as their
attributes and events of interface graph are extracted. These events are,
Figure1 Proposalofthetestmodelanddevelopmentofthispaper.

## Page 6

124 R.deAlmeidaNevesetal.
then, used to generate test cases from the WUI that are sequences of WUI
events. Finished the second step, the generation of test cases is started (see
Figure 1(C)), in which JUnit and Selenium WebDriver based test cases are
generated,asoutput.Finally,inthelaststep(seeFigure1(D)),thetestcases
canbeexecuted.
Seleniumisanopensourcetestingtoolwhichisusedtoautomatethetest
casesandenhancethetestingperformance.Seleniumisanautomatedtesting
tool for web application. Selenium WebDriver basically work in two ways
first locate the element and then perform some action on them. Selenium
WebDriver locate element by usingid, name,Xpath, CSS, link text, partial
linktext.Seleniumprovidesarichsetoffunctionswhichisusedtotestingof
awebapplication[13].
Test cases can be defined as a way of establishing the inputs to be
informed by the tester (manually or with tool support) and the results
expectedfrom thisaction. Thetestcases arecomposedof threesteps:input,
stepsandoracles[7,22].
Inordertogeneratetheinputofatestcase,MorpheusWebTestingiden-
tifies the objects and the properties of a WUI. Then, Morpheus Web Testing
uses different strategies for each type of input (widget), as demonstrated in
Table1anddetailedbelow.
• For widgets of type InputTextArea, InputNumber, InputMask, Input-
Text, Password, TextEditor, CKEditor, or Editor, multiple text input
scenariosaregenerated,suchas:randomlygeneratednumbers/textsand
blankinput;
• For widgets of type: Button, CommandButton, CommandLink, Link
and LinkButton, test cases in which clicks are performed on these
componentsaregenerated;
• For widgets of type SelectBooleanButton, SelectBooleanCheckBox,
SelectOneButton, SelectOneRadio, SelectOneMenu, SelectOneList-
Box, SelectManyButton, SelectManyMenu or SelectManyCheckBox,
multipletestcaseswhichselecteachpossibleinputaregenerated;and
• For widgets of type calendar, test cases which insert random dates,
integers,andemptystringsaregenerated.
For the strategies of insertion of texts and random integers, if the
maxLenght property is not specified in the test cases will consider a default
a size of 50 characters for the component. The test case generation process
is performed through instructions defined in templates. In [4] templates are
definedastextfiles,instrumentedwithselectionandexpansionconditionsof

## Page 7

MorpheusWebTesting 125
Table1 ComponentsandstrategiesusedbyMorpheusWebTesting
Strategy
Component IRIN IRGT TIB Click Selection IRD
InputTextArea X X X
InputNumber X X X
InputMask X X X
InputText X X X
Passoword X X X
TextEditor X X X
Editor X X X
ckEditor X X X
Button X
CommandButton X
ComandLink X
Link X
LinkButton X
SelectBooleanButton X
SelectBooleanCheckBox X
SelectOneButton X
SelectOneMenu X
SelectOneListBox X
SelectManyButton X
SelectManyMenu X
SelectManyCheckBox X
calendar X X X
IRIN=InsertionofRandomIntegerNumbers
IRGT=InsertionofRandomlyGeneratedText
TIB=TextInsertioninBlank
IRD=InsertionofRandomDates
code.Theseinstructionsareresponsibleforconsultinganinputthatcanbea
program, a textual specification or diagrams and as a result, it’s possible to
gettheparametertoproducethesourcecode[3].
Figure 2 illustrates an example of the test case generation process. This
figure illustrates a test case generation for the inputText widget in line 2 of
Figure 2(A), in the XHTML file. The widget definition markup inside the
XHTML file is used to identify the attributes of the widget (id, max length
and type of the widget) and generate test case scenarios associated to that
type of widget. The example illustrates the generation of a test case which
insertsarandomstringastextinputforthewidget.

## Page 8

126 R.deAlmeidaNevesetal.
Figure2 JavacodegenerationwithSeleniumframeworkbasedontemplate.
Figure 3 illustrates a snippet of Java code generated by Morpheus Web
Testing (see Figure 2) wherein, for each widget in the XHTML file, a spe-
cific input will be generated. In JSF XHTML templates, input type widgets
must be placed inside a form element, hence, after generating the input test
cases for the input widgets, Morpheus Web Testing generates an action for
activating their respective form element, clicking the submit button of the
form.
The Morpheus Web Testing approach is an open source software is
available for access through the address.1 Furthermore was developed using
thefollowingframeworks:
1https://github.com/raneves/morpheus.git

## Page 9

MorpheusWebTesting 127
Figure3 ExempleofJavacodegenerated.
• Java:JDKversion1.8;and
• Dom4j: An open source Java library for parsing the XHTML code,
identifyingwidgetsinthewebapplication.
4 Evaluation
In order to evaluate our test case generation approach, we conducted a case
studyforevaluatingthequalityofthetestcaseswhichweregenerated.Inour
study, the quality of test cases was measured in terms of the Code Coverage
metric. The case study design was guided by the following hypotheses H
0
andH .
1
• H :Codecoverageobtainedbytestcasesgeneratedusingwidgetinfor-
0
mation extracted from WUI definition (our approach) does not differ
fromstate-of-arttestcasesgenerationapproaches.
• H :Codecoverageachievedbytestcasesgeneratedusingwidgetinfor-
1
mation extracted from WUI definition (our approach) is superior to
state-of-arttestcasesgenerationapproaches.
4.1 Methodology
Considering the hypotheses H and H previously described, the method-
0 1
ology of this study was designed to compare how our test case generation

## Page 10

128 R.deAlmeidaNevesetal.
approachperformsincomparisonwithotherstate-of-arttestcasegeneration
tool,inregardstotheCodeCoveragemetric.Ourapproachwasimplemented
in Morpheus Web Testing tool, and it focuses on web applications. The
baselineofourcasestudy(control)wastheCrawlJaxtool,whichrepresents
astate-of-artopensourcetoolforgeneratingtestcasesforwebapplications.
However, differently from Morpheu Web Testing, CrawlJax uses semantic
information extracted from the HTML source-code of a web application.
Hence,CrawlJaxdoesnotrelyonwidgetinformation,sincetheseinformation
arenotdefinedintheHTMLcode.
Forthisstudy,weusedawebprojectcalledExactusCRM(acommercial
applicationwithclosedsourcecode)and,twoautomatictestcasegeneration
tools for web applications, Morpheus Web Testing, and CrawlJax (state-of-
the-arttechnique),withtheobjectiveofperformingacomparativeevaluation
between both applications. Morpheus Web Testing is a tool which uses
widgetsinformationextractedfromJSFXHTMLcodetogeneratetestcases.
Exactus CRM is an industrial, production-ready JSF/Primefaces web appli-
cation, which implements client support, finances and accountability man-
agement functionalities. It was developed by Exactus,2 a brazilian software
development company, has 11,168 active users, was first deployed in pro-
duction in 2012 and is currently deployed in Jelastic3 Platform-as-a-Service
infrastructure.ExactusCRMwasbuiltusingthefollowingtechnologies:
• JSF:version2.2.8;
• Primefaces:version6.0;
• Hibernate-JavaPersistenceAPI(JPA):version5.0;
• Maven:version3.1;
• Cobertura:version2.1;
• Jetty:version9.4.9;
• Java:JDKversion1.8;
• selenium-java:version3.7.1;and
• MySql:version5.5.
Morpheus Web Testing was first designed to reduce costs associated
to test case elaboration and execution for Exactus CRM. Exactus CRM
architecturewasdesignedaccordinglytotheModel-View-ControllerDesign
Patternandisdividedinto4layersdescribednext:
2https://www.exactus.com.br/
3https://jelastic.com/

## Page 11

MorpheusWebTesting 129
• Dataaccessobjectlayer(DAO):containsallaccessandexecutionlogic
forthedatabase;
• Plain old java object layer (POJO): maps classes to tables in the
database, that is, a JPA the entity represented by the design pattern
named JavaBeans (the class should have private attributes, a default
constructorwithoutargumentsandmethodsgettersandsettersforeach
attribute);
• ManagedBean layer: contains codes responsible for performing the
back-end, business rules and validation in general. This layer receives
the entered data through the XHTML pages, processes and returns the
resultsoftheoperationtothepage;and
• Utilitieslayer:containscodethatvalidatesdifferentparameterssuchas:
BraziliannumericIDs,passportcode,emails,zipcode,andphone.
Exactus CRM contains a total of 207 classes and 11415 lines of code.
Thenumberofclassesandthetotallinesofcodeforeachlayeraredescribed
next:
• DAOlayer:65classesand1618lineofcode;
• ManagedBeanlayer:39classesand4857lineofcode;
• Utilitieslayer:4classesand171lineofcode;and
• POJOlayer:99classesand4769lineofcode.
After configuring Morpheus Web Testing and CrawlJax for generating
testcasesforExactusCRM,bothapproacheswereexecuted.Theirexecution
were run in an instrumented version of Exactus CRM, which collected
CoverageMetricsforallclassesofthewebapplication.Nextsection,presents
theresultsofthismethodology.
4.2 Results
Inthisstudy,MorpheusWebTestinggenerated91testcases.Comparingthe
results between our approach and the state-of-the-art can provide evidences
supportinghypothesisH orH .Next,wecomparetheCodeCoveragebyline
0 1
and branch results for each approach separately, according to each layer of
ExactusCRM,thenweprovideageneralcomparisonconsideringalllayers:
4.2.1 DAO layer
In the DAO layer, 1062 lines (out of 1618 existing) were covered by test
cases generated by Morpheus Web Testing, totaling 66% coverage. While
for the CrawlJax approach, 543 lines (out of 1618 existing) were covered,

## Page 12

130 R.deAlmeidaNevesetal.
totaling 34% coverage. Grouping the coverage results for each class of the
DAO layer, for each approach we run a Shapiro-Wilk normality test. The
resultsofthesetestsshowedevidencethatcoveragewithbothapproachesdo
notmatchanormaldistribution,withw=0.87864andp-value=1.196e−05
for Morpheus Web Testing, and w = 0.89158 e p-value = 3.438e−05 for
CrawlJax. Then, Mann Whitney Wilcoxon statistical test showed significant
differences between the coverage of both approaches with W=26042 and
p-value = 0.0001478; The probability density of the coverage reported for
the DAO layer using Morpheus Web Testing and Crawljax is illustrated in
Figure4(A).
In regards to branch Code Coverage, 90 branchs (out of 158 existing)
were covered by test cases generated by Morpheus Web Testing, totaling
56% branch. While for the CrawlJax approach, 44 branchs (out of 158
existing) were branched, totaling 27% branch. Grouping the branch results
for each class of the DAO layer, for each approach we run a Shapiro-
Wilk normality test. The results of these tests showed evidence that branch
with both approaches match a normal distribution, with w = 0.96031 and
p-value = 0.78826 for Morpheus Web Testing, and w = 0.86875 e p-
value = 0.06301 for CrawlJax. Then, Mann Whitney Wilcoxon statistical
testshowedsignificantdifferencesbetweenthecoverageofbothapproaches
with V = 35 and, p-value = 0.02055. The probability density of the branch
reported for the DAO layer using Morpheus Web Testing and Crawljax is
illustratedinFigure5(A).
4.2.2 POJO layer
In the POJO Layer, 1200 lines (out of 4769 existing) were covered by test
cases generated by Morpheus Web Testing, totaling 25% coverage. While
for the CrawlJax approach, 1081 lines (out of 4769 existing) were covered,
totaling 23% coverage. Grouping the coverage results for each class of the
POJO layer, for each approach we run a Shapiro-Wilk normality test. The
resultsofthesetestsshowedevidencethatcoveragewithbothapproachesdo
notmatchanormaldistribution,withw=0.848242andp-value=7.137e−05
for Morpheus Web Testing, and w = 0.92879 e p-value = 4.637e−05 for
CrawlJax.Then,MannWhitneyWilcoxonstatisticaltestdidnotshowsignif-
icantdifferencesbetweenthecoverageofbothapproacheswithW=5122.5
and p-value = 0.5825; The probability density of the coverage reported for
the POJO layer using Morpheus Web Testing and Crawljax is illustrated in
Figure4(B).

## Page 13

MorpheusWebTesting 131
In the regards to branch Code Coverage, 74 brachs (out of 390 existing)
werebranchbytestcasesgeneratedbyMorpheusWebTesting,totaling185%
branch.WhilefortheCrawlJaxapproach,72lines(outof390existing)were
branched,totaling18%branch.Groupingthebranchresultsforeachclassof
thePOJOlayer,foreachapproachwerunaShapiro-Wilknormalitytest.The
results of these tests showed evidence that branch with both approaches do
notmatchanormaldistribution,withw=0.70793andp-value=5.008e−06
for Morpheus Web Testing, and w = 0.71375 e p-value = 6.059e−06 for
CrawlJax.Then, Mann Whitney Wilcoxon statistical test did not show sig-
nificant differences between the coverage of both approaches with V = 1,
p-value = 1. The probability density of the branch reported for the POJO
layerusingMorpheusWebTestingandCrawljaxisillustratedinFigure5(B).
4.2.3 ManagedBean layer
IntheManagedBeanLayer,2295rows(outof4857existing)werecoveredby
thetestcasesgeneratedbyMorpheusWebTesting,totaling48%ofcoverage.
While for the CrawlJax approach, 2234 lines (out of 4857 existing) were
covered, totaling 46% coverage. Grouping the coverage results for each
class of the ManagedBean layer, for each approach we run a Shapiro-Wilk
normalitytest.Theresultsofthesetestsshowedevidencethatcoveragewith
both approaches do not match a normal distribution, with w = 0.92668
and p-value = 0.01408 for Morpheus Web Testing, and w = 0.89555 e
p-value = 0.001648 for CrawlJax. Then, Mann Whitney Wilcoxon statisti-
cal test did not show significant differences between the coverage of both
approaches with W = 854.5 and p-value = 0.3495; The probability density
of the coverage reported for the ManagedBean layer using Morpheus Web
TestingandCrawljaxisillustratedinFigure4(C).
In the regards to branch Code Coverage, 531 branchs (out of 121 exist-
ing) were branched by the test cases generated by Morpheus Web Testing,
totaling 43% of branch. While for the CrawlJax approach, 504 branchs
(out of 1212 existing) were branched, totaling 41% branch. Grouping the
branch results for each class of the ManagedBean layer, for each approach
we run a Shapiro-Wilk normality test. The results of these tests showed
evidence that branch with both approaches match a normal distribution,
with w = 0.95113 and p-value = 0.1228 for Morpheus Web Testing, and
w = 0.94319 e p-value = 0.07004 for CrawlJax. Then, no significant differ-
ences were observed according to a Student T-test between the coverage of
both approaches t = 15.451, df = 69, p-value < 2.2e −16. The probability

## Page 14

132 R.deAlmeidaNevesetal.
density of the branch reported for the ManagedBean layer using Morpheus
WebTestingandCrawljaxisillustratedinFigure5(C).
4.2.4 Util layer
In the Util Layer, 109 lines (out of 171 existing) were covered by test cases
generated by Morpheus Web Testing, totaling 64% coverage. While for the
CrawlJax approach, 77 lines (out of 171 existing) were covered, totaling
46% of coverage. Grouping the coverage results for each class of the Util
layer, for each approach we run a Shapiro-Wilk normality test. The results
of these tests did not show evidence that coverage with both approaches
match a normal distribution, with w = 0.95568 and p-value = 0.7518 for
Morpheus Web Testing, and w=0.84161 e p-value=0.2001 for CrawlJax.
Then, no significant differences were observed according to a Student T-
test between the coverage of both approaches with t = 2.2479, df = 4.272
andp-value=0.08358;Theprobabilitydensityofthecoveragereportedfor
the Util layer using Morpheus Web Testing and Crawljax is illustrated in
Figure4(D).
In the regards to branch Code Coverage, 11 branchs (out of 38 existing)
were branched by test cases generated by Morpheus Web Testing, totaling
39% branch. While for the CrawlJax approach, 14 branchs (out of 38 exist-
ing) were branched, totaling 36% of branch. Grouping the branch results
for each class of the Util layer, for each approach we run a Shapiro-Wilk
normality test. The results of these tests did not show evidence that cover-
age with both approaches match a normal distribution, with w = 0.90977
and p-value = 0.4173 for Morpheus Web Testing, and w = 0.98047 e p-
value=0.7322forCrawlJax.Then,nosignificantdifferenceswereobserved
according to a Student T-test between the coverage of both approaches with
t=4.3201,df=5,p-value=0.00757.Theprobabilitydensityofthebranch
reported for the Util layer using Morpheus Web Testing and Crawljax is
illustratedinFigure5(D).
4.2.5 All layers
In the All Layers, 4641 rows (out of 11415 existing) were covered by
the test cases generated by Morpheus Web Testing, totaling 41% coverage.
While for the CrawlJax approach, 3935 lines (out of 11415 existing) were
covered,totaling35%coverage.Groupingthecoverageresultsforeachclass
of all layers of Exactus CRM, for each approach we run a Shapiro-Wilk
normalitytest.Theresultsofthesetestsshowedevidencethatcoveragewith
both approaches do not match a normal distribution, with w = 0.93908

## Page 15

MorpheusWebTesting 133
and p-value = 1.262e−07 for Morpheus Web Testing, and w = 0.90323
e p-value = 2.445e−10 for CrawlJax. Then, significant differences were
observedaccordingtoaMannWhitneyWilcoxontestbetweenthecoverage
of both approaches with w = 26042 and p-value = 0.0001478; The proba-
bilitydensityofthecoveragereportedforthealllayersusingMorpheusWeb
TestingandCrawljaxisillustratedinFigure4(E).
IntheregardstobranchCodeCoverage,710branchs(outof1798exist-
ing) were branched by the test cases generated by Morpheus Web Testing,
totaling 39% branch. While for the CrawlJax approach, 634 branchs (out
of 1798 existing) were branched, totaling 35% branch. Grouping the branch
results for each class of all layers of Exactus CRM, for each approach we
runaShapiro-Wilknormalitytest.Theresultsofthesetestsshowedevidence
thatcoveragewithbothapproachesdonotmatchanormaldistribution,with
w = 0.87319 and p-value = 1.562e−06 for Morpheus Web Testing, and
w = 0.89451 e p-value = 1.0225e−05 for CrawlJax. Then, significant dif-
ferenceswereobservedaccordingtoaMannWhitneyWilcoxontestbetween
thecoverageofbothapproacheswithV=206andp-value=0.0001705.The
probability density of the branch reported for the all layers using Morpheus
WebTestingandCrawljaxisillustratedinFigure5(E).
When the sample has a tendency to follow a normal distribution, a para-
metrictestisappliedStudentT-testandintheoppositecase,ienon-normality,
wilcoxisapplied.Shapiro-Wilknormalitytestswereusedforidentifyingifa
sample is normal or not normal, if its p value is less than 0.05 it means that
thereareindicationsthatthesampleisnotnormal.
In Figure 4, it is possible to observe that the coverage distribution was
greater in Morpheus, mainly in the DAO, UTIL and all layers. At the same
time it is also possible to observe that for certain samples (layer util) the
coveragedistributionsoftheapproachesaresimilartoanormaldistribution,
ontheotherhandsamplesinthelayers(Pojolayer,daoandalllayers)donot
ressembleanormaldistribution.
In Figure 5, it is possible to observe that the coverage distribution was
greater in Morpheus, mainly in the DAO, UTIL and all layers. At the same
time it is also possible to observe that for certain samples (DAO layer and
ManagedBean) the coverage distributions of the approaches are similar to a
normal distribution, on the other hand samples in the layers (Pojo layer, util
andalllayers)donotressembleanormaldistribution.
Allstatisticaltestswereconductedconsideringa0.95confidenceinterval.
Inregardstothecoverageresultsofbothapproaches,thetestcasesgenerated
by Morpheus Web Testing and CrawlJax failed to reach ManagedBean and

## Page 16

134 R.deAlmeidaNevesetal.
Figure4 CoverageprobabilitydensityusingMorpheusWebTestingandCrawljax.
POJOgetandsetmethodswhichwerenotexplicitlyincludedintheWUIof
the web application. Moreover, exception handling routines implemented in
theUtilandDAOlayerswerenotreachedbytheapproachesaswell.Future
worksshouldincludewaysfortestingthesecomponents.

## Page 17

MorpheusWebTesting 135
Figure5 BranchprobabilitydensityusingMorpheusWebTestingandCrawljax.
Considering the case study scenario, the results represent evidences that
supporthypothesisH ,consideringthatallcoverageresultswerehigherwhen
1
using Morpheus Web Testing in comparison to Crawljax. Furthermore, H
1
was also supported by the significant differences observed when comparing
the coverage of both approaches. More specifically, it was observed that
Morpheus Web Testing coverage results impacted significantly the coverage
oftheDAOlayerofthewebapplication.

## Page 18

136 R.deAlmeidaNevesetal.
5 Discussion
This paper presented a strategy for generating functional test cases for
web applications. We proposed a generation strategy which uses widget
information for generating test cases. The test case generation strategy was
implemented in Morpheus Web Testing tool which used widget information
availableinXHTMLJSF/Primefacestemplatesforgeneratingthetestcases.
Our general hypothesis was that using widget information, which stand for
complex UI components, could enhance the coverage of the test case gener-
ation process for web applications, in comparison to state-of-art approaches
which used HTML markup for generating test cases. We conducted a case
study for comparing the coverage obtained when executing the test cases
generatedbyourapproachandtestcasesgeneratedbyastate-of-artapproach,
CrawlJax.
TheCrawlJaxexecutionobtainedanaverageof35%coverage,whilethe
Morpheus Web Testing generated test cases averaged 41% coverage. The
results observed in the case study showed statistical differences between
both approaches, and thereby, bringing evidence to support the alternative
hypothesis H . One of the factors that contributed to the approach of the
1
Morpheus Web Testing achieved a coverage greater compared to CrawlJax,
occurred due to the use of the interface components XHTML in the process
ofgeneratingtestcasesthathavebeendefinedbytheJSFframeworktogether
withthecomponentsofPrimefacesinterface.
Separately analysing the layers of the web application used in the case
study,theDAOlayershowedhighersignificanceinthecoveragecomparison
betweenbothapproaches.Thefactorsthatdeterminedthisdisparitywasthat
whenidentifyingthepagecomponentsXHTML,theMorpheusWebTesting
approach synthesizes multiple test case input scenarios, while the CrawlJax
approachtriggersclicksaboutthelinksratherthannavigatingwithincomplex
widgetsorinsertingdifferentvaluesforforminputelements.
CrawlJax and WebMate use HTML markup for generating events that
are associated with each component. However, Morpheus Web Testing does
not use the markup generic of HTML, but as it is using the JSF XHTML
templates, there is more information than a HTML file. Given that in the
of Morpheus Web Testing analyses the WUI in a higher abstraction level,
through the XHTML template, we argue that it can identify menu or a
calendarwidget,whileotherapproachescanonlyidentifyaDIVoranINPUT
HTMLelement.Havingidentifiedamenu,WebTestingcanpredictatypeof
interaction that a div would not predict, such as: with a menu, it would be

## Page 19

MorpheusWebTesting 137
necessaryasimpleclick,withrightorleftbuttontoopenotheractions.Thus,
given we used complex widgets in the web application used in the case
study, Morpheus Web Testing was capable of identifying more states of the
application,achievingahighercoveragethanCrawlJax.
AutoBlackTest [14], uses two strategies to carry out the process of gen-
erating test cases (i) the use of a learning technique named Q-learnig, and
(ii) multiple heuristics to address some common cases such as: filling out
forms and file persistence. On the other hand, Morpheus Web Testing uses
the semantics of XHTML interface components in the test case generation
process. It shouldbe noted that, to effectivelycompare our work withAuto-
BlackTest [14], further experiments are required and could be realized in
futurework.
Crawljax and Morpheus tools still have room for improvement and that,
in future works we could link the generation of test cases using the types of
inputsgeneratedbyotherapproachesas(TheLink[24],AutoBlackTest[14]
and WebMate [6]) to in order to improve coverage, potentially improving
coverageinDAOandManagedBeanLayers.
Intheareaoftestcasegenerationforwebapplications,tworelatedstudies
(CrawlJax [23] and WebMate [6]) report the use of the structure HTML of
a web page to generate the test cases. HTML pages have a limited set of
interface components by default: text input, buttons, links, among others.
MorpheusWebTesting,ontheotherhand,wasimplementedtousecomplex
interface components (widgets) from JSF/Primefaces XHTML templates to
generate test cases. In these templates, interface components are specified
using higher level of abstraction definitions such as for example calendar
widget, inputs with validation fields, links and associated buttons to input,
amongothers.
In this work, we investigated whether the use of interface components
at a higher abstraction level such as menus could generate greater coverage
in test case generation strategies compared to the use of HTML interaction
elements.Our general research hypothesis was that, when a calendar widget
is identified, associated with a text field, specified in the XHTML template
withthePrimefacesframework,itispossibletopredictmoreelaboratelevels
of interaction (considering the relationship between components, validation
strategies,andmessagefields)comparedtoseparateidentificationofHTML
elements,withoutrelationshipbetweenwidgetlinksandinputsandnoiden-
tificationofvalidationstrategiesinXHTMLwiththePrimefacesframework.
Hence, we argue that using higher abstraction level WUI definition can
enhance the process of test case generation considering that: (i) get more

## Page 20

138 R.deAlmeidaNevesetal.
information than an HTML file and thus predict and improve component
interaction levels, and (ii) the ability to generate more functional test cases
andtherebyachievegreatercodecoverage.
In the Morpheus Web Testing approach, not all possibilities of interface
components have been exercised. The components that were considered
in the process of the test case generation process were: input with masks
and validation messages; calendar widget; checkbox, links, combobox, text
area, radio buttons. For each widget type, it has been established a set
of test cases many different possibilities of input, considering the mech-
anisms of the specific interaction of each widget and their integration in
the web application. Morpheus Web Testing focused the test case genera-
tion process for these widget, given they were the types of widget used in
ExactusCRM.
The technique used was the generation of input for test cases, within
this, the oracles were not generated, so the faults are not revealed, that
is, only the application is explored. In this case if we consider detecting
the number of failures identified by approaches, others study should be
carriedout.
Separately analysing the web application layers, can provide different
insights per layer. Crawljax and Morpheus use different software artifacts
for generating test cases, whereas Crawljax uses HTML and Morpheus
uses XHTML JSF templates. These artifacts are indirectly associated to
the widgets used in the UI of web applications and the user interaction
scenarios. In order to increase the coverage of the different layers, one
possiblescenariosisanalysingtest-casegenerationstrategiesforthedifferent
layers.
Our approach is a black box test case generation approach in which
test case generation is performed without having limited access to software
artifacts (we only evaluate XHTML template models). The goal of our tool
is to work with legacy systems (obsolescent platforms that have been in use
within a company for many years), assisting their refactor activities, even
whennoautomatedtestcaseswereimplementedforthem.
Thesystem(ExactusCRM)inwhichthetestswereperformedisasmall
size system with approximately (11Kloc), with this, the generation of test
cases was performed in around 1 minute. Generating test cases for other
applications would not be difficult, the execution as it is a selenium script
could take time. However there are options for accelerating the execution
timeofthesescripts,suchasrunningSeleniumdistributedinagridtotryto
optimizetheexecution.

## Page 21

MorpheusWebTesting 139
Finally, The time for executing both approaches was not analysed in
our study. However, the generation of the test cases for Morpheus take
(around 1 minute), considering the number of artifacts that composed our
project. The execution time, on the other hand, averaged 40 minutes for
both approaches, considering they run using the Selenium WebDriver API,
similarlytoSystem/Acceptancetestcases.
6 Conclusions
This paper presented a process for generating functional test cases for web
applications,thatusecomplexinterfacecomponentsintheprocessofgener-
ating test cases. Our approach was implemented in a tool, called Morpheus
Web Testing, and it was developed for identifying interface components in
JSF/Primefaces templates to automatically generate test cases. In terms of
the scope of the proposal, Morpheus Web Testing can be applied to any JSF
projectthatusesthePrimefacesframeworkforinterfacecomponents.
We evaluated our approach in a case study, in an industrial setting,
with a production JSF/Primefaces web application. The results indicate that
there is evidence that Morpheus Web Testing achieves greater code cov-
erage compared to state-of-the-art technique, because for all scenarios the
Morpheus Web Testing achieved better coverage on average. Although the
evaluation provided evidence that the approach outperforms state-of-the-art,
moreassessmentsneedtobecarriedouttogeneralizeourfindings.
Thecontributionsofthisworkwere:
• Implementing a test case generation strategy which identifies complex
interface components (widgets) and use their information to generate
moreelaboratetestcasesforwebapplications;
• Reducing costs associated to the testing process, in web applications
that use the JSF frameworks and Primefaces, specifically considering
theindustrialsettinginwhichMorpheusWebTestingwasused.
Thesuggestionsforfutureworkare:
• Extend the case study to other web applications to possibly further
generalizethefindingsofthispaper;
• Extend the case study to perform oracle generation in order to identify
thenumberofflawsidentifiedbytheapproaches;and
• Morpheus Web Testing focus on JSF/Primefaces web applications,
henceitsusageislimitedincomparissontoCrawlJaxwhichcanbeused
to any web application. Regardless, our approach for generating test

## Page 22

140 R.deAlmeidaNevesetal.
casesfromhigherabstractionleveldefinitions,suchaswidgets,couldbe
extendedtootherWidgetlibraries,suchasAngular,4React,5jQueryUI,6
amongothers.
Thelimitationsofthisworkare:
• Thecasestudywasconductedusingonlyoneapplication.WUIthatuses
theJSFandPrimefacesframeworks,inthiscasetheExactusCRMwith
11KLOC;
• Thecasestudywasconductedusingonlyonetooloffunctionaltestcase
generationsuchastheCrawlJax;
• The usefulness of the proposed tool is evaluated only in terms of the
coverageachievedbythegeneratedtestcases(faultdetectioncapability,
forexample,isnotconsidered);and
• In the Morpheus Web Testing approach, were not exercised all the
possibilitiesofinterfacecomponentsofframeworkPrimefaces.
References
[1] Pekka Aho, Nadja Menz, Tomi Ra¨ty, and Ina Schieferdecker. Auto-
mated java gui modeling for model-based testing purposes. In Infor-
mation technology: New generations (itng), 2011 eighth international
conferenceon,pages268–273.IEEE,2011.
[2] RobertVBinder.Testingobject-orientedsystems:models,patterns,and
tools.Addison-WesleyProfessional,2000.
[3] J Craig Cleaveland. Building application generators. IEEE software,
5(4):25–33,1988.
[4] KrzysztofCzarnecki,MichalAntkiewicz,ChangHwanPeterKim,Sean
Lau,andKrzysztofPietroszek.Model-drivensoftwareproductlines.In
Companion to the 20th annual ACM SIGPLAN conference on Object-
oriented programming, systems, languages, and applications, pages
126–127.ACM,2005.
[5] Valentin Dallmeier, Martin Burger, Tobias Orth, and Andreas Zeller.
Webmate:atoolfortestingweb2.0applications.InProceedingsofthe
WorkshoponJavaScriptTools,pages11–15.ACM,2012.
[6] Valentin Dallmeier, Bernd Pohl, Martin Burger, Michael Mirold, and
Andreas Zeller. Webmate: Web application test generation in the real
4http://www.angular.io
5https://reactjs.org/
6https://jqueryui.com/

## Page 23

MorpheusWebTesting 141
world. In Software Testing, Verification and Validation Workshops
(ICSTW),2014IEEESeventhInternationalConferenceon,pages413–
418.IEEE,2014.
[7] Ma´rcio Eduardo Delamaro, Jose´ Carlos Maldonado, and Ma´rio Jino.
Introduc¸a˜oaotestedesoftware.2007.
[8] Kit Edward. Integrated, effective test design and automation. Software
Development,21(2):36–38,1999.
[9] Mark Fewster et al. Common mistakes in test automation. In Proceed-
ingsofFallTestAutomationConference,2001.
[10] Zahra Abdulkarim Hamza and Mustafa Hammad. Web and mobile
applications’testingusingblackandwhiteboxapproaches.2019.
[11] Elisabeth Hendrickson. The differences between test automation suc-
cessandfailure.ProceedingsofSTARWest,1998.
[12] Cem Kaner. Improving the maintainability of automated test suites. In
InternationalSoftwareQualityWeek,1997.
[13] Ajeet Kumar and Sajal Saxena. Data driven testing framework using
selenium webdriver. International Journal of Computer Applications,
118(18),2015.
[14] Leonardo Mariani, Mauro Pezze`, Oliviero Riganelli, and Mauro San-
toro. Automatic testing of gui-based applications. Software Testing,
VerificationandReliability,24(5):341–366,2014.
[15] AtifMMemonetal.ComprehensiveFrameworkforTestingGraphical
UserInterfaces.UniversityofPittsburghPittsburgh,2001.
[16] Glenford J Myers, Tom Badgett, Todd M Thomas, and Corey Sandler.
Theartofsoftwaretesting,2004.
[17] Bao N Nguyen, Bryan Robbins, Ishan Banerjee, and Atif Memon.
Guitar: an innovative tool for automated testing of gui-driven software.
AutomatedSoftwareEngineering,21(1):65–105,2014.
[18] Roger S Pressman. Engenharia de software, volume 6. Makron books
Sa˜oPaulo,1995.
[19] AbdulRauf,SajidAnwar,MArfanJaffer,andArshadAliShahid.Auto-
mated gui test coverage analysis using ga. In Information Technology:
New Generations (ITNG), 2010 Seventh International Conference on,
pages1057–1062.IEEE,2010.
[20] AnaReginaCavalcantidaRocha,Jose´CarlosMaldonado,KivalChaves
Weber, et al. Qualidade de software: teoria e pra´tica. Sa˜o Paulo:
PrentticeHall,2001.
[21] Marton Sakal. Gui vs. wui through the prism of characteristics and
postures.Management,5(1):003–006,2010.

## Page 24

142 R.deAlmeidaNevesetal.
[22] IanSommerville.SoftwareEngineering.Pearson,10thedition,2015.
[23] EDC Van Eyk, WJ Van Leeuwen, Martha A Larson, and Felienne Her-
mans. Performance of near-duplicate detection algorithms for Crawl-
jax.PhDthesis,Citeseer,2014.
[24] Tanapuch Wanwarang, Nataniel P Borges Jr, Leon Bettscheider, and
Andreas Zeller. Testing apps with real-world inputs. In Proceedings of
theIEEE/ACM1stInternationalConferenceonAutomationofSoftware
Test,pages1–10,2020.
Biographies
RomulodeAlmeidaNeves.Agile,eXtremeProgramming,TDD,Hexagonal
Architecture,andFlutterenthusiast.Graduatedincomputerengineeringand
master in computing. Over 17 years of experience with the Java platform,
applicatonsservers,elaborationofarchitectures,back-endprojects,websolu-
tions, desktop, mobile, solution integrations using rest, soap, microservices,
usingproprietaryjavaproducts,JCPproducts,JakartaEEandSpringframe-
workproducts.
Willian Massami Watanbe. Ex-Yahoo!, Professor and Passionate Soft-
ware Engineer, with experience in development practices associated to Web

## Page 25

MorpheusWebTesting 143
technologiesandWebengineeringpractices(suchas:eXtremeProgramming,
TDD – Test-Driven Design, Continuous Integration and Continuous Deliv-
ery). Eager to contribute by developing quality assured Web applications,
alsoconsideringattributessuchasusability,maintenanceandmulti-platform
characteristicoftheWeb.
RafaelOliveira.IsaresearcherinSoftwareEngineeringandadjunctprofes-
sor – The Federal University of Technology – Parana´ – UTFPR. Interested
inresearchactivitiesassociatedwithplanning/implementingautomatedsoft-
waretestingsolutionsindifferentprojects,supportingcodereviewprocesses,
measuring change impact, planning and implementing testing frameworks,
maintaining testing scripts, and reports, supporting API, and manual testing
activities.

