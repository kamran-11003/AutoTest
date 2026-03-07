# 2021 Ase Deep Gui

**Source:** 2021_ase_deep_gui.pdf  
**Converted:** 2026-01-26 09:21:57

---

## Page 1

Deep GUI: Black-box GUI Input Generation with
Deep Learning
Faraz YazdaniBanafsheDaragh Sam Malek
School of Information and Computer Sciences School of Information and Computer Sciences
University of California, Irvine, USA University of California, Irvine, USA
faraz.yazdani@uci.edu malek@uci.edu
Abstract—Despite the proliferation of Android testing tools, tools with insights to produce effective inputs, but also pose
Google Monkey has remained the de facto standard for prac- severe limitations that compromise the applicability of these
titioners. The popularity of Google Monkey is largely due to
tools. First, there is a substantial degree of heterogeneity
the fact that it is a black-box testing tool, making it widely
in the implementation details of apps. Consider for instance
applicable to all types of Android apps, regardless of their
underlying implementation details. An important drawback of the fact that many Android apps are non-native, e.g., built
Google Monkey, however, is the fact that it uses the most naive out of activities that are just wrappers for web content. In
form of test input generation technique, i.e., random testing. these situations, the majority of existing tools either fail to
In this work, we present Deep GUI, an approach that aims
operate or achieve very poor results. Second, the source code
to complement the benefits of black-box testing with a more
analyses underlying these tools are tightly coupled to the
intelligentformofGUIinputgeneration.Givenonlyscreenshots
of apps, Deep GUI first employs deep learning to construct a Android platform, and often to specific versions of it, making
model of valid GUI interactions. It then uses this model to them extremely fragile when used for testing apps in a new
generate effective inputs for an app under test without the environment.
need to probe its implementation details. Moreover, since the
Black-box input generation tools do not suffer from the
data collection, training, and inference processes are performed
same shortcomings. Google Monkey is the most widely used
independent of the platform, the model inferred by Deep GUI
has application for testing apps in other platforms as well. black-box testing tool for Android. Despite being a random
We implemented a prototype of Deep GUI in a tool called input generator, prior studies suggest Google Monkey outper-
Monkey++ by extending Google Monkey and evaluated it for its forms many of the existing white- and gray-box tools [25].
abilitytocrawlAndroidapps.WefoundthatMonkey++achieves
This can be attributed to the fact that Google Monkey is
significantimprovementsoverGoogleMonkeyincaseswherean
significantly more robust than almost all other existing tools,
app’sUIiscomplex,requiringsophisticatedinputs.Furthermore,
our experimental results demonstrate the model inferred using i.e., it works on all types of apps regardless of how they
DeepGUIcanbereusedforeffectiveGUIinputgenerationacross areimplemented.However,GoogleMonkeyemploysthemost
platforms without the need for retraining. basicformofinputgenerationstrategy.Itblindlyinteractswith
thescreenwithoutknowingifitsactionsarevalid.Thismight
I. INTRODUCTION
work well in apps with a simple GUI, where the probability
Automatic input generation for Android applications (apps) of randomly choosing a valid action is high, but not in apps
has been a hot topic for the past decade in the software with a complex GUI. For instance, take Figure 1. In Figure
engineering community [1]–[14]. Input generators have a 1a,sincemostofthescreencontainsbuttons,almostallofthe
variety of applications. Among others, they are used for times that Google Monkey decides to generate a touch action,
verifyingfunctionalcorrectness(e.g.,[13],[15],[16]),security it touches something valid and therefore tests a functionality.
(e.g., [17], [18]), energy consumption (e.g., [19], [20]), and However, in Figure 1b, it is much less probable for Google
accessibility (e.g., [21]) of apps. Depending on the objective Monkeytosuccessfullytouchtheonebuttonthatexistsonthe
athand,inputgeneratorscanbeverygeneric,andsimplycrawl screen, and therefore it takes much longer than needed for it
apps to maximize coverage [22]–[24], or can be very specific, to test the app’s functionality.
looking for certain criteria to be fulfilled, such as reaching This article presents Deep GUI, a black-box GUI input
activities with specific attributes [2]. generation technique with deep learning that aims to address
Common across the majority of existing input generators the above-mentioned shortcoming. Deep GUI is able to filter
is the fact that they are white-box, i.e., require access to out the parts of the screen that are irrelevant with respect to
implementation details of the app under test (AUT). For a specific action, such as touch, and therefore increases the
instance, many tools use static analysis to find the right probabilityofcorrectlyinteractingwiththeAUT.Forexample,
combinationofinteractionswiththeAUT[1]–[4],whileother given the screenshot shown in Figure 1b, Deep GUI first
tools depend on the XML-based GUI layout of the AUT to produces the heatmap in Figure 1c, which shows for each
find the GUI widgets and interact with them [5]–[14]. The pixel the probability of that pixel belonging to a touchable
underlying implementation details of an AUT provide these widget. It then uses this heatmap to touch the pixels with a

## Page 2

(a) (b)
(c) (d) (e)
Fig. 1: Two examples where it is respectively easy (a) and difficult (b) for Google Monkey to find a valid action, as well as
the heatmaps generated by Deep GUI associated with (b) for touch (c), scroll (d), and swipe (e) actions respectively. Note that
in (c) the model correctly identifies both the button and the hyperlink –and not the plain text– as touchable.
probability that is proportionate to their heatmap value, hence of our knowledge, this is the first approach that uses
increasing the chance of touching the button in this example. a completely black-box and cross-platform approach for
In order to produce such heatmaps, Deep GUI undertakes data collection, training, and inference in the generation
a deep-learning approach. We further show that this approach of test inputs.
is a special case of a more general method known as deep 2) WeprovideanimplementationofDeepGUIforAndroid,
reinforcement learning, and we discuss how this method can called Monkey++, by extending Google Monkey. We
be used to develop even more intelligent input generation make this tool available publicly.1
tools. Moreover, what makes Deep GUI unique is that it uses 3) We present detailed evaluation of Deep GUI using An-
a completely black-box and cross-platform method to collect drotest benchmark [25], consisting of 31 real-world mo-
data, learn from it, and produce the mentioned heatmaps, and bile apps, as well as the top 15 websites in the US [26].
hence supports all situations, applications, and platforms. It Our results corroborate Deep GUI’s ability to improve
also uses the power of transfer learning to make its training both the code coverage and the speed with which this
more data-efficient and faster. Our experimental evaluation coverage can be attained.
shows that Deep GUI is able to improve Google Monkey’s
The remainder of this paper is organized as follows. Sec-
performance on apps with complex GUIs, where Google
tion II describes the details of our approach. Section III
Monkey struggles to find valid actions. It also shows that we
provides our evaluation results. Section IV reviews the most
can take a Deep GUI model that is trained on Android, and
relevantpriorwork.Finally,inSectionV,thepaperconcludes
use it on other platforms, specifically web in our experiments,
withadiscussionofourcontributions,limitationsofourwork,
for efficient input generation.
and directions for future research.
In summary, this article makes the following contributions:
1) We propose Deep GUI, a black-box approach for gen-
eration of GUI inputs using deep learning. To the best 1 https://github.com/Feri73/deep-gui

