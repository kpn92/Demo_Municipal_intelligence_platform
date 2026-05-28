import { useCallback } from "react";
import useOperationsStore from "../../../store/useOperationsStore.js";
import { useFleetData } from "./useFleetData.js";
import { useFleetVehicles } from "./useFleetVehicles.js";
import {
  getCollectionAreas,
  getBinSummaryForAreas,
  computeCollectionRoute,
} from "../lib/collectionRouting.js";

export function useCollectionWizard() {
  const { allBins, loading: binsLoading } = useFleetData();
  const { vehicles, loading: vehiclesLoading } = useFleetVehicles();

  const cw = useOperationsStore((s) => s.collectionWizard);
  const setCollectionWizard = useOperationsStore((s) => s.setCollectionWizard);
  const resetCollectionWizard = useOperationsStore((s) => s.resetCollectionWizard);

  const areas = getCollectionAreas(allBins);
  const binSummary =
    cw.selectedAreaCodes.length > 0
      ? getBinSummaryForAreas(cw.selectedAreaCodes, allBins)
      : null;

  const toggleArea = useCallback(
    (code) => {
      const next = cw.selectedAreaCodes.includes(code)
        ? cw.selectedAreaCodes.filter((c) => c !== code)
        : [...cw.selectedAreaCodes, code];
      setCollectionWizard({ selectedAreaCodes: next, selectedVehicleId: null, route: null });
    },
    [cw.selectedAreaCodes, setCollectionWizard],
  );

  const selectVehicle = useCallback(
    (vehicleId) => {
      setCollectionWizard({ selectedVehicleId: vehicleId, route: null });
    },
    [setCollectionWizard],
  );

  const isStepValid = useCallback(
    (step) => {
      if (step === 1) return cw.selectedAreaCodes.length > 0;
      if (step === 2) return cw.selectedVehicleId !== null;
      if (step === 3) return cw.route !== null;
      return true;
    },
    [cw],
  );

  const nextStep = useCallback(() => {
    const { step, selectedAreaCodes, selectedVehicleId } = cw;
    if (step === 1 && selectedAreaCodes.length > 0) {
      setCollectionWizard({ step: 2 });
    } else if (step === 2 && selectedVehicleId !== null) {
      const vehicle = vehicles.find((v) => String(v.id) === String(selectedVehicleId));
      const route = vehicle
        ? computeCollectionRoute(selectedAreaCodes, vehicle, allBins)
        : null;
      setCollectionWizard({ step: 3, route });
    } else if (step === 3 && cw.route !== null) {
      setCollectionWizard({ step: 4 });
    }
  }, [cw, vehicles, allBins, setCollectionWizard]);

  const prevStep = useCallback(() => {
    if (cw.step > 1) setCollectionWizard({ step: cw.step - 1 });
  }, [cw.step, setCollectionWizard]);

  return {
    step: cw.step,
    selectedAreaCodes: cw.selectedAreaCodes,
    selectedVehicleId: cw.selectedVehicleId,
    route: cw.route,
    areas,
    vehicles,
    allBins,
    binSummary,
    loading: binsLoading || vehiclesLoading,
    isStepValid,
    toggleArea,
    selectVehicle,
    nextStep,
    prevStep,
    reset: resetCollectionWizard,
  };
}
