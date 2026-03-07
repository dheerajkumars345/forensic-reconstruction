# Forensic System Process Flowchart

This flowchart illustrates the step-by-step logical processes of the Forensic Crime Scene Reconstruction System, represented as a series of connected blocks.

```mermaid
graph TD
    %% Node Styles
    classDef process fill:#ffffff,stroke:#000000,stroke-width:2px,rx:5,ry:5;
    classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px,rx:5,ry:5;
    classDef terminator fill:#e0f2f1,stroke:#004d40,stroke-width:2px,rx:10,ry:10;
    classDef subproc fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,stroke-dasharray: 5 5;

    %% Main Flow
    Start((START)):::terminator --> Login[User Login & Authentication]:::process
    Login --> CaseCheck{Create New Case?}:::decision

    %% Case Initiation
    CaseCheck -- Yes --> InputDetails[Input Case Information\n(ID, Location, Examiner)]:::process
    InputDetails --> Validate[Validate & Create Record]:::process
    Validate --> UploadPhase[Start Evidence Upload]:::process
    CaseCheck -- No --> SelectCase[Select Existing Case]:::process
    SelectCase --> Dashboard[Load Project Dashboard]:::process
    
    %% Phase 1: Evidence Processing
    subgraph Phase_1 [Phase 1: Evidence Acquisition]
        direction TB
        UploadPhase --> Upload[Upload Raw Images]:::process
        Upload --> Hashing[Calculate SHA-256 Hash\n(Data Integrity)]:::process
        Hashing --> Metadata[Extract EXIF & GPS Data]:::process
        Metadata --> ChainOfCustody[Log to Chain of Custody]:::process
        ChainOfCustody --> Storage[Secure Storage]:::process
    end

    Storage --> ReconDecision{Run Reconstruction?}:::decision
    Dashboard --> ReconDecision

    %% Phase 2: Reconstruction
    ReconDecision -- Yes --> SfMPipeline[Initiate SfM Pipeline]:::process
    
    subgraph Phase_2 [Phase 2: 3D Reconstruction Engine]
        direction TB
        SfMPipeline --> FeatureDetect[Feature Detection\n(SIFT/SURF)]:::subproc
        FeatureDetect --> Matching[Feature Matching]:::subproc
        Matching --> SparseRecon[Sparse Point Cloud Gen]:::subproc
        SparseRecon --> DenseRecon[Dense Point Cloud Gen\n(Depth Maps)]:::subproc
        DenseRecon --> Meshing[Surface Mesh Generation\n(Poisson/Delaunay)]:::subproc
        Meshing --> Texturing[Texture Mapping]:::subproc
    end
    
    Texturing --> Visualization[Interactive 3D Visualization]:::process

    %% Phase 3: Analysis
    ReconDecision -- No --> Visualization
    
    Visualization --> AnalysisChoice{Select Tool}:::decision
    
    subgraph Phase_3 [Phase 3: Forensic Analysis]
        direction TB
        AnalysisChoice -- Measure --> Measuring[Measurement Tool]:::process
        Measuring --> DistCalc[Calculate Distance/Angle]:::subproc
        Measuring --> ErrorEst[Estimate Uncertainty]:::subproc
        
        AnalysisChoice -- Map --> Mapping[Geospatial View]:::process
        Mapping --> GPSMap[Map GPS Coordinates]:::subproc
        Mapping --> Macro[Macro-Reconstruction\n(Blood Spatter/Trajectory)]:::subproc
    end

    %% Phase 4: Reporting
    DistCalc --> ReportGen[Generate Report]:::process
    ErrorEst --> ReportGen
    GPSMap --> ReportGen
    Macro --> ReportGen
    
    subgraph Phase_4 [Phase 4: Reporting & Compliance]
        direction TB
        ReportGen --> FetchData[Compile Measurements & Logs]:::process
        FetchData --> VerifyIntegrity[Verify Image Hashes]:::process
        VerifyIntegrity --> Disclaimer[Apply Legal Disclaimers\n(BSA Sec 63 / IEA 65B)]:::process
        Disclaimer --> DigitalSign[Apply Digital Signature]:::process
        DigitalSign --> GeneratePDF[Render PDF Document]:::process
    end

    GeneratePDF --> End((END / SUBMIT)):::terminator
```
