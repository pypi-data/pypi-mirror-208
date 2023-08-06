# Tri-Model Ensemble System for Classification

Under heavy development and research

Developed by Arkitech(Joshua Tan)

## Examples of usage

Create a config file:

```python
from TriModelSystem.utils import create_config

create_config()
```

Training a RMSprop-Adadelta binary classification model:
```python
from TriModelSystem.binclassification import rms_adadelta_model

example_input_shape = (24,)
model = rms_adadelta_model(input_shape=example_input_shape)
TriModelSystem.fit(x=[train_features, train_features], 
                   y=train_labels_encoded, 
                   batch_size=batch_size, 
                   epochs=epochs, 
                   validation_data=([test_features, test_features], test_labels_encoded))
```