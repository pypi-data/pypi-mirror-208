from django.urls import path

from . import views

urlpatterns = [
    path("seating_plans/", views.SeatingPlanListView.as_view(), name="seating_plans"),
    path(
        "seating_plans/create/",
        views.SeatingPlanCreateView.as_view(),
        name="create_seating_plan",
    ),
    path(
        "seating_plans/<int:pk>/",
        views.SeatingPlanDetailView.as_view(),
        name="seating_plan",
    ),
    path(
        "seating_plans/<int:pk>/edit/",
        views.SeatingPlanEditView.as_view(),
        name="edit_seating_plan",
    ),
    path(
        "seating_plans/<int:pk>/copy/",
        views.SeatingPlanCopyView.as_view(),
        name="copy_seating_plan",
    ),
    path(
        "seating_plans/<int:pk>/delete/",
        views.SeatingPlanDeleteView.as_view(),
        name="delete_seating_plan",
    ),
]
