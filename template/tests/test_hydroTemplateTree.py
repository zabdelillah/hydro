from unittest import TestCase
from template import *
import os

hydro_template_schema_file = os.path.join(
    os.path.dirname(__file__),
    'test_template_schema.yml'
)

class TestHydroTemplateTree(TestCase):
    def setUp(self):
        self.hydro_template_tree = HydroTemplateTree(hydro_template_schema_file)
        self.hydro_template_tree_without_schema = HydroTemplateTree()

    def test__load_template_tree_without_template_schema_file(self):
        self.assertRaises(HydroTemplateSchemaFileNotSpecifiedException,
                          self.hydro_template_tree_without_schema._load_template_tree)

    def test__load_template_tree_with_template_schema_file_no_exception(self):
        self.assertTrue(self.hydro_template_tree._load_template_tree)

    def test__process_template_tree(self):
        self.assertTrue(self.hydro_template_tree._process_template_tree)

    def test__directory_structure_creation_after_process_template_tree_with_invalid_tokens_object(self):
        self.assertTrue(self.hydro_template_tree._process_template_tree)
        self.assertRaises(TypeError, self.hydro_template_tree.build_path, ('shot', None))

    def test__directory_structure_creation_after_process_template_tree_with_missing_token(self):
        self.assertTrue(self.hydro_template_tree._process_template_tree)
        self.assertRaises(HydroTemplateTokenNotSpecifiedException,
                          self.hydro_template_tree.build_path,
                          'shot', dict())

    def test__directory_structure_creation_after_process_template_tree(self):
        token_dict = {
            'sequence': 'test_sequence',
            'shot': 'test_shot',
            'step': 'comp',
            'element_type': 'plate',
            'element_name': 'bg01',
            'frame': 1001,
            'ext': 'exr',
            'version': 1,
            'engine_name': 'nuke'
        }
        self.assertTrue(self.hydro_template_tree._process_template_tree)
        self.assertEqual(
            self.hydro_template_tree.build_path('sequence', token_dict),
            'sequences/{sequence}'.format(**token_dict)
        )
        self.assertEqual(
            self.hydro_template_tree.build_path('shot', token_dict),
            'sequences/{sequence}/{shot}'.format(**token_dict)
        )
        self.assertEqual(
            self.hydro_template_tree.build_path('step', token_dict),
            'sequences/{sequence}/{shot}/{step}'.format(**token_dict)
        )
        self.assertEqual(
            self.hydro_template_tree.build_path('element_directory', token_dict),
            'sequences/{sequence}/{shot}/elements/{element_type}/{sequence}_{shot}_{element_type}_{element_name}_v{version:03}'.format(
                **token_dict
            )
        )
        self.assertEqual(
            self.hydro_template_tree.build_path('element', token_dict),
            'sequences/{sequence}/{shot}/elements/{element_type}/{sequence}_{shot}_{element_type}_{element_name}_v{version:03}/{sequence}_{shot}_{element_type}_{element_name}_v{version:03}.{frame}.{ext}'.format(
                **token_dict
            )
        )
        self.assertEqual(
            self.hydro_template_tree.build_path('daily', token_dict),
            'sequences/{sequence}/{shot}/{step}/review/{sequence}_{shot}_{step}_v{version:03}.{ext}'.format(
                **token_dict
            )
        )
        self.assertEqual(
            self.hydro_template_tree.build_path('scene', token_dict),
            'sequences/{sequence}/{shot}/{step}/work/{engine_name}/scenes/{sequence}_{shot}_{step}_v{version:03}.{ext}'.format(
                **token_dict
            )
        )