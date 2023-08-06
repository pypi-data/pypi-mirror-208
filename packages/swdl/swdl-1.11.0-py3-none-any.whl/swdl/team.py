class Team:
    def __init__(
        self,
        id,
        club_id="",
        age="",
        name="",
        active=False,
        manual_tagging=False,
        dataservice=None,
    ):
        self.id = id
        self.club_id = club_id
        self.age = age
        self.name = name
        self.active = active
        self.manual_tagging = manual_tagging
        self.datasevice = dataservice

    @classmethod
    def from_json(
        cls,
        dataservice,
        RowKey,
        clubId="",
        age="",
        name="",
        active=False,
        manualTagging=False,
        *args,
        **kwargs
    ):
        return Team(
            id=RowKey,
            club_id=clubId,
            age=age,
            name=name,
            active=active,
            manual_tagging=manualTagging,
            dataservice=dataservice,
        )
