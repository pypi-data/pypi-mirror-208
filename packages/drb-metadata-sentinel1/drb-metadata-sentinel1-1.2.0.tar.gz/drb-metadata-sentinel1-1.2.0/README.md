# DRB Sentinel-1 Metadata AddOn
This addon allowing to enrich the `Sentinel-1 Product` topic with its metadata
derivative topics also. 


Defined metadata:

| Sentinel-1 Product              |
|---------------------------------|
| platformShortName               |
| platformSerialIdentifier        |
| instrumentShortName             |
| operationalMode                 |
| swathIdentifier                 |
| processingDate                  |
| processingCenter                |
| processorName                   |
| processorVersion                |
| beginningDateTime               |
| endingDateTime                  |
| polarisationChannels            |
| datatakeId                      |
| startTimeFromAscendingNode      |
| completionTimeFromAscendingNode |
| orbitNumber                     |
| orbitDirection                  |
| cycleNumber                     |
| relativeOrbitNumber             |
| productType                     |
| productClass                    |
| instrumentConfigurationID       |
| sliceProductFlag                |
| sliceNumber                     |
| totalSlices                     |

| Sentinel-1 Level 0 Product |
|----------------------------|
| productConsolidation       |

| Sentinel-1 Level 1 Product |
|----------------------------|
| timeliness                 |
| productComposition         |
| segmentStartTime           |

| Sentinel-1 Level 2 Product |
|----------------------------|
| timeliness                 |
| productComposition         |
| segmentStartTime           |

| Sentinel-1 Auxiliary Product |
|------------------------------|
| PlatformShortName            |
| PlatformSerialIdentifier     |
| InstrumentShortName          |
| ProcessingDate               |
| ProcessingCenter             |
| ProcessorName                |
| ProcessorVersion             |
| beginningDateTime            |
| productType                  |
| productGeneration            |
| instrumentConfigurationID    |

| Sentinel-1 EOF Auxiliary Product |
|----------------------------------|
| PlatformShortName                |
| PlatformSerialIdentifier         |
| ProcessingDate                   |
| ProcessingCenter                 |
| ProcessorVersion                 |
| beginningDateTime                |
| endingDateTime                   |
| productType                      |