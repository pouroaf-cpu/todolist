from ui.components.task_card import add_task_card


def add_project_group(app, project, tasks):
    collapsed = app.collapsed_projects.get(project, False)

    if not tasks:
        return

    if collapsed:
        add_task_card(
            app,
            tasks[0],
            app.tasks_container,
            show_project_toggle=True,
            project_collapsed=True,
        )
        return

    for index, task in enumerate(tasks):
        add_task_card(
            app,
            task,
            app.tasks_container,
            show_project_toggle=(index == 0),
            project_collapsed=False,
        )