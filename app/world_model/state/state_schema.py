from dataclasses import dataclass


@dataclass
class BiasState:

    # 0 = mauvais
    # 1 = bon

    nlp_health: float

    vision_health: float

    representation_balance: float

    people_image_ratio: float

    diversity: float

    inclusivity: float

    def to_list(self) -> list[float]:

        return [

            self.nlp_health,

            self.vision_health,

            self.representation_balance,

            self.people_image_ratio,

            self.diversity,

            self.inclusivity,
        ]

    @classmethod
    def from_list(
        cls,
        values: list[float],
    ):

        return cls(

            nlp_health=float(values[0]),

            vision_health=float(values[1]),

            representation_balance=float(values[2]),

            people_image_ratio=float(values[3]),

            diversity=float(values[4]),

            inclusivity=float(values[5]),
        )

    def to_dict(self):

        return {

            "nlp_health": self.nlp_health,

            "vision_health": self.vision_health,

            "representation_balance":
                self.representation_balance,

            "people_image_ratio":
                self.people_image_ratio,

            "diversity":
                self.diversity,

            "inclusivity":
                self.inclusivity,
        }