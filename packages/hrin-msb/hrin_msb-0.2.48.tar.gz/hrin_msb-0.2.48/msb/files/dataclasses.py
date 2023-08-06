import dataclasses


@dataclasses.dataclass
class GeneratedFile:
	message: str = None
	path: str = None
	password: str = None
	readonly: bool = False
	error: bool = False
