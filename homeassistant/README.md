HomeAssistant local addons

HA configuration.yaml for the retired addon to read directly from the inverter.

```
# REST for direct inverter reading
rest:
  - resource: http://homeassistant.local:8081
    scan_interval: 30
    timeout: 20
    params:
        sun: >
            {{ states('sun.sun') }}
    sensor:
      - name: "Inverter Power"
        unique_id: id_010EE1211220015_power
        value_template: "{{ value_json.inverter }}"
        device_class: power
        state_class: measurement
        unit_of_measurement: W

      - name: "Inverter Energy Today"
        unique_id: id_010EE1211220015_energy_today
        value_template: "{{ value_json.today }}"
        device_class: energy
        state_class: total_increasing
        unit_of_measurement: kWh

      - name: "Inverter Energy Total"
        unique_id: id_010EE1211220015_energy_total
        value_template: "{{ value_json.total }}"
        device_class: energy
        state_class: total_increasing
        unit_of_measurement: kWh
```
