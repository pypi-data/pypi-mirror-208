# drb-topic-sentinel1
The `drb-topic-sentinel1` is a DRB plugin declaring topics about
[Sentinel-1](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1)
EO satellite.

## Installation
```bash
pip install drb-topic-sentinel1
```

## Sentinel-1 topics
This section references topics defined in the `drb-topic-sentinel1` DRB plugin.

```mermaid
graph TB
    subgraph "drb-topic-safe"
        A([SAFE Product<br/>487b0c70-6199-46de-9e41-4914520e25d9])
    end

    subgraph "drb-topic-sentinel1"
        B([Sentinel-1 Product<br/>aff2191f-5b06-4121-a9fa-f3d93f6c6331])
        C([Sentinel-1 Level 0 Product<br/>800588f9-9a98-4383-a661-572b9a18c3dc])
        D([Sentinel-1 Level 1 Product<br/>84f8d85f-4d2b-4be6-99ad-9a295eb1c252])
        E([Sentinel-1 Level 2 Product<br/>029c85f0-d567-46ef-8098-3bb32095d8d4])
        F([Sentinel-1 Auxiliary Product<br/>8c9f1960-f544-47ae-ba45-424b8cc48b45])
        G([Sentinel-1 EOF Auxiliary Product<br/>40273ef3-a898-4779-a788-12322b7ad527])
    end

    B & F --> A
    C & D & E --> B
```

### Sentinel-1 Level 0 topics
```mermaid
graph LR
    L0([Sentinel-1 Level 0 Product<br/>800588f9-9a98-4383-a661-572b9a18c3dc])
    IWL0([Sentinel-1 Interferometric Wide Swath Level 0 Product<br/>61b95406-2960-43db-9ff2-688d1b24e296])
    IWL0S([Sentinel-1 Interferometric Wide Swath Level 0S Product<br/>58eb66b7-8b01-41bb-8722-65355990bb91])
    IWL0SD([Sentinel-1 Interferometric Wide Swath Level 0S Product - Dual polarization<br/>393af75a-809f-45f2-bb92-9a1b2a1f0715])
    EWL0([Sentinel-1 Extra Wide Swath Level 0 Product<br/>161e39e3-ea6b-42f4-a45b-55617c80eb01])
    EWL0S([Sentinel-1 Extra Wide Swath Level 0S Product<br/>fdbf58bd-f346-4926-8508-bf1fbec8dc76])
    EWL0SD([Sentinel-1 Extra Wide Swath Level 0S Product - Dual polarization<br/>5decf67c-e8f0-4069-ba98-a0d86f41a503])
    SML0([Sentinel-1 Stripmap Level 0 Product<br/>dadcb155-c2ba-4f5c-809b-3531aa76188e])
    SML0S([Sentinel-1 Stripmap Level 0S Product<br/>e39c0af2-b8a1-4d88-87df-d8a7c03d01ad])
    SML0SD([Sentinel-1 Stripmap Level 0S Product - Dual polarization<br/>bdd23381-89c8-4bca-9336-a2ec6a05946f])
    WVL0([Sentinel-1 Wave Level 0 Product<br/>a3d9d02d-5371-42c7-a91a-a6d1c05e8e85])
    WVL0S([Sentinel-1 Wave Level 0S Product<br/>09708cda-2e87-4343-897f-ffb8cc008eb8])
    RFL0([Sentinel-1 RF Characterization Mode Level 0 Product<br/>49dddfc8-f11d-4bf1-b724-f7ad1ff151e9])

    IWL0 --> L0
    IWL0S --> IWL0
    IWL0SD --> IWL0S
    EWL0 --> L0
    EWL0S --> EWL0
    EWL0SD --> EWL0S
    SML0 --> L0
    SML0S --> SML0
    SML0SD --> SML0S
    WVL0 --> L0
    WVL0S --> WVL0
    RFL0 --> L0
```

