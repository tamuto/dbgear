

class APIProxy:

    def __init__(self, app):
        self.ins_proj = app.state.project
        self.ins_temp = app.state.project.template
        self.ins_envn = app.state.project.environ

    @property
    def project_name(self):
        return self.ins_proj.config['project_name']

    @property
    def templates(self):
        return self.ins_temp.templates

    @property
    def environs(self):
        return self.ins_envn.environs

    @property
    def instances(self):
        return list(self.ins_proj.definitions.keys())

    def is_exist_template(self, id):
        return self.ins_temp.is_exist_template(id)

    def create_template(self, id, name, instances):
        return self.ins_temp.create_template(id, name, instances)

    def listup_for_init(self, id):
        return self.ins_temp.listup_for_init(id)
