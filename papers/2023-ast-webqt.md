# 2023-Ast-Webqt

**Source:** 2023-ast-webqt.pdf  
**Converted:** 2026-01-26 09:22:02

---

## Page 1

A Reinforcement Learning Approach to Generating
Test Cases for Web Applications
Xiaoning Chang†‡§∗, Zheheng Liang§ξ∗, Yifei Zhang†‡, Lei Cui§ξ, Zhenyue Long§ξ, Guoquan Wu†‡¶, Yu Gao†‡,
Wei Chen†‡, Jun Wei†‡, Tao Huang†‡
†State Key Lab of Computer Sciences, Institute of Software, Chinese Academy of Sciences, Beijing, China
‡University of Chinese Academy of Sciences, Beijing, China
§Joint Laboratory on Cyberspace Security, China Southern Power Grid, Guangzhou, China
ξGuangdong Power Grid, Guangzhou, China
†{changxiaoning17, gqwu, gaoyu15, wchen, wj, tao}@otcaix.iscas.ac.cn
†zhangyifei.steven@gmail.com, §liangzheheng@qq.com, §cuilei@gdxx.csg.cn, §zhenyue@undecidable.org
Abstract—Webapplicationsplayanimportantroleinmodern elements [3]. It is difficult to generate valid action sequences
society. Quality assurance of web applications requires lots of to reach diverse states. Any interruption when performing the
manual efforts. In this paper, we propose WebQT, an automatic
action sequence would fail to reach the target state. Existing
test case generator for web applications based on reinforcement
random-based approaches [4] randomly select actions and are
learning. Specifically, to increase testing efficiency, we design a
newrewardmodel,whichencouragestheagenttomimichuman prone to generate ineffective action sequences. Model-based
testers to interact with the web applications. To alleviate the approaches [5]–[7] first build a model for the target web
problem of state redundancy, we further propose a novel state application and then traverse the model to generate action
abstraction technique, which can identify different web pages
sequences. Since it is hard to build a complete model, these
with the same functionality as the same state, and yields a
approaches only generate limited action sequences. Recently,
simplifiedstatespace.WeevaluateWebQTonsevenopen-source
web applications. The experimental results show that WebQT reinforcementlearningapproachesarewidelyadaptedinauto-
achieves 45.4% more code coverage along with higher efficiency matic software testing [8], [9]. They design reward functions
than the state-of-the-art technique. In addition, WebQT also to train a policy to explore state space. However, their reward
reveals 69 exceptions in 11 real-world web applications.
functions are too simple to efficiently generate valid action
IndexTerms—Stateexploration,Reinforcementlearning,Soft-
sequences. As a result, these approaches cannot discover new
ware testing
deep states in the limited time.
I. INTRODUCTION Another challenge is that, web applications widely consist
ofnear-duplicatewebpages[10].Namely,webpagesreplicate
Web applications have become drastically increased over
functionality but their content and structure are different.
recent years. According to a recent survey [1], there are more
These web pages should be identified as the same state.
than1billionwebapplicationsinJuly2022.Onaverage,users
Otherwise, redundant states would degrade the state space
spend 7 hours per day online. It is important to develop web
exploration efficiency afterwards. However, a recent survey
applicationswithhighquality.Manual/automatedtestingtech-
[10] reveals that, existing approaches [4], [11], [12] that
nique can be used for quality assurance of web applications.
directly compare the content or structure of web pages fail
However, manual testing is time-consuming. Moreover, there
to identify near-duplicate web pages as the same state. In
is a large number of feasible action sequences for real-world
addition, computer vision-based approaches [9], [13] apply
web applications. Manual test cases can only cover a small
deeplearningtoidentifystates.Theseapproachesneedalarge
portion of them. Therefore, an automatic test case generation
numberofdatatotrainthemodel,whichrequirelotsofeffort.
tool is becoming an urgent need to ensure the quality of web
In this paper, we propose WebQT, an automatic test case
applications.
generation tool for web applications based on reinforcement
One challenge in automatic test case generation for web
learning.Itreliesonthereinforcementlearningagenttoselect
applications is that, some deep states can only be reached by
an optimal action, and then perform it on the target web
specific action sequences. For example, in web application
application. Based on the result of execution, WebQT updates
phoenix [2], only action sequence type username (cid:42) type
therewardtotheexecutedaction.Tobeabletogeneratevalid
password (cid:42) click login (cid:42) click Add-new-board (cid:42) type
actionsequenceseffectivelyduringtheexploration,wedesign
board-name (cid:42) click Create-board (cid:42) ... (cid:42) click edition
a novel reward model to guide the agent to mimic human
icon (cid:42) click Tags can reach color edition state. However,
testers to interact with web applications. After execution,
a web page may contain a large number of interactive UI
WebQT extracts state and valid actions from the web page.
To avoid state redundancy, our key observation to identify
*XiaoningChangandZhehengLiangcontributeequally.
¶GuoquanWuisthecorrespondingauthor. statesisthat,similarelementsonthepagewillservethesame

## Page 2

