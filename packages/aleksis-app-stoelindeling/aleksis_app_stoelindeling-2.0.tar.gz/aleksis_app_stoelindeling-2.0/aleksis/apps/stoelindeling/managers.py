from collections import OrderedDict

from django.db.models import Max, Min, QuerySet

from aleksis.core.managers import CurrentSiteManagerWithoutMigrations


class SeatManager(CurrentSiteManagerWithoutMigrations):
    """Custom manager for Seat model."""


class SeatQuerySet(QuerySet):
    """Custom queryset for Seat model."""

    def get_constraints(self) -> (int, int):
        """Get the width and height the grid needs at least."""
        aggr = self.filter(seated=True).aggregate(Max("x"), Max("y"), Min("x"), Min("y"))

        start_x = aggr["x__min"] or 0
        start_y = aggr["y__min"] or 0
        end_x = aggr["x__max"] or 0
        end_y = aggr["y__max"] or 0
        width = max(3, end_x - start_x)
        height = max(3, end_y - start_y)

        end_x = start_x + width
        end_y = start_y + height
        print(start_x, start_y, end_x, end_y)
        return start_x, start_y, end_x, end_y

    def without_position(self) -> "SeatQuerySet":
        """Filter for seats without a position."""
        return self.filter(seated=False)

    def build_grid(self) -> OrderedDict[int, OrderedDict[int, "Seat"]]:
        """Build a grid with the seats as dictionaries."""
        start_x, start_y, end_x, end_y = self.get_constraints()

        grid = OrderedDict()
        for x in range(start_x, end_x + 1):
            grid[x] = OrderedDict()
            for y in range(start_y, end_y + 1):
                grid[x][y] = None

        for seat in self.all():
            if not seat.seated:
                continue
            grid[seat.x][seat.y] = seat

        return grid
