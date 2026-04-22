# BookClub Architecture

Here is the visual layout of the system:
> **_NOTE:_**  Install Mermaid Plugin if not displayed correctly.

```mermaid
flowchart TD
    subgraph Versioning["1. Data & Code Versioning"]
        direction LR
        Git[("fa:fa-code Git (Code)")]
        DVC[("fa:fa-database DVC (Data & Models)")]
    end

    subgraph Training["2. Training & Experimentation"]
        direction LR
        PyTorch["fa:fa-cogs PyTorch (Model Training)"]
        WandB["fa:fa-chart-line Weights & Biases (Experiment Tracking)"]
        
        PyTorch -->|Logs metrics to| WandB
    end

    subgraph Testing["3. CI/CD & Testing"]
        direction LR
        GHA["fa:fa-play-circle GitHub Actions (Pipeline Orchestrator)"]
        Pytest["fa:fa-vial pytest (Unit & Integration Tests)"]
        
        GHA -->|Executes| Pytest
    end

    subgraph Deployment["4. Deployment & Serving"]
        direction LR
        Docker["fa:fa-box Docker (Container Environment)"]
        FastAPI["fa:fa-server FastAPI (Inference API)"]
        Streamlit["fa:fa-desktop Streamlit (User Interface)"]
        
        Docker -.->|Hosts| FastAPI
        Docker -.->|Hosts| Streamlit
        Streamlit -->|Sends API requests to| FastAPI
    end

    %% Invisible scaffolding to strictly enforce block order
    Versioning ~~~ Training
    Training ~~~ Testing
    Testing ~~~ Deployment

    %% 1-level drops (Standard arrows)
    Git -->|Provides Code| PyTorch
    DVC -->|Provides Data| PyTorch
    PyTorch -.->|Saves Trained Model| DVC
    
    %% 2-level drops (Extra dashes to maintain vertical layout)
    Git --->|Triggers Pipeline| GHA
    
    %% 1-level drop
    GHA -->|If tests pass, builds| Docker
    
    %% 3-level drops (Even more dashes to span from top to bottom)
    DVC ---->|Loads Model into| FastAPI
