from sklearn import datasets, svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score

from cortex_cli.core.models.cortex_model import CortexModel


class {{cookiecutter.__model_class}}(CortexModel):
    def transform_data(self):
        # Load data
        self.digits = datasets.load_digits()

        # Preprocess dataset
        n_samples = len(self.digits.images)
        flattened_images = self.digits.images.reshape((n_samples, -1))

        # Split data into 50% train and 50% test subsets
        X_train, X_test, y_train, y_test = train_test_split(
            flattened_images,
            self.digits.target,
            test_size=0.5,
            shuffle=False,
        )

        # Store data
        self.split_data = {
            'train': {'X': X_train, 'y': y_train},
            'test': {'X': X_test, 'y': y_test},
        }

        # Setup example inputs and outputs
        self._set_input_output_examples(X_train, y_train)


    def fit(self):
        # Get parameters. Note that they are already on the server,
        # so no need to call mlflow.log_param() to track them
        try:
            gamma = float(self.params['gamma'])
        except Exception as e:
            gamma = 0.001

        # Create a classifier: a support vector classifier
        self.classifier = svm.SVC(gamma=gamma)

        # Learn the digits on the train subset
        self.classifier = self.classifier.fit(
            self.split_data['train']['X'],
            self.split_data['train']['y']
        )


    def predict(self, model_inputs):
        # Predict the value of the digit on the provided data
        predicted = self.classifier.predict(model_inputs)
        return predicted


    def evaluate(self):
        # Predict the value of the digit on the test subset
        predicted = self.classifier.predict(self.split_data['test']['X'])

        # Compute some scores
        self._add_metric('accuracy', accuracy_score(self.split_data['test']['y'], predicted))
        self._add_metric('precision', precision_score(self.split_data['test']['y'], predicted, average='weighted'))
        self._add_metric('recall', recall_score(self.split_data['test']['y'], predicted, average='weighted'))
        return self.metrics
