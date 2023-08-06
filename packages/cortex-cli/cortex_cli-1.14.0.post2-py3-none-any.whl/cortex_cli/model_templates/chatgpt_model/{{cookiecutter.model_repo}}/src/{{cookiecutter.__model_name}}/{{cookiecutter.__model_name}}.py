import numpy as np
import pandas as pd
import openai

from cortex_cli.core.models.cortex_model import CortexModel


class {{cookiecutter.__model_class}}(CortexModel):
    def initialize(self):
        self.setup_openai_access()

        input_example = pd.DataFrame({'Role': ['system'], 'Message': ['This is a test input']})

        self._set_input_output_examples(
            input_example, 
            np.array(['This is a test output'])
        )

        return 'ChatGPT model initialized successfully'


    def predict(self, model_inputs):
        self.setup_openai_access()

        response = 'Unable to complete the request to ChatGPT.'
        try:
            messages = []
            if self.params and self.params['initial_prompt']:
                messages.append({'role': 'system', 'content': self.params['initial_prompt']})
            
            model_inputs['OpenAI Format'] = model_inputs.apply(lambda x: dict({'role': str(x['Role']), 'content': str(x['Message'])}), axis=1)
            messages.extend(model_inputs['OpenAI Format'])

            response = openai.ChatCompletion.create(
                model    = self.params['model'],
                messages = messages
            )

            response = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            # Returns the error message as an inference response
            return np.array(str(e))

        return np.array(response)


    def setup_openai_access(self):
        if openai.api_key is None:
            openai.api_key = self.secrets_manager.get_secret('OPENAI_TOKEN')