## Page 3

II. APPROACH it can replace Google Monkey and be used in practically
the same way.
We formally provide our definition of the problem for
Figure 2 shows an overview of these four components and
automaticallygeneratinginputsinatestenvironment.Suppose
how they interact.
that at each timestep t, the environment provides us with its
state s . This can be as simple as the screenshot, or can be a
t A. Data Collection
more complicated content such as the UI tree. Also, suppose
Since we reduced the problem to a classification problem,
we define A = {α ,...α } as the set of all possible actions
1 N
each datapoint in our dataset needs to be in the form of a
that can be performed in the environment at all timesteps.
three-way tuple (s ,a ,r ), where our model tries to classify
For instance, in Figure 1b, all of the touch events associated t t t
the pair (s ,a ) into one of the two values that r represents,
with all pixels on the screen can be included in A. Note t t t
i.e.whetherperformingtheactiona onthestates isvalidor
that these actions are not necessarily valid. We define a valid t t
not.Trainingadeepneuralnetworkrequiresalargeamountof
action as an action that results in triggering a functionality
datafortraining.Tothatend,wehavedevelopedanautomatic
(like touching the send button) or changing the UI state (like
method to generate this dataset.
scrolling down a list). Let us define r = r(s ,a ) to be 1
t t t
As defined above, r represents whether the screen has a
if a is valid when performed on s , and 0 otherwise. Our t
t t
legitimate change after an action. We here define legitimate
goal is to come up with a function Q that, given s , produces
t
change as a change that does not involve an animated part
the probability of validity for each possible action. That is,
of the screen. In other words, if specific parts of the screen
Q(s ,a )identifieshowprobableitisfora tobeavalidaction
t t t
change even in case of no interaction with the app, we filter
when performed on s . Therefore, Q is essentially a binary
t
those parts out when computing r . For instance, in Android,
classifier(validvs.non-valid)conditionedons independently t
t
when focused on a textbox, a cursor keeps appearing and dis-
for each action in the set A. For simplicity, we also define
appearingeverysecond.Wefilteroutthepixelscorresponding
Q(s ) as a function that, given an action α, returns Q(s ,α).
t t
to the cursor.
That is, Q(s )(α)=Q(s ,α).
t t
For data collection, we first dedicate a set of apps to be
In Deep GUI, we consider s to be the screenshot of AUT
t
crawled. Then, for each app, we randomly interact with the
at each timestep. Set A consists of touch, up and down scroll,
appwiththeactionsinthesetAandrecordthescreenshot,the
and right and left swipe events, on all of the pixels of the
action, and whether the action resulted in a legitimate change.
screen. We also define r as follows:
t
In order to filter out animated parts of the screen, before each
(cid:40)
0 if equals(s ,s ) action, we first record the screen for 5 seconds and consider
r(s t ,a t )= t t+1 allpixelsthatchangeduringthisperiodtobeanimatedpixels.
1 otherwise
While this method does not fully filter all of the illegitimate
changes2, as our experimental results suggest, it is adequate.
That is, if the screenshot undergoes a legitimate change after
A keen observer would realize that this method of data
an action, we consider that action to be a valid one in that
collectionisaverynaturalchoiceintherealmofAndroid.For
screen.Wedefinewhatalegitimatechangemeanslaterinthis
section.Notethatwedefineds ,A,andr independentofthe years, Google Monkey has been used to crawl Android apps
t t
for different purposes, but the valuable data that it produces
platformonwhichAUToperates.Therefore,thisapproachcan
has never been leveraged to improve its effectiveness. That is,
be used in almost all existing test environments.
even if a particular app has already been crawled by Google
This work consists of four components:
Monkey thousands of times before, when Google Monkey is
A. Data collection: This component helps in collecting nec-
used to crawl that app, it still crawls randomly and makes all
essary data to learn from.
of the mistakes that it has already made thousands of times
B. Model: At the core of this component is a deep neural
before. The collection method described here is an attempt to
network that processes s and produces a heatmap Q(s )
t t share these experiences by training a model and exploiting
for all possible actions a , such as the ones shown in
t such model to improve the effectiveness of testing, as we
Figure 1. The neural network is initialized with weights
discuss next.
learned from large image classification tasks to provide
faster training. B. Model
C. Inference: After training, and at the inference time, there
While, as discussed above, the problem is to classify the
are multiple readout mechanisms available for using the
validity of a single action a when performed on s , it does
produced heatmaps and generating a single action. These t t
notmeanthateachdatapoint(s ,a ,r )cannotbeinformative
mechanisms are used in a hybrid fashion to provide us t t t
about actions other than a . For instance, if touching a point
with the advantages of all of them. t
results in a valid action, touching its adjacent points may
D. Monkey++:Thisistheonlycomponentthatisspecialized
also result in a valid action with a high probability. This can
forAndroid,anditsapplicationistofairlycompareDeep
GUI with Google Monkey. It also provides a convenient
2Forinstance,ifanaccumulativeprogressbarisbeingshown,thismethod
mediumtouseDeepGUIfortestingofAndroidapps,as maynotwork.

## Page 4

