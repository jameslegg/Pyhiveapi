"""Hive EV Charger Module.

This module provides support for Hive EV chargers (EVSE - Electric Vehicle Supply Equipment).
Note: This functionality is specific to UK/British Gas Hive installations and may not be
available in other regions.
"""

# pylint: skip-file
from typing import Optional, Dict, Any
from .helper.const import HIVETOHA


class HiveEVCharger:
    """EV Charger Device (EVSE - Electric Vehicle Supply Equipment).
    
    Provides access to Hive EV charger status and control.
    This includes charging state, power metrics, energy tracking, cost calculation,
    and control commands for PowerPlus smart charging.
    
    Note: EVSE support is UK/British Gas specific and uses the Omnia API endpoint.
    
    Returns:
        object: Returns EVCharger object
    """

    evchargerType = "EVCharger"

    async def getConnectionStatus(self, device: dict) -> Optional[str]:
        """Get EV charger cable connection status.

        Args:
            device (dict): Device to get the connection status for.

        Returns:
            str: Connection status - "OCCUPIED" (cable connected), "AVAILABLE" (no cable), or None
        """
        state = None

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            state = features.get("connectorStatus", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return state

    async def getChargingState(self, device: dict) -> Optional[str]:
        """Get current charging state.

        Args:
            device (dict): Device to get the charging state for.

        Returns:
            str: Charging state - "CHARGING", "SUSPENDED_EVSE", "FINISHING", "IDLE", etc., or None
        """
        state = None

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            state = features.get("transactionChargingState", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return state

    async def getDisplayState(self, device: dict) -> Optional[str]:
        """Get display state shown in Hive app.

        Args:
            device (dict): Device to get the display state for.

        Returns:
            str: Display state - "OPTIMISED", "AVAILABLE", "FINISHING", etc., or None
        """
        state = None

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            state = features.get("displayState", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return state

    async def isCharging(self, device: dict) -> bool:
        """Check if actively charging.

        Args:
            device (dict): Device to check.

        Returns:
            bool: True if actively charging, False otherwise
        """
        state = await self.getChargingState(device)
        return state == "CHARGING"

    async def isCableConnected(self, device: dict) -> bool:
        """Check if cable is connected.

        Args:
            device (dict): Device to check.

        Returns:
            bool: True if cable connected, False otherwise
        """
        state = await self.getConnectionStatus(device)
        return state == "OCCUPIED"

    async def isTransactionActive(self, device: dict) -> bool:
        """Check if a charging transaction is active.

        Args:
            device (dict): Device to check.

        Returns:
            bool: True if transaction active, False otherwise
        """
        active = False

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            active = features.get("transactionActive", {}).get("reportedValue", False)
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return active

    async def isOverrideActive(self, device: dict) -> bool:
        """Check if PowerPlus schedule is overridden (manual charging).

        Args:
            device (dict): Device to check.

        Returns:
            bool: True if override active (manual charge), False otherwise
        """
        overridden = False

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            overridden = features.get("transactionOverridden", {}).get("reportedValue", False)
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return overridden

    async def getPowerMetrics(self, device: dict) -> Dict[str, Optional[float]]:
        """Get current power metrics.

        Args:
            device (dict): Device to get power metrics for.

        Returns:
            dict: Dictionary with keys 'power_w' (Watts), 'current_a' (Amps), 'voltage_v' (Volts)
        """
        metrics = {
            "power_w": None,
            "current_a": None,
            "voltage_v": None
        }

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            metrics["power_w"] = features.get("transactionActivePowerImportW", {}).get("reportedValue")
            metrics["current_a"] = features.get("transactionCurrentImportA", {}).get("reportedValue")
            metrics["voltage_v"] = features.get("transactionVoltageV", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return metrics

    async def getEnergyMetrics(self, device: dict) -> Dict[str, Optional[float]]:
        """Get energy consumption metrics for current transaction.

        Args:
            device (dict): Device to get energy metrics for.

        Returns:
            dict: Dictionary with 'total_wh', 'peak_wh', 'off_peak_wh' (all in Watt-hours)
        """
        metrics = {
            "total_wh": None,
            "peak_wh": None,
            "off_peak_wh": None
        }

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            metrics["total_wh"] = features.get("transactionEnergyTotalWh", {}).get("reportedValue")
            metrics["peak_wh"] = features.get("transactionEnergyTotalPeakWh", {}).get("reportedValue")
            metrics["off_peak_wh"] = features.get("transactionEnergyTotalOffPeakWh", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return metrics

    async def getCostMetrics(self, device: dict) -> Dict[str, Optional[float]]:
        """Get cost metrics for current transaction.

        Args:
            device (dict): Device to get cost metrics for.

        Returns:
            dict: Dictionary with 'total_cost', 'peak_cost', 'off_peak_cost' (in currency units)
        """
        metrics = {
            "total_cost": None,
            "peak_cost": None,
            "off_peak_cost": None
        }

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            metrics["total_cost"] = features.get("transactionCost", {}).get("reportedValue")
            metrics["peak_cost"] = features.get("transactionCostPeak", {}).get("reportedValue")
            metrics["off_peak_cost"] = features.get("transactionCostOffPeak", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return metrics

    async def getMileageMetrics(self, device: dict) -> Dict[str, Optional[float]]:
        """Get mileage/range metrics for current transaction.

        Args:
            device (dict): Device to get mileage metrics for.

        Returns:
            dict: Dictionary with 'miles_added', 'kilometers_added', 'miles_added_rate', 'kilometers_added_rate'
        """
        metrics = {
            "miles_added": None,
            "kilometers_added": None,
            "miles_added_rate": None,
            "kilometers_added_rate": None
        }

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            metrics["miles_added"] = features.get("transactionMilesAdded", {}).get("reportedValue")
            metrics["kilometers_added"] = features.get("transactionKilometersAdded", {}).get("reportedValue")
            metrics["miles_added_rate"] = features.get("transactionMilesAddedRate", {}).get("reportedValue")
            metrics["kilometers_added_rate"] = features.get("transactionKilometersAddedRate", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return metrics

    async def getTransactionInfo(self, device: dict) -> Dict[str, Any]:
        """Get detailed transaction information.

        Args:
            device (dict): Device to get transaction info for.

        Returns:
            dict: Dictionary with transaction details including trigger, start mode, duration, ready-by time, etc.
        """
        info = {
            "active": False,
            "overridden": False,
            "trigger": None,
            "start_mode": None,
            "charge_time_seconds": None,
            "ready_by": None
        }

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            info["active"] = features.get("transactionActive", {}).get("reportedValue", False)
            info["overridden"] = features.get("transactionOverridden", {}).get("reportedValue", False)
            info["trigger"] = features.get("transactionTrigger", {}).get("reportedValue")
            info["start_mode"] = features.get("transactionStartMode", {}).get("reportedValue")
            info["charge_time_seconds"] = features.get("transactionChargeTimeSeconds", {}).get("reportedValue")
            info["ready_by"] = features.get("transactionReadyBy", {}).get("reportedValue")
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return info

    async def getScheduleInfo(self, device: dict) -> Dict[str, Any]:
        """Get charging schedule information.

        Args:
            device (dict): Device to get schedule info for.

        Returns:
            dict: Dictionary with schedule mode, custom schedule, tariff schedule, smart charge settings, etc.
        """
        info = {
            "schedule_mode": None,
            "custom_schedule": None,
            "tariff_schedule": None,
            "tariff_schedule_type": None,
            "smart_charge_ready_by": None,
            "smart_charge_eligible": False
        }

        try:
            data = self.session.data.products[device["hiveID"]]
            features = data.get("props", {}).get("ev_supply_equipment_v1", {})
            info["schedule_mode"] = features.get("scheduleMode", {}).get("reportedValue")
            info["custom_schedule"] = features.get("customSchedule", {}).get("reportedValue")
            info["tariff_schedule"] = features.get("tariffSchedule", {}).get("reportedValue")
            info["tariff_schedule_type"] = features.get("tariffScheduleType", {}).get("reportedValue")
            info["smart_charge_ready_by"] = features.get("smartChargeReadyBy", {}).get("reportedValue")
            info["smart_charge_eligible"] = features.get("smartChargeEligible", {}).get("reportedValue", False)
        except (KeyError, AttributeError) as e:
            await self.session.log.error(e)

        return info

    async def setOverrideOn(self, device: dict) -> bool:
        """Start charging immediately, overriding PowerPlus schedule.

        This bypasses the smart charging schedule and begins charging immediately.
        Useful when you need to charge outside of scheduled times.

        Args:
            device (dict): Device to control.

        Returns:
            bool: True if successful, False otherwise
        """
        final = False

        if (
            device["hiveID"] in self.session.data.products
            and device["deviceData"]["online"]
        ):
            await self.session.hiveRefreshTokens()
            data = self.session.data.products[device["hiveID"]]
            
            # For EVSE, we need to use the Omnia API with a different structure
            node_id = data.get("id")
            if node_id:
                resp = await self.session.api.setEVSEOverride(node_id, override_on=True)
                if resp.get("original") == 200:
                    final = True
                    await self.session.getDevices(device["hiveID"])

        return final

    async def setOverrideOff(self, device: dict) -> bool:
        """Re-enable PowerPlus smart charging schedule.

        This stops the manual override and returns control to the smart charging schedule.

        Args:
            device (dict): Device to control.

        Returns:
            bool: True if successful, False otherwise
        """
        final = False

        if (
            device["hiveID"] in self.session.data.products
            and device["deviceData"]["online"]
        ):
            await self.session.hiveRefreshTokens()
            data = self.session.data.products[device["hiveID"]]
            
            # For EVSE, we need to use the Omnia API with a different structure
            node_id = data.get("id")
            if node_id:
                resp = await self.session.api.setEVSEOverride(node_id, override_on=False)
                if resp.get("original") == 200:
                    final = True
                    await self.session.getDevices(device["hiveID"])

        return final

    async def unlockCable(self, device: dict) -> bool:
        """Unlock the charging cable remotely.

        Note: This feature may not be available on all EVSE models.

        Args:
            device (dict): Device to control.

        Returns:
            bool: True if successful, False otherwise
        """
        final = False

        if (
            device["hiveID"] in self.session.data.products
            and device["deviceData"]["online"]
        ):
            await self.session.hiveRefreshTokens()
            data = self.session.data.products[device["hiveID"]]
            
            # For EVSE, we need to use the Omnia API with a different structure
            node_id = data.get("id")
            if node_id:
                resp = await self.session.api.setEVSECableUnlock(node_id)
                if resp.get("original") == 200:
                    final = True
                    await self.session.getDevices(device["hiveID"])

        return final


class EVCharger(HiveEVCharger):
    """EV Charger - Main wrapper class.
    
    This is the main class for interacting with Hive EV chargers.
    Provides a simplified interface to the HiveEVCharger functionality.
    """

    def __init__(self, session=None):
        """Initialize EVCharger.

        Args:
            session: Hive session object
        """
        self.session = session
        self.evchargerType = "EVCharger"
