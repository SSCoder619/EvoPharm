"""Medicine Catalogue API router."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from evopharm_retail_erp.application.common import UnitOfWork
from evopharm_retail_erp.application.medicine.commands import RegisterMedicineCommand
from evopharm_retail_erp.application.medicine.services import RegisterMedicineService
from evopharm_retail_erp.domain.medicine import (
    Barcode,
    BarcodeType,
    Composition,
    CompositionItem,
    DosageForm,
    DrugSchedule,
    GenericName,
    HSNCode,
    ManufacturerRef,
    MedicineId,
    MedicineName,
    PackConfiguration,
    StorageCondition,
    StrengthUnit,
    UnitOfMeasure,
)
from ..dependencies import get_uow
from ..schemas.medicine import MedicineResponse, RegisterMedicineRequest

router = APIRouter(prefix="/api/v1/medicines", tags=["Medicine Catalogue"])


@router.post("", response_model=MedicineResponse, status_code=201, summary="Register Medicine")
async def register_medicine(
    request: RegisterMedicineRequest,
    uow: UnitOfWork = Depends(get_uow),
) -> MedicineResponse:
    """Register a new pharmaceutical product in the medicine catalogue."""
    async with uow as active_uow:
        comp_items = [
            CompositionItem(
                ingredient=item.ingredient,
                strength=item.strength,
                unit=StrengthUnit(item.unit),
            )
            for item in request.composition
        ]
        composition = Composition.of(*comp_items)

        barcodes = tuple(Barcode(bc, BarcodeType.EAN_13) for bc in request.barcodes)
        storage = StorageCondition(request.storage_condition) if request.storage_condition else None

        command = RegisterMedicineCommand(
            name=MedicineName(request.name),
            generic_name=GenericName(request.generic_name),
            composition=composition,
            manufacturer=ManufacturerRef(request.manufacturer),
            dosage_form=DosageForm(request.dosage_form),
            pack_configuration=PackConfiguration(request.pack_size, UnitOfMeasure(request.unit_of_measure)),
            hsn_code=HSNCode(request.hsn_code),
            schedule=DrugSchedule(request.schedule),
            barcodes=barcodes,
            alternate_names=tuple(request.alternate_names),
            storage_condition=storage,
        )

        service = RegisterMedicineService(active_uow.medicines)
        medicine = service.execute(command)
        await active_uow.commit()

        return MedicineResponse(
            id=medicine.id.value,
            name=medicine.name.value,
            generic_name=medicine.generic_name.value,
            manufacturer=medicine.manufacturer.name,
            hsn_code=medicine.hsn_code.value,
            dosage_form=medicine.dosage_form.value,
            schedule=medicine.schedule.value,
            status=medicine.status.value,
            version=medicine.version,
        )


@router.get("/{medicine_id}", response_model=MedicineResponse, summary="Get Medicine by ID")
async def get_medicine_by_id(
    medicine_id: UUID,
    uow: UnitOfWork = Depends(get_uow),
) -> MedicineResponse:
    """Retrieve medicine product details by ID."""
    async with uow as active_uow:
        medicine = active_uow.medicines.get_by_id(MedicineId(medicine_id))
        if medicine is None:
            raise HTTPException(status_code=404, detail=f"Medicine {medicine_id} not found")

        return MedicineResponse(
            id=medicine.id.value,
            name=medicine.name.value,
            generic_name=medicine.generic_name.value,
            manufacturer=medicine.manufacturer.name,
            hsn_code=medicine.hsn_code.value,
            dosage_form=medicine.dosage_form.value,
            schedule=medicine.schedule.value,
            status=medicine.status.value,
            version=medicine.version,
        )