Fig. 2: Overview of the components comprising Deep GUI & Monkey++.
makeourtrainingprocessmuchfasterandmoredata-efficient. This makes it easier for the network to make deductions
Therefore, we need a model that can capture such logic. about all actions, and not just a . Moreover, the entire model
t
1) Input and Output: As the first step toward this goal, in seems to have an intuitive design: First, the relevant parts of
our model, we define input and output as follows. Input is a information are extracted and grouped in different layers, and
3-channelimagethatrepresentss ,thescreenshotoftheAUT then combined to form the output. This is similar to how the
t
at time t. For output, we require our model to perform the UI elements are usually represented in software applications
classification task for all the actions of all types (i.e., touch, as a GUI tree.
scroll, swipe, etc.), and not just a . While we do not directly
t 3) Transfer Learning: While Google Monkey might strug-
usethepredictionforotheractionstogenerategradientswhen
gle in finding valid actions when crawling an app, and other
training,thisenablesusto(1)useamoreintuitivemodel,and
tools might need to use other information such as GUI tree
(2)usethemodelatinferencetimebychoosingtheactionthat
or source code to detect such actions, humans find the logic
is most confidently classified to be valid. We use a T-channel
behind a valid action to be pretty intuitive, and can learn it
heatmaptorepresentouroutput;T beingthenumberofaction
withinminutesofencounteringanewenvironment.Thereason
types,i.e.touch,scroll,swipe.Notethatwedonotdifferentiate
behind this “intuition” lies in the much more elaborate visual
between up/down scroll or left/right swipe at this stage. Each
experience that humans have that goes beyond the Android
channel is a heatmap for the action type it represents. For
environments. Since birth, we see a myriad of objects in
each action type, the value at (i,j) of the heatmap associated
a myriad of contexts, and we learn to distinguish objects
with that action type represents the probability that the model
from their backgrounds. This information helps us a lot to
assignstothevalidityofperformingthatactiontypeatlocation
distinguish a button in the background of an app, even if the
(i,j).Forinstance,inFigure1,thethreeheatmaps1c,1d,and
background itself is a complicated image. Because of this, we
1e show the model’s confidence in performing touch, scroll,
humansdonotneedthousandsofexamplestolearntointeract
and swipe, respectively, at different locations on the screen.
with an environment.
2) UNet: We also would need a model that can intuitively
How can we use this fact to get the same training perfor-
relate the input and output, as defined above. We use a UNet
mancewithfewerdatainourtool?Researchinmachinelearn-
architecture, since it has shown to be effective in applications
inghasshownthepossibilityofachievingthisthroughtransfer
such as image segmentation, where the output is an altered
learning [29]. In transfer learning, instead of a randomly
version of the input image [27]. In this architecture, the input
initialized network, an existing model previously trained on a
image is first processed in a sequence of convolutional layers
dataset for a potentially different but related problem is used
known as the contracting path. Each of these layers reduces
as the starting point of all or some part of the network. This
the dimensionality of the data while potentially encoding
way,we“transfer”alltheexperiencerelatedtothatdataset(as
different parts of the information relevant to the task at hand.
summarized in the trained weights), without having invested
Thecontractingpathisfollowedbytheexpansivepath,where
time to actually process it. Therefore, training is more data-
various pieces of information at different layers are combined
efficient. This is in particular important for us because, as
using transposed convolutional layers3 to expand the dimen-
discussed, the data collection process is very time-consuming
sionalitytothesuitableformatrequiredbytheproblem.Inour
given that the tool needs to monitor the screen for animations
case, the output would be a 3-channel heatmap. In order for
before collecting each datapoint.
this heatmap to produce values between 0 and 1 (as explained
The contracting path of the UNet seems like a perfect
above), it is processed by a sigmoid function in the last step
candidate for transfer learning because, unlike the expansive
of the model. As one can notice, because of the nature of
path,itismorerelatedtohowthenetworkprocessestheinput,
convolutional and transposed convolutional layers, adjacent
rather than how it produces the output. This means that any
coordinatepairsareprocessedmoresimilarlythanotherpairs.
trained model that exists for processing an image can be a
3 Insomereferencesthesearereferredtoasdeconvolutionallayers. candidate for us to use its weights.

## Page 5

Fig.3:ThedeepneuralnetworkarchitectureusedinDeepGUI.Thelayers’namesshowninMobileNetV2arefromTensorflow
[28] implementation of the architecture. ConvT is a transpose convolutional layer.
In this work, as the contracting path, we used part of
the network architecture MobileNetV2 [30] trained on the
ImageNet dataset [31].4 We chose MobileNetV2 because it
is powerful and yet lightweight enough to be used inside
mobilephonesifnecessary.Figure3showshowMobileNetV2
interacts with our expansive path to build the model used
in Deep GUI. Note that in order for the screenshot to be
compatible with the already trained MobileNetV2 model, we
first resize it to 224×224. Also, because of computational
reasons,theproducedoutputis56×56,andislaterupsampled
linearly to the true screen size.
4) Training: At the training time, for each datapoint
(s ,a ,r ), the network first produces Q(s ) as the described
t t t t
heatmaps. Then, using the information about the performed
action a , it indexes the network’s prediction for the action to (a) (b)
t
getQ(s t )(a t )=Q(s t ,a t ).Finally,sincethisisaclassification Fig. 4: (a) An example of a screen with equally important
task, we use a binary crossentropy loss between r t and widgets of different sizes. (b) The touch channel of the
Q(s t ,a t ) to generate gradients and train the network. produced heatmap. The pixels belonging to different clusters
C. Inference that the cluster_sampling readout detects are colored
with maroon, red, and white, depending on the cluster they
Once we have the trained model, we would like to be able
belong to.
to use it to pick an action given a screenshot of an app at a
specific state. Therefore, we require a readout function that
can sample an action from the produced heatmaps. Here, we
chose to use the linear kernel f(x)=x. Using the probability
propose two readouts, and we explain how we use both in
distribution that the linear kernel produces, we then sample
Deep GUI.
an action. We call this method the weighted_sampling
The simplest possible readout is one that samples actions
readout.
based on their relative prediction. That is, the more probable
the network thinks it is for the action to be a valid one, the However,humansusuallyinteractwithappsdifferently.We
more probable it is for the action to be sampled. For this to seewidgetsratherthanpixels,andinteractwiththosewidgets
happen, we need to normalize the heatmaps to a probability as a whole. The weighted_sampling readout does not
distribution over all actions of all types. Formally: take this into account as it treats each pixel independently.
Take Figure 4a as an example. The “Enable delivery reports”
f(Q(s ,α))
p(a =α|s )= t checkbox is potentially as important as the send button,
t t (cid:80) f(Q(s ,α(cid:48)))
α(cid:48)∈A t because if it is checked a new functionality can be tested.
where f identifies the kernel function. For instance if f(x)= However, because the button is larger than the checkbox, it
exp(x), we have a softmax normalization. In our work, we takes the weighted_sampling readout longer to finally
toggle the checkbox and test the new functionality.
4 Pleasenotethatweusedthisexistingtrainedmodelastheinitialization
To address this issue, we use the cluster_sampling
of the contracting path. In the training step, we do train the weights on the
contractingpath. readout.Inthisapproach,wefirstfilteroutalltheactionsαfor

## Page 6

