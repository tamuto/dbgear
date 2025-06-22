from ..project import Project


class EnvironManager:

    def __init__(self, folder: str):
        self.folder = folder





    def add_env(self, env: Environ) -> None:
        if env.name in self.envs:
            raise ValueError(f"Environment '{env.name}' already exists.")
        self.envs[env.name] = env

    def remove_env(self, env_name: str) -> None:
        if env_name not in self.envs:
            raise ValueError(f"Environment '{env_name}' does not exist.")
        del self.envs[env_name]

    def get_env(self, env_name: str) -> Environ | None:
        return self.envs.get(env_name)

    def get_envs(self) -> list[Environ]:
        return sorted(self.envs.values(), key=lambda x: x.name)
