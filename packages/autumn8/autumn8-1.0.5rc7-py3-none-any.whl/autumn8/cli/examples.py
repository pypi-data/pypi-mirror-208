from typing import List

# scraped from https://modelzoo.co
# also see modelzoo-scrape.csv
example_model_names = """
OpenPose
Mask R-CNN
pytorch-CycleGAN-and-pix2pix
FastPhotoStyle
vid2vid
maskrcnn-benchmark
DCGAN-tensorflow
deep-image-prior
YOLO TensorFlow ++
Wavenet
PyTorch-GAN
faster-rcnn.pytorch
Deep Reinforcement Learning for Keras
StarGAN
pix2pixHD
albumentations
Augmentor
Open-source (MIT) Neural Machine Translation (NMT) System
Colornet
Image analogies
Deep Video Analytics
semantic-segmentation-pytorch
Chatbot
WassersteinGAN
MUSE
Faster-RCNN
Colorful Image Colorization
DQN-tensorflow
SRGAN
BigGAN-PyTorch
YOLO TensorFlow
pytorch-a2c-ppo-acktr
espnet
DeblurGAN
UNIT
TTS
Neural Sequence labeling model
UnsupervisedMT
faster rcnn
Lip Reading
waveglow
DeepOSM
deepvoice3_pytorch
deepspeech2
pytorch-seq2seq
pytorch-semantic-segmentation
async-RL
Popular Image Segmentation Models
ClassyVision
R-FCN
wgan-gp
sentiment-discovery
EDSR-PyTorch
pointnet.pytorch
DiscoGAN
neuraltalk2-pytorch
AnimeGAN
ChainerRL
Rainbow
Ultrasound nerve segmentation
NVIDIA-semantic-segmentation
chainer-DCGAN
pyannote-audio
loop
audio
Show, Attend and Tell
SLM-Lab
image-classification-mobile
Domain Transfer Network
GAN_stability
espresso
AdverTorch
Seq2seq-Chatbot
SSD
stackGAN-v2
pytorch-rl
DEXTR-PyTorch
jetson-reinforcement
official DiscoGAN implementation
MMDetection3D
Faster RCNN
self-critical.pytorch
seq2seq
RandWireNN
semi-supervised-pytorch
android-yolo
DCSCN Super Resolution
pytorch-maml-rl
speech
PyTorch-progressive_growing_of_gans
Neural Caption Generator
seq2seq.pytorch
cnn-vis
AttGAN
GAN-CLS
T2F
vnet.pytorch
Faster RCNN+Focal Loss
rl_a3c_pytorch
TensorFlow White Paper Notes
generative-models
pspnet-pytorch
vegans
pro_gan_pytorch
detecto
joint-vae
mushroom
nmtpytorch
U-Net
ARAE
gan-lib
MusicGenreClassification
mnist-svhn-transfer
lagom
piwise
pytorch-SRResNet
vedaseg
pytorch-cpp-rl
brain-segmentation-pytorch
pytorch_RVAE
Speech Recognition
Improved Training of Wasserstein GANs
DeconvNet
prog_gans_pytorch_inference
neural-combinatorial-rl-pytorch
img_classification_pk_pytorch
opencv_transforms
PNASNet.pytorch
pix2pix-pytorch
pytorch-trpo(Hessian-vector product version)
DCGAN
**Faster_RCNN_for_DOTA**
AGE
Coupled Face Generation
CNN-LSTM-CTC
BEGAN-pytorch
Neural-IMage-Assessment
tacotron_pytorch
adversarial-autoencoder
samplernn-pytorch
Learning to Communicate with Deep Multi-Agent Reinforcement Learning
RetinaNet
Open Source Chatbot with PyTorch
stitchfix-fauxtograph
Neural-IMage-Assessment 2
nonauto-nmt
torch_waveglow
DeepMask object segmentation
Tacotron-pytorch
GAN-weight-norm
DiffAI
Seg-Uncertainty
deep_image_prior
pytorch-seq2seq-intent-parsing
universal-triggers
Deep-Image-Analogy-PyTorch
Pytorch-DPPO
**MobileNetV2**(TVM Supported)
SVHNClassifier
Aspect-level-sentiment
DAGAN
captionGen
MXNMT
neuron-selectivity-transfer
Mnemonic Descent Method
pytorch-trpo
chainer_examples
bandit-nmt
paysage
adversarial-patch
back2future.pytorch
Image Embedding Learning
wasserstein-gan
Categorical DQN
pytorch_image_classifier
biogans
famos
Improved CycleGAN
RobustBench
MobileNetV2
Pytorch Poetry Generation
**deepspeech**
Unsupervised Object Counting
sparse-structure-selection
Fast Neural Style for Image Style Transform by Pytorch
translagent
vae_vpflows
NVIDIA-unsupervised-video-interpolation
im2im
tgan
chainer_caption_generation
mmd-jmmd-adaBN
google_evolution
mxnet-seq2seq
chainer-dfi
LSGAN
bytenet
AVO-pytorch
ppo_pytorch_cpp
Adaptive-segmentation-mask-attack (ASMA)
Monolingual and Multilingual Image Captioning
Hierarchical Attention Network for Document Classification
mxnet-audio
AEGeAN
imagenet-vgg
improved-gan
chainer-Variational-AutoEncoder
VAE
multilabel
chainer-gan-denoising-feature-matching
**dspnet**
SqeezeNet
AdversarialAutoEncoder
ADDA
SEC
chainer_encoder_decoder
MXSeq2Seq
Ultrasound nerve segmentation
FocalLoss(CUDA)
LSGAN
multi-task
VGAN Tensorflow
L-GM-Loss
chainer_superresolution
Image colorization
Neural Image Caption
unrolled-gan
retrieval chatbot
began
SRCNN
mxnet_kaldi
text2image
chainer-srcnn
SSD+FPN
translatR
Hierarchical Question-Imagee Co-Attention
chainer-gan-trainer
AdversarialCrypto
AdversarialText
AttentionOCR
Audioset
BrainCoder
CognitiveMappinGANPlanning
Compression
DeepSpeech
DeepLab
DELF
GAN
Im2txt
LearningUnsupervisedLearning
LFADS
MaskGAN
ObjectDetection
PCLRL
SLIM
Street
Vid2depth
StyleGAN
Policy Gradient
SegNet and Bayesian SegNet
ResNets
Deep Hand
Inception-BN full ImageNet model
DeepYeast
BVLC AlexNet
BVLC Reference CaffeNet
Detectron
ResNet-50
pytorch-kaldi
detectron2
MMDetection
MMSegmentation
MMEditing
tensorboard-pytorch
gandissect
tensorwatch
rlpyt
PyTorch-VAE
ray
InfoGAN
pix2pix
Colorful Image colorization
Auxiliary Classifier GAN
Adversarial Autoencoder
Bidirectional GAN
Boundary-Seeking GAN
Conditional GAN
Context-Conditional GAN
Coupled GANs
CycleGAN
Deep Convolutional GAN
DiscoGAN
DualGAN
Generative Adversarial Network
InfoGAN
LSGAN
Pix2Pix
PixelDA
Semi-Supervised GAN
Super-Resolution GAN
Wasserstein GAN
Wasserstein GAN GP
Adversarial Auto-encoders
DCGAN
DCGAN face generation
Variational Autoencoder with deconvolutions
t-SNE of image CNN fc7 activations
pytorch-pretrained-BERT
Magenta
Kubeflow
Kaldi
flair
AllenNLP
Faster R-CNN
fairseq-py
pyro
pytext
**InsightFace**
DensePose
Sentence Classification with CNN
Neural Style
pytorch vision
Realtime Multi-Person Pose Estimation
denseNet
CapsNet-Tensorflow
Reading Wikipedia to Answer Open-Domain Questions
face-alignment
AlphaPose
Tensorflow-Project-Template
Striving for Simplicity
BERT-PyTorch
Minigo
Single Shot MultiBox Detector
**Faster RCNN+Deeplab+R-FCN+Deformable-ConvNets+FPN+SoftNMS**
pythia
OpenPose TensorFlow
Fast R-CNN
Detectron.pytorch
yolov3
DeepJazz
Neural Style
CapsNet-Keras
CIFAR-10 on Pytorch with VGG, ResNet and DenseNet
Transformer-XL
3DDFA
LASER
pytorch text
TCN
pygcn
SqueezeNet
pytorch-generative-model-collections
Mask R-CNN
InferSent
XLM
pytorch-playground
neuralcoref
Person-reID_pytorch
Neural Style Transfer
FCIS
Averaged Stochastic Gradient Descent with Weight Dropped LSTM
FlowNet 2.0
PyTorch-NLP
style-transfer
kornia
pytorch-faster-rcnn
Data Augmentation and Sampling for Pytorch
CRF-RNN
ChainerCV
YOLO2
end-to-end-negotiator
Pretty Tensor
poincare-embeddings
tacotron2
Center Loss
pytorch-openai-transformer-lm
Deep Feature Flow
pytorch-qrnn
efficient_densenet_pytorch
Single Shot MultiBox Detector
attention-transfer
higher
Neural Turing Machine in TensorFlow
hub
Dilated ResNet combination with Dilated Convolutions
deep-head-pose
MinkowskiEngine
**sockeye**
TensorNets
Human Pose Estimation with TensorFlow
CapsGNN
inplace_abn
pytorch-retinanet
pytorch-yolo2
Realtime_Multi-Person_Pose_Estimation
SparseConvNet
redner
pytorch-fcn
Mask-RCNN
torchstat
pytorch-pose
Video Frame Interpolation via Adaptive Separable Convolution
pytorch-toolbelt
tsn-pytorch
pytorch-struct
Cnn-text classification
jiant
RepDistiller
cvxpylayers
grad-cam
pytorch-deform-conv
bindsnet
yusuketomoto-chainer-fast-neuralstyle
torchMoji
BERT-NER
LM-LSTM-CRF
CNN visualization using Tensorflow
probtorch
Character-Aware Neural Language Models
pytorch-pruning
medicaltorch
MTCNN (original detector)
pytorch-wavenet
SfmLearner-Pytorch
pytorch - fid
Generative Handwriting Demo using TensorFlow
CrypTen
densenet
CondenseNet
FaceBoxes.PyTorch
translate
PyTorch-Style-Transfer
PVANet
voicefilter
bottom-up-attention-vqa
Flow-Guided Feature Aggregation
NCRF
pytorch2keras
pytorch-cnn-finetune
Convolutional LSTM Network
texar-pytorch
sphereface_pytorch
extension-cpp
euclidesdb
MTCNN
pytorch-capsule
breast_cancer_classifier
flownet
gpt-2-Pytorch
graphsage-simple
vqa.pytorch
torchbearer
pytorch-deeplab-resnet
DiracNets
Wide ResNet model in PyTorch
illustration2vec
DUC
MXNet Face
Deep-Compression-AlexNet
DPN
YOLO in caffe
torchgpipe
pytorch2caffe
FlashTorch
pytorch-pose-hg-3d
ResNet
matchbox
ClusterGCN
NeuralArt
convert_torch_to_pytorch
Random-Erasing
Visual question answering
attn2d
RoIAlign.pytorch
STN OCR
torchbeast
treelstm.pytorch
MMPose
SMASH
torchprof
Structured-Self-Attention
qp solver
Arnold
ConvE
pytorch-ntm
ban-vqa
pytorch-dense-correspondence
pytorch-maml
CapsNet-pytorch
pytorch-made
MMAction2
colorization-pytorch
trellisnet
yolo2-pytorch
pytorch-coviar
pytorch-flows
pytoune
Poutyne
ResNeXt.pytorch
STEAL
A Structured Self-Attentive Sentence Embedding
FlappyBird DQN
deformable-convolution-pytorch
Xlearn
pixyz
honk
Shufflenet-v2-Pytorch
DrQA
GraphWaveletNeuralNetwork
DeepPose
wavetorch
densebody_pytorch
geoopt
lightly
Pytorch-contrib
torch2coreml
optnet
fast-neural-style
NGCN
NGCN
Weakly_detector
magnet
BMXNet
ggnn.pytorch
tbd-nets
YOLOv2
vsepp
CoordConv-pytorch
deepfloat
pytorch-i-revnet
QANet-pytorch
ResNet-38
TripletLoss(FaceNet)
SimGNN
PyTorch-LBFGS
pyvarinf
pywick
pytorch_cluster
gogh
pytorch-es
PytorchNeuralStyleTransfer
R2Plus1D-PyTorch
gensen
generative-query-network-pytorch
YellowFin_Pytorch
Face_Attention_Network
nonechucks
Tensorflow FastText
pytorch_fft
Pytorch Geometric Temporal
transfer-nlp
Snapshot Ensembles
faster-rcnn
HMM in TensorFlow
OpenChem
RetinaNet
pyscatwave
GradientEpisodicMemory
quick-nlp
pytorch-explain-black-box
graph_convnets_pytorch
pytorch-dqn
Learning to learn by gradient descent by gradient descent
ClariNet
vel
GrouPy
neural-art-mini
pyinn
pytorch-dnc
nmp_qc
AttentionWalk
NLP-Caffe
dnc
webdataset
pytorch-sgns
caffemodel2pytorch
glow-pytorch
context_encoder_pytorch
neural-style-pt
MTCNN_face_detection_alignment
salad
WideResNets
Neural programmer-interpreter
YOLO-YOLOv2
SFD_pytorch
relational-rnn-pytorch
PyramidNet-PyTorch
inferno
Mask R-CNN
LearningToCompare-Pytorch
Pytorch-Toolbox
fusenet
flambe
pytorch-hessian-eigenthings
DeepRL-Grounding
pytorch-tools
FewShotLearning
GAM
APPNP
dni-pytorch
Skip-Thought Vectors
DQN
TuckER
Lucent
VIN_PyTorch_Visdom
pydlt
Visual Search
fcn
ORN
PyTorch Realtime Multi-Person Pose Estimation
ChainerMN
torchani
DQN-chainer
AccSGD
DQN
Character CNN
FreezeOut
pytorch-transformer
pytorch_compact_bilinear_pooling v1
PyTorchWavelets
beauty-net
Pytorch-NCE
VGG-CAM
NALU-pytorch
Optical Flow Estimation using a Spatial Pyramid Network
pt-dilate-rnn
pywarm
sparktorch
HCN-pytorch
VRNN
pytorch-zssr
mpl.pytorch
packnet
DCC
C3D
volksdep
dockerface
pytorch-text-recognition
odin-pytorch
SGCN
DRRN-pytorch
Splitter
chainer-char-rnn
pytorch-retraining
SEAL-CI
OpenFacePytorch
vqa-winner-cvprw-2017
ChainerUI
simple-effective-text-matching-pytorch
torch-two-sample
DeepCORAL
convnet-aig
fmpytorch
hessian
DGC-Net
Real-time style transfer
SENet
crnn-mxnet-chinese-text-recognition
UntrimmedNets
caffe_to_torch_to_pytorch
mctorch
MobileNet
Attentive Object Tracking
fenchel-young-losses
FractalNet
Pytorch-Sketch-RNN
Attentive Recurrent Comparators
QuCumber
pytorch-pose-estimation
skip-gram-pytorch
FCN-pytorch-easiest
CompactBilinearPooling-Pytorch v2
StackNN
bigBatch
piggyback
Smile detection with a CNN
FaceDetection-ConvNet-3D
DeepPose TensorFlow
neural style transfer
FCNT
e2e-model-learning
cifar10
GoogleNet-V2
AOGNet
pytorch-prunes
transducer
DeepBox
pix2pix
CNN-LSTM-CTC
deep-forecast-pytorch
logger
Realtime Multi-Person Pose Estimation
deep-auto-punctuation
DenseNet
pytorch-sift
doomnet
binary-wide-resnet
DSSD+TDM
pytorch_NEG_loss
Draw like Bob Ross
DepthNet
NoisyNaturalGradient
pytorch-smoothgrad
SRDenseNet-pytorch
NALU
macarico
PySNN
RNN-Transducer
EigenDamage-Pytorch
mixup_pytorch
Probabilistic Programming and Statistical Inference in PyTorch
A3C-PyTorch
lang-emerge-parlai
nmn-pytorch
MSG-Net
dni
distance-encoding
Head Pose
meProp
ewc.pytorch
minimal_glo
binary_net
TDD
PyTorch_GBW_LM
Torchelie
interaction_network_pytorch
mixup
Tiny Face (original detector)
rl-multishot-reid
wavenet
deep-dream-in-pytorch
Whale Detector
pytorch-extension
SSD Text Detection
pytorch-NeuCom
pytorch-mcn
FFTNet
NASNet-A-Mobile. Ported weights
integrated-gradient-pytorch
mxnet-model
PSPNet
E2FAR
EPSR
Neural-Style-MMD
Ladder Network
pytorch-fitmodule
cogitare
**CTPN.mxnet**
imsat
molencoder
scalingscattering
pytorch_TDNN
nninit
sqeezenet
quantile-regression-dqn-pytorch
torchcraft-py
kaggle_CIFAR10
LOLA_DiCE
SINE
forward-thinking-pytorch
CNN Based Text Classification
graph-cnn
chainer-ssd
pytorch_Highway
pytorch-nec
Factorized-Bilinear-Network
candlegp
aorun
DRQN
Faster RCNN
DAGGER
Char-RNN
Highway Network
shampoo.pytorch
pnn.pytorch
chainer-visualization
neural-dream
**Gluon Dynamic-batching**
chainer-ResNet
Tor10
chainer-gogh
binary-stochastic-neurons
mia
Yelp Restaurant Photo Classifacation
ko_en_NMT
psmm
dpwa
MXNet for CTR
generative_zoo
pytorch extras
DarkRank
crnn
LSTNet
fast-rcnn
cat-net
CRU-Net
CortexNet
crnn (with Chinese Support)
CDL
Deep-Leafsnap
reseg-pytorch
diffdist
TRPO
mxnet-videoio
ram
MalConv-Pytorch
fluidnet_cxx
osqpth
simple-fast-rnn
ShuffleNet
segnet
mlpnlp-nmt
segnet
FacialLandmark
chainer-ResDrop
AlexNet3D
StrassenNets
chainer-DenseNet
proxprop
pytorch-ctc
siamese
pyTorch_NCE
Character-level CNN Text Classification
e2c-pytorch
flow
pytorch_hmax
LSTM to predict gender of a name
torch-metrics
Torchlite
netharn
eve.pytorch
YOLO
U-Net
chainer_stylenet
CapsNet
pt-styletransfer
zalando-pytorch
poisson-convolution-sum
PyTorch-docset
neural-assembly-compiler
pytorch-cns
svm
OrthNet
VanillaCNN
Convolutional Neural Fabrics
lgamma
NonLocal+SENet
SSD+Focal Loss
Deeplab v2
OpenPose
sentiment-analysis
Traffic sign classification
galapagos_nao
variational-autoencoder
AC-BLSTM
anuvada
Xception
SqueezeDet
wavenet
pyprob
DeepHumanPrediction
Sequential Matching Network
Visual-Semantic Embedding
YOLO-dark2mxnet
mx-pointnet
DEF
conv-vis
U-Net(kaggle dstl)
PointCNN.MX
VQA
Tiny Face (w. training)
siamese
Language dialect identification with multiple character-level CNNs
SDPoint
Zero-shot Intent CapsNet
P3D
SpectralLDA
memnn
chainer-example-overfeat-classify
YOLOtiny_v2
LightCNN
cnn+Highway Net
cascade-rcnn-gluon
MemN2N
deformable-conv
Tacotron
st-resnet
siamese_network_on_omniglot
mxnet-recommender
chainer_ca
torchplus
Xception+Keras2MXNet
VisualBackProp
Range Loss
RangeLoss
fast-style-transfer
chainer_rnnlm
vat
SuperResolutionCNN
Chest-XRay
SENet(from Caffe)
Convolutional Sketch Inversion
parserChiang
NER with Bidirectional LSTM-CNNs
PPO
prednet
adgm
Convolutional Pose Machines
Dynamic pose estimation
Reinspect
NetVlad
IMSAT
LUCAD
openai-mxnet
mnist-oneshot
VQA
geometric-matching
collaborative_filtering
chainer-fluid
ddgm
delira
FractalNet
IOULoss
cicada classification
DPSH
MemN2N
Neural Programmer-Interpreters
sequence-sampling
minibatch_discrimination
Autoencoder
DeepContextualBandits
DifferentialPrivacy
DomainAdaptation
Inception
KeypointNet
LearningToRememberRareEvents
LexNetc
LM1B
LmCommonsense
Namignizer
NeuralGpu
NeuralProgrammer
NextFramePrediction
PTN
MARCO
QAKG
RealNvp
REBAR
ResNet
Seq2species
SkipThoughts
Swivel
SyntaxNet
TCN
Textsum
Transformer
VideoPrediction
Deep Q-Network
AC
A3C
Network in Network model
Places-CNN model from MIT.
GoogLeNet GPU implementation from Princeton.
ParseNet
Holistically-Nested Edge Detection
VGG Face CNN descriptor
Yearbook Photo Dating
CCNN
Faster R-CNN
Sequence to Sequence - Video to Text
Pascal VOC 2012 Multilabel Classification Model
SqueezeNet
Mixture DCNN
Mulimodal Compact Bilinear Pooling for VQA
Neural Activation Constellations
ResFace101
Striving for Simplicity
VGG 4x without degradation
Using Ranking-CNN for Age Estimation
SSD
BVLC GoogLeNet
BVLC Reference RCNN ILSVRC13
DenseNet-121
Inception v1
SqueezeNet
ZFNet-512
NeMo
transformers
reformer-pytorch
TorchCV
facenet-pytorch
pytorch3d
botorch
pretrained-models.pytorch
gpytorch
spotlight
inferno-sklearn
PyTorch-Encoding
skorch
ignite
simple-faster-rcnn-pytorch
pytorchviz
pytorch-summary
apex
ELF
pytorch_geometric
fastai
gpytorch
QNNPACK
torchdiffeq
dgl
torchgeometry
AdaBound
pytorch-OpCounter
Catalyst
Ax
pytorch-lightning
learn2learn
kaolin
pytorch-metric-learning
pytorch-optimizer
EfficientNet PyTorch
PyTorch-XLA
NVlabs-DG-Net
pulse
Self-Norm Nets
LSTM for HAR
pix2pix
DIRNet
DFI
Context Encoder
chainer_examples
qrnn
chainer-libDNN
Face68Pts
VGG16 Deconvolution network
mxnet_tetris
**gluon-nlp**
SegNet
VGG 16 (with pre-trained weights)
VGG 19 (with pre-trained weights)
DQN
GluonSeg
Double DQN
matchnet
DeepID v1
C3D
DRL
cnnbilstm
NASNet-A
FCN-ASPP
Deep-Q learning Pong with TensorFlow and PyGame
DeepLab
VGG-Face
LRCN
SRCNN
DeepDrive
Berkeley DeepDrive
Princeton deepdriving
Sentiment Analysis
AlexNet
Inception v2
StyleTransfer
VGG19
Multi-GPU Multi-Label DenseNet
Light-Head R-CNN
Segnet
EAST
RC3D
Receptive Field Tool
LSTM on the IMDB dataset (text sentiment classification)
Bidirectional LSTM on the IMDB dataset
1D CNN on the IMDB dataset
1D CNN-LSTM on the IMDB dataset
LSTM-based network on the bAbI dataset
Memory network on the bAbI dataset (reading comprehension question answering)
LSTM text generation
Using pre-trained word embeddings
FastText on the IMDB dataset
Simple CNN on MNIST
Simple CNN on CIFAR10 with data augmentation
Inception v3
Neural Style Transfer
Deep dreams
Stateful LSTM
Siamese network
Pretraining on a different dataset
s2cnn
""".split(
    "\n"
)