which the predicted Q(s t ,α) is less than a certain threshold. Algorithm 1: Monkey++ algorithm
This way, we ensure only the actions that are highly probable
while Google Monkey is running do
tobevalidareconsidered.InDeepGUIthisthresholdis0.99.
get action type t from Google Monkey;
Then,foreachchannelinQ(s ),weuseagglomerativecluster-
t if t is touch or gesture then
ingasimplementedinpythonlibraryscikit-learn[32]to get action a from Deep GUI server
cluster the pixels into widgets. Figure 4b shows the clustering else
result for the touch channel of the heatmap corresponding continue with Google Monkey and get action a
to Figure 4a. After detecting the clusters, we first randomly end
chooseoneoftheactiontypes,andthenrandomlychooseone perform a
oftheclusters(i.e.widgets)inthechannelassociatedwiththat end
action type. Finally, we choose a random pixel that belongs
to that cluster and generate a .
t
While configurable, in our experiments we used a hy-
RQ1. How does Monkey++ compare to Google Monkey?
brid readout that uses weighted_sampling in 30% of
RQ2. Can Deep GUI be used to generate effective test inputs
the times, and cluster_sampling in 70% of the times.
across platforms?
This way, we exploit the benefits that cluster_sampling
RQ3. How much is transfer learning helping Deep GUI in
offers, while we make sure we do not completely abandon
learning better and faster?
certain valid actions because of the imperfections of the tool.
We used the apps in the Androtest benchmark [25] as our
The discussed readouts identify the action type and the
poolofapps.Outof66appsavailable6,werandomlychose28
location of it on the screen. However, scroll and swipe also
for training, 6 for validation, and 31 for testing purposes. We
requireotherparameterssuchasdirectionorlength.DeepGUI
also eliminated one of the apps because of its incompatibility
chooses these parameters randomly. Also, because swipe and
with our data collection procedure.7
scrollaremostlyusedtodiscoverotherbuttons,whiletouchis
Tosupportavarietyofscreensizes,wecollecteddatafrom
actuallytheactionthattriggersthefunctionalityofthebuttons,
virtualdevicesofsize240×320andalso480×854,andtrained
we configure the described readouts so that they are more
biased towards choosing the touch action.5 a single model that is used in the experiments explained in
Sections RQ1 and RQ2. We collected an overall amount of
D. Monkey++
210,000 data points. Virtual devices, both for data collection
While touch, swipe, and scroll are the most used action and the Android experiments, were equipped with a 200MB
types when interacting with an environment, there are other virtualSDcard,aswellas4GB ofRAM.Fordatacollection,
actions that may affect the ability of a tool to crawl Android training, and the experiments, we used an Ubuntu 18.04 LTS
apps.Inordertocoverthoseactionsaswell,andalsoinorder workstation with 24 Intel Xenon CPUs and 150GB RAM.
tobeabletocompareGoogleMonkeywithoursolutionfairly We did not use GPUs at any stage of this work. The entire
in the Android environment, we introduce Monkey++, which source code for this work, the experiments, and the analysis
is an extension to Google Monkey. Monkey++ consists of a is available at https://github.com/Feri73/deep-gui.
server side, which responds to queries with Deep GUI, and a
client side, which is implemented inside Google Monkey. RQ1. Line Coverage
Google Monkey works as follows. First, it randomly In order to test the ability of Monkey++ in exploring
chooses an action type (based on the probabilities provided Android apps, we ran both Monkey++ and Google Monkey
to it when starting it), and then randomly chooses the param- on each app in the test set for one hour, and monitored line
eters (such as the location to touch). Monkey++ works the coverage of the AUT every 60 seconds using Emma [33]. We
same as Google Monkey with one exception. If the chosen ran 9 instances of this experiment in parallel, and calculated
action type is touch or gesture (which represents all types of the average across different executions of each tool. Table
movement, including scroll and swipe), instead of proceeding I shows the final line coverage for the apps in the test set.
with the standard random procedure in Google Monkey, it While in some apps Monkey++ and Google Monkey perform
sendsaquerytotheserverside.Usingtheinferenceprocedure similarly, in other apps, such as com.kvance.Nectroid,
described above, Deep GUI samples an action and returns to Monkey++ significantly outperforms Google Monkey. We
the client, which is then performed on the device. Algorithm believe this is directly related to an attribute of apps, referred
1 shows how Monkey++ works. to as Crawling Complexity (CC) in this paper.
III. EVALUATION CC is a measure of the complexity of exploring an app.
Different factors can affect this value. For instance, if the
We evaluated Deep GUI with respect to the following
majority of the app’s code is executed at the startup, there
research questions:
5 In weighted_sampling, we multiply each heatmap belong- 6 Threeappscausedcrashesintheemulatorsandhencewerenotused.
ing to touch, scroll, and swipe with 1, 0.3, and 0.1 respectively. In 7 Application org.jtb.alogcat keeps updating the screen with new
cluster_sampling, when randomly choosing an action type from the logs from the logcat regardless of the interactions with it, which highly
availableones,weusethesamethreenumberstobiastheprobability. deviatesfromthebehaviorofanormalAndroidapp.

## Page 7