functionality. Based on this observation, we merge similar (a-c) in Figure 1, whose URLs are different and HTML
elementstorepresentoneuniquefunctionality.Webpageswith documents vary a lot, WebExplor would identify them as
similar functionalities are identified as the same state. different states.
To demonstrate effectiveness of WebQT, we evaluate We- To overcome this challenge, our intuition is that, similar
bQT on real-world web applications from three aspects. elements on the page will serve for the same functionality,
First, we compare WebQT and WebExplor [8] on a research and one of these similar elements can be utilized to represent
benchmark of 7 web applications. The experiment shows that the functionality. After simplification, web pages that provide
WebQT achieves 41.23% more branch coverage and 45.4% similar functionality can be identified as the same state. In
more line coverage than WebExplor. Second, we implement this way, our approach is able to identify web pages with
WebQT (i.e., WebQT with state extraction proposed by variousamountofsimilarfunctionalitiesasthesamestate.For
se
WebExplor) and WebQT (i.e., WebQT with reward model example,inFigure1(a),ourapproachidentifieselementsthat
r
proposed by WebExplor). The comparison between WebQT, representing title of news as similar elements and utilizes one
WebQT and WebQT demonstrates WebQT outperforms ofthem(i.e.,e inFigure1(d))torepresenttheirfunctionality
se r 3
WebQT andWebQT incoverageandefficiency.Third,we in the state. Similarly, we utilize element e to represent the
se r 4
evaluate WebQT on 11 real-world web applications randomly functionalityofpublisherofnews,andelemente torepresent
5
chosenfromtop50webapplications[14]intheworld.WebQT the functionality of link of full coverage in the state. As a
discovers 69 exceptions in 11 web applications. result, no matter how many news there are, we extract the
We summarize our main contributions as follows: same state, which is shown in Figure 1 (d). Note that, since
• We propose an automatic test case generation technique we do not take text into consideration, our approach is able
for web applications based on reinforcement learning. to identify web page with different content as the same state.
Specifically,anovelrewardmodelisdesigned,whichcan Statespaceexploration.Theaimofstatespaceexploration
guide the reinforcement learning agent to mimic human is two folds. On the one hand, the exploration strategy should
testers to efficiently explore the state space. be able to randomly explore the web application to cover
• To avoid state redundancy during the exploration, we diverse states. On the other hand, since some deep states can
design a new state abstraction technique, which can only be reached by specific action sequences, the exploration
identify different web pages with the same functionality strategy should be able to generate valid action sequences
as the same state. effectively. For example, for JPetStore web application [15],
• We implement our approach as WebQT and evaluate it inordertoreachcheckoutstate,thefollowingactionsequence
in real-world web applications. The experimental results shouldbeperformed:typeusername(cid:42)typepassword(cid:42)click
showsthatWebQTcaneffectivelyandefficientlygenerate login (cid:42) type keyword (cid:42) click search (cid:42) click a dog (cid:42) click
test cases for web applications. add to cart (cid:42) click checkout. However, according to existing
work[3],awebpagehas76actionsonaverage,makingithard
II. MOTIVATION
toefficientlygeneratevalidactionsequences.Anyinterruption
We regard automatic test case generation for web applica- when performing the action sequence would fail to reach the
tions as a problem of state space exploration. That is said, target state.
we aim to generate action sequences to reach diverse states Existing state space exploration techniques cannot achieve
of the web application under test. In order to achieve this above two goals at the same time. For example, random-
goal, we need to address two technical challenges: (a) how based approaches [4], [16] are able to randomly explore the
to represent and abstract the state for web applications to state space but hard to generate valid action sequences. In
avoid state redundancy problem and (b) how to design an model-basedtesting,modelcanprovideknowledgetogenerate
effective exploration strategy to reach more different states valid action sequences. However, existing approaches [5]–[7]
giving limited time budget. are hard to construct a complete model about the application
State Abstraction.Redundancywidelyexistsacrossdiffer- under test. Recently, researchers tend to adopt reinforcement
ent pages in web applications [10]. Namely, web pages repli- learning to test case generation for web applications [8], [9],
cate functionality but their content and structure are different. assuchtechniquecankeepabalancebetweenexplorationand
For example, Figure 1 (a-c) shows three of web pages, where exploitation. However, the designed reward function, which is
webpage(a-b)consistsoftwopiecesofnewsrespectivelyand the key to reinforcement learning, is too simple, and cannot
web page (c) consists of ten pieces of news (we only show guide the action selection effectively when multiple actions
threeofthem).Althoughwebpagesaredifferentfromcontent need to be performed sequentially to discover new states.
(i.e., web page (a) and (b)) and structure (i.e., web page (a) For example, in WebExplor [8], the reward function only
and (c)), they are conceptually same and should be identified considers the number of each transition in a state, and is hard
as the same state. Otherwise, there would be redundant states, to guide the generation of valid action sequences to expose
degrading the efficiency of state space exploration. some deep states of the application under test. To increase
However,existingworkscannotaddresssuchaproblem.For the effectiveness and efficiency of state space exploration, we
example, WebExplor [8] directly utilizes URLs and HTML observe that, if the reinforcement learning agent can mimic
documents of web pages to represent states. For web pages human interaction behavior with the application, it is able to

## Page 3

e html
1
Massive Snowfall Buries Cars, Keeps Failing … Elon Musk plays down influence of his tweets … Samsung’s 2022 Frame TV’sare Cheaper for …
The Associated Press 3 hours ago Financial Times 12 hours ago Engadget12 hours ago
View Full Coverage View Full Coverage View Full Coverage
All the Apple Back Friday Deals You Can Get … Glass bottles excluded from deposit return … Here Are The Best Black Friday Gaming Deals
MacRumors 8hours ago BBC 17 hours ago KotakuYesterday
View Full Coverage View Full Coverage View Full Coverage e 2 div
AMD Ryzen 9 5900X is 40 percent off on …
Notebookcheck.net2 days ago
View Full Coverage
… p li a
e e e
3 4 5
(a) (b) (c) (d)
Fig.1. Anexampleofwebpagesthathavedifferentcontentandstructurebuthavesamefunctionality.Webpage(a)and(b)havedifferentcontent,while
(a)and(c)havedifferentstructure.(d)isthestateextractedfrom(a-c).
1 2
state action
4 5
State State
state
web Extraction Identification reward
page
3 ns Reinforcement
webapplication acti o RewardModel Learning Agent
Action Extraction actions
test cases
Fig.2. TheoverviewofWebQT
efficiently generate valid action sequence. For example, after tolearnapolicyπ toselectactionsforstatespaceexploration
filling the text box, if the agent chooses to click the search (cid:186) (Section III-E).
button next to the text box, it will reach the product detail
A. State Extraction
state quickly, rather than clicking the homepage tablet far
from the text box. Motivated by this observation, we design a To explore the web application via reinforcement learning,
novelrewardmodel,whichnotonlyencouragestheactionfor we need to define the state representation. As each web page
whichtheexposedstateisworthexploring,butalsotheonefor is represented by a HTML document, a straightforward way
whichthegeneratedactionsequenceisconsistentwithhuman is to leverage HTML document representation of the page.
interaction behaviors. Under the guidance of the new reward However, adopting original HTML document as state directly
model, the reinforcement learning agent is able to effectively will suffer from the state redundancy problem as a large
generate action sequences to explore some deep states. number of pages will be generated during the exploration and
manyofthemonlydifferslightlyinthedocument.Toaddress
III. APPROACH
this limitation, we design a new state representation, defined
Figure 2 presents the overview of WebQT. Given a web as follows.
application, WebQT automatically generates sequences of ac-
Definition 1. A state s is a simplified HTML document tree
tions (i.e., test cases) to test the web application. When the
(V,E), where node e ∈ V represents a DOM element, and
target web application arrives at a web page, WebQT extracts
(e ,e )∈E representstheparent-childrelationship,inwhich
a state (cid:182) (Section III-A), and determines whether it is a 1 2
e is the parent of e .
previously visited state (cid:183) (Section III-B) to avoid redundant 1 2
states. Next, WebQT extracts valid actions from the web page In order to construct an abstract state from the original
(cid:184) (Section III-C). Then, the action previously performed on HTML document, we first reduce the number of elements in
the web application is evaluated by proposed reward model (cid:185) the document tree. We traverse the HTML document tree to
(SectionIII-D),estimatinghowmuchtheactioncontributesto remove element e if it only has one child element. Namely,
state space exploration. Based on extracted states and actions consider the parent element and child element of e is e and
p
along with reward, the reinforcement learning agent is trained e , respectively. We treat e as the child element of e . The
c c p

## Page 4

