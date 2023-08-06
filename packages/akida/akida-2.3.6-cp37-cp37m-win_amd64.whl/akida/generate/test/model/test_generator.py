import os
import json
from pathlib import Path

from ...application_generator import ApplicationGenerator
from ...array_to_cpp import array_to_cpp
from ..template import test_file_from_template


class ModelTestGenerator(ApplicationGenerator):

    def generate(self, test_name, dest_path):
        """Generate model test application files
        """
        model = self.model()
        inputs = self.inputs()
        outputs = self.outputs()
        dest_dir = os.path.join(dest_path, test_name)
        # Generate source arrays
        if model is not None:
            model_buffer = model.to_buffer()
            array_to_cpp(dest_dir, model_buffer, "model")
            with open(dest_dir + '/model.json', 'w') as file:
                file.write(model.to_json())
            tpl_path = os.path.join(Path(__file__).parent, "app_templates")
            # Write test files
            test_file_from_template(test_name, tpl_path, dest_path, "test.h")
            test_file_from_template(
                test_name, tpl_path, dest_path, "test.cpp")
        if inputs is not None:
            array_to_cpp(dest_dir, inputs, "inputs")
            with open(dest_dir + '/inputs.json', 'w') as file:
                json.dump(inputs.tolist(), file)
        if outputs is not None:
            array_to_cpp(dest_dir, outputs, "outputs")
            with open(dest_dir + '/outputs.json', 'w') as file:
                json.dump(outputs.tolist(), file)
