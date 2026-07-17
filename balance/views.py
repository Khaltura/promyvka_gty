from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import redirect, render

from promyvki.models import (
    CompressorStation,
    CleaningFluid,
    Antifreeze,
    Wash,
)

from .forms import MaterialOperationForm
from .models import MaterialOperation


ZERO = Decimal("0.00")


def get_sum(queryset, field_name):
    """
    Возвращает сумму указанного поля.

    Если подходящих записей нет, возвращает Decimal("0.00").
    """
    result = queryset.aggregate(total=Sum(field_name))["total"]
    return result or ZERO


def balance_list(request):
    """
    Формирует таблицу баланса отдельно для каждой комбинации:
    компрессорная станция + промывочная жидкость.
    """

    balance_rows = []

    if (
        request.user.is_authenticated
        and not request.user.is_superuser
        and hasattr(request.user, "userprofile")
    ):
        stations = CompressorStation.objects.filter(
            id=request.user.userprofile.station.id
        )
    else:
        stations = CompressorStation.objects.all().order_by("name")

    fluids = CleaningFluid.objects.all().order_by("name")

    for station in stations:
        for fluid in fluids:

            arrival = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="arrival",
                    to_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            writeoff = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="writeoff",
                    from_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            wash = get_sum(
                Wash.objects.filter(
                    station=station,
                    cleaning_fluid=fluid,
                ),
                "cleaning_fluid_amount",
            )

            transfer_out = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="transfer",
                    from_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            transfer_in = get_sum(
                MaterialOperation.objects.filter(
                    operation_type="transfer",
                    to_station=station,
                    cleaning_fluid=fluid,
                ),
                "amount",
            )

            transfer = transfer_in - transfer_out

            current_balance = (
                arrival
                + transfer_in
                - transfer_out
                - writeoff
                - wash
            )

            has_operations = any(
                value != ZERO
                for value in (
                    arrival,
                    writeoff,
                    wash,
                    transfer_in,
                    transfer_out,
                )
            )

            if has_operations:
                balance_rows.append(
                    {
                        "station": station,
                        "fluid": fluid,
                        "arrival": arrival,
                        "wash": wash,
                        "writeoff": writeoff,
                        "transfer_in": transfer_in,
                        "transfer_out": transfer_out,
                        "transfer": transfer,
                        "balance": current_balance,
                    }
                )

        total_balance = sum(
        (row["balance"] for row in balance_rows),
        ZERO,
    )

        material_summary = []

    # Промывочные жидкости
    for fluid in fluids:

        balance = ZERO

        for row in balance_rows:
            if row["fluid"] == fluid:
                balance += row["balance"]

        if balance != ZERO:
            material_summary.append(
                {
                    "name": fluid.name,
                    "type": "Промывочная жидкость",
                    "balance": balance,
                }
            )

    # Антифриз
    antifreezes = Antifreeze.objects.all().order_by("name")

    for antifreeze in antifreezes:

        total = get_sum(
            Wash.objects.filter(
                antifreeze=antifreeze,
            ),
            "antifreeze_amount",
        )

        if total != ZERO:
            material_summary.append(
                {
                    "name": antifreeze.name,
                    "type": "Антифриз",
                    "balance": total,
                }
            )

    return render(
        request,
        "balance/balance_list.html",
        {
            "balance_rows": balance_rows,
            "total_balance": total_balance,
            "material_summary": material_summary,
        },
    )

    return render(
        request,
        "balance/balance_list.html",
        {
            "balance_rows": balance_rows,
            "total_balance": total_balance,
            "fluid_summary": fluid_summary,
            "antifreeze_summary": antifreeze_summary,
        },
    )


def operation_create(request):
    """
    Создаёт приход, списание или перераспределение жидкости.
    """

    if request.method == "POST":
        form = MaterialOperationForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            form.save()
            return redirect("balance_list")

    else:
        form = MaterialOperationForm(
            user=request.user,
        )

    return render(
        request,
        "balance/operation_form.html",
        {
            "form": form,
        },
    )