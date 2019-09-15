'''
hydro.template.template_tree
Manages the construction of a template tree, by reading the YAML-written schema provided and creating several
HydroTemplateObject items to represent each individual item, and organising the hierarchy.
'''
import copy
import os
import yaml
from .template_item import HydroTemplateObject

class HydroTemplateSchemaFileNotSpecifiedException(Exception):
    '''
    HydroTemplateSchemaFileNotSpecifiedException is thrown when functions from the HydroTemplateTree class that require
    interaction with the schema file have been called without being provided which schema file to look at
    '''
    pass

class HydroTemplateTree(object):
    '''
    HydroTemplateTree represents the construction and manipulation of a template hierarchy.
    '''
    def _load_template_tree(self,
                            process_template_tree=True):
        '''
        Read a schema file from disk and update the template_schema variable with the new data. If process_template_tree
        is left as true, this function will also call the processing function to update the hierarchy within this object
        :param process_template_tree: (bool) also rebuild the hierarchy
        '''
        # Raise a HydroTemplateSchemaFileNotSpecifiedException if we are trying to load the schema without being
        # specified which file to look at
        if not self._template_path:
            raise HydroTemplateSchemaFileNotSpecifiedException('No template file has been specified')

        # Use the YAML library to load the schema from the given location, and convert it to a dictionary
        with open(self._template_path, 'r') as f:
            self._template_schema = copy.deepcopy(
                yaml.load(f, Loader=yaml.Loader)
            )

        # If process_template_tree is True, also rebuild the HydroTemplateItem for each object declared in the schema,
        # and re-build the hierarchy
        if process_template_tree:
            self._process_template_tree()

    def _process_template_tree_item(self, item, parent_item=None):
        '''
        Build a HydroTemplateObject for the item variable passed to this function, and if specified, assigned the
        parent_item variable of the created item to that of the parent_item.

        This function will be in a recursive loop until the end of the hierarchy is reached. Upon each recurse, the
        created HydroTemplateObject is passed as the parent_item argument to this function.
        :param item: (list) list of dictionaries, representing a directory / file structure
        :param parent_item: (HydroTemplateObject) the parent object of children being processed on this function run
        '''
        for child_item in item:
            for child, data in child_item.items():
                preserve = False
                naming = '{%s}' % child

                # If the value on this item is a dictionary, we know we have more information and rules to apply to this
                # particular item, otherwise, it's a list that we can pass further down stream. The *children* variable
                # represents a list of child elements that we want to pass to the re-call of this function for that
                # directory structure.
                if isinstance(data, dict):
                    children = data.get('children', data)
                    preserve = data.get('preserve', False)

                    # If we're preserving the naming convention, we don't want to perform any string manipulation, so
                    # just set the naming variable identical to the key.
                    if preserve:
                        naming = child
                    else:
                        naming = data.get('naming', naming)
                else:
                    children = data

                # Create a HydroTemplateObject with the information we have processed. *name* defines what the object
                # will be using to build the representation of the object, and *parent_item* declares what the parent
                # item in the tree is.
                template_object = HydroTemplateObject(
                    name=naming,
                    preserve=preserve,
                    parent_item=parent_item
                )

                # If we're not preserving the naming convention, store the key name in to the template_tree dictionary,
                # with its' value pointing to the created HydroTemplateObject. Doing so, will allow us to directly
                # interact with this dictionary to get relevant templates, rather than having to continuously perform
                # a search of a hierarchy to get the element we want.
                if not preserve:
                    self._template_tree[child] = template_object

                # If the current item we're processing has children, re-run this process, but provide the children as
                # the argument, with the *parent_item* pointing to our HydroTemplateObject created above.
                if isinstance(children, list):
                    self._process_template_tree_item(children, parent_item=template_object)

    def _process_template_tree(self):
        '''
        Begin the processing of the template schema from the root level. This function will iterate across each root
        declared in the schema, and build their respective trees.
        '''
        for template_root_name, root_data in self._template_schema.items():
            self._process_template_tree_item(root_data)

    def build_path(self, key, tokens):
        '''
        Build a representation of a path with a given key and set of tokens. This will look at the *_template_tree*
        variable for the key that we have been given, and call the build_path function in the object that is found in
        the key that we have given.
        :param key: (str) the path context we want to build
        :param tokens: (dict) tokens to use to construct the path
        :return: (str) a combined root + constructed path string, representing the built path
        '''
        template_object = self._template_tree.get(key)

        # Raise a KeyError if the given key is not found in this tree
        if not template_object:
            raise KeyError('The requested context \'%s\' was not found in the template tree' % key)
        return os.path.join(
            self._template_tree_root,
            template_object.build_path(tokens)
        )

    def __init__(self,
                 template_path=None):
        '''
        Construct the TemplateTree object
        :param template_path: (str) the path to the schema that will be used
        '''
        self._template_path = template_path
        self._template_schema = None
        self._template_tree = dict()
        self._template_tree_root = str()

        if template_path:
            self._load_template_tree()