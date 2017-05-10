from keras.models import Sequential
from keras.layers import Conv2D, Activation, MaxPool2D, Dropout, Flatten, Dense, AvgPool2D

import numpy as np
import dataset
import networks

from evaluation import precision, recall, f1_score

################################################################################

import argparse
parser = argparse.ArgumentParser()

parser.add_argument("--data", action="store", dest="data",
                    default="tmp/data.h5")

parser.add_argument("--model", action="store", dest="model",
                    default="models/model.h5")

parser.add_argument("--batch", action="store", dest="batch_size",
                    default=64, type=int)

parser.add_argument("--epochs", action="store", dest="epochs",
                    default=10, type=int)

parser.add_argument("--samples", action="store", dest="samples",
                    default=100000, type=int)

parser.add_argument("--samples_val", action="store", dest="samples_val",
                    default=10000, type=int)

parser.add_argument("--area", action="store", dest="area_size",
                    default=25, type=int)

parser.add_argument("--queue", action="store", dest="queue_size",
                    default=50, type=int)

args = parser.parse_args()

args.steps_per_epoch = args.samples // args.batch_size
args.steps_per_val = args.samples_val // args.batch_size

################################################################################

def main():
    print("initialize training generator")
    train_gen = dataset.patchGeneratorFromH5(args.data,
                                             size=args.area_size,
                                             batch_size=args.batch_size,
                                             p=0.2)
    print("initialize validation generator")
    val_gen = dataset.patchGeneratorFromH5(args.data,
                                           size=args.area_size,
                                           batch_size=args.batch_size,
                                           p=0.01)
    print("get network")
    model = networks.getRenesNetwork(args.area_size)
    print("compile")
    model.compile(optimizer="adam",
                  loss="binary_crossentropy",
                  metrics=["accuracy", precision, recall, f1_score])
    print("start training")
    model.fit_generator(train_gen,
                        steps_per_epoch=args.steps_per_epoch,
                        epochs=args.epochs,
                        validation_data=val_gen,
                        validation_steps=args.steps_per_val,
                        verbose=True,
                        max_q_size=args.queue_size,
                        workers=1)
    print("store model")
    model.save(args.model)

from keras.models import load_model
import evaluation

def evaluate_model():
    model = load_model("model.h5", custom_objects={"precision": precision,
                                                   "recall": recall,
                                                   "f1_score": f1_score})
    evaluation.evaluate_model(model, 25)

if __name__ == "__main__":
    main()
    #evaluate_model()
    pass
