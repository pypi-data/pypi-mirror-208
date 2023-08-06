# COMMANDS
COMMANDS_NOTEBOOKS_HELP = "List all notebooks and notes, tree-style"
COMMANDS_EDIT_HELP = "Edit or add a note into a notebook"
COMMANDS_SHOW_HELP = "Show a note's contents"
COMMANDS_VERSION = "Show halig's version"

# OPTIONS
OPTION_CONFIG_HELP = "Configuration file. Must be YAML and schema compatible"
OPTION_LEVEL_HELP = (
    "Tree max recursion level; negative numbers indicate a value of infinity"
)

# ARGUMENTS
ARGUMENT_EDIT_NOTE_HELP = """A valid, settings-relative path.
Be aware that valid can also mean implicit notes, that is, pointing to a
current-day note just by its notebook name. For example, if today is
2023-04-04 and you have a notebook containing a 2023-04-04.age note,
simply pointing to the notebook's name, e.g. `halig edit notebook` will
edit the 2023-04-04.age note. Also keep in mind that the note may or may
not exist and it'll be created accordingly; the only requirement is that
the notebook folder structure is correct and exists"""
ARGUMENT_SHOW_NOTE_HELP = """A valid, settings-relative path.
Be aware that valid can also mean implicit notes, that is, pointing to a
current-day note just by its notebook name. For example, if today is
2023-04-04 and you have a notebook containing a 2023-04-04.age note,
simply pointing to the notebook's name, e.g. `halig show notebook` will
print the 2023-04-04.age note"""
