from django.db import models
from django.db.models import signals
from django.dispatch import receiver


class CommonInfo(models.Model):
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True


class Ladder(CommonInfo):
    name=models.CharField(max_length=32)
    initial_deviation=models.FloatField(default=(25/3) ** 2)
    initial_rating=models.FloatField(default=(25/3))
    additional_variance=models.FloatField(default=(25/6) ** 2)
    positive_lower_bound=models.FloatField(default=0.0001)

    class Meta:
        db_table='ladder'


class Match(CommonInfo):
    completed=models.BooleanField(default=False)
    ladder=models.ForeignKey(
        Ladder,
        on_delete=models.CASCADE,
        related_name='matches',
        related_query_name='match',
    )

    class Meta:
        db_table='match'


class Player(CommonInfo):
    name=models.CharField(max_length=32)
    number=models.IntegerField()
    ladders=models.ManyToManyField(
        Ladder,
        related_name='players',
        related_query_name='player',
        through='PlayerLadder',
        through_fields=('player', 'ladder'),
    )

    class Meta:
        db_table='player'
        unique_together=[['name', 'number']]


class PlayerLadder(CommonInfo):
    ladder=models.ForeignKey(Ladder, on_delete=models.CASCADE)
    player=models.ForeignKey(Player, on_delete=models.CASCADE)
    deviation=models.FloatField()
    rating=models.FloatField()

    class Meta:
        db_table='player_ladder'
        unique_together=[['ladder', 'player']]


class Team(CommonInfo):
    match=models.ForeignKey(
        Match, 
        on_delete=models.CASCADE,
        related_name='teams',
        related_query_name='team',
    )
    players=models.ManyToManyField(
        Player,
        through='TeamPlayer',
        through_fields=('team', 'player')
    )
    ranking=models.IntegerField(null=True)

    class Meta:
        db_table='team'


class TeamPlayer(CommonInfo):
    deviation=models.FloatField
    player=models.ForeignKey(Player, on_delete=models.CASCADE)
    rating=models.FloatField
    team=models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        db_table='team_player'