```mermaid
graph TB
    L0([Sentinel-1 Level 0 Product<br/>800588f9-9a98-4383-a661-572b9a18c3dc])
    ENL0([Sentinel-1 Elevation Notch Mode Level 0 Product<br/>83be69fb-0960-408b-9f3e-7ebdf9990a17])
    ANL0([Sentinel-1 Azimuth Notch Mode Level 0 Product<br/>72f1d944-d721-4ad6-9bce-b0e9c0c2c076])
    GPL0([Sentinel-1 GPS Level 0 Product<br/>e253f21f-81d6-4068-b008-6cb0a607233e])
    HKL0([Sentinel-1 HKTM Level 0 Product<br/>f7aa3a16-ada9-4f07-a7ac-225d33272c3e])
    ZEL0([Sentinel-1 ZE Level 0 Product<br/>709ec267-2dad-4a28-ad8d-b1cc5018ab3a])
    ZIL0([Sentinel-1 ZI Level 0 Product<br/>89307deb-ac24-4a20-b5da-bb3b133fae20])
    ZSL0([Sentinel-1 ZS Level 0 Product<br/>29a3b54c-f596-4dae-8546-65f0727aa8f7])

    ENL0 --> L0
    ANL0 --> L0
    GPL0 --> L0
    HKL0 --> L0
    ZEL0 --> L0
    ZIL0 --> L0
    ZSL0 --> L0
```

### Sentinel-1 Level 1 topics
```mermaid
graph LR
    L1([Sentinel-1 Level 1 Product<br/>84f8d85f-4d2b-4be6-99ad-9a295eb1c252])
    IWL1([Sentinel-1 Interferometric Wide Swath Level 1 Product<br/>0cc1dd60-e5a0-4815-8038-54a4a03630e3])
    IWL1S([Sentinel-1 Interferometric Wide Swath Level 1 S Product<br/>1c62f45b-ff9f-4c19-902f-8ee09c17c2e3])
    AIWL1S([Sentinel-1A Interferometric Wide Swath Level 1 S Product<br/>b0dad6fa-9ae4-4694-b00b-449cd456d32a])
    BIWL1S([Sentinel-1B Interferometric Wide Swath Level 1 S Product<br/>c0d9151e-0d94-4de7-ba46-95338725b064])
    EWL1([Sentinel-1 Extra Wide Swath Level 1 Product<br/>72437eb8-cafd-4b6e-9053-f65dffb0f92d])
    EWL1S([Sentinel-1 Extra Wide Swath Level 1 S Product<br/>2b8c4bc3-eb5a-40ee-a199-970b1ff4e8f7])
    AEWL1S([Sentinel-1A Extra Wide Swath Level 1 S Product<br/>8f224655-d685-442b-b1b0-eb40a18f072e])
    BEWL1S([Sentinel-1B Extra Wide Swath Level 1 S Product<br/>8268efa1-2324-44cc-bde7-3a56dd12e1de])
    SML1([Sentinel-1 Stripmap Level 1 Product<br/>289a7a5d-1d66-4a52-96f3-36990cbc2cff])
    SML1S([Sentinel-1 Stripmap Level 1 S Product<br/>9e4f0c8e-6b48-4a26-b5ff-03fa0713bee0])
    ASML1S([Sentinel-1A Stripmap Level 1 S Product<br/>32a85129-bcb9-4343-b631-3809de409127])
    BSML1S([Sentinel-1B Stripmap Level 1 S Product<br/>f0e8fbbf-6b8a-44d6-ad48-79658cf2d720])
    WVL1([Sentinel-1 Wave Level 1 Product<br/>0cb5851e-ba33-436a-bbfb-d1c63c110bb5])

    IWL1 --> L1
    IWL1S --> IWL1
    AIWL1S --> IWL1S
    BIWL1S --> IWL1S
    EWL1 --> L1
    EWL1S --> EWL1
    AEWL1S --> EWL1S
    BEWL1S --> EWL1S
    SML1 --> L1
    SML1S --> SML1
    ASML1S --> SML1S
    BSML1S --> SML1S
    WVL1 --> L1
```

