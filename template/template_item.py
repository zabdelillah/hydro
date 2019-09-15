'''
hydro.template.template_item
A Hydro template_item represents an item on disk. Elements of template handling such as path building is controlled
by the template item itself.
'''
import os
import re

class HydroTemplateTokenNotSpecifiedException(Exception):
    '''
    HydroTemplateTokenNotSpecifiedException is thrown when a path building request has been made, however, the specified
    tokens are not usable with the template object in question.

    As an example, we have a HydroTemplateObject, where the naming contains {sequence}_{shot}, however, the build_path
    function has been given a token set, where only {sequence} is specified. The path building will not work without the
    {shot} token, and this exception is thrown.
    '''
    pass

class HydroTemplateObject(object):
    '''
    HydroTemplateObject represents any single item on disk, whether a directory or a file. It controls everything to do
    with the represented file, such as building the path to it on-disk, controlling permissions, creating and removing.
    '''
    def build_path(self, tokens, child_path=None):
        '''
        Build the path this object represents. This function will scale up the hierarchy tree, by accessing the
        parent_item variable, recursively performing path construction, until the top of the tree is reached.
        :param tokens: (dict) key/value pair of the tokens to process for path construction
        :param child_path: (str) path to the child, which will be appended to the result of this function.
        :return: (str) full path to the object, using the tokens provided
        '''

        # Ensure that provided tokens are a dictionary
        if not isinstance(tokens, dict):
            raise TypeError('Specified tokens object is not a dictionary')

        # Verify that we are provided the required tokens to build the path for this object
        # Use regex to find tokens we are requesting in this object. The regex will do a search on the string for text
        # embedded inside both { } characters, and will also know to look before a colon (:), in the case where we are
        # using an integer padding.
        # TODO: Implement a check for optional fields
        missing_tokens = list()
        requested_tokens = re.findall(
            r'(?!{)[A-z]+(?=[}\:])',
            self._name
        )

        if not self._preserve:
            # Recursively check for missing tokens
            for token in requested_tokens:
                if token not in tokens.keys():
                    missing_tokens.append(token)

            # Raise a HydroTemplateTokenNotSpecifiedException for all missing tokens we have encountered. This will
            # cause the path generation process to fail.
            if len(missing_tokens) > 0:
                raise HydroTemplateTokenNotSpecifiedException('Tokens %s are missing for template %s' % (', '.join(
                            [
                                '\'%s\'' % token
                                for token in missing_tokens
                            ]
                        ),
                    self._name
                    )
            )

            # Apply the valid tokens to the object_name variable, as we know they are valid since we have reached this
            # point.
            object_name = self._name.format(
                **tokens
            )
        else:
            # We are preserving the original naming convention, so we don't have to perform the above logic. In this
            # case, just use the _name variable directory
            object_name = self._name

        # If a child_path is specified, perform a path join to append our object_name to the start of the path.
        path = object_name
        if child_path:
            path = os.path.join(object_name, child_path)

        # If this object has a parent_item declared, call the build_path function on that variable, and pass the above
        # constructed path to it. The parent item will then perform the same logic, and prepend the constructed path to
        # that constructed here.
        if self._parent_item:
            path = self._parent_item.build_path(tokens, path)

        return path

    def __init__(self,
                 name,
                 preserve=False,
                 parent_item=None):
        '''
        Represents a context on-disk.
        :param name: (str) the naming convention that this object will follow
        :param preserve: (bool) perform string manipulation logic
        :param parent_item: (HydroTemplateObject) parent object in the template tree hierarchy
        '''
        self._name = name
        self._preserve = preserve
        self._parent_item = parent_item