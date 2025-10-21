# Sprint Coordinator

A comprehensive multi-agent system that guides entrepreneurs through sprint items using a **Design → Execute → Report → Learn** workflow powered by Google's Agent Development Kit (ADK).

## Overview

The Sprint Coordinator helps business entrepreneurs systematically work through their sprint items, applying validated learning principles to continuously improve their business model. The system uses a sequential agent architecture where specialized agents guide users through each phase of the sprint process.

## Features

- **Sequential Agent Workflow**: Design → Execute → Report → Learn phases
- **Sprint Management**: Complete CRUD operations for sprint items
- **Canvas Integration**: Business Model Canvas, Value Proposition Canvas, and Customer Segments
- **Session Management**: InMemorySessionService for state persistence
- **Interactive Interface**: Simple async Python interface for user interaction

## Architecture

### Master Agent (SequentialAgent)
- Orchestrates the complete workflow
- Manages handoffs between sub-agents
- Maintains context and progress tracking

### Sub-Agents
1. **Design Agent**: Hypothesis definition and task planning
2. **Execute Agent**: Implementation guidance and practical execution
3. **Report Agent**: Results analysis and insight generation
4. **Learn Agent**: Business model updates based on findings

### Tools
- **Sprint Tools**: Manage sprint items and status updates
- **Canvas Tools**: Update Business Model Canvas, Value Proposition Canvas, and Customer Segments

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd co-pilot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   APP_NAME=sprint_coordinator
   DEFAULT_USER_ID=user1234
   ```

4. **Get Google API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## Usage

### Running the Application

```bash
python app/main.py
```

### Example Workflow

1. **Start the application** - The system will present available sprint items
2. **Select a sprint item** - Choose which sprint item to work on
3. **Design Phase** - Define hypothesis and create actionable tasks
4. **Execute Phase** - Implement the plan with guided assistance
5. **Report Phase** - Analyze results and generate insights
6. **Learn Phase** - Update business canvases based on findings

### Sample Sprint Item

The system works with sprint items like:
- **Task**: "Conduct A/B Testing on Integration Features"
- **Objective**: "The platform can effectively integrate with existing medical systems"
- **Success Metric**: "Identify the most effective integration feature with a >10% increase in user satisfaction"

## Data Structure

### Sprint Items (`sprints.json`)
```json
{
  "sprints": [
    {
      "sprint_id": "sprint_1",
      "title": "Sprint 1: Validate Platform Efficiency",
      "goal": "Validate platform efficiency and integration",
      "items": [
        {
          "item_id": "s1_item_1",
          "task": "Conduct a Survey on Content Efficiency",
          "objective": "Doctors will find the platform's curated content more efficient",
          "success_metric": "Achieve >70% positive feedback",
          "status": "pending"
        }
      ]
    }
  ]
}
```

### Business Model Canvas (`bmc.json`)
Contains all 9 sections of the Business Model Canvas with current business model data.

### Value Proposition Canvas (`vpc.json`)
Contains Customer Profile and Value Proposition sections with detailed analysis.

### Customer Segments (`segments.json`)
Contains detailed customer personas and segment information.

## Development

### Project Structure
```
app/
├── copilot/
│   ├── __init__.py
│   ├── agent.py (master sequential agent)
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   ├── design_agent.py
│   │   ├── execute_agent.py
│   │   ├── report_agent.py
│   │   └── learn_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── sprint_tools.py
│   │   └── canvas_tools.py
│   └── data/
│       ├── sprints.json
│       ├── bmc.json
│       ├── vpc.json
│       └── segments.json
├── config.py
├── main.py
└── test.py
```

### Running Tests

```bash
python app/test.py
```

### Key Components

- **Configuration**: Environment variables and file paths
- **Tools**: Custom ADK tools for data management
- **Agents**: Specialized LLM agents for each workflow phase
- **Session Management**: InMemorySessionService for state persistence
- **Interface**: Async Python interface for user interaction

## API Reference

### Sprint Tools
- `get_sprint_items()`: Retrieve all sprint items
- `get_sprint_item(item_id)`: Get specific sprint item
- `update_sprint_item_status(item_id, status, notes)`: Update sprint status
- `get_user_sprint_items(user_id)`: Get user's sprint items

### Canvas Tools
- `get_business_model_canvas()`: Retrieve BMC data
- `update_business_model_canvas(section, updates)`: Update BMC section
- `get_value_proposition_canvas()`: Retrieve VPC data
- `update_value_proposition_canvas(section, updates)`: Update VPC section
- `get_customer_segments()`: Retrieve customer segments
- `update_customer_segments(segment_id, updates)`: Update customer segment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.