### Sentinel-1 Level 2 topics
```mermaid
graph TB
    L2([Sentinel-1 Level 2 Product<br/>029c85f0-d567-46ef-8098-3bb32095d8d4])
    IWL2([Sentinel-1 Interferometric Wide Swath Level 2 Product<br/>0af10c04-d706-4b05-a116-2f7d904e2553])
    EWL2([Sentinel-1 Extra Swath Level 2 Product               <br/>8de255fa-9bfa-4af5-9b7b-5316f0836885])
    SML2([Sentinel-1 Stripmap Level 2 Product                  <br/>37e7169c-314a-425a-a4f2-c738f9cf74f4])
    WVL2([Sentinel-1 Wave Level 2 Product                      <br/>b62cb853-a99c-4885-8b1c-8b81ce0c1459])

    IWL2 & EWL2 & SML2 & WVL2 --> L2
```

### Sentinel-1 Auxiliary topics
```mermaid
graph LR
    AUX([Sentinel-1 Auxiliary Product<br/>8c9f1960-f544-47ae-ba45-424b8cc48b45])
    CAL([Sentinel-1 Calibration Auxiliary Product<br/>0741adad-060f-4449-a4a8-7a955019a085])
    INS([Sentinel-1 Instrument Auxiliary Product<br/>ce5f5b40-4507-4fab-9108-ae3d8437ec4e])
    PP1([Sentinel-1 Level-1 Processor Parameters Auxiliary Product<br/>fa50b022-5780-43ec-aee8-a960f8b36768])
    ICE([Sentinel-1 Sea Ice Auxiliary Product<br/>b941947f-a2ef-4fb9-b979-50340ada402e])
    SCS([Sentinel-1 Simulated Cross Spectra Auxiliary Product<br/>37d97f57-9631-427b-957b-c52716659b60])
    WAV([Sentinel-1 Wavewatch III Model Auxiliary Product<br/>f0be22b7-287a-4eff-8a77-6fd59f814616])
    WND([Sentinel-1 ECMWF Atmospheric Model Auxiliary Product<br/>c8be0ee2-c784-45fd-9da7-23de6045394b])
    PP2([Sentinel-1 Level-2 Processor Parameters Auxiliary Product<br/>32af7255-5e23-489a-b9fe-9ca71bf06cd4])

    CAL & INS & PP1 & ICE & SCS & WAV & WND & PP2 --> AUX
```

### Sentinel-1 EOF Auxiliary topics
```mermaid
graph LR
    EOF([Sentinel-1 EOF Auxiliary Product<br/>40273ef3-a898-4779-a788-12322b7ad527])
    MPL([Sentinel-1 EOF MPL ORBPRE Auxiliary Product<br/>bb1ac359-ac10-4d04-9691-e8ca39261cee])
    AMH([Sentinel-1 EOF AMH ERRMAT Auxiliary Product<br/>33fc9e46-f201-4515-b8c5-51810974e1a7])
    AMV([Sentinel-1 EOF AMV ERRMAT Auxiliary Product<br/>e01eb43e-1c86-4fb8-8419-5789d8e4bdc0])
    POD([Sentinel-1 EOF Precise Orbit Determination Auxiliary Product<br/>103c93a3-16cd-410e-8e2a-66431cd40407])
    RESORB([Sentinel-1 EOF Restituted Orbit File Auxiliary Product<br/>1462dbde-5f3b-4adf-98da-ecd66ceaebbd])
    POEORB([Sentinel-1 EOF Precise Orbit Ephemerides Orbit File Auxiliary Product<br/>f82c26d7-26fd-406d-beeb-3230733c0d0b])
    PREORB([Sentinel-1 EOF Predicted Orbit File Auxiliary Product<br/>0bb12b1e-deed-4dec-aaa5-bdf663aaa6b9])

    MPL & AMH & AMV & POD --> EOF
    RESORB & POEORB & PREORB --> POD
```
