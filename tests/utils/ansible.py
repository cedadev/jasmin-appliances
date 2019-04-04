import subprocess
import sys

import six

INVENTORY_PATH = './openstack.ini'


def _get_inventory_path():
    return INVENTORY_PATH


def run_command(cmd):
    return subprocess.check_output(cmd)


def quote_and_escape(value):
    """Quote and escape a string.

    Adds enclosing single quotes to the string passed, and escapes single
    quotes within the string using backslashes. This is useful for passing
    'extra vars' to Ansible. Without this, Ansible only uses the part of the
    string up to the first whitespace.

    :param value: the string to quote and escape.
    :returns: the quoted and escaped string.
    """
    if not isinstance(value, six.string_types):
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def build_args(playbooks, extra_vars=None, verbose_level=None):
    cmd = ["ansible-playbook"]
    if verbose_level:
        cmd += ["-" + "v" * verbose_level]
    inventory = _get_inventory_path()
    cmd += ["--inventory", inventory]
    if extra_vars:
        for extra_var_name, extra_var_value in extra_vars.items():
            # Quote and escape variables originating within the python CLI.
            extra_var_value = quote_and_escape(extra_var_value)
            cmd += ["-e", "%s=%s" % (extra_var_name, extra_var_value)]
    cmd += playbooks
    return cmd


def run_playbooks(playbooks, extra_vars=None, verbose_level=None):
    cmd = build_args(playbooks, extra_vars=extra_vars,
                     verbose_level=verbose_level)
    try:
        run_command(cmd)
    except subprocess.CalledProcessError as e:
        print("Playbook(s) %s exited %d", ", ".join(playbooks), e.returncode)
        print("The output was:\n%s", e.output)
        return e.returncode
    return 0


def run_playbook(playbook, **kwargs):
    return run_playbooks([playbook], **kwargs)
