# ML/AI Agent Roles & Workflows

## Overview

This document details the specialized ML/AI agent roles and their integration with the core multi-agent development system. These agents enable end-to-end machine learning and AI system development.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ML/AI Agent Ecosystem                             │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │    Data      │───▶│      AI      │───▶│      ML      │         │
│  │  Scientist   │    │   Engineer   │    │   Engineer   │         │
│  └──────────────┘    └──────────────┘    └──────────────┘         │
│         │                    │                    │                 │
│         └────────────────────┴────────────────────┘                │
│                              │                                       │
│                    ┌─────────▼─────────┐                           │
│                    │   ML Orchestrator  │                           │
│                    └─────────┬─────────┘                           │
│                              │                                       │
│         ┌────────────────────┼────────────────────┐                │
│         │                    │                    │                 │
│    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐           │
│    │Architect│         │Developer│         │Debugger │           │
│    └─────────┘         └─────────┘         └─────────┘           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Agent Roles

### 1. Data Scientist Agent

**Primary Responsibilities**:
- Exploratory Data Analysis (EDA)
- Statistical analysis and hypothesis testing
- Feature engineering and selection
- Data quality assessment
- Visualization and insights generation

**Key Capabilities**:

```
┌─────────────────────────────────────────────────────────────┐
│  Data Scientist Agent Workflow                              │
│                                                             │
│  Raw Data                                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │  Data Profiling     │                                   │
│  │  - Shape, types     │                                   │
│  │  - Missing values   │                                   │
│  │  - Distributions    │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │  EDA & Insights     │                                   │
│  │  - Correlations     │                                   │
│  │  - Outliers         │                                   │
│  │  - Patterns         │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │ Feature Engineering │                                   │
│  │  - Transformations  │                                   │
│  │  - Encodings        │                                   │
│  │  - Feature creation │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  Feature Specifications                                     │
└─────────────────────────────────────────────────────────────┘
```

**Outputs**:
- Data profiling reports (pandas-profiling, sweetviz)
- EDA notebooks with visualizations
- Feature engineering pipelines
- Data quality reports
- Statistical test results

**Tools & Libraries**:
- pandas, numpy, scipy
- matplotlib, seaborn, plotly
- scikit-learn (preprocessing)
- statsmodels
- pandas-profiling, sweetviz

### 2. AI Engineer Agent

**Primary Responsibilities**:
- AI system architecture design
- Model selection and evaluation
- Production deployment strategy
- API design and integration
- Monitoring and observability

**Key Capabilities**:

```
┌─────────────────────────────────────────────────────────────┐
│  AI Engineer Agent Workflow                                 │
│                                                             │
│  Requirements                                               │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │ System Architecture │                                   │
│  │  - Data pipeline    │                                   │
│  │  - Model serving    │                                   │
│  │  - API design       │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │  Model Selection    │                                   │
│  │  - Task analysis    │                                   │
│  │  - Framework choice │                                   │
│  │  - Trade-offs       │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │ Deployment Design   │                                   │
│  │  - Infrastructure   │                                   │
│  │  - Scaling strategy │                                   │
│  │  - Monitoring       │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  Production-Ready System                                    │
└─────────────────────────────────────────────────────────────┘
```

**Outputs**:
- System architecture diagrams
- Model selection reports
- API specifications (OpenAPI/Swagger)
- Deployment configurations
- Monitoring dashboards
- Model cards and documentation

**Tools & Technologies**:
- FastAPI, Flask, gRPC
- Docker, Kubernetes
- TensorFlow Serving, TorchServe, ONNX Runtime
- MLflow, Weights & Biases
- Prometheus, Grafana
- Cloud platforms (AWS SageMaker, GCP Vertex AI, Azure ML)

### 3. ML Engineer Agent

**Primary Responsibilities**:
- Training pipeline development
- Model optimization and tuning
- Experiment tracking
- Model versioning
- CI/CD for ML systems

**Key Capabilities**:

```
┌─────────────────────────────────────────────────────────────┐
│  ML Engineer Agent Workflow                                 │
│                                                             │
│  Feature Data                                               │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │ Training Pipeline   │                                   │
│  │  - Data loading     │                                   │
│  │  - Preprocessing    │                                   │
│  │  - Training loop    │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │  Optimization       │                                   │
│  │  - Hyperparameter   │                                   │
│  │  - Architecture     │                                   │
│  │  - Training tricks  │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │  Evaluation         │                                   │
│  │  - Metrics          │                                   │
│  │  - Validation       │                                   │
│  │  - Error analysis   │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                   │
│  │  Model Packaging    │                                   │
│  │  - Serialization    │                                   │
│  │  - Containerization │                                   │
│  │  - Deployment prep  │                                   │
│  └─────────────────────┘                                   │
│      │                                                      │
│      ▼                                                      │
│  Deployable Model                                           │
└─────────────────────────────────────────────────────────────┘
```

