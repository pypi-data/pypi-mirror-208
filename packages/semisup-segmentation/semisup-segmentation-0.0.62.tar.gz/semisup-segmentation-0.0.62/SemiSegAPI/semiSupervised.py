from SemiSegAPI.utils import *
from fastai.vision.all import *
import shutil
import os

def dataDistillation(baseModel, baseBackbone, targetModel, targetBackbone, transforms, path, pathUnlabelled, outputPath, bs=32, size=(480,640)):
    if not testNameModel(baseModel):
        print("The base model selected is not valid")
    elif not testNameModel(targetModel):
        print("The target model selected is not valid")
    elif not testPath(path):
        print("The path is invalid or has an invalid structure")
    elif not testTransforms(transforms):
        print("There are invalid transforms")
    else:
        # Load images
        dls = get_dls(path, size, bs=bs)
        nClasses=numClasses(path)

        learn = getLearner(baseModel,baseBackbone,nClasses,path,dls)

        # Train base learner
        print("Start of base model training")
        train_learner(learn, 50, freeze_epochs=2)
        learn.save(baseModel)

        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        shutil.copy(path + os.sep + 'models' + os.sep + baseModel + '.pth',
                    outputPath + os.sep + 'base_' + baseModel + '.pth')

        # supervised method
        print("Start of annotation")
        omniData(path, pathUnlabelled, learn, transforms,size)
        print("End of annotation")

        # Load new images
        dls2 = get_dls(path, size, bs=bs)

        # Load base model
        learn2 = getLearner(targetModel, targetBackbone, nClasses, path + '_tmp', dls2)

        # Train base learner
        print("Start of target model training")
        train_learner(learn2, 50, freeze_epochs=2)
        learn2.save(targetModel)
        shutil.copy(path + '_tmp' + os.sep + 'models' + os.sep + targetModel + '.pth',
                    outputPath + os.sep + 'target_' + targetModel + '.pth')
        shutil.rmtree(path + '_tmp')


def modelDistillation(baseModels, baseBackbones, targetModel, targetBackbone, path, pathUnlabelled, outputPath, bs=32, size=(480,640)):
    for baseModel in baseModels:
        if not testNameModel(baseModel):
            print("The base model selected is not valid")
            return
    if not testNameModel(targetModel):
        print("The target model selected is not valid")
    elif not testPath(path):
        print("The path is invalid or has an invalid structure")
    else:
        # Load images

        nClasses = numClasses(path)



        # Load base model
        learners=[]
        print("Start of base models training")
        for i,baseModel in enumerate(baseModels):
            dls = get_dls(path, size, bs=bs)
            learn = getLearner(baseModel, baseBackbones[i], nClasses, path, dls)


            # Train base learner
            train_learner(learn, 50, freeze_epochs=2)
            # learn.fine_tune(50, freeze_epochs=2)
            learn.save(baseModel)
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
            shutil.copy(path + os.sep + 'models' + os.sep + baseModel + '.pth',
                        outputPath + os.sep + 'base_' + baseModel + '.pth')
            learners.append(learn)


        # supervised method
        print("Start of annotation")
        omniModel(path, pathUnlabelled, learners,size)
        print("End of annotation")

        # Load new images
        dls2 = get_dls(path, size, bs=bs)

        # Load base model
        learn2 = getLearner(targetModel, targetBackbone, nClasses, path + '_tmp', dls2)

        # Train base learner
        print("Start of target model training")
        train_learner(learn2, 50, freeze_epochs=2)
        # learn2.fine_tune(50, freeze_epochs=2)
        learn2.save(targetModel)
        shutil.copy(path + '_tmp' + os.sep + 'models' + os.sep + targetModel + '.pth',
                    outputPath + os.sep + 'target_' + targetModel + '.pth')
        shutil.rmtree(path + '_tmp')


def modelDataDistillation(baseModels, baseBackbones, targetModel, targetBackbone, transforms, path, pathUnlabelled, outputPath, bs=32, size=(480,640)):
    for baseModel in baseModels:
        if not testNameModel(baseModel):
            print("The base model selected is not valid")
            return
    if not testNameModel(targetModel):
        print("The target model selected is not valid")
    elif not testPath(path):
        print("The path is invalid or has an invalid structure")
    elif not testTransforms(transforms):
        print("There are invalid transforms")
    else:
        nClasses = numClasses(path)

        # Load images
        learners=[]
        print("Start of base models training")
        for i,baseModel in enumerate(baseModels):
            dls = get_dls(path, size, bs=bs)
            learn = getLearner(baseModel, baseBackbones[i], nClasses, path, dls)

            # Train base learner
            train_learner(learn, 50, freeze_epochs=2)
            # learn.fine_tune(50, freeze_epochs=2)
            learn.save(baseModel)
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
            shutil.copy(path + os.sep + 'models' + os.sep + baseModel + '.pth',
                        outputPath + os.sep + 'base_' + baseModel + '.pth')
            learners.append(learn)

        # supervised method
        print("Start of annotation")
        omniModelData(path, pathUnlabelled, learners, transforms,size)
        print("End of annotation")

        # Load new images
        dls2 = get_dls(path, size, bs=bs)

        # Load base model
        learn2 = getLearner(targetModel, targetBackbone, nClasses, path + '_tmp', dls2)

        # Train base learner
        print("Start of target model training")
        train_learner(learn2, 50, freeze_epochs=2)
        # learn2.fine_tune(50, freeze_epochs=2)
        learn2.save(targetModel)
        shutil.copy(path + '_tmp' + os.sep + 'models' + os.sep + targetModel + '.pth',
                    outputPath + os.sep + 'target_' + targetModel + '.pth')
        shutil.rmtree(path + '_tmp')

def simpleTraining(baseModel, baseBackbone, path, outputPath, bs=32, size=(480,640)):
    if not testNameModel(baseModel):
        print("The base model selected is not valid")
    elif not testPath(path):
        print("The path is invalid or has an invalid structure")
    else:
        # Load images
        dls = get_dls(path, size, bs=bs)
        nClasses = numClasses(path)
        learn = getLearner(baseModel, baseBackbone, nClasses, path, dls)

        # Train base learner
        print("Start of model training")
        train_learner(learn, 50, freeze_epochs=2)
        # learn.fine_tune(50, freeze_epochs=2)
        learn.save(baseModel)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        shutil.copy(path+os.sep+'models'+os.sep+baseModel+'.pth',outputPath+os.sep+'target_'+baseModel+'.pth')
