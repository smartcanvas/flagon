# The MIT License (MIT)
#
# Copyright (c) 2014 Steve Milner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
"""
Feature support.
"""

import inspect
import logging

from functools import wraps

from flagon import errors


class Feature(object):
    """
    The feature manager.
    """

    def __init__(self, backend, logger):
        """
        Creates the feature manager.

        :param backend: the backend to use for storing feature states.
        :type backend: flagon.backends.Backend
        :param logger: the logger like object to use for logging.
        :type logger: logging.Logger
        :rtype: Feature
        """
        self.backend = backend
        self.logger = logger
        self.logger.debug(
            'The feature decorator for flagon has been created with %s' % (
                backend.__class__.__name__))

    def __call__(self, name, default=None):
        """
        What acts as a decorator.

        :param name: the name of the feature.
        :type name: str
        :param default: the default callable to fall back to.
        :type default: callable or None
        :rtype: callable
        """
        if not self.backend.exists(name):
            self.logger.error('An unknown feature was requested: %s' % name)
            raise errors.UnknownFeatureError('Unknown feature: %s' % name)

        def deco(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if self.backend.is_active(name):
                    self.logger.debug('%s func=%s:%s(*%s, **%s)' % (
                        name, inspect.getabsfile(func),
                        func.__name__, args, kwargs))
                    return func(*args, **kwargs)
                if default:
                    self.logger.warn(
                        'Disabled featured %s was requested.'
                        ' Using default.' % name)
                    if logging.getLevelName(self.logger.level) == 'DEBUG':
                        self.logger.debug('%s default=%s:%s(*%s, **%s)' % (
                            name, inspect.getabsfile(default),
                            default.__name__, args, kwargs))
                    return default(*args, **kwargs)
                else:
                    self.logger.warn('Disabled featured %s was requested' % (
                        name))
                raise NameError("name '%s' is not enabled" % name)
            return wrapper
        return deco

    is_active = lambda s, name: s.backend.is_active(name)