v e 1 html e 1 html e 1 html
e div e div buttone button e e button
2 3 4 4 4
e div e div e div e div e div
5 6 5 6 5
top li li li li li li li li li li li
e e e e e e e e e e e
7 8 9 10 11 7 8 9 10 11 7
(a) (b) (c) (d)
Fig.3. Anstateextractionexample,where(a)showsasimplifiedwebpagealongwithitsHTMLdocumenttree,HTMLdocumenttreeandextractedstate
shownin(b-d),respectively.
intuition is that, if element e only has one child element e , we continue to search similar elements among child elements
c
XPathofelemente containstheinformationaboutelemente. of e and e(cid:48). If child element e of element e is similar with
c c
In this way, the number of elements in the HTML document child element e(cid:48) of element e(cid:48), we add element e into state
c c
is reduced. s, and treat element e as the child element of e. Otherwise,
c
Then we further merge the similar elements, assuming that if there is no similar element among child elements of e and
similar elements will serve for the same functionality. In a e(cid:48), we add child element e of element e and child element
c
webpage,elemente ande aredeemedtobesimilar,ifthey e(cid:48) of element e(cid:48) as the child of element e into state s.
1 2 c
satisfy following conditions. Example. In Figure 3, (a) and (b) shows a simplified web
(1) They have similar structure. If XPath of page and its HTML document tree, respectively. To extract
e 1 and e 2 is tag 1 [p 1 ]/.../tag i [p i ]/.../tag n [p n ] and the state for web page (a), we first simplify its HTML
tag 1 [p 1 ]/.../tag i [p(cid:48) i ]/.../tag n [p n ] respectively, then we document tree. Element e 2 and e 3 corresponds to dotted box
consider element e 1 and e 2 has similar structure with each in (a), respectively. Since element e 2 and e 3 only has one
other, where p i (cid:54)= p(cid:48) i . Technically, given an element e, we child element respectively, we remove them from the HTML
take advantage of its XPath (by ignoring the index of its documenttreeandtreatelemente ande asthechildelement
5 6
ancestors in the path) to find all elements in the same layer of e . After removal of element e and e , the simplified
1 2 3
that have similar structures with e. HTML document tree is shown in (c). Then, we traverse
(2) They have similar style. The style similarity between the simplified HTML document tree to extract state s. Since
element e 1 and e 2 is defined as the distance between their element e 5 are e 6 similar in both structure and style, which
properties: corresponds to blue box in (a) respectively, we regard they
serve for the same functionality and add element e into state
5
sim(e ,e )= (cid:88) dist(e 1 [p],e 2 [p])·weight[p] (1) storepresenttheirfunctionalityinthestateshownin(d).Next,
1 2 |props| we continue to search similar elements among child elements
p∈props of e and e . We find that, element e is similar with element
5 6 7
where dist(e [p],e [p]) is the edit distance between prop- e ,e ,...,e in both structure and style, which corresponds
1 2 8 9 11
erty p of element e and e . We take property src, href, to green boxes in (a), respectively. Similarly, we add element
1 2
type,className,height,width,positionX andpositionY e into the state s to represent the functionality that elements
7
into consideration, as shown in Table I. The first row presents e ,e ,...,e serve for. In state s, element e is processed as
7 8 11 7
the way we calculate property distance: (i) For property src, thechildelementofe .Forelemente ,sinceithasnosimilar
5 4
href and className, whose values are strings, we calculate element, we reserve it in the state. The extracted state from
property distance by edit distance between them [17]. (ii) For web page (a) is shown in (d).
property height, width, positionX and positionY, whose
values are number, we calculate ratio of them as the property
B. State Identification
distance. (iii) For property type, if property type of two
elements are same, the property distance is 1. Otherwise, the ToavoidduplicatestatesinthestatespaceS,wedetermine
property distance is zero. The second row of Table I shows whether the extracted state s is a previously visited state. If
weights of property distances. thereisnostateinthestatespaceissamewithstates,weadd
If the style similarity is greater than our predefined thresh- state s into the state space. Otherwise, if state s(cid:48) ∈S is same
old, we consider they have similar display styles. withstates,weconsiderstatesapreviouslyvisitedstate,and
Next,weperformthebreath-firsttraversalonthesimplified do not add state s i into the state space.
treetoextractthestate.Forelemente,ifithassimilarelement The basic strategy is to compare s with each state s(cid:48) ∈ S
e(cid:48), we assume they serve for the same functionality, and add one by one. However, to compare state s and s(cid:48), all elements
one of them into state s to represent the functionality. Next, ofstatesneedstobecomparedwithelementsofstates(cid:48).Itis

## Page 5

