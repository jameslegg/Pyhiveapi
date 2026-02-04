
![CodeQL](https://github.com/Pyhive/Pyhiveapi/workflows/CodeQL/badge.svg) ![Python Linting](https://github.com/Pyhive/Pyhiveapi/workflows/Python%20package/badge.svg)

# Important
The package name had to be changed and going forward the Pyhiveapi package should no longer be used. all the same code has been moved into a new package called [pyhive-integration](https://pypi.org/project/pyhive-integration/). Nothing changes in how the package functions its just a rename.

# Introduction
This is a library which interfaces with the Hive smart home platform. 
This library is built mainly to integrate with the Home Assistant platform,
but it can also be used independently (See examples below.)

NOTE:
This integration can only be used with the hive owner account guest accounts are currently not supported.

## EV Charger Support (EVSE)

**IMPORTANT:** EV charger support is UK/British Gas specific functionality and may not be available in other regions. This feature requires a Hive-compatible EV charger (EVSE - Electric Vehicle Supply Equipment) linked to your Hive account.

### Supported Features

The library now supports Hive EV chargers with the following capabilities:

- **Status Monitoring:**
  - Cable connection status (connected/disconnected)
  - Charging state (charging, ready, finishing, idle)
  - Real-time power metrics (Watts, Amps, Volts)
  - Energy consumption (total, peak, off-peak in Wh)
  - Cost tracking (total, peak, off-peak rates)
  - Estimated mileage/range added
  - Transaction information (duration, trigger, mode)

- **Control Commands:**
  - Override PowerPlus smart charging schedule (start charging immediately)
  - Re-enable PowerPlus schedule (resume smart charging)
  - Cable unlock (remote cable release)

- **Smart Charging:**
  - PowerPlus (Demand Side Response / DSR) schedule information
  - Custom charging schedules
  - Tariff schedule details (peak/off-peak periods)
  - Ready-by time settings

### Example Usage

```python
from apyhiveapi import Hive

# Initialize and login
hive = Hive(username="your@email.com", password="yourpassword")
await hive.login()
await hive.startSession()

# Get EV charger devices
devices = await hive.createDevices()

# Assume we have an EV charger device
evcharger_device = devices["evcharger"][0]  # First EV charger

# Check cable connection
is_connected = await hive.evcharger.isCableConnected(evcharger_device)
print(f"Cable connected: {is_connected}")

# Check if actively charging
is_charging = await hive.evcharger.isCharging(evcharger_device)
print(f"Actively charging: {is_charging}")

# Get power metrics
power_metrics = await hive.evcharger.getPowerMetrics(evcharger_device)
print(f"Current power: {power_metrics['power_w']} W")
print(f"Current: {power_metrics['current_a']} A")
print(f"Voltage: {power_metrics['voltage_v']} V")

# Get energy consumed in current session
energy_metrics = await hive.evcharger.getEnergyMetrics(evcharger_device)
print(f"Total energy: {energy_metrics['total_wh'] / 1000:.2f} kWh")
print(f"Peak rate: {energy_metrics['peak_wh'] / 1000:.2f} kWh")
print(f"Off-peak rate: {energy_metrics['off_peak_wh'] / 1000:.2f} kWh")

# Get cost information
cost_metrics = await hive.evcharger.getCostMetrics(evcharger_device)
print(f"Total cost: £{cost_metrics['total_cost']:.2f}")

# Start charging immediately (override PowerPlus schedule)
success = await hive.evcharger.setOverrideOn(evcharger_device)
if success:
    print("Override activated - charging started")

# Resume PowerPlus smart charging schedule
success = await hive.evcharger.setOverrideOff(evcharger_device)
if success:
    print("PowerPlus schedule resumed")
```

### Technical Details

EV charger devices use a different API endpoint (`api-prod.bgchprod.info/omnia`) compared to other Hive devices. The library automatically handles this dual-endpoint architecture. EVSE devices are identified by the node type containing `'evse'` and use the `ev_supply_equipment_v1` feature schema.


## Examples
Here are examples and documentation on how to use the library independently.

https://pyhass.github.io/pyhiveapi.docs/  [WIP]


