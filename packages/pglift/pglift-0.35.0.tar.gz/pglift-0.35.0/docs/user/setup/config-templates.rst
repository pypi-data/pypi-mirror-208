.. _configuration_templates:

Configuration templates
=======================

Instance and satellite components configuration is built from site-wise
configuration files.

These files are templates which means that values in curly braces
``{<placeholder>}`` are substituted by site settings values.

These templates can be overridden by providing them in either
``$XDG_CONFIG_HOME/pglift`` [#xdgconfighome]_ or ``/etc/pglift`` (by order of
precedence).

.. [#xdgconfighome]
   Where ``$XDG_CONFIG_HOME`` would be ``$HOME/.config`` unless configured
   differently.
