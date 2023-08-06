from keras.layers import Input, Dense, Dropout, concatenate
from keras.models import Model
from keras.optimizers import RMSprop, Adadelta, Adam
from keras import regularizers
from utils import get_model_data


def rms_adadelta_model(input_shape):
    model_A_data = get_model_data(mode='A')
    model_B_data = get_model_data(mode='B')
    model_C_data = get_model_data(mode='C')

    modelAInput = Input(shape=input_shape)
    modelADense1 = Dense(model_A_data[0], activation='ELU', kernel_regularizer=regularizers.l2(model_A_data[3]))(modelAInput)
    modelADropout1 = Dropout(model_A_data[1])(modelADense1)
    modelADense2 = Dense(model_A_data[0], activation='LeakyReLU')(modelADropout1)
    modelADropout2 = Dropout(model_A_data[1])(modelADense2)
    modelADense3 = Dense(model_A_data[0], activation='LeakyReLU')(modelADropout2)
    modelADropout3 = Dropout(model_A_data[1])(modelADense3)
    modelADense4 = Dense(model_A_data[0], activation='ELU', kernel_regularizer=regularizers.l2(model_A_data[3]))(modelADropout3)
    modelADropout4 = Dropout(model_A_data[1])(modelADense4)
    modelAOutput = Dense(1, activation='sigmoid')(modelADropout4)

    modelA = Model(modelAInput, modelAOutput, name="ModelA")
    modelAOptimizer = RMSprop(learning_rate=model_A_data[2])
    modelA.compile(optimizer=modelAOptimizer, loss='binary_crossentropy', metrics=['accuracy'])

    modelBInput = Input(shape=input_shape)
    modelBDense1 = Dense(model_B_data[0], activation='ELU', kernel_regularizer=regularizers.l2(model_B_data[3]))(modelBInput)
    modelBDropout1 = Dropout(model_B_data[1])(modelBDense1)
    modelBDense2 = Dense(model_B_data[0] / 2, activation='ELU')(modelBDropout1)
    modelBDropout2 = Dropout(model_B_data[1])(modelBDense2)
    modelBDense3 = Dense(model_B_data[0] / 2, activation='ELU')(modelBDropout2)
    modelBDropout3 = Dropout(model_B_data[1])(modelBDense3)
    modelBDense4 = Dense(model_B_data[0], activation='ELU', kernel_regularizer=regularizers.l2(model_B_data[3]))(modelBDropout3)
    modelBDropout4 = Dropout(model_B_data[1])(modelBDense4)
    modelBOutput = Dense(1, activation='sigmoid')(modelBDropout4)

    modelB = Model(modelBInput, modelBOutput, name="ModelB")
    modelBOptimizer = Adadelta(learning_rate=model_B_data[2])
    modelB.compile(optimizer=modelBOptimizer, loss='binary_crossentropy', metrics=['accuracy'])

    modelCInput1 = modelA.output
    modelCInput2 = modelB.output
    modelCInput = concatenate([modelCInput1, modelCInput2], axis=1)
    modelCDense1 = Dense(model_C_data[0], activation='ELU', kernel_regularizer=regularizers.l2(model_C_data[3]))(modelCInput)
    modelCDropout1 = Dropout(model_C_data[1])(modelCDense1)
    modelCDense2 = Dense(model_C_data[0], activation='ELU')(modelCDropout1)
    modelCDropout2 = Dropout(model_C_data[1])(modelCDense2)
    modelCDense3 = Dense(model_C_data[0], activation='ELU')(modelCDropout2)
    modelCDropout3 = Dropout(model_C_data[1])(modelCDense3)
    modelCDense4 = Dense(model_C_data[0], activation='ELU', kernel_regularizer=regularizers.l2(model_C_data[3]))(modelCDropout3)
    modelCDropout4 = Dropout(model_C_data[1])(modelCDense4)
    modelCOutput = Dense(1, activation='sigmoid')(modelCDropout4)

    TriModelSystem = Model([modelA.input, modelB.input], modelCOutput, name="ModelC")
    modelCOptimizer = Adam(learning_rate=model_C_data[2])
    TriModelSystem.compile(optimizer=modelCOptimizer, loss='binary_crossentropy', metrics=['accuracy'])

    TriModelSystem.summary()
    return TriModelSystem