TABLE I: The results of running Monkey++ and Google Monkey on the test set, sorted by Crawling Complexity. The shading
indicates the tool that achieved the best result.
Application Crawling Complexity Monkey++ Line Coverage G Monkey Line Coverage
es.senselesssolutions.gpl.weightchart 2.8 67% 65%
com.hectorone.multismssender 2.6 64% 67%
com.templaro.opsiz.aka 2.4 72% 66%
com.kvance.Nectroid 2.3 65% 50%
com.tum.yahtzee 2.3 67% 61%
in.shick.lockpatterngenerator 2.2 86% 84%
net.jaqpot.netcounter 2.2 71% 69%
org.waxworlds.edam.importcontacts 2.0 41% 34%
cri.sanity 1.8 25% 23%
com.chmod0.manpages 1.7 72% 63%
com.google.android.divideandconquer 1.5 85% 88%
com.example.android.musicplayer 1.3 71% 71%
ch.blinkenlights.battery 1.3 91% 93%
org.smerty.zooborns 1.2 34% 33%
com.android.spritemethodtest 1.2 71% 87%
com.android.keepass 1.1 7% 8%
org.dnaq.dialer2 1.0 39% 39%
hu.vsza.adsdroid 1.0 24% 24%
com.example.anycut 0.9 71% 71%
org.scoutant.blokish 0.9 45% 46%
org.beide.bomber 0.8 89% 88%
com.beust.android.translate 0.7 48% 48%
com.addi 0.6 18% 18%
org.wordpress.android 0.5 5% 5%
com.example.amazed 0.3 82% 81%
net.everythingandroid.timer 0.2 65% 65%
com.google.android.opengles.spritetext 0.1 59% 59%
aarddict.android 0.0 14% 14%
com.angrydoughnuts.android.alarmclock 0.0 6% 6%
com.everysoft.autoanswer 0.0 9% 9%
hiof.enigma.android.soundboard 0.0 100% 100%
com.tum.yahtzee: This is a dice game with fairly complicated logic and several buttons, each activating different scenarios over time.
org.waxworlds.edam.importcontacts:ThisappimportscontactsfromtheSDcard.Therearemultiplestepstoreachtothefinal
activity, and each contains multiple options that change the course of actions that the app finally takes.
hu.vsza.adsdroid: The only functionality of this app is to search for and list the data-sheets of electronic items. The search activity
contains one drop-down list for search criteria, and a search button.
org.wordpress.android:ThisappisformanagementofWordPresswebsites.Atthestartup,iteitherrequiresaloginoropensaweb
container, which does not affect the line coverage.
is not much code left to be explored. As another example, entropy, because it is more difficult to predict its exact value.
consider apps that require signing in to an account to access The formula for calculating entropy H of a discrete random
theirfunctionality.Unlessitisexplicitlysupportedbythetools variable X is as follows:
(which is not in this study), not much can be explored within
n
the app. (cid:88)
H(X)=− p(x )log (p(x ))
i 2 i
We hypothesize that Monkey++ outperforms Google Mon-
i=1
keyinappswithhighCC.Inordertotestthis,wedefineCCas
theuncertaintyincoveragewhenrandomlyinteractingwithan wherex representsthevaluesthatX canget,andp(x )isthe
i i
app. That is, if random interactions with an app always result probabilitydistributionforX.TocalculateCCofanappusing
inasimilartraceofcoverage,itmeansthattheavailableparts entropy, we take all line coverage information for that app in
of the app are trivial to reach and will always be executed, all timesteps of all experiments involving Google Monkey (as
and therefore, not much is offered by the app to be explored. a random interaction tool), and calculate the entropy of the
To compute uncertainty (and hence CC) for an app, we use distribution of these coverage values using the above formula.
the concept of entropy. The coverage values for two apps with low and high CC are
Theentropyofarandomvariableisameasureoftheuncer- shown in Figure 5.
taintyofthevaluesthatthisvariablecanget.Forinstance,ifa Table I shows the CC value for each app, and discusses
randomvariableonlygetsonevalue(i.e.,itisnotrandom),the some examples of apps with high and low CC, including the
entropy would be zero. On the other hand, a random variable examples in Figure 5. As one can notice, most of the apps in
that samples its values from a uniform distribution has a large which Monkey++ achieves better coverage have higher CC.

## Page 8

(a) (b)
(c)
(d)
Fig. 5: The results of exploring two apps randomly in 9 independent runs: (a) An example of an app with low CC
(hu.vsza.adsdroid). (b) We obtain only 3 distinct coverage values for the entire 60 minutes of randomly testing the
adsdroid app across all 9 agents. This means the portion of the app that is accessible to be explored is very limited. (c) An
example of an app with high CC (com.tum.yahtzee). (d) Here, the coverage values that we obtain by randomly exploring
the yahtzee app span a much more uncertain space than the adsdroid app, which means more is offered by the app to
be explored and therefore it is more meaningful to compare the testing tools on this app.
To further evaluate the ability of Monkey++ in crawling web content wrapped in an android web viewer, and lack
complex apps with high CC, we analyzed the progressive standard UI elements that white-box tools depend on. In
coverage of the top 10 apps with the highest CC. Figure these scenarios, practitioners are bound to use random testing
6 shows that Monkey++ achieves better results compared tools such as Google Monkey. Monkey++ provides a more
to Google Monkey, and does so faster. This superiority is intelligent alternative in these situations that, as the results
statisticallysignificantinalltimesteps,ascalculatedbyaone- suggest, provide better coverage faster.
tail Kolmogorov–Smirnov (KS) test (p-value < 0.05).8
RQ2. Cross-Platform Ability
The improvement over Google Monkey is valuable, since
it is currently the most widely used testing tool that does not Since Deep GUI is completely blind with regards to the
require the AUT to implement any specific API. For instance, app’s implementation or the platform it runs on, we hypothe-
most of the mainstream white-box testing tools fail on non- sizeitisapplicablenotonlyinAndroidbutinotherplatforms
native applications, because these applications are essentially such as web or iOS. Moreover, we claim that since UI design
acrossdifferentplatformsisverysimilar(e.g.buttonsarevery
8TocalculatetheerrorbarsinFigure6andthep-valueforKS-test,firstfor similar in Android and web), we can take a model trained on
eachapp,themeanperformanceofGoogleMonkeyonthatappissubtracted oneplatformanduseitinotherplatforms.Thisisparticularly
fromtheperformanceofbothGoogleMonkeyandMonkey++,andthenthe
useful whendevelopers want to testdifferent implementations
errorbarsandthesignificancearecomputedwithregardstothisvalueacross
allapps. of the same app in different platforms.

## Page 9

TABLE II: The performance of Deep GUI and random agent
on each web site
Website Deep GUI Random
google.com 17.4 12.9
youtube.com 94.3 12.1
amazon.com 13.2 15.2
yahoo.com 15.4 21.8
facebook.com 3.2 7.1
reddit.com 5.3 5.1
zoom.us 4.6 6.9
wikipedia.org 41.1 40.6
myshopify.com 3.6 6.0
ebay.com 13.4 11.4
netflix.com 5.1 4.8
bing.com 32.5 25.5
office.com 16.9 15
live.com 2.7 2.5
Fig. 6: The progressive line coverage of Monkey++ and twitch.tv 65.6 30.1
Google Monkey on the top 10 Android apps with the highest average 22.2 14.4
CC. Error bars indicate standard error of the mean.
(a) (b)
Fig. 8: A screenshot and its corresponding heatmap generated
Fig.7:TheprogressiveperformanceofDeepGUIandrandom
by the model before training.
agent in web crawling. The difference between the three tools
is statistically significant in all timesteps, as calculated by
one tail KS-tests between all pairs (similar to the procedure
Figure7andtableIIshowthatourmodeloutperformsrandom
described in footnote 8).
agent, and confirms that our model has learned the rules of
UI design, which is indeed independent of the platform.
Theresultsofthewebexperimentdemonstratethepowerof
To test whether our approach is truly cross-platform, we
a black-box technique capable of understanding the dynamics
implementedaninterfacetouseDeepGUIforinteractingwith
of GUI-based applications without relying on any sort of
MozillaFirefoxbrowser9 usingSeleniumwebdriver[34],and
platform-dependent information. Such techniques infer gener-
compared it against a random agent10. Note that we did not
alized rules about GUI-based environments instead of relying
re-train our model, and used the exact same hyper-parameters
onspecificAPIsorimplementation-choicesintheconstruction
and weights we used for the experiments in RQ1, which are
ofanapplication,andhenceenableuserstoapplythetoolson
learned from Android apps.
differentapplicationsandondifferentplatformswithoutbeing
For the web experiments, we used the top 15 websites in
constrained by the compatibility issues.
the United States [26] as our test set, and ran each tool on
each website 20 times, each time for 600 steps. To measure RQ3. Transfer Learning Effect
the performance, we counted the number of distinct URLs
Asdescribed,weusedtransferlearningtomakethetraining
visited in each website, and averaged this value for each tool.
process more data-efficient, i.e. we crawl fewer data and train
faster.Tostudyifusingtransferlearningwasactuallyhelpful,
9WeusedResponsiveDesignModeinMozillaFirefoxwiththeresolution
werepeatedthewebexperiments,withtheonlydifferencethat
of480×640.
instead of using the model trained with transfer learning, we
10 Therandomagentusesthesamebiasforactiontypesthatisexplained
infootnote5ofSectionII. trained another model with random initial weights. Figure 7

