from halig.commands.notebooks import NotebooksCommand


def test_build_tree_max_depth_0(notes, notebooks_command: NotebooksCommand):
    notebooks_command.max_depth = 0
    tree = notebooks_command.build_tree(notebooks_command.settings.notebooks_root_path)
    assert not tree.children


def test_build_tree_max_depth_1(notes, notebooks_command: NotebooksCommand):
    notebooks_command.max_depth = 1
    tree = notebooks_command.build_tree(notebooks_command.settings.notebooks_root_path)
    personal = tree.children[0]
    work = tree.children[1]
    assert personal.label == "Personal"
    assert work.label == "Work"
    assert not personal.children
    assert not work.children


def test_build_tree_max_depth_2(notes, notebooks_command: NotebooksCommand):
    notebooks_command.max_depth = 2
    tree = notebooks_command.build_tree(notebooks_command.settings.notebooks_root_path)
    personal = tree.children[0]
    work = tree.children[1]
    assert personal.label == "Personal"
    assert work.label == "Work"
    assert len(work.children) == 2
    assert len(personal.children) == 1


def test_build_tree_max_depth_inf(notes, notebooks_command: NotebooksCommand):
    tree = notebooks_command.build_tree(notebooks_command.settings.notebooks_root_path)
    personal = tree.children[0]
    work = tree.children[1]
    assert personal.label == "Personal"
    assert work.label == "Work"
    assert len(work.children) == 2
    assert len(personal.children) == 1

    assert work.children[0].label == "Dailies"
    assert len(work.children[0].children) == 10
