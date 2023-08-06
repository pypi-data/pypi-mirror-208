# Build a model from scratch

## Build a new model

* **Architecture**: The architecture of a model is the arrangement and connection of its layers. Unet or Linknet are good starting architectures. The architecture of a CNN is divided into an encoder (the 'eyes' of the model, that extract features of the input image) and a decoder (a network that produces the desired output from the detected features).
* **Backbone**: Set the model encoder (the 'eyes'/feature extracting part of the network).
* **Input width**: Often optional (keep it to None if the model works with any image size). Select the model input layer width (keep it low, to avoid memory errors).
* **Input height**: Often optional (keep it to None if the model works with any image size). Select the model input layer height (keep it low, to avoid memory errors).
* **Input channels**: Select the number of channels of the input layer of the model (it needs not be the number of channels of the input images, it is the number of channels the model should learn from).
* **Activation layer**: Choose an activation to be applied to the last layer of the model (sigmoid is a good choice for generating binary images, i.e. a segmentation masks).
* **Number of classes**: Select the number of outputs the model should predict.

## Model weights

* Optional: you can load weights to be applied to the model (the architecture of the model and the weights must match one to one or an error will occur). Usually model weigths are provided as a .h5 file.

## Create the model

* Press 'Go' to build the model (Note that building a model can take a lot of time, up to several minutes so please be patient).