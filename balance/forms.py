from django import forms

from .models import MaterialOperation


class MaterialOperationForm(forms.ModelForm):
    class Meta:
        model = MaterialOperation
        fields = (
            "operation_type",
            "from_station",
            "to_station",
            "cleaning_fluid",
            "amount",
            "date",
            "comment",
        )

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Комментарий или причина операции",
                }
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

        if (
            user is not None
            and user.is_authenticated
            and not user.is_superuser
            and hasattr(user, "userprofile")
        ):
            station = user.userprofile.station

            self.fields["from_station"].initial = station
            self.fields["from_station"].disabled = True

            self.fields["to_station"].queryset = (
                self.fields["to_station"]
                .queryset
                .exclude(id=station.id)
            )

    def clean(self):
        cleaned_data = super().clean()

        if (
            self.user is not None
            and self.user.is_authenticated
            and not self.user.is_superuser
            and hasattr(self.user, "userprofile")
        ):
            cleaned_data["from_station"] = self.user.userprofile.station

        operation_type = cleaned_data.get("operation_type")
        from_station = cleaned_data.get("from_station")
        to_station = cleaned_data.get("to_station")

        if operation_type == "arrival":
            cleaned_data["from_station"] = None

        elif operation_type == "writeoff":
            cleaned_data["to_station"] = None

        elif operation_type == "transfer":
            if (
                from_station is not None
                and to_station is not None
                and from_station == to_station
            ):
                self.add_error(
                    "to_station",
                    "КС-источник и КС-получатель должны различаться.",
                )

        return cleaned_data