## Page 10

shows that without transfer learning, the model’s performance for a new platform. The study of White et al. [44] is the most
significantly decreases. similartoourwork.Theystudytheeffectofmachine-learning-
To gain an intuitive understanding of the reason behind powered processing of screenshots in generating inputs with
this, consider Figure 8b. This figure shows the initial output random strategy. However, because they generate artificial
of the neural network for the screen of Figure 8a before apps for training their model, their data collection method is
training, when initialized with the ImageNet weights. As one limitedinexpressingthevarietyofscreensthatthetoolmight
can see, even without training, the buttons stand out from encounter. Furthermore, their approach is platform dependent.
the background in the heatmap, which gives the model a DeepGUIusesdeeplearningtoimprovecontext-blindinput
significant head-start compared to the randomly initialized generation,whilealsolimitingtheprocessedinformationtobe
model, and makes it possible for us to train it with a small black-box and platform independent. This allows it to be as
amount of data. versatile as Google Monkey in the Android platform, while
being more effective by intelligently generating the inputs for
IV. RELATEDWORK
crawling of apps.
Many different input generation techniques with different
paradigms have been proposed in the past decade. Several V. DISCUSSIONANDFUTUREWORK
techniques [35], [36] rely on a model of the GUI, usually
DeepGUIisthefirstattempttowardsmakingafullyblack-
constructed dynamically and non-systematically, leading to
box and cross-platform test input generation tool. However,
unexplored program states. Sapienz [15], EvoDroid [16], and
there are multiple areas in which this tool can be improved.
time-travel testing [37] employ an evolutionary algorithm.
Thefirstlimitationoftheapproachdescribedhereisthetime-
ACTEve [38], and Collider [39] utilize symbolic execution.
consuming nature of its data collection process, which limits
AppFlow [40] leverages machine learning to automatically
the number of collected data points and may compromise the
recognize common screens and widgets and generate tests
dataset’s expressiveness. By using transfer learning, we man-
accordingly. Dynodroid [23] and Monkey [22] generate test
aged to mitigate this limitation to some degree. In addition,
inputsusingrandominputvalues.Anothergroupoftechniques
the complex set of hyperparameters (such as hybrid readout
focus on testing for specific defects [20], [41], [42].
probabilities) and the time-consuming nature of validating the
These approaches can be classified into two broad cate-
model on apps make it difficult to fine-tune all the hyperpa-
gories: context blind and context aware. The tools in the for-
rameters systematically, which is required for optimizing the
mer category process information in each action independent
performance to its maximum potential.
of other actions. That is, when choosing a new action, they
Deep GUI limits itself to context-blind information pro-
do not consider the previous actions performed, and do not
cessing, in that it does not consider the previous interactions
plan for future actions. Tools such as Google Monkey [22]
with AUT when generating new actions. However, it uses
and DynoDroid [23] are in this category. These tools are fast
a paradigm that can easily be extended to take context into
and require very simple pre-processing, but may miss entire
account as well. We believe this paradigm should be explored
activities or functionalities, as this requires maintaining a
more in the future of the field of automated input generation.
modeloftheappandvisitedstates.Toolsinthelattercategory
Takeourdefinitionoftheproblem.Ifwecalls thestateof
incorporate various sources of information to construct a t
the environment, a the action performed on the environment
model of an app, which is then used to plan for context- t
in that state, r the reward that the environment provides
aware input generation. Most of the existing input generation t
in response to that action, and Q(s ,a ) the predictions of
tools are in this category. For instance, Sapienz [15] uses a t t
the model about the long-term reward that the environment
geneticalgorithmtolearnagenericmodelofapp,representing
provides when performing a in s (also known as the quality
how certain sequences of actions can be more effective than t t
matrix), then this work can essentially be viewed to propose
others. Tools that use different types of static analysis of the
a single-step deep Q-Learning [45] solution to the problem
source code or GUI to model the information flow globally
of test input generation. Looking at the problem this way
also belong to this category.
enablesresearchersintheareaofautomaticinputgenerationto
Not many tools have explored black-box and/or cross-
benefitfromtherichandactiveresearchintheQ-Learningand
platform options for gathering information to be used for
reinforcementlearning(RL)community,andexploredifferent
input generation, either with a context-aware or a context-
directions in the future such as the following:
blind approach. Google Monkey is the only widely used
tool in Android that does not depend on any app-specific • Multi-Step Cross-Platform Input Generation. Deep GUI
information. However, it follows the simplest form of testing, uses Q-Learning in a context-blind and single-step manner.
i.e., random testing. Humanoid [43] is an effort towards However, by redefining s to include more context (such
t
becominglessplatform-dependent,whilealsogeneratingmore as previous screenshots, as tried in Humanoid [43]) and
intelligent inputs. However, it is still largely dependent on expanding the definition of r to express a multi-step sense
t
the UI transition graph of AUT and the GUI tree extracted of reward, one can use the same idea to utilize the full
from the operating system. Moreover, since it depends on an powerofQ-Learningtotrainmodelsthatnotonlylimittheir
existing dataset for Android, it would not be easy to train it actions to only the valid ones (as this tool does), but also

## Page 11