TABLEI
STYLESIMILARITYCOMPUTATION
property src href type className height weight positionX positionY
type str str specified str number number number number
weight 0.62 0.62 0.5 0.45 0.1 0.1 0.1 0.1
time-consuming to compare state s with all states in the state e AB e C
1 8
space.
To address this problem, we observe that, given a web e 2 A e 3 AB B e 4 e 9 C
application A, states of A share a number of elements. Based
on this observation, given states s 0 ,s 1 ,...,s n−1 ∈ S, we e 5 A e 6 A B e 7 e 10 C C e 11
build a state index tree, which consists of all elements and
edges of existing states s ,s ,...,s . We compare s with (a) (b)
0 1 i−1
stateIndexTree to determine whether there is a state s(cid:48) ∈S
that is same with state s , i.e, whether s is newly visited. Fig.4. Anexampleofstateidentification.(a)presentsastateindextreebuilt
We first label elements of state s. The label on an element
bystatesa ands b,whereelementslabeledbyA(orB)belongtostatesa
(orstates b).(b)presentsastatesc.
e will be used to identify the state that element e belongs to.
Then, we get state index tree of existing states. If no state label C and initialize the number of similar elements between
index tree has been built, we regard state s as the state index state s (and state s ) and s to zero. Then, we compare root
a b c
tree, and there is no state that is the same with state s. If state element e of state s with root element e of the state index
8 c 1
index tree stateIndexTree exists, we compare state s with tree.Elemente issimilarwithe .Sinceelemente belongsto
8 1 1
stateIndexTree to determine whether there is a same state state s , we increase the number of similar elements between
a
with state s as follows. state s and s by 1. Since element e also belongs to state
a c 1
We initialize that the number of similar elements between s , the number of similar elements between s and s is also
b b c
state s and each state s(cid:48) ∈ S to zero. Then, we perform pre- increased by 1. We continue to compare child elements of
ordertraversalonstatesandstateindextreestateIndexTree. e and e . We find that, element e of state s is similar
8 1 9 c
Suppose element u in state s is similar to element v in with element e . Again, we increase the number of similar
3
stateIndexTree.Accordingtothelabelofelementv,element elements between state s (and state s ) and s by 1. Next,
a b c
v belongs to the set of states B, then the number of similar wecomparechildelementsofe ande .Elemente issimilar
3 9 10
elements between state s and s(cid:48) ∈B is increased by one. We with element e , which belongs to state s , while element e
6 a 11
also add label of state s on element v. Next, we continue to has no similar element among child elements of element e .
3
find similar elements for each child elements of element u, Therefore, state s has three similar elements with state s
c a
among the children of element v. Otherwise, if there is no (i.e., e , e and e ), and stateSim(s ,s )=3/min(5,4)=
8 9 10 a c
similar element with u in stateIndexTree, we add element 0.75. State s has two similar elements with state s (i.e., e
c b 8
u and its descendants into stateIndexTree. and e ), and stateSim(s ,s )=2/min(4,4)=0.5.
9 b c
Based on the number of similar elements between state s
C. Action Extraction
and state s(cid:48), we calculate state similarity stateSim between
state s and s(cid:48), which is defined as Definition 2. An action a in our approach is defined as a=
(ele,type[,param]),whereeleistheinteractableelementthat
#similarNum a operates on, type is the type of a. In particular, if action
stateSim(s,s(cid:48))= (2)
min(#s,#s(cid:48)) a is of type input, type form-fill or select, action a has input
value param.
where #similarNum is the number of similar elements
between state s and s(cid:48). #s and #s(cid:48) denotes the number of Ourcurrentapproachsupportstheactiontypes:click,input,
elements of state s and s(cid:48), respectively. Note that, since we selectandform-fill,whicharecommonactionsinmodernweb
compare states and state index tree in pre-order traversal, we applications. In particular, type form-fill is specific to form
also take the structure of similar elements into consideration. elements. More types of actions can be integrated into our
If similarity between state s and s(cid:48) is larger than our approach in the future.
predefined threshold between states threshold, we regard s We traverse the HTML document tree to check whether
and s(cid:48) are the same state. element e is interactable. If yes, we generate an action a that
Example. Figure 4 (a) presents a state index tree built by accesses to element e as follows:
state s a and s b , where elements labeled by A (or B) belong • Iftagofematchesourdefaultconfiguration,weconsider
to state s (or state s ). Figure 4 (b) shows the state s . We elementeisinteractableandgenerateanactionforit.Our
a b c
comparestates withthestateindextreetodeterminewhether configuration is depicted in Table II. For example, if tag
c
state s is a new state. We first label elements of state s by of element e is a, we generate an action of type click
c c

## Page 6

TABLEII • Attention of action. Human is prone to perform actions
ACTIONEXTRACTION on elements that newly appear at the current state. For
example, a pop-up menu appears on the new state after
a button input textarea form fieldset select
performinganaction.Comparedtootherelementswhich
√ √
click √ √ already exist in the previous state, human testers tend
input
√ √ to be more attracted by newly appeared elements, and
form-fill
√
select choose to click items on the pop-up menu.
• Frequency of action. In a state, if an action is less to
be chosen in the past compared to other actions, more
on element e. Specially, if tag of element e is form or chance should be given to this action to reach diverse
formset, we generate form-fill actions on it. states during the exploration.
• If tag of e is input or textarea and e.type ∈ • Proportion of unexecuted actions. If a state has more
{radio,label,checkbox},weconsiderelementeisclick- actions that have not been executed after performing an
able and generate an action of type click on element e. action, it is more worthy to encourage this action as new
• If tag and className of e matches user configuration, states may be exposed when reaching such a state.
we consider element e is interactable and generate an
Reward indicator.Basedonaboveobservations,wedefine
actionforelemente.Forexample,iftagandclassName
reward indicators calculated after performing each action.
ofelementeisdiv andsubmitrespectively,wegenerate
After execution of action a , the action sequence is as =
i
a clickable action for it. (cid:104)a ,...,a (cid:105), which makes state transition sequence s − a →1
0 i 0
We provide values for actions of type input as follows s − a →2 s ...s − a →i s , we define:
1 2 i−1 i
[4]. First, we obtain values from user configurations so that (1) r : this reward based on the locality of action a .
loc i
our approach can reach certain states. For example, we need Consider element e and e , which are accessed by action
i−1 i
users to provide username and password to login. Second, if a and a , respectively. We encourage the agent to select
i−1 i
users do not provide custom values, we randomly generate action a so that element e is near to element e in the
i i i−1
values. Specially, for element e accessed by action, if type page.Ifsizeofelemente ore islarge,thespatialdistance
i−1 i
of e is email, we randomly generate an email value. In a betweenelemente ande islarge,evenifthesetwoelement
i−1 i
word, since input values can affect test procedure, we explore are next to each other. In order to ease the impact caused by
normal and exceptional states by valid input values (i.e., user- size of elements, we define r as:
loc
configured values) and invalid input values (i.e., randomly
generated values). As for form-fill action that accesses to the (cid:112)
(h(e )+w(e ))∗(h(e )+w(e ))
form element f, we generate values for each action of type r = i−1 i−1 i i (3)
loc dist(e ,e )
inputthataccessestoelementinsideformf.Asfortheaction i−1 i
of type select on element e, whose tag is select, we process whereh(e)andw(e)representsheightandwidthofelement
the option tag inside the element e and randomly choose one e, respectively. dist(e ,e ) is the Levenshtein distance [17]
i−1 i
of available options as input value. between element e and e .
i−1 i
(2) r : this reward based on the attention of action
D. Reward Model attention
a . Human is more likely to perform an action on the mutant
i
WeadaptreinforcementlearningalgorithmQ-Learning[18]
element (e.g., newly added elements) that appears at state s
i
to generate test cases to explore the state space. A key to
butdoesnotexistatstates .Therefore,wedefiner
i−1 attention
reinforcementlearningisarewardmodel,whichcanoptimize
as:
policy π so that WebQT can reach diverse states efficiently.
Whendesigningtherewardmodel,wehavethefollowingtwo
(cid:26)
1/mutants(s ) isMutant(e )
aims: (a) the reward model should guide WebQT to reach r = i i (4)
attention 0 otherwise.
diverse states during the exploration. (b) the reward model
should encourage WebQT to interact with the application Namely, if element e accessed by action a is a mutant
i i
like human, which can generate valid action sequences to element at state s , action a is rewarded by 1/mutants(s ),
i i i
cover more deep states. To achieve the above two goals, we where mutants(s ) is the number of newly appeared action-
i
manually explore web applications and obtain the following ableelementsins .Thisrewardvalueisinverselyproportional
i
observations, which constitute the basis of our reward model: to the number of mutants in s . If the number of mutants in
i
• Action locality. Human usually selects actions located in s i is large, a small value will be given to a i .
the same area because these actions usually serve for the To guide WebQT to generate test cases with diversity, we
same functionality of web applications. For example, in define the following reward indicators:
order to search for a product, human fills the text box (3) r : this reward based on the execution frequency
freq
and then click the search button next to it, rather than of transition (s ,a ,s ). If transition (s ,a ,s ) has been
i−1 i i i−1 i i
clicking ”About us” link at the bottom of the web page executed many times, we assign a small reward r to it,
freq
after entering keyword in the text box. which is defined as:

## Page 7

Algorithm 1: State space exploration
1
r freq = √ (5) Input: env (the target web application)
N
i Hyperparameter: N (the number of episodes), M
where N i is the execution number of transition (the number of step in each
(s i−1 ,a i ,s i ). episode)
(4) r explore : the degree of exploration of state s i . After Output: T (test cases)
execution of action a i , the web application transits to state 1 get url of target application env;
s i . If state s i has a large portion of valid actions that have not 2 T ←∅,π ←∅,S ←∅;
been executed, action a i contributes to state exploration and 3 for e←1;e≤N;e++ do
we reward it by r explore , which is defined as: 4 reset(env);
n 5 s 0 ,actions←extract(p 0 );
r explore = m i (6) 6 as←∅;
i 7 for i←1;i≤M;i++ do
where m and n denotes the number of executable actions
i i 8 select action a i at state s i−1 ;
at state s and the number of actions that have not been
i+1 9 p i ←env(a i );
executed at state s , respectively.
i 10 s i ,actions←extract(p i );
Reward function. Based on reward indicators, we define a 11 update S by s i ;
reward function r i (a i ) as: 12 r i ←reward(s i−1 ,a i ,s i );
13 update π using s i−1 ,a i ,s i and r i ;
(cid:26)
r (a )= penalty if ext(s i ) or s i =s i−1 , (7) 14 as.push(a i );
i i r i (cid:48)(a i ) otherwise. 15 end
16 T.push(as);
If the web application transits to external link (denoted as
17 end
ext(s )) or state s is same with state s (denoted as s =
i i i−1 i 18 return T;
s ), then we assign a negative reward for such a transition,
i−1
i.e., penalty < 0. Otherwise, we assign a positive reward
r(cid:48)(as) calculated by:
the policy via function Q : S ×A → R, where Q(s ,a )
i−1 i
r i (cid:48)(a i )=w loc ∗r loc +w attention ∗r attention (8) estimates how good it is to perform action a i at state s i−1 .
w ∗r +w ∗r After state transition from s to s by performing action
freq freq explore explore i−1 i
a , reward r is calculated by Equation 7, and function Q is
wherew >0,w >0,w >0andw > i i
loc attention freq explore updated by:
0 are weights, which are determined by several tests in the
experiment.
Q(s ,a)←Q(s ,a)+α(r +γQ∗(s,a )−Q(s ,a)) (9)
E. Reinforcement Learning Agent i−1 i i−1 i i i i+1 i−1 i
Inthissection,weillustratehowourapproachexploresstate where Q∗(s ,a ) is the maximum cumulative reward can
i i+1
space,asshowninAlgorithm1.Givenatargetwebapplication be achieved from state s . As we can see in this equation,
i
env,wefirstretrievetheURLofitshomepage,i.e.,url (Line future cumulative reward is discounted by factor γ ∈ [0,1].
1) and initialize the set of test cases T, policy π and state α∈[0,1] is the learning rate.
space S (Line 2). WebQT runs N episodes to train policy π. Different from traditional reinforcement learning applica-
At the beginning of each episode, the target web application tions, the action space of web applications is large, making
is reset by visiting its homepage page p via url (Line 4). it hard to select an action that contributes to state space
0
WebQT extracts state and executable actions from web page exploration. In order to overcome this challenge, we design
p (Line 5). following strategies, in addition to reward model.
0
WebQT is allowed to try M steps to generate action se- (cid:15)-greedy algorithm. We adapt (cid:15)-greedy algorithm to keep
quenceasduringeachepisode(Line7).Ineachstep,WebQT balancebetweenexplorationandexploitation.Beforeselecting
selectsactiona atstates (Line8).Afterperformingaction anactionat state s ,WebQTfirst computesarandomvalue
i i−1 i−1
a , the web application is directed to the web page p (Line k ∈ [0,1]. If k is no less than (cid:15), WebQT makes exploitation:
i i
9), from which WebQT extracts state s along with the set of action with maximum Q value is selected. Otherwise, WebQT
i
valid actions actions (Line 10). Then, WebQT updates state makes exploration: WebQT randomly selects one of valid
spaceS bys (Line11).Therewardr iscalculatedforaction actionsatstates .Withtheincreasingnumberofepisodes,(cid:15)
i i i−1
a (Line 12). Based on s ,a ,s and r , policy π is update isdecaying,WebQTswitchesfromexplorationtoexploitation,
i i−1 i i i
(Line 13). Finally, act a is added into action sequence acts and action with maximum Q value is more likely to be
i
(Line 14). selected.
Inordertotrainthepolicyπ,ourapproachadaptsreinforce- Form-fill actions. Form elements are widely used in web
ment learning algorithm Q-Learning [18]. Q-Learning trains applications.However,itisdifficultfortheagenttofillaform.

## Page 8

Our approach computes a shortest path from state s to state
a 0
3 s on state graph via Dijkstra algorithm [19] and the web
min
s a 1 s a 2 s s a 5 s applicationexecutescorrespondingactionstoreachstates min .
0 1 2 3 4
a 4 IV. EVALUATION
Fig.5. Anexampleofstatetransition,whereknownandunknownstatesare We have implement WebQT based on Node.js and Python
denotedbysolidanddottedcirclesrespectively. 3.7 with more than 20,000 lines of code. In order to demon-
strateourapproach,ourevaluationanswersfollowingresearch
Accordingtothework[3],inmodernwebapplications,aweb
questions:
pagecontains76actionsonaverage.Foraformconsistedof5
textboxes,thepossibilityofrandomlyfindingacorrectaction • RQ1: How is the exploration ability of WebQT in terms
sequence to fill the form is 1/(76)5 =10−10. of code coverage, compared with WebExplor [8], the
To address above challenge, we identify form-fill actions state-of-the-art web testing tool based on reinforcement
on form elements, as discussed in Section III-C. If the agent learning?
selects a form-fill action on form element f, our approach • RQ2: How effective is proposed state extraction and
fills all input elements in the form element f. For example, identification method? How effective is proposed reward
in the login page, we fill the username text box and password function?
text box. In this way, we increase the possibility of finding a • RQ3: How effective is WebQT in testing real-world web
correct action sequence on f. applications?
Local optima. Although we apply (cid:15)-greedy algorithm to
keep balance between exploration and exploitation, it is still A. Experiment Setup
challenging for reinforcement learning to achieve effective
exploration.Forexample,inFigure5,actona withmaximum Dataset. To answer research question RQ1 and RQ2, we
3
Q value is selected at state s . After execution of acton a , utilize web applications in existing works [5], [8], [9]. One of
2 3
states transitstostates .Similarly,actona withmaximum these application, pagekit, cannot be instrumented. Applica-
2 3 4
Qvalueisselectedatstates ,andstates transitstostates . tions gadael, mean-blog and webogram are not maintained
3 3 2
Next, acton a is selected and state transits to s . We regard and cannot be built. We also include two web application
3 3
the phenomena, where no new state is explored, as a local management and management from GitHub. In total, we
optima. perform our evaluation on 7 web application. We instrument
Inordertoovercometheproblemoflocaloptima,wecheck each web application by nyc [20]. To answer RQ3, we
whether the agent is trapped in the local optima before action randomly select 11 real-world web applications from top 50
selection. Consider the acton sequence as = (cid:104)a ,...,a (cid:105). web applications according to [14]. In order to demonstrate
1 n
If there is no new state in recent window of size Z (i.e., scalability of WebQT, we directly perform WebQT on these
there is no new state among state s ,s ,...,s ), web applications without fine-tuning.
n−Z+1 n−Z+2 n
we consider that the agent is strapped in the local optima. Configuration.ToanswerresearchquestionRQ1,weselect
We propose two strategies to make our agent jump out of state-of-the-art testing tool WebExplor [8] as baseline, which
local optima. If the state where agent is trapped has more has been proved in existing works [8], [9]. We perform
than one valid action, our approach selects actions from valid WebQT and WebExplor on each web application five times
actionsexcepttheactionwithmaximumQvalue.Forexample, and measure average branch and line coverage. To answer re-
inFigure5,whenstrappedatstates ,theagentselectsaction search question RQ2, we implement following two baselines:
3
a andtransitstonewstates toescapelocaloptima.Different (a) WebQT : extract and identify states by URLs and tag
5 4 se
from existing work that ends current episode immediately sequences and equipped with other components of WebQT;
when trapped in the local optima [8], we find that states (e.g., (b) WebQT : replace reward model component of WebQT
r
states )behindthelocaloptimaneedtobeexplored.Stopping with the one of WebExplor. We compare WebQT with above
4
current episode makes it hard to explore states behind local two baselines and measure line coverage. In all experiment,
optima. we set a time budget for each tool, i.e., 15 minutes. We
Second, if the state where agent is trapped only has one set DOM element similarity threshold and state similarity
valid action (i.e., the action with maximum Q value), our threshold is 0.8 and 0.85, respectively. Reward weights are
approach ends current episode and search for the transition set as follows: w = 10, w = 50, w = 5 and
loc attention freq
with lowest execution times, denoted as s a −m→in s . w = 5. Hyperparameter M and N is set to 10000
min−1 min explore
State s is the beginning of the new episode. Our intuition and 100, respectively. Since similarity thresholds and reward
min
is that, putting WebQT at a different state, which has been indicatorweightsareimportanttoourapproach,wedetermine
visited much less, can increase the possibility to exploring them by several tests. Hyperparameters are not optimized. In
diverse states. To achieve this goal, we build a state graph, order to avoid threats introduced by above parameters, these
whosenodesarestatesandedgesaretransitionsamongstates. parameters are set equally in each tool.

## Page 9

TABLEIII TABLEIV
CODECOVERAGERESULT EVALUATIONONREAL-WORLDWEBAPPLICATIONS
Branchcoverage Linecoverage App Client Server Total
App
E Q E Q
www.qq.com 2 3 5
timeoff[21] 13.98% 39.87% 6.54% 48.27% www.tmall.com 4 7 11
dimeshift[22] 14.72% 39.17% 18.94% 46.31% www.baidu.com 5 1 6
splittypie[23] 7.69% 45.16% 32.95% 64.67% www.taobao.com 3 1 4
phoenix[2] 22.37% 69.74% 24.25% 79.10% www.sohu.com 1 8 9
hospital[24] - 30.97% - 82.35% www.bing.com 4 1 5
retroboard[25] 22.81% 60.23% 58.19% 83.82% www.amazon.com 8 4 12
petclinic[26] 0% 85.00% 41.67% 95.83% www.ebay.com 0 1 1
Average 11.65% 52.88% 26.08% 71.48% www.aliexpress.com 1 6 7
www.360.com 6 0 6
www.reddit.com 3 0 3
Total 37 32 69
B. The Ability of Exploration
TheresultofcoveragecomparisonbetweenWebExplorand
WebQTisshowninTableIII,wherecolumnE andQdenotes example, in application phoenix, there is a page transition
WebExplorandWebQT,respectively.SinceWebExplorcannot sequence:homepage→my-boards→board-list→new-board
performonapplicationhospital,wedenotecoveragemeasured →board→edit-board-infopage.Onlyvisitingedit-board-info
on it as -. As shown in Table III, WebQT performs better canincreasecoverage.Anyinterruptionleadingtoanotherweb
than WebExplor. After running 15 minutes, WebQT achieves pages during such a transition sequence degrades exploration
41.23% more branch coverage and 45.4% more line coverage efficiency. Since WebQT is prone to accesses to actions that
than WebExplor on average. The results shows WebQT better newly appear in the current page, e.g., clicking edition icon
exploration ability on web applications, compared with state- in board page, it increases the possibility to explore diverse
of-the-art testing tool WebExplor. pages.
C. Effectiveness of State Extraction Identification E. Scalability
We demonstrate how effective state extraction and iden- Inthissection,wedemonstratethescalabilityofWebQTon
tification method is by comparing WebQT with WebQT . real-world web applications. We perform WebQT on 11 web
se
The result is shown in Figure 6, where the x-axis and y- applications randomly selected from top 50 web applications
axisrepresentsthetestingtimeandlinecoverage,respectively. [14] and catch exception message in the console. As a result,
Note that, some actions, e.g., clicking ”Sales” that transits WebQTdiscovers1,091exceptions.Wemanuallyinspectthese
applicationtimeoff fromemployee-calendarpagetoteam-view exceptions and find most of them are duplicate. For example,
page, can trigger much code and thus causing the sudden when the connection is reset, multiple exceptions is reported.
increasing of line coverage in the figure. Afterfilteringduplicateexceptions,weobtain69exceptionsin
As shown in Figure 6, WebQT achieves higher exploration total, as shown in Table IV, where column Client and Server
efficiency than WebQT (i.e., red line arises faster than blue denotes the number of exceptions found in client and server
se
line). As discussed in Section II, existing approaches cannot side, respectively.
tolerate redundancy in web applications and causes redundant As shown in Table IV, we find exceptions can happen
states, which degrades exploration efficiency. In addition, in in both client side and server side. In addition, we reveal
our evaluation, we find that, with the increasing number of a wide range of exceptions, including net related errors,
states, it is possible for state extraction by tag sequences resource loading errors, cross-domain errors and JavaScript
to incorrectly treat two different states s and s as the errors, which demonstrates the scalability of WebQT.
a b
same state. This is because only taking tag sequences into
F. Threats to Validity
consideration loses too much information of web pages to
identify states. Consequently, at state s , WebQT chooses Representativeness of our studied web applications. We
b se
to perform the action that is executable at state s but non- select a number of web applications to demonstrate effective-
a
executable at state s . As a result, WebQT (blue line) ness of WebQT in our evaluation. First, these experimental
b se
achieves lower line coverage than WebQT (red line). projectscomefromreal-wordwebapplications.Second,these
applications have been widely used in existing works [5], [8],
D. Effectiveness of Reward Model
[9]. Therefore, we believe our studied web applications are
We demonstrate how effective reward model is by compar- representative.
ing WebQT with WebQT . The result is shown in Figure 6. Evaluation configuration. Randomness can threat validity
r
Compared with WebQT , our approaches benefits WebQT of our evaluation. We alleviate this threat by repeating five
r
in two aspects. First, compared with WebQT (black line), runs for each tool. Another threat is the measurement of our
r
WebQT achieves higher exploration efficiency (i.e., red line evaluation. WebQT is a black-box testing approach and we
arises faster). Second, WebQT achieves higher coverage. For cannot access to the server-side code. Therefore, we only

## Page 10

W
W
e
e
b
b
Q
Q
T
Tse
W
W
e
e
b
b
Q
Q
T
Tse
W
W
e
e
b
b
Q
Q
T
Tse
W
W
e
e
b
b
Q
Q
T
Tse
WebQTr WebQTr WebQTr WebQTr
(a) timeoff (b) dimeshift (c) splittypie (d) phoenix
W
W
e
e
b
b
Q
Q
T
Tse
W
W
e
e
b
b
Q
Q
T
Tse
W
W
e
e
b
b
Q
Q
T
Tse
WebQTr WebQTr WebQTr
(e) hospital (f) retrosboard (g) petclinic
Fig.6. EvaluationofWebQT,Webse andWebQTr regardingcodecoverage.
collect client-side code coverage, which is a common practice onAndroidapplications[7],[32]–[39].However,modelbased
in existing works [5], [8], [9]. Finally, we only monitor approaches are neither complete nor sound.
exception messages and do not take other types of failures Reinforcement learning based test case generation. Re-
into consideration. Other types of failures detection can be cently, reinforcement learning is applied to software testing.
integrated into WebQT in the future. For example, at the same time winning the game, Wuji [40]
State identification. Our approach depends on similarity explores the state space of the game. QTesting [13] leverages
thresholds to determine whether two states are same. It is LSTM to divide scenarios with different functionalities and
possible to identify a state as a new state incorrectly, intro- adoptsQlearningalgorithmtogeneratetestcasesforAndroid
ducing state redundancy. To alleviate this threat, we optimize applications.Similarly,UniRLTest[9]utilizesCNNtoidentify
thresholds by several tests. As a result, WebQT still separates states and interactable actions, and adopts DQN to generate
states in much scenarios and thus increasing the efficiency testcasesforbothwebapplicationsandAndroidapplications.
of state space exploration, as demonstrated in the evaluation. WebExplor[8]generatestestcasesforwebapplications,which
Moreover, since test cases generated by state-of-the-art tool identifies states by URL and tag sequences without tolerance
WebExplor [8] are less diverse than ours, it is unfair to ofredundancy.Consequently,ityieldsthelargestatespaceand
compare states identified by these two approaches. Therefore, degradestheexplorationefficiency.Inaddition,itinefficiently
we do not conduct such an evaluation. explores state space only under the guidance of the number
of executions. On the contrary, our approach design a novel
V. RELATEDWORK
reward model to guide the agent to generate human-like test
Random based test case generation. Random based ap- cases with high efficiency, as demonstrated by our evaluation.
proaches [4], [16], [27] analyze candidate actions and ran-
domly execute one of them. Although they have been widely
VI. CONCLUSION
adopted, they are prone to generate invalid test cases, e.g., Web applications are increasingly popular and greatly im-
filling values in buttons. In addition, since they are often in- pact our daily life. However, it is challenging to maintain
terruptedbytherandomlyselectedaction,theyhardtoexplore web applications with high quality. In this paper, we propose
states that can only be reached by valid action sequences. WebQT, an automatic test case generator for web applications
Model based test case generation. Model based ap- based on reinforcement learning. Specifically, we present a
proaches[6],[28]–[30]firstdynamicallyorstaticallybuildthe new state abstraction technique to avoid state redundancy,
modeltodepictbehaviorsofthetargetwebapplication.Then, and design a novel reward model to encourage reinforcement
theydesignstrategiestosearchpathsonthemodeltogenerate learning agent to mimic human behaviors to explore the state
test cases. For example, SubWeb [6] leverages Page Object space. We evaluate WebQT on real-world web applications
[31] defined by developer to build the navigation model, and and experimental results show it outperforms state-of-the-art
designs a set of genetic operators to generate test inputs tool with higher effectiveness and efficiency.
and feasible navigation paths. DIG [28] pre-selects the most
promising candidate test cases based on their diversity from
VII. ACKNOWLEDGE
previously generated test cases. FragGen [30] ranks actions, This work was partially supported by National Natural Sci-
and chooses the next state based on the total score of actions ence Foundation of China U20A6003, China Southern Power
ineachstate.Modelbasedapproachesarealsowidelyapplied Grid Company Limited under Project 037800KK52220005.

## Page 11

REFERENCES [23] “Splittypie,” 2022. [Online]. Available: https://github.com/
matteobiagiola/FSE19-submission-material-DIG/tree/master/fse2019/
[1] “Web server survey,” 2022. [Online]. Available: https://news.netcraft.
splittypie
com/archives/2022/07/28/july-2022-web-server-survey.html
[24] “Hospital-management-nodejs,” 2022. [Online]. Available:
[2] “Phoenix,”2022.[Online].Available:https://github.com/matteobiagiola/
https://github.com/matteobiagiola/FSE19-submission-material-DIG/
FSE19-submission-material-DIG/tree/master/fse2019/phoenix
blob/master/fse2019/dimeshift/README.md
[3] Y. Li and O. Riva, “Glider: A reinforcement learning approach to
[25] “Retroboard,” 2022. [Online]. Available: https://github.com/
extractUIscriptsfromwebsites,”inProceedingsofInternationalACM
matteobiagiola/FSE19-submission-material-DIG/tree/master/fse2019/
Conference on Research and Development in Information Retrieval
retroboard
(SIGIR),2021,pp.1420–1430.
[26] “Petclinic,” 2022. [Online]. Available: https://github.com/
[4] A. M. andArie van Deursen and D. Roest, “Invariant-based automatic
matteobiagiola/FSE19-submission-material-DIG/tree/master/fse2019/
testing of modern web applications,” IEEE Transactions on Software
petclinic
Engineering(TSE),vol.38,no.1,pp.35–53,2011.
[27] A.Mesbah,A.vanDeursen,andS.Lenselink,“Crawlingajax-basedweb
[5] M.Biagiola,A.Stocco,F.Ricca,andP.Tonella,“Diversity-basedweb
applicationsthroughdynamicanalysisofuserinterfacestatechanges,”
testgeneration,”inProceedingsofJointMeetingonEuropeanSoftware
ACMTransactionsontheWeb(TWEB),vol.6,no.1,pp.1–30,2012.
EngineeringConferenceandSymposiumontheFoundationsofSoftware
[28] M.Biagiola,A.Stocco,F.Ricca,andP.Tonella,“Diversity-basedweb
Engineering(ESEC/FSE),2019,pp.142–153.
testgeneration,”inProceedingsofJointMeetingonEuropeanSoftware
[6] M.Biagiola,F.Ricca,andP.Tonella,“Searchbasedpathandinputdata
EngineeringConferenceandSymposiumontheFoundationsofSoftware
generationforwebapplicationtesting,”inProceedingsofInternational
Engineering(ESEC/FSE),2019,pp.142–153.
SymposiumonSearchBasedSoftwareEngineering(SSBSE),2017,pp.
[29] T.Su,G.Meng,Y.Chen,K.Wu,W.Yang,Y.Yao,G.Pu,Y.Liu,and
18–32.
Z.Su,“Guided,stochasticmodel-basedGUItestingofAndroidapps,”
[7] T.Su,G.Meng,Y.Chen,K.Wu,W.Yang,Y.Yao,G.Pu,Y.Liu,and
in Proceedings of Joint Meeting on European Software Engineering
Z.Su,“Guided,stochasticmodel-basedGUItestingofandroidapps,”in
ConferenceandSymposiumontheFoundationsofSoftwareEngineering
Proceedings of Joint Meeting on Foundations of Software Engineering
(ESEC/FSE),2017,pp.245–256.
(ESEC/FSE),2017,pp.245–256.
[30] R.K.YandrapallyandA.Mesbah,“Fragment-basedtestgenerationfor
[8] Y.Zheng,Y.Liu,X.Xie,Y.Liu,L.Ma,J.Hao,andY.Liu,“Automatic
webapps,”IEEETransactionsonSoftwareEngineering(TSE),2022.
webtestingusingcuriosity-drivenreinforcementlearning,”inProceed-
[31] “Pageobject,”2022.[Online].Available:https://martinfowler.com/bliki/
ingsofInternationalConferenceonSoftwareEngineering(ICSE),2021,
PageObject.html
pp.423–435.
[32] D. Amalfitano, A. R. Fasolino, P. Tramontana, B. D. Ta, and A. M.
[9] Z.Zhang,Y.Liu,S.Yu,X.Li,Y.Yun,C.Fang,andZ.Chen,“Unirltest:
Memon,“Mobiguitar:Automatedmodel-basedtestingofmobileapps,”
Universalplatform-independenttestingwithreinforcementlearningvia
IEEESoftware,vol.32,no.5,pp.53–59,2014.
image understanding,” in Proceedings of International Symposium on
[33] B.Yu,L.Ma,andC.Zhang,“Incrementalwebapplicationtestingusing
SoftwareTestingandAnalysis(ISSTA),2022,pp.805–808.
pageobject,”inProceedingsofIEEEWorkshoponHotTopicsinWeb
[10] R.Yandrapally,A.Stocco,andA.Mesbah,“Near-duplicatedetectionin
SystemsandTechnologies(HotWeb),2015,pp.1–6.
webappmodelinference,”inProceedingsofInternationalConference
[34] D. Amalfitano, A. R. Fasolino, P. Tramontana, S. D. Carmine, and
onSoftwareEngineering(ICSE)),2020,pp.186–197.
A. M. Memon, “Using GUI ripping for automated testing of android
[11] A. M. Fard and A. Mesbah, “Feedback-directed exploration of web
applications,” in Proceedings of IEEE/ACM International Conference
applications to derive test models,” in Proceddings of International
on Automated Software Engineering (ASE), M. Goedicke, T. Menzies,
SymposiumonSoftwarReliabilityEngineering(ISSRE),2013,pp.278–
andM.Saeki,Eds.,2012,pp.258–261.
287.
[35] Y.-M. Baek and D.-H. Bae, “Automated model-based android gui
[12] A.Stocco,M.Leotta,F.Ricca,andP.Tonella,“Clustering-aidedpage
testingusingmulti-levelguicomparisoncriteria,”inProceedingsofthe
object generation for web testing,” in Proceedings of International
IEEE/ACMInternationalConferenceonAutomatedSoftwareEngineer-
ConferenceonWebEngineering(ICWE),2016,pp.132–151.
ing(ASE),2016,pp.238–249.
[13] M. Pan, A. Huang, G. Wang, T. Zhang, and X. Li, “Reinforcement
[36] T.Gu,C.Cao,T.Liu,C.Sun,J.Deng,X.Ma,andJ.Lu¨,“Aimdroid:
learningbasedcuriosity-driventestingofAndroidapplications,”inPro-
Activity-insulated multi-level automated testing for android applica-
ceedingsofInternationalSymposiumonSoftwareTestingandAnalysis
tions,” in Proceedings of IEEE International Conference on Software
(ISSTA),2020,pp.153–164.
MaintenanceandEvolution(ICSME),2017,pp.103–114.
[14] “Topwebsitesranklist,”2022.[Online].Available:https://www.alexa.
[37] D.LaiandJ.Rubin,“Goal-drivenexplorationforandroidapplications,”
com/topsites
in Proceedings of IEEE/ACM International Conference on Automated
[15] “Jpetstore demo,” January 1, 2023. [Online]. Available: https:
SoftwareEngineering(ASE),2019,pp.115–127.
//petstore.octoperf.com/actions/Catalog.action
[38] K. Mao, M. Harman, and Y. Jia, “Sapienz: Multi-objective automated
[16] “Monkey,”2022.[Online].Available:https://developer.android.com/
testing for android applications,” in Proceedings of International Sym-
[17] V.I.Levenshteinetal.,“Binarycodescapableofcorrectingdeletions,
posiumonSoftwareTestingandAnalysis(ISSTA),2016,pp.94–105.
insertions, and reversals,” in Soviet Physics Doklady, vol. 10, no. 8,
[39] J. Wang, Y. Jiang, C. Xu, C. Cao, X. Ma, and J. Lu, “Combodroid:
1966,pp.707–710.
Generating high-quality test inputs for Android apps via use case
[18] C. J. Watkins and P. Dayan, “Q-learning,” Machine Learning, vol. 8,
combinations,”inProceedingsofInternationalConferenceonSoftware
no.3,pp.279–292,1992.
Engineering(ICSE),2020,pp.469–480.
[19] J. A. Bondy and U. S. R. Murty, Graph Theory with Applications.
[40] Y. Zheng, X. Xie, T. Su, L. Ma, J. Hao, Z. Meng, Y. Liu, R. Shen,
MacmillanEducationUK,1976.
Y.Chen,andC.Fan,“Wuji:Automaticonlinecombatgametestingusing
[20] “Nyc,”2022.[Online].Available:https://istanbul.js.org/
evolutionarydeepreinforcementlearning,”inProceedingsofIEEE/ACM
[21] “Timeoff-management-application,” 2022. [Online]. Available: https:
International Conference on Automated Software Engineering (ASE),
//github.com/timeoff-management/timeoff-management-application
2019,pp.772–784.
[22] “Dimeshift,” 2022. [Online]. Available: https://github.com/
matteobiagiola/FSE19-submission-material-DIG/blob/master/fse2019/
dimeshift/README.md