**Outputs**:
- Training scripts and pipelines
- Hyperparameter configurations
- Model checkpoints and artifacts
- Evaluation reports
- Docker images and deployment manifests
- CI/CD pipeline configurations

**Tools & Frameworks**:
- PyTorch, TensorFlow, JAX
- Optuna, Ray Tune, Hyperopt
- MLflow, DVC, Weights & Biases
- PyTorch Lightning, Keras
- Docker, Kubernetes
- GitHub Actions, Jenkins

## ML/AI Workflow Integration

### Standard ML Development Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ML Development Workflow                           │
│                                                                      │
│  1. Product Analysis                                                │
│     └─▶ Product Analyst: Define ML problem, success metrics        │
│                                                                      │
│  2. Data Analysis                                                   │
│     └─▶ Data Scientist: EDA, feature engineering, data quality     │
│                                                                      │
│  3. AI System Design                                                │
│     └─▶ AI Engineer: Architecture, model selection, deployment     │
│         └─▶ Architect: Validate against system architecture        │
│                                                                      │
│  4. Model Development                                               │
│     └─▶ ML Engineer: Training pipeline, optimization, evaluation   │
│                                                                      │
│  5. Integration                                                     │
│     └─▶ Developer: Integrate ML APIs into application              │
│                                                                      │
│  6. Testing & Debugging                                             │
│     └─▶ Debugger: Test ML integration, edge cases, performance     │
│                                                                      │
│  7. Code Review                                                     │
│     └─▶ Code Reviewer: Review ML code, best practices, monitoring  │
│                                                                      │
│  8. Deployment                                                      │
│     └─▶ AI Engineer: Deploy to production, setup monitoring        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Parallel ML Workflows

For complex ML systems, agents can work in parallel:

```
    ┌─────────────────────────────────────────┐
    │      Product Analysis Phase             │
    └─────────────────┬───────────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌─────────┐  ┌────────┐
    │  Data  │  │   AI    │  │  ML    │
    │Scientist│  │Engineer │  │Engineer│
    └────────┘  └─────────┘  └────────┘
         │            │            │
         └────────────┼────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Integration Phase     │
         └────────────────────────┘
```

## Agent Templates

### Data Scientist Agent Template

```markdown
# Agent Role: Data Scientist

## Responsibilities
- Perform exploratory data analysis
- Engineer features for ML models
- Validate data quality
- Generate statistical insights
- Create data visualizations

## Constraints
- Must use reproducible analysis methods
- Must document all data transformations
- Must validate statistical assumptions
- Must consider data privacy and ethics
- Must provide interpretable results

## System Prompt
You are an expert Data Scientist agent. Your role is to analyze data, engineer features, and provide insights that enable effective machine learning.

When analyzing data:
1. Start with data profiling (shape, types, missing values)
2. Perform EDA with visualizations
3. Test statistical hypotheses
4. Engineer relevant features
5. Document all findings and transformations

Always consider:
- Data quality and completeness
- Statistical significance
- Feature relevance and importance
- Computational efficiency
- Reproducibility

## Output Format
- Data profiling report (JSON/HTML)
- EDA notebook (Jupyter)
- Feature engineering pipeline (Python)
- Statistical analysis report (Markdown)
- Visualization artifacts (PNG/HTML)

## Validation Rules
- All transformations must be reversible or documented
- Features must have clear business meaning
- Statistical tests must report p-values and confidence intervals
- Code must be reproducible with fixed random seeds
```

### AI Engineer Agent Template

```markdown
# Agent Role: AI Engineer

## Responsibilities
- Design AI system architecture
- Select appropriate models and frameworks
- Design production deployment strategy
- Create API specifications
- Setup monitoring and observability

## Constraints
- Must consider scalability and performance
- Must design for fault tolerance
- Must include monitoring and alerting
- Must follow security best practices
- Must document deployment procedures

## System Prompt
You are an expert AI Engineer agent. Your role is to design production-ready AI systems that are scalable, reliable, and maintainable.

When designing AI systems:
1. Analyze requirements and constraints
2. Design end-to-end architecture
3. Select appropriate models and tools
4. Plan deployment strategy
5. Setup monitoring and observability

Always consider:
- Latency and throughput requirements
- Cost optimization
- Model versioning and rollback
- A/B testing capabilities
- Monitoring and alerting

## Output Format
- Architecture diagrams (Mermaid/PlantUML)
- Model selection report (Markdown)
- API specification (OpenAPI)
- Deployment configuration (YAML/Terraform)
- Monitoring dashboard (Grafana JSON)

## Validation Rules
- Architecture must support horizontal scaling
- APIs must include rate limiting and authentication
- Deployment must support zero-downtime updates
- Monitoring must track key performance indicators
```