plan ahead and perform complex and meaningful sequence [9] W. Choi, G. Necula, and K. Sen, “Guided gui testing of android apps
of actions. withminimalrestartandapproximatelearning,”SIGPLANNot.,vol.48,
p.623–640,Oct.2013.
• Smarter Processing of Information. Even if a tool does [10] S. Hao, B. Liu, S. Nath, W. G. Halfond, and R. Govindan, “Puma:
not want to limit itself to only platform-independent in- Programmableui-automationforlarge-scaledynamicanalysisofmobile
formation, it can still benefit from using a Q-Learning apps,” in Proceedings of the 12th Annual International Conference on
MobileSystems,Applications,andServices,MobiSys’14,(NewYork,
solution. For instance, one can define s to include the
t NY,USA),p.204–217,AssociationforComputingMachinery,2014.
GUI tree or the memory content to provide the model with [11] K. Jamrozik and A. Zeller, “Droidmate: A robust and extensible test
more information, but also use Q-Learning to process this generatorforandroid,”in2016IEEE/ACMInternationalConferenceon
MobileSoftwareEngineeringandSystems(MOBILESoft),pp.293–294,
information more intelligently.
2016.
• Regression Testing and Test Transfer. While this work [12] L. Mariani, M. Pezze, O. Riganelli, and M. Santoro, “Autoblacktest:
presentsatrainedmodelthattargetsallapps,itisnotlimited Automaticblack-boxtestingofinteractiveapplications,”in2012IEEE
Fifth International Conference on Software Testing, Verification and
tothis.DeveloperscantakeaQ-Learningmodelsuchasthe
Validation,pp.81–90,2012.
one described in this work, collect data from the app (or a [13] T.Su,G.Meng,Y.Chen,K.Wu,W.Yang,Y.Yao,G.Pu,Y.Liu,and
family of related apps) they are developing, and train the Z.Su,“Guided,stochasticmodel-basedguitestingofandroidapps,”in
Proceedingsofthe201711thJointMeetingonFoundationsofSoftware
model extensively so that it learns what actions are valid,
Engineering, ESEC/FSE 2017, (New York, NY, USA), p. 245–256,
what sequences of actions are more probable to test an AssociationforComputingMachinery,2017.
important functionality, etc. This way, when new updates [14] Yuanchun Li, Ziyue Yang, Yao Guo, and Xiangqun Chen, “Droidbot:
a lightweight ui-guided test input generator for android,” in 2017
of the app are available, or when the app becomes available
IEEE/ACM 39th International Conference on Software Engineering
in new platforms, developers can quickly test for any fault Companion(ICSE-C),pp.23–26,2017.
in that update without having to rewrite the tests. [15] K. Mao, M. Harman, and Y. Jia, “Sapienz: Multi-objective automated
testingforandroidapplications,”inProceedingsofthe25thInternational
SymposiumonSoftwareTestingandAnalysis,ISSTA2016,(NewYork,
ACKNOWLEDGMENT
NY,USA),p.94–105,AssociationforComputingMachinery,2016.
Thisworkwassupportedinpartbyawardnumbers2106306 [16] R. Mahmood, N. Mirzaei, and S. Malek, “Evodroid: Segmented evo-
lutionary testing of android apps,” in Proceedings of the 22nd ACM
and 1823262 from the National Science Foundation and a
SIGSOFT International Symposium on Foundations of Software Engi-
Google Cloud Platform gift. We would like to thank the neering,pp.599–609,2014.
anonymousreviewersofthispaperfortheirdetailedfeedback, [17] J. Garcia, M. Hammad, N. Ghorbani, and S. Malek, “Automatic gen-
erationofinter-componentcommunicationexploitsforandroidapplica-
which helped us improve the work.
tions,” in Proceedings of the 2017 11th Joint Meeting on Foundations
of Software Engineering, ESEC/FSE 2017, (New York, NY, USA),
REFERENCES p.661–671,AssociationforComputingMachinery,2017.
[18] C. Cao, N. Gao, P. Liu, and J. Xiang, “Towards analyzing the input
[1] T. Azim and I. Neamtiu, “Targeted and depth-first exploration for validation vulnerabilities associated with android system services,” in
systematic testing of android apps,” in Proceedings of the 2013 ACM Proceedings of the 31st Annual Computer Security Applications Con-
SIGPLAN International Conference on Object Oriented Programming ference,ACSAC2015,(NewYork,NY,USA),p.361–370,Association
Systems Languages & Applications, OOPSLA ’13, (New York, NY, forComputingMachinery,2015.
USA),p.641–660,AssociationforComputingMachinery,2013. [19] Y.Liu,C.Xu,S.Cheung,andJ.Lu¨,“Greendroid:Automateddiagnosis
[2] R. Bhoraskar, S. Han, J. Jeon, T. Azim, S. Chen, J. Jung, S. Nath, ofenergyinefficiencyforsmartphoneapplications,”IEEETransactions
R. Wang, and D. Wetherall, “Brahmastra: Driving apps to test the onSoftwareEngineering,vol.40,no.9,pp.911–940,2014.
securityofthird-partycomponents,”inProceedingsofthe23rdUSENIX [20] R.Jabbarvand,J.-W.Lin,andS.Malek,“Search-basedenergytestingof
Conference on Security Symposium, SEC’14, (USA), p. 1021–1036, android,”in2019IEEE/ACM41stInternationalConferenceonSoftware
USENIXAssociation,2014. Engineering(ICSE),pp.1119–1130,2019.
[3] M. Linares-Va´squez, M. White, C. Bernal-Ca´rdenas, K. Moran, and [21] A.Alshayban,I.Ahmed,andS.Malek,“Accessibilityissuesinandroid
D. Poshyvanyk, “Mining android app usages for generating actionable apps:Stateofaffairs,sentiments,andwaysforward,”inProceedingsof
gui-based execution scenarios,” in Proceedings of the 12th Working theACM/IEEE42ndInternationalConferenceonSoftwareEngineering,
Conference on Mining Software Repositories, MSR ’15, p. 111–122, ICSE ’20, (New York, NY, USA), p. 1323–1334, Association for
IEEEPress,2015. ComputingMachinery,2020.
[4] S. Yang, H. Wu, H. Zhang, Y. Wang, C. Swaminathan, D. Yan, and [22] “Ui/applicationexercisermonkey.”https://developer.android.com/studio/
A. Rountev, “Static window transition graphs for android,” Automated test/monkey,2020.
SoftwareEngg.,vol.25,p.833–873,Dec.2018. [23] A.Machiry,R.Tahiliani,andM.Naik,“Dynodroid:Aninputgeneration
[5] D. Amalfitano, A. R. Fasolino, and P. Tramontana, “A gui crawling- systemforandroidapps,”inProceedingsofthe20139thJointMeeting
basedtechniqueforandroidmobileapplicationtesting,”in2011IEEE onFoundationsofSoftwareEngineering,ESEC/FSE2013,(NewYork,
Fourth International Conference on Software Testing, Verification and NY,USA),p.224–234,AssociationforComputingMachinery,2013.
ValidationWorkshops,pp.252–261,2011. [24] K. Mao, M. Harman, and Y. Jia, “Crowd intelligence enhances auto-
[6] D. Amalfitano, A. R. Fasolino, P. Tramontana, S. De Carmine, and mated mobile testing,” in Proceedings of the 32nd IEEE/ACM Inter-
A. M. Memon, “Using gui ripping for automated testing of android national Conference on Automated Software Engineering, ASE 2017,
applications,”in2012Proceedingsofthe27thIEEE/ACMInternational p.16–26,IEEEPress,2017.
ConferenceonAutomatedSoftwareEngineering,pp.258–261,2012. [25] S. R. Choudhary, A. Gorla, and A. Orso, “Automated test input gen-
[7] Y. Baek and D. Bae, “Automated model-based android gui testing eration for android: Are we there yet? (e),” in 2015 30th IEEE/ACM
using multi-level gui comparison criteria,” in 2016 31st IEEE/ACM International Conference on Automated Software Engineering (ASE),
International Conference on Automated Software Engineering (ASE), pp.429–440,2015.
pp.238–249,2016. [26] A.Internet,“Topsitesinunitedstates,”2020.
[8] N.P.Borges,M.Go´mez,andA.Zeller,“Guidingapptestingwithmined [27] O.Ronneberger,P.Fischer,andT.Brox,“U-net:Convolutionalnetworks
interactionmodels,”inProceedingsofthe5thInternationalConference forbiomedicalimagesegmentation,”inMedicalImageComputingand
onMobileSoftwareEngineeringandSystems,MOBILESoft’18,(New Computer-AssistedIntervention–MICCAI2015(N.Navab,J.Horneg-
York, NY, USA), p. 133–143, Association for Computing Machinery, ger,W.M.Wells,andA.F.Frangi,eds.),(Cham),pp.234–241,Springer
2018. InternationalPublishing,2015.

