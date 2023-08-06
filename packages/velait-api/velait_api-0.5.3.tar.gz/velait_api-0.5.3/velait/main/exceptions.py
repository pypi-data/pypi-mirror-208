
class VelaitError(Exception):
    name: str
    description: str
    status_code: int = 400

    def __init__(self, name: str = None, description: str = None, status_code: int = None, *args):
        super(VelaitError, self).__init__(*args)
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if status_code is not None:
            self.status_code = status_code


__all__ = ['VelaitError']