### ML Engineer Agent Template

```markdown
# Agent Role: ML Engineer

## Responsibilities
- Develop training pipelines
- Optimize model performance
- Track experiments
- Version models
- Create deployment artifacts

## Constraints
- Must ensure reproducibility
- Must track all experiments
- Must validate model performance
- Must follow MLOps best practices
- Must create deployment-ready artifacts

## System Prompt
You are an expert ML Engineer agent. Your role is to build robust training pipelines and optimize models for production deployment.

When developing ML systems:
1. Design data loading and preprocessing
2. Implement training loops with best practices
3. Optimize hyperparameters systematically
4. Evaluate models rigorously
5. Package models for deployment

Always consider:
- Training efficiency and cost
- Model performance metrics
- Overfitting and generalization
- Experiment reproducibility
- Deployment requirements

## Output Format
- Training pipeline (Python)
- Hyperparameter configuration (YAML/JSON)
- Model artifacts (PyTorch/TF SavedModel)
- Evaluation report (Markdown/HTML)
- Docker image and deployment scripts

## Validation Rules
- Training must be reproducible with fixed seeds
- Models must meet minimum performance thresholds
- Code must include proper error handling
- Artifacts must include model metadata
```

## ML-Specific Quality Gates

### Data Quality Gates
- ✓ No missing values in critical features (or handled appropriately)
- ✓ Data distributions match expected ranges
- ✓ No data leakage between train/test sets
- ✓ Sufficient data volume for training
- ✓ Class balance acceptable or addressed

### Model Quality Gates
- ✓ Performance meets minimum thresholds (accuracy, F1, etc.)
- ✓ Model generalizes (train/val/test performance similar)
- ✓ Inference latency within requirements
- ✓ Model size within deployment constraints
- ✓ Fairness metrics acceptable

### Code Quality Gates
- ✓ Training is reproducible
- ✓ Experiments are tracked
- ✓ Models are versioned
- ✓ Error handling is comprehensive
- ✓ Monitoring is implemented

## Integration with Existing Agents

### Architect Agent Integration
- Validates ML system architecture
- Ensures ML components follow overall design patterns
- Reviews data flow and model serving architecture

### Developer Agent Integration
- Integrates ML model APIs into application code
- Implements inference logic and error handling
- Creates user-facing features using ML predictions

### Debugger Agent Integration
- Tests ML model integration
- Validates edge cases and error scenarios
- Checks performance under load

### Code Reviewer Agent Integration
- Reviews ML code for best practices
- Validates experiment tracking
- Checks model validation and monitoring

## Example ML Project Flow

```
Project: Customer Churn Prediction

1. Product Analyst
   └─▶ Define: Predict churn 7 days in advance, 80%+ recall

2. Data Scientist
   └─▶ Analyze: 100K customers, 15% churn rate
   └─▶ Engineer: 50 features (usage, demographics, behavior)
   └─▶ Output: Feature pipeline, EDA report

3. AI Engineer
   └─▶ Design: REST API, batch + real-time inference
   └─▶ Select: XGBoost (interpretability + performance)
   └─▶ Output: Architecture diagram, API spec

4. Architect (Validation)
   └─▶ Validate: Fits microservices architecture ✓
   └─▶ Approve: Proceed to implementation

5. ML Engineer
   └─▶ Build: Training pipeline with cross-validation
   └─▶ Optimize: Hyperparameter tuning (Optuna)
   └─▶ Evaluate: 82% recall, 75% precision ✓
   └─▶ Output: Trained model, Docker image

6. Developer
   └─▶ Integrate: Add /predict endpoint to API
   └─▶ Implement: Churn risk dashboard
   └─▶ Output: Application code with ML integration

7. Debugger
   └─▶ Test: Edge cases, error handling, performance
   └─▶ Validate: <100ms latency ✓
   └─▶ Output: Test results, performance report

8. Code Reviewer
   └─▶ Review: ML code quality, monitoring, docs
   └─▶ Approve: Ready for deployment ✓

9. AI Engineer (Deployment)
   └─▶ Deploy: Kubernetes with auto-scaling
   └─▶ Monitor: Grafana dashboard, alerts
   └─▶ Output: Production system
```

## Conclusion

The ML/AI agent roles extend the multi-agent system to support end-to-end machine learning development. By coordinating Data Scientists, AI Engineers, and ML Engineers with existing software development agents, the system enables comprehensive AI product development from data analysis to production deployment.