## Page 12

[28] M.Abadi,P.Barham,J.Chen,Z.Chen,A.Davis,J.Dean,M.Devin,
S.Ghemawat,G.Irving,M.Isard,M.Kudlur,J.Levenberg,R.Monga,
S.Moore,D.G.Murray,B.Steiner,P.Tucker,V.Vasudevan,P.Warden,
M. Wicke, Y. Yu, and X. Zheng, “Tensorflow: A system for large-
scalemachinelearning,”inProceedingsofthe12thUSENIXConference
on Operating Systems Design and Implementation, OSDI’16, (USA),
p.265–283,USENIXAssociation,2016.
[29] S.J.PanandQ.Yang,“Asurveyontransferlearning,”IEEETransac-
tionsonKnowledgeandDataEngineering,vol.22,no.10,pp.1345–
1359,2010.
[30] M. Sandler, A. Howard, M. Zhu, A. Zhmoginov, and L. Chen, “Mo-
bilenetv2:Invertedresidualsandlinearbottlenecks,”in2018IEEE/CVF
Conference on Computer Vision and Pattern Recognition, pp. 4510–
4520,2018.
[31] O. Russakovsky, J. Deng, H. Su, J. Krause, S. Satheesh, S. Ma,
Z. Huang, A. Karpathy, A. Khosla, M. Bernstein, A. C. Berg, and
L. Fei-Fei, “ImageNet Large Scale Visual Recognition Challenge,”
International Journal of Computer Vision (IJCV), vol. 115, no. 3,
pp.211–252,2015.
[32] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion,
O.Grisel,M.Blondel,P.Prettenhofer,R.Weiss,V.Dubourg,J.Vander-
plas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, and E. Duch-
esnay,“Scikit-learn:MachinelearninginPython,”JournalofMachine
LearningResearch,vol.12,pp.2825–2830,2011.
[33] V.Roubtsov,“Emma:afreejavacodecoveragetool,”2006.
[34] Selenium, “The selenium browser automation project.” https://www.
selenium.dev/.
[35] T.Su,G.Meng,Y.Chen,K.Wu,W.Yang,Y.Yao,G.Pu,Y.Liu,and
Z.Su,“Guided,stochasticmodel-basedguitestingofandroidapps,”in
Proceedingsofthe201711thJointMeetingonFoundationsofSoftware
Engineering,pp.245–256,2017.
[36] T. Gu, C. Sun, X. Ma, C. Cao, C. Xu, Y. Yao, Q. Zhang, J. Lu, and
Z.Su,“Practicalguitestingofandroidapplicationsviamodelabstraction
and refinement,” in 2019 IEEE/ACM 41st International Conference on
SoftwareEngineering(ICSE),pp.269–280,IEEE,2019.
[37] Z.Dong,M.Bo¨hme,L.Cojocaru,andA.Roychoudhury,“Time-travel
testing of android apps,” in Proceedings of the 42nd International
ConferenceonSoftwareEngineering(ICSE’20),pp.1–12,2020.
[38] S.Anand,M.Naik,M.J.Harrold,andH.Yang,“Automatedconcolic
testingofsmartphoneapps,”inProceedingsoftheACMSIGSOFT20th
International Symposium on the Foundations of Software Engineering,
pp.1–11,2012.
[39] C. S. Jensen, M. R. Prasad, and A. Møller, “Automated testing with
targetedeventsequencegeneration,”inProceedingsofthe2013Inter-
nationalSymposiumonSoftwareTestingandAnalysis,pp.67–77,2013.
[40] G. Hu, L. Zhu, and J. Yang, “Appflow: using machine learning to
synthesize robust, reusable ui tests,” in Proceedings of the 2018 26th
ACMJointMeetingonEuropeanSoftwareEngineeringConferenceand
SymposiumontheFoundationsofSoftwareEngineering,pp.269–282,
2018.
[41] R. Hay, O. Tripp, and M. Pistoia, “Dynamic detection of inter-
application communication vulnerabilities in android,” in Proceedings
ofthe2015InternationalSymposiumonSoftwareTestingandAnalysis,
pp.118–128,2015.
[42] L. L. Zhang, C.-J. M. Liang, Y. Liu, and E. Chen, “Systematically
testingbackgroundservicesofmobileapps,”in201732ndIEEE/ACM
International Conference on Automated Software Engineering (ASE),
pp.4–15,IEEE,2017.
[43] Y. Li, Z. Yang, Y. Guo, and X. Chen, “Humanoid: A deep learning-
based approach to automated black-box android app testing,” in 2019
34th IEEE/ACM International Conference on Automated Software En-
gineering(ASE),pp.1070–1073,2019.
[44] T.D.White,G.Fraser,andG.J.Brown,“Improvingrandomguitesting
with image-based widget detection,” in Proceedings of the 28th ACM
SIGSOFT International Symposium on Software Testing and Analysis,
ISSTA 2019, (New York, NY, USA), p. 307–317, Association for
ComputingMachinery,2019.
[45] V.Mnih,K.Kavukcuoglu,D.Silver,A.Graves,I.Antonoglou,D.Wier-
stra, and M. A. Riedmiller, “Playing atari with deep reinforcement
learning,”ArXiv,vol.abs/1312.5602,2013.

