"""Application services that coordinate Medicine Catalogue use cases."""
from __future__ import annotations

from evopharm_retail_erp.application.medicine.commands import RegisterMedicineCommand
from evopharm_retail_erp.domain.medicine import Medicine, MedicineRepository


class RegisterMedicineService:
    """Register one aggregate through a domain repository port.

    The service has no SQLAlchemy, PySide, or FastAPI imports.  A composition
    root supplies a concrete repository adapter, preserving the dependency
    direction from the application layer to the domain port.
    """

    def __init__(self, repository: MedicineRepository) -> None:
        self._repository = repository

    def execute(self, command: RegisterMedicineCommand) -> Medicine:
        """Create and persist a fully validated Medicine aggregate."""

        medicine = Medicine.register(
            name=command.name,
            generic_name=command.generic_name,
            composition=command.composition,
            manufacturer=command.manufacturer,
            dosage_form=command.dosage_form,
            pack_configuration=command.pack_configuration,
            hsn_code=command.hsn_code,
            schedule=command.schedule,
            barcodes=command.barcodes,
            alternate_names=command.alternate_names,
            storage_condition=command.storage_condition,
        )
        self._repository.add(medicine)
        return medicine
